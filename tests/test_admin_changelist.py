from django.urls import reverse
from pyquery import PyQuery

from demo.models import Sender1
from strategy_field.utils import fqn


def test_admin_create(webapp, admin_user):
    url = reverse("admin:demo_demomodelnone_add")
    res = webapp.get(url, user=admin_user)
    form = res.forms['demomodelnone_form']
    form['sender'] = fqn(Sender1)
    res = form.submit().follow()
    pq = PyQuery(res.content)
    assert pq('#result_list tbody tr td.field-sender').text() == "<class 'demo.models.Sender1'>"
    assert pq('#result_list tbody tr td.field-strategy').text() == "demo.models.Sender1"
