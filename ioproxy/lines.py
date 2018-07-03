import os


class LinesIn:
    def __init__(self, logger, input_source, output_source):
        self.logger = logger
        self.input_source = input_source
        self.output_source = output_source

        self.__bytes = b''
        self.__message = b''
        self.__messages = []

        self.report_message_callback = None

    def __accumulate_bytes(self, some_bytes):
        self.__bytes += some_bytes
        while b'\n' in self.__bytes:
            (line, self.__bytes) = self.__extract_first_line(self.__bytes)
            self.__accumulate_message_lines(line)
            if self.is_last_line_of_message(line):
                self.__queue_message()

    def __accumulate_message_lines(self, line):
        self.__message += line

    def __queue_message(self):
        self.__messages.append(self.__message)
        self.__message = b''

    @staticmethod
    def __extract_first_line(possibly_multiline):
        (first_line, leftovers) = possibly_multiline.split(b'\n', 1)
        first_line += b'\n'
        return (first_line, leftovers)

    def close(self):
        os.close(self.output_source.output_fd)

    @staticmethod
    def get_log_prefix():
        return b'line>'

    @property
    def read_fd(self):
        return self.input_source.input_fd

    @property
    def write_fd(self):
        return self.output_source.output_fd

    def has_whole_message(self):
        return len(self.__messages) > 0

    def is_last_line_of_message(self, line):
        return True

    def log_disconnect(self):
        self.logger.log(b'[line dropped connection]\r\n')

    def munge_message(self, message):
        return message

    def read(self, read_length):
        some_bytes = self.input_source.read_bytes(read_length)
        if some_bytes:
            self.__accumulate_bytes(some_bytes)
            return True
        else:
            self.log_disconnect()
            return False

    def report_messages(self, callback):
        self.report_message_callback = callback

    def send(self):
        message = self.__messages.pop(0)
        self.logger.log(b'          ' + self.get_log_prefix() +
                        b' ' + message)
        munged_message = self.munge_message(message)
        self.logger.log(b'strangler-' + self.get_log_prefix() +
                        b' ' + munged_message + b'\r\n')
        self.output_source.write_bytes(munged_message)
