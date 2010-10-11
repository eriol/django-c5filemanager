# -*- coding: utf-8 -*-
from django.conf import settings

MEDIA_ROOT = getattr(settings, 'C5FILEMANAGER_MEDIA_ROOT', settings.MEDIA_ROOT)
MEDIA_URL = getattr(settings, 'C5FILEMANAGER_MEDIA_URL', settings.MEDIA_URL)

# c5filemanager path relative to media root
C5FILEMANAGER_DIR = getattr(settings, 'C5FILEMANAGER_DIR', 'upload')
