#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# libyaz0
# Version 0.1
# Copyright © 2017 MasterVermilli0n / AboodXD

# This file is part of libyaz0.

# libyaz0 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# libyaz0 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import math
import struct

def DecompressYaz(src):
    dest_end = struct.unpack(">I", src[4:8])[0]
    dest = bytearray(dest_end)

    code = 0
    code_len = 0

    src_pos = 16
    dest_pos = 0

    while src_pos < len(src) and dest_pos < dest_end:
        if not code_len:
            code = src[src_pos]
            src_pos += 1
            code_len = 8

        if code & 0x80:
            dest[dest_pos] = src[src_pos]
            src_pos += 1
            dest_pos += 1

        else:
            b1 = src[src_pos]
            src_pos += 1
            b2 = src[src_pos]
            src_pos += 1

            copy_src = dest_pos - ((b1 & 0x0f) << 8 | b2) - 1

            n = b1 >> 4
            if not n:
                n = src[src_pos] + 0x12
                src_pos += 1

            else:
                n += 2

            assert (3 <= n <= 0x111)

            while n > 0:
                n -= 1
                dest[dest_pos] = dest[copy_src]
                copy_src += 1
                dest_pos += 1

        code <<= 1
        code_len -= 1

    return dest


def CompressYazFast(src):
    pos = 0
    dest = bytearray()
    src_end = len(src)
    n = 8

    while pos < src_end:
        if n == 8:
            n = 0
            dest += b'\xFF'
        dest += src[pos:pos + 1]
        pos += 1
        n += 1

    return dest


def CompressYaz(src, level):
    dest = bytearray()
    src_end = len(src)

    if not level:
        return CompressYazFast(src)
    elif level < 9:
        search_range = 0x10e0 * level // 9 - 0x0e0
    else:
        search_range = 0x1000

    max_len = 0x111

    pos = 0

    while pos < src_end:
        buffer = bytearray()
        code_byte = 0

        for i in range(8):
            if pos - search_range < 0:
                search = 0
                search_len = pos
            else:
                search = pos - search_range
                search_len = search_range

            found_len = max_len
            if pos + found_len > src_end:
                found_len = src_end - pos

            c1 = src[pos:pos + found_len]
            search_data = src[search:search + search_len]

            found = search_data.rfind(c1)

            while found == -1 and found_len > 3:
                found_len -= 1
                c1 = src[pos:pos + found_len]

                if len(c1) < found_len:
                    found_len = len(c1)

                found = search_data.rfind(c1)

            if found_len >= 3 and found != -1:
                delta = search_len - found - 1
                if found_len < 0x12:
                    buffer += bytes([delta >> 8 | (found_len - 2) << 4])
                    buffer += bytes([delta & 0xFF])
                else:
                    buffer += bytes([delta >> 8])
                    buffer += bytes([delta & 0xFF])
                    buffer += bytes([(found_len - 0x12) & 0xFF])
                pos += found_len

            else:
                byte = src[pos:pos + 1]
                pos += 1

                buffer += byte

                code_byte |= 1 << (7 - i)

        dest += bytes([code_byte])
        dest += buffer

    return dest
