# -*- coding: utf-8 -*-
import os
import shutil
import time
import urllib

import Image

from django.core.servers.basehttp import FileWrapper
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

TIME_FORMAT = '%Y/%m/%d - %H:%M:%S'

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
        'Return': '',
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
            file_info['Path'] = file_info['Path'] + '/'
            file_info['Return'] = requested_path
            preview = PREVIEW_IMAGES['Directory']
        else:
            ext = os.path.splitext(real_path)[1].replace('.', '').lower()
            if not ext:
                ext = 'txt'
                preview = PREVIEW_IMAGES['Default']
            else:
                preview = PREVIEW_IMAGES['Image'] % ext
                # Check if the icon for the specified extension exists.
                preview_file_path = os.path.join(settings.MEDIA_ROOT,
                                        settings.C5FILEMANAGER_MEDIA,
                                        preview)
                if not os.path.exists(preview_file_path):
                    preview = PREVIEW_IMAGES['Default']
        file_info['File Type'] = ext
        file_info['Properties']['Date Created'] = time.strftime(TIME_FORMAT,
            time.localtime(os.path.getctime(real_path)))
        file_info['Properties']['Date Modified'] = time.strftime(TIME_FORMAT,
            time.localtime(os.path.getmtime(real_path)))
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

def getinfo(request):
    requested_path = request.GET.get('path', None)
    real_path = get_path(requested_path)

    getsize = request.GET.get('getsize', None)

    file_info = create_file_info_for(requested_path, real_path)

    return HttpResponse(simplejson.dumps(file_info),
                        mimetype='application/json')

def getfolder(request):
    requested_path = request.GET.get('path', None)
    real_path = get_path(requested_path)
    getsize = request.GET.get('getsize', None)

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


def rename(request):
    old_path = request.GET.get('old', None)
    new_path = request.GET.get('new', None)
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

def delete(request):
    requested_path = request.GET.get('path', None)
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

def add(request):
    requested_path = request.POST.get('currentpath', None)
    new_file = request.FILES['newfile']
    response = {}
    try:
        handle_uploaded_file(requested_path, new_file)
    except IOError, e:
        response = error(e.strerror)
    else:
        response['Path'] = requested_path
        response['Name'] = new_file.name
        response['Code'] = 0
        response['Error'] = 'No Error'
    html = '<textarea>' + simplejson.dumps(response) + '</textarea>'
    return HttpResponse(html)

def addfolder(request):
    requested_path = request.GET.get('path', None)
    dir_name = request.GET.get('name', None)
    response = {}

    real_path = get_path(requested_path)

    os.mkdir(os.path.join(real_path, dir_name))
    response['Code'] = 0
    response['Error'] = 'No Error'
    response['Parent'] = requested_path
    response['Name'] = dir_name

    return HttpResponse(simplejson.dumps(response),
                        mimetype='application/json')

def download(request):
    requested_path = request.GET.get('path', None)
    real_path = get_path(requested_path)
    filename = os.path.basename(real_path)
    response = HttpResponse(FileWrapper(file(real_path)),
                            content_type='application/x-download')
    response['Content-Length'] = os.path.getsize(real_path)
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

handlers = {
    'getinfo': getinfo,
    'getfolder': getfolder,
    'rename': rename,
    'delete': delete,
    'addfolder': addfolder,
    'download': download
}

def handle_uploaded_file(path, f):
    real_path = get_path(path)
    new_file = os.path.join(real_path, f.name)
    try:
        destination = open(new_file, 'wb+')
        for chunk in f.chunks():
            destination.write(chunk)
        destination.close()
    except IOError:
        raise

@csrf_exempt
def filemanager(request):
    if request.method == 'GET':
        mode = request.GET.get('mode', None)
        if mode is not None:
            callback = handlers[mode]
    elif request.method == 'POST':
        return add(request)

    return callback(request)

@csrf_exempt
def dir_list(request):
    requested_path = urllib.unquote(request.POST.get('dir', None))
    real_path = get_path(requested_path)
    response = ['<ul class="jqueryFileTree" style="display: none;">']
    dir_item = ('<li class="directory collapsed">'
                '<a href="#" rel="%s/">%s</a></li>')
    file_item = '<li class="file ext_%s"><a href="#" rel="%s">%s</a></li>'
    if os.path.isdir(real_path):
        for filename in sorted(os.listdir(real_path), key=unicode.lower):
            ext = os.path.splitext(filename)[1].replace('.', '').lower()
            full_requested_path = os.path.join(requested_path, filename)
            full_real_path = os.path.join(real_path, filename)
            if os.path.isdir(full_real_path):
                response.append(dir_item % (full_requested_path, filename))
            else:
                response.append(file_item % (ext,
                                             full_requested_path,
                                             filename))
    response.append('</ul>')
    return HttpResponse(''.join(response))
