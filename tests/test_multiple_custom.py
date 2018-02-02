# -*- coding: utf-8 -*-
# flake8: noqa
# noqa
import pytest
from django.forms.models import modelform_factory
from demoproject.compat import reverse
from demoproject.demoapp.models import (DemoMultipleCustomModel, Strategy,
                                        Strategy1,)
from strategy_field.utils import fqn


def pytest_generate_tests(metafunc):
    func_name = metafunc.function.__name__
    values = ids = []
    if 'target' in metafunc.fixturenames:
        if func_name.endswith('_lookup_in'):
            values = [lambda o: [fqn(o.sender[0])],
                      lambda o: o.sender,
                      lambda o: [fqn(Strategy), fqn(Strategy1)],
                      lambda o: [Strategy, Strategy1]]
            ids = ['fqn(target.sender)',
                   'target.sender',
                   'fqn(Strategy)',
                   'Strategy']
        else:
            values = [lambda o: [fqn(Strategy)],
                      lambda o: [Strategy]]
            ids = ['fqn(Strategy)',
                   'Strategy']

            if 'demo_multiplecustom_model' in metafunc.fixturenames:
                values.extend([lambda o: [fqn(o.sender[0])],
                               lambda o: o.sender])
                ids.extend(['fqn(target.sender)',
                            'target.sender'])

        metafunc.parametrize("target", values, ids=ids)


def test_field():
    d = DemoMultipleCustomModel(sender=[Strategy])
    assert isinstance(d.sender[0], Strategy)


@pytest.mark.django_db
def test_model_save(target):
    d = DemoMultipleCustomModel(sender=target(None))
    d.save()
    assert isinstance(d.sender[0], Strategy)


@pytest.mark.django_db
def test_model_save_multiple():
    d = DemoMultipleCustomModel(sender=[Strategy, Strategy1])
    d.save()
    assert len(d.sender) == 2
    assert isinstance(d.sender[0], Strategy)
    assert isinstance(d.sender[1], Strategy1)


@pytest.mark.django_db
def test_model_get_or_create(target):
    d, __ = DemoMultipleCustomModel.objects.get_or_create(sender=target(None))
    assert isinstance(d.sender[0], Strategy)


@pytest.mark.django_db
def test_model_load(demo_multiplecustom_model):
    d = DemoMultipleCustomModel.objects.get(pk=demo_multiplecustom_model.pk)
    assert isinstance(d.sender[0], Strategy)


@pytest.mark.django_db
def test_form_load():
    d = DemoMultipleCustomModel(sender=[Strategy, Strategy1])
    form_class = modelform_factory(DemoMultipleCustomModel, exclude=[])
    form = form_class(instance=d)
    assert form.fields['sender'].choices == [('demoproject.demoapp.models.Strategy',
                                              'demoproject.demoapp.models.Strategy'),
                                             ('demoproject.demoapp.models.Strategy1',
                                              'demoproject.demoapp.models.Strategy1')]


@pytest.mark.django_db
def test_form_save(demo_multiplecustom_model):
    form_class = modelform_factory(DemoMultipleCustomModel, exclude=[])
    form = form_class({'sender': [fqn(demo_multiplecustom_model.sender[0])]},
                      instance=demo_multiplecustom_model)
    form.is_valid()
    instance = form.save()
    assert instance.sender == demo_multiplecustom_model.sender


@pytest.mark.django_db
def test_form_not_valid(demo_multiplecustom_model):
    form_class = modelform_factory(DemoMultipleCustomModel, exclude=[])
    form = form_class(
        {'sender': [fqn(DemoMultipleCustomModel)]}, instance=demo_multiplecustom_model)
    assert not form.is_valid()
    assert form.errors['sender'] == ['Select a valid choice. '
                                     'demoproject.demoapp.models.DemoMultipleCustomModel '
                                     'is not one of the available choices.']


