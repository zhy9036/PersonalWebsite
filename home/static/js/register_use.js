var validateName = false;
var validatePass = false;
function checkUsername() {
    var username = $("#username").val();
    //alert("username " + username);
    if(username){
      $.ajax({
        url: '/validate_username/',
        data: {
          'username': username
        },
        dataType: 'json',
        success: function (data) {
          if (data.is_taken) {
            $("#status").css({'color':'light_green', 'font-size': '16px'});
            $("#status").html("Unavailable, username already exists.");
            validateName = false;
          }else{
            $("#status").css({'color':'white', 'font-size': '16px'});
            $("#status").html("Available");
            validateName = true;
          }
        }
      });
    }else{
    $("#status").html("");
    }

}

function matchPassword(){
    var pass1 = $("#pass1").val();
    var pass2 = $("#pass2").val();
    if(pass1 != pass2){
        $("#status1").css({'color':'red', 'font-size': '20px'});
        $("#status1").html("Password doesn't match.");
        validatePass = false
    }else{
        $("#status1").html("");
        validatePass = true

    }
}

$(document).ready(function() {
    $("#username").keyup(checkUsername);
    $("#pass2").keyup(matchPassword);
    $("#subBtn").click(function(event) {
        if(validatePass && validateName){
            $(this).submit();
        }else{
            event.preventDefault();
            alert("Wrong info");
        }
    });
});