# coding: utf-8

import unittest

from tornado_smb.nbt import NetBIOSName


class NetBIOSNameTestCase(unittest.TestCase):

    def test_encode_byte(self):
        self.assertEqual(
            NetBIOSName.encode_byte(0),
            b"AA"
        )
        self.assertEqual(
            NetBIOSName.encode_byte(ord(' ')),
            b"CA"
        )

    def test_to_bytes(self):
        testee = NetBIOSName("Neko")
        self.assertEqual(
            testee.to_bytes(),
            b"\x20EOEFELEPCACACACACACACACACACACAAA\x00"
        )

    def test_to_bytes_wildcard(self):
        testee = NetBIOSName("*")
        self.assertEqual(
            testee.to_bytes(),
            b"\x20CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x00"
        )

    def test_to_bytes_with_scope(self):
        testee = NetBIOSName("Neko", "cat.org")
        self.assertEqual(
            testee.to_bytes(),
            b"\x20EOEFELEPCACACACACACACACACACACAAA\x03CAT\x03ORG\x00"
        )

    def test_to_str(self):
        testee = NetBIOSName("Neko")
        self.assertEqual(str(testee), "NEKO<00>")

    def test_to_str_with_scope(self):
        testee = NetBIOSName("Neko", "cat.org")
        self.assertEqual(str(testee), "NEKO<00>.CAT.ORG")
