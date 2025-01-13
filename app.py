from flask import Flask, request, render_template
from nba_api.stats.static import players
from centroid_clustering import single_player_coor
import json
import os
from math import dist
import matplotlib.pyplot as plt

app = Flask(__name__)

# Configurations
OUTPUT_FILE = "data/archetype_centroids.json"
THRESHOLD_DISTANCE = 6.8
MAX_ARCHETYPES = 3
STATIC_DIR = "static"

# Helper function to get player archetypes
def get_player_archetypes(player_name):
    player_dict = players.find_players_by_full_name(player_name)

    if not player_dict:
        return {"error": f"Player '{player_name}' not found."}

    player_id = player_dict[0]['id']
    player_coordinates = single_player_coor(player_id)

    if not player_coordinates:
        return {"error": f"Could not determine coordinates for '{player_name}'."}

    if not os.path.exists(OUTPUT_FILE):
        return {"error": f"'{OUTPUT_FILE}' not found. Please run centroid_clustering.py first."}

    with open(OUTPUT_FILE, "r") as json_file:
        archetype_centroid_dict = json.load(json_file)

    archetype_distances = {}
    for archetype, centroid in archetype_centroid_dict.items():
        archetype_distances[archetype] = dist(centroid, player_coordinates)

    closest_archetype = min(archetype_distances, key=archetype_distances.get)
    sorted_archetypes = sorted(archetype_distances.items(), key=lambda x: x[1])
    player_archetypes = [arch for arch, distance in sorted_archetypes[:MAX_ARCHETYPES] if distance <= THRESHOLD_DISTANCE]

    if closest_archetype not in player_archetypes:
        if len(player_archetypes) >= MAX_ARCHETYPES:
            player_archetypes.pop()
        player_archetypes.insert(0, closest_archetype)

    # Generate and save plot
    file_path = os.path.join(STATIC_DIR, f"{player_name}_archetypes.png")
    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR)

    plt.figure(figsize=(12, 8))
    for archetype, centroid in archetype_centroid_dict.items():
        plt.scatter(centroid[0], centroid[1], c='red', marker='x', s=200,
                    label=archetype if archetype in player_archetypes else None)
        plt.text(centroid[0] + 0.1, centroid[1], archetype, fontsize=9)

    plt.scatter(player_coordinates[0], player_coordinates[1], c='blue', marker='o', s=100, label=f"{player_name}'s location")
    plt.text(player_coordinates[0] + 0.1, player_coordinates[1], player_name, fontsize=10, color='blue')

    plt.title(f"Archetype Visualization for {player_name.title()}", fontsize=16)
    plt.xlabel("Principal Component 1", fontsize=14)
    plt.ylabel("Principal Component 2", fontsize=14)
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.savefig(file_path, dpi=300, bbox_inches='tight', transparent=True)
    plt.close()

    return {"name": player_name, "archetypes": player_archetypes, "plot_path": os.path.basename(file_path)}

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_archetype', methods=['POST'])
def get_archetype():
    player_name = request.form['player_name']
    result = get_player_archetypes(player_name)
    return render_template('result.html', result=result)

if __name__ == "__main__":
    app.run(debug=True)
