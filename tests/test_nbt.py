# coding: utf-8

import unittest

from tornado_smb.nbt import NetBIOSName


class NetBIOSNameTestCase(unittest.TestCase):

    def test_encode_char(self):
        self.assertEqual(
            NetBIOSName.encode_char(' '),
            b"CA"
        )

    def test_to_bytes(self):
        testee = NetBIOSName("Neko")
        self.assertEqual(
            testee.to_bytes(),
            b"\x20EOGFGLGPCACACACACACACACACACACACA\x00"
        )

    def test_to_bytes_with_scope(self):
        testee = NetBIOSName("Neko", "cat.org")
        self.assertEqual(
            testee.to_bytes(),
            b"\x20EOGFGLGPCACACACACACACACACACACACA\x03CAT\x03ORG\x00"
        )

    def test_to_str(self):
        testee = NetBIOSName("Neko")
        self.assertEqual(str(testee), "Neko")

    def test_to_str_with_scope(self):
        testee = NetBIOSName("Neko", "cat.org")
        self.assertEqual(str(testee), "Neko.CAT.ORG")
