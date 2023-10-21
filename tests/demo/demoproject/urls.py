from django.contrib.admin.sites import site
from django.urls import path, re_path

from demoproject.demoapp.api import DemoModelView, DemoMultipleModelView


urlpatterns = (
    re_path(r'^api/s/(?P<pk>.*)/$', DemoModelView.as_view({'get': 'retrieve'}), name='detail'),
    re_path(r'^api/s/$', DemoModelView.as_view({'get': 'list', 'post': 'create'}), name='single'),

    re_path(r'^api/m/(?P<pk>.*)/$', DemoMultipleModelView.as_view({'get': 'retrieve'}), name="multiple"),
    re_path(r'^api/m/$', DemoMultipleModelView.as_view({'get': 'list', 'post': 'create'}), name='multiple'),

    path(r'', site.urls),
)
