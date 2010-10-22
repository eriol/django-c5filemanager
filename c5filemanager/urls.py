# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('c5filemanager.views',
    url(r'^dir_list/$', 'dir_list', name='c5filemanager-dir_list'),
    url(r'^$', 'filemanager', name='c5filemanager-view'),
)
