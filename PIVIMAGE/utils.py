# coding: utf8
from __future__ import unicode_literals
from __future__ import absolute_import

import sys
'''
projet : PIVIMAGE

'''

def encode(txt):
    ''' Python 3 : do nothing
        Python 2 : encode
    '''
    if (sys.version_info > (3, 0)):
        return txt
    else:
        return txt.encode(sys.getfilesystemencoding())
