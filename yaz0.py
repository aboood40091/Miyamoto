#!/usr/bin/python
# -*- coding: latin-1 -*-

# Reggie Next - New Super Mario Bros. Wii / New Super Mario Bros 2 Level Editor
# Milestone 2 Alpha 4
# Copyright (C) 2009-2014 Treeki, Tempus, angelsl, JasonP27, Kamek64,
# MalStar1000, RoadrunnerWMC

# This file is part of Reggie Next.

# Reggie Next is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Reggie Next is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Reggie Next.  If not, see <http://www.gnu.org/licenses/>.


# yaz0.py
# Implementation of a yaz0 decoder/encoder in Python, by Yoshi2
# Using the specifications in http://www.amnoid.de/gc/yaz0.txt


################################################################
################################################################


import hashlib
from io import BytesIO
import math
import os
import re
import struct
from timeit import default_timer as time



class yaz0():
    """
    Yaz0 compressor/decompresser
    """
    def __init__(self, inputobj, outputobj=None, compress=False):
        
        self.compressFlag = compress
        self.fileobj = inputobj
        
        if outputobj == None:
            self.output = BytesIO
        else:
            self.output = outputobj
        
        # A way to discover the total size of the input data that
        # should be compatible with most file-like objects.
        self.fileobj.seek(0, 2)
        self.maxsize = self.fileobj.tell()
        self.fileobj.seek(0)
        
        
        if self.compressFlag == False:
            self.header = self.fileobj.read(4)
            if self.header != b'Yaz0':
                raise RuntimeError('File is not Yaz0-compressed! Header: {0}'.format(self.header))
            
            self.decompressedSize = struct.unpack('>I', self.fileobj.read(4))[0]
            nothing = self.fileobj.read(8) # Unused data
        
        else:
            self.output.write(b'Yaz0')
            
            self.output.write(struct.pack('>I', self.maxsize))
            self.output.write(b'\x00' * 8)
        

    def decompress(self):
        if self.compressFlag:
            raise RuntimeError('Compress flag is set, uncompress is not possible.')
        
        fileobj = self.fileobj
        output = self.output
        
        while output.tell() < self.decompressedSize:
            # The codebyte tells us what we need to do for the next 8 steps.
            codeByte = fileobj.read(1)
            print('codeByte {0} at position {1}'.format(hex(codeByte), fileobj.tell()))
            
            if fileobj.tell() >= self.maxsize:
                # We have reached the end of the compressed file, but the amount
                # of written data does not match the decompressed size.
                # This is generally a sign of the compressed file being invalid.
                raise RuntimeError('The end of file has been reached.'
                                   '{0} bytes out of {1} written.'.format(output.tell(), self.decompressedSize))
            
            for bit_number, bit in enumerate(self.__bit_iter__(codeByte)):
                if bit:
                    # The bit is set to 1, we do not need to decompress anything. 
                    # Write the data to the output.
                    byte = fileobj.read(1)
                    if output.tell() < self.decompressedSize:
                        output.append(byte)
                    else:
                        print (
                               'Decompressed size already reached. '
                               'Disregarding Byte {0}, ascii: [{1}]'.format(hex(byte), byte)
                               )
                    
                else:
                    if output.tell() >= self.decompressedSize:
                        print ('Bit at position {0} in byte {1} tells us that there '
                               'is more data to be decompressed, but we have reached '
                               'the decompressed size!'.format(bit_number, hex(codeByte)))
                        continue
                    
                    # Time to work some decompression magic. The next two bytes will tell us
                    # where we find the data to be copied and how much data it is.
                    byte1 = fileobj.read(1)
                    byte2 = fileobj.read(1)
                    
                    byteCount = byte1 >> 4
                    byte1_lowerNibble = byte1 & 0xF
                    
                    if byteCount == 0:
                        # We need to read a third byte which tells us 
                        # how much data we have to read.
                        byte3 = fileobj.read(1)
                       
                        byteCount = byte3 + 0x12
                    else:
                        byteCount += 2
                        
                    moveDistance = ((byte1_lowerNibble << 8) | byte2)
                    
                    normalPosition = len(output)
                    moveTo = normalPosition - (moveDistance + 1)
                    
                    if moveTo < 0: 
                        raise RuntimeError('Invalid Seek Position: Trying to move from '
                                           '{0} to {1} (MoveDistance: {2})'.format(normalPosition, moveTo,
                                                                                  moveDistance + 1))
                        
                    # We move back to a position that has the data we will copy to the front.
                    output.seek(moveTo)
                    toCopy = output.read(byteCount)
                    
                    
                    if len(toCopy) < byteCount:
                        # The data we have read is less than what we should read, 
                        # so we will repeat the data we have read so far until we 
                        # have reached the bytecount.
                        newCopy = [toCopy]
                        diff = byteCount - len(toCopy)
                        
                        # Append full copy of the current string to our new copy
                        for i in range(diff // len(toCopy)):
                            newCopy.append(toCopy)
                        
                        # Append the rest of the copy to the new copy
                        newCopy.append(toCopy[:(diff % len(toCopy))])
                        toCopy = b''.join(newCopy)


                    output.seek(normalPosition)
                    
                    
                    if self.decompressedSize - normalPosition < byteCount:
                        diff = self.decompressedSize - normalPosition
                        oldCopy = map(hex, toCopy)
                        print('Difference between current position and '
                              'decompressed size is smaller than the length '
                              'of the current string to be copied.')
                        if diff < 0:
                            raise RuntimeError('We are already past the compressed size, '
                                               'this shouldn\'t happen! Uncompressed Size: {0}, '
                                               'current position: {1}.'.format(self.decompressedSize,
                                                                               normalPosition))
                        elif diff == 0:
                            toCopy = ''
                            print('toCopy string (content: \'{0}\') has been cleared because '
                                'current position is close to decompressed size.'.format(oldCopy))
                        else:
                            toCopy = toCopy[:diff]
                            print(len(toCopy), diff)
                            print('toCopy string (content: \'{0}\') has been shortened to {1} byte/s '
                                'because current position is close to decompressed size.'.format(oldCopy,
                                                                                                 diff))
                        
                    
                    output.write(toCopy)
                       
                    
        print('Done!', codeByte)
        print('Check the output position and uncompressed size (should be the same):')
        print('OutputPos: {0}, uncompressed Size: {1}'.format(output.tell(), self.decompressedSize))
        
        return output
    
    
    # To do: 
    # 1) Optimization
    # 2) Better compression
    # 3) Testing under real conditions 
    #    (e.g. replace a file in a game with a file compressed with this method)
    def compress(self, compressLevel = 0, advanced = False):
        if not self.compressFlag:
            raise RuntimeError('Trying to compress, but compress flag is not set.'
                               'Create yaz0 object with compress = True as one of its arguments.')
        
        if compressLevel >= 10 or compressLevel < 0:
            raise RuntimeError('CompressionLevel is limited to 0-9.')
        
        fileobj = self.fileobj
        output = self.output
        maxsize = self.maxsize
        
        # compressLevel can be one of the values from 0 to 9.
        # It will reduce the area in which the method will look
        # for matches and speed up compression slightly.
        compressRatio = 0.1 * (compressLevel + 1)
        maxSearch = 2**12 - 1
        adjustedSearch = int(maxSearch  *compressRatio)
        adjustedMaxBytes = int(math.ceil(15 * compressRatio + 2))
        
        # The advanced flag will allow the use of a third byte,
        # enabling the method to look for matches that are up to 
        # 256 bytes long. NOT IMPLEMENTED YET
        
        if advanced == False:
            while fileobj.tell() < maxsize:
                buffer = bytearray()
                codeByte = 0
                
                for i in range(8):
                    # 15 bytes can be stored in a nybble. The decompressor will
                    # read 15 + 2 bytes, possibly to account for the way compression works.
                    maxBytes = adjustedMaxBytes
                    
                    # Store the current file pointer for reference.
                    currentPos = fileobj.tell()
                    
                    # Adjust maxBytes if we are close to the end.
                    if maxsize - currentPos < maxBytes:
                        maxBytes = maxsize - currentPos
                        print('Maxbytes adjusted to', maxBytes)
                    
                    # Calculate the starting position for the search
                    searchPos = currentPos - adjustedSearch
                    
                    # Should the starting position be negative, it will be set to 0.
                    # We will also adjust how much we need to read.
                    if searchPos < 0:
                        searchPos = 0
                        realSearch = currentPos
                    else:
                        realSearch = adjustedSearch
                    
                    # toSearch will be the bytes (up to 2**12 long) in which
                    # we will search for matches of the pattern.
                    pattern = fileobj.read(maxBytes)
                    fileobj.seek(searchPos)
                    toSearch = fileobj.read(realSearch)
                    fileobj.seek(currentPos + len(pattern))
                    
                    index = toSearch.rfind(pattern)
                    
                    # If a match hasn't been found, we will start a loop in which we
                    # will steadily reduce the length of the pattern, increasing the chance
                    # of finding a matching string. The pattern needs to be at least 3 bytes
                    # long, otherwise there is no point in trying to compress it.
                    # (The algorithm uses at least 2 bytes to represent such patterns)
                    while index == -1 and maxBytes > 3:
                        fileobj.seek(currentPos)
                        
                        maxBytes -= 1
                        pattern = fileobj.read(maxBytes)
                        
                        if len(pattern) < maxBytes:
                            maxBytes = len(pattern) 
                            print('adjusted pattern length')
                            
                        index = toSearch.rfind(pattern)
                    
                    if index == -1 or maxBytes <= 2:
                        # No match found. Read a byte and append it to the buffer directly.
                        fileobj.seek(currentPos)
                        byte = fileobj.read(1)
                        
                        # At the end of the file, read() will return an empty string.
                        # In that case we will set the byte to the 0 character.
                        # Hopefully, a decompressor will check the uncompressed size
                        # of the file and remove any padding bytes past this position.
                        if len(byte) == 0:
                            byte = 0
                        
                        buffer.append(byte)
                        
                        # Mark the bit in the codebyte as 1.
                        codeByte = (1 << (7-i)) | codeByte
                        
                    else:
                        # A match has been found, we need to calculate its index relative to
                        # the current position. (RealSearch stores the total size of the search string,
                        # while the index variable holds the position of the pattern in the search string)
                        relativeIndex = realSearch - index 
                        
                        # Create the two descriptor bytes which hold the length of the pattern and
                        # its index relative to the current position.
                        # Marking the bit in the codebyte as 0 isn't necessary, it will be 0 by default.
                        byte1, byte2 = self.__build_byte__(maxBytes - 2, relativeIndex - 1)
                        
                        buffer.append(byte1)
                        buffer.append(byte2)
            
                # Now that everything is done, we will append the code byte and
                # our compressed data from the buffer to the output.
                output.extend(codeByte)
                output.extend(buffer)
        else:
            raise RuntimeError('Advanced compression not implemented yet.')
        
        return output
                    
    def __build_byte__(self, byteCount, position):
        if position >= 2**12:
            raise RuntimeError('{0} is outside of the range for 12 bits!'.format(position))
        if byteCount > 0xF:
            raise RuntimeError('{0} is too much for 4 bits.'.format(byteCount))
        
        positionNibble = position >> 8
        positionByte = position & 0xFF
        
        byte1 = (byteCount << 4) | positionNibble
        
        return byte1, positionByte
        
        
    # A simple iterator for iterating over the bits of a single byte
    def __bit_iter__(self, byte):
        for i in xrange(8):
            result = (byte << i) & 0x80
            yield result != 0



#
#    Helper Functions for easier usage of
#    the compress & decompress methods of the module.
#

# Take a compressed bytes object, decompress it and return
# the result as a bytes object.
def decompress(bytesObj):
    bufferObj = BytesIO(bytesObj)
    yaz0obj = yaz0(bytesObj, compress=False)
    return yaz0obj.decompress().getvalue()

# Take a file-like object, decompress it and return the
# result as a BytesIO object.
def decompress_fileobj(fileobj):
    yaz0obj = yaz0(fileobj, compress=False)
    return yaz0obj.decompress()

# Take a file name and decompress the contents of that file. 
# If outputPath is given, save the results to a file with
# the name defined by outputPath, otherwise return the results
# as a StringIO object.
def decompress_file(filenamePath, outputPath=None):
    with open(filenamePath, 'rb') as fileobj:
        yaz0obj = yaz0(fileobj, compress=False)
        
        result = yaz0obj.decompress()
        
        if outputPath != None:
            with open(outputPath, 'wb') as output:
                output.write(result.getvalue())
            
            result = None
            
    return result

# Take an uncompressed bytes object, compress it and
# return the results as a bytes object.
def compress(bytesObj, compressLevel=9):
    buffer = BytesIO(bytesObj)
    yaz0obj = yaz0(buffer, compress=True)
    return yaz0obj.compress(compressLevel).getvalue()

# Take a file-like object, compress it and
# return the results as a BytesIO object.
def compress_fileobj(fileobj, compressLevel=9):
    yaz0obj = yaz0(fileobj, compress=True)
    return yaz0obj.compress(compressLevel)

# Take a file name and compress the contents of that file.
# If outputPath is not None, write the results to a file
# with the name defined by outputPath, otherwise return
# results as a StringIO object.
def compress_file(filenamePath, outputPath=None, compressLevel=9):
    with open(filenamePath, 'rb') as fileobj:
        yaz0obj = yaz0(fileobj, compress=True)
        
        result = yaz0obj.compress(compressLevel)
        
        if outputPath != None:
            with open(outputPath, 'wb') as output:
                output.write(result.getvalue())
            
            result = None
            
    return result


def main():
    """
    Main method for testing
    """
    compress = True
        
    if not compress:
        fileobj = open('compressed.dat', 'rb')
        yazObj = yaz0(fileobj)
        output = yazObj.decompress()
        fileobj.close()
        
        writefile = open('decompressed.dat', 'wb')
        writefile.write(output.getvalue())
        writefile.close()
        
    else:
        start = time()
        fileobj = open('decompressed.dat', 'rb')
        yazObj = yaz0(fileobj, compress = True)
        output = yazObj.compress(compressLevel = 9)
        fileobj.close()
        
        writefile = open('compressed.dat', 'wb')
        writefile.write(output.getvalue())
        writefile.close()
        
        print('Time taken: {0} seconds'.format(time()-start))


if __name__ == '__main__': main()