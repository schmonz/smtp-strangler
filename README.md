# smtp-strangler

This is an implementation of the
[Strangler pattern](https://martinfowler.com/bliki/StranglerApplication.html)
for any SMTP or POP3 server program that can run under
[inetd(8)](https://wiki.netbsd.org/guide/inetd/)
or
[tcpserver(1)](https://cr.yp.to/ucspi-tcp/tcpserver.html).

In this environment, client requests arrive on `stdin` and server
responses go to `stdout`.

`io_strangler.py` sits in the command chain just before the
server program. It passes requests to the server and returns responses
to the client. This is pretty boring. But since it's written in Python,
it's pretty easy to start handling certain requests in a new way.
