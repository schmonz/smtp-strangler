import os

from ioproxy.lines import LinesIn
from ioproxy.smtp.request_parser import SMTPRequestParser

class SMTPResponses(LinesIn):
    def __init__(self, logger, input_source, output_fd):
        LinesIn.__init__(self, logger, input_source, output_fd)
        self.safe_to_modify = True
        self.reset_flags()

    def reset_flags(self):
        self.conf = False
        self.ehlo = False

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

    def modify_message(self, response):
        if self.report_message_callback:
            self.report_message_callback(response)

        if not self.safe_to_modify:
            return response

        if self.conf:
            return b"250 https://www.agilealliance.org/deliveragile-2019\r\n"

        if self.ehlo:
            response += b'250 GDPR 20160414\r\n'

        response = self.__reformat_multiline_response(response)
        return response

    def set_state_for_next_response(self, request):
        self.reset_flags()
        (verb, arg) = SMTPRequestParser(request).get_verb_and_arg()
        if verb.upper() == b'CONF':
            self.conf = True
        if verb.upper() == b'EHLO':
            self.ehlo = True
