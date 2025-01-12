from flask import Flask, request, render_template
from nba_api.stats.static import players
from centroid_clustering import single_player_coor
import json
import os
from math import dist

app = Flask(__name__)

# Configurations
OUTPUT_FILE = "data/archetype_centroids.json"
THRESHOLD_DISTANCE = 6.8
MAX_ARCHETYPES = 3

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

    return {"name": player_name, "archetypes": player_archetypes}

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
