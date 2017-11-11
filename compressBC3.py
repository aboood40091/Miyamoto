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

# compressBC3_cy.pyx
# A Python port of Wexos's Toolbox BC3 compressor.


################################################################
################################################################

def CompressAlphaBlock(AlphaBlock, Palette, Width, Height, x, y):
    Indices = [0] * 16

    for y2 in range(4):
        for x2 in range(4):
            if (y + y2) < Height and (x + x2) < Width:
                Index = 0
                Delta = 2147483647

                A = AlphaBlock[y2 * 4 + x2]

                for i in range(len(Palette)):
                    if A == Palette[i]:
                        Index = i
                        break

                    AlphaDelta = A - Palette[i]
                    AlphaDelta = max(AlphaDelta, -AlphaDelta)

                    if AlphaDelta < Delta:
                        Delta = AlphaDelta
                        Index = i

                Indices[y2 * 4 + x2] = Index

    return Indices

def GetAlphaPalette(A0, A1):
    Palette = bytearray(8)
    Palette[0] = A0
    Palette[1] = A1

    if A0 > A1:
        Palette[2] = (6 * A0 + 1 * A1) // 7
        Palette[3] = (5 * A0 + 2 * A1) // 7
        Palette[4] = (4 * A0 + 3 * A1) // 7
        Palette[5] = (3 * A0 + 4 * A1) // 7
        Palette[6] = (2 * A0 + 5 * A1) // 7
        Palette[7] = (1 * A0 + 6 * A1) // 7

    else:
        Palette[2] = (4 * A0 + 1 * A1) // 5
        Palette[3] = (3 * A0 + 2 * A1) // 5
        Palette[4] = (2 * A0 + 3 * A1) // 5
        Palette[5] = (1 * A0 + 4 * A1) // 5
        Palette[6] = 0
        Palette[7] = 0xFF

    return Palette


def CompressBlock(ColorBlock, Palette, Width, Height, x, y, ScaleR, ScaleG, ScaleB):
    Indices = [0] * 16

    for y2 in range(4):
        for x2 in range(4):
            if y + y2 < Height and x + x2 < Width:
                Index = 0
                Delta = 2147483647

                Color = ColorBlock[y2 * 4 + x2]
                R = (Color >> 16) & 0xFF
                G = (Color >> 8) & 0xFF
                B = Color & 0xFF
                A = (Color >> 24) & 0xFF

                for i in range(len(Palette)):
                    if Color == Palette[i]:
                        Index = i
                        break

                    RedDelta = R - ((Palette[i] >> 16) & 0xFF)
                    GreenDelta = G - ((Palette[i] >> 8) & 0xFF)
                    BlueDelta = B - (Palette[i] & 0xFF)

                    RedDelta = max(RedDelta, -RedDelta)
                    GreenDelta = max(GreenDelta, -GreenDelta)
                    BlueDelta = max(BlueDelta, -BlueDelta)

                    NewDelta = RedDelta * ScaleR + GreenDelta * ScaleG + BlueDelta * ScaleB

                    if NewDelta < Delta:
                        Delta = NewDelta
                        Index = i

                Indices[y2 * 4 + x2] = Index

    return Indices

def FindMinMax(Colors):
    MaxR = 0
    MaxG = 0
    MaxB = 0

    MinR = 255
    MinG = 255
    MinB = 255

    TransparentBlock = True

    for Color in Colors:
        R = (Color >> 16) & 0xFF
        G = (Color >> 8) & 0xFF
        B = Color & 0xFF
        A = (Color >> 24) & 0xFF

        if not A:
            continue

        TransparentBlock = False

        # Max color
        if R > MaxR: MaxR = R
        if G > MaxG: MaxG = G
        if B > MaxB: MaxB = B

        # Min color
        if R < MinR: MinR = R
        if G < MinG: MinG = G
        if B < MinB: MinB = B

    if TransparentBlock:
        MinR = 0
        MinG = 0
        MinB = 0

        MaxR = 0
        MaxG = 0
        MaxB = 0

    return MinR, MinG, MinB, MaxR, MaxG, MaxB, TransparentBlock

def ToARGB8(Red, Green, Blue, Alpha):
    R = int(Red * 255)
    G = int(Green * 255)
    B = int(Blue * 255)
    A = int(Alpha * 255)

    return (A << 24) | (R << 16) | (G << 8) | B

