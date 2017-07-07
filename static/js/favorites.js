$(function () { // this is the jquery shortcut for document.ready()

    function addToFavorites(evt) {

        var id = this.id; // this is the id on the button we clicked, which is the image's id

        $.post("/add-to-favorites", {'id': id}, addToFavoritesSuccess);
    }

    function addToFavoritesSuccess(result) {

        console.log(result.id);

        var id = result.id;

        $('#' + id).css('color', 'red'); // give our user some feedback
    }

    $('.favorite-btn').click(addToFavorites);

});