from ioproxy.abstract_strangler import AbstractStrangler
from ioproxy.buffer_list import FileDescriptorBufferList
from ioproxy.pop3.requests import POP3Requests
from ioproxy.pop3.responses import POP3Responses
from ioproxy.proxy import Proxy


class POP3Strangler(AbstractStrangler):
    def __init__(self, logger, from_client_input_source, to_client_output_source):
        AbstractStrangler.__init__(self, logger, from_client_input_source, to_client_output_source)

        requests = POP3Requests(logger, from_client_input_source, self.to_server_output_source)
        responses = POP3Responses(logger, self.from_server_input_source, self.to_client_output_source)
        requests.report_messages(responses.receive_message)
        self.proxy = Proxy(FileDescriptorBufferList([requests, responses]))
