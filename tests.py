#!/usr/bin/env python

import unittest

from ioproxy.input import StringInput
from ioproxy.logger import NullLogger
from ioproxy.output import StringOutput
from ioproxy.smtp.strangler import SMTPStringStrangler


class TestStrangler(unittest.TestCase):
    def test_BRXT_is_same_as_QUIT(self):
        input = StringInput(b'BRXT plz\r\n')
        output = StringOutput()
        strangler = SMTPStringStrangler(NullLogger(), input, output, None, None)

        strangler.requests.read(77)
        strangler.requests.send()

        self.assertEqual(b'QUIT plz\r\n', output.output_string)

    # def test_CONF_gives_success_code_and_url(self):
    #     # XXX request becomes NOOP
    #     # XXX response becomes '250 https://www.spaconference.org/spa2018/'
    #     self.fail('not yet implemented: CONF')
    #
    # def test_EHLO_includes_gdpr_notice(self):
    #     # XXX server response does not include '250 GDPR 20160414'
    #     # XXX proxy response does
    #     self.fail('not yet implemented: GDPR capability')
    #
    # def test_reject_mail_from_tim(self):
    #     # XXX when MAIL FROM: tim,
    #     # XXX request becomes NOOP
    #     # XXX response becomes '553 no thank you'
    #     self.fail('not yet implemented: rejecting mail from Tim')
    #
    # More ideas:
    #
    # - Log `MAIL FROM` and `RCPT TO` parameters, with a timestamp
    # - Also log whether the server accepted or rejected
    # - Log to SQLite instead of stderr


if __name__ == '__main__':
    unittest.main()
