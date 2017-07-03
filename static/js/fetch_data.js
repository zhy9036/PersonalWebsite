$(document).ready(function() {
    fetch();
    setInterval(fetch, 60*1000);
});

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
                        {"class": "list-group-item list-group-item-info",
                         "href" : obj.pk
                         });
                    a_tag.html("<Strong>" + obj.fields.projectName + "</Strong>")
                    var div = $("<div>", {"class":"text-right"})
                    var sub_tag = $("<a>", {"href" : obj.fields.projectUrl, "target": "_blank",
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