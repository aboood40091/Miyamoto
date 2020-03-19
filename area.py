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

from PyQt5 import QtWidgets
import struct

from bytes import bytes_to_string, to_bytes
import globals

from items import ObjectItem, ZoneItem, LocationItem
from items import SpriteItem, EntranceItem, PathItem
from items import NabbitPathItem, CommentItem

from loading import LoadTileset
from misc import Metadata
import spritelib as SLib

#################################


class AbstractArea:
    """
    An extremely basic abstract area. Implements the basic function API.
    """

    def __init__(self):
        self.areanum = 1
        self.course = None
        self.L0 = None
        self.L1 = None
        self.L2 = None

    def load(self, course, L0, L1, L2, progress=None):
        self.course = course
        self.L0 = L0
        self.L1 = L1
        self.L2 = L2
        self.LoadBlocks(course)
        self.LoadTilesetNames()
        self.bgs = self.LoadBackgrounds()
        self.LoadSprites()

    def LoadBlocks(self, course):
        """
        Loads self.blocks from the course file
        """
        self.blocks = [None] * 15
        getblock = struct.Struct('<II')
        for i in range(15):
            data = getblock.unpack_from(course, i * 8)
            if data[1] == 0:
                self.blocks[i] = b''
            else:
                self.blocks[i] = course[data[0]:data[0] + data[1]]

        self.block1pos = getblock.unpack_from(course, 0)

    def LoadTilesetNames(self):
        """
        Loads block 1, the tileset names
        """
        data = struct.unpack_from('32s32s32s32s', self.blocks[0])
        self.tileset0 = bytes_to_string(data[0])
        self.tileset1 = bytes_to_string(data[1])
        self.tileset2 = bytes_to_string(data[2])
        self.tileset3 = bytes_to_string(data[3])

    def LoadBackgrounds(self):
        """
        Loads block 5, the background data
        """
        bgData = self.blocks[4]
        bgCount = len(bgData) // 28

        bgStruct = struct.Struct('<HHHH16sxBxx')
        offset = 0

        bgs = {}
        for i in range(bgCount):
            bg = bgStruct.unpack_from(bgData, offset)
            bgs[bg[0]] = bg

            offset += 28

        return bgs

    def LoadSprites(self):
        """
        Loads block 8, the sprites
        """
        spritedata = self.blocks[7]
        sprcount = len(spritedata) // 24
        sprstruct = struct.Struct('<HHHHIIBB2sBxxx')
        offset = 0
        sprites = []

        unpack = sprstruct.unpack_from
        append = sprites.append
        obj = SpriteItem
        for i in range(sprcount):
            data = unpack(spritedata, offset)
            append(obj(data[0], data[1], data[2], to_bytes(data[3], 2) + to_bytes(data[4], 4) + to_bytes(data[5], 4) + data[8], data[7], data[9]))
            offset += 24
        self.sprites = sprites

    def save(self, isNewArea=False):
        return (self.course, self.L0, self.L1, self.L2)


