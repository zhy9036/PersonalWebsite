
    $(function() {
        var run_job_validator = false;
        // data
        var filename_list = [];
        var file_count = 0;
        var formData = new FormData();
        var yml_data = {'test':{}, 'failure':{}, 'deploy':{}};
        // button
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
                    $.ajax({
                        type: "POST",
                        url: 'yml_process/',
                        data: JSON.stringify(yml_data),
                        dataType: 'json',
                        success: function(data){
                            yml_data = {'test':{}, 'failure':{}, 'deploy':{}};
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
            var listContainer = $(list_id);

            // value of input
            //var ary = $(input_id).val().split('\\');
            var files = $(input_id).prop('files');
            var fname_list = $.map(files, function(val){return val.name;});
            var files_list = [];
            $.each(files, function(i, file){
                files_list.push(file);
                file_count += 1;
            });

            // add new list item
            if(fname_list.length > 0){
                $.each(fname_list, function(i, fname){
                    if(fname.includes("test_")){
                        fname = "- pytest " + fname;
                    }else{
                        fname = "- python " + fname;
                    }
                    if($(input_id).attr('id')== "input"){
                        if(!('script' in yml_data['test'])){
                            yml_data['test']['script'] = []
                        }
                        yml_data['test']['script'].push(fname);
                        run_job_validator = true;
                    }else if($(input_id).attr('id') == "input1"){
                        if(!('script' in yml_data['failure'])){
                            yml_data['failure']['script'] = []
                        }
                        yml_data['failure']['script'].push(fname);
                        run_job_validator = true;
                    }else{
                        if(!('script' in yml_data['deploy'])){
                            yml_data['deploy']['script'] = []
                        }
                        yml_data['deploy']['script'].push(fname);
                        run_job_validator = true;
                    }
                    // alert(JSON.stringify(yml_data));
                    function delete_file(obj, input_id){
                        //let flist = $('#form_upload')[0][input_name].files;
                        for(var i = 0; i < files_list.length; i++){

                            if(obj.text().indexOf(files_list[i].name) > -1){
                                filename_list.push(files_list[i].name);
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
            }
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
                                if(data['status'] == 'failed' ||data['status'] == 'success'){
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
            $.ajax({
                type: "YML_FILE",
                url: 'yml_process/',
                dataType: 'json',
                success: function(data){
                    $("#run_job").attr('data-toggle', '');
                    if(data.invalid){
                        var msg = data.yml_missing + data.aci_missing + data.runner_missing;
                        $("#run_job").attr('data-toggle', 'modal');
                        $("#job_result").html('Cannot run job: ' + msg);

                    }else{
                        $("#loading_img").show();
                        $("#job_result").html('');
                        run_job_validator = (file_count == filename_list.length)? false : true;
                        formData = new FormData($("#form_upload")[0]);
                        formData.append("delete_file", filename_list);
                        if(run_job_validator){
                            $("#run_job").attr('data-toggle', 'modal');
                            $('#btn_upload').click();
                        }else{
                            alert("Run with previous configurations:\n" + atob(data.content));
                            $("#run_job").attr('data-toggle', 'modal');
                            $('#btn_upload').click();
                            yml_data = (run_job_validator) ? yml_data : "";
                        }
                    }
                }
            })

        });

    });

