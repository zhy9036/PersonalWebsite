id
ssh_url_to_repo
http_url_to_repo
owner.name  owner.username
name

./curl.exe -k --request POST --form token=mP1yug9M_Bpjg9eLsvDQ --form ref=master https://gitlab.chq.ei/api/v4/projects/1210/trigger/pipline



Unverified H
TTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-u

https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings


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
