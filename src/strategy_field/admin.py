from __future__ import annotations

from typing import TYPE_CHECKING, Any, Generator

from django.contrib.admin import ChoicesFieldListFilter, FieldListFilter
from django.utils.translation import gettext as _

from strategy_field.fields import AbstractStrategyField
from strategy_field.utils import fqn

if TYPE_CHECKING:
    from django.contrib.admin.views.main import ChangeList

    from strategy_field.registry import Registry


class StrategyFieldListFilter(ChoicesFieldListFilter):
    field: AbstractStrategyField

    def choices(self, changelist: ChangeList) -> Generator[dict[str, Any], None]:
        registry: Registry = self.field.registry
        yield {
            "selected": self.lookup_val is None,
            "query_string": changelist.get_query_string(remove=[self.lookup_kwarg, self.lookup_kwarg_isnull]),
            "display": _("All"),
        }
        values = sorted(self.field.registry, key=lambda field: registry.get_name(field))

        for field in values:
            yield {
                "selected": self.lookup_val is not None and fqn(field) in self.lookup_val,
                "query_string": changelist.get_query_string(
                    {self.lookup_kwarg: fqn(field)}, [self.lookup_kwarg_isnull]
                ),
                "display": registry.get_name(field),
            }


FieldListFilter.register(lambda f: isinstance(f, AbstractStrategyField), StrategyFieldListFilter, True)
