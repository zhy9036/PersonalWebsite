from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.debug import sensitive_post_parameters
from mysite import settings
from .models import UserLoginInfo

# Create your views here.
@sensitive_post_parameters('password')
def index(request):
    return render(request, 'home/login.html', {"form_action": '/db/'})


def validate(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(username, password)
        user = User(username=username)
        user.set_password(password)
        user.save()
        u = UserLoginInfo(username=username, password=password)
        u.save()
        q = User.objects.filter(username=username)
        if q.exists():
            return login_view(request)
        else:
            return HttpResponse("can't save to database")
    else:
        return render(request, 'home/register.html', {"form_action": '/signup/'})



def login_view(request):
    next = request.GET.get('next', '/db/')
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(next)
        else:
            return HttpResponse('<h1> WRONG </h1>')

    return render(request, 'home/login.html', {"form_action": '/login/'})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)

@login_required
def foo(request):
    return HttpResponse('<a href="/logout/"> Log out </a>')

