from django.conf.urls import url
from django.contrib.admin import AdminSite, autodiscover

from demoproject.demoapp.api import DemoModelView, DemoMultipleModelView
from .demoapp.models import (DemoAllModel, DemoCustomModel, DemoModel,
                             DemoModelProxy, DemoMultipleCustomModel,
                             DemoMultipleModel, DemoModelDefault,
                             DemoModelCallableDefault)

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
    url(r'', public_site.urls),

    url(r'api/s/(?P<pk>.*)/$', DemoModelView.as_view({'get': 'retrieve'})),
    url(r'api/s/$', DemoModelView.as_view({'get': 'list',
                                           'post': 'create'}), name='single'),

    url(r'api/m/(?P<pk>.*)/$', DemoMultipleModelView.as_view({'get': 'retrieve'})),
    url(r'api/m/$', DemoMultipleModelView.as_view({'get': 'list',
                                                   'post': 'create'}), name='multiple'),

)
