# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import django

DJANGO2 = django.VERSION[0] == 2
DJANGO1 = django.VERSION[0] == 1

# MONITOR THIS: DJANGO version compatibility code:
if DJANGO2:
    from django.urls import reverse  # noqa
else:
    from django.core.urlresolvers import reverse  # noqa
