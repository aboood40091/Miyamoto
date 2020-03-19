#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! DX Level Editor - New Super Mario Bros. U Deluxe Level Editor
# Copyright (C) 2009-2020 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7, John10v10,
# mrbengtsson

# This file is part of Miyamoto! DX.

# Miyamoto! DX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Miyamoto! DX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Miyamoto! DX.  If not, see <http://www.gnu.org/licenses/>.


################################################################
################################################################

############ Imports ############

import os
from xml.etree import ElementTree as etree

import globals
import SarcLib
import spritelib as SLib
from tileset import CreateTilesets, SaveTileset, generateTilesetNames

#################################


class AbstractLevel:
    """
    Class for an abstract level from any game. Defines the API.
    """

    def __init__(self):
        """
        Initializes the level with default settings
        """
        self.filepath = None
        self.name = 'untitled'

        self.areas = []

    def load(self, data, areaNum, progress=None):
        """
        Loads a level from bytes data. You MUST reimplement this in subclasses!
        """
        pass

    def save(self):
        """
        Returns the level as a bytes object. You MUST reimplement this in subclasses!
        """
        return b''

    def deleteArea(self, number):
        """
        Removes the area specified. Number is a 1-based value, not 0-based;
        so you would pass a 1 if you wanted to delete the first area.
        """
        del self.areas[number - 1]
        return True


class Level_NSMBU(AbstractLevel):
    """
    Class for a level from New Super Mario Bros. U
    """

    def __init__(self):
        """
        Initializes the level with default settings
        """
        super().__init__()
        CreateTilesets()
        
        import area
        self.areas.append(area.Area_NSMBU())
        globals.Area = self.areas[0]

    def new(self):
        """
        Creates a completely new level
        """
        # Create area objects
        self.areas = []
        import area
        newarea = area.Area_NSMBU()
        globals.Area = newarea
        SLib.Area = globals.Area
        self.areas.append(newarea)

    def load(self, data, areaNum, progress=None):
        """
        Loads a NSMBU level from bytes data.
        """
        super().load(data, areaNum, progress)

        arc = SarcLib.SARC_Archive()
        arc.load(data)

        try:
            courseFolder = arc['course']
        except:
            return False

        # Sort the area data
        areaData = {}
        for file in courseFolder.contents:
            name, val = file.name, file.data

            if val is None: continue

            if not name.startswith('course'): continue
            if not name.endswith('.bin'): continue
            if '_bgdatL' in name:
                # It's a layer file
                if len(name) != 19: continue
                try:
                    thisArea = int(name[6])
                    laynum = int(name[14])
                except ValueError:
                    continue
                if not (0 < thisArea < 5): continue

                if thisArea not in areaData: areaData[thisArea] = [None] * 4
                areaData[thisArea][laynum + 1] = val
            else:
                # It's the course file
                if len(name) != 11: continue
                try:
                    thisArea = int(name[6])
                except ValueError:
                    continue
                if not (0 < thisArea < 5): continue

                if thisArea not in areaData: areaData[thisArea] = [None] * 4
                areaData[thisArea][0] = val

        # Create area objects
        self.areas = []
        thisArea = 1
        while thisArea in areaData:
            course = areaData[thisArea][0]
            L0 = areaData[thisArea][1]
            L1 = areaData[thisArea][2]
            L2 = areaData[thisArea][3]

            import area
            if thisArea == areaNum:
                newarea = area.Area_NSMBU()
                globals.Area = newarea
                SLib.Area = globals.Area
            else:
                newarea = area.AbstractArea()

            newarea.areanum = thisArea
            newarea.load(course, L0, L1, L2, progress)
            self.areas.append(newarea)

            thisArea += 1

        return True

    def save(self):
        """
        Save the level back to a file
        """

        # Make a new archive
        newArchive = SarcLib.SARC_Archive(endianness='<')

        # Create a folder within the archive
        courseFolder = SarcLib.Folder('course')
        newArchive.addFolder(courseFolder)

        # Go through the areas, save them and add them back to the archive
        for areanum, area in enumerate(self.areas):
            course, L0, L1, L2 = area.save()

            if course is not None:
                courseFolder.addFile(SarcLib.File('course%d.bin' % (areanum + 1), course))
            if L0 is not None:
                courseFolder.addFile(SarcLib.File('course%d_bgdatL0.bin' % (areanum + 1), L0))
            if L1 is not None:
                courseFolder.addFile(SarcLib.File('course%d_bgdatL1.bin' % (areanum + 1), L1))
            if L2 is not None:
                courseFolder.addFile(SarcLib.File('course%d_bgdatL2.bin' % (areanum + 1), L2))

        # Save all the tilesets
        if globals.TilesetEdited or globals.OverrideTilesetSaving:
            tilesetNames = generateTilesetNames()
            if globals.Area.tileset1:
                if globals.Area.tileset1 == "Pa1_untitled_%d" % globals.CurrentArea or globals.OverrideTilesetSaving:
                    globals.Area.tileset1 = tilesetNames[0]

                tilesetData = SaveTileset(1)

            if globals.Area.tileset2:
                if globals.Area.tileset2 == "Pa2_untitled_%d" % globals.CurrentArea or globals.OverrideTilesetSaving:
                    globals.Area.tileset2 = tilesetNames[1]

                tilesetData = SaveTileset(2)

            if globals.Area.tileset3:
                if globals.Area.tileset3 == "Pa3_untitled_%d" % globals.CurrentArea or globals.OverrideTilesetSaving:
                    globals.Area.tileset3 = tilesetNames[2]

                tilesetData = SaveTileset(3)

        return newArchive.save()[0]

    def saveNewArea(self, course_new, L0_new, L1_new, L2_new):
        """
        Save the level back to a file (when adding a new or deleting an existing Area)
        """

        # Make a new archive
        newArchive = SarcLib.SARC_Archive(endianness='<')

        # Create a folder within the archive
        courseFolder = SarcLib.Folder('course')
        newArchive.addFolder(courseFolder)

        # Go through the areas, save them and add them back to the archive
        for areanum, area in enumerate(self.areas):
            course, L0, L1, L2 = area.save(True)

            if course is not None:
                courseFolder.addFile(SarcLib.File('course%d.bin' % (areanum + 1), course))
            if L0 is not None:
                courseFolder.addFile(SarcLib.File('course%d_bgdatL0.bin' % (areanum + 1), L0))
            if L1 is not None:
                courseFolder.addFile(SarcLib.File('course%d_bgdatL1.bin' % (areanum + 1), L1))
            if L2 is not None:
                courseFolder.addFile(SarcLib.File('course%d_bgdatL2.bin' % (areanum + 1), L2))

        if course_new is not None:
            courseFolder.addFile(SarcLib.File('course%d.bin' % (len(self.areas) + 1), course_new))
        if L0_new is not None:
            courseFolder.addFile(SarcLib.File('course%d_bgdatL0.bin' % (len(self.areas) + 1), L0_new))
        if L1_new is not None:
            courseFolder.addFile(SarcLib.File('course%d_bgdatL1.bin' % (len(self.areas) + 1), L1_new))
        if L2_new is not None:
            courseFolder.addFile(SarcLib.File('course%d_bgdatL2.bin' % (len(self.areas) + 1), L2_new))

        return newArchive.save()[0]
