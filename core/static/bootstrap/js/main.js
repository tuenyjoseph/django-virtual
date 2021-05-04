$('#post-form').on('submit', function(event){
    event.preventDefault();
    var form = $(this).closest("form");
    jsonData = {comment : $('#id_comment').val(), slug : $('.title').attr('slug')};
    $.ajax({
        url: form.attr("data-validate-username-url"),
        type: "POST",
//        data: JSON.stringify(jsonData),
        data: jsonData,
        dataType: "json",
        success: function(data){
//            console.log(data);
 //           console.log(data.comment);
            $("#jscomment").prepend(data.html_form);
            $('#id_comment').val('');
            }
      })
  });

$('.js-reply').on('click', function(event){
    event.preventDefault();
    $("#js-reply-post").remove();
    var form = $(this).closest("p");
    $.ajax({
        url: form.attr("form-reply-url"),
        type: "GET",
        dataType: "json",
        success: function(data){
            var commentpk = data.pk;
            var div = $("#" + commentpk).closest("div");
             div.append(data.html_form)

        }
    })
});

$(".js-delete-comment").on('click', function(event){
    event.preventDefault();
    var p = $(this).closest("p");
    $.ajax({
        url: p.attr("comment-delete-url"),
        type: "GET",
        dataType: "json",
        success: function(data){
            p.remove()
        }
    })
})

$(".js-delete-comment-parent").on('click', function(event){
    event.preventDefault();
    var p = $(this).closest("p");
    var div = $(this).closest("div");
    $.ajax({
        url: p.attr("comment-delete-url"),
        type: "GET",
        dataType: "json",
        success: function(data){
            div.remove()
        }
    })
})

$(".js-is-writer").on('click', function(event){
      console.log('starting')
      event.preventDefault();
      var div = $(this).closest("div");
      var act = $(this)
      console.log("done");
      $.ajax({
        url: div.attr("is-writer-url"),
        type: "GET",
        dataType: "json",
        success: function(data){
          console.log("type");
          $(".js-is-writer").text(data.value);
          $(".writer-not-writer").text(data.writer);
          console.log(data.value);
        }
      })
    });
/*$(function() {
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i=0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    function csrfSafeMethod(method) {
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        var host = document.location.host;
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') || */
//            !(/^(\/\/|http:|https:).*/.test(url));
/*    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
}); */

/*$(function() {


    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    /*
    The functions below will create a header with csrftoken
    */

 /*   function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
/*    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.   */
//            !(/^(\/\/|http:|https:).*/.test(url));
/*    }

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

});
*/
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
