#!/usr/bin/env python
# -*- coding: utf-8 -*-

from json import loads
from FrontBot import C


class GithubHooks:

    su = None

    def add_su(self, su):
        self.su = su

    def handle (self, headers, body):
        body = loads (body)
        if 'X-Github-Event' in headers.keys():
            return '[%s] %s' % ( C.Pink ( body['repository']['full_name'] ),
                                 getattr(self, headers['X-Github-Event']) (headers, body) )
        return ''

    def commit_comment (self, headers, body):
        return '%s commented on commit %s. (%s)' % ( C.Cyan( body['comment']['user']['login'] ),
                                                     C.Gray( body['comment']['commit_id'][:7] ),
                                                     C.Blue( self.su.url_to_short( body['comment']['html_url'] ), False ) )

    def create (self, headers, body):
        if body['ref_type'] == 'repository':
            return '%s created a repository. (%s)' % ( C.Cyan( body['sender']['login'] ),
                                                       C.Blue( self.su.url_to_short( body['repository']['html_url'] ), False ) )
        else:
            return '%s created the %s %s.' % ( C.Cyan( body['sender']['login'] ),
                                               body['ref_type'],
                                               C.Red( body['ref'] ) )

    def delete (self, headers, body):
        return '%s deleted the %s %s.' % ( C.Cyan( body['sender']['login'] ),
                                           body['ref_type'],
                                           C.Red( body['ref'] ) )

    def deployment (self, headers, body):
#        # V.prnt( 'GithubHooks.deployment', V.ERROR )
        return 'The %s environment has been deployed.' % ( C.Bold( body['deployment']['environment'] ), )

    def deployment_status (self, headers, body):
        # V.prnt( 'GithubHooks.deployment', V.ERROR )
        return 'The %s environment has been deployed with %s.' % ( C.Bold( body['deployment']['environment'] ),
                                                                   C.Bold( body['deployment_status']['state'] ) )

    def download (self, headers, body):
        # V.prnt( 'GithubHooks.download', V.ERROR )
        return ''

    def follow (self, headers, body):
        # V.prnt( 'GithubHooks.follow', V.ERROR )
        return ''

    def fork (self, headers, body):
        return '%s forked to %s.' % ( C.Cyan( body['sender']['login'] ),
                                      C.Pink( body['forkee']['full_name'] ) )

    def fork_apply (self, headers, body):
        # V.prnt( 'GithubHooks.fork_apply', V.ERROR )
        return ''

    def gist (self, headers, body):
        # V.prnt( 'GithubHooks.gist', V.ERROR )
        return ''

    def gollum (self, headers, body):
        string = '%s updated the wiki. (%s)' % ( C.Cyan( body['sender']['login'] ),
                                                 C.Blue( self.su.url_to_short( body['repository']['html_url']+'/wiki' ), False ) )
        for page in body['pages']:
            string += '\n%s %s %s. (%s)' % ( C.Gray( page['sha'][:7] ), # Really 7 for pages sha ?
                                             page['action'],
                                             C.Bold( page['page_name'] ),
                                             C.Blue( page['html_url'], False ) )
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
                                       C.Blue( self.su.url_to_short( body['issue']['html_url'] ), False ) )
        return string

    def issue_comment (self, headers, body):
        return '%s commented issue %s. (%s)' % ( C.Cyan( body['comment']['user']['login'] ),
                                                 C.Gray( '#'+str(body['issue']['number']) ),
                                                 C.Blue( self.su.url_to_short( body['issue']['html_url'] ), False ) )

    def member (self, headers, body):
        return '%s added %s as collaborator.' % ( C.Cyan( body['sender']['login'] ),
                                                       C.Cyan( body['member']['login'] ) )

    def page_build (self, headers, body):
        # V.prnt( 'GithubHooks.page_build', V.ERROR )
        return ''

    def ping (self, headers, body):
        # V.prnt( 'GithubHooks.ping', V.ERROR )
        return ''

    def public (self, headers, body):
        return '%s made this repository public.' % ( C.Cyan( body['sender']['login'] ) )

    def pull_request (self, headers, body):
        string = '%s %s ' % ( C.Cyan( body['sender']['login'] ),
                              body['action'] )
        if body['action'] in ['assigned', 'unassigned']:
            string += '%s on ' % ( C.Cyan( body['assignee']['login'] ), )
        string += 'pull request %s. (%s)' % ( C.Gray( '#'+str(body['pull_request']['number']) ),
                                              C.Blue( self.su.url_to_short( body['pull_request']['html_url'] ), False ) )

    def pull_request_review_comment (self, headers, body):
        return '%s commented pull request %s. (%s)' % ( C.Cyan( body['comment']['user']['login'] ),
                                                        C.Gray( '#'+str(body['pull_request']['number']) ),
                                                        C.Blue( self.su.url_to_short( body['comment']['html_url'] ), False ) )

    def push (self, headers, body):
	if body['commits']:
	        string = '%s pushed %s commits to %s. (%s)' % ( C.Cyan( body['pusher']['name'] ),
        	                                                C.Bold( len(body['commits']) ),
                	                                        C.Red( body['ref'].split('/')[-1] ),
                        	                                C.Blue( self.su.url_to_short( body['compare'] ), False ) )
        	for commit in body['commits']:
                    string += '\n%s %s: %s' % ( C.Gray( commit['id'][:7] ),
                	                        C.Cyan( commit['committer']['username'] ),
                        	                commit['message'].split('\n')[0] )
	        return string
	else:
		return ""

    def release (self, headers, body):
        # V.prnt( 'GithubHooks.release', V.ERROR )
        return ''

    def status (self, headers, body):
        # V.prnt( 'GithubHooks.status', V.ERROR )
        return ''

    def team_add (self, headers, body):
        # V.prnt( 'GithubHooks.team_add', V.ERROR )
        return ''

    def watch (self, headers, body):
        # V.prnt ('GithubHooks.watch', V.ERROR )
        return ''


GithubHooks = GithubHooks ()
