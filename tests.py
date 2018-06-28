#!/usr/bin/env python

from smtp_strangler import ProtocolLogger, SMTPRequests

import unittest

class TestStrangler(unittest.TestCase):

    def test_whole_request(self):
        requests = SMTPRequests(ProtocolLogger(-1), -2, -3)
        self.assertEqual(1, 1)

if __name__ == '__main__':
    unittest.main()
