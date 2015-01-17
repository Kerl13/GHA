#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen

def short (url):
    short_url = urlopen ('http://niols.net/u/?api_url=' + url)
    return short_url.readline ()

