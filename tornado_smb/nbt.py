# coding: utf-8

ORD_A = ord('A')

NETBIOS_NAME_LEN = 16
NETBIOS_NAME_FMT = "{{:{}}}".format(NETBIOS_NAME_LEN)
NETBIOS_NAME_WILD_CARD = '*'
NETBIOS_NAME_WILD_CARD_PADDED = bytes.ljust(
    NETBIOS_NAME_WILD_CARD.encode(), NETBIOS_NAME_LEN, b'\x00',
)


# TODO: last byte in name


class NetBIOSName:
    __slots__ = ('name', 'scope', )

    def __init__(self, name, scope=None):
        if len(name) > NETBIOS_NAME_LEN:
            raise ValueError(
                "NetBIOS name '{name}' is too long! "
                "Truncate it to {max} bytes."
                .format(name=name, max=NETBIOS_NAME_LEN)
            )

        self.name = name.upper()
        self.scope = scope.upper() if scope else ''

    def to_bytes(self):
        chunks = [
            self._encode_name(),
        ]
        if self.scope:
            chunks.extend(self.scope.split('.'))

        def pack_item(item):
            if isinstance(item, str):
                item = item.encode()
            return bytes((len(item), )) + item

        return b''.join(map(pack_item, chunks)) + b'\x00'

    def _encode_name(self):
        if self.name == NETBIOS_NAME_WILD_CARD:
            padded = NETBIOS_NAME_WILD_CARD_PADDED
        else:
            padded = NETBIOS_NAME_FMT.format(self.name).encode()

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
        return (
            "{}.{}".format(self.name, self.scope)
            if self.scope else
            self.name
        )
