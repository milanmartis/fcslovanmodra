$(document).ready(function() {


var form = document.getElementById("form-team-id");

      var team_id=null;
      var score_scrap=null;
      var player_list_scrap=null;


document.getElementById("update-score-table").addEventListener("click", function () {

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


document.getElementById("score_scrap").addEventListener("input", function () {
  $('#update-score-table').val('Update');
});
document.getElementById("player_list_scrap").addEventListener("input", function () {
  $('#update-player-list').val('Update');
});
  
document.getElementById("update-player-list").addEventListener("click", function () {
  
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




    
    });