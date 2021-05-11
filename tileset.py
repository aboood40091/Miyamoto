#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! DX Level Editor - New Super Mario Bros. U Deluxe Level Editor
# Copyright (C) 2009-2021 Treeki, Tempus, angelsl, JasonP27, Kinnay,
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

import json
import os
import platform
import struct
import subprocess

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

import globals

import bntx as BNTX
import SarcLib
import spritelib as SLib

from yaz0 import determineCompressionMethod
CompYaz0, _ = determineCompressionMethod()

#################################


class TilesetTile:
    """
    Class that represents a single tile in a tileset
    """
    exists = True
    _collisionedImgCache = {}

    def __init__(self, main=None, nml=None):
        """
        Initializes the TilesetTile
        """
        if not main:
            main = QtGui.QPixmap(60, 60)
            main.fill(Qt.transparent)
            self.exists = False

        self.main = main

        if not nml:
            nml = QtGui.QPixmap(60, 60)
            nml.fill(QtGui.QColor(128, 128, 255))

        self.nml = nml
        self.isAnimated = False
        self.animFrame = 0
        self.animTiles = []
        self.setCollisions(0)
        self.collOverlay = None

    def imgWithCollisions(self, img):
        """
        Return a copy of "img" with self.collOverlay applied.
        Uses self._collisionedImgCache, which has to be reset if
        self.collOverlay changes.
        """
        imgId = id(img)
        if imgId not in self._collisionedImgCache:
            newImg = QtGui.QPixmap(img)
            p = QtGui.QPainter(newImg)
            p.drawPixmap(0, 0, self.collOverlay)
            del p

            self._collisionedImgCache[imgId] = newImg

        return self._collisionedImgCache[imgId]


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
        if not self.isAnimated:
            return

        self.animFrame += 1
        if self.animFrame == len(self.animTiles):
            self.animFrame = 0

    def resetAnimation(self):
        """
        Resets the animation frame
        """
        self.animFrame = 0

    def getCurrentTile(self, onLayer1=False):
        """
        Returns the current tile based on the current animation frame
        """
        if not (globals.TilesetsAnimating and self.isAnimated):
            result = QtGui.QPixmap(self.main)

            if onLayer1 and globals.CollisionsShown and (self.collOverlay is not None):
                result = self.imgWithCollisions(result)

        else:
            result = QtGui.QPixmap(self.animTiles[self.animFrame])

            if onLayer1 and globals.CollisionsShown and (self.collOverlay is not None):
                p = QtGui.QPainter(result)
                p.drawPixmap(0, 0, self.collOverlay)
                del p

        return result

    def setCollisions(self, collision):
        """
        Sets the collision data for this tile
        """
        self.coreType = (collision >>  0) & 0xFFFF
        self.params   = (collision >> 16) &   0xFF
        self.params2  = (collision >> 24) &   0xFF
        self.solidity = (collision >> 32) &   0xFF
        self.terrain  = (collision >> 40) &   0xFF
        
        self.collOverlay = QtGui.QPixmap(globals.TileWidth, globals.TileWidth)
        self.collOverlay.fill(QtGui.QColor(0, 0, 0, 0))

        pen = QtGui.QPen(QtGui.QColor(0, 0, 0, 128))
        painter = QtGui.QPainter(self.collOverlay)
        painter.setPen(pen)
        updateCollisionOverlay(self, 0, 0, globals.TileWidth, painter)

        self._collisionedImgCache = {}

    def getCollision(self):
        return ((self.coreType <<  0) |
                (self.params   << 16) |
                (self.params2  << 24) |
                (self.solidity << 32) |
                (self.terrain  << 40))

    def setQuestionCollisions(self):
        """
        Sets the collision data to that of a question block
        """
        self.setCollisions(0x100000007)

    def setBrickCollisions(self):
        """
        Sets the collision data to that of a brick block
        """
        self.setCollisions(0x100000006)


