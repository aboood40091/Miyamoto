#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2017 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7

# addrlib_cy.pyx
# A Cython Address Library for Wii U textures.


################################################################
################################################################

cdef list BCn_formats = [0x31, 0x431, 0x32, 0x432, 0x33, 0x433, 0x34, 0x234, 0x35, 0x235]


cpdef bytearray deswizzle(int width, int height, int height2, int format_, int tileMode, int swizzle_,
                          int pitch, int bpp, bytes data):
    cdef int bpp2
    cdef int pipeSwizzle
    cdef int bankSwizzle
    cdef int pos
    cdef int pos_

    cdef bytearray result = bytearray(data)

    if format_ in BCn_formats:
        width = (width + 3) // 4
        height = (height + 3) // 4

    for y in range(height):
        for x in range(width):
            pipeSwizzle = (swizzle_ >> 8) & 1
            bankSwizzle = (swizzle_ >> 9) & 3

            if tileMode == 0 or tileMode == 1:
                pos = computeSurfaceAddrFromCoordLinear(x, y, bpp, pitch)
            elif tileMode == 2 or tileMode == 3:
                pos = computeSurfaceAddrFromCoordMicroTiled(x, y, bpp, pitch, tileMode)
            else:
                pos = computeSurfaceAddrFromCoordMacroTiled(x, y, bpp, pitch, height2, tileMode,
                                                                              pipeSwizzle, bankSwizzle)

            bpp2 = bpp
            bpp2 //= 8

            pos_ = (y * width + x) * bpp2

            if (pos_ < len(data)) and (pos < len(data)):
                result[pos_:pos_ + bpp2] = data[pos:pos + bpp2]

    return result


cpdef bytearray swizzle(int width, int height, int height2, int format_, int tileMode, int swizzle_,
                          int pitch, int bpp, bytes data):
    cdef int bpp2
    cdef int pipeSwizzle
    cdef int bankSwizzle
    cdef int pos
    cdef int pos_

    cdef bytearray result = bytearray(data)

    if format_ in BCn_formats:
        width = (width + 3) // 4
        height = (height + 3) // 4

    for y in range(height):
        for x in range(width):
            pipeSwizzle = (swizzle_ >> 8) & 1
            bankSwizzle = (swizzle_ >> 9) & 3

            if tileMode == 0 or tileMode == 1:
                pos = computeSurfaceAddrFromCoordLinear(x, y, bpp, pitch)
            elif tileMode == 2 or tileMode == 3:
                pos = computeSurfaceAddrFromCoordMicroTiled(x, y, bpp, pitch, tileMode)
            else:
                pos = computeSurfaceAddrFromCoordMacroTiled(x, y, bpp, pitch, height2, tileMode,
                                                                              pipeSwizzle, bankSwizzle)

            bpp2 = bpp
            bpp2 //= 8

            pos_ = (y * width + x) * bpp2

            if (pos < len(data)) and (pos_ < len(data)):
                result[pos:pos + bpp2] = data[pos_:pos_ + bpp2]

    return result


cdef int m_banks = 4
cdef int m_banksBitcount = 2
cdef int m_pipes = 2
cdef int m_pipesBitcount = 1
cdef int m_pipeInterleaveBytes = 256
cdef int m_pipeInterleaveBytesBitcount = 8
cdef int m_rowSize = 2048
cdef int m_swapSize = 256
cdef int m_splitSize = 2048

cdef int m_chipFamily = 2

cdef int MicroTilePixels = 8 * 8

cdef bytes formatHwInfo = b"\x00\x00\x00\x01\x08\x03\x00\x01\x08\x01\x00\x01\x00\x00\x00\x01" \
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


cpdef int surfaceGetBitsPerPixel(int surfaceFormat):
    cdef int hwFormat = surfaceFormat & 0x3F
    cdef int bpp = formatHwInfo[hwFormat * 4 + 0]

    return bpp


cdef int computeSurfaceThickness(int tileMode):
    cdef int thickness = 1

    if tileMode in [3, 7, 11, 13, 15]:
        thickness = 4

    elif tileMode in [16, 17]:
        thickness = 8

    return thickness


cdef int computePixelIndexWithinMicroTile(int x, int y, int bpp, int tileMode):
    cdef int z = 0
    cdef int thickness
    cdef int pixelBit8
    cdef int pixelBit7
    cdef int pixelBit6
    cdef int pixelBit5
    cdef int pixelBit4
    cdef int pixelBit3
    cdef int pixelBit2
    cdef int pixelBit1
    cdef int pixelBit0
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

    elif bpp in [0x20, 0x60]:
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


cdef int computePipeFromCoordWoRotation(int x, int y):
    # hardcoded to assume 2 pipes
    return ((y >> 3) ^ (x >> 3)) & 1


