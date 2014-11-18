from django.conf.urls import patterns, include, url
from django.contrib import admin

try:
    from django.apps import AppConfig  # noqa
    import django
    django.setup()
except ImportError:
    pass

admin.autodiscover()


urlpatterns = patterns('',
                       (r'', include(include(admin.site.urls))),
                       (r'admin/', include(include(admin.site.urls))),
                       )
