"""
Database queries for the badminton app.
"""
import sqlite3
from typing import List, Dict, Optional, Any, Union
from .database import get_connection
from .models import User, Match, Available, Elo

# User queries
def get_all_users() -> List[Dict[str, Any]]:
    """Get all users from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users ORDER BY display_name")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def create_user(user: User) -> int:
    """Create a new user and return the new user ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (display_name, first_name, last_name) VALUES (?, ?, ?)",
        (user.display_name, user.first_name, user.last_name)
    )
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return user_id

def update_user(user: User) -> None:
    """Update an existing user's information."""
    if user.id is None:
        raise ValueError("User ID cannot be None for update operation")
        
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET display_name = ?, first_name = ?, last_name = ? WHERE id = ?",
        (user.display_name, user.first_name, user.last_name, user.id)
    )
    conn.commit()
    conn.close()
    
def delete_user(user_id: int) -> None:
    """Delete a user and all related data (elo, availability)."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if user is involved in any matches
    cursor.execute("""
        SELECT COUNT(*) as match_count FROM matches 
        WHERE side_1_user_1_id = ? OR side_1_user_2_id = ? OR 
              side_2_user_1_id = ? OR side_2_user_2_id = ?
    """, (user_id, user_id, user_id, user_id))
    
    result = cursor.fetchone()
    if result and result['match_count'] > 0:
        # Update matches to replace this user with NULL
        cursor.execute("UPDATE matches SET side_1_user_1_id = NULL WHERE side_1_user_1_id = ?", (user_id,))
        cursor.execute("UPDATE matches SET side_1_user_2_id = NULL WHERE side_1_user_2_id = ?", (user_id,))
        cursor.execute("UPDATE matches SET side_2_user_1_id = NULL WHERE side_2_user_1_id = ?", (user_id,))
        cursor.execute("UPDATE matches SET side_2_user_2_id = NULL WHERE side_2_user_2_id = ?", (user_id,))
    
    # Delete from all related tables
    cursor.execute("DELETE FROM availables WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM elos WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM save WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    
    conn.commit()
    conn.close()

# Available player queries
def get_all_availables() -> List[Dict[str, Any]]:
    """Get all available players with their details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            availables.id, availables.user_id, users.display_name, 
            users.first_name, users.last_name, elos.elo,
            CASE WHEN save.id IS NOT NULL THEN 1 ELSE 0 END as is_saved
        FROM availables
        JOIN users ON availables.user_id = users.id
        LEFT JOIN elos ON elos.user_id = availables.user_id
        LEFT JOIN save ON save.user_id = availables.user_id
        ORDER BY elos.elo DESC
    """)
    availables = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return availables

def get_all_unavailables() -> List[Dict[str, Any]]:
    """Get all unavailable players with their details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            users.id as user_id, users.display_name, elos.elo,
            CASE WHEN save.id IS NOT NULL THEN 1 ELSE 0 END as is_saved
        FROM users
        LEFT JOIN availables ON availables.user_id = users.id
        LEFT JOIN elos ON elos.user_id = users.id
        LEFT JOIN save ON save.user_id = users.id
        WHERE availables.user_id IS NULL
        ORDER BY elos.elo DESC
    """)
    unavailables = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return unavailables

def toggle_availability(user_id: int) -> None:
    """Toggle a player's availability status."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if user is available
    cursor.execute("SELECT user_id FROM availables WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result:
        # Remove from availables if already available
        cursor.execute("DELETE FROM availables WHERE user_id = ?", (user_id,))
    else:
        # Add to availables if not available
        cursor.execute("INSERT INTO availables (user_id) VALUES (?)", (user_id,))
    
    conn.commit()
    conn.close()

def save_available_state() -> None:
    """Save the current available players state."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear current saved state
    cursor.execute("DELETE FROM save")
    
    # Save current available players
    cursor.execute("INSERT INTO save (user_id) SELECT user_id FROM availables")
    
    conn.commit()
    conn.close()

def load_available_state() -> None:
    """Load the saved available players state."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Clear current availables
    cursor.execute("DELETE FROM availables")
    
    # Load saved availables
    cursor.execute("INSERT INTO availables (user_id) SELECT user_id FROM save")
    
    conn.commit()
    conn.close()

# Match queries
def get_all_matches() -> List[Dict[str, Any]]:
    """Get all matches with player details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            matches.id, matches.side_1_user_1_id, matches.side_1_user_2_id,
            matches.side_2_user_1_id, matches.side_2_user_2_id, 
            matches.set_1_side_1_score, matches.set_1_side_2_score,
            matches.set_2_side_1_score, matches.set_2_side_2_score,
            matches.set_3_side_1_score, matches.set_3_side_2_score,
            u1.display_name AS side_1_user_1_display_name,
            u2.display_name AS side_1_user_2_display_name,
            u3.display_name AS side_2_user_1_display_name,
            u4.display_name AS side_2_user_2_display_name,
            matches.timestamp
        FROM matches
        LEFT JOIN users AS u1 ON matches.side_1_user_1_id = u1.id
        LEFT JOIN users AS u2 ON matches.side_1_user_2_id = u2.id
        LEFT JOIN users AS u3 ON matches.side_2_user_1_id = u3.id
        LEFT JOIN users AS u4 ON matches.side_2_user_2_id = u4.id
        ORDER BY matches.id DESC
    """)
    matches = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return matches

