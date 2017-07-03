
from django.conf.urls import url, include
from django.views.generic import RedirectView
from django.contrib.auth.views import logout
from . import views

urlpatterns = [
    url(r'^$', views.panel_home, name='panel_home'),
    url(r'^update_project/$', views.update_project_info, name='panel_project'),
    # url(r'^foo/$', views.foo, name='test_page'),
    # url(r'^validate_username/$', views.validate, name='validate_username'),

]