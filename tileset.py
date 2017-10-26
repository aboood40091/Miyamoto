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


################################################################
################################################################

import os
import platform
import struct

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

import globals
import SARC as SarcLib
import spritelib as SLib


class TilesetTile:
    """
    Class that represents a single tile in a tileset
    """

    def __init__(self, main=None, nml=None):
        """
        Initializes the TilesetTile
        """
        if not main:
            main = QtGui.QPixmap(60, 60)
            main.fill(Qt.transparent)

        self.main = main

        if not nml:
            nml = QtGui.QPixmap(60, 60)
            nml.fill(QtGui.QColor(128, 128, 255))

        self.nml = nml
        self.isAnimated = False
        self.animFrame = 0
        self.animTiles = []
        self.collData = ()
        self.collOverlay = None

    def addAnimationData(self, data):
        """
        Applies animation data to the tile
        """
        animTiles = []

        dest = QtGui.QPixmap.fromImage(data)
        for y in range(dest.height() // 64):
            for x in range(dest.width() // 64):
                tile = dest.copy((x * 64) + 2, (y * 64) + 2, 60, 60)
                animTiles.append(tile)

        self.animTiles = animTiles
        self.isAnimated = True

    def addConveyorAnimationData(self, data, x, reverse=False):
        """
        Applies animation data to the conveyor tile
        """
        animTiles = []

        dest = QtGui.QPixmap.fromImage(data)

        for y in range(dest.height() // 64):
            tile = dest.copy((x * 64) + 2, (y * 64) + 2, 60, 60)
            animTiles.append(tile)

        if reverse:
            animTiles = list(reversed(animTiles))

        self.animTiles = animTiles
        self.isAnimated = True

    def nextFrame(self):
        """
        Increments to the next frame
        """
        if not self.isAnimated: return
        self.animFrame += 1
        if self.animFrame == len(self.animTiles):
            self.animFrame = 0

    def resetAnimation(self):
        """
        Resets the animation frame
        """
        self.animFrame = 0

    def getCurrentTile(self):
        """
        Returns the current tile based on the current animation frame
        """
        result = None
        if (not globals.TilesetsAnimating) or (not self.isAnimated):
            result = self.main
        else:
            result = self.animTiles[self.animFrame]
        result = QtGui.QPixmap(result)

        p = QtGui.QPainter(result)
        if globals.CollisionsShown and (self.collOverlay is not None):
            p.drawPixmap(0, 0, self.collOverlay)
        del p

        return result

    def setCollisions(self, colldata):
        """
        Sets the collision data for this tile
        """
        self.collData = tuple(colldata)
        self.updateCollisionOverlay()

    def setQuestionCollisions(self):
        """
        Sets the collision data to that of a question block
        """
        self.setCollisions((7, 0, 0, 0, 1, 0, 0, 0))

    def setBrickCollisions(self):
        """
        Sets the collision data to that of a brick block
        """
        self.setCollisions((6, 0, 0, 0, 1, 0, 0, 0))

    def updateCollisionOverlay(self):
        """
        Updates the collisions overlay for this pixmap
        """
        # From Puzzle NSMBU:
        # https://github.com/aboood40091/Puzzle-NSMBU/blob/master/puzzle.py

        CD = self.collData
        # Sets the colour based on terrain type
        if CD[5] == 1:  # Ice
            color = QtGui.QColor(0, 0, 255, 120)
        elif CD[5] == 2:  # Snow
            color = QtGui.QColor(120, 120, 255, 120)
        elif CD[5] == 4:  # Sand
            color = QtGui.QColor(128,64,0, 120)
        elif CD[5] == 5:  # Grass
            color = QtGui.QColor(0, 255, 0, 120)
        else:
            color = QtGui.QColor(0, 0, 0, 120)

        # Sets Brush style for fills
        if CD[0] in [14, 20, 21]:  # Climbing Grid
            style = Qt.DiagCrossPattern
        elif CD[0] in [5, 6, 7]:  # Breakable
            style = Qt.Dense5Pattern
        else:
            style = Qt.SolidPattern

        brush = QtGui.QBrush(color, style)
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 128))
        collPix = QtGui.QPixmap(globals.TileWidth, globals.TileWidth)
        collPix.fill(QtGui.QColor(0, 0, 0, 0))
        painter = QtGui.QPainter(collPix)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Paints shape based on other junk
        if CD[0] == 0xB:  # Slope
            if not CD[2]:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, 0)]))
            elif CD[2] == 1:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 2:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5)]))
            elif CD[2] == 3:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth)]))
            elif CD[2] == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth)]))
            elif CD[2] == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 10:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, 0)]))
            elif CD[2] == 11:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.75),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth)]))
            elif CD[2] == 12:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.75),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 13:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.25),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 14:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.25),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 15:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.25),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 16:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.25),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 17:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.75),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 18:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.75),
                                                    QtCore.QPoint(0, globals.TileWidth)]))

        elif CD[0] == 0xC:  # Reverse Slope
            if not CD[2]:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, 0)]))
            elif CD[2] == 1:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0)]))
            elif CD[2] == 2:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5)]))
            elif CD[2] == 3:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, 0)]))
            elif CD[2] == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5)]))
            elif CD[2] == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0)]))
            elif CD[2] == 10:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, 0)]))
            elif CD[2] == 11:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.25)]))
            elif CD[2] == 12:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.25)]))
            elif CD[2] == 13:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.75),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5)]))
            elif CD[2] == 14:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.75)]))
            elif CD[2] == 15:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.75),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 16:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.75)]))
            elif CD[2] == 17:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.25),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5)]))
            elif CD[2] == 18:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.25)]))

        elif CD[0] == 9:  # Partial
            if CD[2] == 2:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5)]))

        elif CD[4] == 3:  # Solid-on-bottom
            painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.75),
                                                QtCore.QPoint(0, globals.TileWidth * 0.75)]))

            painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.625, 0),
                                                QtCore.QPoint(globals.TileWidth * 0.625, globals.TileWidth * 0.5),
                                                QtCore.QPoint(globals.TileWidth * 0.75, globals.TileWidth * 0.5),
                                                QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth * (17/24)),
                                                QtCore.QPoint(globals.TileWidth * 0.25, globals.TileWidth * 0.5),
                                                QtCore.QPoint(globals.TileWidth * 0.375, globals.TileWidth * 0.5),
                                                QtCore.QPoint(globals.TileWidth * 0.375, 0)]))

        elif CD[4] == 2:  # Solid-on-top
            painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                QtCore.QPoint(globals.TileWidth, 0),
                                                QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.25),
                                                QtCore.QPoint(0, globals.TileWidth * 0.25)]))

            painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.625, globals.TileWidth),
                                                QtCore.QPoint(globals.TileWidth * 0.625, globals.TileWidth * 0.5),
                                                QtCore.QPoint(globals.TileWidth * 0.75, globals.TileWidth * 0.5),
                                                QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth * 0.295),
                                                QtCore.QPoint(globals.TileWidth * 0.25, globals.TileWidth * 0.5),
                                                QtCore.QPoint(globals.TileWidth * 0.375, globals.TileWidth * 0.5),
                                                QtCore.QPoint(globals.TileWidth * 0.375, globals.TileWidth)]))

        elif CD[0] == 15:  # Spikes
            if CD[2] == 3:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.25)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.75)]))
            if CD[2] == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.25)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.75)]))
            if CD[2] == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.25, 0)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.75, 0)]))
            if CD[2] == 6:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.25, globals.TileWidth)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.75, globals.TileWidth)]))

        elif CD[4] == 1 or CD[0] in [6, 7]:  # Solid
            painter.drawRect(0, 0, globals.TileWidth, globals.TileWidth)

        self.collOverlay = collPix


