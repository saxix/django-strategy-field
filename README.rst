=====================
django-strategy-field
=====================

DFS is a custom field to enable the implementation of the `Strategy Pattern`_ with
the Django models.

The Strategies are displayed in SelectBoxes as standard choice field

.. _Strategy Pattern: http://www.oodesign.com/strategy-pattern.html

This package provides the following custom fields:

* StrategyField
* MultipleStrategyField
* StrategyClassField
* MultipleStrategyClassField

 The *StrategyField can be accessed as instance of the model and have an
 attribute `context` that point to model (reverse relation)

Use case
========

As example we can imagine an application that manages `Events` that need to be notified to users.
Each `Occurrence` of `Event` can be notified using different transport, (email, sms,...).
We want to be able to add/change the way we send notification, per event basis, simply using
the Django admin panel. 

.. code-block:: python


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
    registry = Registry()
    registry.register(EmailStrategy)
    registry.register(SMSStrategy)

    class Event(models.Model):
        sender = StrategyField(registry)

    Event.objects.get_or_create(sender=EmailStrategy)
    ...
    ...
    e = Event.objects.get(sender=EmailStrategy)
    e.sender.send() # e.sender.context == e
