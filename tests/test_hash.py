from collections.abc import Hashable

import pytest
from strategy_field.fields import (
    MultipleStrategyClassField,
    MultipleStrategyField,
    StrategyClassField,
    StrategyField,
)


@pytest.mark.parametrize(
    "field",
    [
        StrategyClassField,
        MultipleStrategyClassField,
        StrategyField,
        MultipleStrategyField,
    ],
)
def test_is_hashable(field):
    assert isinstance(field(), Hashable)
