import logging
from django import forms
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH, NOT_PROVIDED
from django.db.models.lookups import Contains, IContains, In
from django.utils.text import capfirst
from inspect import isclass
from operator import itemgetter

from strategy_field.exceptions import StrategyNameError
from strategy_field.forms import (StrategyFormField,
                                  StrategyMultipleChoiceFormField,)
from strategy_field.utils import fqn, get_class, get_display_string, stringify
from strategy_field.validators import ClassnameValidator, RegistryValidator

NOCONTEXT = object()

logger = logging.getLogger(__name__)


class StrategyClassFieldDescriptor(object):
    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        if obj is None:
            return None

        value = obj.__dict__.get(self.field.name)
        try:
            return get_class(value)
        except (AttributeError, ModuleNotFoundError, ImportError, StrategyNameError) as e:
            if callable(self.field.import_error):
                return self.field.import_error(value, e)
            else:
                return self.field.import_error
        except Exception as e:  # pragma: no-cover
            logger.exception(e)
            raise ValidationError(value)

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = value


class MultipleStrategyClassFieldDescriptor(object):
    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        if obj is None:
            return None
        value = obj.__dict__.get(self.field.name)
        if value is None:
            return None
        if isinstance(value, str):
            value = value.split(',')
        if not isinstance(value, (list, tuple)):
            value = [value] if value is not None else None
        # if isinstance(value, (list, tuple)):
        ret = []
        for v in value:
            if v:
                try:
                    v = get_class(v)
                    ret.append(v)
                except StrategyNameError as e:
                    if callable(self.field.import_error):
                        return self.field.import_error(value, e)
                    else:
                        return self.field.import_error

        return ret

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = value


# @deconstructible
class AbstractStrategyField(models.Field):
    registry = None

    def __init__(self, *args, **kwargs):
        self.display_attribute = kwargs.pop('display_attribute', None)
        self.import_error = kwargs.pop('import_error', None)
        kwargs['max_length'] = 200

        self.registry = kwargs.pop("registry", None)
        super().__init__(*args, **kwargs)
        self.validators.append(ClassnameValidator(None))
        if self.registry:
            self.validators.append(RegistryValidator(self.registry))

    def contribute_to_class(self, cls, name, private_only=False, virtual_only=NOT_PROVIDED):
        self.set_attributes_from_name(name)
        self.model = cls
        if callable(self.registry):
            self.registry = self.registry(cls)
        cls._meta.add_field(self)
        setattr(cls, self.name, self.descriptor(self))

    # def __eq__(self, other):
    #     if isinstance(other, Field):
    #         return self.creation_counter == other.creation_counter
    #     return self.registry == other.registry

    def get_internal_type(self):
        return 'CharField'

    def _check_choices(self):
        return []

    def _get_choices(self):
        if self.registry:
            return sorted([(klass, get_display_string(klass, self.display_attribute))
                    for klass in self.registry], key=itemgetter(1))
            # return [(klass, get_display_string(klass, self.display_attribute))
            #         for klass in self.registry]
        return []

    def _set_choices(self, value):
        pass

    choices = property(_get_choices, _set_choices)

    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH,
                    limit_choices_to=None, **kwargs):
        first_choice = blank_choice if include_blank else []

        return first_choice + [(fqn(klass), l)
                               for klass, l in self.choices]

    def validate(self, value, model_instance):
        return value in self.registry

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs["max_length"]
        if "registry" in kwargs:
            del kwargs["registry"]
        if "choices" in kwargs:
            del kwargs["choices"]
        return name, path, args, kwargs

    def formfield(self, form_class=None, choices_form_class=None, **kwargs):
        defaults = {'required': not self.blank,
                    'label': capfirst(self.verbose_name),
                    'display_attribute': self.display_attribute,
                    'help_text': self.help_text,
                    'registry': self.registry}
        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()
        include_blank = (self.blank or not (self.has_default() or 'initial' in kwargs))
        defaults['choices'] = self.get_choices(include_blank=include_blank)
        if self.null:
            defaults['empty_value'] = None
        form_class = choices_form_class or self.form_class
        for k in list(kwargs):
            if k not in ('empty_value', 'required', 'choices',
                         'registry', 'display_attribute',
                         'widget', 'label', 'initial', 'help_text',
                         'error_messages', 'show_hidden_initial'):
                del kwargs[k]
        defaults.update(kwargs)
        return form_class(**defaults)


class RegexFormField(forms.CharField):
    pass


class StrategyClassField(AbstractStrategyField):
    form_class = StrategyFormField
    descriptor = StrategyClassFieldDescriptor

    def get_prep_value(self, value):
        if value is None:
            return None
        # if isinstance(value, six.string_types):
        #     return value
        # if isclass(value) or isinstance(value, object):
        #     return fqn(value)
        return fqn(value)

    # def get_prep_lookup(self, lookup_type, value):
    #     if lookup_type == 'exact':
    #         return self.get_prep_value(value)
    #     elif lookup_type == 'in':
    #         return [self.get_prep_value(v) for v in value]
    #     elif lookup_type == 'contains':
    #         return self.get_prep_value(value)
    #     elif lookup_type == 'icontains':
    #         return self.get_prep_value(value)
    #     else:
    #         raise TypeError('Lookup type %r not supported.' % lookup_type)


