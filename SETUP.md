# 0. Have Linux or another Unix-like system

- The legacy code to be strangled is a Unix command-line program

# 1. Get the old C code to be strangled

     $ cd .../place/to/put/source/trees
     $ wget https://cr.yp.to/software/mess822-0.58.tar.gz
     $ tar -zxf mess822-0.58.tar.gz && rm mess822-0.58.tar.gz
     $ cd mess822
     $ sed -e '1s|$| -include /usr/include/errno.h|' < conf-cc > tmp && mv tmp conf-cc
     $ sed -e "1s|.*|$(pwd)|" < conf-qmail > tmp && mv tmp conf-qmail
     $ make

# 2. Get the Python Strangler code

     $ cd .../place/to/put/source/trees
     $ git clone https://github.com/schmonz/smtp-strangler

# 3. Configure PyCharm

- Right-click and run `tests.py`
- Right-click and run `io_strangler.py`
- Run -> Edit Configurations -> Parameters should be `smtp .../place/to/put/source/trees/mess822-0.58/ofmipd`
- Run `io_strangler.py` again and it should work interactively (try `HELP`, `QUIT`)
