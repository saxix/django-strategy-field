from demo.models import Sender1, Sender2, Strategy1, Strategy2
from django.urls import reverse
from pyquery import PyQuery

from strategy_field.utils import fqn


def test_admin_create(webapp, admin_user):
    url = reverse("admin:demo_demoallmodel_add")
    res = webapp.get(url, user=admin_user)

    form = res.forms["demoallmodel_form"]
    form["choice"] = fqn(Sender1)
    form["multiple"] = [fqn(Sender1), fqn(Sender2)]

    form["custom"] = fqn(Strategy2)
    form["custom_multiple"] = [fqn(Strategy1), fqn(Strategy2)]
    res = form.submit().follow()
    pq = PyQuery(res.content)
    assert pq("#result_list tbody tr td.field-choice").text() == "<class 'demo.models.Sender1'>"
    assert (
        pq("#result_list tbody tr td.field-multiple").text()
        == "<class 'demo.models.Sender1'>, <class 'demo.models.Sender2'>"
    )
    assert pq("#result_list tbody tr td.field-custom").text() == "Verbose Strategy2"
    assert pq("#result_list tbody tr td.field-custom_multiple").text() == "Verbose Strategy1, Verbose Strategy2"


def test_admin_edit(webapp, admin_user, demo_all_model):
    url = reverse("admin:demo_demoallmodel_change", args=(demo_all_model.id,))
    res = webapp.get(url, user=admin_user)
    form = res.forms["demoallmodel_form"]
    assert form.fields["choice"][0].value == fqn(demo_all_model.choice)
    form["choice"] = fqn(Sender2)
    form["multiple"] = [fqn(Sender2)]

    form["custom"] = fqn(Strategy1)
    form["custom_multiple"] = [fqn(Strategy1)]
    res = form.submit().follow()

    pq = PyQuery(res.content)
    assert pq("#result_list tbody tr td.field-choice").text() == "<class 'demo.models.Sender2'>"
    assert pq("#result_list tbody tr td.field-multiple").text() == "<class 'demo.models.Sender2'>"
    assert pq("#result_list tbody tr td.field-custom").text() == "Verbose Strategy1"
    assert pq("#result_list tbody tr td.field-custom_multiple").text() == "Verbose Strategy1"


def test_admin_changelist(webapp, admin_user, demo_all_model):
    url = reverse("admin:demo_demoallmodel_changelist")
    res = webapp.get(url, user=admin_user)
    res = res.click("demo.models.Sender1")
    pq = PyQuery(res.content)
    assert pq("#result_list tbody tr td.field-choice").text() == "<class 'demo.models.Sender1'>"
    res = res.click("demo.models.Sender2")
    assert "0 demo all models" in res.text
    res = res.click("demo.models.Sender1")
    assert "1 demo all model" in res.text
