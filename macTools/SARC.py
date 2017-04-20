#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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

# SARC.py
# A library for opening and saving the Nintendo SARC archive format


################################################################
################################################################

# Imports

import struct


class File():
    """
    Class that represents a file of unknown format
    """
    def __init__(self, name='', data=b''):
        self.name = name
        self.data = data



class Folder():
    """
    Class that represents a folder
    """
    def __init__(self, name='', contents=None):
        self.name = name
        if contents is not None:
            self.contents = contents
        else:
            self.contents = set()

    def addFile(self, file):
        self.contents.add(file)

    def removeFile(self, file):
        self.contents.add(file)

    def addFolder(self, folder):
        self.contents.add(folder)

    def removeFolder(self, folder):
        self.contents.add(folder)



class FileArchive():
    """
    Class that represents any Nintendo file archive
    """
    def __init__(self):
        self.contents = set()
        self.endian = '>'

    def clear(self):
        self.contents = set()

    def __str__(self):
        """
        Returns a string representation of this archive
        """
        s = ''

        def addFolderStructure(folder, indent):
            """
            Adds a folder structure to the repr with an indent level set to indent
            """
            nonlocal s
            folders = set()
            files = set()
            for thing in folder:
                if isinstance(thing, File):
                    files.add(thing)
                else:
                    folders.add(thing)
            folders = sorted(folders, key=lambda entry: entry.name)
            files = sorted(files, key=lambda entry: entry.name)
            for folder in folders:
                s += '\n' + (' ' * indent) + folder.name + '/'
                addFolderStructure(folder.contents, indent + 2)
            for file in files:
                s += '\n' + (' ' * indent) + file.name

        addFolderStructure(self.contents, 0)
        return s[1:] # Remove the leading \n

    def __getitem__(self, key):
        """
        Returns the file requested when one indexes this archive
        """
        currentPlaceToLook = self.contents
        folderStructure = key.replace('\\', '/').split('/')

        for folderName in folderStructure[:-1]:
            found = False

            for lookObj in currentPlaceToLook:
                if isinstance(lookObj, Folder) and lookObj.name == folderName:
                    currentPlaceToLook = lookObj.contents
                    found = True
                    break

            if not found:
                raise KeyError('File/Folder not found')

        for file in currentPlaceToLook:
            if file.name == folderStructure[-1]: return file

        raise KeyError('File/Folder not found')


    def __setitem__(self, key, val):
        """
        Handles the request to set a value to an index of the archive
        """
        if not isinstance(val, (Folder, File)):
            raise TypeError('New value is not a file or folder!')

        currentPlaceToLook = self.contents
        folderStructure = key.replace('\\', '/').split('/')

        File.name = folderStructure[-1]

        for folderName in folderStructure[1:]:
            found = False
            for lookObj in currentPlaceToLook:
                if isinstance(lookObj, Folder) and lookObj.name == folderName:
                    currentPlaceToLook = lookObj.contents
                    found = True
                    break
            if not found:
                newFolder = Folder(folderName)
                currentPlaceToLook.add(newFolder)
                currentPlaceToLook = newFolder.contents

        for file in currentPlaceToLook:
            if file.name == key: currentPlaceToLook.remove(file)
        currentPlaceToLook.add(val)



    def __delitem__(self, key):
        """
        Handles the request to delete an index of the archive
        """
        currentPlaceToLook = self.contents
        folderStructure = key.replace('\\', '/').split('/')

        for folderName in folderStructure[1:]:
            found = False
            for lookObj in currentPlaceToLook:
                if isinstance(lookObj, Folder) and lookObj.name == folderName:
                    currentPlaceToLook = lookObj.contents
                    found = True
                    break
            if not found:
                raise KeyError('File/Folder not found')

        for file in currentPlaceToLook:
            if file.name == key:
                currentPlaceToLook.remove(file)
                return

        raise KeyError('File/Folder not found')

    def addFile(self, file):
        self.contents.add(file)

    def removeFile(self, file):
        self.contents.add(file)

    def addFolder(self, folder):
        self.contents.add(folder)

    def removeFolder(self, folder):
        self.contents.add(folder)



