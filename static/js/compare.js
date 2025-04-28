function addPlayerInput() {
    const playerContainer = document.getElementById('players-container');
    const playerCount = playerContainer.children.length;
    
    if (playerCount >= 5) {
        alert("Maximum 5 players can be compared at once.");
        return;
    }
    
    const playerNum = playerCount + 1;
    const playerDiv = document.createElement('div');
    playerDiv.className = 'column';
    playerDiv.innerHTML = `
        <label for="player${playerNum}_name">Enter Player ${playerNum} Name:</label>
        <input type="text" id="player${playerNum}_name" name="player${playerNum}_name" placeholder="e.g., Player ${playerNum}" ${playerNum <= 2 ? 'required' : ''}>
        ${playerNum > 2 ? '<button type="button" class="remove-btn" onclick="removePlayerInput(this)">Remove</button>' : ''}
    `;
    
    playerContainer.appendChild(playerDiv);
    
    // Hide the "Add Another Player" button if we've reached 5 players
    if (playerContainer.children.length >= 5) {
        document.getElementById('addPlayerButton').style.display = 'none';
    }
}

function removePlayerInput(button) {
    const playerDiv = button.parentNode;
    const playerContainer = playerDiv.parentNode;
    playerContainer.removeChild(playerDiv);
    
    // Renumber the remaining players
    const playerDivs = playerContainer.children;
    for (let i = 0; i < playerDivs.length; i++) {
        const inputs = playerDivs[i].getElementsByTagName('input');
        const labels = playerDivs[i].getElementsByTagName('label');
        
        if (inputs.length > 0 && labels.length > 0) {
            const playerNum = i + 1;
            inputs[0].id = `player${playerNum}_name`;
            inputs[0].name = `player${playerNum}_name`;
            labels[0].htmlFor = `player${playerNum}_name`;
            labels[0].textContent = `Enter Player ${playerNum} Name:`;
        }
    }
    
    // Show the "Add Another Player" button again
    document.getElementById('addPlayerButton').style.display = 'inline-block';
}
