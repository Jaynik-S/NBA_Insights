from nba_api.stats.static import players
from collections import defaultdict
import career_stats as cs
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt

nba_players = ["LeBron James","Kevin Durant","Stephen Curry","Giannis Antetokounmpo","Nikola Jokić","Joel Embiid","Luka Dončić","James Harden","Damian Lillard","Jayson Tatum","Devin Booker","Kawhi Leonard","Paul George","Kyrie Irving","Jimmy Butler","Anthony Davis","Chris Paul","Trae Young","Donovan Mitchell","Bradley Beal","Ja Morant","Russell Westbrook","Karl-Anthony Towns","Draymond Green","Bam Adebayo","Rudy Gobert","Ben Simmons","Klay Thompson","Andrew Wiggins","Pascal Siakam","DeMar DeRozan","Zach LaVine","Brandon Ingram","Jaylen Brown","LaMelo Ball","Anthony Edwards","Domantas Sabonis","De'Aaron Fox","CJ McCollum","Khris Middleton","Jrue Holiday","Mikal Bridges","Steven Adams","Clint Capela","Myles Turner","Fred VanVleet","Kyle Lowry","Gordon Hayward","Julius Randle","Shai Gilgeous-Alexander","Darius Garland","Evan Mobley","Cade Cunningham","Tyrese Haliburton","RJ Barrett","Miles Bridges","Terry Rozier","Derrick Rose","Victor Oladipo","Malcolm Brogdon","Al Horford","Brook Lopez","Mitchell Robinson","Buddy Hield","Gary Trent Jr.","Michael Porter Jr.","Christian Wood","Spencer Dinwiddie","Caris LeVert","Eric Gordon","Derrick White","John Collins","Nikola Vučević","Aaron Gordon","Bojan Bogdanović","Marcus Smart","Lauri Markkanen","Robert Covington","Norman Powell","Serge Ibaka","Jarrett Allen","Seth Curry","Joe Ingles","Tim Hardaway Jr.","Reggie Jackson","Harrison Barnes","Jaren Jackson Jr.","Bogdan Bogdanović","Rui Hachimura","Kyle Kuzma","Jordan Clarkson","Richaun Holmes","D'Angelo Russell","Dejounte Murray","Keldon Johnson","Lonzo Ball","Coby White","Alex Caruso","Devin Vassell","James Wiseman","Deandre Ayton","Franz Wagner","Jordan Poole","Kevin Porter Jr.","Patrick Beverley","Doug McDermott","Davis Bertans","Kelly Olynyk","Daniel Gafford","Cam Reddish","Trey Murphy III","Kevin Love","De'Andre Hunter","Cameron Johnson","Markelle Fultz","Cole Anthony","Jalen Suggs","OG Anunoby","Scottie Barnes","Precious Achiuwa","Obi Toppin","Tyrese Maxey","Matisse Thybulle","Jalen Brunson","Kevin Huerter", "Alec Burks","Patrick Williams","Kentavious Caldwell-Pope","Moritz Wagner","Trey Lyles","Bennedict Mathurin","Jaden Ivey","Walker Kessler","Shaedon Sharpe","Jabari Smith Jr.","Jalen Green","Josh Giddey","Luguentz Dort","Kenrich Williams","Austin Reaves","Bones Hyland","Jamal Murray","Nikola Jović","Caleb Martin","Cody Martin","Grant Williams","Payton Pritchard","Gabe Vincent","Bobby Portis","DeAndre Jordan"]


print(nba_players)
cluster_num = 18

players_id = []
for player in nba_players:
    clean_player_name = player.split(' (')[0].strip()
    player_dict = players.find_players_by_full_name(clean_player_name)
    if player_dict:
        player_id = player_dict[0]['id']
        players_id.append(player_id)
    else:
        print(f"Player not found: {player}")

players_data = []
expected_feature_count = None

for p_id in players_id:
    try:
        one, two, three = cs.get_player_career_stats(p_id)
        full_stats = cs.merged_df(one, two, three)
        numeric_stats = full_stats.select_dtypes(include=[np.number])
        if not numeric_stats.empty:
            if expected_feature_count is None:
                expected_feature_count = numeric_stats.values.flatten().shape[0]
            players_data.append(numeric_stats.values.flatten())
        else:
            players_data.append(np.zeros(expected_feature_count))
    except Exception as e:
        print(f"Error fetching data for player ID {p_id}: {e}")
        players_data.append(np.zeros(expected_feature_count))

players_array = np.array([row if len(row) == expected_feature_count else np.zeros(expected_feature_count) for row in players_data])
players_array = np.nan_to_num(players_array)

# Scale the data
scaler = StandardScaler()
scaled_data = scaler.fit_transform(players_array)

# Dimensionality reduction
pca = PCA(n_components=0.95)  # Retain 95% variance
reduced_data = pca.fit_transform(scaled_data)

# Set number of clusters to 20+
kmeans = KMeans(n_clusters=cluster_num, random_state=42, init='k-means++')
kmeans.fit(reduced_data)
labels = kmeans.labels_
centroids = kmeans.cluster_centers_

cluster_dict = {}
for cluster_id in np.unique(labels):
    players_in_cluster = [nba_players[i] for i in range(len(labels)) if labels[i] == cluster_id]
    cluster_dict[f"Cluster_{cluster_id}"] = players_in_cluster

# for cluster_id in np.unique(labels):
#     players_in_cluster = [nba_players[i] for i in range(len(labels)) if labels[i] == cluster_id]
#     centroid_coords = reduced_centroids[cluster_id].tolist()
#     cluster_dict[f"Cluster_{cluster_id}"] = [players_in_cluster, centroid_coords]


print(cluster_dict)

# Visualize clusters
plt.figure(figsize=(12, 8))
plt.scatter(reduced_data[:, 0], reduced_data[:, 1], c=labels, cmap='viridis', alpha=0.7, s=100)
plt.scatter(centroids[:, 0], centroids[:, 1], c='red', marker='x', s=200, label='Centroids')
plt.title("NBA Player Clustering", fontsize=16)
plt.xlabel("Principal Component 1", fontsize=14)
plt.ylabel("Principal Component 2", fontsize=14)
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Create a cluster dictionary



# Show the plot
plt.show()