def updateCollisionOverlay(tile, x, y, tileWidth, painter):
        """
        Updates the collisions overlay for this pixmap
        """
        # Sets the colour based on terrain type
        if tile.coreType == 15 and (tile.solidity == 1 and tile.params in (3, 4, 5, 6) or tile.solidity == 0 and tile.params in (0, 1, 2, 7, 8, 9)):
            if tile.params == 7:
                color = QtGui.QColor(128, 128, 128, 120)
            elif tile.params == 9:
                color = QtGui.QColor(255, 0, 255, 120)
            else:
                color = QtGui.QColor(255, 0, 0, 120)
        elif tile.terrain == 1:  # Ice
            color = QtGui.QColor(120, 208, 255, 120)
        elif tile.terrain == 2:  # Snow
            color = QtGui.QColor(120, 120, 255, 120)
        elif tile.terrain == 3:  # Quicksand
            color = QtGui.QColor(224, 160, 0, 120)
        elif tile.terrain == 4:  # Desert Sand
            color = QtGui.QColor(128, 64, 0, 120)
        elif tile.terrain == 5:  # Grass
            color = QtGui.QColor(0, 255, 0, 120)
        elif tile.terrain == 6:  # Cloud
            color = QtGui.QColor(208, 255, 255, 120)
        elif tile.terrain == 7:  # Beach Sand
            color = QtGui.QColor(240, 224, 96, 120)
        elif tile.terrain == 8:  # Carpet
            color = QtGui.QColor(240, 96, 128, 120)
        elif tile.terrain == 9:  # Leaves
            color = QtGui.QColor(0, 144, 32, 120)
        elif tile.terrain == 10:  # Wood
            color = QtGui.QColor(144, 96, 0, 120)
        elif tile.terrain == 11:  # Water
            color = QtGui.QColor(32, 208, 224, 120)
        elif tile.terrain == 12:  # Beanstalk Leaf
            color = QtGui.QColor(96, 208, 0, 120)
        else:
            color = QtGui.QColor(0, 0, 0, 120)

        # Sets Brush style for fills
        if tile.coreType in (14, 20, 22) and tile.solidity == 0 or tile.coreType == 21 and tile.solidity == 1:  # Climbing Grid
            style = Qt.DiagCrossPattern
        elif tile.coreType in (5, 6, 7):  # Breakable
            style = Qt.Dense5Pattern
        else:
            style = Qt.SolidPattern

        brush = QtGui.QBrush(color, style)
        painter.setBrush(brush)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Paints shape based on other junk
        if tile.coreType == 0xB and tile.solidity not in (0, 3):  # Slope
            if not tile.params:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y)]))
            elif tile.params == 1:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 2:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5)]))
            elif tile.params == 3:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth)]))
            elif tile.params == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth)]))
            elif tile.params == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 6:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y)]))
            elif tile.params == 7:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y)]))
            elif tile.params == 8:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 9:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 10:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y)]))
            elif tile.params == 11:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.75),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth)]))
            elif tile.params == 12:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth * 0.75),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 13:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.25),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 14:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x, y + tileWidth * 0.25),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 15:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.25),
                                                    QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 16:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth * 0.25),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 17:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.75),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 18:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth * 0.75),
                                                    QtCore.QPoint(x, y + tileWidth)]))

        elif tile.coreType == 0xC and tile.solidity not in (0, 2):  # Reverse Slope
            if not tile.params:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y)]))
            elif tile.params == 1:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y)]))
            elif tile.params == 2:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5)]))
            elif tile.params == 3:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y)]))
            elif tile.params == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5)]))
            elif tile.params == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y)]))
            elif tile.params == 6:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x, y)]))
            elif tile.params == 7:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y)]))
            elif tile.params == 8:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 9:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth * 0.5, y),
                                                    QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 10:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y)]))
            elif tile.params == 11:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.25)]))
            elif tile.params == 12:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth * 0.25)]))
            elif tile.params == 13:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.75),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5)]))
            elif tile.params == 14:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth * 0.75)]))
            elif tile.params == 15:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.75),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 16:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth * 0.75)]))
            elif tile.params == 17:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.25),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5)]))
            elif tile.params == 18:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x, y + tileWidth * 0.25)]))

        elif tile.coreType == 9 and tile.solidity:  # Partial
            if tile.params == 0:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5)]))
            elif tile.params == 1:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth * 0.5, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth * 0.5)]))
            elif tile.params == 2:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5)]))
            elif tile.params == 3:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5)]))
            elif tile.params == 6:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 7:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth)]))
            elif tile.params == 8:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y)]))
            elif tile.params == 9:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth * 0.5, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth)]))
            elif tile.params == 10:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5)]))
            elif tile.params == 11:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 12:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 13:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth)]))
            elif tile.params == 14:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth)]))

        elif tile.solidity in (2, 3, 4, 17, 18, 33, 34):
            if tile.solidity in (3, 4):  # Solid-on-bottom
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.75),
                                                    QtCore.QPoint(x, y + tileWidth * 0.75)]))

                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth * 0.625, y),
                                                    QtCore.QPoint(x + tileWidth * 0.625, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.75, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth * (17 / 24)),
                                                    QtCore.QPoint(x + tileWidth * 0.25, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.375, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.375, y)]))

            if tile.solidity != 3:  # Solid-on-top
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.25),
                                                    QtCore.QPoint(x, y + tileWidth * 0.25)]))

                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth * 0.625, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.625, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.75, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth * 0.295),
                                                    QtCore.QPoint(x + tileWidth * 0.25, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.375, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth * 0.375, y + tileWidth)]))

        elif tile.coreType == 15 and tile.solidity == 1:  # Spikes
            if tile.params == 3:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth * 0.25)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x, y + tileWidth * 0.75)]))
            elif tile.params == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.25)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth * 0.5),
                                                    QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth * 0.75)]))
            elif tile.params == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.25, y)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.75, y)]))
            elif tile.params == 6:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y),
                                                    QtCore.QPoint(x + tileWidth * 0.25, y + tileWidth)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth * 0.5, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth * 0.75, y + tileWidth)]))

            elif tile.params in (0, 1, 2, 7, 8, 9):
                painter.drawRect(x, y, tileWidth, tileWidth)

        elif tile.coreType == 15 and tile.solidity == 0:  # Damage Tiles
            if tile.params == 0:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth)]))

            elif tile.params == 1:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                    QtCore.QPoint(x + tileWidth, y),
                                                    QtCore.QPoint(x + tileWidth * 0.75, y + tileWidth),
                                                    QtCore.QPoint(x + tileWidth * 0.25, y + tileWidth)]))

            elif tile.params == 2:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + tileWidth * 0.25, y),
                                                    QtCore.QPoint(x + tileWidth * 0.75, y),
                                                    QtCore.QPoint(x + tileWidth * 0.5, y + tileWidth)]))

            elif tile.params in (7, 8, 9):
                painter.drawRect(x, y, tileWidth, tileWidth)

        elif tile.solidity == 1 or tile.coreType in (14, 20, 22) and tile.solidity == 0:  # Solid or Climbable
            painter.drawRect(x, y, tileWidth, tileWidth)


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
        self.folderIndex = -1
        self.objAllIndex = -1
        self.randByte = 0
        self.reversed = False
        self.mainPartAt = -1
        self.subPartAt = -1
        self.rows = []
        self.data = 0

    def load(self, source, offset):
        """
        Load an object definition
        """
        source = source[offset:]

        if source[0] & 0x80 and source[0] & 2:
            self.reversed = True

        i = 0
        row = []

        while i < len(source):
            cbyte = source[i]

            if cbyte == 0xFF:
                break

            elif cbyte == 0xFE:
                self.rows.append(row)
                i += 1
                row = []

            elif (cbyte & 0x80) != 0:
                if self.mainPartAt == -1:
                    assert len(self.rows) == 0
                    self.mainPartAt = 0

                else:
                    self.subPartAt = len(self.rows)

                row.append((cbyte,))
                i += 1

            else:
                if i + 3 > len(source):
                    source += b'\0' * (i + 3 - len(source)) + b'\xfe\xff'

                extra = source[i + 2]
                tile = [cbyte, source[i + 1] | ((extra & 3) << 8), extra >> 2]
                row.append(tile)
                i += 3


