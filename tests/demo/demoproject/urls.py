from django.conf.urls import include, url
from django.contrib.admin import AdminSite, autodiscover

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
    url(r'', include(public_site.urls)),
    # url(r'^admin/', include(site.urls)),
)
