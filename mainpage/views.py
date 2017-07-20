from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.http.response import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from django.conf import settings
from home.models import Profile
from .models import Projects
from home.views import gitlab_client
import json
from django.contrib.auth.models import User
from django.core import serializers as se
import os, subprocess
sys_path = settings.SYS_PATH

@login_required
def panel_home(request):

    return render(request, 'mainpage/panel_index.html')


@login_required
def detail(request, project_id):
    check_oauth(request)
    if request.method == 'RUNNER':
        r = gitlab_client.get('https://gitlab.chq.ei/api/v4/runners', verify=False)
        r = json.loads(r.content)
        print(r)
        return JsonResponse(r, safe=False)
    try:
        project_object = Projects.objects.get(pk=project_id)
        if request.user == project_object.user:
            # return HttpResponse(project_id + " " + proj.user.username)
            runner_dict = detail_check_runner(request, project_id)
            print(runner_dict)
            runner_count = len(runner_dict)
            # print(runner_dict)
            result_dict = {
                'upload_url': None if 'UPLOAD_URL' not in request.session else request.session['UPLOAD_URL'],
                'runner_id': None if runner_count < 1 else runner_dict[0]['id'],
                'runner_name': None if runner_count < 1 else runner_dict[0]['name'],
                'status': None if runner_count < 1 else ('Active' if runner_dict[0]['active'] else 'Inactive'),
                'project_object': project_object,
            }
            # check local repo
            import os.path as op
            os.chdir(sys_path)
            if project_object.localRepoExist:
                print("************ recheck", os.getcwd())
                print("************ recheck", project_object.localRepoPath)
                if not op.exists(project_object.localRepoPath + '\.git'):
                    project_object.localRepoPath = ''
                    project_object.localRepoExist = False
                    project_object.save()
                else:
                    os.chdir(project_object.localRepoPath)
                    subprocess.check_call('git checkout aci')
                    os.chdir(sys_path)

            return render(request, 'mainpage/panel_detail.html', result_dict)
        else:
            raise Http404("Project doesn't exist!")
    except ObjectDoesNotExist:
        raise Http404("Project doesn't exist!")


@login_required
def detail_check_runner(request, project_id):
    r = gitlab_client.get('https://gitlab.chq.ei/api/v4/projects/%s/runners' % project_id, verify=False)
    r = json.loads(r.content)
    return r


@login_required
def detail_reg_runner(request, project_id, runner_id):
    if request.method == "POST":
        token = bytes(request.POST['reg_token'], 'utf-8')
        os.chdir('C:/Users/chq-yangz/Desktop/gitlab-runner')
        ps = subprocess.Popen('gitlab-runner register', shell=True, stdin=subprocess.PIPE)
        ps.communicate(b'https://gitlab.chq.ei/ci \n %b \n aci_runner \n aci \n true \n shell \n'%token)
        os.chdir(sys_path)
    else:
        form = {'runner_id': runner_id}
        r = gitlab_client.post('https://gitlab.chq.ei/api/v4/projects/%s/runners' % project_id, form, verify=False)
        r = json.loads(r.content)
    return HttpResponseRedirect(reverse('panel_home') + project_id)


@login_required
def detail_remove_runner(request, project_id, runner_id):
    r = gitlab_client.delete('https://gitlab.chq.ei/api/v4/projects/%s/runners/%s' % (project_id, runner_id))
    r = json.loads(r.content)
    print(r)
    return HttpResponseRedirect(reverse('panel_home') + project_id)


@login_required
def detail_clone_repo(request, project_id):
    os.chdir(sys_path)
    user_id = Profile.objects.get(user=request.user).gitlabUserId
    remote_url = request.POST['repo_type'].split()[1]
    local_path = './rsc/'+user_id+'/'+project_id
    if not os.path.exists(local_path):
        os.makedirs(local_path)
    print(local_path)
    os.chdir(local_path)
    subprocess.check_call('git init')
    subprocess.check_call('git remote add origin %s' % remote_url)
    subprocess.check_call('git config http.sslVerify false')
    try:
        subprocess.check_call('git pull origin master')
    except Exception:
        pass
    try:
        subprocess.check_call('git checkout aci')
        subprocess.check_call('git pull origin aci')
    except:
        subprocess.check_call('git checkout -b aci')
        subprocess.check_call('git push origin aci')

    # subprocess.check_call('git merge origin/aci')

    os.chdir(sys_path)
    print('!!!!!!!!!!!!!!!!!!!!! 98', project_id)
    project_object = Projects.objects.get(projectId=project_id)
    project_object.localRepoExist = True
    project_object.localRepoPath = local_path
    project_object.save()

    return HttpResponseRedirect(reverse('panel_home') + project_id)