class Area_NSMBU(AbstractArea):
    """
    Class for a parsed NSMBU level area
    """

    def __init__(self):
        """
        Creates a completely new NSMBU area
        """
        super().__init__()

        # Default area number
        self.areanum = 1

        # Default tileset names for NSMBU
        self.tileset0 = 'Pa0_jyotyu'
        self.tileset1 = ''
        self.tileset2 = ''
        self.tileset3 = ''

        self.blocks = [b''] * 15
        self.blocks[4] = (to_bytes(0, 8) + to_bytes(0x426C61636B, 5)
                          + to_bytes(0, 15))

        # Settings
        self.eventBits32 = 0
        self.eventBits64 = 0
        self.wrapFlag = False
        self.unkFlag1 = False
        self.timelimit = 400
        self.unkFlag2 = True
        self.unkFlag3 = True
        self.unkFlag4 = True
        self.startEntrance = 0
        self.startEntranceCoinBoost = 0
        self.timelimit2 = 300
        self.timelimit3 = 0

        # Lists of things
        self.entrances = []
        self.sprites = []
        self.bounding = []
        self.zones = []
        self.locations = []
        self.pathdata = []
        self.nPathdata = []
        self.paths = []
        self.nPaths = []
        self.comments = []
        self.layers = [[], [], []]

        # Metadata
        self.LoadMiyamotoInfo(None)

        # BG data
        self.bgs = {}
        bg = struct.unpack('<HHHH16sxBxx', self.blocks[4])
        self.bgs[bg[0]] = bg

    def load(self, course, L0, L1, L2, progress=None):
        """
        Loads an area from the archive files
        """

        # Load in the course file and blocks
        self.LoadBlocks(course)

        # Load stuff from individual blocks
        self.LoadTilesetNames()  # block 1
        self.LoadOptions()  # block 2
        self.LoadEntrances()  # block 7
        self.LoadSprites()  # block 8
        self.LoadZones()  # blocks 10, 3, and 5
        self.LoadLocations()  # block 11
        self.LoadPaths()  # block 14 and 15

        # Load the editor metadata
        if self.block1pos[0] != 0x78:
            rddata = course[0x78:self.block1pos[0]]
            self.LoadMiyamotoInfo(rddata)

        else:
            self.LoadMiyamotoInfo(None)

        del self.block1pos

        # Now, load the comments
        self.LoadComments()

        if self.tileset0 not in ('', None):
            LoadTileset(0, self.tileset0)

        if self.tileset1 not in ('', None):
            LoadTileset(1, self.tileset1)

        if self.tileset2 not in ('', None):
            LoadTileset(2, self.tileset2)

        if self.tileset3 not in ('', None):
            LoadTileset(3, self.tileset3)

        # Load the object layers
        self.layers = [[], [], []]

        if L0 is not None:
            self.LoadLayer(0, L0)
        if L1 is not None:
            self.LoadLayer(1, L1)
        if L2 is not None:
            self.LoadLayer(2, L2)

        return True

    def save(self, isNewArea=False):
        """
        Save the area back to a file
        """
        # Prepare this first because otherwise the game refuses to load some sprites
        self.SortSpritesByZone()

        # We don't parse blocks 4, 6, 12, 13
        # Save the other blocks
        self.SaveTilesetNames(isNewArea)  # block 1
        self.SaveOptions()  # block 2
        self.SaveEntrances()  # block 7
        self.SaveSprites()  # block 8
        self.SaveLoadedSprites()  # block 9
        self.SaveZones()  # blocks 10, 3, and 5
        self.SaveLocations()  # block 11
        self.SavePaths()  # blocks 14 and 15

        # Save the metadata
        rdata = bytearray(self.Metadata.save())
        if len(rdata) % 4 != 0:
            for i in range(4 - (len(rdata) % 4)):
                rdata.append(0)
        rdata = bytes(rdata)

        # Save the main course file
        # We'll be passing over the blocks array two times.
        # Using bytearray here because it offers mutable bytes
        # and works directly with struct.pack_into(), so it's a
        # win-win situation
        FileLength = (15 * 8) + len(rdata)
        for block in self.blocks:
            FileLength += len(block)

        course = bytearray()
        for i in range(FileLength): course.append(0)
        saveblock = struct.Struct('<II')

        HeaderOffset = 0
        FileOffset = (15 * 8) + len(rdata)
        struct.pack_into('{0}s'.format(len(rdata)), course, 0x78, rdata)
        for block in self.blocks:
            blocksize = len(block)
            saveblock.pack_into(course, HeaderOffset, FileOffset, blocksize)
            if blocksize > 0:
                course[FileOffset:FileOffset + blocksize] = block
            HeaderOffset += 8
            FileOffset += blocksize

        # Return stuff
        return (
            bytes(course),
            self.SaveLayer(0),
            self.SaveLayer(1),
            self.SaveLayer(2),
        )

    def RemoveFromLayer(self, obj):
        """
        Removes a specific object from the level and updates Z-indices accordingly
        """
        layer = self.layers[obj.layer]
        idx = layer.index(obj)
        del layer[idx]
        for i in range(idx, len(layer)):
            upd = layer[i]
            upd.setZValue(upd.zValue() - 1)

    def SortSpritesByZone(self):
        """
        Sorts the sprite list by zone ID so it will work in-game
        """

        split = {}
        zones = []

        f_MapPositionToZoneID = SLib.MapPositionToZoneID
        zonelist = self.zones

        for sprite in self.sprites:
            zone = f_MapPositionToZoneID(zonelist, sprite.objx, sprite.objy)
            sprite.zoneID = zone
            if not zone in split:
                split[zone] = []
                zones.append(zone)
            split[zone].append(sprite)

        newlist = []
        zones.sort()
        for z in zones:
            newlist += split[z]

        self.sprites = newlist

    def LoadMiyamotoInfo(self, data):
        if (data is None) or (len(data) == 0):
            self.Metadata = Metadata()
            return

        try:
            self.Metadata = Metadata(data)
        except Exception:
            self.Metadata = Metadata()  # fallback

    def LoadOptions(self):
        """
        Loads block 2, the general options
        """
        optdata = self.blocks[1]
        optstruct = struct.Struct('<IIHHxBBBBxxBHH')
        offset = 0
        data = optstruct.unpack_from(optdata, offset)
        self.eventBits32, self.eventBits64, wrapByte, self.timelimit, unk1, unk2, unk3, self.startEntrance, self.startEntranceCoinBoost, self.timelimit2, self.timelimit3 = data
        self.wrapFlag = bool(wrapByte & 1)
        self.unkFlag1 = bool(wrapByte >> 3)
        self.unkFlag2 = bool(unk1 == 100)
        self.unkFlag3 = bool(unk2 == 100)
        self.unkFlag4 = bool(unk3 == 100)

    def LoadEntrances(self):
        """
        Loads block 7, the entrances
        """
        entdata = self.blocks[6]
        entcount = len(entdata) // 24
        entstruct = struct.Struct('<HHhhBBBBBBxBHBBBBBx')
        offset = 0
        entrances = []
        for i in range(entcount):
            data = entstruct.unpack_from(entdata, offset)
            entrances.append(EntranceItem(*data))
            offset += 24
        self.entrances = entrances

    def LoadZones(self):
        """
        Loads blocks 3, 5 and 10 - the bounding, background and zone data
        """

        # Block 3 - bounding data
        bdngdata = self.blocks[2]
        count = len(bdngdata) // 28
        bdngstruct = struct.Struct('<llllHHxxxxxxxx')
        offset = 0
        bounding = []
        for i in range(count):
            datab = bdngstruct.unpack_from(bdngdata, offset)
            bounding.append([datab[0], datab[1], datab[2], datab[3], datab[4], datab[5]])
            offset += 28
        self.bounding = bounding

        # Block 5 - Bg data
        self.bgs = self.LoadBackgrounds()

        # Block 10 - zone data
        zonedata = self.blocks[9]
        zonestruct = struct.Struct('<HHHHHHBBBBxBBxBxBBxBxx')
        count = len(zonedata) // 28
        offset = 0
        zones = []
        for i in range(count):
            dataz = zonestruct.unpack_from(zonedata, offset)

            # Find the proper bounding
            boundObj = None
            zoneBoundId = dataz[7]
            for checkb in self.bounding:
                if checkb[4] == zoneBoundId: boundObj = checkb

            # Find the proper bg
            bgObj = self.bgs[dataz[11]]

            zones.append(ZoneItem(
                dataz[0], dataz[1], dataz[2], dataz[3],
                dataz[4], dataz[5], dataz[6], dataz[7],
                dataz[8], dataz[9], dataz[10], dataz[11],
                dataz[12], dataz[13], dataz[14], dataz[15],
                boundObj, bgObj, i))
            offset += 28
        self.zones = zones

    def LoadLocations(self):
        """
        Loads block 11, the locations
        """
        locdata = self.blocks[10]
        locstruct = struct.Struct('<HHHHBxxx')
        count = len(locdata) // 12
        offset = 0
        locations = []
        for i in range(count):
            data = locstruct.unpack_from(locdata, offset)
            locations.append(LocationItem(data[0], data[1], data[2], data[3], data[4]))
            offset += 12
        self.locations = locations

    def LoadLayer(self, idx, layerdata):
        """
        Loads a specific object layer from a bytes object
        """
        objcount = len(layerdata) // 16
        objstruct = struct.Struct('<HhhHHB')
        offset = 0
        z = (2 - idx) * 8192

        layer = self.layers[idx]
        append = layer.append
        unpack = objstruct.unpack_from
        for i in range(objcount):
            data = unpack(layerdata, offset)
            # Just for clarity, assigning these things to variables explaining what they are
            tileset = (data[0] >> 12) & 3
            type = data[0] & 255
            layer = idx
            x = data[1]
            y = data[2]
            width = data[3]
            height = data[4]
            z = z
            objdata = data[5]
            append(ObjectItem(tileset, type, layer, x, y, width, height, z, objdata))
            z += 1
            offset += 16

    def LoadPaths(self):
        """
        Loads blocks 14 and 15, the paths
        """
        pathdata = self.blocks[13]
        pathcount = len(pathdata) // 12
        pathstruct = struct.Struct('<BbHHHxxxx')  # updated struct -- MrRean
        offset = 0
        unpack = pathstruct.unpack_from
        pathinfo = []
        paths = []
        for i in range(pathcount):
            data = unpack(pathdata, offset)

            if data[0] == 90:
                self.LoadNabbitPath(data)
                continue

            nodes = self.LoadPathNodes(data[2], data[3])
            add2p = {'id': int(data[0]),
                     'unk1': int(data[1]),  # no idea what this is
                     'nodes': [node for node in nodes],
                     'loops': data[4] == 2,
                     }
            pathinfo.append(add2p)

            offset += 12

        for xpi in pathinfo:
            if xpi['id'] == 90:
                continue
            for j, xpj in enumerate(xpi['nodes']):
                paths.append(PathItem(xpj['x'], xpj['y'], xpi, xpj, 0, 0, 0, 0))

        self.pathdata = pathinfo
        self.paths = paths

    def LoadNabbitPath(self, data):
        nodes = self.LoadNabbitPathNodes(data[2], data[3])

        add2p = {'nodes': [node for node in nodes]}

        paths = []
        for j, xpj in enumerate(add2p['nodes']):
            paths.append(NabbitPathItem(xpj['x'], xpj['y'], add2p, xpj, 0, 0, 0, 0))

        self.nPathdata = add2p
        self.nPaths = paths

    def LoadPathNodes(self, startindex, count):
        """
        Loads block 15, the path nodes
        """
        ret = []
        nodedata = self.blocks[14]
        nodestruct = struct.Struct('<HHffhHBBBx')
        offset = startindex * 20
        unpack = nodestruct.unpack_from
        for i in range(count):
            data = unpack(nodedata, offset)
            ret.append({'x': int(data[0]),
                        'y': int(data[1]),
                        'speed': float(data[2]),
                        'accel': float(data[3]),
                        'delay': int(data[4]),
                        })
            offset += 20
        return ret

    def LoadNabbitPathNodes(self, startindex, count):
        """
        Loads the Nabbit path nodes
        """
        ret = []
        nodedata = self.blocks[14]
        nodestruct = struct.Struct('<HHffhHBBBx')
        offset = startindex * 20
        unpack = nodestruct.unpack_from
        for i in range(count):
            data = unpack(nodedata, offset)
            ret.append({'x': int(data[0]),
                        'y': int(data[1]),
                        'action': int(data[4]),
                        'unk1': int(data[5]),
                        'unk2': int(data[6]),
                        'unk3': int(data[7]),
                        'unk4': int(data[8]),
                        })
            offset += 20
        return ret

    def LoadComments(self):
        """
        Loads the comments from self.Metadata
        """
        self.comments = []
        b = self.Metadata.binData('InLevelComments_A%d' % self.areanum)
        if b is None: return
        idx = 0
        while idx < len(b):
            xpos = b[idx] << 24
            xpos |= b[idx + 1] << 16
            xpos |= b[idx + 2] << 8
            xpos |= b[idx + 3]
            idx += 4
            ypos = b[idx] << 24
            ypos |= b[idx + 1] << 16
            ypos |= b[idx + 2] << 8
            ypos |= b[idx + 3]
            idx += 4
            tlen = b[idx] << 24
            tlen |= b[idx + 1] << 16
            tlen |= b[idx + 2] << 8
            tlen |= b[idx + 3]
            idx += 4
            s = ''
            for char in range(tlen):
                s += chr(b[idx])
                idx += 1

            com = CommentItem(xpos, ypos, s)
            com.listitem = QtWidgets.QListWidgetItem()

            self.comments.append(com)

            com.UpdateListItem()

    def SaveTilesetNames(self, isNewArea):
        """
        Saves the tileset names back to block 1
        """
        self.blocks[0] = ''.join(
            [self.tileset0.ljust(32, '\0'), self.tileset1.ljust(32, '\0'), self.tileset2.ljust(32, '\0'),
             self.tileset3.ljust(32, '\0')]).encode('latin-1')

    def SaveOptions(self):
        """
        Saves block 2, the general options
        """
        wrapByte = 1 if self.wrapFlag else 0
        if self.unkFlag1: wrapByte |= 8
        unk1 = 100 if self.unkFlag2 else 0
        unk2 = 100 if self.unkFlag3 else 0
        unk3 = 100 if self.unkFlag4 else 0

        optstruct = struct.Struct('<IIHHxBBBBxxBHH')
        buffer = bytearray(0x18)
        optstruct.pack_into(buffer, 0, self.eventBits32, self.eventBits64, wrapByte, self.timelimit,
                            unk1, unk2, unk3, self.startEntrance, self.startEntranceCoinBoost, self.timelimit2, self.timelimit3)
        self.blocks[1] = bytes(buffer)

    def SaveLayer(self, idx):
        """
        Saves an object layer to a bytes object
        """
        layer = self.layers[idx]
        if not layer: return None

        layer.sort(key=lambda obj: obj.zValue())

        offset = 0
        objstruct = struct.Struct('<HhhHHB')
        buffer = bytearray((len(layer) * 16) + 2)
        f_int = int
        for obj in layer:
            objstruct.pack_into(buffer,
                                offset,
                                f_int((obj.tileset << 12) | obj.type),
                                f_int(obj.objx),
                                f_int(obj.objy),
                                f_int(obj.width),
                                f_int(obj.height),
                                f_int(obj.data))
            offset += 16
        buffer[offset] = 0xFF
        buffer[offset + 1] = 0xFF
        return bytes(buffer)

    def SaveEntrances(self):
        """
        Saves the entrances back to block 7
        """
        offset = 0
        entstruct = struct.Struct('<HHhhBBBBBBxBHBBBBBx')
        buffer = bytearray(len(self.entrances) * 24)
        zonelist = self.zones
        for entrance in self.entrances:
            zoneID = SLib.MapPositionToZoneID(zonelist, entrance.objx, entrance.objy)
            try:
                entstruct.pack_into(buffer, offset, int(entrance.objx), int(entrance.objy), int(entrance.camerax),
                                    int(entrance.cameray), int(entrance.entid), int(entrance.destarea), int(entrance.destentrance),
                                    int(entrance.enttype), int(entrance.players), zoneID, int(entrance.playerDistance),
                                    int(entrance.entsettings), int(entrance.otherID), int(entrance.coinOrder),
                                    int(entrance.pathID), int(entrance.pathnodeindex), int(entrance.transition))
            except struct.error:
                if zoneID < 0:
                    raise ValueError('Entrance %d at (%d, %d) is too far from any zone\'s boundaries!\nPlease place it near a zone.' % (entrance.entid, int(entrance.objx), int(entrance.objy))) from None
                else:
                    raise ValueError('SaveEntrances struct.error.')
            offset += 24
        self.blocks[6] = bytes(buffer)

    def SavePaths(self):
        """
        Saves the paths back to block 14 and 15
        """
        pathstruct = struct.Struct('<BbHHHxxxx')
        nodecount = 0
        for path in self.pathdata:
            nodecount += len(path['nodes'])
        if self.nPathdata:
            nodecount += len(self.nPathdata['nodes'])
        nodebuffer = bytearray(nodecount * 20)
        nodeoffset = 0
        nodeindex = 0
        offset = 0
        pathcount = len(self.pathdata)
        if self.nPathdata:
            pathcount += 1
        buffer = bytearray(pathcount * 12)

        nPathSaved = False

        for path in self.pathdata:
            if len(path['nodes']) < 1: continue

            if path['id'] > 90 and not nPathSaved and self.nPathdata:
                self.WriteNabbitPathNodes(nodebuffer, nodeoffset, self.nPathdata['nodes'])

                pathstruct.pack_into(buffer, offset, 90, 0, int(nodeindex), int(len(self.nPathdata['nodes'])), 0)
                offset += 12
                nodeoffset += len(self.nPathdata['nodes']) * 20
                nodeindex += len(self.nPathdata['nodes'])

                nPathSaved = True

            self.WritePathNodes(nodebuffer, nodeoffset, path['nodes'])

            pathstruct.pack_into(buffer, offset, int(path['id']), 0, int(nodeindex), int(len(path['nodes'])),
                                 2 if path['loops'] else 0)
            offset += 12
            nodeoffset += len(path['nodes']) * 20
            nodeindex += len(path['nodes'])

        if not nPathSaved and self.nPathdata:
            self.WriteNabbitPathNodes(nodebuffer, nodeoffset, self.nPathdata['nodes'])

            pathstruct.pack_into(buffer, offset, 90, 0, int(nodeindex), int(len(self.nPathdata['nodes'])), 0)
            offset += 12
            nodeoffset += len(self.nPathdata['nodes']) * 20
            nodeindex += len(self.nPathdata['nodes'])

        self.blocks[13] = bytes(buffer)
        self.blocks[14] = bytes(nodebuffer)

    def WritePathNodes(self, buffer, offst, nodes):
        """
        Writes the path node data to the block 15 bytearray
        """
        offset = int(offst)

        nodestruct = struct.Struct('<HHffhHBBBx')
        for node in nodes:
            nodestruct.pack_into(buffer, offset, int(node['x']), int(node['y']), float(node['speed']),
                                 float(node['accel']), int(node['delay']), 0, 0, 0, 0)
            offset += 20

    def WriteNabbitPathNodes(self, buffer, offst, nodes):
        """
        Writes the Nabbit path node data to the block 15 bytearray
        """
        offset = int(offst)

        nodestruct = struct.Struct('<HHffhHBBBx')
        for node in nodes:
            nodestruct.pack_into(buffer, offset, int(node['x']), int(node['y']), 0.0,
                                 0.0, int(node['action']), int(node['unk1']), int(node['unk2']),
                                 int(node['unk3']), int(node['unk4']))
            offset += 20

    def SaveSprites(self):
        """
        Saves the sprites back to block 8
        """
        offset = 0
        sprstruct = struct.Struct('<HHHHIIBB2sBxxx')
        buffer = bytearray((len(self.sprites) * 24) + 4)
        f_int = int
        for sprite in self.sprites:
            zoneID = SLib.MapPositionToZoneID(self.zones, sprite.objx, sprite.objy, True)
            try:
                sprstruct.pack_into(buffer, offset, f_int(sprite.type), f_int(sprite.objx), f_int(sprite.objy),
                                    struct.unpack(">H", sprite.spritedata[:2])[0], struct.unpack(">I", sprite.spritedata[2:6])[0], struct.unpack(">I", sprite.spritedata[6:10])[0],
                                    zoneID, sprite.layer, sprite.spritedata[10:], sprite.initialState)
            except struct.error:
                # Hopefully this will solve the mysterious bug, and will
                # soon no longer be necessary.
                if zoneID < 0:
                    raise ValueError('Sprite %d at (%d, %d) is too far from any zone\'s boundaries!\nPlease place it near a zone.' % (sprite.type, sprite.objx, sprite.objy)) from None
                else:
                    raise ValueError('SaveSprites struct.error. Current sprite data dump:\n' + \
                                     str(offset) + '\n' + \
                                     str(sprite.type) + '\n' + \
                                     str(sprite.objx) + '\n' + \
                                     str(sprite.objy) + '\n' + \
                                     str(sprite.spritedata[:10]) + '\n' + \
                                     str(zoneID) + '\n' + \
                                     str(sprite.layer) + '\n' + \
                                     str(sprite.spritedata[10:]) + '\n' + \
                                     str(sprite.initialState) + '\n',
                                     )
            offset += 24
        buffer[offset] = 0xFF
        buffer[offset + 1] = 0xFF
        buffer[offset + 2] = 0xFF
        buffer[offset + 3] = 0xFF
        self.blocks[7] = bytes(buffer)

    def SaveLoadedSprites(self):
        """
        Saves the list of loaded sprites back to block 9
        """
        ls = []
        for sprite in self.sprites:
            if sprite.type not in ls: ls.append(sprite.type)
        ls.sort()

        offset = 0
        sprstruct = struct.Struct('<Hxx')
        buffer = bytearray(len(ls) * 4)
        for s in ls:
            sprstruct.pack_into(buffer, offset, int(s))
            offset += 4
        self.blocks[8] = bytes(buffer)

    def SaveZones(self):
        """
        Saves blocks 10, 3, and 5; the zone data, boundings, and background data respectively
        """
        bdngstruct = struct.Struct('<llllHHxxxxxxxx')
        bgStruct = struct.Struct('<HHHH16sxBxx')
        zonestruct = struct.Struct('<HHHHHHBBBBxBBxBxBBxBxx')
        offset = 0
        bdngs, bdngcount = self.GetOptimizedBoundings()
        bgs, bgcount = self.GetOptimizedBGs()
        zcount = len(globals.Area.zones)
        buffer2 = bytearray(28 * bdngcount)
        buffer4 = bytearray(28 * bgcount)
        buffer9 = bytearray(28 * zcount)
        for z in globals.Area.zones:
            if z.objx < 0: z.objx = 0
            if z.objy < 0: z.objy = 0
            bounding = bdngs[z.id]
            bdngstruct.pack_into(buffer2, bounding[4] * 28, bounding[0], bounding[1], bounding[2], bounding[3], bounding[4],
                                 bounding[5])
            background = bgs[z.id]
            bgStruct.pack_into(buffer4, background[0] * 28, background[0], background[1], background[2], background[3],
                               background[4], background[5])
            zonestruct.pack_into(buffer9, offset,
                                 z.objx, z.objy, z.width, z.height,
                                 0, 0, z.id, bounding[4],
                                 z.cammode, z.camzoom, z.visibility, background[0],
                                 z.camtrack, z.music, z.sfxmod, z.type)
            offset += 28

        self.blocks[2] = bytes(buffer2)
        self.blocks[4] = bytes(buffer4)
        self.blocks[9] = bytes(buffer9)

    def GetOptimizedBoundings(self):
        bdngs = {}
        bdngstruct = struct.Struct('>llllHHxxxxxxxx')
        for z in globals.Area.zones:
            bdng = bdngstruct.pack(z.yupperbound, z.ylowerbound, z.yupperbound2, z.ylowerbound2, 0, z.unknownbnf)
            if bdng not in bdngs:
                bdngs[bdng] = []
            bdngs[bdng].append(z.id)
        bdngs = sorted(bdngs.items(), key=lambda kv: min(kv[1]))
        oBdngs = {}
        for i, bdng in enumerate(bdngs):
            for z in globals.Area.zones:
                if z.id in bdng[1]:
                    oBdngs[z.id] = *bdngstruct.unpack(bdng[0])[:4], i, bdngstruct.unpack(bdng[0])[5]

        return oBdngs, len(bdngs)

    def GetOptimizedBGs(self):
        bgs = {}
        bgStruct = struct.Struct('>HHHH16sxBxx')
        for z in globals.Area.zones:
            bg = bgStruct.pack(0, z.background[1], z.background[2], z.background[3], z.background[4], z.background[5])
            if bg not in bgs:
                bgs[bg] = []
            bgs[bg].append(z.id)
        bgs = sorted(bgs.items(), key=lambda kv: min(kv[1]))
        oBgs = {}
        for i, bg in enumerate(bgs):
            for z in globals.Area.zones:
                if z.id in bg[1]:
                    oBgs[z.id] = i, *bgStruct.unpack(bg[0])[1:]

        return oBgs, len(bgs)

    def SaveLocations(self):
        """
        Saves block 11, the location data
        """
        locstruct = struct.Struct('<HHHHBxxx')
        offset = 0
        zcount = len(globals.Area.locations)
        buffer = bytearray(12 * zcount)

        for z in globals.Area.locations:
            locstruct.pack_into(buffer, offset, int(z.objx), int(z.objy), int(z.width), int(z.height), int(z.id))
            offset += 12

        self.blocks[10] = bytes(buffer)
