#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BC3 Compressor/Decompressor
# Version 0.1
# Copyright © 2018 MasterVermilli0n / AboodXD

################################################################
################################################################

try:
    import pyximport

    pyximport.install()
    from . import compress_cy as compress_
    from . import decompress_cy as decompress_

except:
    from . import compress_
    from . import decompress_


def decompress(data, width, height):
    if not isinstance(data, bytes):
        try:
            data = bytes(data)

        except:
            print("Couldn't decompress data")
            return b''

    csize = ((width + 3) // 4) * ((height + 3) // 4) * 16
    if len(data) < csize:
        print("Compressed data is incomplete")
        return b''

    data = data[:csize]
    return decompress_.decompress(data, width, height)


def compress(data, width, height):
    if not isinstance(data, bytes):
        try:
            data = bytes(data)

        except:
            print("Couldn't compress data")
            return b''

    csize = width * height * 4
    if len(data) < csize:
        print("Decompressed data is incomplete")
        return b''

    data = data[:csize]
    return compress_.compress(data, width, height)
