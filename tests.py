#!/usr/bin/env python

from protocol_logger import ProtocolLogger
from protocol_smtp_requests import SMTPRequests
from protocol_smtp_request_parser import SMTPRequestParser

import unittest


class TestStrangler(unittest.TestCase):

    def test_whole_request(self):
        requests = SMTPRequests(ProtocolLogger(-1), -2, -3)
        self.assertEqual(1, 1)

    def test_last_line_of_data(self):
        parser = SMTPRequestParser(b'.\r\n')
        (verb, arg) = parser.get_verb_and_arg()
        self.assertEqual(b'.', verb)


if __name__ == '__main__':
    unittest.main()
