from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from home.models import Projects
import json
from django.contrib.auth.models import User
from django.core import serializers as se


@login_required
def panel_home(request):
    return render(request, 'mainpage/panel_index.html')


@login_required
def update_project_info(request):
    current_user_id = request.user.id
    projects = Projects.objects.filter(username=User.objects.get(id=current_user_id))

    projects_json_str = se.serialize('json', projects)
    projects_json = json.loads(projects_json_str)

    return JsonResponse(projects_json, safe=False)
