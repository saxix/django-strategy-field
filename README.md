# django-strategy-field

[![Pypi](https://badge.fury.io/py/django-strategy-field.svg)](https://badge.fury.io/py/django-strategy-field)
[![coverage](https://codecov.io/github/saxix/django-strategy-field/coverage.svg?branch=develop)](https://codecov.io/github/saxix/django-strategy-field?branch=develop)
[![Test](https://github.com/saxix/django-strategy-field/actions/workflows/test.yml/badge.svg)](https://github.com/saxix/django-strategy-field/actions/workflows/test.yml)
[![Django](https://img.shields.io/pypi/frameworkversions/django/django-strategy-field)](https://pypi.org/project/django-strategy-field/)


Set of custom fields useful to implement the [Strategy Pattern](http://www.oodesign.com/strategy-pattern.html) with Django models.

The Strategies are displayed in SelectBoxes as standard choice field

This package provides the following custom fields:

* StrategyField
* MultipleStrategyField
* StrategyClassField
* MultipleStrategyClassField

The StrategyField can be accessed as instance of the model with an attribute
``context`` that points to model that 'owns' the field (inverse relation). So:

## Example


```python

    from strategy_field.fields import StrategyField
    from django.core.mail.backends.filebased.EmailBackend


    class Event(models.Model):
        backend = StrategyField()

    Event(sender='django.core.mail.backends.filebased.EmailBackend')

```

## Use case


As example we can imagine an application that manages `Events` that need to be notified to users.
Each `Occurrence` of `Event` can be notified using different transport, (email, sms,...).
We want to be able to add/change the way we send notification, per event basis, simply using
the Django admin panel.

```python

    from strategy_field.fields import StrategyField
    from strategy_field.registry import Registry

    class TransportRegistry(Registry)
        pass

    class AbstractStrategy(object):
        def __init__(self, context):
            self.context = context

        def send(self):
            raise NotImplementedError

    class EmailStrategy(AbstractTransport):
        def send(self):
            ...

    class SMSStrategy(AbstractTransport):
        def send(self):
            ...
    registry = TransportRegistry(AbstractStrategy)
    registry.register(EmailStrategy)
    registry.register(SMSStrategy)

    class Event(models.Model):
        sender = StrategyField(registry=registry)

    Event.objects.get_or_create(sender=EmailStrategy)
    ...
    ...
    e = Event.objects.get(sender=EmailStrategy)
    e.sender.send() # e.sender.context == e

```

### More examples


*Use callable*


```python

    from strategy_field.fields import StrategyField
    from strategy_field.registry import Registry

    registry1 = Registry()
    registry2 = Registry()

    class A(model):
        sender = StrategyField(registry=lambda model: model._registry)
        class Meta:
            abstract = True

    class C1(A):
        _registry = registry1
        class Meta:
            abstract = True

    class C2(A):
        _registry = registry2
        class Meta:
            abstract = True

```
