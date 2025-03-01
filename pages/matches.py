"""
Matches management page.
"""
import streamlit as st
import random
from typing import List, Dict, Any, Tuple, Optional

from db import queries
from db.models import Match
from utils import matching

def render_matches():
    """Render the matches management page."""
    st.title("Badminton Matches")
    
    # Create matches section
    st.header("Create New Match")
    
    # Match creation options
    match_type = st.radio(
        "Match Type",
        options=["Doubles", "Singles"],
        horizontal=True
    )
    
    col1, col2 = st.columns(2)
    with col1:
        match_method = st.radio(
            "Team Selection Method",
            options=["Random", "Balanced by ELO", "Optimal Balance"],
            horizontal=False
        )
    
    with col2:
        if st.button("Create Match", use_container_width=True, type="primary"):
            available_players = queries.get_available_players()
            
            if len(available_players) < (4 if match_type == "Doubles" else 2):
                st.error(f"Not enough available players for a {match_type.lower()} match!")
            else:
                try:
                    if match_type == "Doubles":
                        if match_method == "Random":
                            team1, team2 = matching.create_random_match(available_players)
                        elif match_method == "Balanced by ELO":
                            team1, team2 = matching.create_balanced_match(available_players)
                        else:  # Optimal Balance
                            team1, team2 = matching.find_optimal_teams(available_players)
                            
                        # Create the match
                        match = Match(
                            side_1_user_1_id=team1[0],
                            side_1_user_2_id=team1[1] if len(team1) > 1 else None,
                            side_2_user_1_id=team2[0],
                            side_2_user_2_id=team2[1] if len(team2) > 1 else None
                        )
                    else:  # Singles
                        team1, team2 = matching.create_singles_match(available_players)
                        
                        # Create the match
                        match = Match(
                            side_1_user_1_id=team1[0],
                            side_1_user_2_id=None,
                            side_2_user_1_id=team2[0],
                            side_2_user_2_id=None
                        )
                    
                    # Save the match to the database
                    match_id = queries.create_match(match)
                    
                    # Remove players from available pool
                    all_players = team1 + team2
                    queries.remove_players_from_available(all_players)
                    
                    st.success(f"Match created successfully!")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error creating match: {str(e)}")
    
    # Display current matches
    st.header("Current Matches")
    matches = queries.get_all_matches()
    
    if not matches:
        st.info("No matches have been created yet.")
    else:
        for match in matches:
            with st.expander(f"Match #{match['id']}"):
                # Determine if it's singles or doubles
                is_singles = (match['side_1_user_2_id'] is None and match['side_2_user_2_id'] is None)
                match_type_str = "Singles" if is_singles else "Doubles"
                
                # Display match details
                st.markdown(f"**{match_type_str} Match**")
                
                # Team 1
                st.markdown("**Team 1:**")
                team1_str = f"• {match['side_1_user_1_display_name']}"
                if not is_singles and match['side_1_user_2_display_name']:
                    team1_str += f" + {match['side_1_user_2_display_name']}"
                st.markdown(team1_str)
                
                # Team 2
                st.markdown("**Team 2:**")
                team2_str = f"• {match['side_2_user_1_display_name']}"
                if not is_singles and match['side_2_user_2_display_name']:
                    team2_str += f" + {match['side_2_user_2_display_name']}"
                st.markdown(team2_str)
                
                # Score input section
                st.markdown("---")
                st.markdown("**Score:**")
                
                # First set
                col1, col2 = st.columns(2)
                with col1:
                    set1_team1 = st.number_input(
                        "Set 1 - Team 1", 
                        min_value=0, 
                        max_value=30, 
                        value=match['set_1_side_1_score'] or 0,
                        key=f"match_{match['id']}_set1_team1"
                    )
                with col2:
                    set1_team2 = st.number_input(
                        "Set 1 - Team 2", 
                        min_value=0, 
                        max_value=30, 
                        value=match['set_1_side_2_score'] or 0,
                        key=f"match_{match['id']}_set1_team2"
                    )
                
                # Second set
                col1, col2 = st.columns(2)
                with col1:
                    set2_team1 = st.number_input(
                        "Set 2 - Team 1", 
                        min_value=0, 
                        max_value=30, 
                        value=match['set_2_side_1_score'] or 0,
                        key=f"match_{match['id']}_set2_team1"
                    )
                with col2:
                    set2_team2 = st.number_input(
                        "Set 2 - Team 2", 
                        min_value=0, 
                        max_value=30, 
                        value=match['set_2_side_2_score'] or 0,
                        key=f"match_{match['id']}_set2_team2"
                    )
                
                # Third set (optional)
                col1, col2 = st.columns(2)
                with col1:
                    set3_team1 = st.number_input(
                        "Set 3 - Team 1 (if needed)", 
                        min_value=0, 
                        max_value=30, 
                        value=match['set_3_side_1_score'] or 0,
                        key=f"match_{match['id']}_set3_team1"
                    )
                with col2:
                    set3_team2 = st.number_input(
                        "Set 3 - Team 2 (if needed)", 
                        min_value=0, 
                        max_value=30, 
                        value=match['set_3_side_2_score'] or 0,
                        key=f"match_{match['id']}_set3_team2"
                    )
                
                # Save score button
                if st.button("Save Score", key=f"save_score_{match['id']}"):
                    queries.update_match_score(
                        match['id'],
                        set1_team1, set1_team2,
                        set2_team1, set2_team2,
                        set3_team1, set3_team2
                    )
                    st.success("Score updated successfully!")
                
                # Return players to available pool button
                if st.button("Return Players to Available Pool", key=f"return_players_{match['id']}"):
                    # Get all players in this match
                    match_players = queries.get_match_players(match['id'])
                    # Add them back to available pool
                    queries.add_players_to_available(match_players)
                    st.success("Players returned to available pool!")
                    st.experimental_rerun()
