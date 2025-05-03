from nba_api.stats.static import players
import career_stats as cs
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score
import json
import os
import pickle

# Constants
OUTPUT_DIR = "data"
MODEL_FILE = os.path.join(OUTPUT_DIR, "gmm_model.pkl")
SCALER_FILE = os.path.join(OUTPUT_DIR, "scaler.pkl")
PCA_FILE = os.path.join(OUTPUT_DIR, "pca.pkl")
CENTROIDS_FILE = os.path.join(OUTPUT_DIR, "archetype_centroids.json")
ARCHETYPE_MAPPING_FILE = os.path.join(OUTPUT_DIR, "archetype_mapping.json")

# Ensure the data directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Archetype names mapping - can be customized
ARCHETYPE_NAMES = {
    0: "Versatile Role Players",
    1: "Elite Wing Scorers",
    2: "Raw Athletic Bigs",
    3: "Veteran Utility Forwards",
    4: "Dynamic Two-Way Forwards",
    5: "All-Around Superstars",
    6: "Defensive Anchor Centers",
    7: "3-and-D Wings",
    8: "Dominant Freak",
    9: "High-Volume Scoring Guards",
    10: "Maestro Big",
    11: "Savvy Floor Generals",
    12: "High-Energy Hustlers",
    13: "Sharpshooting Phenoms",
    14: "Creative Shot Creators",
    15: "Dominant Interior Forces",
    16: "Hybrid Creators",
}


def load_player_data(player_names):
    """Load and preprocess data for a list of players."""
    print(f"Loading data for {len(player_names)} players...")
    
    # Get player IDs
    players_id = []
    for player in player_names:
        player_dict = players.find_players_by_full_name(player.strip())
        if player_dict:
            players_id.append(player_dict[0]['id'])
        else:
            print(f"Player not found: {player}")
    
    # Get player stats
    players_data = []
    for p_id in players_id:
        try:
            # Get career stats
            overall_df, shooting_df, finishing_df = cs.get_player_career_stats(p_id)
            # Merge stats into a single DataFrame
            full_stats = cs.merged_df(overall_df, shooting_df, finishing_df)
            # Extract numeric features
            numeric_stats = full_stats.select_dtypes(include=[np.number])
            if not numeric_stats.empty:
                players_data.append({
                    'id': p_id,
                    'name': player_names[players_id.index(p_id)],
                    'features': numeric_stats.values.flatten()
                })
        except Exception as e:
            print(f"Error processing player ID {p_id}: {e}")
    
    return players_data


def preprocess_features(players_data):
    """Scale and reduce dimensionality of player features."""
    # Extract feature arrays
    feature_arrays = [player['features'] for player in players_data]
    
    # Standardize feature lengths
    max_length = max(len(arr) for arr in feature_arrays)
    padded_arrays = [np.pad(arr, (0, max_length - len(arr)), 'constant') 
                    for arr in feature_arrays]
    
    # Convert to numpy array and handle NaN values
    X = np.array(padded_arrays)
    X = np.nan_to_num(X)
    
    # Scale the data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Apply PCA for dimensionality reduction
    pca = PCA(n_components=0.95)  # Retain 95% variance
    X_reduced = pca.fit_transform(X_scaled)
    
    # Save preprocessing models
    with open(SCALER_FILE, "wb") as f:
        pickle.dump(scaler, f)
    
    with open(PCA_FILE, "wb") as f:
        pickle.dump(pca, f)
    
    return X_reduced, scaler, pca


def find_optimal_clusters(X, max_clusters=30):
    """Find optimal number of clusters using silhouette scores."""
    silhouette_scores = []
    
    # Test different numbers of clusters
    for n_clusters in range(15, max_clusters + 1):
        try:
            # Fit GMM with n components
            gmm = GaussianMixture(n_components=n_clusters, random_state=42, 
                                 covariance_type='full', n_init=10)
            cluster_labels = gmm.fit_predict(X)
            
            # Calculate silhouette score
            score = silhouette_score(X, cluster_labels)
            silhouette_scores.append((n_clusters, score))
        except Exception as e:
            print(f"Error with {n_clusters} clusters: {e}")
    
    # Find best number of clusters
    best_n_clusters, best_score = max(silhouette_scores, key=lambda x: x[1])
    
    # Plot silhouette scores
    plt.figure(figsize=(10, 6))
    plt.plot(*zip(*silhouette_scores), marker='o')
    plt.xlabel('Number of Clusters')
    plt.ylabel('Silhouette Score')
    plt.title('Silhouette Score vs Number of Clusters')
    plt.grid(True)
    plt.savefig(os.path.join(OUTPUT_DIR, "silhouette_scores.png"))
    
    return best_n_clusters


