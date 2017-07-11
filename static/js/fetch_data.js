$(document).ready(function() {
    var url = window.location.href;
    if(url == 'http://127.0.0.1:8000/panel/'){
        fetch();
        setInterval(fetch, 10*60*1000);
    }else{
        check_runner();
    }
});

function check_runner() {
    var url = window.location.href;

    $.ajax({
        type: "RUNNER",
        url: url,
        dataType: 'json',
        success: function(data){
            $('#dropdown').html("");
            data.forEach(
                function(obj){
                    var li = $("<li>");
                    var a_tag = $("<a>",
                        {
                         "href" : 'reg_runner/' + obj.id
                         });
                    a_tag.html(obj.name);
                    li.append(a_tag);
                    $("#dropdown").append(li);
                }
            );
            //$('#project_list').html(data);
        }
    });
}


function fetch() {
    $('#loading_img').show();
    $.ajax({
        url:$("#project_list").attr("data-ajax-target"),
        dataType: 'json',
        success: function(data){
            data1 = JSON.parse(data)
            //alert(data);
            /**  Sample JSON response
            [
            {"model": "home.projects", "pk": "",
                "fields": {"user": 5, "projectName": "test3", "projectToken": ""}},
            {"model": "home.projects", "pk": "1",
                "fields": {"user": 5, "projectName": "test3", "projectToken": ""}},
            {"model": "home.projects", "pk": "2",
                "fields": {"user": 5, "projectName": "test3", "projectToken": ""}},
            ]

            */

            //alert("json: " + data1[0].fields.projectName);
            $('#project_list').html("");
            data1.forEach(
                function(obj){
                    var a_tag = $("<a>",
                        {"class": "list-group-item",
                         "href" : obj.pk
                         });
                    a_tag.html("<Strong>" + obj.fields.projectName + "</Strong>")
                    var div = $("<div>", {"class":"text-right"})
                    var sub_tag = $("<a>", {"href" : obj.fields.webUrl, "target": "_blank",
                                    "class": "text-right"})
                    sub_tag.html("Open in Gitlab");
                    div.append(sub_tag)
                    a_tag.append(div);
                   $("#project_list").append(a_tag);
                }
            );
            //$('#project_list').html(data);
        },
        complete: function() {
            $('#loading_img').hide();
        }
    });
}