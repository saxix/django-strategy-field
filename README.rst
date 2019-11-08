=====================
django-strategy-field
=====================

Set of custom fields useful to implement the `Strategy Pattern`_ with Django models.

The Strategies are displayed in SelectBoxes as standard choice field

This package provides the following custom fields:

* StrategyField
* MultipleStrategyField
* StrategyClassField
* MultipleStrategyClassField

The StrategyField can be accessed as instance of the model with an attribute
``context`` that points to model that 'owns' the field (inverse relation). So:

Example
=======

.. code-block:: python

    from strategy_field.fields import StrategyField
    from django.core.mail.backends.filebased.EmailBackend


    class Event(models.Model):
        backend = StrategyField()

    Event(sender='django.core.mail.backends.filebased.EmailBackend')


Use case
========

As example we can imagine an application that manages `Events` that need to be notified to users.
Each `Occurrence` of `Event` can be notified using different transport, (email, sms,...).
We want to be able to add/change the way we send notification, per event basis, simply using
the Django admin panel.

.. code-block:: python

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


More examples
-------------

Use callable
~~~~~~~~~~~~

.. code-block:: python

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


Project links
=============

+--------------------+----------------+--------------+---------------------------+
| Stable             | |master-build| | |master-cov| |                           |
+--------------------+----------------+--------------+---------------------------+
| Development        | |dev-build|    | |dev-cov|    |                           |
+--------------------+----------------+--------------+---------------------------+
| Project home page: |https://github.com/saxix/django-strategy-field             |
+--------------------+---------------+-------------------------------------------+
| Issue tracker:     |https://github.com/saxix/django-strategy-field/issues?sort |
+--------------------+---------------+-------------------------------------------+
| Download:          |http://pypi.python.org/pypi/django-strategy-field/         |
+--------------------+---------------+-------------------------------------------+

.. _Strategy Pattern: http://www.oodesign.com/strategy-pattern.html

.. |master-build| image:: https://secure.travis-ci.org/saxix/django-strategy-field.png?branch=master
    :target: http://travis-ci.org/saxix/django-strategy-field/

.. |master-cov| image:: https://codecov.io/github/saxix/django-strategy-field/coverage.svg?branch=master
    :target: https://codecov.io/github/saxix/django-strategy-field?branch=develop


.. |dev-build| image:: https://secure.travis-ci.org/saxix/django-strategy-field.png?branch=develop
    :target: http://travis-ci.org/saxix/django-strategy-field/

.. |dev-cov| image:: https://codecov.io/github/saxix/django-strategy-field/coverage.svg?branch=develop
    :target: https://codecov.io/github/saxix/django-strategy-field?branch=develop
