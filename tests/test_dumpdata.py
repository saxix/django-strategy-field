import io
import json

from django.core.management import call_command

from demoproject.demoapp.models import DemoCustomModel, Strategy1, DemoModel


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
