import tempfile
import json
import os
import subprocess
import yaml
import collections
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.http.response import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse
from django.conf import settings
from home.models import Profile
from mainpage.models import Log
from .models import Projects
import base64
from home.views import gitlab_client
from django.core import serializers as se
sys_path = settings.SYS_PATH


@login_required
def panel_home(request):
    return render(request, 'mainpage/panel_index.html')


@login_required
def panel_log(request):
    return render(request, 'mainpage/panel_log.html')


@login_required
def about_page(request):
    return render(request, 'mainpage/panel_about.html')


@login_required
def detail(request, project_id):
    check_oauth(request)
    if request.method == 'RUNNER':
        r = gitlab_client.get('https://gitlab.chq.ei/api/v4/runners', verify=False)
        r = json.loads(r.content)
        return JsonResponse(r, safe=False)
    try:
        project_object = Projects.objects.get(projectId=project_id)
        project_object.save()
        if request.user == project_object.user:
            runner_dict = detail_check_runner(request, project_id)
            runner_count = len(runner_dict)

            result_dict = {
                'upload_url': None if 'UPLOAD_URL' not in request.session else request.session['UPLOAD_URL'],
                'runner_id': None if runner_count < 1 else runner_dict[0]['id'],
                'runner_name': None if runner_count < 1 else runner_dict[0]['name'],
                'status': None if runner_count < 1 else ('Active' if runner_dict[0]['active'] else 'Inactive'),
                'project_object': project_object,
            }

            # check aci branch

            api_str = 'https://gitlab.chq.ei/api/v4/projects/' \
                        '{0}/repository/branches/aci'.format(project_id)
            r = gitlab_client.get(api_str, verify=False)
            r = json.loads(r.content)
            if 'message' in r:
                project_object.localRepoPath = ''
                project_object.localRepoExist = False

            else:
                project_object.localRepoPath = 'aci'
                project_object.localRepoExist = True
            project_object.save()
            return render(request, 'mainpage/panel_detail.html', result_dict)
        else:
            raise Http404("Project doesn't exist!")
    except ObjectDoesNotExist:
        raise Http404("Project doesn't exist!")


@login_required
def detail_check_runner(request, project_id):
    r = gitlab_client.get('https://gitlab.chq.ei/api/v4/projects/%s/runners' % project_id, verify=False)
    r = json.loads(r.content)
    runner_count = len(r)
    project_object = Projects.objects.get(projectId=project_id)
    if runner_count > 0:
        project_object.runnerExist = True
        project_object.runnerName = r[0]['name']
    else:
        project_object.runnerExist = False
        project_object.runnerName = ''
    project_object.save()
    return r


@login_required
def detail_reg_runner(request, project_id, runner_id):
    if request.method == "POST":
        token = bytes(request.POST['reg_token'], 'utf-8')
        os.chdir('C:/Users/chq-yangz/Desktop/gitlab-runner')
        ps = subprocess.Popen('gitlab-runner register', shell=True, stdin=subprocess.PIPE)
        ps.communicate(b'https://gitlab.chq.ei/ci \n %b \n aci_runner \n aci \n true \n shell \n'%token)
        os.chdir(sys_path)
        make_log(request, 'runner', 'registered a runner', project_id)
    else:
        form = {'runner_id': runner_id}
        r = gitlab_client.post('https://gitlab.chq.ei/api/v4/projects/%s/runners' % project_id, form, verify=False)
        print(r)
        make_log(request, 'runner', 'activated a runner({0})'.format(runner_id), project_id)
    project_object = Projects.objects.get(projectId=project_id)
    project_object.runnerExist = True
    project_object.save()
    return HttpResponseRedirect(reverse('panel_home') + project_id)


@login_required
def detail_remove_runner(request, project_id, runner_id):
    r = gitlab_client.delete('https://gitlab.chq.ei/api/v4/projects/%s/runners/%s' % (project_id, runner_id), verify=False)
    r = json.loads(r.content)
    print(r)
    project_object = Projects.objects.get(projectId=project_id)
    project_object.runnerExist = False
    project_object.save()
    make_log(request, 'runner', 'removed a runner({0})'.format(runner_id), project_id)
    return HttpResponseRedirect(reverse('panel_home') + project_id)


@login_required
def detail_clone_repo(request, project_id):
    check_oauth(request)
    api_str = 'https://gitlab.chq.ei/api/v4/projects/' \
              '{0}/repository/branches?branch=newbranch&ref=master'.format(project_id)
    r = gitlab_client.post(api_str, verify=False)
    r = json.loads(r.content)
    project_object = Projects.objects.get(projectId=project_id)
    project_object.localRepoExist = True
    project_object.localRepoPath = r['name']+': '+r['short_id']
    project_object.save()
    make_log(request, 'branch', 'created aci branch', project_id)
    return HttpResponseRedirect(reverse('panel_home') + project_id)


