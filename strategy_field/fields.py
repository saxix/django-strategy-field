# -*- coding: utf-8 -*-
import six
from inspect import isclass
from strategy_field.forms import StrategyMultipleChoiceFormField, StrategyFormField
from .utils import fqn, import_by_name, stringify
from django.db import models
from django.db.models.fields import BLANK_CHOICE_DASH
from django.utils.text import capfirst


class StrategyClassFieldDescriptor(object):
    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        if obj is None:
            raise AttributeError('Can only be accessed via an instance.')
        value = obj.__dict__.get(self.field.name)

        if isclass(value) and issubclass(value, self.field.registry.klass):
            return value
        elif isinstance(value, six.string_types):
            return import_by_name(value)
        # elif value is None:
        #     return None
        # raise ValueError(value)

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = value


class MultipleStrategyClassFieldDescriptor(object):
    def __init__(self, field):
        self.field = field

    def __get__(self, obj, type=None):
        if obj is None:
            raise AttributeError('Can only be accessed via an instance.')
        value = obj.__dict__.get(self.field.name)
        # if value is None:
        #     return value

        if not isinstance(value, (list, tuple)):
            value = [value]
        if isinstance(value, (list, tuple)):
            ret = []
            # if isinstance(value, six.string_types):
            #     value = value.split(',')
            for v in value:
                if isinstance(v, six.string_types):
                    v = import_by_name(v)
                # if not issubclass(v, self.field.registry.klass):
                #     raise ValueError(fqn(v))
                ret.append(v)
            return ret
        # raise ValueError(value)

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = value


class AbstractStrategyField(models.Field):
    def __init__(self, registry=None, *args, **kwargs):
        kwargs['max_length'] = 2000
        self.registry = registry
        super(AbstractStrategyField, self).__init__(*args, **kwargs)

    def contribute_to_class(self, cls, name, virtual_only=False):
        self.set_attributes_from_name(name)
        self.model = cls
        cls._meta.add_field(self)
        setattr(cls, self.name, self.descriptor(self))

    def get_internal_type(self):
        return 'CharField'

    def _get_choices(self):
        return self.registry.as_choices()

    choices = property(_get_choices)

    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
        first_choice = blank_choice if include_blank else []
        return first_choice + [(k, k) for k, v in self.choices]

    def deconstruct(self):
        name, path, args, kwargs = super(AbstractStrategyField, self).deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs

    def formfield(self, form_class=None, choices_form_class=None, **kwargs):
        defaults = {'required': not self.blank,
                    'label': capfirst(self.verbose_name),
                    'help_text': self.help_text,
                    'registry': self.registry}
        if self.has_default():
            if callable(self.default):
                defaults['initial'] = self.default
                defaults['show_hidden_initial'] = True
            else:
                defaults['initial'] = self.get_default()
        include_blank = (self.blank or
                         not (self.has_default() or 'initial' in kwargs))
        defaults['choices'] = self.get_choices(include_blank=include_blank)
        defaults['coerce'] = self.to_python
        if self.null:
            defaults['empty_value'] = None
        form_class = choices_form_class or self.form_class
        for k in list(kwargs):
            if k not in ('coerce', 'empty_value', 'choices', 'required',
                         'registry',
                         'widget', 'label', 'initial', 'help_text',
                         'error_messages', 'show_hidden_initial'):
                del kwargs[k]
        defaults.update(kwargs)
        return form_class(**defaults)


class StrategyClassField(AbstractStrategyField):
    form_class = StrategyFormField
    descriptor = StrategyClassFieldDescriptor

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        if value:
            return fqn(value)
        return ""

    def get_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, self.registry.klass):
            return fqn(value)
        if isinstance(value, six.string_types):
            return value
        if isclass(value) or isinstance(value, object):
            return fqn(value)
        # raise ValueError(value)

    def get_prep_lookup(self, lookup_type, value):
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        elif lookup_type == 'contains':
            return self.get_prep_value(value)
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)


