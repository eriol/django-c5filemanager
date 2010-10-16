# -*- coding: utf-8 -*-
from django.conf import settings

MEDIA_ROOT = getattr(settings, 'C5FILEMANAGER_MEDIA_ROOT', settings.MEDIA_ROOT)
MEDIA_URL = getattr(settings, 'C5FILEMANAGER_MEDIA_URL', settings.MEDIA_URL)

# c5filemanager media path relative to MEDIA_ROOT
C5FILEMANAGER_MEDIA = getattr(settings,
                              'C5FILEMANAGER_MEDIA',
                              'filemanager')

# c5filemanager upload path relative to MEDIA_ROOT
C5FILEMANAGER_DIR = getattr(settings, 'C5FILEMANAGER_DIR', 'upload')