cdef int computeBankFromCoordWoRotation(int x, int y):
    cdef int numPipes = m_pipes
    cdef int numBanks = m_banks
    cdef int bankBit0
    cdef int bankBit0a
    cdef int bank = 0

    if numBanks == 4:
        bankBit0 = ((y // (16 * numPipes)) ^ (x >> 3)) & 1
        bank = bankBit0 | 2 * (((y // (8 * numPipes)) ^ (x >> 4)) & 1)

    elif numBanks == 8:
        bankBit0a = ((y // (32 * numPipes)) ^ (x >> 3)) & 1
        bank = (bankBit0a | 2 * (((y // (32 * numPipes)) ^ (y // (16 * numPipes) ^ (x >> 4))) & 1) |
                4 * (((y // (8 * numPipes)) ^ (x >> 5)) & 1))

    return bank


cdef int isThickMacroTiled(int tileMode):
    cdef int thickMacroTiled = 0

    if tileMode in [7, 11, 13, 15]:
        thickMacroTiled = 1

    return thickMacroTiled


cdef int isBankSwappedTileMode(int tileMode):
    cdef int bankSwapped = 0

    if tileMode in [8, 9, 10, 11, 14, 15]:
        bankSwapped = 1

    return bankSwapped


cdef int computeMacroTileAspectRatio(int tileMode):
    cdef int ratio = 1

    if tileMode in [8, 12, 14]:
        ratio = 1

    elif tileMode in [5, 9]:
        ratio = 2

    elif tileMode in [6, 10]:
        ratio = 4

    return ratio


cdef int computeSurfaceBankSwappedWidth(int tileMode, int bpp, int pitch, int numSamples=1):
    if isBankSwappedTileMode(tileMode) == 0:
        return 0

    cdef int numBanks = m_banks
    cdef int numPipes = m_pipes
    cdef int swapSize = m_swapSize
    cdef int rowSize = m_rowSize
    cdef int splitSize = m_splitSize
    cdef int groupSize = m_pipeInterleaveBytes
    cdef int bytesPerSample = 8 * bpp
    cdef int samplesPerTile
    cdef int slicesPerTile

    if bytesPerSample != 0:
        samplesPerTile = splitSize // bytesPerSample
        slicesPerTile = max(1, numSamples // samplesPerTile)
    else:
        slicesPerTile = 1

    if isThickMacroTiled(tileMode) != 0:
        numSamples = 4

    cdef int bytesPerTileSlice = numSamples * bytesPerSample // slicesPerTile

    cdef int factor = computeMacroTileAspectRatio(tileMode)
    cdef int swapTiles = max(1, (swapSize >> 1) // bpp)

    cdef int swapWidth = swapTiles * 8 * numBanks
    cdef int heightBytes = numSamples * factor * numPipes * bpp // slicesPerTile
    cdef int swapMax = numPipes * numBanks * rowSize // heightBytes
    cdef int swapMin = groupSize * 8 * numBanks // bytesPerTileSlice

    cdef int bankSwapWidth = min(swapMax, max(swapMin, swapWidth))

    while not bankSwapWidth < (2 * pitch):
        bankSwapWidth >>= 1

    return bankSwapWidth


cpdef int computeSurfaceAddrFromCoordLinear(int x, int y, int bpp, int pitch):
    cdef int rowOffset = y * pitch
    cdef int pixOffset = x

    cdef int addr = (rowOffset + pixOffset) * bpp
    addr //= 8

    return addr


cpdef int computeSurfaceAddrFromCoordMicroTiled(int x, int y, int bpp, int pitch,
                                                       int tileMode):
    cdef int microTileThickness = 1

    if tileMode == 3:
        microTileThickness = 4

    cdef int microTileBytes = (MicroTilePixels * microTileThickness * bpp + 7) // 8
    cdef int microTilesPerRow = pitch >> 3
    cdef int microTileIndexX = x >> 3
    cdef int microTileIndexY = y >> 3

    cdef int microTileOffset = microTileBytes * (microTileIndexX + microTileIndexY * microTilesPerRow)

    cdef int pixelIndex = computePixelIndexWithinMicroTile(x, y, bpp, tileMode)

    cdef int pixelOffset = bpp * pixelIndex

    pixelOffset >>= 3

    return pixelOffset + microTileOffset


cpdef int computeSurfaceAddrFromCoordMacroTiled(int x, int y, int bpp, int pitch, int height,
                                                       int tileMode, int pipeSwizzle,
                                                       int bankSwizzle):
    cdef int sampleSlice
    cdef int numSamples
    cdef int samplesPerSlice
    cdef int numSampleSplits
    cdef list bankSwapOrder
    cdef int bankSwapWidth
    cdef int swapIndex

    cdef int numPipes = m_pipes
    cdef int numBanks = m_banks
    cdef int numGroupBits = m_pipeInterleaveBytesBitcount
    cdef int numPipeBits = m_pipesBitcount
    cdef int numBankBits = m_banksBitcount

    cdef int microTileThickness = computeSurfaceThickness(tileMode)

    cdef int microTileBits = bpp * (microTileThickness * MicroTilePixels)
    cdef int microTileBytes = (microTileBits + 7) // 8

    cdef int pixelIndex = computePixelIndexWithinMicroTile(x, y, bpp, tileMode)

    cdef int pixelOffset = bpp * pixelIndex

    cdef int elemOffset = pixelOffset

    cdef int bytesPerSample = microTileBytes
    if microTileBytes <= m_splitSize:
        numSamples = 1
        sampleSlice = 0
    else:
        samplesPerSlice = m_splitSize // bytesPerSample
        numSampleSplits = max(1, 1 // samplesPerSlice)
        numSamples = samplesPerSlice
        sampleSlice = elemOffset // (microTileBits // numSampleSplits)
        elemOffset %= microTileBits // numSampleSplits
    elemOffset += 7
    elemOffset //= 8

    cdef int pipe = computePipeFromCoordWoRotation(x, y)
    cdef int bank = computeBankFromCoordWoRotation(x, y)

    cdef int bankPipe = pipe + numPipes * bank

    cdef int swizzle_ = pipeSwizzle + numPipes * bankSwizzle

    bankPipe ^= numPipes * sampleSlice * ((numBanks >> 1) + 1) ^ swizzle_
    bankPipe %= numPipes * numBanks
    pipe = bankPipe % numPipes
    bank = bankPipe // numPipes

    cdef int sliceBytes = (height * pitch * microTileThickness * bpp * numSamples + 7) // 8
    cdef int sliceOffset = sliceBytes * (sampleSlice // microTileThickness)

    cdef int macroTilePitch = 8 * m_banks
    cdef int macroTileHeight = 8 * m_pipes

    if tileMode in [5, 9]:  # GX2_TILE_MODE_2D_TILED_THIN4 and GX2_TILE_MODE_2B_TILED_THIN2
        macroTilePitch >>= 1
        macroTileHeight *= 2

    elif tileMode in [6, 10]:  # GX2_TILE_MODE_2D_TILED_THIN4 and GX2_TILE_MODE_2B_TILED_THIN4
        macroTilePitch >>= 2
        macroTileHeight *= 4

    cdef int macroTilesPerRow = pitch // macroTilePitch
    cdef int macroTileBytes = (numSamples * microTileThickness * bpp * macroTileHeight
                               * macroTilePitch + 7) // 8
    cdef int macroTileIndexX = x // macroTilePitch
    cdef int macroTileIndexY = y // macroTileHeight
    cdef int macroTileOffset = (macroTileIndexX + macroTilesPerRow * macroTileIndexY) * macroTileBytes

    if tileMode in [8, 9, 10, 11, 14, 15]:
        bankSwapOrder = [0, 1, 3, 2, 6, 7, 5, 4, 0, 0]
        bankSwapWidth = computeSurfaceBankSwappedWidth(tileMode, bpp, pitch)
        swapIndex = macroTilePitch * macroTileIndexX // bankSwapWidth
        bank ^= bankSwapOrder[swapIndex & (m_banks - 1)]

    cdef int groupMask = ((1 << numGroupBits) - 1)

    cdef int numSwizzleBits = (numBankBits + numPipeBits)

    cdef int totalOffset = (elemOffset + ((macroTileOffset + sliceOffset) >> numSwizzleBits))

    cdef int offsetHigh = (totalOffset & ~groupMask) << numSwizzleBits
    cdef int offsetLow = groupMask & totalOffset

    cdef int pipeBits = pipe << numGroupBits
    cdef int bankBits = bank << (numPipeBits + numGroupBits)

    return bankBits | pipeBits | offsetLow | offsetHigh


cdef int ADDR_OK = 0

pIn = None
pOut = None

cdef int expPitch = 0
cdef int expHeight = 0
cdef int expNumSlices = 0

cdef int m_configFlags = 4


class surfaceIn:
    def __init__(self):
        self.size = 0
        self.tileMode = 0
        self.format = 0
        self.bpp = 0
        self.numSamples = 0
        self.width = 0
        self.height = 0
        self.numSlices = 0
        self.slice = 0
        self.mipLevel = 0
        self.flags = flags()
        self.numFrags = 0
        self.pTileInfo = tileInfo()
        self.tileIndex = 0


class surfaceOut:
    def __init__(self):
        self.size = 0
        self.pitch = 0
        self.height = 0
        self.depth = 0
        self.surfSize = 0
        self.tileMode = 0
        self.baseAlign = 0
        self.pitchAlign = 0
        self.heightAlign = 0
        self.depthAlign = 0
        self.bpp = 0
        self.pixelPitch = 0
        self.pixelHeight = 0
        self.pixelBits = 0
        self.sliceSize = 0
        self.pitchTileMax = 0
        self.heightTileMax = 0
        self.sliceTileMax = 0
        self.pTileInfo = tileInfo()
        self.tileType = 0
        self.tileIndex = 0


class flags:
    def __init__(self):
        self.value = 0


class tileInfo:
    def __init__(self):
        self.banks = 0
        self.bankWidth = 0
        self.bankHeight = 0
        self.macroAspectRatio = 0
        self.tileSplitBytes = 0
        self.pipeConfig = 0


cdef int getFillSizeFieldsFlags():
    return (m_configFlags >> 6) & 1


cdef int getSliceComputingFlags():
    return (m_configFlags >> 4) & 3


cdef int powTwoAlign(int x, int align):
    return ~(align - 1) & (x + align - 1)


cdef int nextPow2(int dim):
    cdef int newDim = 1
    if dim <= 0x7FFFFFFF:
        while newDim < dim:
            newDim *= 2
    else:
        newDim = 2147483648
    return newDim


cdef int useTileIndex(int index):
    return (m_configFlags >> 7) & 1 and index != -1


cdef tuple getBitsPerPixel(int format_):
    cdef int expandY = 1
    cdef int bitUnused = 0
    cdef int elemMode = 3
    cdef int bpp, expandX
    if format_ == 1:
        bpp = 8
        expandX = 1
    elif format_ in [5, 6, 7, 8, 9, 10, 11]:
        bpp = 16
        expandX = 1
    elif format_ == 39:
        elemMode = 7
        bpp = 16
        expandX = 1
    elif format_ == 40:
        elemMode = 8
        bpp = 16
        expandX = 1
    elif format_ in [13, 14, 15, 16, 19, 20, 21, 23, 25, 26]:
        bpp = 32
        expandX = 1
    elif format_ in [29, 30, 31, 32, 62]:
        bpp = 64
        expandX = 1
    elif format_ in [34, 35]:
        bpp = 128
        expandX = 1
    elif format_ == 0:
        bpp = 0
        expandX = 1
    elif format_ == 38:
        elemMode = 6
        bpp = 1
        expandX = 8
    elif format_ == 37:
        elemMode = 5
        bpp = 1
        expandX = 8
    elif format_ in [2, 3]:
        bpp = 8
        expandX = 1
    elif format_ == 12:
        bpp = 16
        expandX = 1
    elif format_ in [17, 18, 22, 24, 27, 41, 42, 43]:
        bpp = 32
        expandX = 1
    elif format_ == 28:
        bpp = 64
        bitUnused = 24
        expandX = 1
    elif format_ == 44:
        elemMode = 4
        bpp = 24
        expandX = 3
    elif format_ in [45, 46]:
        elemMode = 4
        bpp = 48
        expandX = 3
    elif format_ in [47, 48]:
        elemMode = 4
        bpp = 96
        expandX = 3
    elif format_ == 49:
        elemMode = 9
        expandY = 4
        bpp = 64
        expandX = 4
    elif format_ == 52:
        elemMode = 12
        expandY = 4
        bpp = 64
        expandX = 4
    elif format_ == 50:
        elemMode = 10
        expandY = 4
        bpp = 128
        expandX = 4
    elif format_ == 51:
        elemMode = 11
        expandY = 4
        bpp = 128
        expandX = 4
    elif format_ in [53, 54, 55]:
        elemMode = 13
        expandY = 4
        bpp = 128
        expandX = 4
    else:
        bpp = 0
        expandX = 1
    return bpp, expandX, expandY, elemMode


cdef int adjustSurfaceInfo(int elemMode, int expandX, int expandY, int pBpp, int pWidth, int pHeight):
    cdef int bBCnFormat = 0
    cdef int bpp
    cdef int packedBits
    cdef int width
    cdef int height
    cdef int widtha
    cdef int heighta
    cdef int v6
    cdef int v7
    if pBpp:
        bpp = pBpp
        if elemMode == 4:
            packedBits = bpp // expandX // expandY
        elif elemMode in [5, 6]:
            packedBits = expandY * expandX * bpp
        elif elemMode in [7, 8]:
            packedBits = pBpp
        elif elemMode in [9, 12]:
            packedBits = 64
            bBCnFormat = 1
        elif elemMode in [10, 11, 13]:
            bBCnFormat = 1
            packedBits = 128
        elif elemMode in [0, 1, 2, 3]:
            packedBits = pBpp
        else:
            packedBits = pBpp
        pIn.bpp = packedBits
    if pWidth:
        if pHeight:
            width = pWidth
            height = pHeight
            if expandX > 1 or expandY > 1:
                if elemMode == 4:
                    widtha = expandX * width
                    heighta = expandY * height
                elif bBCnFormat:
                    widtha = width // expandX
                    heighta = height // expandY
                else:
                    widtha = (width + expandX - 1) // expandX
                    heighta = (height + expandY - 1) // expandY
                if widtha:
                    v7 = widtha
                else:
                    v7 = 1
                pIn.width = v7
                if heighta:
                    v6 = heighta
                else:
                    v6 = 1
                pIn.height = v6
    return packedBits


cdef int hwlComputeMipLevel():
    cdef int width, widtha
    cdef int height, heighta
    cdef int slices
    cdef int v6, v7
    cdef int handled = 0
    if 49 <= pIn.format <= 55:
        if pIn.mipLevel:
            width = pIn.width
            height = pIn.height
            slices = pIn.numSlices
            if (pIn.flags.value >> 12) & 1:
                widtha = width >> pIn.mipLevel
                heighta = height >> pIn.mipLevel
                if not ((pIn.flags.value >> 4) & 1):
                    slices >>= pIn.mipLevel
                width = max(1, widtha)
                height = max(1, heighta)
                slices = max(1, slices)
            v6 = nextPow2(width)
            v7 = nextPow2(height)
            pIn.width = v6
            pIn.height = v7
            pIn.numSlices = slices
        handled = 1
    return handled


def computeMipLevel():
    cdef int slices = 0
    cdef int height = 0
    cdef int width = 0
    cdef int hwlHandled = 0

    if 49 <= pIn.format <= 55 and (not pIn.mipLevel or ((pIn.flags.value >> 12) & 1)):
        pIn.width = powTwoAlign(pIn.width, 4)
        pIn.height = powTwoAlign(pIn.height, 4)
    hwlHandled = hwlComputeMipLevel()
    if not hwlHandled and pIn.mipLevel and ((pIn.flags.value >> 12) & 1):
        width = pIn.width
        height = pIn.height
        slices = pIn.numSlices
        width >>= pIn.mipLevel
        height >>= pIn.mipLevel
        if not ((pIn.flags.value >> 4) & 1):
            slices >>= pIn.mipLevel
        width = max(1, width)
        height = max(1, height)
        slices = max(1, slices)
        if pIn.format not in [47, 48]:
            width = nextPow2(width)
            height = nextPow2(height)
            slices = nextPow2(slices)
        pIn.width = width
        pIn.height = height
        pIn.numSlices = slices


cdef int convertToNonBankSwappedMode(int tileMode):
    cdef int expTileMode
    if tileMode == 8:
        expTileMode = 4
    elif tileMode == 9:
        expTileMode = 5
    elif tileMode == 10:
        expTileMode = 6
    elif tileMode == 11:
        expTileMode = 7
    elif tileMode == 14:
        expTileMode = 12
    elif tileMode == 15:
        expTileMode = 13
    else:
        expTileMode = tileMode
    return expTileMode


cdef int computeSurfaceTileSlices(int tileMode, int bpp, int numSamples):
    cdef int bytePerSample = ((bpp << 6) + 7) >> 3
    cdef int tileSlices = 1
    cdef int samplePerTile
    if computeSurfaceThickness(tileMode) > 1:
        numSamples = 4
    if bytePerSample:
        samplePerTile = m_splitSize // bytePerSample
        if samplePerTile:
            tileSlices = max(1, numSamples // samplePerTile)
    return tileSlices


cdef int computeSurfaceRotationFromTileMode(tileMode):
    cdef int pipes = m_pipes
    cdef int result = 0
    if tileMode in [4, 5, 6, 7, 8, 9, 10, 11]:
        result = pipes * ((m_banks >> 1) - 1)
    elif tileMode in [12, 13, 14, 15]:
        result = 1
    return result


cdef int computeSurfaceMipLevelTileMode(int baseTileMode, int bpp, int level, int width, int height, int numSlices, int numSamples, int isDepth, int noRecursive):
    cdef int expTileMode = baseTileMode
    cdef int numPipes = m_pipes
    cdef int numBanks = m_banks
    cdef int groupBytes = m_pipeInterleaveBytes
    cdef int tileSlices = computeSurfaceTileSlices(baseTileMode, bpp, numSamples)
    cdef int widtha
    cdef int heighta
    cdef int numSlicesa
    cdef int thickness
    cdef int microTileBytes
    cdef int v13
    cdef int widthAlignFactor
    cdef int macroTileWidth
    cdef int macroTileHeight
    cdef int v11
    if baseTileMode == 5:
        if 2 * m_pipeInterleaveBytes > m_splitSize:
            expTileMode = 4
    elif baseTileMode == 6:
        if 4 * m_pipeInterleaveBytes > m_splitSize:
            expTileMode = 5
    elif baseTileMode == 7:
        if numSamples > 1 or tileSlices > 1 or isDepth:
            expTileMode = 4
    elif baseTileMode == 13:
        if numSamples > 1 or tileSlices > 1 or isDepth:
            expTileMode = 12
    elif baseTileMode == 9:
        if 2 * m_pipeInterleaveBytes > m_splitSize:
            expTileMode = 8
    elif baseTileMode == 10:
        if 4 * m_pipeInterleaveBytes > m_splitSize:
            expTileMode = 9
    elif baseTileMode == 11:
        if numSamples > 1 or tileSlices > 1 or isDepth:
            expTileMode = 8
    elif baseTileMode == 15:
        if numSamples > 1 or tileSlices > 1 or isDepth:
            expTileMode = 14
    elif baseTileMode == 2:
        if numSamples > 1 and ((m_configFlags >> 2) & 1):
            expTileMode = 4
    elif baseTileMode == 3:
        if numSamples > 1 or isDepth:
            expTileMode = 2
        if numSamples in [2, 4]:
            expTileMode = 7
    else:
        expTileMode = baseTileMode
    cdef int rotation = computeSurfaceRotationFromTileMode(expTileMode)
    if not (rotation % m_pipes):
        if expTileMode == 12:
            expTileMode = 4
        if expTileMode == 14:
            expTileMode = 8
        if expTileMode == 13:
            expTileMode = 7
        if expTileMode == 15:
            expTileMode = 11
    if noRecursive:
        result = expTileMode
    else:
        if bpp in [24, 48, 96]:
            bpp //= 3
        widtha = nextPow2(width)
        heighta = nextPow2(height)
        numSlicesa = nextPow2(numSlices)
        if level:
            expTileMode = convertToNonBankSwappedMode(expTileMode)
            thickness = computeSurfaceThickness(expTileMode)
            microTileBytes = (numSamples * bpp * (thickness << 6) + 7) >> 3
            if microTileBytes >= groupBytes:
                v13 = 1
            else:
                v13 = groupBytes // microTileBytes
            widthAlignFactor = v13
            macroTileWidth = 8 * numBanks
            macroTileHeight = 8 * numPipes
            if expTileMode in [4, 12]:
                if (widtha < widthAlignFactor * macroTileWidth) or heighta < macroTileHeight:
                    expTileMode = 2
            elif expTileMode == 5:
                macroTileWidth >>= 1
                macroTileHeight *= 2
                if (widtha < widthAlignFactor * macroTileWidth) or heighta < macroTileHeight:
                    expTileMode = 2
            elif expTileMode == 6:
                macroTileWidth >>= 2
                macroTileHeight *= 4
                if (widtha < widthAlignFactor * macroTileWidth) or heighta < macroTileHeight:
                    expTileMode = 2
            if expTileMode in [7, 13]:
                if (widtha < widthAlignFactor * macroTileWidth) or heighta < macroTileHeight:
                    expTileMode = 3
            v11 = expTileMode
            if expTileMode == 3:
                if numSlicesa < 4:
                    expTileMode = 2
            elif v11 == 7:
                if numSlicesa < 4:
                    expTileMode = 4
            elif v11 == 13 and numSlicesa < 4:
                expTileMode = 12
            result = computeSurfaceMipLevelTileMode(
                expTileMode,
                bpp,
                level,
                widtha,
                heighta,
                numSlicesa,
                numSamples,
                isDepth,
                1)
        else:
            result = expTileMode
    return result


cdef int isDualPitchAlignNeeded(int tileMode, int isDepth, int mipLevel):
    cdef int needed
    if isDepth or mipLevel or m_chipFamily != 1:
        needed = 0
    else:
        if tileMode in [0, 1, 2, 3, 7, 11, 13, 15]:
            needed = 0
        else:
            needed = 1
    return needed


def isPow2(int dim):
    return (dim & (dim - 1)) == 0


cdef tuple padDimensions(int tileMode, int padDims, int isCube, int cubeAsArray, int pitchAlign, int heightAlign, int sliceAlign):
    global expPitch
    global expHeight
    global expNumSlices

    cdef int thickness = computeSurfaceThickness(tileMode)
    if not padDims:
        padDims = 3
    if isPow2(pitchAlign):
        expPitch = powTwoAlign(expPitch, pitchAlign)
    else:
        expPitch = pitchAlign + expPitch - 1
        expPitch //= pitchAlign
        expPitch *= pitchAlign
    if padDims > 1:
        expHeight = powTwoAlign(expHeight, heightAlign)
    if padDims > 2 or thickness > 1:
        if isCube and ((not ((m_configFlags >> 3) & 1)) or cubeAsArray):
            expNumSlices = nextPow2(expNumSlices)
        if thickness > 1:
            expNumSlices = powTwoAlign(expNumSlices, sliceAlign)
    return expPitch, expHeight, expNumSlices


cdef int adjustPitchAlignment(flags, int pitchAlign):
    if (flags.value >> 13) & 1:
        pitchAlign = powTwoAlign(pitchAlign, 0x20)
    return pitchAlign


cdef tuple computeSurfaceAlignmentsLinear(int tileMode, int bpp, flags):
    cdef int pixelsPerPipeInterleave
    cdef int baseAlign
    cdef int pitchAlign
    cdef int heightAlign
    if tileMode:
        if tileMode == 1:
            pixelsPerPipeInterleave = 8 * m_pipeInterleaveBytes // bpp
            baseAlign = m_pipeInterleaveBytes
            pitchAlign = max(0x40, pixelsPerPipeInterleave)
            heightAlign = 1
        else:
            baseAlign = 1
            pitchAlign = 1
            heightAlign = 1
    else:
        baseAlign = 1
        pitchAlign = (1 if bpp != 1 else 8)
        heightAlign = 1
    pitchAlign = adjustPitchAlignment(flags, pitchAlign)
    return baseAlign, pitchAlign, heightAlign


cdef tuple computeSurfaceInfoLinear(int tileMode, int bpp, int numSamples, int pitch, int height, int numSlices, int mipLevel, int padDims, flags):
    global expPitch
    global expHeight
    global expNumSlices

    cdef int valid = 1
    expPitch = pitch
    expHeight = height
    expNumSlices = numSlices
    cdef int microTileThickness = computeSurfaceThickness(tileMode)
    cdef int baseAlign, pitchAlign, heightAlign
    cdef int tileSlices
    cdef int slices
    cdef int pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign
    baseAlign, pitchAlign, heightAlign = computeSurfaceAlignmentsLinear(tileMode, bpp, flags)
    if ((flags.value >> 9) & 1) and not mipLevel:
        expPitch //= 3
        expPitch = nextPow2(expPitch)
    if mipLevel:
        expPitch = nextPow2(expPitch)
        expHeight = nextPow2(expHeight)
        if (flags.value >> 4) & 1:
            expNumSlices = numSlices
            if numSlices <= 1:
                padDims = 2
            else:
                padDims = 0
        else:
            expNumSlices = nextPow2(numSlices)
    expPitch, expHeight, expNumSlices = padDimensions(
        tileMode,
        padDims,
        (flags.value >> 4) & 1,
        (flags.value >> 7) & 1,
        pitchAlign,
        heightAlign,
        microTileThickness)
    if ((flags.value >> 9) & 1) and not mipLevel:
        expPitch *= 3
    tileSlices = numSamples
    slices = expNumSlices * numSamples // microTileThickness
    pPitchOut = expPitch
    pHeightOut = expHeight
    pNumSlicesOut = expNumSlices
    pSurfSize = (expHeight * expPitch * slices * bpp * numSamples + 7) // 8
    pBaseAlign = baseAlign
    pPitchAlign = pitchAlign
    pHeightAlign = heightAlign
    pDepthAlign = microTileThickness
    return valid, pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign


cdef tuple computeSurfaceAlignmentsMicroTiled(int tileMode, int bpp, flags, int numSamples):
    if bpp in [24, 48, 96]:
        bpp //= 3
    cdef int v8 = computeSurfaceThickness(tileMode)
    cdef int baseAlign = m_pipeInterleaveBytes
    cdef int pitchAlign = max(8, m_pipeInterleaveBytes // bpp // numSamples // v8)
    cdef int heightAlign = 8
    pitchAlign = adjustPitchAlignment(flags, pitchAlign)
    return baseAlign, pitchAlign, heightAlign


cdef tuple computeSurfaceInfoMicroTiled(int tileMode, int bpp, int numSamples, int pitch, int height, int numSlices, int mipLevel, int padDims, flags):
    global expPitch
    global expHeight
    global expNumSlices

    cdef int valid = 1
    cdef int expTileMode = tileMode
    expPitch = pitch
    expHeight = height
    expNumSlices = numSlices
    cdef int microTileThickness = computeSurfaceThickness(tileMode)
    cdef int pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pTileModeOut, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign
    if mipLevel:
        expPitch = nextPow2(pitch)
        expHeight = nextPow2(height)
        if (flags.value >> 4) & 1:
            expNumSlices = numSlices
            if numSlices <= 1:
                padDims = 2
            else:
                padDims = 0
        else:
            expNumSlices = nextPow2(numSlices)
        if expTileMode == 3 and expNumSlices < 4:
            expTileMode = 2
            microTileThickness = 1
    baseAlign, pitchAlign, heightAlign = computeSurfaceAlignmentsMicroTiled(
        expTileMode,
        bpp,
        flags,
        numSamples)
    expPitch, expHeight, expNumSlices = padDimensions(
        expTileMode,
        padDims,
        (flags.value >> 4) & 1,
        (flags.value >> 7) & 1,
        pitchAlign,
        heightAlign,
        microTileThickness)
    pPitchOut = expPitch
    pHeightOut = expHeight
    pNumSlicesOut = expNumSlices
    pSurfSize = (expHeight * expPitch * expNumSlices * bpp * numSamples + 7) // 8
    pTileModeOut = expTileMode
    pBaseAlign = baseAlign
    pPitchAlign = pitchAlign
    pHeightAlign = heightAlign
    pDepthAlign = microTileThickness
    return valid, pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pTileModeOut, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign


cdef int isDualBaseAlignNeeded(int tileMode):
    cdef int needed = 1
    if m_chipFamily == 1:
        if tileMode >= 0 and tileMode <= 3:
            needed = 0
    else:
        needed = 0
    return needed


cdef tuple computeSurfaceAlignmentsMacroTiled(int tileMode, int bpp, flags, int numSamples):
    cdef int groupBytes = m_pipeInterleaveBytes
    cdef int numBanks = m_banks
    cdef int numPipes = m_pipes
    cdef int splitBytes = m_splitSize
    cdef int aspectRatio = computeMacroTileAspectRatio(tileMode)
    cdef int thickness = computeSurfaceThickness(tileMode)
    if bpp in [24, 48, 96]:
        bpp //= 3
    if bpp == 3:
        bpp = 1
    cdef int macroTileWidth = 8 * numBanks // aspectRatio
    cdef int macroTileHeight = aspectRatio * 8 * numPipes
    cdef int pitchAlign = max(macroTileWidth, macroTileWidth * (groupBytes // bpp // (8 * thickness) // numSamples))
    pitchAlign = adjustPitchAlignment(flags, pitchAlign)
    cdef int heightAlign = macroTileHeight
    cdef int macroTileBytes = numSamples * ((bpp * macroTileHeight * macroTileWidth + 7) >> 3)
    if m_chipFamily == 1 and numSamples == 1:
        macroTileBytes *= 2
    cdef int baseAlign
    if thickness == 1:
        baseAlign = max(macroTileBytes, (numSamples * heightAlign * bpp * pitchAlign + 7) >> 3)
    else:
        baseAlign = max(groupBytes, (4 * heightAlign * bpp * pitchAlign + 7) >> 3)
    microTileBytes = (thickness * numSamples * (bpp << 6) + 7) >> 3
    cdef int v11
    if microTileBytes < splitBytes:
        v11 = 1
    else:
        v11 = microTileBytes // splitBytes
    cdef int numSlicesPerMicroTile = v11
    baseAlign //= v11
    cdef int macroBytes
    if isDualBaseAlignNeeded(tileMode):
        macroBytes = (bpp * macroTileHeight * macroTileWidth + 7) >> 3
        if baseAlign // macroBytes % 2:
            baseAlign += macroBytes
    return baseAlign, pitchAlign, heightAlign, macroTileWidth, macroTileHeight


cdef tuple computeSurfaceInfoMacroTiled(int tileMode, int baseTileMode, int bpp, int numSamples, int pitch, int height, int numSlices, int mipLevel, int padDims, flags):
    global expPitch
    global expHeight
    global expNumSlices

    cdef int valid = 1
    expPitch = pitch
    expHeight = height
    expNumSlices = numSlices
    cdef int expTileMode = tileMode
    cdef int microTileThickness = computeSurfaceThickness(tileMode)
    cdef int bankSwappedWidth
    cdef int pitchAlign
    cdef int v21
    cdef int tilePerGroup
    cdef int evenHeight
    cdef int evenWidth
    cdef int pitchAlignFactor
    cdef int pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pTileModeOut, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign
    if mipLevel:
        expPitch = nextPow2(pitch)
        expHeight = nextPow2(height)
        if (flags.value >> 4) & 1:
            expNumSlices = numSlices
            padDims = 2 if numSlices <= 1 else 0
        else:
            expNumSlices = nextPow2(numSlices)
        if expTileMode == 7 and expNumSlices < 4:
            expTileMode = 4
            microTileThickness = 1
    if (tileMode == baseTileMode
        or not mipLevel
        or not isThickMacroTiled(baseTileMode)
        or isThickMacroTiled(tileMode)):
        baseAlign, pitchAlign, heightAlign, macroWidth, macroHeight = computeSurfaceAlignmentsMacroTiled(
            tileMode,
            bpp,
            flags,
            numSamples)
        bankSwappedWidth = computeSurfaceBankSwappedWidth(tileMode, bpp, pitch, numSamples)
        if bankSwappedWidth > pitchAlign:
            pitchAlign = bankSwappedWidth
        if isDualPitchAlignNeeded(tileMode, (flags.value >> 1) & 1, mipLevel):
            v21 = (m_pipeInterleaveBytes >> 3) // bpp // numSamples
            tilePerGroup = v21 // computeSurfaceThickness(tileMode)
            if not tilePerGroup:
                tilePerGroup = 1
            evenHeight = (expHeight - 1) // macroHeight & 1
            evenWidth = (expPitch - 1) // macroWidth & 1
            if (numSamples == 1
                and tilePerGroup == 1
                and not evenWidth
                and (expPitch > macroWidth or not evenHeight and expHeight > macroHeight)):
                expPitch += macroWidth
        expPitch, expHeight, expNumSlices = padDimensions(
            tileMode,
            padDims,
            (flags.value >> 4) & 1,
            (flags.value >> 7) & 1,
            pitchAlign,
            heightAlign,
            microTileThickness)
        pPitchOut = expPitch
        pHeightOut = expHeight
        pNumSlicesOut = expNumSlices
        pSurfSize = (expHeight * expPitch * expNumSlices * bpp * numSamples + 7) // 8
        pTileModeOut = expTileMode
        pBaseAlign = baseAlign
        pPitchAlign = pitchAlign
        pHeightAlign = heightAlign
        pDepthAlign = microTileThickness
        result = valid
    else:
        baseAlign, pitchAlign, heightAlign, macroWidth, macroHeight = computeSurfaceAlignmentsMacroTiled(
            baseTileMode,
            bpp,
            flags,
            numSamples)
        pitchAlignFactor = (m_pipeInterleaveBytes >> 3) // bpp
        if not pitchAlignFactor:
            pitchAlignFactor = 1
        if expPitch < pitchAlign * pitchAlignFactor or expHeight < heightAlign:
            expTileMode = 2

            result, pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pTileModeOut, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign = computeSurfaceInfoMicroTiled(
                2,
                bpp,
                numSamples,
                pitch,
                height,
                numSlices,
                mipLevel,
                padDims,
                flags)
        else:
            baseAlign, pitchAlign, heightAlign, macroWidth, macroHeight = computeSurfaceAlignmentsMacroTiled(
                tileMode,
                bpp,
                flags,
                numSamples)
            bankSwappedWidth = computeSurfaceBankSwappedWidth(tileMode, bpp, pitch, numSamples)
            if bankSwappedWidth > pitchAlign:
                pitchAlign = bankSwappedWidth
            if isDualPitchAlignNeeded(tileMode, (flags.value >> 1) & 1, mipLevel):
                v21 = (m_pipeInterleaveBytes >> 3) // bpp // numSamples
                tilePerGroup = v21 // computeSurfaceThickness(tileMode)
                if not tilePerGroup:
                    tilePerGroup = 1
                evenHeight = (expHeight - 1) // macroHeight & 1
                evenWidth = (expPitch - 1) // macroWidth & 1
                if numSamples == 1 and tilePerGroup == 1 and not evenWidth and (expPitch > macroWidth or not evenHeight and expHeight > macroHeight):
                    expPitch += macroWidth
            expPitch, expHeight, expNumSlices = padDimensions(
                tileMode,
                padDims,
                (flags.value >> 4) & 1,
                (flags.value >> 7) & 1,
                pitchAlign,
                heightAlign,
                microTileThickness)
            pPitchOut = expPitch
            pHeightOut = expHeight
            pNumSlicesOut = expNumSlices
            pSurfSize = (expHeight * expPitch * expNumSlices * bpp * numSamples + 7) // 8
            pTileModeOut = expTileMode
            pBaseAlign = baseAlign
            pPitchAlign = pitchAlign
            pHeightAlign = heightAlign
            pDepthAlign = microTileThickness
            result = valid
    return result, pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pTileModeOut, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign


cdef int ComputeSurfaceInfoEx():
    cdef int tileMode = pIn.tileMode
    cdef int bpp = pIn.bpp
    cdef int v6
    if pIn.numSamples:
        v6 = pIn.numSamples
    else:
        v6 = 1
    cdef int numSamples = v6
    cdef int pitch = pIn.width
    cdef int height = pIn.height
    cdef int numSlices = pIn.numSlices
    cdef int mipLevel = pIn.mipLevel
    flags.value = pIn.flags.value
    cdef int pPitchOut = pOut.pitch
    cdef int pHeightOut = pOut.height
    cdef int pNumSlicesOut = pOut.depth
    cdef int pTileModeOut = pOut.tileMode
    cdef int pSurfSize = pOut.surfSize
    cdef int pBaseAlign = pOut.baseAlign
    cdef int pPitchAlign = pOut.pitchAlign
    cdef int pHeightAlign = pOut.heightAlign
    cdef int pDepthAlign = pOut.depthAlign
    cdef int padDims = 0
    cdef int valid = 0
    cdef int baseTileMode = tileMode
    cdef int result
    if ((flags.value >> 4) & 1) and not mipLevel:
        padDims = 2
    if ((flags.value >> 6) & 1):
        tileMode = convertToNonBankSwappedMode(tileMode)
    else:
        tileMode = computeSurfaceMipLevelTileMode(
            tileMode,
            bpp,
            mipLevel,
            pitch,
            height,
            numSlices,
            numSamples,
            (flags.value >> 1) & 1,
            0)
    if tileMode in [0, 1]:
        valid, pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign = computeSurfaceInfoLinear(
            tileMode,
            bpp,
            numSamples,
            pitch,
            height,
            numSlices,
            mipLevel,
            padDims,
            flags)
        pTileModeOut = tileMode
    elif tileMode in [2, 3]:
        valid, pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pTileModeOut, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign = computeSurfaceInfoMicroTiled(
            tileMode,
            bpp,
            numSamples,
            pitch,
            height,
            numSlices,
            mipLevel,
            padDims,
            flags)
    elif tileMode in [4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]:
        valid, pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pTileModeOut, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign = computeSurfaceInfoMacroTiled(
            tileMode,
            baseTileMode,
            bpp,
            numSamples,
            pitch,
            height,
            numSlices,
            mipLevel,
            padDims,
            flags)
    result = 0
    if valid == 0:
        result = 3

    pOut.pitch = pPitchOut
    pOut.height = pHeightOut
    pOut.depth = pNumSlicesOut
    pOut.tileMode = pTileModeOut
    pOut.surfSize = pSurfSize
    pOut.baseAlign = pBaseAlign
    pOut.pitchAlign = pPitchAlign
    pOut.heightAlign = pHeightAlign
    pOut.depthAlign = pDepthAlign

    return result


cdef int restoreSurfaceInfo(elemMode, expandX, expandY, bpp):
    cdef int originalBits
    cdef int width
    cdef int height
    cdef int v6
    cdef int v7
    if bpp:
        if elemMode == 4:
            originalBits = expandY * expandX * bpp
        elif elemMode in [5, 6]:
            originalBits = bpp // expandX // expandY
        elif elemMode in [7, 8]:
            originalBits = bpp
        elif elemMode in [9, 12]:
            originalBits = 64
        elif elemMode in [10, 11, 13]:
            originalBits = 128
        elif elemMode in [0, 1, 2, 3]:
            originalBits = bpp
        else:
            originalBits = bpp
        bpp = originalBits
    if pOut.pixelPitch and pOut.pixelHeight:
        width = pOut.pixelPitch
        height = pOut.pixelHeight
        if expandX > 1 or expandY > 1:
            if elemMode == 4:
                width //= expandX
                height //= expandY
            else:
                width *= expandX
                height *= expandY
        if width:
            v7 = width
        else:
            v7 = 1
        pOut.pixelPitch = v7
        if height:
            v6 = height
        else:
            v6 = 1
        pOut.pixelHeight = v6
    return bpp


def computeSurfaceInfo(aSurfIn, pSurfOut):
    global pIn
    pIn = aSurfIn
    global pOut
    pOut = pSurfOut
    cdef int v4 = 0
    cdef int v6 = 0
    cdef int v7 = 0
    cdef int v8 = 0
    cdef int v10 = 0
    cdef int v11 = 0
    cdef int v12 = 0
    cdef int v14 = 0
    cdef int v16 = 0
    cdef int v17 = 0
    cdef int v18 = 0
    tileInfoNull = tileInfo()
    cdef int sliceFlags = 0
    cdef int returnCode
    cdef int width
    cdef int height
    cdef int bpp
    cdef int elemMode
    cdef int expandY
    cdef int expandX
    cdef int sliceTileMax

    returnCode = 0
    if getFillSizeFieldsFlags() == 1 and (pIn.size != 60 or pOut.size != 96):  # --> m_configFlags.value = 4
        returnCode = 6
    # v3 = pIn
    if pIn.bpp > 0x80:
        returnCode = 3
    if returnCode == ADDR_OK:
        v18 = 0
        computeMipLevel()
        width = pIn.width
        height = pIn.height
        bpp = pIn.bpp
        expandX = 1
        expandY = 1
        sliceFlags = getSliceComputingFlags()
        if useTileIndex(pIn.tileIndex) and (not pIn.pTileInfo):
            if pOut.pTileInfo:
                pIn.pTileInfo = pOut.pTileInfo
            else:
                pOut.pTileInfo = tileInfoNull
                pIn.pTileInfo = tileInfoNull
        returnCode = 0  # does nothing
        if returnCode == ADDR_OK:
            pOut.pixelBits = pIn.bpp
            # v3 = pIn
            if pIn.format:
                v18 = 1
                v4 = pIn.format
                bpp, expandX, expandY, elemMode = getBitsPerPixel(v4)
                if elemMode == 4 and expandX == 3 and pIn.tileMode == 1:
                    pIn.flags.value |= 0x200
                v6 = expandY
                v7 = expandX
                v8 = elemMode
                bpp = adjustSurfaceInfo(v8, v7, v6, bpp, width, height)
            elif pIn.bpp:
                if pIn.width:
                    v17 = pIn.width
                else:
                    v17 = 1
                pIn.width = v17
                if pIn.height:
                    v16 = pIn.height
                else:
                    v16 = 1
                pIn.height = v16
            else:
                returnCode = 3
        if returnCode == ADDR_OK:
            returnCode = ComputeSurfaceInfoEx()
        if returnCode == ADDR_OK:
            pOut.bpp = pIn.bpp
            pOut.pixelPitch = pOut.pitch
            pOut.pixelHeight = pOut.height
            if pIn.format and (not ((pIn.flags.value >> 9) & 1) or not pIn.mipLevel):
                if not v18:
                    return
                v10 = expandY
                v11 = expandX
                v12 = elemMode
                bpp = restoreSurfaceInfo(v12, v11, v10, bpp)
            if sliceFlags:
                if sliceFlags == 1:
                    pOut.sliceSize = (pOut.height * pOut.pitch * pOut.bpp * pIn.numSamples + 7) // 8
            elif (pIn.flags.value >> 5) & 1:
                pOut.sliceSize = pOut.surfSize
            else:
                v14 = (pOut.surfSize >> 32)
                pOut.sliceSize = pOut.surfSize // pOut.depth
                if pIn.slice == (pIn.numSlices - 1) and pIn.numSlices > 1:
                    pOut.sliceSize += pOut.sliceSize * (pOut.depth - pIn.numSlices)
            pOut.pitchTileMax = (pOut.pitch >> 3) - 1
            pOut.heightTileMax = (pOut.height >> 3) - 1
            sliceTileMax = ((pOut.height * pOut.pitch >> 6) - 1)
            pOut.sliceTileMax = sliceTileMax


cpdef getSurfaceInfo(int surfaceFormat, int surfaceWidth, int surfaceHeight, int surfaceDepth, int surfaceDim, int surfaceTileMode, int surfaceAA, int level):
    cdef int v3 = 0
    cdef int v4 = 0
    cdef int v5 = 0
    cdef int v6 = 0
    cdef int v7 = 0
    cdef int v8 = 0
    cdef int v9 = 0
    cdef int v10 = 0
    cdef int v12 = 0
    cdef int newHeight = 0
    cdef int v14 = 0
    cdef int v15 = 0
    cdef int v16 = 0
    cdef int v17 = 0
    cdef int v18 = 0
    cdef int v19 = 0
    cdef int v20 = 0
    cdef int v21 = 0
    cdef int v22 = 0
    cdef int dim = 0
    cdef int v24 = 0
    cdef int width = 0
    cdef int blockSize = 0
    cdef int numSamples = 0
    cdef int hwFormat = 0
    aSurfIn = surfaceIn()
    pSurfOut = surfaceOut()

    hwFormat = surfaceFormat & 0x3F
    if surfaceTileMode == 16:
        numSamples = 1 << surfaceAA
        if hwFormat < 0x31 or hwFormat > 0x35:
            v24 = 1
        else:
            v24 = 4
        blockSize = v24
        width = ~(v24 - 1) & ((surfaceWidth >> level) + v24 - 1)
        if hwFormat == 0x35:
            return
        pSurfOut.bpp = formatHwInfo[hwFormat * 4]
        pSurfOut.size = 96
        pSurfOut.pitch = width // blockSize
        pSurfOut.pixelBits = formatHwInfo[hwFormat * 4]
        pSurfOut.baseAlign = 1
        pSurfOut.pitchAlign = 1
        pSurfOut.heightAlign = 1
        pSurfOut.depthAlign = 1
        dim = surfaceDim
        if dim == 0:
            pSurfOut.height = 1
            pSurfOut.depth = 1
        elif dim == 1:
            pSurfOut.height = surfaceHeight >> level
            if pSurfOut.height >= 1:
                v22 = pSurfOut.height
            else:
                v22 = 1
            pSurfOut.height = v22
            pSurfOut.depth = 1
        elif dim == 2:
            pSurfOut.height = surfaceHeight >> level
            if pSurfOut.height >= 1:
                v21 = pSurfOut.height
            else:
                v21 = 1
            pSurfOut.height = v21
            pSurfOut.depth = surfaceDepth >> level
            if pSurfOut.depth >= 1:
                v20 = pSurfOut.depth
            else:
                v20 = 1
            pSurfOut.depth = v20
        elif dim == 3:
            pSurfOut.height = surfaceHeight >> level
            if pSurfOut.height >= 1:
                v19 = pSurfOut.height
            else:
                v19 = 1
            pSurfOut.height = v19
            if surfaceDepth >= 6:
                v18 = surfaceDepth
            else:
                v18 = 6
            pSurfOut.depth = v18
        elif dim == 4:
            pSurfOut.height = 1
            pSurfOut.depth = surfaceDepth
        elif dim == 5:
            pSurfOut.height = surfaceHeight >> level
            if pSurfOut.height >= 1:
                v17 = pSurfOut.height
            else:
                v17 = 1
            pSurfOut.height = v17
            pSurfOut.depth = surfaceDepth
        pSurfOut.height = (~(blockSize - 1) & (pSurfOut.height + blockSize - 1)) // blockSize
        pSurfOut.pixelPitch = ~(blockSize - 1) & ((surfaceWidth >> level) + blockSize - 1)
        if blockSize <= pSurfOut.pixelPitch:
            v16 = pSurfOut.pixelPitch
        else:
            v16 = blockSize
        pSurfOut.pixelPitch = v16
        pSurfOut.pixelHeight = ~(blockSize - 1) & ((surfaceHeight >> level) + blockSize - 1)
        if blockSize <= pSurfOut.pixelHeight:
            v15 = pSurfOut.pixelHeight
        else:
            v15 = blockSize
        pSurfOut.pixelHeight = v15
        if pSurfOut.pitch >= 1:
            v14 = pSurfOut.pitch
        else:
            v14 = 1
        pSurfOut.pitch = v14
        if pSurfOut.height >= 1:
            newHeight = pSurfOut.height
        else:
            newHeight = 1
        pSurfOut.height = newHeight
        pSurfOut.surfSize = pSurfOut.bpp * numSamples * pSurfOut.depth * pSurfOut.height * pSurfOut.pitch >> 3
        if surfaceDim == 2:
            pSurfOut.sliceSize = pSurfOut.surfSize
        else:
            pSurfOut.sliceSize = pSurfOut.surfSize // pSurfOut.depth
        pSurfOut.pitchTileMax = (pSurfOut.pitch >> 3) - 1
        pSurfOut.heightTileMax = (pSurfOut.height >> 3) - 1
        pSurfOut.sliceTileMax = (pSurfOut.height * pSurfOut.pitch >> 6) - 1
    else:
        aSurfIn.size = 60
        aSurfIn.tileMode = surfaceTileMode & 0xF
        aSurfIn.format = hwFormat
        aSurfIn.bpp = formatHwInfo[hwFormat * 4]
        aSurfIn.numSamples = 1 << surfaceAA
        aSurfIn.numFrags = aSurfIn.numSamples
        aSurfIn.width = surfaceWidth >> level
        if aSurfIn.width >= 1:
            v12 = aSurfIn.width
        else:
            v12 = 1
        aSurfIn.width = v12
        dim = surfaceDim
        if dim == 0:
            aSurfIn.height = 1
            aSurfIn.numSlices = 1
        elif dim == 1:
            aSurfIn.height = surfaceHeight >> level
            if aSurfIn.height >= 1:
                v10 = aSurfIn.height
            else:
                v10 = 1
            aSurfIn.height = v10
            aSurfIn.numSlices = 1
        elif dim == 2:
            aSurfIn.height = surfaceHeight >> level
            if aSurfIn.height >= 1:
                v9 = aSurfIn.height
            else:
                v9 = 1
            aSurfIn.height = v9
            aSurfIn.numSlices = surfaceDepth >> level
            if aSurfIn.numSlices >= 1:
                v8 = aSurfIn.numSlices
            else:
                v8 = 1
            aSurfIn.numSlices = v8
        elif dim == 3:
            aSurfIn.height = surfaceHeight >> level
            if aSurfIn.height >= 1:
                v7 = aSurfIn.height
            else:
                v7 = 1
            aSurfIn.height = v7
            if surfaceDepth >= 6:
                v6 = surfaceDepth
            else:
                v6 = 6
            aSurfIn.numSlices = v6
            aSurfIn.flags.value |= 0x10
        elif dim == 4:
            aSurfIn.height = 1
            aSurfIn.numSlices = surfaceDepth
        elif dim == 5:
            aSurfIn.height = surfaceHeight >> level
            if aSurfIn.height >= 1:
                v5 = aSurfIn.height
            else:
                v5 = 1
            aSurfIn.height = v5
            aSurfIn.numSlices = surfaceDepth
        elif dim == 6:
            aSurfIn.height = surfaceHeight >> level
            if aSurfIn.height >= 1:
                v4 = aSurfIn.height
            else:
                v4 = 1
            aSurfIn.height = v4
            aSurfIn.numSlices = 1
        elif dim == 7:
            aSurfIn.height = surfaceHeight >> level
            if aSurfIn.height >= 1:
                v3 = aSurfIn.height
            else:
                v3 = 1
            aSurfIn.height = v3
            aSurfIn.numSlices = surfaceDepth
        aSurfIn.slice = 0
        aSurfIn.mipLevel = level
        if surfaceDim == 2:
            aSurfIn.flags.value |= 0x20
        aSurfIn.flags.value = ((1 if level == 0 else 0) << 12) | aSurfIn.flags.value & 0xFFFFEFFF
        pSurfOut.size = 96
        computeSurfaceInfo(aSurfIn, pSurfOut)
        pSurfOut = pOut

    return pSurfOut
