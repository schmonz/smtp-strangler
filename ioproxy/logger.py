import os


class Logger:
    def __init__(self, fd):
        self.__fd = fd

    def log(self, message):
        os.write(self.__fd, message)
