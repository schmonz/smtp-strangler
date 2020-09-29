from ioproxy.lines import LinesIn
from ioproxy.smtp.request_parser import SMTPRequestParser


class SMTPRequests(LinesIn):
    def __init__(self, logger, input_source, output_fd):
        LinesIn.__init__(self, logger, input_source, output_fd)
        self.want_data = False
        self.safe_to_modify = True

    @staticmethod
    def __modify_noop(verb, arg):
        arg = verb + b' ' + arg
        verb = b'NOOP'
        return (verb, arg)

    @staticmethod
    def __modify_bye(verb, arg):
        return (b'QUIT', arg)

    def is_last_line_of_message(self, line):
        (verb, arg) = SMTPRequestParser(line).get_verb_and_arg()
        if self.safe_to_modify and verb.upper() == b'DATA':
            self.want_data = True
        if not self.safe_to_modify and verb == b'.':
            self.want_data = False
        return True

    @staticmethod
    def get_log_prefix():
        return b'SMTP  request>'

    def log_disconnect(self):
        self.logger.log(b'[client dropped connection]\r\n')

    def modify_message(self, message):
        if self.report_message_callback:
            self.report_message_callback(message)

        if not self.safe_to_modify:
            return message

        (verb, arg) = SMTPRequestParser(message).get_verb_and_arg()

        modifier_functions = {
            b'WORD': self.__modify_noop,
            b'BYE': self.__modify_bye,
            b'CONF': self.__modify_noop,
        }
        try:
            function = modifier_functions[verb.upper()]
            (verb, arg) = function(verb, arg)
        except KeyError:
            pass

        return verb + b' ' + arg + b'\r\n'

    def set_state_for_next_request(self, message):
        if self.want_data and message.lower().startswith(b'354 '):
            self.safe_to_modify = False
        else:
            self.safe_to_modify = True
