import os

from ioproxy.abstract_strangler import AbstractStrangler
from ioproxy.input_source import FileDescriptorInputSource
from ioproxy.smtp.requests import SMTPRequests
from ioproxy.smtp.responses import SMTPResponses
from ioproxy.proxy import Proxy


class SMTPStrangler(AbstractStrangler):
    def __init__(self, logger, from_client, to_client):
        AbstractStrangler.__init__(self, logger, from_client, to_client)
        requests = SMTPRequests(logger, FileDescriptorInputSource(self.from_client), self.to_server)
        responses = SMTPResponses(logger, FileDescriptorInputSource(self.from_server), self.to_client)
        requests.report_messages(responses.receive_message)
        responses.report_messages(requests.receive_message)
        self.proxy = Proxy([requests, responses])
