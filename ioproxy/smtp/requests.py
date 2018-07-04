import os

from ioproxy.lines import LinesIn
from ioproxy.smtp.request_parser import SMTPRequestParser


class SMTPRequests(LinesIn):
    def __init__(self, logger, input_source, output_fd):
        LinesIn.__init__(self, logger, input_source, output_fd)
        self.want_data = False
        self.safe_to_munge = True

    @staticmethod
    def __munge_brxt(verb, arg):
        verb = b'QUIT'
        return (verb, arg)

    @staticmethod
    def __munge_mail(verb, arg):
        (unused, recipient) = arg.split(b': ', 1)
        if (b'tim' == recipient):
            return (b'NOOP', verb + b' ' + arg)
        else:
            return (verb, arg)

    @staticmethod
    def __munge_noop(verb, arg):
        arg = verb + b' ' + arg
        verb = b'NOOP'
        return (verb, arg)

    def is_last_line_of_message(self, line):
        (verb, arg) = SMTPRequestParser(line).get_verb_and_arg()
        if self.safe_to_munge and verb.upper() == b'DATA':
            self.want_data = True
        if not self.safe_to_munge and verb == b'.':
            self.want_data = False
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
            b'CONF': self.__munge_noop,
            b'MAIL': self.__munge_mail,
            b'WORD': self.__munge_noop,
        }
        try:
            function = munge_functions[verb.upper()]
            (verb, arg) = function(verb, arg)
        except KeyError:
            pass

        return verb + b' ' + arg + b'\r\n'

    def receive_message(self, message):
        if self.want_data and message.lower().startswith(b'354 '):
            self.safe_to_munge = False
        else:
            self.safe_to_munge = True
