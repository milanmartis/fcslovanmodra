$(document).ready(function() {


var form = document.getElementById("form-team-id");

      var team_id=null;
      var score_scrap=null;
      var player_list_scrap=null;


document.getElementById("update-score-table").addEventListener("click", function () {

      team_id = $('#team_id').val();
      score_scrap = $('#score_scrap').val();

      $.ajax({
        url:"/teams/"+team_id+"/update",
        type:"POST",
        data:{what:'table', score_scrap:score_scrap, team:team_id},
        success:function()
        {
          
          $('#info-updated').modal('show');
          setTimeout(function(){
          $('#info-updated').modal("hide");
        
        }, 2500);
        }
        });
    });

document.getElementById("update-player-list").addEventListener("click", function () {

      team_id = $('#team_id').val();
      player_list_scrap = $('#player_list_scrap').val();

      $.ajax({
        url:"/teams/"+team_id+"/update",
        type:"POST",
        data:{what:'table', player_list_scrap:player_list_scrap, team:team_id},
        success:function()
        {
          
          $('#info-updated').modal('show');
          setTimeout(function(){
          $('#info-updated').modal("hide");
        
        }, 2500);
        }
        });
    });




    
    });