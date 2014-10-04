# Imports
from urllib import urlopen
from json import dumps, loads
from getpass import getpass

# 
print 'Hooker v0.1'
print '==========='
print 'This script will help you to configure your webhooks on GitHub.'
print 'Do not trust third-party softs too fast when they want to use your credentials...'
print

# Logins
print 'We first need your username and password.'
USERNAME = raw_input('Username: ')
PASSWORD = getpass()
print

def get_api (page = '', data = None):
    global USERNAME
    global PASSWORD
    return loads(urlopen('https://%s:%s@api.github.com/%s' \
                         % (USERNAME, PASSWORD, page),
                         data).read())

# Repositories
repos = get_api('users/%s/repos' % USERNAME)
print 'Found %d repositories on your account :' % len(repos)
print ', '.join([r['name'] for r in repos])
print

# Default values
print 'I will now ask you for the default hooks values of your repositories'

# URL
print 'The URL where you want the hooks to be sent. Don\'t forget the port !'
D_URL = raw_input('URL: ')
print

# Content type
print 'The hooks content type. Only json is supported by this project.'
#raw_input('Content type: ')
D_CTYPE = 'json'
print 'Content type: json'
print

# Secret
print 'The secret of the hook. Not supported yet.'
#SECRET = getpass('Secret: ')
D_SECRET = ''
print 'Secret: '
print

# Events
print 'A list separated by commas in which you can write the following hook events.'
print '  push, create, delete, status, deployment, deployment_status, pull_request,'
print '  pull_request_review_comment, commit_comment, issues, issue_comment, watch,'
print '  fork, public, member, team_add, release, gollum, page_build'
print '  You can also let this field empty (nothing) or fill it with \'*\' (everything).'
D_EVENTS = [s.strip() for s in raw_input('Events: ').split(',')]
print 

print 'I will now ask you for the configuration of each repository.'
print 'For each repo, you can answer three things: y, d, n.'
print '  y: Yes, install hook with the default config'
print '  n: No, do not install hook for this repository'
print '  d: Detail, install hook with the special config I\'ll give you'
print

for repo in repos:
    print 'Repository ' + repo['name']
    while True:
        ydn = raw_input('Install hook ? (ydn) [y] ')
        if ydn == '': ydn = 'y'
        if ydn in 'ydn': break
    if ydn == 'd':
        URL = raw_input('URL: ')
        CTYPE = 'json'
        print 'Content type: json'
        SECRET = ''
        print 'Secret: '
        EVENTS = [s.strip() for s in raw_input('Events: ').split(',')]
    else:
        URL = D_URL
        CTYPE = D_CTYPE
        SECRET = D_SECRET
        EVENTS = D_EVENTS
    if ydn in 'yd':
        ans = get_api('repos/%s/%s/hooks' % (USERNAME, repo['name']),
                      dumps({ 'name': 'web', 'active': True, 'events': EVENTS,
                              'config': {'url': URL, 'content_type': CTYPE } }))
        if 'errors' in ans:
            for error in ans['errors']:
                print error['message']
        else:
            print 'Done.'
    print

print 'Job done, cya !'