class ObjectDef:
    """
    Class for the object definitions
    """

    def __init__(self):
        """
        Constructor
        """
        self.width = 0
        self.height = 0
        self.randByte = 0
        self.rows = []
        self.data = 0

    def load(self, source, offset):
        """
        Load an object definition
        """
        i = offset
        row = []
        cbyte = source[i]

        while cbyte != 0xFF and i < len(source):
            cbyte = source[i]

            if cbyte == 0xFE:
                self.rows.append(row)
                i += 1
                row = []

            elif (cbyte & 0x80) != 0:
                row.append((cbyte,))
                i += 1

            else:
                if i + 1 >= len(source) or i + 2 >= len(source):
                    break

                extra = source[i + 2]
                tile = [cbyte, source[i + 1] | ((extra & 3) << 8), extra >> 2]
                row.append(tile)
                i += 3


def CreateTilesets():
    """
    Blank out the tileset arrays
    """
    T = TilesetTile()
    T.setCollisions([0] * 8)
    globals.Tiles = [T] * 0x200 * 4
    globals.Tiles += globals.Overrides
    # globals.TileBehaviours = [0]*1024
    globals.TilesetAnimTimer = QtCore.QTimer()
    globals.TilesetAnimTimer.timeout.connect(IncrementTilesetFrame)
    globals.TilesetAnimTimer.start(90)
    globals.ObjectDefinitions = [None] * 4
    SLib.Tiles = globals.Tiles


def getUsedTiles():
    """
    Get the number of used tiles in each tileset
    """
    usedTiles = {}

    for idx in range(1, 4):
        usedTiles[idx] = []

        defs = globals.ObjectDefinitions[idx]

        if defs is not None:
            for i in range(256):
                obj = defs[i]
                if obj is None: break

                for row in obj.rows:
                    for tile in row:
                        if len(tile) == 3:
                            randLen = obj.randByte & 0xF
                            tileNum = tile[1] & 0xFF
                            if randLen > 0:
                                for i in range(randLen):
                                    if tileNum + i not in usedTiles[idx]:
                                        usedTiles[idx].append(tileNum + i)
                            else:
                                if tileNum not in usedTiles[idx]:
                                    usedTiles[idx].append(tileNum)

    return usedTiles


