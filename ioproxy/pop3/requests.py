import os

from ioproxy.input_source import FileDescriptorInputSource
from ioproxy.lines import LinesIn


class POP3Requests(LinesIn):
    def __init__(self, logger, input_fd, output_fd):
        LinesIn.__init__(self, logger, FileDescriptorInputSource(input_fd), output_fd)

    def is_last_line_of_message(self, line):
        return True

    @staticmethod
    def get_log_prefix():
        return b'POP3  request>'

    def log_disconnect(self):
        self.logger.log(b'[client dropped connection]\r\n')

    def munge_message(self, message):
        if self.report_message_callback:
            self.report_message_callback(message)

        return message
