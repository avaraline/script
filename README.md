script
======

Our little IRC bot, written in Python 3 using tornado.

Email Gateway
=============

In /etc/postfix/master.cf:

    script    unix  -       n       n       -       -       pipe
      user=dcwatson argv=/usr/bin/nc -c localhost 7100

And in /etc/postfix/transport:

    script@domain.com    script:
