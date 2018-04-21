# -*- coding: utf-8 -*-
# flake8: noqa
import pytest
from demoproject.demoapp.models import Sender2, SenderNotRegistered
from django.forms.models import modelform_factory
from demoproject.compat import reverse
from demoproject.demoapp.models import (DemoModel, DemoModelDefault,
                                        DemoModelCallableDefault,
                                        DemoModelNone, Sender1, )
from strategy_field.utils import fqn


def pytest_generate_tests(metafunc):
    func_name = metafunc.function.__name__
    values = ids = []
    if 'target' in metafunc.fixturenames:
        if func_name.endswith('_lookup_in'):
            values = [lambda o: [fqn(o.sender)],
                      lambda o: [o.sender],
                      lambda o: [fqn(Sender1), fqn(Sender2)],
                      lambda o: [Sender1, Sender2]]
            ids = ['fqn(target.sender)',
                   'target.sender',
                   'fqn(Sender1)',
                   'Sender1']
        else:
            values = [lambda o: fqn(Sender1),
                      lambda o: Sender1]
            ids = [fqn(Sender1),
                   'Sender1']
            if 'demomodel' in metafunc.fixturenames:
                values.extend([lambda o: fqn(o.sender),
                               lambda o: o.sender])
                ids.extend(['fqn(target.sender)',
                            'target.sender'])

        metafunc.parametrize("target", values, ids=ids)


def test_field():
    d = DemoModel(sender=Sender1)
    assert d.sender == Sender1


@pytest.mark.django_db
def test_model_save(target):
    d = DemoModel(sender=target(None))
    d.save()
    assert d.sender == Sender1


@pytest.mark.django_db
def test_model_save_none():
    d = DemoModelNone(sender=None)
    d.save()
    assert d.sender is None


@pytest.mark.django_db
def test_model_save_default():
    d = DemoModelDefault()
    d.save()
    # registry = d._meta.get_field_by_name('sender')[0].registry
    registry = d._meta.get_field('sender').registry
    assert d.sender == registry[0]


@pytest.mark.django_db
def test_model_save_default_with_callable():
    d = DemoModelCallableDefault()
    d.save()
    # registry = d._meta.get_field_by_name('sender')[0].registry
    registry = d._meta.get_field('sender').registry
    assert d.sender == registry[0]


@pytest.mark.django_db
def test_model_get_or_create(target):
    t = target(None)
    d, __ = DemoModel.objects.get_or_create(sender=t)
    assert d.sender == Sender1


@pytest.mark.django_db
def test_model_load(demomodel):
    d = DemoModel.objects.get(pk=demomodel.pk)
    assert d.sender == Sender1


@pytest.mark.django_db
def test_form(demomodel, registry):
    # demomodel._meta.get_field_by_name('sender')[0].registry = registry
    demomodel._meta.get_field('sender').registry = registry
    form_class = modelform_factory(DemoModel, exclude=[])
    form = form_class(instance=demomodel)
    assert form.fields['sender'].choices[1:] == registry.as_choices()


@pytest.mark.django_db
def test_form_save(demomodel):
    form_class = modelform_factory(DemoModel, exclude=[])
    form = form_class({'sender': fqn(demomodel.sender)}, instance=demomodel)
    assert form.is_valid(), form.errors
    instance = form.save()
    assert instance.sender == demomodel.sender


@pytest.mark.django_db
def test_form_not_valid(demomodel):
    form_class = modelform_factory(DemoModel, exclude=[])
    form = form_class({'sender': fqn(DemoModel)}, instance=demomodel)
    assert not form.is_valid()
    assert form.errors['sender'] == ['Select a valid choice. '
                                     'demoproject.demoapp.models.DemoModel '
                                     'is not one of the available choices.']


@pytest.mark.django_db
def test_form_default(demomodel):
    form_class = modelform_factory(DemoModel, exclude=[])
    form = form_class(instance=demomodel)
    assert form.fields['sender'].choices == [(u'', u'---------'),
                                             ('demoproject.demoapp.models.Sender1',
                                              'demoproject.demoapp.models.Sender1'),
                                             ('demoproject.demoapp.models.Sender2',
                                              'demoproject.demoapp.models.Sender2')]

    # assert form.as_table() == u'<tr><th><label for="id_sender">Sender:</label></th>' \
    #                           u'<td><select id="id_sender" name="sender" required>\n' \
    #                           u'<option value="">---------</option>\n' \
    #                           u'<option value="demoproject.demoapp.models.Sender1" selected="selected">demoproject.demoapp.models.Sender1</option>\n' \
    #                           u'<option value="demoproject.demoapp.models.Sender2">demoproject.demoapp.models.Sender2</option>\n</select></td></tr>'


@pytest.mark.django_db
def test_admin_demomodel_add(webapp, admin_user):
    res = webapp.get('/demoapp/demomodel/add/', user=admin_user)
    res.form['sender'] = 'demoproject.demoapp.models.Sender1'
    # import pdb; pdb.set_trace()

    res.form.submit().follow()
    assert DemoModel.objects.filter(
        sender='demoproject.demoapp.models.Sender1').count() == 1


@pytest.mark.django_db
def test_admin_demomodel_edit(webapp, admin_user, demomodel):
    url = reverse('admin:demoapp_demomodel_change', args=[demomodel.pk])
    res = webapp.get(url, user=admin_user)
    res.form['sender'] = 'demoproject.demoapp.models.Sender2'
    res.form.submit().follow()
    assert DemoModel.objects.filter(
        sender='demoproject.demoapp.models.Sender2').count() == 1


@pytest.mark.django_db
def test_admin_demomodel_validate(webapp, admin_user, demomodel):
    url = reverse('admin:demoapp_demomodel_change', args=[demomodel.pk])
    res = webapp.get(url, user=admin_user)
    res.form['sender'].force_value('invalid_strategy_classname')
    res = res.form.submit()
    assert 'Select a valid choice' in res.context[
        'adminform'].form.errors['sender'][0]


@pytest.mark.django_db
def test_demomodel_lookup_equal(demomodel, target):
    assert DemoModel.objects.get(sender=target(demomodel)) == demomodel


@pytest.mark.django_db
def test_demomodel_lookup_contains(demomodel, target):
    assert DemoModel.objects.get(
        sender__contains=target(demomodel)) == demomodel


@pytest.mark.django_db
def test_demomodel_lookup_in(demomodel, target):
    assert DemoModel.objects.get(sender__in=target(demomodel)) == demomodel


@pytest.mark.django_db
def test_display_attribute(demomodel, registry, monkeypatch):
    monkeypatch.setattr(SenderNotRegistered, 'label',
                        classmethod(lambda s: fqn(s).split('.')[-1]),
                        raising=False)

    DemoModel._meta.get_field('sender').display_attribute = 'label'
    DemoModel._meta.get_field('sender').registry = registry
    registry.register(SenderNotRegistered)

    form_class = modelform_factory(DemoModel, exclude=[])
    form = form_class(instance=demomodel)
    assert form.fields['sender'].choices[1][1] == 'SenderNotRegistered'
