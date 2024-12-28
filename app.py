from nba_api.stats.static import players
from nba_api.stats.endpoints import (
    playercareerstats,
    playerdashboardbyshootingsplits,
)
import pandas as pd

def get_player_career_stats(player_name):
    # Step 1: Get player ID
    player_dict = players.find_players_by_full_name(player_name)
    if not player_dict:
        print(f"Player {player_name} not found.")
        return None, None, None
    player_id = player_dict[0]['id']
    
    # Step 2: Fetch career stats
    career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    career_df = career_stats.get_data_frames()[0]

    # Step 3: Select relevant columns
    relevant_columns = [
        "SEASON_ID", "TEAM_ABBREVIATION", "PLAYER_AGE",
        "GP", "GS",  # Games Played, Games Started
        "MIN", "PTS", "REB", "AST", "STL", "BLK",  # Totals
        "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT", "FTM", "FTA", "FT_PCT",  # Shooting
        "OREB", "DREB",  # Rebounds (Offensive and Defensive)
        "PF",  # Personal Fouls
    ]

    # Ensure only existing columns are selected
    available_columns = [col for col in relevant_columns if col in career_df.columns]
    career_df = career_df[available_columns]
    
        # Calculate the all-time row
    team_abbreviations = career_df["TEAM_ABBREVIATION"].dropna().unique().tolist()
    player_age = career_df["PLAYER_AGE"].dropna().tolist()
    all_time = {
        "SEASON_ID": "ALL_TIME",
        "TEAM_ABBREVIATION": team_abbreviations,
        "PLAYER_AGE": [player_age[0], player_age[-1]] if len(player_age) > 1 else player_age,
        "GP": career_df["GP"].sum() if "GP" in career_df else None,
        "GS": career_df["GS"].sum() if "GS" in career_df else None,
        "MIN": career_df["MIN"].sum() if "MIN" in career_df else None,
        "PTS": career_df["PTS"].sum() if "PTS" in career_df else None,
        "REB": career_df["REB"].sum() if "REB" in career_df else None,
        "AST": career_df["AST"].sum() if "AST" in career_df else None,
        "STL": career_df["STL"].sum() if "STL" in career_df else None,
        "BLK": career_df["BLK"].sum() if "BLK" in career_df else None,
        "FGM": career_df["FGM"].sum() if "FGM" in career_df else None,
        "FGA": career_df["FGA"].sum() if "FGA" in career_df else None,
        "FG_PCT": round(career_df["FGM"].sum() / career_df["FGA"].sum(), 3) if "FGM" in career_df and "FGA" in career_df and career_df["FGA"].sum() > 0 else None,
        "FG3M": career_df["FG3M"].sum() if "FG3M" in career_df else None,
        "FG3A": career_df["FG3A"].sum() if "FG3A" in career_df else None,
        "FG3_PCT": round(career_df["FG3M"].sum() / career_df["FG3A"].sum(), 3) if "FG3M" in career_df and "FG3A" in career_df and career_df["FG3A"].sum() > 0 else None,
        "FTM": career_df["FTM"].sum() if "FTM" in career_df else None,
        "FTA": career_df["FTA"].sum() if "FTA" in career_df else None,
        "FT_PCT": round(career_df["FTM"].sum() / career_df["FTA"].sum(), 3) if "FTM" in career_df and "FTA" in career_df and career_df["FTA"].sum() > 0 else None,
        "OREB": career_df["OREB"].sum() if "OREB" in career_df else None,
        "DREB": career_df["DREB"].sum() if "DREB" in career_df else None,
        "PF": career_df["PF"].sum() if "PF" in career_df else None,
    }

    # Convert all_time dictionary to DataFrame row and append it
    all_time_df = pd.DataFrame([all_time])
    career_df = pd.concat([career_df, all_time_df], ignore_index=True)


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
    shooting_splits_df = shooting_splits_df.iloc[0:, 1:15]
    finishing_splits_df = shooting_splits.get_data_frames()[5]
    finishing_splits_df = finishing_splits_df.iloc[0:, 1:]
    

    return career_df, shooting_splits_df, finishing_splits_df

# Example usage
player_name = ""
while player_name != 'finish':
    player_name = input('Enter a player\'s name: ')
    overall_df, shooting_df, finishing_df = get_player_career_stats(player_name)

    print('\n\n------------------------------------------------------------------------------\n\n')
    print(overall_df)
    print('\n\n------------------------------------------------------------------------------\n\n')
    print(shooting_df)
    print('\n\n------------------------------------------------------------------------------\n\n')
    print(finishing_df)
    print('\n\n------------------------------------------------------------------------------\n\n')