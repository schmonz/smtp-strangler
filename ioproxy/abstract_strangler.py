import os

from ioproxy.proxied import Proxied


class AbstractStrangler:
    def __init__(self, logger, from_client, to_client):
        self.logger = logger
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
        self.proxy = None

    def strangle(self, read_size, command_line_arguments):
        if self.child_process_id:
            self.proxy.proxy_and_exit(self.child_process_id, read_size)
        else:
            Proxied(
                self.from_client, self.to_proxy,
                self.from_proxy, self.to_client,
            ).exec_and_exit(self.logger, command_line_arguments)
