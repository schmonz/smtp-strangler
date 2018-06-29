import os


class ProtocolLinesIn:
    def __init__(self, logger, read_from_fd, write_to_fd):
        self.logger = logger
        self.__read_from_fd = read_from_fd
        self.__write_to_fd = write_to_fd

        self.__bytes = b''
        self.__protocol_message = b''
        self.__protocol_messages = []

        self.report_message_callback = None

    def __accumulate(self, some_bytes):
        self.__bytes += some_bytes
        while b'\n' in self.__bytes:
            (line, self.__bytes) = self.__extract_first_line(self.__bytes)
            self.__protocol_message += line
            if self.is_last_line_of_protocol_message(line):
                self.__protocol_messages.append(self.__protocol_message)
                self.__protocol_message = b''

    @staticmethod
    def __extract_first_line(possibly_multiline):
        (first_line, leftovers) = possibly_multiline.split(b'\n', 1)
        first_line += b'\n'
        return (first_line, leftovers)

    def close(self):
        os.close(self.get_write_fd())

    @staticmethod
    def get_log_prefix():
        return b'protocol-line>'

    def get_read_fd(self):
        return self.__read_from_fd

    def get_write_fd(self):
        return self.__write_to_fd

    def has_whole_message(self):
        return len(self.__protocol_messages) > 0

    def is_last_line_of_protocol_message(self, line):
        return True

    def log_disconnect(self):
        self.logger.log(b'[protocol-line dropped connection]\r\n')

    def munge_message(self, message):
        return message

    def read(self, read_length):
        some_bytes = os.read(self.__read_from_fd, read_length)
        if some_bytes:
            self.__accumulate(some_bytes)
            return True
        else:
            self.log_disconnect()
            return False

    def report_messages(self, callback):
        self.report_message_callback = callback

    def send(self):
        message = self.__protocol_messages.pop(0)
        self.logger.log(b'       ' + self.get_log_prefix() +
                        b' ' + message)
        munged_message = self.munge_message(message)
        self.logger.log(b'munged-' + self.get_log_prefix() +
                        b' ' + munged_message + b'\r\n')
        os.write(self.__write_to_fd, munged_message)


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


class SMTPResponses(ProtocolLinesIn):
    def __init__(self, logger, read_from_fd, write_to_fd):
        ProtocolLinesIn.__init__(self, logger, read_from_fd, write_to_fd)
        self.__should_munge_ehlo = False
        self.safe_to_munge = True

    @staticmethod
    def __munge_ehlo(message):
        return message + b'250 GDPR 20160414\r\n'

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
        os.close(self.get_read_fd())

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

    def is_last_line_of_protocol_message(self, line):
        return len(line) >= 4 and self.__is_one_ordinary_space(line[3])

    def log_disconnect(self):
        self.logger.log(b'[server dropped connection]\r\n')

    def munge_message(self, message):
        if self.report_message_callback:
            self.report_message_callback(message)

        if not self.safe_to_munge:
            return message

        if self.__should_munge_ehlo:
            message = self.__munge_ehlo(message)
            self.__should_munge_ehlo = False

        message = self.__reformat_multiline_response(message)
        return message

    def receive_message(self, message):
        (verb, arg) = SMTPRequestParser(message).get_verb_and_arg()

        if verb.lower() == b'ehlo':
            self.__should_munge_ehlo = True


class SMTPRequestParser:
    def __init__(self, request):
        self.request = request
        request = request.rstrip(b'\r\n')
        try:
            (self.verb, self.arg) = request.split(b' ', 1)
        except ValueError:
            (self.verb, self.arg) = (request, b'')

    def get_verb_and_arg(self):
        return (self.verb, self.arg)
