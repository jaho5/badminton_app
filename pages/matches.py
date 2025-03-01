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
    
    # Create matches section with accordion/expander for mobile friendliness
    with st.expander("Create New Match", expanded=True):
        # Simple wizard-like interface for match creation
        st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)
        
        # Step 1: Match Type with larger clickable buttons instead of radio
        st.subheader("Step 1: Select Match Type")
        col1, col2 = st.columns(2)
        
        # Session state for storing match creation choices
        if 'match_type' not in st.session_state:
            st.session_state.match_type = "Doubles"
            
        with col1:
            if st.button("Doubles", use_container_width=True, 
                       type="primary" if st.session_state.match_type == "Doubles" else "secondary"):
                st.session_state.match_type = "Doubles"
                st.rerun()
        
        with col2:
            if st.button("Singles", use_container_width=True,
                       type="primary" if st.session_state.match_type == "Singles" else "secondary"):
                st.session_state.match_type = "Singles"
                st.rerun()
                
        # Step 2: Team Selection Method with more visual buttons
        st.subheader("Step 2: Team Selection Method")
        
        if 'match_method' not in st.session_state:
            st.session_state.match_method = "Balanced by ELO"
        
        # Create 3 columns for the 3 options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎲\nRandom", use_container_width=True,
                       type="primary" if st.session_state.match_method == "Random" else "secondary"):
                st.session_state.match_method = "Random"
                st.rerun()
                
        with col2:
            if st.button("⚖️\nBalanced", use_container_width=True,
                       type="primary" if st.session_state.match_method == "Balanced by ELO" else "secondary"):
                st.session_state.match_method = "Balanced by ELO"
                st.rerun()
                
        with col3:
            if st.button("✨\nOptimal", use_container_width=True,
                       type="primary" if st.session_state.match_method == "Optimal Balance" else "secondary"):
                st.session_state.match_method = "Optimal Balance"
                st.rerun()
        
        # Step 3: Create the Match
        st.subheader("Step 3: Create Match")
        match_type = st.session_state.match_type
        match_method = st.session_state.match_method
        
        # Summary of selection
        st.markdown(f"**Match Type:** {match_type}")
        st.markdown(f"**Team Selection:** {match_method}")
        
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
                    st.rerun()
                except Exception as e:
                    st.error(f"Error creating match: {str(e)}")
    
    # Display current matches
    st.header("Current Matches")
    matches = queries.get_all_matches()
    
    if not matches:
        st.info("No matches have been created yet.")
    else:
        # Group matches by status for better organization
        ongoing_matches = []
        completed_matches = []
        
        for match in matches:
            # Check if scores exist to determine match status
            has_scores = match['set_1_side_1_score'] is not None and match['set_1_side_2_score'] is not None
            
            if has_scores:
                completed_matches.append(match)
            else:
                ongoing_matches.append(match)
        
        # Display ongoing matches first
        if ongoing_matches:
            st.markdown("### 🔥 Ongoing Matches")
            for match in ongoing_matches:
                # Use a visual indicator for match status
                with st.expander(f"Match #{match['id']} - ONGOING", expanded=True):
                    # Determine if it's singles or doubles
                    is_singles = (match['side_1_user_2_id'] is None and match['side_2_user_2_id'] is None)
                    match_type_str = "Singles" if is_singles else "Doubles"
                
                    # Display match details with improved styling
                    st.markdown(f"**{match_type_str} Match**")
                    
                    # Team information with better visual formatting
                    st.markdown("<div style='background-color: #f8f9fa; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                
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
                    
                    # Close the team info div
                    st.markdown("</div>", unsafe_allow_html=True)
                
                    # Score input section with better mobile layout
                    st.markdown("<h4 style='margin-top:15px;'>Score</h4>", unsafe_allow_html=True)
                    
                    # Score input boxes organized in a mobile-friendly way
                    st.markdown("<div style='background-color: #f0f0f0; padding: 15px; border-radius: 10px;'>", unsafe_allow_html=True)
                    
                    # First set with better spacing
                    st.markdown("<p style='font-weight:bold;'>Set 1</p>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        set1_team1 = st.number_input(
                            "Team 1", 
                            min_value=0, 
                            max_value=30, 
                            value=match['set_1_side_1_score'] or 0,
                            key=f"match_{match['id']}_set1_team1"
                        )
                    with col2:
                        set1_team2 = st.number_input(
                            "Team 2", 
                            min_value=0, 
                            max_value=30, 
                            value=match['set_1_side_2_score'] or 0,
                            key=f"match_{match['id']}_set1_team2"
                        )
                    
                    # Second set with better spacing
                    st.markdown("<p style='font-weight:bold; margin-top:10px;'>Set 2</p>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        set2_team1 = st.number_input(
                            "Team 1", 
                            min_value=0, 
                            max_value=30, 
                            value=match['set_2_side_1_score'] or 0,
                            key=f"match_{match['id']}_set2_team1"
                        )
                    with col2:
                        set2_team2 = st.number_input(
                            "Team 2", 
                            min_value=0, 
                            max_value=30, 
                            value=match['set_2_side_2_score'] or 0,
                            key=f"match_{match['id']}_set2_team2"
                        )
                    
                    # Third set (optional) with better spacing
                    st.markdown("<p style='font-weight:bold; margin-top:10px;'>Set 3 (if needed)</p>", unsafe_allow_html=True)
                    col1, col2 = st.columns(2)
                    with col1:
                        set3_team1 = st.number_input(
                            "Team 1", 
                            min_value=0, 
                            max_value=30, 
                            value=match['set_3_side_1_score'] or 0,
                            key=f"match_{match['id']}_set3_team1"
                        )
                    with col2:
                        set3_team2 = st.number_input(
                            "Team 2", 
                            min_value=0, 
                            max_value=30, 
                            value=match['set_3_side_2_score'] or 0,
                            key=f"match_{match['id']}_set3_team2"
                        )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Save score button with better visibility
                    if st.button("Save Score", key=f"save_score_{match['id']}", use_container_width=True, type="primary"):
                        # First save the score
                        queries.update_match_score(
                            match['id'],
                            set1_team1, set1_team2,
                            set2_team1, set2_team2,
                            set3_team1, set3_team2
                        )
                        
                        # Check if a winner can be determined for ELO updates
                        sets_team1 = 0
                        sets_team2 = 0
                        
                        # Count sets won by each team
                        if set1_team1 > set1_team2:
                            sets_team1 += 1
                        elif set1_team2 > set1_team1:
                            sets_team2 += 1
                            
                        if set2_team1 > set2_team2:
                            sets_team1 += 1
                        elif set2_team2 > set2_team1:
                            sets_team2 += 1
                            
                        if set3_team1 > set3_team2:
                            sets_team1 += 1
                        elif set3_team2 > set3_team1:
                            sets_team2 += 1
                        
                        # Check if a team has won
                        if sets_team1 > sets_team2 or sets_team2 > sets_team1:
                            # Ask if ELO should be updated
                            update_elo = st.checkbox("Update ELO ratings?", value=True, key=f"update_elo_{match['id']}")
                            
                            if update_elo:
                                try:
                                    # Get ELO ratings of all players
                                    player_elos = {}
                                    for player_id in [match['side_1_user_1_id'], match['side_1_user_2_id'], 
                                                    match['side_2_user_1_id'], match['side_2_user_2_id']]:
                                        if player_id is not None:
                                            player_elos[player_id] = 1500.0  # Default
                                    
                                    # Get actual ELO ratings from database
                                    for elo_data in queries.get_all_elos():
                                        if elo_data['user_id'] in player_elos:
                                            player_elos[elo_data['user_id']] = elo_data['elo']
                                    
                                    # Determine team ratings and result
                                    team1_won = sets_team1 > sets_team2
                                    
                                    # Prepare ratings for ELO calculation
                                    from utils.elo import update_doubles_elo
                                    
                                    team1_ratings = []
                                    team2_ratings = []
                                    
                                    # Add player ELO ratings to their teams
                                    if match['side_1_user_1_id'] is not None:
                                        team1_ratings.append(player_elos[match['side_1_user_1_id']])
                                    if match['side_1_user_2_id'] is not None:
                                        team1_ratings.append(player_elos[match['side_1_user_2_id']])
                                    if match['side_2_user_1_id'] is not None:
                                        team2_ratings.append(player_elos[match['side_2_user_1_id']])
                                    if match['side_2_user_2_id'] is not None:
                                        team2_ratings.append(player_elos[match['side_2_user_2_id']])
                                    
                                    # Calculate new ratings
                                    if len(team1_ratings) > 0 and len(team2_ratings) > 0:
                                        new_team1_ratings, new_team2_ratings = update_doubles_elo(
                                            tuple(team1_ratings), tuple(team2_ratings), team1_won
                                        )
                                        
                                        # Update ELO ratings in database
                                        match_result = f"Match #{match['id']}: {'Victory' if team1_won else 'Defeat'} ({sets_team1}-{sets_team2})"
                                        
                                        idx = 0
                                        if match['side_1_user_1_id'] is not None and idx < len(new_team1_ratings):
                                            queries.update_elo(match['side_1_user_1_id'], new_team1_ratings[idx], match_result)
                                            idx += 1
                                        idx = 0
                                        if match['side_1_user_2_id'] is not None and idx < len(new_team1_ratings):
                                            queries.update_elo(match['side_1_user_2_id'], new_team1_ratings[idx], match_result)
                                            idx += 1
                                        
                                        idx = 0
                                        if match['side_2_user_1_id'] is not None and idx < len(new_team2_ratings):
                                            queries.update_elo(match['side_2_user_1_id'], new_team2_ratings[idx], match_result)
                                            idx += 1
                                        idx = 0
                                        if match['side_2_user_2_id'] is not None and idx < len(new_team2_ratings):
                                            queries.update_elo(match['side_2_user_2_id'], new_team2_ratings[idx], match_result)
                                            idx += 1
                                        
                                        st.success("ELO ratings updated successfully!")
                                except Exception as e:
                                    st.error(f"Error updating ELO ratings: {str(e)}")
                        
                        st.success("Score updated successfully!")
                    
                        # Return players to available pool button
                        if st.button("Return Players to Available Pool", key=f"return_players_{match['id']}", use_container_width=True):
                            # Get all players in this match
                            match_players = queries.get_match_players(match['id'])
                            # Add them back to available pool
                            queries.add_players_to_available(match_players)
                            st.success("Players returned to available pool!")
                            st.rerun()
            
            # Display completed matches
            if completed_matches:
                st.markdown("### ✅ Completed Matches")
                for match in completed_matches:
                    # Calculate sets won to determine the result
                    sets_team1 = 0
                    sets_team2 = 0
                    
                    # Count sets won by each team
                    if match['set_1_side_1_score'] > match['set_1_side_2_score']:
                        sets_team1 += 1
                    elif match['set_1_side_2_score'] > match['set_1_side_1_score']:
                        sets_team2 += 1
                        
                    if match['set_2_side_1_score'] and match['set_2_side_2_score']:
                        if match['set_2_side_1_score'] > match['set_2_side_2_score']:
                            sets_team1 += 1
                        elif match['set_2_side_2_score'] > match['set_2_side_1_score']:
                            sets_team2 += 1
                            
                    if match['set_3_side_1_score'] and match['set_3_side_2_score']:
                        if match['set_3_side_1_score'] > match['set_3_side_2_score']:
                            sets_team1 += 1
                        elif match['set_3_side_2_score'] > match['set_3_side_1_score']:
                            sets_team2 += 1
                    
                    winner = "Team 1" if sets_team1 > sets_team2 else "Team 2" if sets_team2 > sets_team1 else "Draw"
                    result_str = f"{sets_team1}-{sets_team2}"
                    
                    # Use a visual indicator for match status and result
                    status_color = "#4CAF50"  # Green for completed
                    
                    with st.expander(f"Match #{match['id']} - {winner} won {result_str}", expanded=False):
                        # Determine if it's singles or doubles
                        is_singles = (match['side_1_user_2_id'] is None and match['side_2_user_2_id'] is None)
                        match_type_str = "Singles" if is_singles else "Doubles"
                        
                        # Display match details with improved styling
                        st.markdown(f"**{match_type_str} Match**")
                        
                        # Team information with better visual formatting
                        st.markdown("<div style='background-color: #f8f9fa; padding: 10px; border-radius: 10px; margin-bottom: 10px;'>", unsafe_allow_html=True)
                        
                        # Team 1 with win/loss indicator
                        team1_color = "#4CAF50" if sets_team1 > sets_team2 else "#000000"
                        st.markdown(f"**Team 1:** <span style='color:{team1_color};'>{sets_team1 > sets_team2 and '🏆' or ''}</span>", unsafe_allow_html=True)
                        team1_str = f"• {match['side_1_user_1_display_name']}"
                        if not is_singles and match['side_1_user_2_display_name']:
                            team1_str += f" + {match['side_1_user_2_display_name']}"
                        st.markdown(team1_str)
                        
                        # Team 2 with win/loss indicator
                        team2_color = "#4CAF50" if sets_team2 > sets_team1 else "#000000"
                        st.markdown(f"**Team 2:** <span style='color:{team2_color};'>{sets_team2 > sets_team1 and '🏆' or ''}</span>", unsafe_allow_html=True)
                        team2_str = f"• {match['side_2_user_1_display_name']}"
                        if not is_singles and match['side_2_user_2_display_name']:
                            team2_str += f" + {match['side_2_user_2_display_name']}"
                        st.markdown(team2_str)
                        
                        # Close the team info div
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Display scores in a readable format
                        st.markdown("<div style='background-color: #f0f0f0; padding: 15px; border-radius: 10px;'>", unsafe_allow_html=True)
                        st.markdown("<p style='font-weight:bold;'>Match Result</p>", unsafe_allow_html=True)
                        
                        # Create a simple score table
                        st.markdown(f"""
                        <table style='width:100%; border-collapse: collapse;'>
                            <tr>
                                <th style='text-align:left; padding:8px;'>Set</th>
                                <th style='text-align:center; padding:8px;'>Team 1</th>
                                <th style='text-align:center; padding:8px;'>Team 2</th>
                            </tr>
                            <tr>
                                <td style='text-align:left; padding:8px;'>Set 1</td>
                                <td style='text-align:center; padding:8px;'>{match['set_1_side_1_score']}</td>
                                <td style='text-align:center; padding:8px;'>{match['set_1_side_2_score']}</td>
                            </tr>
                            <tr>
                                <td style='text-align:left; padding:8px;'>Set 2</td>
                                <td style='text-align:center; padding:8px;'>{match['set_2_side_1_score'] or '-'}</td>
                                <td style='text-align:center; padding:8px;'>{match['set_2_side_2_score'] or '-'}</td>
                            </tr>
                            <tr>
                                <td style='text-align:left; padding:8px;'>Set 3</td>
                                <td style='text-align:center; padding:8px;'>{match['set_3_side_1_score'] or '-'}</td>
                                <td style='text-align:center; padding:8px;'>{match['set_3_side_2_score'] or '-'}</td>
                            </tr>
                        </table>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Return players to available pool button with better visibility
                        if st.button("Return Players to Available Pool", key=f"return_players_{match['id']}", use_container_width=True):
                            # Get all players in this match
                            match_players = queries.get_match_players(match['id'])
                            # Add them back to available pool
                            queries.add_players_to_available(match_players)
                            st.success("Players returned to available pool!")
                            st.rerun()
