#!/usr/bin/env python

import unittest

from ioproxy.input import StringInput
from ioproxy.logger import DoNothingLogger
from ioproxy.output import StringOutput
from ioproxy.smtp.strangler import SMTPStringStrangler

GENEROUS_READ_LENGTH = 5000


class TestStrangler(unittest.TestCase):
    @unittest.skip('soon')
    def test_bye_means_quit(self):
        request = StringInput(b'BYE plz\r\n')
        request_instead = StringOutput()
        strangler = SMTPStringStrangler(DoNothingLogger(), request, request_instead, None, None)

        strangler.requests.read(GENEROUS_READ_LENGTH)
        strangler.requests.send()

        self.assertEqual(b'QUIT plz\r\n', request_instead.output_string)

    @unittest.skip('soon')
    def test_ehlo_response_includes_gdpr_capability(self):
        request = StringInput(b'EHLO\r\n')
        response = StringInput(b'250-very.plausible.server\r\n' +
                               b'250-SINGING\r\n' +
                               b'250 DANCING\r\n')
        response_instead = StringOutput()
        expected_response_instead = b'250-very.plausible.server\r\n' +\
                                    b'250-SINGING\r\n' +\
                                    b'250-DANCING\r\n'+\
                                    b'250 GDPR 20160414\r\n'
        strangler = SMTPStringStrangler(DoNothingLogger(), request, StringOutput(), response, response_instead)

        strangler.requests.read(GENEROUS_READ_LENGTH)
        strangler.requests.send()
        strangler.responses.read(GENEROUS_READ_LENGTH)
        strangler.responses.send()

        self.assertEqual(expected_response_instead, response_instead.output_string)


if __name__ == '__main__':
    unittest.main()
