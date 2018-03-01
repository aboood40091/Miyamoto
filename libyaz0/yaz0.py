#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# libyaz0
# Version 0.4
# Copyright © 2017 MasterVermilli0n / AboodXD

################################################################
################################################################

import struct


def DecompressYaz(src):
    dest_end = struct.unpack(">I", src[4:8])[0]
    dest = bytearray(dest_end)

    src_end = len(src)

    code = src[16]

    src_pos = 17
    dest_pos = 0

    while src_pos < src_end and dest_pos < dest_end:
        for _ in range(8):
            if src_pos >= src_end or dest_pos >= dest_end:
                break

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

                while n > 0:
                    n -= 1
                    dest[dest_pos] = dest[copy_src]
                    copy_src += 1
                    dest_pos += 1

            code <<= 1

        else:
            if src_pos >= src_end or dest_pos >= dest_end:
                break

            code = src[src_pos]
            src_pos += 1

    return dest


def CompressYazFast(src):
    pos = 0
    dest = bytearray(b'\xff')
    src_end = len(src)

    while pos < src_end:
        for _ in range(8):
            if pos >= src_end:
                break

            dest.append(src[pos])
            pos += 1

        else:
            dest.append(0xFF)

    return dest


def compressionSearch(data, pos, maxMatchLen, maxMatchDiff, src_end):
    """
    Find the longest match in `data` at or after `pos`.
    From ndspy, thanks RoadrunnerWMC!
    """
    start = max(0, pos - maxMatchDiff)

    lower = 0
    upper = min(maxMatchLen, src_end - pos)

    recordMatchPos = 0
    recordMatchLen = 0

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


def CompressYaz(src, level):
    dest = bytearray()
    src_end = len(src)

    if not level:
        return CompressYazFast(src)

    search_range = 0x10e0 * level // 9 - 0x0e0

    max_len = 0x111

    pos = 0

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
