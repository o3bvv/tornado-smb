# coding: utf-8

import binascii

ORD_A = ord('A')
WILD_CARD = '*'
BYTE_ZERO = bytes([0, ])

NETBIOS_NAME_PURPOSE_WORKSTATION = 0x00
NETBIOS_NAME_PURPOSE_MESSENGER = 0x03
NETBIOS_NAME_PURPOSE_FILE_SERVER = 0x20
NETBIOS_NAME_PURPOSE_DOMAIN_MASTER = 0x1B

NETBIOS_NAME_FULL_LEN = 16
NETBIOS_NAME_VALUE_LEN = NETBIOS_NAME_FULL_LEN - 1  # 1 byte for purpose

NETBIOS_NAME_FMT = "{{:{}}}".format(NETBIOS_NAME_VALUE_LEN)
NETBIOS_NAME_WILD_CARD_PADDED = bytes.ljust(
    WILD_CARD.encode(), NETBIOS_NAME_VALUE_LEN, BYTE_ZERO,
)


class NetBIOSName:
    __slots__ = ('value', 'scope', 'purpose', )

    def __init__(self, value, scope=None, purpose=NETBIOS_NAME_PURPOSE_WORKSTATION):
        if len(value) > NETBIOS_NAME_VALUE_LEN:
            raise ValueError(
                "NetBIOS name '{value}' is too long! "
                "Truncate it to {max} bytes."
                .format(value=value, max=NETBIOS_NAME_VALUE_LEN)
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
            padded = NETBIOS_NAME_WILD_CARD_PADDED
        else:
            padded = NETBIOS_NAME_FMT.format(self.value).encode()

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
