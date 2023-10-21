import io
import json

from demoproject.demoapp.models import DemoModel, Strategy1
from django.core.management import call_command


def test_dumpdata(db):
    r = DemoModel.objects.create(sender=Strategy1)
    out = io.StringIO()
    call_command("dumpdata", "demoapp.DemoModel", stdout=out)
    dump = json.loads(out.getvalue())
    assert dump == [
        {
            "model": "demoapp.demomodel",
            "pk": r.pk,
            "fields": {"sender": "demoproject.demoapp.models.Strategy1"},
        }
    ]
