from django.shortcuts import render
from django.http import HttpResponse
from .models import Db_Table
# Create your views here.


def index(request):
    return HttpResponse("<h1> Hello </h1>")


def show_content(request, item_id):
    try:
        content = Db_Table.objects.get(id=item_id).content
        return HttpResponse("<h1> %s </h1>" % content)
    except Exception:
        return HttpResponse("<h1> Item doesn't exist</h1>")
