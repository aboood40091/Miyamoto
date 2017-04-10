#!/usr/bin/env python

# GTX Extractor
# Version v1.2a
# Copyright © 2014 Treeki, 2015-2016 AboodXD

# This file is part of GTX Extractor.

# GTX Extractor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# GTX Extractor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""gtx_extract.py: Decode GFD (GTX/GSH) images."""

import os, struct, sys

from PyQt5 import QtCore, QtGui

__author__ = "AboodXD"
__copyright__ = "Copyright 2015, 2016 AboodXD"
__credits__ = ["AboodXD", "libdxtn", "Treeki",
                    "Reggie Next! team"]

# ----------\/-Start of libdxtn section-\/---------- #
def Expand_shit(packedcol):
    EXP5TO8R = int((((packedcol) >> 8) & 0xf8) | (((packedcol) >> 13) & 0x07))
    EXP6TO8G = int((((packedcol) >> 3) & 0xfc) | (((packedcol) >>  9) & 0x03))
    EXP5TO8B = int((((packedcol) << 3) & 0xf8) | (((packedcol) >>  2) & 0x07))

    return EXP5TO8R, EXP6TO8G, EXP5TO8B

def dxt135_decode_imageblock(pixdata, img_block_src, i, j, dxt_type):
    color0 = pixdata[img_block_src] | (pixdata[img_block_src + 1] << 8)
    color1 = pixdata[img_block_src + 2] | (pixdata[img_block_src + 3] << 8)
    bits = (pixdata[img_block_src + 4] | (pixdata[img_block_src + 5] << 8) |
        (pixdata[img_block_src + 6] << 16) | (pixdata[img_block_src + 7] << 24))
    # What about big/little endian?
    bit_pos = 2 * (j * 4 + i)
    code = (bits >> bit_pos) & 3

    ACOMP = 255

    EXP5TO8R0, EXP6TO8G0, EXP5TO8B0 = Expand_shit(color0)
    EXP5TO8R1, EXP6TO8G1, EXP5TO8B1 = Expand_shit(color1)

    if code == 0:
        RCOMP = EXP5TO8R0
        GCOMP = EXP6TO8G0
        BCOMP = EXP5TO8B0
    elif code == 1:
        RCOMP = EXP5TO8R1
        GCOMP = EXP6TO8G1
        BCOMP = EXP5TO8B1
    elif code == 2:
        if (dxt_type > 1) or (color0 > color1):
            RCOMP = (EXP5TO8R0 * 2 + EXP5TO8R1) // 3
            GCOMP = (EXP6TO8G0 * 2 + EXP6TO8G1) // 3
            BCOMP = (EXP5TO8B0 * 2 + EXP5TO8B1) // 3
        else:
            RCOMP = (EXP5TO8R0 + EXP5TO8R1) // 2
            GCOMP = (EXP6TO8G0 + EXP6TO8G1) // 2
            BCOMP = (EXP5TO8B0 + EXP5TO8B1) // 2
    elif code == 3:
        if (dxt_type > 1) or (color0 > color1):
            RCOMP = (EXP5TO8R0 + EXP5TO8R1 * 2) // 3
            GCOMP = (EXP6TO8G0 + EXP6TO8G1 * 2) // 3
            BCOMP = (EXP5TO8B0 + EXP5TO8B1 * 2) // 3
        else:
            RCOMP = 0
            GCOMP = 0
            BCOMP = 0
            if dxt_type == 1: ACOMP = 0
    return ACOMP, RCOMP, GCOMP, BCOMP

