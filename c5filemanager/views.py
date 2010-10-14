# -*- coding: utf-8 -*-
import os
import shutil

import Image

from django.http import HttpResponse
from django.utils import simplejson
# For OrderedDict is needed simplejson >= 2.1.0
from django.utils.simplejson import OrderedDict
from django.views.decorators.csrf import csrf_exempt

from c5filemanager import settings


IMAGES_EXT = ('jpg', 'jpeg', 'gif', 'png')
PREVIEW_IMAGES_PATH = 'images/fileicons/'
PREVIEW_IMAGES = {
    'Directory': PREVIEW_IMAGES_PATH + '_Open.png',
    'Default': PREVIEW_IMAGES_PATH + 'default.png',
    'Image': PREVIEW_IMAGES_PATH + '%s.png'
}

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
            preview = PREVIEW_IMAGES['Directory']
        else:
            ext = os.path.splitext(real_path)[1].replace('.', '').lower()
            if not ext:
                preview = PREVIEW_IMAGES['Default']
                ext = 'txt'
            else:
                preview = PREVIEW_IMAGES['Image'] % ext
        file_info['File Type'] = ext
        file_info['Properties']['Date Created'] = os.path.getctime(real_path)
        file_info['Properties']['Date Modified'] = os.path.getmtime(real_path)
        if ext in IMAGES_EXT:
            img = Image.open(real_path)
            width, height = img.size
            file_info['Properties']['Height'] = height
            file_info['Properties']['Width'] = width
            preview = ''.join((settings.MEDIA_URL,
                               settings.C5FILEMANAGER_DIR,
                               requested_path))
        file_info['Preview'] = preview
        file_info['Properties']['Size'] = os.path.getsize(real_path)
    else:
        return error('No such file or directory')

    return file_info

def error(message, code=-1):
    """Returns an error."""
    err = {'Error': message, 'Code': code}
    return err



class Filemanager:

    @csrf_exempt
    def __call__(self, request):
        self.request = request

        if self.request.method == 'GET':
            mode = self.request.GET.get('mode', None)
            if mode is not None:
                callback = getattr(self, mode)
        elif self.request.method == 'POST':
            return self.add()

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
        files_info = OrderedDict()
        if os.path.isdir(real_path):
            for filename in sorted(os.listdir(real_path), key=unicode.lower):
                requested_file_path = os.path.join(requested_path, filename)
                real_file_path = os.path.join(real_path, filename)
                files_info[filename] = create_file_info_for(
                                           requested_file_path,
                                           real_file_path)
        else:
            files_info = error('No such directory')

        return HttpResponse(simplejson.dumps(files_info),
                            mimetype='application/json')


    def rename(self):
        old_path = self.request.GET.get('old', None)
        new_path = self.request.GET.get('new', None)
        response = {}

        old_file = get_path(old_path)

        if os.path.exists(old_file):
            old_name = os.path.basename(old_file)
            old_path_dir = os.path.dirname(old_file)
            # Using rename to move a file is not allowed so any directory
            # will be stripped.
            new_name = os.path.basename(new_path)
            new_file = os.path.join(old_path_dir, new_name)
            shutil.move(old_file, os.path.join(old_path_dir, new_name))
            response['Code'] = 0
            response['Error'] = 'No Error'
            response['Old Path'] = old_file
            response['Old Name'] = old_name
            response['New Path'] = new_file
            response['New Name'] = new_name
        else:
            response = error('No such file or directory')

        return HttpResponse(simplejson.dumps(response),
                            mimetype='application/json')

    def delete(self):
        requested_path = self.request.GET.get('path', None)
        file_to_be_deleted = get_path(requested_path)
        response = {}

        if os.path.exists(file_to_be_deleted):
            if os.path.isdir(file_to_be_deleted):
                os.rmdir(file_to_be_deleted)
            else:
                os.remove(file_to_be_deleted)
            response['Code'] = 0
            response['Error'] = 'No Error'
            response['Path'] = requested_path
        else:
            response = error('No such file or directory')

        return HttpResponse(simplejson.dumps(response),
                            mimetype='application/json')

    def add(self):
        pass

    def addfolder(self):
        requested_path = self.request.GET.get('path', None)
        dir_name = self.request.GET.get('name', None)
        response = {}

        real_path = get_path(requested_path)

        os.mkdir(os.path.join(real_path, dir_name))
        response['Code'] = 0
        response['Error'] = 'No Error'
        response['Parent'] = requested_path
        response['Name'] = dir_name

        return HttpResponse(simplejson.dumps(response),
                            mimetype='application/json')

    def download(self):
        pass