def addObjToTileset(obj, colldata, img, nml, isfromAll=False):
    """
    Adds a specific object to one of the tilesets
    """
    if isfromAll:
        paintType = 10

    else:
        paintType = 11

    objNum = -1

    for idx in range(1, 4):
        # Get the number of used tiles in this tileset
        usedTiles = getUsedTiles()[idx]
        if len(usedTiles) >= 256:  # It can't be more than 256, oh well
            # Skip to to the next tileset because no free tiles were found
            continue

        # Get the number of tiles in this object
        if len(obj.rows) == 1:
            randLen = obj.randByte & 0xF

        else:
            randLen = 0

        numTiles = 0
        for row in obj.rows:
            for tile in row:
                if len(tile) == 3:
                    numTiles += (randLen if randLen else 1)

        
        if numTiles + len(usedTiles) > 256:
            # Skip to to the next tileset because the free tiles are not enough
            continue

        tileoffset = idx * 256

        # Add the free tiles to a list
        freeTiles = []
        for i in range(256):
            if i not in usedTiles: freeTiles.append(i)

        # Handle randomized objects differently
        if randLen:
            # Look for any "randLen" free tiles in a row
            found = False
            for i in freeTiles:
                for z in range(randLen):
                    if i + z not in freeTiles:
                        break

                    if z == randLen - 1:
                        tileNum = i
                        found = True
                        break

                if found:
                    break

            if not found:
                # Skip to to the next tileset because no "randLen" free tiles in a row were found
                continue

            # Set the object's tiles' indecies
            ctile = 0
            z = 0
            for tile in obj.rows[0]:
                if len(tile) == 3:
                    obj.rows[0][ctile][1] = (tileNum + z) | (idx << 8)
                    if z < randLen:
                        z += 1
                ctile += 1

            if globals.ObjectDefinitions[idx] is None:
                # Make us a new ObjectDefinitions for this tileset
                globals.ObjectDefinitions[idx] = [None] * 256

            defs = globals.ObjectDefinitions[idx]

            # Set the object's number
            objNum = 0
            while defs[objNum] is not None and objNum < 256:
                objNum += 1

            globals.ObjectDefinitions[idx][objNum] = obj

            # Adds the object's tiles to the Tiles dict.
            tileNum += tileoffset
            for z in range(randLen):
                T = TilesetTile(img.copy(z * 60, 0, 60, 60), nml.copy(z * 60, 0, 60, 60))
                T.setCollisions(struct.unpack_from('>8B', colldata, z * 8))
                globals.Tiles[tileNum + z] = T

        else:
            # Set the object's tiles' indecies
            ctile = 0
            crow = 0
            i = 0
            for row in obj.rows:
                for tile in row:
                    if len(tile) == 3:
                        obj.rows[crow][ctile][1] = freeTiles[i] | (idx << 8)
                        i += 1
                    ctile += 1
                crow += 1
                ctile = 0

            if globals.ObjectDefinitions[idx] is None:
                # Make us a new ObjectDefinitions for this tileset
                globals.ObjectDefinitions[idx] = [None] * 256

            defs = globals.ObjectDefinitions[idx]

            # Set the object's number
            objNum = 0
            while defs[objNum] is not None and objNum < 256:
                objNum += 1

            globals.ObjectDefinitions[idx][objNum] = obj

            # Checks if the slop is reversed and reverses the rows
            # Also adds the object's tiles to the Tiles dict.
            isSlope = obj.rows[0][0][0]
            if (isSlope & 0x80) and (isSlope & 0x2):
                x = 0
                y = (obj.height - 1) * 60
                i = 0
                crow = 0
                for row in obj.rows:
                    for tile in row:
                        if len(tile) == 3:
                            tileNum = (tile[1] & 0xFF) + tileoffset
                            T = TilesetTile(img.copy(x, y, 60, 60), nml.copy(x, y, 60, 60))
                            realRow = len(obj.rows) - 1 - crow
                            colls = struct.unpack_from('>8B', colldata, (8 * obj.width * realRow) + i)
                            T.setCollisions(colls)
                            globals.Tiles[tileNum] = T
                            x += 60
                            i += 8
                    crow += 1
                    y -= 60
                    x = 0
                    i = 0

            else:
                x = 0
                y = 0
                i = 0
                for row in obj.rows:
                    for tile in row:
                        if len(tile) == 3:
                            tileNum = (tile[1] & 0xFF) + tileoffset
                            T = TilesetTile(img.copy(x, y, 60, 60), nml.copy(x, y, 60, 60))
                            T.setCollisions(struct.unpack_from('>8B', colldata, i))
                            globals.Tiles[tileNum] = T
                            x += 60
                            i += 8
                    y += 60
                    x = 0

        # Set the paint type
        paintType = idx

        # Misc.
        SLib.Tiles = globals.Tiles

        globals.mainWindow.objPicker.LoadFromTilesets()

        if not eval('globals.Area.tileset%d' % idx):
            if idx == 1:
                globals.Area.tileset1 = 'temp1'

            elif idx == 2:
                globals.Area.tileset2 = 'temp2'

            elif idx == 3:
                globals.Area.tileset3 = 'temp3'

        globals.mainWindow.updateNumUsedTilesLabel()

        break

    return paintType, objNum


def writeGTX(tex, idx):
    """
    Generates a GTX file from a QImage
    """
    if platform.system() == 'Windows':
        tile_path = globals.miyamoto_path + '/Tools'

    elif platform.system() == 'Linux':
        tile_path = globals.miyamoto_path + '/linuxTools'

    elif platform.system() == 'Darwin':
        tile_path = globals.miyamoto_path + '/macTools'

    if idx != 0:  # Save as DXT5/BC3
        tex.save(tile_path + '/tmp.png')
    
        os.chdir(tile_path)

        if platform.system() == 'Windows':
            exe = 'nvcompress.exe'

        elif platform.system() == 'Linux':
            os.system('chmod +x nvcompress.elf')
            exe = './nvcompress.elf'

        elif platform.system() == 'Darwin':
            os.system('chmod 777 nvcompress-osx.app')
            exe = './nvcompress-osx.app'

        os.system(exe + ' -bc3 tmp.png tmp.dds')
    
        os.chdir(globals.miyamoto_path)

        os.remove(tile_path + '/tmp.png')

    else:  # Save as RGBA8
        import dds

        data = tex.bits()
        data.setsize(tex.byteCount())
        data = data.asstring()

        with open(tile_path + '/tmp.dds', 'wb+') as out:
            hdr = dds.generateRGBA8Header(2048, 512)
            out.write(hdr)
            out.write(data)

    import gtx
    gtxdata = gtx.DDStoGTX(tile_path + '/tmp.dds')

    os.remove(tile_path + '/tmp.dds')

    return gtxdata


