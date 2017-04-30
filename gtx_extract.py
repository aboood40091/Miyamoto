#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# GTX Extractor
# Copyright © 2014 Treeki, 2015-2017 AboodXD

"""gtx_extract.py: Decode GFD (GTX) images."""

import os, struct, sys, time

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
            result = swizzle_BC(gfd.width, gfd.height, gfd.depth, gfd.format, gfd.tileMode, gfd.swizzle, gfd.pitch, gfd.data, gfd.dataSize)
            hdr = writeHeader(gfd.width, gfd.height)

    else:
        print("")
        print("Unsupported texture format: " + hex(gfd.format))
        sys.exit(1)

    return hdr, result

# ----------\/-Start of the swizzling section-\/---------- #
def swizzle_BC(width, height, depth, format_, tileMode, swizzle, pitch, data, dataSize, toGFD=False):
    result = bytearray(dataSize)

    width = width // 4
    height = height // 4

    for y in range(height):
        for x in range(width):
            bitPos = 0
            bpp = surfaceGetBitsPerPixel(format_)
            pipeSwizzle = (swizzle >> 8) & 1
            bankSwizzle = (swizzle >> 9) & 3

            if (tileMode == 0 or tileMode == 1):
                pos = AddrLib_computeSurfaceAddrFromCoordLinear(x, y, 0, 0, bpp, pitch, height, depth, bitPos)
            elif (tileMode == 2 or tileMode == 3):
                pos = AddrLib_computeSurfaceAddrFromCoordMicroTiled(x, y, 0, bpp, pitch, height, tileMode, 0, 0, 0, bitPos)
            else:
                pos = AddrLib_computeSurfaceAddrFromCoordMacroTiled(x, y, 0, 0, bpp, pitch, height, 1, tileMode, 0, 0, 0, pipeSwizzle, bankSwizzle, bitPos)

            if (format_ == 0x31 or format_ == 0x431):
                pos_ = (y * width + x) * 8

                if toGFD:
                    result[pos:pos + 8] = data[pos_:pos_ + 8]
                else:
                    result[pos_:pos_ + 8] = data[pos:pos + 8]
            else:
                pos_ = (y * width + x) * 16

                if toGFD:
                    result[pos:pos + 16] = data[pos_:pos_ + 16]
                else:
                    result[pos_:pos_ + 16] = data[pos:pos + 16]

    return result

# I'd like to give a huge thanks to Exzap for this,
# Thanks Exzap!

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
    if (tileMode == 3 or tileMode == 7 or tileMode == 11 or tileMode == 13 or tileMode == 15):
        thickness = 4
    elif (tileMode == 16 or tileMode == 17):
        thickness = 8
    else:
        thickness = 1
    return thickness

def computePixelIndexWithinMicroTile(x, y, z, bpp, tileMode, microTileType):
    pixelBit6 = 0
    pixelBit7 = 0
    pixelBit8 = 0
    thickness = computeSurfaceThickness(tileMode)

    if microTileType == 3:
        pixelBit0 = x & 1
        pixelBit1 = y & 1
        pixelBit2 = z & 1
        pixelBit3 = (x & 2) >> 1
        pixelBit4 = (y & 2) >> 1
        pixelBit5 = (z & 2) >> 1
        pixelBit6 = (x & 4) >> 2
        pixelBit7 = (y & 4) >> 2
    else:
        if microTileType != 0:
            pixelBit0 = x & 1
            pixelBit1 = y & 1
            pixelBit2 = (x & 2) >> 1
            pixelBit3 = (y & 2) >> 1
            pixelBit4 = (x & 4) >> 2
            pixelBit5 = (y & 4) >> 2
        else:
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
    return (pixelBit8 << 8) | (pixelBit7 << 7) | (pixelBit6 << 6) | 32 * pixelBit5 | 16 * pixelBit4 | 8 * pixelBit3 | 4 * pixelBit2 | pixelBit0 | 2 * pixelBit1

def computePipeFromCoordWoRotation(x, y):
    # hardcoded to assume 2 pipes
    pipe = ((y >> 3) ^ (x >> 3)) & 1
    return pipe

