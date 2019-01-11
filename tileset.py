#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! DX Level Editor - New Super Mario Bros. U Deluxe Level Editor
# Copyright (C) 2009-2019 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7, John10v10

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
import gibberish
import SarcLib
import spritelib as SLib

#################################


class TilesetTile:
    """
    Class that represents a single tile in a tileset
    """
    exists = True

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

    def getCurrentTile(self):
        """
        Returns the current tile based on the current animation frame
        """
        if not (globals.TilesetsAnimating and self.isAnimated):
            result = QtGui.QPixmap(self.main)

        else:
            result = QtGui.QPixmap(self.animTiles[self.animFrame])

        if globals.CollisionsShown and (self.collOverlay is not None):
            painter = QtGui.QPainter(result)
            painter.drawPixmap(0, 0, self.collOverlay)
            del painter

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
            color = QtGui.QColor(128, 64, 0, 120)
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
            elif CD[2] == 6:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, 0)]))
            elif CD[2] == 7:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, 0)]))
            elif CD[2] == 8:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 9:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
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
            elif CD[2] == 6:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(0, 0)]))
            elif CD[2] == 7:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, 0)]))
            elif CD[2] == 8:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 9:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
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
            if CD[2] == 0:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5)]))
            elif CD[2] == 1:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth * 0.5)]))
            elif CD[2] == 2:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5)]))
            elif CD[2] == 3:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5)]))
            elif CD[2] == 6:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 7:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth)]))
            elif CD[2] == 8:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, 0)]))
            elif CD[2] == 9:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth)]))
            elif CD[2] == 10:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5)]))
            elif CD[2] == 11:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 12:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 13:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth)]))
            elif CD[2] == 14:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(0, globals.TileWidth)]))

        elif CD[4] == 3:  # Solid-on-bottom
            painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.75),
                                                QtCore.QPoint(0, globals.TileWidth * 0.75)]))

            painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.625, 0),
                                                QtCore.QPoint(globals.TileWidth * 0.625, globals.TileWidth * 0.5),
                                                QtCore.QPoint(globals.TileWidth * 0.75, globals.TileWidth * 0.5),
                                                QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth * (17 / 24)),
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
            elif CD[2] == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.25)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth * 0.5),
                                                    QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth * 0.75)]))
            elif CD[2] == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.25, 0)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.5, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth, globals.TileWidth),
                                                    QtCore.QPoint(globals.TileWidth * 0.75, 0)]))
            elif CD[2] == 6:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.25, globals.TileWidth)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(globals.TileWidth * 0.5, 0),
                                                    QtCore.QPoint(globals.TileWidth, 0),
                                                    QtCore.QPoint(globals.TileWidth * 0.75, globals.TileWidth)]))

        elif CD[4] == 1:  # Solid
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
        cbyte = source[i]

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
    T.setCollisions([0] * 8)
    globals.Tiles = [T] * 0x200 * 4
    globals.Tiles += globals.Overrides
    SLib.Tiles = globals.Tiles

    globals.TilesetAnimTimer = QtCore.QTimer()
    globals.TilesetAnimTimer.timeout.connect(IncrementTilesetFrame)
    globals.TilesetAnimTimer.start(90)

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
                    colldata[pos:pos + 8] = bytes(globals.Tiles[tileNum].collData)

                    ctile += 1

    else:
        colldata = b''
        for row in obj.rows:
            for tile in row:
                if len(tile) == 3:
                    tileNum = (tile[1] & 0xFF) + (((tile[1] >> 8) & 3) * 256)
                    if randLen and (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
                        for z in range(randLen):
                            colldata += bytes(globals.Tiles[tileNum + z].collData)

                        break

                    else:
                        colldata += bytes(globals.Tiles[tileNum].collData)

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

    indexfile = struct.pack('>HBBxB', 0, obj.width, obj.height, obj.randByte)

    with open(name + ".meta", "wb+") as meta:
        meta.write(indexfile)

    jsonData['meta'] = baseName + ".meta"

    if randLen and (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
        jsonData['randLen'] = randLen

    with open(name + ".json", 'w+') as outfile:
        json.dump(jsonData, outfile)


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
    T.setCollisions([0] * 8)
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
            if len(row) == 0:
                continue

            if (row[0][0] & 2) != 0:
                repeatFound = True
                inRepeat.append(row)

            else:
                if repeatFound:
                    afterRepeat.append(row)

                else:
                    beforeRepeat.append(row)

        bc = len(beforeRepeat)
        ic = len(inRepeat)
        ac = len(afterRepeat)

        if ic == 0:
            for y in range(height):
                RenderStandardRow(dest[y], beforeRepeat[y % bc], width)

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


def RenderStandardRow(dest, row, width):
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

    bc = len(beforeRepeat)
    ic = len(inRepeat)
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
    pa1 = sorted(ParseCategory(globals.TilesetNames[1][0]), key=lambda entry: entry[1])
    pa2 = sorted(ParseCategory(globals.TilesetNames[2][0]), key=lambda entry: entry[1])
    pa3 = sorted(ParseCategory(globals.TilesetNames[3][0]), key=lambda entry: entry[1])
    return (pa0, pa1, pa2, pa3)
