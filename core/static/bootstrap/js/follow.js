$("#id-follow").click(function(event){
    event.preventDefault();
    console.log("clicked");
    var div = $(this).closest("div");
    var value = $(this).val();
    console.log($(this).val())
})
/*
    $.ajax({
        url: div.attr("url-follow-attr"),
        dataType: "json",
        success: function(data) {
            if (value == "") {
                console.log("Success");
                $("#id-follow").val("Unfollow")
            } else {
                $("#id-follow").val("Follow")
            }

        }
    })
})















function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
*/
