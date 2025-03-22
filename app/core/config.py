#app/core/config.py
from pydantic import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "ZERO2ONE"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite:///./zero2one.db"
    
    # Game settings
    POINTS_PER_RANK: int = 85
    STREAK_REQUIREMENT: int = 8
    DAILY_POINTS: int = 1
    WEEKLY_POINTS: int = 2
    
    # Rank thresholds
    RANK_THRESHOLDS = {
        "E": 0,
        "D": 85,
        "C": 170,
        "B": 255,
        "A": 340,
        "S": 425,
        "SS": 510,
        "SSS": 595
    }
    
    # UI Settings
    THEME_COLOR: str = "#8B5CF6"
    BACKGROUND_COLOR: str = "#1a1a1a"
    CARD_COLOR: str = "#2d2d2d"
    
    class Config:
        case_sensitive = True

settings = Settings()