from django.contrib import admin
from django.forms import ModelForm, TextInput

from strategy_field.utils import fqn
from .models import (
    DemoAllModel,
    DemoCustomModel,
    DemoModel,
    DemoModelCallableDefault,
    DemoModelDefault,
    DemoModelProxy,
    DemoMultipleCustomModel,
    DemoMultipleModel,
    DemoModelNone,
)


class DemoModelForm(ModelForm):
    class Meta:
        model = DemoModelProxy
        widgets = {"sender": TextInput}
        fields = "__all__"


class DemoModelProxyAdmin(admin.ModelAdmin):
    form = DemoModelForm


class DemoModelNoneAdmin(admin.ModelAdmin):
    list_display = ("sender", "strategy")

    def strategy(self, obj):
        if obj.sender:
            return fqn(obj.sender)


for s in (admin.site,):
    s.register(DemoModelProxy, DemoModelProxyAdmin)
    s.register(DemoAllModel)
    s.register(DemoMultipleModel)
    s.register(DemoModel)
    s.register(DemoCustomModel)
    s.register(DemoMultipleCustomModel)
    s.register(DemoModelCallableDefault)
    s.register(DemoModelDefault)
    s.register(DemoModelNone, DemoModelNoneAdmin)
