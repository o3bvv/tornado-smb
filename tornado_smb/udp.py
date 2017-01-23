# coding: utf-8

import socket

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.iostream import IOStream


class UDPClient:
    """
    A non-blocking UDP connection factory.

    """

    def __init__(self, io_loop=None):
        self.io_loop = io_loop or IOLoop.current()

    @gen.coroutine
    def connect(
        self, host, port, ssl_options=None, max_buffer_size=None,
        allow_broadcast=False,
    ):
        """
        Connect to the given host and port.

        Asynchronously returns an `.IOStream`
        (or `.SSLIOStream` if ``ssl_options`` is not None).

        """
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        if allow_broadcast:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        stream = IOStream(
            socket=sock,
            io_loop=self.io_loop,
            max_buffer_size=max_buffer_size,
        )

        if ssl_options is not None:
            stream = yield stream.start_tls(
                server_side=False,
                ssl_options=ssl_options,
                server_hostname=host,
            )

        stream.connect(address=(host, port), )
        return stream
