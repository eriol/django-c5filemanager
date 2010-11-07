# -*- coding: utf-8 -*-
import os
import time

from django.test import TestCase
from django.utils import simplejson
from mock import Mock, patch

from c5filemanager import settings
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

class FilemanagerTestCase(TestCase):
    urls = 'c5filemanager.tests.urls'

    def setUp(self):
        self.mockify()


class ViewsTest(FilemanagerTestCase):

    def mockify(self, mock_hook=Mock()):
        pass

    def test_getfolder(self):
        """Test getfolder."""
        # ?path=/&mode=getfolder&showThumbs=true
        response = self.client.get('', {'path': '/',
                                        'mode': 'getfolder',
                                        'showThumbs': 'true'})
        self.failUnlessEqual(response.status_code, 200)

    @patch('shutil.move')
    @patch('os.path.exists')
    def test_rename(self, exists_mock, shmove_mock):
        """Test rename of a file or directory."""
        exists_mock.return_value = True
        #?mode=rename&old=/oldfile.txt&new=newfile.txt
        response = self.client.get('', {'mode': 'rename',
                                        'old': 'oldfile.txt',
                                        'new': 'newfile.txt'})

        self.failUnlessEqual(response.status_code, 200)

        expected_content = {
            'Code': 0,
            'New Path': os.path.join(settings.MEDIA_ROOT,
                                     settings.C5FILEMANAGER_DIR,
                                     'newfile.txt'),
            'Old Path':  os.path.join(settings.MEDIA_ROOT,
                                      settings.C5FILEMANAGER_DIR,
                                     'oldfile.txt'),
            'New Name': 'newfile.txt',
            'Error': 'No Error',
            'Old Name': 'oldfile.txt'}

        self.failUnlessEqual(response.content,
                             simplejson.dumps(expected_content))

        # If the file does't exists an error message is returned.
        exists_mock.return_value = False
        response = self.client.get('', {'mode': 'rename',
                                        'old': 'notexists.txt',
                                        'new': 'newfile.txt'})

        expected_content = {'Code': -1, 'Error': 'No such file or directory'}

        self.failUnlessEqual(response.content,
                             simplejson.dumps(expected_content))


class DeleteTest(FilemanagerTestCase):
    """Tests for c5filemanager.views.delete."""

    def setUp(self):
        self.exists_mock = Mock()
        self.isdir_mock = Mock()
        self.remove_mock = Mock()
        self.rmdir_mock = Mock()

    def mockify(self, exists_mock=Mock(), isdir_mock=Mock(),
                remove_mock=Mock(), rmdir_mock=Mock(), path=None):
        @patch('os.rmdir', rmdir_mock)
        @patch('os.remove', remove_mock)
        @patch('os.path.isdir', isdir_mock)
        @patch('os.path.exists', exists_mock)
        def patching():
            query = {'mode': 'delete', 'path': path}
            self.response = self.client.get('', query)
        patching()

    def test_delete_file_success(self):
        """Test succesful deletion of a file."""
        self.exists_mock.return_value = True
        self.isdir_mock.return_value = False
        self.mockify(exists_mock=self.exists_mock,
                     isdir_mock=self.isdir_mock,
                     remove_mock=self.remove_mock,
                     path='/file-to-be-deleted.txt')

        self.failUnless(self.exists_mock.called)
        self.failUnless(self.remove_mock.called)

        expected_content = {'Code': 0,
                            'Error': 'No Error',
                            'Path': '/file-to-be-deleted.txt'}
        self.failUnlessEqual(self.response.content,
                             simplejson.dumps(expected_content))

    def test_delete_directory_success(self):
        """Test succesful deletion of a directory."""
        self.exists_mock.return_value = True
        self.isdir_mock.return_value = True
        self.mockify(exists_mock=self.exists_mock,
                     isdir_mock=self.isdir_mock,
                     rmdir_mock=self.rmdir_mock,
                     path='/directory-to-be-deleted/')

        self.failUnless(self.exists_mock.called)
        self.failUnless(self.rmdir_mock.called)

        expected_content = {'Code': 0,
                            'Error': 'No Error',
                            'Path': '/directory-to-be-deleted/'}
        self.failUnlessEqual(self.response.content,
                             simplejson.dumps(expected_content))

    def test_delete_file_or_directory_not_existent(self):
        """Test deletion of a not existent file or directory."""
        self.exists_mock.return_value = False
        self.mockify(exists_mock=self.exists_mock,
                     path='/nofile-or-directory-to-be-deleted')

        expected_content = {'Code': -1, 'Error': 'No such file or directory'}
        self.failUnlessEqual(self.response.content,
                             simplejson.dumps(expected_content))


class UploadFileTest(FilemanagerTestCase):
    """Tests for c5filemanager.views.add."""

    def mockify(self, mock_hook=Mock()):
        @patch('c5filemanager.views.handle_uploaded_file', mock_hook)
        def patching():
            self.handle_uploaded_file_mock = mock_hook
            self.file_mock = Mock()
            # Return some meaningfull data :)
            self.file_mock.read = lambda: '42'
            self.file_mock.name = 'newfile.txt'
            path = '/' + self.file_mock.name
            self.response = self.client.post('', {'currentpath': path,
                                                  'newfile': self.file_mock})
        patching()

    def test_add_success(self):
        """Test succesful upload of a file."""
        self.failUnless(self.handle_uploaded_file_mock.called)

        expected_content = {'Code': 0,
                            'Error': 'No Error',
                            'Name': self.file_mock.name,
                            'Path': '/' + self.file_mock.name }
        self.failUnlessEqual(self.response.content,
                             ('<textarea>' + simplejson.dumps(expected_content)
                              + '</textarea>'))

    def test_add_fail(self):
        """Test unsuccesful upload of a file."""
        handle_uploaded_file_mock = Mock()
        handle_uploaded_file_mock.side_effect = IOError(2, 'No such file!')
        self.mockify(handle_uploaded_file_mock)

        expected_content = {'Code': -1, 'Error': 'No such file!'}
        self.failUnlessEqual(self.response.content,
                             ('<textarea>' + simplejson.dumps(expected_content)
                              + '</textarea>'))


class AddFolderTest(FilemanagerTestCase):
    """Tests for c5filemanager.views.addfolder."""

    def mockify(self, mock_hook=Mock()):
        @patch('os.mkdir', mock_hook)
        def patching():
            self.mkdir_mock = mock_hook
            #?mode=addfolder&path=/&name=new_directory
            self.response = self.client.get('', {'mode': 'addfolder',
                                                 'path': '/',
                                                 'name': 'new_directory'})
        patching()

    def test_addfolder_success(self):
        """Test succesful creation of a new directory."""
        self.failUnless(self.mkdir_mock.called)

        expected_content = {'Code': 0,
                            'Error': 'No Error',
                            'Name': 'new_directory',
                            'Parent': '/'}
        self.failUnlessEqual(self.response.content,
                             simplejson.dumps(expected_content))

    def test_addfolder_fail(self):
        """Test unsuccessful creation of a new directory."""
        # Raise an OSError exception during directory creation.
        mkdir_mock = Mock()
        mkdir_mock.side_effect = OSError(2, 'File exists')
        self.mockify(mkdir_mock)

        expected_content = {'Code': -1, 'Error': 'File exists'}
        self.failUnlessEqual(self.response.content,
                             simplejson.dumps(expected_content))
