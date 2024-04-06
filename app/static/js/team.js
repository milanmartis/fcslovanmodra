


var form = document.getElementById("form-team-id");

	var team_id=null;
	var score_scrap=null;
	var player_list_scrap=null;
	// const update_score_table = document.querySelector('#update-score-table');

  document.addEventListener('DOMContentLoaded', function() {
    var update_score_table = document.querySelector('#update-score-table');
    if (update_score_table) {
      update_score_table.addEventListener('click', function() {

		$('#update-score-table').val('Loading...');
		team_id = $('#team_id').val();
	score_scrap = $('#score_scrap').val();
	$.ajax({
		url:"/teams/"+team_id+"/update",
		type:"POST",
		data:{what:'table', score_scrap:score_scrap, team:team_id},
		success:function()
		{
			$('#update-score-table').val('Updated');

			$('#info-updated').modal('show');
			setTimeout(function(){
				$('#info-updated').modal("hide");

		}, 2500);
		}
		});
	});
}

var score_scrap = document.getElementById('score_scrap');

if (score_scrap) {
score_scrap.addEventListener("input", function () {
	$('#update-score-table').val('Update');
});
}

var player_list_scrap = document.getElementById('player_list_scrap');
if (player_list_scrap) {
player_list_scrap.addEventListener("input", function () {
	$('#update-player-list').val('Update');
});
}


const update_player_list = document.querySelector('#update-player-list');
if (player_list_scrap) {
  update_player_list.addEventListener("click", function () {

	$('#update-player-list').val('Loading...');
	team_id = $('#team_id').val();
	player_list_scrap = $('#player_list_scrap').val();

	$.ajax({
		url:"/teams/"+team_id+"/update",
		type:"POST",
		data:{what:'table', player_list_scrap:player_list_scrap, team:team_id},
		success:function()
		{
			$('#update-player-list').val('Updated');

			$('#info-updated').modal('show');
			setTimeout(function(){
			$('#info-updated').modal("hide");

		}, 2500);
		}
		});
	});
}
});




