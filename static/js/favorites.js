
$(function () { // this is the jquery shortcut for document.ready()

    function addToProjects(evt) {

        var id = this.id; // this is the id on the button we clicked, which is the image's id
        var url = window.location.pathname;
        var info = url.split("/");
        var user_id = info[2];
        var stock_type = info[3];
        $.post("/add-to-project.json", {'id': id, 'user_id': user_id, 'stock_type': stock_type}, addToProjectsSuccess);
    }

    function addToProjectsSuccess(result) {

        console.log(result.status);

        var id = result.id;
        var url = window.location.pathname;
        var info = url.split("/");
        var user_id = info[2];

        $('#' + id).css('color', 'red'); // give our user some feedback
        $('.favorite-btn').attr("disabled", "disabled");
        alert("This fabric will be add to your new project.");
        window.location.replace("http://localhost:5000/user/" + user_id + "/projects")
    }

    $('.favorite-btn').click(addToProjects);

});