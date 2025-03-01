"""
Player statistics and rankings page.
"""
import streamlit as st
import pandas as pd
import altair as alt
from typing import List, Dict, Any
from datetime import datetime

from db import queries

def render_stats():
    """Render the player statistics page."""
    st.title("Player Statistics")
    
    # Create tabs for different stats views
    tab1, tab2 = st.tabs(["Player Rankings", "ELO History"])
    
    with tab1:
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
        top_n = st.slider("Number of top players to display", min_value=1, max_value=len(df_elo), value=min(10, len(df_elo)))
        
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
    
    with tab2:
        st.header("Player ELO History")
        
        # Get all players for selection
        all_players = queries.get_all_users()
        elo_data = {player['id']: player.get('elo', 1500.0) for player in queries.get_all_elos()}
        
        if not all_players:
            st.info("No players available yet.")
            return
        
        # Create a selection dropdown for players
        player_names = {p['id']: f"{p['display_name']} (ELO: {elo_data.get(p['id'], 1500.0):.1f})" for p in all_players}
        player_options = list(player_names.items())
        
        selected_player_id = st.selectbox(
            "Select Player",
            options=[p[0] for p in player_options],
            format_func=lambda x: player_names[x],
            help="Select a player to view their ELO history"
        )
        
        if selected_player_id:
            # Get the player's ELO history
            elo_history = queries.get_player_elo_history(selected_player_id)
            
            if not elo_history:
                st.info(f"No ELO history available for this player. History is tracked after each ELO change.")
            else:
                # Create dataframe for display and visualization
                df_history = pd.DataFrame(elo_history)
                
                # Add a change column to show the difference
                df_history['change'] = df_history.apply(
                    lambda row: (row['new_elo'] - row['old_elo']) if row['old_elo'] is not None else 0, 
                    axis=1
                )
                
                # Format timestamps
                df_history['formatted_time'] = pd.to_datetime(df_history['timestamp']).dt.strftime('%Y-%m-%d %H:%M')
                
                # Display history table
                st.subheader("ELO Rating History")
                
                # Format the dataframe for display
                display_history = df_history[['formatted_time', 'old_elo', 'new_elo', 'change', 'change_reason']].copy()
                display_history.columns = ['Date', 'Previous ELO', 'New ELO', 'Change', 'Reason']
                
                # Convert numeric columns to float for proper formatting
                for col in ['Previous ELO', 'New ELO', 'Change']:
                    display_history[col] = pd.to_numeric(display_history[col], errors='coerce')
                
                # Add colored background for change column
                st.dataframe(
                    display_history,
                    use_container_width=True,
                    column_config={
                        "Date": st.column_config.TextColumn("Date"),
                        "Previous ELO": st.column_config.NumberColumn("Previous ELO", format="%.1f"),
                        "New ELO": st.column_config.NumberColumn("New ELO", format="%.1f"),
                        "Change": st.column_config.NumberColumn("Change", format="%+.1f"),
                        "Reason": st.column_config.TextColumn("Reason")
                    }
                )
                
                # Create a visualization of ELO over time
                if len(df_history) > 1:
                    st.subheader("ELO Rating Trend")
                    
                    # Create data for visualization with time on the x-axis
                    chart_data = df_history[['timestamp', 'new_elo']].copy()
                    chart_data.columns = ['Time', 'ELO']
                    chart_data['Time'] = pd.to_datetime(chart_data['Time'])
                    chart_data = chart_data.sort_values('Time')
                    
                    # Create the line chart
                    line_chart = alt.Chart(chart_data).mark_line(point=True).encode(
                        x=alt.X('Time:T', title='Date'),
                        y=alt.Y('ELO:Q', title='ELO Rating', scale=alt.Scale(zero=False)),
                        tooltip=['Time:T', 'ELO:Q']
                    ).properties(
                        title=f'ELO Rating Trend for {df_history["display_name"].iloc[0]}',
                        height=300
                    )
                    
                    st.altair_chart(line_chart, use_container_width=True)
