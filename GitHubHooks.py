#!/usr/bin/env python
# -*- coding: utf-8 -*-


class GitHubHooks:

    def push (self, headers, body):
        string = '[%s] % pushed %d commits to %s: %s' % ( body['repository']['full_name'], # rose
                                                          body['pusher']['name'],
                                                          len(body['commits']), # gras
                                                          body['ref_name'], # violet
                                                          body['compare'] ) # bleu + miniurl))
        for commit in body['commits']:
            string += '%s %s: %s' % ( commit['id'][:7], # gris
                                      commit['committer']['username'],
                                      commit['message'].split('\n')[0] )
        return string



GitHubHooks = GitHubHooks ()
GHH = GitHubHooks
