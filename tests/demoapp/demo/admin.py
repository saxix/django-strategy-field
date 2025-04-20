from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.forms import ModelForm, TextInput

from strategy_field.utils import fqn

from .models import (
    DemoAllModel,
    DemoCustomModel,
    DemoModel,
    DemoModelCallableDefault,
    DemoModelDefault,
    DemoModelNone,
    DemoModelProxy,
    DemoMultipleCustomModel,
    DemoMultipleModel,
)


class DemoModelForm(ModelForm):
    class Meta:
        model = DemoModelProxy
        widgets = {"sender": TextInput}
        fields = "__all__"


class DemoModelProxyAdmin(admin.ModelAdmin):
    form = DemoModelForm


class DemoAllModelAdmin(admin.ModelAdmin):
    list_display = ("pk", "choice", "multiple", "custom", "custom_multiple")
    list_filter = ("choice", "custom")


class MyChangeList(ChangeList):
    pass


class DemoModelNoneAdmin(admin.ModelAdmin):
    list_display = ("pk", "sender", "strategy")

    def get_changelist(self, request, **kwargs):
        return MyChangeList

    def strategy(self, obj):
        if obj.sender:
            return fqn(obj.sender)


for s in (admin.site,):
    s.register(DemoModelProxy, DemoModelProxyAdmin)
    s.register(DemoAllModel, DemoAllModelAdmin)
    s.register(DemoMultipleModel)
    s.register(DemoModel)
    s.register(DemoCustomModel)
    s.register(DemoMultipleCustomModel)
    s.register(DemoModelCallableDefault)
    s.register(DemoModelDefault)
    s.register(DemoModelNone, DemoModelNoneAdmin)
