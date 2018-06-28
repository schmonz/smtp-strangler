#!/usr/bin/env python

import os
import sys

from protocol_logger import ProtocolLogger
from protocol_strangler import SMTPProtocolStrangler


def die_usage(logger):
    this_program = os.path.basename(sys.argv[0]).encode('ASCII')
    logger.log(b'usage: ' + this_program +
               b' program-to-strangle [ arg ... ]\r\n')
    sys.exit(99)


def main(command_line_arguments):
    logger = ProtocolLogger(sys.stderr.fileno())

    if not command_line_arguments:
        die_usage(logger)

    SMTPProtocolStrangler(
        sys.stdin.fileno(),
        sys.stdout.fileno(),
    ).strangle_and_exit(logger, command_line_arguments)


if '__main__' == __name__:
    main(sys.argv[1:])