def CreateTilesets():
    """
    Blank out the tileset arrays
    """
    T = TilesetTile()
    T.setCollisions(0)
    globals.Tiles = [T] * 0x200 * 4
    globals.Tiles += globals.Overrides
    SLib.Tiles = globals.Tiles

    globals.TilesetAnimTimer = QtCore.QTimer()
    globals.TilesetAnimTimer.timeout.connect(IncrementTilesetFrame)
    globals.TilesetAnimTimer.start(62.5)

    globals.ObjectDefinitions = [None] * 4


def getUsedTiles():
    """
    Get the number of used tiles in each tileset
    """
    usedTiles = [[], [], [], []]

    for idx in range(1, 4):
        defs = globals.ObjectDefinitions[idx]

        if defs is None:
            continue

        for obj in defs:
            if obj is None:
                break

            if (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
                randLen = obj.randByte & 0xF

            else:
                randLen = 0

            for row in obj.rows:
                for tile in row:
                    if len(tile) == 3:
                        if tile == [0, 0, 0]:  # Pa0 tile 0 used in another slot, don't count it
                            continue

                        tileNum = tile[1] & 0xFF
                        tilesetIdx = (tile[1] >> 8) & 3

                        if randLen:
                            for z in range(randLen):
                                if tileNum + z not in usedTiles[tilesetIdx]:
                                    usedTiles[tilesetIdx].append(tileNum + z)
                        else:
                            if tileNum not in usedTiles[tilesetIdx]:
                                usedTiles[tilesetIdx].append(tileNum)

    return usedTiles


def objFitsInTileset(obj, idx):
    if globals.ObjectDefinitions[idx] is not None and None not in globals.ObjectDefinitions[idx]:
        # Skip to to the next tileset because we can't add any more objects to this tileset
        return None

    # Get the number of used tiles in this tileset
    usedTiles = getUsedTiles()[idx]
    if len(usedTiles) >= 256:  # It can't be more than 256, oh well
        # Skip to to the next tileset because no free tiles were found
        return None

    # Get the number of tiles in this object
    ## Check if the object *can* be randomized
    if (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
        # If it can be randomized, the number is the random tiles length
        randLen = obj.randByte & 0xF

    else:
        randLen = 0

    if randLen:
        numTiles = randLen

    else:
        tilesUsed = []
        for row in obj.rows:
            for tile in row:
                if len(tile) == 3:
                    if tile != [0, 0, 0]:
                        if tile[1] & 0xFF not in tilesUsed:
                            tilesUsed.append(tile[1] & 0xFF)

        numTiles = len(tilesUsed)
        del tilesUsed

    if numTiles + len(usedTiles) > 256:
        # Free tiles are not enough
        return None

    # Add the free tiles to a list
    freeTiles = [i for i in range(256) if i not in usedTiles]

    # Add additional check for randomized objects
    tileNum = 0
    if randLen:
        # Look for any free tiles in a row with length "randLen"
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
            # No free tiles in a row with length "randLen" were found
            return None

    # If we got to this point, the object fits!
    return randLen, tileNum, freeTiles


def addObjToTilesetImpl(obj, colldata, img, nml, idx, fits):
    randLen, tileNum, freeTiles = fits
    tileoffset = idx * 256

    # Handle randomized objects differently
    if randLen:
        # Set the object's tiles' indecies
        for ctile, tile in enumerate(obj.rows[0]):
            if len(tile) == 3:
                obj.rows[0][ctile][1] = tileNum | (idx << 8)

        # Adds the object's tiles to the Tiles dict.
        tileNum += tileoffset
        for z in range(randLen):
            T = TilesetTile(img.copy(z * 60, 0, 60, 60), nml.copy(z * 60, 0, 60, 60))
            T.setCollisions(struct.unpack_from('<Q', colldata, z * 8)[0])
            globals.Tiles[tileNum + z] = T

    else:
        # Set the object's tiles' indecies
        tilesUsed = {}

        i = 0
        for row in obj.rows:
            for tile in row:
                if len(tile) == 3:
                    if tile != [0, 0, 0]:
                        tileIdx = tile[1] & 0xFF
                        if tileIdx not in tilesUsed:
                            tilesUsed[tileIdx] = i
                            tile[1] = freeTiles[i] | (idx << 8)
                            i += 1

                        else:
                            tile[1] = freeTiles[tilesUsed[tileIdx]] | (idx << 8)

        # Adds the object's tiles to the Tiles dict.
        tilesReplaced = []

        if obj.reversed:
            for crow, row in enumerate(obj.rows):
                if obj.subPartAt != -1:
                    if crow >= obj.subPartAt:
                        crow -= obj.subPartAt

                    else:
                        crow += obj.height - obj.subPartAt

                x = 0; i = 0
                y = crow * 60

                for tile in row:
                    if len(tile) == 3:
                        if tile != [0, 0, 0]:
                            tileNum = (tile[1] & 0xFF) + tileoffset
                            if tileNum not in tilesReplaced:
                                tilesReplaced.append(tileNum)
                                T = TilesetTile(img.copy(x, y, 60, 60), nml.copy(x, y, 60, 60))
                                T.setCollisions(struct.unpack_from('<Q', colldata, (crow * obj.width * 8) + i)[0])
                                globals.Tiles[tileNum] = T

                        x += 60
                        i += 8

        else:
            i = 0

            for crow, row in enumerate(obj.rows):
                x = 0
                y = crow * 60

                for tile in row:
                    if len(tile) == 3:
                        if tile != [0, 0, 0]:
                            tileNum = (tile[1] & 0xFF) + tileoffset
                            if tileNum not in tilesReplaced:
                                tilesReplaced.append(tileNum)
                                T = TilesetTile(img.copy(x, y, 60, 60), nml.copy(x, y, 60, 60))
                                T.setCollisions(struct.unpack_from('<Q', colldata, i)[0])
                                globals.Tiles[tileNum] = T

                        x += 60
                        i += 8

    return obj


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
        # Check if the object fits in the tileset
        fits = objFitsInTileset(obj, idx)
        if fits is None:
            continue

        obj = addObjToTilesetImpl(obj, colldata, img, nml, idx, fits)

        if globals.ObjectDefinitions[idx] is None:
            # Make us a new ObjectDefinitions for this tileset
            globals.ObjectDefinitions[idx] = [None] * 256

        defs = globals.ObjectDefinitions[idx]

        # Set the object's number
        for objNum, def_ in enumerate(defs):
            if def_ is None:
                break

        globals.ObjectDefinitions[idx][objNum] = obj

        # Set the paint type
        paintType = idx

        # Misc.
        HandleTilesetEdited()
        if not eval('globals.Area.tileset%d' % idx):
            exec("globals.Area.tileset%d = generateTilesetNames()[%d]" % (idx, idx - 1))

        break

    return paintType, objNum


def getImgFromObj(obj, randLen):
    if randLen and (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
        tex = QtGui.QPixmap(randLen * 60, obj.height * 60)
        nml = QtGui.QPixmap(randLen * 60, obj.height * 60)

    else:
        tex = QtGui.QPixmap(obj.width * 60, obj.height * 60)
        nml = QtGui.QPixmap(obj.width * 60, obj.height * 60)

    tex.fill(Qt.transparent)
    nml.fill(QtGui.QColor(128, 128, 255))
    painter = QtGui.QPainter(tex)
    nmlPainter = QtGui.QPainter(nml)

    # Paint the tiles on the pixmap
    if obj.reversed:
        for crow, row in enumerate(obj.rows):
            if obj.subPartAt != -1:
                if crow >= obj.subPartAt:
                    crow -= obj.subPartAt

                else:
                    crow += obj.height - obj.subPartAt

            x = 0
            y = crow * 60

            for tile in row:
                if len(tile) == 3:
                    if tile != [0, 0, 0]:
                        tileNum = (tile[1] & 0xFF) + (((tile[1] >> 8) & 3) * 256)
                        painter.drawPixmap(x, y, globals.Tiles[tileNum].main)
                        nmlPainter.drawPixmap(x, y, globals.Tiles[tileNum].nml)

                    x += 60

    else:
        for crow, row in enumerate(obj.rows):
            x = 0
            y = crow * 60

            for tile in row:
                if len(tile) == 3:
                    if tile != [0, 0, 0]:
                        tileNum = (tile[1] & 0xFF) + (((tile[1] >> 8) & 3) * 256)
                        if randLen and (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
                            for z in range(randLen):
                                painter.drawPixmap(x, y, globals.Tiles[tileNum + z].main)
                                nmlPainter.drawPixmap(x, y, globals.Tiles[tileNum + z].nml)
                                x += 60

                            break

                        else:
                            painter.drawPixmap(x, y, globals.Tiles[tileNum].main)
                            nmlPainter.drawPixmap(x, y, globals.Tiles[tileNum].nml)

                    elif randLen and (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
                        break

                    x += 60

    painter.end()
    nmlPainter.end()

    return tex, nml


def exportObject(name, baseName, idx, objNum):
    obj = globals.ObjectDefinitions[idx][objNum]
    randLen = obj.randByte & 0xF
    tex, nml = getImgFromObj(obj, randLen)

    # Get the collision data
    if obj.reversed:
        colldata = bytearray(obj.width * obj.height * 8)
        for crow, row in enumerate(obj.rows):
            if obj.subPartAt != -1:
                if crow >= obj.subPartAt:
                    crow -= obj.subPartAt

                else:
                    crow += obj.height - obj.subPartAt

            ctile = 0
            for tile in row:
                if len(tile) == 3:
                    tileNum = (tile[1] & 0xFF) + (((tile[1] >> 8) & 3) * 256)

                    pos = (crow * obj.width + ctile) * 8
                    colldata[pos:pos + 8] = struct.pack('<Q', globals.Tiles[tileNum].getCollision())

                    ctile += 1

    else:
        colldata = b''
        for row in obj.rows:
            for tile in row:
                if len(tile) == 3:
                    tileNum = (tile[1] & 0xFF) + (((tile[1] >> 8) & 3) * 256)
                    if randLen and (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
                        for z in range(randLen):
                            colldata += struct.pack('<Q', globals.Tiles[tileNum + z].getCollision())

                        break

                    else:
                        colldata += struct.pack('<Q', globals.Tiles[tileNum].getCollision())

    jsonData = {}

    tex.save(name + ".png", "PNG")
    jsonData['img'] = baseName + ".png"

    nml.save(name + "_nml.png", "PNG")
    jsonData['nml'] = baseName + "_nml.png"

    with open(name + ".colls", "wb+") as colls:
            colls.write(colldata)

    jsonData['colls'] = baseName + ".colls"

    deffile = b''

    for row in obj.rows:
        for tile in row:
            if len(tile) == 3:
                byte2 = tile[2] << 2
                byte2 |= (tile[1] >> 8) & 3  # Slot

                deffile += bytes([tile[0], tile[1] & 0xFF, byte2])

            else:
                deffile += bytes(tile)

        deffile += b'\xFE'

    deffile += b'\xFF'

    with open(name + ".objlyt", "wb+") as objlyt:
        objlyt.write(deffile)

    jsonData['objlyt'] = baseName + ".objlyt"

    indexfile = struct.pack('>HBBH', 0, obj.width, obj.height, obj.randByte)

    with open(name + ".meta", "wb+") as meta:
        meta.write(indexfile)

    jsonData['meta'] = baseName + ".meta"

    if randLen and (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
        jsonData['randLen'] = randLen

    with open(name + ".json", 'w+') as outfile:
        json.dump(jsonData, outfile)


def HandleTilesetEdited(soft=False):
    if not soft:
        globals.TilesetEdited = True

    mainWindow = globals.mainWindow
    mainWindow.objPicker.clearSelection()
    mainWindow.objPicker.LoadFromTilesets()
    mainWindow.updateNumUsedTilesLabel()
    mainWindow.CreationTabChanged(mainWindow.creationTabs.currentIndex())


def DeleteObject(idx, objNum, soft=False):
    # Get the tiles used by this object
    obj = globals.ObjectDefinitions[idx][objNum]
    usedTiles = []
    for row in obj.rows:
        for tile in row:
            if len(tile) == 3:
                if tile == [0, 0, 0]:  # Pa0 tile 0 used in another slot, don't count it
                    continue

                randLen = obj.randByte & 0xF
                tileNum = tile[1] & 0xFF

                if idx != (tile[1] >> 8) & 3:
                    continue

                if randLen:
                    for i in range(randLen):
                        if tileNum + i not in usedTiles:
                            usedTiles.append(tileNum + i)
                else:
                    if tileNum not in usedTiles:
                        usedTiles.append(tileNum)

    folderIndex = obj.folderIndex
    objAllIndex = obj.objAllIndex

    # Completely remove the object's definition
    if soft:
        globals.ObjectDefinitions[idx][objNum] = None

    else:
        del globals.ObjectDefinitions[idx][objNum]
        globals.ObjectDefinitions[idx].append(None)

    # Replace the object's tiles with empty tiles
    # if they are not used by other objects in the same tileset
    tilesetUsedTiles = getUsedTiles()[idx]

    T = TilesetTile()
    T.setCollisions(0)

    tileoffset = idx * 256

    for i in usedTiles:
        if i not in tilesetUsedTiles:
            globals.Tiles[i + tileoffset] = T

    # If soft deletion, stop here
    if soft:
        return

    # Unload the tileset if it's empty
    if globals.ObjectDefinitions[idx] == [None] * 256:
        UnloadTileset(idx)
        exec("globals.Area.tileset%d = ''" % idx)

    # Remove the object from globals.ObjectAddedtoEmbedded
    if folderIndex > -1 and globals.ObjectAddedtoEmbedded[globals.CurrentArea][folderIndex]:
        globals.ObjectAddedtoEmbedded[globals.CurrentArea][folderIndex].pop(objAllIndex, None)

    # Subtract 1 from the objects' types that after this object and in the same slot
    for folderIndex in globals.ObjectAddedtoEmbedded[globals.CurrentArea]:
        for i in globals.ObjectAddedtoEmbedded[globals.CurrentArea][folderIndex]:
            tempIdx, tempNum = globals.ObjectAddedtoEmbedded[globals.CurrentArea][folderIndex][i]
            if tempIdx == idx:
                if tempNum > objNum:
                    globals.ObjectAddedtoEmbedded[globals.CurrentArea][folderIndex][i] = (tempIdx, tempNum - 1)

    for layer in globals.Area.layers:
        for obj in layer:
            if obj.tileset == idx:
                if obj.type > objNum:
                    obj.SetType(obj.tileset, obj.type - 1)

    for stamp in globals.mainWindow.stampChooser.model.items:
        layers, sprites = globals.mainWindow.getEncodedObjects(stamp.MiyamotoClip, False)
        objects = []

        for layer in layers:
            for obj in layer:
                if obj.tileset == idx:
                    if obj.type > objNum:
                        obj.SetType(obj.tileset, obj.type - 1)

                objects.append(obj)

        stamp.MiyamotoClip = globals.mainWindow.encodeObjects(objects, sprites)

    if globals.mainWindow.clipboard is not None:
        if globals.mainWindow.clipboard.startswith('MiyamotoClip|') and globals.mainWindow.clipboard.endswith('|%'):
            layers, sprites = globals.mainWindow.getEncodedObjects(globals.mainWindow.clipboard, False)
            objects = []

            for layer in layers:
                for obj in layer:
                    if obj.tileset == idx:
                        if obj.type > objNum:
                            obj.SetType(obj.tileset, obj.type - 1)

                    objects.append(obj)

            globals.mainWindow.clipboard = globals.mainWindow.encodeObjects(objects, sprites)


def generateTilesetNames():
    """
    Generate 3 Tileset names
    """
    tilesetNames = ['Pa%d_%s_%d' % (i, os.path.splitext(globals.mainWindow.fileTitle)[0], globals.CurrentArea) for i in range(1, 4)]
    return tilesetNames


def writeBNTX(images):
    """
    Generates a BNTX file from our two QImages
    """
    if platform.system() == 'Windows':
        tile_path = globals.miyamoto_path + '/Tools'

    elif platform.system() == 'Linux':
        tile_path = globals.miyamoto_path + '/linuxTools'

    else:
        tile_path = globals.miyamoto_path + '/macTools'

    bntx = BNTX.File()
    bntx.new('textures')

    for name, img, width, height in images:
        hdr = BNTX.dds.generateHeader(1, width, height, "rgba8", [2, 3, 4, 5], 0, False)

        data = img.bits()
        data.setsize(img.byteCount())
        data = data.asstring()

        with open(tile_path + '/%s.dds' % name, 'wb+') as out:
            out.write(hdr)
            out.write(data)

        bntx.addTexture(0, False, False, False, False, tile_path + '/%s.dds' % name)
        os.remove(tile_path + '/%s.dds' % name)

    return bntx.save()


def writeBFRES(bfresdata, bntx):
    bom = ">" if bfresdata[0xC:0xE] == b'\xFE\xFF' else "<"

    alignmentShift = bfresdata[0xE]
    relocTbloff = struct.unpack(bom + "I", bfresdata[0x18:0x1C])[0]
    relocTbl = bytearray(bfresdata[relocTbloff:])

    assert struct.unpack(bom + "I", bfresdata[relocTbloff + 8:relocTbloff + 12])[0] == 5

    bfresdata = bytearray(bfresdata[:relocTbloff])

    startoff = struct.unpack(bom + "q", bfresdata[0x98:0xA0])[0]
    count = struct.unpack(bom + "q", bfresdata[0xC8:0xD0])[0]

    assert count > 0
    i = count - 1

    fileoff = struct.unpack(bom + "q", bfresdata[startoff + i * 16:startoff + 8 + i * 16])[0]
    dataSize = struct.unpack(bom + "q", bfresdata[startoff + 8 + i * 16:startoff + 16 + i * 16])[0]

    assert bfresdata[fileoff:fileoff + 4] == b'BNTX' and relocTbloff - fileoff - dataSize < 1 << alignmentShift

    round_up = lambda x, y: ((x - 1) | (y - 1)) + 1

    bfresdata[startoff + 8 + i * 16:startoff + 16 + i * 16] = struct.pack(bom + "q", len(bntx))
    bfresdata[fileoff:] = bntx

    relocAlignBytes = b'\0' * (round_up(len(bfresdata), 1 << alignmentShift) - len(bfresdata))
    bfresdata += relocAlignBytes

    bRelocTbloff = struct.pack(bom + "I", len(bfresdata))
    relocTbl[4:8] = bRelocTbloff

    sec5Size = struct.unpack(bom + "I", relocTbl[0x7C:0x80])[0]
    sec5Size += len(bfresdata) - relocTbloff
    relocTbl[0x7C:0x80] = struct.pack(bom + "I", sec5Size)

    bfresdata += relocTbl

    bfresdata[0x18:0x1C] = bRelocTbloff
    bfresdata[0x1C:0x20] = struct.pack(bom + "I", len(bfresdata))

    return bfresdata


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

    for z in range(tileoffset, tileoffset + 256):
        tile = QtGui.QImage(64, 64, QtGui.QImage.Format_RGBA8888)
        tile.fill(Qt.transparent)
        tilePainter = QtGui.QPainter(tile)

        tilePainter.drawPixmap(2, 2, globals.Tiles[z].nml if nml else globals.Tiles[z].main)
        tilePainter.end()

        for i in range(2, 62):
            color = tile.pixel(i, 2)
            for pix in range(0, 2):
                tile.setPixel(i, pix, color)

            color = tile.pixel(2, i)
            for p in range(0, 2):
                tile.setPixel(p, i, color)

            color = tile.pixel(i, 61)
            for p in range(62, 64):
                tile.setPixel(i, p, color)

            color = tile.pixel(61, i)
            for p in range(62, 64):
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
    return tex


def SaveTileset(idx):
    """
    Saves a tileset from a specific slot
    """
    name = eval('globals.Area.tileset%d' % idx)

    tileoffset = idx * 256

    img = PackTexture(idx)
    nml = PackTexture(idx, True)
    bntx = writeBNTX([(name, img, 2048, 512), ('%s_nml' % name, nml, 2048, 512)])

    with open(globals.miyamoto_path + '/miyamotodata/output.bfres', 'rb') as file:
        bfresdata = file.read()

    bfresdata = writeBFRES(bfresdata, bntx)

    defs = globals.ObjectDefinitions[idx]

    if defs is None:
        return False

    colldata = b''
    deffile = b''
    indexfile = b''

    for i in range(tileoffset, tileoffset + 256):
        colldata += struct.pack('<Q', globals.Tiles[i].getCollision())

    for obj in defs:
        if obj is None:
            break

        indexfile += struct.pack('<HBBH', len(deffile), obj.width, obj.height, obj.randByte)

        for row in obj.rows:
            for tile in row:
                if len(tile) == 3:
                    byte2 = tile[2] << 2
                    byte2 |= (tile[1] >> 8) & 3  # Slot

                    deffile += bytes([tile[0], tile[1] & 0xFF, byte2])

                else:
                    deffile += bytes(tile)

            deffile += b'\xFE'

        deffile += b'\xFF'

    arc = SarcLib.SARC_Archive(endianness='<')
    arc.addFile(SarcLib.File('output.bfres', bfresdata))

    chk = SarcLib.Folder('BG_chk')
    arc.addFolder(chk)
    chk.addFile(SarcLib.File('d_bgchk_%s.bin' % name, colldata))

    unt = SarcLib.Folder('BG_unt')
    arc.addFolder(unt)
    unt.addFile(SarcLib.File('%s.bin' % name, deffile))
    unt.addFile(SarcLib.File('%s_hd.bin' % name, indexfile))

    paths = reversed(globals.gamedef.GetGamePaths())
    for path in paths:
        if not os.path.isdir(os.path.join(os.path.dirname(path), 'Unit')):
            continue

        sarcname = os.path.join(os.path.dirname(path), 'Unit', name + '.szs')
        CompYaz0(arc.save()[0], sarcname, globals.CompLevel)
        break

    else:
        raise RuntimeError("Could not save tileset!")


def loadBNTXFromBFRES(inb):
    assert inb[:8] == b'FRES    '
    bom = ">" if inb[0xC:0xE] == b'\xFE\xFF' else "<"
    startoff = struct.unpack(bom + "q", inb[0x98:0xA0])[0]
    count = struct.unpack(bom + "q", inb[0xC8:0xD0])[0]

    if not count:
        raise RuntimeError("Tileset not found")

    else:
        # Not sure if this is correct, I hope it is.
        # If you face any problems, try replacing "0x20" with "0x10 * count".
        namesoff = struct.unpack(bom + "q", inb[0xA0:0xA8])[0] + 0x20

        for i in range(count):
            fileoff = struct.unpack(bom + "q", inb[startoff + i * 16:startoff + 8 + i * 16])[0]
            dataSize = struct.unpack(bom + "q", inb[startoff + 8 + i * 16:startoff + 16 + i * 16])[0]

            data = inb[fileoff:fileoff + dataSize]
            nameoff = struct.unpack(bom + "q", inb[namesoff + i * 16:namesoff + 8 + i * 16])[0]
            nameSize = struct.unpack(bom + 'H', inb[nameoff:nameoff + 2])[0]
            name = inb[nameoff + 2:nameoff + 2 + nameSize].decode('utf-8')

            if name == "textures.bntx":
                bntx = BNTX.File(); bntx.load(data, 0)
                break

        else:
            raise RuntimeError("Tileset not found")

    return bntx


def loadTexFromBNTX(bntx, name):
    for texture in bntx.textures:
        if name == texture.name:
            break

    else:
        raise RuntimeError("Tileset not found")

    if texture.format_ in [0x101, 0x201, 0x301, 0x401, 0x501, 0x601, 0x701,
                           0x801, 0x901, 0xb01, 0xb06, 0xc01, 0xc06, 0xe01,
                           0x1a01, 0x1a06, 0x1b01, 0x1b06, 0x1c01, 0x1c06,
                           0x1d01, 0x1d02, 0x1e01, 0x1e02, 0x3b01] and texture.dim == 2:

        result, _, _ = bntx.rawData(texture)

        if texture.format_ == 0x101:
            data = result[0]

            format_ = 'la4'
            bpp = 1

        elif texture.format_ == 0x201:
            data = result[0]

            format_ = 'l8'
            bpp = 1

        elif texture.format_ == 0x301:
            data = result[0]

            format_ = 'rgba4'
            bpp = 2

        elif texture.format_ == 0x401:
            data = result[0]

            format_ = 'abgr4'
            bpp = 2

        elif texture.format_ == 0x501:
            data = result[0]

            format_ = 'rgb5a1'
            bpp = 2

        elif texture.format_ == 0x601:
            data = result[0]

            format_ = 'a1bgr5'
            bpp = 2

        elif texture.format_ == 0x701:
            data = result[0]

            format_ = 'rgb565'
            bpp = 2

        elif texture.format_ == 0x801:
            data = result[0]

            format_ = 'bgr565'
            bpp = 2

        elif texture.format_ == 0x901:
            data = result[0]

            format_ = 'la8'
            bpp = 2

        elif (texture.format_ >> 8) == 0xb:
            data = result[0]

            format_ = 'rgba8'
            bpp = 4

        elif (texture.format_ >> 8) == 0xc:
            data = result[0]

            format_ = 'bgra8'
            bpp = 4

        elif texture.format_ == 0xe01:
            data = result[0]

            format_ = 'bgr10a2'
            bpp = 4

        elif (texture.format_ >> 8) == 0x1a:
            data = BNTX.bcn.decompressDXT1(result[0], texture.width, texture.height)

            format_ = 'rgba8'
            bpp = 4

        elif (texture.format_ >> 8) == 0x1b:
            data = BNTX.bcn.decompressDXT3(result[0], texture.width, texture.height)

            format_ = 'rgba8'
            bpp = 4

        elif (texture.format_ >> 8) == 0x1c:
            data = BNTX.bcn.decompressDXT5(result[0], texture.width, texture.height)

            format_ = 'rgba8'
            bpp = 4

        elif (texture.format_ >> 8) == 0x1d:
            data = BNTX.bcn.decompressBC4(result[0], texture.width, texture.height, 0 if texture.format_ & 3 == 1 else 1)

            format_ = 'rgba8'
            bpp = 4

        elif (texture.format_ >> 8) == 0x1e:
            data = BNTX.bcn.decompressBC5(result[0], texture.width, texture.height, 0 if texture.format_ & 3 == 1 else 1)

            format_ = 'rgba8'
            bpp = 4

        elif texture.format_ == 0x3b01:
            data = result[0]

            format_ = 'bgr5a1'
            bpp = 2

        data = BNTX.dds.formConv.torgba8(texture.width, texture.height, bytearray(data), format_, bpp, texture.compSel)
        return QtGui.QImage(data, texture.width, texture.height, QtGui.QImage.Format_RGBA8888)

    raise RuntimeError("%s could not be loaded" % name)


def CascadeTilesetNames_Category(lower, upper):
    """
    Applies upper as a patch of lower
    """
    lower = list(lower)
    for item in upper:

        if isinstance(item[1], tuple) or isinstance(item[1], list):
            # It's a category

            for i, lowitem in enumerate(lower):
                lowitem = lower[i]
                if lowitem[0] == item[0]:  # names are ==
                    lower[i] = list(lower[i])
                    lower[i][1] = CascadeTilesetNames_Category(lowitem[1], item[1])
                    break

            else:
                i = 0
                while (i < len(lower)) and (isinstance(lower[i][1], tuple) or isinstance(lower[i][1], list)): i += 1
                lower.insert(i + 1, item)

        else:  # It's a tileset entry
            for i, lowitem in enumerate(lower):
                lowitem = lower[i]
                if lowitem[0] == item[0]:  # filenames are ==
                    lower[i] = list(lower[i])
                    lower[i][1] = item[1]
                    break

            else:
                lower.append(item)
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
    T = TilesetTile()
    T.setCollisions(0)
    globals.Tiles[tileoffset:tileoffset + 256] = [T] * 256

    globals.ObjectDefinitions[idx] = [None] * 256


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


def _RenderObject(obj, width, height, fullslope=False):
    """
    Render a tileset object into an array
    """
    # allocate an array
    dest = [[0] * width for _ in range(height)]

    # ignore non-existent objects
    if obj is None or len(obj.rows) == 0:
        return dest

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
            if row and (row[0][0] & 2) != 0:
                repeatFound = True
                inRepeat.append(row)

            elif repeatFound:
                afterRepeat.append(row)

            else:
                beforeRepeat.append(row)

        bc = len(beforeRepeat)
        ic = len(inRepeat)
        ac = len(afterRepeat)

        if ic == 0:
            for y in range(height):
                RenderStandardRow(dest[y], beforeRepeat[y % bc], width)

        elif height <= bc + ac:
            for y in range(height):
                if y < bc:
                    RenderStandardRow(dest[y], beforeRepeat[y], width)

                else:
                    RenderStandardRow(dest[y], afterRepeat[y - bc], width)

        else:
            afterthreshold = height - ac - 1
            for y in range(height):
                if y < bc:
                    RenderStandardRow(dest[y], beforeRepeat[y], width)

                elif y > afterthreshold:
                    RenderStandardRow(dest[y], afterRepeat[y - height + ac], width)

                else:
                    RenderStandardRow(dest[y], inRepeat[(y - bc) % ic], width)

    return dest


def RenderObject(tileset, objnum, width, height, fullslope=False):
    # ignore non-existent objects
    try:
        tileset_defs = globals.ObjectDefinitions[tileset]

    except IndexError:
        tileset_defs = None

    if tileset_defs is None:
        return [[0] * width for _ in range(height)]

    try:
        obj = tileset_defs[objnum]

    except IndexError:
        obj = None

    return _RenderObject(obj, width, height, fullslope)


def RenderObjectAll(obj, width, height, fullslope=False):
    return _RenderObject(obj, width, height, fullslope)


def RenderStandardRow(dest, row, width):
    """
    Render a row from an object
    """
    if not row:
        return

    repeatFound = False
    beforeRepeat = []
    inRepeat = []
    afterRepeat = []

    for tile in row:
        if tile[0] & 1:
            repeatFound = True
            inRepeat.append(tile)

        elif repeatFound:
            afterRepeat.append(tile)

        else:
            beforeRepeat.append(tile)

    bc = len(beforeRepeat)
    ic = len(inRepeat)
    ac = len(afterRepeat)
    if ic == 0:
        for x in range(width):
            dest[x] = beforeRepeat[x % bc][1]

    elif width <= bc + ac:
        for x in range(width):
            if x < bc:
                dest[x] = beforeRepeat[x][1]

            else:
                dest[x] = afterRepeat[x - bc][1]

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
        return sections[0], None

    else:
        return sections[0], sections[1]


def ProcessOverrides(name):
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
            t[offset + len(globals.Overrides) - 1].main = t[49].main
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
            grassType = 5
            for sprite in globals.Area.sprites:
                if sprite.type == 564:
                    grassType = min(sprite.spritedata[5] & 0xf, 5)
                    if grassType < 2:
                        grassType = 0

                    elif grassType in [3, 4]:
                        grassType = 3

            if grassType == 0:  # Forest
                replace_flowers = offset + 160
                replace_grass = offset + 163
                replace_both = offset + 168

            elif grassType == 2:  # Underground
                replace_flowers = offset + 55
                replace_grass = offset + 171
                replace_both = offset + 188

            elif grassType == 3:  # Sky
                replace_flowers = offset + 176
                replace_grass = offset + 179
                replace_both = offset + 184

            else:  # Normal
                replace_flowers = offset + 55
                replace_grass = offset + 58
                replace_both = offset + 106

            ## Flowers
            replace = replace_flowers
            for i in range(210, 213):
                t[i].main = t[replace].main
                replace += 1
            ## Grass
            replace = replace_grass
            for i in range(178, 183):
                t[i].main = t[replace].main
                replace += 1
            ## Flowers and grass
            replace = replace_both
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
    pa1 = sorted(ParseCategory(globals.TilesetNames[1][0]), key=lambda entry: entry[1])
    pa2 = sorted(ParseCategory(globals.TilesetNames[2][0]), key=lambda entry: entry[1])
    pa3 = sorted(ParseCategory(globals.TilesetNames[3][0]), key=lambda entry: entry[1])
    return (pa0, pa1, pa2, pa3)
