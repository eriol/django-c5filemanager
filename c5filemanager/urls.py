# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('c5filemanager.views',
    url(r'^$', 'filemanager', name='c5filemanager-view'),
)
