#!/usr/bin/env python

import unittest

from ioproxy.input import StringInput
from ioproxy.logger import NullLogger
from ioproxy.output import StringOutput
from ioproxy.smtp.strangler import SMTPStringStrangler

GENEROUS_READ_LENGTH = 5000


class TestStrangler(unittest.TestCase):
    @unittest.skip('soon')
    def test_BRXT_is_same_as_QUIT(self):
        request = StringInput(b'BRXT plz\r\n')
        request_instead = StringOutput()
        strangler = SMTPStringStrangler(NullLogger(), request, request_instead, None, None)

        strangler.requests.read(GENEROUS_READ_LENGTH)
        strangler.requests.send()

        self.assertEqual(b'QUIT plz\r\n', request_instead.output_string)

    @unittest.skip('soon')
    def test_CONF_gives_success_code_and_url(self):
        request = StringInput(b'CONF\r\n')
        request_instead = StringOutput()
        response = StringInput(b'777 incredibly fake server response\r\n')
        response_instead = StringOutput()
        strangler = SMTPStringStrangler(NullLogger(), request, request_instead, response, response_instead)

        strangler.requests.read(GENEROUS_READ_LENGTH)
        strangler.requests.send()

        self.assertEqual(b'NOOP CONF \r\n', request_instead.output_string)

        strangler.responses.read(GENEROUS_READ_LENGTH)
        strangler.responses.send()

        self.assertEqual(b'250 https://www.spaconference.org/spa2018/\r\n', response_instead.output_string)

    @unittest.skip('soon')
    def test_EHLO_includes_gdpr_notice(self):
        # XXX server response does not include '250 GDPR 20160414'
        # XXX proxy response does
        self.fail('not yet implemented: GDPR capability')

    @unittest.skip('soon')
    def test_reject_mail_from_tim(self):
        # XXX when MAIL FROM: tim,
        # XXX request becomes NOOP
        # XXX response becomes '553 no thank you'
        self.fail('not yet implemented: rejecting mail from Tim')

    # More ideas:
    #
    # - Log `MAIL FROM` and `RCPT TO` parameters, with a timestamp
    # - Also log whether the server accepted or rejected
    # - Log to SQLite instead of stderr


if __name__ == '__main__':
    unittest.main()
