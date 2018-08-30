import os

from ioproxy.buffer_list import FileDescriptorBufferList, StringBufferList
from ioproxy.smtp.requests import SMTPRequests
from ioproxy.smtp.responses import SMTPResponses
from ioproxy.proxy import Proxy

from ioproxy.input import FileDescriptorInput
from ioproxy.output import FileDescriptorOutput


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
        self.requests.report_messages(self.responses.set_state_for_next_response)
        self.responses.report_messages(self.requests.set_state_for_next_request)
        self.proxy = Proxy(FileDescriptorBufferList([self.requests, self.responses]))

    def strangle(self, read_size, command_line_arguments):
        if self.child_process_id:
            self.proxy.proxy(read_size)
            self.proxy.exit(self.child_process_id)
        else:
            os.dup2(self.from_proxy, self.from_client_input_source.input_fd)
            os.dup2(self.to_proxy, self.to_client_output_source.output_fd)

            program_to_strangle = command_line_arguments[0]
            try:
                os.execvp(program_to_strangle, command_line_arguments)
            except OSError as o:
                self.logger.log(program_to_strangle + ': ' + o.strerror + '\r\n')


class SMTPStringStrangler:
    def __init__(self, logger, from_client_input_source, to_server_output_source, from_server_input_source, to_client_output_source):
        self.logger = logger
        (self.from_client_input_source, self.to_client_output_source) = (from_client_input_source, to_client_output_source)
        (self.from_server_input_source, self.to_server_output_source) = (from_server_input_source, to_server_output_source)

        self.requests = SMTPRequests(logger, from_client_input_source, self.to_server_output_source)
        self.responses = SMTPResponses(logger, self.from_server_input_source, self.to_client_output_source)
        self.requests.report_messages(self.responses.set_state_for_next_response)
        self.responses.report_messages(self.requests.set_state_for_next_request)
        self.proxy = Proxy(StringBufferList([self.requests, self.responses]))

    def strangle(self, read_size, command_line_arguments):
        self.proxy.proxy(read_size)
