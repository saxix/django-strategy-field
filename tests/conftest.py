import pytest

from strategy_field.utils import fqn


@pytest.fixture
def registry():
    from demo.models import AbstractSender, Sender1, Sender2

    from strategy_field.registry import Registry

    r = Registry(AbstractSender, label_attribute="label")
    r.register(Sender1)
    r.register(Sender2)
    return r


@pytest.fixture
def custom_registry():
    from demo.models import Strategy1

    from strategy_field.registry import Registry

    r = Registry(Strategy1)
    r.register(Strategy1)
    return r


@pytest.fixture
def demomodel():
    from demo.models import DemoModel, Sender1

    return DemoModel.objects.get_or_create(sender=Sender1)[0]


@pytest.fixture
def democustommodel():
    from demo.models import DemoCustomModel, Strategy1

    from strategy_field.utils import fqn

    return DemoCustomModel.objects.get_or_create(sender=fqn(Strategy1))[0]


@pytest.fixture
def demo_all_model() -> "DemoAllModel":
    from demo.models import DemoAllModel, Sender1, Sender2, Strategy1, Strategy2

    return DemoAllModel.objects.get_or_create(choice=Sender1,
                                              multiple=[Sender1, Strategy2],
                                              custom=fqn(Strategy1),
                                              custom_multiple=[Strategy1, Strategy2],
                                              )[0]

@pytest.fixture
def demo_multiplecustom_model():
    from demo.models import DemoMultipleCustomModel, Strategy1

    from strategy_field.utils import fqn

    return DemoMultipleCustomModel.objects.get_or_create(sender=[fqn(Strategy1)])[0]


@pytest.fixture
def demo_multiple_model():
    from demo.models import DemoMultipleModel, Sender1

    return DemoMultipleModel.objects.get_or_create(sender=[Sender1])[0]


@pytest.fixture(scope="function")
def webapp(django_app):
    return django_app
