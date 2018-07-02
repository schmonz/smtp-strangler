import os

from ioproxy.protocols.lines.lines import ProtocolLinesIn


class POP3Requests(ProtocolLinesIn):
    def is_last_line_of_protocol_message(self, line):
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