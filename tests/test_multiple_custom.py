# -*- coding: utf-8 -*-
from fixtures import *  # noqa
import logging
import pytest
from demo.models import Strategy, DemoMultipleCustomModel, Strategy1
from strategy_field.utils import fqn
from django.forms.models import modelform_factory

logger = logging.getLogger(__name__)


def pytest_generate_tests(metafunc):
    func_name = metafunc.function.func_name
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
    form_class = modelform_factory(DemoMultipleCustomModel)
    form = form_class(instance=d)
    assert form.as_table() == u'<tr><th><label for="id_sender">Sender:</label></th>' \
                              u'<td><select multiple="multiple" id="id_sender" name="sender">\n' \
                              u'<option value="demo.models.Strategy" selected="selected">demo.models.Strategy</option>\n' \
                              u'<option value="demo.models.Strategy1" selected="selected">demo.models.Strategy1</option>\n' \
                              u'</select></td></tr>'


@pytest.mark.django_db
def test_form_save(demo_multiplecustom_model):
    form_class = modelform_factory(DemoMultipleCustomModel)
    form = form_class({'sender': [fqn(demo_multiplecustom_model.sender[0])]}, instance=demo_multiplecustom_model)
    form.is_valid()
    instance = form.save()
    assert instance.sender == demo_multiplecustom_model.sender


@pytest.mark.django_db
def test_form_not_valid(demo_multiplecustom_model):
    form_class = modelform_factory(DemoMultipleCustomModel)
    form = form_class({'sender': [fqn(DemoMultipleCustomModel)]}, instance=demo_multiplecustom_model)
    assert not form.is_valid()
    assert form.errors['sender'] == ['Select a valid choice. '
                                     'demo.models.DemoMultipleCustomModel '
                                     'is not one of the available choices.']


@pytest.mark.django_db
def test_form_default(demo_multiplecustom_model):
    form_class = modelform_factory(DemoMultipleCustomModel)
    form = form_class(instance=demo_multiplecustom_model)
    assert form.as_table() == u'<tr><th><label for="id_sender">Sender:</label></th>' \
                              u'<td><select multiple="multiple" id="id_sender" name="sender">\n' \
                              u'<option value="demo.models.Strategy" selected="selected">demo.models.Strategy</option>\n' \
                              u'<option value="demo.models.Strategy1">demo.models.Strategy1</option>\n</select></td></tr>'


@pytest.mark.django_db
def test_admin_demo_multiple_model_add(webapp, admin_user):
    res = webapp.get('/admin/demo/demomultiplecustommodel/add/', user=admin_user)
    res.form['sender'] = ['demo.models.Strategy']
    res.form.submit().follow()
    assert DemoMultipleCustomModel.objects.filter(sender='demo.models.Strategy').count() == 1


@pytest.mark.django_db
def test_admin_demo_multiple_model_edit(webapp, admin_user, demo_multiplecustom_model):
    demo_multiplecustom_model.sender = [Strategy, Strategy1]
    demo_multiplecustom_model.save()
    res = webapp.get('/admin/demo/demomultiplecustommodel/%s/' % demo_multiplecustom_model.pk, user=admin_user)

    assert res.context['adminform'].form.as_table() == u'<tr><th><label for="id_sender">Sender:</label></th>' \
                                                       u'<td><select multiple="multiple" id="id_sender" name="sender">\n' \
                                                       u'<option value="demo.models.Strategy" selected="selected">demo.models.Strategy</option>\n' \
                                                       u'<option value="demo.models.Strategy1" selected="selected">demo.models.Strategy1</option>\n</select></td></tr>'

    res.form['sender'] = ['demo.models.Strategy', 'demo.models.Strategy1']
    res.form.submit().follow()
    res = webapp.get('/admin/demo/demomultiplecustommodel/%s/' % demo_multiplecustom_model.pk, user=admin_user)

    assert res.context['adminform'].form.as_table() == u'<tr><th><label for="id_sender">Sender:</label></th>' \
                                                       u'<td><select multiple="multiple" id="id_sender" name="sender">\n' \
                                                       u'<option value="demo.models.Strategy" selected="selected">demo.models.Strategy</option>\n' \
                                                       u'<option value="demo.models.Strategy1" selected="selected">demo.models.Strategy1</option>\n' \
                                                       u'</select></td></tr>'


# @pytest.mark.django_db
# def test_admin_demo_multiple_model_validate(webapp, admin_user, demo_multiplecustom_model):
# res = webapp.get('/admin/demo/demomultiplecustommodel/%s/' % demo_multiplecustom_model.pk, user=admin_user)
#     res.form['sender'] = ['invalid']
#     res = res.form.submit()
#     assert 'Select a valid choice' in res.context['adminform'].form.errors['sender'][0]


@pytest.mark.django_db
def test_demo_multiple_model_lookup_equal(demo_multiplecustom_model, target):
    assert DemoMultipleCustomModel.objects.get(sender=target(demo_multiplecustom_model)) == demo_multiplecustom_model


@pytest.mark.django_db
def test_demo_multiple_model_lookup_contains(demo_multiplecustom_model, target):
    assert DemoMultipleCustomModel.objects.get(
        sender__contains=target(demo_multiplecustom_model)) == demo_multiplecustom_model


@pytest.mark.django_db
def test_demo_multiple_model_lookup_in(demo_multiplecustom_model, target):
    with pytest.raises(TypeError):
        assert DemoMultipleCustomModel.objects.get(
            sender__in=target(demo_multiplecustom_model)) == demo_multiplecustom_model
