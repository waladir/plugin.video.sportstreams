# -*- coding: utf-8 -*-
import sys
import xbmc
from urllib.parse import urlencode

_url = sys.argv[0]

def get_url(**kwargs):
    return '{0}?{1}'.format(_url, urlencode(kwargs))
    