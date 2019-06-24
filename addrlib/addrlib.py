#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# addrlib.py
# A Python Address Library for Wii U textures.


################################################################
################################################################

BCn_formats = [
    0x31, 0x431, 0x32, 0x432,
    0x33, 0x433, 0x34, 0x234,
    0x35, 0x235,
]


def getDefaultGX2TileMode(dim, width, height, depth, format_, aa, use):
    """
    dim: dim of the surface (GX2SurfaceDim)
    width: width of the surface
    height: height of the surface
    depth: depth of the surface
    format_: format of the surface (GX2SurfaceFormat)
    aa: AA mode of the surface (GX2AAMode)
    use: use of the surface (GX2SurfaceUse)
    """

    tileMode = 1
    isDepthBuffer = bool(use & 4)
    isColorBuffer = bool(use & 2)

    if dim or aa or isDepthBuffer:
        if dim != 2 or isColorBuffer:
            tileMode = 4

        else:
            tileMode = 7

        surfOut = getSurfaceInfo(format_, width, height, depth, dim, tileMode, aa, 0)
        if width < surfOut.pitchAlign and height < surfOut.heightAlign:
            if tileMode == 7:
                tileMode = 3

            else:
                tileMode = 2

    return tileMode


def GX2TileModeToAddrTileMode(tileMode):
    if not tileMode:
        raise RuntimeError("Use tileMode from getDefaultGX2TileMode().")

    if tileMode == 16:
        return 0

    return tileMode


def swizzleSurf(width, height, depth, format_, aa, use, tileMode, swizzle_,
                pitch, bitsPerPixel, slice, sample, data, dataSize, swizzle):

    """
    width: width of the surface
    height: height of the surface
    depth: depth of the surface
    format_: format of the surface (GX2SurfaceFormat)
    aa: AA mode of the surface (GX2AAMode)
    use: use of the surface (GX2SurfaceUse)
    tileMode: tileMode of the surface (GX2TileMode)
    swizzle_: swizzle of the surface (GX2Surface.swizzle)
    pitch: aligned width of the surface (can be calculated using getSurfaceInfo())
    bitsPerPixel: bits per element for the given format (use surfaceGetBitsPerPixel())
    data: data to be (un)swizzled
    swizzle: boolen where the data will be swizzled if true, otherwise unswizzled
    """

    bytesPerPixel = bitsPerPixel // 8
    result = bytearray(len(data))

    if format_ in BCn_formats:
        width = (width + 3) // 4
        height = (height + 3) // 4

    pipeSwizzle = (swizzle_ >> 8) & 1
    bankSwizzle = (swizzle_ >> 9) & 3

    tileMode = GX2TileModeToAddrTileMode(tileMode)

    for y in range(height):
        for x in range(width):
            if tileMode in [0, 1]:
                pos = computeSurfaceAddrFromCoordLinear(x, y, slice, sample, bytesPerPixel, pitch, height, depth)

            elif tileMode in [2, 3]:
                pos = computeSurfaceAddrFromCoordMicroTiled(x, y, slice, bitsPerPixel, pitch, height, tileMode, bool(use & 4))

            else:
                pos = computeSurfaceAddrFromCoordMacroTiled(x, y, slice, sample, bitsPerPixel, pitch, height, 1 << aa,
                                                            tileMode, bool(use & 4), pipeSwizzle, bankSwizzle)

            pos_ = (y * width + x) * bytesPerPixel

            if pos_ + bytesPerPixel <= len(data) and pos + bytesPerPixel <= len(data):
                if swizzle == 0:
                    result[pos_:pos_ + bytesPerPixel] = data[pos:pos + bytesPerPixel]

                else:
                    result[pos:pos + bytesPerPixel] = data[pos_:pos_ + bytesPerPixel]

    return bytes(result)


def deswizzle(width, height, depth, format_, aa, use, tileMode, swizzle_,
              pitch, bpp, slice, sample, data):

    return swizzleSurf(width, height, depth, format_, aa, use, tileMode, swizzle_, pitch, bpp,
                       slice, sample, data, len(data), False)


def swizzle(width, height, depth, format_, aa, use, tileMode, swizzle_,
            pitch, bpp, slice, sample, data):

    return swizzleSurf(width, height, depth, format_, aa, use, tileMode, swizzle_, pitch, bpp,
                       slice, sample, data, len(data), True)


