function updateStats(seasonId) {
    const stats = JSON.parse(document.getElementById('player_stats').textContent);
    const columns = JSON.parse(document.getElementById('player_columns').textContent);
    const seasonStats = stats.find(stat => stat.SEASON_ID === seasonId);
    const statsDiv = document.getElementById('season_stats');
    statsDiv.innerHTML = '<table class="stats-table"><thead><tr><th>Stat</th><th>Value</th></tr></thead><tbody></tbody></table>';
    const tbody = statsDiv.querySelector('tbody');
    columns.forEach(column => {
        if (seasonStats[column] !== undefined) {
            tbody.innerHTML += `<tr><td><strong>${column}</strong></td><td>${seasonStats[column]}</td></tr>`;
        }
    });
}

// Initialize panzoom functionality when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    const elem = document.getElementById('cluster-visualization');
    if (elem) {
        const panzoomInstance = panzoom(elem, {
            maxZoom: 10,
            minZoom: 1, // Changed from 0.5 to 1 to prevent zooming out smaller than default
            bounds: true,
            boundsPadding: 0.1
        });
        
        // Add reset button functionality with correct methods
        document.getElementById('reset-zoom').addEventListener('click', function() {
            // Reset position to (0,0) and zoom level to 1 (original scale)
            panzoomInstance.moveTo(0, 0);
            panzoomInstance.zoomAbs(0, 0, 1);
        });
        
        // Information about panning
        elem.addEventListener('mouseenter', function() {
            document.getElementById('zoom-instructions').style.opacity = "1";
        });
        
        elem.addEventListener('mouseleave', function() {
            document.getElementById('zoom-instructions').style.opacity = "0.5";
        });
    }
});
