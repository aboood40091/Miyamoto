#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# libyaz0
# Version 0.5
# Copyright © 2017-2018 MasterVermilli0n / AboodXD

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


cdef (u8 *, u32) compressionSearch(u8 *src, u8 *src_pos, int max_len, u32 range_, u8 *src_end):
    cdef:
        u32 found_len = 1

        u8 *found
        u8 *search
        u8 *cmp_end
        u8 c1
        u8 *cmp1
        u8 *cmp2
        int len_

    if src + 2 < src_end:
        search = src - range_
        if search < src_pos:
             search = src_pos

        cmp_end = src + max_len
        if cmp_end > src_end:
            cmp_end = src_end

        c1 = src[0]
        while search < src:
            search = <u8 *>memchr(search, c1, src - search)
            if not search:
                break

            cmp1 = search + 1
            cmp2 = src + 1

            while cmp2 < cmp_end and cmp1[0] == cmp2[0]:
                cmp1 += 1; cmp2 += 1

            len_ = cmp2 - src

            if found_len < len_:
                found_len = len_
                found = search
                if found_len == max_len:
                    break

            search += 1

    return found, found_len


cpdef bytearray CompressYaz(bytes src_, u8 opt_compr):
    cdef u32 range_

    if not opt_compr:
        range_ = 0

    elif opt_compr < 9:
        range_ = 0x10e0 * opt_compr / 9 - 0x0e0

    else:
        range_ = 0x1000

    cdef:
        array.array dataArr = array.array('B', src_)
        u8 *src = dataArr.data.as_uchars
        u8 *src_pos = src
        u8 *src_end = src + len(src_)

        u8 *dest = <u8 *>malloc(len(src_) + (len(src_) + 8) // 8)
        u8 *dest_pos = dest

        u8 mask = 0
        u8 *code_byte = dest

        int max_len = 0x111
        u32 found_len
        u8 *found
        u32 delta

    try:
        while src < src_end:
            if not mask:
                code_byte = dest
                dest[0] = 0; dest += 1
                mask = 0x80

            found_len = 1

            if range_:
                found, found_len = compressionSearch(src, src_pos, max_len, range_, src_end)

            if found_len >= 3:
                delta = src - found - 1

                if found_len < 0x12:
                    dest[0] = delta >> 8 | ( found_len - 2 ) << 4; dest += 1
                    dest[0] = delta; dest += 1

                else:
                    dest[0] = delta >> 8; dest += 1
                    dest[0] = delta; dest += 1
                    dest[0] = found_len - 0x12; dest += 1

                src += found_len

            else:
                code_byte[0] |= mask
                dest[0] = src[0]; dest += 1; src += 1

            mask >>= 1

        return bytearray(<u8[:dest - dest_pos]>dest_pos)

    finally:
        free(dest_pos)
