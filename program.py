from nba_api.stats.static import players
import career_stats as cs
from centroid_clustering import single_player_coor  # Import the function
import json
from math import dist
import os
import matplotlib.pyplot as plt

OUTPUT_FILE = "archetype_centroids.json"
THRESHOLD_DISTANCE = 4  # Maximum distance for assigning multiple archetypes
MAX_ARCHETYPES = 3  # Maximum number of archetypes a player can have

player_name = ""
while player_name != 'finish':
    player_name = input("Enter a player's name: ").lower()
    player_dict = players.find_players_by_full_name(player_name)

    if not player_dict:
        print(f"Player {player_name} not found.")
        continue

    player_id = player_dict[0]['id']
    player_coordinates = single_player_coor(player_id)  # Get player coordinates

    if not player_coordinates:
        print(f"Could not determine coordinates for {player_name}.")
        continue

    if not os.path.exists(OUTPUT_FILE):
        print(f"{OUTPUT_FILE} not found. Please run centroid_clustering.py first.")
        continue

    with open(OUTPUT_FILE, "r") as json_file:
        archetype_centroid_dict = json.load(json_file)

    # Calculate distances to each archetype
    archetype_distances = {}
    for arch, centroid in archetype_centroid_dict.items():
        archetype_distances[arch] = dist(centroid, player_coordinates)

    # Assign the closest archetype (every player gets at least one)
    closest_archetype = min(archetype_distances, key=archetype_distances.get)

    # Sort archetypes by distance and limit to MAX_ARCHETYPES
    sorted_archetypes = sorted(archetype_distances.items(), key=lambda x: x[1])
    player_archetypes = [arch for arch, distance in sorted_archetypes[:MAX_ARCHETYPES] if distance <= THRESHOLD_DISTANCE]

    # Ensure the closest archetype is always included
    if closest_archetype not in player_archetypes:
        if len(player_archetypes) >= MAX_ARCHETYPES:
            player_archetypes.pop()  # Remove the furthest archetype if at the limit
        player_archetypes.insert(0, closest_archetype)

    print(f"{player_name}'s archetypes: {player_archetypes}")

    # Plot the centroids, archetypes, and player point
    plt.figure(figsize=(12, 8))
    
    # Plot archetype centroids
    for archetype, centroid in archetype_centroid_dict.items():
        plt.scatter(centroid[0], centroid[1], c='red', marker='x', s=200,
                    label=archetype if archetype in player_archetypes else None)
        plt.text(centroid[0] + 0.1, centroid[1], archetype, fontsize=9)

    # Plot player coordinates
    plt.scatter(player_coordinates[0], player_coordinates[1], c='blue', marker='o', s=100, label=f"{player_name}'s location")
    plt.text(player_coordinates[0] + 0.1, player_coordinates[1], player_name, fontsize=10, color='blue')

    plt.title(f"Archetype Visualization for {player_name.title()}", fontsize=16)
    plt.xlabel("Principal Component 1", fontsize=14)
    plt.ylabel("Principal Component 2", fontsize=14)
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.show()

print("PROGRAM FINISHED.")
