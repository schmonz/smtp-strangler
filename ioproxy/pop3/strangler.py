from ioproxy.abstract_strangler import AbstractStrangler
from ioproxy.pop3.requests import POP3Requests
from ioproxy.pop3.responses import POP3Responses
from ioproxy.proxy import Proxy


class POP3Strangler(AbstractStrangler):
    def __init__(self, logger, from_client_input_source, to_client):
        AbstractStrangler.__init__(self, logger, from_client_input_source, to_client)

        requests = POP3Requests(logger, from_client_input_source, self.to_server)
        responses = POP3Responses(logger, self.from_server_input_source, self.to_client)
        requests.report_messages(responses.receive_message)
        self.proxy = Proxy([requests, responses])
