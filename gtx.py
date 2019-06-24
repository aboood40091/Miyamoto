#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2019 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7, John10v10

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

# gtx.py
# A small script for loading and creating RGBA8 and DXT5 GTX files.


################################################################
################################################################

import struct

import dds
import addrlib
from texRegisters import makeRegsBytearray


class GFDHeader(struct.Struct):
    def __init__(self):
        super().__init__('>4s7I')

    def data(self, data, pos):
        (self.magic,
         self.size_,
         self.majorVersion,
         self.minorVersion,
         self.gpuVersion,
         self.alignMode,
         self.reserved1,
         self.reserved2) = self.unpack_from(data, pos)


class GFDBlockHeader(struct.Struct):
    def __init__(self):
        super().__init__('>4s7I')

    def data(self, data, pos):
        (self.magic,
         self.size_,
         self.majorVersion,
         self.minorVersion,
         self.type_,
         self.dataSize,
         self.id,
         self.typeIdx) = self.unpack_from(data, pos)


class GX2Surface(struct.Struct):
    def __init__(self):
        super().__init__('>16I')

    def data(self, data, pos):
        (self.dim,
         self.width,
         self.height,
         self.depth,
         self.numMips,
         self.format_,
         self.aa,
         self.use,
         self.imageSize,
         self.imagePtr,
         self.mipSize,
         self.mipPtr,
         self.tileMode,
         self.swizzle,
         self.alignment,
         self.pitch) = self.unpack_from(data, pos)


def readGFD(f):
    pos = 0
    dim, width, height, depth, format, tileMode = 0, 0, 0, 0, 0, 0
    data = b''

    header = GFDHeader()
    header.data(f, pos)

    if header.magic != b'Gfx2':
        raise ValueError("Invalid file header!")

    pos += header.size

    blkhead = GFDBlockHeader()
    gx2surf = GX2Surface()

    while pos < len(f):
        blkhead.data(f, pos)

        if blkhead.magic != b'BLK{':
            raise ValueError("Invalid block header!")

        pos += blkhead.size

        if blkhead.type_ == 0x0B:
            gx2surf.data(f, pos)

            dim = gx2surf.dim
            width = gx2surf.width
            height = gx2surf.height
            depth = gx2surf.depth
            format = gx2surf.format_ & 0xFF
            use = gx2surf.use
            tileMode = gx2surf.tileMode
            swizzle = gx2surf.swizzle

        elif blkhead.type_ == 0x0C and not data:
            data = bytes(f[pos:pos + blkhead.dataSize])

        pos += blkhead.dataSize

    return dim, width, height, depth, format, use, tileMode, swizzle, data


def divRoundUp(n, d):
    return (n + d - 1) // d


def roundUp(x, y):
    return ((x - 1) | (y - 1)) + 1


def getCurrentMipOffset_Size(width, height, blkWidth, blkHeight, bpp, currLevel):
    offset = 0

    for mipLevel in range(currLevel):
        width_ = divRoundUp(max(1, width >> mipLevel), blkWidth)
        height_ = divRoundUp(max(1, height >> mipLevel), blkHeight)

        offset += width_ * height_ * bpp

    width_ = divRoundUp(max(1, width >> currLevel), blkWidth)
    height_ = divRoundUp(max(1, height >> currLevel), blkHeight)

    size = width_ * height_ * bpp

    return offset, size


def getAlignBlockSize(dataOffset, alignment):
    alignSize = roundUp(dataOffset, alignment) - dataOffset - 32

    z = 1
    while alignSize < 0:
        alignSize = roundUp(dataOffset + (alignment * z), alignment) - dataOffset - 32
        z += 1

    return alignSize