def PackTexture(idx, nml=False):
    """
    Packs the tiles into a GTX file
    """
    tex = QtGui.QImage(2048, 512, QtGui.QImage.Format_RGBA8888)
    tex.fill(Qt.transparent)
    painter = QtGui.QPainter(tex)

    tileoffset = idx * 256
    x = 0
    y = 0

    for i in range(tileoffset, tileoffset + 256):
        tile = QtGui.QImage(64, 64, QtGui.QImage.Format_RGBA8888)
        tile.fill(Qt.transparent)
        tilePainter = QtGui.QPainter(tile)

        tilePainter.drawPixmap(2, 2, globals.Tiles[i].nml if nml else globals.Tiles[i].main)
        tilePainter.end()

        for i in range(2, 62):
            color = tile.pixel(i, 2)
            for pix in range(0,2):
                tile.setPixel(i, pix, color)

            color = tile.pixel(2, i)
            for p in range(0,2):
                tile.setPixel(p, i, color)

            color = tile.pixel(i, 61)
            for p in range(62,64):
                tile.setPixel(i, p, color)

            color = tile.pixel(61, i)
            for p in range(62,64):
                tile.setPixel(p, i, color)

        color = tile.pixel(2, 2)
        for a in range(0, 2):
            for b in range(0, 2):
                tile.setPixel(a, b, color)

        color = tile.pixel(61, 2)
        for a in range(62, 64):
            for b in range(0, 2):
                tile.setPixel(a, b, color)

        color = tile.pixel(2, 61)
        for a in range(0, 2):
            for b in range(62, 64):
                tile.setPixel(a, b, color)

        color = tile.pixel(61, 61)
        for a in range(62, 64):
            for b in range(62, 64):
                tile.setPixel(a, b, color)


        painter.drawImage(x, y, tile)

        x += 64

        if x >= 2048:
            x = 0
            y += 64

    painter.end()

    outData = writeGTX(tex, idx)

    return outData


def SaveTileset(idx):
    """
    Saves a tileset from a specific slot
    """
    name = eval('globals.Area.tileset%d' % idx)

    tileoffset = idx * 256

    tiledata = PackTexture(idx)
    nmldata = PackTexture(idx, True)

    defs = globals.ObjectDefinitions[idx]

    if defs is None: return False

    colldata = b''
    deffile = b''
    indexfile = b''

    for i in range(tileoffset, tileoffset + 256):
        colldata += bytes(globals.Tiles[i].collData)

    for obj in defs:
        if obj is None:
            break

        indexfile += struct.pack('>HBBxB', len(deffile), obj.width, obj.height, obj.randByte)

        for row in obj.rows:
            for tile in row:
                if len(tile) == 3:
                    byte0 = tile[0]
                    byte1 = tile[1] & 0xFF
                    byte2 = tile[2] << 2
                    byte2 |= (tile[1] >> 8) & 3  # Slot

                    deffile += bytes([byte0, byte1, byte2])

                else:
                    deffile += bytes(tile)

            deffile += b'\xFE'

        deffile += b'\xFF'

    arc = SarcLib.SARC_Archive()

    tex = SarcLib.Folder('BG_tex'); arc.addFolder(tex)
    tex.addFile(SarcLib.File('%s.gtx' % name, tiledata))
    tex.addFile(SarcLib.File('%s_nml.gtx' % name, nmldata))

    chk = SarcLib.Folder('BG_chk'); arc.addFolder(chk)
    chk.addFile(SarcLib.File('d_bgchk_%s.bin' % name, colldata))

    unt = SarcLib.Folder('BG_unt'); arc.addFolder(unt)
    unt.addFile(SarcLib.File('%s.bin' % name, deffile))
    unt.addFile(SarcLib.File('%s_hd.bin' % name, indexfile))

    return arc.save(0x2000)


