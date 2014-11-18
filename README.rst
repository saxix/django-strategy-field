=====================
django-strategy-field
=====================

DFS is a custome field to enable the implementation of the Strategy Pattern with
the django models.

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

    class Event(models.Model):
        sender = StrategyField()


    e = Event()
    e.sender = EmailStrategy
    e.save()

    e.sender.send()
    # e.sender.context == e

