#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2017 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7, John10v10

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

# sprites.py
# Contains code to render NSMBU sprite images
# not even close to done...


# IMPORTANT!!!! An offset value of 16 is one block!


################################################################
################################################################

############ Imports ############

import math

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *

Qt = QtCore.Qt

from miyamoto import *

import spritelib as SLib

#################################

ImageCache = SLib.ImageCache

# Global varible for rotations.
Rotations = [0, 0, 0]
StoneRotation = 0


################################################################
################################################################

# GETTING SPRITEDATA:
# You can get the spritedata that is set on a sprite to alter
# the image that is shown. To do this, add a datachanged method,
# with the parameter self. In this method, you can access the
# spritedata through self.parent.spritedata[n], which returns
# the (n+1)th byte of the spritedata. To find the n for nybble
# x, use this formula:
# n = (x/2) - 1
#
# If the nybble you want is the upper 4 bits of n (x is odd),
# you can get the value of x like this:
# val_x = n >> 4

class SpriteImage_Pipe(SLib.SpriteImage):
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.spritebox.shown = self.mini = self.big = self.painted = self.typeinfluence = False
        self.hasTop = True
        self.direction = 'U'
        self.colours = ("Green", "Red", "Yellow", "Blue")
        self.topY = self.topX = self.colour = self.extraLength = self.x = self.y = 0
        self.width = self.height = 32
        self.pipeHeight = self.pipeWidth = 120
        self.parent.setZValue(24999)

    #        self.expandable = False
    #        self.moving = False

    @staticmethod
    def loadImages():
        if 'PipeTopGreen' not in ImageCache:
            for colour in ("Green", "Red", "Yellow", "Blue"):
                ImageCache['PipeTop%s' % colour] = SLib.GetImg('pipe_%s_top.png' % colour.lower())
                ImageCache['PipeMiddleV%s' % colour] = SLib.GetImg('pipe_%s_middleV.png' % colour.lower())
                ImageCache['PipeMiddleH%s' % colour] = SLib.GetImg('pipe_%s_middleH.png' % colour.lower())
                ImageCache['PipeBottom%s' % colour] = SLib.GetImg('pipe_%s_bottom.png' % colour.lower())
                ImageCache['PipeLeft%s' % colour] = SLib.GetImg('pipe_%s_left.png' % colour.lower())
                ImageCache['PipeRight%s' % colour] = SLib.GetImg('pipe_%s_right.png' % colour.lower())

                # Paint
                ImageCache['PipePaintedTop%s' % colour] = SLib.GetImg('pipe_painted_%s_top.png' % colour.lower())
                ImageCache['PipePaintedMiddleV%s' % colour] = SLib.GetImg(
                    'pipe_painted_%s_middleV.png' % colour.lower())
                ImageCache['PipePaintedMiddleH%s' % colour] = SLib.GetImg(
                    'pipe_painted_%s_middleH.png' % colour.lower())
                ImageCache['PipePaintedBottom%s' % colour] = SLib.GetImg('pipe_painted_%s_bottom.png' % colour.lower())
                ImageCache['PipePaintedLeft%s' % colour] = SLib.GetImg('pipe_painted_%s_left.png' % colour.lower())
                ImageCache['PipePaintedRight%s' % colour] = SLib.GetImg('pipe_painted_%s_right.png' % colour.lower())

                # BIG
                ImageCache['PipeBigTop%s' % colour] = ImageCache['PipeTop%s' % colour].scaled(240, 240,
                                                                                              QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigMiddleV%s' % colour] = ImageCache['PipeMiddleV%s' % colour].scaled(240, 240)
                ImageCache['PipeBigMiddleH%s' % colour] = ImageCache['PipeMiddleH%s' % colour].scaled(240, 240)
                ImageCache['PipeBigBottom%s' % colour] = ImageCache['PipeBottom%s' % colour].scaled(240, 240,
                                                                                                    QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigLeft%s' % colour] = ImageCache['PipeLeft%s' % colour].scaled(240, 240,
                                                                                                QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigRight%s' % colour] = ImageCache['PipeRight%s' % colour].scaled(240, 240,
                                                                                                  QtCore.Qt.KeepAspectRatio)

                # MINI
                if colour == "Green":
                    ImageCache['MiniPipeTop%s' % colour] = SLib.GetImg('pipe_mini_%s_top.png' % colour.lower())
                    ImageCache['MiniPipeMiddleV%s' % colour] = SLib.GetImg('pipe_mini_%s_middleV.png' % colour.lower())
                    ImageCache['MiniPipeMiddleH%s' % colour] = SLib.GetImg('pipe_mini_%s_middleH.png' % colour.lower())
                    ImageCache['MiniPipeBottom%s' % colour] = SLib.GetImg('pipe_mini_%s_bottom.png' % colour.lower())
                    ImageCache['MiniPipeLeft%s' % colour] = SLib.GetImg('pipe_mini_%s_left.png' % colour.lower())
                    ImageCache['MiniPipeRight%s' % colour] = SLib.GetImg('pipe_mini_%s_right.png' % colour.lower())

    def dataChanged(self):
        super().dataChanged()

        # if self.moving: rawlength = (self.parent.spritedata[4] & 0x0F) + 1
        # else:
        rawlength = (self.parent.spritedata[5] & 0x0F) + 1

        if not self.mini:
            rawtop = (self.parent.spritedata[2] >> 4) & 3

            # if self.moving:
            # rawtop = 0 & 3

            # if self.expandable: rawcolour = (self.parent.spritedata[3]) & 3
            # elif self.moving: rawcolour = (self.parent.spritedata[3]) & 3
            #            else:
            rawcolour = (self.parent.spritedata[5] >> 4) & 3

            if self.typeinfluence and rawtop == 0:
                # if self.expandable: rawtype = self.parent.spritedata[4] & 3
                # elif self.moving: rawtype = self.parent.spritedata[5] >> 4
                # else:
                rawtype = self.parent.spritedata[3] & 3
            else:
                rawtype = 0

            if rawtop == 1:
                pipeLength = rawlength + rawtype + self.extraLength + 1
            elif rawtop == 0:
                if rawtype == 0:
                    pipeLength = rawlength + rawtype + self.extraLength + 1
                else:
                    pipeLength = rawlength + rawtype + self.extraLength
            else:
                pipeLength = rawlength + rawtype + self.extraLength

            self.hasTop = (rawtop != 3)
            #            self.big = (rawtype == 3)
            self.colour = self.colours[rawcolour]
        else:
            pipeLength = rawlength
            self.colour = "Green"

        if self.direction in 'LR':  # horizontal
            self.pipeWidth = pipeLength * 60
            self.width = (self.pipeWidth / 3.75)
            if self.big:
                self.middle = ImageCache['PipeBigMiddleH%s' % self.colour]
                self.height = 64
                self.pipeHeight = 240
            elif self.painted:
                self.middle = ImageCache['PipePaintedMiddleH%s' % self.colour]
            elif not self.mini:
                self.middle = ImageCache['PipeMiddleH%s' % self.colour]
            else:
                self.middle = ImageCache['MiniPipeMiddleH%s' % self.colour]
                self.height = 16
                self.pipeHeight = 60

            if self.direction == 'R':  # faces right
                if self.big:
                    self.top = ImageCache['PipeBigRight%s' % self.colour]
                    self.topX = self.pipeWidth - 120
                elif self.painted:
                    self.topX = self.pipeWidth - 60
                    self.top = ImageCache['PipePaintedRight%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeRight%s' % self.colour]
                    self.topX = self.pipeWidth - 60
                else:
                    self.top = ImageCache['MiniPipeRight%s' % self.colour]
                    self.topX = self.pipeWidth - 60
            else:  # faces left
                if self.big:
                    self.top = ImageCache['PipeBigLeft%s' % self.colour]
                elif self.painted:
                    self.top = ImageCache['PipePaintedLeft%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeLeft%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeLeft%s' % self.colour]
                self.xOffset = 16 - self.width

        if self.direction in 'UD':  # vertical
            self.pipeHeight = pipeLength * 60
            self.height = (self.pipeHeight / 3.75)
            if self.big:
                self.middle = ImageCache['PipeBigMiddleV%s' % self.colour]
                self.width = 64
                self.pipeWidth = 240
            elif self.painted:
                self.middle = ImageCache['PipePaintedMiddleV%s' % self.colour]
            elif not self.mini:
                self.middle = ImageCache['PipeMiddleV%s' % self.colour]
            else:
                self.middle = ImageCache['MiniPipeMiddleV%s' % self.colour]
                self.width = 16
                self.pipeWidth = 60

            if self.direction == 'D':  # faces down
                if self.big:
                    self.top = ImageCache['PipeBigBottom%s' % self.colour]
                    self.topY = self.pipeHeight - 120
                elif self.painted:
                    self.top = ImageCache['PipePaintedBottom%s' % self.colour]
                    self.topY = self.pipeHeight - 60
                elif not self.mini:
                    self.top = ImageCache['PipeBottom%s' % self.colour]
                    self.topY = self.pipeHeight - 60
                else:
                    self.top = ImageCache['MiniPipeBottom%s' % self.colour]
                    self.topY = self.pipeHeight - 60
            else:  # faces up
                if self.big:
                    self.top = ImageCache['PipeBigTop%s' % self.colour]
                elif self.painted:
                    self.top = ImageCache['PipePaintedTop%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeTop%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeTop%s' % self.colour]
                self.yOffset = 16 - (self.pipeHeight / 3.75)

    def paint(self, painter):
        super().paint(painter)
        painter.drawTiledPixmap(self.x, self.y, self.pipeWidth, self.pipeHeight, self.middle)
        if self.hasTop:
            painter.drawPixmap(self.topX, self.topY, self.top)


class SpriteImage_PipeAlt(SLib.SpriteImage):
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.spritebox.shown = self.mini = self.big = self.painted = self.typeinfluence = False
        self.hasTop = True
        self.direction = 'U'
        self.colours = ("Green", "Red", "Yellow", "Blue")
        self.topY = self.topX = self.colour = self.extraLength = self.x = self.y = 0
        self.width = self.height = 32
        self.pipeHeight = self.pipeWidth = 120
        self.parent.setZValue(24999)

    #        self.expandable = False
    #        self.moving = False

    @staticmethod
    def loadImages():
        if 'PipeTopGreen' not in ImageCache:
            for colour in ("Green", "Red", "Yellow", "Blue"):
                ImageCache['PipeTop%s' % colour] = SLib.GetImg('pipe_%s_top.png' % colour.lower())
                ImageCache['PipeMiddleV%s' % colour] = SLib.GetImg('pipe_%s_middleV.png' % colour.lower())
                ImageCache['PipeMiddleH%s' % colour] = SLib.GetImg('pipe_%s_middleH.png' % colour.lower())
                ImageCache['PipeBottom%s' % colour] = SLib.GetImg('pipe_%s_bottom.png' % colour.lower())
                ImageCache['PipeLeft%s' % colour] = SLib.GetImg('pipe_%s_left.png' % colour.lower())
                ImageCache['PipeRight%s' % colour] = SLib.GetImg('pipe_%s_right.png' % colour.lower())

                # Paint
                ImageCache['PipePaintedTop%s' % colour] = SLib.GetImg('pipe_painted_%s_top.png' % colour.lower())
                ImageCache['PipePaintedMiddleV%s' % colour] = SLib.GetImg(
                    'pipe_painted_%s_middleV.png' % colour.lower())
                ImageCache['PipePaintedMiddleH%s' % colour] = SLib.GetImg(
                    'pipe_painted_%s_middleH.png' % colour.lower())
                ImageCache['PipePaintedBottom%s' % colour] = SLib.GetImg('pipe_painted_%s_bottom.png' % colour.lower())
                ImageCache['PipePaintedLeft%s' % colour] = SLib.GetImg('pipe_painted_%s_left.png' % colour.lower())
                ImageCache['PipePaintedRight%s' % colour] = SLib.GetImg('pipe_painted_%s_right.png' % colour.lower())

                # BIG
                ImageCache['PipeBigTop%s' % colour] = ImageCache['PipeTop%s' % colour].scaled(240, 240,
                                                                                              QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigMiddleV%s' % colour] = ImageCache['PipeMiddleV%s' % colour].scaled(240, 240)
                ImageCache['PipeBigMiddleH%s' % colour] = ImageCache['PipeMiddleH%s' % colour].scaled(240, 240)
                ImageCache['PipeBigBottom%s' % colour] = ImageCache['PipeBottom%s' % colour].scaled(240, 240,
                                                                                                    QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigLeft%s' % colour] = ImageCache['PipeLeft%s' % colour].scaled(240, 240,
                                                                                                QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigRight%s' % colour] = ImageCache['PipeRight%s' % colour].scaled(240, 240,
                                                                                                  QtCore.Qt.KeepAspectRatio)

                # MINI
                if colour == "Green":
                    ImageCache['MiniPipeTop%s' % colour] = SLib.GetImg('pipe_mini_%s_top.png' % colour.lower())
                    ImageCache['MiniPipeMiddleV%s' % colour] = SLib.GetImg('pipe_mini_%s_middleV.png' % colour.lower())
                    ImageCache['MiniPipeMiddleH%s' % colour] = SLib.GetImg('pipe_mini_%s_middleH.png' % colour.lower())
                    ImageCache['MiniPipeBottom%s' % colour] = SLib.GetImg('pipe_mini_%s_bottom.png' % colour.lower())
                    ImageCache['MiniPipeLeft%s' % colour] = SLib.GetImg('pipe_mini_%s_left.png' % colour.lower())
                    ImageCache['MiniPipeRight%s' % colour] = SLib.GetImg('pipe_mini_%s_right.png' % colour.lower())

    def dataChanged(self):
        super().dataChanged()

        # if self.moving: rawlength = (self.parent.spritedata[4] & 0x0F) + 1
        # else:
        rawlength = (self.parent.spritedata[4] & 0x0F) + 1

        if not self.mini:
            # rawtop = (self.parent.spritedata[2] >> 4) & 3
            rawtop = 0

            # if self.moving:
            # rawtop = 0 & 3

            # if self.expandable: rawcolour = (self.parent.spritedata[3]) & 3
            # elif self.moving: rawcolour = (self.parent.spritedata[3]) & 3
            # else:
            rawcolour = (self.parent.spritedata[3] & 0x0F) & 3

            if self.typeinfluence and rawtop == 0:
                # if self.expandable: rawtype = self.parent.spritedata[4] & 3
                # elif self.moving: rawtype = self.parent.spritedata[5] >> 4
                # else:
                rawtype = (self.parent.spritedata[5] >> 4) & 3
            else:
                rawtype = 0

            if rawtop == 1:
                pipeLength = rawlength + rawtype + self.extraLength + 1
            elif rawtop == 0:
                if rawtype == 0:
                    pipeLength = rawlength + rawtype + self.extraLength + 1
                else:
                    pipeLength = rawlength + rawtype + self.extraLength
            else:
                pipeLength = rawlength + rawtype + self.extraLength

            self.hasTop = (rawtop != 3)
            #            self.big = (rawtype == 3)
            self.colour = self.colours[rawcolour]
        else:
            pipeLength = rawlength
            self.colour = "Green"

        if self.direction in 'LR':  # horizontal
            self.pipeWidth = pipeLength * 60
            self.width = (self.pipeWidth / 3.75)
            if self.big:
                self.middle = ImageCache['PipeBigMiddleH%s' % self.colour]
                self.height = 64
                self.pipeHeight = 240
            elif self.painted:
                self.middle = ImageCache['PipePaintedMiddleH%s' % self.colour]
            elif not self.mini:
                self.middle = ImageCache['PipeMiddleH%s' % self.colour]
            else:
                self.middle = ImageCache['MiniPipeMiddleH%s' % self.colour]
                self.height = 16
                self.pipeHeight = 60

            if self.direction == 'R':  # faces right
                if self.big:
                    self.top = ImageCache['PipeBigRight%s' % self.colour]
                    self.topX = self.pipeWidth - 120
                elif self.painted:
                    self.topX = self.pipeWidth - 60
                    self.top = ImageCache['PipePaintedRight%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeRight%s' % self.colour]
                    self.topX = self.pipeWidth - 60
                else:
                    self.top = ImageCache['MiniPipeRight%s' % self.colour]
                    self.topX = self.pipeWidth - 60
            else:  # faces left
                if self.big:
                    self.top = ImageCache['PipeBigLeft%s' % self.colour]
                elif self.painted:
                    self.top = ImageCache['PipePaintedLeft%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeLeft%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeLeft%s' % self.colour]
                    # self.xOffset = 16 - self.width

        if self.direction in 'UD':  # vertical
            self.pipeHeight = pipeLength * 60
            self.height = (self.pipeHeight / 3.75)
            if self.big:
                self.middle = ImageCache['PipeBigMiddleV%s' % self.colour]
                self.width = 64
                self.pipeWidth = 240
            elif self.painted:
                self.middle = ImageCache['PipePaintedMiddleV%s' % self.colour]
            elif not self.mini:
                self.middle = ImageCache['PipeMiddleV%s' % self.colour]
            else:
                self.middle = ImageCache['MiniPipeMiddleV%s' % self.colour]
                self.width = 16
                self.pipeWidth = 60

            if self.direction == 'D':  # faces down
                if self.big:
                    self.top = ImageCache['PipeBigBottom%s' % self.colour]
                    self.topY = self.pipeHeight - 120
                elif self.painted:
                    self.top = ImageCache['PipePaintedBottom%s' % self.colour]
                    self.topY = self.pipeHeight - 60
                elif not self.mini:
                    self.top = ImageCache['PipeBottom%s' % self.colour]
                    self.topY = self.pipeHeight - 60
                else:
                    self.top = ImageCache['MiniPipeBottom%s' % self.colour]
                    self.topY = self.pipeHeight - 60
            else:  # faces up
                if self.big:
                    self.top = ImageCache['PipeBigTop%s' % self.colour]
                elif self.painted:
                    self.top = ImageCache['PipePaintedTop%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeTop%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeTop%s' % self.colour]
                    # self.yOffset = 16 - (self.pipeHeight/3.75)

    def paint(self, painter):
        super().paint(painter)
        painter.drawTiledPixmap(self.x, self.y, self.pipeWidth, self.pipeHeight, self.middle)
        if self.hasTop:
            painter.drawPixmap(self.topX, self.topY, self.top)


class SpriteImage_PipeExpand(SLib.SpriteImage):
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.spritebox.shown = self.mini = self.big = self.painted = self.typeinfluence = False
        self.hasTop = True
        self.direction = 'U'
        self.colours = ("Green", "Red", "Yellow", "Blue")
        self.topY = self.topX = self.colour = self.extraLength = self.x = self.y = 0
        self.width = self.height = 32
        self.pipeHeight = self.pipeWidth = 120
        self.parent.setZValue(24999)

    #        self.expandable = False
    #        self.moving = False

    @staticmethod
    def loadImages():
        if 'PipeTopGreen' not in ImageCache:
            for colour in ("Green", "Red", "Yellow", "Blue"):
                ImageCache['PipeTop%s' % colour] = SLib.GetImg('pipe_%s_top.png' % colour.lower())
                ImageCache['PipeMiddleV%s' % colour] = SLib.GetImg('pipe_%s_middleV.png' % colour.lower())
                ImageCache['PipeMiddleH%s' % colour] = SLib.GetImg('pipe_%s_middleH.png' % colour.lower())
                ImageCache['PipeBottom%s' % colour] = SLib.GetImg('pipe_%s_bottom.png' % colour.lower())
                ImageCache['PipeLeft%s' % colour] = SLib.GetImg('pipe_%s_left.png' % colour.lower())
                ImageCache['PipeRight%s' % colour] = SLib.GetImg('pipe_%s_right.png' % colour.lower())

                # Paint
                ImageCache['PipePaintedTop%s' % colour] = SLib.GetImg('pipe_painted_%s_top.png' % colour.lower())
                ImageCache['PipePaintedMiddleV%s' % colour] = SLib.GetImg(
                    'pipe_painted_%s_middleV.png' % colour.lower())
                ImageCache['PipePaintedMiddleH%s' % colour] = SLib.GetImg(
                    'pipe_painted_%s_middleH.png' % colour.lower())
                ImageCache['PipePaintedBottom%s' % colour] = SLib.GetImg('pipe_painted_%s_bottom.png' % colour.lower())
                ImageCache['PipePaintedLeft%s' % colour] = SLib.GetImg('pipe_painted_%s_left.png' % colour.lower())
                ImageCache['PipePaintedRight%s' % colour] = SLib.GetImg('pipe_painted_%s_right.png' % colour.lower())

                # BIG
                ImageCache['PipeBigTop%s' % colour] = ImageCache['PipeTop%s' % colour].scaled(240, 240,
                                                                                              QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigMiddleV%s' % colour] = ImageCache['PipeMiddleV%s' % colour].scaled(240, 240)
                ImageCache['PipeBigMiddleH%s' % colour] = ImageCache['PipeMiddleH%s' % colour].scaled(240, 240)
                ImageCache['PipeBigBottom%s' % colour] = ImageCache['PipeBottom%s' % colour].scaled(240, 240,
                                                                                                    QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigLeft%s' % colour] = ImageCache['PipeLeft%s' % colour].scaled(240, 240,
                                                                                                QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigRight%s' % colour] = ImageCache['PipeRight%s' % colour].scaled(240, 240,
                                                                                                  QtCore.Qt.KeepAspectRatio)

                # MINI
                if colour == "Green":
                    ImageCache['MiniPipeTop%s' % colour] = SLib.GetImg('pipe_mini_%s_top.png' % colour.lower())
                    ImageCache['MiniPipeMiddleV%s' % colour] = SLib.GetImg('pipe_mini_%s_middleV.png' % colour.lower())
                    ImageCache['MiniPipeMiddleH%s' % colour] = SLib.GetImg('pipe_mini_%s_middleH.png' % colour.lower())
                    ImageCache['MiniPipeBottom%s' % colour] = SLib.GetImg('pipe_mini_%s_bottom.png' % colour.lower())
                    ImageCache['MiniPipeLeft%s' % colour] = SLib.GetImg('pipe_mini_%s_left.png' % colour.lower())
                    ImageCache['MiniPipeRight%s' % colour] = SLib.GetImg('pipe_mini_%s_right.png' % colour.lower())

    def dataChanged(self):
        super().dataChanged()

        # if self.moving: rawlength = (self.parent.spritedata[4] & 0x0F) + 1
        # else:
        rawlength = (self.parent.spritedata[5] & 0x0F) + 1

        if not self.mini:
            rawtop = (self.parent.spritedata[2] >> 4) & 3

            # if self.moving:
            # rawtop = 0 & 3

            # if self.expandable: rawcolour = (self.parent.spritedata[3]) & 3
            # elif self.moving: rawcolour = (self.parent.spritedata[3]) & 3
            #            else:
            rawcolour = (self.parent.spritedata[3]) & 3

            if self.typeinfluence and rawtop == 0:
                # if self.expandable: rawtype = self.parent.spritedata[4] & 3
                # elif self.moving: rawtype = self.parent.spritedata[5] >> 4
                # else:
                rawtype = self.parent.spritedata[4] & 3
            else:
                rawtype = 0

            if rawtop == 1:
                pipeLength = rawlength + rawtype + self.extraLength + 1
            elif rawtop == 0:
                if rawtype == 0:
                    pipeLength = rawlength + rawtype + self.extraLength + 1
                else:
                    pipeLength = rawlength + rawtype + self.extraLength
            else:
                pipeLength = rawlength + rawtype + self.extraLength

            self.hasTop = (rawtop != 3)
            #            self.big = (rawtype == 3)
            self.colour = self.colours[rawcolour]
        else:
            pipeLength = rawlength
            self.colour = "Green"

        if self.direction in 'LR':  # horizontal
            self.pipeWidth = pipeLength * 60
            self.width = (self.pipeWidth / 3.75)
            if self.big:
                self.middle = ImageCache['PipeBigMiddleH%s' % self.colour]
                self.height = 64
                self.pipeHeight = 240
            elif self.painted:
                self.middle = ImageCache['PipePaintedMiddleH%s' % self.colour]
            elif not self.mini:
                self.middle = ImageCache['PipeMiddleH%s' % self.colour]
            else:
                self.middle = ImageCache['MiniPipeMiddleH%s' % self.colour]
                self.height = 16
                self.pipeHeight = 60

            if self.direction == 'R':  # faces right
                if self.big:
                    self.top = ImageCache['PipeBigRight%s' % self.colour]
                    self.topX = self.pipeWidth - 120
                elif self.painted:
                    self.topX = self.pipeWidth - 60
                    self.top = ImageCache['PipePaintedRight%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeRight%s' % self.colour]
                    self.topX = self.pipeWidth - 60
                else:
                    self.top = ImageCache['MiniPipeRight%s' % self.colour]
                    self.topX = self.pipeWidth - 60
            else:  # faces left
                if self.big:
                    self.top = ImageCache['PipeBigLeft%s' % self.colour]
                elif self.painted:
                    self.top = ImageCache['PipePaintedLeft%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeLeft%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeLeft%s' % self.colour]
                self.xOffset = 16 - self.width

        if self.direction in 'UD':  # vertical
            self.pipeHeight = pipeLength * 60
            self.height = (self.pipeHeight / 3.75)
            if self.big:
                self.middle = ImageCache['PipeBigMiddleV%s' % self.colour]
                self.width = 64
                self.pipeWidth = 240
            elif self.painted:
                self.middle = ImageCache['PipePaintedMiddleV%s' % self.colour]
            elif not self.mini:
                self.middle = ImageCache['PipeMiddleV%s' % self.colour]
            else:
                self.middle = ImageCache['MiniPipeMiddleV%s' % self.colour]
                self.width = 16
                self.pipeWidth = 60

            if self.direction == 'D':  # faces down
                if self.big:
                    self.top = ImageCache['PipeBigBottom%s' % self.colour]
                    self.topY = self.pipeHeight - 120
                elif self.painted:
                    self.top = ImageCache['PipePaintedBottom%s' % self.colour]
                    self.topY = self.pipeHeight - 60
                elif not self.mini:
                    self.top = ImageCache['PipeBottom%s' % self.colour]
                    self.topY = self.pipeHeight - 60
                else:
                    self.top = ImageCache['MiniPipeBottom%s' % self.colour]
                    self.topY = self.pipeHeight - 60
            else:  # faces up
                if self.big:
                    self.top = ImageCache['PipeBigTop%s' % self.colour]
                elif self.painted:
                    self.top = ImageCache['PipePaintedTop%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeTop%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeTop%s' % self.colour]
                self.yOffset = 16 - (self.pipeHeight / 3.75)

    def paint(self, painter):
        super().paint(painter)
        painter.drawTiledPixmap(self.x, self.y, self.pipeWidth, self.pipeHeight, self.middle)
        if self.hasTop:
            painter.drawPixmap(self.topX, self.topY, self.top)


class SpriteImage_StackedSprite(SLib.SpriteImage):
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.spritebox.shown = self.typeinfluence = False
        self.hasTop = True
        self.hasBottom = True
        self.topY = self.topX = self.bottomX = self.bottomY = self.extraLength = self.x = self.y = 0
        #        self.width = self.height = 32
        #        self.pipeHeight = self.pipeWidth = 100
        self.parent.setZValue(24999)


class SpriteImage_Useless(SLib.SpriteImage_Static):  # X
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Useless'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Useless', 'useless.png')


class SpriteImage_Crash(SLib.SpriteImage_Static):  # X
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Crash', 'crash.png')


class SpriteImage_LiquidOrFog(SLib.SpriteImage):  # 88, 89, 90, 92, 198, 201
    def __init__(self, parent):
        super().__init__(parent)

        self.crest = None
        self.mid = None
        self.rise = None
        self.riseCrestless = None

        self.top = 0

        self.drawCrest = False
        self.risingHeight = 0

        self.paintZone = False
        self.paintLoc = False

    def positionChanged(self):
        super().positionChanged()
        self.parent.scene().update()

    def dataChanged(self):
        super().dataChanged()
        self.parent.scene().update()

    def realViewZone(self, painter, zoneRect, viewRect):
        """
        Real view zone painter for liquids/fog
        """
        if not self.paintZone: return

        # (0, 0) is the top-left corner of the zone

        zy, zw, zh = zoneRect.topLeft().y(), zoneRect.width(), zoneRect.height()

        drawRise = self.risingHeight != 0
        drawCrest = self.drawCrest

        # Get positions
        offsetFromTop = (self.top * 3.75) - zy
        if offsetFromTop <= 4:
            offsetFromTop = 4
            drawCrest = False  # off the top of the zone; no crest
        if self.top > (zy + zh) / 3.75:
            # the sprite is below the zone; don't draw anything
            return

        # If all that fits in the zone is some of the crest, determine how much
        if drawCrest:
            crestSizeRemoval = (zy + offsetFromTop + self.crest.height()) - (zy + zh) + 4
            if crestSizeRemoval < 0: crestSizeRemoval = 0
            crestHeight = self.crest.height() - crestSizeRemoval

        # Determine where to put the rise image
        offsetRise = offsetFromTop - (self.risingHeight * 60)
        riseToDraw = self.rise
        if offsetRise < 4:  # close enough to the top zone border
            offsetRise = 4
            riseToDraw = self.riseCrestless
        if not drawCrest:
            riseToDraw = self.riseCrestless

        if drawCrest:
            painter.drawTiledPixmap(4, offsetFromTop, zw - 8, crestHeight, self.crest)
            painter.drawTiledPixmap(4, offsetFromTop + crestHeight, zw - 8, zh - crestHeight - offsetFromTop - 4,
                                    self.mid)
        else:
            painter.drawTiledPixmap(4, offsetFromTop, zw - 8, zh - offsetFromTop - 4, self.mid)
        if drawRise:
            painter.drawTiledPixmap(4, offsetRise, zw - 8, riseToDraw.height(), riseToDraw)


class SpriteImage_Goomba(SLib.SpriteImage_Static):  # 0
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Goomba'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Goomba', 'goomba.png')


class SpriteImage_Paragoomba(SLib.SpriteImage_Static):  # 1
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Paragoomba'],
            (-8, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Paragoomba', 'paragoomba.png')


class SpriteImage_PipePiranhaUp(SLib.SpriteImage_Static):  # 2
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaUp'],
            (0, -32),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaUp', 'pipe_piranha.png')


class SpriteImage_PipePiranhaDown(SLib.SpriteImage_Static):  # 3
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaDown'],
            (0, 32),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaDown', 'pipe_piranha_down.png')


class SpriteImage_PipePiranhaLeft(SLib.SpriteImage_Static):  # 4
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaLeft'],
            (-32, 0),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaLeft', 'pipe_piranha_left.png')


class SpriteImage_PipePiranhaRight(SLib.SpriteImage_Static):  # 5
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaRight'],
            (32, 0),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaRight', 'pipe_piranha_right.png')


class SpriteImage_PipePiranhaUpFire(SLib.SpriteImage_Static):  # 6
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaUpFire'],
            (-6, -32),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaUpFire', 'firetrap_pipe_up.png')


class SpriteImage_PipePiranhaDownFire(SLib.SpriteImage_Static):  # 7
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaDownFire'],
            (-6, 32),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaDownFire', 'firetrap_pipe_down.png')


class SpriteImage_PipePiranhaLeftFire(SLib.SpriteImage_Static):  # 8
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaLeftFire'],
            (-32, -6),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaLeftFire', 'firetrap_pipe_left.png')


class SpriteImage_PipePiranhaRightFire(SLib.SpriteImage_Static):  # 9
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaRightFire'],
            (32, -6),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaRightFire', 'firetrap_pipe_right.png')


class SpriteImage_GroundPiranha(SLib.SpriteImage_StaticMultiple):  # 14
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.xOffset = -6.4

    @staticmethod
    def loadImages():
        if 'GroundPiranha' in ImageCache: return
        GP = SLib.GetImg('grounded_piranha.png', True)
        ImageCache['GroundPiranha'] = QtGui.QPixmap.fromImage(GP)
        ImageCache['GroundPiranhaU'] = QtGui.QPixmap.fromImage(GP.mirrored(False, True))

    def dataChanged(self):

        upsideDown = self.parent.spritedata[5] & 0xF
        if upsideDown != 8:
            self.yOffset = 28 / 60 * 16
            self.image = ImageCache['GroundPiranha']
        else:
            self.yOffset = 109 / 60 * 16
            self.image = ImageCache['GroundPiranhaU']

        super().dataChanged()


class SpriteImage_GroundVenustrap(SLib.SpriteImage_StaticMultiple):  # 15, 16
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.xOffset = 14 / 60 * 16

    @staticmethod
    def loadImages():
        if 'GroundVenustrap' in ImageCache: return
        GF = SLib.GetImg('grounded_venus_trap.png', True)
        ImageCache['GroundVenustrap'] = QtGui.QPixmap.fromImage(GF)
        ImageCache['GroundVenustrapU'] = QtGui.QPixmap.fromImage(GF.mirrored(False, True))

    def dataChanged(self):

        upsideDown = self.parent.spritedata[5] & 0xF
        if upsideDown != 8:
            self.yOffset = -34 / 60 * 16
            self.image = ImageCache['GroundVenustrap']
        else:
            self.yOffset = 30.4
            self.image = ImageCache['GroundVenustrapU']

        super().dataChanged()


class SpriteImage_BigGroundPiranha(SLib.SpriteImage_StaticMultiple):  # 17
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.xOffset = -143 / 60 * 16

    @staticmethod
    def loadImages():
        if 'BigGroundPiranha' in ImageCache: return
        BGP = SLib.GetImg('big_grounded_piranha.png', True)
        ImageCache['BigGroundPiranha'] = QtGui.QPixmap.fromImage(BGP)
        ImageCache['BigGroundPiranhaU'] = QtGui.QPixmap.fromImage(BGP.mirrored(False, True))

    def dataChanged(self):

        upsideDown = self.parent.spritedata[5] & 0xF
        if upsideDown != 8:
            self.yOffset = 127 / 60 * 16
            self.image = ImageCache['BigGroundPiranha']
        else:
            self.yOffset = 289 / 60 * 16
            self.image = ImageCache['BigGroundPiranhaU']

        super().dataChanged()


class SpriteImage_BigGroundVenustrap(SLib.SpriteImage_StaticMultiple):  # 18
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.xOffset = -61 / 60 * 16

    @staticmethod
    def loadImages():
        if 'BigGroundVenustrap' in ImageCache: return
        BGF = SLib.GetImg('big_grounded_venus_trap.png', True)
        ImageCache['BigGroundVenustrap'] = QtGui.QPixmap.fromImage(BGF)
        ImageCache['BigGroundVenustrapU'] = QtGui.QPixmap.fromImage(BGF.mirrored(False, True))

    def dataChanged(self):

        upsideDown = self.parent.spritedata[5] & 0xF
        if upsideDown != 8:
            self.yOffset = -2.4
            self.image = ImageCache['BigGroundVenustrap']
        else:
            self.yOffset = 76.8
            self.image = ImageCache['BigGroundVenustrapU']

        super().dataChanged()


class SpriteImage_KoopaTroopa(SLib.SpriteImage_StaticMultiple):  # 19
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['KoopaG'],
            (-8, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('KoopaShellG', 'koopa_shell_green.png')
        SLib.loadIfNotInImageCache('KoopaShellR', 'koopa_shell_red.png')
        SLib.loadIfNotInImageCache('KoopaG', 'koopa_green.png')
        SLib.loadIfNotInImageCache('KoopaR', 'koopa_red.png')

    def dataChanged(self):
        shellcolour = self.parent.spritedata[5] & 1
        inshell = (self.parent.spritedata[5] >> 4) & 1

        if inshell:
            self.offset = (-0.5 * (66 / 60 - 1) * 16, 0)
            self.image = ImageCache['KoopaShellR' if shellcolour else 'KoopaShellG']
        else:
            self.offset = (-16, -16)
            self.image = ImageCache['KoopaR' if shellcolour else 'KoopaG']

        super().dataChanged()


class SpriteImage_KoopaParatroopa(SLib.SpriteImage_StaticMultiple):  # 20
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['KoopaGWings'],
            (-16, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('KoopaGWings', 'koopa_wings_g.png')
        SLib.loadIfNotInImageCache('KoopaRWings', 'koopa_wings_r.png')

    def dataChanged(self):
        shellcolour = self.parent.spritedata[5] & 1

        if shellcolour == 0:
            self.image = ImageCache['KoopaGWings']
        else:
            self.image = ImageCache['KoopaRWings']

        super().dataChanged()


class SpriteImage_BuzzyBeetle(SLib.SpriteImage_StaticMultiple):  # 22
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.directions = {
            0: 'L',
            1: 'R',
        }

        self.types = {
            0: 'U',
            1: 'D',
            2: 'US',
            3: 'DS',
        }

    @staticmethod
    def loadImages():
        if 'BuzzyUL' not in ImageCache:
            ImageCache['BuzzyUL'] = QtGui.QPixmap.fromImage(SLib.GetImg('buzzy_beetle.png', True))
            ImageCache['BuzzyUR'] = QtGui.QPixmap.fromImage(SLib.GetImg('buzzy_beetle.png', True).mirrored(True, False))
            ImageCache['BuzzyDL'] = QtGui.QPixmap.fromImage(SLib.GetImg('buzzy_beetle_down.png', True))
            ImageCache['BuzzyDR'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('buzzy_beetle_down.png', True).mirrored(True, False))
            ImageCache['BuzzyUSL'] = QtGui.QPixmap.fromImage(SLib.GetImg('buzzy_beetle_shell.png', True))
            ImageCache['BuzzyUSR'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('buzzy_beetle_shell.png', True).mirrored(True, False))
            ImageCache['BuzzyDSL'] = QtGui.QPixmap.fromImage(SLib.GetImg('buzzy_beetle_shell_down.png', True))
            ImageCache['BuzzyDSR'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('buzzy_beetle_shell_down.png', True).mirrored(True, False))

    def dataChanged(self):

        direction = self.parent.spritedata[4] & 0xF
        type_ = self.parent.spritedata[5] & 0xF

        if direction > 1:
            direction = 0

        if type_ > 3:
            type_ = 0

        self.image = ImageCache['Buzzy%s%s' % (self.types[type_], self.directions[direction])]
        self.xOffset = -0.5 * (self.image.width() / 60 - 1) * 16

        super().dataChanged()


class SpriteImage_ArrowSignboard(SLib.SpriteImage_StaticMultiple):  # 32
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ArrowSign0_0'],
        )

        self.types = {0: "", 1: "_snow", 3: "_rock", 4: "_spooky"}

    @staticmethod
    def loadImages():
        types = {0: "", 1: "_snow", 3: "_rock", 4: "_spooky"}
        for i in types:
            for j in range(8):
                SLib.loadIfNotInImageCache('ArrowSign{0}_{1}'.format(i, j),
                                           'arrow_signboard{0}_{1}.png'.format(types[i], j))

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 0xF
        if direction > 7: direction -= 8
        type_ = self.parent.spritedata[3] >> 4

        if type_ in self.types:
            self.image = ImageCache['ArrowSign{0}_{1}'.format(type_, direction)]
        else:
            self.image = ImageCache['ArrowSign{0}_{1}'.format(0, direction)]

        if type_ == 3:
            self.offset = (-9.6, -(53 / 60 * 16))
        else:
            self.offset = (-8, -17.6)

        super().dataChanged()


class SpriteImage_Spiny(SLib.SpriteImage_StaticMultiple):  # 23
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.yOffset = -1

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Spiny', 'spiny_norm.png')
        SLib.loadIfNotInImageCache('SpinyBall', 'spiny_ball.png')
        SLib.loadIfNotInImageCache('SpinyShell', 'spiny_shell.png')
        SLib.loadIfNotInImageCache('SpinyShellU', 'spiny_shell_u.png')

    def dataChanged(self):

        spawntype = self.parent.spritedata[5]

        if spawntype == 0:
            self.image = ImageCache['Spiny']
        elif spawntype == 1:
            self.image = ImageCache['SpinyBall']
        elif spawntype == 2:
            self.image = ImageCache['SpinyShell']
        elif spawntype == 3:
            self.image = ImageCache['SpinyShellU']
        else:
            self.image = ImageCache['Spiny']

        super().dataChanged()


class SpriteImage_MidwayFlag(SLib.SpriteImage_Static):  # 25
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MidwayFlag'],
        )

        self.yOffset = -48

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MidwayFlag', 'midway_flag.png')


class SpriteImage_LimitU(SLib.SpriteImage_StaticMultiple):  # 29
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LimitUR', 'limit_u_r.png')
        SLib.loadIfNotInImageCache('LimitUL', 'limit_u_l.png')

    def dataChanged(self):

        direction = self.parent.spritedata[2]

        if direction == 0:
            self.image = ImageCache['LimitUR']
        elif direction == 16 or direction == 17 or direction == 18 or direction == 19 or direction == 20 or direction == 21 or direction == 22 or direction == 23 or direction == 24 or direction == 25 or direction == 26 or direction == 27 or direction == 28 or direction == 29 or direction == 30 or direction == 31:
            self.image = ImageCache['LimitUL']
        else:
            self.image = ImageCache['LimitUR']

        super().dataChanged()


class SpriteImage_LimitD(SLib.SpriteImage_StaticMultiple):  # 30
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LimitDR', 'limit_d_r.png')
        SLib.loadIfNotInImageCache('LimitDL', 'limit_d_l.png')

    def dataChanged(self):

        direction = self.parent.spritedata[2]

        if direction == 0:
            self.image = ImageCache['LimitDR']
        elif direction == 16 or direction == 17 or direction == 18 or direction == 19 or direction == 20 or direction == 21 or direction == 22 or direction == 23 or direction == 24 or direction == 25 or direction == 26 or direction == 27 or direction == 28 or direction == 29 or direction == 30 or direction == 31:
            self.image = ImageCache['LimitDL']
        else:
            self.image = ImageCache['LimitDR']

        super().dataChanged()


class SpriteImage_Flagpole(SLib.SpriteImage_StaticMultiple):  # 31
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -48
        self.yOffset = -160

        self.parent.setZValue(24999)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FlagReg', 'flag_reg.png')
        SLib.loadIfNotInImageCache('FlagSnow', 'flag_snow.png')
        SLib.loadIfNotInImageCache('FlagNo', 'flag_no.png')
        SLib.loadIfNotInImageCache('FlagSecReg', 'flag_sec_reg.png')
        SLib.loadIfNotInImageCache('FlagSecSnow', 'flag_sec_snow.png')
        SLib.loadIfNotInImageCache('FlagSecNo', 'flag_sec_no.png')

    def dataChanged(self):

        secret = self.parent.spritedata[2]
        snowno = self.parent.spritedata[5]

        secretb = False
        nob = False
        snowb = False

        if snowno == 16:
            nob = True
        else:
            nob = False
        if snowno == 1:
            snowb = True
        else:
            snowb = False
        if secret == 16:
            secretb = True
        else:
            secretb = False
        if snowno == 17:
            nob = True
            snowb = True

        # print("Snow: "+str(snowb) + "   Secret: "+str(secretb) + "   No: "+str(nob) + "     SecretN:" + str(secret)+ "     SnowNo:"+str(snowno))
        # That was a coding challenge

        if nob and not secretb:
            self.image = ImageCache['FlagNo']
        elif nob and secretb:
            self.image = ImageCache['FlagSecNo']
        elif not nob and not secretb and snowb:
            self.image = ImageCache['FlagSnow']
        elif not nob and secretb and not snowb:
            self.image = ImageCache['FlagSecReg']
        elif not nob and secretb and snowb:
            self.image = ImageCache['FlagSecSnow']
        elif not nob and not secretb and not snowb:
            self.image = ImageCache['FlagReg']
        else:
            self.image = ImageCache['FlagReg']

        super().dataChanged()


class SpriteImage_ZoneTrigger(SLib.SpriteImage_Static):  # 36
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ZoneTrigger'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ZoneTrigger', 'zone_trigger.png')


class SpriteImage_LocationTrigger(SLib.SpriteImage_Static):  # 41
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['LocationTrigger'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LocationTrigger', 'location_trigger.png')


class SpriteImage_RedRing(SLib.SpriteImage_Static):  # 44
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['RedRing'],
        )

        self.yOffset = -14
        self.xOffset = -7

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RedRing', 'red_ring.png')


class SpriteImage_StarCoin(SLib.SpriteImage_Static):  # 45
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['StarCoin'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StarCoin', 'star_coin.png')


class SpriteImage_LineControlledStarCoin(SLib.SpriteImage_Static):  # 46
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['LineStarCoin'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LineStarCoin', 'star_coin.png')


class SpriteImage_BoltControlledStarCoin(SLib.SpriteImage_Static):  # 47
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BoltStarCoin'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoltStarCoin', 'star_coin.png')


class SpriteImage_MvmtRotControlledStarCoin(SLib.SpriteImage_Static):  # 48
    # Movement Controlled, Rotation Controlled Star Coin
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MRStarCoin'],
        )

        self.xOffset = -16

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MRStarCoin', 'star_coin.png')


class SpriteImage_RedCoin(SLib.SpriteImage_Static):  # 49
    # Red Coin
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['RedCoin'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RedCoin', 'red_coin.png')


class SpriteImage_GreenCoin(SLib.SpriteImage_Static):  # 50
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GreenCoin'],
        )

        self.xOffset = -7
        self.yOffset = -2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GreenCoin', 'green_coins.png')


class SpriteImage_MontyMole(SLib.SpriteImage_Static):  # 51
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MontyMole'],
        )

        self.xOffset = -6
        self.yOffset = -2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MontyMole', 'monty_mole.png')


