from django.conf import settings
import os
import os.path
import sys


def pytest_configure(config):
    import warnings
    sys.path.insert(0, os.path.dirname(__file__))
    warnings.filterwarnings('error',
                            module=r'(spreader|spreader)')

    if not settings.configured:
        os.environ['DJANGO_SETTINGS_MODULE'] = 'demo.settings'

    # http://djangosnippets.org/snippets/646/
    class InvalidVarException(object):
        def __mod__(self, missing):
            try:
                missing_str = unicode(missing)
            except:
                missing_str = 'Failed to create string representation'
            raise Exception('Unknown template variable %r %s' %
                            (missing, missing_str))

        def __contains__(self, search):
            if search == '%s':
                return True
            return False

    settings.TEMPLATE_DEBUG = True
    settings.TEMPLATE_STRING_IF_INVALID = InvalidVarException()

    # Disable static compiling in tests
    settings.STATIC_BUNDLES = {}

    # override a few things with our test specifics
    settings.INSTALLED_APPS = tuple(settings.INSTALLED_APPS) + (
        'demo',
    )
    # This speeds up the tests considerably, pbkdf2 is by design, slow.
    settings.PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
