from django.conf import settings

CLASSLOADER = getattr(
    settings, "STRATEGY_CLASSLOADER", "strategy_field.utils.default_classloader"
)
