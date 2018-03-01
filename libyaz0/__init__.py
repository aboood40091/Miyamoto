#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# libyaz0
# Version 0.4
# Copyright © 2017 MasterVermilli0n / AboodXD

################################################################
################################################################

try:
    from . import yaz0_pyd as yaz0

except:
    try:
        from . import yaz0_so as yaz0

    except:
        try:
            import pyximport

            pyximport.install()
            from . import yaz0_cy as yaz0

        except:
            from . import yaz0


def IsYazCompressed(data):
    return data[:4] in [b'Yaz0', b'Yaz1']


def decompress(data):
    isYaz = IsYazCompressed(data)

    if isYaz:
        return yaz0.DecompressYaz(bytearray(data))

    else:
        raise ValueError("Not Yaz0 compressed!")


def compress(data, unk=0, level=9):
    compressed_data = yaz0.CompressYaz(bytes(data), level)

    result = bytearray(b'Yaz0')
    result += len(data).to_bytes(4, "big")
    result += unk.to_bytes(4, "big")
    result += bytes(4)
    result += compressed_data

    return result


def guessFileExt(data):
    if data[0:4] == b"BNTX":
        return ".bntx"

    elif data[0:4] == b"BNSH":
        return ".bnsh"

    elif data[0:4] == b"FLAN":
        return ".bflan"

    elif data[0:4] == b"FLYT":
        return ".bflyt"

    elif data[0:4] == b"Gfx2":
        return ".gtx"

    elif data[0:4] == b"SARC":
        return ".sarc"

    elif data[0:4] == b"Yaz0":
        return ".yaz0"

    elif data[-0x28:-0x24] == b"FLIM":
        return ".bflim"

    else:  # Couldn't guess the file extension
        return ".bin"
