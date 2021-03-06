import os
import sys

from ioproxy.buffer_list import FileDescriptorBufferList


class Proxy:
    def __init__(self, buffer_list):
        self.__buffers = buffer_list

    @staticmethod
    def __await_child_exitcode(child):
        (pid, exitcode, resources) = os.wait4(child, 0)
        return exitcode

    def proxy(self, read_length):
        someone_closed = False

        while not someone_closed:
            for each_buffer in self.__buffers.get_all():
                while each_buffer.has_whole_message():
                    each_buffer.send()
            for each_buffer in self.__buffers.get_readables():
                if not each_buffer.read(read_length):
                    someone_closed = True

        self.__buffers.close()

    def exit(self, child):
        sys.exit(self.__await_child_exitcode(child))
