#!/usr/bin/env python3
# coding: utf-8

import argparse

from tornado import gen
from tornado.ioloop import IOLoop

from tornado_smb.nbt import NBName, NBNSNameQueryRequest
from tornado_smb.udp import UDPClient


BROADCAST_ADDR = '<broadcast>'
NB_NS_PORT = 137


@gen.coroutine
def run_query(ioloop, name, scope):
    c = UDPClient(ioloop)
    stream = yield c.connect(BROADCAST_ADDR, NB_NS_PORT, broadcast=True)
    nb_name = NBName(name, scope)
    nb_name_query = NBNSNameQueryRequest(
        name_trn_id=1964,
        q_name=nb_name.to_bytes(),
        broadcast=True,
    )
    yield stream.write(nb_name_query.to_bytes())
    stream.close()
    ioloop.stop()


def main():
    parser = argparse.ArgumentParser(
        description="Example of NetBIOS Name Query request"
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

    ioloop = IOLoop.current()
    ioloop.add_callback(run_query, ioloop, args.name, args.scope)
    ioloop.start()


if __name__ == '__main__':
    main()
