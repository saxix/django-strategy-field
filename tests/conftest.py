import pytest


@pytest.fixture
def registry():
    from demoproject.demoapp.models import AbstractSender, Sender1, Sender2
    from strategy_field.registry import Registry

    r = Registry(AbstractSender)
    r.register(Sender1)
    r.register(Sender2)
    return r


@pytest.fixture
def custom_registry():
    from demoproject.demoapp.models import Strategy
    from strategy_field.registry import Registry

    r = Registry(Strategy)
    r.register(Strategy)
    return r


@pytest.fixture
def demomodel():
    from demoproject.demoapp.models import DemoModel, Sender1

    return DemoModel.objects.get_or_create(sender=Sender1)[0]


@pytest.fixture
def democustommodel():
    from demoproject.demoapp.models import DemoCustomModel, Strategy
    from strategy_field.utils import fqn

    return DemoCustomModel.objects.get_or_create(sender=fqn(Strategy))[0]


@pytest.fixture
def demo_multiplecustom_model():
    from demoproject.demoapp.models import DemoMultipleCustomModel, Strategy
    from strategy_field.utils import fqn
    return DemoMultipleCustomModel.objects.get_or_create(sender=[fqn(Strategy)])[0]


@pytest.fixture
def demo_multiple_model():
    from demoproject.demoapp.models import DemoMultipleModel, Sender1

    return DemoMultipleModel.objects.get_or_create(sender=[Sender1])[0]


@pytest.fixture(scope='function')
def webapp(django_app):
    return django_app
    # import django_webtest
    #
    # wtm = django_webtest.WebTestMixin()
    # wtm.csrf_checks = False
    # wtm._patch_settings()
    # request.addfinalizer(wtm._unpatch_settings)
#     return django_webtest.DjangoTestApp()
