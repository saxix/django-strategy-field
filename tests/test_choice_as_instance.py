# -*- coding: utf-8 -*-
# !qa: E501
import pytest
from django.forms.models import modelform_factory
from demoproject.compat import reverse
from demoproject.demoapp.models import DemoCustomModel, Strategy, Strategy1
from strategy_field.utils import fqn


def pytest_generate_tests(metafunc):
    func_name = metafunc.function.__name__
    values = ids = []
    if 'target_factory' in metafunc.fixturenames:
        if func_name.endswith('_lookup_in'):
            values = [lambda o: [fqn(o.sender)],
                      lambda o: [o.sender],
                      lambda o: [fqn(Strategy), fqn(Strategy1)],
                      lambda o: [Strategy, Strategy1]]
            ids = [fqn(Strategy),
                   '<context.sender instance>',
                   str([fqn(Strategy)]),
                   str([Strategy, Strategy1])]
        elif func_name == ('test_model_save'):
            values = [lambda o: fqn(o.sender),
                      lambda o: o.sender,
                      lambda o: Strategy(o, 'b')]
            ids = [fqn(Strategy),
                   '<context.sender instance>',
                   'Strategy1(context)']
        else:
            values = [lambda o: fqn(Strategy)]
            ids = ['fqn(Strategy)']
            if 'democustommodel' in metafunc.fixturenames:
                values.extend([lambda o: fqn(o.sender),
                               lambda o: o.sender])
                ids.extend(['fqn(target_factory.sender)',
                            'target_factory.sender'])

        metafunc.parametrize("target_factory", values, ids=ids)


def test_field():
    d = DemoCustomModel(sender=Strategy)
    assert isinstance(d.sender, Strategy)
    assert d.sender == d.sender
    assert d.sender.context == d


@pytest.mark.django_db
def test_model_save(target_factory):
    d = DemoCustomModel(sender=Strategy)
    d.sender = target_factory(d)
    d.save()
    assert isinstance(d.sender, Strategy)
    assert d.sender == d.sender
    assert d.sender.context == d


@pytest.mark.django_db
def test_model_get_or_create(target_factory):
    d, __ = DemoCustomModel.objects.get_or_create(sender=target_factory(None))
    assert isinstance(d.sender, Strategy)


@pytest.mark.django_db
def test_model_load(democustommodel):
    d = DemoCustomModel.objects.get(pk=democustommodel.pk)
    assert isinstance(d.sender, Strategy)


# @pytest.mark.django_db
# def test_form(democustommodel, registry):
#     democustommodel._meta.get_field_by_name('sender')[0].registry = registry
#     form_class = modelform_factory(DemoCustomModel)
#     form = form_class(instance=democustommodel)
#     assert form.fields['sender'].choices[1:] == registry.as_choices()


@pytest.mark.django_db
def test_form_save(democustommodel):
    form_class = modelform_factory(DemoCustomModel, exclude=[])
    form = form_class({'sender': fqn(democustommodel.sender)},
                      instance=democustommodel)
    form.is_valid()
    instance = form.save()
    assert instance.sender == democustommodel.sender


@pytest.mark.django_db
def test_form_not_valid(democustommodel):
    form_class = modelform_factory(DemoCustomModel, exclude=[])
    form = form_class({'sender': fqn(DemoCustomModel)},
                      instance=democustommodel)
    assert not form.is_valid()
    assert form.errors['sender'] == ['Select a valid choice. '
                                     'demoproject.demoapp.models.DemoCustomModel '
                                     'is not one of the available choices.']


@pytest.mark.django_db
def test_form_default(democustommodel):
    form_class = modelform_factory(DemoCustomModel, exclude=[])
    form = form_class(instance=democustommodel)
    assert form.fields['sender'].choices == [(u'', u'---------'),
                                             ('demoproject.demoapp.models.Strategy',
                                              'demoproject.demoapp.models.Strategy'),
                                             ('demoproject.demoapp.models.Strategy1',
                                              'demoproject.demoapp.models.Strategy1')]


@pytest.mark.django_db
def test_admin_demomodel_add(webapp, admin_user):
    res = webapp.get('/demoapp/democustommodel/add/', user=admin_user)
    res.form['sender'] = 'demoproject.demoapp.models.Strategy'
    res.form.submit().follow()
    assert DemoCustomModel.objects.filter(
        sender='demoproject.demoapp.models.Strategy').count() == 1


@pytest.mark.django_db
def test_admin_demomodel_edit(webapp, admin_user, democustommodel):
    url = reverse('admin:demoapp_democustommodel_change',
                  args=[democustommodel.pk])
    res = webapp.get(url, user=admin_user)
    res.form['sender'] = 'demoproject.demoapp.models.Strategy'
    res.form.submit().follow()
    assert DemoCustomModel.objects.filter(
        sender='demoproject.demoapp.models.Strategy').count() == 1


@pytest.mark.django_db
def test_demomodel_lookup_equal(democustommodel, target_factory):
    assert DemoCustomModel.objects.get(
        sender=target_factory(democustommodel)) == democustommodel


@pytest.mark.django_db
def test_demomodel_lookup_contains(democustommodel, target_factory):
    assert DemoCustomModel.objects.get(
        sender__contains=target_factory(democustommodel)) == democustommodel


@pytest.mark.django_db
def test_demomodel_lookup_in(democustommodel, target_factory):
    assert DemoCustomModel.objects.get(
        sender__in=target_factory(democustommodel)) == democustommodel
