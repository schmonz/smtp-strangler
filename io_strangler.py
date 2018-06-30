#!/usr/bin/env python

import os
import sys

from ioproxy.logger import ProtocolLogger
from ioproxy.protocols.pop3.strangler import POP3ProtocolStrangler


def die_usage(logger):
    this_program = os.path.basename(sys.argv[0]).encode('ASCII')
    logger.log(b'usage: ' + this_program +
               b' program-to-strangle [ arg ... ]\r\n')
    sys.exit(99)


def die_interrupt(logger):
    logger.log(b'[interrupted]\r\n')
    sys.exit(0)


def main(command_line_arguments):
    logger = ProtocolLogger(sys.stderr.fileno())

    if not command_line_arguments:
        die_usage(logger)

    try:
        POP3ProtocolStrangler(
            sys.stdin.fileno(),
            sys.stdout.fileno(),
        ).strangle_and_exit(logger, command_line_arguments)
    except KeyboardInterrupt:
        die_interrupt(logger)


if '__main__' == __name__:
    main(sys.argv[1:])
