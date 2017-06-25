#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# GTX Extractor
# Copyright © 2014 Treeki, 2015-2017 AboodXD

"""gtx_extract.py: Decode GFD (GTX) images."""

import math, os, struct, sys, time

__author__ = "AboodXD"
__copyright__ = "Copyright 2014 Treeki, 2015-2017 AboodXD"
__credits__ = ["AboodXD", "Treeki", "AddrLib", "Exzap"]

class GFDData():
    width, height = 0, 0
    format = 0
    dataSize = 0
    data = b''

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

class GFDSurface(struct.Struct):
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
    gfd = GFDData()

    pos = 0

    header = GFDHeader()
    header.data(f, pos)
    
    if header.magic != b'Gfx2':
        raise ValueError("Invalid file header!")

    pos += header.size

    blockB = False
    blockC = False

    while pos < len(f): # Loop through the entire file, stop if reached the end of the file.
        block = GFDBlockHeader()
        block.data(f, pos)

        if block.magic != b'BLK{':
            raise ValueError("Invalid block header!")

        pos += block.size

        if block.type_ == 0x0B:
            blockB = True

            surface = GFDSurface()
            surface.data(f, pos)

            pos += surface.size
            pos += (23 * 4)

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

        elif block.type_ == 0x0C:
            blockC = True

            gfd.dataSize = block.dataSize
            gfd.data = f[pos:pos + block.dataSize]
            pos += block.dataSize

        else:
            pos += block.dataSize

    if blockB:
        if not blockC:
            print("")
            print("Image info was found but no Image data was found.")
            print("")
            print("Exiting in 5 seconds...")
            time.sleep(5)
            sys.exit(1)
    if not blockB:
        if not blockC:
            print("")
            print("No Image was found in this file.")
            print("")
            print("Exiting in 5 seconds...")
            time.sleep(5)
            sys.exit(1)
        elif blockC:
            print("")
            print("Image data was found but no Image info was found.")
            print("")
            print("Exiting in 5 seconds...")
            time.sleep(5)
            sys.exit(1)

    return gfd

def get_deswizzled_data(gfd):
    if gfd.format == 0x33:
        if gfd.depth != 1:
            raise NotImplementedError("Unsupported depth!")

        else:
            result = swizzle(gfd.width, gfd.height, gfd.format, gfd.tileMode, gfd.swizzle, gfd.pitch, gfd.data)
            hdr = writeHeader(gfd.width, gfd.height)

    else:
        print("")
        print("Unsupported texture format: " + hex(gfd.format))
        sys.exit(1)

    return hdr, result

# ----------\/-Start of the swizzling section-\/---------- #
def swizzle(width, height, format_, tileMode, swizzle, pitch, data):
    result = bytearray(data)

    width /= 4
    width_float = math.modf(width)
    width = int(width_float[1])
    if width_float[0] == 0.5:
        width += 1

    height /= 4
    height_float = math.modf(height)
    height = int(height_float[1])
    if height_float[0] == 0.5:
        height += 1

    for y in range(height):
        for x in range(width):
            bpp = surfaceGetBitsPerPixel(format_)
            pipeSwizzle = (swizzle >> 8) & 1
            bankSwizzle = (swizzle >> 9) & 3

            if (tileMode == 0 or tileMode == 1):
                pos = AddrLib_computeSurfaceAddrFromCoordLinear(x, y, bpp, pitch, height)
            elif (tileMode == 2 or tileMode == 3):
                pos = AddrLib_computeSurfaceAddrFromCoordMicroTiled(x, y, bpp, pitch, height, tileMode)
            else:
                pos = AddrLib_computeSurfaceAddrFromCoordMacroTiled(x, y, bpp, pitch, height, tileMode, pipeSwizzle, bankSwizzle)

            bpp //= 8

            pos_ = (y * width + x) * bpp

            if (pos_ < len(data)) and (pos < len(data)):
                result[pos_:pos_ + bpp] = data[pos:pos + bpp]

    return result

# Credits:
#  -AddrLib: actual code
#  -Exzap: modifying code to apply to Wii U textures
#  -AboodXD: porting, code improvements and cleaning up

m_banks = 4
m_banksBitcount = 2
m_pipes = 2
m_pipesBitcount = 1
m_pipeInterleaveBytes = 256
m_pipeInterleaveBytesBitcount = 8
m_rowSize = 2048
m_swapSize = 256
m_splitSize = 2048

m_chipFamily = 2

MicroTilePixels = 8 * 8

