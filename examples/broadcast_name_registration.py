#!/usr/bin/env python3
# coding: utf-8

import argparse
import random
import socket
import struct

from tornado import gen
from tornado.ioloop import IOLoop

from tornado_smb.nbt import (
    NBName, NBNSNameRegistrationRequest, NBNSNameOverwriteDemand,
    NB_NS_R_RESPONSE, NB_NS_RCODE_ACT_ERR,
)
from tornado_smb.udp import UDPClient


BROADCAST_ADDR = '<broadcast>'
NB_NS_PORT = 137
TIMEOUT = 0.750


class Runner:
    io_loop = None
    nb_name = None

    def __init__(self, io_loop, nb_name):
        self.io_loop = io_loop
        self.nb_name = nb_name

    @gen.coroutine
    def run(self):
        c = UDPClient(self.io_loop)
        self.stream = yield c.connect(
            BROADCAST_ADDR,
            NB_NS_PORT,
            broadcast=True,
        )

        try:
            yield self._run()
        except Exception as e:
            print(str(e))
        else:
            print("Success: no negative replies received.")
        finally:
            self.stream.close()

    @gen.coroutine
    def _run(self):
        address, port = self.stream.socket.getsockname()
        nb_address = socket.inet_aton(address)
        trn_id = random.randint(0, 0xFFFF)

        self.registration_request = NBNSNameRegistrationRequest(
            name_trn_id=trn_id,
            q_name=self.nb_name.to_bytes(),
            nb_address=nb_address,
            broadcast=True,
        )

        for i in range(3):
            print("Trying...")
            yield self.stream.write(self.registration_request.to_bytes())

            try:
                f = self.stream.read_bytes(12)
                header = yield gen.with_timeout(
                    timeout=self.io_loop.time() + TIMEOUT,
                    future=f,
                    io_loop=self.io_loop,
                )
            except gen.TimeoutError:
                # A dirty hack to cancel reading and clear state of the stream
                self.io_loop.remove_handler(self.stream.socket)
                state = (self.stream._state & ~self.io_loop.READ)
                self.stream._state = None
                self.stream._read_callback = None
                self.stream._read_future = None
                self.stream._add_io_state(state)
                continue
            else:
                self._process_header(header)

        overwrite_demand = NBNSNameOverwriteDemand(
            name_trn_id=trn_id,
            q_name=self.nb_name.to_bytes(),
            nb_address=nb_address,
            broadcast=True,
        )
        yield self.stream.write(overwrite_demand.to_bytes())

    def _process_header(self, header):
        (
            trn_id,
            flags,
            question_count,
            answer_count,
            authority_count,
            additional_count,
        ) = struct.unpack(">6H", header)

        if self.registration_request.name_trn_id != trn_id:
            raise ValueError(
                "Got response for unknown transaction. "
                "Expected: {}, actual: {}"
                .format(self.registration_request.name_trn_id, trn_id)
            )

        rcode    = 0b0001111 &  flags
        nm_flags = 0b1111111 & (flags >> 4)
        opcode   = 0b0001111 & (flags >> 11)
        r        = 0b0000001 & (flags >> 15)

        if r != NB_NS_R_RESPONSE:
            raise ValueError("Expected to receive response, but got request")

        if opcode != self.registration_request.opcode:
            raise ValueError(
                "Unexpected transaction ID. Expected: {}, actual: {}"
                .format(self.registration_request.opcode, opcode)
            )

        if opcode != self.registration_request.opcode:
            raise ValueError(
                "Unexpected operation code. Expected: {}, actual: {}"
                .format(self.registration_request.opcode, opcode)
            )

        if rcode == NB_NS_RCODE_ACT_ERR:
            raise ValueError("Requested name is owned by another node")
        else:
            raise ValueError("Unexpected return code: {}".format(rcode))


def main():
    parser = argparse.ArgumentParser(
        description="Example of NetBIOS name registration"
    )
    parser.add_argument(
        'name',
        help="name to query",
    )
    parser.add_argument(
        'scope',
        nargs='?',
        help="scope of name",
    )
    args = parser.parse_args()
    nb_name = NBName(args.name, args.scope)

    io_loop = IOLoop.current()

    runner = Runner(io_loop, nb_name)
    future = runner.run()

    io_loop.add_future(future, lambda future: io_loop.stop())
    io_loop.start()


if __name__ == '__main__':
    main()
