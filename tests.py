#!/usr/bin/env python

from ioproxy.logger import Logger
from ioproxy.smtp.requests import SMTPRequests
from ioproxy.smtp.request_parser import SMTPRequestParser

import unittest


class TestStrangler(unittest.TestCase):

    def test_whole_request(self):
        requests = SMTPRequests(Logger(-1), -2, -3)
        self.assertEqual(1, 1)

    def test_last_line_of_data(self):
        parser = SMTPRequestParser(b'.\r\n')
        (verb, arg) = parser.get_verb_and_arg()
        self.assertEqual(b'.', verb)
        self.assertEqual(b'', arg)

    def test_munge_last_line_of_data(self):
        requests = SMTPRequests(Logger(-1), -2, -3)
        requests.safe_to_munge = False
        last_line_of_data = b'.\r\n'
        munged = requests.munge_message(last_line_of_data)
        self.assertEqual(last_line_of_data, munged)

    def test_verb_no_arg(self):
        parser = SMTPRequestParser(b'BRXT\r\n')
        (verb, arg) = parser.get_verb_and_arg()
        self.assertEqual(b'BRXT', verb)


if __name__ == '__main__':
    unittest.main()
