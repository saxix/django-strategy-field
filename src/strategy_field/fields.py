from __future__ import annotations

import logging
from inspect import isclass
from typing import TYPE_CHECKING, Any, Protocol, Sequence

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Field, Model
from django.db.models.fields import BLANK_CHOICE_DASH
from django.db.models.lookups import (
    Contains,
    Exact,
    IContains,
    IExact,
    Lookup,
)
from django.utils.text import capfirst

from .exceptions import StrategyClassError, StrategyNameError
from .forms import StrategyFormField, StrategyMultipleChoiceFormField
from .utils import fqn, get_class, stringify
from .validators import ClassnameValidator, RegistryValidator

if TYPE_CHECKING:
    from django.db.backends.base.base import BaseDatabaseWrapper
    from django.db.models.base import ModelBase
    from django.db.models.fields import _ChoicesList, _LimitChoicesTo
    from django.utils.choices import BlankChoiceIterator

NOCONTEXT = object()

logger = logging.getLogger(__name__)


class StrategyDescriptor(Protocol):
    def __init__(self, field: AbstractStrategyField) -> None: ...  # pragma: no cover
    def __get__(self, instance: Any, owner: type[BaseDatabaseWrapper]) -> Any: ...  # pragma: no cover
    def __set__(self, obj: Model, original: str) -> None: ...  # pragma: no cover


class StrategyClassFieldDescriptor:
    def __init__(self, field: StrategyField) -> None:
        self.field = field

    def __get__(self, obj: Model | None, value: type[Model] | None = None) -> StrategyClassField | None:
        if obj is None:
            return None
        return obj.__dict__.get(self.field.name)

    def __set__(self, obj: Model, original: str) -> None:
        if not original:
            value = None
        else:
            try:
                value = get_class(original)
            except (
                AttributeError,
                ModuleNotFoundError,
                ImportError,
                StrategyNameError,
            ) as e:
                if callable(self.field.import_error):
                    value = self.field.import_error(original, e)
                else:
                    value = self.field.import_error
            except Exception as e:  # pragma: no-cover
                logger.exception(e)
                raise ValidationError(original) from e

        obj.__dict__[self.field.name] = value
        try:
            raw_value = fqn(original or "")
        except StrategyClassError:
            raw_value = None
        obj.__dict__[f"_strategy_fqn_{self.field.name}"] = raw_value


class MultipleStrategyClassFieldDescriptor:
    def __init__(self, field: StrategyField) -> None:
        self.field = field

    def __get__(self, obj: Model, __: type[ModelBase] | None = None) -> list[type] | None:
        if obj is None:
            return None
        value = obj.__dict__.get(self.field.name)
        if value is None:
            return None
        if isinstance(value, str):
            value = value.split(",")
        if not isinstance(value, (list, tuple)):
            value = [value] if value is not None else None
        ret = []
        for v in value:
            if v:
                try:
                    v1 = get_class(v)
                    ret.append(v1)
                except StrategyNameError as e:
                    if callable(self.field.import_error):
                        return self.field.import_error(value, e)
                    return self.field.import_error

        return ret

    def __set__(self, obj: Model, value: Any) -> None:
        obj.__dict__[self.field.name] = value


