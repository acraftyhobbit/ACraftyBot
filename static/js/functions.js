
function calendarDisplay() {
    var x = document.getElementById('caleandar');
    if (x.style.display === 'none') {
        x.style.display = 'block';
    } else {
        x.style.display = 'none';
    }
}

function projectDisplay() {
    var x = document.getElementById('projects');
    if (x.style.display === 'none') {
        x.style.display = 'block';
    } else {
        x.style.display = 'none';
    }
}

function incompleteDisplay() {
    var x = document.getElementById('in_progress');
    if (x.style.display === 'none') {
        x.style.display = 'block';
    } else {
        x.style.display = 'none';
    }
}

$('.select').click(function() {
  $( "input:checkbox" ).toggle();
  $( ".delete" ).toggle();
});
$(function () {
    $(".delete").click(deleteProjects);

    function deleteProjects(evt) {
        

        var id = this.id;
        var url = window.location.pathname;
        var info = url.split("/");
        var user_id = info[2];
        console.log(id);
        $.post("/delete-project.json", {'id': id, 'user_id': user_id}, removeProjectsSuccess);
    }

    function removeProjectsSuccess(result) {

        console.log(result.status);
        console.log(result.id);
        var id = result.id;
        
        // $("#" + id).remove();
    }

});
  
$('.delete').click(function (){
   var answer = confirm("Are you sure?");
      if (answer) {
         return true;
      }else{
         return false;
      }
});