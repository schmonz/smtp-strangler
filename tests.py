#!/usr/bin/env python

import unittest


class TestStrangler(unittest.TestCase):

    @unittest.skip('not yet implemented: BRXT')
    def test_BRXT_is_same_as_QUIT(self):
        # XXX request becomes QUIT
        self.fail('not yet implemented: BRXT')

    @unittest.skip('not yet implemented: CONF')
    def test_CONF_gives_success_code_and_url(self):
        # XXX request becomes NOOP
        # XXX response becomes '250 https://www.spaconference.org/spa2018/'
        self.fail('not yet implemented: CONF')

    @unittest.skip('not yet implemented: GDPR capability')
    def test_EHLO_includes_gdpr_notice(self):
        # XXX server response does not include '250 GDPR 20160414'
        # XXX proxy response does
        self.fail('not yet implemented: GDPR capability')

    @unittest.skip('not yet implemented: rejecting mail from Tim')
    def test_reject_mail_from_tim(self):
        # XXX when MAIL FROM: tim,
        # XXX request becomes NOOP
        # XXX response becomes '553 no thank you'
        self.fail('not yet implemented: rejecting mail from Tim')


if __name__ == '__main__':
    unittest.main()

# More ideas:
#
# - Log `MAIL FROM` and `RCPT TO` parameters, with a timestamp
# - Also log whether the server accepted or rejected
# - Log to SQLite instead of stderr
