from nba_api.stats.static import players
from nba_api.stats.endpoints import (
    playercareerstats,
    playerdashboardbygeneralsplits,
    playerdashboardbyshootingsplits,
    playerdashboardbyclutch,
    playerdashboardbygamesplits,
    playerdashboardbylastngames
)
import pandas as pd

def get_player_career_stats(player_name):
    # Step 1: Get player ID
    player_dict = players.find_players_by_full_name(player_name)
    if not player_dict:
        print(f"Player {player_name} not found.")
        return None
    player_id = player_dict[0]['id']
    
    # Step 2: Fetch career stats
    career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    career_df = career_stats.get_data_frames()[0]

    # Step 3: Select relevant columns
    relevant_columns = [
        "SEASON_ID", "TEAM_ID", "TEAM_ABBREVIATION", "PLAYER_AGE",
        "GP", "GS",  # Games Played, Games Started
        "MIN", "PTS", "REB", "AST", "STL", "BLK",  # Totals
        "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT",  # Shooting
        "OREB", "DREB",  # Rebounds (Offensive and Defensive)
        "PF",  # Personal Fouls
        "PLUS_MINUS", "PFD"  # Plus/Minus, Personal Fouls Drawn
    ]

    # Ensure only existing columns are selected
    available_columns = [col for col in relevant_columns if col in career_df.columns]
    career_df = career_df[available_columns]

    # Step 4: Add per-game stats (handle missing columns gracefully)
    if "GP" in career_df.columns and career_df["GP"].sum() > 0:  # Check GP exists and is valid
        career_df["PTS_PER_GAME"] = round(career_df["PTS"] / career_df["GP"], 2) if "PTS" in career_df else None
        career_df["REB_PER_GAME"] = round(career_df["REB"] / career_df["GP"], 2) if "REB" in career_df else None
        career_df["AST_PER_GAME"] = round(career_df["AST"] / career_df["GP"], 2) if "AST" in career_df else None
        career_df["STL_PER_GAME"] = round(career_df["STL"] / career_df["GP"], 2) if "STL" in career_df else None
        career_df["BLK_PER_GAME"] = round(career_df["BLK"] / career_df["GP"], 2) if "BLK" in career_df else None
        career_df["MIN_PER_GAME"] = round(career_df["MIN"] / career_df["GP"], 2) if "MIN" in career_df else None

    # Shooting Splits
    shooting_splits = playerdashboardbyshootingsplits.PlayerDashboardByShootingSplits(player_id=player_id)
    shooting_splits_df = shooting_splits.get_data_frames()[3]
    finishing_splits_df = shooting_splits.get_data_frames()[5]
    

    return career_df, shooting_splits_df, finishing_splits_df

# Example usage
player_name = input('Enter a player\'s name: ')
overall_df, shooting_df, finishing_df = get_player_career_stats(player_name)

print('\n\n------------------------------------------------------------------------------\n\n')
print(overall_df)
print('\n\n------------------------------------------------------------------------------\n\n')
print(shooting_df)
print('\n\n------------------------------------------------------------------------------\n\n')
print(finishing_df)
print('\n\n------------------------------------------------------------------------------\n\n')