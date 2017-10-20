function clearErrors() {
    $( ".form-control-feedback" ).empty();
}

function showErrors(errors) {
    clearErrors();
    if (typeof(errors) == "string") {
        $(".form-email-error").append(errors);
    }
    else {
        for (var field in errors) {
            if (!errors.hasOwnProperty(field))
                continue;
            var err = errors[field];
            for (var error in err ) {
                var errorElem = $(".form-" + field + "-error");
                errorElem.append(err[error]);
                errorElem.parents('.form-group').addClass('has-danger');
            }
        }
    }
}

function urlParam(name){
    var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
    if (results==null){
       return null;
    }
    else{
       return results[1] || 0;
    }
}
