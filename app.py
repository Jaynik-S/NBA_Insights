from nba_api.stats.static import players
from centroid_clustering import single_player_archetypes
import career_stats as cs
from flask import Flask, render_template, request, redirect, url_for
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import logging
import json
import io
import base64
import os

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

# Configuration for production deployment
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-production-secret-key-change-this')

# Handle both local and production environments
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CENTROIDS_FILE = os.path.join(BASE_DIR, 'data', 'archetype_centroids.json')
ARCHETYPE_MAPPING_FILE = os.path.join(BASE_DIR, 'data', 'archetype_mapping.json')


# Helper function to get player archetypes using GMM
def get_player_archetypes(player_name):
    player_name = player_name.title()
    player_dict = players.find_players_by_full_name(player_name)

    if not player_dict:
        return {"error": f"Player '{player_name}' not found."}

    player_id = player_dict[0]['id']
    
    # Get archetype probabilities using the new GMM-based function
    result = single_player_archetypes(player_id)
    
    if not result:
        return {"error": f"Could not determine archetypes for '{player_name}'."}
    
    # Check if centroids file exists for visualization
    if not os.path.exists(CENTROIDS_FILE):
        return {"error": f"'{CENTROIDS_FILE}' not found. Please run centroid_clustering.py first."}

    # Extract player coordinates and top archetypes (now sorted by distance)
    player_coordinates = result['coordinates']
    closest_archetypes = result['archetypes']
    closest_archetype_names = [arch['name'] for arch in closest_archetypes]
    
    # Debug information
    print(f"Player: {player_name}")
    for arch in closest_archetypes:
        print(f"  {arch['name']}: distance={arch['distance']:.2f}, probability={arch['probability']:.2%}")
    
    # Load centroid data for plotting
    with open(CENTROIDS_FILE, "r") as json_file:
        archetype_centroid_dict = json.load(json_file)

    # Generate and encode plot as base64
    img_buffer = io.BytesIO()
    plt.figure(figsize=(12, 8))
    
    # Define colors for the top 3 archetypes
    colors = ['#FF5733', '#33A8FF', '#45FF33']  # Red, Blue, Green
    
    # First plot all centroids in gray (low alpha)
    for archetype, centroid in archetype_centroid_dict.items():
        if archetype not in closest_archetype_names:
            plt.scatter(centroid[0], centroid[1], c='gray', marker='x', s=100, alpha=0.3)
            plt.text(centroid[0] + 0.1, centroid[1], archetype, fontsize=8, alpha=0.3)
    
    # Plot the top 3 closest archetypes with distinct colors
    for i, archetype in enumerate(closest_archetypes):
        archetype_name = archetype['name']
        distance = archetype['distance']
        probability = archetype['probability']
        
        if archetype_name in archetype_centroid_dict:
            centroid = archetype_centroid_dict[archetype_name]
            color = colors[i]
            
            # Format label with distance and probability
            label = f"{archetype_name} (dist: {distance:.2f})"
            
            # Plot centroid with color
            plt.scatter(centroid[0], centroid[1], c=color, marker='x', s=200, label=label)
            plt.text(centroid[0] + 0.1, centroid[1], archetype_name, fontsize=10, weight='bold', color=color)
            
            # Draw line connecting player to archetype
            plt.plot([player_coordinates[0], centroid[0]], 
                    [player_coordinates[1], centroid[1]], 
                    c=color, alpha=0.8, 
                    linewidth=4.0 - i, # Thicker lines for closer archetypes
                    linestyle='-')

    # Plot player location
    plt.scatter(player_coordinates[0], player_coordinates[1], c='black', marker='o', s=120, label=f"{player_name}'s location")
    plt.text(player_coordinates[0] + 0.1, player_coordinates[1], player_name, fontsize=11, color='black', weight='bold')

    plt.title(f"Top 3 Closest Archetypes for {player_name}", fontsize=16)
    plt.xlabel("Principal Component 1", fontsize=14)
    plt.ylabel("Principal Component 2", fontsize=14)
    plt.legend(loc='best')
    plt.grid(True, alpha=0.3)
    plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight', transparent=True)
    plt.close()
    img_buffer.seek(0)
    plot_base64 = base64.b64encode(img_buffer.read()).decode('utf-8')
    img_buffer.close()

    # Format archetypes with distances for display
    formatted_archetypes = []
    for i in range(len(closest_archetypes)):
        formatted_archetypes.append(
            f"{i+1}: {closest_archetypes[i]['name']} (distance: {closest_archetypes[i]['distance']:.2f})"
        )

    return {
        "name": player_name, 
        "archetypes": formatted_archetypes, 
        "plot_base64": plot_base64
    }


# Routes
@app.route('/')
def home():
    return render_template('index.html', active_page='home')

@app.route('/select')
def select():
    return render_template('select.html', active_page='select')

@app.route('/custom')
def custom():
    return render_template('custom.html', active_page='custom')

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
    return render_template('cluster.html', active_page='cluster')

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
    return render_template('compare.html', active_page='compare')

@app.route('/compare_players', methods=['POST'])
def run_compare():
    # Get all player entries from form
    players_data = {}
    max_players = 5
    
    # Collect all player data from the form
    for i in range(1, max_players + 1):
        player_name_key = f'player{i}_name'
        if player_name_key in request.form and request.form[player_name_key].strip():
            player_name = request.form[player_name_key].strip()
            player_dict = players.find_players_by_full_name(player_name)
            
            if not player_dict:
                return render_template('error.html', error_message=f"Player {i} '{player_name}' not found.")
            
            player_id = player_dict[0]['id']
            player_stats, _, _ = cs.get_player_career_stats(player_id)
            
            players_data[str(i)] = {
                'id': player_id,
                'name': player_name,
                'stats': player_stats.to_dict(orient="records"),
                'seasons': player_stats["SEASON_ID"].tolist(),
                'columns': player_stats.columns.tolist()
            }
    
    if len(players_data) < 2:
        return render_template('error.html', error_message="Please enter at least 2 players to compare.")
    
    return render_template('compare_result.html', players=players_data)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_message="Page not found"), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    app.run(host='0.0.0.0', port=port, debug=debug)