formatHwInfo = b"\x00\x00\x00\x01\x08\x03\x00\x01\x08\x01\x00\x01\x00\x00\x00\x01" \
    b"\x00\x00\x00\x01\x10\x07\x00\x00\x10\x03\x00\x01\x10\x03\x00\x01" \
    b"\x10\x0B\x00\x01\x10\x01\x00\x01\x10\x03\x00\x01\x10\x03\x00\x01" \
    b"\x10\x03\x00\x01\x20\x03\x00\x00\x20\x07\x00\x00\x20\x03\x00\x00" \
    b"\x20\x03\x00\x01\x20\x05\x00\x00\x00\x00\x00\x00\x20\x03\x00\x00" \
    b"\x00\x00\x00\x00\x00\x00\x00\x01\x20\x03\x00\x01\x00\x00\x00\x01" \
    b"\x00\x00\x00\x01\x20\x0B\x00\x01\x20\x0B\x00\x01\x20\x0B\x00\x01" \
    b"\x40\x05\x00\x00\x40\x03\x00\x00\x40\x03\x00\x00\x40\x03\x00\x00" \
    b"\x40\x03\x00\x01\x00\x00\x00\x00\x80\x03\x00\x00\x80\x03\x00\x00" \
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x01\x10\x01\x00\x00" \
    b"\x10\x01\x00\x00\x20\x01\x00\x00\x20\x01\x00\x00\x20\x01\x00\x00" \
    b"\x00\x01\x00\x01\x00\x01\x00\x00\x00\x01\x00\x00\x60\x01\x00\x00" \
    b"\x60\x01\x00\x00\x40\x01\x00\x01\x80\x01\x00\x01\x80\x01\x00\x01" \
    b"\x40\x01\x00\x01\x80\x01\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00" \
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00" \
    b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"

def surfaceGetBitsPerPixel(surfaceFormat):
    hwFormat = surfaceFormat & 0x3F
    bpp = formatHwInfo[hwFormat * 4 + 0]

    return bpp

def computeSurfaceThickness(tileMode):
    thickness = 1

    if (tileMode == 3 or tileMode == 7 or tileMode == 11 or tileMode == 13 or tileMode == 15):
        thickness = 4

    elif (tileMode == 16 or tileMode == 17):
        thickness = 8

    return thickness

def computePixelIndexWithinMicroTile(x, y, bpp, tileMode, z=0):
    pixelBit6 = 0
    pixelBit7 = 0
    pixelBit8 = 0
    thickness = computeSurfaceThickness(tileMode)

    if bpp == 0x08:
        pixelBit0 = x & 1
        pixelBit1 = (x & 2) >> 1
        pixelBit2 = (x & 4) >> 2
        pixelBit3 = (y & 2) >> 1
        pixelBit4 = y & 1
        pixelBit5 = (y & 4) >> 2

    elif bpp == 0x10:
        pixelBit0 = x & 1
        pixelBit1 = (x & 2) >> 1
        pixelBit2 = (x & 4) >> 2
        pixelBit3 = y & 1
        pixelBit4 = (y & 2) >> 1
        pixelBit5 = (y & 4) >> 2

    elif (bpp == 0x20 or bpp == 0x60):
        pixelBit0 = x & 1
        pixelBit1 = (x & 2) >> 1
        pixelBit2 = y & 1
        pixelBit3 = (x & 4) >> 2
        pixelBit4 = (y & 2) >> 1
        pixelBit5 = (y & 4) >> 2

    elif bpp == 0x40:
        pixelBit0 = x & 1
        pixelBit1 = y & 1
        pixelBit2 = (x & 2) >> 1
        pixelBit3 = (x & 4) >> 2
        pixelBit4 = (y & 2) >> 1
        pixelBit5 = (y & 4) >> 2

    elif bpp == 0x80:
        pixelBit0 = y & 1
        pixelBit1 = x & 1
        pixelBit2 = (x & 2) >> 1
        pixelBit3 = (x & 4) >> 2
        pixelBit4 = (y & 2) >> 1
        pixelBit5 = (y & 4) >> 2

    else:
        pixelBit0 = x & 1
        pixelBit1 = (x & 2) >> 1
        pixelBit2 = y & 1
        pixelBit3 = (x & 4) >> 2
        pixelBit4 = (y & 2) >> 1
        pixelBit5 = (y & 4) >> 2

    if thickness > 1:
        pixelBit6 = z & 1
        pixelBit7 = (z & 2) >> 1

    if thickness == 8:
        pixelBit8 = (z & 4) >> 2

    return ((pixelBit8 << 8) | (pixelBit7 << 7) | (pixelBit6 << 6) |
            32 * pixelBit5 | 16 * pixelBit4 | 8 * pixelBit3 |
            4 * pixelBit2 | pixelBit0 | 2 * pixelBit1)

def computePipeFromCoordWoRotation(x, y):
    # hardcoded to assume 2 pipes
    return ((y >> 3) ^ (x >> 3)) & 1

