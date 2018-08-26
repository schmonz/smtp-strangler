import os

from ioproxy.buffer_list import FileDescriptorBufferList, StringBufferList
from ioproxy.smtp.requests import SMTPRequests
from ioproxy.smtp.responses import SMTPResponses
from ioproxy.proxy import Proxy

from ioproxy.input import FileDescriptorInput
from ioproxy.output import FileDescriptorOutput
from ioproxy.proxied import Proxied


class SMTPFileDescriptorStrangler:
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

        self.requests = SMTPRequests(logger, from_client_input_source, self.to_server_output_source)
        self.responses = SMTPResponses(logger, self.from_server_input_source, self.to_client_output_source)
        self.requests.report_messages(self.responses.receive_message)
        self.responses.report_messages(self.requests.receive_message)
        self.proxy = Proxy(FileDescriptorBufferList([self.requests, self.responses]))

    def strangle(self, read_size, command_line_arguments):
        if self.child_process_id:
            self.proxy.proxy(read_size)
            self.proxy.exit(self.child_process_id)
        else:
            Proxied(
                self.from_client_input_source.input_fd, self.to_proxy,
                self.from_proxy, self.to_client_output_source.output_fd,
            ).exec_and_exit(self.logger, command_line_arguments)


class SMTPStringStrangler:
    def __init__(self, logger, from_client_input_source, to_server_output_source, from_server_input_source, to_client_output_source):
        self.logger = logger
        (self.from_client_input_source, self.to_client_output_source) = (from_client_input_source, to_client_output_source)
        (self.from_server_input_source, self.to_server_output_source) = (from_server_input_source, to_server_output_source)

        self.requests = SMTPRequests(logger, from_client_input_source, self.to_server_output_source)
        self.responses = SMTPResponses(logger, self.from_server_input_source, self.to_client_output_source)
        self.requests.report_messages(self.responses.receive_message)
        self.responses.report_messages(self.requests.receive_message)
        self.proxy = Proxy(StringBufferList([self.requests, self.responses]))

    def strangle(self, read_size, command_line_arguments):
        self.proxy.proxy(read_size)
