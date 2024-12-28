import career_stats as cs
from nba_api.stats.static import players

# Example usage
player_name = ""
while player_name != 'finish':
    player_name = input('Enter a player\'s name: ')
    player_dict = players.find_players_by_full_name(player_name)
    if not player_dict:
        print(f"Player {player_name} not found.")
    else:
        player_id = player_dict[0]['id']
        overall_df, shooting_df, finishing_df = cs.get_player_career_stats(player_id)

    print('\n\n------------------------------------------------------------------------------\n\n')
    print(overall_df)
    print('\n\n------------------------------------------------------------------------------\n\n')
    print(shooting_df)
    print('\n\n------------------------------------------------------------------------------\n\n')
    print(finishing_df)
    print('\n\n------------------------------------------------------------------------------\n\n')
    
    overall_df, shooting_df, finishing_df = None, None, None
    
if __name__ == "__main__":
    print("PROGRAM FINISHED.")