def fit_gmm_model(X, n_clusters):
    """Fit a Gaussian Mixture Model with the specified number of clusters."""
    # Initialize and fit GMM
    gmm = GaussianMixture(
        n_components=n_clusters,
        random_state=42,
        covariance_type='full',
        n_init=10
    )
    gmm.fit(X)
    
    # Save the model
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(gmm, f)
    
    return gmm


def create_archetype_mapping(n_clusters):
    """Create a mapping from cluster indices to archetype names."""
    # Use predefined names or generate defaults
    archetype_mapping = {}
    for i in range(n_clusters):
        if i in ARCHETYPE_NAMES:
            archetype_mapping[i] = ARCHETYPE_NAMES[i]
        else:
            archetype_mapping[i] = f"Archetype_{i}"
    
    # Save the mapping
    with open(ARCHETYPE_MAPPING_FILE, "w") as f:
        json.dump(archetype_mapping, f, indent=4)
    
    return archetype_mapping


def save_cluster_centroids(gmm, pca, archetype_mapping):
    """Save cluster centroids in PCA space."""
    # Get centroids in PCA space
    centroids = gmm.means_
    
    # Create dictionary of archetype centroids
    archetype_centroids = {}
    for i, centroid in enumerate(centroids):
        archetype_name = archetype_mapping[i]
        # Store just first two components for visualization
        archetype_centroids[archetype_name] = centroid[:2].tolist()
    
    # Save to json file
    with open(CENTROIDS_FILE, "w") as f:
        json.dump(archetype_centroids, f, indent=4)
    
    return archetype_centroids


def visualize_clusters(X, cluster_probs, gmm, archetype_mapping):
    """Visualize clusters with probability information."""
    # Get cluster assignments and probabilities
    cluster_labels = gmm.predict(X)
    
    # Create a colormap
    colors = plt.cm.viridis(np.linspace(0, 1, len(archetype_mapping)))
    
    # Plot points with cluster colors
    plt.figure(figsize=(16, 12))  # Increase figure size for better spacing
    
    # First plot all points with low alpha
    for i, label in enumerate(cluster_labels):
        plt.scatter(X[i, 0], X[i, 1], color=colors[label], alpha=0.3, s=50)
    
    # Then plot centroids
    for i, mean in enumerate(gmm.means_):
        plt.scatter(mean[0], mean[1], color=colors[i], marker='X', 
                   s=200, edgecolor='black')  # Remove inline labels
    
    plt.title("NBA Player Archetypes using Gaussian Mixture Model", fontsize=16)
    plt.xlabel("Principal Component 1", fontsize=14)
    plt.ylabel("Principal Component 2", fontsize=14)
    plt.grid(True, alpha=0.3)
    
    # Create a separate legend with better positioning
    plt.legend([plt.Line2D([0], [0], marker='X', color='w', markerfacecolor=colors[i], 
                          markersize=15, markeredgecolor='black') for i in range(len(archetype_mapping))],
              [archetype_mapping[i] for i in range(len(archetype_mapping))],
              bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)
    
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust layout to make room for legend
    plt.savefig(os.path.join(OUTPUT_DIR, "cluster_visualization.png"))
    plt.close()
    
    # Create a second visualization showing probability distributions
    plt.figure(figsize=(16, 12))  # Increase figure size
    
    # For each point, draw lines to centroids with width proportional to probability
    for i in range(len(X)):
        for j, prob in enumerate(cluster_probs[i]):
            if prob > 0.1:  # Only draw significant probabilities
                plt.plot([X[i, 0], gmm.means_[j, 0]], 
                         [X[i, 1], gmm.means_[j, 1]], 
                         color=colors[j], alpha=prob, linewidth=prob*3)
    
    # Plot the points and centroids
    for i, label in enumerate(cluster_labels):
        plt.scatter(X[i, 0], X[i, 1], color='black', alpha=0.7, s=30)
    
    for i, mean in enumerate(gmm.means_):
        plt.scatter(mean[0], mean[1], color=colors[i], marker='X', 
                   s=200, edgecolor='black')  # Remove inline labels
    
    plt.title("NBA Player Archetype Probability Visualization", fontsize=16)
    plt.xlabel("Principal Component 1", fontsize=14)
    plt.ylabel("Principal Component 2", fontsize=14)
    plt.grid(True, alpha=0.3)
    
    # Create a separate legend with better positioning
    plt.legend([plt.Line2D([0], [0], marker='X', color='w', markerfacecolor=colors[i], 
                          markersize=15, markeredgecolor='black') for i in range(len(archetype_mapping))],
              [archetype_mapping[i] for i in range(len(archetype_mapping))],
              bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)
    
    plt.tight_layout(rect=[0, 0, 0.85, 1])  # Adjust layout to make room for legend
    plt.savefig(os.path.join(OUTPUT_DIR, "probability_visualization.png"))
    plt.close()


