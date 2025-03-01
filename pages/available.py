"""
Available players management page.
"""
import streamlit as st
from typing import List, Dict, Any

from db import queries

def render_available_players():
    """Render the available players management page."""
    st.title("Available Players")
    
    # Add Save/Load buttons at the top
    col_save, col_load = st.columns(2)
    with col_save:
        if st.button("Save Current Availability", use_container_width=True):
            queries.save_available_state()
            st.success("Available players saved successfully!")
            st.experimental_rerun()
    
    with col_load:
        if st.button("Load Saved Availability", use_container_width=True, 
                     type="primary", help="Load the previously saved player availability"):
            queries.load_available_state()
            st.success("Available players loaded successfully!")
            st.experimental_rerun()
    
    # Create two columns for available and unavailable players
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Available Players")
        available_players = queries.get_all_availables()
        
        # Display available players
        for player in available_players:
            player_name = player['display_name']
            elo = player.get('elo', 'N/A')
            is_saved = player.get('is_saved', 0) == 1
            
            # Create a container for each player with background color based on saved status
            player_container = st.container()
            
            # Apply styling based on saved status
            if is_saved:
                bgcolor = "#89f0e5"
            else:
                bgcolor = "#f0f0f0"
            
            # Create a horizontal layout for each player
            cols = player_container.columns([4, 1])
            
            # Display player info with custom styling
            cols[0].markdown(
                f"""
                <div style="background-color: {bgcolor}; padding: 8px; border-radius: 5px; margin: 2px 0;">
                    <span style="font-weight: bold;">{player_name}</span> - {elo}
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Add button to move player to unavailable
            if cols[1].button(">", key=f"make_unavailable_{player['user_id']}"):
                queries.toggle_availability(player['user_id'])
                st.experimental_rerun()
    
    with col2:
        st.subheader("Unavailable Players")
        unavailable_players = queries.get_all_unavailables()
        
        # Display unavailable players
        for player in unavailable_players:
            player_name = player['display_name']
            elo = player.get('elo', 'N/A')
            is_saved = player.get('is_saved', 0) == 1
            
            # Create a container for each player
            player_container = st.container()
            
            # Apply styling based on saved status
            if is_saved:
                bgcolor = "#89f0e5"
            else:
                bgcolor = "#f0f0f0"
            
            # Create a horizontal layout for each player
            cols = player_container.columns([1, 4])
            
            # Add button to move player to available
            if cols[0].button("<", key=f"make_available_{player['user_id']}"):
                queries.toggle_availability(player['user_id'])
                st.experimental_rerun()
            
            # Display player info with custom styling
            cols[1].markdown(
                f"""
                <div style="background-color: {bgcolor}; padding: 8px; border-radius: 5px; margin: 2px 0;">
                    <span style="font-weight: bold;">{player_name}</span> - {elo}
                </div>
                """, 
                unsafe_allow_html=True
            )
