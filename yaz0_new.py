#!/usr/bin/python
# -*- coding: latin-1 -*-

# Miyamoto! Next - New Super Mario Bros. U Level Editor
# Version v0.4 ALPHA
# Copyright (C) 2009-2016 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop

# This file is part of Miyamoto! Next.

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

# yaz0.py
# Allows compression and decompression of the Yaz0 format.

# This file's original copyright information is preserved below.

# Copyright (C) 2015, NWPlayer123
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, pulverize, distribute,
# synergize, compost, defenestrate, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO BLAH BLAH BLAH ISN'T IT FUNNY
# HOW UPPER-CASE MAKES IT SOUND LIKE THE LICENSE IS ANGRY AND SHOUTING AT YOU.

# This script is based on SARCUnpack v0.2 by NWPlayer.
# It was modified by Kinnay in order to get much
# faster decompression speeds.
# Then it was modified by RoadrunnerWMC to support
# Python 3, and also to squeeze out even more speed.


import struct


def decompress(data):
    uint16struct = struct.Struct('>H')

    assert data[:4] == b'Yaz0'

    pos = 16
    decompsize = struct.unpack_from('>I', data, 4)[0]
    out = bytearray(decompsize)
    outpos = 0
    bits = 0

    while outpos < decompsize: # Read entire file
        if not bits:
            code = data[pos]
            pos += 1
            bits = 8

        if code & 0x80: # Copy 1 byte
            out[outpos] = data[pos]
            outpos += 1
            pos += 1
        else:
            rle = uint16struct.unpack_from(data, pos)[0]
            pos += 2

            dist = rle & 0xFFF
            dstpos = outpos - dist - 1
            read = rle >> 12
            if read:
                read += 2
            else:
                read = data[pos] + 0x12
                pos += 1

            for x in range(read):
                out[outpos + x] = out[dstpos + x]
            outpos += read

        code <<= 1
        bits -= 1
    return out