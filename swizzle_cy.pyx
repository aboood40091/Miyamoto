#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! DX Level Editor - New Super Mario Bros. U Deluxe Level Editor
# Copyright (C) 2009-2020 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7, John10v10,
# mrbengtsson

# This file is part of Miyamoto! DX.

# Miyamoto! DX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Miyamoto! DX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Miyamoto! DX.  If not, see <http://www.gnu.org/licenses/>.

from cpython cimport array
from cython cimport view
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy


ctypedef unsigned char u8
ctypedef unsigned int u32


cpdef u32 DIV_ROUND_UP(u32 n, u32 d):
    return (n + d - 1) // d


cpdef u32 round_up(u32 x, u32 y):
    return ((x - 1) | (y - 1)) + 1


cpdef u32 pow2_round_up(u32 x):
    x -= 1
    x |= x >> 1
    x |= x >> 2
    x |= x >> 4
    x |= x >> 8
    x |= x >> 16

    return x + 1


cpdef u32 getBlockHeight(u32 height):
    cdef blockHeight = pow2_round_up(height // 8)
    if blockHeight > 16:
        blockHeight = 16

    return blockHeight


cdef bytearray _swizzle(u32 width, u32 height, u32 blkWidth, u32 blkHeight, int roundPitch, u32 bpp, u32 tileMode, int blockHeightLog2, bytearray data, int toSwizzle):
    assert 0 <= blockHeightLog2 <= 5
    cdef u32 blockHeight = 1 << blockHeightLog2

    width = DIV_ROUND_UP(width, blkWidth)
    height = DIV_ROUND_UP(height, blkHeight)

    cdef:
        u32 pitch
        u32 surfSize

    if tileMode == 1:
        pitch = width * bpp

        if roundPitch:
            pitch = round_up(pitch, 32)

        surfSize = pitch * height

    else:
        pitch = round_up(width * bpp, 64)
        surfSize = pitch * round_up(height, blockHeight * 8)

    cdef:
        u8 *result = <u8 *>malloc(surfSize)
        u32 x, y, pos, pos_, i

    try:
        for y in range(height):
            for x in range(width):
                if tileMode == 1:
                    pos = y * pitch + x * bpp

                else:
                    pos = getAddrBlockLinear(x, y, width, bpp, 0, blockHeight)

                pos_ = (y * width + x) * bpp

                if pos + bpp <= surfSize:
                    if toSwizzle:
                        for i in range(bpp):
                            result[pos + i] = data[pos_ + i]

                    else:
                        for i in range(bpp):
                            result[pos_ + i] = data[pos + i]

        return bytearray(<u8[:surfSize]>result)

    finally:
        free(result)


cpdef deswizzle(u32 width, u32 height, u32 blkWidth, u32 blkHeight, int roundPitch, u32 bpp, u32 tileMode, int blockHeightLog2, data):
    return _swizzle(width, height, blkWidth, blkHeight, roundPitch, bpp, tileMode, blockHeightLog2, bytearray(data), 0)


cpdef swizzle(u32 width, u32 height, u32 blkWidth, u32 blkHeight, int roundPitch, u32 bpp, u32 tileMode, int blockHeightLog2, data):
    return _swizzle(width, height, blkWidth, blkHeight, roundPitch, bpp, tileMode, blockHeightLog2, bytearray(data), 1)


cdef u32 getAddrBlockLinear(u32 x, u32 y, u32 image_width, u32 bytes_per_pixel, u32 base_address, u32 blockHeight):
    """
    From the Tegra X1 TRM
    """
    cdef:
        u32 image_width_in_gobs = DIV_ROUND_UP(image_width * bytes_per_pixel, 64)

        u32 GOB_address = (base_address
                           + (y // (8 * blockHeight)) * 512 * blockHeight * image_width_in_gobs
                           + (x * bytes_per_pixel // 64) * 512 * blockHeight
                           + (y % (8 * blockHeight) // 8) * 512)

    x *= bytes_per_pixel

    cdef u32 Address = (GOB_address + ((x % 64) // 32) * 256 + ((y % 8) // 2) * 64
                        + ((x % 32) // 16) * 32 + (y % 2) * 16 + (x % 16))

    return Address
