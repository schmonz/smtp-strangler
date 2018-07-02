import os

from ioproxy.proxy import ProtocolProxy
from ioproxy.proxied import ProtocolProxied
from ioproxy.protocols.smtp.requests import SMTPRequests
from ioproxy.protocols.smtp.responses import SMTPResponses


# XXX generalize to ProtocolStrangler
class SMTPStrangler:
    def __init__(self, from_client, to_client):
        (self.from_client, self.to_client) = (from_client, to_client)
        (self.from_proxy, self.to_server) = os.pipe()
        (self.from_server, self.to_proxy) = os.pipe()
        self.child_process_id = os.fork()
        if self.child_process_id:
            os.close(self.from_proxy)
            os.close(self.to_proxy)
        else:
            os.close(self.from_server)
            os.close(self.to_server)

    def strangle_and_exit(self, logger, command_line_arguments):
        if self.child_process_id:
            # XXX pass in as params (or maybe implement in SMTP subclass)
            requests = SMTPRequests(logger, self.from_client, self.to_server)
            responses = SMTPResponses(logger, self.from_server, self.to_client)
            requests.report_messages(responses.receive_message)
            responses.report_messages(requests.receive_message)
            proxy = ProtocolProxy([
                requests,
                responses,
            ])
            proxy.proxy_and_exit(self.child_process_id, 77)
        else:
            ProtocolProxied(
                self.from_client, self.to_proxy,
                self.from_proxy, self.to_client,
            ).exec_and_exit(logger, command_line_arguments)
