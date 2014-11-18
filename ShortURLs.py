#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import loads, dumps
from os.path import exists, isfile


class Base:

    chars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def to_ten (self, base, num):
        l = len (num)
        res = 0
        for i in range (l):
            res += self.chars.index(num[l-1-i]) * (base ** i)
        return str(res)

    def from_ten (self, base, num):
        num = int(num)
        res = ''
        while num > 0:
            res = self.chars[num % base] + res
            num = num / base
        return res

    def convert (self, start_base, end_base, num):
        return self.from_ten (end_base, self.to_ten (start_base, num))

Base = Base ()



class ShortURLs:

    '''
    This class tries to provide a URL shortener (and reverse).
    It's not fully working atm.
    '''

    def __init__(self, base_url, save_file):
        self.base_url = base_url
        self.save_file = save_file

    def get_list(self):
        if exists(self.save_file) and isfile(self.save_file):
            return loads( open(self.save_file, 'r').read() )['content']
        else:
            self.set_list([])
            return []

    def set_list(self, l):
        open(self.save_file, 'w+').write( dumps( {'content':l}, indent=4 ) )

    def string_to_int(self, string):
        return int(Base.to_ten(62, string))

    def int_to_string(self, i):
        return Base.from_ten(62, str(i))

    def url_to_short(self, url):
#        V.prnt ('[ShortURL] url_to_short: '+url, V.DEBUG)
        l = self.get_list()
        if url in l:
            i = l.index(url)
        else:
            i = len(l)
            l.append( url )
            self.set_list(l)
        return self.base_url+self.int_to_string(i)

    def short_to_url(self, short, with_base_url=True):
#        V.prnt ('[ShortURL] short_to_url: '+short, V.DEBUG)
        if with_base_url:
            i = self.string_to_int( short[len(self.base_url):] )
        else:
            i = self.string_to_int( short )
        url = self.get_list()[i]
        return url
