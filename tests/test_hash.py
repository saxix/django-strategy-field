# -*- coding: utf-8 -*-
import collections

import pytest
from strategy_field.fields import StrategyClassField, MultipleStrategyClassField, StrategyField, MultipleStrategyField


@pytest.mark.parametrize("field", [StrategyClassField,
                                   MultipleStrategyClassField, StrategyField,
                                   MultipleStrategyField])
def test_is_hashable(field):
    assert isinstance(field(), collections.Hashable)
