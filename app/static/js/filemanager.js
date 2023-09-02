$(document).ready(function() {
    $('#upload-form34').submit(function(e) {
        alert('kuk');
        e.preventDefault();

        let formData = new FormData(this);
        
        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                $('#message').text(response.message);
                if(response.file_path) {
                    // Update the displayed file path or reload the page or other UI actions.
                }
            },
            error: function(error) {
                $('#message').text("An error occurred.");
            }
        });
    });

    $('#delete-form').submit(function(e) {
        e.preventDefault();

        $.ajax({
            type: 'POST',
            url: $(this).attr('action'),
            success: function(response) {
                $('#message').text(response.message);
                if(!response.file_path) {
                    // Update the UI to indicate the file has been deleted or reload the page.
                }
            },
            error: function(error) {
                $('#message').text("An error occurred.");
            }
        });
    });
});