# -*- coding: utf-8 -*-
import pytest
from django.forms.models import modelform_factory
from demoproject.compat import reverse
from demoproject.demoapp.models import DemoMultipleModel, Sender1, Sender2
from strategy_field.utils import fqn


def pytest_generate_tests(metafunc):
    func_name = metafunc.function.__name__
    values = ids = []
    if 'target' in metafunc.fixturenames:
        if func_name.endswith('_lookup_in'):
            values = [lambda o: [fqn(o.sender[0])],
                      lambda o: o.sender,
                      lambda o: [fqn(Sender1), fqn(Sender2)],
                      lambda o: [Sender1, Sender2]]
            ids = ['fqn(target.sender)',
                   'target.sender',
                   'fqn(Sender1)',
                   'Sender1']
        else:
            values = [lambda o: [fqn(Sender1)],
                      lambda o: [Sender1]]
            ids = ['fqn(Sender1)',
                   'Sender1']

            if 'demo_multiple_model' in metafunc.fixturenames:
                values.extend([lambda o: [fqn(o.sender[0])],
                               lambda o: o.sender])
                ids.extend(['fqn(target.sender)',
                            'target.sender'])

        metafunc.parametrize("target", values, ids=ids)


def test_field_none():
    d = DemoMultipleModel(sender=None)
    assert d.sender is None


@pytest.mark.django_db
def test_field_none_saved():
    d = DemoMultipleModel(sender=None)
    d.sender = None
    d.save()
    assert d.sender is None


def test_field_empty():
    d = DemoMultipleModel(sender=[])
    assert d.sender == []


def test_field_empty_len():
    expected = 0
    d = DemoMultipleModel(sender=[])
    assert d.sender.__len__() == expected


def test_field():
    d = DemoMultipleModel(sender=Sender1)
    assert d.sender == [Sender1]


@pytest.mark.django_db
def test_basic():
    d = DemoMultipleModel(sender=Sender1)
    d.save()
    assert d.sender == [Sender1]

    d = DemoMultipleModel(sender=[Sender1])
    d.save()
    assert d.sender == [Sender1]

    d = DemoMultipleModel()
    d.sender = Sender1
    d.save()
    assert d.sender == [Sender1]

    d = DemoMultipleModel()
    d.sender = [Sender1]
    d.save()
    assert d.sender == [Sender1]

    d = DemoMultipleModel()
    d.sender = [Sender1, Sender2]
    d.save()
    assert d.sender == [Sender1, Sender2]


@pytest.mark.django_db
def test_model_save(target):
    d = DemoMultipleModel(sender=target(None))
    d.save()
    assert d.sender == [Sender1]


@pytest.mark.django_db
def test_model_get_or_create(target):
    d, __ = DemoMultipleModel.objects.get_or_create(sender=target(None))
    assert d.sender == [Sender1]


@pytest.mark.django_db
def test_model_load(demo_multiple_model):
    d = DemoMultipleModel.objects.get(pk=demo_multiple_model.pk)
    assert d.sender == [Sender1]


@pytest.mark.django_db
def test_form(demo_multiple_model, registry):
    # demo_multiple_model._meta.get_field_by_name('sender')[0].registry = registry
    demo_multiple_model._meta.get_field('sender').registry = registry
    form_class = modelform_factory(DemoMultipleModel, exclude=[])
    form = form_class(instance=demo_multiple_model)
    assert form.fields['sender'].choices == registry.as_choices()


@pytest.mark.django_db
def test_form_save(demo_multiple_model):
    form_class = modelform_factory(DemoMultipleModel, exclude=[])
    form = form_class({'sender': [fqn(demo_multiple_model.sender[0])]}, instance=demo_multiple_model)
    form.is_valid()
    instance = form.save()
    assert instance.sender == demo_multiple_model.sender


@pytest.mark.django_db
def test_form_not_valid(demo_multiple_model):
    form_class = modelform_factory(DemoMultipleModel, exclude=[])
    form = form_class({'sender': [fqn(DemoMultipleModel)]}, instance=demo_multiple_model)
    assert not form.is_valid()
    assert form.errors['sender'] == ['Select a valid choice. '
                                     'demoproject.demoapp.models.DemoMultipleModel '
                                     'is not one of the available choices.']


@pytest.mark.django_db
def test_form_default(demo_multiple_model):
    form_class = modelform_factory(DemoMultipleModel, exclude=[])
    form = form_class(instance=demo_multiple_model)
    assert form.fields['sender'].choices == [('demoproject.demoapp.models.Sender1',
                                              'demoproject.demoapp.models.Sender1'),
                                             ('demoproject.demoapp.models.Sender2',
                                              'demoproject.demoapp.models.Sender2')]


@pytest.mark.django_db
def test_admin_demo_multiple_model_add(webapp, admin_user):
    res = webapp.get('/demoapp/demomultiplemodel/add/', user=admin_user)
    res.form['sender'] = ['demoproject.demoapp.models.Sender1']
    res.form.submit().follow()
    assert DemoMultipleModel.objects.filter(sender='demoproject.demoapp.models.Sender1').count() == 1


@pytest.mark.django_db
def test_admin_demo_multiple_model_edit(webapp, admin_user, demo_multiple_model):
    url = reverse('admin:demoapp_demomultiplemodel_change', args=[demo_multiple_model.pk])
    res = webapp.get(url, user=admin_user)
    res.form['sender'] = ['demoproject.demoapp.models.Sender2']
    res.form.submit().follow()
    assert DemoMultipleModel.objects.filter(sender='demoproject.demoapp.models.Sender2').count() == 1


@pytest.mark.django_db
def test_demo_multiple_model_lookup_equal(demo_multiple_model, target):
    assert DemoMultipleModel.objects.get(sender=target(demo_multiple_model)) == demo_multiple_model


@pytest.mark.django_db
def test_demo_multiple_model_lookup_contains(demo_multiple_model, target):
    assert DemoMultipleModel.objects.get(sender__contains=target(demo_multiple_model)) == demo_multiple_model


@pytest.mark.django_db
def test_demo_multiple_model_lookup_in(demo_multiple_model, target):
    with pytest.raises(TypeError):
        assert DemoMultipleModel.objects.get(sender__in=[target(demo_multiple_model)]) == demo_multiple_model
