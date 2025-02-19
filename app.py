from flask import Flask, render_template, request, redirect, url_for
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

    # Sort centroids by distance and select the closest 5
    sorted_centroids = sorted(archetype_centroid_dict.items(), key=lambda x: dist(x[1], player_coordinates))[:5]

    plt.figure(figsize=(12, 8))
    for archetype, centroid in sorted_centroids:
        plt.scatter(centroid[0], centroid[1], c='red', marker='x', s=200, label=archetype)
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
def select():
    return render_template('select.html')

@app.route('/select_program', methods=['POST'])
def select_program():
    program = request.form['program']
    if program == 'cluster':
        return redirect(url_for('cluster'))
    elif program == 'compare':
        return redirect(url_for('compare'))

    # Return an error if the program is not recognized
    return "Invalid program selected", 400

@app.route('/cluster')
def cluster():
    return render_template('cluster.html')

@app.route('/get_archetype', methods=['POST'])
def get_archetype():
    player_name = request.form['player_name']
    result = get_player_archetypes(player_name)
    return render_template('cluster_result.html', result=result)

@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/compare_players', methods=['POST'])
def run_compare():
    player1_name = request.form['player1_name']
    player2_name = request.form['player2_name']
    player1_dict = players.find_players_by_full_name(player1_name)
    if not player1_dict:
        return {"error": f"Player 1 '{player1_name}' not found."}
    player1_id = player1_dict[0]['id']
    player2_dict = players.find_players_by_full_name(player2_name)
    if not player2_dict:
        return {"error": f"Player 2 '{player2_name}' not found."}
    player2_id = player1_dict[0]['id']
    p1_stats = cs.get_player_career_stats(player1_id)
    p2_stats = cs.get_player_career_stats(player2_id)
    
    
    return render_template('compare_result.html', player1=p1_stats, player2=p2_stats)


if __name__ == '__main__':
    app.run(debug=True)
