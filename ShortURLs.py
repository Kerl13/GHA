#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Prnt import *
from json import loads, dumps
from base64 import urlsafe_b64encode, urlsafe_b64decode

class ShortURLs:

    '''
    This class tries to provide a URL shortener (and reverse).
    It's not fully working atm.
    '''

    def __init__(self, base_url, save_file):
        self.base_url = base_url
        self.save_file = save_file

    def get_list(self):
        return loads( open(self.save_file, 'r').read() )['content']

    def set_list(self, l):
        open(self.save_file, 'w+').write( dumps( {'content':l}, indent=4 ) )

    def string_to_int(self, string):
        return int(urlsafe_b64decode(string))

    def int_to_string(self, i):
        return urlsafe_b64encode(str(i))

    def url_to_short(self, url):
        l = self.get_list()
        if url in l:
            i = l.index(url)
        else:
            i = len(l)
            l.append( url )
            self.set_list(l)
        return self.base_url+self.int_to_string(i)

    def short_to_url(self, short, with_base_url=True):
        if with_base_url:
            i = self.string_to_int( short[len(self.base_url):] )
        else:
            i = self.string_to_int( short )
        url = self.get_list()[i]
        return url
