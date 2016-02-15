TS3 maintainer bot
==================

Right now this software is clasiffied as a garbage. A lot of improvements are needed.

Main requirements:
- cleaning not needed channels (with prior quarantine time) - done
- monitoring time of users spent on each channel
- data gathering (which channel is used the most, which can be deleted, previous usernames)



Additional:
- monitoring users, relations (tbd)
- add possibity to post informations via webpage on the 'banner'
- ensure channel name length, poke/msg when too long +automatically shorten
- implement mechanics of 'trust' for old users.



How to start using maintaner
============================

1. Resolve dependencies by installing requirements.txt
2. Fill maintainer/configuration.py with your credentials
3. ./maintainer.sh


I'm running that in cron.

Right now it is only cleaning up older, not used channels. More functionalities are pending. 
