#!/usr/bin/env python
# -*- coding: utf-8 -*-

################################################################################
#                                                                              #
#                                GitHubHooks.py                                #
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


class GitHubHooks:

    def handle (self, headers, body):
        logging.debug('Handling Github hook')
        body = loads (body)
        if 'X-Github-Event' in headers.keys():
            message = getattr(self, headers['X-Github-Event']) (headers, body);
            if message:
                return '[%s] %s' % ( C.Pink ( body['repository']['full_name'] ), message )
            else:
                return ''
        return ''

    def commit_comment (self, headers, body):
        return '%s commented on commit %s. (%s)' % ( C.Cyan( body['comment']['user']['login'] ),
                                                     C.Gray( body['comment']['commit_id'][:7] ),
                                                     C.Blue( URLShortener.short( body['comment']['html_url'] ), False ) )

    def create (self, headers, body):
        if body['ref_type'] == 'repository':
            return '%s created a repository. (%s)' % ( C.Cyan( body['sender']['login'] ),
                                                       C.Blue( URLShortener.short( body['repository']['html_url'] ), False ) )
        else:
            return '%s created the %s %s.' % ( C.Cyan( body['sender']['login'] ),
                                               body['ref_type'],
                                               C.Red( body['ref'] ) )

    def delete (self, headers, body):
        return '%s deleted the %s %s.' % ( C.Cyan( body['sender']['login'] ),
                                           body['ref_type'],
                                           C.Red( body['ref'] ) )

    def deployment (self, headers, body):
        logging.warning('GitHubHooks.deployment')
        return 'The %s environment has been deployed.' % ( C.Bold( body['deployment']['environment'] ), )

    def deployment_status (self, headers, body):
        logging.warning('GitHubHooks.deployment')
        return 'The %s environment has been deployed with %s.' % ( C.Bold( body['deployment']['environment'] ),
                                                                   C.Bold( body['deployment_status']['state'] ) )

    def download (self, headers, body):
        logging.warning('GitHubHooks.download')
        return ''

    def follow (self, headers, body):
        logging.warning('GitHubHooks.follow')
        return ''

    def fork (self, headers, body):
        return '%s forked to %s.' % ( C.Cyan( body['sender']['login'] ),
                                      C.Pink( body['forkee']['full_name'] ) )

    def fork_apply (self, headers, body):
        logging.warning('GitHubHooks.fork_apply')
        return ''

    def gist (self, headers, body):
        logging.warning('GitHubHooks.gist')
        return ''

    def gollum (self, headers, body):
        string = '%s updated the wiki. (%s)' % ( C.Cyan( body['sender']['login'] ),
                                                 C.Blue( URLShortener.short( body['repository']['html_url']+'/wiki' ), False ) )
        for page in body['pages']:
            string += '\n%s %s %s. (%s)' % ( C.Gray( page['sha'][:7] ), # Really 7 for pages sha ?
                                             page['action'],
                                             C.Bold( page['page_name'] ),
                                             C.Blue( URLShortener.short( page['html_url'] ) , False ) )
        return string

    def issues (self, headers, body):
        string = '%s %s ' % ( C.Cyan( body['sender']['login'] ),
                              body['action'] )
        if body['action'] in ['assigned', 'unassigned']:
            if body['assignee']['login'] == body['sender']['login']:
                string += 'himself on ' # What about women ? =(
            else:
                string += '%s on ' % ( C.Cyan( body['assignee']['login'] ), )
        string += 'issue %s. (%s)' % ( C.Gray( '#'+str(body['issue']['number']) ),
                                       C.Blue( URLShortener.short( body['issue']['html_url'] ), False ) )
        return string

    def issue_comment (self, headers, body):
        return '%s commented issue %s. (%s)' % ( C.Cyan( body['comment']['user']['login'] ),
                                                 C.Gray( '#'+str(body['issue']['number']) ),
                                                 C.Blue( URLShortener.short( body['issue']['html_url'] ), False ) )

    def member (self, headers, body):
        return '%s added %s as collaborator.' % ( C.Cyan( body['sender']['login'] ),
                                                  C.Cyan( body['member']['login'] ) )

    def page_build (self, headers, body):
        logging.warning('GitHubHooks.page_build')
        return ''

    def ping (self, headers, body):
        return '%s pinged me.' % body['sender']['login']

    def public (self, headers, body):
        return '%s made this repository public.' % ( C.Cyan( body['sender']['login'] ) )

    def pull_request (self, headers, body):
        string = '%s %s ' % ( C.Cyan( body['sender']['login'] ),
                              body['action'] )
        if body['action'] in ['assigned', 'unassigned']:
            string += '%s on ' % ( C.Cyan( body['assignee']['login'] ), )
        string += 'pull request %s. (%s)' % ( C.Gray( '#'+str(body['pull_request']['number']) ),
                                              C.Blue( URLShortener.short( body['pull_request']['html_url'] ), False ) )

    def pull_request_review_comment (self, headers, body):
        return '%s commented pull request %s. (%s)' % ( C.Cyan( body['comment']['user']['login'] ),
                                                        C.Gray( '#'+str(body['pull_request']['number']) ),
                                                        C.Blue( URLShortener.short( body['comment']['html_url'] ), False ) )

    def push (self, headers, body):
        max_commits_shown = 5
	if body['commits']:
            string = '%s pushed %s commits to %s. (%s)' % ( C.Cyan( body['pusher']['name'] ),
        	                                                C.Bold( len(body['commits']) ),
                	                                        C.Red( body['ref'].split('/')[-1] ),
                        	                                C.Blue( URLShortener.short( body['compare'] ), False ) )
            if len (body['commits']) > max_commits_shown:
                string += '\nHere are the last %d:' % (max_commits_shown,)
            for commit in body['commits'][-max_commits_shown:]:
                string += '\n%s %s: %s' % ( C.Gray( commit['id'][:7] ),
                	                        C.Cyan( commit['committer']['username'] if 'username' in commit['committer'] else commit['committer']['name'] ),
                        	                commit['message'].split('\n')[0] )
            return string
	else:
            return ''

    def release (self, headers, body):
        ret = '%s %s the release %s' % ( C.Cyan ( body['release']['author']['login'] ) ,
                                          body['action'] ,
                                          C.Red ( body['release']['tag_name'] ) )
        if body['release']['name']: ret += ': ' + body['release']['name']
        return ret + '.'

    def status (self, headers, body):
        logging.warning('GitHubHooks.status')
        return ''

    def team_add (self, headers, body):
        logging.warning('GitHubHooks.team_add')
        return ''

    def watch (self, headers, body):
        return '%s just watched this repository.' % ( C.Cyan ( body['sender']['login']) )


GitHubHooks = GitHubHooks ()
