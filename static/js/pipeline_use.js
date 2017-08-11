
    $(function() {

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
        var run_job_validator = false;
        // data
        var files_list = [];
        var filename_list = [];
        var file_count = 0;
        var formData = new FormData();
        var yml_data = {'test':{}, 'failure':{}, 'deploy':{}};
        // button
        $('#input').on('click', function(){$(this).val('')});
        $('#input').on('change', function(){add_to_list('#input','#list')});
        $('#input1').on('change', function(){add_to_list('#input1', '#list1')});
        $('#input2').on('change', function(){add_to_list('#input2', '#list2')});

        // override submit
         $('#form_upload').submit(function(e){
            //formData = new FormData($(this)[0]);
            e.preventDefault();
            $.ajax({
                type: 'POST',
                url: $(this).attr('action'),
                data: formData,//new FormData($(this)[0]),
                success: function(data){
                    //alert("Upload successed!");
                    $.ajax({
                        type: "POST",
                        url: 'yml_process/',
                        data: JSON.stringify(yml_data),
                        dataType: 'json',
                        success: function(data){
                            //yml_data = {'test':{}, 'failure':{}, 'deploy':{}};
                            get_data();
                        },
                    });
                },
                cache: false,
                contentType: false,
                processData: false
            });
         });



        function add_to_list(input_id, list_id){
            //alert('triggered');

            var listContainer = $(list_id);
            // value of input
            //var ary = $(input_id).val().split('\\');
            var files = $(input_id).prop('files');
            var fname_list = $.map(files, function(val){return val.name;});

            $.each(files, function(i, file){
                files_list.push(file);
                file_count += 1;
            });
            $(input_id).val('')
            // add new list item
            //if(fname_list.length > 0){
                //alert(fname_list.length);
                $.each(fname_list, function(i, fname){
                    //var delete_index = filename_list.indexOf(fname);
                    //if(delete_index > -1){
                    //    filename_list.splice(delete_index, 1);
                    //}
                    if(fname.indexOf("test_") > -1){
                        fname = "- pytest " + fname;
                    }else{
                        fname = "- python " + fname;
                    }
                    if($(input_id).attr('id')== "input"){

                        if(!('script' in yml_data['test'])){
                            yml_data['test']['script'] = [];
                        }
                        yml_data['test']['script'].push(fname);
                        run_job_validator = true;

                    }else if($(input_id).attr('id') == "input1"){

                        if(!('script' in yml_data['failure'])){
                            yml_data['failure']['script'] = [];
                            yml_data['failure']['when'] = 'on_failure';
                        }
                        yml_data['failure']['script'].push(fname);
                        run_job_validator = true;

                    }else{

                        if(!('script' in yml_data['deploy'])){
                            yml_data['deploy']['script'] = [];
                        }
                        yml_data['deploy']['script'].push(fname);
                        run_job_validator = true;
                    }
                    // alert(JSON.stringify(yml_data));
                    function delete_file(obj, input_id){
                        //let flist = $('#form_upload')[0][input_name].files;
                        var ii = 0;
                        for(var i = 0; i < files_list.length; i++){
                            if(obj.text().indexOf(files_list[i].name) > -1){
                                ii = i;
                                //filename_list.push(files_list[i].name);
                            }
                        }
                        files_list.splice(ii, 1);
                        if($(input_id).attr('id')== "input"){
                            var index = yml_data['test']['script'].indexOf(fname);
                            yml_data['test']['script'].splice(index, 1);
                            if(yml_data['test']['script'].length == 0){
                                delete yml_data['test']['script'];
                                delete yml_data['test']['when'];
                            }

                        }else if($(input_id).attr('id') == "input1"){
                            var index = yml_data['failure']['script'].indexOf(fname);
                            yml_data['failure']['script'].splice(index, 1);
                            if(yml_data['failure']['script'].length == 0){
                                delete yml_data['failure']['script'];
                                delete yml_data['failure']['when'];
                            }
                        }else{
                            var index = yml_data['deploy']['script'].indexOf(fname);
                            yml_data['deploy']['script'].splice(index, 1);
                            if(yml_data['deploy']['script'].length == 0){
                                delete yml_data['deploy']['script'];
                                delete yml_data['deploy']['when'];
                            }

                        }
                        obj.remove();
                    }
                    //listContainer.append('<li> ' + fname +
                    //'<a onClick="delete_file(input_id, list_id);"> delete </a></li>');
                    var li = $("<li>");
                    li.html(fname);
                    var la = $("<a>", {"style": "padding:10px"});
                    la.html("delete");
                    la.bind('click', function(){delete_file(li, input_id);});
                    li.append(la);
                    listContainer.append(li);

                });
            //}
        }


        function get_data(){
            var interval_id = setInterval(
                function(){
                    $.ajax({
                        type: "GET",
                        url: 'yml_process/',
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
                                $("#loading_img").hide();
                                $("#job_result").html(data);
                            }else{
                                if(data['status'] == 'failed' ||data['status'] == 'success' || data['status'] == 'skipped'){
                                    clearInterval(interval_id);
                                    $("#loading_img").hide();
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

        $("#run_job").on('click', function(){
            $("#job_result").html('');
            $.ajax({
                type: "YML_FILE",
                url: 'yml_process/',
                dataType: 'json',
                success: function(data){
                    $("#run_job").attr('data-toggle', '');
                    var emptyYml = jQuery.isEmptyObject(yml_data['test']) && jQuery.isEmptyObject(yml_data['failure'])
                                    && jQuery.isEmptyObject(yml_data['deploy']);
                    if((data.invalid &&  !('yml_missing' in data)) ||
                        (data.invalid && data.yml_missing && emptyYml)){
                        var msg = '';
                        if ('yml_missing' in data){
                            msg += data.yml_missing;
                        }
                        if ('aci_missing' in data){
                            msg += data.aci_missing;
                        }
                        if ('runner_missing' in data){
                            msg += data.runner_missing;
                        }
                        $("#run_job").attr('data-toggle', 'modal');
                        $("#job_result").html('Cannot run job: ' + msg);

                    }else{
                        $("#loading_img").show();
                        $("#job_result").html('');
                        run_job_validator = (files_list.length==0)? false : true;
                        //alert(file_count + ' : ' + filename_list.length);
                        formData = new FormData();
                        for (var i = 0; i < files_list.length; i++){
                            formData.append('aci_files', files_list[i], files_list[i].name);
                        }

                        //formData.append('test_files', files_list);
                        //formData.append("delete_file", filename_list);
                        if(run_job_validator){
                            $("#run_job").attr('data-toggle', 'modal');
                            $('#btn_upload').click();
                        }else{
                            alert("Run with previous configurations:\n" + atob(data.content));
                            $("#run_job").attr('data-toggle', 'modal');
                            $('#btn_upload').click();

                        }
                    }
                }
            })
        });
    });