def _LoadTileset(idx, name, reload=False):
    """
    Load in a tileset into a specific slot
    """

    # if this file's not found, return
    if name not in globals.szsData: return

    sarcdata = globals.szsData[name]
    sarc = SarcLib.SARC_Archive()
    sarc.load(sarcdata)

    tileoffset = idx * 256

    # Decompress the textures
    try:
        comptiledata = sarc['BG_tex/%s.gtx' % name].data
        nmldata = sarc['BG_tex/%s_nml.gtx' % name].data
        colldata = sarc['BG_chk/d_bgchk_%s.bin' % name].data
    except KeyError:
        QtWidgets.QMessageBox.warning(None, globals.trans.string('Err_CorruptedTilesetData', 0),
                                      globals.trans.string('Err_CorruptedTilesetData', 1, '[file]', name))
        return False

    # load in the textures
    img = LoadTexture_NSMBU(comptiledata)
    nml = LoadTexture_NSMBU(nmldata)

    # Divide it into individual tiles and
    # add collisions at the same time
    def getTileFromImage(tilemap, xtilenum, ytilenum):
        return tilemap.copy((xtilenum * 64) + 2, (ytilenum * 64) + 2, 60, 60)

    dest = QtGui.QPixmap.fromImage(img)
    dest2 = QtGui.QPixmap.fromImage(nml)
    sourcex = 0
    sourcey = 0
    for i in range(tileoffset, tileoffset + 256):
        T = TilesetTile(getTileFromImage(dest, sourcex, sourcey), getTileFromImage(dest2, sourcex, sourcey))
        T.setCollisions(struct.unpack_from('>8B', colldata, (i - tileoffset) * 8))
        globals.Tiles[i] = T
        sourcex += 1
        if sourcex >= 32:
            sourcex = 0
            sourcey += 1

    def exists(fn):
        nonlocal sarc
        try:
            sarc[fn]
        except:
            return False
        return True
    
    # Load the tileset animations, if there are any
    tileoffset = idx*256
    row = 0
    col = 0

    hatena_anime = None
    block_anime = None
    tuka_coin_anime = None
    belt_conveyor_anime = None

    fn = 'BG_tex/hatena_anime.gtx'
    found = exists(fn)

    if found:
        hatena_anime = LoadTexture_NSMBU(sarc[fn].data)

    fn = 'BG_tex/block_anime.gtx'
    found = exists(fn)

    if found:
        block_anime = LoadTexture_NSMBU(sarc[fn].data)

    fn = 'BG_tex/tuka_coin_anime.gtx'
    found = exists(fn)

    if found:
        tuka_coin_anime = LoadTexture_NSMBU(sarc[fn].data)

    fn = 'BG_tex/belt_conveyor_anime.gtx'
    found = exists(fn)

    if found:
        belt_conveyor_anime = LoadTexture_NSMBU(sarc[fn].data)

    for i in range(tileoffset,tileoffset+256):
        if idx == 0:
            if globals.Tiles[i].collData[0] == 7:
                if hatena_anime:
                    globals.Tiles[i].addAnimationData(hatena_anime)

            elif globals.Tiles[i].collData[0] == 6:
                if block_anime:
                    globals.Tiles[i].addAnimationData(block_anime)

            elif globals.Tiles[i].collData[0] == 2:
                if tuka_coin_anime:
                    globals.Tiles[i].addAnimationData(tuka_coin_anime)

            elif globals.Tiles[i].collData[0] == 17:
                if belt_conveyor_anime:
                    for x in range(2):
                        if i == 144+x*16:
                            globals.Tiles[i].addConveyorAnimationData(belt_conveyor_anime, 0, True)

                        elif i == 145+x*16:
                            globals.Tiles[i].addConveyorAnimationData(belt_conveyor_anime, 1, True)

                        elif i == 146+x*16:
                            globals.Tiles[i].addConveyorAnimationData(belt_conveyor_anime, 2, True)

                        elif i == 147+x*16:
                            globals.Tiles[i].addConveyorAnimationData(belt_conveyor_anime, 0)

                        elif i == 148+x*16:
                            globals.Tiles[i].addConveyorAnimationData(belt_conveyor_anime, 1)

                        elif i == 149+x*16:
                            globals.Tiles[i].addConveyorAnimationData(belt_conveyor_anime, 2)

        col += 1

        if col == 16:
            col = 0
            row += 1

    # Load the object definitions
    defs = [None] * 256

    indexfile = sarc['BG_unt/%s_hd.bin' % name].data
    deffile = sarc['BG_unt/%s.bin' % name].data
    objcount = len(indexfile) // 6
    indexstruct = struct.Struct('>HBBH')

    for i in range(objcount):
        data = indexstruct.unpack_from(indexfile, i * 6)
        obj = ObjectDef()
        obj.width = data[1]
        obj.height = data[2]
        obj.randByte = data[3]
        obj.load(deffile, data[0])
        defs[i] = obj

    globals.ObjectDefinitions[idx] = defs

    ProcessOverrides(idx, name)

    # Add Tiles to spritelib
    SLib.Tiles = globals.Tiles


def LoadTexture_NSMBU(tiledata):
    if platform.system() == 'Windows':
        tile_path = globals.miyamoto_path + '/Tools'
    elif platform.system() == 'Linux':
        tile_path = globals.miyamoto_path + '/linuxTools'
    elif platform.system() == 'Darwin':
        tile_path = globals.miyamoto_path + '/macTools'

    with open(tile_path + '/texture.gtx', 'wb') as binfile:
        binfile.write(tiledata)

    os.chdir(tile_path)

    if platform.system() == 'Windows':
        os.system('gtx_extract_bmp.exe texture.gtx')

    elif platform.system() == 'Linux':
        os.system('chmod +x ./gtx_extract.elf')
        os.system('./gtx_extract.elf texture.gtx texture.bmp')

    elif platform.system() == 'Darwin':
        os.system(
            'open -a "' + tile_path + '/gtx_extract" --args "' + tile_path + '/texture.gtx" "' + tile_path + '/texture.bmp"')

    else:
        warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'OH NO', 'Not a supported platform, sadly...')
        warningBox.exec_()
        return

    os.chdir(globals.miyamoto_path)

    # Return as a QImage
    img = QtGui.QImage(tile_path + '/texture.bmp')
    os.remove(tile_path + '/texture.bmp')

    os.remove(tile_path + '/texture.gtx')

    return img


