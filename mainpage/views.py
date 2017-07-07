from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.http.response import HttpResponse, Http404
from django.shortcuts import render
from .models import Projects
import json
from django.contrib.auth.models import User
from django.core import serializers as se


@login_required
def panel_home(request):
    return render(request, 'mainpage/panel_index.html')


@login_required
def detail(request, project_id):
    try:
        proj = Projects.objects.get(pk=project_id)
        if request.user == proj.user:
            return HttpResponse(project_id + " " + proj.user.username)
        else:
            raise Http404("Project doesn't exist!")
    except ObjectDoesNotExist:
        raise Http404("Project doesn't exist!")


@login_required
def update_project_info(request):
    current_user_id = request.user.id
    projects = Projects.objects.filter(user=request.user)

    projects_json_str = se.serialize('json', projects)
    projects_json = json.loads(projects_json_str)

    return JsonResponse(projects_json_str, safe=False)
