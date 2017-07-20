
from django.conf.urls import url, include
from django.views.generic import RedirectView
from django.contrib.auth.views import logout
from django.views.generic.detail import DetailView
from . import views



from django.contrib.auth.models import User
urlpatterns = [
    #url(r'^$', views.panel_home, name='panel_home'),
    url(r'^$', views.panel_home, name='panel_home'),
    url(r'^update_project/$', views.update_project_info, name='panel_project'),
    url(r'^(?P<project_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<project_id>\d+)/upload/$', views.detail_upload, name='upload'),
    url(r'^(?P<project_id>\d+)/reg_runner/(?P<runner_id>\d+)/$', views.detail_reg_runner, name='detail_reg_runner'),
    url(r'^(?P<project_id>\d+)/remove_runner/(?P<runner_id>\d+)/$', views.detail_remove_runner, name='detail_remvoe_runner'),
    url(r'^(?P<project_id>\d+)/clone_repo/$', views.detail_clone_repo, name='clone_repo'),
    url(r'^(?P<project_id>\d+)/yml_process/$', views.yml_process, name='yml_post'),
    # url(r'^check_runner/$', views.detail, name='detail'),
    # url(r'^foo/$', views.foo, name='test_page'),
    # url(r'^validate_username/$', views.validate, name='validate_username'),

]