@pytest.mark.django_db
def test_form_default(demo_multiplecustom_model):
    form_class = modelform_factory(DemoMultipleCustomModel, exclude=[])
    form = form_class(instance=demo_multiplecustom_model)
    assert form.fields['sender'].choices == [('demoproject.demoapp.models.Strategy',
                                              'demoproject.demoapp.models.Strategy'),
                                             ('demoproject.demoapp.models.Strategy1',
                                              'demoproject.demoapp.models.Strategy1')]
    # assert form.as_table() == u'<tr><th><label for="id_sender">Sender:</label></th>' \
    #                           u'<td><select multiple="multiple" id="id_sender" name="sender">\n' \
    #                           u'<option value="demoproject.demoapp.models.Strategy" selected="selected">demoproject.demoapp.models.Strategy</option>\n' \
    #                           u'<option value="demoproject.demoapp.models.Strategy1">demoproject.demoapp.models.Strategy1</option>\n</select></td></tr>'


@pytest.mark.django_db
def test_admin_demo_multiple_model_add(webapp, admin_user):
    res = webapp.get('/demoapp/demomultiplecustommodel/add/', user=admin_user)
    res.form['sender'].force_value(['demoproject.demoapp.models.Strategy'])
    res.form.submit().follow()
    assert DemoMultipleCustomModel.objects.filter(
        sender='demoproject.demoapp.models.Strategy').count() == 1


@pytest.mark.django_db
def test_admin_demo_multiple_model_edit(webapp, admin_user, demo_multiplecustom_model):
    demo_multiplecustom_model.sender = [Strategy, Strategy1]
    demo_multiplecustom_model.save()
    url = reverse('admin:demoapp_demomultiplecustommodel_change', args=[demo_multiplecustom_model.pk])
    res = webapp.get(url, user=admin_user)
    assert res.context['adminform'].form.fields['sender'].choices == [('demoproject.demoapp.models.Strategy',
                                              'demoproject.demoapp.models.Strategy'),
                                             ('demoproject.demoapp.models.Strategy1',
                                              'demoproject.demoapp.models.Strategy1')]


    res.form['sender'] = ['demoproject.demoapp.models.Strategy',
                          'demoproject.demoapp.models.Strategy1']
    res.form.submit().follow()
    res = webapp.get(url, user=admin_user)
    assert res.context['adminform'].form.fields['sender'].choices == [('demoproject.demoapp.models.Strategy',
                                                                       'demoproject.demoapp.models.Strategy'),
                                                                      ('demoproject.demoapp.models.Strategy1',
                                                                       'demoproject.demoapp.models.Strategy1')]

    # assert res.context['adminform'].form.as_table() == u'<tr><th><label for="id_sender">Sender:</label></th>' \
    #                                                    u'<td><select multiple="multiple" id="id_sender" name="sender">\n' \
    #                                                    u'<option value="demoproject.demoapp.models.Strategy" selected="selected">demoproject.demoapp.models.Strategy</option>\n' \
    #                                                    u'<option value="demoproject.demoapp.models.Strategy1" selected="selected">demoproject.demoapp.models.Strategy1</option>\n' \
    #                                                    u'</select></td></tr>'


# @pytest.mark.django_db
# def test_admin_demo_multiple_model_validate(webapp, admin_user, demo_multiplecustom_model):
# res = webapp.get('/admin/demo/demomultiplecustommodel/%s/' % demo_multiplecustom_model.pk, user=admin_user)
#     res.form['sender'] = ['invalid']
#     res = res.form.submit()
#     assert 'Select a valid choice' in res.context['adminform'].form.errors['sender'][0]


@pytest.mark.django_db
def test_demo_multiple_model_lookup_equal(demo_multiplecustom_model, target):
    assert DemoMultipleCustomModel.objects.get(sender=target(
        demo_multiplecustom_model)) == demo_multiplecustom_model


@pytest.mark.django_db
def test_demo_multiple_model_lookup_contains(demo_multiplecustom_model, target):
    assert DemoMultipleCustomModel.objects.get(
        sender__contains=target(demo_multiplecustom_model)) == demo_multiplecustom_model


@pytest.mark.django_db
def test_demo_multiple_model_lookup_in(demo_multiplecustom_model, target):
    with pytest.raises(TypeError):
        assert DemoMultipleCustomModel.objects.get(
            sender__in=target(demo_multiplecustom_model)) == demo_multiplecustom_model
