from demo.models import DemoModel, Strategy2


def test_raw_value():
    d = DemoModel(sender=Strategy2)
    assert d.sender == Strategy2
    assert d._strategy_fqn_sender == "demo.models.Strategy2"
