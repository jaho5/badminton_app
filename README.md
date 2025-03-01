# Badminton Club Manager - Streamlit App

This is a Streamlit application for managing a badminton club, including player availability tracking, match creation, and statistics.

## Features

- Track available and unavailable players
- Save and load player availability states
- Create balanced matches based on ELO ratings
- Record match scores
- View player statistics and rankings

## Installation

1. Make sure you have Python 3.8+ installed
2. Install required packages:

```bash
pip install streamlit pandas altair
```

## Running the Application

Navigate to the project directory and run:

```bash
streamlit run app.py
```

## Data Import

The application allows importing player data and ELO ratings using CSV files:

1. **User CSV Format**:
   ```
   display_name,last_name,first_name
   Player1,LastName1,FirstName1
   Player2,LastName2,FirstName2
   ```

2. **ELO Ratings CSV Format**:
   ```
   name,elo
   Player1,1500.0
   Player2,1650.5
   ```

Use the Admin section in the sidebar to upload these files.

## Project Structure

```
badminton_app/
│
├── app.py              # Main Streamlit application entry point
├── db/
│   ├── __init__.py
│   ├── models.py       # Database models and schemas
│   ├── database.py     # Database connection and initialization
│   └── queries.py      # Database operations
│
├── utils/
│   ├── __init__.py
│   ├── elo.py          # ELO calculation utilities
│   └── matching.py     # Player matching algorithms
│
├── pages/
│   ├── __init__.py
│   ├── available.py    # Available players management page
│   ├── matches.py      # Matches management page
│   └── stats.py        # Player statistics page
│
└── data/
    └── puma.db         # SQLite database
```
