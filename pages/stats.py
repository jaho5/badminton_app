"""
Player statistics and rankings page.
"""
import streamlit as st
import pandas as pd
import altair as alt
from typing import List, Dict, Any

from db import queries

def render_stats():
    """Render the player statistics page."""
    st.title("Player Statistics")
    
    # Get all players with their Elo ratings
    elo_data = queries.get_all_elos()
    
    if not elo_data:
        st.info("No Elo data available yet.")
        return
    
    # Create a dataframe for the Elo ratings
    df_elo = pd.DataFrame(elo_data)
    
    # Display overall rankings
    st.header("Player Rankings")
    
    # Create a dataframe with the columns we want to display
    display_df = df_elo[['display_name', 'elo']].copy()
    display_df = display_df.sort_values('elo', ascending=False)
    display_df = display_df.reset_index(drop=True)
    display_df.index = display_df.index + 1  # Start from 1 instead of 0
    display_df.columns = ['Player', 'ELO Rating']
    display_df['ELO Rating'] = display_df['ELO Rating'].round(1)
    
    # Display the rankings table
    st.dataframe(
        display_df, 
        use_container_width=True,
        hide_index=False,
        column_config={
            "Player": st.column_config.TextColumn("Player"),
            "ELO Rating": st.column_config.NumberColumn("ELO Rating", format="%.1f")
        }
    )
    
    # Visualization section
    st.header("ELO Rating Visualization")
    
    # Get top N players for visualization
    top_n = st.slider("Number of top players to display", min_value=5, max_value=len(df_elo), value=min(10, len(df_elo)))
    
    # Create dataframe for visualization
    top_players = display_df.head(top_n).copy()
    
    # Create horizontal bar chart
    chart = alt.Chart(top_players.reset_index()).mark_bar().encode(
        x=alt.X('ELO Rating:Q', title='ELO Rating'),
        y=alt.Y('Player:N', sort='-x', title='Player'),
        color=alt.Color('ELO Rating:Q', scale=alt.Scale(scheme='blues'), legend=None),
        tooltip=['Player', 'ELO Rating']
    ).properties(
        title=f'Top {top_n} Players by ELO Rating',
        height=top_n * 40  # Adjust height based on number of players
    )
    
    st.altair_chart(chart, use_container_width=True)
    
    # Match Statistics section (if we implement match history)
    st.header("Match Statistics")
    
    # Get all matches
    matches = queries.get_all_matches()
    
    if not matches:
        st.info("No matches recorded yet.")
        return
    
    # Display basic match statistics
    st.metric("Total Matches Played", len(matches))
    
    # Filter matches that have scores
    completed_matches = [m for m in matches if m['set_1_side_1_score'] is not None and m['set_1_side_2_score'] is not None]
    
    if completed_matches:
        st.metric("Completed Matches", len(completed_matches))
        
        # Create a dataframe of match results
        match_data = []
        for match in completed_matches:
            # Determine winner based on sets won
            team1_sets = 0
            team2_sets = 0
            
            # Count sets won
            if match['set_1_side_1_score'] > match['set_1_side_2_score']:
                team1_sets += 1
            elif match['set_1_side_1_score'] < match['set_1_side_2_score']:
                team2_sets += 1
                
            if match['set_2_side_1_score'] is not None and match['set_2_side_2_score'] is not None:
                if match['set_2_side_1_score'] > match['set_2_side_2_score']:
                    team1_sets += 1
                elif match['set_2_side_1_score'] < match['set_2_side_2_score']:
                    team2_sets += 1
                    
            if match['set_3_side_1_score'] is not None and match['set_3_side_2_score'] is not None:
                if match['set_3_side_1_score'] > match['set_3_side_2_score']:
                    team1_sets += 1
                elif match['set_3_side_1_score'] < match['set_3_side_2_score']:
                    team2_sets += 1
            
            # Format team names
            team1_name = match['side_1_user_1_display_name']
            if match['side_1_user_2_display_name']:
                team1_name += f" & {match['side_1_user_2_display_name']}"
                
            team2_name = match['side_2_user_1_display_name']
            if match['side_2_user_2_display_name']:
                team2_name += f" & {match['side_2_user_2_display_name']}"
            
            # Add match result
            match_data.append({
                'Match ID': match['id'],
                'Team 1': team1_name,
                'Team 2': team2_name,
                'Team 1 Sets': team1_sets,
                'Team 2 Sets': team2_sets,
                'Winner': 'Team 1' if team1_sets > team2_sets else 'Team 2' if team2_sets > team1_sets else 'Draw'
            })
        
        # Convert to dataframe
        df_matches = pd.DataFrame(match_data)
        
        # Display recent matches
        st.subheader("Recent Match Results")
        st.dataframe(
            df_matches[['Match ID', 'Team 1', 'Team 2', 'Team 1 Sets', 'Team 2 Sets', 'Winner']].head(5),
            use_container_width=True
        )
