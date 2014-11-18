# -*- coding: utf-8 -*-
from django.contrib import admin
from django.forms import TextInput, ModelForm
from .models import (DemoModel, DemoMultipleModel,
                     DemoModelProxy, DemoCustomModel, DemoAllModel,
                     DemoMultipleCustomModel)
# from .fields import CustomMultipleStrategyField, CustomStrategyField
# from strategy_field.fields import StrategyField


class DemoModelForm(ModelForm):
    class Meta:
        model = DemoModelProxy
        widgets = {'sender': TextInput}


class DemoModelProxyAdmin(admin.ModelAdmin):
    form = DemoModelForm


admin.site.register(DemoModelProxy, DemoModelProxyAdmin)

admin.site.register(DemoAllModel)
admin.site.register(DemoMultipleModel)
admin.site.register(DemoModel)
admin.site.register(DemoCustomModel)

admin.site.register(DemoMultipleCustomModel)
