#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2017 Treeki, Tempus, angelsl, JasonP27, Kinnay,
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
    width, height, format = 0, 0, 0
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
            pos += blkhead.dataSize

            width = gx2surf.width
            height = gx2surf.height
            format = gx2surf.format_

        elif blkhead.type_ == 0x0C and not data:
            dataSize = blkhead.dataSize
            data = bytes(f[pos:pos + dataSize])
            pos += dataSize

        else:
            pos += blkhead.dataSize

    return width, height, format,  dataSize, data


def writeGFD(f):
    tileMode = 4

    width, height, format_, fourcc, dataSize, compSel, numMips, data = dds.readDDS(f)

    imageData = data[:dataSize]
    mipData = data[dataSize:]
    numMips += 1

    if format_ == 0x33:
        align = 0x1EE4
        mipAlign = 0x1FC0
    else:
        align = 0x6E4
        mipAlign = 0x7C0

    bpp = addrlib.surfaceGetBitsPerPixel(format_) >> 3

    alignment = 512 * bpp

    surfOut = addrlib.getSurfaceInfo(format_, width, height, 1, 1, tileMode, 0, 0)

    pitch = surfOut.pitch

    if format_ == 0x33:
        s = 0x40000
    else:
        s = 0xd0000

    swizzled_data = []
    imageSize = 0
    mipSize = 0
    mipOffsets = []
    for i in range(numMips):
        if i == 0:
            data = imageData

            imageSize = surfOut.surfSize
        else:
            offset, dataSize = get_curr_mip_off_size(width, height, bpp, i, format_ == 0x33)

            data = mipData[offset:offset + dataSize]

            surfOut = addrlib.getSurfaceInfo(format_, width, height, 1, 1, tileMode, 0, i)

        padSize = surfOut.surfSize - dataSize
        data += padSize * b"\x00"

        if i != 0:
            offset += padSize

            if i == 1:
                mipOffsets.append(imageSize)
            else:
                mipOffsets.append(offset)

            mipSize += len(data)

        swizzled_data.append(addrlib.swizzle(max(1, width >> i), max(1, height >> i), surfOut.height, format_,
                                             surfOut.tileMode, s, surfOut.pitch, surfOut.bpp, data))

    block_head_struct = GFDBlockHeader()
    gx2surf_blk_head = block_head_struct.pack(b"BLK{", 32, 1, 0, 0xb, 0x9c, 0, 0)

    gx2surf_struct = GX2Surface()
    gx2surf = gx2surf_struct.pack(1, width, height, 1, numMips, format_, 0, 1, imageSize, 0, mipSize, 0, tileMode, s,
                                  alignment, pitch)

    align_blk_head = block_head_struct.pack(b"BLK{", 32, 1, 0, 2, align, 0, 0)

    image_blk_head = block_head_struct.pack(b"BLK{", 32, 1, 0, 0xc, imageSize, 0, 0)

    mipAlign_blk_head = block_head_struct.pack(b"BLK{", 32, 1, 0, 2, mipAlign, 0, 0)

    mip_blk_head = block_head_struct.pack(b"BLK{", 32, 1, 0, 0xd, mipSize, 0, 0)

    output = gx2surf_blk_head + gx2surf

    if numMips > 1:
        i = 0
        for offset in mipOffsets:
            output += offset.to_bytes(4, 'big')
            i += 1
        for z in range(14 - i):
            output += (0).to_bytes(4, 'big')
    else:
        output += b"\x00" * 56

    output += numMips.to_bytes(4, 'big')
    output += b"\x00" * 4
    output += (1).to_bytes(4, 'big')

    for value in compSel:
        output += value.to_bytes(1, 'big')

    output += b"\x00" * 20
    output += align_blk_head
    output += b"\x00" * align
    output += image_blk_head
    output += swizzled_data[0]

    if numMips > 1:
        output += mipAlign_blk_head
        output += b"\x00" * mipAlign
        output += mip_blk_head
        i = 0
        for data in swizzled_data:
            if i != 0:
                output += data
            i += 1

    return output


def get_curr_mip_off_size(width, height, bpp, curr_level, compressed):
    off = 0

    for i in range(curr_level - 1):
        level = i + 1
        if compressed:
            off += ((max(1, width >> level) + 3) >> 2) * ((max(1, height >> level) + 3) >> 2) * bpp
        else:
            off += max(1, width >> level) * max(1, height >> level) * bpp

    if compressed:
        size = ((max(1, width >> curr_level) + 3) >> 2) * ((max(1, height >> curr_level) + 3) >> 2) * bpp
    else:
        size = max(1, width >> curr_level) * max(1, height >> curr_level) * bpp

    return off, size


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