def CascadeTilesetNames_Category(lower, upper):
    """
    Applies upper as a patch of lower
    """
    lower = list(lower)
    for item in upper:

        if isinstance(item[1], tuple) or isinstance(item[1], list):
            # It's a category

            found = False
            for i, lowitem in enumerate(lower):
                lowitem = lower[i]
                if lowitem[0] == item[0]:  # names are ==
                    lower[i] = list(lower[i])
                    lower[i][1] = CascadeTilesetNames_Category(lowitem[1], item[1])
                    found = True
                    break

            if not found:
                i = 0
                while (i < len(lower)) and (isinstance(lower[i][1], tuple) or isinstance(lower[i][1], list)): i += 1
                lower.insert(i + 1, item)

        else:  # It's a tileset entry
            found = False
            for i, lowitem in enumerate(lower):
                lowitem = lower[i]
                if lowitem[0] == item[0]:  # filenames are ==
                    lower[i] = list(lower[i])
                    lower[i][1] = item[1]
                    found = True
                    break

            if not found: lower.append(item)
    return lower


def SortTilesetNames_Category(cat):
    """
    Sorts a tileset names category
    """
    cat = list(cat)

    # First, remove all category nodes
    cats = []
    for node in cat:
        if isinstance(node[1], tuple) or isinstance(node[1], list):
            cats.append(node)
    for node in cats: cat.remove(node)

    # Sort the tileset names
    cat.sort(key=lambda entry: entry[1])

    # Sort the data within each category
    for i, cat_ in enumerate(cats):
        cats[i] = list(cat_)
        if not cats[i][2]: cats[i][1] = SortTilesetNames_Category(cats[i][1])

    # Put them back together
    new = []
    for category in cats: new.append(tuple(category))
    for tileset in cat: new.append(tuple(tileset))
    return tuple(new)


def IncrementTilesetFrame():
    """
    Moves each tileset to the next frame
    """
    if not globals.TilesetsAnimating: return
    for tile in globals.Tiles:
        if tile is not None: tile.nextFrame()
    globals.mainWindow.scene.update()
    globals.mainWindow.objPicker.update()


def UnloadTileset(idx):
    """
    Unload the tileset from a specific slot
    """
    tileoffset = idx * 256
    for i in range(tileoffset, tileoffset + 256):
        globals.Tiles[i] = Tiles[4 * 0x200]

    globals.ObjectDefinitions[idx] = None


def CountTiles(row):
    """
    Counts the amount of real tiles in an object row
    """
    res = 0
    for tile in row:
        if (tile[0] & 0x80) == 0:
            res += 1
    return res


def CreateSection(rows):
    """
    Create a slope section
    """
    # calculate width
    width = 0
    for row in rows:
        thiswidth = CountTiles(row)
        if width < thiswidth: width = thiswidth

    # create the section
    section = []
    for row in rows:
        drow = [0] * width
        x = 0
        for tile in row:
            if (tile[0] & 0x80) == 0:
                drow[x] = tile
                x += 1
        section.append(drow)

    return section


def PutObjectArray(dest, xo, yo, block, width, height):
    """
    Places a tile array into an object
    """
    # for y in range(yo,min(yo+len(block),height)):
    for y in range(yo, yo + len(block)):
        if y < 0: continue
        if y >= height: continue
        drow = dest[y]
        srow = block[y - yo]
        # for x in range(xo,min(xo+len(srow),width)):
        for x in range(xo, xo + len(srow)):
            if x < 0: continue
            if x >= width: continue
            drow[x] = srow[x - xo][1]


def RenderObject(tileset, objnum, width, height, fullslope=False):
    """
    Render a tileset object into an array
    """
    # allocate an array
    dest = []
    for i in range(height): dest.append([0] * width)

    # ignore non-existent objects
    try:
        tileset_defs = globals.ObjectDefinitions[tileset]
    except IndexError:
        tileset_defs = None
    if tileset_defs is None: return dest
    try:
        obj = tileset_defs[objnum]
    except IndexError:
        obj = None
    if obj is None: return dest
    if len(obj.rows) == 0: return dest

    # diagonal objects are rendered differently
    if (obj.rows[0][0][0] & 0x80) != 0:
        RenderDiagonalObject(dest, obj, width, height, fullslope)
    else:
        # standard object
        repeatFound = False
        beforeRepeat = []
        inRepeat = []
        afterRepeat = []

        for row in obj.rows:
            if len(row) == 0: continue
            if (row[0][0] & 2) != 0:
                repeatFound = True
                inRepeat.append(row)
            else:
                if repeatFound:
                    afterRepeat.append(row)
                else:
                    beforeRepeat.append(row)

        bc = len(beforeRepeat);
        ic = len(inRepeat);
        ac = len(afterRepeat)
        if ic == 0:
            for y in range(height):
                RenderStandardRow(dest[y], beforeRepeat[y % bc], y, width)
        else:
            afterthreshold = height - ac - 1
            for y in range(height):
                if y < bc:
                    RenderStandardRow(dest[y], beforeRepeat[y], y, width)
                elif y > afterthreshold:
                    RenderStandardRow(dest[y], afterRepeat[y - height + ac], y, width)
                else:
                    RenderStandardRow(dest[y], inRepeat[(y - bc) % ic], y, width)

    return dest


