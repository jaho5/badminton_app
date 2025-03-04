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
from pages.players import render_players

# Set page configuration
st.set_page_config(
    page_title="Badminton Club Manager",
    page_icon="🏸",
    layout="wide",
    initial_sidebar_state="auto"
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
    
    /* Mobile-friendly styles */
    @media screen and (max-width: 640px) {
        .main .block-container {
            padding: 1rem 0.5rem;
        }
        
        /* Make columns stack on mobile */
        .row-widget.stHorizontal {
            flex-direction: column;
        }
        
        /* Larger touch targets for buttons */
        button {
            min-height: 44px !important;
            margin: 5px 0 !important;
        }
        
        /* Improve spacing for touch interfaces */
        .stRadio > div, .stCheckbox > div {
            margin-bottom: 12px;
        }
        
        /* Bottom navigation for mobile */
        .mobile-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
            padding: 10px 5px;
            display: none; /* Will be shown via JavaScript */
            z-index: 1000;
        }
        
        /* Better player cards */
        .player-card {
            padding: 12px 8px !important;
            border-radius: 10px !important;
            margin: 8px 0 !important;
            transition: all 0.2s;
        }
        
        /* Larger form elements */
        .stNumberInput, .stTextInput, .stSelectbox {
            min-height: 44px;
        }
    }
</style>

<script>
// JavaScript to detect mobile and show alternative navigation
document.addEventListener('DOMContentLoaded', function() {
    if (window.innerWidth <= 640) {
        // Show mobile navigation
        var mobileNav = document.querySelector('.mobile-nav');
        if (mobileNav) mobileNav.style.display = 'flex';
        
        // Potentially collapse sidebar
        var sidebarToggle = document.querySelector('button[data-testid="baseButton-header"]');
        if (sidebarToggle) sidebarToggle.click();
    }
});
</script>
""", unsafe_allow_html=True)

# Sidebar for navigation
with st.sidebar:
    st.title("🏸 Badminton Club")
    
    # Navigation
    st.subheader("Navigation")
    
    if st.button("Available Players", use_container_width=True, 
                type="primary" if st.session_state.page == 'available' else "secondary"):
        st.session_state.page = 'available'
        st.rerun()
        
    if st.button("Matches", use_container_width=True,
                type="primary" if st.session_state.page == 'matches' else "secondary"):
        st.session_state.page = 'matches'
        st.rerun()
        
    if st.button("Player Stats", use_container_width=True,
                type="primary" if st.session_state.page == 'stats' else "secondary"):
        st.session_state.page = 'stats'
        st.rerun()
        
    if st.button("Player Management", use_container_width=True,
                type="primary" if st.session_state.page == 'players' else "secondary"):
        st.session_state.page = 'players'
        st.rerun()
    
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
elif st.session_state.page == 'players':
    render_players()

