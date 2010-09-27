# -*- coding: utf-8 -*-
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


