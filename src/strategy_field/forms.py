from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence

from django.core.exceptions import ValidationError
from django.forms.fields import ChoiceField, TypedMultipleChoiceField

from .utils import fqn, stringify

if TYPE_CHECKING:
    from .registry import Registry


class StrategyFormField(ChoiceField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.registry = kwargs.pop("registry")
        self.empty_value = kwargs.pop("empty_value", "")
        super().__init__(*args, **kwargs)

    def prepare_value(self, value: str | type) -> str | None:
        if isinstance(value, str):
            return value
        if value:
            return fqn(value)
        return None

    def valid_value(self, value: str) -> bool:
        return value in self.registry

    def _coerce(self, value: str) -> Any:
        if value == self.empty_value or value in self.empty_values:
            return self.empty_value
        try:
            v = self.to_python(value)
            if v in self.registry:
                return v
            raise ValidationError
        except (ValueError, TypeError, ValidationError):
            raise ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": f"'{value}'"},
            ) from None

    def clean(self, value: Any) -> type:
        value = super().clean(value)
        return self._coerce(value)


class StrategyMultipleChoiceFormField(TypedMultipleChoiceField):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.registry: Registry = kwargs.pop("registry")
        kwargs["coerce"] = self.coerce
        super().__init__(*args, **kwargs)

    def prepare_value(self, value: str | Sequence[str]) -> list[str] | None:
        ret = value
        if isinstance(value, (list, tuple)):
            ret = stringify(value)
        if ret:
            return ret.split(",")

    def coerce(self, value: str) -> type | None:
        return self.registry.get_by_name(value)

    def valid_value(self, value: str) -> bool:
        return value in self.registry
