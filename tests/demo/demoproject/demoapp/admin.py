from django.contrib import admin
from django.forms import ModelForm, TextInput

from .models import (DemoAllModel, DemoCustomModel, DemoModel,
                     DemoModelCallableDefault, DemoModelDefault, DemoModelProxy,
                     DemoMultipleCustomModel, DemoMultipleModel,)


class DemoModelForm(ModelForm):
    class Meta:
        model = DemoModelProxy
        widgets = {'sender': TextInput}
        fields = '__all__'


class DemoModelProxyAdmin(admin.ModelAdmin):
    form = DemoModelForm


for s in (admin.site,):
    s.register(DemoModelProxy, DemoModelProxyAdmin)
    s.register(DemoAllModel)
    s.register(DemoMultipleModel)
    s.register(DemoModel)
    s.register(DemoCustomModel)
    s.register(DemoMultipleCustomModel)
    s.register(DemoModelCallableDefault)
    s.register(DemoModelDefault)
