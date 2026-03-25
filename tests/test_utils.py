import pytest
from demo.models import DemoModel, DemoModelNone, Strategy1, Strategy2

from strategy_field.utils import (
    fqn,
    get_attr,
    get_class,
    get_display_string,
    import_by_name,
    stringify,
)


def test_get_class():
    assert get_class(None) is None
    assert get_class("") is None
    assert get_class(fqn(DemoModel)) == DemoModel
    assert get_class(DemoModel) == DemoModel
    assert get_class(DemoModel()) == DemoModel
    with pytest.raises(ValueError, match="x"):
        assert get_class("x")
    assert get_class(2) is None


def test_get_display_string():
    assert get_display_string(DemoModel) == "demo.models.DemoModel"
    assert get_display_string(Strategy1, "label") == "strategy"
    assert get_display_string(Strategy2, "label") == "demo.models.Strategy2"
    assert get_display_string(Strategy1, "verbose_name") == "Verbose Name"
    assert get_display_string(Strategy1, "none") == "demo.models.Strategy1"


def test_get_attr():
    class C:
        def __repr__(self):
            return "c"

    a = C()
    a.b = C()
    a.b.c = 4
    assert get_attr(a, "b.c") == 4
    assert get_attr(a, "b.c.y", None) is None

    assert get_attr(a, "b.c.y", 1) == 1
    assert str(get_attr(a, "b", 1)) == "c"


def test_import_by_name():
    assert import_by_name("demo.models.DemoModel") == DemoModel
    with pytest.raises(AttributeError):
        import_by_name("demo.models.Wrong")


def test_stringify():
    assert stringify([DemoModel, DemoModelNone]) == "demo.models.DemoModel,demo.models.DemoModelNone"
    assert stringify(["demo.models.DemoModel", DemoModelNone]) == "demo.models.DemoModel,demo.models.DemoModelNone"


def test_fqn():
    assert fqn(DemoModel) == "demo.models.DemoModel"
    assert fqn("demo.models.DemoModel") == "demo.models.DemoModel"
    assert fqn(fqn) == "strategy_field.utils.fqn"
    with pytest.raises(ValueError, match="2"):
        assert fqn(2)


def test_fqn2():
    with pytest.raises(ValueError, match="None"):
        assert fqn(None)

    with pytest.raises(ValueError, match="2"):
        assert fqn(2)
