=====================
django-strategy-field
=====================

A Django field for storing a reference to a class or type (as opposed to a specific instance)

DFS is a custom field to enable the implementation of the `Strategy Pattern`_ with
the Django models.

The Strategies are displayed in SelectBoxes as standard choice field


.. _Strategy Pattern: http://www.oodesign.com/strategy-pattern.html


Example
=======

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
