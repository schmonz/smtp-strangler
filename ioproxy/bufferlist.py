import select


class BufferList:
    def __init__(self, buffer_list):
        self.__buffer_list = buffer_list
        self.__fd_list = []
        for each_buffer in self.__buffer_list:
            self.__fd_list.append(each_buffer.read_fd)

    def close(self):
        for each_buffer in self.__buffer_list:
            each_buffer.close()

    def get_all(self):
        return self.__buffer_list

    def get_readables(self):
        (reads, writes, exceptionals) = select.select(self.__fd_list, [], [])
        readables = []
        for each_buffer in self.__buffer_list:
            if each_buffer.read_fd in reads:
                readables.append(each_buffer)
        return readables