class SpriteImage_YoshiBerry(SLib.SpriteImage_Static):  # 54
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['YoshiBerry'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('YoshiBerry', 'yoshi_berry.png')


class SpriteImage_QBlock(SLib.SpriteImage_Static):  # 59
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    def dataChanged(self):
        super().dataChanged()

        self.contents = self.parent.spritedata[9] & 0xF
        self.acorn = (self.parent.spritedata[6] >> 4) & 1

        items = {0: 0x800 + 160, 1: 49, 2: 32, 3: 32, 4: 37, 5: 38, 6: 36, 7: 33, 8: 34, 9: 41, 12: 35, 13: 42, 15: 39}

        self.dopaint = True
        self.image = None

        if self.acorn:
            self.tilenum = 40
        elif self.contents in items:
            self.tilenum = items[self.contents]
        else:
            self.dopaint = False
            if self.contents == 10:
                self.image = ImageCache['Q10']
            elif self.contents == 11:
                self.image = ImageCache['QKinokoUP']
            elif self.contents == 14:
                self.image = ImageCache['QKinoko']
            else:
                self.dopaint = True
                self.tilenum = 49

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Q10', 'block_q_10.png')
        SLib.loadIfNotInImageCache('QKinokoUP', 'block_q_kinoko_up.png')
        SLib.loadIfNotInImageCache('QKinoko', 'block_q_kinoko_coin.png')

    def paint(self, painter):
        super().paint(painter)

        if self.dopaint:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.drawPixmap(self.yOffset, self.xOffset, 60, 60, SLib.Tiles[self.tilenum].main)


class SpriteImage_BrickBlock(SLib.SpriteImage_Static):  # 60
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    def dataChanged(self):
        super().dataChanged()

        self.contents = self.parent.spritedata[9] & 0xF
        self.acorn = (self.parent.spritedata[6] >> 4) & 1

        items = {0: 48, 1: 26, 2: 16, 3: 16, 4: 21, 5: 22, 6: 20, 7: 17, 9: 25, 10: 27, 11: 18, 12: 19, 15: 23}

        self.dopaint = True
        self.image = None

        if self.acorn:
            self.tilenum = 24
        elif self.contents in items:
            self.tilenum = items[self.contents]
        else:
            self.dopaint = False
            if self.contents == 8:
                self.image = ImageCache['BCstar']
            elif self.contents == 13:
                self.image = ImageCache['BSpring']
            elif self.contents == 14:
                self.image = ImageCache['BKinoko']
            else:
                self.dopaint = True
                self.tilenum = 49

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BCstar', 'block_c_star.png')
        SLib.loadIfNotInImageCache('BSpring', 'block_spring.png')
        SLib.loadIfNotInImageCache('BKinoko', 'block_kinoko_coin.png')

    def paint(self, painter):
        super().paint(painter)

        if self.dopaint:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.drawPixmap(self.yOffset, self.xOffset, 60, 60, SLib.Tiles[self.tilenum].main)


class SpriteImage_InvisiBlock(SLib.SpriteImage_Static):  # 61
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    def dataChanged(self):
        super().dataChanged()

        self.contents = self.parent.spritedata[9] & 0xF
        self.acorn = (self.parent.spritedata[6] >> 4) & 1

        items = {1: 3, 2: 4, 3: 4, 4: 9, 5: 10, 6: 8, 7: 5, 11: 6, 12: 7, 15: 13}

        self.dopaint = True
        self.image = None

        if self.acorn:
            self.tilenum = 29
        elif self.contents in items:
            self.tilenum = items[self.contents]
        else:
            self.dopaint = False
            if self.contents == 8:
                self.image = ImageCache['InvisiCstar']
            elif self.contents == 9:
                self.image = ImageCache['InvisiYoshi']
            elif self.contents == 10:
                self.image = ImageCache['Invisi10']
            elif self.contents == 13:
                self.image = ImageCache['InvisiSpring']
            elif self.contents == 14:
                self.image = ImageCache['InvisiKinoko']
            else:
                self.image = ImageCache['InvisiBlock']

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('InvisiCstar', 'block_i_c_star.png')
        SLib.loadIfNotInImageCache('InvisiYoshi', 'block_i_yoshi.png')
        SLib.loadIfNotInImageCache('Invisi10', 'block_i_10.png')
        SLib.loadIfNotInImageCache('InvisiSpring', 'block_i_spring.png')
        SLib.loadIfNotInImageCache('InvisiKinoko', 'block_i_kinoko_coin.png')
        SLib.loadIfNotInImageCache('InvisiBlock', 'block_invisible.png')

    def paint(self, painter):
        super().paint(painter)

        if self.dopaint:
            painter.setRenderHint(QtGui.QPainter.Antialiasing)
            painter.drawPixmap(0, 0, 60, 60, SLib.Tiles[self.tilenum].main)


class SpriteImage_StalkingPiranha(SLib.SpriteImage_Static):  # 63
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['StalkingPiranha'],
        )

        self.yOffset = -17
        # self.xOffset = -10

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StalkingPiranha', 'stalking_piranha.png')


