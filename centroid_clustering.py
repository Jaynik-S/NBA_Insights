from nba_api.stats.static import players
import career_stats as cs
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import numpy as np
import matplotlib.pyplot as plt
import json
import os
import pickle  # For saving and loading scaler and PCA

OUTPUT_FILE = "archetype_centroids.json"
SCALER_FILE = "scaler.pkl"
PCA_FILE = "pca.pkl"


if __name__ == "__main__":
    nba_players = ["LeBron James","Kevin Durant","Stephen Curry","Giannis Antetokounmpo","Nikola Jokić","Joel Embiid","Luka Dončić","James Harden","Damian Lillard","Jayson Tatum","Devin Booker","Kawhi Leonard","Paul George","Kyrie Irving","Jimmy Butler","Anthony Davis","Chris Paul","Trae Young","Donovan Mitchell","Bradley Beal","Ja Morant","Russell Westbrook","Karl-Anthony Towns","Draymond Green","Bam Adebayo","Rudy Gobert","Ben Simmons","Klay Thompson","Andrew Wiggins","Pascal Siakam","DeMar DeRozan","Zach LaVine","Brandon Ingram","Jaylen Brown","LaMelo Ball","Anthony Edwards","Domantas Sabonis","De'Aaron Fox","CJ McCollum","Khris Middleton","Jrue Holiday","Mikal Bridges","Steven Adams","Clint Capela","Myles Turner","Fred VanVleet","Kyle Lowry","Gordon Hayward","Julius Randle","Shai Gilgeous-Alexander","Darius Garland","Evan Mobley","Cade Cunningham","Tyrese Haliburton","RJ Barrett","Miles Bridges","Terry Rozier","Derrick Rose","Victor Oladipo","Malcolm Brogdon","Al Horford","Brook Lopez","Mitchell Robinson","Buddy Hield","Gary Trent Jr.","Michael Porter Jr.","Christian Wood","Spencer Dinwiddie","Caris LeVert","Eric Gordon","Derrick White","John Collins","Nikola Vučević","Aaron Gordon","Bojan Bogdanović","Marcus Smart","Lauri Markkanen","Robert Covington","Norman Powell","Serge Ibaka","Jarrett Allen","Seth Curry","Joe Ingles","Tim Hardaway Jr.","Reggie Jackson","Harrison Barnes","Jaren Jackson Jr.","Bogdan Bogdanović","Rui Hachimura","Kyle Kuzma","Jordan Clarkson","Richaun Holmes","D'Angelo Russell","Dejounte Murray","Keldon Johnson","Lonzo Ball","Coby White","Alex Caruso","Devin Vassell","James Wiseman","Deandre Ayton","Franz Wagner","Jordan Poole","Kevin Porter Jr.","Patrick Beverley","Doug McDermott","Davis Bertans","Kelly Olynyk","Daniel Gafford","Cam Reddish","Trey Murphy III","Kevin Love","De'Andre Hunter","Cameron Johnson","Markelle Fultz","Cole Anthony","Jalen Suggs","OG Anunoby","Scottie Barnes","Precious Achiuwa","Obi Toppin","Tyrese Maxey","Matisse Thybulle","Jalen Brunson","Kevin Huerter", "Alec Burks","Patrick Williams","Kentavious Caldwell-Pope","Moritz Wagner","Trey Lyles","Bennedict Mathurin","Jaden Ivey","Walker Kessler","Shaedon Sharpe","Jabari Smith Jr.","Jalen Green","Josh Giddey","Luguentz Dort","Kenrich Williams","Austin Reaves","Bones Hyland","Jamal Murray","Nikola Jović","Caleb Martin","Cody Martin","Grant Williams","Payton Pritchard","Gabe Vincent","Bobby Portis","DeAndre Jordan"]


    print(nba_players)

    cluster_num = 18
    players_id = []
    for player in nba_players:
        player_dict = players.find_players_by_full_name(player.strip())
        if player_dict:
            players_id.append(player_dict[0]['id'])
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

    # Save scaler and PCA for reuse
    with open(SCALER_FILE, "wb") as scaler_file:
        pickle.dump(scaler, scaler_file)

    with open(PCA_FILE, "wb") as pca_file:
        pickle.dump(pca, pca_file)

    # KMeans clustering
    kmeans = KMeans(n_clusters=cluster_num, random_state=42, init='k-means++')
    kmeans.fit(reduced_data)
    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_

    cluster_dict = {}
    for cluster_id in np.unique(labels):
        players_in_cluster = [nba_players[i] for i in range(len(labels)) if labels[i] == cluster_id]
        cluster_dict[f"Cluster_{cluster_id}"] = {
            "players": players_in_cluster,
            "centroid": centroids[cluster_id][:2].tolist()
        }

    custom_cluster_names = {
        0: "3-and-D Glue Wing",
        1: "Crafty Playmaking Guard",
        2: "All-Star Versatile Scorer",
        3: "Defensive Frontcourt Anchor",
        4: "High-Energy Play Finisher",
        5: "Specialist Role Player",
        6: "Elite Two-Way Leader",
        7: "Playmaking Facilitator",
        8: "Dynamic Shot Creator",
        9: "High-Impact Role Player",
        10: "Explosive Offensive Creator",
        11: "Statistical Unicorn",
        12: "Quiet Contributor",
        13: "Rebounding and Hustle Specialist",
        14: "High-Upside All-Around Talent",
        15: "Elite Rim Protector",
        16: "Mid-Range Scoring Specialist",
        17: "3-and-D Sniper"
    }

    archetype_centroid_dict = {}
    for cluster_id in np.unique(labels):
        custom_name = custom_cluster_names.get(cluster_id, f"Cluster_{cluster_id}")
        archetype_centroid_dict[custom_name] = cluster_dict[f"Cluster_{cluster_id}"]["centroid"]
        
    print(archetype_centroid_dict)

    with open(OUTPUT_FILE, "w") as json_file:
        json.dump(archetype_centroid_dict, json_file, indent=4)

    print("Centroid clustering complete and files saved.")


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



def single_player_coor(p_id):
    if not os.path.exists(SCALER_FILE) or not os.path.exists(PCA_FILE):
        print("Scaler or PCA file not found. Please run centroid_clustering.py first.")
        return []

    try:
        with open(SCALER_FILE, "rb") as scaler_file:
            scaler = pickle.load(scaler_file)

        with open(PCA_FILE, "rb") as pca_file:
            pca = pickle.load(pca_file)

        overall_df, shooting_df, finishing_df = cs.get_player_career_stats(p_id)
        full_stats = cs.merged_df(overall_df, shooting_df, finishing_df)
        numeric_stats = full_stats.select_dtypes(include=[np.number])

        if numeric_stats.empty:
            print("No numeric stats found for the player.")
            return []

        player_stats = numeric_stats.values.flatten()
        scaled_stats = scaler.transform([player_stats])
        reduced_stats = pca.transform(scaled_stats)

        return reduced_stats[0][:2].tolist()

    except Exception as e:
        print(f"Error processing player ID {p_id}: {e}")
        return []


