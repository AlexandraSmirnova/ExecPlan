$(document).ready(function () {
    $('#js-reg-form').submit(function (event) {
        event.preventDefault();
        clearErrors();
        
        $.post($(this).attr('action'), $(this).serialize())
            .done(function (response) {
                console.log(response);
                if (response.status === 'OK') {
                    $('.js-reg-success').show();
                    $('#js-reg-form').hide()
                } else if(response.status === 'ERROR') {
                    showErrors(response.errors);
                }
            }).fail(function (xhr, responseText) {
        });
    });
});