@login_required
def yml_process(request, project_id):
    check_oauth(request)
    if request.method == 'POST':
        tmp = json.loads(request.body)
        if tmp != '':
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
            with tempfile.TemporaryFile(mode='r+') as yaml_file:
                yaml.dump(content, yaml_file, default_flow_style=False)
                yaml_file.seek(0)
                fname = '.gitlab-ci.yml'
                fcontent = yaml_file.read().encode('utf-8')
                _upload_file(request, project_id, fname, fcontent)

        # make merge request #
        api_str = 'https://gitlab.chq.ei/api/v4/projects/{0}/merge_requests?' \
                  'source_branch=master&target_branch=aci&title=sync_source_code'\
                    .format(project_id)
        r = gitlab_client.post(api_str, verify=False)
        r = json.loads(r.content)
        print("Merge request: ", r)
        # accept MR only when MR requested#
        if 'message' not in r:
            mr_id = r['id']
            api_str = 'https://gitlab.chq.ei/api/v4/projects/' \
                      '{0}/merge_requests/{1}/merge?merge_commit_message=acceptMR[ci skip]'.format(project_id, mr_id)
            r = gitlab_client.put(api_str, verify=False)
            r = json.loads(r.content)
            print("Accept Merge request: ", r)
            # if cannot accept close it
            if 'message' in r:
                api_str = 'https://gitlab.chq.ei/api/v4/projects/' \
                          '{0}/merge_requests/{1}?state_event=close'.format(project_id, mr_id)
                r = gitlab_client.put(api_str, verify=False)
                print("close MR: ", r.content)
        else:
            return JsonResponse('No change detected', safe=False)

        # create a pipline #
        r = gitlab_client.post("https://gitlab.chq.ei/api/v4/projects/%s/"
                               "pipeline?ref=aci" % project_id, verify=False)
        r = json.loads(r.content)
        print(r)
        make_log(request, 'pipeline',
                 'created a pipeline job({0})'.format(r['id']), project_id, r['id'])
        request.session['pipeline_id'] = r['id']
        return JsonResponse(r, safe=False)
    elif request.method == 'YML_FILE':
        r = gitlab_client.get("https://gitlab.chq.ei/api/v4/projects/%s/"
                              "repository/files?file_path=.gitlab-ci.yml&ref=aci" % project_id, verify=False)
        r = json.loads(r.content)
        if 'message' in r:
            r['invalid'] = True
            r['yml_missing'] = " [yml missing] "
        detail_check_runner(request, project_id)
        project_object = Projects.objects.get(projectId=project_id)
        if not project_object.localRepoExist:
            r['invalid'] = True
            r['aci_missing'] = " [aci branch missing] "
        if not project_object.runnerExist:
            r['invalid'] = True
            r['runner_missing'] = " [runner missing] "
        print("****************** YML FILE", r)
        return JsonResponse(r, safe=False)

    else:
        pipeline_id = request.session['pipeline_id']
        r = gitlab_client.get("https://gitlab.chq.ei/api/v4/projects/%s/"
                              "pipelines/%s" % (project_id, pipeline_id), verify=False)
        r = json.loads(r.content)
        if r['status'] in ['success', 'failed']:
            make_log(request, 'pipeline', 'job({0}) was {1}'.format(pipeline_id, r['status']), project_id, pipeline_id)
        return JsonResponse(r, safe=False)


@login_required
def detail_upload(request, project_id):
    print(request.FILES)
    print(request.POST['delete_file'])
    if request.method == 'POST':
        #print(request.FILES['files_delete'])
        if 'test_files' in request.FILES:
            print("******************11111111111111111111111111111111111111111111111111111111")
            my_file_list = request.FILES.getlist('test_files')
            print("hahahah", len(my_file_list))
            for my_file in my_file_list:
                if my_file.name not in request.POST['delete_file']:
                    fname = my_file.name
                    content = my_file.read()
                    _upload_file(request, project_id, fname, content)

        if 'test_failure_files' in request.FILES:
            my_file_list = request.FILES.getlist('test_failure_files')
            for my_file in my_file_list:
                if my_file.name not in request.POST['delete_file']:
                    fname = my_file.name
                    content = my_file.read()
                    _upload_file(request, project_id, fname, content)

        if 'deploy_files' in request.FILES:
            my_file_list = request.FILES.getlist('deploy_files')
            for my_file in my_file_list:
                if my_file.name not in request.POST['delete_file']:
                    fname = my_file.name
                    content = my_file.read()
                    _upload_file(request, project_id, fname, content)

    return HttpResponseRedirect(
        reverse('detail', kwargs={'project_id': project_id}))


@login_required
def update_log(request):
    logs = Log.objects.filter(user=request.user).order_by("-timestamp")[:8]
    logs_json_str = se.serialize('json', logs)
    return JsonResponse(logs_json_str, safe=False)