def analyze_player_clusters(players_data, X, gmm, archetype_mapping):
    """Analyze player assignments to clusters."""
    # Get probabilities for each cluster
    cluster_probs = gmm.predict_proba(X)
    
    # Create a DataFrame with player info and cluster probabilities
    result_data = []
    for i, player in enumerate(players_data):
        player_probs = cluster_probs[i]
        # Get top 3 archetype probabilities
        top_indices = np.argsort(player_probs)[::-1][:3]
        archetypes = [(archetype_mapping[idx], float(player_probs[idx])) 
                     for idx in top_indices if player_probs[idx] > 0.05]
        
        result_data.append({
            'id': player['id'],
            'name': player['name'],
            'primary_archetype': archetype_mapping[np.argmax(player_probs)],
            'primary_probability': float(np.max(player_probs)),
            'archetypes': archetypes
        })
    
    # Save player analysis
    with open(os.path.join(OUTPUT_DIR, "player_archetypes.json"), "w") as f:
        json.dump(result_data, f, indent=4)
    
    # Print some example players from each cluster
    for cluster_idx in range(len(archetype_mapping)):
        cluster_players = [p for p in result_data 
                          if p['primary_archetype'] == archetype_mapping[cluster_idx]]
        print(f"\nArchetype: {archetype_mapping[cluster_idx]}")
        # Sort by probability and show top 5
        for player in sorted(cluster_players, 
                            key=lambda x: x['primary_probability'], 
                            reverse=True)[:15]:
            print(f"  {player['name']} ({player['primary_probability']:.2f})")
    
    return cluster_probs


def single_player_archetypes(player_id):
    """Get archetype probabilities for a single player, sorted by distance to centroids."""
    try:
        # Check if models exist
        if not all(os.path.exists(f) for f in [MODEL_FILE, SCALER_FILE, PCA_FILE, ARCHETYPE_MAPPING_FILE]):
            print("Models not found. Please run clustering first.")
            return None
        
        # Load models
        with open(MODEL_FILE, "rb") as f:
            gmm = pickle.load(f)
        
        with open(SCALER_FILE, "rb") as f:
            scaler = pickle.load(f)
        
        with open(PCA_FILE, "rb") as f:
            pca = pickle.load(f)
        
        with open(ARCHETYPE_MAPPING_FILE, "r") as f:
            archetype_mapping = json.load(f)
            
        # Load centroids for distance calculation
        with open(CENTROIDS_FILE, "r") as f:
            archetype_centroids = json.load(f)
        
        # Get player stats
        overall_df, shooting_df, finishing_df = cs.get_player_career_stats(player_id)
        full_stats = cs.merged_df(overall_df, shooting_df, finishing_df)
        numeric_stats = full_stats.select_dtypes(include=[np.number])
        
        if numeric_stats.empty:
            print("No numeric stats found for player.")
            return None
        
        # Preprocess
        features = numeric_stats.values.flatten()
        
        # Make sure features have the right length
        expected_length = scaler.n_features_in_
        if len(features) < expected_length:
            features = np.pad(features, (0, expected_length - len(features)), 'constant')
        elif len(features) > expected_length:
            features = features[:expected_length]
        
        # Scale and reduce
        features = np.nan_to_num(features)
        features_scaled = scaler.transform(features.reshape(1, -1))
        features_reduced = pca.transform(features_scaled)
        
        # Get probabilities from GMM model
        probs = gmm.predict_proba(features_reduced)[0]
        
        # Get coordinates for plotting
        player_coords = features_reduced[0, :2].tolist()
        
        # Calculate Euclidean distances to each archetype centroid
        distances = []
        for archetype_name, centroid in archetype_centroids.items():
            # Calculate Euclidean distance
            distance = np.sqrt((player_coords[0] - centroid[0])**2 + (player_coords[1] - centroid[1])**2)
            
            # Find probability for this archetype
            prob = 0.0
            for i, name in archetype_mapping.items():
                if name == archetype_name:
                    prob = float(probs[int(i)])
                    break
                    
            distances.append({
                'name': archetype_name,
                'distance': float(distance),
                'probability': prob
            })
        
        # Sort by distance (closest first)
        archetypes = sorted(distances, key=lambda x: x['distance'])
        
        # Take top 3 closest archetypes
        top_archetypes = archetypes[:3]
        
        return {
            'coordinates': player_coords,
            'archetypes': top_archetypes
        }
    
    except Exception as e:
        print(f"Error processing player ID {player_id}: {e}")
        return None


