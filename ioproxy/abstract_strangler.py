import os

from ioproxy.input import FileDescriptorInput
from ioproxy.output import FileDescriptorOutput
from ioproxy.proxied import Proxied


class AbstractStrangler:
    def __init__(self, logger, from_client_input_source, to_client_output_source):
        self.logger = logger
        (self.from_client_input_source, self.to_client_output_source) = (from_client_input_source, to_client_output_source)
        (self.from_proxy, to_server) = os.pipe()
        self.to_server_output_source = FileDescriptorOutput(to_server)
        (from_server, self.to_proxy) = os.pipe()
        self.from_server_input_source = FileDescriptorInput(from_server)
        self.child_process_id = os.fork()
        if self.child_process_id:
            os.close(self.from_proxy)
            os.close(self.to_proxy)
        else:
            os.close(from_server)
            os.close(to_server)
        self.proxy = None

    def strangle(self, read_size, command_line_arguments):
        if self.child_process_id:
            self.proxy.proxy_and_exit(self.child_process_id, read_size)
        else:
            Proxied(
                self.from_client_input_source.input_fd, self.to_proxy,
                self.from_proxy, self.to_client_output_source.output_fd,
            ).exec_and_exit(self.logger, command_line_arguments)
