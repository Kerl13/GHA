#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Prnt import *
from json import loads, dumps


class ShortURLs:

    '''
    This class tries to provide a URL shortener (and reverse).
    It's not fully working atm.
    '''

    def __init__(self, base_url, save_file):
        self.base_url = base_url
        self.save_file = save_file

    def get_list(self):
        return load( open(self.save_file, 'r').read() )['content']

    def set_list(self, l):
        open(self.save_file, 'w+').write( dumps( {'content':l}, indent=4 ) )

    def string_to_int(self, string):
        return int(string) # to be changed

    def int_to_string(self, i):
        return str(i) # to be changed

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
