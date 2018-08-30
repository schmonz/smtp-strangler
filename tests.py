#!/usr/bin/env python

import unittest

from ioproxy.input import StringInput
from ioproxy.logger import DoNothingLogger
from ioproxy.output import StringOutput
from ioproxy.smtp.strangler import SMTPStringStrangler

GENEROUS_READ_LENGTH = 5000


class TestStrangler(unittest.TestCase):
    @unittest.skip('soon')
    def test_bassd_scho_means_quit(self):
        request = StringInput(b'BASSD scho\r\n')
        request_instead = StringOutput()
        strangler = SMTPStringStrangler(DoNothingLogger(), request, request_instead, None, None)

        strangler.requests.read(GENEROUS_READ_LENGTH)
        strangler.requests.send()

        self.assertEqual(b'QUIT scho\r\n', request_instead.output_string)

    @unittest.skip('soon')
    def test_munich_gives_meetup_url(self):
        request = StringInput(b'MUNICH\r\n')
        request_instead = StringOutput()
        response = StringInput(b'777 incredibly fake server response\r\n')
        response_instead = StringOutput()
        strangler = SMTPStringStrangler(DoNothingLogger(), request, request_instead, response, response_instead)

        strangler.requests.read(GENEROUS_READ_LENGTH)
        strangler.requests.send()

        self.assertEqual(b'NOOP MUNICH \r\n', request_instead.output_string)

        strangler.responses.read(GENEROUS_READ_LENGTH)
        strangler.responses.send()

        self.assertEqual(b'250 https://www.meetup.com/munich-software-craft-community/\r\n', response_instead.output_string)

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

    @unittest.skip('soon')
    def test_reject_mail_from_david(self):
        request = StringInput(b'MAIL FROM: david\r\n')
        request_instead = StringOutput()
        response = StringInput(b'250 ok\r\n')
        response_instead = StringOutput()
        strangler = SMTPStringStrangler(DoNothingLogger(), request, request_instead, response, response_instead)

        strangler.requests.read(GENEROUS_READ_LENGTH)
        strangler.requests.send()

        expected_request_instead = b'NOOP MAIL FROM: david\r\n'
        self.assertEqual(expected_request_instead, request_instead.output_string)

        strangler.responses.read(GENEROUS_READ_LENGTH)
        strangler.responses.send()

        expected_response_instead = b'553 sorry, your envelope sender is in my badmailfrom list (#5.7.1)\r\n'
        self.assertEqual(expected_response_instead, response_instead.output_string)


if __name__ == '__main__':
    unittest.main()
