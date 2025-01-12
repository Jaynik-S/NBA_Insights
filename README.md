# NBA Player Archetype Finder

## Project Overview
The NBA Player Archetype Finder is a web application designed to classify NBA players into predefined archetypes based on their career statistics. This application leverages the `nba_api` to fetch player data, applies advanced data preprocessing techniques, and uses clustering algorithms to assign archetypes. The results include a graphical visualization of the player's coordinates and archetype centroids.

---

## Features
- **Player Search**: Users can input the name of any NBA player to find their archetypes.
- **Archetype Identification**: Automatically calculates a player's archetypes by comparing their statistics with predefined archetype centroids.
- **Multiple Archetypes**: Displays up to three archetypes for a player, depending on proximity to centroids.
- **Visualization**: Provides a graph showing the player's coordinates and archetype centroids.
- **Caching Mechanism**: Reduces API calls by caching player statistics for efficiency.

---

## How It Works
1. **Data Fetching**: The application retrieves player statistics using the `nba_api`.
2. **Data Processing**: Preprocessed statistics are transformed into normalized feature vectors using a trained scaler and PCA model.
3. **Clustering**: Predefined clusters and centroids are loaded from a JSON file generated via `centroid_clustering.py`.
4. **Distance Calculation**: Euclidean distances between a player's coordinates and archetype centroids are computed.
5. **Archetype Assignment**: Archetypes are assigned based on the closest centroids. A maximum of three archetypes is displayed if the distances meet a defined threshold.
6. **Visualization**: A graph is generated to visualize the player's coordinates relative to archetype centroids.

---

## Technical Details
- **Flask**: Used for web development and routing.
- **nba_api**: Facilitates retrieval of NBA player statistics.
- **Clustering**: Archetypes and centroids are calculated using K-Means clustering, implemented in `centroid_clustering.py`.
- **Visualization**: Graphs are generated using Matplotlib to depict clustering results.
- **Data Storage**:
  - Predefined centroids are stored in `data/archetype_centroids.json`.
  - Scaler and PCA models are serialized in `data/scaler.pkl` and `data/pca.pkl`.

---

## Example Usage

### User Steps
1. **Enter Player Name**: Go to the homepage and type the player's name in the input field (e.g., *LeBron James*).
2. **View Archetypes**: The application processes the input and displays the player's archetypes (e.g., *Elite Two-Way Leader, Statistical Unicorn*).
3. **Graph Visualization**: A visualization is generated showing the player's position relative to archetype centroids.

### Sample Output
- **Player Name**: LeBron James  
- **Archetypes**: Elite Two-Way Leader, All-Star Versatile Scorer, Playmaking Facilitator  
- **Visualization**: *(Generated graph showing player position relative to archetypes)*

---

## How to Customize

### Adding New Archetypes
- Modify `centroid_clustering.py` to include new clustering parameters and regenerate clusters.

### Adjusting Parameters
- Update the threshold distance (`THRESHOLD_DISTANCE`) or maximum archetypes (`MAX_ARCHETYPES`) in `app.py`.

---

## Contributing
Contributions are welcome! Submit issues or pull requests to improve functionality or add new features.

---

## License
This project is licensed under the MIT License. See the LICENSE file for details.

---

## Acknowledgements
- **nba_api**: For providing easy access to NBA data.
- **Flask**: For the web framework.
- **Matplotlib**: For creating visualizations.

Feel free to reach out if you have questions or need assistance setting up the project!
