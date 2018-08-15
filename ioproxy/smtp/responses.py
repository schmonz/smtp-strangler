import os

from ioproxy.lines import LinesIn
from ioproxy.smtp.request_parser import SMTPRequestParser


class SMTPResponses(LinesIn):
    def __init__(self, logger, input_source, output_fd):
        LinesIn.__init__(self, logger, input_source, output_fd)
        self.safe_to_munge = True
        self.should_munge_nebytes = False
        self.should_munge_ehlo = False

    @staticmethod
    def __reformat_multiline_response(message):
        reformatted = b''

        index = 3
        continues = b'-'
        ends = b' '

        lines = message.splitlines(True)
        for line in lines[:-1]:
            reformatted += line[:index] + continues + line[1+index:]
        reformatted += lines[-1][:index] + ends + lines[-1][1+index:]

        return reformatted

    def close(self):
        os.close(self.read_fd)

    @staticmethod
    def get_log_prefix():
        return b'SMTP response<'

    @staticmethod
    def __is_one_ordinary_space(char):
        one_ordinary_space = ord(b' ')
        try:
            return one_ordinary_space == ord(char)
        except TypeError:
            return one_ordinary_space == char

    def is_last_line_of_message(self, line):
        return len(line) >= 4 and self.__is_one_ordinary_space(line[3])

    def log_disconnect(self):
        self.logger.log(b'[server dropped connection]\r\n')

    def munge_message(self, message):
        if self.report_message_callback:
            self.report_message_callback(message)

        if not self.safe_to_munge:
            return message

        if self.should_munge_nebytes:
            message = b'250 http://www.nebytes.net\r\n'
            self.should_munge_nebytes = False
        if self.should_munge_ehlo:
            message += b'250 GDPR 20160414\r\n'
            self.should_munge_ehlo = False
        message = self.__reformat_multiline_response(message)
        return message

    def receive_message(self, message):
        (verb, arg) = SMTPRequestParser(message).get_verb_and_arg()
        if verb.upper() == b'NEBYTES':
            self.should_munge_nebytes = True
        if verb.upper() == b'EHLO':
            self.should_munge_ehlo = True