from demoproject.demoapp.models import Strategy1
from strategy_field.fields import (MultipleStrategyClassFieldDescriptor,
                                   MultipleStrategyFieldDescriptor,
                                   StrategyClassFieldDescriptor,
                                   StrategyFieldDescriptor,)
from strategy_field.utils import fqn


class MockField:
    value = fqn(StrategyFieldDescriptor)
    import_error = None
    factory = lambda x, s: x(s)

    # name = 'strategy'
    def __init__(self, owner=None):
        pass


class MockModel:
    def __init__(self):
        self.strategy = fqn(MockField)
        self.errored = '3333'


class MultipleMockModel:
    def __init__(self):
        self.strategy = [fqn(MockField)]
        self.strategy1 = 'test_descriptors.MockField,'
        self.strategy2 = MockField
        self.errored = ['3333']


def test_strategyclassfielddescriptor():
    desc1 = StrategyClassFieldDescriptor(type("Field", (MockField,), {'name': 'strategy'}))
    desc2 = StrategyClassFieldDescriptor(type("Field", (MockField,), {'name': 'errored'}))
    desc3 = StrategyClassFieldDescriptor(type("Field", (MockField,), {'name': 'errored',
                                                                      'import_error': lambda *a: Strategy1}))

    # strategy
    obj = MockModel()
    assert desc1.__get__(None) is None
    assert desc1.__get__(obj) == 'test_descriptors.MockField'

    # assert desc2.__get__(obj) is None
    assert desc3.__set__(obj, 22) is None

    desc1.__set__(obj, fqn(StrategyClassFieldDescriptor))
    assert obj.strategy == StrategyClassFieldDescriptor


def test_multiplestrategyclassfielddescriptor():
    desc0 = MultipleStrategyClassFieldDescriptor(type("Field", (MockField,), {'name': 'strategy'}))
    desc1 = MultipleStrategyClassFieldDescriptor(type("Field", (MockField,), {'name': 'strategy1'}))
    desc2 = MultipleStrategyClassFieldDescriptor(type("Field", (MockField,), {'name': 'strategy2'}))
    desc3 = MultipleStrategyClassFieldDescriptor(type("Field", (MockField,), {'name': 'errored'}))
    desc4 = MultipleStrategyClassFieldDescriptor(type("Field", (MockField,), {'name': 'errored',
                                                                              'import_error': lambda *a: 22}))

    # strategy
    obj = MultipleMockModel()
    assert desc0.__get__(None) is None
    assert desc0.__get__(obj) == [MockField]

    assert desc1.__get__(obj) == [MockField]
    assert desc2.__get__(obj) == [MockField]

    assert desc3.__get__(obj) is None
    assert desc4.__get__(obj) == 22

    #
    desc1.__set__(obj, [fqn(StrategyClassFieldDescriptor)])
    assert obj.strategy1 == ['strategy_field.fields.StrategyClassFieldDescriptor']


def test_strategyfielddescriptor():
    desc1 = StrategyFieldDescriptor(type("Field", (MockField,), {'name': 'strategy'}))
    # desc2 = StrategyFieldDescriptor(type("Field", (MockField,), {'name': 'errored'}))
    desc3 = StrategyFieldDescriptor(type("Field", (MockField,), {'name': 'errored',
                                                                 'import_error': lambda *a: None}))

    # strategy
    obj = MockModel()
    assert desc1.__get__(None) is None
    assert desc1.__get__(obj) == 'test_descriptors.MockField'

    # assert desc2.__get__(obj) == '3333'
    # assert desc3.__get__(obj) == '3333'

    desc1.__set__(obj, fqn(StrategyClassFieldDescriptor))
    assert isinstance(obj.strategy, StrategyClassFieldDescriptor)

    desc1.__set__(obj, 0)
    assert obj.strategy is None

    desc1.__set__(obj, '--')
    assert obj.strategy is None

    desc3.__set__(obj, '--')
    assert obj.strategy is None


def test_MultipleStrategyFieldDescriptor():
    desc0 = MultipleStrategyFieldDescriptor(type("Field", (MockField,), {'name': 'strategy'}))
    desc1 = MultipleStrategyFieldDescriptor(type("Field", (MockField,), {'name': 'strategy1'}))
    # desc2 = MultipleStrategyFieldDescriptor(type("Field", (MockField,), {'name': 'strategy2'}))
    desc3 = MultipleStrategyFieldDescriptor(type("Field", (MockField,), {'name': 'errored'}))
    desc4 = MultipleStrategyFieldDescriptor(type("Field", (MockField,), {'name': 'errored',
                                                                         'import_error': lambda *a: 22}))

    # strategy
    obj = MultipleMockModel()
    assert desc0.__get__(None) == []
    # assert desc0.__get__(obj) == [MockField]

    # assert desc1.__get__(obj) == [MockField]
    # assert desc2.__get__(obj) == [MockField]

    assert desc3.__get__(obj) == []
    assert desc4.__get__(obj) == []

    #
    desc1.__set__(obj, [fqn(StrategyClassFieldDescriptor)])
    assert obj.strategy1 == ['strategy_field.fields.StrategyClassFieldDescriptor']
