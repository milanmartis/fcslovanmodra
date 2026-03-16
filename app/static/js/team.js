


var form = document.getElementById("form-team-id");

	var team_id=null;
	var score_scrap=null;
	var player_list_scrap=null;
	// const update_score_table = document.querySelector('#update-score-table');

	document.addEventListener('DOMContentLoaded', function() {
		const updateScoreBtn = document.querySelector('#update-score-table');
		if (updateScoreBtn) {
		  updateScoreBtn.addEventListener('click', function() {
			this.innerText = 'Loading...';
			this.disabled = true;
		  });
		}
	  
		const updatePlayerBtn = document.querySelector('#update-player-list');
		if (updatePlayerBtn) {
		  updatePlayerBtn.addEventListener('click', function() {
			this.innerText = 'Loading...';
			this.disabled = true;
		  });
		}
	  
		const scoreScrap = document.getElementById('score_scrap');
		if (scoreScrap && updateScoreBtn) {
		  scoreScrap.addEventListener('input', function () {
			updateScoreBtn.innerText = 'Update';
			updateScoreBtn.disabled = false;
		  });
		}
	  
		const playerListScrap = document.getElementById('player_list_scrap');
		if (playerListScrap && updatePlayerBtn) {
		  playerListScrap.addEventListener('input', function () {
			updatePlayerBtn.innerText = 'Update';
			updatePlayerBtn.disabled = false;
		  });
		}
	  });