def computeBankFromCoordWoRotation(x, y):
    numPipes = m_pipes
    numBanks = m_banks
    bankOpt = 0
    if numBanks == 4:
        bankBit0 = ((y // (16 * numPipes)) ^ (x >> 3)) & 1
        if (bankOpt == 1 and numPipes == 8):
            bankBit0 ^= x // 0x20 & 1
        bank = bankBit0 | 2 * (((y // (8 * numPipes)) ^ (x >> 4)) & 1)
    elif numBanks == 8:
        bankBit0a = ((y // (32 * numPipes)) ^ (x >> 3)) & 1
        if (bankOpt == 1 and numPipes == 8):
            bankBit0a ^= x // (8 * numBanks) & 1
        bank = bankBit0a | 2 * (((y // (32 * numPipes)) ^ (y // (16 * numPipes) ^ (x >> 4))) & 1) | 4 * (((y // (8 * numPipes)) ^ (x >> 5)) & 1)
    else:
        bank = 0

    return bank

def computeSurfaceRotationFromTileMode(tileMode):
    pipes = m_pipes
    if (tileMode == 4 or tileMode == 5 or tileMode == 6 or tileMode == 7 or tileMode == 8 or tileMode == 9 or tileMode == 10 or tileMode == 11):
        result = pipes * ((m_banks >> 1) - 1)
    elif (tileMode == 12 or tileMode == 13 or tileMode == 14 or tileMode == 15):
        if (pipes > 4 or pipes == 4):
            result = (pipes >> 1) - 1
        else:
            result = 1
    else:
        result = 0
    return result

def isThickMacroTiled(tileMode):
    thickMacroTiled = 0
    if (tileMode == 7 or tileMode == 11 or tileMode == 13 or tileMode == 15):
        thickMacroTiled = 1
    else:
        thickMacroTiled = thickMacroTiled
    return thickMacroTiled

def isBankSwappedTileMode(tileMode):
    bankSwapped = 0
    if (tileMode == 8 or tileMode == 9 or tileMode == 10 or tileMode == 11 or tileMode == 14 or tileMode == 15):
        bankSwapped = 1
    else:
        bankSwapped = bankSwapped
    return bankSwapped

def computeMacroTileAspectRatio(tileMode):
    ratio = 1
    if (tileMode == 8 or tileMode == 12 or tileMode == 14):
        ratio = 1
    elif (tileMode == 5 or tileMode == 9):
        ratio = 2
    elif (tileMode == 6 or tileMode == 10):
        ratio = 4
    else:
        ratio = ratio
    return ratio

def computeSurfaceBankSwappedWidth(tileMode, bpp, numSamples, pitch, pSlicesPerTile):
    bankSwapWidth = 0
    numBanks = m_banks
    numPipes = m_pipes
    swapSize = m_swapSize
    rowSize = m_rowSize
    splitSize = m_splitSize
    groupSize = m_pipeInterleaveBytes
    slicesPerTile = 1
    bytesPerSample = 8 * bpp & 0x1FFFFFFF
    samplesPerTile = splitSize // bytesPerSample
    if (splitSize // bytesPerSample) != 0:
        slicesPerTile = numSamples // samplesPerTile
        if not ((numSamples // samplesPerTile) != 0):
            slicesPerTile = 1
    if pSlicesPerTile != 0:
        pSlicesPerTile = slicesPerTile
    if isThickMacroTiled(tileMode) == 1:
        numSamples = 4
    bytesPerTileSlice = numSamples * bytesPerSample // slicesPerTile
    if isBankSwappedTileMode(tileMode) != 0:
        factor = computeMacroTileAspectRatio(tileMode)
        swapTiles = (swapSize >> 1) // bpp
        if swapTiles != 0:
            v9 = swapTiles
        else:
            v9 = 1
        swapWidth = v9 * 8 * numBanks
        heightBytes = numSamples * factor * numPipes * bpp // slicesPerTile
        swapMax = numPipes * numBanks * rowSize // heightBytes
        swapMin = groupSize * 8 * numBanks // bytesPerTileSlice
        if (swapMax > swapWidth or swapMax == swapWidth):
            if (swapMin < swapWidth or swapMin == swapWidth):
                v7 = swapWidth
            else:
                v7 = swapMin
            v8 = v7
        else:
            v8 = swapMax
        bankSwapWidth = v8
        while (bankSwapWidth > (2 * pitch) or bankSwapWidth == (2 * pitch)): # Let's wish this works :P
            bankSwapWidth >>= 1
    return bankSwapWidth

bankSwapOrder = bytes([0, 1, 3, 2])

def AddrLib_getTileType(isDepth):
    return (1 if isDepth != 0 else 0)

def AddrLib_computePixelIndexWithinMicroTile(x, y, z, bpp, tileMode, microTileType):
    pixelBit6 = 0
    pixelBit7 = 0
    pixelBit8 = 0
    thickness = computeSurfaceThickness(tileMode)
    if microTileType == 3:
        pixelBit0 = x & 1
        pixelBit1 = y & 1
        pixelBit2 = z & 1
        pixelBit3 = (x & 2) >> 1
        pixelBit4 = (y & 2) >> 1
        pixelBit5 = (z & 2) >> 1
        pixelBit6 = (x & 4) >> 2
        pixelBit7 = (y & 4) >> 2
    else:
        if microTileType != 0:
            pixelBit0 = x & 1
            pixelBit1 = y & 1
            pixelBit2 = (x & 2) >> 1
            pixelBit3 = (y & 2) >> 1
            pixelBit4 = (x & 4) >> 2
            pixelBit5 = (y & 4) >> 2
        else:
            v8 = bpp - 8
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
    return (pixelBit8 << 8) | (pixelBit7 << 7) | (pixelBit6 << 6) | 32 * pixelBit5 | 16 * pixelBit4 | 8 * pixelBit3 | 4 * pixelBit2 | pixelBit0 | 2 * pixelBit1

def AddrLib_computeSurfaceAddrFromCoordLinear(x, y, slice, sample, bpp, pitch, height, numSlices, pBitPosition):
    v9 = x + pitch * y + (slice + numSlices * sample) * height * pitch

    addr = v9 * bpp

    pBitPosition = v9 * bpp % 8
    return addr // 8

def AddrLib_computeSurfaceAddrFromCoordMicroTiled(x, y, slice, bpp, pitch, height, tileMode, isDepth, tileBase, compBits, pBitPosition):
    v14 = tileMode
    if tileMode == 3:
        microTileThickness = 4
    else:
        microTileThickness = 1
    microTileBytes = microTileThickness * (((bpp << 6) + 7) >> 3)
    microTilesPerRow = pitch >> 3
    microTileIndexX = x >> 3
    microTileIndexY = y >> 3
    microTileOffset = microTileThickness * (((bpp << 6) + 7) >> 3) * (x >> 3 + (pitch >> 3) * (y >> 3))
    sliceBytes = (height * pitch * microTileThickness * bpp + 7) // 8
    sliceOffset = sliceBytes * (slice // microTileThickness)
    v12 = AddrLib_getTileType(isDepth)
    pixelIndex = AddrLib_computePixelIndexWithinMicroTile(x, y, slice, bpp, tileMode, v12)
    if (compBits != 0 and compBits != bpp and isDepth!= 0):
        pixelOffset = tileBase + compBits * pixelIndex
    else:
        pixelOffset = bpp * pixelIndex
    pBitPosition = pixelOffset % 8
    pixelOffset >>= 3
    return pixelOffset + microTileOffset + sliceOffset

def AddrLib_computeSurfaceAddrFromCoordMacroTiled(x, y, slice, sample, bpp, pitch, height, numSamples, tileMode, isDepth, tileBase, compBits, pipeSwizzle, bankSwizzle, pBitPosition):
    # numSamples is used for AA surfaces and can be set to 1 for all others
    numPipes = m_pipes
    numBanks = m_banks
    numGroupBits = m_pipeInterleaveBytesBitcount
    numPipeBits = m_pipesBitcount
    numBankBits = m_banksBitcount
    microTileThickness = computeSurfaceThickness(tileMode)
    microTileBits = numSamples * bpp * (microTileThickness * (8*8))
    microTileBytes = microTileBits >> 3
    microTileType = (1 if isDepth != 0 else 0)
    pixelIndex = computePixelIndexWithinMicroTile(x, y, slice, bpp, tileMode, microTileType)
    if isDepth != 0:
        if (compBits != 0 and compBits != bpp):
            sampleOffset = tileBase + compBits * sample
            pixelOffset = numSamples * compBits * pixelIndex
        else:
            sampleOffset = bpp * sample
            pixelOffset = numSamples * bpp * pixelIndex
    else:
        sampleOffset = sample * (microTileBits // numSamples)
        pixelOffset = bpp * pixelIndex
    elemOffset = pixelOffset + sampleOffset
    pBitPosition = (pixelOffset + sampleOffset) % 8
    bytesPerSample = microTileBytes // numSamples
    if (numSamples <= 1 or microTileBytes <= m_splitSize):
        samplesPerSlice = numSamples
        numSampleSplits = 1
        sampleSlice = 0
    else:
        samplesPerSlice = m_splitSize // bytesPerSample
        numSampleSplits = numSamples // samplesPerSlice
        numSamples = samplesPerSlice
        tileSliceBits = microTileBits // numSampleSplits
        sampleSlice = elemOffset // (microTileBits // numSampleSplits)
        elemOffset %= microTileBits // numSampleSplits
    elemOffset >>= 3
    pipe = computePipeFromCoordWoRotation(x, y)
    bank = computeBankFromCoordWoRotation(x, y)
    bankPipe = pipe + numPipes * bank
    rotation = computeSurfaceRotationFromTileMode(tileMode)
    swizzle = pipeSwizzle + numPipes * bankSwizzle
    sliceIn = slice
    if isThickMacroTiled(tileMode) != 0:
        sliceIn >>= 2
    bankPipe ^= numPipes * sampleSlice * ((numBanks >> 1) + 1) ^ (swizzle + sliceIn * rotation)
    bankPipe %= numPipes * numBanks
    pipe = bankPipe % numPipes
    bank = bankPipe // numPipes
    sliceBytes = (height * pitch * microTileThickness * bpp * numSamples + 7) // 8
    sliceOffset = sliceBytes * ((sampleSlice + numSampleSplits * slice) // microTileThickness)
    macroTilePitch = 8 * m_banks
    macroTileHeight = 8 * m_pipes
    v18 = tileMode - 5
    if (tileMode == 5 or tileMode == 9): # GX2_TILE_MODE_2D_TILED_THIN4 and GX2_TILE_MODE_2B_TILED_THIN2
        macroTilePitch >>= 1
        macroTileHeight *= 2
    elif (tileMode == 6 or tileMode == 10): # GX2_TILE_MODE_2D_TILED_THIN4 and GX2_TILE_MODE_2B_TILED_THIN4
        macroTilePitch >>= 2
        macroTileHeight *= 4
    macroTilesPerRow = pitch // macroTilePitch
    macroTileBytes = (numSamples * microTileThickness * bpp * macroTileHeight * macroTilePitch + 7) >> 3
    macroTileIndexX = x // macroTilePitch
    macroTileIndexY = y // macroTileHeight
    macroTileOffset = (x // macroTilePitch + pitch // macroTilePitch * (y // macroTileHeight)) * macroTileBytes
    if (tileMode == 8 or tileMode == 9 or tileMode == 10 or tileMode == 11 or tileMode == 14 or tileMode == 15):
        bankSwapWidth = computeSurfaceBankSwappedWidth(tileMode, bpp, numSamples, pitch, 0)
        swapIndex = macroTilePitch * macroTileIndexX // bankSwapWidth
        if m_banks > 4:
            raise ValueError("TODO.")
        bankMask = m_banks-1
        bank ^= bankSwapOrder[swapIndex & bankMask]
    p4 = (pipe << numGroupBits)
    p5 = (bank << (numPipeBits + numGroupBits))
    numSwizzleBits = (numBankBits + numPipeBits)
    ukn1 = ((macroTileOffset + sliceOffset) >> numSwizzleBits)
    ukn2 = ~((1 << numGroupBits) - 1)
    ukn3 = ((elemOffset + ukn1) & ukn2)
    groupMask = ((1 << numGroupBits) - 1)
    offset1 = (macroTileOffset + sliceOffset)
    ukn4 = (elemOffset + (offset1 >> numSwizzleBits))
 
    subOffset1 = (ukn3 << numSwizzleBits)
    subOffset2 = groupMask & ukn4
 
    return subOffset1 | subOffset2 | p4 | p5

def addrLib_computeTileDataWidthAndHeight(bpp, cacheBits, pTileInfo, pMacroWidth, pMacroHeight):
    height = 1
    width = cacheBits // bpp
    pipes = m_pipes
    while (width > (pipes * 2 * height) and (width & 1) == 0):
        width >>= 1
        height *= 2
    pMacroWidth = 8 * width
    pMacroHeight = pipes * 8 * height

def AddrLib_computeCmaskBytes(pitch, height, numSlices):
    return (4 * height * pitch * numSlices + 7) // 8 // 64

def AddrLib__ComputeCmaskBaseAlign(pTileInfo):
    print("AddrLib__ComputeCmaskBaseAlign(): Uknown")
    v2 = 1 # uknown
    return m_pipeInterleaveBytes * v2

def AddrLib_computeCmaskInfo(pitchIn, heightIn, numSlices, isLinear, pTileInfo, pPitchOut, pHeightOut, pCmaskBytes, pMacroWidth, pMacroHeight, pBaseAlign, pBlockMax):
    bpp = 4
    cacheBits = 1024
    returnCode = 0
    if isLinear != 0:
        raise ValueError("Invalid isLinear value!")
    else:
        addrLib_computeTileDataWidthAndHeight(bpp, cacheBits, pTileInfo, macroWidth, macroHeight)
    pPitchOut = ~(macroWidth - 1) & (pitchIn + macroWidth - 1)
    pHeightOut = ~(macroHeight - 1) & (heightIn + macroHeight - 1)
    sliceBytes = AddrLib_computeCmaskBytes(pPitchOut, pHeightOut, 1)
    baseAlign = AddrLib__ComputeCmaskBaseAlign(pTileInfo)
    while 1:
        v14 = sliceBytes % baseAlign
        if not (sliceBytes % baseAlign != 0):
            break
        pHeightOut += macroHeight
        sliceBytes = AddrLib_computeCmaskBytes(pPitchOut, pHeightOut, 1)
    surfBytes = sliceBytes * numSlices
    pCmaskBytes = surfBytes
    pMacroWidth = macroWidth
    pMacroHeight = macroHeight
    pBaseAlign = baseAlign
    slice = pHeightOut * pPitchOut
    blockMax = (slice >> 14) - 1
    # uknown part possibly missing here
    pBlockMax = blockMax
    return returnCode

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
