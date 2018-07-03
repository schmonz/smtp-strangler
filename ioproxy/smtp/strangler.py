from ioproxy.abstract_strangler import AbstractStrangler
from ioproxy.smtp.requests import SMTPRequests
from ioproxy.smtp.responses import SMTPResponses
from ioproxy.proxy import Proxy


class SMTPStrangler(AbstractStrangler):
    def __init__(self, logger, from_client_input_source, to_client):
        AbstractStrangler.__init__(self, logger, from_client_input_source, to_client)
        requests = SMTPRequests(logger, from_client_input_source, self.to_server)
        responses = SMTPResponses(logger, self.from_server_input_source, self.to_client)
        requests.report_messages(responses.receive_message)
        responses.report_messages(requests.receive_message)
        self.proxy = Proxy([requests, responses])
