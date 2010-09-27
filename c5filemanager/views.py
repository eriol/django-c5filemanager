# -*- coding: utf-8 -*-
import os

from c5filemanager import settings

def get_path(path):
    """
    Returns the ``path'' relative to settings.MEDIA_ROOT.
    """
    # Clean absolute path that will brake os.path.join!
    if os.path.isabs(path):
        path = path[1:]

    return os.path.join(settings.MEDIA_ROOT,
                        settings.C5FILEMANAGER_DIR,
                        path)


class Filemanager:

    def __call__(self, request):
        self.request = request

        mode = self.request.GET.get('mode', None)
        callback = getattr(self, mode)

        return callback()

    def getinfo(self):
        pass

    def getfolder(self):
        pass

    def rename(self):
        pass

    def delete(self):
        pass

    def add(self):
        pass

    def addfolder(self):
        pass

    def download(self):
        pass