def writeGFD(f):
    width, height, format_, fourcc, dataSize, compSel, numMips, data = dds.readDDS(f)
    numMips += 1

    tileMode = addrlib.getDefaultGX2TileMode(1, width, height, 1, format_, 0, 1)

    bpp = addrlib.surfaceGetBitsPerPixel(format_) >> 3
    surfOut = addrlib.getSurfaceInfo(format_, width, height, 1, 1, tileMode, 0, 0)

    alignment = surfOut.baseAlign
    imageSize = surfOut.surfSize
    pitch = surfOut.pitch

    tilingDepth = surfOut.depth
    if surfOut.tileMode == 3:
        tilingDepth //= 4

    s = 0

    if format_ == 0x33:
        blkWidth, blkHeight = 4, 4

    else:
        blkWidth, blkHeight = 1, 1

    swizzled_data = []
    mipSize = 0
    mipOffsets = []

    tiling1dLevel = 0
    tiling1dLevelSet = False

    for mipLevel in range(numMips):
        offset, size = getCurrentMipOffset_Size(width, height, blkWidth, blkHeight, bpp, mipLevel)
        data_ = data[offset:offset + size]

        width_ = max(1, width >> mipLevel)
        height_ = max(1, height >> mipLevel)

        if mipLevel:
            surfOut = addrlib.getSurfaceInfo(format_, width, height, 1, 1, tileMode, 0, mipLevel)

            if mipLevel == 1:
                mipOffsets.append(imageSize)

            else:
                mipOffsets.append(mipSize)

        data_ += b'\0' * (surfOut.surfSize - size)
        dataAlignBytes = b'\0' * (roundUp(mipSize, surfOut.baseAlign) - mipSize)

        if mipLevel:
            mipSize += surfOut.surfSize + len(dataAlignBytes)

        swizzled_data.append(bytearray(dataAlignBytes) + addrlib.swizzle(
            width_, height_, 1, format_, 0, 1, surfOut.tileMode,
            s, surfOut.pitch, surfOut.bpp, 0, 0, data_))

        if surfOut.tileMode in [1, 2, 3, 16]:
            tiling1dLevelSet = True

        if not tiling1dLevelSet:
            tiling1dLevel += 1

    if tiling1dLevelSet:
        s |= tiling1dLevel << 16

    else:
        s |= 13 << 16

    block_head_struct = GFDBlockHeader()
    gx2surf_blk_head = block_head_struct.pack(b"BLK{", 32, 1, 0, 0xb, 0x9c, 0, 0)

    gx2surf_struct = GX2Surface()
    gx2surf = gx2surf_struct.pack(1, width, height, 1, numMips, format_, 0, 1, imageSize, 0, mipSize, 0, tileMode, s,
                                  alignment, pitch)

    image_blk_head = block_head_struct.pack(b"BLK{", 32, 1, 0, 0xc, imageSize, 0, 0)
    mip_blk_head = block_head_struct.pack(b"BLK{", 32, 1, 0, 0xd, mipSize, 0, 0)

    output = gx2surf_blk_head + gx2surf

    if numMips > 1:
        i = 0
        for offset in mipOffsets:
            output += offset.to_bytes(4, 'big')
            i += 1

        for z in range(14 - i):
            output += 0 .to_bytes(4, 'big')

    else:
        output += b'\0' * 56

    output += numMips.to_bytes(4, 'big')
    output += b'\0' * 4
    output += 1 .to_bytes(4, 'big')

    for value in compSel:
        output += value.to_bytes(1, 'big')

    if format_ == 0x33:
        output += makeRegsBytearray(width, height, numMips, format_, tileMode, pitch * 4, compSel)

    else:
        output += makeRegsBytearray(width, height, numMips, format_, tileMode, pitch, compSel)

    alignSize = getAlignBlockSize(len(output) + 64, alignment)
    align_blk_head = block_head_struct.pack(b"BLK{", 32, 1, 0, 2, alignSize, 0, 0)

    output += align_blk_head
    output += b'\0' * alignSize
    output += image_blk_head
    output += swizzled_data[0]

    if numMips > 1:
        mipAlignSize = getAlignBlockSize(len(output) + 64, alignment)
        mipAlign_blk_head = block_head_struct.pack(b"BLK{", 32, 1, 0, 2, mipAlignSize, 0, 0)
        output += mipAlign_blk_head
        output += b'\0' * mipAlignSize
        output += mip_blk_head

        for i in range(1, len(swizzled_data)):
            output += swizzled_data[i]

    return output


def DDStoGTX(f):
    head_struct = GFDHeader()
    head = head_struct.pack(b"Gfx2", 32, 7, 1, 2, 1, 0, 0)

    outData = head

    imgblk = writeGFD(f)
    outData += imgblk

    block_head_struct = GFDBlockHeader()
    eof_blk_head = block_head_struct.pack(b"BLK{", 32, 1, 0, 1, 0, 0, 0)

    outData += eof_blk_head

    return outData
