import os

from protocol_lines import ProtocolLinesIn
from protocol_smtp_request_parser import SMTPRequestParser


class SMTPRequests(ProtocolLinesIn):
    def __init__(self, logger, read_from_fd, write_to_fd):
        ProtocolLinesIn.__init__(self, logger, read_from_fd, write_to_fd)
        self.__want_data = False
        self.__in_data = False
        self.safe_to_munge = False

    def is_last_line_of_protocol_message(self, line):
        # XXX verb only
        if self.safe_to_munge and line.lower() == b'data\r\n':
            self.__want_data = True
        if self.__in_data and line == b'.\r\n':
            self.safe_to_munge = True
        return True

    @staticmethod
    def get_log_prefix():
        return b'SMTP  request>'

    def log_disconnect(self):
        self.logger.log(b'[client dropped connection]\r\n')

    def munge_message(self, message):
        if self.report_message_callback:
            self.report_message_callback(message)

        if not self.safe_to_munge:
            return message

        (verb, arg) = SMTPRequestParser(message).get_verb_and_arg()

        if verb.upper() == b'WORD':
            arg = verb + b' ' + arg
            verb = b'NOOP'
        elif verb.upper() == b'BRXT':
            verb = b'QUIT'

        return verb + b' ' + arg + b'\r\n'

    def receive_message(self, message):
        if self.__want_data:
            self.__want_data = False
            if message.lower().startswith(b'354 '):
                self.__in_data = True
            else:
                self.__in_data = False

        if self.__in_data:
            self.safe_to_munge = False
        else:
            self.safe_to_munge = True