def computeBankFromCoordWoRotation(x, y):
    # hardcoded to assume 4 banks
    numPipes = m_pipes

    bankBit0 = ((y // (16 * numPipes)) ^ (x >> 3)) & 1
    bank = bankBit0 | 2 * (((y // (8 * numPipes)) ^ (x >> 4)) & 1)

    return bank

def computeSurfaceRotationFromTileMode(tileMode):
    pipes = m_pipes
    result = 0

    if (tileMode == 4 or tileMode == 5 or tileMode == 6 or tileMode == 7 or tileMode == 8 or tileMode == 9 or tileMode == 10 or tileMode == 11):
        result = pipes * ((m_banks >> 1) - 1)

    elif (tileMode == 12 or tileMode == 13 or tileMode == 14 or tileMode == 15):
        # hardcoded to assume 2 pipes
        result = 1

    return result

def isThickMacroTiled(tileMode):
    thickMacroTiled = 0

    if (tileMode == 7 or tileMode == 11 or tileMode == 13 or tileMode == 15):
        thickMacroTiled = 1

    return thickMacroTiled

def isBankSwappedTileMode(tileMode):
    bankSwapped = 0

    if (tileMode == 8 or tileMode == 9 or tileMode == 10 or tileMode == 11 or tileMode == 14 or tileMode == 15):
        bankSwapped = 1

    return bankSwapped

def computeMacroTileAspectRatio(tileMode):
    ratio = 1

    if (tileMode == 5 or tileMode == 9):
        ratio = 2

    elif (tileMode == 6 or tileMode == 10):
        ratio = 4

    return ratio

def computeSurfaceBankSwappedWidth(tileMode, bpp, numSamples, pitch):
    if isBankSwappedTileMode(tileMode) == 0: return 0

    numBanks = m_banks
    numPipes = m_pipes
    swapSize = m_swapSize
    rowSize = m_rowSize
    splitSize = m_splitSize
    groupSize = m_pipeInterleaveBytes
    bytesPerSample = 8 * bpp & 0x1FFFFFFF

    try:
        samplesPerTile = splitSize // bytesPerSample
        slicesPerTile = max(1, numSamples // samplesPerTile)
    except ZeroDivisionError:
        slicesPerTile = 1

    if isThickMacroTiled(tileMode) != 0:
        numSamples = 4

    bytesPerTileSlice = numSamples * bytesPerSample // slicesPerTile

    factor = computeMacroTileAspectRatio(tileMode)
    swapTiles = max(1, (swapSize >> 1) // bpp)

    swapWidth = swapTiles * 8 * numBanks;
    heightBytes = numSamples * factor * numPipes * bpp // slicesPerTile
    swapMax = numPipes * numBanks * rowSize // heightBytes
    swapMin = groupSize * 8 * numBanks // bytesPerTileSlice

    bankSwapWidth = min(swapMax, max(swapMin, swapWidth))

    while bankSwapWidth >= 2 * pitch:
        bankSwapWidth >>= 1

    return bankSwapWidth

def AddrLib_computeSurfaceAddrFromCoordLinear(x, y, bpp, pitch, height):
    rowOffset = y * pitch
    pixOffset = x

    addr = (rowOffset + pixOffset) * bpp
    addr //= 8

    return addr

def AddrLib_computeSurfaceAddrFromCoordMicroTiled(x, y, bpp, pitch, height, tileMode):
    microTileThickness = 1

    if tileMode == 3:
        microTileThickness = 4

    microTileBytes = (MicroTilePixels * microTileThickness * bpp + 7) // 8
    microTilesPerRow = pitch >> 3
    microTileIndexX = x >> 3
    microTileIndexY = y >> 3

    microTileOffset = microTileBytes * (microTileIndexX + microTileIndexY * microTilesPerRow)

    pixelIndex = computePixelIndexWithinMicroTile(x, y, bpp, tileMode)

    pixelOffset = bpp * pixelIndex

    pixelOffset >>= 3

    return pixelOffset + microTileOffset

def AddrLib_computeSurfaceAddrFromCoordMacroTiled(x, y, bpp, pitch, height, tileMode, pipeSwizzle, bankSwizzle, numSamples=1):
    numPipes = m_pipes
    numBanks = m_banks
    numGroupBits = m_pipeInterleaveBytesBitcount
    numPipeBits = m_pipesBitcount
    numBankBits = m_banksBitcount

    microTileThickness = computeSurfaceThickness(tileMode)

    microTileBits = bpp * (microTileThickness * MicroTilePixels)
    microTileBytes = (microTileBits + 7) // 8

    pixelIndex = computePixelIndexWithinMicroTile(x, y, bpp, tileMode)

    pixelOffset = bpp * pixelIndex

    elemOffset = pixelOffset

    bytesPerSample = microTileBytes

    if (microTileBytes <= m_splitSize):
        sampleSlice = 0
    else:
        samplesPerSlice = m_splitSize // bytesPerSample
        numSampleSplits = max(1, 1 // samplesPerSlice)
        numSamples = samplesPerSlice
        sampleSlice = elemOffset // (microTileBits // numSampleSplits)
        elemOffset %= microTileBits // numSampleSplits
    elemOffset += 7
    elemOffset //= 8

    pipe = computePipeFromCoordWoRotation(x, y)
    bank = computeBankFromCoordWoRotation(x, y)

    bankPipe = pipe + numPipes * bank
    rotation = computeSurfaceRotationFromTileMode(tileMode)

    swizzle = pipeSwizzle + numPipes * bankSwizzle

    bankPipe ^= numPipes * sampleSlice * ((numBanks >> 1) + 1) ^ swizzle
    bankPipe %= numPipes * numBanks
    pipe = bankPipe % numPipes
    bank = bankPipe // numPipes

    sliceBytes = (height * pitch * microTileThickness * bpp * numSamples + 7) // 8
    sliceOffset = sliceBytes * (sampleSlice // microTileThickness)

    macroTilePitch = 8 * m_banks
    macroTileHeight = 8 * m_pipes

    if (tileMode == 5 or tileMode == 9): # GX2_TILE_MODE_2D_TILED_THIN4 and GX2_TILE_MODE_2B_TILED_THIN2
        macroTilePitch >>= 1
        macroTileHeight *= 2

    elif (tileMode == 6 or tileMode == 10): # GX2_TILE_MODE_2D_TILED_THIN4 and GX2_TILE_MODE_2B_TILED_THIN4
        macroTilePitch >>= 2
        macroTileHeight *= 4

    macroTilesPerRow = pitch // macroTilePitch
    macroTileBytes = (numSamples * microTileThickness * bpp * macroTileHeight * macroTilePitch + 7) // 8
    macroTileIndexX = x // macroTilePitch
    macroTileIndexY = y // macroTileHeight
    macroTileOffset = (macroTileIndexX + macroTilesPerRow * (macroTileIndexY)) * macroTileBytes

    if (tileMode == 8 or tileMode == 9 or tileMode == 10 or tileMode == 11 or tileMode == 14 or tileMode == 15):
        bankSwapOrder = [0, 1, 3, 2, 6, 7, 5, 4, 0, 0]
        bankSwapWidth = computeSurfaceBankSwappedWidth(tileMode, bpp, numSamples, pitch)
        swapIndex = macroTilePitch * macroTileIndexX // bankSwapWidth
        bank ^= bankSwapOrder[swapIndex & (m_banks - 1)]

    groupMask = ((1 << numGroupBits) - 1)

    numSwizzleBits = (numBankBits + numPipeBits)

    totalOffset = (elemOffset + ((macroTileOffset + sliceOffset) >> numSwizzleBits))
 
    offsetHigh  = (totalOffset & ~(groupMask)) << numSwizzleBits
    offsetLow = groupMask & totalOffset

    pipeBits = pipe << numGroupBits
    bankBits = bank << (numPipeBits + numGroupBits)

    return bankBits | pipeBits | offsetLow | offsetHigh

# ----------\/-Start of DDS writer section-\/---------- #

# Copyright © 2016-2017 AboodXD

def writeHeader(w, h):
    hdr = bytearray(128)

    hdr[:4] = b'DDS '
    hdr[4:4+4] = 124 .to_bytes(4, 'little')
    hdr[12:12+4] = h.to_bytes(4, 'little')
    hdr[16:16+4] = w.to_bytes(4, 'little')
    hdr[76:76+4] = 32 .to_bytes(4, 'little')

    flags = (0x00000001) | (0x00001000) | (0x00000004) | (0x00000002)

    caps = (0x00001000)

    hdr[28:28+4] = 1 .to_bytes(4, 'little')
    hdr[108:108+4] = caps.to_bytes(4, 'little')

    flags |= (0x00080000)
    pflags = (0x00000004)

    fourcc = b'DXT5'

    hdr[8:8+4] = flags.to_bytes(4, 'little')
    hdr[80:80+4] = pflags.to_bytes(4, 'little')
    hdr[84:84+4] = fourcc

    size = ((w + 3) >> 2) * ((h + 3) >> 2)
    size *= 16

    hdr[20:20+4] = size.to_bytes(4, 'little') # linear size

    return hdr

def main():
    """
    This place is a mess...
    """
    print("GTX Extractor")
    print("(C) 2014 Treeki, 2015-2017 AboodXD")
    
    print("")
    print("Usage: python gtx_extract.py input")
    print("")
    print("Exiting in 5 seconds...")
    time.sleep(5)
    sys.exit(1)

if __name__ == '__main__': main()
