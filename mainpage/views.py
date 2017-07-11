from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.http.response import HttpResponse, Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls.base import reverse

from home.models import Profile
from .models import Projects
from home.views import gitlab_client
import json
from django.contrib.auth.models import User
from django.core import serializers as se


@login_required
def panel_home(request):

    return render(request, 'mainpage/panel_index.html')


@login_required
def detail(request, project_id):
    if request.method == 'RUNNER':
        r = gitlab_client.get('https://gitlab.chq.ei/api/v4/runners')
        r = json.loads(r.content)
        print(r)
        return JsonResponse(r, safe=False)
    try:
        proj = Projects.objects.get(pk=project_id)
        if request.user == proj.user:
            # return HttpResponse(project_id + " " + proj.user.username)
            runner_dict = detail_check_runner(request, project_id)
            print(runner_dict)
            runner_count = len(runner_dict)
            # print(runner_dict)
            result_dict = {
                'projectName': proj.projectName,
                'projectId': project_id,
                'runner_id': None if runner_count < 1 else runner_dict[0]['id'],
                'runner_name': None if runner_count < 1 else runner_dict[0]['name'],
                'status': None if runner_count < 1 else ('Active' if runner_dict[0]['active'] else 'Inactive'),
            }

            return render(request, 'mainpage/panel_detail.html', result_dict)
        else:
            raise Http404("Project doesn't exist!")
    except ObjectDoesNotExist:
        raise Http404("Project doesn't exist!")


@login_required
def detail_check_runner(request, project_id):
    r = gitlab_client.get('https://gitlab.chq.ei/api/v4/projects/%s/runners' % project_id)
    r = json.loads(r.content)
    return r


@login_required
def detail_reg_runner(request, project_id, runner_id):
    form = {'runner_id': runner_id}
    r = gitlab_client.post('https://gitlab.chq.ei/api/v4/projects/%s/runners' % project_id, form)
    r = json.loads(r.content)
    return HttpResponseRedirect(reverse('panel_home') + project_id)


@login_required
def detail_remove_runner(request, project_id, runner_id):
    r = gitlab_client.delete('https://gitlab.chq.ei/api/v4/projects/%s/runners/%s' % (project_id, runner_id))
    r = json.loads(r.content)
    print(r)
    return HttpResponseRedirect(reverse('panel_home') + project_id)


@login_required
def update_project_info(request):
    gitlab_user_id = Profile.objects.get(user=request.user).gitlabUserId
    print(gitlab_user_id)
    r = gitlab_client.get('https://gitlab.chq.ei/api/v4/projects')
    r = json.loads(r.content)
    print(r)

    for item in r:
        if item['namespace']['name'] == request.user.username:
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
