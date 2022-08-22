from demoproject.demoapp.models import DemoCustomModel, DemoModel, Strategy1


def test_class_set_value():
    d = DemoModel(sender=Strategy1)
    assert d.sender == Strategy1
    assert d._strategy_fqn_sender == "demoproject.demoapp.models.Strategy1"


def test_instance_set_value():
    d = DemoCustomModel(sender=Strategy1)
    assert isinstance(d.sender, Strategy1)
    assert d._strategy_fqn_sender == "demoproject.demoapp.models.Strategy1"


def test_class_create(db):
    d = DemoModel.objects.create(sender=Strategy1)
    assert d.sender == Strategy1


def test_instance_create(db):
    d = DemoCustomModel.objects.create(sender=Strategy1)
    assert isinstance(d.sender, Strategy1)


def test_class_filter(db):
    DemoModel.objects.create(sender=Strategy1)
    assert DemoModel.objects.get(sender="demoproject.demoapp.models.Strategy1")
    assert DemoModel.objects.get(sender=Strategy1)


def test_instance_filter(db):
    DemoCustomModel.objects.create(sender=Strategy1)
    assert DemoCustomModel.objects.get(sender=Strategy1)
