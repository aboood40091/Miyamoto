#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BC3 Compressor/Decompressor
# Version 0.1
# Copyright © 2018 MasterVermilli0n / AboodXD

# compress_cy.pyx
# A Cython port of Wexos's Toolbox BC3 compressor.

################################################################
################################################################

ctypedef unsigned char u8
ctypedef unsigned short u16
ctypedef unsigned int u32
ctypedef unsigned long long u64


cdef u32 * CompressAlphaBlock(u8 AlphaBlock[16], list Palette, u32 Width, u32 Height, u32 x, u32 y):
    cdef:
        u32 Indices[16]

        int y2, x2, Delta, AlphaDelta
        u8 A
        u32 Index, i

    for y2 in range(4):
        for x2 in range(4):
            if (y + y2) < Height and (x + x2) < Width:
                Index = 0
                Delta = 2147483647

                A = AlphaBlock[y2 * 4 + x2]

                for i in range(8):
                    if A == Palette[i]:
                        Index = i
                        break

                    AlphaDelta = abs(A - Palette[i])

                    if AlphaDelta < Delta:
                        Delta = AlphaDelta
                        Index = i

                Indices[y2 * 4 + x2] = Index

    return Indices


cdef list GetAlphaPalette(u8 A0, u8 A1):
    cdef list Palette = [None] * 8
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


cdef u32 * CompressBlock(u32 ColorBlock[16], u32 Palette[4], u32 Width, u32 Height, u32 x, u32 y, int ScaleR, int ScaleG, int ScaleB):
    cdef:
        u32 Indices[16]

        int y2, x2, Delta, RedDelta, GreenDelta, BlueDelta, NewDelta
        u32 Index, Color, i
        u8 R, G, B, A

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

                for i in range(4):
                    if Color == Palette[i]:
                        Index = i
                        break

                    RedDelta = abs(R - ((Palette[i] >> 16) & 0xFF))
                    GreenDelta = abs(G - ((Palette[i] >> 8) & 0xFF))
                    BlueDelta = abs(B - (Palette[i] & 0xFF))

                    NewDelta = RedDelta * ScaleR + GreenDelta * ScaleG + BlueDelta * ScaleB

                    if NewDelta < Delta:
                        Delta = NewDelta
                        Index = i

                Indices[y2 * 4 + x2] = Index

    return Indices


cdef (u8, u8, u8, u8, u8, u8, u8) FindMinMax(list Colors):
    cdef:
        u8 MaxR = 0
        u8 MaxG = 0
        u8 MaxB = 0

        u8 MinR = 255
        u8 MinG = 255
        u8 MinB = 255

        u8 TransparentBlock = 1

        u32 Color
        u8 R, G, B, A

    for Color in Colors:
        R = (Color >> 16) & 0xFF
        G = (Color >> 8) & 0xFF
        B = Color & 0xFF
        A = (Color >> 24) & 0xFF

        if not A:
            continue

        TransparentBlock = 0

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


cdef u32 ToARGB8(float Red, float Green, float Blue, float Alpha):
    cdef:
        u8 R = int(Red * 255)
        u8 G = int(Green * 255)
        u8 B = int(Blue * 255)
        u8 A = int(Alpha * 255)

    return (A << 24) | (R << 16) | (G << 8) | B


