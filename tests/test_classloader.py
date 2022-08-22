from demoproject.classloader import custom_classloader
from unittest.mock import patch

from demoproject.demoapp.models import Sender1
from strategy_field.utils import fqn, get_class


@patch("demoproject.classloader.custom_classloader", side_effect=custom_classloader)
def test_custom_classloader(mocked, settings, monkeypatch):
    settings.STRATEGY_CLASSLOADER = "demoproject.classloader.custom_classloader"
    monkeypatch.setattr("strategy_field.utils.importer", None)
    monkeypatch.setattr("strategy_field.config.CLASSLOADER", settings.STRATEGY_CLASSLOADER)
    name = fqn(Sender1)
    assert get_class(name) == Sender1
    assert mocked.call_count == 1
