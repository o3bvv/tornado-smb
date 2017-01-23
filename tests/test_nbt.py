# coding: utf-8

import binascii
import unittest

from tornado_smb.nbt import NBName, NBNSNameQueryRequest


class NBNameTestCase(unittest.TestCase):

    def test_encode_byte(self):
        self.assertEqual(
            NBName.encode_byte(0),
            b"AA"
        )
        self.assertEqual(
            NBName.encode_byte(ord(' ')),
            b"CA"
        )

    def test_to_bytes(self):
        testee = NBName("Neko")
        self.assertEqual(
            testee.to_bytes(),
            b"\x20EOEFELEPCACACACACACACACACACACAAA\x00"
        )

    def test_to_bytes_wildcard(self):
        testee = NBName("*")
        self.assertEqual(
            testee.to_bytes(),
            b"\x20CKAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\x00"
        )

    def test_to_bytes_with_scope(self):
        testee = NBName("Neko", "cat.org")
        self.assertEqual(
            testee.to_bytes(),
            b"\x20EOEFELEPCACACACACACACACACACACAAA\x03CAT\x03ORG\x00"
        )

    def test_to_str(self):
        testee = NBName("Neko")
        self.assertEqual(str(testee), "NEKO<00>")

    def test_to_str_with_scope(self):
        testee = NBName("Neko", "cat.org")
        self.assertEqual(str(testee), "NEKO<00>.CAT.ORG")


class NBNSNameQueryRequestTestCase(unittest.TestCase):

    def test_to_bytes(self):
        testee = NBNSNameQueryRequest(
            name_trn_id=1964,
            question_name=NBName("neko", "cat.org").to_bytes(),
            broadcast=True,
        )
        data = testee.to_bytes()
        self.assertEqual(
            binascii.hexlify(data).decode(),
            (
                "07ac0110000100000000000020454f4546454c4550434143414341434143"
                "41434143414341434143414341414103434154034f52470000200001"
            )
        )
