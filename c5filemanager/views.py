# -*- coding: utf-8 -*-
import Image
import os

from c5filemanager import settings


IMAGES_EXT = ('jpg', 'jpeg', 'gif', 'png')


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

def create_file_info_for(path):
    """Fills proper file information needed by Code Five Filemanager."""

    file_info = {
        'Path': '',
        'Filename': '',
        'File Type': '',
        'Preview': '',
        'Properties': {
            'Date Created': '',
            'Date Modified': '',
            'Height': '',
            'Width': '',
            'Size': ''
        },
        'Error': '',
        'Code': 0
    }

    if os.path.exists(path):
        file_info['Path'] = path
        file_info['Filename'] = os.path.basename(path)
        # Handle file extension: if ``path'' is a directory must be set to
        # 'dir', if absent or unknown to 'txt'.
        if os.path.isdir(path):
            ext = 'dir'
        else:
            ext = os.path.splitext(path)[1].replace('.', '').lower()
            if not ext:
                ext = 'txt'
        file_info['File Type'] = ext
        file_info['Preview'] = path
        file_info['Properties']['Date Created'] = os.path.getctime(path)
        file_info['Properties']['Date Modified'] = os.path.getmtime(path)
        if ext in IMAGES_EXT:
            img = Image.open(path)
            width, height = img.size
            file_info['Properties']['Height'] = height
            file_info['Properties']['Width'] = width
        file_info['Properties']['Size'] = os.path.getsize(path)
    else:
        return error('No such file or directory')

    return file_info

def error(message, code=-1):
    """Returns an error."""
    err = {'Error': message, 'Code': code}
    return err


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
