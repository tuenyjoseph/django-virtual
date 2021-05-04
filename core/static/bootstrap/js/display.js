/*$('#login-comment').on('submit', function(event){
  event.preventDefault();
  var form = $(this).closest("form");
  jsonData = {email : $('#usrname').val(), password : $('#pword').val()};
  $("#login-error-p").remove();
  $.ajax({
    url: form.attr("login-authenticate-url"),
    type: "POST",
//  data: JSON.stringify(jsonData),
    data: jsonData,
    dataType: "json",
    success: function(data){
      if (data.success == 'yes') {
          window.location.reload();
          $("#id_comment").focus();
      } else {
        $("#login-error").append(data.html_form);
        }
    }
  });
}); */
$('#login-modal-link').on('click', function(event){
  event.preventDefault();
  $('#login_hidden').remove();
  var form = $('#display-auth').closest('form');
  $.ajax({
    url: form.attr('login-authenticate-display-url'),
    type: "GET",
    success: function(data){
      var div = $('#hidden_col_id');
      div.append(data.html_form);
    }
  });
});

$('#display-auth').on('submit', function(event){
  event.preventDefault();
  $("#login-error-d").remove()
  var form = $(this).closest("form");
  $('#id_username').val($('#username').val());
  $('#id_password').val($('#password').val());
//  $('#login_hidden').submit();
  //  console.log($('#login_hidden').serialize());
  $.ajax({
      url: form.attr("login-authenticate-display-url"),
      type: "POST",
      data: $('#login_hidden').serialize(),
      dataType: "json",
      success: function(data){
        if (data.success == 'yes') {
          window.location.reload();
        } else if (data.success == 'no') {} {
          $("#display-auth").append(data.html_form);
          }
//      $('#login_hidden').remove();
      }
  });
});


