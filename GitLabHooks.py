#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#                                                                              #
#                                GitLabHooks.py                                #
#                                   by Niols                                   #
#                                                                              #
#  BEERWARE License:                                                           #
#  <niols@niols.net> wrote this file. As long as you retain this notice you    #
#  can do whatever you want with this stuff. If we meet some day, and you      #
#  think this stuff is worth it, you can buy me a beer in return.              #
#                                                        –– Poul-Henning Kamp  #
#                                                                              #
################################################################################

from json import loads
from FrontBot import C
import URLShortener
import logging

def handle (headers, body):

    logging.debug('Handling GitLab hook')

    body = loads(body)

    if 'commits' in body:
        return push (headers, body)

    if 'object_kind' in body and body['object_kind'] == 'issue':
        return issues (headers, body)

    if 'object_kind' in body and body['object_kind'] == 'merge_request':
        return merge_request (headers, body)

    return tag (headers, body)


def push (headers, body):
    ret = '[%s] %s pushed %s commits to %s. (%s)' % ( C.Pink ( body['repository']['name'] ),
                                                      C.Cyan ( body['user_name'] ),
                                                      C.Bold ( len (body['commits']) ),
                                                      C.Red ( body['ref'].split('/')[-1] ),
                                                      C.Blue ( URLShortener.short ( body['repository']['homepage'] ), False ))
    for commit in body['commits']:
        ret += '\n%s %s: %s (%s)' % ( C.Gray ( commit['id'][:7] ) ,
                                      C.Cyan ( commit['author']['name'] ) ,
                                      commit['message'].split('\n')[0] ,
                                      C.Blue ( URLShortener.short ( commit['url'] ), False ) )
    return ret
        


def tag (headers, body):
    return ''


def issues (headers, body):
    ret = '%s %s' % ( C.Cyan ( body['user']['name'] ) ,
                      body['object_attributes']['action'] )
    if body['object_attributes']['action'] in [ 'open' , 'reopen' ]:
        ret += 'ed'
    else:
        ret += 'd'
    ret += ' issue %s. (%s)' % ( C.Gray ( '#'+str(body['object_attributes']['iid']) ) ,
                                 C.Blue ( URLShortener.short ( body['object_attributes']['url'] ) , False ) )
    return ret


def merge_request (headers, body):
    return ''

