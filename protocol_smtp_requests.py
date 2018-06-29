import os

from protocol_lines import ProtocolLinesIn
from protocol_smtp_request_parser import SMTPRequestParser


class SMTPRequests(ProtocolLinesIn):
    def __init__(self, logger, read_from_fd, write_to_fd):
        ProtocolLinesIn.__init__(self, logger, read_from_fd, write_to_fd)
        self.__want_data = False
        self.__in_data = False
        self.safe_to_munge = False

    @staticmethod
    def __munge_brxt(verb, arg):
        verb = b'QUIT'
        return (verb, arg)

    @staticmethod
    def __munge_word(verb, arg):
        arg = verb + b' ' + arg
        verb = b'NOOP'
        return (verb, arg)

    def is_last_line_of_protocol_message(self, line):
        (verb, arg) = SMTPRequestParser(line).get_verb_and_arg()
        if self.safe_to_munge and verb.upper() == b'DATA':
            self.__want_data = True
        if self.__in_data and verb == b'.':
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

        munge_functions = {
            b'BRXT': self.__munge_brxt,
            b'WORD': self.__munge_word,
        }
        try:
            function = munge_functions[verb.upper()]
            (verb, arg) = function(verb, arg)
        except KeyError:
            pass

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
