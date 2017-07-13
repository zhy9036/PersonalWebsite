
from django.conf.urls import url, include
from django.views.generic import RedirectView
from django.contrib.auth.views import logout
from . import views

urlpatterns = [
    url(r'^$', RedirectView.as_view(url='/login/', permanent=True)),
    url(r'^foo/$', views.foo, name='test_page'),
    url(r'^login/', views.login_view, name='login'),
    url(r'^login_gitlab/$', views.gitlab_login, name='login_gitlab'),
    url(r'^callback/', views.oauth2_authenticate, name='callback'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^logout/$', views.logout_view, name='logout'),
    # url(r'^logout/$', logout, {'next_page': '/login/'}, name='logout'),
    url(r'^validate_username/$', views.validate, name='validate_username'),

]