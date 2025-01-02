import os
import json
from nba_api.stats.endpoints import playercareerstats, playerdashboardbyshootingsplits
from nba_api.stats.static import players
import pandas as pd

CACHE_FILE = "player_stats_cache.json"

def load_cache():
    if os.path.exists("player_stats_cache.json"):
        with open("player_stats_cache.json", "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open("player_stats_cache.json", "w") as f:
        json.dump(cache, f)

# Load cache globally at the start
player_stats_cache = load_cache()


#------------------------------------------------------------------------------

def get_player_career_stats(player_id):
    if str(player_id) in player_stats_cache:
        print(f"Using cached data for player ID: {player_id}")
        cached_data = player_stats_cache[str(player_id)]
        return (
            pd.DataFrame(cached_data["career"]),
            pd.DataFrame(cached_data["shooting"]),
            pd.DataFrame(cached_data["finishing"]),
        )
    
    print(f"Fetching data from API for player ID: {player_id}")
    # Fetch career stats
    career_stats = playercareerstats.PlayerCareerStats(player_id=player_id)
    career_df = career_stats.get_data_frames()[0]

    # Select relevant columns
    relevant_columns = [
        "SEASON_ID", "TEAM_ABBREVIATION", "PLAYER_AGE",
        "GP", "GS", "MIN", "PTS", "REB", "AST", "STL", "BLK",
        "FGM", "FGA", "FG_PCT", "FG3M", "FG3A", "FG3_PCT",
        "FTM", "FTA", "FT_PCT", "OREB", "DREB", "PF",
    ]
    available_columns = [col for col in relevant_columns if col in career_df.columns]
    career_df = career_df[available_columns]

    # Add all-time stats
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
    all_time_df = pd.DataFrame([all_time])
    career_df = pd.concat([career_df, all_time_df], ignore_index=True)

    # Add per-game stats
    if "GP" in career_df.columns and career_df["GP"].sum() > 0:
        # Basic per-game stats
        career_df["PTS_PER_GAME"] = round(career_df["PTS"] / career_df["GP"], 2) if "PTS" in career_df else None
        career_df["REB_PER_GAME"] = round(career_df["REB"] / career_df["GP"], 2) if "REB" in career_df else None
        career_df["AST_PER_GAME"] = round(career_df["AST"] / career_df["GP"], 2) if "AST" in career_df else None
        career_df["STL_PER_GAME"] = round(career_df["STL"] / career_df["GP"], 2) if "STL" in career_df else None
        career_df["BLK_PER_GAME"] = round(career_df["BLK"] / career_df["GP"], 2) if "BLK" in career_df else None
        career_df["MIN_PER_GAME"] = round(career_df["MIN"] / career_df["GP"], 2) if "MIN" in career_df else None

        # Additional per-game stats
        career_df["OREB_PG"] = round(career_df["OREB"] / career_df["GP"], 2) if "OREB" in career_df else None
        career_df["DREB_PG"] = round(career_df["DREB"] / career_df["GP"], 2) if "DREB" in career_df else None
        career_df["PF_PG"] = round(career_df["PF"] / career_df["GP"], 2) if "PF" in career_df else None
        career_df["FTA_PG"] = round(career_df["FTA"] / career_df["GP"], 2) if "FTA" in career_df else None
        
        # Shooting per-game stats
        career_df["FGA_PG"] = round(career_df["FGA"] / career_df["GP"], 2) if "FGA" in career_df else None
        career_df["FGM_PG"] = round(career_df["FGM"] / career_df["GP"], 2) if "FGM" in career_df else None
        career_df["FG3A_PG"] = round(career_df["FG3A"] / career_df["GP"], 2) if "FG3A" in career_df else None
        career_df["FG3M_PG"] = round(career_df["FG3M"] / career_df["GP"], 2) if "FG3M" in career_df else None

        # Free throw stats
        career_df["FTM_PG"] = round(career_df["FTM"] / career_df["GP"], 2) if "FTM" in career_df else None
        career_df["FT_PCT"] = round(career_df["FTM"] / career_df["FTA"], 3) if "FTM" in career_df and "FTA" in career_df and career_df["FTA"].sum() > 0 else None
        
        # 3-point stats
        career_df["FG3_PCT"] = round(career_df["FG3M"] / career_df["FG3A"], 3) if "FG3M" in career_df and "FG3A" in career_df and career_df["FG3A"].sum() > 0 else None
        
        # Field goal stats
        career_df["FG_PCT"] = round(career_df["FGM"] / career_df["FGA"], 3) if "FGM" in career_df and "FGA" in career_df and career_df["FGA"].sum() > 0 else None



    # Fetch shooting splits
    shooting_splits = playerdashboardbyshootingsplits.PlayerDashboardByShootingSplits(player_id=player_id)
    shooting_splits_df = shooting_splits.get_data_frames()[3]
    shooting_splits_df = shooting_splits_df.iloc[0:, 1:15]
    finishing_splits_df = shooting_splits.get_data_frames()[5]
    finishing_splits_df = finishing_splits_df.iloc[0:, 1:]

    # Prepare data
    data = {
        "career": career_df.to_dict(orient="list"),
        "shooting": shooting_splits_df.to_dict(orient="list"),
        "finishing": finishing_splits_df.to_dict(orient="list")
    }
    player_stats_cache[str(player_id)] = data
    save_cache(player_stats_cache)

    return career_df, shooting_splits_df, finishing_splits_df


def merged_df(o_df, s_df, f_df):
    # Extract the number of games played in the 2024-25 season
    games_played = o_df.iloc[-2]['GP']  # Adjust this column selection based on actual column label in o_df
    
    # Avoid division by zero
    if games_played == 0:
        raise ValueError("Number of games played in the 2024-25 season is zero, division not possible.")
    
    # Normalize columns in s_df
    s_df[['FGM', 'FGA', 'FG_PCT', 'FG3A', 'FG3M']] = s_df[['FGM', 'FGA', 'FG_PCT', 'FG3A', 'FG3M']].div(games_played)
    
    # Normalize columns in f_df
    f_df[['FGM', 'FGA', 'FG_PCT', 'FG3A', 'FG3M']] = f_df[['FGM', 'FGA', 'FG_PCT', 'FG3A', 'FG3M']].div(games_played)

    season_df = o_df.iloc[-2:-1, 23:]
    crop_shots_df = s_df.iloc[0:, 0:7]
    crop_finish_df = f_df.iloc[0:, 0:7]
    
    # Combine shots and finish data
    clustering_df = pd.concat([crop_shots_df, crop_finish_df]).reset_index(drop=True)

    single_row = {}
    for _, row in clustering_df.iterrows():
        group_value = row['GROUP_VALUE'].replace(" ", "_").replace("(", "").replace(")", "")
        for col in clustering_df.columns[1:]:  # Skip 'GROUP_VALUE'
            single_row[f"{col}_{group_value}"] = row[col]
    
    # Include columns from season_df into single_row
    for col in season_df.columns:
        single_row[col] = season_df.iloc[0][col]
    
    # Convert the dictionary to a single-row DataFrame
    single_row_df = pd.DataFrame([single_row])
    
    return single_row_df




if __name__ == "__main__":
    # inputted_name = input('ENTER A PLAYERS NAME: ')
    # player_dict = players.find_players_by_full_name(inputted_name)
    # if player_dict:
    #     player_id = player_dict[0]['id']
    # else:
    #     print(f"Player not found: {player}")
    
    overall_df, shooting_df, finishing_df = get_player_career_stats('202695')
    print('\n\n------------------------------------------------------------------------------\n\n')
    print(overall_df)
    print('\n\n------------------------------------------------------------------------------\n\n')
    print(shooting_df)
    print('\n\n------------------------------------------------------------------------------\n\n')
    print(finishing_df)
    print('\n\n------------------------------------------------------------------------------\n\n')

    
    combined_df = merged_df(overall_df, shooting_df, finishing_df)
    print(combined_df)

