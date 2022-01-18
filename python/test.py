#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import struct


def serial_package_builder(data, can, param_bin = 0b00000000):
    package = []
    package.append(0x02)
    package.append(0x05)
    package.append(param_bin)

    #TODO Lage til alle typer data som skal mottas: https://docs.python.org/3/library/struct.html
    [package.append(i) for i in struct.pack('<q', 42)]

    package.append(0x03)

    return bytearray(package)

print(serial_package_builder(1, True))