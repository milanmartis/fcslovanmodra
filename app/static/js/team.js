


var form = document.getElementById("form-team-id");

	var team_id=null;
	var score_scrap=null;
	var player_list_scrap=null;
	// const update_score_table = document.querySelector('#update-score-table');

	document.addEventListener('DOMContentLoaded', function () {
		function setupUpdateButton(buttonId, inputId) {
			const button = document.getElementById(buttonId);
			const input = document.getElementById(inputId);
	
			if (!button) return;
	
			button.addEventListener('click', function () {
				this.innerText = 'Loading...';
				this.disabled = true;
			});
	
			if (input) {
				input.addEventListener('input', function () {
					button.innerText = 'Update';
					button.disabled = false;
				});
			}
		}
	
		setupUpdateButton('update-score-table', 'score_scrap');
		setupUpdateButton('update-player-list', 'player_list_scrap');
		setupUpdateButton('update-events-results', 'events_results_scrap');
	
		const updatePlayerBtn = document.getElementById('update-player-list');
		if (updatePlayerBtn) {
			updatePlayerBtn.addEventListener('click', function () {
				if (typeof refreshNextMatchesSidebar === 'function') {
					refreshNextMatchesSidebar();
				}
			});
		}
	
		const updateScoreBtn = document.getElementById('update-score-table');
		if (updateScoreBtn) {
			updateScoreBtn.addEventListener('click', function () {
				if (window.parent) {
					window.parent.postMessage({ type: 'calendar-updated' }, '*');
				}
			});
		}
	});