class SARC_Archive(FileArchive):
    """
    Class that represents a Wii U SARC Archive
    """
    def __init__(self, data=None):
        super().__init__()

        self.endianness = '>'
        # If you change this default value, be prepared
        # to make some changes to miyamoto.py, because the
        # NSMB2 file-saving code assumes that a brand-new
        # SARC_Archive will be little-endian!

        self.hashMultiplier = 0x65

        if data is not None:
            self.load(data)

    def load(self, data):
        """
        Loads a SARC file from data
        """

        result = self._load(data)
        if result is not True:
            raise ValueError('This is not a valid SARC file! Error code: ' + str(result))

    def _load(self, data):

        # SARC Header -----------------------------------------

        # File magic (0x00 - 0x03)
        if not data.startswith(b'SARC'): return 1

        # Come back to header length later, when we have endianness

        # Endianness/BOM (0x06 - 0x07)
        bom = data[0x06:0x08]
        if bom not in (b'\xFE\xFF', b'\xFF\xFE'): return 2
        bigendian = bom == b'\xFE\xFF'
        self.endianness = '>' if bigendian else '<'
        endian = self.endianness

        # Header length (0x04 - 0x05)
        headLen = struct.unpack(endian + 'H', data[0x04:0x06])[0]
        if headLen != 0x14: return 3

        # File Length (0x08 - 0x0B)
        filelen = struct.unpack(endian + 'I', data[0x08:0x0C])[0]
        if len(data) != filelen: return 4

        # Beginning Of Data offset (0x0C - 0x0F)
        begOfDat = struct.unpack(endian + 'I', data[0x0C:0x10])[0]

        # Unknown value (0x10 - 0x13)
        unkVal = struct.unpack(endian + 'I', data[0x10:0x14])[0]
        # This is always 0x10000000, but let's not check for that
        # because we ultimately don't know what this is.


        # SFAT Header -----------------------------------------

        # Sanity check (0x14 - 0x17)
        if data[0x14:0x18] != b'SFAT': return 5

        # Header length (0x18 - 0x19)
        headLen = struct.unpack(endian + 'H', data[0x18:0x1A])[0]
        if headLen != 0x0C: return 6

        # Node count (0x1A - 0x1C)
        nodeCount = struct.unpack(endian + 'H', data[0x1A:0x1C])[0]

        # Hash multiplier (0x1D - 0x1F)
        self.hashMultiplier = struct.unpack(endian + 'I', data[0x1C:0x20])[0]


        # SFAT Nodes (0x20 - 0x20+(0x10*nodeCount))
        SFATNodes = []

        SFATNodeOffset = 0x20
        for nodeNum in range(nodeCount):

            # SFAT Node ID: we don't really use this for anything.
            nodeID = struct.unpack(endian + 'I', data[SFATNodeOffset:SFATNodeOffset + 4])[0]

            if endian == '>':
                unkFlagOffset = SFATNodeOffset + 4
                fileNameTableEntryOffsetOffset = SFATNodeOffset + 5
            else:
                unkFlagOffset = SFATNodeOffset + 7
                fileNameTableEntryOffsetOffset = SFATNodeOffset + 4

            # Unknown flag: Could function as a file/folder flag.
            unkFlag = data[unkFlagOffset]

            # File Name Table Entry offset
            if endian == '>':
                fileNameTableEntryOffsetData = b'\x00' + data[fileNameTableEntryOffsetOffset:fileNameTableEntryOffsetOffset + 3]
            else:
                fileNameTableEntryOffsetData = data[fileNameTableEntryOffsetOffset:fileNameTableEntryOffsetOffset + 3] + b'\x00'
            fileNameTableEntryOffset = struct.unpack(endian + 'I', fileNameTableEntryOffsetData)[0]

            # Beginning of Node File Data
            fileDataStart = struct.unpack(endian + 'I', data[SFATNodeOffset + 8:SFATNodeOffset + 0x0C])[0]

            # End of Node File Data
            fileDataEnd = struct.unpack(endian + 'I', data[SFATNodeOffset + 0x0C:SFATNodeOffset + 0x10])[0]

            # Calculate file data length
            fileDataLength = fileDataEnd - fileDataStart

            # Add an entry to the node list
            SFATNodes.append((unkFlag, fileNameTableEntryOffset, fileDataStart, fileDataLength))

            # Increment the offset counter
            SFATNodeOffset += 0x10


        # SFNT Header -----------------------------------------

        # From now on we need to keep track of an offset variable
        offset = 0x20 + (0x10 * nodeCount)

        # Sanity check (offset - offset+0x03)
        if data[offset:offset + 0x04] != b'SFNT': return 7

        # Header length (offset+0x04 - offset+0x05)
        headLen = struct.unpack(endian + 'H', data[offset + 0x04:offset + 0x06])[0]
        if headLen != 0x08: return 8

        # Unknown value (offset+0x06 - offset+0x07)
        unkVal = struct.unpack(endian + 'H', data[offset + 0x06:offset + 0x08])[0]
        # This is always 0x0000, but let's not check for that
        # because we ultimately don't know what this is.

        # Increment the offset
        offset += 0x08


        # Add the files to the self.contents set --------------
        self.clear()
        for unkFlag, fileNameTableEntryOffset, fileDataStart, fileDataLength in SFATNodes:

            # Get the file name (search for the first null byte manually)
            nameOffset = offset + (fileNameTableEntryOffset * 4)
            nameLen = 0
            while True:
                if data[nameOffset + nameLen] > 0:
                    nameLen += 1
                else:
                    break
            name = data[nameOffset:nameOffset + nameLen].decode('utf-8')

            # Get the file data
            fileData = data[begOfDat + fileDataStart:begOfDat + fileDataStart + fileDataLength]

            # Split it into its folders
            folderStructure = name.split('/')

            # Handle it differently if the file is not in a folder
            if len(folderStructure) == 1:
                self.contents.add(File(name, fileData))
            else:
                # Get the first folder, or make one if needed
                folderName = folderStructure[0]
                foundFolder = None
                for checkFolder in self.contents:
                    if not isinstance(checkFolder, Folder): continue
                    if checkFolder.name == folderName:
                        foundFolder = checkFolder
                        break
                if foundFolder is None:
                    foundFolder = Folder(folderName)
                    self.contents.add(foundFolder)

                # Now find/make the rest of them
                outerFolder = foundFolder
                for folderName in folderStructure[1:-1]:
                    foundFolder = None
                    for checkFolder in outerFolder.contents:
                        if not isinstance(checkFolder, Folder): continue
                        if checkFolder.name == folderName:
                            foundFolder = checkFolder
                            break
                    if foundFolder is None:
                        foundFolder = Folder(folderName)
                        outerFolder.addFolder(folder)

                    outerFolder = foundFolder

                # Now make a new file and add it to self.contents
                outerFolder.addFile(File(folderStructure[-1], fileData))

        # We're done! Return True so no exception will be thrown.
        return True

    @staticmethod
    def filenameHash(filename, endian, multiplier):
        """
        Returns the hash that should be used by an SFAT node.
        """
        result = 0
        for char in filename:
            result = result * multiplier + ord(char)
            result &= 0xFFFFFFFF

        return struct.pack(endian + 'I', result)

    def save(self, padding=4, dataStartOffset=None):
        """
        Returns a bytes object that can be saved to a file.

        This function works but is a total mess that needs to be cleaned up sometime.
        """
        endian = self.endianness
        if dataStartOffset == None: dataStartOffset = padding



        # Flatten the file list
        flatList = []

        def addToFlatList(folder, path):
            nonlocal flatList

            for checkObj in folder.contents:
                if isinstance(checkObj, File):
                    flatList.append((path + '/' + checkObj.name, checkObj))
                else:
                    addToFlatList(checkObj, path + checkObj.name)

        for checkObj in self.contents:
            if isinstance(checkObj, File):
                flatList.append((checkObj.name, checkObj))
            else:
                addToFlatList(checkObj, checkObj.name)


        # Sort the files
        flatList.sort(
            key=lambda filetuple:
                struct.unpack(
                    self.endianness + 'I',
                    self.filenameHash(filetuple[0], self.endianness, self.hashMultiplier),
                    ),
            )

        # Put each file object into a list
        files = [[file,] for file in flatList]

        # Create the File Names table
        fileNamesTable = b''
        for i, filetuplelist in enumerate(files):

            filepath = filetuplelist[0][0]
            files[i] = [filetuplelist[0][1],]
            file = files[i]

            # Add the name offset, this will be used later
            file.append(len(fileNamesTable))

            # Add the name to the table
            fileNamesTable += filepath.encode('utf-8')

            # Pad to 0x04
            fileNamesTable += b'\x00' * (0x04 - (len(fileNamesTable) % 0x04))

        # Determine the length of the SFAT Nodes table
        SFATNodesTableLen = 0x10 * len(files)

        # Determine the Beginning Of Data offset
        begOfDat = max(0x20 + SFATNodesTableLen + 0x08 + len(fileNamesTable), dataStartOffset)

        # Create the File Data table
        fileDataTable = b''
        for file in files:

            # Pad it to 0x04, relative to file start (if we're not at the very start)
            totalFileLen = len(fileDataTable) + begOfDat
            if totalFileLen % padding != 0:
                fileDataTable += b'\x00' * (padding - (totalFileLen % padding))
            assert (begOfDat + len(fileDataTable)) % padding == 0

            # Add the data offset, this will be used later
            file.append(len(fileDataTable))

            # Add the data to the table
            fileDataTable += file[0].data

        # Calculate total file length
        totalFileLen = begOfDat + len(fileDataTable)


        # SARC Header -----------------------------------------

        # File magic
        sarcHead = b'SARC'

        # Header length (always 0x14)
        sarcHead += struct.pack(endian + 'H', 0x14)

        # BOM
        sarcHead += b'\xFE\xFF' if self.endianness == '>' else b'\xFF\xFE'

        # File Length
        sarcHead += struct.pack(endian + 'I', totalFileLen)

        # Beginning Of Data offset
        sarcHead += struct.pack(endian + 'I', begOfDat)

        # Unknown value 0x10000000
        if self.endianness == '>':
            sarcHead += b'\x01\x00\x00\x00'
        else:
            sarcHead += b'\x00\x01\x00\x00'

        # SFAT Header -----------------------------------------

        # File magic
        sfatHead = b'SFAT'

        # Header length (always 0x0C)
        sfatHead += struct.pack(endian + 'H', 0x0C)

        # Number of files
        sfatHead += struct.pack(endian + 'H', len(files))

        # Hash multiplier
        sfatHead += struct.pack(endian + 'I', self.hashMultiplier)

        # SFAT Nodes
        sfat = b''
        for file_filenameoffset_filedataoffset, filepath_file in zip(files, flatList):
            file, filenameoffset, filedataoffset = file_filenameoffset_filedataoffset
            #filedataoffset -= begOfDat
            print(hex(filedataoffset))
            filepath, file = filepath_file
            # File ID
            sfat += self.filenameHash(filepath, self.endianness, self.hashMultiplier)
            # Filename Offset (4 bytes + a constant?)
            sfat += struct.pack(endian + 'I', (filenameoffset // 4) | 0x1000000)
            # Filedata Offset
            sfat += struct.pack(endian + 'I', filedataoffset)
            # Filedata Length + Filedata Offset
            sfat += struct.pack(endian + 'I', filedataoffset + len(file.data))


        # SFNT Header -----------------------------------------

        # File magic
        sfntHead = b'SFNT'

        # Header length (always 0x08)
        if self.endianness == '>':
            sfntHead += b'\x00\x08'
        else:
            sfntHead += b'\x08\x00'

        # 2-byte padding
        sfntHead += b'\x00\x00'


        # File Data Table Padding
        headerSize = len(sarcHead + sfatHead + sfat + sfntHead + fileNamesTable)
        fileDataTablePadding = b''
        if begOfDat > headerSize:
            fileDataTablePadding = b'\0' * (begOfDat - headerSize)


        # Put It All Together ---------------------------------

        fileData = sarcHead + sfatHead + sfat + sfntHead + fileNamesTable + fileDataTablePadding + fileDataTable

        # Return the data
        return fileData
