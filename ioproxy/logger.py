import os


class ProtocolLogger:
    def __init__(self, fd):
        self.__fd = fd

    def log(self, message):
        os.write(self.__fd, message)
