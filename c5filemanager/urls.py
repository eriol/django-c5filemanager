# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

from c5filemanager.views import Filemanager

urlpatterns = patterns('',
    url(r'^$', Filemanager(), name='c5filemanager-view'),
)
