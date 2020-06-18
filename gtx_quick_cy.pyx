#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2020 Treeki, Tempus, angelsl, JasonP27, Kinnay,
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

# gtx_quick_cy.pyx
# A script for decoding RGBA8 and DXT5 GX2 data


################################################################
################################################################

from cpython cimport array
from cython cimport view
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy


ctypedef unsigned char u8
ctypedef unsigned short u16
ctypedef unsigned int u32


cdef u8 EXP5TO8R(u16 packedcol):
    return (((packedcol) >> 8) & 0xf8) | (((packedcol) >> 13) & 0x07)


cdef u8 EXP6TO8G(u16 packedcol):
    return (((packedcol) >> 3) & 0xfc) | (((packedcol) >>  9) & 0x03)


cdef u8 EXP5TO8B(u16 packedcol):
    return (((packedcol) << 3) & 0xf8) | (((packedcol) >>  2) & 0x07)


cdef (u8, u8, u8, u8) dxt5_decode_imageblock(u8 *pixdata, u32 img_block_src, u8 i, u8 j):
    cdef:
        u16 color0 = pixdata[img_block_src] | (pixdata[img_block_src + 1] << 8)
        u16 color1 = pixdata[img_block_src + 2] | (pixdata[img_block_src + 3] << 8)
        u32 bits = (pixdata[img_block_src + 4] | (pixdata[img_block_src + 5] << 8) |
                    (pixdata[img_block_src + 6] << 16) | (pixdata[img_block_src + 7] << 24))

        u8 bit_pos = 2 * (j * 4 + i)
        u8 code = (bits >> bit_pos) & 3
 
        u8 ACOMP, RCOMP, GCOMP, BCOMP

    ACOMP = 255
    if code == 0:
        RCOMP = EXP5TO8R(color0)
        GCOMP = EXP6TO8G(color0)
        BCOMP = EXP5TO8B(color0)

    elif code == 1:
        RCOMP = EXP5TO8R(color1)
        GCOMP = EXP6TO8G(color1)
        BCOMP = EXP5TO8B(color1)

    elif code == 2:
        RCOMP = ((EXP5TO8R(color0) * 2 + EXP5TO8R(color1)) // 3)
        GCOMP = ((EXP6TO8G(color0) * 2 + EXP6TO8G(color1)) // 3)
        BCOMP = ((EXP5TO8B(color0) * 2 + EXP5TO8B(color1)) // 3)

    elif code == 3:
        RCOMP = ((EXP5TO8R(color0) + EXP5TO8R(color1) * 2) // 3)
        GCOMP = ((EXP6TO8G(color0) + EXP6TO8G(color1) * 2) // 3)
        BCOMP = ((EXP5TO8B(color0) + EXP5TO8B(color1) * 2) // 3)
 
    return ACOMP, RCOMP, GCOMP, BCOMP


cdef (u8, u8, u8, u8) fetch_2d_texel_rgba_dxt5(u32 srcRowStride, u8 *pixdata, u32 i, u32 j):
    cdef:
        u32 blksrc = ((srcRowStride + 3) // 4 * (j // 4) + (i // 4)) * 16

        u8 alpha0 = pixdata[blksrc]
        u8 alpha1 = pixdata[blksrc + 1]

        u8 bit_pos = ((j & 3) * 4 + (i & 3)) * 3
        u8 acodelow = pixdata[blksrc + 2 + bit_pos // 8]
        u8 acodehigh = pixdata[blksrc + 3 + bit_pos // 8]
        u8 code = (acodelow >> (bit_pos & 0x07) |
                (acodehigh << (8 - (bit_pos & 0x07)))) & 0x07

        u8 ACOMP, RCOMP, GCOMP, BCOMP

    ACOMP, RCOMP, GCOMP, BCOMP = dxt5_decode_imageblock(pixdata, blksrc + 8, i & 3, j & 3)
 
    if code == 0:
        ACOMP = alpha0

    elif code == 1:
        ACOMP = alpha1

    elif alpha0 > alpha1:
        ACOMP = (alpha0 * (8 - code) + (alpha1 * (code - 1))) // 7

    elif code < 6:
        ACOMP = (alpha0 * (6 - code) + (alpha1 * (code - 1))) // 5

    elif code == 6:
        ACOMP = 0

    else:
        ACOMP = 255
 
    return RCOMP, GCOMP, BCOMP, ACOMP


cpdef bytes decodeGTX(u32 width, u32 height, u32 format, data):
    cdef array.array dataArr = array.array('B', data)

    if format == 0x1a:
        return export_RGBA8(width, height, dataArr.data.as_uchars)

    elif format == 0x33:
        return export_DXT5(width, height, dataArr.data.as_uchars)

    else:
        raise NotImplementedError("Unimplemented texture format!")


cdef bytes export_RGBA8(u32 width, u32 height, u8 *source):
    cdef:
        u32 pos, x, y, pos_
        u8 *output

    output = <u8 *>malloc(width * height * 4)
    pos = 0

    try:
        for y in range(height):
            for x in range(width):
                pos = (y & ~15) * width
                pos ^= (x & 3)
                pos ^= ((x >> 2) & 1) << 3
                pos ^= ((x >> 3) & 1) << 6
                pos ^= ((x >> 3) & 1) << 7
                pos ^= (x & ~0xF) << 4
                pos ^= (y & 1) << 2
                pos ^= ((y >> 1) & 7) << 4
                pos ^= (y & 0x10) << 4
                pos ^= (y & 0x20) << 2
                pos *= 4

                pos_ = (y * width + x) * 4

                memcpy(output + pos_, source + pos, 4)

        return bytes(<u8[:width * height * 4]>output)

    finally:
        free(output)


cdef bytes export_DXT5(u32 width, u32 height, u8 *source):
    cdef:
        u32 pos, x, y, pos_
        u8 *work
        u32 blobWidth = (width + 3) // 4
        u32 blobHeight = (height + 3) // 4

    work = <u8 *>malloc(blobWidth * blobHeight * 16)
    pos = 0

    for y in range(blobHeight):
        for x in range(blobWidth):
            pos = (y >> 4) * (blobWidth * 16)
            pos ^= (y & 1)
            pos ^= (x & 7) << 1
            pos ^= (x & 8) << 1
            pos ^= (x & 8) << 2
            pos ^= (x & 0x10) << 2
            pos ^= (x & ~0x1F) << 4
            pos ^= (y & 2) << 6
            pos ^= (y & 4) << 6
            pos ^= (y & 8) << 1
            pos ^= (y & 0x10) << 2
            pos ^= (y & 0x20)
            pos *= 16

            pos_ = (y * blobWidth + x) * 16

            memcpy(work + pos_, source + pos, 16)

    cdef:
        u8 R, G, B, A
        u8 *output = <u8 *>malloc(width * height * 4)
 
    try:
        for y in range(height):
            for x in range(width):
                R, G, B, A = fetch_2d_texel_rgba_dxt5(width, work, x, y)

                pos = (y * width + x) * 4

                output[pos + 0] = R
                output[pos + 1] = G
                output[pos + 2] = B
                output[pos + 3] = A
     
        return bytes(<u8[:width * height * 4]>output)

    finally:
        free(work)
        free(output)
