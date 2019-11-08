# -*- coding: utf-8 -*-
import pytest

from demoproject.demoapp.models import DemoModel, Strategy1, Strategy, DemoModelNone
from strategy_field.utils import get_class, fqn, get_display_string, get_attr, import_by_name, stringify


def test_get_class():
    assert get_class(None) == None
    assert get_class('') == ''
    assert get_class(fqn(DemoModel)) == DemoModel
    assert get_class(DemoModel) == DemoModel
    assert get_class(DemoModel()) == DemoModel
    with pytest.raises(ValueError):
        assert get_class('x')
    assert get_class(2) == int


def test_get_display_string():
    assert get_display_string(DemoModel) == 'demoproject.demoapp.models.DemoModel'
    assert get_display_string(Strategy, 'label') == 'strategy'
    assert get_display_string(Strategy1, 'label') == 'demoproject.demoapp.models.Strategy1'
    assert get_display_string(Strategy, 'verbose_name') == 'Verbose Name'


def test_get_attr():
    class C(object):
        def __repr__(self):
            return "c"

    a = C()
    a.b = C()
    a.b.c = 4
    assert get_attr(a, 'b.c') == 4
    assert get_attr(a, 'b.c.y', None) is None

    assert get_attr(a, 'b.c.y', 1) == 1
    assert str(get_attr(a, 'b', 1)) == 'c'



def test_import_by_name():
    assert import_by_name('demoproject.demoapp.models.DemoModel') == DemoModel
    with pytest.raises(AttributeError):
        import_by_name('demoproject.demoapp.models.Wrong')


def test_stringify():
    assert stringify([DemoModel,
                      DemoModelNone]) == 'demoproject.demoapp.models.DemoModel,' \
                                         'demoproject.demoapp.models.DemoModelNone'
    assert stringify(['demoproject.demoapp.models.DemoModel',
                      DemoModelNone]) == 'demoproject.demoapp.models.DemoModel,' \
                                         'demoproject.demoapp.models.DemoModelNone'


def test_fqn():
    assert fqn(DemoModel) == 'demoproject.demoapp.models.DemoModel'
    assert fqn('demoproject.demoapp.models.DemoModel') == 'demoproject.demoapp.models.DemoModel'
    assert fqn(fqn) == 'strategy_field.utils.fqn'
    with pytest.raises(ValueError):
        assert fqn(2)
