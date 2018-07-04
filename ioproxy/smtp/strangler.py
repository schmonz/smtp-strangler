from ioproxy.abstract_strangler import AbstractFileDescriptorStrangler, AbstractStringStrangler
from ioproxy.buffer_list import FileDescriptorBufferList, StringBufferList
from ioproxy.smtp.requests import SMTPRequests
from ioproxy.smtp.responses import SMTPResponses
from ioproxy.proxy import Proxy


class SMTPFileDescriptorStrangler(AbstractFileDescriptorStrangler):
    def __init__(self, logger, from_client_input_source, to_client_output_source):
        AbstractFileDescriptorStrangler.__init__(self, logger, from_client_input_source, to_client_output_source)
        self.requests = SMTPRequests(logger, from_client_input_source, self.to_server_output_source)
        self.responses = SMTPResponses(logger, self.from_server_input_source, self.to_client_output_source)
        self.requests.report_messages(self.responses.receive_message)
        self.responses.report_messages(self.requests.receive_message)
        self.proxy = Proxy(FileDescriptorBufferList([self.requests, self.responses]))


class SMTPStringStrangler(AbstractStringStrangler):
    def __init__(self, logger, from_client_input_source, to_server_output_source, from_server_input_source, to_client_output_source):
        AbstractStringStrangler.__init__(self, logger, from_client_input_source, to_server_output_source, from_server_input_source, to_client_output_source)
        self.requests = SMTPRequests(logger, from_client_input_source, self.to_server_output_source)
        self.responses = SMTPResponses(logger, self.from_server_input_source, self.to_client_output_source)
        self.requests.report_messages(self.responses.receive_message)
        self.responses.report_messages(self.requests.receive_message)
        self.proxy = Proxy(StringBufferList([self.requests, self.responses]))
