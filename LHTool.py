#!/usr/bin/python3
# -*- coding: latin-1 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2017 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7

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

# LHTool.py
# Pure-Python decompressing functions for LH-compressed files
# BONUS: Contains command-line functions.
# Originally written by Treeki <treeki@gmail.com> in C++.


################################################################
################################################################


import ctypes
import os
import sys

u8 = ctypes.c_ubyte
u16 = ctypes.c_ushort
u32 = ctypes.c_uint


class LHContext():
    """
    A storage place for LH data while decompressing
    """
    def __init__(self):
        self.buf1 = bytearray(0x800)
        self.buf2 = bytearray(0x80)


def getDecompressedSize(compData):
    """
    Reads the header of the compressed data to predict the
    data size once decompressed
    """
    outSize = compData[1] | (compData[2] << 8) | (compData[3] << 16)

    if outSize == 0:
        outSize = compData[4] | (compData[5] << 8) | (compData[6] << 16) | (compData[7] << 24)

    return outSize

def loadLHPiece(buf, inData, unk):
    """
    Unknown. Has something to do with reading the LH header(s)?
    """
    r0, r4, r6, r7, r9, r10, r11, r12, r30 = \
        [u32() for i in range(9)]
    inOffset, dataSize, copiedAmount = \
        [u32() for i in range(3)]

    r6.value = 1 << unk.value;
    r7.value = 2
    r9.value = 1
    r10.value = 0
    r11.value = 0
    r12.value = r6.value - 1
    r30.value = r6.value << 1

    if unk.value <= 8:
        r6.value = inData[0]
        inOffset.value = 1
        copiedAmount.value = 1
    else:
        r6.value = inData[0] | (inData[1] << 8)
        inOffset.value = 2
        copiedAmount.value = 2

    dataSize.value = (r6.value + 1) << 2

    while copiedAmount.value < dataSize.value:

        r6.value = unk.value + 7
        r6.value = (r6.value - r11.value) >> 3
        
        if r11.value < unk.value:
            for i in range(r6.value):
                r4.value = inData[inOffset.value]
                r10.value <<= 8
                r10.value |= r4.value
                copiedAmount.value += 1
                inOffset.value += 1
            r11.value += r6.value << 3

        if r9.value < r30.value:
            r0.value = r11.value - unk.value
            r9.value += 1
            r0.value = r10.value >> r0.value
            r0.value &= r12.value
            buf[r7.value] = r0.value >> 8
            buf[r7.value + 1] = r0.value & 0xFF
            r7.value += 2

        r11.value -= unk.value

    return copiedAmount.value
    

