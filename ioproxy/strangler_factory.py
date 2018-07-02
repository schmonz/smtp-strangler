from ioproxy.pop3.strangler import POP3Strangler
from ioproxy.smtp.strangler import SMTPStrangler


class StranglerFactory:
    def __init__(self, logger, input_fd, output_fd):
        self.logger = logger
        self.input_fd = input_fd
        self.output_fd = output_fd

    def find_strangler(self, protocol):
        strangler_for = {
            'POP3': POP3Strangler,
            'SMTP': SMTPStrangler,
        }

        return strangler_for[protocol.upper()](
            self.logger,
            self.input_fd,
            self.output_fd,
        )