from demo.models import DemoModel, Strategy1


def test_raw_value():
    d = DemoModel(sender=Strategy1)
    assert d.sender == Strategy1
    assert d._strategy_fqn_sender == "demo.models.Strategy1"
