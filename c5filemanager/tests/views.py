# -*- coding: utf-8 -*-

import time

from django.test import TestCase
from mock import Mock, patch

from c5filemanager.views import create_file_info_for

FILE_CTIME = time.mktime(
    time.strptime("8 Feb 82 10:10:10", "%d %b %y %H:%M:%S"))
FILE_MTIME = time.mktime(
    time.strptime("8 Feb 00 10:10:10", "%d %b %y %H:%M:%S"))
FILE_SIZE = 1024
IMG_HEIGHT = 768
IMG_WIDTH = 1024

# An image mock to test size
ImageMock = Mock()
ImageMock.size = IMG_WIDTH, IMG_HEIGHT

@patch('Image.open')
@patch('os.path.getsize')
@patch('os.path.getmtime')
@patch('os.path.getctime')
@patch('os.path.exists')
def create_file_info_for_mock(exists_mock,
                              getctime_mock,
                              getmtime_mock,
                              getsize_mock,
                              image_open_mock,
                              requested_path,
                              real_path):
    """Mock version of the real create_file_info_for."""
    exists_mock.return_value = True
    getctime_mock.return_value = FILE_CTIME
    getmtime_mock.return_value = FILE_MTIME
    getsize_mock.return_value = FILE_SIZE
    image_open_mock.return_value = ImageMock
    info = create_file_info_for(requested_path, real_path)

    return info

class CreateFileInfoTest(TestCase):

    def test_create_file_info_for_txt(self):
        """Test information creation for a txt file."""
        expected_result = {
            'Code': 0,
            'Error': '',
            'File Type': 'txt',
            'Filename': 'file.txt',
            'Path': '/path/to/file.txt',
            'Preview': 'images/fileicons/txt.png',
            'Properties': {'Date Created': '1982/02/08 - 10:10:10',
                           'Date Modified': '2000/02/08 - 10:10:10',
                           'Height': '',
                           'Size': 1024,
                           'Width': ''
            }
        }

        info = create_file_info_for_mock(requested_path='/path/to/file.txt',
                                         real_path='/real/path/to/file.txt')

        self.failUnlessEqual(info, expected_result)

    def test_create_file_info_for_png(self):
        """Test information creation for a png file."""
        expected_result = {
            'Code': 0,
            'Error': '',
            'File Type': 'png',
            'Filename': 'file.png',
            'Path': '/path/to/file.png',
            'Preview': '/media/upload/path/to/file.png',
            'Properties': {'Date Created': '1982/02/08 - 10:10:10',
                           'Date Modified': '2000/02/08 - 10:10:10',
                           'Height': 768,
                           'Size': 1024,
                           'Width': 1024
            }
        }

        info = create_file_info_for_mock(requested_path='/path/to/file.png',
                                         real_path='/real/path/to/file.png')

        self.failUnlessEqual(info, expected_result)

    @patch('os.path.isdir')
    def test_create_file_info_for_directory(self, isdir_mock):
        """Test information creation for a directory."""
        isdir_mock.return_value = True
        expected_result = {
            'Code': 0,
            'Error': '',
            'File Type': 'Directory',
            'Filename': 'directory',
            'Path': '/path/to/directory/',
            'Preview': 'images/fileicons/_Open.png',
            'Properties': {'Date Created': '1982/02/08 - 10:10:10',
                           'Date Modified': '2000/02/08 - 10:10:10',
                           'Height': '',
                           'Size': 1024,
                           'Width': ''
            }
        }

        info = create_file_info_for_mock(requested_path='/path/to/directory',
                                         real_path='/real/path/to/directory')

        self.failUnlessEqual(info, expected_result)