$(document).ready(function() {
    $('.results.no-login a.open-file').on('click', function(e) {
        alert('You need to login first, before you can open files from your browser.');
        e.preventDefault();
    })
})