def create_match(match: Match) -> int:
    """Create a new match and return the match ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO matches (
            side_1_user_1_id, side_1_user_2_id, 
            side_2_user_1_id, side_2_user_2_id
        ) VALUES (?, ?, ?, ?)
        """,
        (
            match.side_1_user_1_id, match.side_1_user_2_id,
            match.side_2_user_1_id, match.side_2_user_2_id
        )
    )
    match_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return match_id

def update_match_score(match_id: int, 
                      set_1_side_1_score: int, set_1_side_2_score: int,
                      set_2_side_1_score: Optional[int] = None, set_2_side_2_score: Optional[int] = None,
                      set_3_side_1_score: Optional[int] = None, set_3_side_2_score: Optional[int] = None) -> None:
    """Update a match's score."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        UPDATE matches 
        SET set_1_side_1_score = ?, set_1_side_2_score = ?,
            set_2_side_1_score = ?, set_2_side_2_score = ?,
            set_3_side_1_score = ?, set_3_side_2_score = ?
        WHERE id = ?
        """,
        (
            set_1_side_1_score, set_1_side_2_score,
            set_2_side_1_score, set_2_side_2_score,
            set_3_side_1_score, set_3_side_2_score,
            match_id
        )
    )
    conn.commit()
    conn.close()

def get_match_players(match_id: int) -> List[int]:
    """Get all player IDs participating in a match."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT side_1_user_1_id, side_1_user_2_id, side_2_user_1_id, side_2_user_2_id
        FROM matches
        WHERE id = ?
        """,
        (match_id,)
    )
    match = cursor.fetchone()
    conn.close()
    
    if not match:
        return []
    
    players = []
    for player_id in [match['side_1_user_1_id'], match['side_1_user_2_id'], 
                     match['side_2_user_1_id'], match['side_2_user_2_id']]:
        if player_id is not None:
            players.append(player_id)
    
    return players

# Elo queries
def get_all_elos() -> List[Dict[str, Any]]:
    """Get all Elo ratings with player details."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT elos.id, elos.user_id, elos.elo, users.display_name, 
               users.first_name, users.last_name
        FROM elos
        JOIN users ON elos.user_id = users.id
        ORDER BY elos.elo DESC
    """)
    elos = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return elos

def update_elo(user_id: int, new_elo: float, change_reason: Optional[str] = None) -> None:
    """Update a player's Elo rating or create it if it doesn't exist."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if Elo exists for this user
    cursor.execute("SELECT id, elo FROM elos WHERE user_id = ?", (user_id,))
    elo_record = cursor.fetchone()
    
    if elo_record:
        # Get the old ELO for history tracking
        old_elo = elo_record['elo']
        
        # Update existing Elo
        cursor.execute(
            "UPDATE elos SET elo = ? WHERE user_id = ?",
            (new_elo, user_id)
        )
    else:
        # Create new Elo
        cursor.execute(
            "INSERT INTO elos (user_id, elo) VALUES (?, ?)",
            (user_id, new_elo)
        )
        old_elo = None
    
    # Record this change in the history
    cursor.execute(
        "INSERT INTO elo_history (user_id, old_elo, new_elo, change_reason) VALUES (?, ?, ?, ?)",
        (user_id, old_elo, new_elo, change_reason)
    )
    
    conn.commit()
    conn.close()

def get_available_players(min_rank: Optional[int] = None, max_rank: Optional[int] = None) -> List[Dict[str, Any]]:
    """Get available players, optionally filtered by rank range."""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT availables.user_id, users.display_name, elos.elo 
        FROM availables 
        JOIN users ON availables.user_id = users.id
        LEFT JOIN elos ON availables.user_id = elos.user_id 
        ORDER BY elos.elo DESC
    """
    
    cursor.execute(query)
    players = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    # Apply rank filtering if needed
    if min_rank is not None or max_rank is not None:
        # Default values if one bound is not specified
        min_idx = min_rank - 1 if min_rank is not None else 0
        max_idx = max_rank - 1 if max_rank is not None else len(players) - 1
        
        # Ensure valid indexes
        min_idx = max(0, min_idx)
        max_idx = min(len(players) - 1, max_idx)
        
        if min_idx <= max_idx:
            players = players[min_idx:(max_idx + 1)]
        else:
            players = []
    
    return players

def remove_players_from_available(player_ids: List[int]) -> None:
    """Remove multiple players from the available list."""
    if not player_ids:
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    
    # Using parameter substitution for a list of IDs
    placeholders = ', '.join(['?'] * len(player_ids))
    cursor.execute(f"DELETE FROM availables WHERE user_id IN ({placeholders})", player_ids)
    
    conn.commit()
    conn.close()

def add_players_to_available(player_ids: List[int]) -> None:
    """Add multiple players to the available list."""
    if not player_ids:
        return
        
    conn = get_connection()
    cursor = conn.cursor()
    
    for player_id in player_ids:
        try:
            cursor.execute("INSERT INTO availables (user_id) VALUES (?)", (player_id,))
        except sqlite3.IntegrityError:
            # Ignore if player is already in the available list
            pass
    
    conn.commit()
    conn.close()
    

def get_player_elo_history(user_id: int) -> List[Dict[str, Any]]:
    """Get the ELO rating history for a player."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT elo_history.id, elo_history.user_id, elo_history.old_elo, 
               elo_history.new_elo, elo_history.change_reason, elo_history.timestamp,
               users.display_name
        FROM elo_history
        JOIN users ON elo_history.user_id = users.id
        WHERE elo_history.user_id = ?
        ORDER BY elo_history.timestamp DESC
    """, (user_id,))
    history = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return history
