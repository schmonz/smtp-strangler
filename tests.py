#!/usr/bin/env python

import unittest

from ioproxy.input import StringInput
from ioproxy.logger import NoLogging
from ioproxy.output import StringOutput
from ioproxy.smtp.strangler import SMTPStringStrangler

GENEROUS_READ_LENGTH = 5000


class TestStrangler(unittest.TestCase):
    def test_brxt_means_quit(self):
        request = StringInput(b'BRXT plz\r\n')
        request_instead = StringOutput()
        strangler = SMTPStringStrangler(NoLogging(), request, request_instead, None, None)

        strangler.requests.read(GENEROUS_READ_LENGTH)
        strangler.requests.send()

        self.assertEqual(b'QUIT plz\r\n', request_instead.output_string)

    @unittest.skip('soon')
    def test_conf_gives_conference_url(self):
        request = StringInput(b'CONF\r\n')
        request_instead = StringOutput()
        response = StringInput(b'777 incredibly fake server response\r\n')
        response_instead = StringOutput()
        strangler = SMTPStringStrangler(NoLogging(), request, request_instead, response, response_instead)

        strangler.requests.read(GENEROUS_READ_LENGTH)
        strangler.requests.send()

        self.assertEqual(b'NOOP CONF \r\n', request_instead.output_string)

        strangler.responses.read(GENEROUS_READ_LENGTH)
        strangler.responses.send()

        self.assertEqual(b'250 https://www.spaconference.org/spa2018/\r\n', response_instead.output_string)

    @unittest.skip('soon')
    def test_ehlo_response_includes_gdpr_capability(self):
        request = StringInput(b'EHLO\r\n')
        response = StringInput(b'250-very.plausible.server\r\n250-SINGING\r\n250 DANCING\r\n')
        response_instead = StringOutput()
        expected_response_instead = b'250-very.plausible.server\r\n250-SINGING\r\n250-DANCING\r\n250 GDPR 20160414\r\n'
        strangler = SMTPStringStrangler(NoLogging(), request, StringOutput(), response, response_instead)

        strangler.requests.read(GENEROUS_READ_LENGTH)
        strangler.requests.send()
        strangler.responses.read(GENEROUS_READ_LENGTH)
        strangler.responses.send()

        self.assertEqual(expected_response_instead, response_instead.output_string)

    @unittest.skip('soon')
    def test_reject_mail_from_tim(self):
        request = StringInput(b'MAIL FROM: tim\r\n')
        request_instead = StringOutput()
        response = StringInput(b'250 ok\r\n')
        response_instead = StringOutput()
        strangler = SMTPStringStrangler(NoLogging(), request, request_instead, response, response_instead)

        strangler.requests.read(GENEROUS_READ_LENGTH)
        strangler.requests.send()

        expected_request_instead = b'NOOP MAIL FROM: tim\r\n'
        self.assertEqual(expected_request_instead, request_instead.output_string)

        strangler.responses.read(GENEROUS_READ_LENGTH)
        strangler.responses.send()

        expected_response_instead = b'553 sorry, your envelope sender is in my badmailfrom list (#5.7.1)\r\n'
        self.assertEqual(expected_response_instead, response_instead.output_string)


if __name__ == '__main__':
    unittest.main()

# More ideas:
#
# - Log `MAIL FROM` and `RCPT TO` parameters, with a timestamp
# - Also log whether the server accepted or rejected
# - Log to SQLite instead of stderr
