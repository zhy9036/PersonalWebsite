    $(function() {
        var run_job_validator = false;
        // data
        yml_data = {'test':{}, 'failure':{}, 'deploy':{}};
        // button
        $('#input').on('change', function(){add_to_list('#input','#list')});
        $('#input1').on('change', function(){add_to_list('#input1', '#list1')});
        $('#input2').on('change', function(){add_to_list('#input2', '#list2')});
        yml_data = (run_job_validator) ? yml_data : "";
        // override submit
         $('#form_upload').submit(function(e){
            e.preventDefault();
            $.ajax({
                type: 'POST',
                url: $(this).attr('action'),
                data: new FormData($(this)[0]),
                success: function(data){
                    //alert('haha');
                    $.ajax({
                        type: "POST",
                        url: 'yml_process/',
                        data: JSON.stringify(yml_data),
                        dataType: 'json',
                        success: get_data,
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
                    listContainer.append('<li> ' + fname + '</li>');
                    // clear value input
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
            $("#loading_img").show();
            $("#job_result").html('');
            if(run_job_validator){
                $(this).attr('data-toggle', 'modal');
                $('#btn_upload').click();
            }else{
                alert("Run with previous configurations");
                $('#btn_upload').click();
            }
        });
    });