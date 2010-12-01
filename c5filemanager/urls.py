# -*- coding: utf-8 -*-
"""c5filemanager.urls module, custom URLs for django-c5filemanager.

THIS SOFTWARE IS UNDER BSD LICENSE.
Copyright (c) 2010 Daniele Tricoli <eriol@mornie.org>

Read LICENSE for more informations.
"""
from django.conf.urls.defaults import *

urlpatterns = patterns('c5filemanager.views',
    url(r'^dir_list/$', 'dir_list', name='c5filemanager-dir_list'),
    url(r'^$', 'filemanager', name='c5filemanager-view'),
)
