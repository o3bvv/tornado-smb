# coding: utf-8

import binascii
import socket
import unittest

from tornado_smb.nbt import NB_NAME_PURPOSE_WORKSTATION, NB_NS_NB_FLAGS_ONT_B
from tornado_smb.nbt import (
    NBName, NBNSNameQueryRequest, NBNSNameRegistrationRequest,
    NBNSNameOverwriteDemand, NBNSNegativeNameRegistrationResponse,
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
            q_name=NBName("neko", "cat.org").to_bytes(),
            broadcast=True,
        )
        data = testee.to_bytes()
        self.assertEqual(
            binascii.hexlify(data).decode(),
            (
                "07ac" "0110" "0001" "0000" "0000" "0000" "20454f4546454c4550"
                "434143414341434143414341434143414341434143414141034341"
                "54034f524700" "0020" "0001"
            )
        )


class NBNSNameRegistrationRequestTestCase(unittest.TestCase):

    def test_to_bytes(self):
        testee = NBNSNameRegistrationRequest(
            name_trn_id=1964,
            q_name=NBName("neko").to_bytes(),
            nb_address=socket.inet_aton("10.129.203.95"),
            broadcast=True,
        )
        data = testee.to_bytes()
        self.assertEqual(
            binascii.hexlify(data).decode(),
            (
                "07ac" "2910" "0001" "0000" "0000" "0001" "20454f4546454c4550"
                "43414341434143414341434143414341434143414341414100" "0020"
                "0001" "c00c" "0020" "0001" "00000000" "0006" "0000" "0a81cb5f"
            )
        )


class NBNSNameOverwriteDemandTestCase(unittest.TestCase):

    def test_to_bytes(self):
        testee = NBNSNameOverwriteDemand(
            name_trn_id=1964,
            q_name=NBName("neko").to_bytes(),
            nb_address=socket.inet_aton("10.129.203.95"),
            broadcast=True,
        )
        data = testee.to_bytes()
        self.assertEqual(
            binascii.hexlify(data).decode(),
            (
                "07ac" "2810" "0001" "0000" "0000" "0001" "20454f4546454c4550"
                "43414341434143414341434143414341434143414341414100" "0020"
                "0001" "c00c" "0020" "0001" "00000000" "0006" "0000" "0a81cb5f"
            )
        )

class NBNSNegativeNameRegistrationResponseTestCase(unittest.TestCase):

    def test_to_bytes(self):
        testee = NBNSNegativeNameRegistrationResponse(
            name_trn_id=1964,
            q_name=NBName("neko").to_bytes(),
            nb_address=socket.inet_aton("10.129.203.95"),
            ont=NB_NS_NB_FLAGS_ONT_B,
        )
        data = testee.to_bytes()
        self.assertEqual(
            binascii.hexlify(data).decode(),
            (
                "07ac" "ad86" "0000" "0001" "0000" "0000" "20454f4546454c4550"
                "43414341434143414341434143414341434143414341414100" "0020"
                "0001" "00000000" "0006" "0000" "0a81cb5f"
            )
        )
