#!/usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
#                                                                             #
#                                GitLabHooks.py                               #
#                                   by Niols                                  #
#                                                                             #
#  BEERWARE License:                                                          #
#  <niols@niols.net> wrote this file. As long as you retain this notice you   #
#  can do whatever you want with this stuff. If we meet some day, and you     #
#  think this stuff is worth it, you can buy me a beer in return.             #
#                                                       –– Poul-Henning Kamp  #
#                                                                             #
###############################################################################

from json import loads
from FrontBot import C
import URLShortener
import logging


def _strip_repo(repo):
    return('/'.join(repo.split('/')[-2:]))


def _preterit(verb):
    if verb in ['open', 'reopen']:
        return "%sed" % verb
    else:
        return "%sd" % verb


def handle(headers, body):

    logging.debug('Handling GitLab hook')

    body = loads(body)

    if 'commits' in body:
        return push(headers, body)

    if 'object_kind' in body and body['object_kind'] == 'issue':
        return issues(headers, body)

    if 'object_kind' in body and body['object_kind'] == 'merge_request':
        return merge_request(headers, body)

    return tag(headers, body)


def push(headers, body):
    max_commits_shown = 5
    if body['commits']:
        ret = '[%s] %s pushed %s commits to %s. (%s)' \
              % (C.Pink(_strip_repo(body['repository']['homepage'])),
                 C.Cyan(body['user_name']),
                 C.Bold(len(body['commits'])),
                 C.LightRed(body['ref'].split('/')[-1]),
                 C.Blue(URLShortener.short("%s/compare/%s...%s"
                        % (body['repository']['homepage'],
                           body['before'],
                           body['after'])), False))
        if len(body['commits']) > max_commits_shown:
            ret += '\nHere are the last %d:' % (max_commits_shown,)
        for commit in body['commits'][-max_commits_shown:]:
            ret += '\n%s %s: %s' % (C.Gray(commit['id'][:9]),
                                    # For GitLab, this is 9 ^
                                    C.Cyan(commit['author']['name']),
                                    commit['message'].split('\n')[0])
        return ret
    else:
        return ''


def tag(headers, body):
    return '[%s] %s added the tag %s.' \
            % (C.Pink(_strip_repo(body['repository']['homepage'])),
               C.Cyan(body['user_name']),
               C.LightRed(body['ref'].split('/')[-1]))


def issues(headers, body):
    ret = '%s %s' % (C.Cyan(body['user']['name']),  # user / username ?
                     _preterit(body['object_attributes']['action']))
    ret += ' issue %s. (%s)' \
           % (C.Gray('#%d' % body['object_attributes']['iid']),
              C.Blue(URLShortener.short(body['object_attributes']['url']),
                     False))
    return ret


def merge_request(headers, body):
    return '[%s] %s %s merge request %s. (%s)' \
            % (C.Pink(_strip_repo(
                   body['object_attributes']['target']['web_url'])),
               C.Cyan(body['user']['name']),
               _preterit(body['object_attributes']['action']),
               C.Bold(body['object_attributes']['iid']),
               C.Blue(URLShortener.short(body['object_attributes']['url']),
                      False))
