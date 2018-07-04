from ioproxy.abstract_strangler import AbstractFileDescriptorStrangler, AbstractStringStrangler
from ioproxy.buffer_list import FileDescriptorBufferList, StringBufferList
from ioproxy.pop3.requests import POP3Requests
from ioproxy.pop3.responses import POP3Responses
from ioproxy.proxy import Proxy


class POP3FileDescriptorStrangler(AbstractFileDescriptorStrangler):
    def __init__(self, logger, from_client_input_source, to_client_output_source):
        AbstractFileDescriptorStrangler.__init__(self, logger, from_client_input_source, to_client_output_source)
        self.requests = POP3Requests(logger, from_client_input_source, self.to_server_output_source)
        self.responses = POP3Responses(logger, self.from_server_input_source, self.to_client_output_source)
        self.requests.report_messages(self.responses.receive_message)
        self.proxy = Proxy(FileDescriptorBufferList([self.requests, self.responses]))


class POP3StringStrangler(AbstractStringStrangler):
    def __init__(self, logger, from_client_input_source, to_client_output_source):
        AbstractStringStrangler.__init__(self, logger, from_client_input_source, to_client_output_source)
        self.requests = POP3Requests(logger, from_client_input_source, self.to_server_output_source)
        self.responses = POP3Responses(logger, self.from_server_input_source, self.to_client_output_source)
        self.requests.report_messages(self.responses.receive_message)
        self.proxy = Proxy(StringBufferList([self.requests, self.responses]))
