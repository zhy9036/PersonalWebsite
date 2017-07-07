
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
    # url(r'^foo/$', views.foo, name='test_page'),
    # url(r'^validate_username/$', views.validate, name='validate_username'),

]