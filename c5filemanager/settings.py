# -*- coding: utf-8 -*-
import posixpath

from django.conf import settings

# Main MEDIA settings
MEDIA_ROOT = getattr(settings, 'C5FILEMANAGER_MEDIA_ROOT', settings.MEDIA_ROOT)
MEDIA_URL = getattr(settings, 'C5FILEMANAGER_MEDIA_URL', settings.MEDIA_URL)

# c5filemanager media path. Must be relative to MEDIA_ROOT.
C5FILEMANAGER_MEDIA = getattr(settings, 'C5FILEMANAGER_MEDIA', 'filemanager')

# c5filemanager upload directory. Must be relative to MEDIA_ROOT.
UPLOAD_DIRECTORY = getattr(settings,
                           'C5FILEMANAGER_UPLOAD_DIRECTORY',
                           'upload')

# c5filemanager upload directory relative to MEDIA_URL.
UPLOAD_DIRECTORY_URL = posixpath.join(settings.MEDIA_URL,
                                      settings.UPLOAD_DIRECTORY)
