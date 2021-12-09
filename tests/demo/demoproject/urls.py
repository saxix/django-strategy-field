from django.contrib.admin import AdminSite, autodiscover
from django.urls import path, re_path

from demoproject.demoapp.api import DemoModelView, DemoMultipleModelView

from .demoapp.models import (DemoAllModel, DemoCustomModel, DemoModel,
                             DemoModelCallableDefault, DemoModelDefault,
                             DemoModelProxy, DemoMultipleCustomModel,
                             DemoMultipleModel,)

autodiscover()


class PublicAdminSite(AdminSite):
    def has_permission(self, request):
        from django.contrib.auth.models import User
        request.user = User.objects.get_or_create(username='sax')[0]
        return True


public_site = PublicAdminSite()
for m in (DemoAllModel, DemoCustomModel, DemoModel, DemoModelProxy,
          DemoMultipleCustomModel, DemoMultipleModel,
          DemoModelDefault, DemoModelCallableDefault):
    public_site.register(m)

urlpatterns = (
    re_path(r'^api/s/(?P<pk>.*)/$', DemoModelView.as_view({'get': 'retrieve'}), name='detail'),
    re_path(r'^api/s/$', DemoModelView.as_view({'get': 'list', 'post': 'create'}), name='single'),

    re_path(r'^api/m/(?P<pk>.*)/$', DemoMultipleModelView.as_view({'get': 'retrieve'}), name="multiple"),
    re_path(r'^api/m/$', DemoMultipleModelView.as_view({'get': 'list', 'post': 'create'}), name='multiple'),

    path(r'', public_site.urls),
)
