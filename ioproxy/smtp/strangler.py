from ioproxy.abstract_strangler import AbstractStrangler
from ioproxy.buffer_list import FileDescriptorBufferList
from ioproxy.smtp.requests import SMTPRequests
from ioproxy.smtp.responses import SMTPResponses
from ioproxy.proxy import Proxy


class SMTPStrangler(AbstractStrangler):
    def __init__(self, logger, from_client_input_source, to_client_output_source):
        AbstractStrangler.__init__(self, logger, from_client_input_source, to_client_output_source)
        requests = SMTPRequests(logger, from_client_input_source, self.to_server_output_source)
        responses = SMTPResponses(logger, self.from_server_input_source, self.to_client_output_source)
        requests.report_messages(responses.receive_message)
        responses.report_messages(requests.receive_message)
        self.proxy = Proxy(FileDescriptorBufferList([requests, responses]))
