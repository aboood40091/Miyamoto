#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# addrlib_cy.pyx
# A Cython Address Library for Wii U textures.


################################################################
################################################################

from cpython cimport array
from cython cimport view
from libc.stdlib cimport malloc, free
from libc.string cimport memcpy


ctypedef unsigned char u8
ctypedef unsigned int u32
ctypedef long long int64
ctypedef unsigned long long u64


cdef list BCn_formats = [
    0x31, 0x431, 0x32, 0x432,
    0x33, 0x433, 0x34, 0x234,
    0x35, 0x235,
]


cdef bytes swizzleSurf(u32 width, u32 height, u32 height_, u32 format_, u32 tileMode, u32 swizzle_,
                           u32 pitch, u32 bitsPerPixel, u8 *data, u32 dataSize, int swizzle):

    cdef:
        u32 bytesPerPixel = bitsPerPixel // 8
        u8 *result = <u8 *>malloc(dataSize)

        u32 pipeSwizzle, bankSwizzle, y, x, pos_
        u64 pos

    if format_ in BCn_formats:
        width = (width + 3) // 4
        height = (height + 3) // 4

    try:
        for y in range(height):
            for x in range(width):
                pipeSwizzle = (swizzle_ >> 8) & 1
                bankSwizzle = (swizzle_ >> 9) & 3

                if tileMode in [0, 1]:
                    pos = computeSurfaceAddrFromCoordLinear(x, y, bitsPerPixel, pitch)

                elif tileMode in [2, 3]:
                    pos = computeSurfaceAddrFromCoordMicroTiled(x, y, bitsPerPixel, pitch, tileMode)

                else:
                    pos = computeSurfaceAddrFromCoordMacroTiled(x, y, bitsPerPixel, pitch, height_, tileMode,
                                                                pipeSwizzle, bankSwizzle)

                pos_ = (y * width + x) * bytesPerPixel

                if pos_ + bytesPerPixel < dataSize and pos + bytesPerPixel < dataSize:
                    if swizzle == 0:
                        memcpy(result + pos_, data + pos, bytesPerPixel)

                    else:
                        memcpy(result + pos, data + pos_, bytesPerPixel)

        return bytes(<u8[:dataSize]>result)

    finally:
        free(result)


cpdef bytes deswizzle(u32 width, u32 height, u32 height_, u32 format_, u32 tileMode, u32 swizzle_,
                          u32 pitch, u32 bpp, bytes data):

    cdef array.array dataArr = array.array('B', data)

    return swizzleSurf(width, height, height_, format_, tileMode, swizzle_, pitch, bpp,
                       dataArr.data.as_uchars, len(data), 0)


cpdef bytes swizzle(u32 width, u32 height, u32 height_, u32 format_, u32 tileMode, u32 swizzle_,
                          u32 pitch, u32 bpp, bytes data):

    cdef array.array dataArr = array.array('B', data)

    return swizzleSurf(width, height, height_, format_, tileMode, swizzle_, pitch, bpp,
                       dataArr.data.as_uchars, len(data), 1)


cdef:
    u32 m_banks = 4
    u32 m_banksBitcount = 2
    u32 m_pipes = 2
    u32 m_pipesBitcount = 1
    u32 m_pipeInterleaveBytes = 256
    u32 m_pipeInterleaveBytesBitcount = 8
    u32 m_rowSize = 2048
    u32 m_swapSize = 256
    u32 m_splitSize = 2048

    u32 m_chipFamily = 2

    u32 MicroTilePixels = 64

    u8 formatHwInfo[0x100]

