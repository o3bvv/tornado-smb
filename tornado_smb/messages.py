# coding: utf-8

from struct import pack


class SMBMessage:
    """
    SMB message.

    See: https://msdn.microsoft.com/en-us/library/ee441774.aspx

    """
    __slots__ = (
        'Command', 'NT_Status', 'Flags1', 'Flags2', 'PIDHigh',
        'SecurityFeatures', 'TID', 'PIDLow', 'UID', 'MID', 'Words', 'Bytes',
    )

    HEADER_LENGTH = 32
    _HEADER_PROTOCOL_SIGNATURE = pack('B 3s', 0xFF, b'SMB')

    def __init__(
        self, Command=0, NT_Status=0, Flags1=0, Flags2=0, PIDHigh=0,
        SecurityFeatures=None, TID=0xFFFF, PIDLow=0, UID=0, MID=0,
        Words=None, Bytes=None,
    ):
        self.Command = Command
        self.NT_Status = NT_Status
        self.Flags1 = Flags1
        self.Flags2 = Flags2
        self.PIDHigh = PIDHigh
        self.SecurityFeatures = (
            SecurityFeatures
            if SecurityFeatures is not None else
            pack('q', 0)
        )
        self.TID = TID
        self.PIDLow = PIDLow
        self.UID = UID
        self.MID = MID
        self.Words = Words if Words is not None else b''
        self.Bytes = Bytes if Bytes is not None else b''

    def to_bytes(self):
        return (
              self._build_header()
            + self._build_parameters_block()
            + self._build_data_block()
        )

    def _build_header(self):
        return (
              self._HEADER_PROTOCOL_SIGNATURE
            + pack(' B', self.Command)
            + pack('<I', self.NT_Status)
            + pack(' B', self.Flags1)
            + pack('<H', self.Flags2)
            + pack('<H', self.PIDHigh)
            + pack('8s', self.SecurityFeatures)
            + pack('<H', 0)
            + pack('<H', self.TID)
            + pack('<H', self.PIDLow)
            + pack('<H', self.UID)
            + pack('<H', self.MID)
        )

    def _build_parameters_block(self):
        count = len(self.Words)
        return pack(
            'B {count}B'.format(count=count),
            count >> 1,
            *bytearray(self.Words)
        )

    def _build_data_block(self):
        count = len(self.Bytes)
        return pack(
            'H {count}B'.format(count=count),
            count,
            *bytearray(self.Bytes)
        )
