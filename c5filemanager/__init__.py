# -*- coding: utf-8 -*-
"""c5filemanager package, Django connector for Core Five Filemanager.

THIS SOFTWARE IS UNDER BSD LICENSE.
Copyright (c) 2010 Daniele Tricoli <eriol@mornie.org>

Read LICENSE for more informations.
"""
VERSION = (0, 1, 0)

def get_version():
    """Returns project version in a human readable form."""
    return '.'.join(str(v) for v in VERSION)
