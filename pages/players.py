"""
Player management page.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any

from db import queries
from db.models import User

def render_players():
    """Render the player management page."""
    st.title("Player Management")
    
    # Create tabs for adding individual players vs. bulk import
    add_tab1, add_tab2 = st.tabs(["Add Individual Player", "Bulk Import"])
    
    with add_tab1:
        # Individual player form
        with st.form("add_player_form"):
            display_name = st.text_input("Display Name", help="The name shown in the app")
            col1, col2 = st.columns(2)
            with col1:
                first_name = st.text_input("First Name (Optional)")
            with col2:
                last_name = st.text_input("Last Name (Optional)")
            
            elo = st.number_input("Initial ELO Rating", value=1500.0, step=10.0, help="Initial ELO rating for the player")
            
            submitted = st.form_submit_button("Add Player")
            if submitted:
                if not display_name:
                    st.error("Display Name is required")
                else:
                    # Create new user
                    user = User(
                        display_name=display_name,
                        first_name=first_name if first_name else None,
                        last_name=last_name if last_name else None
                    )
                    
                    try:
                        # Save user to database
                        user_id = queries.create_user(user)
                        
                        # Set initial ELO rating
                        queries.update_elo(user_id, elo, "Initial player setup")
                        
                        st.success(f"Player '{display_name}' added successfully!")
                    except Exception as e:
                        st.error(f"Error adding player: {str(e)}")
    
    with add_tab2:
        # Bulk import section
        st.subheader("Import Players from CSV")
        
        # Template download
        st.markdown("""
        ### CSV Format
        Your CSV file should have the following columns:
        - `display_name` (required)
        - `first_name` (optional)
        - `last_name` (optional)
        - `elo` (optional, defaults to 1500)
        """)
        
        # Example CSV content
        example_csv = """display_name,first_name,last_name,elo
