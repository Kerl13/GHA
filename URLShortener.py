#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib import quote_plus
from urllib2 import urlopen


def short(url):
    short_url = urlopen('http://is.gd/create.php?format=simple&url='
                        + quote_plus(url))
    return short_url.readline()