if __name__ == "__main__":
    # List of NBA players for clustering
    nba_players = [
        "LeBron James", "Kevin Durant", "Stephen Curry", "Giannis Antetokounmpo", "Nikola Jokić", "Joel Embiid",
        "Luka Dončić", "James Harden", "Damian Lillard", "Jayson Tatum", "Devin Booker", "Kawhi Leonard",
        "Paul George", "Kyrie Irving", "Jimmy Butler", "Anthony Davis", "Chris Paul", "Trae Young",
        "Donovan Mitchell", "Bradley Beal", "Ja Morant", "Russell Westbrook", "Karl-Anthony Towns",
        "Draymond Green", "Bam Adebayo", "Rudy Gobert", "Ben Simmons", "Klay Thompson", "Andrew Wiggins",
        "Pascal Siakam", "DeMar DeRozan", "Zach LaVine", "Brandon Ingram", "Jaylen Brown", "LaMelo Ball",
        "Anthony Edwards", "Domantas Sabonis", "De'Aaron Fox", "CJ McCollum", "Khris Middleton",
        "Jrue Holiday", "Mikal Bridges", "Steven Adams", "Clint Capela", "Myles Turner", "Fred VanVleet",
        "Kyle Lowry", "Gordon Hayward", "Julius Randle", "Shai Gilgeous-Alexander", "Darius Garland",
        "Evan Mobley", "Cade Cunningham", "Tyrese Haliburton", "RJ Barrett", "Miles Bridges", "Terry Rozier",
        "Derrick Rose", "Victor Oladipo", "Malcolm Brogdon", "Al Horford", "Brook Lopez", "Mitchell Robinson",
        "Buddy Hield", "Gary Trent Jr.", "Michael Porter Jr.", "Christian Wood", "Spencer Dinwiddie",
        "Caris LeVert", "Eric Gordon", "Derrick White", "John Collins", "Nikola Vučević", "Aaron Gordon",
        "Bojan Bogdanović", "Marcus Smart", "Lauri Markkanen", "Robert Covington", "Norman Powell",
        "Serge Ibaka", "Jarrett Allen", "Seth Curry", "Joe Ingles", "Tim Hardaway Jr.", "Reggie Jackson",
        "Harrison Barnes", "Jaren Jackson Jr.", "Bogdan Bogdanović", "Rui Hachimura", "Kyle Kuzma",
        "Jordan Clarkson", "Richaun Holmes", "D'Angelo Russell", "Dejounte Murray", "Keldon Johnson",
        "Lonzo Ball", "Coby White", "Alex Caruso", "Devin Vassell", "James Wiseman", "Deandre Ayton",
        "Franz Wagner", "Jordan Poole", "Kevin Porter Jr.", "Patrick Beverley", "Doug McDermott",
        "Davis Bertans", "Kelly Olynyk", "Daniel Gafford", "Cam Reddish", "Trey Murphy III", "Kevin Love",
        "De'Andre Hunter", "Cameron Johnson", "Markelle Fultz", "Cole Anthony", "Jalen Suggs", "OG Anunoby",
        "Scottie Barnes", "Precious Achiuwa", "Obi Toppin", "Tyrese Maxey",
        "Jabari Smith Jr.", "Jalen Green", "Josh Giddey", "Luguentz Dort", "Kenrich Williams", "Austin Reaves",
        "Bones Hyland", "Jamal Murray", "Nikola Jović", "Caleb Martin", "Cody Martin", "Grant Williams",
    ]

    # Main clustering pipeline
    print("Starting NBA player clustering with GMM...")
    
    # 1. Load and preprocess player data
    players_data = load_player_data(nba_players)
    X_reduced, scaler, pca = preprocess_features(players_data)
    
    # 2. Find optimal number of clusters (or use predefined value)
    n_clusters = find_optimal_clusters(X_reduced, max_clusters=30)
    
    # 3. Fit GMM model
    gmm = fit_gmm_model(X_reduced, n_clusters)
    
    # 4. Create archetype mapping
    archetype_mapping = create_archetype_mapping(n_clusters)
    
    # 5. Save cluster centroids
    centroids = save_cluster_centroids(gmm, pca, archetype_mapping)
    
    # 6. Analyze and visualize results
    cluster_probs = analyze_player_clusters(players_data, X_reduced, gmm, archetype_mapping)
    visualize_clusters(X_reduced, cluster_probs, gmm, archetype_mapping)
    
    print("NBA player clustering with GMM complete!")



