#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# libyaz0
# Version 0.4
# Copyright © 2017 MasterVermilli0n / AboodXD

################################################################
################################################################

from cpython cimport array
from cython cimport view
from libc.stdlib cimport malloc, free


ctypedef unsigned char u8
ctypedef char s8
ctypedef unsigned int u32
ctypedef signed long long s64


cpdef bytes DecompressYaz(bytearray src):
    cdef:
        array.array dataArr = array.array('B', src)
        u8 *src_ = dataArr.data.as_uchars

        u32 dest_end = (src_[4] << 24 | src_[5] << 16 | src_[6] << 8 | src_[7])
        u8 *dest = <u8 *>malloc(dest_end)

        u32 src_end = len(src)

        u8 code = src_[16]

        u32 src_pos = 17
        u32 dest_pos = 0

        u8 b1, b2
        u32 copy_src
        int n

    try:
        while src_pos < src_end and dest_pos < dest_end:
            for _ in range(8):
                if src_pos >= src_end or dest_pos >= dest_end:
                    break

                if code & 0x80:
                    dest[dest_pos] = src_[src_pos]
                    src_pos += 1
                    dest_pos += 1

                else:
                    b1 = src_[src_pos]
                    src_pos += 1
                    b2 = src_[src_pos]
                    src_pos += 1

                    copy_src = dest_pos - ((b1 & 0x0f) << 8 | b2) - 1

                    n = b1 >> 4
                    if not n:
                        n = src_[src_pos] + 0x12
                        src_pos += 1

                    else:
                        n += 2

                    while n > 0:
                        n -= 1
                        dest[dest_pos] = dest[copy_src]
                        copy_src += 1
                        dest_pos += 1

                code <<= 1

            else:
                if src_pos >= src_end or dest_pos >= dest_end:
                    break

                code = src_[src_pos]
                src_pos += 1

        return bytes(<u8[:dest_end]>dest)

    finally:
        free(dest)


cdef bytearray CompressYazFast(bytes src):
    cdef:
        array.array dataArr = array.array('B', src)
        u8 *src_ = dataArr.data.as_uchars

        u32 src_pos = 0
        u32 src_end = len(src)

        u32 dest_pos = 1
        u32 dest_end = src_end + (src_end + 8) // 8
        u8 *dest = <u8 *>malloc(dest_end)

    try:
        dest[0] = 0xff
        while src_pos < src_end:
            for _ in range(8):
                if src_pos >= src_end:
                    break

                dest[dest_pos] = src_[src_pos]
                src_pos += 1
                dest_pos += 1

            else:
                dest[dest_pos] = 0xff
                dest_pos += 1

        return bytearray(<u8[:dest_end]>dest)

    finally:
        free(dest)


cdef inline s64 MAX(s64 a, s64 b):
    return a if a > b else b


cdef inline s64 MIN(s64 a, s64 b):
    return a if a < b else b


cdef (u32, u32) compressionSearch(bytes data, s64 pos, s64 maxMatchLen, s64 maxMatchDiff, s64 src_end):
    """
    Find the longest match in `data` at or after `pos`.
    From ndspy, thanks RoadrunnerWMC!
    """
    cdef u32 start = MAX(0, pos - maxMatchDiff)

    cdef u32 lower = 0
    cdef u32 upper = MIN(maxMatchLen, src_end - pos)

    cdef u32 recordMatchPos = 0
    cdef u32 recordMatchLen = 0

    cdef u32 matchLen
    cdef bytes match
    cdef s64 matchPos

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


cpdef bytearray CompressYaz(bytes src, u8 level):
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
