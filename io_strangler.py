#!/usr/bin/env python

import os
import sys

from ioproxy.logger import Logger
from ioproxy.strangler_factory import StranglerFactory


def die_usage(logger):
    this_program = os.path.basename(sys.argv[0]).encode('ASCII')
    logger.log(b'usage: ' + this_program + b' <pop3|smtp>' +
               b' program-to-strangle [ arg ... ]\r\n')
    sys.exit(99)


def die_interrupt(logger):
    logger.log(b'[interrupted]\r\n')
    sys.exit(0)


def main(command_line_arguments):
    logger = Logger(sys.stderr.fileno())

    if not command_line_arguments:
        die_usage(logger)
    protocol = command_line_arguments.pop(0)
    if not command_line_arguments:
        die_usage(logger)

    try:
        StranglerFactory(
            logger,
            sys.stdin.fileno(),
            sys.stdout.fileno(),
        ).create(protocol).strangle(77, command_line_arguments)
    except KeyError:
        die_usage(logger)
    except KeyboardInterrupt:
        die_interrupt(logger)


if '__main__' == __name__:
    main(sys.argv[1:])
