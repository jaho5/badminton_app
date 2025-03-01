"""
Elo rating calculation utilities.
"""
import math
from typing import Tuple, List

# Constants for Elo calculation
K_FACTOR = 32  # Standard K-factor for Elo calculations
BASE_RATING = 1500  # Default starting rating for new players

def calculate_elo_change(player_rating: float, opponent_rating: float, result: float) -> float:
    """
    Calculate the change in Elo rating for a player.
    
    Args:
        player_rating: Current Elo rating of the player
        opponent_rating: Current Elo rating of the opponent
        result: 1 for win, 0.5 for draw, 0 for loss
    
    Returns:
        The change in Elo rating (positive or negative)
    """
    expected_score = 1 / (1 + math.pow(10, (opponent_rating - player_rating) / 400))
    elo_change = K_FACTOR * (result - expected_score)
    return elo_change

def update_doubles_elo(team1_ratings: Tuple[float, float], 
                      team2_ratings: Tuple[float, float], 
                      team1_won: bool) -> Tuple[List[float], List[float]]:
    """
    Update Elo ratings for players in a doubles match.
    
    Args:
        team1_ratings: Tuple of (player1_rating, player2_rating) for team 1
        team2_ratings: Tuple of (player1_rating, player2_rating) for team 2
        team1_won: True if team 1 won, False if team 2 won
    
    Returns:
        Tuple of (new_team1_ratings, new_team2_ratings)
    """
    # Calculate average team ratings
    team1_avg = sum(team1_ratings) / len(team1_ratings)
    team2_avg = sum(team2_ratings) / len(team2_ratings)
    
    # Determine result
    result = 1 if team1_won else 0
    
    # Calculate Elo changes for each player
    team1_new_ratings = []
    team2_new_ratings = []
    
    for rating in team1_ratings:
        elo_change = calculate_elo_change(rating, team2_avg, result)
        team1_new_ratings.append(rating + elo_change)
    
    for rating in team2_ratings:
        elo_change = calculate_elo_change(rating, team1_avg, 1 - result)
        team2_new_ratings.append(rating + elo_change)
    
    return (team1_new_ratings, team2_new_ratings)

def calculate_win_probability(team1_ratings: Tuple[float, float], 
                             team2_ratings: Tuple[float, float]) -> float:
    """
    Calculate the probability of team1 winning against team2.
    
    Args:
        team1_ratings: Tuple of (player1_rating, player2_rating) for team 1
        team2_ratings: Tuple of (player1_rating, player2_rating) for team 2
    
    Returns:
        Probability of team1 winning (0 to 1)
    """
    team1_avg = sum(team1_ratings) / len(team1_ratings)
    team2_avg = sum(team2_ratings) / len(team2_ratings)
    
    # Use the Elo formula to calculate win probability
    win_probability = 1 / (1 + math.pow(10, (team2_avg - team1_avg) / 400))
    return win_probability
