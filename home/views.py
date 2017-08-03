from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.debug import sensitive_post_parameters

from mainpage.models import Log, Projects
from mysite import settings
from .models import Profile
from django.core.urlresolvers import reverse
import json
import requests
from requests_oauthlib import OAuth2Session
import os


@sensitive_post_parameters('password')
def index(request):
    return render(request, 'home/login.html', {"form_action": reverse('login')})


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
        q = User.objects.filter(username=username)
        if q.exists():
            return login_view(request)
        else:
            return HttpResponse("can't save to database")
    else:
        return render(request, 'home/register.html', {"form_action": reverse('signup')})

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
CLIENT_ID = settings.CLIENT_ID
CLIENT_SECRET = settings.CLIENT_SECRET
REDIRECT_URL = 'http://chq-yangzh-lx.corp.expeditors.com/callback'
AUTHORIZATION_URL = 'https://gitlab.chq.ei/oauth/authorize'
TOKEN_URL = 'https://gitlab.chq.ei/oauth/token'
API_BASE_URL = 'https://gitlab.chq.ei/api/v4'
SCOPE = ['api', 'read_user']
gitlab_client = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URL, scope=SCOPE)


def gitlab_login(request):
    if request.GET['next'] != '/panel/':
        request.session['next'] = request.GET['next']

    a_url, state = gitlab_client.authorization_url(AUTHORIZATION_URL)
    return HttpResponseRedirect(a_url)


def oauth2_authenticate(request):
    exchange_code = request.GET['code']

    token = gitlab_client.fetch_token(TOKEN_URL,
                                      client_secret=CLIENT_SECRET, code=exchange_code, verify=False)
    access_token = token['access_token']
    refresh_token = token['refresh_token']
    r = gitlab_client.get(API_BASE_URL + '/user', verify=False)
    r = json.loads(r.content)
    screen_name = r['name']
    username = r['username']
    email = r['email']
    gitlab_user_id = r['id']
    try:
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        profile.gitlabUserId = gitlab_user_id
        profile.screenName = screen_name
        profile.user = user
        profile.accessToken = access_token
        profile.refreshToken = refresh_token
        profile.save()

    except User.DoesNotExist:
        # create_user(USERNAME, EMAIL, PASSWORD)
        user = User.objects.create_user(username, email, email)
        profile = Profile()
        profile.gitlabUserId = gitlab_user_id
        profile.screenName = screen_name
        profile.user = user
        profile.accessToken = access_token
        profile.refreshToken = refresh_token
        profile.save()

    user = authenticate(username=username, password=email)
    login(request, user)
    log = Log()
    log.user = user
    log.logType = 'user'
    log.description = 'logged in the system'
    log.save()

    return HttpResponseRedirect(reverse('login'))


def login_view(request, nx=None):

    nextgo = request.session['next'] if 'next' in request.session\
        else request.GET.get('next', reverse('panel_home'))
    if request.user.is_authenticated():

        return HttpResponseRedirect(nextgo)
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(nextgo)
        else:
            return HttpResponse('<h1> WRONG </h1>')
    return render(request, 'home/login.html', {"next": nextgo})


def logout_view(request):
    log = Log()
    log.user = request.user
    log.logType = 'user'
    log.description = 'logged out the system'
    log.save()
    Projects.objects.filter(user=request.user).delete()
    gitlab_client.close()
    logout(request)

    return HttpResponseRedirect(settings.LOGIN_URL)


@login_required
def foo(request):
    return HttpResponse("<a href= '%s' > Log out </a>" % reverse('logout'))

