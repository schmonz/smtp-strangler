# smtp-strangler

This is an implementation of the
[Strangler Fig pattern](https://martinfowler.com/bliki/StranglerFigApplication.html)
for any SMTP server program that can run under
[inetd(8)](https://wiki.netbsd.org/guide/inetd/)
or
[tcpserver(1)](https://cr.yp.to/ucspi-tcp/tcpserver.html).

In this environment, client requests arrive on `stdin` and server
responses go to `stdout`.

`io_strangler.py` sits in the command chain just before the
server program. It passes requests to the server and returns responses
to the client. This is pretty boring. But since it's written in Python,
it's pretty easy to start handling certain requests in a new way.

## Setup

### 0. Have Linux or another Unix-like system

- The legacy code to be strangled is a Unix command-line program

### 1. Get the old C code to be strangled

     $ cd .../place/to/put/source/trees
     $ git clone https://github.com/schmonz/mess822
     $ cd mess822
     $ git checkout smtp-strangler
     $ make

### 2. Get the Python Strangler code

     $ cd .../place/to/put/source/trees
     $ git clone https://github.com/schmonz/smtp-strangler

### 3. Configure PyCharm

- Right-click and run `tests.py`
- Right-click and run `io_strangler.py`
- Run -> Edit Configurations -> Parameters should be `.../place/to/put/source/trees/mess822-0.58/ofmipd`
- Run `io_strangler.py` again and it should work interactively (try `HELP`, `WORD UP`, `QUIT`)
