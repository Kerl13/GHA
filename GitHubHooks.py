#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import loads
from FrontBot import C

class GitHubHooks:

    def handle (self, headers, body):
        if 'X-Github-Event' in headers.keys():
            return getattr(self, headers['X-Github-Event']) (headers, loads(body))
        return ''

    def push (self, headers, body):
        string = '[%s] %s pushed %s commits to %s: %s' % ( C.Pink( body['repository']['full_name'] ), # rose
                                                           body['pusher']['name'],
                                                           C.Bold( len(body['commits']) ), # gras
                                                           C.Red( body['ref'].split('/')[-1] ), # violet
                                                           C.Blue( body['compare'], False ) ) # bleu + miniurl))
        for commit in body['commits']:
            string += '\n%s %s: %s' % ( C.Gray( commit['id'][:7] ), # gris
                                        commit['committer']['username'],
                                        commit['message'].split('\n')[0] )
        return string



GitHubHooks = GitHubHooks ()
GHH = GitHubHooks
