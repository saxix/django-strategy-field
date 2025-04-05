from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, ClassVar, Sequence

from django.core.validators import BaseValidator
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..fields import AbstractStrategyField, ClassnameValidator
from ..utils import fqn, import_by_name

if TYPE_CHECKING:
    from ..registry import Registry


logger = logging.getLogger(__name__)


class RegistryValidator(BaseValidator):
    def __call__(self, value: Sequence[str]) -> None:
        if not isinstance(value, (list, tuple)):
            value = [value]
        for entry in value:
            if not self.limit_value.is_valid(entry):
                raise ValidationError(f"Invalid entry `{fqn(entry)}`")


class DrfStrategyField(serializers.ChoiceField):
    default_validators: ClassVar[list] = [ClassnameValidator]

    def __init__(self, registry: Registry, **kwargs: Any) -> None:
        choices = registry.as_choices()
        super().__init__(choices, **kwargs)
        self.registry = registry

    def get_validators(self) -> Sequence[BaseValidator]:
        ret = super().get_validators()
        ret.append(RegistryValidator(self.registry))
        return ret

    def to_representation(self, obj: AbstractStrategyField) -> str:
        return fqn(obj)

    def to_internal_value(self, data: Any) -> Any:
        return data


class DrfMultipleStrategyField(serializers.MultipleChoiceField):
    default_validators: ClassVar[list] = [ClassnameValidator]

    def __init__(self, registry: Registry, **kwargs: Any) -> None:
        choices = registry.as_choices()
        self.registry = registry
        super().__init__(choices=choices, **kwargs)

    def get_validators(self) -> list[BaseValidator]:
        ret = super().get_validators()
        ret.append(RegistryValidator(self.registry))
        return ret

    def to_representation(self, obj: list[type]) -> list[str]:
        return [fqn(i) for i in obj]

    def to_internal_value(self, data: list[str]) -> list[type]:
        return [import_by_name(i) for i in data]
