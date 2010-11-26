# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from c5filemanager import VERSION

setup(
    name='django-c5filemanager',
    version='.'.join(str(v) for v in VERSION),
    description='Django connector for Core Five Filemanager.',
    author='Daniele Tricoli',
    author_email='eriol@mornie.org',
    packages=find_packages(),
    package_data = {
        'c5filemanager': [
            'locale/*/LC_MESSAGES/*',
        ],
    },
    install_requires = [
        'simplejson>=2.1.0',
    ],
)
