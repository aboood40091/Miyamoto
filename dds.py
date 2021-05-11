#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2021 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7, John10v10,
# mrbengtsson

# This file is part of Miyamoto!.

# Miyamoto! is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Miyamoto! is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Miyamoto!.  If not, see <http://www.gnu.org/licenses/>.

# dds.py
# A small script for reading/writing RGBA8 and DXT5 DDS files.


################################################################
################################################################

import struct


def readDDS(f):
    with open(f, "rb") as inf:
        inb = inf.read()

    width = struct.unpack("<I", inb[16:20])[0]
    height = struct.unpack("<I", inb[12:16])[0]

    fourcc = inb[84:88]

    caps = struct.unpack("<I", inb[108:112])[0]

    compSel = [0, 1, 2, 3]

    if fourcc == b'DXT5':
        format_ = 0x33
        bpp = 16

        size = ((width + 3) >> 2) * ((height + 3) >> 2) * bpp

    else:
        format_ = 0x1a
        bpp = 4

        size = width * height * bpp

    if caps == 0x401008:
        numMips = struct.unpack("<I", inb[28:32])[0] - 1
        mipSize = get_mipSize(width, height, bpp, numMips, fourcc == b'DXT5')
    else:
        numMips = 0
        mipSize = 0

    data = inb[0x80:0x80 + size + mipSize]

    return width, height, format_, fourcc, size, compSel, numMips, data


def get_mipSize(width, height, bpp, numMips, compressed):
    size = 0
    for i in range(numMips):
        level = i + 1
        if compressed:
            size += ((max(1, width >> level) + 3) >> 2) * ((max(1, height >> level) + 3) >> 2) * bpp
        else:
            size += max(1, width >> level) * max(1, height >> level) * bpp
    return size


def generateHeader(w, h, fmt, num_mipmaps=1):
    compressed = fmt & 0xFF == 0x33

    hdr = bytearray(128)

    flags = 0x00000001 | 0x00001000 | 0x00000004 | 0x00000002

    caps = 0x00001008

    if num_mipmaps == 0:
        num_mipmaps = 1

    elif num_mipmaps != 1:
        flags |= 0x00020000
        caps |= 0x00000008 | 0x00400000

    if not compressed:
        flags |= 0x00000008
        pflags = 0x00000041

        size = w * 4

    else:
        flags |= 0x00080000
        pflags = 0x00000004

        size = ((w + 3) // 4) * ((h + 3) // 4) * 16

    hdr[0:0 + 4] = b'DDS '
    hdr[4:4 + 4] = b'|\x00\x00\x00'
    hdr[8:8 + 4] = flags.to_bytes(4, 'little')
    hdr[12:12 + 4] = h.to_bytes(4, 'little')
    hdr[16:16 + 4] = w.to_bytes(4, 'little')
    hdr[20:20 + 4] = size.to_bytes(4, 'little')
    hdr[28:28 + 4] = num_mipmaps.to_bytes(4, 'little')
    hdr[76:76 + 4] = b' \x00\x00\x00'
    hdr[80:80 + 4] = pflags.to_bytes(4, 'little')

    if compressed:
        hdr[84:84 + 4] = b'DXT5'

    else:
        hdr[88:88 + 4] = b' \x00\x00\x00'

        hdr[92:92 + 4] = b'\xff\x00\x00\x00'
        hdr[96:96 + 4] = b'\x00\xff\x00\x00'
        hdr[100:100 + 4] = b'\x00\x00\xff\x00'
        hdr[104:104 + 4] = b'\x00\x00\x00\xff'

    hdr[108:108 + 4] = caps.to_bytes(4, 'little')

    return hdr
