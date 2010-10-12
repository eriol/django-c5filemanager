# -*- coding: utf-8 -*-
import Image
import os

from django.http import HttpResponse
from django.utils import simplejson

from c5filemanager import settings


IMAGES_EXT = ('jpg', 'jpeg', 'gif', 'png')


def get_path(requested_path):
    """
    Returns the ``path'' relative to settings.MEDIA_ROOT.
    """
    # Clean absolute path that will brake os.path.join!
    if os.path.isabs(requested_path):
        requested_path = requested_path[1:]

    return os.path.join(settings.MEDIA_ROOT,
                        settings.C5FILEMANAGER_DIR,
                        requested_path)

def create_file_info_for(requested_path, real_path):
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

    if os.path.exists(real_path):
        file_info['Path'] = requested_path
        file_info['Filename'] = os.path.basename(real_path)
        # Handle file extension: if ``path'' is a directory must be set to
        # 'dir', if absent or unknown to 'txt'.
        if os.path.isdir(real_path):
            ext = 'Directory'
            file_info['Return'] = requested_path
            file_info['Path'] = file_info['Path'] + '/'

        else:
            ext = os.path.splitext(real_path)[1].replace('.', '').lower()
            if not ext:
                ext = 'txt'
        file_info['File Type'] = ext
        file_info['Preview'] = ''.join((settings.MEDIA_URL,
                                        settings.C5FILEMANAGER_DIR,
                                        requested_path))
        file_info['Properties']['Date Created'] = os.path.getctime(real_path)
        file_info['Properties']['Date Modified'] = os.path.getmtime(real_path)
        if ext in IMAGES_EXT:
            img = Image.open(real_path)
            width, height = img.size
            file_info['Properties']['Height'] = height
            file_info['Properties']['Width'] = width
        file_info['Properties']['Size'] = os.path.getsize(real_path)
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
        requested_path = self.request.GET.get('path', None)
        real_path = get_path(requested_path)

        getsize = self.request.GET.get('getsize', None)

        file_info = create_file_info_for(requested_path, real_path)

        return HttpResponse(simplejson.dumps(file_info),
                            mimetype='application/json')

    def getfolder(self):
        requested_path = self.request.GET.get('path', None)
        real_path = get_path(requested_path)
        getsize = self.request.GET.get('getsize', None)

        # A list to collect info for all the files in the directory
        # pointed by ``path''
        files_info = {}
        if os.path.isdir(real_path):
            for filename in os.listdir(real_path):
                requested_file_path = os.path.join(requested_path, filename)
                real_file_path = os.path.join(real_path, filename)
                files_info['/' + filename] = create_file_info_for(
                                                        requested_file_path,
                                                        real_file_path)
        else:
            files_info = error('No such directory')

        return HttpResponse(simplejson.dumps(files_info),
                            mimetype='application/json')


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
