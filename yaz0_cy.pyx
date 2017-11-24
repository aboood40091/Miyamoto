#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# libyaz0
# Version 0.3
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

import struct

ctypedef unsigned char u8
ctypedef char s8
ctypedef unsigned int u32

cimport libc.math as math


cpdef bytearray DecompressYaz(src):
    cdef u32 dest_end = struct.unpack(">I", src[4:8])[0]
    cdef bytearray dest = bytearray(dest_end)

    cdef u32 src_end = len(src)

    cdef u8 code = 0
    cdef int code_len = 0

    cdef u32 src_pos = 16
    cdef u32 dest_pos = 0

    cdef u8 b1, b2
    cdef u32 copy_src
    cdef bytes copy_data
    cdef list new_data
    cdef int n

    while src_pos < src_end and dest_pos < dest_end:
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


cdef bytearray CompressYazFast(src):
    cdef u32 pos = 0
    cdef bytearray dest = bytearray()
    cdef u32 src_end = len(src)
    cdef u8 n = 8

    while pos < src_end:
        if n == 8:
            n = 0
            dest += b'\xFF'
        dest += src[pos:pos + 1]
        pos += 1
        n += 1

    return dest


cdef compressionSearch(data, pos, maxMatchLen, maxMatchDiff, src_end):
    """
    Find the longest match in `data` at or after `pos`.
    From ndspy, thanks RoadrunnerWMC!
    """
    cdef u32 start = max(0, pos - maxMatchDiff)

    cdef u32 lower = 0
    cdef u32 upper = min(maxMatchLen, src_end - pos)

    cdef u32 recordMatchPos = 0
    cdef u32 recordMatchLen = 0

    cdef u32 matchLen
    cdef bytes match
    cdef int matchPos

    while lower <= upper:
        matchLen = (lower + upper) // 2
        match = data[pos : pos + matchLen]
        matchPos = data.find(match, start, pos)

        if matchPos == -1:
            upper = matchLen - 1
        else:
            if matchLen > recordMatchLen:
                recordMatchPos, recordMatchLen = matchPos, matchLen
            lower = matchLen + 1

    return recordMatchPos, recordMatchLen


cpdef bytearray CompressYaz(src, level):
    cdef bytearray dest = bytearray()
    cdef u32 src_end = len(src)

    if not level:
        return CompressYazFast(src)

    cdef u32 search_range = 0x10e0 * level // 9 - 0x0e0

    cdef u32 max_len = 0x111

    cdef u32 pos = 0

    cdef bytearray buffer
    cdef u8 code_byte
    cdef int i
    cdef u32 found, found_len, delta

    while pos < src_end:
        buffer = bytearray()
        code_byte = 0

        for i in range(8):
            if pos >= src_end:
                break

            found, found_len = compressionSearch(src, pos, max_len, search_range, src_end)

            if found_len > 2:
                delta = pos - found - 1

                if found_len < 0x12:
                    buffer.append(delta >> 8 | (found_len - 2) << 4)
                    buffer.append(delta & 0xFF)

                else:
                    buffer.append(delta >> 8)
                    buffer.append(delta & 0xFF)
                    buffer.append((found_len - 0x12) & 0xFF)

                pos += found_len

            else:
                buffer.append(src[pos])
                pos += 1

                code_byte |= 1 << (7 - i)

        dest.append(code_byte)
        dest += buffer

    return dest