@login_required
def yml_process(request, project_id):
    check_oauth(request)
    import os, yaml, collections
    project_path = Projects.objects.get(projectId=project_id).localRepoPath
    if request.method == 'POST':
        print("************ 141", project_path)
        os.chdir(project_path)
        print("************ 143", os.getcwd())
        subprocess.check_call('git checkout aci')
        tmp = json.loads(request.body)
        print(tmp)
        tmp = collections.OrderedDict(tmp)
        content = collections.OrderedDict()
        content['stages'] = []
        for key in tmp:
            if 'script' in tmp[key]:
                content['stages'].append(key)
                content[key] = collections.OrderedDict()
                content[key]['stage'] = key
                if 'script' in tmp[key]:
                    content[key]['script'] = []
                    for item in tmp[key]['script']:
                        content[key]['script'].append(item[2:])


        """ https://stackoverflow.com/a/8661021 """
        represent_dict_order = lambda self, data: self.represent_mapping('tag:yaml.org,2002:map', data.items())
        yaml.add_representer(collections.OrderedDict, represent_dict_order)

        with open('.gitlab-ci.yml', 'w') as yaml_file:
            yaml.dump(content, yaml_file, default_flow_style=False)

        subprocess.check_call('git pull origin master')

        try:
            subprocess.check_call('git merge master -m \"[ci skip]\"')
        except:
            pass
        subprocess.check_call('git add -A')
        subprocess.check_call('git commit -m \"[ci skip]\"')
        print("************ 175", os.getcwd(), request.method)
        subprocess.check_call('git push origin aci')
        r = gitlab_client.post("https://gitlab.chq.ei/api/v4/projects/%s/"
                               "pipeline?ref=aci" % project_id, verify=False)
        r = json.loads(r.content)
        print('pipline id:', r['id'])
        request.session['pipline_id'] = r['id']

        os.chdir(sys_path)
        return JsonResponse('', safe=False)
    else:

        pipline_id = request.session['pipline_id']

        r = gitlab_client.get("https://gitlab.chq.ei/api/v4/projects/%s/"
                               "pipelines/%s" % (project_id, pipline_id), verify=False)
        r = json.loads(r.content)
        print(r)
        if r['status'] in ['success', 'failed']:
            request.session.pop('pipline_id', None)
        os.chdir(sys_path)
        return JsonResponse(r, safe=False)
        """
        except:
            os.chdir('C:/Users/chq-yangz/Desktop/mysite')
            print('hahahahaha except')
            return JsonResponse('No change detected', safe=False)
        """


@login_required
def detail_upload(request, project_id):
    if request.method == 'POST' and 'my_file' in request.FILES:
        user_id = Profile.objects.get(user=request.user).gitlabUserId
        my_file_list = request.FILES.getlist('my_file')
        for my_file in my_file_list:
            fname = my_file.name
            destination_dir = './rsc/'+user_id+'/'+project_id
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)
            with open(destination_dir+'/'+fname, 'wb+') as destination_file:
                for chunk in my_file.chunks():
                    destination_file.write(chunk)
        # fs = FileSystemStorage()
        # filename = fs.save(my_file.name, my_file)
        # upload_url = fs.url(my_file)

        # if upload_url:
        #    request.session['UPLOAD_URL'] = upload_url
    os.chdir(sys_path)
    return HttpResponseRedirect(
        reverse('detail', kwargs={'project_id': project_id}))


@login_required
def update_project_info(request):
    check_oauth(request)
    r = gitlab_client.get('https://gitlab.chq.ei/api/v4/projects', verify=False)
    r = json.loads(r.content)
    user_id = Profile.objects.get(user=request.user).gitlabUserId
    print(r)
    for item in r:
        print('******************',item['id'], item['creator_id'], user_id)
        if str(item['creator_id']) == str(user_id):
            print('yes')
            if not Projects.objects.filter(projectId=item['id']).exists():
                print('yes database')
                p = Projects()
                p.user = request.user
                p.projectName = item['name']
                p.projectId = item['id']
                p.sshRepoUrl = item['ssh_url_to_repo']
                p.httpRepoUrl = item['http_url_to_repo']
                p.webUrl = item['web_url']
                p.save()

    projects = Projects.objects.filter(user=request.user)

    projects_json_str = se.serialize('json', projects)
    projects_json = json.loads(projects_json_str)

    return JsonResponse(projects_json_str, safe=False)


#######################
# Utility Functions
#######################
def check_oauth(request):
    p = Profile.objects.get(user=request.user)
    gitlab_client.token = {'access_token': p.accessToken,
                           'refresh_token': p.refreshToken}
