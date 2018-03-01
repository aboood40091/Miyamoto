#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BC3 Compressor/Decompressor
# Version 0.1
# Copyright © 2018 MasterVermilli0n / AboodXD

# decompress_cy.pyx
# A BC3/DXT5 decompressor in Cython based on libtxc_dxtn.

################################################################
################################################################

from cpython cimport array
from cython cimport view
from libc.stdlib cimport malloc, free


ctypedef unsigned char u8
ctypedef unsigned short u16
ctypedef unsigned int u32


cdef u8 EXP5TO8R(u16 packedcol):
    return (((packedcol) >> 8) & 0xf8) | (((packedcol) >> 13) & 0x07)


cdef u8 EXP6TO8G(u16 packedcol):
    return (((packedcol) >> 3) & 0xfc) | (((packedcol) >>  9) & 0x03)


cdef u8 EXP5TO8B(u16 packedcol):
    return (((packedcol) << 3) & 0xf8) | (((packedcol) >>  2) & 0x07)


cdef (u8, u8, u8, u8) dxt5_decode_imageblock(u8 pixdata[], u32 img_block_src, u8 i, u8 j):
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


cdef (u8, u8, u8, u8) fetch_2d_texel_rgba_dxt5(u32 srcRowStride, u8 pixdata[], u32 i, u32 j):
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


cpdef bytes decompress(bytes data, u32 width, u32 height):
    cdef:
        array.array dataArr = array.array('B', data)

        u8 *work = dataArr.data.as_uchars
        u8 *output = <u8 *>malloc(width * height * 4)

        u8 R, G, B, A
        u32 y, x, pos
 
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
        free(output)
