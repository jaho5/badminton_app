"""
Player matching algorithms for creating balanced matches.
"""
import random
from typing import List, Dict, Any, Tuple, Optional
import itertools

def create_random_match(available_players: List[Dict[str, Any]]) -> Tuple[List[int], List[int]]:
    """
    Create a random match from available players.
    
    Args:
        available_players: List of player dictionaries with user_id and elo
    
    Returns:
        Tuple of (team1_player_ids, team2_player_ids)
    """
    if len(available_players) < 4:
        raise ValueError("Need at least 4 players to create a match")
    
    # Randomly select 4 players
    selected_players = random.sample(available_players, 4)
    
    # Divide into teams
    team1 = [selected_players[0]['user_id'], selected_players[1]['user_id']]
    team2 = [selected_players[2]['user_id'], selected_players[3]['user_id']]
    
    return (team1, team2)

def create_balanced_match(available_players: List[Dict[str, Any]]) -> Tuple[List[int], List[int]]:
    """
    Create a balanced match from available players based on Elo ratings.
    
    Args:
        available_players: List of player dictionaries with user_id and elo
    
    Returns:
        Tuple of (team1_player_ids, team2_player_ids)
    """
    if len(available_players) < 4:
        raise ValueError("Need at least 4 players to create a match")
    
    # Make sure all players have Elo ratings
    for player in available_players:
        if 'elo' not in player or player['elo'] is None:
            player['elo'] = 1500  # Default Elo rating
    
    # Sort players by Elo (highest to lowest)
    sorted_players = sorted(available_players, key=lambda p: p['elo'], reverse=True)
    
    # Method 1: Split by skill - best and worst vs 2nd and 3rd best
    team1 = [sorted_players[0]['user_id'], sorted_players[3]['user_id']]
    team2 = [sorted_players[1]['user_id'], sorted_players[2]['user_id']]
    
    return (team1, team2)

def find_optimal_teams(available_players: List[Dict[str, Any]], team_size: int = 2) -> Tuple[List[int], List[int]]:
    """
    Find the most balanced teams from available players based on Elo ratings.
    
    Args:
        available_players: List of player dictionaries with user_id and elo
        team_size: Number of players in each team
    
    Returns:
        Tuple of (team1_player_ids, team2_player_ids)
    """
    if len(available_players) < team_size * 2:
        raise ValueError(f"Need at least {team_size * 2} players to create balanced teams")
    
    # Ensure all players have an Elo rating
    players_with_elo = []
    for player in available_players:
        elo = player.get('elo')
        if elo is None:
            elo = 1500  # Default Elo rating
        players_with_elo.append({'user_id': player['user_id'], 'elo': elo})
    
    # Try all possible combinations of teams
    best_diff = float('inf')
    best_team1 = []
    best_team2 = []
    
    # Get all possible combinations of team_size players
    all_players = list(range(len(players_with_elo)))
    for team1_indices in itertools.combinations(all_players, team_size):
        team2_indices = [i for i in all_players if i not in team1_indices]
        
        # Calculate total Elo for each team
        team1_elo = sum(players_with_elo[i]['elo'] for i in team1_indices)
        team2_elo = sum(players_with_elo[i]['elo'] for i in team2_indices[:team_size])
        
        # Calculate difference in team strength
        elo_diff = abs(team1_elo - team2_elo)
        
        if elo_diff < best_diff:
            best_diff = elo_diff
            best_team1 = [players_with_elo[i]['user_id'] for i in team1_indices]
            best_team2 = [players_with_elo[i]['user_id'] for i in team2_indices[:team_size]]
    
    return (best_team1, best_team2)

def create_singles_match(available_players: List[Dict[str, Any]]) -> Tuple[List[int], List[int]]:
    """
    Create a singles match with close Elo ratings.
    
    Args:
        available_players: List of player dictionaries with user_id and elo
    
    Returns:
        Tuple of ([player1_id], [player2_id])
    """
    if len(available_players) < 2:
        raise ValueError("Need at least 2 players to create a singles match")
    
    return find_optimal_teams(available_players, team_size=1)
