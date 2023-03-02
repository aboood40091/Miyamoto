#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2021 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7, John10v10,
# mrbengtsson

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


################################################################
################################################################

############ Imports ############

import os
from xml.etree import ElementTree as etree

import globals
import SarcLib
import spritelib as SLib
from tileset import CreateTilesets, SaveTileset

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

    def save(self, innerfilename):
        """
        Save the level back to a file
        """

        # Save all the tilesets before anything
        if globals.TilesetEdited or globals.OverrideTilesetSaving:
            if globals.Area.tileset1:
                tilesetData = SaveTileset(1)
                if tilesetData:
                    globals.szsData[globals.Area.tileset1] = tilesetData

            if globals.Area.tileset2:
                tilesetData = SaveTileset(2)
                if tilesetData:
                    globals.szsData[globals.Area.tileset2] = tilesetData

            if globals.Area.tileset3:
                tilesetData = SaveTileset(3)
                if tilesetData:
                    globals.szsData[globals.Area.tileset3] = tilesetData

        # Make a new archive
        newArchive = SarcLib.SARC_Archive()

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

        # Here we have the new inner-SARC savedata
        innersarc = newArchive.save()[0]
        globals.szsData[innerfilename] = innersarc

        # Now make an outer SARC
        outerArchive = SarcLib.SARC_Archive()

        # Add the innersarc to it
        outerArchive.addFile(SarcLib.File(innerfilename, innersarc))

        # Make it easy for future Miyamotos to pick out the innersarc level name
        outerArchive.addFile(SarcLib.File('levelname', innerfilename.encode('utf-8')))
        globals.szsData['levelname'] = innerfilename.encode('utf-8')

        # Add all the other stuff, too
        if os.path.isdir(globals.miyamoto_path + '/data'):
            szsNewData = {}

            szsNewData[innerfilename] = globals.szsData[innerfilename]
            szsNewData['levelname'] = globals.szsData['levelname']

            paths = [globals.miyamoto_path + '/miyamotodata/spriteresources.xml']
            for path in globals.gamedef.recursiveFiles('spriteresources'):
                if path:
                    paths.append(os.path.join(globals.miyamoto_path, path if isinstance(path, str) else path.path))

            sprites_xml = {}
            for path in paths:
                # Read the sprites resources xml
                tree = etree.parse(path)
                root = tree.getroot()

                # Get all sprites' filenames and add them to a list
                for sprite in root.iter('sprite'):
                    id = int(sprite.get('id'))

                    name = []
                    for id2 in sprite:
                        name.append(id2.get('name'))

                    sprites_xml[id] = list(name)

            # Look up every sprite and tileset used in each area
            sprites_SARC = []
            tilesets_names = []
            for area_SARC in globals.Level.areas:
                for sprite in area_SARC.sprites:
                    sprites_SARC.append(sprite.type)

                if area_SARC.tileset0 not in ('', None):
                    tilesets_names.append(area_SARC.tileset0)

                if area_SARC.tileset1 not in ('', None):
                    tilesets_names.append(area_SARC.tileset1)

                if area_SARC.tileset2 not in ('', None):
                    tilesets_names.append(area_SARC.tileset2)

                if area_SARC.tileset3 not in ('', None):
                    tilesets_names.append(area_SARC.tileset3)

            sprites_SARC = list(set(sprites_SARC))
            tilesets_names = list(set(tilesets_names))

            # Sort the filenames for each "used" sprite
            sprites_names = []
            for sprite in sprites_SARC:
                if sprite in sprites_xml:
                    for sprite_name in sprites_xml[sprite]:
                        sprites_names.append(sprite_name)

            sprites_names = list(set(sprites_names))

            # Look up each needed file and add it to our archive
            for sprite_name in sprites_names:
                # Get it from inside the original archive
                if not globals.OverwriteSprite and sprite_name in globals.szsData:
                    outerArchive.addFile(SarcLib.File(sprite_name, globals.szsData[sprite_name]))
                    szsNewData[sprite_name] = globals.szsData[sprite_name]

                # Get it from the "custom" data folder
                elif os.path.isfile(globals.miyamoto_path + '/data/custom/' + sprite_name):
                    with open(globals.miyamoto_path + '/data/custom/' + sprite_name, 'rb') as f:
                        f1 = f.read()

                    outerArchive.addFile(SarcLib.File(sprite_name, f1))
                    szsNewData[sprite_name] = f1

                # Get it from the data folder
                elif os.path.isfile(globals.miyamoto_path + '/data/' + sprite_name):
                    with open(globals.miyamoto_path + '/data/' + sprite_name, 'rb') as f:
                        f1 = f.read()

                    outerArchive.addFile(SarcLib.File(sprite_name, f1))
                    szsNewData[sprite_name] = f1

                # Throw a warning because the file was not found...
                else:
                    print("WARNING: Could not find the file: %s" % sprite_name)
                    print("Expect the level to crash ingame...")

            # Add each tileset to our archive
            for tileset_name in tilesets_names:
                if tileset_name in globals.szsData:
                    outerArchive.addFile(SarcLib.File(tileset_name, globals.szsData[tileset_name]))
                    szsNewData[tileset_name] = globals.szsData[tileset_name]

            # Add the other default Pa0 tilesets to our new dict
            for def_tileset in globals.Pa0Tilesets:
                if def_tileset not in szsNewData and def_tileset in globals.szsData:
                    szsNewData[def_tileset] = globals.szsData[def_tileset]

            globals.szsData = szsNewData

        else:
            # data folder not found, copy the files
            for szsThingName in globals.szsData:
                if szsThingName in [globals.levelNameCache, innerfilename, 'levelname']: continue
                outerArchive.addFile(SarcLib.File(szsThingName, globals.szsData[szsThingName]))

        # Save the outer sarc and return it
        return outerArchive.save()[0]

    def saveNewArea(self, innerfilename, course_new, L0_new, L1_new, L2_new):
        """
        Save the level back to a file (when adding a new or deleting an existing Area)
        """

        # Make a new archive
        newArchive = SarcLib.SARC_Archive()

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

        # Here we have the new inner-SARC savedata
        innersarc = newArchive.save()[0]

        # Now make an outer SARC
        outerArchive = SarcLib.SARC_Archive()

        # Add the innersarc to it
        outerArchive.addFile(SarcLib.File(innerfilename, innersarc))

        # Make it easy for future Miyamotos to pick out the innersarc level name
        outerArchive.addFile(SarcLib.File('levelname', innerfilename.encode('utf-8')))

        # Add all the other stuff, too
        for szsThingName in globals.szsData:
            if szsThingName in [globals.levelNameCache, 'levelname']: continue
            outerArchive.addFile(SarcLib.File(szsThingName, globals.szsData[szsThingName]))

        # Save the outer sarc and return it
        return outerArchive.save()[0]