class SpriteImage_WaterPlant(SLib.SpriteImage_Static):  # 64
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['WaterPlant'],
        )

        self.yOffset = -120
        self.xOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WaterPlant', 'water_plant.png')


class SpriteImage_Coin(SLib.SpriteImage_Static):  # 65
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.parent.setZValue(20000)

    def paint(self, painter):
        super().paint(painter)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawPixmap(self.yOffset, self.xOffset, 60, 60, SLib.Tiles[30].main)


class SpriteImage_Swooper(SLib.SpriteImage_Static):  # 67
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Swooper'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Swooper', 'swooper.png')


class SpriteImage_ControllerSwaying(SLib.SpriteImage_Static):  # 68
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerSwaying'],
        )
        self.parent.setZValue(500000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerSwaying', 'controller_swaying.png')

    def dataChanged(self):
        #        rotation = self.parent.spritedata[4]

        """
        if rotation == 1: Rotations[rotid] = 22.5
        elif rotation == 2: Rotations[rotid] = 45
        elif rotation == 3: Rotations[rotid] = 67.5
        elif rotation == 4: Rotations[rotid] = 90
        elif rotation == 5: Rotations[rotid] = 112.5
        elif rotation == 6: Rotations[rotid] = 135
        elif rotation == 7: Rotations[rotid] = 157.5
        elif rotation == 8: Rotations[rotid] = 180
        elif rotation == 9: Rotations[rotid] = 22.5 + 180
        elif rotation == 10: Rotations[rotid] = 45 + 180
        elif rotation == 11: Rotations[rotid] = 67.5 + 180
        elif rotation == 12: Rotations[rotid] = 90 + 180
        elif rotation == 13: Rotations[rotid] = 112.5 + 180
        elif rotation == 14: Rotations[rotid] = 135 + 180
        elif rotation == 15: Rotations[rotid] = 157.5 + 180
        else: Rotations[rotid] = 0
        """

        super().dataChanged()


# func = SpriteImage_StoneEye(SLib.SpriteImage_StaticMultiple)
#        func.translateImage()



class SpriteImage_ControllerSpinning(SLib.SpriteImage_Static):  # 69, 484
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerSpinning'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerSpinning', 'controller_spinning.png')


class SpriteImage_TwoWay(SLib.SpriteImage_StaticMultiple):  # 70
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TwoWayHor', 'twoway_hor.png')
        SLib.loadIfNotInImageCache('TwoWayVer', 'twoway_ver.png')

    def dataChanged(self):

        direction = self.parent.spritedata[3]

        if direction == 0:
            self.image = ImageCache['TwoWayHor']
        elif direction == 1:
            self.image = ImageCache['TwoWayHor']
        elif direction == 2:
            self.image = ImageCache['TwoWayVer']
        elif direction == 3:
            self.image = ImageCache['TwoWayVer']
        else:
            self.image = ImageCache['TwoWayHor']

        super().dataChanged()


class SpriteImage_MovingLandBlock(SLib.SpriteImage):  # 72
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        # self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        ImageCache['MovLTopL'] = SLib.GetImg('mov_land_top_l.png')
        ImageCache['MovLTopM'] = SLib.GetImg('mov_land_top_m.png')
        ImageCache['MovLTopR'] = SLib.GetImg('mov_land_top_r.png')
        ImageCache['MovLMiddleL'] = SLib.GetImg('mov_land_middle_l.png')
        ImageCache['MovLMiddleM'] = SLib.GetImg('mov_land_middle_m.png')
        ImageCache['MovLMiddleR'] = SLib.GetImg('mov_land_middle_r.png')
        ImageCache['MovLBottomL'] = SLib.GetImg('mov_land_bottom_l.png')
        ImageCache['MovLBottomM'] = SLib.GetImg('mov_land_bottom_m.png')
        ImageCache['MovLBottomR'] = SLib.GetImg('mov_land_bottom_r.png')

    def dataChanged(self):
        super().dataChanged()

        self.width = (self.parent.spritedata[8] & 0xF) * 16
        self.height = (self.parent.spritedata[9] & 0xF) * 16
        if self.width / 16 == 0: self.width = 1
        if self.height / 16 == 0: self.height = 1

    def paint(self, painter):
        super().paint(painter)

        # Time to code this lazily.

        # Top of sprite.
        if self.width / 16 == 0:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopM'])
        elif self.width / 16 == 1:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopM'])
        elif self.width / 16 == 2:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopL'])
            painter.drawPixmap(60, 0, 60, 60, ImageCache['MovLTopR'])
        elif self.width / 16 == 3:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopL'
            ])
            painter.drawPixmap(60, 0, 60, 60, ImageCache['MovLTopM'])
            painter.drawPixmap(120, 0, 60, 60, ImageCache['MovLTopR'])
        else:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopL'
            ])
            painter.drawTiledPixmap(60, 0, (self.width / 16 - 2) * 60, 60, ImageCache['MovLTopM'])
            painter.drawPixmap(60 + ((self.width / 16 - 2) * 60), 0, 60, 60, ImageCache['MovLTopR'])

        # Bottom
        if self.height / 16 > 1:
            if self.width / 16 == 0:
                painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLBottomM'])
            elif self.width / 16 == 1:
                painter.drawPixmap(0, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovLBottomM'])
            elif self.width / 16 == 2:
                painter.drawPixmap(0, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovLBottomL'])
                painter.drawPixmap(60, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovLBottomR'])
            elif self.width / 16 == 3:
                painter.drawPixmap(0, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovLBottomL'
                ])
                painter.drawPixmap(60, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovLBottomM'])
                painter.drawPixmap(120, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovLBottomR'])
            else:
                painter.drawPixmap(0, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovLBottomL'
                ])
                painter.drawTiledPixmap(60, (self.height / 16) * 60 - 60, (self.width / 16 - 2) * 60, 60,
                                        ImageCache['MovLBottomM'])
                painter.drawPixmap(60 + ((self.width / 16 - 2) * 60), (self.height / 16) * 60 - 60, 60, 60,
                                   ImageCache['MovLBottomR'])

        # Left
        if self.height / 16 == 3:
            painter.drawPixmap(0, 60, 60, 60, ImageCache['MovLMiddleL'])
        elif self.height / 16 > 3:
            painter.drawPixmap(0, 60, 60, 60, ImageCache['MovLMiddleL'])
            painter.drawTiledPixmap(0, 120, 60, (self.height / 16 - 3) * 60, ImageCache['MovLMiddleL'])

        # Right
        if self.height / 16 == 3:
            painter.drawPixmap((self.width / 16 * 60) - 60, 60, 60, 60, ImageCache['MovLMiddleR'])
        elif self.height / 16 > 3:
            painter.drawPixmap((self.width / 16 * 60) - 60, 60, 60, 60, ImageCache['MovLMiddleR'])
            painter.drawTiledPixmap((self.width / 16 * 60) - 60, 120, 60, (self.height / 16 - 3) * 60,
                                    ImageCache['MovLMiddleR'])

        # Middle
        if self.width / 16 > 2:
            if self.height / 16 > 2:
                painter.drawTiledPixmap(60, 60, ((self.width / 16) - 2) * 60, ((self.height / 16) - 2) * 60,
                                        ImageCache['MovLMiddleM'])

        # 1 Glitch
        if self.width / 16 < 2:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopM'])
            painter.drawTiledPixmap(0, 60, 60, ((self.height / 16) - 2) * 60, ImageCache['MovLMiddleM'])
            if self.height > 1:
                painter.drawPixmap(0, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovLBottomM'])
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopM'])


class SpriteImage_CoinSpawner(SLib.SpriteImage_Liquid):  # 73
    def __init__(self, parent):
        super().__init__(parent, 3.75, ImageCache['CoinSpawner'])
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def dataChanged(self):
        super().dataChanged()

        nybbleHeight = self.parent.spritedata[7]
        height = 3

        if nybbleHeight == 0 or nybbleHeight == 16 or nybbleHeight == 32 or nybbleHeight == 48 or nybbleHeight == 64 or nybbleHeight == 80 or nybbleHeight == 96 or nybbleHeight == 112 or nybbleHeight == 128 or nybbleHeight == 144 or nybbleHeight == 160 or nybbleHeight == 176 or nybbleHeight == 192 or nybbleHeight == 208 or nybbleHeight == 224 or nybbleHeight == 240:
            height = 3
        elif nybbleHeight == 1 or nybbleHeight == 17 or nybbleHeight == 33 or nybbleHeight == 49 or nybbleHeight == 65 or nybbleHeight == 86 or nybbleHeight == 97 or nybbleHeight == 113 or nybbleHeight == 129 or nybbleHeight == 145 or nybbleHeight == 161 or nybbleHeight == 177 or nybbleHeight == 193 or nybbleHeight == 209 or nybbleHeight == 225 or nybbleHeight == 241:
            height = 6
        elif nybbleHeight == 2 or nybbleHeight == 18 or nybbleHeight == 34 or nybbleHeight == 50 or nybbleHeight == 66 or nybbleHeight == 82 or nybbleHeight == 98 or nybbleHeight == 114 or nybbleHeight == 129 or nybbleHeight == 146 or nybbleHeight == 162 or nybbleHeight == 178 or nybbleHeight == 194 or nybbleHeight == 210 or nybbleHeight == 226 or nybbleHeight == 242:
            height = 7
        else:
            height = 3

        self.yOffset = -16 * height

        self.aux[0].setSize(60, height * 60)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CoinSpawner', 'coin_spawner.png')


class SpriteImage_HuckitCrab(SLib.SpriteImage_Static):  # 74
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['HuckitCrab'],
        )

        self.yOffset = -4.5  # close enough, it can't be a whole number
        self.xOffset = -10

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('HuckitCrab', 'huckit_crab.png')


class SpriteImage_BroIce(SLib.SpriteImage_Static):  # 75
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BroIce'],
        )

        self.yOffset = -16
        self.xOffset = -32

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BroIce', 'bro_ice.png')


class SpriteImage_BroHammer(SLib.SpriteImage_Static):  # 76
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BroHammer'],
        )

        self.yOffset = -16
        self.xOffset = -8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BroHammer', 'bro_hammer.png')


class SpriteImage_BroBoomerang(SLib.SpriteImage_Static):  # 78
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BroBoomerang'],
        )

        self.yOffset = -16
        self.xOffset = -32

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BroBoomerang', 'bro_boomerang.png')


class SpriteImage_BroFire(SLib.SpriteImage_Static):  # 79
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BroFire'],
        )

        self.yOffset = -16
        self.xOffset = -32

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BroFire', 'bro_fire.png')


class SpriteImage_MovingCoin(SLib.SpriteImage_Static):  # 87
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MovCoin'],
        )
        self.parent.setZValue(20000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovCoin', 'mov_coin.png')


class SpriteImage_Water(SpriteImage_LiquidOrFog):  # 88
    def __init__(self, parent):
        super().__init__(parent)

        self.crest = ImageCache['LiquidWaterCrest']
        self.mid = ImageCache['LiquidWater']
        self.rise = ImageCache['LiquidWaterRiseCrest']
        self.riseCrestless = ImageCache['LiquidWaterRise']

    @staticmethod
    def loadImages():
        if 'LiquidWater' in ImageCache: return
        ImageCache['LiquidWater'] = SLib.GetImg('liquid_water.png')
        ImageCache['LiquidWaterCrest'] = SLib.GetImg('liquid_water_crest.png')
        ImageCache['LiquidWaterRise'] = SLib.GetImg('liquid_water_rise.png')
        ImageCache['LiquidWaterRiseCrest'] = SLib.GetImg('liquid_water_rise_crest.png')

    def dataChanged(self):
        super().dataChanged()

        self.paintZone = self.parent.spritedata[5] == 0

        self.parent.scene().update()

    def realViewZone(self, painter, zoneRect, viewRect):

        self.paintZone = self.parent.spritedata[5] == 0
        self.top = self.parent.objy
        self.drawCrest = self.parent.spritedata[4] & 15 < 8
        self.risingHeight = (self.parent.spritedata[3] & 0xF) << 4
        self.risingHeight |= self.parent.spritedata[4] >> 4

        if self.parent.spritedata[2] & 15 > 7:  # falling
            self.risingHeight = -self.risingHeight

        super().realViewZone(painter, zoneRect, viewRect)


class SpriteImage_Lava(SpriteImage_LiquidOrFog):  # 89
    def __init__(self, parent):
        super().__init__(parent)

        self.crest = ImageCache['LiquidLavaCrest']
        self.mid = ImageCache['LiquidLava']
        self.rise = ImageCache['LiquidLavaRiseCrest']
        self.riseCrestless = ImageCache['LiquidLavaRise']

    @staticmethod
    def loadImages():
        if 'LiquidLava' in ImageCache: return
        ImageCache['LiquidLava'] = SLib.GetImg('liquid_lava.png')
        ImageCache['LiquidLavaCrest'] = SLib.GetImg('liquid_lava_crest.png')
        ImageCache['LiquidLavaRise'] = SLib.GetImg('liquid_lava_rise.png')
        ImageCache['LiquidLavaRiseCrest'] = SLib.GetImg('liquid_lava_rise_crest.png')

    def dataChanged(self):
        super().dataChanged()

        self.paintZone = self.parent.spritedata[5] == 0

        self.parent.scene().update()

    def realViewZone(self, painter, zoneRect, viewRect):

        self.paintZone = self.parent.spritedata[5] == 0
        self.top = self.parent.objy
        self.drawCrest = self.parent.spritedata[4] & 15 < 8
        self.risingHeight = (self.parent.spritedata[3] & 0xF) << 4
        self.risingHeight |= self.parent.spritedata[4] >> 4

        if self.parent.spritedata[2] & 15 > 7:  # falling
            self.risingHeight = -self.risingHeight

        super().realViewZone(painter, zoneRect, viewRect)


class SpriteImage_Poison(SpriteImage_LiquidOrFog):  # 90
    def __init__(self, parent):
        super().__init__(parent)

        self.crest = ImageCache['LiquidPoisonCrest']
        self.mid = ImageCache['LiquidPoison']
        self.rise = ImageCache['LiquidPoisonRiseCrest']
        self.riseCrestless = ImageCache['LiquidPoisonRise']

    @staticmethod
    def loadImages():
        if 'LiquidPoison' in ImageCache: return
        ImageCache['LiquidPoison'] = SLib.GetImg('liquid_poison.png')
        ImageCache['LiquidPoisonCrest'] = SLib.GetImg('liquid_poison_crest.png')
        ImageCache['LiquidPoisonRise'] = SLib.GetImg('liquid_poison_rise.png')
        ImageCache['LiquidPoisonRiseCrest'] = SLib.GetImg('liquid_poison_rise_crest.png')

    def dataChanged(self):
        super().dataChanged()

        self.paintZone = self.parent.spritedata[5] == 0

        self.parent.scene().update()

    def realViewZone(self, painter, zoneRect, viewRect):

        self.paintZone = self.parent.spritedata[5] == 0
        self.top = self.parent.objy
        self.drawCrest = self.parent.spritedata[4] & 15 < 8
        self.risingHeight = (self.parent.spritedata[3] & 0xF) << 4
        self.risingHeight |= self.parent.spritedata[4] >> 4

        if self.parent.spritedata[2] & 15 > 7:  # falling
            self.risingHeight = -self.risingHeight

        super().realViewZone(painter, zoneRect, viewRect)


class SpriteImage_Quicksand(SLib.SpriteImage_Static):  # 91
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Quicksand'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Quicksand', 'quicksand.png')


class SpriteImage_Fog(SpriteImage_LiquidOrFog):  # 92
    def __init__(self, parent):
        super().__init__(parent)
        self.mid = ImageCache['Fog']

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Fog', 'fog.png')

    def dataChanged(self):
        super().dataChanged()

        self.paintZone = self.parent.spritedata[5] == 0

        self.parent.scene().update()

    def realViewZone(self, painter, zoneRect, viewRect):
        self.paintZone = self.parent.spritedata[5] == 0

        self.top = self.parent.objy

        super().realViewZone(painter, zoneRect, viewRect)


class SpriteImage_BouncyCloud(SLib.SpriteImage_StaticMultiple):  # 94
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BouncyCloudS'],
        )
        self.xOffset = -1.6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BouncyCloudS', 'bouncy_cloud_small.png')
        SLib.loadIfNotInImageCache('BouncyCloudL', 'bouncy_cloud_large.png')

    def dataChanged(self):
        size = self.parent.spritedata[8] & 0xF

        if size == 1:
            self.yOffset = -3.47
            self.image = ImageCache['BouncyCloudL']

        else:
            self.yOffset = -2.67
            self.image = ImageCache['BouncyCloudS']

        super().dataChanged()


class SpriteImage_Lamp(SLib.SpriteImage_StaticMultiple):  # 96
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.offset = (-32, -32)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Lamp', 'lamp.png')
        SLib.loadIfNotInImageCache('Candle', 'candle.png')

    def dataChanged(self):
        style = self.parent.spritedata[5] & 3
        if style > 1: style -= 2
        self.image = ImageCache['Candle' if style == 1 else 'Lamp']

        super().dataChanged()


class SpriteImage_BackCenter(SLib.SpriteImage_Static):  # 97
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BackCenter'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BackCenter', 'back_center.png')


class SpriteImage_PipeEnemyGenerator(SLib.SpriteImage):  # 98
    def __init__(self, parent):
        super().__init__(parent, 3.75)

    def dataChanged(self):
        super().dataChanged()

        self.spritebox.size = (16, 16)
        direction = (self.parent.spritedata[5] & 0xF) % 4
        if direction in (0, 1):  # vertical pipe
            self.spritebox.size = (32, 16)
        elif direction in (2, 3):  # horizontal pipe
            self.spritebox.size = (16, 32)

        self.yOffset = 0
        if direction in (2, 3):
            self.yOffset = -16


class SpriteImage_CheepCheep(SLib.SpriteImage_Static):  # 101
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['CheepCheep'],
            (-1, -2),
        )
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def dataChanged(self):
        super().dataChanged()

        nybbleWidth = self.parent.spritedata[3] & 0xF

        width = nybbleWidth * 60 + 120

        offsetX = -(nybbleWidth * 60 + 60)

        self.aux[0].setSize(width, 60, offsetX, 0)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CheepCheep', 'cheep_cheep.png')


class SpriteImage_QuestionSwitch(SLib.SpriteImage_Static):  # 104
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['QSwitch'],
        )

    @staticmethod
    def loadImages():
        if 'QSwitch' not in ImageCache:
            # we need to cache 2 things, the regular switch, and the upside down one
            image = SLib.GetImg('q_switch.png', True)
            # now we set up a transform to turn the switch upside down
            transform180 = QtGui.QTransform()
            transform180.rotate(180)
            # now we store it
            ImageCache['QSwitch'] = QtGui.QPixmap.fromImage(image)
            ImageCache['QSwitchU'] = QtGui.QPixmap.fromImage(image.transformed(transform180))

    def dataChanged(self):
        isflipped = self.parent.spritedata[5] & 1

        if isflipped == 0:
            self.image = ImageCache['QSwitch']
        else:
            self.image = ImageCache['QSwitchU']

        super().dataChanged()


class SpriteImage_PSwitch(SLib.SpriteImage_Static):  # 105
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PSwitch'],
        )

    @staticmethod
    def loadImages():
        if 'PSwitch' not in ImageCache:
            # we need to cache 2 things, the regular switch, and the upside down one
            image = SLib.GetImg('p_switch.png', True)
            # now we set up a transform to turn the switch upside down
            transform180 = QtGui.QTransform()
            transform180.rotate(180)
            # now we store it
            ImageCache['PSwitch'] = QtGui.QPixmap.fromImage(image)
            ImageCache['PSwitchU'] = QtGui.QPixmap.fromImage(image.transformed(transform180))

    def dataChanged(self):
        isflipped = self.parent.spritedata[5] & 1

        if isflipped == 0:
            self.image = ImageCache['PSwitch']
        else:
            self.image = ImageCache['PSwitchU']

        super().dataChanged()


class SpriteImage_GhostHouseDoor(SLib.SpriteImage_Static):  # 108
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GhostHouseDoor'],
        )

        self.xOffset = -3.125
        self.yOffset = 2.25

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GhostHouseDoor', 'ghost_house_door.png')


