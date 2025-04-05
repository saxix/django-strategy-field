import pytest
from demo.models import DemoMultipleCustomModel, Strategy1, Strategy2, DemoAllModel
from django.forms.models import modelform_factory
from django.urls import reverse
from strategy_field.utils import fqn


def pytest_generate_tests(metafunc):
    func_name = metafunc.function.__name__
    values = ids = []
    if "target" in metafunc.fixturenames:
        if func_name.endswith("_lookup_in"):
            values = [
                lambda o: [fqn(o.sender[0])],
                lambda o: o.sender,
                lambda o: [fqn(Strategy1), fqn(Strategy2)],
                lambda o: [Strategy1, Strategy2],
            ]
            ids = ["fqn(target.sender)", "target.sender", "fqn(Strategy1)", "Strategy1"]
        else:
            values = [lambda o: [fqn(Strategy1)], lambda o: [Strategy1]]
            ids = ["fqn(Strategy1)", "Strategy1"]

            if "demo_multiplecustom_model" in metafunc.fixturenames:
                values.extend([lambda o: [fqn(o.sender[0])], lambda o: o.sender])
                ids.extend(["fqn(target.sender)", "target.sender"])

        metafunc.parametrize("target", values, ids=ids)


def test_field():
    d = DemoMultipleCustomModel(sender=[Strategy1])
    assert isinstance(d.sender[0], Strategy1)


@pytest.mark.django_db
def test_model_save(target):
    d = DemoMultipleCustomModel(sender=target(None))
    d.save()
    assert isinstance(d.sender[0], Strategy1)


@pytest.mark.django_db
def test_model_save_multiple():
    d = DemoMultipleCustomModel(sender=[Strategy1, Strategy2])
    d.save()
    assert len(d.sender) == 2
    assert isinstance(d.sender[0], Strategy1)
    assert isinstance(d.sender[1], Strategy2)


@pytest.mark.django_db
def test_model_get_or_create(target):
    d, __ = DemoMultipleCustomModel.objects.get_or_create(sender=target(None))
    assert isinstance(d.sender[0], Strategy1)


@pytest.mark.django_db
def test_model_load(demo_multiplecustom_model):
    d = DemoMultipleCustomModel.objects.get(pk=demo_multiplecustom_model.pk)
    assert isinstance(d.sender[0], Strategy1)


@pytest.mark.django_db
def test_form_load():
    d = DemoMultipleCustomModel(sender=[Strategy1, Strategy2])
    form_class = modelform_factory(DemoMultipleCustomModel, exclude=[])
    form = form_class(instance=d)
    assert form.fields["sender"].choices == [
        ("demo.models.Strategy1", "demo.models.Strategy1"),
        ("demo.models.Strategy2", "demo.models.Strategy2"),
    ]


@pytest.mark.django_db
def test_form_save(demo_multiplecustom_model):
    form_class = modelform_factory(DemoMultipleCustomModel, exclude=[])
    form = form_class(
        {"sender": [fqn(demo_multiplecustom_model.sender[0])]},
        instance=demo_multiplecustom_model,
    )
    form.is_valid()
    instance = form.save()
    assert fqn(instance.sender[0]) == fqn(demo_multiplecustom_model.sender[0])


@pytest.mark.django_db
def test_form_not_valid(demo_multiplecustom_model):
    form_class = modelform_factory(DemoMultipleCustomModel, exclude=[])
    form = form_class({"sender": [fqn(DemoMultipleCustomModel)]}, instance=demo_multiplecustom_model)
    assert not form.is_valid()
    assert form.errors["sender"] == [
        "Select a valid choice. demo.models.DemoMultipleCustomModel is not one of the available choices."
    ]


@pytest.mark.django_db
def test_form_default(demo_multiplecustom_model):
    form_class = modelform_factory(DemoMultipleCustomModel, exclude=[])
    form = form_class(instance=demo_multiplecustom_model)
    assert form.fields["sender"].choices == [
        ("demo.models.Strategy1", "demo.models.Strategy1"),
        ("demo.models.Strategy2", "demo.models.Strategy2"),
    ]
    # assert form.as_table() == u'<tr><th><label for="id_sender">Sender:</label></th>' \
    #                           u'<td><select multiple="multiple" id="id_sender" name="sender">\n' \
    #                           u'<option value="demo.models.Strategy" selected="selected">demo.models.Strategy</option>\n' \
    #                           u'<option value="demo.models.Strategy1">demo.models.Strategy1</option>\n</select></td></tr>'


@pytest.mark.django_db
def test_admin_demo_multiple_model_add(webapp, admin_user):
    res = webapp.get("/demo/demomultiplecustommodel/add/", user=admin_user)
    form = res.forms["demomultiplecustommodel_form"]
    form["sender"].force_value(["demo.models.Strategy1"])
    form.submit().follow()
    assert DemoMultipleCustomModel.objects.filter(sender="demo.models.Strategy1").count() == 1


@pytest.mark.django_db
def test_admin_demo_multiple_model_edit(webapp, admin_user, demo_multiplecustom_model):
    demo_multiplecustom_model.sender = [Strategy1, Strategy2]
    demo_multiplecustom_model.save()
    url = reverse(
        "admin:demo_demomultiplecustommodel_change",
        args=[demo_multiplecustom_model.pk],
    )
    res = webapp.get(url, user=admin_user)
    assert res.context["adminform"].form.fields["sender"].choices == [
        ("demo.models.Strategy1", "demo.models.Strategy1"),
        ("demo.models.Strategy2", "demo.models.Strategy2"),
    ]

    form = res.forms["demomultiplecustommodel_form"]
    form["sender"] = ["demo.models.Strategy1", "demo.models.Strategy2"]
    form.submit().follow()
    res = webapp.get(url, user=admin_user)
    assert res.context["adminform"].form.fields["sender"].choices == [
        ("demo.models.Strategy1", "demo.models.Strategy1"),
        ("demo.models.Strategy2", "demo.models.Strategy2"),
    ]


@pytest.mark.django_db
def test_demo_multiple_model_lookup_equal(demo_multiplecustom_model, target):
    assert DemoMultipleCustomModel.objects.get(sender=target(demo_multiplecustom_model)) == demo_multiplecustom_model


@pytest.mark.django_db
def test_lookups(demo_all_model):
    assert DemoAllModel.objects.filter(choice=demo_all_model.choice).exists()
    assert DemoAllModel.objects.filter(choice__in=[demo_all_model.choice]).exists()

    assert DemoAllModel.objects.filter(custom=demo_all_model.custom).exists()
    assert DemoAllModel.objects.filter(custom__in=[demo_all_model.custom]).exists()

    assert DemoAllModel.objects.filter(multiple=demo_all_model.multiple).exists()
    assert DemoAllModel.objects.filter(multiple__exact=demo_all_model.multiple).exists()
    assert DemoAllModel.objects.filter(multiple__iexact=demo_all_model.multiple).exists()
    assert DemoAllModel.objects.filter(multiple__contains=demo_all_model.multiple[0]).exists()


@pytest.mark.django_db
def test_demo_multiple_model_lookup_in(demo_multiplecustom_model, target):
    with pytest.raises(TypeError):
        assert (
            DemoMultipleCustomModel.objects.get(sender__in=target(demo_multiplecustom_model))
            == demo_multiplecustom_model
        )