class AbstractStrategyField(Field):
    descriptor: type[StrategyDescriptor]

    registry = None
    form_class: type[StrategyFormField | StrategyMultipleChoiceFormField]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.import_error = kwargs.pop("import_error", None)
        kwargs["max_length"] = 200

        self.registry = kwargs.pop("registry", None)
        super().__init__(*args, **kwargs)
        self.validators.append(ClassnameValidator(None))
        if self.registry:
            self.validators.append(RegistryValidator(self.registry))

    @property
    def flatchoices(self) -> None:  # type:ignore[override] #  this is needed to display in admin #
        return None

    def contribute_to_class(self, cls: type[Model], name: str, private_only: bool = False) -> None:
        self.set_attributes_from_name(name)
        self.model = cls
        if callable(self.registry):
            self.registry = self.registry(cls)
        cls._meta.add_field(self)
        setattr(cls, self.name, self.descriptor(self))

    def deconstruct(self) -> tuple[str, str, Sequence[Any], dict[str, Any]]:
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        if "registry" in kwargs:
            del kwargs["registry"]
        if "choices" in kwargs:
            del kwargs["choices"]
        return name, path, args, kwargs

    def get_db_prep_value(self, value: Any, connection: BaseDatabaseWrapper, prepared: bool = False) -> Any:
        return super().get_db_prep_value(value, connection, prepared)

    def get_db_prep_save(self, value: Any, connection: BaseDatabaseWrapper) -> Any:
        return super().get_db_prep_value(value, connection)

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return None
        return fqn(value)

    def value_to_string(self, obj: Model) -> str:
        value = self.value_from_object(obj)
        return fqn(value)

    def get_internal_type(self) -> str:
        return "CharField"

    def _check_choices(self) -> list:
        return []

    def _get_choices(self) -> list[tuple[AbstractStrategyField, str]]:
        if self.registry:
            return self.registry.as_choices()
        return []

    def _set_choices(self, value: tuple) -> None:
        pass

    choices = property(_get_choices, _set_choices)

    def get_choices(
        self,
        include_blank: bool = True,
        blank_choice: _ChoicesList = BLANK_CHOICE_DASH,
        limit_choices_to: _LimitChoicesTo | None = None,
        ordering: Sequence[str] = (),
    ) -> BlankChoiceIterator | _ChoicesList:
        first_choice = blank_choice if include_blank else []

        return first_choice + self.choices

    def validate(self, value: Any, model_instance: Model | None) -> None:
        if fqn(value) not in self.registry:
            raise ValidationError(f"{value} is not a valid choice")

    def formfield(
        self,
        form_class: type[forms.Field] | None = None,
        choices_form_class: type[forms.ChoiceField] | None = None,
        **kwargs: Any,
    ) -> forms.Field | None:
        defaults = {
            "required": not self.blank,
            "label": capfirst(self.verbose_name),
            "help_text": self.help_text,
            "registry": self.registry,
        }
        if self.has_default():
            if callable(self.default):
                defaults["initial"] = self.default
                defaults["show_hidden_initial"] = True
            else:
                defaults["initial"] = self.get_default()
        include_blank = self.blank or not (self.has_default() or "initial" in kwargs)
        defaults["choices"] = self.get_choices(include_blank=include_blank)
        if self.null:
            defaults["empty_value"] = None
        form_class = choices_form_class or self.form_class
        for k in list(kwargs):
            if k not in (
                "empty_value",
                "required",
                "choices",
                "registry",
                "widget",
                "label",
                "initial",
                "help_text",
                "error_messages",
                "show_hidden_initial",
            ):
                del kwargs[k]
        defaults.update(kwargs)
        return form_class(**defaults)


class RegexFormField(forms.CharField):
    pass


class StrategyClassField(AbstractStrategyField):
    form_class = StrategyFormField
    descriptor = StrategyClassFieldDescriptor

    def validate(self, value: Any, model_instance: Model | None) -> None:
        if fqn(value) not in self.registry:
            raise ValidationError(f"{value} is not a valid choice")


