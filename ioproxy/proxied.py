import os


class ProtocolProxied:
    def __init__(self, from_client, to_proxy, from_proxy, to_client):
        os.dup2(from_proxy, from_client)
        os.dup2(to_proxy, to_client)

    def exec_and_exit(self, logger, command_line_arguments):
        program_to_strangle = command_line_arguments[0]
        try:
            os.execvp(program_to_strangle, command_line_arguments)
        except OSError as o:
            logger.log(program_to_strangle + ': ' + o.strerror + '\r\n')