class SpriteImage_TowerBossDoor(SLib.SpriteImage_Static):  # 109
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['TowerBossDoor'],
        )

        self.xOffset = -8
        self.yOffset = -8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TowerBossDoor', 'tower_boss_door.png')


class SpriteImage_CastleBossDoor(SLib.SpriteImage_Static):  # 110
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['CastleBossDoor'],
        )

        self.xOffset = -16
        self.yOffset = -32

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CastleBossDoor', 'castle_boss_door.png')


class SpriteImage_SpecialExit(SLib.SpriteImage):  # 115
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def dataChanged(self):
        super().dataChanged()

        w = (self.parent.spritedata[4] & 15) + 1
        h = (self.parent.spritedata[5] >> 4) + 1
        if w == 1 and h == 1:  # no point drawing a 1x1 outline behind the self.parent
            self.aux[0].setSize(0, 0)
            return
        self.aux[0].setSize(w * 60, h * 60)


class SpriteImage_Spinner(SLib.SpriteImage_StaticMultiple):  # 117
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -48
        self.yOffset = -16

    @staticmethod
    def loadImages():
        for i in range(16):
            SLib.loadIfNotInImageCache('Spinner' + str(i), 'big_spinner_s' + str(i) + '.png')

    def dataChanged(self):
        size = self.parent.spritedata[4] & 0xF

        self.image = ImageCache['Spinner' + str(size)]

        super().dataChanged()


class SpriteImage_SpinyCheep(SLib.SpriteImage_Static):  # 120
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SpinyCheep'],
            (-1, -2),
        )
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def dataChanged(self):
        super().dataChanged()

        nybbleWidth = self.parent.spritedata[3] & 0xF

        width = nybbleWidth * 60 + 120

        offsetX = -(nybbleWidth * 60 + 60)

        self.aux[0].setSize(width, 60, offsetX, 0)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpinyCheep', 'cheep_spiny.png')


class SpriteImage_SandPillar(SLib.SpriteImage_Static):  # 123
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SandPillar'],
        )

        self.yOffset = -143  # what
        self.xOffset = -18

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SandPillar', 'sand_pillar.png')


class SpriteImage_Thwomp(SLib.SpriteImage_Static):  # 135
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Thwomp'],
        )

        self.xOffset = -8
        self.yOffset = 0

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Thwomp', 'thwomp.png')


class SpriteImage_GiantThwomp(SLib.SpriteImage_Static):  # 136
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GiantThwomp'],
        )

        self.xOffset = -4
        self.yOffset = 0

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantThwomp', 'thwomp_giant.png')


class SpriteImage_DryBones(SLib.SpriteImage_Static):  # 137
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['DryBones'],
        )

        self.yOffset = -12
        self.xOffset = -7

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('DryBones', 'dry_bones.png')


class SpriteImage_BigDryBones(SLib.SpriteImage_Static):  # 138
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigDryBones'],
        )

        self.yOffset = -21
        self.xOffset = -7

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigDryBones', 'big_dry_bones.png')


class SpriteImage_PipeUp(SpriteImage_Pipe):  # 139
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'U'
        self.typeinfluence = True

    def dataChanged(self):

        size = self.parent.spritedata[3]

        if size == 1:
            self.big = False
            self.painted = True
            self.width = 32
            self.xOffset = 0
        elif size == 2:
            self.big = True
            self.painted = False
            self.width = 64
            self.xOffset = -16
        else:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0

        super().dataChanged()


class SpriteImage_PipeDown(SpriteImage_Pipe):  # 140
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'D'
        self.typeinfluence = True

    def dataChanged(self):

        size = self.parent.spritedata[3]

        if size == 1:
            self.big = False
            self.painted = True
            self.width = 32
            self.xOffset = 0
            self.yOffset = 0
        elif size == 2:
            self.big = True
            self.painted = False
            self.width = 64
            self.xOffset = -16
            self.yOffset = 0
        else:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0
            self.yOffset = 0

        super().dataChanged()


class SpriteImage_PipeLeft(SpriteImage_Pipe):  # 141
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'L'
        self.typeinfluence = True

    def dataChanged(self):

        size = self.parent.spritedata[3]

        if size == 1:
            self.big = False
            self.painted = True
            self.height = 32
            self.yOffset = 0
        elif size == 2:
            self.big = True
            self.painted = False
            self.height = 64
            self.yOffset = -16
        else:
            self.big = False
            self.painted = False
            self.height = 32
            self.yOffset = 0

        super().dataChanged()


class SpriteImage_PipeRight(SpriteImage_Pipe):  # 142
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'R'
        self.typeinfluence = True

    def dataChanged(self):

        size = self.parent.spritedata[3]

        if size == 1:
            self.big = False
            self.painted = True
            self.height = 32
            self.yOffset = 0
        elif size == 2:
            self.big = True
            self.painted = False
            self.height = 64
            self.yOffset = -16
        else:
            self.big = False
            self.painted = False
            self.height = 32
            self.yOffset = 0

        super().dataChanged()


class SpriteImage_BubbleYoshi(SLib.SpriteImage_Static):  # 143, 243
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BubbleYoshi'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BubbleYoshi', 'babyyoshibubble.png')


class SpriteImage_PalmTree(SLib.SpriteImage_StaticMultiple):  # 145
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -32

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Palm1', 'palm_1.png')
        SLib.loadIfNotInImageCache('Palm1L', 'palm_1_l.png')
        SLib.loadIfNotInImageCache('Palm1D', 'palm_1_d.png')
        SLib.loadIfNotInImageCache('Palm1LD', 'palm_1_l_d.png')
        SLib.loadIfNotInImageCache('Palm2', 'palm_2.png')
        SLib.loadIfNotInImageCache('Palm2L', 'palm_2_l.png')
        SLib.loadIfNotInImageCache('Palm2D', 'palm_2_d.png')
        SLib.loadIfNotInImageCache('Palm2LD', 'palm_2_l_d.png')
        SLib.loadIfNotInImageCache('Palm3', 'palm_3.png')
        SLib.loadIfNotInImageCache('Palm3L', 'palm_3_l.png')
        SLib.loadIfNotInImageCache('Palm3D', 'palm_3_d.png')
        SLib.loadIfNotInImageCache('Palm3LD', 'palm_3_l_d.png')
        SLib.loadIfNotInImageCache('Palm4', 'palm_4.png')
        SLib.loadIfNotInImageCache('Palm4L', 'palm_4_l.png')
        SLib.loadIfNotInImageCache('Palm4D', 'palm_4_d.png')
        SLib.loadIfNotInImageCache('Palm4LD', 'palm_4_l_d.png')
        SLib.loadIfNotInImageCache('Palm5', 'palm_5.png')
        SLib.loadIfNotInImageCache('Palm5L', 'palm_5_l.png')
        SLib.loadIfNotInImageCache('Palm5D', 'palm_5_d.png')
        SLib.loadIfNotInImageCache('Palm5LD', 'palm_5_l_d.png')
        SLib.loadIfNotInImageCache('Palm6', 'palm_6.png')
        SLib.loadIfNotInImageCache('Palm6L', 'palm_6_l.png')
        SLib.loadIfNotInImageCache('Palm6D', 'palm_6_d.png')
        SLib.loadIfNotInImageCache('Palm6LD', 'palm_6_l_d.png')
        SLib.loadIfNotInImageCache('Palm7', 'palm_7.png')
        SLib.loadIfNotInImageCache('Palm7L', 'palm_7_l.png')
        SLib.loadIfNotInImageCache('Palm7D', 'palm_7_d.png')
        SLib.loadIfNotInImageCache('Palm7LD', 'palm_7_l_d.png')
        SLib.loadIfNotInImageCache('Palm8', 'palm_8.png')
        SLib.loadIfNotInImageCache('Palm8L', 'palm_8_l.png')
        SLib.loadIfNotInImageCache('Palm8D', 'palm_8_d.png')
        SLib.loadIfNotInImageCache('Palm8LD', 'palm_8_l_d.png')
        SLib.loadIfNotInImageCache('Palm9', 'palm_9.png')
        SLib.loadIfNotInImageCache('Palm9L', 'palm_9_l.png')
        SLib.loadIfNotInImageCache('Palm9D', 'palm_9_d.png')
        SLib.loadIfNotInImageCache('Palm9LD', 'palm_9_l_d.png')
        SLib.loadIfNotInImageCache('Palm10', 'palm_10.png')
        SLib.loadIfNotInImageCache('Palm10L', 'palm_10_l.png')
        SLib.loadIfNotInImageCache('Palm10D', 'palm_10_d.png')
        SLib.loadIfNotInImageCache('Palm10LD', 'palm_10_l_d.png')
        SLib.loadIfNotInImageCache('Palm11', 'palm_11.png')
        SLib.loadIfNotInImageCache('Palm11L', 'palm_11_l.png')
        SLib.loadIfNotInImageCache('Palm11D', 'palm_11_d.png')
        SLib.loadIfNotInImageCache('Palm11LD', 'palm_11_l_d.png')
        SLib.loadIfNotInImageCache('Palm12', 'palm_12.png')
        SLib.loadIfNotInImageCache('Palm12L', 'palm_12_l.png')
        SLib.loadIfNotInImageCache('Palm12D', 'palm_12_d.png')
        SLib.loadIfNotInImageCache('Palm12LD', 'palm_12_l_d.png')
        SLib.loadIfNotInImageCache('Palm13', 'palm_13.png')
        SLib.loadIfNotInImageCache('Palm13L', 'palm_13_l.png')
        SLib.loadIfNotInImageCache('Palm13D', 'palm_13_d.png')
        SLib.loadIfNotInImageCache('Palm13LD', 'palm_13_l_d.png')
        SLib.loadIfNotInImageCache('Palm14', 'palm_14.png')
        SLib.loadIfNotInImageCache('Palm14L', 'palm_14_l.png')
        SLib.loadIfNotInImageCache('Palm14D', 'palm_14_d.png')
        SLib.loadIfNotInImageCache('Palm14LD', 'palm_14_l_d.png')
        SLib.loadIfNotInImageCache('Palm15', 'palm_15.png')
        SLib.loadIfNotInImageCache('Palm15L', 'palm_15_l.png')
        SLib.loadIfNotInImageCache('Palm15D', 'palm_15_d.png')
        SLib.loadIfNotInImageCache('Palm15LD', 'palm_15_l_d.png')
        SLib.loadIfNotInImageCache('Palm16', 'palm_16.png')
        SLib.loadIfNotInImageCache('Palm16L', 'palm_16_l.png')
        SLib.loadIfNotInImageCache('Palm16D', 'palm_16_d.png')
        SLib.loadIfNotInImageCache('Palm16LD', 'palm_16_l_d.png')

    def dataChanged(self):

        height = self.parent.spritedata[5] & 0x0F

        rawleft = (self.parent.spritedata[4] >> 4) & 0x0F

        rawdesert = (self.parent.spritedata[2] >> 4) & 0x0F

        left = False

        desert = False

        if rawleft == 1:
            left = False
        else:
            left = True

        if rawdesert == 1:
            desert = True
        else:
            desert = False

        self.yOffset = -1 * (height + 4) * 16

        if height == 0:

            if left:
                self.image = ImageCache['Palm1L']
                if desert:
                    self.image = ImageCache['Palm1LD']
            else:
                self.image = ImageCache['Palm1']
                if desert:
                    self.image = ImageCache['Palm1D']

        elif height == 1:

            if left:
                self.image = ImageCache['Palm2L']
                if desert:
                    self.image = ImageCache['Palm2LD']
            else:
                self.image = ImageCache['Palm2']
                if desert:
                    self.image = ImageCache['Palm2D']

        elif height == 2:

            if left:
                self.image = ImageCache['Palm3L']
                if desert:
                    self.image = ImageCache['Palm3LD']
            else:
                self.image = ImageCache['Palm3']
                if desert:
                    self.image = ImageCache['Palm3D']

        elif height == 3:

            if left:
                self.image = ImageCache['Palm4L']
                if desert:
                    self.image = ImageCache['Palm4LD']
            else:
                self.image = ImageCache['Palm4']
                if desert:
                    self.image = ImageCache['Palm4D']

        elif height == 4:

            if left:
                self.image = ImageCache['Palm5L']
                if desert:
                    self.image = ImageCache['Palm5LD']
            else:
                self.image = ImageCache['Palm5']
                if desert:
                    self.image = ImageCache['Palm5D']

        elif height == 5:

            if left:
                self.image = ImageCache['Palm6L']
                if desert:
                    self.image = ImageCache['Palm6LD']
            else:
                self.image = ImageCache['Palm6']
                if desert:
                    self.image = ImageCache['Palm6D']

        elif height == 6:

            if left:
                self.image = ImageCache['Palm7L']
                if desert:
                    self.image = ImageCache['Palm7LD']
            else:
                self.image = ImageCache['Palm7']
                if desert:
                    self.image = ImageCache['Palm7D']

        elif height == 7:

            if left:
                self.image = ImageCache['Palm8L']
                if desert:
                    self.image = ImageCache['Palm8LD']
            else:
                self.image = ImageCache['Palm8']
                if desert:
                    self.image = ImageCache['Palm8D']

        elif height == 8:

            if left:
                self.image = ImageCache['Palm9L']
                if desert:
                    self.image = ImageCache['Palm9LD']
            else:
                self.image = ImageCache['Palm9']
                if desert:
                    self.image = ImageCache['Palm9D']

        elif height == 9:

            if left:
                self.image = ImageCache['Palm10L']
                if desert:
                    self.image = ImageCache['Palm10LD']
            else:
                self.image = ImageCache['Palm10']
                if desert:
                    self.image = ImageCache['Palm10D']

        elif height == 10:

            if left:
                self.image = ImageCache['Palm11L']
                if desert:
                    self.image = ImageCache['Palm11LD']
            else:
                self.image = ImageCache['Palm11']
                if desert:
                    self.image = ImageCache['Palm11D']

        elif height == 11:

            if left:
                self.image = ImageCache['Palm12L']
                if desert:
                    self.image = ImageCache['Palm12LD']
            else:
                self.image = ImageCache['Palm12']
                if desert:
                    self.image = ImageCache['Palm12D']

        elif height == 12:

            if left:
                self.image = ImageCache['Palm13L']
                if desert:
                    self.image = ImageCache['Palm13LD']
            else:
                self.image = ImageCache['Palm13']
                if desert:
                    self.image = ImageCache['Palm13D']

        elif height == 13:

            if left:
                self.image = ImageCache['Palm14L']
                if desert:
                    self.image = ImageCache['Palm14LD']
            else:
                self.image = ImageCache['Palm14']
                if desert:
                    self.image = ImageCache['Palm14D']

        elif height == 14:

            if left:
                self.image = ImageCache['Palm15L']
                if desert:
                    self.image = ImageCache['Palm15LD']
            else:
                self.image = ImageCache['Palm15']
                if desert:
                    self.image = ImageCache['Palm15D']

        elif height == 15:

            if left:
                self.image = ImageCache['Palm16L']
                if desert:
                    self.image = ImageCache['Palm16LD']
            else:
                self.image = ImageCache['Palm16']
                if desert:
                    self.image = ImageCache['Palm16D']


        else:
            self.image = ImageCache['Palm1']

        super().dataChanged()


class SpriteImage_MovPipe(SpriteImage_PipeAlt):  # 146
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'U'
        self.typeinfluence = True

    def dataChanged(self):

        rawlength = (self.parent.spritedata[4] & 0x0F) + 1

        if not self.mini:
            # rawtop = (self.parent.spritedata[2] >> 4) & 3
            rawtop = 0

            # if self.moving:
            # rawtop = 0 & 3

            # if self.expandable: rawcolour = (self.parent.spritedata[3]) & 3
            # elif self.moving: rawcolour = (self.parent.spritedata[3]) & 3
            # else: rawcolour = (self.parent.spritedata[3] & 0x0F) & 3

            if self.typeinfluence and rawtop == 0:
                # if self.expandable: rawtype = self.parent.spritedata[4] & 3
                # elif self.moving: rawtype = self.parent.spritedata[5] >> 4
                # else:
                rawtype = (self.parent.spritedata[5] >> 4) & 3
            else:
                rawtype = 0

            if rawtop == 1:
                pipeLength = rawlength + rawtype + self.extraLength + 1
            elif rawtop == 0:
                if rawtype == 0:
                    pipeLength = rawlength + rawtype + self.extraLength + 1
                else:
                    pipeLength = rawlength + rawtype + self.extraLength
            else:
                pipeLength = rawlength + rawtype + self.extraLength

        size = self.parent.spritedata[5] >> 4
        direction = self.parent.spritedata[3] >> 4
        self.moving = True

        self.pipeWidth = pipeLength * 60
        self.pipeHeight = pipeLength * 60

        if direction == 1:
            self.direction = 'L'
            self.height = 32
            self.xOffset = 16 - self.width
            self.topX = 0
            self.topY = 0
        elif direction == 2:
            self.direction = 'U'
            self.width = 32
            self.yOffset = 16 - (self.pipeHeight / 3.75)
            self.topY = 0
            self.topX = 0
        elif direction == 3:
            self.direction = 'D'
            self.width = 32
            self.yOffset = 0
            self.topY = self.pipeHeight - 60
            self.topX = 0
        else:
            self.direction = 'R'
            self.height = 32
            self.xOffset = 0
            self.topX = self.pipeWidth - 60
            self.topY = 0

        if size == 0:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0
        elif size == 1:
            self.big = False
            self.painted = True
            self.width = 32
            self.xOffset = 0
        elif size == 2:
            self.big = True
            self.painted = False
            self.width = 64
            self.xOffset = -16
        else:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0

        super().dataChanged()


class SpriteImage_StoneEye(SLib.SpriteImage_StaticMultiple):  # 150
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():

        SLib.loadIfNotInImageCache('StoneRightUp', 'stone_right_up.png')
        SLib.loadIfNotInImageCache('StoneLeftUp', 'stone_left_up.png')
        SLib.loadIfNotInImageCache('StoneFront', 'stone_front.png')
        SLib.loadIfNotInImageCache('StoneRight', 'stone_right.png')
        SLib.loadIfNotInImageCache('StoneLeft', 'stone_left.png')
        ImageCache['BigStoneRightUp'] = ImageCache['StoneRightUp'].scaled(439 * 1.5, 821 * 1.5,
                                                                          QtCore.Qt.KeepAspectRatio)
        ImageCache['BigStoneLeftUp'] = ImageCache['StoneLeftUp'].scaled(439 * 1.5, 821 * 1.5, QtCore.Qt.KeepAspectRatio)
        ImageCache['BigStoneFront'] = ImageCache['StoneFront'].scaled(354 * 1.5, 745 * 1.5, QtCore.Qt.KeepAspectRatio)
        ImageCache['BigStoneRight'] = ImageCache['StoneRight'].scaled(478 * 1.5, 747 * 1.5, QtCore.Qt.KeepAspectRatio)
        ImageCache['BigStoneLeft'] = ImageCache['StoneLeft'].scaled(487 * 1.5, 747 * 1.5, QtCore.Qt.KeepAspectRatio)

    def dataChanged(self):

        direction = self.parent.spritedata[4]

        t = QTransform()

        t.rotate(0)

        #        StoneRotation = Rotations[movID]


        if direction == 0:
            self.image = ImageCache['StoneRightUp'].transformed(t)
            self.xOffset = -25.5
            self.yOffset = -16

        elif direction == 1:
            self.image = ImageCache['StoneLeftUp'].transformed(t)
            self.xOffset = -29
            self.yOffset = -16

        elif direction == 2:
            self.image = ImageCache['StoneFront'].transformed(t)
            self.xOffset = -14
            self.yOffset = 8

        elif direction == 3:
            self.image = ImageCache['StoneRight'].transformed(t)
            self.xOffset = -48.5
            self.yOffset = 8

        elif direction == 4:
            self.image = ImageCache['StoneLeft'].transformed(t)
            self.xOffset = -48.5 + 17.5
            self.yOffset = 8
        elif direction == 16:
            self.image = ImageCache['BigStoneRightUp'].transformed(t)
            self.xOffset = -56
            self.yOffset = -72

        elif direction == 17:
            self.image = ImageCache['BigStoneLeftUp'].transformed(t)
            self.xOffset = -60
            self.yOffset = -72

        elif direction == 18:
            self.image = ImageCache['BigStoneFront'].transformed(t)
            self.xOffset = -40
            self.yOffset = -48

        elif direction == 19:
            self.image = ImageCache['BigStoneRight'].transformed(t)
            self.xOffset = -41.5 + (-16 * 3)
            self.yOffset = -48

        elif direction == 20:
            self.image = ImageCache['BigStoneLeft'].transformed(t)
            self.xOffset = -38
            self.yOffset = -48

        else:
            self.image = ImageCache['StoneFront'].transformed(t)
            self.xOffset = -14
            self.yOffset = 8

        super().dataChanged()


# self.translateImage()

"""
    def translateImage(self):

        t = QTransform()

        t.rotate(StoneRotation)

        ImageCache['BigStoneRightUp'] = ImageCache['BigStoneRightUp'].transformed(t)
        ImageCache['BigStoneLeftUp'] = ImageCache['BigStoneLeftUp'].transformed(t)
        ImageCache['BigStoneFront'] = ImageCache['BigStoneFront'].transformed(t)
        ImageCache['BigStoneRight'] = ImageCache['BigStoneRight'].transformed(t)
        ImageCache['BigStoneLeft'] = ImageCache['BigStoneLeft'].transformed(t)

        ImageCache['StoneRightUp'] = ImageCache['StoneRightUp'].transformed(t)
        ImageCache['StoneLeftUp'] = ImageCache['StoneLeftUp'].transformed(t)
        ImageCache['StoneFront'] = ImageCache['StoneFront'].transformed(t)
        ImageCache['StoneRight'] = ImageCache['StoneRight'].transformed(t)
        ImageCache['StoneLeft'] = ImageCache['StoneLeft'].transformed(t)
"""


class SpriteImage_POWBlock(SLib.SpriteImage_Static):  # 152
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['POWBlock'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('POWBlock', 'block_pow.png')


class SpriteImage_FlyingQBlock(SLib.SpriteImage):  # 154
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

        self.dimensions = (-12, -16, 42, 32)

    def dataChanged(self):
        super().dataChanged()

        self.contents = self.parent.spritedata[9] & 0xF
        self.acorn = (self.parent.spritedata[6] >> 4) & 1

        items = {0: 0x800 + 160, 1: 49, 2: 32, 3: 32, 4: 37, 5: 38, 6: 36, 7: 33, 8: 34, 9: 41, 12: 35, 13: 42, 15: 39}

        self.dopaint = True
        self.image = None

        if self.acorn:
            self.tilenum = 40
        elif self.contents in items:
            self.tilenum = items[self.contents]
        else:
            self.dopaint = False
            if self.contents == 10:
                self.imagecache = ImageCache['Q10']
            elif self.contents == 11:
                self.imagecache = ImageCache['QKinokoUP']
            elif self.contents == 14:
                self.imagecache = ImageCache['QKinoko']
            else:
                self.dopaint = True
                self.tilenum = 49

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FlyingQBlock', 'flying_qblock.png')
        SLib.loadIfNotInImageCache('Q10', 'block_q_10.png')
        SLib.loadIfNotInImageCache('QKinokoUP', 'block_q_kinoko_up.png')
        SLib.loadIfNotInImageCache('QKinoko', 'block_q_kinoko_coin.png')

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['FlyingQBlock'])
        if self.dopaint:
            painter.drawPixmap(45, 57.5, SLib.Tiles[self.tilenum].main)
        else:
            painter.drawPixmap(45, 57.5, self.imagecache)


