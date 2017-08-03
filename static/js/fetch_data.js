$(document).ready(function() {
    fetch();
    setInterval(fetch, 10*60*1000);
    last_job();
    setInterval(last_job, 10*60*1000);
    check_runner();
});

function last_job(){
    $.ajax({
        url: $("#last_job").attr("data-ajax-target"),
        dataType: 'json',
        success: function(data){
            data = JSON.parse(data);
            $("#last_job").html("");
            if(data == ''){
                var div_tag = $("<div>",{"class" : 'alert alert-success'});
                var i_tag = $("<i>",{"class" : 'fa fa-info-circle'});
                i_tag.html("<Strong style='font-family: sans-serif;'> No previous job yet! </Strong>");
                div_tag.append(i_tag);
                $("#last_job").append(div_tag);
            }else{
                var des = data[0].fields.description;
                if (des.includes("success")){
                    var div_tag = $("<div>",{"class" : 'alert alert-info'});
                    var i_tag = $("<i>",{"class" : 'fa fa-check'});
                    i_tag.html("<Strong style='font-family: sans-serif;'> Last " + des + "</Strong>");
                    div_tag.append(i_tag);
                    $("#last_job").append(div_tag);
                }else{
                    var div_tag = $("<div>",{"class" : 'alert alert-danger'});
                    var i_tag = $("<i>",{"class" : 'fa fa-info-circle'});
                    i_tag.html("<Strong style='font-family: sans-serif;'> Last " + des + "</Strong> ");
                    var a_tag = $("<button>",{"id" : 'retry_a', "class": "btn btn-success",
                                "data-toggle": "modal", 'data-target': "#myModal"});
                    a_tag.html("Restart CI");
                    div_tag.append(i_tag);
                    div_tag.append(a_tag);
                    $("#last_job").append(div_tag);
                    $("#retry_a").on('click', function(){
                        $.ajax({
                            type: "POST",
                            url: 'retry_job/',
                            data: "",
                            dataType: 'json',
                            success: retry_pipeline,
                        });
                    });
                }
            }
        }
    });
}

function retry_pipeline(){
    var interval_id = setInterval(
        function(){
            $.ajax({
                type: "GET",
                url: 'retry_job/',
                dataType: 'json',
                success: function(data){
                    var json_verify = false;
                    try{
                        ('id' in data);
                        json_verify = true;
                    }catch(e){
                        json_verify = false;
                    }
                    if(!json_verify){
                        clearInterval(interval_id);
                        $("#loading_img1").hide();
                        $("#job_result").html(data);
                    }else{
                        if(data['status'] == 'failed' ||data['status'] == 'success'){
                            clearInterval(interval_id);
                            $("#loading_img1").hide();
                            $("#job_status").html('preparing');
                            $("#job_result").html(data['status'] + " " + data['id']);
                        }else{
                            $("#job_status").html(data['status']);
                        }
                    }
                }
            });
        }
    , 2000);
}

function check_runner() {
    var url = window.location.href;
    $.ajax({
        type: "RUNNER",
        url: url,
        dataType: 'json',
        success: function(data){
            $('#dropdown').html("");
            if(data.length > 0){
                $('#runner_list').show();
                $('#register_runner').hide();
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
            }else{
                $('#register_runner').show();
                $('#runner_list').hide();

            }
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
    }),

    // Fetch log
    $.ajax({
        url:$("#log_list").attr("data-ajax-target"),
        dataType: 'json',
        success: function(data){
            data = JSON.parse(data)
            $('#log_list').html("");
            data.forEach(
                function(obj){
                    var a_tag = $("<a>",
                        {"class": "list-group-item",
                         });

                    var span = $("<span>", {"class" : "badge"});
                    var before = new Date(obj.fields.timestamp).getTime()
                    var now = new Date()
                    var dif_sec = (now - before)/1000
                    if(dif_sec < 60){
                        span.html("less a minute")
                    }else if(dif_sec < 3600){
                         if(Math.round(dif_sec/60) == 1){
                            span.html("one minute ago")
                        }else{
                            span.html(Math.round(dif_sec/60)+" mins ago")
                        }
                    }else if(dif_sec < 86400){
                         if(Math.round(dif_sec/3600) == 1){
                            span.html("one hour ago")
                        }else{
                            span.html(Math.round(dif_sec/3600)+" hours ago")
                        }
                    }else if(dif_sec < 432000){
                        if(Math.round(dif_sec/86400) == 1){
                            span.html("one day ago")
                        }else{
                            span.html(Math.round(dif_sec/86400)+" days ago")
                        }
                    }else{
                        span.html(new Date(obj.fields.timestamp).toDateString())
                    }
                    var i_tag = $("<i>", {"class" : "fa fa-fw fa-calendar"});
                    a_tag.append(span);
                    a_tag.append(i_tag);
                    a_tag.append(obj.fields.description)
                   $("#log_list").append(a_tag);
                }
            );
        },
        complete: function() {

        }
    });
}