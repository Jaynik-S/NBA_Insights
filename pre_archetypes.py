from nba_api.stats.static import players
from collections import defaultdict

nba_archetypes = {
    "Post Scorer": ["Nikola Jokić", "Joel Embiid", "Karl-Anthony Towns", "Anthony Davis", "Domantas Sabonis"],
    "Three-Point Specialist": ["Stephen Curry", "Klay Thompson", "Duncan Robinson", "Buddy Hield", "Desmond Bane"],
    "Rim Protector": ["Rudy Gobert", "Brook Lopez", "Myles Turner", "Jaren Jackson Jr.", "Clint Capela"],
    "Slasher": ["Giannis Antetokounmpo", "Ja Morant", "DeMar DeRozan", "Zion Williamson", "Anthony Edwards"],
    "Mid-Range Maestro": ["Kevin Durant", "DeMar DeRozan", "Chris Paul", "Kawhi Leonard", "Bradley Beal"],
    "Fast Break Finisher": ["LeBron James", "Ja Morant", "Zion Williamson", "Russell Westbrook", "Aaron Gordon"],
    "Floor General": ["Chris Paul", "Luka Dončić", "Trae Young", "Damian Lillard", "James Harden"],
    "Offensive Rebounder": ["Steven Adams", "Clint Capela", "Kevon Looney", "Mitchell Robinson", "Jarrett Allen"],
    "Corner Specialist": ["P.J. Tucker", "Joe Harris", "Jae Crowder", "Danny Green", "Mikal Bridges"],
    "Fadeaway Artist": ["Kevin Durant", "Kobe Bryant (historical)", "Kawhi Leonard", "Dirk Nowitzki (historical)", "Paul George"],
    "Paint Beast": ["Joel Embiid", "Giannis Antetokounmpo", "Bam Adebayo", "Jonas Valančiūnas", "Deandre Ayton"],
    "Perimeter Defender": ["Marcus Smart", "Jrue Holiday", "Matisse Thybulle", "Jimmy Butler", "Derrick White"],
    "Pick-and-Roll Playmaker": ["Trae Young", "Chris Paul", "Luka Dončić", "Ja Morant", "Darius Garland"],
    "Iso Scorer": ["James Harden", "Kyrie Irving", "Kevin Durant", "Jayson Tatum", "Devin Booker"],
    "Undersized Scorer": ["Fred VanVleet", "Kemba Walker", "T.J. McConnell", "Terry Rozier", "Tyrese Maxey"],
    "Versatile Big": ["Nikola Jokić", "Bam Adebayo", "Draymond Green", "Al Horford", "Evan Mobley"],
    "Sharpshooter": ["Stephen Curry", "Klay Thompson", "Duncan Robinson", "Kevin Huerter", "Tyler Herro"],
    "Glue Guy": ["Draymond Green", "Marcus Smart", "Mikal Bridges", "Alex Caruso", "OG Anunoby"],
    "Cut Specialist": ["Zion Williamson", "Aaron Gordon", "Bruce Brown", "Josh Hart", "Gary Payton II"],
    "All-Around Scorer": ["Kevin Durant", "LeBron James", "Luka Dončić", "Jayson Tatum", "Donovan Mitchell"]
}


archetypes_id = defaultdict(list)
for key, player_names in nba_archetypes.items():
    for player in player_names:
        # Clean the player name (e.g., remove annotations like "(historical)")
        clean_player_name = player.split(' (')[0].strip()
        
        # Find player by name
        player_dict = players.find_players_by_full_name(clean_player_name)
        if player_dict:
            # If player found, get their ID
            player_id = player_dict[0]['id']
            archetypes_id[key].append(player_id)
        else:
            print(f"Player not found: {player}")
            
print('\nMapped Archetypes with Player IDs:')
print(archetypes_id)