import os


class Output:
    def write_bytes(self, the_bytes):
        pass


class FileDescriptorOutput(Output):
    def __init__(self, output_fd):
        self.output_fd = output_fd

    def write_bytes(self, the_bytes):
        os.write(self.output_fd, the_bytes)


class StringOutput(Output):
    def __init__(self):
        self.output_string = b''

    def write_bytes(self, the_bytes):
        self.output_string += the_bytes