class SpriteImage_PipeCannon(SLib.SpriteImage):  # 155
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

        # self.aux[0] is the pipe image
        self.aux.append(SLib.AuxiliaryImage(parent, 60, 60))
        self.aux[0].hover = False

        # self.aux[1] is the trajectory indicator
        self.aux.append(SLib.AuxiliaryPainterPath(parent, QtGui.QPainterPath(), 60, 60))
        self.aux[1].fillFlag = False

        self.aux[0].setZValue(self.aux[1].zValue() + 1)

        self.size = (32, 64)

    @staticmethod
    def loadImages():
        if 'PipeCannon0' in ImageCache: return
        for i in range(7):
            ImageCache['PipeCannon%d' % i] = SLib.GetImg('pipe_cannon_%d.png' % i)

    def dataChanged(self):
        fireDirection = (self.parent.spritedata[5] & 0xF) % 8
        if fireDirection == 7: fireDirection = 5

        self.aux[0].image = ImageCache['PipeCannon%d' % (fireDirection)]

        if fireDirection == 0:
            # 30 deg to the right
            self.aux[0].setSize(84 * 2.5, 101 * 2.5, 0, -5 * 2.5)
            path = QtGui.QPainterPath(QtCore.QPoint(0, 184 * 2.5))
            path.cubicTo(QtCore.QPoint(152 * 2.5, -24 * 2.5), QtCore.QPoint(168 * 2.5, -24 * 2.5),
                         QtCore.QPoint(264 * 2.5, 48 * 2.5))
            path.lineTo(QtCore.QPoint(480 * 2.5, 216 * 2.5))
            self.aux[1].setSize(480 * 2.5, 216 * 2.5, 24 * 2.5, -120 * 2.5)
        elif fireDirection == 1:
            # 30 deg to the left
            self.aux[0].setSize(85 * 2.5, 101 * 2.5, -36 * 2.5, -5 * 2.5)
            path = QtGui.QPainterPath(QtCore.QPoint(480 * 2.5 - 0, 184 * 2.5))
            path.cubicTo(QtCore.QPoint(480 * 2.5 - 152 * 2.5, -24 * 2.5),
                         QtCore.QPoint(480 * 2.5 - 168 * 2.5, -24 * 2.5),
                         QtCore.QPoint(480 * 2.5 - 264 * 2.5, 48 * 2.5))
            path.lineTo(QtCore.QPoint(480 * 2.5 - 480 * 2.5, 216 * 2.5))
            self.aux[1].setSize(480 * 2.5, 216 * 2.5, -480 * 2.5 + 24 * 2.5, -120 * 2.5)
        elif fireDirection == 2:
            # 15 deg to the right
            self.aux[0].setSize(60 * 2.5, 102 * 2.5, 0 * 2.5, -6 * 2.5)
            path = QtGui.QPainterPath(QtCore.QPoint(0, 188 * 2.5))
            path.cubicTo(QtCore.QPoint(36 * 2.5, -36 * 2.5), QtCore.QPoint(60 * 2.5, -36 * 2.5),
                         QtCore.QPoint(96 * 2.5, 84 * 2.5))
            path.lineTo(QtCore.QPoint(144 * 2.5, 252 * 2.5))
            self.aux[1].setSize(144 * 2.5, 252 * 2.5, 30 * 2.5, -156 * 2.5)
        elif fireDirection == 3:
            # 15 deg to the left
            self.aux[0].setSize(61 * 2.5, 102 * 2.5, -12 * 2.5, -6 * 2.5)
            path = QtGui.QPainterPath(QtCore.QPoint(144 * 2.5 - 0, 188 * 2.5))
            path.cubicTo(QtCore.QPoint(144 * 2.5 - 36 * 2.5, -36 * 2.5), QtCore.QPoint(144 * 2.5 - 60 * 2.5, -36 * 2.5),
                         QtCore.QPoint(144 * 2.5 - 96 * 2.5, 84 * 2.5))
            path.lineTo(QtCore.QPoint(144 * 2.5 - 144 * 2.5, 252 * 2.5))
            self.aux[1].setSize(144 * 2.5, 252 * 2.5, -144 * 2.5 + 18 * 2.5, -156 * 2.5)
        elif fireDirection == 4:
            # Straight up
            self.aux[0].setSize(135 * 2.5, 132 * 2.5, -43 * 2.5, -35 * 2.5)
            path = QtGui.QPainterPath(QtCore.QPoint(26 * 2.5, 0))
            path.lineTo(QtCore.QPoint(26 * 2.5, 656 * 2.5))
            self.aux[1].setSize(48 * 2.5, 656 * 2.5, 0, -632 * 2.5)
        elif fireDirection == 5:
            # 45 deg to the right
            self.aux[0].setSize(90 * 2.5, 98 * 2.5, 0, -1 * 2.5)
            path = QtGui.QPainterPath(QtCore.QPoint(0, 320 * 2.5))
            path.lineTo(QtCore.QPoint(264 * 2.5, 64 * 2.5))
            path.cubicTo(QtCore.QPoint(348 * 2.5, -14 * 2.5), QtCore.QPoint(420 * 2.5, -14 * 2.5),
                         QtCore.QPoint(528 * 2.5, 54 * 2.5))
            path.lineTo(QtCore.QPoint(1036 * 2.5, 348 * 2.5))
            self.aux[1].setSize(1036 * 2.5, 348 * 2.5, 24 * 2.5, -252 * 2.5)
        elif fireDirection == 6:
            # 45 deg to the left
            self.aux[0].setSize(91 * 2.5, 98 * 2.5, -42 * 2.5, -1 * 2.5)
            path = QtGui.QPainterPath(QtCore.QPoint(1036 * 2.5 - 0 * 2.5, 320 * 2.5))
            path.lineTo(QtCore.QPoint(1036 * 2.5 - 264 * 2.5, 64 * 2.5))
            path.cubicTo(QtCore.QPoint(1036 * 2.5 - 348 * 2.5, -14 * 2.5),
                         QtCore.QPoint(1036 * 2.5 - 420 * 2.5, -14 * 2.5),
                         QtCore.QPoint(1036 * 2.5 - 528 * 2.5, 54 * 2.5))
            path.lineTo(QtCore.QPoint(1036 * 2.5 - 1036 * 2.5, 348 * 2.5))
            self.aux[1].setSize(1036 * 2.5, 348 * 2.5, -1036 * 2.5 + 24 * 2.5, -252 * 2.5)
        self.aux[1].SetPath(path)

        super().dataChanged()


class SpriteImage_WaterGeyser(SpriteImage_StackedSprite):  # 156
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)

    @staticmethod
    def loadImages():
        ImageCache['WaterGeyserTop'] = SLib.GetImg('water_geyser_top.png')
        ImageCache['WaterGeyserMiddle'] = SLib.GetImg('water_geyser_middle.png')

    def dataChanged(self):
        super().dataChanged()
        rawlengthones = self.parent.spritedata[5]
        rawlengthtwos = self.parent.spritedata[4] & 0xF

        if rawlengthones == 0:
            rawlengthones = 0
        elif rawlengthones == 16:
            rawlengthones = 1
        elif rawlengthones == 32:
            rawlengthones = 2
        elif rawlengthones == 48:
            rawlengthones = 3
        elif rawlengthones == 64:
            rawlengthones = 4
        elif rawlengthones == 80:
            rawlengthones = 5
        elif rawlengthones == 96:
            rawlengthones = 6
        elif rawlengthones == 112:
            rawlengthones = 7
        elif rawlengthones == 128:
            rawlengthones = 8
        elif rawlengthones == 144:
            rawlengthones = 9
        elif rawlengthones == 160:
            rawlengthones = 10
        elif rawlengthones == 176:
            rawlengthones = 11
        elif rawlengthones == 192:
            rawlengthones = 12
        elif rawlengthones == 208:
            rawlengthones = 13
        elif rawlengthones == 224:
            rawlengthones = 14
        elif rawlengthones == 240:
            rawlengthones = 15
        elif rawlengthones == 256:
            rawlengthones = 16

        rawlengthtwos = rawlengthtwos * 16

        #        if rawlengthtwos > 255: rawlengthtwos = rawlengthtwos - 256

        rawlength = rawlengthones + rawlengthtwos

        pipeLength = rawlength

        #        print(rawlengthones, rawlengthtwos, pipeLength)

        self.hasTop = True
        self.hasBottom = False

        self.pipeHeight = (pipeLength + 1) * 60
        self.height = (self.pipeHeight / 3.75)
        self.pipeHeight = (pipeLength) * 60

        self.middle = ImageCache['WaterGeyserMiddle']
        self.top = ImageCache['WaterGeyserTop']

        self.pipeWidth = 360
        self.width = 96

        self.yOffset = 8 + (-6 * 16) + (-1 * ((rawlength - 2) * 8))
        #        self.yOffset = -12 * 16
        self.xOffset = -40

    def paint(self, painter):
        super().paint(painter)

        painter.drawTiledPixmap(self.x, self.y, self.pipeWidth, self.pipeHeight, self.middle)
        if self.hasTop:
            painter.drawPixmap(self.topX, self.topY, self.top)


class SpriteImage_CoinOutline(SLib.SpriteImage_StaticMultiple):  # 158
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,  # native res (3.75*16=60)
            ImageCache['CoinOutlineMultiplayer'],
        )
        self.parent.setZValue(20000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CoinOutline', 'coin_outline.png')
        SLib.loadIfNotInImageCache('CoinOutlineMultiplayer', 'coin_outline_multiplayer.png')

    def dataChanged(self):
        multi = (self.parent.spritedata[2] >> 4) & 1
        self.image = ImageCache['CoinOutline' + ('Multiplayer' if multi else '')]
        super().dataChanged()


class SpriteImage_ExpandingPipeRight(SpriteImage_PipeExpand):  # 159
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.direction = 'R'
        self.typeinfluence = True

    def dataChanged(self):

        size = self.parent.spritedata[4]
        self.expandable = True

        bigSize = self.parent.spritedata[5] & 0xF

        adderSize = self.parent.spritedata[5] >> 4

        addSize = 0

        if size == 0:
            self.big = False
            self.painted = False
            self.height = 32
            self.yOffset = 0
            addSize = 1
        elif size == 1:
            self.big = False
            self.painted = True
            self.height = 32
            self.yOffset = 0
            addSize = 1
        elif size == 2:
            self.big = True
            self.painted = False
            self.height = 64
            self.yOffset = -16
            bigSize = bigSize + 1
            addSize = 1
        else:
            self.big = False
            self.painted = False
            self.height = 32
            self.yOffset = 0
            addSize = 1

        totalHeight = (0 - 1) + (addSize) + adderSize

        xOff = 0

        self.aux[0].setSize(totalHeight * 60 + 120 + (bigSize * 60), self.height / 16 * 60, xOff * 60, 0)

        super().dataChanged()


class SpriteImage_ExpandingPipeLeft(SpriteImage_PipeExpand):  # 160
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.direction = 'L'
        self.typeinfluence = True

    def dataChanged(self):

        size = self.parent.spritedata[4]
        self.expandable = True

        bigSize = self.parent.spritedata[5] & 0xF

        adderSize = self.parent.spritedata[5] >> 4

        addSize = 0

        if size == 0:
            self.big = False
            self.painted = False
            self.height = 32
            self.yOffset = 0
            addSize = 1
        elif size == 1:
            self.big = False
            self.painted = True
            self.height = 32
            self.yOffset = 0
            addSize = 1
        elif size == 2:
            self.big = True
            self.painted = False
            self.height = 64
            self.yOffset = -16
            bigSize = bigSize + 1
            addSize = 1
        else:
            self.big = False
            self.painted = False
            self.height = 32
            self.yOffset = 0
            addSize = 1

        totalHeight = (0 - 1) + (addSize) + adderSize

        xOff = -totalHeight

        self.aux[0].setSize(totalHeight * 60 + 120 + (bigSize * 60), self.height / 16 * 60, xOff * 60, 0)

        super().dataChanged()


class SpriteImage_ExpandingPipeUp(SpriteImage_PipeExpand):  # 161
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.direction = 'U'
        self.typeinfluence = True

    def dataChanged(self):

        size = self.parent.spritedata[4]
        self.expandable = True

        bigSize = self.parent.spritedata[5] & 0xF

        adderSize = self.parent.spritedata[5] >> 4

        addSize = 0

        if size == 0:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0
            addSize = 1
        elif size == 1:
            self.big = False
            self.painted = True
            self.width = 32
            self.xOffset = 0
            addSize = 1
        elif size == 2:
            self.big = True
            self.painted = False
            self.width = 64
            self.xOffset = -16
            bigSize = bigSize + 1
            addSize = 1
        else:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0
            addSize = 1

        totalHeight = (0 - 1) + (addSize) + adderSize

        yOff = -totalHeight

        self.aux[0].setSize(self.width / 16 * 60, totalHeight * 60 + 120 + (bigSize * 60), 0, yOff * 60)

        super().dataChanged()


class SpriteImage_ExpandingPipeDown(SpriteImage_PipeExpand):  # 162
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.direction = 'D'
        self.typeinfluence = True

    def dataChanged(self):

        size = self.parent.spritedata[4]
        self.expandable = True

        bigSize = self.parent.spritedata[5] & 0xF

        adderSize = self.parent.spritedata[5] >> 4

        addSize = 0

        if size == 0:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0
            addSize = 1
        elif size == 1:
            self.big = False
            self.painted = True
            self.width = 32
            self.xOffset = 0
            addSize = 1
        elif size == 2:
            self.big = True
            self.painted = False
            self.width = 64
            self.xOffset = -16
            bigSize = bigSize + 1
            addSize = 1
        else:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0
            addSize = 1

        totalHeight = (0 - 1) + (addSize) + adderSize

        yOff = 0

        self.aux[0].setSize(self.width / 16 * 60, totalHeight * 60 + 120 + (bigSize * 60), 0, yOff * 60)

        super().dataChanged()


class SpriteImage_WaterGeyserLocation(SpriteImage_StackedSprite):  # 163
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)

    @staticmethod
    def loadImages():
        ImageCache['WaterGeyserTop'] = SLib.GetImg('water_geyser_top.png')
        ImageCache['WaterGeyserMiddle'] = SLib.GetImg('water_geyser_middle.png')

    def dataChanged(self):
        super().dataChanged()
        rawlengthones = self.parent.spritedata[5]
        rawlengthtwos = self.parent.spritedata[4] & 0xF

        if rawlengthones == 0:
            rawlengthones = 0
        elif rawlengthones == 16:
            rawlengthones = 1
        elif rawlengthones == 32:
            rawlengthones = 2
        elif rawlengthones == 48:
            rawlengthones = 3
        elif rawlengthones == 64:
            rawlengthones = 4
        elif rawlengthones == 80:
            rawlengthones = 5
        elif rawlengthones == 96:
            rawlengthones = 6
        elif rawlengthones == 112:
            rawlengthones = 7
        elif rawlengthones == 128:
            rawlengthones = 8
        elif rawlengthones == 144:
            rawlengthones = 9
        elif rawlengthones == 160:
            rawlengthones = 10
        elif rawlengthones == 176:
            rawlengthones = 11
        elif rawlengthones == 192:
            rawlengthones = 12
        elif rawlengthones == 208:
            rawlengthones = 13
        elif rawlengthones == 224:
            rawlengthones = 14
        elif rawlengthones == 240:
            rawlengthones = 15
        elif rawlengthones == 256:
            rawlengthones = 16

        rawlengthtwos = rawlengthtwos * 16

        #        if rawlengthtwos > 255: rawlengthtwos = rawlengthtwos - 256

        rawlength = rawlengthones

        pipeLength = rawlength

        #        print(rawlengthones, rawlengthtwos, pipeLength)

        self.hasTop = True
        self.hasBottom = False

        self.pipeHeight = (pipeLength + 1) * 60
        self.height = (self.pipeHeight / 3.75)
        self.pipeHeight = (pipeLength) * 60

        self.middle = ImageCache['WaterGeyserMiddle']
        self.top = ImageCache['WaterGeyserTop']

        self.pipeWidth = 360
        self.width = 96

        self.yOffset = 8 + (-6 * 16) + (-1 * ((rawlength - 2) * 8))
        #        self.yOffset = -12 * 16
        self.xOffset = -40

    def paint(self, painter):
        super().paint(painter)

        painter.drawTiledPixmap(self.x, self.y, self.pipeWidth, self.pipeHeight, self.middle)
        if self.hasTop:
            painter.drawPixmap(self.topX, self.topY, self.top)


class SpriteImage_CoinBlue(SLib.SpriteImage_Static):  # 167
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.parent.setZValue(20000)

    def paint(self, painter):
        super().paint(painter)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawPixmap(self.yOffset, self.xOffset, 60, 60, SLib.Tiles[46].main)


class SpriteImage_ClapCoin(SLib.SpriteImage_Static):  # 168
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ClapCoin'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ClapCoin', 'clap_coin.png')


class SpriteImage_ControllerIf(SLib.SpriteImage_Static):  # 169
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerIf'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerIf', 'controller_if.png')


class SpriteImage_Parabomb(SLib.SpriteImage_Static):  # 170
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Parabomb'],
        )

        self.yOffset = -16
        # self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Parabomb', 'parabomb.png')


class SpriteImage_Mechakoopa(SLib.SpriteImage_Static):  # 175
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Mechakoopa'],
        )

        self.yOffset = -10
        self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Mechakoopa', 'mechakoopa.png')


class SpriteImage_AirshipCannon(SLib.SpriteImage_StaticMultiple):  # 176
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.yOffset = -8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CannonL', 'Cannon_L.png')
        SLib.loadIfNotInImageCache('CannonR', 'Cannon_R.png')

    def dataChanged(self):

        direction = self.parent.spritedata[5]

        if direction == 1:
            self.image = ImageCache['CannonR']
            self.xOffset = 0
        else:
            self.image = ImageCache['CannonL']
            self.xOffset = -8

        super().dataChanged()


class SpriteImage_Spike(SLib.SpriteImage_Static):  # 180
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Spike'],
            (-16, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Spike', 'spike.png')


class SpriteImage_MovingPlatform(SLib.SpriteImage_StaticMultiple):  # 182, 186
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MovPlatNL'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovPlatNL', 'wood_platform_left.png')
        SLib.loadIfNotInImageCache('MovPlatNM', 'wood_platform_middle.png')
        SLib.loadIfNotInImageCache('MovPlatNR', 'wood_platform_right.png')
        SLib.loadIfNotInImageCache('MovPlatSL', 'wood_platform_snow_left.png')
        SLib.loadIfNotInImageCache('MovPlatSM', 'wood_platform_snow_middle.png')
        SLib.loadIfNotInImageCache('MovPlatSR', 'wood_platform_snow_right.png')
        SLib.loadIfNotInImageCache('MovPlatRL', 'metal_platform_left.png')
        SLib.loadIfNotInImageCache('MovPlatRM', 'metal_platform_middle.png')
        SLib.loadIfNotInImageCache('MovPlatRR', 'metal_platform_right.png')

    def dataChanged(self):
        super().dataChanged()

        type_ = (self.parent.spritedata[3] >> 4) & 0x3
        self.width = (self.parent.spritedata[8] & 0xF) + 1

        if self.width == 1:
            self.width = 2

        self.width *= 16

        self.imgType = 'N'

        if type_ == 1:
            self.imgType = 'R'

        elif type_ == 3:
            self.imgType = 'S'

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['MovPlat%sL' % self.imgType])
        painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['MovPlat%sR' % self.imgType])

        if self.width > 32:
            painter.drawTiledPixmap(60, 0, (self.width - 32) * 3.75, 60, ImageCache['MovPlat%sM' % self.imgType])


class SpriteImage_FallingIcicle(SLib.SpriteImage_StaticMultiple):  # 183
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FallingIcicle1x1', 'falling_icicle_1x1.png')
        SLib.loadIfNotInImageCache('FallingIcicle1x2', 'falling_icicle_1x2.png')

    def dataChanged(self):

        size = self.parent.spritedata[5]

        if size == 0:
            self.image = ImageCache['FallingIcicle1x1']
        elif size == 1:
            self.image = ImageCache['FallingIcicle1x2']
        else:
            self.image = ImageCache['FallingIcicle1x1']

        super().dataChanged()


class SpriteImage_GiantIcicle(SLib.SpriteImage_Static):  # 184
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GiantIcicle'],
        )

        self.xOffset = -24

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantIcicle', 'giant_icicle.png')


class SpriteImage_MovingPlatformSpawner(SLib.SpriteImage_StaticMultiple):  # 192
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MovPlatNL'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovPlatNL', 'wood_platform_left.png')
        SLib.loadIfNotInImageCache('MovPlatNM', 'wood_platform_middle.png')
        SLib.loadIfNotInImageCache('MovPlatNR', 'wood_platform_right.png')

    def dataChanged(self):
        super().dataChanged()

        self.width = self.parent.spritedata[8] & 0xF
        self.xOffset = 0

        if not self.width:
            self.width = 4

        elif self.width == 1:
            self.width = 1.5
            self.xOffset = -4

        self.width *= 16

    def paint(self, painter):
        super().paint(painter)

        if self.width > 16:
            painter.drawPixmap(0, 0, ImageCache['MovPlatNL'])
            painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['MovPlatNR'])

            if self.width > 32:
                painter.drawTiledPixmap(60, 0, (self.width - 32) * 3.75, 60, ImageCache['MovPlatNM'])

        else:
            painter.drawPixmap(0, 0, ImageCache['MovPlatNL'])
            painter.drawPixmap(30, 0, ImageCache['MovPlatNR'])


class SpriteImage_LineMovingPlatform(SLib.SpriteImage_StaticMultiple):  # 193
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MovPlatNL'],
        )
        self.yOffset = 8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovPlatNL', 'wood_platform_left.png')
        SLib.loadIfNotInImageCache('MovPlatNM', 'wood_platform_middle.png')
        SLib.loadIfNotInImageCache('MovPlatNR', 'wood_platform_right.png')
        SLib.loadIfNotInImageCache('MovPlatRL', 'metal_platform_left.png')
        SLib.loadIfNotInImageCache('MovPlatRM', 'metal_platform_middle.png')
        SLib.loadIfNotInImageCache('MovPlatRR', 'metal_platform_right.png')

    def dataChanged(self):
        super().dataChanged()

        self.width = self.parent.spritedata[8] & 0xF
        type_ = self.parent.spritedata[4] >> 4

        if not self.width:
            self.width = 4

        self.xOffset = (1.5 - 0.5 * (self.width - 1)) * 16

        if self.width == 1:
            self.width = 1.5

        self.width *= 16

        self.imgType = 'R'

        if not type_:
            self.imgType = 'N'

    def paint(self, painter):
        super().paint(painter)

        if self.width > 16:
            painter.drawPixmap(0, 0, ImageCache['MovPlat%sL' % self.imgType])
            painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['MovPlat%sR' % self.imgType])

            if self.width > 32:
                painter.drawTiledPixmap(60, 0, (self.width - 32) * 3.75, 60, ImageCache['MovPlat%sM' % self.imgType])

        else:
            painter.drawPixmap(0, 0, ImageCache['MovPlat%sL' % self.imgType])
            painter.drawPixmap(30, 0, ImageCache['MovPlat%sR' % self.imgType])


class SpriteImage_RouletteBlock(SLib.SpriteImage_Static):  # 195
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['RouletteBlock'],
        )

        self.yOffset = -4
        self.xOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RouletteBlock', 'block_roulette.png')


class SpriteImage_SnowEffect(SpriteImage_LiquidOrFog):  # 198
    def __init__(self, parent):
        super().__init__(parent)
        self.mid = ImageCache['SnowEffect']

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SnowEffect', 'snow.png')

    def dataChanged(self):
        super().dataChanged()

        self.paintZone = self.parent.spritedata[5] == 0

        self.parent.scene().update()

    def realViewZone(self, painter, zoneRect, viewRect):
        # For now, we only paint snow
        self.paintZone = self.parent.spritedata[5] == 0

        super().realViewZone(painter, zoneRect, viewRect)


