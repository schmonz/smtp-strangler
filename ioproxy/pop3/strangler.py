from ioproxy.abstract_strangler import AbstractStrangler
from ioproxy.buffer_list import FileDescriptorBufferList, StringBufferList
from ioproxy.pop3.requests import POP3Requests
from ioproxy.pop3.responses import POP3Responses
from ioproxy.proxy import Proxy


class AbstractPOP3Strangler(AbstractStrangler):
    def __init__(self, logger, from_client_input_source, to_client_output_source):
        AbstractStrangler.__init__(self, logger, from_client_input_source, to_client_output_source)

        self.requests = POP3Requests(logger, from_client_input_source, self.to_server_output_source)
        self.responses = POP3Responses(logger, self.from_server_input_source, self.to_client_output_source)
        self.requests.report_messages(self.responses.receive_message)


class POP3FileDescriptorStrangler(AbstractPOP3Strangler):
    def __init__(self, logger, from_client_input_source, to_client_output_source):
        AbstractPOP3Strangler.__init__(self, logger, from_client_input_source, to_client_output_source)
        self.proxy = Proxy(FileDescriptorBufferList([self.requests, self.responses]))


class POP3StringStrangler(AbstractPOP3Strangler):
    def __init__(self, logger, from_client_input_source, to_client_output_source):
        AbstractPOP3Strangler.__init__(self, logger, from_client_input_source, to_client_output_source)
        self.proxy = Proxy(StringBufferList([self.requests, self.responses]))
