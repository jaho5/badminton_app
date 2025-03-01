"""
Database models and schemas for the badminton app.
"""
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: Optional[int] = None
    display_name: str = ""
    first_name: Optional[str] = None
    last_name: Optional[str] = None

@dataclass
class Match:
    id: Optional[int] = None
    side_1_user_1_id: int = 0
    side_1_user_2_id: Optional[int] = None
    side_2_user_1_id: int = 0
    side_2_user_2_id: Optional[int] = None
    set_1_side_1_score: Optional[int] = None
    set_1_side_2_score: Optional[int] = None
    set_2_side_1_score: Optional[int] = None
    set_2_side_2_score: Optional[int] = None
    set_3_side_1_score: Optional[int] = None
    set_3_side_2_score: Optional[int] = None
    on_court: Optional[int] = None
    # Additional fields for UI display
    side_1_user_1_display_name: Optional[str] = None
    side_1_user_2_display_name: Optional[str] = None
    side_2_user_1_display_name: Optional[str] = None
    side_2_user_2_display_name: Optional[str] = None

@dataclass
class Available:
    id: Optional[int] = None
    user_id: int = 0

@dataclass
class Elo:
    id: Optional[int] = None
    user_id: int = 0
    elo: float = 0
    # Additional fields for UI display
    display_name: Optional[str] = None
