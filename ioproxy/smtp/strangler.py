from ioproxy.abstract_strangler import AbstractStrangler
from ioproxy.buffer_list import FileDescriptorBufferList, StringBufferList
from ioproxy.output import StringOutput
from ioproxy.smtp.requests import SMTPRequests
from ioproxy.smtp.responses import SMTPResponses
from ioproxy.proxy import Proxy


class AbstractSMTPStrangler(AbstractStrangler):
    def __init__(self, logger, from_client_input_source, to_client_output_source):
        AbstractStrangler.__init__(self, logger, from_client_input_source, to_client_output_source)
        self.requests = SMTPRequests(logger, from_client_input_source, self.to_server_output_source)
        self.responses = SMTPResponses(logger, self.from_server_input_source, self.to_client_output_source)
        self.requests.report_messages(self.responses.receive_message)
        self.responses.report_messages(self.requests.receive_message)


class SMTPFileDescriptorStrangler(AbstractSMTPStrangler):
    def __init__(self, logger, from_client_input_source, to_client_output_source):
        AbstractSMTPStrangler.__init__(self, logger, from_client_input_source, to_client_output_source)
        self.proxy = Proxy(FileDescriptorBufferList([self.requests, self.responses]))


class SMTPStringStrangler(AbstractSMTPStrangler):
    def __init__(self, logger, from_client_input_source, to_client_output_source):
        AbstractSMTPStrangler.__init__(self, logger, from_client_input_source, to_client_output_source)
        self.to_server_output_source = StringOutput()
        self.proxy = Proxy(StringBufferList([self.requests, self.responses]))