class SpriteImage_MushroomPlatform(SLib.SpriteImage):  # 200
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False
        self.xOffset = -2

    @staticmethod
    def loadImages():
        if 'RedShroomL' in ImageCache: return
        ImageCache['RedShroomL'] = SLib.GetImg('red_mushroom_left.png')
        ImageCache['RedShroomM'] = SLib.GetImg('red_mushroom_middle.png')
        ImageCache['RedShroomR'] = SLib.GetImg('red_mushroom_right.png')
        ImageCache['GreenShroomL'] = SLib.GetImg('green_mushroom_left.png')
        ImageCache['GreenShroomM'] = SLib.GetImg('green_mushroom_middle.png')
        ImageCache['GreenShroomR'] = SLib.GetImg('green_mushroom_right.png')
        ImageCache['BlueShroomL'] = SLib.GetImg('blue_mushroom_left.png')
        ImageCache['BlueShroomM'] = SLib.GetImg('blue_mushroom_middle.png')
        ImageCache['BlueShroomR'] = SLib.GetImg('blue_mushroom_right.png')
        ImageCache['OrangeShroomL'] = SLib.GetImg('orange_mushroom_left.png')
        ImageCache['OrangeShroomM'] = SLib.GetImg('orange_mushroom_middle.png')
        ImageCache['OrangeShroomR'] = SLib.GetImg('orange_mushroom_right.png')

    def dataChanged(self):
        super().dataChanged()

        # get size/color
        self.color = self.parent.spritedata[4] & 1
        self.shroomsize = (self.parent.spritedata[5] >> 4) & 1
        self.height = 16 * (self.shroomsize + 1)

        # get width
        width = width = self.parent.spritedata[8] & 0xF
        if self.shroomsize == 0:
            self.width = (width << 4) + 32
            self.offset = (
                0 - (((width + 1) // 2) << 4),
                0,
            )
        else:
            self.width = (width << 5) + 64
            self.offset = (
                16 - (self.width / 2),
                -16,
            )

    def paint(self, painter):
        super().paint(painter)

        tilesize = 60 + (self.shroomsize * 60)
        if self.shroomsize == 0:
            if self.color == 0:
                color = 'Orange'
            else:
                color = 'Green'
        else:
            if self.color == 0:
                color = 'Red'
            else:
                color = 'Blue'

        painter.drawPixmap(0, 0, ImageCache[color + 'ShroomL'])
        painter.drawTiledPixmap(tilesize, 0, (self.width * 3.75) - (tilesize * 2), tilesize,
                                ImageCache[color + 'ShroomM'])
        painter.drawPixmap((self.width * 3.75) - tilesize, 0, ImageCache[color + 'ShroomR'])


class SpriteImage_LavaParticles(SpriteImage_LiquidOrFog):  # 201
    def __init__(self, parent):
        super().__init__(parent)
        self.paintZone = True

    @staticmethod
    def loadImages():
        if 'LavaParticlesA' in ImageCache: return
        ImageCache['LavaParticlesA'] = SLib.GetImg('lava_particles_a.png')
        ImageCache['LavaParticlesB'] = SLib.GetImg('lava_particles_b.png')
        ImageCache['LavaParticlesC'] = SLib.GetImg('lava_particles_c.png')

    def realViewZone(self, painter, zoneRect, viewRect):
        type = (self.parent.spritedata[5] & 0xF) % 3
        self.mid = (
            ImageCache['LavaParticlesA'],
            ImageCache['LavaParticlesB'],
            ImageCache['LavaParticlesC'],
        )[type]

        super().realViewZone(painter, zoneRect, viewRect)


class SpriteImage_IceBlock(SLib.SpriteImage_StaticMultiple):  # 203
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('IceBlock', 'ice_block.png')
        SLib.loadIfNotInImageCache('IceBlockCoin', 'ice_block_coin.png')

    def dataChanged(self):

        direction = self.parent.spritedata[4]

        if direction == 0:
            self.image = ImageCache['IceBlock']
        elif direction == 1:
            self.image = ImageCache['IceBlockCoin']
        else:
            self.image = ImageCache['IceBlock']

        super().dataChanged()


class SpriteImage_Fuzzy(SLib.SpriteImage_StaticMultiple):  # 204
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Fuzzy', 'fuzzy.png')
        SLib.loadIfNotInImageCache('FuzzyGiant', 'fuzzy_giant.png')

    def dataChanged(self):
        giant = self.parent.spritedata[4] & 1

        self.image = ImageCache['FuzzyGiant'] if giant else ImageCache['Fuzzy']
        self.offset = (-18, -18) if giant else (-7, -7)

        super().dataChanged()


class SpriteImage_Block_QuestionSwitch(SLib.SpriteImage_Static):  # 208
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Block_QSwitch'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Block_QSwitch', 'block_q_switch.png')


class SpriteImage_Block_PSwitch(SLib.SpriteImage_Static):  # 209
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Block_PSwitch'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Block_PSwitch', 'block_p_switch.png')


class SpriteImage_ControllerAutoscroll(SLib.SpriteImage_Static):  # 212
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerAutoscroll'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerAutoscroll', 'controller_autoscroll.png')


class SpriteImage_ControllerSpinOne(SLib.SpriteImage_Static):  # 214
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerSpinOne'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerSpinOne', 'controller_spinning_one.png')


class SpriteImage_Springboard(SLib.SpriteImage_Static):  # 215
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Springboard'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Springboard', 'springboard.png')


class SpriteImage_Boo(SLib.SpriteImage):  # 218, 220
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryImage(parent, 125, 128))
        self.aux[0].image = ImageCache['Boo1']
        self.aux[0].setPos(-15, -15)

        self.dimensions = (-1, -4, 22, 22)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Boo1', 'boo1.png')


class SpriteImage_BooCircle(SLib.SpriteImage):  # 221, 703
    def __init__(self, parent):
        super().__init__(parent, 3.75)

        self.BooAuxImage = QtGui.QPixmap(2560, 2560)
        self.BooAuxImage.fill(Qt.transparent)
        self.aux.append(SLib.AuxiliaryImage(parent, 2560, 2560))
        self.aux[0].image = self.BooAuxImage
        offsetX = ImageCache['Boo1'].width() / 4
        offsetY = ImageCache['Boo1'].height() / 4
        self.aux[0].setPos(-1280 + offsetX, -1280 + offsetY)
        self.aux[0].hover = False

    @staticmethod
    def loadImages():
        if 'Boo2' in ImageCache: return
        ImageCache['Boo1'] = SLib.GetImg('boo1.png')
        ImageCache['Boo2'] = SLib.GetImg('boo2.png')
        ImageCache['Boo3'] = SLib.GetImg('boo3.png')
        ImageCache['Boo4'] = SLib.GetImg('boo4.png')

    def dataChanged(self):
        # Constants (change these to fine-tune the boo positions)
        radiusMultiplier = 60  # pixels between boos per distance value
        radiusConstant = 60  # add to all radius values
        opacity = 0.5

        # Read the data
        outrad = self.parent.spritedata[2] & 15
        inrad = self.parent.spritedata[3] >> 4
        ghostnum = 1 + (self.parent.spritedata[3] & 15)
        differentRads = not (inrad == outrad)

        # Give up if the data is invalid
        if inrad > outrad:
            null = QtGui.QPixmap(5, 5)
            null.fill(Qt.transparent)
            self.aux[0].image = null
            return

        # Create a pixmap
        pix = QtGui.QPixmap(2560, 2560)
        pix.fill(Qt.transparent)
        paint = QtGui.QPainter(pix)
        paint.setOpacity(opacity)

        # Paint each boo
        for i in range(ghostnum):
            # Find the angle at which to place the ghost from the center
            MissingGhostWeight = 0.75 - (1 / ghostnum)  # approximate
            angle = math.radians(-360 * i / (ghostnum + MissingGhostWeight)) + 89.6

            # Since the origin of the boo img is in the top left, account for that
            offsetX = ImageCache['Boo1'].width() / 2
            offsetY = (ImageCache['Boo1'].height() / 2) + 40  # the circle is not centered

            # Pick a pixmap
            boo = ImageCache['Boo%d' % (1 if i == 0 else ((i - 1) % 3) + 2)]  # 1  2 3 4  2 3 4  2 3 4 ...

            # Find the abs pos, and paint the ghost at its inner position
            x = math.sin(angle) * ((inrad * radiusMultiplier) + radiusConstant) - offsetX
            y = -(math.cos(angle) * ((inrad * radiusMultiplier) + radiusConstant)) - offsetY
            paint.drawPixmap(x + 1280, y + 1280, boo)

            # Paint it at its outer position if it has one
            if differentRads:
                x = math.sin(angle) * ((outrad * radiusMultiplier) + radiusConstant) - offsetX
                y = -(math.cos(angle) * ((outrad * radiusMultiplier) + radiusConstant)) - offsetY
                paint.drawPixmap(x + 1280, y + 1280, boo)

        # Finish it
        paint = None
        self.aux[0].image = pix


class SpriteImage_BalloonYoshi(SLib.SpriteImage_Static):  # 224
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BalloonYoshi'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BalloonYoshi', 'balloonbabyyoshi.png')


class SpriteImage_Foo(SLib.SpriteImage_Static):  # 229
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Foo'],
        )

        self.yOffset = -13
        self.xOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Foo', 'foo.png')


class SpriteImage_Larry(SLib.SpriteImage_Static):  # 230
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Larry'],
            (-32, -32)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Larry', 'larry.png')


class SpriteImage_IceFloe(SLib.SpriteImage_StaticMultiple):  # 231
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -16
        self.yOffset = -16

    @staticmethod
    def loadImages():
        for i in range(16):
            SLib.loadIfNotInImageCache('IceFloe' + str(i), 'ice_floe_' + str(i) + '.png')

    def dataChanged(self):
        size = self.parent.spritedata[5] & 0xF

        self.image = ImageCache['IceFloe' + str(size)]

        super().dataChanged()


class SpriteImage_LightBlock(SLib.SpriteImage_Static):  # 232
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['LightBlock'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LightBlock', 'lightblock.png')


class SpriteImage_SpinningFirebar(SLib.SpriteImage):  # 235
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75
        )

        self.spritebox.shown = False
        self.aux.append(SLib.AuxiliaryCircleOutline(parent, 60, Qt.AlignCenter))

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FirebarBase', 'firebar_0.png')
        SLib.loadIfNotInImageCache('FirebarBaseWide', 'firebar_1.png')

    def dataChanged(self):
        super().dataChanged()

        size = self.parent.spritedata[5] & 0xF
        wideBase = (self.parent.spritedata[3] >> 4) & 1

        width = ((size * 2) + 1) * 40
        self.aux[0].setSize(width)
        if wideBase:
            currentAuxX = self.aux[0].x() - 16
            currentAuxY = self.aux[0].y() + 12
            self.aux[0].setPos(currentAuxX + 60, currentAuxY)
        else:
            currentAuxX = self.aux[0].x() + 16
            currentAuxY = self.aux[0].y() + 16
            self.aux[0].setPos(currentAuxX, currentAuxY)

        self.image = ImageCache['FirebarBase'] if not wideBase else ImageCache['FirebarBaseWide']
        self.xOffset = 0 if not wideBase else -8
        self.width = 16 if not wideBase else 32

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(0, 0, self.image)


class SpriteImage_Bolt(SLib.SpriteImage_StaticMultiple):  # 238
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.yOffset = 3

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoltMetal', 'bolt_metal.png')
        SLib.loadIfNotInImageCache('BoltStone', 'bolt_stone.png')

    def dataChanged(self):
        stone = self.parent.spritedata[4] & 1

        if stone == 1:
            self.image = ImageCache['BoltStone']
        else:
            self.image = ImageCache['BoltMetal']

        super().dataChanged()


class SpriteImage_TileGod(SLib.SpriteImage_StaticMultiple):  # 237, 673
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux2 = [SLib.AuxiliaryRectOutline(parent, 0, 0)]
        self.aux = self.aux2

    def dataChanged(self):
        super().dataChanged()

        type_ = self.parent.spritedata[4] >> 4
        self.width = (self.parent.spritedata[5] >> 4) * 16
        self.height = (self.parent.spritedata[5] & 0xF) * 16

        if not self.width:
            self.width = 16

        if not self.height:
            self.height = 16

        if type_ in [2, 5, 8, 9, 10, 11, 14, 15]:
            self.aux = self.aux2
            self.spritebox.shown = True
            self.image = None

            if [self.width, self.height] == [16, 16]:
                self.aux2[0].setSize(0, 0)
                return
        else:
            self.aux = []
            self.spritebox.shown = False

            if not type_:
                tile = SLib.Tiles[208]

            elif type_ == 1:
                tile = SLib.Tiles[48]

            elif type_ == 3:
                tile = SLib.Tiles[52]

            elif type_ == 4:
                tile = SLib.Tiles[51]

            elif type_ in [6, 12]:
                tile = SLib.Tiles[256 + 240]

            elif type_ in [7, 13]:
                tile = SLib.Tiles[256 + 4]

            if tile.exists:
                self.image = tile.main

            else:
                self.image = SLib.Tiles[0x200 * 4].main

        self.aux2[0].setSize(self.width * 3.75, self.height * 3.75)

    def paint(self, painter):
        if self.image is None:
            return

        painter.save()

        painter.setOpacity(self.alpha)
        painter.setRenderHint(painter.SmoothPixmapTransform)

        for yTile in range(self.height // 16):
            for xTile in range(self.width // 16):
                painter.drawPixmap(xTile * 60, yTile * 60, self.image)

        aux = self.aux2
        aux[0].paint(painter, None, None)

        painter.restore()


class SpriteImage_PricklyGoomba(SLib.SpriteImage_Static):  # 247
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PricklyGoomba'],
        )

        self.yOffset = -13
        # self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PricklyGoomba', 'prickly_goomba.png')


class SpriteImage_Wiggler(SLib.SpriteImage_Static):  # 249
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Wiggler'],
        )

        self.yOffset = -17
        # self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Wiggler', 'wiggler.png')


class SpriteImage_GiantBubble(SLib.SpriteImage):  # 251
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'GiantBubble0' not in ImageCache:
            for shape in range(4):
                ImageCache['GiantBubble%d' % shape] = SLib.GetImg('giant_bubble_%d.png' % shape)

    def dataChanged(self):
        super().dataChanged()

        self.shape = self.parent.spritedata[4] >> 4
        self.direction = self.parent.spritedata[5] & 15

        if self.shape == 0 or self.shape > 3:
            self.size = (122, 137)
        elif self.shape == 1:
            self.size = (76, 170)
        elif self.shape == 2:
            self.size = (160, 81)

        self.xOffset = -(self.width / 2) + 8
        self.yOffset = -(self.height / 2) + 8

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['GiantBubble%d' % self.shape])


class SpriteImage_MicroGoomba(SLib.SpriteImage_Static):  # 255
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MicroGoomba'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MicroGoomba', 'micro_goomba.png')


class SpriteImage_Muncher(SLib.SpriteImage_StaticMultiple):  # 259
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MuncherReg', 'muncher.png')
        SLib.loadIfNotInImageCache('MuncherFr', 'muncher_frozen.png')

    def dataChanged(self):
        isfrozen = self.parent.spritedata[5] & 1

        if isfrozen == 0:
            self.image = ImageCache['MuncherReg']
        else:
            self.image = ImageCache['MuncherFr']

        super().dataChanged()


class SpriteImage_Parabeetle(SLib.SpriteImage_Static):  # 261
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Parabeetle'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Parabeetle', 'parabeetle.png')


class SpriteImage_RollingHill(SLib.SpriteImage):  # 265
    RollingHillSizes = [2 * 40, 18 * 40, 32 * 40, 50 * 40, 64 * 40, 0, 0, 0, 18 * 40, 2 * 40, 30 * 40]

    def __init__(self, parent):
        super().__init__(parent, 3.75)

        size = (self.parent.spritedata[3] >> 4) & 0xF
        if size in [0, 9]:
            increase = self.parent.spritedata[4]
            realSize = self.RollingHillSizes[size] * (increase + 1)

        elif size > 10:
            realSize = 0

        else:
            realSize = self.RollingHillSizes[size]

        self.aux.append(SLib.AuxiliaryCircleOutline(parent, realSize))

    def dataChanged(self):
        super().dataChanged()

        size = (self.parent.spritedata[3] >> 4) & 0xF
        if size in [0, 9]:
            increase = self.parent.spritedata[4]
            realSize = self.RollingHillSizes[size] * (increase + 1)

        elif size > 10:
            realSize = 0

        else:
            realSize = self.RollingHillSizes[size]

        self.aux[0].setSize(realSize)
        self.aux[0].update()


class SpriteImage_TowerCog(SLib.SpriteImage_StaticMultiple):  # 269
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TowerCogS', 'tower_cog_s.png')
        SLib.loadIfNotInImageCache('TowerCogB', 'tower_cog_b.png')

    def dataChanged(self):
        size = self.parent.spritedata[4]

        if size == 1:
            self.image = ImageCache['TowerCogB']
            self.xOffset = -138
            self.yOffset = -144
        else:
            self.image = ImageCache['TowerCogS']
            self.xOffset = -92
            self.yOffset = -96

        super().dataChanged()
        self.parent.setZValue(-50000)


class SpriteImage_Amp(SLib.SpriteImage_StaticMultiple):  # 270
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Amp'],
            (-16, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Amp', 'amp.png')
        SLib.loadIfNotInImageCache('BigAmp', 'big_amp.png')

    def dataChanged(self):
        big = self.parent.spritedata[4] & 0xF

        if big == 1:
            self.image = ImageCache['BigAmp']
        else:
            self.image = ImageCache['Amp']

        shift = (self.parent.spritedata[5] >> 4) & 0xF

        if shift == 1:
            self.yOffset = -16
            self.xOffset = -8
        elif shift == 2:
            self.yOffset = -8
            self.xOffset = -16
        elif shift == 3:
            self.yOffset = -8
            self.xOffset = -8
        else:
            self.yOffset = -16
            self.xOffset = -16

        super().dataChanged()


class SpriteImage_CoinBubble(SLib.SpriteImage_Static):  # 281
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['CoinBubble'],
        )

        self.yOffset = -0.5 * (ImageCache['CoinBubble'].height() / 60 - 1) * 16
        self.xOffset = -0.5 * (ImageCache['CoinBubble'].width() / 60 - 1) * 16

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CoinBubble', 'coin_bubble.png')


class SpriteImage_KingBill(SLib.SpriteImage_StaticMultiple):  # 282
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        # self.xOffset = -7
        # self.yOffset = -2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('KingR', 'king_bill_r.png')
        SLib.loadIfNotInImageCache('KingL', 'king_bill_l.png')
        SLib.loadIfNotInImageCache('KingU', 'king_bill_u.png')
        SLib.loadIfNotInImageCache('KingD', 'king_bill_d.png')

    def dataChanged(self):

        direction = self.parent.spritedata[5]

        if direction == 0 or direction == 16 or direction == 32 or direction == 48 or direction == 64 or direction == 80 or direction == 96 or direction == 112 or direction == 128 or direction == 144 or direction == 160 or direction == 176 or direction == 192 or direction == 208 or direction == 224 or direction == 240:
            self.image = ImageCache['KingL']
            self.yOffset = -120
        elif direction == 1 or direction == 17 or direction == 33 or direction == 49 or direction == 65 or direction == 86 or direction == 97 or direction == 113 or direction == 129 or direction == 145 or direction == 161 or direction == 177 or direction == 193 or direction == 209 or direction == 225 or direction == 241:
            self.image = ImageCache['KingR']
            self.yOffset = -120
        elif direction == 2 or direction == 18 or direction == 34 or direction == 50 or direction == 66 or direction == 82 or direction == 98 or direction == 114 or direction == 129 or direction == 146 or direction == 162 or direction == 178 or direction == 194 or direction == 210 or direction == 226 or direction == 242:
            self.image = ImageCache['KingD']
            self.xOffset = -85
        elif direction == 3 or direction == 19 or direction == 35 or direction == 51 or direction == 67 or direction == 83 or direction == 99 or direction == 115 or direction == 130 or direction == 147 or direction == 163 or direction == 179 or direction == 195 or direction == 211 or direction == 227 or direction == 243:
            self.image = ImageCache['KingU']
            self.xOffset = -85
        else:
            self.image = ImageCache['KingR']
            self.yOffset = -120

        super().dataChanged()


class SpriteImage_LavaBubble(SLib.SpriteImage_Static):  # 286
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['LavaBubble'],
        )

        self.yOffset = -16
        self.xOffset = -16

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LavaBubble', 'lavabubble.png')


