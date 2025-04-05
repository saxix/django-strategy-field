from demo.models import DemoCustomModel, DemoModel, Strategy2, DemoAllModel


def test_class_set_value():
    d = DemoModel(sender=Strategy2)
    assert d.sender == Strategy2
    assert d._strategy_fqn_sender == "demo.models.Strategy2"


def test_instance_set_value():
    d = DemoCustomModel(sender=Strategy2)
    assert isinstance(d.sender, Strategy2)
    assert d._strategy_fqn_sender == "demo.models.Strategy2"


def test_class_create(db):
    d = DemoModel.objects.create(sender=Strategy2)
    assert d.sender == Strategy2


def test_instance_create(db):
    d = DemoCustomModel.objects.create(sender=Strategy2)
    assert isinstance(d.sender, Strategy2)


def test_class_filter(db):
    DemoModel.objects.create(sender=Strategy2)
    assert DemoModel.objects.get(sender="demo.models.Strategy2")
    assert DemoModel.objects.get(sender=Strategy2)


def test_instance_filter(db):
    DemoCustomModel.objects.create(sender=Strategy2)
    assert DemoCustomModel.objects.get(sender=Strategy2)


def test_wrong_argument(db):
    d = DemoAllModel(choice=22, custom=22)
    assert d.choice is None
    assert d.custom is None
