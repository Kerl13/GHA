#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Prnt import *
from json import loads, dumps


class ShortURLs:

    '''
    This class tries to provide a URL shortener (and reverse).
    It's not fully working atm.
    '''

    def __init__(self, base_url, save_file = None):
        self.base_url = base_url
        self.save_file = save_file
        if save_file:
            try:
                self.url_list = loads( open(save_file, 'r').read() )['content']
            except:
                self.url_list = []
        else:
            self.url_list = []
        
    def _save(self):
        if self.save_file:
            open(self.save_file, 'w+').write( dumps( {'content':self.url_list}, indent=4 ) )

    def string_to_int(self, string):
        return int(string) # to be changed

    def int_to_string(self, i):
        return str(i) # to be changed

    def url_to_short(self, url):
        print 'url_to_short before', self.url_list
        if url in self.url_list:
            i = self.url_list.index(url)
        else:
            i = len(self.url_list)
            self.url_list.append( url )
            self._save()
        print 'url_to_short modif', url, i
        print 'url_to_short after', self.url_list        
        return self.base_url+self.int_to_string(i)

    def short_to_url(self, short, with_base_url=True):
        try:
            print 'short_to_url before', self.url_list
            if with_base_url:
                i = self.string_to_int( short[len(self.base_url):] )
            else:
                i = self.string_to_int( short )
            url = self.url_list[i]
            print 'short_to_url modif', i, url
            print 'short_to_url after', self.url_list
            return url
        except:
            return ''