class SpriteImage_Bush(SLib.SpriteImage_StaticMultiple):  # 288
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.parent.setZValue(24000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BushSmall', 'bush_small.png')
        SLib.loadIfNotInImageCache('BushMedium', 'bush_medium.png')
        SLib.loadIfNotInImageCache('BushBig', 'bush_big.png')
        SLib.loadIfNotInImageCache('BushVeryBig', 'bush_very_big.png')
        SLib.loadIfNotInImageCache('BushSmallY', 'bush_small_y.png')
        SLib.loadIfNotInImageCache('BushMediumY', 'bush_medium_y.png')
        SLib.loadIfNotInImageCache('BushBigY', 'bush_big_y.png')
        SLib.loadIfNotInImageCache('BushVeryBigY', 'bush_very_big_y.png')

    def dataChanged(self):

        Btype = self.parent.spritedata[5]

        if Btype == 0:
            self.image = ImageCache['BushSmall']
            self.xOffset = -32
            self.yOffset = -32

        elif Btype == 1:
            self.image = ImageCache['BushMedium']
            self.xOffset = -32
            self.yOffset = -48

        elif Btype == 2:
            self.image = ImageCache['BushBig']
            self.xOffset = -40
            self.yOffset = -64

        elif Btype == 3:
            self.image = ImageCache['BushVeryBig']
            self.xOffset = -40
            self.yOffset = -78

        elif Btype == 16:
            self.image = ImageCache['BushSmallY']
            self.xOffset = -32
            self.yOffset = -32

        elif Btype == 17:
            self.image = ImageCache['BushMediumY']
            self.xOffset = -32
            self.yOffset = -48

        elif Btype == 18:
            self.image = ImageCache['BushBigY']
            self.xOffset = -40
            self.yOffset = -64

        elif Btype == 19:
            self.image = ImageCache['BushVeryBigY']
            self.xOffset = -40
            self.yOffset = -78

        else:
            self.image = ImageCache['BushSmall']
            self.xOffset = -32
            self.yOffset = -32

        super().dataChanged()


class SpriteImage_NoteBlock(SLib.SpriteImage_Static):  # 295
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['NoteBlock'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('NoteBlock', 'noteblock.png')


class SpriteImage_Clampy(SLib.SpriteImage_StaticMultiple):  # 298
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.offset = (-26, -53)

    @staticmethod
    def loadImages():
        if 'ClamEmpty' in ImageCache: return

        SLib.loadIfNotInImageCache('StarCoin', 'star_coin.png')

        if 'PSwitch' not in ImageCache:
            p = SLib.GetImg('p_switch.png', True)
            ImageCache['PSwitch'] = QtGui.QPixmap.fromImage(p)
            ImageCache['PSwitchU'] = QtGui.QPixmap.fromImage(p.mirrored(True, True))

        SLib.loadIfNotInImageCache('ClamEmpty', 'clam.png')
        SLib.loadIfNotInImageCache('1Up', '1up.png')

        overlays = (
            (65, 55, 'Star', ImageCache['StarCoin']),
            (100, 105, '1Up', ImageCache['1Up']),
            (100, 105, 'PSwitch', ImageCache['PSwitch']),
            (100, 105, 'PSwitchU', ImageCache['PSwitchU']),
        )
        for x, y, clamName, overlayImage in overlays:
            newPix = QtGui.QPixmap(ImageCache['ClamEmpty'])
            painter = QtGui.QPainter(newPix)
            painter.setOpacity(0.6)
            painter.drawPixmap(x, y, overlayImage)
            del painter
            ImageCache['Clam' + clamName] = newPix

        # 2 coins special case
        newPix = QtGui.QPixmap(ImageCache['ClamEmpty'])
        painter = QtGui.QPainter(newPix)
        painter.setOpacity(0.6)
        painter.drawPixmap(70, 105, SLib.Tiles[30].main)
        painter.drawPixmap(130, 105, SLib.Tiles[30].main)
        del painter
        ImageCache['Clam2Coin'] = newPix

    def dataChanged(self):

        holds = self.parent.spritedata[5] & 0xF
        switchdir = self.parent.spritedata[4] & 0xF

        holdsStr = 'Empty'
        if holds == 1:
            holdsStr = 'Star'
        elif holds == 2:
            holdsStr = '2Coin'
        elif holds == 3:
            holdsStr = '1Up'
        elif holds == 4:
            if switchdir == 1:
                holdsStr = 'PSwitchU'
            else:
                holdsStr = 'PSwitch'

        self.image = ImageCache['Clam' + holdsStr]

        super().dataChanged()


class SpriteImage_Lemmy(SLib.SpriteImage_Static):  # 296
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Lemmy'],
            (-8, -64),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Lemmy', 'lemmy.png')


class SpriteImage_Thwimp(SLib.SpriteImage_Static):  # 303
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Thwimp'],
        )

        self.yOffset = (1 - ImageCache['Thwimp'].height() / 60) * 16
        self.xOffset = -0.5 * (ImageCache['Thwimp'].width() / 60 - 1) * 16

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Thwimp', 'thwimp.png')


class SpriteImage_Blooper(SLib.SpriteImage_Static):  # 313
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Blooper'],
            (-3, -2),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Blooper', 'blooper.png')


class SpriteImage_Crystal(SLib.SpriteImage_StaticMultiple):  # 316
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        for i in range(11):
            SLib.loadIfNotInImageCache('Crystal' + str(i), 'crystal_' + str(i) + '.png')

    def dataChanged(self):
        size = self.parent.spritedata[4] & 0xF

        if size <= 10:
            self.image = ImageCache['Crystal' + str(size)]

        if size == 6:
            self.xOffset = -32
            self.yOffset = -16
        elif size == 7:
            self.xOffset = -16
            self.yOffset = -112
        else:
            self.xOffset = -16
            self.yOffset = -16

        super().dataChanged()


class SpriteImage_Broozer(SLib.SpriteImage_Static):  # 320
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Broozer'],
        )

        self.xOffset = -20
        self.yOffset = -20

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Broozer', 'broozer.png')


class SpriteImage_BlooperBabies(SLib.SpriteImage_Static):  # 322
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BlooperBabies'],
            (-5, -2),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BlooperBabies', 'blooper_babies.png')


class SpriteImage_Barrel(SLib.SpriteImage_Static):  # 323
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Barrel'],
        )

        self.xOffset = -7
        self.yOffset = -2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Barrel', 'barrel.png')


class SpriteImage_Cooligan(SLib.SpriteImage_StaticMultiple):  # 334
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -7
        self.yOffset = -2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CooliganL', 'cooligan_l.png')
        SLib.loadIfNotInImageCache('CooliganR', 'cooligan_r.png')

    def dataChanged(self):

        direction = self.parent.spritedata[5]

        if direction == 0:
            self.image = ImageCache['CooliganL']
        elif direction == 1:
            self.image = ImageCache['CooliganR']
        elif direction == 2:
            self.image = ImageCache['CooliganL']
        else:
            self.image = ImageCache['CooliganL']

        super().dataChanged()


class SpriteImage_PipeCooliganGenerator(SLib.SpriteImage):  # 335
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.size = (16, 32)
        self.yOffset = -16


class SpriteImage_Bramball(SLib.SpriteImage_Static):  # 336
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Bramball'],
        )

        self.xOffset = -30
        self.yOffset = -46

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Bramball', 'bramball.png')


class SpriteImage_WoodenBox(SLib.SpriteImage_StaticMultiple):  # 338
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Reg2x2', 'reg_box_2x2.png')
        SLib.loadIfNotInImageCache('Reg4x2', 'reg_box_4x2.png')
        SLib.loadIfNotInImageCache('Reg2x4', 'reg_box_2x4.png')
        SLib.loadIfNotInImageCache('Reg4x4', 'reg_box_4x4.png')
        SLib.loadIfNotInImageCache('Inv2x2', 'inv_box_2x2.png')
        SLib.loadIfNotInImageCache('Inv4x2', 'inv_box_4x2.png')
        SLib.loadIfNotInImageCache('Inv2x4', 'inv_box_2x4.png')
        SLib.loadIfNotInImageCache('Inv4x4', 'inv_box_4x4.png')

    def dataChanged(self):

        boxcolor = self.parent.spritedata[4]
        boxsize = self.parent.spritedata[5] >> 4

        if boxsize == 0 and boxcolor == 0:
            self.image = ImageCache['Reg2x2']
        elif boxsize == 1 and boxcolor == 0:
            self.image = ImageCache['Reg2x4']
        elif boxsize == 2 and boxcolor == 0:
            self.image = ImageCache['Reg4x2']
        elif boxsize == 3 and boxcolor == 0:
            self.image = ImageCache['Reg4x4']
        elif boxsize == 0 and boxcolor == 1 or boxcolor == 2:
            self.image = ImageCache['Inv2x2']
        elif boxsize == 1 and boxcolor == 1 or boxcolor == 2:
            self.image = ImageCache['Inv2x4']
        elif boxsize == 2 and boxcolor == 1 or boxcolor == 2:
            self.image = ImageCache['Inv4x2']
        elif boxsize == 3 and boxcolor == 1 or boxcolor == 2:
            self.image = ImageCache['Inv4x4']
        else:
            self.image = ImageCache['Reg2x2']  # let's not make some nonsense out of this

        super().dataChanged()


class SpriteImage_StoneBlock(SLib.SpriteImage_Static):  # 347
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    def paint(self, painter):
        super().paint(painter)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawPixmap(self.yOffset, self.xOffset, 60, 60, SLib.Tiles[52].main)


class SpriteImage_SuperGuide(SLib.SpriteImage_Static):  # 348
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SuperGuide'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SuperGuide', 'guide_block.png')


class SpriteImage_Pokey(SLib.SpriteImage):  # 351
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        ImageCache['PokeyTop'] = SLib.GetImg('pokey_top.png')
        ImageCache['PokeyMiddle'] = SLib.GetImg('pokey_middle.png')
        ImageCache['PokeyBottom'] = SLib.GetImg('pokey_bottom.png')
        ImageCache['PokeyTopD'] = SLib.GetImg('pokey_top_d.png')
        ImageCache['PokeyMiddleD'] = SLib.GetImg('pokey_middle_d.png')
        ImageCache['PokeyBottomD'] = SLib.GetImg('pokey_bottom_d.png')

    def dataChanged(self):

        self.rawlength = (self.parent.spritedata[5] & 0x0F) + 3
        self.upsideDown = self.parent.spritedata[4]

        self.length = self.rawlength * 60

        self.width = 27
        self.xOffset = -5.33

        self.height = (self.rawlength - 1) * 16 + 25
        self.yOffset = -1 * (self.rawlength * 16) + 32 - 25 + 1.33

        if self.upsideDown == 1:
            self.length = self.rawlength * 60

            self.width = 27
            self.xOffset = -5.33

            self.height = (self.rawlength - 1) * 16 + 25
            self.yOffset = 0

        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)

        # Not upside-down:
        if self.upsideDown is not 1:
            painter.drawPixmap(0, 0 + (self.length - 120) + 91, 100, 60, ImageCache['PokeyBottom'])
            painter.drawTiledPixmap(0, 91, 100, (self.length - 120), ImageCache['PokeyMiddle'])
            painter.drawPixmap(0, 0, 100, 91, ImageCache['PokeyTop'])

        # Upside Down
        else:
            painter.drawPixmap(0, 0 + (self.length - 120) + 60, 100, 91, ImageCache['PokeyTopD'])
            painter.drawTiledPixmap(0, 60, 100, (self.length - 120), ImageCache['PokeyMiddleD'])
            painter.drawPixmap(0, 0, 100, 60, ImageCache['PokeyBottomD'])


class SpriteImage_SpikeTop(SLib.SpriteImage_Static):  # 352
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SpikeTop'],
        )
        self.yOffset = -8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpikeTop', 'spike_top.png')

    def dataChanged(self):
        self.xOffset = -0.5 * (self.image.width() / 60 - 1) * 16
        super().dataChanged()


class SpriteImage_GoldenYoshi(SLib.SpriteImage_Static):  # 365
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GoldenYoshi'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GoldenYoshi', 'babyyoshiglowing.png')


class SpriteImage_Morton(SLib.SpriteImage_Static):  # 368
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Morton'],
            (-32, -48)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Morton', 'morton.png')


class SpriteImage_TorpedoLauncher(SLib.SpriteImage_Static):  # 378
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['TorpedoLauncher'],
        )

        # self.yOffset = -17
        self.xOffset = -22

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TorpedoLauncher', 'torpedo_launcher.png')


class SpriteImage_QBlockBYoshi(SLib.SpriteImage_StaticMultiple):  # 380
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BlueBYoshi', 'block_q_yoshi_b.png')
        SLib.loadIfNotInImageCache('PinkBYoshi', 'block_q_yoshi_p.png')
        SLib.loadIfNotInImageCache('YellBYoshi', 'block_q_yoshi_y.png')

    def dataChanged(self):
        super().dataChanged()

        color = self.parent.spritedata[5] & 0xF

        if color == 1:
            self.image = ImageCache['PinkBYoshi']
        elif color == 2:
            self.image = ImageCache['YellBYoshi']
        else:
            self.image = ImageCache['BlueBYoshi']


class SpriteImage_Wendy(SLib.SpriteImage_Static):  # 383
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Wendy'],
            (-16, -32)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Wendy', 'wendy.png')


class SpriteImage_Ludwig(SLib.SpriteImage_Static):  # 385
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Ludwig'],
            (-32, -32)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Ludwig', 'ludwig.png')


class SpriteImage_Roy(SLib.SpriteImage_Static):  # 389
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Roy'],
            (-48, -48)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Roy', 'roy.png')


class SpriteImage_Starman(SLib.SpriteImage_StaticMultiple):  # 395
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StarmanS', 'starman_s.png')
        SLib.loadIfNotInImageCache('StarmanB', 'starman_b.png')
        SLib.loadIfNotInImageCache('StarmanG', 'starman_g.png')

    def dataChanged(self):

        direction = self.parent.spritedata[4]

        if direction == 0:
            self.image = ImageCache['StarmanS']
            self.xOffset = -44
            self.yOffset = -32
        elif direction == 16:
            self.image = ImageCache['StarmanB']
            self.xOffset = -64
            self.yOffset = -52
        elif direction == 32:
            self.image = ImageCache['StarmanG']
            self.xOffset = -100
            self.yOffset = -100
        else:
            self.image = ImageCache['StarmanS']
            self.xOffset = -44
            self.yOffset = -32

        super().dataChanged()


class SpriteImage_GreenRing(SLib.SpriteImage_Static):  # 402
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GreenRing'],
        )

        self.yOffset = -14
        self.xOffset = -7

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GreenRing', 'green_ring.png')


class SpriteImage_Iggy(SLib.SpriteImage_Static):  # 403
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Iggy'],
            (-16, -48)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Iggy', 'iggy.png')


class SpriteImage_PipeUpEnterable(SpriteImage_Pipe):  # 404
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'U'
        self.extraHeight = 1

    def dataChanged(self):

        size = self.parent.spritedata[3]

        if size == 0:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0
        elif size == 1:
            self.big = False
            self.painted = True
            self.width = 32
            self.xOffset = 0
        elif size == 2:
            self.big = True
            self.painted = False
            self.width = 64
            self.xOffset = -16
        else:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0

        super().dataChanged()


class SpriteImage_BumpPlatform(SLib.SpriteImage):  # 407
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        ImageCache['BumpPlatformL'] = SLib.GetImg('bump_platform_l.png')
        ImageCache['BumpPlatformM'] = SLib.GetImg('bump_platform_m.png')
        ImageCache['BumpPlatformR'] = SLib.GetImg('bump_platform_r.png')

    def dataChanged(self):
        super().dataChanged()

        self.width = (self.parent.spritedata[8] & 0xF) << 4
        if not self.width:
            self.width = 1

    def paint(self, painter):
        super().paint(painter)

        if self.width > 32:
            painter.drawTiledPixmap(60, 0, ((self.width * 3.75) - 120), 60, ImageCache['BumpPlatformM'])

        if self.width == 24:
            painter.drawPixmap(0, 0, ImageCache['BumpPlatformR'])
            painter.drawPixmap(8, 0, ImageCache['BumpPlatformL'])
        else:
            # normal rendering
            painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['BumpPlatformR'])
            painter.drawPixmap(0, 0, ImageCache['BumpPlatformL'])


class SpriteImage_BigBrickBlock(SLib.SpriteImage):  # 422
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

        self.dimensions = (0, 16, 32, 32)

    def dataChanged(self):
        super().dataChanged()

        self.contents = self.parent.spritedata[9] & 0xF
        self.acorn = (self.parent.spritedata[6] >> 4) & 1

        items = {0: 48, 1: 26, 2: 16, 3: 16, 4: 21, 5: 22, 6: 20, 7: 17, 9: 25, 10: 27, 11: 18, 12: 19, 15: 23}

        self.dopaint = True
        self.image = None

        if self.acorn:
            self.tilenum = 24
        elif self.contents in items:
            self.tilenum = items[self.contents]
        else:
            self.dopaint = False
            if self.contents == 8:
                self.imagecache = ImageCache['BCstar']
            elif self.contents == 13:
                self.imagecache = ImageCache['BSpring']
            elif self.contents == 14:
                self.imagecache = ImageCache['BKinoko']
            else:
                self.dopaint = True
                self.tilenum = 49

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BCstar', 'block_c_star.png')
        SLib.loadIfNotInImageCache('BSpring', 'block_spring.png')
        SLib.loadIfNotInImageCache('BKinoko', 'block_kinoko_coin.png')

    def paint(self, painter):
        super().paint(painter)

        if self.dopaint:
            painter.drawPixmap(0, 0, 120, 120, SLib.Tiles[self.tilenum].main)
        else:
            painter.drawPixmap(0, 0, 120, 120, self.imagecache)


class SpriteImage_ToAirshipCannon(SLib.SpriteImage_Static):  # 424
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['AirshipCannon'],
            (-8, -32),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('AirshipCannon', 'airship_cannon.png')


class SpriteImage_SnowyBoxes(SLib.SpriteImage_StaticMultiple):  # 427
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SnowyBoxes1', 'snowy_box_1.png')
        SLib.loadIfNotInImageCache('SnowyBoxes2', 'snowy_box_2.png')
        SLib.loadIfNotInImageCache('SnowyBoxes3', 'snowy_box_3.png')

    def dataChanged(self):

        amount = self.parent.spritedata[5]

        if amount == 2:
            self.image = ImageCache['SnowyBoxes2']
            self.yOffset = -47.5
        elif amount == 3:
            self.image = ImageCache['SnowyBoxes3']
            self.yOffset = -95
        else:
            self.image = ImageCache['SnowyBoxes1']

        super().dataChanged()


class SpriteImage_Fliprus(SLib.SpriteImage_StaticMultiple):  # 441
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.yOffset = -16
        self.xOffset = -6

    @staticmethod
    def loadImages():
        if "FliprusL" not in ImageCache:
            fliprus = SLib.GetImg('fliprus.png', True)
            ImageCache['FliprusL'] = QtGui.QPixmap.fromImage(fliprus)
            ImageCache['FliprusR'] = QtGui.QPixmap.fromImage(fliprus.mirrored(True, False))

    def dataChanged(self):
        direction = self.parent.spritedata[4]

        if direction == 0:
            self.image = ImageCache['FliprusL']
        elif direction == 1:
            self.image = ImageCache['FliprusR']
        elif direction == 2:
            self.image = ImageCache['FliprusL']
        else:
            self.image = ImageCache['FliprusL']

        super().dataChanged()


class SpriteImage_BonyBeetle(SLib.SpriteImage_Static):  # 443
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BonyBeetle'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BonyBeetle', 'bony_beetle.png')


class SpriteImage_FliprusSnowball(SLib.SpriteImage_Static):  # 446
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Snowball'],
        )

        self.yOffset = -10
        # self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Snowball', 'snowball.png')


class SpriteImage_NabbitPlacement(SLib.SpriteImage_Static):  # 451
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['NabbitP'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('NabbitP', 'nabbit_placement.png')


class SpriteImage_ClapCrowd(SLib.SpriteImage_Static):  # 455
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ClapCrowd'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ClapCrowd', 'clap_crowd.png')


class SpriteImage_Bowser(SLib.SpriteImage_Static):  # 462
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Bowser'],
            (-48, -80),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Bowser', 'bowser.png')


class SpriteImage_BowserBridge(SLib.SpriteImage_StaticMultiple):  # 464
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BowserBridgeL', 'bowser_bridge_l.png')
        SLib.loadIfNotInImageCache('BowserBridgeM', 'bowser_bridge_m.png')
        SLib.loadIfNotInImageCache('BowserBridgeR', 'bowser_bridge_r.png')

    def dataChanged(self):
        self.piece = self.parent.spritedata[5] & 0xF

        if self.piece == 1:
            self.image = ImageCache['BowserBridgeR']
        elif self.piece == 2:
            self.image = ImageCache['BowserBridgeL']
        else:
            self.image = ImageCache['BowserBridgeM']

        super().dataChanged()


class SpriteImage_BowserShutter(SLib.SpriteImage_Static):  # 467
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BowserShutter'],
            (0, 16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BowserShutter', 'bowser_shutter.png')


class SpriteImage_BigGoomba(SLib.SpriteImage_Static):  # 472
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigGoomba'],
        )

        self.yOffset = -20

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigGoomba', 'big_goomba.png')


class SpriteImage_MegaBowser(SLib.SpriteImage_Static):  # 473
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MegaBowser'],
        )

        self.yOffset = -245
        self.xOffset = -210

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MegaBowser', 'mega_bowser.png')


class SpriteImage_BigQBlock(SLib.SpriteImage):  # 475
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

        self.dimensions = (0, 16, 32, 32)

    def dataChanged(self):
        super().dataChanged()

        self.contents = self.parent.spritedata[9] & 0xF
        self.acorn = (self.parent.spritedata[6] >> 4) & 1

        items = {0: 0x800 + 160, 1: 49, 2: 32, 3: 32, 4: 37, 5: 38, 6: 36, 7: 33, 8: 34, 9: 41, 12: 35, 13: 42, 15: 39}

        self.dopaint = True
        self.image = None

        if self.acorn:
            self.tilenum = 40
        elif self.contents in items:
            self.tilenum = items[self.contents]
        else:
            self.dopaint = False
            if self.contents == 10:
                self.imagecache = ImageCache['Q10']
            elif self.contents == 11:
                self.imagecache = ImageCache['QKinokoUP']
            elif self.contents == 14:
                self.imagecache = ImageCache['QKinoko']
            else:
                self.dopaint = True
                self.tilenum = 49

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Q10', 'block_q_10.png')
        SLib.loadIfNotInImageCache('QKinokoUP', 'block_q_kinoko_up.png')
        SLib.loadIfNotInImageCache('QKinoko', 'block_q_kinoko_coin.png')

    def paint(self, painter):
        super().paint(painter)

        if self.dopaint:
            painter.drawPixmap(0, 0, 120, 120, SLib.Tiles[self.tilenum].main)
        else:
            painter.drawPixmap(0, 0, 120, 120, self.imagecache)


class SpriteImage_BigKoopaTroopa(SLib.SpriteImage_StaticMultiple):  # 476
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.yOffset = -32

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigKoopaG', 'big_koopa_green.png')
        SLib.loadIfNotInImageCache('BigKoopaR', 'big_koopa_red.png')

    def dataChanged(self):

        color = self.parent.spritedata[5] & 1

        if color == 0:
            self.image = ImageCache['BigKoopaG']
        elif color == 1:
            self.image = ImageCache['BigKoopaR']
        else:
            self.image = ImageCache['BigKoopaG']

        super().dataChanged()


class SpriteImage_MovementControlledStarCoin(SLib.SpriteImage_Static):  # 480
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MovementStarCoin'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovementStarCoin', 'star_coin.png')


class SpriteImage_WaddleWing(SLib.SpriteImage_StaticMultiple):  # 481
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )  # What image to load is taken care of later

        self.yOffset = -9
        self.xOffset = -9

    @staticmethod
    def loadImages():
        waddlewing = SLib.GetImg('waddlewing.png', True)

        ImageCache['WaddlewingL'] = QtGui.QPixmap.fromImage(waddlewing)
        ImageCache['WaddlewingR'] = QtGui.QPixmap.fromImage(waddlewing.mirrored(True, False))

    def dataChanged(self):
        rawdir = self.parent.spritedata[5]

        if rawdir == 2:
            self.image = ImageCache['WaddlewingR']
        else:
            self.image = ImageCache['WaddlewingL']

        super().dataChanged()


class SpriteImage_MultiSpinningFirebar(SLib.SpriteImage):  # 483
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75
        )

        self.spritebox.shown = False
        self.aux.append(SLib.AuxiliaryCircleOutline(parent, 60, Qt.AlignCenter))

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FirebarBase', 'firebar_0.png')
        SLib.loadIfNotInImageCache('FirebarBaseWide', 'firebar_1.png')

    def dataChanged(self):
        super().dataChanged()

        size = self.parent.spritedata[5] & 0xF
        wideBase = (self.parent.spritedata[3] >> 4) & 1

        width = ((size * 2) + 1) * 40
        self.aux[0].setSize(width)
        if wideBase:
            currentAuxX = self.aux[0].x() - 16
            currentAuxY = self.aux[0].y() + 12
            self.aux[0].setPos(currentAuxX + 60, currentAuxY)
        else:
            currentAuxX = self.aux[0].x() + 16
            currentAuxY = self.aux[0].y() + 16
            self.aux[0].setPos(currentAuxX, currentAuxY)

        self.image = ImageCache['FirebarBase'] if not wideBase else ImageCache['FirebarBaseWide']
        self.xOffset = 0 if not wideBase else -8
        self.width = 16 if not wideBase else 32

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(0, 0, self.image)