class MultipleStrategyClassField(AbstractStrategyField):
    descriptor = MultipleStrategyClassFieldDescriptor
    form_class = StrategyMultipleChoiceFormField

    def validate(self, value, model_instance):
        return value in self.registry

    def get_db_prep_save(self, value, connection):
        value = list(filter(lambda x: x, value)) if value is not None else None
        return super().get_db_prep_save(value, connection)

    def get_prep_value(self, value):
        if value is None:
            return None
        elif isinstance(value, (list, tuple)):
            return stringify(value)
        elif isinstance(value, str):
            return value

    # def get_prep_lookup(self, lookup_type, value):
    #     if lookup_type == 'exact':
    #         return self.get_prep_value(value)
    #     elif lookup_type == 'in':
    #         raise TypeError('Lookup type %r not supported.' % lookup_type)
    #     elif lookup_type == 'icontains':
    #         return self.get_prep_value(value)
    #     elif lookup_type == 'contains':
    #         return self.get_prep_value(value)

    def get_lookup(self, lookup_name):
        if lookup_name == 'in':
            raise TypeError('Lookup type %r not supported.' % lookup_name)
        return super().get_lookup(lookup_name)

    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH,
                    limit_choices_to=None, **kwargs):
        return AbstractStrategyField.get_choices(self, False, blank_choice)


class StrategyFieldDescriptor(StrategyClassFieldDescriptor):

    def __get__(self, obj, value=None):
        if obj is None:
            return None
        return obj.__dict__.get(self.field.name)

    def __set__(self, obj, value):
        if not value:
            value = None
        else:
            try:
                value = get_class(value)
            except (AttributeError, ModuleNotFoundError, ImportError, StrategyNameError) as e:
                if callable(self.field.import_error):
                    value = self.field.import_error(value, e)
                else:
                    value = self.field.import_error
            except Exception as e:  # pragma: no-cover
                logger.exception(e)
                raise ValidationError(value)

        if isclass(value):
            value = self.field.factory(value, obj)

        obj.__dict__[self.field.name] = value


class StrategyField(StrategyClassField):
    descriptor = StrategyFieldDescriptor

    def __init__(self, *args, **kwargs):
        self.factory = kwargs.pop('factory', lambda klass, obj: klass(obj))
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        value = getattr(model_instance, self.attname)
        if value:
            return fqn(value)


class MultipleStrategyFieldDescriptor(MultipleStrategyClassFieldDescriptor):
    def __get__(self, obj, type=None):
        if obj is None:
            return []
        value = obj.__dict__.get(self.field.name)

        if value and isinstance(value, str) or isinstance(value, (list, tuple)):
            ret = []
            if isinstance(value, str):
                value = value.split(',')
            for v in value:
                try:
                    cleaned = get_class(v)
                    ret.append(self.field.factory(cleaned, obj))
                except (AttributeError, ModuleNotFoundError, ImportError, StrategyNameError) as e:
                    if callable(self.field.import_error):
                        value = self.field.import_error(value, e)
                    else:
                        value = self.field.import_error
                except Exception as e:  # pragma: no-cover
                    logger.exception(e)
                    raise ValidationError(value)

            return ret

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = value


class MultipleStrategyField(MultipleStrategyClassField):
    descriptor = MultipleStrategyFieldDescriptor

    def __init__(self, *args, **kwargs):
        self.factory = kwargs.pop('factory', lambda klass, obj: klass(obj))
        super().__init__(*args, **kwargs)

    def get_lookup(self, lookup_name):
        if lookup_name == 'in':
            raise TypeError('Lookup type %r not supported.' % lookup_name)
        return super().get_lookup(lookup_name)


class StrategyFieldLookupMixin(object):
    def get_prep_lookup(self):
        value = super().get_prep_lookup()
        if value is None:
            return None
        if isinstance(value, str):
            pass
        elif isinstance(value, (list, tuple)):
            value = stringify(value)
        elif isinstance(value, self.lhs.output_field.registry.klass):
            value = fqn(value)
        elif isclass(value) or isinstance(value, object):
            value = fqn(value)
        return value


class StrategyFieldContains(StrategyFieldLookupMixin, IContains):
    pass


class StrategyFieldIContains(StrategyFieldLookupMixin, Contains):
    pass


class StrategyFieldIn(StrategyFieldLookupMixin, In):
    pass


class MultipleStrategyFieldContains(StrategyFieldLookupMixin, Contains):
    pass


class MultipleStrategyFieldIn(StrategyFieldLookupMixin, In):
    pass


StrategyField.register_lookup(StrategyFieldContains)
StrategyField.register_lookup(StrategyFieldIContains)
MultipleStrategyField.register_lookup(MultipleStrategyFieldContains)

StrategyClassField.register_lookup(StrategyFieldContains)
StrategyClassField.register_lookup(StrategyFieldIContains)
MultipleStrategyClassField.register_lookup(MultipleStrategyFieldContains)
