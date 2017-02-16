GHA
===

A GitHub Announcer for IRC. Also support GitLab.

This project is made of :

- A web server receiving web hooks from GitHub or GitLab
- An [IRCBot](https://pypi.python.org/pypi/irc) writing on IRC.

It has been completely rewritten in python3 and does not support python 2 anymore

Get started
-----------

1. Copy the files to some place (or clone this repository).
2. Install the dependencies (you may want to use a
   [virtual environment](https://pypi.python.org/pypi/virtualenv))

```
pip3 install --upgrade -r requirements.txt
```

Try `./GHA.py --help`. You should see something like

    usage: ./GHA.py [-h] [-lh LISTEN_HOST] [-lp LISTEN_PORT] [-ih IRC_HOST]
                    [-ip IRC_PORT] [-ic [IRC_CHANS [IRC_CHANS ...]]]
                    [-in IRC_NAME] [-ea FILE] [-ia FILE] [--write-pid FILE]
                    [-re NICK]

    Github Announcer
    
    optional arguments:
      -h, --help            show this help message and exit
      -lh LISTEN_HOST, --listen-host LISTEN_HOST
                            the address where GHA will be listening
      -lp LISTEN_PORT, --listen-port LISTEN_PORT
                            the port where GHA will be listening
      -ih IRC_HOST, --irc-host IRC_HOST
                            the irc server's address
      -ip IRC_PORT, --irc-port IRC_PORT
                            the irc server's port
      -ic [IRC_CHANS [IRC_CHANS ...]], --irc-chans [IRC_CHANS [IRC_CHANS ...]]
                            the irc channels
      -in IRC_NAME, --irc-name IRC_NAME
                            the bot's name
      -ea FILE, --export-arguments FILE
                            export arguments in the given file
      -ia FILE, --import-arguments FILE
                            import arguments from the given file
      -re NICK, --report-errors NICK
			    Report errors to the given person
    
A simple case to get started:

    ./GHA.py -lp 9090 -ih irc.freenode.net -ic '#GHA' -ea my-gha.cnf

This will create the file `my.cnf` containing the configuration for a GitHub Announcer listening on `0.0.0.0:9090`, and connected on `irc.freenode.net/6667` on channel `#GHA`.
You can change the listening host with `-lh`, the IRC port with `-ip`, the IRC name of the bot with `-in`.
You can tell GHA to report error messages to a specific person using the `-re`
option.

Note that the channel list must be quoted, since `#` is a special character in shell.

After that, you just need to use:

    ./GHA.py -ia my-gha.cnf

You can change the `my-gha.cnf` yourself, if you respect the JSON syntax
[supported by python](https://docs.python.org/3/library/json.html).

Now that your `GHA` is running, you just have to
[set your GitHub/GitLab webhooks](https://github.com/Niols/GHA/wiki/Add-a-WebHook).



Why this script ?
-----------------

Note that there exists an IRC Service for GitHub.

But:

- This script also support GitLab.
- The bot stays on the IRC chan, and do not join-part all the time.
- A script can easily be modified, if you want to change a little part of it.


License
-------

> BEERWARE Licence
> 
> <niols@niols.net> wrote this file. As long as you retain this notice you
> can do whatever you want with this stuff. If we meet some day, and you think
> this stuff is worth it, you can buy me a beer in return.
> 
> —— Poul-Henning Kamp

