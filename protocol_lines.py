import os


class ProtocolLinesIn:
    def __init__(self, logger, read_from_fd, write_to_fd):
        self.logger = logger
        self.__read_from_fd = read_from_fd
        self.__write_to_fd = write_to_fd

        self.__bytes = b''
        self.__protocol_message = b''
        self.__protocol_messages = []

        self.report_message_callback = None

    def __accumulate(self, some_bytes):
        self.__bytes += some_bytes
        while b'\n' in self.__bytes:
            (line, self.__bytes) = self.__extract_first_line(self.__bytes)
            self.__protocol_message += line
            if self.is_last_line_of_protocol_message(line):
                self.__protocol_messages.append(self.__protocol_message)
                self.__protocol_message = b''

    @staticmethod
    def __extract_first_line(possibly_multiline):
        (first_line, leftovers) = possibly_multiline.split(b'\n', 1)
        first_line += b'\n'
        return (first_line, leftovers)

    def close(self):
        os.close(self.write_fd)

    @staticmethod
    def get_log_prefix():
        return b'protocol-line>'

    @property
    def read_fd(self):
        return self.__read_from_fd

    @property
    def write_fd(self):
        return self.__write_to_fd

    def has_whole_message(self):
        return len(self.__protocol_messages) > 0

    def is_last_line_of_protocol_message(self, line):
        return True

    def log_disconnect(self):
        self.logger.log(b'[protocol-line dropped connection]\r\n')

    def munge_message(self, message):
        return message

    def read(self, read_length):
        some_bytes = os.read(self.__read_from_fd, read_length)
        if some_bytes:
            self.__accumulate(some_bytes)
            return True
        else:
            self.log_disconnect()
            return False

    def report_messages(self, callback):
        self.report_message_callback = callback

    def send(self):
        message = self.__protocol_messages.pop(0)
        self.logger.log(b'       ' + self.get_log_prefix() +
                        b' ' + message)
        munged_message = self.munge_message(message)
        self.logger.log(b'munged-' + self.get_log_prefix() +
                        b' ' + munged_message + b'\r\n')
        os.write(self.__write_to_fd, munged_message)