def fetch_2d_texel_rgba_dxt5(srcRowStride, pixdata, i, j):

    """
    Extract the (i,j) pixel from pixdata and return it
    in RCOMP, GCOMP, BCOMP, ACOMP.
    """

    blksrc = ((srcRowStride + 3) // 4 * (j // 4) + (i // 4)) * 16
    alpha0 = pixdata[blksrc]
    alpha1 = pixdata[blksrc + 1]
    # TODO test this!
    bit_pos = ((j & 3) * 4 + (i & 3)) * 3
    acodelow = pixdata[blksrc + 2 + bit_pos // 8]
    acodehigh = pixdata[blksrc + 3 + bit_pos // 8]
    code = (acodelow >> (bit_pos & 0x07) |
        (acodehigh << (8 - (bit_pos & 0x07)))) & 0x07
    ACOMP, RCOMP, GCOMP, BCOMP = dxt135_decode_imageblock(pixdata, blksrc + 8, i & 3, j & 3, 2)

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

    return bytes([RCOMP, GCOMP, BCOMP, ACOMP])
    
# ----------\/-Start of GFD Extractor section-\/------------- #
class GFDData():
    width, height = 0, 0
    format = 0
    dataSize = 0
    data = b''

class GFDHeader(struct.Struct):
    def __init__(self):
        super().__init__('>4s7I') # Totally stolen, thanks Reggie Next team!

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
        super().__init__('>4s7I') # Totally stolen, thanks Reggie Next team!

    def data(self, data, pos):
        (self.magic,
        self.size_,
        self.majorVersion,
        self.minorVersion,
        self.type_,
        self.dataSize,
        self.id,
        self.typeIdx) = self.unpack_from(data, pos)

class GFDSurface(struct.Struct):
    def __init__(self):
        super().__init__('>39I') # Totally stolen, thanks Reggie Next team!

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
        self.pitch,
        self.mipOffset,
        self._44,
        self._48,
        self._4C,
        self._50,
        self._54,
        self._58,
        self._5C,
        self._60,
        self._64,
        self._68,
        self._6C,
        self._70,
        self._74,
        self._78,
        self._7C,
        self._80,
        self._84,
        self._88,
        self._8C,
        self._90,
        self._94,
        self._98) = self.unpack_from(data, pos)

def readGFD(f):
    gfd = GFDData()
    pos = 0

    header = GFDHeader()

    # This is kinda bad. Don't really care right now >.>
    gfd.width = 0
    gfd.height = 0
    gfd.data = b''

    header.data(f, pos)
    
    if header.magic != b'Gfx2':
        raise ValueError("Invalid file header!")

    pos += header.size

    while pos < len(f):
        block = GFDBlockHeader()
        block.data(f, pos)

        if block.magic != b'BLK{':
            raise ValueError("Invalid block header!")

        pos += block.size

        if block.type_ == 0x0B:
            surface = GFDSurface()
            surface.data(f, pos)

            pos += surface.size

            if block.dataSize != 0x9C:
                raise ValueError("Invalid data block size!")

            gfd.dim = surface.dim
            gfd.width = surface.width
            gfd.height = surface.height
            gfd.depth = surface.depth
            gfd.numMips = surface.numMips
            gfd.format = surface.format_
            gfd.aa = surface.aa
            gfd.use = surface.use
            gfd.imageSize = surface.imageSize
            gfd.imagePtr = surface.imagePtr
            gfd.mipSize = surface.mipSize
            gfd.mipPtr = surface.mipPtr
            gfd.tileMode = surface.tileMode
            gfd.swizzle = surface.swizzle
            gfd.alignment = surface.alignment
            gfd.pitch = surface.pitch

        elif block.type_ == 0x0C and len(gfd.data) == 0:
            gfd.dataSize = block.dataSize
            gfd.data = f[pos:pos + block.dataSize]
            pos += block.dataSize

        else:
            pos += block.dataSize

    return gfd

def writeFile(data):
    if data.format == 0x00:
        raise ValueError("Invalid format!")
    elif data.format == 0x1a:
        return export_RGBA8(data)
    elif data.format == 0x33:
        return export_DXT5(data)
    else:
        raise NotImplementedError("Unimplemented texture format: " + hex(data.format))

def export_RGBA8(gfd):
    pos, x, y = 0, 0, 0

    source = gfd.data
    output = bytearray(gfd.width * gfd.height * 4)

    for y in range(gfd.height):
        for x in range(gfd.width):
            pos = (y & ~15) * gfd.width
            pos ^= (x & 3)
            pos ^= ((x >> 2) & 1) << 3
            pos ^= ((x >> 3) & 1) << 6
            pos ^= ((x >> 3) & 1) << 7
            pos ^= (x & ~0xF) << 4
            pos ^= (y & 1) << 2
            pos ^= ((y >> 1) & 7) << 4
            pos ^= (y & 0x10) << 4
            pos ^= (y & 0x20) << 2
            pos_ = (y * gfd.width + x) * 4
            pos *= 4
            output[pos_:pos_ + 4] = gfd.data[pos:pos + 4]

    img = QtGui.QImage(output, gfd.width, gfd.height, QtGui.QImage.Format_RGBA8888)
    return img.copy(0, 0, gfd.width, gfd.height)

def export_DXT5(gfd):
    pos, x, y = 0, 0, 0
    outValue = 0
    blobWidth = gfd.width // 4
    blobHeight = gfd.height // 4
    work = bytearray(gfd.width * gfd.height)

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

            pos_ = (y * blobWidth + x) * 16
            pos *= 16
            work[pos_:pos_ + 16] = gfd.data[pos:pos + 16]

    output = bytearray(gfd.width * gfd.height * 4)

    for y in range(gfd.height):
        for x in range(gfd.width):
            outValue = fetch_2d_texel_rgba_dxt5(gfd.width, work, x, y)

            pos__ = (y * gfd.width + x) * 4
            output[pos__:pos__ + 4] = outValue

    img = QtGui.QImage(output, gfd.width, gfd.height, QtGui.QImage.Format_RGBA8888)
    return img.copy(0, 0, gfd.width, gfd.height)
