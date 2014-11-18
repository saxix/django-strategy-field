import django_webtest
import pytest
from strategy_field.registry import Registry
from demo.models import AbstractSender, Sender1, Sender2, DemoModel, DemoMultipleModel, DemoCustomModel, Strategy, \
    DemoMultipleCustomModel
from strategy_field.utils import fqn


@pytest.fixture
def registry():
    r = Registry(AbstractSender)
    r.register(Sender1)
    r.register(Sender2)
    return r


@pytest.fixture
def custom_registry():
    r = Registry(Strategy)
    r.register(Strategy)
    return r


@pytest.fixture
def demomodel():
    return DemoModel.objects.get_or_create(sender=Sender1)[0]


@pytest.fixture
def democustommodel():
    return DemoCustomModel.objects.get_or_create(sender=fqn(Strategy))[0]


@pytest.fixture
def demo_multiplecustom_model():
    return DemoMultipleCustomModel.objects.get_or_create(sender=[fqn(Strategy)])[0]


@pytest.fixture
def demo_multiple_model():
    return DemoMultipleModel.objects.get_or_create(sender=[Sender1])[0]


@pytest.fixture(scope='function')
def webapp(request):
    wtm = django_webtest.WebTestMixin()
    wtm.csrf_checks = False
    wtm._patch_settings()
    request.addfinalizer(wtm._unpatch_settings)
    return django_webtest.DjangoTestApp()
