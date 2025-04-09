from flask import Flask, render_template, request, redirect, url_for
from nba_api.stats.static import players
from centroid_clustering import single_player_coor
import json
# import os
from math import dist
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import career_stats as cs
import io
import base64

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

    # if not player_coordinates:
    #     return {"error": f"Could not determine coordinates for '{player_name}'."}

    # if not os.path.exists(OUTPUT_FILE):
    #     return {"error": f"'{OUTPUT_FILE}' not found. Please run centroid_clustering.py first."}

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

    # Sort centroids by distance and select the closest 5
    sorted_centroids = sorted(archetype_centroid_dict.items(), key=lambda x: dist(x[1], player_coordinates))[:5]

    # Generate and encode plot as base64
    img_buffer = io.BytesIO()
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
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', transparent=True)
    plt.close()
    img_buffer.seek(0)
    plot_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    img_buffer.close()

    return {"name": player_name, "archetypes": player_archetypes, "plot_base64": plot_base64}

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
    player_dict = players.find_players_by_full_name(player_name)
    if not player_dict:
        return render_template('error.html', error_message=f"Player '{player_name}' not found.")
    player_id = player_dict[0]['id']

    # Fetch player stats
    player_stats, _, _ = cs.get_player_career_stats(player_id)
    seasons = player_stats["SEASON_ID"].tolist()
    columns = player_stats.columns.tolist()

    return render_template(
        'cluster_result.html',
        result=result,
        player_id=player_id,
        stats=player_stats.to_dict(orient="records"),
        seasons=seasons,
        columns=columns
    )

@app.route('/compare')
def compare():
    return render_template('compare.html')

@app.route('/compare_players', methods=['POST'])
def run_compare():
    player1_name = request.form['player1_name']
    player2_name = request.form['player2_name']
    player1_dict = players.find_players_by_full_name(player1_name)
    if not player1_dict:
        return render_template('error.html', error_message=f"Player 1 '{player1_name}' not found.")
    player1_id = player1_dict[0]['id']
    player2_dict = players.find_players_by_full_name(player2_name)
    if not player2_dict:
        return render_template('error.html', error_message=f"Player 2 '{player2_name}' not found.")
    player2_id = player2_dict[0]['id']
    p1_stats, _, _ = cs.get_player_career_stats(player1_id)
    p2_stats, _, _ = cs.get_player_career_stats(player2_id)
    
    p1_seasons = p1_stats["SEASON_ID"].tolist()
    p2_seasons = p2_stats["SEASON_ID"].tolist()
    p1_columns = p1_stats.columns.tolist()
    p2_columns = p2_stats.columns.tolist()
    
    return render_template('compare_result.html', player1=p1_stats.to_dict(orient="records"), player2=p2_stats.to_dict(orient="records"), p1_seasons=p1_seasons, p2_seasons=p2_seasons, p1_columns=p1_columns, p2_columns=p2_columns, player1_id=player1_id, player2_id=player2_id, player1_name=player1_name, player2_name=player2_name)
if __name__ == '__main__':
    app.run(debug=True)
    # pass