@login_required
def update_log_all(request):
    logs = Log.objects.filter(user=request.user).order_by("-timestamp")
    logs_json_str = se.serialize('json', logs)
    return JsonResponse(logs_json_str, safe=False)


@login_required
def get_last_job(request):
    log = Log.objects.filter(user=request.user, logType='pipeline').order_by("-timestamp")[:1]
    logs_json_str = se.serialize('json', log)
    print("$$$$$$$$$$", logs_json_str)
    return JsonResponse(logs_json_str, safe=False)


@login_required
def retry_last_job(request):
    if request.method == 'POST':
        check_oauth(request)
        log = Log.objects.filter(user=request.user, logType='pipeline').order_by("-timestamp")[:1]
        log = list(log)[0]
        project_id = log.projectId
        request.session['project_id'] = project_id
        # make merge request #
        api_str = 'https://gitlab.chq.ei/api/v4/projects/{0}/merge_requests?' \
                  'source_branch=master&target_branch=aci&title=sync_source_code'\
                    .format(project_id)
        r = gitlab_client.post(api_str, verify=False)
        r = json.loads(r.content)
        # accept MR only when MR requested#
        if 'message' not in r:
            mr_id = r['id']
            api_str = 'https://gitlab.chq.ei/api/v4/projects/' \
                      '{0}/merge_requests/{1}/merge?merge_commit_message=acceptMR[ci skip]'.format(project_id, mr_id)
            r = gitlab_client.put(api_str, verify=False)
            r = json.loads(r.content)
            print("Accept Merge request: ", r)
            # if cannot accept close it
            if 'message' in r:
                api_str = 'https://gitlab.chq.ei/api/v4/projects/' \
                          '{0}/merge_requests/{1}?state_event=close'.format(project_id, mr_id)
                r = gitlab_client.put(api_str, verify=False)
                print("close MR: ", r.content)

        r = gitlab_client.post("https://gitlab.chq.ei/api/v4/projects/%s/"
                               "pipeline?ref=aci" % project_id, verify=False)
        r = json.loads(r.content)
        request.session['pipeline_id'] = r['id']
        make_log(request, 'pipeline',
                 'created a pipeline job({0})'.format(r['id']), project_id, r['id'])
        return JsonResponse(r, safe=False)
    else:
        pipeline_id = request.session['pipeline_id']
        project_id = request.session['project_id']
        r = gitlab_client.get("https://gitlab.chq.ei/api/v4/projects/%s/"
                              "pipelines/%s" % (project_id, pipeline_id), verify=False)
        r = json.loads(r.content)
        if r['status'] in ['success', 'failed']:
            make_log(request, 'pipeline', 'job({0}) was {1}'.format(pipeline_id, r['status']), project_id, pipeline_id)
        return JsonResponse(r, safe=False)


@login_required
def update_project_info(request):
    check_oauth(request)
    r = gitlab_client.get('https://gitlab.chq.ei/api/v4/projects', verify=False)
    r = json.loads(r.content)
    user_id = Profile.objects.get(user=request.user).gitlabUserId
    for item in r:
        if item['permissions']['project_access']: #str(item['creator_id']) == str(user_id):
            if not Projects.objects.filter(user=request.user, projectId=item['id']).exists():
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
    return JsonResponse(projects_json_str, safe=False)


#######################
# Utility Functions
#######################
def make_log(request, log_type, description, project_id=None, pipeline_id=None):
    log = Log()
    log.user = request.user
    log.logType = log_type
    log.description = description
    if project_id:
        #log.project = Projects.objects.get(projectId=project_id)
        log.projectId = project_id
    if pipeline_id:
        log.pipelineId = pipeline_id
    log.save()


def check_oauth(request):
    p = Profile.objects.get(user=request.user)
    gitlab_client.token = {'access_token': p.accessToken,
                           'refresh_token': p.refreshToken}


def _upload_file(request, project_id, fname, content):
    check_oauth(request)
    content = base64.b64encode(content)
    form = {'content': content}
    api_str = 'https://gitlab.chq.ei/api/v4/projects/{0}/repository/' \
              'files?file_path={1}&branch_name=aci' \
              '&commit_message={2}&encoding=base64' \
              .format(project_id, fname, 'upload[ci skip]')

    r = gitlab_client.post(api_str, form, verify=False)
    #r = json.loads(r.content)
    print(api_str)
    print("**************************************", r)
    if '201' not in r:

        api_str = 'https://gitlab.chq.ei/api/v4/projects/{0}/repository/' \
                  'files?file_path={1}' \
                  '&branch_name=aci&commit_message=update[ci skip]&encoding=base64' \
                  .format(project_id, fname)
        r = gitlab_client.put(api_str, form, verify=False)
        print("***********************", r.content)
