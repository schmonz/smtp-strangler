import os

class Input:
    def read_bytes(self, num_bytes):
        pass


class FileDescriptorInput(Input):
    def __init__(self, input_fd):
        self.input_fd = input_fd

    def read_bytes(self, num_bytes):
        return os.read(self.input_fd, num_bytes)


class StringInput(Input):
    def __init__(self, input_string):
        self.input_string = input_string

    def read_bytes(self, num_bytes):
        some_bytes = self.input_string[:num_bytes]
        self.input_string = self.input_string[num_bytes:]
        return some_bytes
