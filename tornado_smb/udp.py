# coding: utf-8

import socket

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.iostream import IOStream


class UDPStream(IOStream):
    _destination = None

    def __init__(self, destination, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._destination = destination

    def write_to_fd(self, data):
        # A dirty hack. Do not use 'socket.connect()' & 'socket.send()',
        # as dectination can be a broadcast and a socket 'connected' to
        # broadcast will not be able to receive data.
        return self.socket.sendto(data, self._destination)

class UDPClient:
    """
    A non-blocking UDP connection factory.

    """
    io_loop = None

    def __init__(self, io_loop=None):
        self.io_loop = io_loop or IOLoop.current()

    @gen.coroutine
    def connect(
        self, host, port, ssl_options=None, max_buffer_size=None,
        broadcast=False, reuse=True,
    ):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # TODO: make configurable
        sock.bind(('', 0))

        if broadcast:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        if reuse:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        stream = UDPStream(
            socket=sock,
            io_loop=self.io_loop,
            max_buffer_size=max_buffer_size,
            destination=(host, port),
        )

        if ssl_options is not None:
            stream = yield stream.start_tls(
                server_side=False,
                ssl_options=ssl_options,
                server_hostname=host,
            )

        return stream