formatHwInfo[:] = [
    0x00, 0x00, 0x00, 0x01, 0x08, 0x03, 0x00, 0x01, 0x08, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x01, 0x10, 0x07, 0x00, 0x00, 0x10, 0x03, 0x00, 0x01, 0x10, 0x03, 0x00, 0x01,
    0x10, 0x0B, 0x00, 0x01, 0x10, 0x01, 0x00, 0x01, 0x10, 0x03, 0x00, 0x01, 0x10, 0x03, 0x00, 0x01,
    0x10, 0x03, 0x00, 0x01, 0x20, 0x03, 0x00, 0x00, 0x20, 0x07, 0x00, 0x00, 0x20, 0x03, 0x00, 0x00,
    0x20, 0x03, 0x00, 0x01, 0x20, 0x05, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20, 0x03, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x20, 0x03, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x00, 0x00, 0x00, 0x01, 0x20, 0x0B, 0x00, 0x01, 0x20, 0x0B, 0x00, 0x01, 0x20, 0x0B, 0x00, 0x01,
    0x40, 0x05, 0x00, 0x00, 0x40, 0x03, 0x00, 0x00, 0x40, 0x03, 0x00, 0x00, 0x40, 0x03, 0x00, 0x00,
    0x40, 0x03, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x80, 0x03, 0x00, 0x00, 0x80, 0x03, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x10, 0x01, 0x00, 0x00,
    0x10, 0x01, 0x00, 0x00, 0x20, 0x01, 0x00, 0x00, 0x20, 0x01, 0x00, 0x00, 0x20, 0x01, 0x00, 0x00,
    0x00, 0x01, 0x00, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x60, 0x01, 0x00, 0x00,
    0x60, 0x01, 0x00, 0x00, 0x40, 0x01, 0x00, 0x01, 0x80, 0x01, 0x00, 0x01, 0x80, 0x01, 0x00, 0x01,
    0x40, 0x01, 0x00, 0x01, 0x80, 0x01, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
]


cpdef u32 surfaceGetBitsPerPixel(u32 surfaceFormat):
    cdef:
        u32 hwFormat = surfaceFormat & 0x3F
        u32 bpp = formatHwInfo[hwFormat * 4]

    return bpp


cdef u32 computeSurfaceThickness(u32 tileMode):
    cdef u32 thickness = 1

    if tileMode in [3, 7, 11, 13, 15]:
        thickness = 4

    elif tileMode in [16, 17]:
        thickness = 8

    return thickness


cdef u32 computePixelIndexWithinMicroTile(u32 x, u32 y, u32 bpp, u32 tileMode):
    cdef:
        u32 z = 0

        u32 thickness, pixelBit8, pixelBit7, pixelBit6, pixelBit5
        u32 pixelBit4, pixelBit3, pixelBit2, pixelBit1, pixelBit0

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


cdef u32 computePipeFromCoordWoRotation(u32 x, u32 y):
    # hardcoded to assume 2 pipes
    return ((y >> 3) ^ (x >> 3)) & 1