def RenderObjectAll(obj, width, height, fullslope=False):
    """
    Used by "All" tab, render a tileset object into an array
    """
    # allocate an array
    dest = []
    for i in range(height): dest.append([0]*width)

    # ignore non-existent objects
    if obj is None: return dest
    if len(obj.rows) == 0: return dest

    # diagonal objects are rendered differently
    if (obj.rows[0][0][0] & 0x80) != 0:
        RenderDiagonalObject(dest, obj, width, height, fullslope)
    else:
        # standard object
        repeatFound = False
        beforeRepeat = []
        inRepeat = []
        afterRepeat = []

        for row in obj.rows:
            if len(row) == 0: continue
            if (row[0][0] & 2) != 0:
                repeatFound = True
                inRepeat.append(row)
            else:
                if repeatFound:
                    afterRepeat.append(row)
                else:
                    beforeRepeat.append(row)

        bc = len(beforeRepeat); ic = len(inRepeat); ac = len(afterRepeat)
        if ic == 0:
            for y in range(height):
                RenderStandardRow(dest[y], beforeRepeat[y % bc], y, width)
        else:
            afterthreshold = height - ac - 1
            for y in range(height):
                if y < bc:
                    RenderStandardRow(dest[y], beforeRepeat[y], y, width)
                elif y > afterthreshold:
                    RenderStandardRow(dest[y], afterRepeat[y - height + ac], y, width)
                else:
                    RenderStandardRow(dest[y], inRepeat[(y - bc) % ic], y, width)

    return dest


def RenderStandardRow(dest, row, y, width):
    """
    Render a row from an object
    """
    repeatFound = False
    beforeRepeat = []
    inRepeat = []
    afterRepeat = []

    for tile in row:
        tiling = (tile[0] & 1) != 0

        if tiling:
            repeatFound = True
            inRepeat.append(tile)
        else:
            if repeatFound:
                afterRepeat.append(tile)
            else:
                beforeRepeat.append(tile)

    bc = len(beforeRepeat);
    ic = len(inRepeat);
    ac = len(afterRepeat)
    if ic == 0:
        for x in range(width):
            dest[x] = beforeRepeat[x % bc][1]
    else:
        afterthreshold = width - ac - 1
        for x in range(width):
            if x < bc:
                dest[x] = beforeRepeat[x][1]
            elif x > afterthreshold:
                dest[x] = afterRepeat[x - width + ac][1]
            else:
                dest[x] = inRepeat[(x - bc) % ic][1]


