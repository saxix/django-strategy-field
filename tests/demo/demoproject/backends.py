from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class AnyUserBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user, __ = get_user_model().objects.update_or_create(
            username=username,
            defaults=dict(
                is_staff=True,
                is_active=True,
                is_superuser=True,
                email=f"{username}@demo.org",
            ),
        )
        return user