cdef u32 computeBankFromCoordWoRotation(u32 x, u32 y):
    cdef:
        u32 numPipes = m_pipes
        u32 numBanks = m_banks

        u32 bankBit0, bankBit0a

        u32 bank = 0

    if numBanks == 4:
        bankBit0 = ((y // (16 * numPipes)) ^ (x >> 3)) & 1
        bank = bankBit0 | 2 * (((y // (8 * numPipes)) ^ (x >> 4)) & 1)

    elif numBanks == 8:
        bankBit0a = ((y // (32 * numPipes)) ^ (x >> 3)) & 1
        bank = (bankBit0a | 2 * (((y // (32 * numPipes)) ^ (y // (16 * numPipes) ^ (x >> 4))) & 1) |
                4 * (((y // (8 * numPipes)) ^ (x >> 5)) & 1))

    return bank


cdef u32 isThickMacroTiled(u32 tileMode):
    cdef u32 thickMacroTiled = 0

    if tileMode in [7, 11, 13, 15]:
        thickMacroTiled = 1

    return thickMacroTiled


cdef u32 isBankSwappedTileMode(u32 tileMode):
    cdef u32 bankSwapped = 0

    if tileMode in [8, 9, 10, 11, 14, 15]:
        bankSwapped = 1

    return bankSwapped


cdef u32 computeMacroTileAspectRatio(u32 tileMode):
    cdef u32 ratio = 1

    if tileMode in [8, 12, 14]:
        ratio = 1

    elif tileMode in [5, 9]:
        ratio = 2

    elif tileMode in [6, 10]:
        ratio = 4

    return ratio


cdef u32 computeSurfaceBankSwappedWidth(u32 tileMode, u32 bpp, u32 pitch, u32 numSamples):
    if isBankSwappedTileMode(tileMode) == 0:
        return 0

    cdef:
        u32 numBanks = m_banks
        u32 numPipes = m_pipes
        u32 swapSize = m_swapSize
        u32 rowSize = m_rowSize
        u32 splitSize = m_splitSize
        u32 groupSize = m_pipeInterleaveBytesBitcount
        u32 bytesPerSample = 8 * bpp

        u32 samplesPerTile, slicesPerTile

    if bytesPerSample != 0:
        samplesPerTile = splitSize // bytesPerSample
        slicesPerTile = max(1, numSamples // samplesPerTile)
    else:
        slicesPerTile = 1

    if isThickMacroTiled(tileMode) != 0:
        numSamples = 4

    cdef:
        u32 bytesPerTileSlice = numSamples * bytesPerSample // slicesPerTile

        u32 factor = computeMacroTileAspectRatio(tileMode)
        u32 swapTiles = max(1, (swapSize >> 1) // bpp)

        u32 swapWidth = swapTiles * 8 * numBanks
        u32 heightBytes = numSamples * factor * numPipes * bpp // slicesPerTile
        u32 swapMax = numPipes * numBanks * rowSize // heightBytes
        u32 swapMin = groupSize * 8 * numBanks // bytesPerTileSlice

        u32 bankSwapWidth = min(swapMax, max(swapMin, swapWidth))

    while bankSwapWidth >= 2 * pitch:
        bankSwapWidth >>= 1

    return bankSwapWidth


cdef u64 computeSurfaceAddrFromCoordLinear(u32 x, u32 y, u32 bpp, u32 pitch):
    cdef:
        u64 rowOffset = y * pitch
        u64 pixOffset = x

        u64 addr = (rowOffset + pixOffset) * bpp

    addr //= 8

    return addr


cdef u64 computeSurfaceAddrFromCoordMicroTiled(u32 x, u32 y, u32 bpp, u32 pitch,
                                                       u32 tileMode):
    cdef int microTileThickness = 1

    if tileMode == 3:
        microTileThickness = 4

    cdef:
        u32 microTileBytes = (MicroTilePixels * microTileThickness * bpp + 7) // 8
        u32 microTilesPerRow = pitch >> 3
        u32 microTileIndexX = x >> 3
        u32 microTileIndexY = y >> 3

        u64 microTileOffset = microTileBytes * (microTileIndexX + microTileIndexY * microTilesPerRow)

        u32 pixelIndex = computePixelIndexWithinMicroTile(x, y, bpp, tileMode)

        u64 pixelOffset = bpp * pixelIndex

    pixelOffset >>= 3

    return pixelOffset + microTileOffset


cdef u8 bankSwapOrder[10]
bankSwapOrder[:] = [0, 1, 3, 2, 6, 7, 5, 4, 0, 0]


cdef u64 computeSurfaceAddrFromCoordMacroTiled(u32 x, u32 y, u32 bpp, u32 pitch, u32 height,
                                                       u32 tileMode, u32 pipeSwizzle,
                                                       u32 bankSwizzle):

    cdef:
        u32 sampleSlice, numSamples, samplesPerSlice
        u32 numSampleSplits, bankSwapWidth, swapIndex

        u32 numPipes = m_pipes
        u32 numBanks = m_banks
        u32 numGroupBits = m_pipeInterleaveBytesBitcount
        u32 numPipeBits = m_pipesBitcount
        u32 numBankBits = m_banksBitcount

        u32 microTileThickness = computeSurfaceThickness(tileMode)

        u32 microTileBits = bpp * (microTileThickness * MicroTilePixels)
        u32 microTileBytes = (microTileBits + 7) // 8

        u32 pixelIndex = computePixelIndexWithinMicroTile(x, y, bpp, tileMode)

        u64 pixelOffset = bpp * pixelIndex

        u64 elemOffset = pixelOffset

        u32 bytesPerSample = microTileBytes

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

    cdef:
        u32 pipe = computePipeFromCoordWoRotation(x, y)
        u32 bank = computeBankFromCoordWoRotation(x, y)

        u32 bankPipe = pipe + numPipes * bank

        u32 swizzle_ = pipeSwizzle + numPipes * bankSwizzle

    bankPipe ^= numPipes * sampleSlice * ((numBanks >> 1) + 1) ^ swizzle_
    bankPipe %= numPipes * numBanks
    pipe = bankPipe % numPipes
    bank = bankPipe // numPipes

    cdef:
        u32 sliceBytes = (height * pitch * microTileThickness * bpp * numSamples + 7) // 8
        u32 sliceOffset = sliceBytes * (sampleSlice // microTileThickness)

        u32 macroTilePitch = 8 * m_banks
        u32 macroTileHeight = 8 * m_pipes

    if tileMode in [5, 9]:  # GX2_TILE_MODE_2D_TILED_THIN2 and GX2_TILE_MODE_2B_TILED_THIN2
        macroTilePitch >>= 1
        macroTileHeight *= 2

    elif tileMode in [6, 10]:  # GX2_TILE_MODE_2D_TILED_THIN4 and GX2_TILE_MODE_2B_TILED_THIN4
        macroTilePitch >>= 2
        macroTileHeight *= 4

    cdef:
        u32 macroTilesPerRow = pitch // macroTilePitch
        u32 macroTileBytes = (numSamples * microTileThickness * bpp * macroTileHeight
                              * macroTilePitch + 7) // 8
        u32 macroTileIndexX = x // macroTilePitch
        u32 macroTileIndexY = y // macroTileHeight
        u64 macroTileOffset = (macroTileIndexX + macroTilesPerRow * macroTileIndexY) * macroTileBytes

    if tileMode in [8, 9, 10, 11, 14, 15]:
        bankSwapWidth = computeSurfaceBankSwappedWidth(tileMode, bpp, pitch, 1)
        swapIndex = macroTilePitch * macroTileIndexX // bankSwapWidth
        bank ^= bankSwapOrder[swapIndex & (m_banks - 1)]

    cdef:
        u32 groupMask = ((1 << numGroupBits) - 1)

        u32 numSwizzleBits = (numBankBits + numPipeBits)

        u64 totalOffset = (elemOffset + ((macroTileOffset + sliceOffset) >> numSwizzleBits))

        u64 offsetHigh = (totalOffset & ~groupMask) << numSwizzleBits
        u64 offsetLow = groupMask & totalOffset

        u64 pipeBits = pipe << numGroupBits
        u64 bankBits = bank << (numPipeBits + numGroupBits)

    return bankBits | pipeBits | offsetLow | offsetHigh


cdef:
    u32 ADDR_OK = 0

    u32 expPitch = 0
    u32 expHeight = 0
    u32 expNumSlices = 0

    u32 m_configFlags = 4


cdef class Flags:
    cdef u32 value

    def __cinit__(self):
        self.value = 0


cdef class tileInfo:
    cdef u32 banks
    cdef u32 bankWidth
    cdef u32 bankHeight
    cdef u32 macroAspectRatio
    cdef u32 tileSplitBytes
    cdef u32 pipeConfig

    def __cinit__(self):
        self.banks = 0
        self.bankWidth = 0
        self.bankHeight = 0
        self.macroAspectRatio = 0
        self.tileSplitBytes = 0
        self.pipeConfig = 0


cdef class surfaceIn:
    cdef u32 size
    cdef u32 tileMode
    cdef u32 format
    cdef u32 bpp
    cdef u32 numSamples
    cdef u32 width
    cdef u32 height
    cdef u32 numSlices
    cdef u32 slice
    cdef u32 mipLevel
    cdef Flags flags
    cdef u32 numFrags
    cdef tileInfo pTileInfo
    cdef int tileIndex

    def __cinit__(self):
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
        self.flags = Flags()
        self.numFrags = 0
        self.pTileInfo = tileInfo()
        self.tileIndex = 0


cdef class surfaceOut:
    cdef u32 size
    cdef u32 pitch
    cdef u32 height
    cdef u32 depth
    cdef int64 surfSize
    cdef u32 tileMode
    cdef u32 baseAlign
    cdef u32 pitchAlign
    cdef u32 heightAlign
    cdef u32 depthAlign
    cdef u32 bpp
    cdef u32 pixelPitch
    cdef u32 pixelHeight
    cdef u32 pixelBits
    cdef u32 sliceSize
    cdef u32 pitchTileMax
    cdef u32 heightTileMax
    cdef u32 sliceTileMax
    cdef tileInfo pTileInfo
    cdef u32 tileType
    cdef int tileIndex

    def __cinit__(self):
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


class pySurfaceOut:
    pass


cdef:
    surfaceIn pIn = surfaceIn()
    surfaceOut pOut = surfaceOut()


cdef u32 getFillSizeFieldsFlags():
    return (m_configFlags >> 6) & 1


cdef u32 getSliceComputingFlags():
    return (m_configFlags >> 4) & 3


cdef u32 powTwoAlign(u32 x, u32 align):
    return ~(align - 1) & (x + align - 1)


cdef u32 nextPow2(u32 dim):
    cdef u32 newDim = 1
    if dim <= 0x7FFFFFFF:
        while newDim < dim:
            newDim *= 2

    else:
        newDim = 2147483648

    return newDim


cdef u32 useTileIndex(u32 index):
    if (m_configFlags >> 7) & 1 and index != -1:
        return 1

    else:
        return 0


cdef (u32, u32, u32, u32) getBitsPerPixel(u32 format_):
    cdef:
        u32 expandY = 1
        u32 elemMode = 3

    cdef u32 bpp, expandX

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


cdef u32 adjustSurfaceInfo(u32 elemMode, u32 expandX, u32 expandY, u32 pBpp, u32 pWidth, u32 pHeight):
    cdef:
        u32 bBCnFormat = 0

        u32 bpp, packedBits, width, height
        u32 widtha, heighta

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

                pIn.width = max(1, widtha)
                pIn.height = max(1, heighta)

    return packedBits


cdef u32 hwlComputeMipLevel():
    cdef:
        u32 width, widtha
        u32 height, heighta
        u32 slices

        u32 handled = 0

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

            pIn.width = nextPow2(width)
            pIn.height = nextPow2(height)
            pIn.numSlices = slices

        handled = 1

    return handled


cdef void computeMipLevel():
    cdef:
        u32 slices = 0
        u32 height = 0
        u32 width = 0
        u32 hwlHandled = 0

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


cdef u32 convertToNonBankSwappedMode(u32 tileMode):
    cdef u32 expTileMode

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


cdef u32 computeSurfaceTileSlices(u32 tileMode, u32 bpp, u32 numSamples):
    cdef:
        u32 bytePerSample = ((bpp << 6) + 7) >> 3
        u32 tileSlices = 1

        u32 samplePerTile

    if computeSurfaceThickness(tileMode) > 1:
        numSamples = 4

    if bytePerSample:
        samplePerTile = m_splitSize // bytePerSample
        if samplePerTile:
            tileSlices = max(1, numSamples // samplePerTile)

    return tileSlices


cdef u32 computeSurfaceRotationFromTileMode(u32 tileMode):
    cdef:
        u32 pipes = m_pipes
        u32 result = 0

    if tileMode in [4, 5, 6, 7, 8, 9, 10, 11]:
        result = pipes * ((m_banks >> 1) - 1)

    elif tileMode in [12, 13, 14, 15]:
        result = 1

    return result


cdef u32 computeSurfaceMipLevelTileMode(u32 baseTileMode, u32 bpp, u32 level, u32 width, u32 height, u32 numSlices, u32 numSamples, u32 isDepth, u32 noRecursive):
    cdef:
        u32 expTileMode = baseTileMode
        u32 numPipes = m_pipes
        u32 numBanks = m_banks
        u32 groupBytes = m_pipeInterleaveBytes
        u32 tileSlices = computeSurfaceTileSlices(baseTileMode, bpp, numSamples)

        u32 widtha, heighta, numSlicesa, thickness, microTileBytes, v13
        u32 widthAlignFactor, macroTileWidth, macroTileHeight, v11

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

    cdef u32 rotation = computeSurfaceRotationFromTileMode(expTileMode)
    if not (rotation % m_pipes):
        if expTileMode == 12:
            expTileMode = 4

        if expTileMode == 14:
            expTileMode = 8

        if expTileMode == 13:
            expTileMode = 7

        if expTileMode == 15:
            expTileMode = 11

    cdef u32 result
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


cdef u32 isDualPitchAlignNeeded(u32 tileMode, u32 isDepth, u32 mipLevel):
    cdef u32 needed
    if isDepth or mipLevel or m_chipFamily != 1:
        needed = 0

    elif tileMode in [0, 1, 2, 3, 7, 11, 13, 15]:
        needed = 0

    else:
        needed = 1

    return needed


cdef u32 isPow2(u32 dim):
    if dim & (dim - 1) == 0:
        return 1

    else:
        return 0


cdef (u32, u32, u32) padDimensions(u32 tileMode, u32 padDims, u32 isCube, u32 cubeAsArray, u32 pitchAlign, u32 heightAlign, u32 sliceAlign):
    global expPitch
    global expHeight
    global expNumSlices

    cdef u32 thickness = computeSurfaceThickness(tileMode)
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


cdef u32 adjustPitchAlignment(Flags flags, u32 pitchAlign):
    if (flags.value >> 13) & 1:
        pitchAlign = powTwoAlign(pitchAlign, 0x20)

    return pitchAlign


cdef (u32, u32, u32) computeSurfaceAlignmentsLinear(u32 tileMode, u32 bpp, Flags flags):
    cdef:
        u32 pixelsPerPipeInterleave
        u32 baseAlign, pitchAlign, heightAlign

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


cdef (u32, u32, u32, u32, u32, u32, u32, u32, u32) computeSurfaceInfoLinear(u32 tileMode, u32 bpp, u32 numSamples, u32 pitch, u32 height, u32 numSlices, u32 mipLevel, u32 padDims, Flags flags):
    global expPitch
    global expHeight
    global expNumSlices

    expPitch = pitch
    expHeight = height
    expNumSlices = numSlices

    cdef:
        u32 valid = 1
        u32 microTileThickness = computeSurfaceThickness(tileMode)

        u32 baseAlign, pitchAlign, heightAlign, slices
        u32 pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign

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


cdef (u32, u32, u32) computeSurfaceAlignmentsMicroTiled(u32 tileMode, u32 bpp, Flags flags, u32 numSamples):
    if bpp in [24, 48, 96]:
        bpp //= 3

    cdef:
        u32 v8 = computeSurfaceThickness(tileMode)
        u32 baseAlign = m_pipeInterleaveBytes
        u32 pitchAlign = max(8, m_pipeInterleaveBytes // bpp // numSamples // v8)
        u32 heightAlign = 8

    pitchAlign = adjustPitchAlignment(flags, pitchAlign)

    return baseAlign, pitchAlign, heightAlign


cdef (u32, u32, u32, u32, u32, u32, u32, u32, u32, u32) computeSurfaceInfoMicroTiled(u32 tileMode, u32 bpp, u32 numSamples, u32 pitch, u32 height, u32 numSlices, u32 mipLevel, u32 padDims, Flags flags):
    global expPitch
    global expHeight
    global expNumSlices

    expPitch = pitch
    expHeight = height
    expNumSlices = numSlices

    cdef:
        u32 valid = 1
        u32 expTileMode = tileMode
        u32 microTileThickness = computeSurfaceThickness(tileMode)
        u32 pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pTileModeOut, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign

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


cdef u32 isDualBaseAlignNeeded(u32 tileMode):
    cdef u32 needed = 1

    if m_chipFamily == 1:
        if 0 <= tileMode <= 3:
            needed = 0

    else:
        needed = 0

    return needed


cdef (u32, u32, u32, u32, u32) computeSurfaceAlignmentsMacroTiled(u32 tileMode, u32 bpp, Flags flags, u32 numSamples):
    cdef:
        u32 groupBytes = m_pipeInterleaveBytes
        u32 numBanks = m_banks
        u32 numPipes = m_pipes
        u32 splitBytes = m_splitSize
        u32 aspectRatio = computeMacroTileAspectRatio(tileMode)
        u32 thickness = computeSurfaceThickness(tileMode)

    if bpp in [24, 48, 96]:
        bpp //= 3

    if bpp == 3:
        bpp = 1

    cdef:
        u32 macroTileWidth = 8 * numBanks // aspectRatio
        u32 macroTileHeight = aspectRatio * 8 * numPipes

    cdef u32 pitchAlign = max(macroTileWidth, macroTileWidth * (groupBytes // bpp // (8 * thickness) // numSamples))
    pitchAlign = adjustPitchAlignment(flags, pitchAlign)

    cdef:
        u32 heightAlign = macroTileHeight
        u32 macroTileBytes = numSamples * ((bpp * macroTileHeight * macroTileWidth + 7) >> 3)

    if m_chipFamily == 1 and numSamples == 1:
        macroTileBytes *= 2

    cdef u32 baseAlign

    if thickness == 1:
        baseAlign = max(macroTileBytes, (numSamples * heightAlign * bpp * pitchAlign + 7) >> 3)

    else:
        baseAlign = max(groupBytes, (4 * heightAlign * bpp * pitchAlign + 7) >> 3)

    cdef:
        u32 microTileBytes = (thickness * numSamples * (bpp << 6) + 7) >> 3
        u32 numSlicesPerMicroTile = 1 if microTileBytes < splitBytes else microTileBytes // splitBytes

    baseAlign //= numSlicesPerMicroTile

    cdef u32 macroBytes

    if isDualBaseAlignNeeded(tileMode):
        macroBytes = (bpp * macroTileHeight * macroTileWidth + 7) >> 3

        if baseAlign // macroBytes % 2:
            baseAlign += macroBytes

    return baseAlign, pitchAlign, heightAlign, macroTileWidth, macroTileHeight


cdef (u32, u32, u32, u32, u32, u32, u32, u32, u32, u32) computeSurfaceInfoMacroTiled(u32 tileMode, u32 baseTileMode, u32 bpp, u32 numSamples, u32 pitch, u32 height, u32 numSlices, u32 mipLevel, u32 padDims, Flags flags):
    global expPitch
    global expHeight
    global expNumSlices

    expPitch = pitch
    expHeight = height
    expNumSlices = numSlices

    cdef:
        u32 valid = 1
        u32 expTileMode = tileMode
        u32 microTileThickness = computeSurfaceThickness(tileMode)

        u32 baseAlign, pitchAlign, heightAlign, macroWidth, macroHeight

        u32 bankSwappedWidth, v21, tilePerGroup
        u32 evenHeight, evenWidth, pitchAlignFactor

        u32 result, pPitchOut, pHeightOut, pNumSlicesOut, pSurfSize, pTileModeOut, pBaseAlign, pPitchAlign, pHeightAlign, pDepthAlign

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


cdef u32 ComputeSurfaceInfoEx():
    cdef:
        u32 tileMode = pIn.tileMode
        u32 bpp = pIn.bpp
        u32 numSamples = max(1, pIn.numSamples)
        u32 pitch = pIn.width
        u32 height = pIn.height
        u32 numSlices = pIn.numSlices
        u32 mipLevel = pIn.mipLevel
        Flags flags = Flags()
        u32 pPitchOut = pOut.pitch
        u32 pHeightOut = pOut.height
        u32 pNumSlicesOut = pOut.depth
        u32 pTileModeOut = pOut.tileMode
        u32 pSurfSize = pOut.surfSize
        u32 pBaseAlign = pOut.baseAlign
        u32 pPitchAlign = pOut.pitchAlign
        u32 pHeightAlign = pOut.heightAlign
        u32 pDepthAlign = pOut.depthAlign
        u32 padDims = 0
        u32 valid = 0
        u32 baseTileMode = tileMode

        u32 result

    flags.value = pIn.flags.value

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


cdef u32 restoreSurfaceInfo(u32 elemMode, u32 expandX, u32 expandY, u32 bpp):
    cdef u32 originalBits, width, height

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

        pOut.pixelPitch = max(1, width)
        pOut.pixelHeight = max(1, height)

    return bpp


cdef void computeSurfaceInfo(surfaceIn aSurfIn, surfaceOut pSurfOut):
    global pIn
    global pOut
    global ADDR_OK

    pIn = aSurfIn
    pOut = pSurfOut

    cdef:
        u32 v4 = 0
        u32 v6 = 0
        u32 v7 = 0
        u32 v8 = 0
        u32 v10 = 0
        u32 v11 = 0
        u32 v12 = 0
        u32 v18 = 0
        tileInfo tileInfoNull = tileInfo()
        u32 sliceFlags = 0

        u32 returnCode

        u32 width, height, bpp, elemMode
        u32 expandY, expandX, sliceTileMax

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

        if useTileIndex(pIn.tileIndex) and not pIn.pTileInfo:
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
                pIn.width = max(1, pIn.width)
                pIn.height = max(1, pIn.height)

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
                pOut.sliceSize = pOut.surfSize // pOut.depth

                if pIn.slice == (pIn.numSlices - 1) and pIn.numSlices > 1:
                    pOut.sliceSize += pOut.sliceSize * (pOut.depth - pIn.numSlices)

            pOut.pitchTileMax = (pOut.pitch >> 3) - 1
            pOut.heightTileMax = (pOut.height >> 3) - 1
            sliceTileMax = (pOut.height * pOut.pitch >> 6) - 1
            pOut.sliceTileMax = sliceTileMax


def getSurfaceInfo(u32 surfaceFormat, u32 surfaceWidth, u32 surfaceHeight, u32 surfaceDepth, u32 surfaceDim, u32 surfaceTileMode, u32 surfaceAA, u32 level):
    cdef:
        u32 dim = 0
        u32 width = 0
        u32 blockSize = 0
        u32 numSamples = 0
        u32 hwFormat = 0

        surfaceIn aSurfIn = surfaceIn()
        surfaceOut pSurfOut = surfaceOut()

    hwFormat = surfaceFormat & 0x3F
    if surfaceTileMode == 16:
        numSamples = 1 << surfaceAA

        if hwFormat < 0x31 or hwFormat > 0x35:
            blockSize = 1

        else:
            blockSize = 4

        width = ~(blockSize - 1) & ((surfaceWidth >> level) + blockSize - 1)

        if hwFormat == 0x35:
            return pSurfOut

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
            pSurfOut.height = max(1, surfaceHeight >> level)
            pSurfOut.depth = 1

        elif dim == 2:
            pSurfOut.height = max(1, surfaceHeight >> level)
            pSurfOut.depth = max(1, surfaceDepth >> level)

        elif dim == 3:
            pSurfOut.height = max(1, surfaceHeight >> level)
            pSurfOut.depth = max(6, surfaceDepth)

        elif dim == 4:
            pSurfOut.height = 1
            pSurfOut.depth = surfaceDepth

        elif dim == 5:
            pSurfOut.height = max(1, surfaceHeight >> level)
            pSurfOut.depth = surfaceDepth

        pSurfOut.height = (~(blockSize - 1) & (pSurfOut.height + blockSize - 1)) // blockSize
        pSurfOut.pixelPitch = ~(blockSize - 1) & ((surfaceWidth >> level) + blockSize - 1)
        pSurfOut.pixelPitch = max(blockSize, pSurfOut.pixelPitch)
        pSurfOut.pixelHeight = ~(blockSize - 1) & ((surfaceHeight >> level) + blockSize - 1)
        pSurfOut.pixelHeight = max(blockSize, pSurfOut.pixelHeight)
        pSurfOut.pitch = max(1, pSurfOut.pitch)
        pSurfOut.height = max(1, pSurfOut.height)
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
        aSurfIn.width = max(1, surfaceWidth >> level)
        dim = surfaceDim

        if dim == 0:
            aSurfIn.height = 1
            aSurfIn.numSlices = 1

        elif dim == 1:
            aSurfIn.height = max(1, surfaceHeight >> level)
            aSurfIn.numSlices = 1

        elif dim == 2:
            aSurfIn.height = max(1, surfaceHeight >> level)
            aSurfIn.numSlices = max(1, surfaceDepth >> level)

        elif dim == 3:
            aSurfIn.height = max(1, surfaceHeight >> level)
            aSurfIn.numSlices = max(6, surfaceDepth)
            aSurfIn.flags.value |= 0x10

        elif dim == 4:
            aSurfIn.height = 1
            aSurfIn.numSlices = surfaceDepth

        elif dim == 5:
            aSurfIn.height = max(1, surfaceHeight >> level)
            aSurfIn.numSlices = surfaceDepth

        elif dim == 6:
            aSurfIn.height = max(1, surfaceHeight >> level)
            aSurfIn.numSlices = 1

        elif dim == 7:
            aSurfIn.height = max(1, surfaceHeight >> level)
            aSurfIn.numSlices = surfaceDepth

        aSurfIn.slice = 0
        aSurfIn.mipLevel = level

        if surfaceDim == 2:
            aSurfIn.flags.value |= 0x20

        if level == 0:
            aSurfIn.flags.value = (1 << 12) | aSurfIn.flags.value & 0xFFFFEFFF

        else:
            aSurfIn.flags.value = aSurfIn.flags.value & 0xFFFFEFFF

        pSurfOut.size = 96
        computeSurfaceInfo(aSurfIn, pSurfOut)

        pSurfOut = pOut

    # We can't return a Cython class
    # Copy the attributes from our Cython class to a Python class
    # and return it instead
    pypOut = pySurfaceOut()

    pypOut.size = pOut.size
    pypOut.pitch = pOut.pitch
    pypOut.height = pOut.height
    pypOut.depth = pOut.depth
    pypOut.surfSize = pOut.surfSize
    pypOut.tileMode = pOut.tileMode
    pypOut.baseAlign = pOut.baseAlign
    pypOut.pitchAlign = pOut.pitchAlign
    pypOut.heightAlign = pOut.heightAlign
    pypOut.depthAlign = pOut.depthAlign
    pypOut.bpp = pOut.bpp
    pypOut.pixelPitch = pOut.pixelPitch
    pypOut.pixelHeight = pOut.pixelHeight
    pypOut.pixelBits = pOut.pixelBits
    pypOut.sliceSize = pOut.sliceSize
    pypOut.pitchTileMax = pOut.pitchTileMax
    pypOut.heightTileMax = pOut.heightTileMax
    pypOut.sliceTileMax = pOut.sliceTileMax
    pypOut.pTileInfo = pOut.pTileInfo
    pypOut.tileType = pOut.tileType
    pypOut.tileIndex = pOut.tileIndex

    return pypOut
