from __future__ import annotations

from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError
from django.forms.fields import ChoiceField, TypedMultipleChoiceField

from .utils import fqn, stringify

if TYPE_CHECKING:
    from .registry import Registry


class StrategyFormField(ChoiceField):
    def __init__(self, *args, **kwargs):
        self.registry = kwargs.pop("registry")
        self.empty_value = kwargs.pop("empty_value", "")
        super().__init__(*args, **kwargs)

    def prepare_value(self, value) -> str | None:
        if isinstance(value, str):
            return value
        if value:
            return fqn(value)

    def bound_data(self, data, initial):
        if isinstance(data, str):
            return data
        return fqn(data)

    def valid_value(self, value):
        return value in self.registry

    def _coerce(self, value):
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

    def clean(self, value):
        value = super().clean(value)
        return self._coerce(value)


class StrategyMultipleChoiceFormField(TypedMultipleChoiceField):
    def __init__(self, *args, **kwargs):
        self.registry: Registry = kwargs.pop("registry")
        kwargs["coerce"] = self.coerce
        super().__init__(*args, **kwargs)

    def prepare_value(self, value):
        ret = value
        if isinstance(value, str):
            ret = [value]
        if isinstance(value, (list, tuple)):
            ret = stringify(value)
        if ret:
            return ret.split(",")

    def coerce(self, value):
        try:
            if value in self.registry:
                return self.registry.get_by_name(value)
            raise ValidationError
        except (ValueError, TypeError, ValidationError):
            raise ValidationError(
                self.error_messages["invalid_choice"],
                code="invalid_choice",
                params={"value": f"'{value}'"},
            ) from None

    def valid_value(self, value):
        return value in self.registry