class SpriteImage_FrameSetting(SLib.SpriteImage_Static):  # 486
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['FrameSetting'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FrameSetting', 'frame_setting.png')


class SpriteImage_MovingGrassPlatform(SLib.SpriteImage):  # 499
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        # self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.parent.setZValue(24999)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        ImageCache['MovGTopL'] = SLib.GetImg('mov_grass_top_l.png')
        ImageCache['MovGTopM'] = SLib.GetImg('mov_grass_top_m.png')
        ImageCache['MovGTopR'] = SLib.GetImg('mov_grass_top_r.png')
        ImageCache['MovGMiddleL'] = SLib.GetImg('mov_grass_middle_l.png')
        ImageCache['MovGMiddleM'] = SLib.GetImg('mov_grass_middle_m.png')
        ImageCache['MovGMiddleR'] = SLib.GetImg('mov_grass_middle_r.png')

    def dataChanged(self):
        super().dataChanged()

        self.width = (self.parent.spritedata[8] & 0xF) * 16 + 16
        if self.width == 16: self.width *= 2

        if self.width / 16 < 3:
            self.height = 240
        else:
            self.height = 256

        zOrder = (self.parent.spritedata[5] & 0xF) + 1
        self.parent.setZValue(24999 // zOrder)

    def paint(self, painter):
        super().paint(painter)

        # Top
        if self.width / 16 < 3:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovGTopL'])
            painter.drawPixmap(60, 0, 60, 60, ImageCache['MovGTopR'])
        else:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovGTopL'])
            painter.drawTiledPixmap(60, 0, (self.width / 16 - 2) * 60, 60, ImageCache['MovGTopM'])
            painter.drawPixmap(60 + ((self.width / 16 - 2) * 60), 0, 60, 60, ImageCache['MovGTopR'])

        # Bottom
        if self.width / 16 < 3:
            painter.drawPixmap(0, 60, 60, 840, ImageCache['MovGMiddleL'])
            painter.drawPixmap(60, 60, 60, 840, ImageCache['MovGMiddleR'])
        else:
            painter.drawPixmap(0, 60, 60, 900, ImageCache['MovGMiddleL'])
            painter.drawTiledPixmap(60, 60, ((self.width / 16) - 2) * 60, 900, ImageCache['MovGMiddleM'])
            painter.drawPixmap(60 + ((self.width / 16 - 2) * 60), 60, 60, 900, ImageCache['MovGMiddleR'])


class SpriteImage_PaintGoal(SLib.SpriteImage_StaticMultiple):  # 503
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -48
        self.yOffset = -160

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PaintFlagReg', 'flag_paint_reg.png')
        SLib.loadIfNotInImageCache('PaintFlagSec', 'flag_paint_sec.png')

    def dataChanged(self):

        secret = self.parent.spritedata[2] >> 4

        if secret == 1:
            self.image = ImageCache['PaintFlagSec']
        else:
            self.image = ImageCache['PaintFlagReg']

        super().dataChanged()


class SpriteImage_Grrrol(SLib.SpriteImage_Static):  # 504
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GrrrolSmall'],
        )

        self.yOffset = -12
        # self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GrrrolSmall', 'grrrol_small.png')


class SpriteImage_ShootingStar(SLib.SpriteImage_Static):  # 507
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ShootingStar'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ShootingStar', 'shooting_star.png')


class SpriteImage_PipeJoint(SLib.SpriteImage_Static):  # 513
    def __init__(self, parent, scale=3.75):
        super().__init__(
            parent,
            scale,
            ImageCache['PipeJoint'])

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeJoint', 'pipe_joint.png')


class SpriteImage_PipeJointSmall(SLib.SpriteImage_Static):  # 514
    def __init__(self, parent, scale=3.75):
        super().__init__(
            parent,
            scale,
            ImageCache['PipeJointSmall'])

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeJointSmall', 'pipe_joint_mini.png')


class SpriteImage_BowserSwitch(SLib.SpriteImage_Static):  # 520
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BowserSwitch'],
            (-48, -64),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BowserSwitch', 'bowser_switch.png')


class SpriteImage_MiniPipeRight(SpriteImage_Pipe):  # 516
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.mini = True
        self.direction = 'R'


class SpriteImage_MiniPipeLeft(SpriteImage_Pipe):  # 517
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.mini = True
        self.direction = 'L'


class SpriteImage_MiniPipeUp(SpriteImage_Pipe):  # 518
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.mini = True
        self.direction = 'U'


class SpriteImage_MiniPipeDown(SpriteImage_Pipe):  # 519
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.mini = True
        self.direction = 'D'


class SpriteImage_FlyingQBlockAmbush(SLib.SpriteImage):  # 523
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

        self.dimensions = (-12, -16, 42, 32)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FlyingQBlock', 'flying_qblock.png')

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['FlyingQBlock'])
        painter.drawPixmap(45, 57.5, SLib.Tiles[0x800 + 160].main)


class SpriteImage_RockyWrench(SLib.SpriteImage_Static):  # 536
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['RockyWrench'],
            (4, -41),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RockyWrench', 'rocky_wrench.png')


class SpriteImage_MushroomMovingPlatform(SLib.SpriteImage):  # 544
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        ImageCache['PinkL'] = SLib.GetImg('pink_mushroom_skinny_l.png')
        ImageCache['PinkM'] = SLib.GetImg('pink_mushroom_skinny_m.png')
        ImageCache['PinkR'] = SLib.GetImg('pink_mushroom_skinny_r.png')
        ImageCache['CyanL'] = SLib.GetImg('cyan_mushroom_skinny_l.png')
        ImageCache['CyanM'] = SLib.GetImg('cyan_mushroom_skinny_m.png')
        ImageCache['CyanR'] = SLib.GetImg('cyan_mushroom_skinny_r.png')
        ImageCache['PinkStemT'] = SLib.GetImg('pink_mushroom_stem_top.png')
        ImageCache['PinkStemM'] = SLib.GetImg('pink_mushroom_stem_middle.png')
        ImageCache['PinkStemB'] = SLib.GetImg('pink_mushroom_stem_bottom.png')
        ImageCache['CyanStemT'] = SLib.GetImg('cyan_mushroom_stem_top.png')
        ImageCache['CyanStemM'] = SLib.GetImg('cyan_mushroom_stem_middle.png')
        ImageCache['CyanStemB'] = SLib.GetImg('cyan_mushroom_stem_bottom.png')

    def dataChanged(self):
        super().dataChanged()

        self.color = self.parent.spritedata[7]
        if self.color:
            self.color = 1

        self.width = ((self.parent.spritedata[4] >> 4) + 3) * 16
        self.height = ((self.parent.spritedata[6] >> 4) + 2.5) * 16

        self.xOffset = -0.5 * (self.width - 16)

    def paint(self, painter):
        super().paint(painter)

        # Top
        painter.drawPixmap(0, 0, ImageCache['CyanL' if self.color else 'PinkL'])
        painter.drawTiledPixmap(60, 0, (self.width - 32) * 3.75, 60, ImageCache['CyanM' if self.color else 'PinkM'])
        painter.drawPixmap((self.width - 16) * 3.75, 0, 60, 60, ImageCache['CyanR' if self.color else 'PinkR'])

        # Stem
        for row in range(int((self.height - 24) / 16)):
            if not row:
                painter.drawPixmap((-self.xOffset - 16) * 3.75, 60,
                                   ImageCache['CyanStemT' if self.color else 'PinkStemT'])

            elif row == 1:
                painter.drawPixmap(-self.xOffset * 3.75, 150, ImageCache['CyanStemM' if self.color else 'PinkStemM'])

            else:
                painter.drawPixmap(-self.xOffset * 3.75, (row * 60) + 90,
                                   ImageCache['CyanStemB' if self.color else 'PinkStemB'])

        # trololo
        if self.height == 40:
            painter.drawPixmap(-self.xOffset * 3.75, (self.height - 8) * 3.75,
                               ImageCache['CyanStemB' if self.color else 'PinkStemM'])

        else:
            painter.drawPixmap(-self.xOffset * 3.75, (self.height - 8) * 3.75,
                               ImageCache['CyanStemB' if self.color else 'PinkStemB'])


class SpriteImage_Flowers(SLib.SpriteImage_StaticMultiple):  # 546
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Flower1', 'flower_1.png')
        SLib.loadIfNotInImageCache('Flower2', 'flower_2.png')
        SLib.loadIfNotInImageCache('Flower3', 'flower_3.png')
        SLib.loadIfNotInImageCache('Flower4', 'flower_4.png')
        SLib.loadIfNotInImageCache('Flower5', 'flower_5.png')
        SLib.loadIfNotInImageCache('Flower15', 'flower_15.png')
        SLib.loadIfNotInImageCache('WTF', 'wtf.png')

    #    TODO: Find out wtf are the other nybbles other than 0.

    def dataChanged(self):

        otherid = self.parent.spritedata[5]

        if otherid == 33:
            self.image = ImageCache['Flower1']
            self.xOffset = -32
        elif otherid == 35:
            self.image = ImageCache['Flower5']
            self.xOffset = -24
        elif otherid == 39:
            self.image = ImageCache['Flower4']
            self.xOffset = -24
        elif otherid == 43:
            self.image = ImageCache['Flower2']
        elif otherid == 44:
            self.image = ImageCache['Flower3']
            self.xOffset = -16
        elif otherid == 47:
            self.image = ImageCache['Flower15']
            self.xOffset = -32
        else:
            self.image = ImageCache['WTF']

        super().dataChanged()


class SpriteImage_RecordSignboard(SLib.SpriteImage):  # 561
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def dataChanged(self):
        super().dataChanged()

        w = ((self.parent.spritedata[2] >> 4) & 0xF) + 1
        self.xOffset = -0.5 * (w - 1) * 16
        self.aux[0].setSize(w * 60, 60)


class SpriteImage_NabbitMetal(SLib.SpriteImage_Static):  # 566
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['NabbitMetal'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('NabbitMetal', 'nabbit_metal.png')


class SpriteImage_NabbitPrize(SLib.SpriteImage_Static):  # 569
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['NabbitPrize'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('NabbitPrize', 'nabbit_prize.png')


class SpriteImage_StoneSpike(SLib.SpriteImage_Static):  # 579
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['StoneSpike'],
            (-16, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StoneSpike', 'stone_spike.png')


class SpriteImage_CheepGreen(SLib.SpriteImage_Static):  # 588
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['CheepGreen'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CheepGreen', 'cheep_green.png')


class SpriteImage_SumoBro(SLib.SpriteImage_Static):  # 593
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SumoBro'],
        )

        self.xOffset = -18
        self.yOffset = -20

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SumoBro', 'sumo_bro.png')


class SpriteImage_Goombrat(SLib.SpriteImage_Static):  # 595
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Goombrat'],
        )

        # self.yOffset = -17
        # self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Goombrat', 'goombrat.png')


class SpriteImage_MoonBlock(SLib.SpriteImage_Static):  # 600
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MoonBlock'],
        )

        self.yOffset = -4
        self.xOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MoonBlock', 'moon_block.png')


class SpriteImage_PacornBlock(SLib.SpriteImage_Static):  # 612
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PacornBlock'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PacornBlock', 'pacorn_block.png')


class SpriteImage_SteelBlock(SLib.SpriteImage_Static):  # 618
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    def paint(self, painter):
        super().paint(painter)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawPixmap(self.yOffset, self.xOffset, 60, 60, SLib.Tiles[54].main)


class SpriteImage_BlueRing(SLib.SpriteImage_Static):  # 662
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BlueRing'],
        )

        self.yOffset = -14
        self.xOffset = -7

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BlueRing', 'blue_ring.png')

    ################################################################


################## SPRITE CLASSES ##############################
################################################################

ImageClasses = {
    0: SpriteImage_Goomba,
    1: SpriteImage_Paragoomba,
    2: SpriteImage_PipePiranhaUp,
    3: SpriteImage_PipePiranhaDown,
    4: SpriteImage_PipePiranhaLeft,
    5: SpriteImage_PipePiranhaRight,
    6: SpriteImage_PipePiranhaUpFire,
    7: SpriteImage_PipePiranhaDownFire,
    8: SpriteImage_PipePiranhaLeftFire,
    9: SpriteImage_PipePiranhaRightFire,
    10: SpriteImage_PipePiranhaUpFire,
    11: SpriteImage_PipePiranhaDownFire,
    12: SpriteImage_PipePiranhaLeftFire,
    13: SpriteImage_PipePiranhaRightFire,
    14: SpriteImage_GroundPiranha,
    15: SpriteImage_GroundVenustrap,
    16: SpriteImage_GroundVenustrap,
    17: SpriteImage_BigGroundPiranha,
    18: SpriteImage_BigGroundVenustrap,
    19: SpriteImage_KoopaTroopa,
    20: SpriteImage_KoopaParatroopa,
    21: SpriteImage_KoopaParatroopa,
    22: SpriteImage_BuzzyBeetle,
    23: SpriteImage_Spiny,
    25: SpriteImage_MidwayFlag,
    29: SpriteImage_LimitU,
    30: SpriteImage_LimitD,
    31: SpriteImage_Flagpole,
    32: SpriteImage_ArrowSignboard,
    36: SpriteImage_ZoneTrigger,
    41: SpriteImage_LocationTrigger,
    44: SpriteImage_RedRing,
    45: SpriteImage_StarCoin,
    46: SpriteImage_LineControlledStarCoin,
    47: SpriteImage_BoltControlledStarCoin,
    48: SpriteImage_MvmtRotControlledStarCoin,
    49: SpriteImage_RedCoin,
    50: SpriteImage_GreenCoin,
    51: SpriteImage_MontyMole,
    54: SpriteImage_YoshiBerry,
    55: SpriteImage_KoopaTroopa,
    59: SpriteImage_QBlock,
    60: SpriteImage_BrickBlock,
    61: SpriteImage_InvisiBlock,
    63: SpriteImage_StalkingPiranha,
    64: SpriteImage_WaterPlant,
    65: SpriteImage_Coin,
    66: SpriteImage_Coin,
    67: SpriteImage_Swooper,
    68: SpriteImage_ControllerSwaying,
    69: SpriteImage_ControllerSpinning,
    70: SpriteImage_TwoWay,
    72: SpriteImage_MovingLandBlock,
    73: SpriteImage_CoinSpawner,
    74: SpriteImage_HuckitCrab,
    75: SpriteImage_BroIce,
    76: SpriteImage_BroHammer,
    78: SpriteImage_BroBoomerang,
    79: SpriteImage_BroFire,
    87: SpriteImage_MovingCoin,
    88: SpriteImage_Water,
    89: SpriteImage_Lava,
    90: SpriteImage_Poison,
    91: SpriteImage_Quicksand,
    92: SpriteImage_Fog,
    94: SpriteImage_BouncyCloud,
    96: SpriteImage_Lamp,
    97: SpriteImage_BackCenter,
    98: SpriteImage_PipeEnemyGenerator,
    101: SpriteImage_CheepCheep,
    102: SpriteImage_Useless,
    104: SpriteImage_QuestionSwitch,
    105: SpriteImage_PSwitch,
    108: SpriteImage_GhostHouseDoor,
    109: SpriteImage_TowerBossDoor,
    110: SpriteImage_CastleBossDoor,
    115: SpriteImage_SpecialExit,
    117: SpriteImage_Spinner,
    120: SpriteImage_SpinyCheep,
    123: SpriteImage_SandPillar,
    134: SpriteImage_Useless,
    135: SpriteImage_Thwomp,
    136: SpriteImage_GiantThwomp,
    137: SpriteImage_DryBones,
    138: SpriteImage_BigDryBones,
    139: SpriteImage_PipeUp,
    140: SpriteImage_PipeDown,
    141: SpriteImage_PipeLeft,
    142: SpriteImage_PipeRight,
    143: SpriteImage_BubbleYoshi,
    145: SpriteImage_PalmTree,
    146: SpriteImage_MovPipe,
    147: SpriteImage_QBlock,
    148: SpriteImage_BrickBlock,
    150: SpriteImage_StoneEye,
    152: SpriteImage_POWBlock,
    154: SpriteImage_FlyingQBlock,
    155: SpriteImage_PipeCannon,
    156: SpriteImage_WaterGeyser,
    158: SpriteImage_CoinOutline,
    159: SpriteImage_ExpandingPipeRight,
    160: SpriteImage_ExpandingPipeLeft,
    161: SpriteImage_ExpandingPipeUp,
    162: SpriteImage_ExpandingPipeDown,
    163: SpriteImage_WaterGeyserLocation,
    166: SpriteImage_CoinOutline,
    167: SpriteImage_CoinBlue,
    168: SpriteImage_ClapCoin,
    169: SpriteImage_ClapCoin,
    170: SpriteImage_Parabomb,
    175: SpriteImage_Mechakoopa,
    176: SpriteImage_AirshipCannon,
    177: SpriteImage_Crash,
    178: SpriteImage_Crash,
    180: SpriteImage_Spike,
    182: SpriteImage_MovingPlatform,
    183: SpriteImage_FallingIcicle,
    184: SpriteImage_GiantIcicle,
    186: SpriteImage_MovingPlatform,
    190: SpriteImage_QBlock,
    191: SpriteImage_BrickBlock,
    192: SpriteImage_MovingPlatformSpawner,
    193: SpriteImage_LineMovingPlatform,
    195: SpriteImage_RouletteBlock,
    198: SpriteImage_SnowEffect,
    200: SpriteImage_MushroomPlatform,
    201: SpriteImage_LavaParticles,
    203: SpriteImage_IceBlock,
    204: SpriteImage_Fuzzy,
    205: SpriteImage_QBlock,
    208: SpriteImage_Block_QuestionSwitch,
    209: SpriteImage_Block_PSwitch,
    212: SpriteImage_ControllerAutoscroll,
    214: SpriteImage_ControllerSpinOne,
    215: SpriteImage_Springboard,
    218: SpriteImage_Boo,
    220: SpriteImage_Boo,
    221: SpriteImage_BooCircle,
    224: SpriteImage_BalloonYoshi,
    229: SpriteImage_Foo,
    230: SpriteImage_Larry,
    231: SpriteImage_IceFloe,
    232: SpriteImage_LightBlock,
    233: SpriteImage_QBlock,
    234: SpriteImage_BrickBlock,
    235: SpriteImage_SpinningFirebar,
    237: SpriteImage_TileGod,
    238: SpriteImage_Bolt,
    243: SpriteImage_BubbleYoshi,
    244: SpriteImage_Useless,
    247: SpriteImage_PricklyGoomba,
    249: SpriteImage_Wiggler,
    251: SpriteImage_GiantBubble,
    255: SpriteImage_MicroGoomba,
    256: SpriteImage_Crash,
    259: SpriteImage_Muncher,
    261: SpriteImage_Parabeetle,
    265: SpriteImage_RollingHill,
    269: SpriteImage_TowerCog,
    270: SpriteImage_Amp,
    281: SpriteImage_CoinBubble,
    282: SpriteImage_KingBill,
    286: SpriteImage_LavaBubble,
    288: SpriteImage_Bush,
    295: SpriteImage_NoteBlock,
    298: SpriteImage_Clampy,
    296: SpriteImage_Lemmy,
    303: SpriteImage_Thwimp,
    306: SpriteImage_Crash,
    310: SpriteImage_Crash,
    312: SpriteImage_Crash,
    313: SpriteImage_Blooper,
    314: SpriteImage_Crash,
    316: SpriteImage_Crystal,
    318: SpriteImage_LavaBubble,
    319: SpriteImage_Crash,
    320: SpriteImage_Broozer,
    322: SpriteImage_BlooperBabies,
    323: SpriteImage_Barrel,
    325: SpriteImage_Coin,
    326: SpriteImage_Coin,
    328: SpriteImage_Coin,
    334: SpriteImage_Cooligan,
    335: SpriteImage_PipeCooliganGenerator,
    336: SpriteImage_Bramball,
    338: SpriteImage_WoodenBox,
    345: SpriteImage_Crash,
    347: SpriteImage_StoneBlock,
    348: SpriteImage_SuperGuide,
    351: SpriteImage_Pokey,
    352: SpriteImage_SpikeTop,
    355: SpriteImage_Crash,
    357: SpriteImage_Fuzzy,
    358: SpriteImage_Crash,
    360: SpriteImage_Crash,
    365: SpriteImage_GoldenYoshi,
    368: SpriteImage_Morton,
    376: SpriteImage_Crash,
    377: SpriteImage_Crash,
    378: SpriteImage_TorpedoLauncher,
    380: SpriteImage_QBlockBYoshi,
    383: SpriteImage_Wendy,
    385: SpriteImage_Ludwig,
    389: SpriteImage_Roy,
    395: SpriteImage_Starman,
    397: SpriteImage_QBlock,
    398: SpriteImage_BrickBlock,
    402: SpriteImage_GreenRing,
    403: SpriteImage_Iggy,
    404: SpriteImage_PipeUpEnterable,
    405: SpriteImage_Crash,
    407: SpriteImage_BumpPlatform,
    422: SpriteImage_BigBrickBlock,
    424: SpriteImage_ToAirshipCannon,
    427: SpriteImage_SnowyBoxes,
    436: SpriteImage_Crash,
    439: SpriteImage_Crash,
    441: SpriteImage_Fliprus,
    443: SpriteImage_BonyBeetle,
    446: SpriteImage_FliprusSnowball,
    449: SpriteImage_Useless,
    451: SpriteImage_NabbitPlacement,
    452: SpriteImage_Crash,
    455: SpriteImage_ClapCrowd,
    456: SpriteImage_Useless,
    462: SpriteImage_Bowser,
    464: SpriteImage_BowserBridge,
    467: SpriteImage_BowserShutter,
    472: SpriteImage_BigGoomba,
    473: SpriteImage_MegaBowser,
    475: SpriteImage_BigQBlock,
    476: SpriteImage_BigKoopaTroopa,
    479: SpriteImage_Crash,
    480: SpriteImage_MovementControlledStarCoin,
    481: SpriteImage_WaddleWing,
    483: SpriteImage_MultiSpinningFirebar,
    484: SpriteImage_ControllerSpinning,
    486: SpriteImage_FrameSetting,
    496: SpriteImage_Coin,
    499: SpriteImage_MovingGrassPlatform,
    503: SpriteImage_PaintGoal,
    504: SpriteImage_Grrrol,
    507: SpriteImage_ShootingStar,
    511: SpriteImage_PipeDown,
    513: SpriteImage_PipeJoint,
    514: SpriteImage_PipeJointSmall,
    516: SpriteImage_MiniPipeRight,
    517: SpriteImage_MiniPipeLeft,
    518: SpriteImage_MiniPipeUp,
    519: SpriteImage_MiniPipeDown,
    520: SpriteImage_BowserSwitch,
    521: SpriteImage_Crash,
    522: SpriteImage_Crash,
    523: SpriteImage_FlyingQBlockAmbush,
    525: SpriteImage_QBlock,
    526: SpriteImage_BrickBlock,
    529: SpriteImage_Crash,
    536: SpriteImage_RockyWrench,
    538: SpriteImage_Crash,
    542: SpriteImage_MushroomPlatform,
    544: SpriteImage_MushroomMovingPlatform,
    546: SpriteImage_Flowers,
    551: SpriteImage_Useless,
    555: SpriteImage_Crash,
    556: SpriteImage_Crash,
    561: SpriteImage_RecordSignboard,
    566: SpriteImage_NabbitMetal,
    569: SpriteImage_NabbitPrize,
    572: SpriteImage_Crash,
    579: SpriteImage_StoneSpike,
    588: SpriteImage_CheepGreen,
    593: SpriteImage_SumoBro,
    595: SpriteImage_Goombrat,
    600: SpriteImage_MoonBlock,
    612: SpriteImage_PacornBlock,
    615: SpriteImage_CheepCheep,
    618: SpriteImage_SteelBlock,
    630: SpriteImage_Flagpole,
    631: SpriteImage_PaintGoal,
    643: SpriteImage_LavaBubble,
    644: SpriteImage_LavaBubble,
    662: SpriteImage_BlueRing,
    673: SpriteImage_TileGod,
    683: SpriteImage_QBlock,
    692: SpriteImage_BrickBlock,
    701: SpriteImage_BrickBlock,
    703: SpriteImage_BooCircle,
    704: SpriteImage_BrickBlock,
    706: SpriteImage_BrickBlock,
    707: SpriteImage_QBlock,
    716: SpriteImage_Foo,
}
