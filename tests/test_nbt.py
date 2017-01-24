# coding: utf-8

import binascii
import unittest

from tornado_smb.nbt import (
    NBName, NBNSNameQueryRequest, NB_NAME_PURPOSE_WORKSTATION,
)


class NBNameTestCase(unittest.TestCase):

    def test_to_str(self):
        testee = NBName("Neko")
        self.assertEqual(str(testee), "NEKO<00>")

    def test_to_str_with_scope(self):
        testee = NBName("Neko", "cat.org")
        self.assertEqual(str(testee), "NEKO<00>.CAT.ORG")

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

    def test_decode_word(self):
        result = NBName.decode_word(ord('E'), ord('O'))
        self.assertEqual(result, b'N')

    def test_decode_bytes(self):
        result = NBName.decode_bytes(
            b"EOEFELEPCACACACACACACACACACACAAA"
        )
        self.assertEqual(
            result,
            b"NEKO           \x00"
        )

    def test_decode_value_and_purpose(self):
        value, purpose = NBName.decode_value_and_purpose(
            b"NEKO           \x00"
        )
        self.assertEqual(value, "NEKO")
        self.assertEqual(purpose, NB_NAME_PURPOSE_WORKSTATION)

    def test_decode_scope(self):
        result = NBName.decode_scope(
            b"\x03CAT\x03ORG"
        )
        self.assertEqual(
            result,
            "CAT.ORG"
        )

    def test_from_bytes(self):
        testee = NBName.from_bytes(
            b"\x20EOEFELEPCACACACACACACACACACACAAA\x03CAT\x03ORG\x00"
        )
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
