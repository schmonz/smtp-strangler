from ioproxy.input import FileDescriptorInput
from ioproxy.output import FileDescriptorOutput
from ioproxy.pop3.strangler import POP3FileDescriptorStrangler
from ioproxy.smtp.strangler import SMTPFileDescriptorStrangler


class StranglerFactory:
    def __init__(self, logger, input_fd, output_fd):
        self.logger = logger
        self.input_source = FileDescriptorInput(input_fd)
        self.output_source = FileDescriptorOutput(output_fd)

    def create(self, protocol):
        strangler_for = {
            'POP3': POP3FileDescriptorStrangler,
            'SMTP': SMTPFileDescriptorStrangler,
        }

        return strangler_for[protocol.upper()](
            self.logger,
            self.input_source,
            self.output_source,
        )