def decompressLH(inData):
    """
    Decompresses LH data. Argument should be a
    bytes or bytearray object.
    """
    # Make a LHContext
    context = LHContext()

    # Make an in buffer (must be safely mutable)
    inBuf = bytearray(inData)

    # Make an out buffer
    outBuf = bytearray(getDecompressedSize(inBuf))

    outIndex = u32(0)
    outSize = u32(inBuf[1] | (inBuf[2] << 8) | (inBuf[3] << 16))
    inBuf = inBuf[4:]

    if outSize.value == 0:
        outSize = inBuf[0] | (inBuf[1] << 8) | (inBuf[2] << 16) | (inBuf[3] << 24)
        inBuf = inBuf[4:]

    inBuf = inBuf[loadLHPiece(context.buf1, inBuf, u8(9)):]
    inBuf = inBuf[loadLHPiece(context.buf2, inBuf, u8(5)):]

    r0 = u32(0x10)
    r3 = u32(0x100)
    r4 = u32(0)
    r5 = u32(0)
    r6 = u32(0)
    r7, r8, r9, r10, r11, r12, r25 = [u32() for i in range(7)]
    flag = False

    while outIndex.value < outSize.value:

        r12.value = 2 # Used as an offset into context.buf1
        r7.value = r4.value # Used as an offset into inBuf

        enter = True
        while flag or enter:
            enter = False

            if r6.value == 0:
                r5.value = inBuf[r7.value]
                r6.value = 8
                r4.value += 1
                r7.value += 1

            r11.value = (context.buf1[r12.value] << 8) | context.buf1[r12.value + 1]
            r8.value = r5.value >> (r6.value - 1)
            r6.value -= 1

            r9.value = r8.value & 1
            r10.value = r11.value & 0x7F
            r8.value = r3.value >> r9.value # sraw?
            r8.value = r11.value & r8.value
            flag = (r8.value == 0)
            r8.value = (r10.value + 1) << 1
            r9.value += r8.value

            if flag:
                r12.value &= ~3
                r8.value = r9.value << 1
                r12.value += r8.value
            else:
                r8.value = r12.value & ~3
                r7.value = r9.value << 1
                r7.value = (context.buf1[r8.value + r7.value] << 8) | context.buf1[r8.value + r7.value + 1]

        if r7.value < 0x100:
            outBuf[outIndex.value] = u8(r7.value).value
            outIndex.value += 1
            continue

        # block copy?
        r7.value &= 0xFF
        r25.value = 2
        r7.value += 3
        r7.value &= 0xFFFF # r7 is really an ushort, probably
        r8.value = r4.value # used as an offset into inBuf

        enter = True
        while enter or flag:
            enter = False

            if r6.value == 0:
                r5.value = inBuf[r8.value]
                r6.value = 8
                r4.value += 1
                r8.value += 1

            r12.value = (context.buf2[r25.value] << 8) | context.buf2[r25.value + 1]
            r9.value = r5.value >> (r6.value - 1)
            r6.value -= 1
            r10.value = r9.value & 1
            r11.value = r12.value & 7
            r9.value = r0.value >> r10.value # sraw
            r9.value = r12.value & r9.value
            flag = (r9.value == 0)
            r9.value = r11.value + 1
            r9.value <<= 1
            r10.value += r9.value

            if flag:
                r25.value &= ~3
                r9.value = r10.value << 1
                r25.value += r9.value
            else:
                r9.value = r25.value & ~3
                r8.value = r10.value << 1
                r11.value = (context.buf2[r9.value + r8.value] << 8) | context.buf2[r9.value + r8.value + 1]

        r10.value = 0
        if r11.value != 0:
            r8.value = r4.value # offset into inBuf
            r10.value = 1

            r11.value -= 1
            r9.value = r11.value & 0xFFFF
            while r9.value != 0:
                r10.value = (r10.value << 1) & 0xFFFF
                if r6.value == 0:
                    r5.value = inBuf[r8.value]
                    r6.value = 8
                    r4.value += 1
                    r8.value += 1

                r6.value -= 1
                r9.value = r5.value >> r6.value
                r9.value &= 1
                r10.value |= r9.value

                r11.value -= 1
                r9.value = r11.value & 0xFFFF

        if (outIndex.value + r7.value) > outSize.value:
            r7.value = outSize.value - outIndex.value
            r7.value &= 0xFFFF

        r9.value = r10.value + 1
        r8.value = outIndex.value # offset into outBuf
        r10.value = r9.value & 0xFFFF

        # Block copy loop
        r9.value = r7.value & 0xFFFF
        r7.value -= 1
        while r9.value != 0:
            r9.value = outIndex.value - r10.value
            outIndex.value += 1
            outBuf[r8.value] = outBuf[r9.value]
            r8.value += 1

            r9.value = r7.value & 0xFFFF
            r7.value -= 1

    return bytes(outBuf)

def isLHCompressed(data):
    """
    Returns True if it appears that the data is LH-compressed.
    """

    # The only way to tell if a file is LH-compressed is that
    # it appears that every LH file begins with an @.
    # Since U8 archives begin with U\xAA8-, they will
    # never trigger this.
    return data.startswith(b'@')

def main():
    """
    Main script function for command-line usage
    """

    # Print message
    print('LH Tool by RoadrunnerWMC')
    print('For the Miyamoto! Next Level Editor')
    print('Originally LH Decompressor by Treeki')
    print('Converted to Python by RoadrunnerWMC')
    print('Compressing not yet implemented!')

    # Argument parsing!
    argv = list(sys.argv)

    selfName = argv[0]
    argv = argv[1:]

    argsAreCorrect = ('-d' in argv) or ('-c' in argv)
    if ('-d' in argv) and ('-c' in argv):
        argsAreCorrect = False
    if len(argv) != 3:
        argsAreCorrect = False

    if not argsAreCorrect:
        errorTxt = '' \
            'Command-line arguments are missing or wrong. Usage:\n' \
            'To decompress a file: ' + selfName + ' -d compFile.bin decompFile.bin\n' \
            'To compress a file: ' + selfName + ' -c decompFile.bin compFile.bin\n'
        raise ValueError(errorTxt)

    if '-d' in argv:
        mode = 'd'
        argv.remove('-d')
    else:
        mode = 'c'
        argv.remove('-c')

    inFileName = argv[0]
    outFileName = argv[1]

    # Open the file
    with open(inFileName, 'rb') as inFile:
        inData = inFile.read()

    # Do stuff with the data
    if mode == 'd':
        # Decompress
        outData = decompressLH(inData)
    else:
        # Compress
        raise NotImplementedError('Compression is not yet implemented!!!')

    # Save the file
    with open(outFileName, 'wb') as outFile:
        outFile.write(outData)


if __name__ == '__main__': main()
