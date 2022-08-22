from demoproject.demoapp.models import DemoModel, Strategy1


def test_raw_value():
    d = DemoModel(sender=Strategy1)
    assert d.sender == Strategy1
    assert d._strategy_fqn_sender == "demoproject.demoapp.models.Strategy1"