formatHwInfo = [
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

formatExInfo = [
    0x00, 0x01, 0x01, 0x03, 0x08, 0x01, 0x01, 0x03, 0x08, 0x01, 0x01, 0x03, 0x08, 0x01, 0x01, 0x03,
    0x00, 0x01, 0x01, 0x03, 0x10, 0x01, 0x01, 0x03, 0x10, 0x01, 0x01, 0x03, 0x10, 0x01, 0x01, 0x03,
    0x10, 0x01, 0x01, 0x03, 0x10, 0x01, 0x01, 0x03, 0x10, 0x01, 0x01, 0x03, 0x10, 0x01, 0x01, 0x03,
    0x10, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03,
    0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03,
    0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03,
    0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03,
    0x40, 0x01, 0x01, 0x03, 0x40, 0x01, 0x01, 0x03, 0x40, 0x01, 0x01, 0x03, 0x40, 0x01, 0x01, 0x03,
    0x40, 0x01, 0x01, 0x03, 0x00, 0x01, 0x01, 0x03, 0x80, 0x01, 0x01, 0x03, 0x80, 0x01, 0x01, 0x03,
    0x00, 0x01, 0x01, 0x03, 0x01, 0x08, 0x01, 0x05, 0x01, 0x08, 0x01, 0x06, 0x10, 0x01, 0x01, 0x07,
    0x10, 0x01, 0x01, 0x08, 0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03, 0x20, 0x01, 0x01, 0x03,
    0x18, 0x03, 0x01, 0x04, 0x30, 0x03, 0x01, 0x04, 0x30, 0x03, 0x01, 0x04, 0x60, 0x03, 0x01, 0x04,
    0x60, 0x03, 0x01, 0x04, 0x40, 0x04, 0x04, 0x09, 0x80, 0x04, 0x04, 0x0A, 0x80, 0x04, 0x04, 0x0B,
    0x40, 0x04, 0x04, 0x0C, 0x40, 0x04, 0x04, 0x0D, 0x40, 0x04, 0x04, 0x0D, 0x40, 0x04, 0x04, 0x0D,
    0x00, 0x01, 0x01, 0x03, 0x00, 0x01, 0x01, 0x03, 0x00, 0x01, 0x01, 0x03, 0x00, 0x01, 0x01, 0x03,
    0x00, 0x01, 0x01, 0x03, 0x00, 0x01, 0x01, 0x03, 0x40, 0x01, 0x01, 0x03, 0x00, 0x01, 0x01, 0x03,
]


def surfaceGetBitsPerPixel(surfaceFormat):
    return formatHwInfo[(surfaceFormat & 0x3F) * 4]


def computeSurfaceThickness(tileMode):
    if tileMode in [3, 7, 11, 13, 15]:
        return 4

    elif tileMode in [16, 17]:
        return 8

    return 1


def computePixelIndexWithinMicroTile(x, y, z, bpp, tileMode, isDepth):
    pixelBit6 = 0
    pixelBit7 = 0
    pixelBit8 = 0

    thickness = computeSurfaceThickness(tileMode)

    if isDepth:
        pixelBit0 = x & 1
        pixelBit1 = y & 1
        pixelBit2 = (x & 2) >> 1
        pixelBit3 = (y & 2) >> 1
        pixelBit4 = (x & 4) >> 2
        pixelBit5 = (y & 4) >> 2

    else:
        if bpp == 8:
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

    return (pixelBit8 << 8) | (pixelBit7 << 7) | (pixelBit6 << 6) | 32 * pixelBit5 | 16 * pixelBit4 | 8 * pixelBit3 | 4 * pixelBit2 | pixelBit0 | 2 * pixelBit1


def computePipeFromCoordWoRotation(x, y):
    return ((y >> 3) ^ (x >> 3)) & 1


def computeBankFromCoordWoRotation(x, y):
    return ((y >> 5) ^ (x >> 3)) & 1 | 2 * (((y >> 4) ^ (x >> 4)) & 1)


def computeSurfaceRotationFromTileMode(tileMode):
    if tileMode in [4, 5, 6, 7, 8, 9, 10, 11]:
        return 2

    elif tileMode in [12, 13, 14, 15]:
        return 1

    return 0


def isThickMacroTiled(tileMode):
    if tileMode in [7, 11, 13, 15]:
        return 1

    return 0


def isBankSwappedTileMode(tileMode):
    if tileMode in [8, 9, 10, 11, 14, 15]:
        return 1

    return 0


def computeMacroTileAspectRatio(tileMode):
    if tileMode in [5, 9]:
        return 2

    elif tileMode in [6, 10]:
        return 4

    return 1


def computeSurfaceBankSwappedWidth(tileMode, bpp, numSamples, pitch):
    if isBankSwappedTileMode(tileMode) == 0:
        return 0

    bytesPerSample = 8 * bpp

    if bytesPerSample != 0:
        samplesPerTile = 2048 // bytesPerSample
        slicesPerTile = max(1, numSamples // samplesPerTile)

    else:
        slicesPerTile = 1

    if isThickMacroTiled(tileMode) != 0:
        numSamples = 4

    bytesPerTileSlice = numSamples * bytesPerSample // slicesPerTile

    factor = computeMacroTileAspectRatio(tileMode)
    swapTiles = max(1, 128 // bpp)

    swapWidth = swapTiles * 32
    heightBytes = numSamples * factor * bpp * 2 // slicesPerTile
    swapMax = 0x4000 // heightBytes
    swapMin = 256 // bytesPerTileSlice

    bankSwapWidth = min(swapMax, max(swapMin, swapWidth))
    while bankSwapWidth >= 2 * pitch:
        bankSwapWidth >>= 1

    return bankSwapWidth


def computeSurfaceAddrFromCoordLinear(x, y, slice, sample, bpp, pitch, height, numSlices):
    sliceOffset = pitch * height * (slice + sample * numSlices)
    addr = (y * pitch + x + sliceOffset) * bpp
    
    return addr


def computeSurfaceAddrFromCoordMicroTiled(x, y, slice, bpp, pitch, height,
                                          tileMode, isDepth):

    microTileThickness = 1
    if tileMode == 3:
        microTileThickness = 4

    microTileBytes = (64 * microTileThickness * bpp + 7) // 8
    microTilesPerRow = pitch >> 3
    microTileIndexX = x >> 3
    microTileIndexY = y >> 3
    microTileIndexZ = slice // microTileThickness

    microTileOffset = microTileBytes * (microTileIndexX + microTileIndexY * microTilesPerRow)
    sliceBytes = (pitch * height * microTileThickness * bpp + 7) // 8
    sliceOffset = microTileIndexZ * sliceBytes

    pixelIndex = computePixelIndexWithinMicroTile(x, y, slice, bpp, tileMode, isDepth)
    pixelOffset = (bpp * pixelIndex) >> 3

    return pixelOffset + microTileOffset + sliceOffset


bankSwapOrder = [0, 1, 3, 2, 6, 7, 5, 4, 0, 0]


def computeSurfaceAddrFromCoordMacroTiled(x, y, slice, sample, bpp, pitch, height,
                                          numSamples, tileMode, isDepth,
                                          pipeSwizzle, bankSwizzle):

    microTileThickness = computeSurfaceThickness(tileMode)

    microTileBits = numSamples * bpp * (microTileThickness * 64)
    microTileBytes = (microTileBits + 7) // 8

    pixelIndex = computePixelIndexWithinMicroTile(x, y, slice, bpp, tileMode, isDepth)
    bytesPerSample = microTileBytes // numSamples

    if isDepth:
        sampleOffset = bpp * sample
        pixelOffset = numSamples * bpp * pixelIndex

    else:
        sampleOffset = sample * (microTileBits // numSamples)
        pixelOffset = bpp * pixelIndex

    elemOffset = pixelOffset + sampleOffset

    if numSamples <= 1 or microTileBytes <= 2048:
        samplesPerSlice = numSamples
        numSampleSplits = 1
        sampleSlice = 0

    else:
        samplesPerSlice = 2048 // bytesPerSample
        numSampleSplits = numSamples // samplesPerSlice
        numSamples = samplesPerSlice

        tileSliceBits = microTileBits // numSampleSplits
        sampleSlice = elemOffset // tileSliceBits
        elemOffset %= tileSliceBits

    elemOffset = (elemOffset + 7) // 8

    pipe = computePipeFromCoordWoRotation(x, y)
    bank = computeBankFromCoordWoRotation(x, y)

    swizzle_ = pipeSwizzle + 2 * bankSwizzle
    bankPipe = pipe + 2 * bank
    rotation = computeSurfaceRotationFromTileMode(tileMode)
    sliceIn = slice

    if isThickMacroTiled(tileMode):
        sliceIn >>= 2

    bankPipe ^= 2 * sampleSlice * 3 ^ (swizzle_ + sliceIn * rotation)
    bankPipe %= 8
    pipe = bankPipe % 2
    bank = bankPipe // 2

    sliceBytes = (height * pitch * microTileThickness * bpp * numSamples + 7) // 8
    sliceOffset = sliceBytes * ((sampleSlice + numSampleSplits * slice) // microTileThickness)

    macroTilePitch = 32
    macroTileHeight = 16

    if tileMode in [5, 9]:  # GX2_TILE_MODE_2D_TILED_THIN2 and GX2_TILE_MODE_2B_TILED_THIN2
        macroTilePitch = 16
        macroTileHeight = 32

    elif tileMode in [6, 10]:  # GX2_TILE_MODE_2D_TILED_THIN4 and GX2_TILE_MODE_2B_TILED_THIN4
        macroTilePitch = 8
        macroTileHeight = 64

    macroTilesPerRow = pitch // macroTilePitch
    macroTileBytes = (numSamples * microTileThickness * bpp * macroTileHeight
                      * macroTilePitch + 7) // 8
    macroTileIndexX = x // macroTilePitch
    macroTileIndexY = y // macroTileHeight
    macroTileOffset = (macroTileIndexX + macroTilesPerRow * macroTileIndexY) * macroTileBytes

    if isBankSwappedTileMode(tileMode):
        bankSwapWidth = computeSurfaceBankSwappedWidth(tileMode, bpp, numSamples, pitch)
        swapIndex = macroTilePitch * macroTileIndexX // bankSwapWidth
        bank ^= bankSwapOrder[swapIndex & 3]

    totalOffset = elemOffset + ((macroTileOffset + sliceOffset) >> 3)
    return bank << 9 | pipe << 8 | totalOffset & 255 | (totalOffset & -256) << 3


expPitch = 0
expHeight = 0
expNumSlices = 0


class Flags:
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
        self.flags = Flags()
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


pIn = surfaceIn()
pOut = surfaceOut()


def powTwoAlign(x, align):
    return ~(align - 1) & (x + align - 1)


def nextPow2(dim):
    newDim = 1
    if dim <= 0x7FFFFFFF:
        while newDim < dim:
            newDim *= 2

    else:
        newDim = 0x80000000

    return newDim


def getBitsPerPixel(format_):
    fmtIdx = format_ * 4
    return (formatExInfo[fmtIdx    ], formatExInfo[fmtIdx + 1],
            formatExInfo[fmtIdx + 2], formatExInfo[fmtIdx + 3])


def adjustSurfaceInfo(elemMode, expandX, expandY, bpp, width, height):
    bBCnFormat = 0
    if bpp and elemMode in [9, 10, 11, 12, 13]:
        bBCnFormat = 1

    if width and height:
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

    if bpp:
        if elemMode == 4:
            pIn.bpp = bpp // expandX // expandY

        elif elemMode in [5, 6]:
            pIn.bpp = expandY * expandX * bpp

        elif elemMode in [7, 8]:
            pIn.bpp = bpp

        elif elemMode in [9, 12]:
            pIn.bpp = 64

        elif elemMode in [10, 11, 13]:
            pIn.bpp = 128

        elif elemMode in [0, 1, 2, 3]:
            pIn.bpp = bpp

        else:
            pIn.bpp = bpp

        return pIn.bpp

    return 0


def hwlComputeMipLevel():
    handled = 0

    if 49 <= pIn.format <= 55:
        if pIn.mipLevel:
            width = pIn.width
            height = pIn.height
            slices = pIn.numSlices

            if (pIn.flags.value >> 12) & 1:
                widtha = width >> pIn.mipLevel
                heighta = height >> pIn.mipLevel

                if not (pIn.flags.value >> 4) & 1:
                    slices >>= pIn.mipLevel

                width = max(1, widtha)
                height = max(1, heighta)
                slices = max(1, slices)

            pIn.width = nextPow2(width)
            pIn.height = nextPow2(height)
            pIn.numSlices = slices

        handled = 1

    return handled


def computeMipLevel():
    slices = 0
    height = 0
    width = 0
    hwlHandled = 0

    if 49 <= pIn.format <= 55 and (not pIn.mipLevel or (pIn.flags.value >> 12) & 1):
        pIn.width = powTwoAlign(pIn.width, 4)
        pIn.height = powTwoAlign(pIn.height, 4)

    hwlHandled = hwlComputeMipLevel()
    if not hwlHandled and pIn.mipLevel and (pIn.flags.value >> 12) & 1:
        width = max(1, pIn.width >> pIn.mipLevel)
        height = max(1, pIn.height >> pIn.mipLevel)
        slices = max(1, pIn.numSlices)

        if not (pIn.flags.value >> 4) & 1:
            slices = max(1, slices >> pIn.mipLevel)

        if pIn.format not in [47, 48]:
            width = nextPow2(width)
            height = nextPow2(height)
            slices = nextPow2(slices)

        pIn.width = width
        pIn.height = height
        pIn.numSlices = slices


def convertToNonBankSwappedMode(tileMode):
    if tileMode == 8:
        return 4

    elif tileMode == 9:
        return 5

    elif tileMode == 10:
        return 6

    elif tileMode == 11:
        return 7

    elif tileMode == 14:
        return 12

    elif tileMode == 15:
        return 13

    return tileMode


def computeSurfaceTileSlices(tileMode, bpp, numSamples):
    bytePerSample = ((bpp << 6) + 7) >> 3
    tileSlices = 1

    if computeSurfaceThickness(tileMode) > 1:
        numSamples = 4

    if bytePerSample:
        samplePerTile = 2048 // bytePerSample
        if samplePerTile:
            tileSlices = max(1, numSamples // samplePerTile)

    return tileSlices


def computeSurfaceMipLevelTileMode(baseTileMode, bpp, level, width, height, numSlices, numSamples, isDepth, noRecursive):
    widthAlignFactor = 1
    macroTileWidth = 32
    macroTileHeight = 16
    tileSlices = computeSurfaceTileSlices(baseTileMode, bpp, numSamples)
    expTileMode = baseTileMode

    if numSamples > 1 or tileSlices > 1 or isDepth:
        if baseTileMode == 7:
            expTileMode = 4

        elif baseTileMode == 13:
            expTileMode = 12

        elif baseTileMode == 11:
            expTileMode = 8

        elif baseTileMode == 15:
            expTileMode = 14

    if baseTileMode == 2 and numSamples > 1:
        expTileMode = 4

    elif baseTileMode == 3:
        if numSamples > 1 or isDepth:
            expTileMode = 2

        if numSamples in [2, 4]:  # Mistake, should be elif?
            expTileMode = 7

    if noRecursive or not level:
        return expTileMode

    if bpp in [24, 48, 96]:
        bpp //= 3

    widtha = nextPow2(width)
    heighta = nextPow2(height)
    numSlicesa = nextPow2(numSlices)

    expTileMode = convertToNonBankSwappedMode(expTileMode)
    thickness = computeSurfaceThickness(expTileMode)
    microTileBytes = (numSamples * bpp * (thickness << 6) + 7) >> 3

    if microTileBytes < 256:
        widthAlignFactor = max(1, 256 // microTileBytes)

    if expTileMode in [4, 12]:
        if (widtha < widthAlignFactor * macroTileWidth) or heighta < macroTileHeight:
            expTileMode = 2

    elif expTileMode == 5:
        macroTileWidth = 16
        macroTileHeight = 32

        if (widtha < widthAlignFactor * macroTileWidth) or heighta < macroTileHeight:
            expTileMode = 2

    elif expTileMode == 6:
        macroTileWidth = 8
        macroTileHeight = 64

        if (widtha < widthAlignFactor * macroTileWidth) or heighta < macroTileHeight:
            expTileMode = 2

    if expTileMode in [7, 13]:
        if (widtha < widthAlignFactor * macroTileWidth) or heighta < macroTileHeight:
            expTileMode = 3

    if numSlicesa < 4:
        if expTileMode == 3:
            expTileMode = 2

        elif expTileMode == 7:
            expTileMode = 4

        elif expTileMode == 13:
            expTileMode = 12

    return computeSurfaceMipLevelTileMode(
        expTileMode,
        bpp,
        level,
        widtha,
        heighta,
        numSlicesa,
        numSamples,
        isDepth,
        1)


def padDimensions(tileMode, padDims, isCube, pitchAlign, heightAlign, sliceAlign):
    global expPitch
    global expHeight
    global expNumSlices

    thickness = computeSurfaceThickness(tileMode)
    if not padDims:
        padDims = 3

    if not pitchAlign & (pitchAlign - 1):
        expPitch = powTwoAlign(expPitch, pitchAlign)

    else:
        expPitch += pitchAlign - 1
        expPitch //= pitchAlign
        expPitch *= pitchAlign

    if padDims > 1:
        expHeight = powTwoAlign(expHeight, heightAlign)

    if padDims > 2 or thickness > 1:
        if isCube:
            expNumSlices = nextPow2(expNumSlices)

        if thickness > 1:
            expNumSlices = powTwoAlign(expNumSlices, sliceAlign)

    return expPitch, expHeight, expNumSlices


def adjustPitchAlignment(flags, pitchAlign):
    if (flags.value >> 13) & 1:
        pitchAlign = powTwoAlign(pitchAlign, 0x20)

    return pitchAlign


def computeSurfaceAlignmentsLinear(tileMode, bpp, flags):
    if not tileMode:
        baseAlign = 1
        pitchAlign = 1 if bpp != 1 else 8
        heightAlign = 1

    elif tileMode == 1:
        pixelsPerPipeInterleave = 2048 // bpp
        baseAlign = 256
        pitchAlign = max(0x40, pixelsPerPipeInterleave)
        heightAlign = 1

    else:
        baseAlign = 1
        pitchAlign = 1
        heightAlign = 1

    pitchAlign = adjustPitchAlignment(flags, pitchAlign)

    return baseAlign, pitchAlign, heightAlign


def computeSurfaceInfoLinear(tileMode, bpp, numSamples, pitch, height, numSlices, mipLevel, padDims, flags):
    global expPitch
    global expHeight
    global expNumSlices

    expPitch = pitch
    expHeight = height
    expNumSlices = numSlices

    valid = 1
    microTileThickness = computeSurfaceThickness(tileMode)

    baseAlign, pitchAlign, heightAlign = computeSurfaceAlignmentsLinear(tileMode, bpp, flags)

    if (flags.value >> 9) & 1 and not mipLevel:
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
        pitchAlign,
        heightAlign,
        microTileThickness)

    if (flags.value >> 9) & 1 and not mipLevel:
        expPitch *= 3

    slices = expNumSlices * numSamples // microTileThickness
    pOut.pitch = expPitch
    pOut.height = expHeight
    pOut.depth = expNumSlices
    pOut.surfSize = (expHeight * expPitch * slices * bpp * numSamples + 7) // 8
    pOut.baseAlign = baseAlign
    pOut.pitchAlign = pitchAlign
    pOut.heightAlign = heightAlign
    pOut.depthAlign = microTileThickness

    return valid


def computeSurfaceAlignmentsMicroTiled(tileMode, bpp, flags, numSamples):
    if bpp in [24, 48, 96]:
        bpp //= 3

    thickness = computeSurfaceThickness(tileMode)
    baseAlign = 256
    pitchAlign = max(8, 256 // bpp // numSamples // thickness)
    heightAlign = 8

    pitchAlign = adjustPitchAlignment(flags, pitchAlign)

    return baseAlign, pitchAlign, heightAlign


def computeSurfaceInfoMicroTiled(tileMode, bpp, numSamples, pitch, height, numSlices, mipLevel, padDims, flags):
    global expPitch
    global expHeight
    global expNumSlices

    expTileMode = tileMode
    expPitch = pitch
    expHeight = height
    expNumSlices = numSlices

    valid = 1
    microTileThickness = computeSurfaceThickness(tileMode)

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
        pitchAlign,
        heightAlign,
        microTileThickness)

    pOut.pitch = expPitch
    pOut.height = expHeight
    pOut.depth = expNumSlices
    pOut.surfSize = (expHeight * expPitch * expNumSlices * bpp * numSamples + 7) // 8
    pOut.tileMode = expTileMode
    pOut.baseAlign = baseAlign
    pOut.pitchAlign = pitchAlign
    pOut.heightAlign = heightAlign
    pOut.depthAlign = microTileThickness

    return valid


def computeSurfaceAlignmentsMacroTiled(tileMode, bpp, flags, numSamples):
    aspectRatio = computeMacroTileAspectRatio(tileMode)
    thickness = computeSurfaceThickness(tileMode)

    if bpp in [24, 48, 96]:
        bpp //= 3

    if bpp == 3:
        bpp = 1

    macroTileWidth = 32 // aspectRatio
    macroTileHeight = aspectRatio * 16

    pitchAlign = max(macroTileWidth, macroTileWidth * (256 // bpp // (8 * thickness) // numSamples))
    pitchAlign = adjustPitchAlignment(flags, pitchAlign)

    heightAlign = macroTileHeight
    macroTileBytes = numSamples * ((bpp * macroTileHeight * macroTileWidth + 7) >> 3)

    if thickness == 1:
        baseAlign = max(macroTileBytes, (numSamples * heightAlign * bpp * pitchAlign + 7) >> 3)

    else:
        baseAlign = max(256, (4 * heightAlign * bpp * pitchAlign + 7) >> 3)

    microTileBytes = (thickness * numSamples * (bpp << 6) + 7) >> 3
    numSlicesPerMicroTile = 1 if microTileBytes < 2048 else microTileBytes // 2048
    baseAlign //= numSlicesPerMicroTile

    return baseAlign, pitchAlign, heightAlign, macroTileWidth, macroTileHeight


def computeSurfaceInfoMacroTiled(tileMode, baseTileMode, bpp, numSamples, pitch, height, numSlices, mipLevel, padDims, flags):
    global expPitch
    global expHeight
    global expNumSlices

    expPitch = pitch
    expHeight = height
    expNumSlices = numSlices

    valid = 1
    expTileMode = tileMode
    microTileThickness = computeSurfaceThickness(tileMode)

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

        bankSwappedWidth = computeSurfaceBankSwappedWidth(tileMode, bpp, numSamples, pitch)

        if bankSwappedWidth > pitchAlign:
            pitchAlign = bankSwappedWidth

        expPitch, expHeight, expNumSlices = padDimensions(
            tileMode,
            padDims,
            (flags.value >> 4) & 1,
            pitchAlign,
            heightAlign,
            microTileThickness)

        pOut.pitch = expPitch
        pOut.height = expHeight
        pOut.depth = expNumSlices
        pOut.surfSize = (expHeight * expPitch * expNumSlices * bpp * numSamples + 7) // 8
        pOut.tileMode = expTileMode
        pOut.baseAlign = baseAlign
        pOut.pitchAlign = pitchAlign
        pOut.heightAlign = heightAlign
        pOut.depthAlign = microTileThickness
        result = valid

    else:
        baseAlign, pitchAlign, heightAlign, macroWidth, macroHeight = computeSurfaceAlignmentsMacroTiled(
            baseTileMode,
            bpp,
            flags,
            numSamples)

        pitchAlignFactor = max(1, 32 // bpp)

        if expPitch < pitchAlign * pitchAlignFactor or expHeight < heightAlign:
            expTileMode = 2

            result = computeSurfaceInfoMicroTiled(
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

            bankSwappedWidth = computeSurfaceBankSwappedWidth(tileMode, bpp, numSamples, pitch)
            if bankSwappedWidth > pitchAlign:
                pitchAlign = bankSwappedWidth

            expPitch, expHeight, expNumSlices = padDimensions(
                tileMode,
                padDims,
                (flags.value >> 4) & 1,
                pitchAlign,
                heightAlign,
                microTileThickness)

            pOut.pitch = expPitch
            pOut.height = expHeight
            pOut.depth = expNumSlices
            pOut.surfSize = (expHeight * expPitch * expNumSlices * bpp * numSamples + 7) // 8
            pOut.tileMode = expTileMode
            pOut.baseAlign = baseAlign
            pOut.pitchAlign = pitchAlign
            pOut.heightAlign = heightAlign
            pOut.depthAlign = microTileThickness
            result = valid

    return result


def ComputeSurfaceInfoEx():
    tileMode = pIn.tileMode
    bpp = pIn.bpp
    numSamples = max(1, pIn.numSamples)
    pitch = pIn.width
    height = pIn.height
    numSlices = pIn.numSlices
    mipLevel = pIn.mipLevel
    flags = Flags()
    flags.value = pIn.flags.value
    padDims = 0
    valid = 0
    baseTileMode = tileMode

    if (flags.value >> 4) & 1 and not mipLevel:
        padDims = 2

    if (flags.value >> 6) & 1:
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
        valid = computeSurfaceInfoLinear(
            tileMode,
            bpp,
            numSamples,
            pitch,
            height,
            numSlices,
            mipLevel,
            padDims,
            flags)

        pOut.tileMode = tileMode

    elif tileMode in [2, 3]:
        valid = computeSurfaceInfoMicroTiled(
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
        valid = computeSurfaceInfoMacroTiled(
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

    if not valid:
        return 3

    return 0


def restoreSurfaceInfo(elemMode, expandX, expandY, bpp):
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

    if bpp:
        if elemMode == 4:
            return expandY * expandX * bpp

        elif elemMode in [5, 6]:
            return bpp // expandX // expandY

        elif elemMode in [9, 12]:
            return 64

        elif elemMode in [10, 11, 13]:
            return 128

        return bpp

    return 0


def computeSurfaceInfo(aSurfIn, pSurfOut):
    global pIn
    global pOut

    pIn = aSurfIn
    pOut = pSurfOut

    returnCode = 0
    elemMode = 0

    if pIn.bpp > 0x80:
        returnCode = 3

    if returnCode == 0:
        computeMipLevel()

        width = pIn.width
        height = pIn.height
        bpp = pIn.bpp
        expandX = 1
        expandY = 1

        pOut.pixelBits = pIn.bpp

        if pIn.format:
            bpp, expandX, expandY, elemMode = getBitsPerPixel(pIn.format)

            if elemMode == 4 and expandX == 3 and pIn.tileMode == 1:
                pIn.flags.value |= 0x200

            bpp = adjustSurfaceInfo(elemMode, expandX, expandY, bpp, width, height)

        elif pIn.bpp:
            pIn.width = max(1, pIn.width)
            pIn.height = max(1, pIn.height)

        else:
            returnCode = 3

        if returnCode == 0:
            returnCode = ComputeSurfaceInfoEx()

        if returnCode == 0:
            pOut.bpp = pIn.bpp
            pOut.pixelPitch = pOut.pitch
            pOut.pixelHeight = pOut.height

            if pIn.format and (not (pIn.flags.value >> 9) & 1 or not pIn.mipLevel):
                bpp = restoreSurfaceInfo(elemMode, expandX, expandY, bpp)

            if (pIn.flags.value >> 5) & 1:
                pOut.sliceSize = pOut.surfSize

            else:
                pOut.sliceSize = pOut.surfSize // pOut.depth

                if pIn.slice == (pIn.numSlices - 1) and pIn.numSlices > 1:
                    pOut.sliceSize += pOut.sliceSize * (pOut.depth - pIn.numSlices)

            pOut.pitchTileMax = (pOut.pitch >> 3) - 1
            pOut.heightTileMax = (pOut.height >> 3) - 1
            pOut.sliceTileMax = (pOut.height * pOut.pitch >> 6) - 1


def getSurfaceInfo(surfaceFormat, surfaceWidth, surfaceHeight, surfaceDepth, surfaceDim, surfaceTileMode, surfaceAA, level):
    """
    surfaceFormat: format of the surface (GX2SurfaceFormat)
    surfaceWidth: width of the surface
    surfaceHeight: height of the surface
    surfaceDepth: depth of the surface
    surfaceDim: dim of the surface (GX2SurfaceDim)
    surfaceTileMode: GX2TileMode (note: NOT AddrTileMode)
    surfaceAA: AA mode of the surface (GX2AAMode)
    level: mip level of which the info will be calculated for (first mipmap corresponds to value 1)
    """

    dim = 0
    width = 0
    blockSize = 0
    numSamples = 0
    hwFormat = 0

    aSurfIn = surfaceIn()
    pSurfOut = surfaceOut()

    hwFormat = surfaceFormat & 0x3F
    if surfaceTileMode == 16:
        numSamples = 1 << surfaceAA

        if hwFormat < 0x31 or hwFormat > 0x35:
            blockSize = 1

        else:
            blockSize = 4

        width = ~(blockSize - 1) & (max(1, surfaceWidth >> level) + blockSize - 1)

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

        elif dim in [1, 6]:
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

        elif dim in [5, 7]:
            pSurfOut.height = max(1, surfaceHeight >> level)
            pSurfOut.depth = surfaceDepth

        pSurfOut.pixelPitch = width
        pSurfOut.pixelHeight = ~(blockSize - 1) & (pSurfOut.height + blockSize - 1)
        pSurfOut.height = pSurfOut.pixelHeight // blockSize
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

        elif dim in [1, 6]:
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

        elif dim in [5, 7]:
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

    if not pSurfOut.tileMode:
        pSurfOut.tileMode = 16

    return pSurfOut
