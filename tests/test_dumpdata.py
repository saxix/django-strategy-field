import io
import json

from demo.models import DemoModel, Strategy1
from django.core.management import call_command


def test_dumpdata(db):
    r = DemoModel.objects.create(sender=Strategy1)
    out = io.StringIO()
    call_command("dumpdata", "demo.DemoModel", stdout=out)
    dump = json.loads(out.getvalue())
    assert dump == [
        {
            "model": "demo.demomodel",
            "pk": r.pk,
            "fields": {"sender": "demo.models.Strategy1"},
        }
    ]
