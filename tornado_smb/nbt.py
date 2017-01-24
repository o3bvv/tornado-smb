# coding: utf-8

import abc
import binascii

from struct import pack


ORD_A     = ord('A')
WILD_CARD = '*'
BYTE_ZERO = bytes([0, ])

NB_NAME_PURPOSE_WORKSTATION   = 0x00
NB_NAME_PURPOSE_MESSENGER     = 0x03
NB_NAME_PURPOSE_FILE_SERVER   = 0x20
NB_NAME_PURPOSE_DOMAIN_MASTER = 0x1B

NB_NAME_FULL_LEN  = 16
NB_NAME_VALUE_LEN = NB_NAME_FULL_LEN - 1  # 1 byte for purpose

NB_NAME_FMT = "{{:{}}}".format(NB_NAME_VALUE_LEN)
NB_NAME_WILD_CARD_PADDED = bytes.ljust(
    WILD_CARD.encode(), NB_NAME_VALUE_LEN, BYTE_ZERO,
)


class NBName:
    """
    NetBIOS name.

    """
    __slots__ = ('value', 'scope', 'purpose', )

    def __init__(self, value, scope=None, purpose=NB_NAME_PURPOSE_WORKSTATION):
        if len(value) > NB_NAME_VALUE_LEN:
            raise ValueError(
                "NetBIOS name '{value}' is too long! "
                "Truncate it to {max} bytes."
                .format(value=value, max=NB_NAME_VALUE_LEN)
            )

        self.value = value.upper()
        self.scope = scope.upper() if scope else ''
        self.purpose = bytes([purpose, ])

    def to_bytes(self):
        chunks = [
            self._encode_value(),
        ]
        if self.scope:
            chunks.extend(self.scope.split('.'))

        def pack_item(item):
            if isinstance(item, str):
                item = item.encode()
            return bytes((len(item), )) + item

        return b''.join(map(pack_item, chunks)) + BYTE_ZERO

    def _encode_value(self):
        if self.value == WILD_CARD:
            padded = NB_NAME_WILD_CARD_PADDED
        else:
            padded = NB_NAME_FMT.format(self.value).encode()

        padded += self.purpose
        return b''.join(map(self.encode_byte, padded))

    @staticmethod
    def encode_byte(value):
        hi_nibble = 0x0F & (value >> 4)
        lo_nibble = 0x0F & value
        return bytes((hi_nibble + ORD_A, lo_nibble + ORD_A))

    @classmethod
    def from_bytes(cls, data):
        raise NotImplementedError

    def __str__(self):
        hex_purpose = binascii.hexlify(self.purpose).decode()
        name = "{}<{}>".format(self.value, hex_purpose)
        return "{}.{}".format(name, self.scope) if self.scope else name


NB_NS_R_REQUEST  = 0
NB_NS_R_RESPONSE = 1

NB_NS_OPCODE_QUERY                         = 0x0
NB_NS_OPCODE_NAME_REGISTRATION             = 0x5
NB_NS_OPCODE_NAME_RELEASE                  = 0x6
NB_NS_OPCODE_WACK                          = 0x7
NB_NS_OPCODE_NAME_REFRESH                  = 0x8
NB_NS_OPCODE_NAME_REFRESH_ALT              = 0x9
NB_NS_OPCODE_MULTI_HOMED_NAME_REGISTRATION = 0xF

NB_NS_NM_FLAGS_B  = 1 << 0
NB_NS_NM_FLAGS_RA = 1 << 3
NB_NS_NM_FLAGS_RD = 1 << 4
NB_NS_NM_FLAGS_TC = 1 << 5
NB_NS_NM_FLAGS_AA = 1 << 6

NB_NS_RCODE_NONE    = 0x0
NB_NS_RCODE_FMT_ERR = 0x1
NB_NS_RCODE_SRV_ERR = 0x2
NB_NS_RCODE_IMP_ERR = 0x4
NB_NS_RCODE_RFS_ERR = 0x5
NB_NS_RCODE_ACT_ERR = 0x6
NB_NS_RCODE_CFT_ERR = 0x7


class NBNSMessage(metaclass=abc.ABCMeta):
    """
    Base class for NetBIOS Name Service (NBNS) messages.

    """
    __slots__ = (
        'name_trn_id', 'r', 'opcode', 'nm_flags', 'rcode',
        'qdcount', 'ancount', 'nscount', 'arcount',
    )

    def __init__(
        self, name_trn_id, r, opcode, nm_flags, rcode, qdcount, ancount,
        nscount, arcount,
    ):
        self.name_trn_id = name_trn_id
        self.r           = r
        self.opcode      = opcode
        self.nm_flags    = nm_flags
        self.rcode       = rcode
        self.qdcount     = qdcount
        self.ancount     = ancount
        self.nscount     = nscount
        self.arcount     = arcount

    def to_bytes(self):
        return (
              self._build_header()
            + self._build_body()
        )

    def _build_header(self):
        return pack(
            '>6H',
            self.name_trn_id,
            (
                  (0b0001111 & self.rcode)
                | (0b1111111 & self.nm_flags) << 4
                | (0b0001111 & self.opcode)   << 11
                | (0b0000001 & self.r)        << 15
            ),
            self.qdcount,
            self.ancount,
            self.nscount,
            self.arcount,
        )

    @abc.abstractmethod
    def _build_body(self):
        raise NotImplementedError


NBNS_QUESTION_TYPE_NB     = 0x0020
NBNS_QUESTION_TYPE_NBSTAT = 0x0021

NBNS_QUESTION_CLASS_IN    = 0x0001


class NBNSRequest(NBNSMessage):
    __slots__ = NBNSMessage.__slots__ + (
        'question_name', 'question_type', 'question_class',
    )

    def __init__(
        self,
        name_trn_id, opcode, nm_flags, qdcount, ancount, nscount, arcount,
        question_name, question_type, question_class=NBNS_QUESTION_CLASS_IN,
    ):
        super().__init__(
            name_trn_id = name_trn_id,
            r           = NB_NS_R_REQUEST,
            opcode      = opcode,
            nm_flags    = nm_flags,
            rcode       = NB_NS_RCODE_NONE,
            qdcount     = qdcount,
            ancount     = ancount,
            nscount     = nscount,
            arcount     = arcount,
        )
        self.question_name  = question_name
        self.question_type  = question_type
        self.question_class = question_class

    def _build_body(self):
        return self._build_query_entry()

    def _build_query_entry(self):
        return (
              self.question_name
            + pack(
                '>2H',
                self.question_type,
                self.question_class,
            )
        )


class NBNSNameQueryRequest(NBNSRequest):
    """
    NetBIOS Name Service Name Query request.

    See also: section 4.2.12 of RFC 1002 (https://tools.ietf.org/html/rfc1002).

    """

    def __init__(self, name_trn_id, question_name, broadcast=False):
        nm_flags = (
               NB_NS_NM_FLAGS_RD
            | (NB_NS_NM_FLAGS_B if broadcast else 0)
        )
        super().__init__(
            name_trn_id    = name_trn_id,
            opcode         = NB_NS_OPCODE_QUERY,
            nm_flags       = nm_flags,
            qdcount        = 0x0001,
            ancount        = 0x0000,
            nscount        = 0x0000,
            arcount        = 0x0000,
            question_name  = question_name,
            question_type  = NBNS_QUESTION_TYPE_NB,
            question_class = NBNS_QUESTION_CLASS_IN,
        )