class MultipleStrategyClassField(AbstractStrategyField):
    descriptor = MultipleStrategyClassFieldDescriptor
    form_class = StrategyMultipleChoiceFormField

    def validate(self, values: Any, model_instance: Model | None) -> None:
        for value in values:
            if value not in self.registry:
                raise ValidationError(f"{value} is not a valid choice")

    def get_db_prep_save(self, value: Any, connection: BaseDatabaseWrapper, prepared: bool = False) -> Any:
        value = list(filter(lambda x: x, value)) if value is not None else None
        return super().get_db_prep_save(value, connection)

    def get_prep_value(self, value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            return stringify(value)
        if isinstance(value, str):
            return value
        return None

    def get_lookup(self, lookup_name: str) -> type[Lookup] | None:
        if lookup_name == "in":
            raise TypeError(f"Lookup type {lookup_name} not supported.")
        return super().get_lookup(lookup_name)

    def get_choices(
        self,
        include_blank: bool = True,
        blank_choice: _ChoicesList = BLANK_CHOICE_DASH,
        limit_choices_to: _LimitChoicesTo | None = None,
        ordering: Sequence[str] = (),
    ) -> BlankChoiceIterator | _ChoicesList:
        return AbstractStrategyField.get_choices(self, False, blank_choice)


class StrategyFieldDescriptor(StrategyClassFieldDescriptor):
    def __get__(self, obj: Model | None, value: type[Model] | None = None) -> StrategyField | None:
        if obj is None:
            return None
        return obj.__dict__.get(self.field.name)

    def __set__(self, obj: Model, original: str | None) -> None:
        if not original:
            value = None
        else:
            try:
                value = get_class(original)
            except (
                AttributeError,
                ModuleNotFoundError,
                ImportError,
                StrategyNameError,
            ) as e:
                if callable(self.field.import_error):
                    value = self.field.import_error(original, e)
                else:
                    value = self.field.import_error
            except Exception as e:  # pragma: no-cover
                logger.exception(e)
                raise ValidationError(original) from e

        if isclass(value):
            value = self.field.factory(value, obj)

        obj.__dict__[self.field.name] = value
        try:
            raw_value = fqn(original or "")
        except StrategyClassError:
            raw_value = None
        obj.__dict__[f"_strategy_fqn_{self.field.name}"] = raw_value


class StrategyField(StrategyClassField):
    descriptor = StrategyFieldDescriptor

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.factory = kwargs.pop("factory", lambda klass, obj: klass(obj))
        super().__init__(*args, **kwargs)

    def validate(self, value: Any, model_instance: Model | None) -> None:
        if fqn(value) not in self.registry:
            raise ValidationError(f"{value} is not a valid choice")

    def pre_save(self, model_instance: Model, add: bool) -> str | None:
        value = getattr(model_instance, self.attname)
        if value:
            return fqn(value)
        return None


class MultipleStrategyFieldDescriptor(MultipleStrategyClassFieldDescriptor):
    def __get__(self, obj: Model, __: type[ModelBase] | None = None) -> list[type]:
        if obj is None:
            return []
        value = obj.__dict__.get(self.field.name)

        if value and isinstance(value, (list, tuple, str)):
            ret = []
            if isinstance(value, str):
                value = value.split(",")
            for v in value:
                try:
                    cleaned = get_class(v)
                    ret.append(self.field.factory(cleaned, obj))
                except (  # noqa: PERF203
                    AttributeError,
                    ModuleNotFoundError,
                    ImportError,
                    StrategyNameError,
                ) as e:
                    if callable(self.field.import_error):
                        value = self.field.import_error(value, e)
                    else:
                        value = self.field.import_error
                except Exception as e:  # pragma: no-cover
                    logger.exception(e)
                    raise ValidationError(value) from e
            return ret
        return []

    def __set__(self, obj: Model, value: Any) -> None:
        obj.__dict__[self.field.name] = value


class MultipleStrategyField(MultipleStrategyClassField):
    descriptor = MultipleStrategyFieldDescriptor

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.factory = kwargs.pop("factory", lambda klass, obj: klass(obj))
        super().__init__(*args, **kwargs)

    def validate(self, values: Any, model_instance: Model | None) -> None:
        for value in values:
            if type(value) not in self.registry:
                raise ValidationError(f"{value} is not a valid choice")

    def get_lookup(self, lookup_name: str) -> type[Lookup[Any]] | None:
        if lookup_name == "in":
            raise TypeError(f"Lookup type {lookup_name} not supported.")
        return super().get_lookup(lookup_name)


class StrategyFieldLookupMixin(Lookup):
    def get_prep_lookup(self) -> str | None:
        value = super().get_prep_lookup()
        if value is None:
            return None
        if isinstance(value, str):
            pass
        elif isinstance(value, (list, tuple)):
            value = stringify(value)
        elif isclass(value) or isinstance(value, (self.lhs.output_field.registry.klass, object)):
            value = fqn(value)
        return value


class MultipleStrategyFieldLookupMixin(Lookup):
    def get_prep_lookup(self) -> str | None:
        value = super().get_prep_lookup()
        if value is None:
            return None
        if isinstance(value, str):
            pass
        elif isinstance(value, (list, tuple)):
            value = stringify(value)
        elif isclass(value) or isinstance(value, (self.lhs.output_field.registry.klass, object)):
            value = fqn(value)
        return value


class StrategyFieldContains(StrategyFieldLookupMixin, IContains):
    pass


class StrategyFieldIContains(StrategyFieldLookupMixin, Contains):
    pass


class MultipleStrategyFieldContains(MultipleStrategyFieldLookupMixin, Contains):
    pass


class MultipleStrategyFieldExact(MultipleStrategyFieldLookupMixin, Exact):
    pass


class MultipleStrategyFieldIExact(MultipleStrategyFieldLookupMixin, IExact):
    pass


StrategyField.register_lookup(StrategyFieldContains)
StrategyField.register_lookup(StrategyFieldIContains)

StrategyClassField.register_lookup(StrategyFieldContains)
StrategyClassField.register_lookup(StrategyFieldIContains)

MultipleStrategyClassField.register_lookup(MultipleStrategyFieldContains)
MultipleStrategyClassField.register_lookup(MultipleStrategyFieldExact)
MultipleStrategyClassField.register_lookup(MultipleStrategyFieldIExact)
MultipleStrategyField.register_lookup(MultipleStrategyFieldContains)
