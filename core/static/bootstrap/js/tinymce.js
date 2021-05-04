$('#post-tinymce').on('submit', function(event){
    event.preventDefault();
    var form = $('#post-tinymce');
    jsonData = {content : $('#id_content').val()}
    $.ajax({
        url: form.attr("data-validate-username-url"),
        type: "POST",
        data: jsonData,
        dataType: "json",
        success: function(data){
            $('#content').append(data.html_form);
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

var custom_file_picker = function(cb, value, meta) {
    console.log('started');
    var input = document.createElement('input');
    input.setAttribute('type', 'file');
    input.setAttribute('accept', 'image/*');

    input.onchange = function() {
        var fil = this.files[0];
        var file = document.querySelector("#id_picture");
        file.value = fil;
        var reader = new FileReader();

        reader.onload = function () {
            var id = 'blobid' + (new Date()).getTime();
            var blogCache = tinymce.activeEditor.editorUpload.blobCache;
            var base64 = reader.result.split(',')[1];
            var blobInfo = blobCache.create(id, file, base64);
            blobCache.add(blobInfo);

        };
        reader.readAsDataURL(fil);
    };
    input.click();
};
