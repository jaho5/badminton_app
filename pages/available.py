"""
Available players management page.
"""
import streamlit as st
from typing import List, Dict, Any

from db import queries

def render_available_players():
    """Render the available players management page."""
    st.title("Available Players")
    
    # Add a floating action button for player management functions
    #with st.expander("Player Management", expanded=False):
    col_save, col_load = st.columns(2)
    with col_save:
        if st.button("Save Current Availability", use_container_width=True):
            queries.save_available_state()
            st.success("Available players saved successfully!")
            st.rerun()
    
    with col_load:
        if st.button("Load Saved Availability", use_container_width=True, 
                    help="Load the previously saved player availability"):
            queries.load_available_state()
            st.success("Available players loaded successfully!")
            st.rerun()

    # Add search filter
    search_term = st.text_input("Search Players", "")
    
    # Fetch all players
    available_players = queries.get_all_availables()
    unavailable_players = queries.get_all_unavailables()
    
    # Filter players based on search term
    if search_term:
        available_players = [p for p in available_players if search_term.lower() in p['display_name'].lower()]
        unavailable_players = [p for p in unavailable_players if search_term.lower() in p['display_name'].lower()]
    
    # Create two columns for available and unavailable players
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Available Players")
        
        # Display available players count
        st.caption(f"{len(available_players)} players available")
        
        # Display available players
        for player in available_players:
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
            cols = player_container.columns([5, 1])
            
            # Display player info with custom styling and class for mobile targeting
            cols[0].markdown(
                f"""
                <div class="player-card" style="background-color: {bgcolor}; padding: 12px; border-radius: 10px; margin: 8px 0; display: flex; align-items: center;">
                    <div style="flex-grow: 1;">
                        <span style="font-weight: bold; font-size: 16px;">{player_name}</span><br>
                        <span style="font-size: 14px; color: #555;">ELO: {elo}</span>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            # Add button to move player to unavailable with more mobile-friendly icon
            if cols[1].button("🔄", key=f"make_unavailable_{player['user_id']}", help="Move to unavailable"):
                queries.toggle_availability(player['user_id'])
                st.rerun()
    
    with col2:
        st.subheader("Unavailable Players")
        
        # Display unavailable players count
        st.caption(f"{len(unavailable_players)} players unavailable")
        
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
            cols = player_container.columns([1, 5])
            
            # Add button to move player to available with more mobile-friendly icon
            if cols[0].button("✅", key=f"make_available_{player['user_id']}", help="Make available"):
                queries.toggle_availability(player['user_id'])
                st.rerun()
            
            # Display player info with custom styling and class for mobile targeting
            cols[1].markdown(
                f"""
                <div class="player-card" style="background-color: {bgcolor}; padding: 12px; border-radius: 10px; margin: 8px 0; display: flex; align-items: center;">
                    <div style="flex-grow: 1;">
                        <span style="font-weight: bold; font-size: 16px;">{player_name}</span><br>
                        <span style="font-size: 14px; color: #555;">ELO: {elo}</span>
                    </div>
                </div>
                """, 
                unsafe_allow_html=True
            )