class MultipleStrategyClassField(AbstractStrategyField):
    descriptor = MultipleStrategyClassFieldDescriptor
    form_class = StrategyMultipleChoiceFormField

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return ",".join(value)

    # def pre_save(self, model_instance, add):
    # value = getattr(model_instance, self.attname)
    # if isinstance(value, (list, tuple)):
    #         return self.registry.serialize(value)
    #     elif value is None:
    #         return value
    #     raise ValueError(value)

    # def to_python(self, value):
    # if not value:
    # return None
    #     elif isinstance(value, (list, tuple)):
    #         return self.builder(value, self.registry.klass)
    #     elif isinstance(value, six.string_types):
    #         return [import_by_name(value)]
    #     raise ValueError(value)

    def get_prep_value(self, value):
        if value is None:
            return None
        elif isinstance(value, (list, tuple)):
            return stringify(value)
        elif isinstance(value, six.string_types):
            return value
        # raise ValueError('Invalid value %s for %s', value, type(self))

        # def validate(self, value, model_instance):
        #     target = []
        #     if isinstance(value, (list, tuple)):
        #         target = value
        #     elif value is None:
        #         return None
        #     elif isinstance(value, (list, tuple)):
        #         target = self.registry.deserialize(value, self.registry.klass)

        # choices = [str(choice) for choice in self.registry]
        # if set(target) - set(choices):
        #     error = self.error_messages["invalid_choice"] % value
        #     raise ValidationError(error)
        # for el in target:
        #     if el not in self.registry:
        #         raise exceptions.ValidationError(self.error_messages['invalid_choice'],
        #                                          code='invalid_choice',
        #                                          params={'value': fqn(el)}, )

    def get_prep_lookup(self, lookup_type, value):
        # import ipdb; ipdb.set_trace()
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            raise TypeError('Lookup type %r not supported.' % lookup_type)
        elif lookup_type == 'contains':
            return self.get_prep_value(value)
        # raise TypeError('Lookup type %r not supported.' % lookup_type)

    def get_choices(self, include_blank=True, blank_choice=BLANK_CHOICE_DASH):
        return AbstractStrategyField.get_choices(self, False, blank_choice)


class StrategyFieldDescriptor(StrategyClassFieldDescriptor):
    def __get__(self, obj, type=None):
        if obj is None:
            raise AttributeError('Can only be accessed via an instance.')
        value = obj.__dict__.get(self.field.name)

        if isinstance(value, self.field.registry.klass):
            return value
        elif isclass(value) and issubclass(value, self.field.registry.klass):
            return value(obj)
        elif isinstance(value, six.string_types):
            return import_by_name(value)(obj)
        elif value is None:
            return None
        # raise ValueError(value)


class StrategyField(StrategyClassField):
    descriptor = StrategyFieldDescriptor


class MultipleStrategyFieldDescriptor(MultipleStrategyClassFieldDescriptor):
    def __get__(self, obj, type=None):
        if obj is None:
            raise AttributeError('Can only be accessed via an instance.')
        value = obj.__dict__.get(self.field.name)
        if not value:
            return None
        if isinstance(value, six.string_types) or isinstance(value, (list, tuple)):
            ret = []
            if isinstance(value, six.string_types):
                value = value.split(',')
            for v in value:
                if isinstance(v, six.string_types):
                    v = import_by_name(v)

                if isclass(v) and not issubclass(v, self.field.registry.klass):
                    raise ValueError(v)

                if isinstance(v, self.field.registry.klass):
                    ret.append(v)
                else:
                    ret.append(v(obj))

            return ret

        # raise ValueError(value)

    def __set__(self, obj, value):
        obj.__dict__[self.field.name] = value


class MultipleStrategyField(MultipleStrategyClassField):
    descriptor = MultipleStrategyFieldDescriptor
