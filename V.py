#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Verbose constants
DEBUG = 10
WARNING = 20
ERROR = 30

# Verbose level wanted
_LEVEL = ERROR

# 
def get_level (as_string = False):
    if as_string:
        if _LEVEL == DEBUG:
            return 'DEBUG'
        elif _LEVEL == WARNING:
            return 'WARNING'
        elif _LEVEL == ERROR:
            return 'ERROR'
        else:
            return None
    else:
        return _LEVEL

# 
def set_level (level):
    if level == 'DEBUG':
        _LEVEL = DEBUG
    elif level == 'WARNING':
        _LEVEL = WARNING
    elif level == 'ERROR':
        _LEVEL = ERROR
    else:
        _LEVEL = int(level)

#
def _test (level):
    return level >= get_level()

#
def _string (string, level=None):
    if _test(level):
        return string
    else:
        return ''

#
def prnt (string, level=None):
    if _test(level):
        print '%s %s' % (get_level(True), string)

