# -*- coding: utf-8 -*-
# !qa: E501
import pytest
from django.forms.models import modelform_factory
from django.core.urlresolvers import reverse
from demoproject.demoapp.models import DemoCustomModel, Strategy, Strategy1
from strategy_field.utils import fqn


def pytest_generate_tests(metafunc):
    func_name = metafunc.function.__name__
    values = ids = []
    if 'target' in metafunc.fixturenames:
        if func_name.endswith('_lookup_in'):
            values = [lambda o: [fqn(o.sender)],
                      lambda o: [o.sender],
                      lambda o: [fqn(Strategy), fqn(Strategy1)],
                      lambda o: [Strategy, Strategy1]]
            ids = ['fqn(target.sender)',
                   'target.sender',
                   'fqn(Strategy)',
                   'Strategy']
        else:
            values = [lambda o: fqn(Strategy)]
            ids = ['fqn(Strategy)']
            if 'democustommodel' in metafunc.fixturenames:
                values.extend([lambda o: fqn(o.sender),
                               lambda o: o.sender])
                ids.extend(['fqn(target.sender)',
                            'target.sender'])

        metafunc.parametrize("target", values, ids=ids)


def test_field():
    d = DemoCustomModel(sender=Strategy)
    assert isinstance(d.sender, Strategy)


@pytest.mark.django_db
def test_model_save(target):
    d = DemoCustomModel(sender=target(None))
    d.save()
    assert isinstance(d.sender, Strategy)


@pytest.mark.django_db
def test_model_get_or_create(target):
    d, __ = DemoCustomModel.objects.get_or_create(sender=target(None))
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
    form = form_class({'sender': fqn(DemoCustomModel)}, instance=democustommodel)
    assert not form.is_valid()
    assert form.errors['sender'] == ['Select a valid choice. '
                                     'demoproject.demoapp.models.DemoCustomModel '
                                     'is not one of the available choices.']


@pytest.mark.django_db
def test_form_default(democustommodel):
    form_class = modelform_factory(DemoCustomModel, exclude=[])
    form = form_class(instance=democustommodel)
    assert form.as_table() == u'<tr><th><label for="id_sender">Sender:</label></th>' \
                              u'<td><select id="id_sender" name="sender">\n' \
                              u'<option value="">---------</option>\n' \
                              u'<option value="demoproject.demoapp.models.Strategy" selected="selected">demoproject.demoapp.models.Strategy</option>\n' \
                              u'<option value="demoproject.demoapp.models.Strategy1">demoproject.demoapp.models.Strategy1</option>\n</select></td></tr>'


@pytest.mark.django_db
def test_admin_demomodel_add(webapp, admin_user):
    res = webapp.get('/demoapp/democustommodel/add/', user=admin_user)
    res.form['sender'] = 'demoproject.demoapp.models.Strategy'
    res.form.submit().follow()
    assert DemoCustomModel.objects.filter(sender='demoproject.demoapp.models.Strategy').count() == 1


@pytest.mark.django_db
def test_admin_demomodel_edit(webapp, admin_user, democustommodel):
    url = reverse('admin:demoapp_democustommodel_change', args=[democustommodel.pk])
    res = webapp.get(url, user=admin_user)
    res.form['sender'] = 'demoproject.demoapp.models.Strategy'
    res.form.submit().follow()
    assert DemoCustomModel.objects.filter(sender='demoproject.demoapp.models.Strategy').count() == 1


@pytest.mark.django_db
def test_demomodel_lookup_equal(democustommodel, target):
    assert DemoCustomModel.objects.get(sender=target(democustommodel)) == democustommodel


@pytest.mark.django_db
def test_demomodel_lookup_contains(democustommodel, target):
    assert DemoCustomModel.objects.get(sender__contains=target(democustommodel)) == democustommodel


@pytest.mark.django_db
def test_demomodel_lookup_in(democustommodel, target):
    assert DemoCustomModel.objects.get(sender__in=target(democustommodel)) == democustommodel
