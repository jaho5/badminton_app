"""
Main entry point for the Badminton Club Management Streamlit app.
"""
import streamlit as st
import pandas as pd
import csv
import os

# Import database modules
from db.database import setup_database
from db import queries
from db.models import User, Elo

# Import page modules
from pages.available import render_available_players
from pages.matches import render_matches
from pages.stats import render_stats

# Set page configuration
st.set_page_config(
    page_title="Badminton Club Manager",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
setup_database()

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'available'

# CSS for styling
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
    }
    /* Custom styles for the app */
    .saved-player {
        background-color: #89f0e5;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Sidebar for navigation
with st.sidebar:
    st.title("🏸 Badminton Club")
    
    # Navigation
    st.subheader("Navigation")
    
    if st.button("Available Players", use_container_width=True, 
                type="primary" if st.session_state.page == 'available' else "secondary"):
        st.session_state.page = 'available'
#        st.experimental_rerun()
        
    if st.button("Matches", use_container_width=True,
                type="primary" if st.session_state.page == 'matches' else "secondary"):
        st.session_state.page = 'matches'
        #st.experimental_rerun()
        
    if st.button("Player Stats", use_container_width=True,
                type="primary" if st.session_state.page == 'stats' else "secondary"):
        st.session_state.page = 'stats'
        #st.experimental_rerun()
    
    # Admin section
    st.sidebar.markdown("---")
    with st.sidebar.expander("Admin"):
        # Data import form
        st.subheader("Import Player Data")
        
        # User upload for players
        uploaded_users = st.file_uploader("Upload Users CSV", type=["csv"])
        if uploaded_users is not None:
            try:
                # Read the CSV file
                user_data = pd.read_csv(uploaded_users)
                
                if st.button("Import Users"):
                    # Process each row to create a user
                    for _, row in user_data.iterrows():
                        try:
                            user = User(
                                display_name=row.get('display_name', ''),
                                first_name=row.get('first_name', None),
                                last_name=row.get('last_name', None)
                            )
                            queries.create_user(user)
                        except Exception as e:
                            st.error(f"Error importing user {row.get('display_name', '')}: {str(e)}")
                    
                    st.success(f"Successfully imported {len(user_data)} users")
            except Exception as e:
                st.error(f"Error processing user CSV: {str(e)}")
        
        # ELO ratings upload
        uploaded_elos = st.file_uploader("Upload ELO Ratings CSV", type=["csv"])
        if uploaded_elos is not None:
            try:
                # Read the CSV file
                elo_data = pd.read_csv(uploaded_elos)
                
                if st.button("Import ELO Ratings"):
                    # First, get all users to match display names to user IDs
                    users = {user['display_name']: user['id'] for user in queries.get_all_users()}
                    
                    # Process each row to update ELO
                    imported_count = 0
                    for _, row in elo_data.iterrows():
                        try:
                            display_name = row.get('name', '')
                            elo_rating = float(row.get('elo', 1500))
                            
                            if display_name in users:
                                user_id = users[display_name]
                                queries.update_elo(user_id, elo_rating)
                                imported_count += 1
                        except Exception as e:
                            st.error(f"Error importing ELO for {display_name}: {str(e)}")
                    
                    st.success(f"Successfully imported {imported_count} ELO ratings")
            except Exception as e:
                st.error(f"Error processing ELO CSV: {str(e)}")

# Main content based on selected page
if st.session_state.page == 'available':
    render_available_players()
elif st.session_state.page == 'matches':
    render_matches()
elif st.session_state.page == 'stats':
    render_stats()
