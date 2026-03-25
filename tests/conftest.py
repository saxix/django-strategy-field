from typing import TYPE_CHECKING

import pytest

from strategy_field.utils import fqn

if TYPE_CHECKING:
    from demo.models import DemoAllModel


@pytest.fixture
def registry():
    from demo.models import AbstractSender, Sender1, Sender2  # noqa

    from strategy_field.registry import Registry  # noqa

    r = Registry(AbstractSender, label_attribute="label")
    r.register(Sender1)
    r.register(Sender2)
    return r


@pytest.fixture
def custom_registry():
    from demo.models import Strategy1  # noqa

    from strategy_field.registry import Registry  # noqa

    r = Registry(Strategy1)
    r.register(Strategy1)
    return r


@pytest.fixture
def demomodel():
    from demo.models import DemoModel, Sender1  # noqa

    return DemoModel.objects.get_or_create(sender=Sender1)[0]


@pytest.fixture
def democustommodel():
    from demo.models import DemoCustomModel, Strategy1  # noqa

    from strategy_field.utils import fqn  # noqa

    return DemoCustomModel.objects.get_or_create(sender=fqn(Strategy1))[0]


@pytest.fixture
def demo_all_model() -> "DemoAllModel":
    from demo.models import DemoAllModel, Sender1, Strategy1, Strategy2  # noqa

    return DemoAllModel.objects.get_or_create(
        choice=Sender1,
        multiple=[Sender1, Strategy2],
        custom=fqn(Strategy1),
        custom_multiple=[Strategy1, Strategy2],
    )[0]


@pytest.fixture
def demo_multiplecustom_model():
    from demo.models import DemoMultipleCustomModel, Strategy1  # noqa

    from strategy_field.utils import fqn  # noqa

    return DemoMultipleCustomModel.objects.get_or_create(sender=[fqn(Strategy1)])[0]


@pytest.fixture
def demo_multiple_model():
    from demo.models import DemoMultipleModel, Sender1  # noqa

    return DemoMultipleModel.objects.get_or_create(sender=[Sender1])[0]


@pytest.fixture
def webapp(django_app):
    return django_app