def GetPalette(Color0, Color1):
    Palette = [0] * 4
    Palette[0] = ToARGB8(((Color0 >> 11) & 0b11111) / 31, ((Color0 >> 5) & 0b111111) / 63, (Color0 & 0b11111) / 31, 0)
    Palette[1] = ToARGB8(((Color1 >> 11) & 0b11111) / 31, ((Color1 >> 5) & 0b111111) / 63, (Color1 & 0b11111) / 31, 0)

    R0 = (Palette[0] >> 16) & 0xFF
    G0 = (Palette[0] >> 8) & 0xFF
    B0 = Palette[0] & 0xFF
    R1 = (Palette[1] >> 16) & 0xFF
    G1 = (Palette[1] >> 8) & 0xFF
    B1 = Palette[1] & 0xFF

    Palette[2] = ((2 * R0 // 3 + 1 * R1 // 3) << 16) | ((2 * G0 // 3 + 1 * G1 // 3) << 8) | (2 * B0 // 3 + 1 * B1 // 3)
    Palette[3] = ((1 * R0 // 3 + 2 * R1 // 3) << 16) | ((1 * G0 // 3 + 2 * G1 // 3) << 8) | (1 * B0 // 3 + 2 * B1 // 3)

    return Palette

def ToRGB565(R, G, B):
    return ((R >> 3) << 11) | ((G >> 2) << 5) | (B >> 3)


def FindColors(Colors):
    ThresholdMin = 0x02
    ThresholdMax = 0xFD

    PartMin = 255
    PartMax = 0
    Min = 255
    Max = 0
    UseLessThanAlgorithm = False  # Used when colors are close to both 0 and 0xFF

    for Color in Colors:
        if Color <= ThresholdMin:
            UseLessThanAlgorithm = True

        elif Color >= ThresholdMax:
            UseLessThanAlgorithm = True

        if not UseLessThanAlgorithm and Color < PartMin:
            PartMin = Color

        if not UseLessThanAlgorithm and Color > PartMax:
            PartMax = Color

        if Color < Min:
            Min = Color

        if Color > Max:
            Max = Color

    if Max <= 0x15 or (Min <= 0x05 and Max <= 0x30) or Min >= 0xEA or (Max >= 0xFA and Min >= 0xCF):  # What is good here?
        UseLessThanAlgorithm = False

    else:
        Max = PartMax
        Min = PartMin

    if not UseLessThanAlgorithm and Min == Max:
        Max -= 1

    if Max < 0:
        Max = 256 + Max

    Color0 = Min if UseLessThanAlgorithm else Max
    Color1 = Max if UseLessThanAlgorithm else Min

    return Color0, Color1


def CompressBC3(SrcPtr, Stride, Width, Height):
    Stride //= 4

    DstPtr = bytearray()

    for y in range(0, Height, 4):
        for x in range(0, Width, 4):
            Colors = []
            Alphas = []
            ActualColors = [0] * 16
            ActualAlphas =  bytearray(16)

            for y2 in range(4):
                for x2 in range(4):
                    if y + y2 < Height and x + x2 < Width:
                        # Read RGBA data and convert it to ARGB
                        pos = (y + y2) * Stride + (x + x2)
                        pos *= 4

                        A = SrcPtr[pos + 3]
                        R = SrcPtr[pos]
                        G = SrcPtr[pos + 1]
                        B = SrcPtr[pos + 2]

                        Color = (A << 24) | (R << 16) | (G << 8) | B

                        Colors.append(Color)
                        Alphas.append(A)
                        ActualColors[y2 * 4 + x2] = Color
                        ActualAlphas[y2 * 4 + x2] = A

            MinR, MinG, MinB, MaxR, MaxG, MaxB, TransparentBlock = FindMinMax(Colors)
            Alpha0, Alpha1 = FindColors(Alphas)

            Color0 = ToRGB565(MaxR, MaxG, MaxB)
            Color1 = ToRGB565(MinR, MinG, MinB)

            if Color0 == Color1:
                Color0 += 1

            Palette = GetPalette(Color0, Color1)
            AlphaPalette = GetAlphaPalette(Alpha0, Alpha1)

            Indices = 0
            AlphaIndices = 0

            if not TransparentBlock:
                IndexBlock = CompressBlock(ActualColors, Palette, Width, Height, x, y, 256 - (MaxR - MinR), 256 - (MaxG - MinG), 256 - (MaxB - MinB))
                AlphaIndexBlock = CompressAlphaBlock(ActualAlphas, AlphaPalette, Width, Height, x, y)

                for y2 in range(4):
                    for x2 in range(4):
                        i = y2 * 4 + x2
                        Indices |= IndexBlock[i] << (i * 2)
                        AlphaIndices |= AlphaIndexBlock[i] << (i * 3)

            else:
                Indices = 0xFFFFFFFF

                TransparentIndex = 0
                for i in range(len(AlphaPalette)):
                    if not AlphaPalette[i]:
                        TransparentIndex = i
                        break

                if AlphaPalette[TransparentIndex]:
                    raise RuntimeError

                for y2 in range(4):
                    for x2 in range(4):
                        AlphaIndices |= TransparentIndex << ((y2 * 4 + x2) * 3)

            DstPtr += bytes([Alpha0])
            DstPtr += bytes([Alpha1])

            DstPtr += bytes([AlphaIndices & 0xFF])
            DstPtr += bytes([(AlphaIndices >> 8) & 0xFF])
            DstPtr += bytes([(AlphaIndices >> 16) & 0xFF])
            DstPtr += bytes([(AlphaIndices >> 24) & 0xFF])
            DstPtr += bytes([(AlphaIndices >> 32) & 0xFF])
            DstPtr += bytes([(AlphaIndices >> 40) & 0xFF])

            DstPtr += bytes([Color0 & 0xFF])
            DstPtr += bytes([(Color0 >> 8) & 0xFF])
            DstPtr += bytes([Color1 & 0xFF])
            DstPtr += bytes([(Color1 >> 8) & 0xFF])

            DstPtr += bytes([Indices & 0xFF])
            DstPtr += bytes([(Indices >> 8) & 0xFF])
            DstPtr += bytes([(Indices >> 16) & 0xFF])
            DstPtr += bytes([(Indices >> 24) & 0xFF])

    return DstPtr