John Doe,John,Doe,1550
Jane Smith,Jane,Smith,1600
Mike Johnson,Mike,Johnson,1450"""
        
        # Download button for template
        st.download_button(
            label="Download CSV Template",
            data=example_csv,
            file_name="players_template.csv",
            mime="text/csv"
        )
        
        # File uploader
        uploaded_file = st.file_uploader("Upload Players CSV", type=["csv"])
        
        if uploaded_file is not None:
            try:
                # Read CSV file
                df = pd.read_csv(uploaded_file)
                
                # Display preview
                st.write("Preview:")
                st.dataframe(df.head())
                
                if st.button("Import Players", type="primary"):
                    success_count = 0
                    error_count = 0
                    
                    # Process each row
                    for _, row in df.iterrows():
                        try:
                            # Validate required field
                            if 'display_name' not in row or pd.isna(row['display_name']) or row['display_name'] == '':
                                error_count += 1
                                continue
                                
                            # Create user object
                            user = User(
                                display_name=row['display_name'],
                                first_name=row.get('first_name') if 'first_name' in row and not pd.isna(row['first_name']) else None,
                                last_name=row.get('last_name') if 'last_name' in row and not pd.isna(row['last_name']) else None
                            )
                            
                            # Add user to database
                            user_id = queries.create_user(user)
                            
                            # Set ELO if provided
                            elo_value = 1500.0  # Default
                            if 'elo' in row and not pd.isna(row['elo']):
                                try:
                                    elo_value = float(row['elo'])
                                except ValueError:
                                    pass  # Use default if conversion fails
                            
                            queries.update_elo(user_id, elo_value, "Bulk import - initial setup")
                            
                            success_count += 1
                        except Exception as e:
                            error_count += 1
                            st.error(f"Error importing row {_+1}: {str(e)}")
                    
                    # Show results
                    if success_count > 0:
                        st.success(f"Successfully imported {success_count} players!")
                    if error_count > 0:
                        st.warning(f"Failed to import {error_count} players. Check the format and try again.")
                    
                    if success_count > 0:
                        st.rerun()
            except Exception as e:
                st.error(f"Error processing CSV file: {str(e)}")
    
    # Player list
    st.header("Existing Players")
    players = queries.get_all_users()
    
    # Add search functionality
    search_query = st.text_input("Search Players", placeholder="Enter name to search...")
    if search_query:
        # Filter players based on search query (case-insensitive)
        search_query = search_query.lower()
        players = [p for p in players if search_query in p['display_name'].lower() or 
                  (p['first_name'] and search_query in p['first_name'].lower()) or 
                  (p['last_name'] and search_query in p['last_name'].lower())]
    
    if not players:
        st.info("No players have been added yet.")
    else:
        # Get ELO ratings for all players
        elo_data = {player['user_id']: player['elo'] for player in queries.get_all_elos()}
        
        # Create tabs for different views
        tab1, tab2 = st.tabs(["View Players", "Edit Players"])
        
        with tab1:
            # Create a dataframe-like display with multiselect functionality
            # Add bulk delete option
            bulk_delete_enabled = st.checkbox("Enable Bulk Delete")
            selected_players = []
            
            if bulk_delete_enabled:
                cols = st.columns([0.5, 3, 2, 2, 1.5])
                cols[0].markdown("**Select**")
                cols[1].markdown("**Display Name**")
                cols[2].markdown("**First Name**")
                cols[3].markdown("**Last Name**")
                cols[4].markdown("**ELO Rating**")
                
                st.markdown("---")
                
                # Display each player with checkbox
                for player in sorted(players, key=lambda p: p['display_name']):
                    cols = st.columns([0.5, 3, 2, 2, 1.5])
                    is_selected = cols[0].checkbox("", key=f"select_{player['id']}")
                    if is_selected:
                        selected_players.append(player['id'])
                    cols[1].text(player['display_name'])
                    cols[2].text(player['first_name'] or "")
                    cols[3].text(player['last_name'] or "")
                    cols[4].text(f"{elo_data.get(player['id'], 1500.0):.1f}")
                
                # Add bulk delete button
                if selected_players:
                    if st.button(f"Delete Selected Players ({len(selected_players)})", type="primary"):
                        st.warning("Are you sure you want to delete these players? This cannot be undone.")
                        if st.button("Yes, Delete Selected", type="primary"):
                            for player_id in selected_players:
                                try:
                                    queries.delete_user(player_id)
                                except Exception as e:
                                    st.error(f"Error deleting player ID {player_id}: {str(e)}")
                            st.success(f"Successfully deleted {len(selected_players)} players!")
                            st.rerun()
            else:
                cols = st.columns([3, 2, 2, 1.5])
                cols[0].markdown("**Display Name**")
                cols[1].markdown("**First Name**")
                cols[2].markdown("**Last Name**")
                cols[3].markdown("**ELO Rating**")
                
                st.markdown("---")
                
                # Display each player
                for player in sorted(players, key=lambda p: p['display_name']):
                    cols = st.columns([3, 2, 2, 1.5])
                    cols[0].text(player['display_name'])
                    cols[1].text(player['first_name'] or "")
                    cols[2].text(player['last_name'] or "")
                    cols[3].text(f"{elo_data.get(player['id'], 1500.0):.1f}")
        
        with tab2:
            # Create an edit/delete interface
            for player in sorted(players, key=lambda p: p['display_name']):
                with st.expander(f"{player['display_name']} (ELO: {elo_data.get(player['id'], 1500.0):.1f})"):
                    with st.form(key=f"edit_player_{player['id']}"):
                        # Edit fields
                        display_name = st.text_input("Display Name", value=player['display_name'], key=f"display_{player['id']}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            first_name = st.text_input("First Name", value=player['first_name'] or "", key=f"first_{player['id']}")
                        with col2:
                            last_name = st.text_input("Last Name", value=player['last_name'] or "", key=f"last_{player['id']}")
                        
                        # ELO rating field
                        current_elo = elo_data.get(player['id'], 1500.0)
                        elo = st.number_input("ELO Rating", value=float(current_elo), step=10.0, key=f"elo_{player['id']}")
                        
                        # Form buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            submit = st.form_submit_button("Update Player")
                        with col2:
                            delete = st.form_submit_button("Delete Player", type="secondary")
                        
                        if submit:
                            if not display_name:
                                st.error("Display Name is required")
                            else:
                                # Update user information
                                updated_user = User(
                                    id=player['id'],
                                    display_name=display_name,
                                    first_name=first_name if first_name else None,
                                    last_name=last_name if last_name else None
                                )
                                
                                try:
                                    # Update user info
                                    queries.update_user(updated_user)
                                    
                                    # Update ELO if changed
                                    if elo != current_elo:
                                        queries.update_elo(
                                            player['id'], 
                                            elo, 
                                            f"Manual adjustment from {current_elo:.1f} to {elo:.1f}"
                                        )
                                    
                                    st.success(f"Player '{display_name}' updated successfully!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error updating player: {str(e)}")
                        
                        if delete:
                            # Create a confirmation dialog
                            st.warning(f"Are you sure you want to delete '{player['display_name']}'? This cannot be undone.")
                            confirm_col1, confirm_col2 = st.columns(2)
                            with confirm_col1:
                                if st.button("Yes, Delete", key=f"confirm_delete_{player['id']}", type="primary"):
                                    try:
                                        queries.delete_user(player['id'])
                                        st.success(f"Player '{player['display_name']}' deleted successfully!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error deleting player: {str(e)}")
                            with confirm_col2:
                                st.button("Cancel", key=f"cancel_delete_{player['id']}", type="secondary")
