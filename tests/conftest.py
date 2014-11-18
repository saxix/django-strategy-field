import os
import os.path
import sys


def pytest_configure(config):
    from django.conf import settings
    sys.path.insert(0, os.path.dirname(__file__))

    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'demo.settings'

    try:
        from django.apps import AppConfig  # noqa
        import django
        django.setup()
    except ImportError:
        pass


    settings.TEMPLATE_DEBUG = True

    # Disable static compiling in tests
    settings.STATIC_BUNDLES = {}

    # This speeds up the tests considerably, pbkdf2 is by design, slow.
    settings.PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
