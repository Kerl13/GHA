GHA
===

A GitHub Announcer for IRC.

This project has two parts :

* one very simple webserver listening for webhooks on a given port
* one little IRCBot writing it (in colors !) on IRC


Installation
------------

Just copy the files to some place (or clone this repository).

You also need to install Bottle (http://bottlepy.org).
That can be done with `pip install bottle`.
There's also a version of Bottle in the repository.
So you can just rename Bottle-version.py into Bottle.py.


Utilisation
-----------

### Script's side

The python script needs some parameters, that you can get *via* `python gha.py --help`.

    usage: gha.py [-h] [-gh GH_HOST] [-gp GH_PORT] [-ih IRC_HOST] [-ip IRC_PORT]
                  [-ic [IRC_CHANS [IRC_CHANS ...]]] [-in IRC_NAME] [-ea FILE]
                  [-ia FILE]

    optional arguments:
      -h, --help            show this help message and exit
      -gh GH_HOST, --gh-host GH_HOST
                            the address where github sends the data
      -gp GH_PORT, --gh-port GH_PORT
                            the port where github sends the data
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

For example :

    python gha.py --gh-host some.place.com --gh-port 4242 \
        --irc-host irc.freenode.net --irc-port 6667 \
        --irc-chans '#oneChan' '#oneOtherChan' --irc-name MyIRCBot

If you want to re-use several times the same config, you should save it in a file :

    python gha.py -gh some.place.com ... -in MyIRCBot --export-arguments my_file.cnf

After that, you only need to import your arguments from this file :

    python gha.py --import-arguments my_file.cnf

And you can override the file arguments with yours :

    python gha.py -ia my_file.cnf -gp 4224


### GitHub's side

In your repositoriy's settings, go to « Webhooks & Services ».
Look for the « Add webhook » button.

* You need to give the url that you gave to the script to « Payload URL » (in the example, that will be `http://some.place.com:4242/`).
* In « Content type » select `application/json` (by default) which is the only one supported
* The select your webhooks. GHA doesn't support everything, but it'll improve (i promise !)
* Aaaand… click on « Add webhook » :)

You can also use the `hooker.py` script. It'll try to help you adding your webhooks.  
**Be carefull with scripts that want to access to your credentials !**

Simply run `python hooker.py` and answer to his questions.


Why this script ?
-----------------

Note that there exists an IRC Service for GitHub, but it has an inconvenient : the bot isn't staying on the IRC channel(s). You have then two solutions : either your channel doesn't have the `+n` mode, either the bot will join/part each time you have a message…

I wanted not to get spammed (too much), and to keep my `+n` mode.

By the way, a script can be easely modified :)


License
-------

BEERWARE Licence

<niols@niols.net> wrote this file. As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return.

–– Poul-Henning Kamp

