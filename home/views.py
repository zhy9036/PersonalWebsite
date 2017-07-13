from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.debug import sensitive_post_parameters
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
CLIENT_ID = 'bdc5a7fe0a4c9b96046489709ec4a12fd5405a81fa0fa7b614cfababe286c513'
CLIENT_SECRET = 'fe42d0cb36d3c3ae0dc93925a464d5aa72d1492790b3621e2471de70172f06b9'
REDIRECT_URL = 'http://localhost:8000/callback'
authorization_url = 'https://gitlab.chq.ei/oauth/authorize'
token_url = 'https://gitlab.chq.ei/oauth/token'
api_base_url = 'https://gitlab.chq.ei/api/v4'
scope = ['api', 'read_user']
gitlab_client = OAuth2Session(CLIENT_ID, redirect_uri=REDIRECT_URL, scope=scope)


def gitlab_login(request):
    if request.GET['next'] != '/panel/':
        request.session['next'] = request.GET['next']

    a_url, state = gitlab_client.authorization_url(authorization_url)
    return HttpResponseRedirect(a_url)


def oauth2_authenticate(request):
    exchange_code = request.GET['code']

    token = gitlab_client.fetch_token(token_url,
                        client_secret=CLIENT_SECRET, code=exchange_code, verify=False)
    access_token = token['access_token']
    refresh_token = token['refresh_token']
    r = gitlab_client.get(api_base_url+'/user', verify=False)
    r = json.loads(r.content)

    print(r)
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

    return HttpResponseRedirect(reverse('login'))


def login_view(request, nx=None):

    nextgo = request.session['next'] if 'next' in request.session\
        else request.GET.get('next', reverse('panel_home'))

    print("******************** " + request.user.username)
    print("******************** " + str(request.user.is_authenticated()))
    if request.user.is_authenticated():

        return HttpResponseRedirect(nextgo)
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            # print("******************** " + next)
            return HttpResponseRedirect(nextgo)
        else:
            return HttpResponse('<h1> WRONG </h1>')

    return render(request, 'home/login.html', {"next": nextgo})


def logout_view(request):
    gitlab_client.close()
    logout(request)
    return HttpResponseRedirect(settings.LOGIN_URL)


@login_required
def foo(request):
    return HttpResponse("<a href= '%s' > Log out </a>" % reverse('logout'))

