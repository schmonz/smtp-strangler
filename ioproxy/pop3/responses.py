import os

from ioproxy.lines import LinesIn


class POP3Responses(LinesIn):
    def __init__(self, logger, input_fd, output_fd):
        LinesIn.__init__(self, logger, input_fd, output_fd)
        self.expect_multiline_response = False
        self.report_message_callback = None

    def close(self):
        os.close(self.read_fd)

    @staticmethod
    def get_log_prefix():
        return b'POP3 response<'

    def is_last_line_of_message(self, line):
        if self.expect_multiline_response:
            if line.upper().startswith(b'-ERR ') or line == b'.\r\n':
                self.expect_multiline_response = False
                return True
        else:
            return True

    def log_disconnect(self):
        self.logger.log(b'[server dropped connection]\r\n')

    def munge_message(self, message):
        return message

    def receive_message(self, message):
        message = message.rstrip(b'\r\n')
        if b' ' in message:
            verb = message.split(b' ', 1)
        else:
            verb = message
        verb = verb.upper()

        multiline_response_verbs = {
            b'CAPA': True,
            b'GET': True,
            b'LIST': True,
            b'TOP': True,
            b'UIDL': True,
        }

        self.expect_multiline_response = verb in multiline_response_verbs
