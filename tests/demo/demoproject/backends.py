from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission


class AnyUserBackend(ModelBackend):
    supports_object_permissions = False
    supports_anonymous_user = True

    def get_all_permissions(self, user_obj, obj=None):
        # if settings.DEBUG:
        return Permission.objects.all().values_list('content_type__app_label',
                                                    'codename').order_by()
        # return super().get_all_permissions(user_obj, obj)

    def get_group_permissions(self, user_obj, obj=None):
        # if settings.DEBUG:
        return Permission.objects.all().values_list('content_type__app_label',
                                                    'codename').order_by()
        # return super().get_group_permissions(user_obj,
        # obj)

    def has_perm(self, user_obj, perm, obj=None):
        # if settings.DEBUG:
        return True
        # return super().has_perm(user_obj, perm, obj)

    def has_module_perms(self, user_obj, app_label):
        # if settings.DEBUG:
        return True
        # return super().has_module_perms(user_obj,
        # app_label)
