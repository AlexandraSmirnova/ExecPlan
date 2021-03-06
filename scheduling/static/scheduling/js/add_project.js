$(document).ready( function () {
    $('#js-add-project-form').submit(function (event) {
        event.preventDefault();
        clearErrors();
        $.post($(this).attr('action'), $(this).serialize())
            .done(function (response) {
                console.log(response);
                if (response.status === 'OK') {
                    var next = urlParam('next');

                	if (next) {
                		location.replace(next);
                	} else {
                		location.replace(response.success_url);
                	}
                } else if(response.status === 'ERROR') {
                    showErrors(response.errors);
                }
            }).fail(function (xhr, responseText) {
        });
    });
});