def RenderDiagonalObject(dest, obj, width, height, fullslope):
    """
    Render a diagonal object
    """
    # set all to empty tiles
    for row in dest:
        for x in range(width):
            row[x] = -1

    # get sections
    mainBlock, subBlock = GetSlopeSections(obj)
    cbyte = obj.rows[0][0][0]

    # get direction
    goLeft = ((cbyte & 1) != 0)
    goDown = ((cbyte & 2) != 0)

    # base the amount to draw by seeing how much we can fit in each direction
    if fullslope:
        drawAmount = max(height // len(mainBlock), width // len(mainBlock[0]))
    else:
        drawAmount = min(height // len(mainBlock), width // len(mainBlock[0]))

    # if it's not goingLeft and not goingDown:
    if not goLeft and not goDown:
        # slope going from SW => NE
        # start off at the bottom left
        x = 0
        y = height - len(mainBlock) - (0 if subBlock is None else len(subBlock))
        xi = len(mainBlock[0])
        yi = -len(mainBlock)

    # ... and if it's goingLeft and not goingDown:
    elif goLeft and not goDown:
        # slope going from SE => NW
        # start off at the top left
        x = 0
        y = 0
        xi = len(mainBlock[0])
        yi = len(mainBlock)

    # ... and if it's not goingLeft but it's goingDown:
    elif not goLeft and goDown:
        # slope going from NW => SE
        # start off at the top left
        x = 0
        y = (0 if subBlock is None else len(subBlock))
        xi = len(mainBlock[0])
        yi = len(mainBlock)

    # ... and finally, if it's goingLeft and goingDown:
    else:
        # slope going from SW => NE
        # start off at the bottom left
        x = 0
        y = height - len(mainBlock)
        xi = len(mainBlock[0])
        yi = -len(mainBlock)

    # finally draw it
    for i in range(drawAmount):
        PutObjectArray(dest, x, y, mainBlock, width, height)
        if subBlock is not None:
            xb = x
            if goLeft: xb = x + len(mainBlock[0]) - len(subBlock[0])
            if goDown:
                PutObjectArray(dest, xb, y - len(subBlock), subBlock, width, height)
            else:
                PutObjectArray(dest, xb, y + len(mainBlock), subBlock, width, height)
        x += xi
        y += yi


def GetSlopeSections(obj):
    """
    Sorts the slope data into sections
    """
    sections = []
    currentSection = None

    for row in obj.rows:
        if len(row) > 0 and (row[0][0] & 0x80) != 0:  # begin new section
            if currentSection is not None:
                sections.append(CreateSection(currentSection))
            currentSection = []
        currentSection.append(row)

    if currentSection is not None:  # end last section
        sections.append(CreateSection(currentSection))

    if len(sections) == 1:
        return (sections[0], None)
    else:
        return (sections[0], sections[1])


def ProcessOverrides(idx, name):
    """
    Load overridden tiles if there are any
    """
    # For every tileset loaded, Tiles[] contains all tiles.
    # Offsets for tiles: 0000-0255 for Pa0;
    #                    0256-0511 for Pa1;
    #                    0512-0767 for Pa2;
    #                    0768-1023 for Pa3;
    # From 1024 (0x200 * 4), there is room for the overrides.
    try:
        if name.startswith('Pa0'):
            # We use the same overrides for all Pa0 tilesets
            offset = 0x200 * 4

            defs = globals.ObjectDefinitions[idx]
            t = globals.Tiles

            # Invisible, brick and ? blocks
            ## Invisible
            replace = offset + 3
            for i in [3, 4, 5, 6, 7, 8, 9, 10, 13, 29]:
                t[i].main = t[replace].main
                replace += 1

            ## Brick
            for i in range(16, 28):
                t[i].main = t[offset + i].main

            ## ?
            t[offset + 160].main = t[49].main
            t[49].main = t[offset + 46].main
            for i in range(32, 43):
                t[i].main = t[offset + i].main

            # Collisions
            ## Full block
            t[1].main = t[offset + 1].main

            ## Vine stopper
            t[2].main = t[offset + 2].main

            ## Solid-on-top
            t[11].main = t[offset + 13].main

            ## Half block
            t[12].main = t[offset + 14].main

            ## Muncher (hit)
            t[45].main = t[offset + 45].main

            ## Muncher (hit) 2
            t[209].main = t[offset + 44].main

            ## Donut lift
            t[53].main = t[offset + 43].main

            ## Conveyor belts
            ### Left
            #### Fast
            replace = offset + 115
            for i in range(163, 166):
                t[i].main = t[replace].main
                replace += 1
            #### Slow
            replace = offset + 99
            for i in range(147, 150):
                t[i].main = t[replace].main
                replace += 1

            ### Right
            #### Fast
            replace = offset + 112
            for i in range(160, 163):
                t[i].main = t[replace].main
                replace += 1
            #### Slow
            replace = offset + 96
            for i in range(144, 147):
                t[i].main = t[replace].main
                replace += 1

            ## Pipes
            ### Green
            #### Vertical
            t[64].main = t[offset + 48].main
            t[65].main = t[offset + 49].main
            t[80].main = t[offset + 64].main
            t[81].main = t[offset + 65].main
            t[96].main = t[offset + 80].main
            t[97].main = t[offset + 81].main
            #### Horizontal
            t[87].main = t[offset + 71].main
            t[103].main = t[offset + 87].main
            t[88].main = t[offset + 72].main
            t[104].main = t[offset + 88].main
            t[89].main = t[offset + 73].main
            t[105].main = t[offset + 89].main
            ### Yellow
            #### Vertical
            t[66].main = t[offset + 50].main
            t[67].main = t[offset + 51].main
            t[82].main = t[offset + 66].main
            t[83].main = t[offset + 67].main
            t[98].main = t[offset + 82].main
            t[99].main = t[offset + 83].main
            #### Horizontal
            t[90].main = t[offset + 74].main
            t[106].main = t[offset + 90].main
            t[91].main = t[offset + 75].main
            t[107].main = t[offset + 91].main
            t[92].main = t[offset + 76].main
            t[108].main = t[offset + 92].main
            ### Red
            #### Vertical
            t[68].main = t[offset + 52].main
            t[69].main = t[offset + 53].main
            t[84].main = t[offset + 68].main
            t[85].main = t[offset + 69].main
            t[100].main = t[offset + 84].main
            t[101].main = t[offset + 85].main
            #### Horizontal
            t[93].main = t[offset + 77].main
            t[109].main = t[offset + 93].main
            t[94].main = t[offset + 78].main
            t[110].main = t[offset + 94].main
            t[95].main = t[offset + 79].main
            t[111].main = t[offset + 95].main
            ### Mini (green)
            #### Vertical
            t[70].main = t[offset + 54].main
            t[86].main = t[offset + 70].main
            t[102].main = t[offset + 86].main
            #### Horizontal
            t[120].main = t[offset + 104].main
            t[121].main = t[offset + 105].main
            t[137].main = t[offset + 121].main
            ### Joints
            #### Normal
            t[118].main = t[offset + 102].main
            t[119].main = t[offset + 103].main
            t[134].main = t[offset + 118].main
            t[135].main = t[offset + 119].main
            #### Mini
            t[136].main = t[offset + 120].main

            # Coins
            t[30].main = t[offset + 30].main
            ## Outline
            t[31].main = t[offset + 29].main
            ### Multiplayer
            t[28].main = t[offset + 28].main
            ## Blue
            t[46].main = t[offset + 47].main

            # Flowers / Grass
            ## Flowers
            replace = offset + 55
            for i in range(210, 213):
                t[i].main = t[replace].main
                replace += 1
            ## Grass
            replace = offset + 58
            for i in range(178, 183):
                t[i].main = t[replace].main
                replace += 1
            ## Flowers and grass
            replace = offset + 106
            for i in range(213, 216):
                t[i].main = t[replace].main
                replace += 1

            # Lines
            ## Straight lines
            ### Normal
            t[216].main = t[offset + 128].main
            t[217].main = t[offset + 63].main
            ### Corners and diagonals
            replace = offset + 122
            for i in range(218, 231):
                if i != 224:  # random empty tile
                    t[i].main = t[replace].main
                replace += 1

            ## Circles and stops
            for i in range(231, 256):
                t[i].main = t[replace].main
                replace += 1

    except Exception:
        warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'OH NO',
                                           'Whoops, something went wrong while processing the overrides...')
        warningBox.exec_()


def SimpleTilesetNames():
    """
    simple
    """

    # Category parser
    def ParseCategory(items):
        """
        Parses a list of strings and returns a tuple of strings
        """
        result = []
        for item in items:
            if isinstance(item[1], str):
                # It's a tileset
                name = item[1]
                file = item[0]
                result.append((file, name))
            else:
                # It's a category
                childStrings = ParseCategory(item[1])
                for child in childStrings:
                    result.append(child)
        return result

    pa0 = sorted(ParseCategory(globals.TilesetNames[0][0]), key=lambda entry: entry[1])
    return pa0
