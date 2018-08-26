import os


class Logger:
    def __init__(self, fd):
        self.__fd = fd

    def log(self, message):
        os.write(self.__fd, message)


class NoLogging(Logger):
    def __init__(self):
        Logger.__init__(self, -1)

    def log(self, message):
        pass
