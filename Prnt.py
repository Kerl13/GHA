#!/usr/bin/env python
# -*- coding: utf-8 -*-


class Prnt:

    '''
    The Prnt class is a little class made to help printing leveled messages.
    You define some levels (by default, DEBUG, WARNING and ERROR), and give
    the level you currently have).
    Then you can print (using Prnt.prnt) messages with a given level, and it'll
    appear or not depending on the level previously given.
    '''

    DEBUG = 10
    WARNING = 20
    ERROR = 30

    level = ERROR


    def __init__(self, level = ERROR):
        self.level = level


    def get_level (self, as_string = False):
        if as_string:
            for l in self.get_levels().keys():
                if self.level == getattr(self, l):
                    return l
        else:
            return self.level


    def set_level (level):
        for l in self.get_levels().keys():
            if level == l:
                self.level = getattr(self, l)
                return None
        self.level = int(level)
        return None


    def get_levels (self):
        result = {}
        for attr in dir(self):
            if attr == attr.upper():
                result[attr] = getattr(self, attr)
        return result


    def add_level (self, name, level):
        setattr(self, name.upper(), level)

        
    def del_level (self, name):
        delattr(self, name.upper())


    def level_of_string (self, string):
        return getattr(self, string.upper())


    def string_of_level (self, level):
        for string in self.get_levels().keys():
            if getattr(self, string) == level:
                return string


    def test (self, level):
        return level >= self.level


    def prnt (self, string, level = None):
        if self.test(level):
            print '%s %s' % (self.string_of_level(level), string)



V = Prnt ()
