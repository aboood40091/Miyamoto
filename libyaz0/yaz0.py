#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# libyaz0
# Version 0.5
# Copyright © 2017-2018 MasterVermilli0n / AboodXD

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


def compressionSearch(src, pos, max_len, search_range, src_end):
    found_len = 1
    found = 0

    if pos + 2 < src_end:
        search = pos - search_range
        if search < 0:
             search = 0

        cmp_end = pos + max_len
        if cmp_end > src_end:
            cmp_end = src_end

        c1 = src[pos:pos + 1]
        while search < pos:
            search = src.find(c1, search, pos)
            if search == -1:
                break

            cmp1 = search + 1
            cmp2 = pos + 1

            while cmp2 < cmp_end and src[cmp1] == src[cmp2]:
                cmp1 += 1; cmp2 += 1

            len_ = cmp2 - pos

            if found_len < len_:
                found_len = len_
                found = search
                if found_len == max_len:
                    break

            search += 1

    return found, found_len


def CompressYaz(src, level):
    dest = bytearray()
    src_end = len(src)

    if not level:
        search_range = 0

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
            if pos >= src_end:
                break

            found_len = 1

            if search_range:
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
