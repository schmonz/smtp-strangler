import os


class AbstractProtocolMessage:
    def __init__(self, logger, read_from_fd, write_to_fd):
        self.logger = logger
        self.__read_from_fd = read_from_fd
        self.__write_to_fd = write_to_fd

        self.__bytes = b''
        self.__protocol_message = b''
        self.__protocol_messages = []
        self.safe_to_munge = True
        self.line_at_a_time = True

    def __accumulate(self, some_bytes):
        if self.line_at_a_time:
            self.__bytes += some_bytes
            while b'\n' in self.__bytes:
                (line, self.__bytes) = self.__first_line_and_leftovers(self.__bytes)
                self.__protocol_message += line
                if self.is_last_line_of_protocol_message(line):
                    self.__protocol_messages.append(self.__protocol_message)
                    self.__protocol_message = b''
        else:
            self.__protocol_messages.append(self.__protocol_message)
            self.__protocol_message = b''

    @staticmethod
    def __first_line_and_leftovers(possibly_multiline):
        (first_line, leftovers) = possibly_multiline.split(b'\n', 1)
        first_line += b'\n'
        return (first_line, leftovers)

    def get_read_fd(self):
        return self.__read_from_fd

    def get_write_fd(self):
        return self.__write_to_fd

    def has_whole_message(self):
        return len(self.__protocol_messages) > 0

    def read(self, read_length):
        some_bytes = os.read(self.__read_from_fd, read_length)
        if some_bytes:
            self.__accumulate(some_bytes)
            return True
        else:
            self.log_disconnect()
            return False

    def send(self):
        message = self.__protocol_messages.pop(0)
        self.logger.log(b'       ' + self.get_log_prefix() +
                        b' ' + message)
        munged_message = self.munge_message(message)
        self.logger.log(b'munged-' + self.get_log_prefix() +
                        b' ' + munged_message + b'\r\n')
        os.write(self.__write_to_fd, munged_message)


class GenericLinesIn(AbstractProtocolMessage):
    def close(self):
        os.close(self.get_write_fd())

    def is_last_line_of_protocol_message(self, line):
        return True

    @staticmethod
    def get_log_prefix():
        return b'unspecified-request>'

    def log_disconnect(self):
        self.logger.log(b'[client dropped connection]\r\n')

    def munge_message(self, message):
        return message


class GenericLinesOut(AbstractProtocolMessage):
    def close(self):
        os.close(self.get_read_fd())

    def is_last_line_of_protocol_message(self, line):
        return True

    @staticmethod
    def get_log_prefix():
        return b'unspecified-response>'

    def log_disconnect(self):
        self.logger.log(b'[server dropped connection]\r\n')

    def munge_message(self, message):
        return message


class GenericBytesIn(GenericLinesIn):
    def __init__(self, logger, read_from_fd, write_to_fd):
        GenericLinesIn.__init__(self, logger, read_from_fd, write_to_fd)
        self.line_at_a_time = False

    def is_last_line_of_protocol_message(self, line):
        return True

    @staticmethod
    def get_log_prefix():
        return b'unspecified-request-bytes>'

    def log_disconnect(self):
        self.logger.log(b'[client dropped connection]\r\n')

    def munge_message(self, message):
        return message


class GenericBytesOut(GenericLinesOut):
    def __init__(self, logger, read_from_fd, write_to_fd):
        GenericLinesOut.__init__(self, logger, read_from_fd, write_to_fd)
        self.line_at_a_time = False

    def is_last_line_of_protocol_message(self, line):
        return True

    @staticmethod
    def get_log_prefix():
        return b'unspecified-response-bytes>'

    def log_disconnect(self):
        self.logger.log(b'[server dropped connection]\r\n')

    def munge_message(self, message):
        return message


class SMTPRequests(GenericLinesIn):
    def __init__(self, logger, read_from_fd, write_to_fd):
        GenericLinesIn.__init__(self, logger, read_from_fd, write_to_fd)
        self.__want_data = False
        self.__in_data = False
        self.__report_message_callback = None

    def is_last_line_of_protocol_message(self, line):
        # XXX verb only
        if self.safe_to_munge and line.lower() == 'data\r\n':
            self.__want_data = True
        if self.__in_data and line == '.\r\n':
            self.safe_to_munge = True
        return True

    @staticmethod
    def get_log_prefix():
        return b'request>'

    def log_disconnect(self):
        self.logger.log(b'[client dropped connection]\r\n')

    def munge_message(self, message):
        if self.__report_message_callback:
            self.__report_message_callback(message)

        if not self.safe_to_munge:
            return message

        munged_message = message.rstrip(b'\r\n')
        # XXX verb only
        if munged_message.lower().startswith(b'word '):
            munged_message = b'noop ' + munged_message
        munged_message += b'\r\n'
        return munged_message

    def receive_message(self, message):
        if self.__want_data:
            self.__want_data = False
            if message.lower().startswith('354 '):
                self.__in_data = True
            else:
                self.__in_data = False

        if self.__in_data:
            self.safe_to_munge = False
        else:
            self.safe_to_munge = True

    def report_messages(self, callback):
        self.__report_message_callback = callback


class SMTPResponses(GenericLinesOut):
    def __init__(self, logger, read_from_fd, write_to_fd):
        GenericLinesOut.__init__(self, logger, read_from_fd, write_to_fd)
        self.__report_message_callback = None
        self.__should_munge_ehlo = False

    def is_last_line_of_protocol_message(self, line):
        return len(line) >= 4 and ' ' == line[3]

    @staticmethod
    def get_log_prefix():
        return b'response<'

    def log_disconnect(self):
        self.logger.log(b'[server dropped connection]\r\n')

    @staticmethod
    def __munge_ehlo(message):
        return message + '250 GDPR 20160414\r\n'

    @staticmethod
    def __reformat_multiline_response(message):
        reformatted = b''
        lines = message.splitlines(True)
        for line in lines[:-1]:
            reformatted += line[:3] + '-' + line[4:]
        reformatted += lines[-1][:3] + ' ' + lines[-1][4:]
        return reformatted

    def munge_message(self, message):
        if self.__report_message_callback:
            self.__report_message_callback(message)

        if not self.safe_to_munge:
            return message

        if self.__should_munge_ehlo:
            message = self.__munge_ehlo(message)
            self.__should_munge_ehlo = False

        message = self.__reformat_multiline_response(message)
        return message

    def receive_message(self, message):
        try:
            (verb, arg) = message.split(b' ')
        except ValueError:
            (verb, arg) = (message.rstrip(b'\r\n'), b'')

        if verb.lower() == 'ehlo':
            self.__should_munge_ehlo = True

    def report_messages(self, callback):
        self.__report_message_callback = callback
