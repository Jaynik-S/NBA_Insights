function updateStats(playerId, seasonId) {
    const stats = JSON.parse(document.getElementById(`player${playerId}_stats`).textContent);
    const columns = JSON.parse(document.getElementById(`player${playerId}_columns`).textContent);
    const seasonStats = stats.find(stat => stat.SEASON_ID === seasonId);
    const statsDiv = document.getElementById(`player${playerId}_season_stats`);
    statsDiv.innerHTML = '<table class="stats-table"><thead><tr><th>Stat</th><th>Value</th></tr></thead><tbody></tbody></table>';
    const tbody = statsDiv.querySelector('tbody');
    columns.forEach(column => {
        if (seasonStats[column] !== undefined) {
            tbody.innerHTML += `<tr><td><strong>${column}</strong></td><td class="player${playerId}_stat" data-column="${column}">${seasonStats[column]}</td></tr>`;
        }
    });

    // Highlight comparison logic after all stats are loaded
    highlightComparison();
}

function highlightComparison() {
    // Get all column names from the first player (assuming they're the same across players)
    const firstPlayerColumns = JSON.parse(document.getElementById('player1_columns').textContent);
    const playerCount = parseInt(document.getElementById('player_count').textContent);
    
    // Columns to exclude from highlighting
    const excludeColumns = ['SEASON_ID', 'TEAM_ABBREVIATION', 'PLAYER_AGE'];
    
    // For each column/stat
    firstPlayerColumns.forEach(column => {
        // Skip excluded columns
        if (excludeColumns.includes(column)) return;
        
        // Get all cells for this column across all players
        const cellsByColumn = [];
        for (let i = 1; i <= playerCount; i++) {
            const cells = document.querySelectorAll(`.player${i}_stat[data-column="${column}"]`);
            if (cells.length > 0) {
                cellsByColumn.push({
                    index: i,
                    cell: cells[0],
                    value: parseFloat(cells[0].textContent) || 0
                });
            }
        }
        
        // Remove previous highlights
        cellsByColumn.forEach(item => item.cell.classList.remove('highlight'));
        
        // Find the highest value for this column
        if (cellsByColumn.length > 0) {
            const maxValue = Math.max(...cellsByColumn.map(item => item.value));
            // Highlight cells with the max value
            cellsByColumn.filter(item => item.value === maxValue).forEach(item => {
                item.cell.classList.add('highlight');
            });
        }
    });
}

function updateChart(statCategory) {
    // Get all player data
    const playerCount = parseInt(document.getElementById('player_count').textContent);
    const players = {};
    const allSeasons = new Set();
    
    // Extract data for all players and gather all seasons
    for (let i = 1; i <= playerCount; i++) {
        const stats = JSON.parse(document.getElementById(`player${i}_stats`).textContent);
        const playerName = document.querySelector(`.stats-column:nth-child(${i}) h2`).textContent.trim();
        players[i] = { 
            name: playerName, 
            stats: stats,
            seasonData: {}
        };
        
        // Extract all seasons for this player
        stats.forEach(season => {
            const seasonYear = season.SEASON_ID;
            allSeasons.add(seasonYear);
            players[i].seasonData[seasonYear] = season[statCategory] || 0;
        });
    }
    
    // Convert to array and sort seasons chronologically
    const sortedSeasons = Array.from(allSeasons).sort();
    
    // Create dataset for chart
    const datasets = [];
    const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF'];
    
    Object.keys(players).forEach((playerId, index) => {
        const player = players[playerId];
        const data = sortedSeasons.map(season => 
            player.seasonData[season] !== undefined ? player.seasonData[season] : 0
        );
        
        datasets.push({
            label: player.name,
            data: data,
            borderColor: colors[index % colors.length],
            backgroundColor: 'transparent',
            pointBackgroundColor: colors[index % colors.length],
            tension: 0.1
        });
    });
    
    // Get the canvas element
    const ctx = document.getElementById('statsChart').getContext('2d');
    
    // Destroy previous chart if it exists
    if (window.statsLineChart) {
        window.statsLineChart.destroy();
    }
    
    // Create the chart
    window.statsLineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sortedSeasons,
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: `${statCategory} Comparison`,
                    font: {
                        size: 16
                    }
                },
                legend: {
                    position: 'top',
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                },
                zoom: {
                    zoom: {
                        wheel: {
                            enabled: true,
                            speed: 0.1,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'xy',
                    },
                    pan: {
                        enabled: true,
                        mode: 'xy',
                    },
                    limits: {
                        y: {min: 'original', max: 'original', minRange: 1}
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: statCategory
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Season'
                    }
                }
            }
        }
    });
}

// Initialize chart with default stat category when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Get first valid category from dropdown
    const dropdown = document.getElementById('statCategorySelect');
    if (dropdown && dropdown.options.length > 0) {
        updateChart(dropdown.options[0].value);
    }
    // Initial highlight after page load and potential initial stats update
    highlightComparison(); 
});