cdef u32 * GetPalette(Color0, Color1):
    cdef u32 Palette[4]

    Palette[0] = ToARGB8(((Color0 >> 11) & 0b11111) / 31, ((Color0 >> 5) & 0b111111) / 63, (Color0 & 0b11111) / 31, 0)
    Palette[1] = ToARGB8(((Color1 >> 11) & 0b11111) / 31, ((Color1 >> 5) & 0b111111) / 63, (Color1 & 0b11111) / 31, 0)
    Palette[2] = 0
    Palette[3] = 0

    R0 = (Palette[0] >> 16) & 0xFF
    G0 = (Palette[0] >> 8) & 0xFF
    B0 = Palette[0] & 0xFF
    R1 = (Palette[1] >> 16) & 0xFF
    G1 = (Palette[1] >> 8) & 0xFF
    B1 = Palette[1] & 0xFF

    Palette[2] = ((2 * R0 // 3 + 1 * R1 // 3) << 16) | ((2 * G0 // 3 + 1 * G1 // 3) << 8) | (2 * B0 // 3 + 1 * B1 // 3)
    Palette[3] = ((1 * R0 // 3 + 2 * R1 // 3) << 16) | ((1 * G0 // 3 + 2 * G1 // 3) << 8) | (1 * B0 // 3 + 2 * B1 // 3)

    return Palette


cdef u16 ToRGB565(u8 R, u8 G, u8 B):
    return ((R >> 3) << 11) | ((G >> 2) << 5) | (B >> 3)


cdef (u8, u8) FindColors(list Colors):
    cdef:
        u8 ThresholdMin = 0x02
        u8 ThresholdMax = 0xFD

        u8 PartMin = 255
        u8 PartMax = 0
        u8 Min = 255
        u8 Max = 0
        u8 UseLessThanAlgorithm = 0  # Used when colors are close to both 0 and 0xFF

        u8 Color

    for Color in Colors:
        if Color <= ThresholdMin:
            UseLessThanAlgorithm = 1

        elif Color >= ThresholdMax:
            UseLessThanAlgorithm = 1

        if not UseLessThanAlgorithm and Color < PartMin:
            PartMin = Color

        if not UseLessThanAlgorithm and Color > PartMax:
            PartMax = Color

        if Color < Min:
            Min = Color

        if Color > Max:
            Max = Color

    if Max <= 0x15 or (Min <= 0x05 and Max <= 0x30) or Min >= 0xEA or (Max >= 0xFA and Min >= 0xCF):  # What is good here?
        UseLessThanAlgorithm = 0

    else:
        Max = PartMax
        Min = PartMin

    if not UseLessThanAlgorithm and Min == Max:
        Max -= 1

    Color0 = Min if UseLessThanAlgorithm else Max
    Color1 = Max if UseLessThanAlgorithm else Min

    return Color0, Color1


cpdef bytearray compress(bytes SrcPtr, u32 Width, u32 Height):
    cdef:
        bytearray DstPtr = bytearray()

        u8 ActualAlphas[16]
        u8 A, R, G, B, MinR, MinG, MinB, MaxR, MaxG, MaxB, Alpha0, Alpha1
        u16 Color0, Color1
        int y2, x2
        u32 y, x, pos, Color, Indices
        u32 IndexBlock[16]
        u32 AlphaIndexBlock[16]
        u32 Palette[4]
        u32 ActualColors[16]
        u64 AlphaIndices
        list AlphaPalette, Colors, Alphas

    for y in range(0, Height, 4):
        for x in range(0, Width, 4):
            Colors, Alphas = [], []

            for y2 in range(4):
                for x2 in range(4):
                    if y + y2 < Height and x + x2 < Width:
                        # Read RGBA data and convert it to ARGB
                        pos = (y + y2) * Width + (x + x2)
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
                for i in range(8):
                    if not AlphaPalette[i]:
                        TransparentIndex = i
                        break

                if AlphaPalette[TransparentIndex]:
                    raise RuntimeError

                for y2 in range(4):
                    for x2 in range(4):
                        AlphaIndices |= TransparentIndex << ((y2 * 4 + x2) * 3)

            DstPtr.append(Alpha0)
            DstPtr.append(Alpha1)

            DstPtr.append(AlphaIndices & 0xFF)
            DstPtr.append((AlphaIndices >> 8) & 0xFF)
            DstPtr.append((AlphaIndices >> 16) & 0xFF)
            DstPtr.append((AlphaIndices >> 24) & 0xFF)
            DstPtr.append((AlphaIndices >> 32) & 0xFF)
            DstPtr.append((AlphaIndices >> 40) & 0xFF)

            DstPtr.append(Color0 & 0xFF)
            DstPtr.append((Color0 >> 8) & 0xFF)
            DstPtr.append(Color1 & 0xFF)
            DstPtr.append((Color1 >> 8) & 0xFF)

            DstPtr.append(Indices & 0xFF)
            DstPtr.append((Indices >> 8) & 0xFF)
            DstPtr.append((Indices >> 16) & 0xFF)
            DstPtr.append((Indices >> 24) & 0xFF)

    return DstPtr
