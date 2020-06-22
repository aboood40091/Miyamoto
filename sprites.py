#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2020 Treeki, Tempus, angelsl, JasonP27, Kinnay,
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

        self.setImage(pipeLength)

    def setImage(self, pipeLength):
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


class SpriteImage_PlatformBase(SLib.SpriteImage):  # X
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

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
        SLib.loadIfNotInImageCache('MovPlatBL', 'bone_platform_left.png')
        SLib.loadIfNotInImageCache('MovPlatBM', 'bone_platform_middle.png')
        SLib.loadIfNotInImageCache('MovPlatBR', 'bone_platform_right.png')
        SLib.loadIfNotInImageCache('MovPlatCL', 'cloud_platform_left.png')
        SLib.loadIfNotInImageCache('MovPlatCM', 'wood_platform_middle.png') # No middle type exists for cloud
        SLib.loadIfNotInImageCache('MovPlatCR', 'cloud_platform_right.png')

    def getPlatformWidth(self):
        """
        Return an integer specifying the length of the platform.
        Should not be pre-multiplied with 16 or 60.
        """
        return 2.5

    def getPlatformType(self):
        """
        Returns a string with 'N', 'S', 'R', 'B' or 'C' depending on the type of platform.
        """
        return 'N'

    def getPlatformOffset(self):
        """
        Returns a tuple with an x and y offset.
        """
        return (-4, 0)

    def dataChanged(self):
        super().dataChanged()
        self.offset = self.getPlatformOffset()
        self.imgType = self.getPlatformType()
        self.width = self.getPlatformWidth() * 16
        self.height = max(ImageCache['MovPlat%sL' % self.imgType].height(), ImageCache['MovPlat%sM' % self.imgType].height(), ImageCache['MovPlat%sR' % self.imgType].height()) / 3.75

    def paint(self, painter):
        super().paint(painter)
        left = ImageCache['MovPlat%sL' % self.imgType]
        mid = ImageCache['MovPlat%sM' % self.imgType]
        right = ImageCache['MovPlat%sR' % self.imgType]
        
        painter.drawPixmap(0, 0, left)
        painter.drawPixmap(self.width * 3.75 - right.width(), 0, right)

        if self.width > (left.width() + right.width()) / 3.75:
            painter.drawTiledPixmap(int(left.width()), 0, self.width * 3.75 - (left.width() + right.width()), mid.height(), mid)


class SpriteImage_Goomba(SLib.SpriteImage_Static):  # 0
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Goomba'],
            (-4, -4)
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
            (-4, -12),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Paragoomba', 'paragoomba.png')


class SpriteImage_PipePiranhaUp(SLib.SpriteImage_Static):  # 2, 62
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


class SpriteImage_PipePiranhaDown(SLib.SpriteImage_Static):  # 3, 82
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


class SpriteImage_PipePiranhaLeft(SLib.SpriteImage_Static):  # 4, 83
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


class SpriteImage_PipePiranhaRight(SLib.SpriteImage_Static):  # 5, 84
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
            (-4, -32),
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
            (-4, 32),
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
            (-32, -4),
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
            (32, -4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaRightFire', 'firetrap_pipe_right.png')


class SpriteImage_GroundPiranha(SLib.SpriteImage_StaticMultiple):  # 14, 698, 712
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
        )

        self.xOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('KoopaShellG', 'koopatroopa_shell_green.png')
        SLib.loadIfNotInImageCache('KoopaShellR', 'koopatroopa_shell_red.png')
        SLib.loadIfNotInImageCache('KoopatroopaG', 'koopatroopa_green.png')
        SLib.loadIfNotInImageCache('KoopatroopaR', 'koopatroopa_red.png')

    def dataChanged(self):
        shellcolour = self.parent.spritedata[5] & 1
        inshell = (self.parent.spritedata[5] >> 4) & 1

        if inshell:
            self.yOffset = 0
            self.image = ImageCache['KoopaShellR' if shellcolour else 'KoopaShellG']
        else:
            self.yOffset = -16
            self.image = ImageCache['KoopatroopaR' if shellcolour else 'KoopatroopaG']

        super().dataChanged()


class SpriteImage_KoopaParatroopa(SLib.SpriteImage_StaticMultiple):  # 20
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.offset = (-4, -16)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('KoopaParatroopaG', 'koopa_paratroopa_green.png')
        SLib.loadIfNotInImageCache('KoopaParatroopaR', 'koopa_paratroopa_red.png')

    def dataChanged(self):
        shellcolour = self.parent.spritedata[5] & 1

        if shellcolour == 0:
            self.image = ImageCache['KoopaParatroopaG']
        else:
            self.image = ImageCache['KoopaParatroopaR']

        super().dataChanged()


class SpriteImage_BuzzyBeetle(SLib.SpriteImage_StaticMultiple):  # 22
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BuzzyLU'],
            (-8/15, -8/15),
        )

        self.directions = [
            ('L', ''),
            ('R', '_right'),
        ]

        self.types = [
            ('U', ''),
            ('D', '_down'),
            ('US', '_shell'),
            ('DS', '_shell_down'),
        ]

    @staticmethod
    def loadImages():
        if 'BuzzyLU' not in ImageCache:
            directions = [
                ('L', ''),
                ('R', '_right'),
            ]

            types = [
                ('U', ''),
                ('D', '_down'),
                ('US', '_shell'),
                ('DS', '_shell_down'),
            ]

            for direction in directions:
                for type_ in types:
                   ImageCache['Buzzy%s%s' % (direction[0], type_[0])] = SLib.GetImg('buzzy_beetle%s%s.png' % (direction[1], type_[1]))

    def dataChanged(self):
        direction = self.parent.spritedata[4] & 0xF; direction = 0 if direction > 1 else direction
        type_ = self.parent.spritedata[5] & 0xF; type_ = 0 if type_ > 3 else type_
        self.image = ImageCache['Buzzy%s%s' % (self.directions[direction][0], self.types[type_][0])]

        super().dataChanged()


class SpriteImage_Spiny(SLib.SpriteImage_StaticMultiple):  # 23
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -2
        self.yOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Spiny', 'spiny.png')
        SLib.loadIfNotInImageCache('SpinyBall', 'spiny_ball.png')
        SLib.loadIfNotInImageCache('SpinyShell', 'spiny_shell.png')
        SLib.loadIfNotInImageCache('SpinyShellU', 'spiny_shell_u.png')

    def dataChanged(self):

        spawntype = self.parent.spritedata[5]
        self.yOffset = 0

        if spawntype == 1:
            self.image = ImageCache['SpinyBall']
        elif spawntype == 2:
            self.image = ImageCache['SpinyShell']
        elif spawntype == 3:
            self.image = ImageCache['SpinyShellU']
        else:
            self.image = ImageCache['Spiny']
            self.yOffset = -4

        super().dataChanged()


class SpriteImage_SpinyU(SLib.SpriteImage_Static):  # 24
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SpinyU'],
            (-32/15, 0),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpinyU', 'spiny_u.png')


class SpriteImage_MidwayFlag(SLib.SpriteImage_Static):  # 25
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MidwayFlag'],
            (-4, -40),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MidwayFlag', 'midway_flag.png')


class SpriteImage_ZoomArea(SLib.SpriteImage):  # 26
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def dataChanged(self):
        super().dataChanged()

        h = self.parent.spritedata[4]
        w = self.parent.spritedata[5]
        if w == 0:
            w = 1
        if h == 0:
            h = 1
        
        if w == 1 and h == 1:  # no point drawing a 1x1 outline behind the self.parent
            self.aux[0].setSize(0, 0, 0, 0)
            return
        self.aux[0].setSize(w * 60, h * 60, 0, -h * 60 + 60)


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
        self.xOffset = -36
        self.yOffset = -144

        self.parent.setZValue(24999)
        self.aux.append(SLib.AuxiliaryImage(parent, 390, 375))
        self.aux[0].setPos(135 + 13*60, 4*60 - 15)
        self.aux[0].alpha = 0.5
        self.dataChanged()

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FlagPole', 'flag_pole.png')
        SLib.loadIfNotInImageCache('FlagPoleSecret', 'flag_pole_secret.png')
        SLib.loadIfNotInImageCache('Castle', 'castle.png')
        SLib.loadIfNotInImageCache('CastleSnow', 'castle_snow.png')
        SLib.loadIfNotInImageCache('CastleSecret', 'castle_secret.png')
        SLib.loadIfNotInImageCache('CastleSecretSnow', 'castle_secret_snow.png')

    def dataChanged(self):
        super().dataChanged()

        secret = (self.parent.spritedata[2] & 0x10) != 0
        castle = (self.parent.spritedata[5] & 0x10) == 0
        snow =   (self.parent.spritedata[5] & 1)    != 0

        if secret:
            self.image = ImageCache['FlagPoleSecret']
            
            if snow:
                self.aux[0].image = ImageCache['CastleSecretSnow']
            else:
                self.aux[0].image = ImageCache['CastleSecret']
        else:
            self.image = ImageCache['FlagPole']
            
            if snow:
                self.aux[0].image = ImageCache['CastleSnow']
            else:
                self.aux[0].image = ImageCache['Castle']

        if not castle:
            self.aux[0].image = None


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


class SpriteImage_Grrrol(SLib.SpriteImage_Static):  # 33, 504
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Grrrol'],
            (-4, -4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Grrrol', 'grrrol.png')


class SpriteImage_BigGrrrol(SLib.SpriteImage_Static):  # 34, 505
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigGrrrol'],
            (-32, -24),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigGrrrol', 'big_grrrol.png')


class SpriteImage_Seaweed(SLib.SpriteImage_StaticMultiple):  # 35
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.shapes = {0: 'a', 1: 'b', 2: 'c'}

    @staticmethod
    def loadImages():
        for i in [0, 1, 2, 3]:
            for shape in ['a', 'b', 'c']:
                SLib.loadIfNotInImageCache('Seaweed%d%s' % (i, shape), 'seaweed_%d%s.png' % (i, shape))

    def dataChanged(self):
        size = self.parent.spritedata[5] & 0xF

        if size == 3:
            size = 2

        elif size in [4, 5]:
            size = 3

        elif size > 2:
            size = 0

        shape = self.parent.spritedata[5] >> 4
        if shape > 2:
            shape = 0

        self.image = ImageCache['Seaweed%d%s' % (size, self.shapes[shape])]

        if not size:
            self.yOffset = -72

            if shape in [0, 1]:
                self.xOffset = -8

            else:
                self.xOffset = -16

        elif size == 1:
            self.yOffset = -104

            if shape in [0, 1]:
                self.xOffset = -16

            else:
                self.xOffset = -24

        elif size == 2:
            self.yOffset = -120

            if shape in [0, 1]:
                self.xOffset = -16

            else:
                self.xOffset = -32

        elif size == 3:
            self.yOffset = -152

            if shape in [0, 1]:
                self.xOffset = -24

            else:
                self.xOffset = -40

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


class SpriteImage_EventController(SLib.SpriteImage):  # X
    font = QtGui.QFont(globals.NumberFont)
    font.setPointSize(14)
    font.setBold(True)
    
    def __init__(self, parent, text):
        super().__init__(
            parent,
            3.75,
        )
        topLeft = self.spritebox.BoundingRect.topLeft()
        size = self.spritebox.BoundingRect.size()
        self.rect = QtCore.QRectF(topLeft.x() + 1, topLeft.y() + 1, size.width() - 2, size.height() - 2)
        self.text = text
        self.spritebox.shown = False

    def paint(self, painter):
        super().paint(painter)
        oldB = painter.brush()
        oldP = painter.pen()

        if self.parent.isSelected():
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1 / 24 * globals.TileWidth))
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 1 / 24 * globals.TileWidth))

        painter.setBrush(QtGui.QBrush(QtGui.QColor(230, 115, 0)))
        painter.drawRoundedRect(self.rect, 4, 4)
        painter.setFont(SpriteImage_EventController.font)
        painter.drawText(self.rect, Qt.AlignCenter, self.text)

        painter.setBrush(oldB)
        painter.setPen(oldP)
        

class SpriteImage_EventControllerAnd(SpriteImage_EventController):  # 37
    def __init__(self, parent):
        super().__init__(parent, 'Event\nAND')


class SpriteImage_EventControllerOr(SpriteImage_EventController):  # 38
    def __init__(self, parent):
        super().__init__(parent, 'Event\nOR')


class SpriteImage_EventControllerRandom(SpriteImage_EventController):  # 39
    def __init__(self, parent):
        super().__init__(parent, 'Event\nRAND')


class SpriteImage_EventControllerChainer(SpriteImage_EventController):  # 40
    def __init__(self, parent):
        super().__init__(parent, 'Event\nIF')


class SpriteImage_EventControllerMultiChainer(SpriteImage_EventController):  # 42
    def __init__(self, parent):
        super().__init__(parent, 'Event\nCHNR')


class SpriteImage_EventControllerTimer(SpriteImage_EventController):  # 43
    def __init__(self, parent):
        super().__init__(parent, 'Event\nTMR')


class SpriteImage_RedRing(SLib.SpriteImage_Static):  # 44
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['RedRing'],
            (-12, -12),
        )

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


class SpriteImage_LineControlledStarCoin(SLib.SpriteImage_Static):  # 46, 607
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['LineStarCoin'],
            (-16, -12),
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


class SpriteImage_MvmtRotControlledStarCoin(SLib.SpriteImage_Static):  # 48, 480
    # Movement Controlled, Rotation Controlled Star Coin
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MRStarCoin'],
        )

        self.yOffset = 6

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
            (-8, -4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GreenCoin', 'green_coins.png')


class SpriteImage_MontyMole(SLib.SpriteImage_Static):  # 51
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MontyMole'],
            (-104/15, -64/15),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MontyMole', 'monty_mole.png')


class SpriteImage_GrrrolPassage(SLib.SpriteImage_StaticMultiple):  # 52, 671
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GrrrolPassageR'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GrrrolPassageR', 'grrrol_passage.png')

        if 'GrrrolPassageL' not in ImageCache:
            ImageCache['GrrrolPassageL'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('grrrol_passage.png', True).mirrored(True, False))

    def dataChanged(self):
        super().dataChanged()

        direction = self.parent.spritedata[5] & 0xF

        if direction == 1:
            self.image = ImageCache['GrrrolPassageL']
            self.xOffset = 0

        else:
            self.image = ImageCache['GrrrolPassageR']
            self.xOffset = -80


class SpriteImage_Porcupuffer(SLib.SpriteImage_Static):  # 53
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Porcupuffer'],
            (-20, -20),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Porcupuffer', 'porcupuffer.png')


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


class SpriteImage_FishBone(SLib.SpriteImage_StaticMultiple):  # 57
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.yOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FishBoneR', 'fish_bone.png')

        if 'FishBoneL' not in ImageCache:
            ImageCache['FishBoneL'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('fish_bone.png', True).mirrored(True, False))

    def dataChanged(self):
        super().dataChanged()

        direction = (self.parent.spritedata[5] >> 4) & 1

        if direction == 1:
            self.image = ImageCache['FishBoneL']
            self.xOffset = -8

        else:
            self.image = ImageCache['FishBoneR']
            self.xOffset = -4


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

        items = {0: 0x800 + len(globals.Overrides) - 1, 1: 49, 2: 32, 3: 32, 4: 37, 5: 38, 6: 36, 7: 33, 8: 34, 9: 41, 12: 35, 13: 42, 15: 39}

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
            (-2.4, -24),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StalkingPiranha', 'stalking_piranha.png')


class SpriteImage_WaterPlant(SLib.SpriteImage_Static):  # 64, 682
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['WaterPlant'],
            (-8, -128)
        )

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


class SpriteImage_ControllerSwaying(SLib.SpriteImage_MovementController):  # 68, 116
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerSwaying'],
        )
        self.parent.setZValue(500000)
        self.aux.append(SLib.AuxiliaryRotationAreaOutline(parent, 60))
        self.aux.append(SLib.AuxiliaryRotationAreaOutline(parent, 120))

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerSwaying', 'controller_swaying.png')

    def dataChanged(self):
        startOffset = (self.parent.spritedata[2] & 0xF) * 22.5
        reversedDir = (self.parent.spritedata[4] >> 4) & 1
        rotation = (self.parent.spritedata[4] & 0xF) * 22.5
        arc = (self.parent.spritedata[7] >> 4) * 22.5

        if reversedDir == 1:
            startOffset += 180
        
        startOffset = math.cos(math.radians(startOffset + 90))
            
        self.aux[0].SetAngle(90 + rotation - arc * 0.5, arc)
        self.aux[1].SetAngle(90 + rotation - startOffset * arc * 0.5, 0)
        super().dataChanged()


# func = SpriteImage_StoneEye(SLib.SpriteImage_StaticMultiple)
#        func.translateImage()



class SpriteImage_ControllerSpinning(SLib.SpriteImage_MovementController):  # 69, 118, 484
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


class SpriteImage_MovingIronBlock(SLib.SpriteImage):  # 71
    def __init__(self, parent):
        super().__init__(parent, 3.75)

        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        ImageCache['MovITopL'] = SLib.GetImg('mov_iron_top_l.png')
        ImageCache['MovITopM'] = SLib.GetImg('mov_iron_top_m.png')
        ImageCache['MovITopR'] = SLib.GetImg('mov_iron_top_r.png')
        ImageCache['MovIMiddleL'] = SLib.GetImg('mov_iron_middle_l.png')
        ImageCache['MovIMiddleM'] = SLib.GetImg('mov_iron_middle_m.png')
        ImageCache['MovIMiddleR'] = SLib.GetImg('mov_iron_middle_r.png')
        ImageCache['MovIBottomL'] = SLib.GetImg('mov_iron_bottom_l.png')
        ImageCache['MovIBottomM'] = SLib.GetImg('mov_iron_bottom_m.png')
        ImageCache['MovIBottomR'] = SLib.GetImg('mov_iron_bottom_r.png')

    def dataChanged(self):
        super().dataChanged()

        self.width = (self.parent.spritedata[8] & 0xF) * 16 + 16
        self.height = (self.parent.spritedata[9] & 0xF) * 16 + 16

        if self.width < 32:
            self.width = 32

        if self.height < 32:
            self.height = 32

    def paint(self, painter):
        super().paint(painter)

        # Time to code this lazily.

        # Top of sprite.
        if self.width / 16 == 0:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovITopM'])
        elif self.width / 16 == 1:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovITopM'])
        elif self.width / 16 == 2:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovITopL'])
            painter.drawPixmap(60, 0, 60, 60, ImageCache['MovITopR'])
        elif self.width / 16 == 3:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovITopL'
            ])
            painter.drawPixmap(60, 0, 60, 60, ImageCache['MovITopM'])
            painter.drawPixmap(120, 0, 60, 60, ImageCache['MovITopR'])
        else:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovITopL'
            ])
            painter.drawTiledPixmap(60, 0, (self.width / 16 - 2) * 60, 60, ImageCache['MovITopM'])
            painter.drawPixmap(60 + ((self.width / 16 - 2) * 60), 0, 60, 60, ImageCache['MovITopR'])

        # Bottom
        if self.height / 16 > 1:
            if self.width / 16 == 0:
                painter.drawPixmap(0, 0, 60, 60, ImageCache['MovIBottomM'])
            elif self.width / 16 == 1:
                painter.drawPixmap(0, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovIBottomM'])
            elif self.width / 16 == 2:
                painter.drawPixmap(0, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovIBottomL'])
                painter.drawPixmap(60, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovIBottomR'])
            elif self.width / 16 == 3:
                painter.drawPixmap(0, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovIBottomL'
                ])
                painter.drawPixmap(60, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovIBottomM'])
                painter.drawPixmap(120, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovIBottomR'])
            else:
                painter.drawPixmap(0, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovIBottomL'
                ])
                painter.drawTiledPixmap(60, (self.height / 16) * 60 - 60, (self.width / 16 - 2) * 60, 60,
                                        ImageCache['MovIBottomM'])
                painter.drawPixmap(60 + ((self.width / 16 - 2) * 60), (self.height / 16) * 60 - 60, 60, 60,
                                   ImageCache['MovIBottomR'])

        # Left
        if self.height / 16 == 3:
            painter.drawPixmap(0, 60, 60, 60, ImageCache['MovIMiddleL'])
        elif self.height / 16 > 3:
            painter.drawPixmap(0, 60, 60, 60, ImageCache['MovIMiddleL'])
            painter.drawTiledPixmap(0, 120, 60, (self.height / 16 - 3) * 60, ImageCache['MovIMiddleL'])

        # Right
        if self.height / 16 == 3:
            painter.drawPixmap((self.width / 16 * 60) - 60, 60, 60, 60, ImageCache['MovIMiddleR'])
        elif self.height / 16 > 3:
            painter.drawPixmap((self.width / 16 * 60) - 60, 60, 60, 60, ImageCache['MovIMiddleR'])
            painter.drawTiledPixmap((self.width / 16 * 60) - 60, 120, 60, (self.height / 16 - 3) * 60,
                                    ImageCache['MovIMiddleR'])

        # Middle
        if self.width / 16 > 2:
            if self.height / 16 > 2:
                painter.drawTiledPixmap(60, 60, ((self.width / 16) - 2) * 60, ((self.height / 16) - 2) * 60,
                                        ImageCache['MovIMiddleM'])

        # 1 Glitch
        if self.width / 16 < 2:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovITopM'])
            painter.drawTiledPixmap(0, 60, 60, ((self.height / 16) - 2) * 60, ImageCache['MovIMiddleM'])
            if self.height > 1:
                painter.drawPixmap(0, (self.height / 16) * 60 - 60, 60, 60, ImageCache['MovIBottomM'])
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovITopM'])


class SpriteImage_MovingLandBlock(SLib.SpriteImage):  # 72
    def __init__(self, parent):
        super().__init__(parent, 3.75)

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

        self.width = (self.parent.spritedata[8] & 0xF) * 16 + 16
        self.height = (self.parent.spritedata[9] & 0xF) * 16 + 16

        if self.width < 32:
            self.width = 32

        if self.height < 32:
            self.height = 32

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
            (-16, -4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('HuckitCrab', 'huckit_crab.png')


class SpriteImage_BroIce(SLib.SpriteImage_Static):  # 75
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BroIce'],
            (-4, -24),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BroIce', 'bro_ice.png')


class SpriteImage_BroHammer(SLib.SpriteImage_Static):  # 76
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BroHammer'],
            (-4, -24),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BroHammer', 'bro_hammer.png')


class SpriteImage_BroSledge(SLib.SpriteImage_Static):  # 77
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BroSledge'],
            (-16, -32),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BroSledge', 'bro_sledge.png')


class SpriteImage_BroBoomerang(SLib.SpriteImage_Static):  # 78
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BroBoomerang'],
            (-4, -24),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BroBoomerang', 'bro_boomerang.png')


class SpriteImage_BroFire(SLib.SpriteImage_Static):  # 79
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BroFire'],
            (-4, -24),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BroFire', 'bro_fire.png')


class SpriteImage_FlameChomp(SLib.SpriteImage_Static):  # 85, 640
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['FlameChomp'],
            (-4, -4)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FlameChomp', 'flame_chomp.png')

        
class SpriteImage_Urchin(SLib.SpriteImage_Static):  # 86, 695, 713
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Urchin'],
            (-8, -4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Urchin', 'urchin.png')


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
        )

        self.xOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BouncyCloudS', 'bouncy_cloud_small.png')
        SLib.loadIfNotInImageCache('BouncyCloudL', 'bouncy_cloud_large.png')

    def dataChanged(self):
        size = self.parent.spritedata[8] & 0xF

        if size == 1:
            self.image = ImageCache['BouncyCloudL']
            self.yOffset = -8

        else:
            self.image = ImageCache['BouncyCloudS']
            self.yOffset = -4

        super().dataChanged()


class SpriteImage_BouncyCloudL(SLib.SpriteImage_Static):  # 95
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BouncyCloudL'],
            (-28, -4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BouncyCloudL', 'bouncy_cloud_large.png')


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


class SpriteImage_MegaUrchin(SLib.SpriteImage_Static):  # 99
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MegaUrchin'],
            (-48, -48),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MegaUrchin', 'mega_urchin.png')


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

class SpriteImage_RotatingBillCanon(SLib.SpriteImage_StaticMultiple):  # 103
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RotatingBillCanon', 'rotating_bullet_bill_canon.png')
        SLib.loadIfNotInImageCache('RotatingBillCanonInverted', 'rotating_bullet_bill_canon_right.png')
        SLib.loadIfNotInImageCache('RotatingBillCanonNone', 'rotating_bullet_bill_canon_nothing.png')

    def dataChanged(self):
        super().dataChanged()

        self.pieces = (self.parent.spritedata[3] & 0xF) % 8 + 1
        
        tempNothing = self.parent.spritedata[4]

        self.nothing = [
            tempNothing & 1,
            tempNothing & 2,
            tempNothing & 4,
            tempNothing & 8,
            tempNothing & 16,
            tempNothing & 32,
            tempNothing & 64,
            tempNothing & 128,
        ]

        tempInverted = self.parent.spritedata[5]

        self.inverted = [
            tempInverted & 1,
            tempInverted & 2,
            tempInverted & 4,
            tempInverted & 8,
            tempInverted & 16,
            tempInverted & 32,
            tempInverted & 64,
            tempInverted & 128,
        ]

        self.height = 16 * self.pieces
        self.yOffset = 16 - self.height
        
        self.width = 100 / 3.75
        self.xOffset = -20 / 3.75

    def paint(self, painter):
        super().paint(painter)

        for x in range(self.pieces):
            # Draw Cannon
            if self.nothing[x] < 1:
                # Facing right
                if self.inverted[x] < 1:
                    painter.drawPixmap(20, (self.pieces - 1) * 60 - (x * 60), ImageCache['RotatingBillCanonInverted'])

                # Facing left
                else:
                    painter.drawPixmap(1, (self.pieces - 1) * 60 - (x * 60), ImageCache['RotatingBillCanon'])

            # Draw None
            else:
                painter.drawPixmap(19, (self.pieces - 1) * 60 - (x * 60), ImageCache['RotatingBillCanonNone'])


class SpriteImage_QuestionSwitch(SLib.SpriteImage_Static):  # 104
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.offset = (-4, -4)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('QSwitch', 'q_switch.png')
        SLib.loadIfNotInImageCache('QSwitchU', 'q_switch_u.png')

    def dataChanged(self):
        isflipped = self.parent.spritedata[5] & 1

        if isflipped == 0:
            self.image = ImageCache['QSwitch']
        else:
            self.image = ImageCache['QSwitchU']

        super().dataChanged()


class SpriteImage_PSwitch(SLib.SpriteImage_Static):  # 105, 686, 710
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.offset = (-4, -4)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PSwitch', 'p_switch.png')
        SLib.loadIfNotInImageCache('PSwitchU', 'p_switch_u.png')

    def dataChanged(self):
        isflipped = self.parent.spritedata[5] & 1

        if isflipped == 0:
            self.image = ImageCache['PSwitch']
        else:
            self.image = ImageCache['PSwitchU']

        super().dataChanged()


class SpriteImage_PeachCastleDoor(SLib.SpriteImage_Static):  # 107
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PeachCastleDoor'],
            (-16, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PeachCastleDoor', 'peach_castle_door.png')


class SpriteImage_GhostHouseDoor(SLib.SpriteImage_Static):  # 108
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GhostHouseDoor'],
            (-4, 0),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GhostHouseDoor', 'ghost_house_door.png')


class SpriteImage_TowerBossDoor(SLib.SpriteImage_Static):  # 109, 636
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['TowerBossDoor'],
            (-16, -20),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TowerBossDoor', 'tower_boss_door.png')


class SpriteImage_CastleBossDoor(SLib.SpriteImage_Static):  # 110, 635
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['CastleBossDoor'],
            (-16, -20),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CastleBossDoor', 'castle_boss_door.png')


class SpriteImage_BowserBossDoor(SLib.SpriteImage_Static):  # 111, 637
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BowserBossDoor'],
            (-60, -136),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BowserBossDoor', 'bowser_boss_door.png')


class SpriteImage_MediumCheepCheep(SLib.SpriteImage_Static):  # 113
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MediumCheepCheep'],
            (-8, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MediumCheepCheep', 'medium_cheep_cheep.png')


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


class SpriteImage_Spinner(SLib.SpriteImage_StaticMultiple):  # 117, 693
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


class SpriteImage_Lakitu(SLib.SpriteImage_Static):  # 119
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Lakitu'],
            (-12, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Lakitu', 'lakitu.png')


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


class SpriteImage_SandPillar(SLib.SpriteImage_StaticMultiple):  # 123, 124
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SandPillar0'],
        )

        self.alpha = 0.65
        self.xOffset = -40

    @staticmethod
    def loadImages():
        for i in range(4):
            SLib.loadIfNotInImageCache('SandPillar%d' % i, 'sand_pillar_%d.png' % i)

    def dataChanged(self):
        size = self.parent.spritedata[5] >> 4; size = 0 if size > 3 else size
        self.image = ImageCache['SandPillar%d' % size]

        self.yOffset = -160
        if size == 1:
            self.yOffset = -240

        elif size == 2:
            self.yOffset = -80

        elif size == 3:
            self.yOffset = -208

        super().dataChanged()


class SpriteImage_BulletBill(SLib.SpriteImage_StaticMultiple):  # 125
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BulletBill0'],
        )

    @staticmethod
    def loadImages():
        for i in range(4):
            SLib.loadIfNotInImageCache('BulletBill%d' % i, 'bullet_bill_%d.png' % i)

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 0xF; direction = 0 if direction > 3 else direction
        self.image = ImageCache['BulletBill%d' % direction]

        self.xOffset = 0
        self.yOffset = 8

        if direction == 1:
            self.xOffset = -8

        elif direction == 2:
            self.yOffset = -8

        elif direction == 3:
            self.yOffset = 0

        super().dataChanged()


class SpriteImage_BanzaiBill(SLib.SpriteImage_StaticMultiple):  # 126
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BanzaiBill0'],
        )

    @staticmethod
    def loadImages():
        for i in range(4):
            SLib.loadIfNotInImageCache('BanzaiBill%d' % i, 'banzai_bill_%d.png' % i)

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 0xF; direction = 0 if direction > 3 else direction
        self.image = ImageCache['BanzaiBill%d' % direction]

        self.xOffset = -24
        self.yOffset = -24

        if direction == 0:
            self.xOffset = -32
            self.yOffset = -16

        elif direction == 1:
            self.xOffset = -40
            self.yOffset = -16

        elif direction == 3:
            self.yOffset = -32

        super().dataChanged()


class SpriteImage_HomingBulletBill(SLib.SpriteImage_StaticMultiple):  # 127
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['HomingBulletBill0'],
        )

    @staticmethod
    def loadImages():
        for i in range(4):
            SLib.loadIfNotInImageCache('HomingBulletBill%d' % i, 'homing_bullet_bill_%d.png' % i)

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 0xF; direction = 0 if direction > 3 else direction
        self.image = ImageCache['HomingBulletBill%d' % direction]

        self.xOffset = 0
        self.yOffset = 8

        if direction == 1:
            self.xOffset = -8

        elif direction == 2:
            self.yOffset = -8

        elif direction == 3:
            self.yOffset = 0

        super().dataChanged()


class SpriteImage_HomingBanzaiBill(SLib.SpriteImage_StaticMultiple):  # 128
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['HomingBanzaiBill0'],
        )

    @staticmethod
    def loadImages():
        for i in range(4):
            SLib.loadIfNotInImageCache('HomingBanzaiBill%d' % i, 'homing_banzai_bill_%d.png' % i)

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 0xF; direction = 0 if direction > 3 else direction
        self.image = ImageCache['HomingBanzaiBill%d' % direction]

        self.xOffset = -24
        self.yOffset = -24

        if direction == 0:
            self.xOffset = -32
            self.yOffset = -16

        elif direction == 1:
            self.xOffset = -40
            self.yOffset = -16

        elif direction == 3:
            self.yOffset = -32

        super().dataChanged()


class SpriteImage_JumpingCheepCheep(SLib.SpriteImage_StaticMultiple):  # 129
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['JumpingCheepCheepL'],
        )

    @staticmethod
    def loadImages():
        if 'JumpingCheepCheepL' not in ImageCache:
            img = SLib.GetImg('jumping_cheep_cheep.png', True)

            ImageCache['JumpingCheepCheepL'] = QtGui.QPixmap.fromImage(img)
            ImageCache['JumpingCheepCheepR'] = QtGui.QPixmap.fromImage(img.mirrored(True, False))

    def dataChanged(self):
        direction = self.parent.spritedata[2] >> 4
        if direction != 1:
            self.image = ImageCache['JumpingCheepCheepL']

        else:
            self.image = ImageCache['JumpingCheepCheepR']

        super().dataChanged()


class SpriteImage_ShiftingRectangle(SLib.SpriteImage_StaticMultiple):  # 132
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        for i in range(5):
            for j in range(2):
                SLib.loadIfNotInImageCache('ShiftingRectangle_%d_%d' % (i, j), 'rect_platform_%d_%d.png' % (i, j))

    def dataChanged(self):
        saturation = self.parent.spritedata[3] & 1
        color = self.parent.spritedata[5] & 0xF

        if color > 5:
            color = 0

        elif color == 5:
            color = 2

        self.image = ImageCache['ShiftingRectangle_%d_%d' % (color, saturation)]

        if color == 0:
            self.offset = (-52, -48)

        elif color == 1:
            self.offset = (-48, -52)

        elif color == 2:
            self.offset = (-68, -32)

        elif color == 3:
            self.offset = (-36, -48)

        elif color == 4:
            self.offset = (-36, -48)

        super().dataChanged()


class SpriteImage_SpineCoaster(SLib.SpriteImage_Static):  # 133, 699, 700
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CoasterConnectPiecePieceA', 'coaster_connect_piece_piece_a.png')
        SLib.loadIfNotInImageCache('CoasterConnectPiecePieceB', 'coaster_connect_piece_piece_b.png')
        SLib.loadIfNotInImageCache('CoasterConnectPieceSkull',  'coaster_connect_piece_skull.png')
        SLib.loadIfNotInImageCache('CoasterConnectTailPiece',   'coaster_connect_tail_piece.png')
        SLib.loadIfNotInImageCache('CoasterConnectTailSkull',   'coaster_connect_tail_skull.png')
        SLib.loadIfNotInImageCache('CoasterConnectTailTail',    'coaster_connect_tail_tail.png')
        SLib.loadIfNotInImageCache('CoasterSkull',              'coaster_skull.png')

    def dataChanged(self):
        super().dataChanged()
        
        self.nPieces = (self.parent.spritedata[5] & 0xF) + 1
        
        self.width = self.nPieces * 32 + 6  # 5.2
        self.height = 22  # 21.6

        self.xOffset = -(self.nPieces - 1) * 32 - 4
        self.yOffset = -4

    def paint(self, painter):
        # Head
        painter.drawPixmap(QtCore.QPointF((self.nPieces - 1) * 120 + 7.5, 0), ImageCache['CoasterSkull'])

        if self.nPieces > 1:
            # Final piece
            painter.drawPixmap(QtCore.QPointF(7.5, 7.5), ImageCache['CoasterConnectTailTail'])

            if self.nPieces == 2:
                # Middle piece
                painter.drawPixmap(QtCore.QPointF(75, 15), ImageCache['CoasterConnectTailSkull'])

            else:
                # First piece after head
                painter.drawPixmap(QtCore.QPointF(15 + (self.nPieces - 2) * 120, 7.5), ImageCache['CoasterConnectPiecePieceB'])
                painter.drawPixmap(QtCore.QPointF(15 + (self.nPieces - 1) * 120 - 60, 15), ImageCache['CoasterConnectPieceSkull'])

                # Last piece before the final piece
                painter.drawPixmap(QtCore.QPointF(75, 15), ImageCache['CoasterConnectTailPiece'])

                # Everything in between
                for i in range(self.nPieces-3):
                    painter.drawPixmap(QtCore.QPointF(135 + i * 120, 7.5), ImageCache['CoasterConnectPiecePieceB'])
                    painter.drawPixmap(QtCore.QPointF(135 + i * 120 + 60, 15), ImageCache['CoasterConnectPiecePieceA'])

        super().paint(painter)


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
            (-8.8, -2.4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantThwomp', 'thwomp_giant.png')


class SpriteImage_DryBones(SLib.SpriteImage_Static):  # 137
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['DryBones'],
            (-8, -12),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('DryBones', 'dry_bones.png')


class SpriteImage_BigDryBones(SLib.SpriteImage_Static):  # 138
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigDryBones'],
            (-16, -80/3),
        )

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
        if 'Palm1' not in ImageCache:
            for i in range(1, 17):
                image = SLib.GetImg('palm_%d.png' % i, True)
                ImageCache['Palm%d' % i] = QtGui.QPixmap.fromImage(image)
                ImageCache['Palm%dL' % i] = QtGui.QPixmap.fromImage(image.mirrored(True, False))

                image = SLib.GetImg('palm_%d_d.png' % i, True)
                ImageCache['Palm%dD' % i] = QtGui.QPixmap.fromImage(image)
                ImageCache['Palm%dLD' % i] = QtGui.QPixmap.fromImage(image.mirrored(True, False))

    def dataChanged(self):
        height = self.parent.spritedata[5] & 0xF
        left = (self.parent.spritedata[4] >> 4) & 1
        desert = (self.parent.spritedata[2] >> 4) & 1

        self.xOffset = -32
        self.yOffset = -16 * (3.5 + height)

        if height > 10:
            self.xOffset -= 4

        imageName = 'Palm%d' % (height + 1)
        if left: imageName += 'L'
        if desert: imageName += 'D'

        self.image = ImageCache[imageName]

        super().dataChanged()


class SpriteImage_MovPipe(SpriteImage_PipeAlt):  # 146, 679
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'U'
        self.typeinfluence = True

    def dataChanged(self):
        super().dataChanged()

        rawlength = self.parent.spritedata[4] + 1

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
        else:
            pipeLength = rawlength

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

        super().setImage(pipeLength)


class SpriteImage_StoneEye(SLib.SpriteImage_StaticMultiple):  # 150, 719
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        for i in range(6):
            SLib.loadIfNotInImageCache('StoneEyeSN%d' % i, 'stone_eye_%d.png' % i)
            SLib.loadIfNotInImageCache('StoneEyeSS%d' % i, 'stone_eye_spooky_%d.png' % i)
            SLib.loadIfNotInImageCache('StoneEyeBN%d' % i, 'stone_eye_big_%d.png' % i)
            SLib.loadIfNotInImageCache('StoneEyeBS%d' % i, 'stone_eye_big_spooky_%d.png' % i)

    def dataChanged(self):
        appearance = 'S' if (self.parent.spritedata[2] & 0x1) != 0 else 'N'
        size = 'B' if (self.parent.spritedata[4] & 0x10) != 0 else 'S'
        type_ = self.parent.spritedata[4] & 0xF
        if type_ > 4:
            type_ = 0

        self.image = ImageCache['StoneEye%s%s%d' % (size, appearance, type_)]

        if size == 'S':
            if type_ == 0:
                self.xOffset = -28
                self.yOffset = -16
            elif type_ == 1:
                self.xOffset = -32
                self.yOffset = -16
            elif type_ == 3:
                self.xOffset = -56
                self.yOffset = 4
            else:
                self.xOffset = -16
                self.yOffset = 4
        else:
            if type_ == 0:
                self.xOffset = -56
                self.yOffset = -76
            elif type_ == 1:
                self.xOffset = -64
                self.yOffset = -76
            elif type_ == 3:
                self.xOffset = -96
                self.yOffset = -48
            else:
                self.xOffset = -40
                self.yOffset = -48
        super().dataChanged()


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


class SpriteImage_Spotlight(SLib.SpriteImage):  # 153
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False
        self.dimensions = (-28, -56, 72, 104)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpotlightHolder', 'spotlight_holder.png')
        SLib.loadIfNotInImageCache('SpotlightLamp', 'spotlight_lamp.png')
        SLib.loadIfNotInImageCache('SpotlightScrew', 'spotlight_screw.png')

    def dataChanged(self):
        super().dataChanged()
        self.rotation = (self.parent.spritedata[3] & 0xF) * 22.5

    def paint(self, painter):
        super().paint(painter)
        oldT = painter.transform() # Save old transform
        
        painter.translate(135, 265)
        painter.rotate(self.rotation)
        painter.drawPixmap(-150, -150, ImageCache['SpotlightLamp'])

        painter.setTransform(oldT) # Recover old transform
        painter.drawPixmap(105, 0, ImageCache['SpotlightHolder'])

        painter.translate(135, 265)
        painter.rotate(self.rotation)
        painter.drawPixmap(-30, -30, ImageCache['SpotlightScrew'])
        
        painter.setTransform(oldT) # Recover old transform


class SpriteImage_FlyingQBlock(SLib.SpriteImage):  # 154
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

        self.dimensions = (-12, -16, 42, 32)

    def dataChanged(self):
        super().dataChanged()

        self.contents = self.parent.spritedata[9] & 0xF
        self.acorn = (self.parent.spritedata[6] >> 4) & 1

        items = {0: 0x800 + len(globals.Overrides) - 1, 1: 49, 2: 32, 3: 32, 4: 37, 5: 38, 6: 36, 7: 33, 8: 34, 9: 41, 12: 35, 13: 42, 15: 39}

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


class SpriteImage_PipeCannon(SLib.SpriteImage):  # 155, 667
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
        SLib.loadIfNotInImageCache('WaterGeyserTop', 'water_geyser_top.png')
        SLib.loadIfNotInImageCache('WaterGeyserMiddle', 'water_geyser_middle.png')

    def dataChanged(self):
        super().dataChanged()

        if self.parent.spritedata[8] & 1:
            width = 2

        else:
            raw_width = self.parent.spritedata[3] >> 4
            width = 1.625 * raw_width + 1.625
            if width == 1.625:
                width = 6.5

        length = (self.parent.spritedata[4] & 0xF) << 4 | self.parent.spritedata[5] >> 4
        length = 33/64 * length + 6

        self.middle = ImageCache['WaterGeyserMiddle']
        self.top = ImageCache['WaterGeyserTop']

        self.width = width * 16
        self.height = length * 16

        self.xOffset = -(self.width / 2) + 8
        self.yOffset = -(length - 1) * 16

    def paint(self, painter):
        super().paint(painter)

        painter.drawTiledPixmap(self.x, self.y + 15, self.width * (60/16), self.height * (60/16) - 15, self.middle.scaledToWidth(self.width * (60/16), Qt.SmoothTransformation))
        if self.hasTop:
            painter.drawPixmap(self.topX, self.topY, self.width * (60/16), 180, self.top)


class SpriteImage_BarCenter(SLib.SpriteImage_Static):  # 157
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BarCenter'],
            (-16, -24),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BarCenter', 'bar_center.png')


class SpriteImage_CoinOutline(SLib.SpriteImage_StaticMultiple):  # 158
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.parent.setZValue(20000)

    def dataChanged(self):
        multi = (self.parent.spritedata[2] >> 4) & 1
        self.image = SLib.Tiles[28 if multi else 31].main
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


class SpriteImage_WaterGeyserLocation(SpriteImage_StackedSprite):  # 163, 705
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WaterGeyserTop', 'water_geyser_top.png')
        SLib.loadIfNotInImageCache('WaterGeyserMiddle', 'water_geyser_middle.png')

    def dataChanged(self):
        super().dataChanged()

        if self.parent.spritedata[8] & 1:
            width = 2

        else:
            raw_width = self.parent.spritedata[3] >> 4
            width = 1.625 * raw_width + 1.625
            if width == 1.625:
                width = 6.5

        length = self.parent.spritedata[5] >> 4
        length = 31/60 * length + 6

        self.middle = ImageCache['WaterGeyserMiddle']
        self.top = ImageCache['WaterGeyserTop']

        self.width = width * 16
        self.height = length * 16

        self.xOffset = -(self.width / 2) + 8
        self.yOffset = -(length - 1) * 16

    def paint(self, painter):
        super().paint(painter)

        painter.drawTiledPixmap(self.x, self.y + 15, self.width * (60/16), self.height * (60/16) - 15, self.middle.scaledToWidth(self.width * (60/16), Qt.SmoothTransformation))
        if self.hasTop:
            painter.drawPixmap(self.topX, self.topY, self.width * (60/16), 180, self.top)


class SpriteImage_BobOmb(SLib.SpriteImage_Static):  # 164
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BobOmb'],
            (-4, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BobOmb', 'bob_omb.png')


class SpriteImage_CoinCircle(SLib.SpriteImage):  # 165
    def __init__(self, parent):
        super().__init__(parent, 3.75)

        self.tileIdx = 30
        auxImage = QtGui.QPixmap(60, 60)
        auxImage.fill(Qt.transparent)
        self.aux.append(SLib.AuxiliaryImage(parent, 60, 60))
        self.aux[0].image = auxImage
        self.aux[0].hover = False

    def dataChanged(self):
        tilt = ((self.parent.spritedata[2] >> 2) & 1) | ((self.parent.spritedata[3] >> 4) & 1) | (self.parent.spritedata[3] & 1)
        arc = (self.parent.spritedata[6] >> 4) * 22.5 + 22.5
        offset = (self.parent.spritedata[6] & 0xF) * 22.5
        coinAmount = 1 + self.parent.spritedata[8]
        diameter = self.parent.spritedata[9]
        movementID = self.parent.spritedata[10]

        tiltX = self.parent.objx
        tiltY = self.parent.objy

        # Uncomment to enable tilt towards movement controllers
        
        #if tilt == 1:
        #    for sprite in globals.Area.sprites:
        #        if isinstance(sprite.ImageObj, SLib.SpriteImage_MovementController):
        #            if sprite.ImageObj.getMovementID() == movementID:
        #                tiltX = sprite.objx + 8
        #                tiltY = sprite.objy + 8
        #                break

        pix = QtGui.QPixmap(60 * (diameter + 2), 60 * (diameter + 2))
        pix.fill(Qt.transparent)
        paint = QtGui.QPainter(pix)
        paint.setOpacity(0.5)
        angle = offset

        for i in range(coinAmount):
            if arc == 360:
                angle = math.radians(-arc * i / coinAmount - offset)
            elif coinAmount > 1:
                angle = math.radians(arc * 0.5 - arc * i / (coinAmount - 1) - offset)

            x = math.sin(angle) * ((diameter * 30) + 30) - 30
            y = -(math.cos(angle) * ((diameter * 30) + 30)) - 30

            if tilt == 1:
                imageAngle = math.degrees(math.atan2(tiltY - (self.parent.objy + (y / 60) * 16 + 8), tiltX - (self.parent.objx + (x / 60) * 16 + 8))) - 90
                img = SLib.Tiles[self.tileIdx].main.transformed(QTransform().rotate(imageAngle))
                paint.drawPixmap(x + pix.width() / 2 + 30 - img.width() / 2, y + pix.height() / 2 + 30 - img.height() / 2, img);
            else:
                paint.drawPixmap(x + pix.width() / 2, y + pix.height() / 2, SLib.Tiles[self.tileIdx].main)

        paint = None
        self.aux[0].image = pix
        self.aux[0].setSize(pix.width(), pix.height(), -pix.width() / 2 + 30, -pix.height() / 2 + 30)


class SpriteImage_CoinOutlineCircle(SpriteImage_CoinCircle):  # 166
    def __init__(self, parent):
        super().__init__(parent)

    def dataChanged(self):
        multi = (self.parent.spritedata[2] >> 4) & 1
        self.tileIdx = 28 if multi else 31
        super().dataChanged()


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


class SpriteImage_ClapCoin(SLib.SpriteImage_Static):  # 168, 169
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ClapCoin'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ClapCoin', 'clap_coin.png')


class SpriteImage_Parabomb(SLib.SpriteImage_Static):  # 170, 687
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Parabomb'],
            (-4, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Parabomb', 'parabomb.png')


class SpriteImage_BulletBillCannon(SLib.SpriteImage_Static):  # 171, 581
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BulletBillCannon', 'bullet_bill_cannon.png')
        SLib.loadIfNotInImageCache('BulletBillCannonPiece', 'bullet_bill_cannon_piece.png')

        if 'BulletBillCannonInverted' not in ImageCache:
            ImageCache['BulletBillCannonInverted'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('bullet_bill_cannon.png', True).mirrored(False, True))

    def dataChanged(self):
        super().dataChanged()

        self.inverted = ((self.parent.spritedata[2] & 0xF0) >> 4) & 1
        self.cannonHeight = (self.parent.spritedata[5] & 0xF0) >> 4
        self.height = (self.cannonHeight + 2) * 16

        if self.inverted == 1:
            self.yOffset = 0

        else:
            self.yOffset = -(self.cannonHeight + 1) * 16

    def paint(self, painter):
        if self.inverted == 1:
            painter.drawTiledPixmap(0, 0, 60, 60 * self.cannonHeight, ImageCache['BulletBillCannonPiece'])
            painter.drawPixmap(0, 60 * self.cannonHeight, 60, 120, ImageCache['BulletBillCannonInverted'])

        else:
            painter.drawPixmap(0, 0, 60, 120, ImageCache['BulletBillCannon'])
            painter.drawTiledPixmap(0, 120, 60, 60 * self.cannonHeight, ImageCache['BulletBillCannonPiece'])
        
        super().paint(painter)


class SpriteImage_RisingLoweringBulletBillCannon(SLib.SpriteImage_Static):  # 172
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BulletBillCannon', 'bullet_bill_cannon.png')
        SLib.loadIfNotInImageCache('BulletBillCannonPiece', 'bullet_bill_cannon_piece.png')

        if 'BulletBillCannonInverted' not in ImageCache:
            ImageCache['BulletBillCannonInverted'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('bullet_bill_cannon.png', True).mirrored(False, True))

    def dataChanged(self):
        super().dataChanged()

        self.inverted = ((self.parent.spritedata[2] & 0xF0) >> 4) & 1
        self.cannonHeight = (self.parent.spritedata[5] & 0xF0) >> 4
        self.cannonHeightTwo = self.parent.spritedata[5] & 0xF

        if self.cannonHeight >= self.cannonHeightTwo:
            self.height = (self.cannonHeight + 2) * 16

        else:
            self.height = (self.cannonHeightTwo + 2) * 16

        if self.inverted == 1:
            self.yOffset = 0

        else:
            if self.cannonHeight >= self.cannonHeightTwo:
                self.yOffset = -(self.cannonHeight + 1) * 16

            else:
                self.yOffset = -(self.cannonHeightTwo + 1) * 16

    def paint(self, painter):
        if self.inverted == 1:
            if self.cannonHeightTwo > self.cannonHeight:
                painter.setOpacity(0.5)
                painter.drawTiledPixmap(0, 0, 60, 60 * self.cannonHeightTwo, ImageCache['BulletBillCannonPiece'])
                painter.drawPixmap(0, 60 * self.cannonHeightTwo, 60, 120, ImageCache['BulletBillCannonInverted'])
                painter.setOpacity(1)
            
            painter.drawTiledPixmap(0, 0, 60, 60 * self.cannonHeight, ImageCache['BulletBillCannonPiece'])
            painter.drawPixmap(0, 60 * self.cannonHeight, 60, 120, ImageCache['BulletBillCannonInverted'])

        else:
            if self.cannonHeightTwo > self.cannonHeight:
                painter.setOpacity(0.5)
                painter.drawPixmap(0, 0, 60, 120, ImageCache['BulletBillCannon'])
                painter.drawTiledPixmap(0, 120, 60, 60 * self.cannonHeightTwo, ImageCache['BulletBillCannonPiece'])
                painter.setOpacity(1)

                painter.drawPixmap(0, 60 * (self.cannonHeightTwo - self.cannonHeight), 60, 120, ImageCache['BulletBillCannon'])
                painter.drawTiledPixmap(0, 60 * (self.cannonHeightTwo - self.cannonHeight + 2), 60, 60 * self.cannonHeight, ImageCache['BulletBillCannonPiece'])

            else:
                painter.drawPixmap(0, 0, 60, 120, ImageCache['BulletBillCannon'])
                painter.drawTiledPixmap(0, 120, 60, 60 * self.cannonHeight, ImageCache['BulletBillCannonPiece'])
        
        super().paint(painter)


class SpriteImage_BanzaiBillCannon(SLib.SpriteImage_Static):  # 173, 582
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BanzaiBillCannon'],
            (-32, -200/3),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BanzaiBillCannon', 'banzai_bill_cannon.png')



class SpriteImage_BanzaiBillCannonU(SLib.SpriteImage_Static):  # 174, 583
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BanzaiBillCannonU'],
            (-32, 16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BanzaiBillCannonU', 'banzai_bill_cannon_u.png')

class SpriteImage_Mechakoopa(SLib.SpriteImage_Static):  # 175
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Mechakoopa'],
            (-8, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Mechakoopa', 'mechakoopa.png')


class SpriteImage_AirshipCannon(SLib.SpriteImage_StaticMultiple):  # 176
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.yOffset = -32/3

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CannonL', 'cannon.png')
        SLib.loadIfNotInImageCache('CannonR', 'cannon_r.png')

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 0xF
        if direction == 1:
            self.image = ImageCache['CannonR']; self.xOffset = -16/15

        else:
            self.image = ImageCache['CannonL']; self.xOffset = -8

        super().dataChanged()


class SpriteImage_Cannonball(SLib.SpriteImage_StaticMultiple):  # 179
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Cannonball', 'cannonball.png')
        SLib.loadIfNotInImageCache('CannonballBig', 'cannonball_big.png')

    def dataChanged(self):
        size = self.parent.spritedata[5] & 0xF
        if size == 1:
            self.image = ImageCache['CannonballBig']; self.xOffset = -16

        else:
            self.image = ImageCache['Cannonball']; self.xOffset = -8

        super().dataChanged()


class SpriteImage_Spike(SLib.SpriteImage_Static):  # 180, 181, 651
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


class SpriteImage_MovingPlatform(SpriteImage_PlatformBase):  # 182, 186
    def __init__(self, parent):
        super().__init__(parent)

    def getPlatformWidth(self):
        width = (self.parent.spritedata[8] & 0xF) + 1
        if width == 1:
            width = 2
            
        return width + 0.5

    def getPlatformType(self):
        type_ = (self.parent.spritedata[3] >> 4) & 0x3
        imgType = 'N'

        if type_ == 1:
            imgType = 'R'
        elif type_ == 3:
            imgType = 'S'
            
        return imgType


class SpriteImage_FallingIcicle(SLib.SpriteImage_StaticMultiple):  # 183, 185
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.yOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FallingIcicle1x1', 'falling_icicle_1x1.png')
        SLib.loadIfNotInImageCache('FallingIcicle1x2', 'falling_icicle_1x2.png')

    def dataChanged(self):
        size = self.parent.spritedata[5]

        if size == 1:
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
            (-28, -4)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantIcicle', 'giant_icicle.png')


class SpriteImage_ScaredyRat(SLib.SpriteImage_Static):  # 187
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ScaredyRat'],
            (-8, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ScaredyRat', 'scaredy_rat.png')


class SpriteImage_MovingPlatformSpawner(SpriteImage_PlatformBase):  # 192
    def __init__(self, parent):
        super().__init__(parent)

    def getPlatformWidth(self):
        width = self.parent.spritedata[8] & 0xF
        
        if not width:
            width = 4
        elif width == 1:
            width = 1.5
            
        return width + 0.5

    def getPlatformOffset(self):
        width = self.parent.spritedata[8] & 0xF

        if width == 1:
            return (-8, 0)
        else:
            return (-4, 0)


class SpriteImage_MovingLinePlatform(SpriteImage_PlatformBase):  # 193, 573, 658
    def __init__(self, parent):
        super().__init__(parent)

    def getPlatformWidth(self):
        width = self.parent.spritedata[8] & 0xF
        
        if not width:
            width = 4
        elif width == 1:
            width = 1.5

        return width + 0.5

    def getPlatformType(self):
        type_ = self.parent.spritedata[4] >> 4

        if not type_:
            return 'N'
        else:
            return 'R'

    def getPlatformOffset(self):
        width = self.parent.spritedata[8] & 0xF
        
        if width == 1:
            return (16, 8)
        else:
            if not width:
                width = 4
                
            return (20 - 8 * (width - 1), 8)


class SpriteImage_FireSnake(SLib.SpriteImage_Static):  # 194
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['FireSnake'],
            (0, -8)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FireSnake', 'fire_snake.png')


class SpriteImage_RouletteBlock(SLib.SpriteImage_Static):  # 195
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['RouletteBlock'],
            (-4, -4),
        )

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
        self.offset = (-20, -20) if giant else (-8, -8)

        super().dataChanged()


class SpriteImage_BoomBoom(SLib.SpriteImage_Static):  # 206
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BoomBoom'],
            (-56/3, -20),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoomBoom', 'boom_boom.png')


class SpriteImage_LavaGeyser(SLib.SpriteImage_StaticMultiple):  # 207
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -48

    @staticmethod
    def loadImages():
        for i in range(7):
            SLib.loadIfNotInImageCache('LavaGeyser%d' % i, 'lava_geyser_%d.png' % i)

    def dataChanged(self):
        size = self.parent.spritedata[4] >> 4; size = 0 if size > 6 else size
        self.image = ImageCache['LavaGeyser%d' % size]

        startsOn = self.parent.spritedata[5] & 1
        self.alpha = 0.75 if startsOn else 0.5

        self.yOffset = -160
        
        if size == 1:
            self.yOffset = -152

        elif size == 2:
            self.yOffset = -144

        elif size == 3:
            self.yOffset = -120

        elif size == 4:
            self.yOffset = -104

        elif size == 5:
            self.yOffset = -96

        elif size == 6:
            self.yOffset = -48

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


class SpriteImage_GreyTestPlatform(SLib.SpriteImage_StaticMultiple):  # 211
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GrayBlock', 'gray_block.png')

    def dataChanged(self):
        width = self.parent.spritedata[8] & 0x1F
        if width == 0:
            width = 0.25 #Just to make it show up in the editor. It's actually scale 0.
            
        self.image = ImageCache['GrayBlock'].transformed(QTransform().scale(width, 0.5))
        super().dataChanged()


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


class SpriteImage_SwingingVine(SLib.SpriteImage_Static):  # 213
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SwingingVine'],
            (0, -8)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SwingingVine', 'swinging_vine.png')


class SpriteImage_ControllerSpinOne(SLib.SpriteImage_MovementController):  # 214
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


class SpriteImage_WiiTowerBlock(SLib.SpriteImage):  # 217, 311
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WiiTowerBlockTL', 'wii_tower_block_top_l.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockTM', 'wii_tower_block_top_m.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockTR', 'wii_tower_block_top_r.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockML', 'wii_tower_block_middle_l.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockMM', 'wii_tower_block_middle_m.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockMR', 'wii_tower_block_middle_r.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockBL', 'wii_tower_block_bottom_l.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockBM', 'wii_tower_block_bottom_m.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockBR', 'wii_tower_block_bottom_r.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockHole', 'wii_tower_block_hole.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockTMGood', 'wii_tower_block_top_m_good.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockMLGood', 'wii_tower_block_middle_l_good.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockMRGood', 'wii_tower_block_middle_r_good.png')
        SLib.loadIfNotInImageCache('WiiTowerBlockBMGood', 'wii_tower_block_bottom_m_good.png')
        
    def dataChanged(self):
        super().dataChanged()

        self.sizeW = (self.parent.spritedata[8] & 0xF) + 1
        self.sizeH = (self.parent.spritedata[9] & 0xF) + 1
        if self.sizeW < 2:
            self.sizeW = 2
        if self.sizeH < 2:
            self.sizeH = 2

        self.width = self.sizeW << 4
        self.height = self.sizeH << 4

    def paint(self, painter):
        super().paint(painter)

        # Draw middle first
        painter.drawTiledPixmap(60, 60, (self.sizeW - 2) * 60, (self.sizeH - 2) * 60, ImageCache['WiiTowerBlockMM'])

        painter.drawPixmap(0, 0, ImageCache['WiiTowerBlockTL'])
        painter.drawPixmap((self.sizeW - 1) * 60, 0, ImageCache['WiiTowerBlockTR'])
        painter.drawTiledPixmap(60, 0, (self.sizeW - 2) * 60, 60, ImageCache['WiiTowerBlockTM' if self.sizeW > 3 else 'WiiTowerBlockTMGood'])
        painter.drawTiledPixmap(0, 60, 60, (self.sizeH - 2) * 60, ImageCache['WiiTowerBlockML' if self.sizeH > 3 else 'WiiTowerBlockMLGood'])
        painter.drawTiledPixmap((self.sizeW - 1) * 60, 60, 60, (self.sizeH - 2) * 60, ImageCache['WiiTowerBlockMR' if self.sizeH > 3 else 'WiiTowerBlockMRGood'])
        painter.drawPixmap(0, (self.sizeH - 1) * 60, ImageCache['WiiTowerBlockBL'])
        painter.drawPixmap((self.sizeW - 1) * 60, (self.sizeH - 1) * 60, ImageCache['WiiTowerBlockBR'])
        painter.drawTiledPixmap(60, (self.sizeH - 1) * 60, (self.sizeW - 2) * 60, 60, ImageCache['WiiTowerBlockBM' if self.sizeW > 3 else 'WiiTowerBlockBMGood'])

        amountX = max((int(self.sizeW + 1) // 3), 1)
        offsetX = (self.sizeW - (amountX * 3 - 2)) * 30
        amountY = max((int(self.sizeH) // 2), 1)
        offsetY = (self.sizeH - (amountY * 2 - 1)) * 30
        
        for x in range(amountX):
            for y in range(amountY):
                painter.drawPixmap(offsetX + x * 180, offsetY + y * 120, ImageCache['WiiTowerBlockHole'])


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


class SpriteImage_BigBoo(SLib.SpriteImage_Static):  # 219
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigBoo'],
            (-64, -112),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigBoo', 'big_boo.png')


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
        alpha = 0.5

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
        paint.setOpacity(alpha)

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


class SpriteImage_SnakeBlock(SLib.SpriteImage):  # 222
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'SnakeBlock0' not in ImageCache:
            SLib.loadIfNotInImageCache('SnakeBlock3N', 'snake_block.png')
            SLib.loadIfNotInImageCache('SnakeBlock3I', 'snake_block_ice.png')

            for x in range(3):
                ImageCache['SnakeBlock%dN' % x] = ImageCache['SnakeBlock3N'].transformed(
                    QTransform().scale((x + 1) / 4, (x + 1) / 4))

                ImageCache['SnakeBlock%dI' % x] = ImageCache['SnakeBlock3I'].transformed(
                    QTransform().scale((x + 1) / 4, (x + 1) / 4))

    def dataChanged(self):
        super().dataChanged()

        self.scale = (self.parent.spritedata[2] & 0xF) >> 2
        self.direction = self.parent.spritedata[2] & 3

        self.length = (self.parent.spritedata[5] & 0xF) + 3

        self.xOffset = 0
        self.yOffset = 0

        if self.direction in [0, 1]:
            self.height = (self.scale + 1) * 16
            self.width = self.height * self.length

            if self.direction == 1:
                self.xOffset = self.height - self.width

        elif self.direction in [2, 3]:
            self.width = (self.scale + 1) * 16
            self.height = self.width * self.length

            if self.direction == 3:
                self.yOffset = self.width - self.height

        type_ = self.parent.spritedata[7] >> 4

        if type_ == 1:
            self.imgType = "I"

        else:
            self.imgType = "N"

    def paint(self, painter):
        super().paint(painter)

        painter.drawTiledPixmap(
            0, 0,
            60 * (self.width / 16),
            60 * (self.height / 16),
            ImageCache['SnakeBlock%d%s' % (self.scale, self.imgType)],
        )


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


class SpriteImage_Scaffold(SLib.SpriteImage_StaticMultiple):  # 228, 714
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.yOffset = -0.8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Scaffold', 'scaffold.png')
        SLib.loadIfNotInImageCache('ScaffoldBig', 'scaffold_big.png')

    def dataChanged(self):
        size = self.parent.spritedata[8] >> 4
        if size == 1:
            self.image = ImageCache['ScaffoldBig']; self.xOffset = -108

        else:
            self.image = ImageCache['Scaffold']; self.xOffset = -72

        super().dataChanged()


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
            (-16.8, -32)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Larry', 'larry.png')


class SpriteImage_IceFloe(SLib.SpriteImage_StaticMultiple):  # 226, 227, 231
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.alpha = 0.65
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


class SpriteImage_SpinningFirebar(SLib.SpriteImage_StaticMultiple):  # 235, 483
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75
        )
        self.aux.append(SLib.AuxiliaryCircleOutline(parent, 0))

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FirebarBase', 'firebar_0.png')
        SLib.loadIfNotInImageCache('FirebarBaseWide', 'firebar_1.png')

    def dataChanged(self):

        size = self.parent.spritedata[5] & 0xF
        wideBase = (self.parent.spritedata[3] >> 4) & 1

        width = ((size << 1) + 1) << 4
        self.aux[0].setSize(width)
        self.aux[0].setPos(-width * 1.875 + (60 if wideBase else 30), -width * 1.875 + 30)

        self.image = ImageCache['FirebarBase'] if not wideBase else ImageCache['FirebarBaseWide']
        self.xOffset = 0 if not wideBase else -8
        super().dataChanged()


class SpriteImage_BigFirebar(SLib.SpriteImage_Static):  # 236
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigFirebarBase'],
            (-8, -8),
        )
        self.aux.append(SLib.AuxiliaryCircleOutline(parent, 0))

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigFirebarBase', 'big_firebar.png')

    def dataChanged(self):
        isBig = (self.parent.spritedata[2] & 0x1) != 0
        size = self.parent.spritedata[5] & 0xF

        width = ((size << (2 if isBig else 1)) + 1) << 4 
        self.aux[0].setSize(width)
        self.aux[0].setPos(-width * 1.875 + 60, -width * 1.875 + 60)
        super().dataChanged()


class SpriteImage_Bolt(SLib.SpriteImage_StaticMultiple):  # 238
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoltMetal', 'bolt_metal.png')
        SLib.loadIfNotInImageCache('BoltStone', 'bolt_stone.png')

    def dataChanged(self):
        stone = self.parent.spritedata[4] & 1

        if stone == 1:
            self.image = ImageCache['BoltStone']
            self.xOffset = -8
        else:
            self.image = ImageCache['BoltMetal']
            self.xOffset = 0

        super().dataChanged()


class SpriteImage_BoltIronPlatform(SLib.SpriteImage):  # 239
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoltIronTopLeft', 'iron_platform_bolt_tl.png')
        SLib.loadIfNotInImageCache('BoltIronTop', 'iron_platform_bolt_t.png')
        SLib.loadIfNotInImageCache('BoltIronTopRight', 'iron_platform_bolt_tr.png')
        SLib.loadIfNotInImageCache('BoltIronLeft', 'iron_platform_bolt_l.png')
        SLib.loadIfNotInImageCache('BoltIronMiddle', 'iron_platform_bolt_center.png')
        SLib.loadIfNotInImageCache('BoltIronRight', 'iron_platform_bolt_r.png')
        SLib.loadIfNotInImageCache('BoltIronBottomLeft', 'iron_platform_bolt_bl.png')
        SLib.loadIfNotInImageCache('BoltIronBottom', 'iron_platform_bolt_b.png')
        SLib.loadIfNotInImageCache('BoltIronBottomRight', 'iron_platform_bolt_br.png')

    def dataChanged(self):
        super().dataChanged()

        self.sizeW = (self.parent.spritedata[8] & 0xF) + 2
        self.sizeH = (self.parent.spritedata[9] & 0xF) + 2

        self.width = self.sizeW * 16
        self.height = self.sizeH * 16

    def paint(self, painter):
        super().paint(painter)

        # Draw middle first
        painter.drawTiledPixmap(30, 30, (self.sizeW - 1) * 60, (self.sizeH - 1) * 60, ImageCache['BoltIronMiddle'])

        painter.drawPixmap(0, 0, ImageCache['BoltIronTopLeft'])
        painter.drawPixmap((self.sizeW - 1) * 60, 0, ImageCache['BoltIronTopRight'])
        painter.drawTiledPixmap(60, 0, (self.sizeW - 2) * 60, 60, ImageCache['BoltIronTop'])
        painter.drawTiledPixmap(0, 60, 60, (self.sizeH - 2) * 60, ImageCache['BoltIronLeft'])
        painter.drawTiledPixmap((self.sizeW - 1) * 60, 60, 60, (self.sizeH - 2) * 60, ImageCache['BoltIronRight'])
        painter.drawPixmap(0, (self.sizeH - 1) * 60, ImageCache['BoltIronBottomLeft'])
        painter.drawPixmap((self.sizeW - 1) * 60, (self.sizeH - 1) * 60, ImageCache['BoltIronBottomRight'])
        painter.drawTiledPixmap(60, (self.sizeH - 1) * 60, (self.sizeW - 2) * 60, 60, ImageCache['BoltIronBottom'])


class SpriteImage_BoltMushroom(SLib.SpriteImage_StaticMultiple):  # 241
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.xOffset = -4
        self.yOffset = -16
        self.aux.append(SLib.AuxiliaryImage(parent, 90, 615))
        self.aux[0].alpha = 0.5

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoltMushroomBolt', 'bolt_mushroom_bolt.png')
        SLib.loadIfNotInImageCache('BoltMushroomBoltLong', 'bolt_mushroom_long_bolt.png')
        SLib.loadIfNotInImageCache('BoltMushroomSpring', 'bolt_mushroom_spring.png')

    def dataChanged(self):
        stretchable = (self.parent.spritedata[2] & 4) != 0
        stretchMultiplier = self.parent.spritedata[3] / 10.0
        isLong = (self.parent.spritedata[8] & 1) != 0
        
        auxOffset = 510 if isLong else 270
        self.image = ImageCache['BoltMushroomBoltLong'] if isLong else ImageCache['BoltMushroomBolt']

        if stretchable:
            self.aux[0].image = ImageCache['BoltMushroomSpring'].transformed(QTransform().scale(1, stretchMultiplier))
            self.aux[0].setSize(90, 615 * stretchMultiplier, auxOffset, 180)
        else:
            self.aux[0].image = ImageCache['BoltMushroomSpring']
            self.aux[0].setSize(90, 615, auxOffset, 180)
            
        super().dataChanged()
            

class SpriteImage_BoltMushroomNoBolt(SLib.SpriteImage_StaticMultiple):  # 242
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.xOffset = -4
        self.aux.append(SLib.AuxiliaryImage(parent, 90, 615))
        self.aux[0].alpha = 0.5

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoltMushroom', 'bolt_mushroom.png')
        SLib.loadIfNotInImageCache('BoltMushroomLong', 'bolt_mushroom_long.png')
        SLib.loadIfNotInImageCache('BoltMushroomSpring', 'bolt_mushroom_spring.png')

    def dataChanged(self):
        stretchable = (self.parent.spritedata[2] & 4) != 0
        stretchMultiplier = self.parent.spritedata[3] / 10.0
        isLong = (self.parent.spritedata[8] & 1) != 0
        
        auxOffset = 510 if isLong else 270
        self.image = ImageCache['BoltMushroomLong'] if isLong else ImageCache['BoltMushroom']

        if stretchable:
            self.aux[0].image = ImageCache['BoltMushroomSpring'].transformed(QTransform().scale(1, stretchMultiplier))
            self.aux[0].setSize(90, 615 * stretchMultiplier, auxOffset, 120)
        else:
            self.aux[0].image = ImageCache['BoltMushroomSpring']
            self.aux[0].setSize(90, 615, auxOffset, 120)
            
        super().dataChanged()


class SpriteImage_TileGod(SLib.SpriteImage_StaticMultiple):  # 237, 673
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux2 = [SLib.AuxiliaryRectOutline(parent, 0, 0)]
        self.aux = self.aux2
        self.checkType = 0

    def dataChanged(self):
        super().dataChanged()

        self.checkType = (self.parent.spritedata[3] & 0xF)
        if self.checkType > 2:
            self.checkType = 1

        type_ = self.parent.spritedata[4] >> 4

        self.alpha = 1 if (self.parent.spritedata[4] & 0xF) != 0 else 0.5
        
        self.width = (self.parent.spritedata[8] & 0xF) * 16
        self.height = (self.parent.spritedata[9] & 0xF) * 16

        if not self.width:
            self.width = 16

        if not self.height:
            self.height = 16

        if type_ > 5:
            self.aux = self.aux2
            self.spritebox.shown = True
            self.image = None

            if [self.width, self.height] == [16, 16]:
                self.aux2[0].setSize(0, 0)
                return
        else:
            self.aux = []
            self.spritebox.shown = False

            if type_ == 0:
                tile = SLib.Tiles[208]

            elif type_ == 1:
                tile = SLib.Tiles[48]

            elif type_ == 2:
                tile = SLib.Tiles[0]

            elif type_ == 3:
                tile = SLib.Tiles[52]

            else:
                tile = SLib.Tiles[51]

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
                if ( self.checkType == 0                                                                                     # Solid Fill
                     or self.checkType == 1 and (xTile % 2 == 0 and yTile % 2 == 0 or xTile % 2 != 0 and yTile % 2 != 0)     # Checkers
                     or self.checkType == 2 and (xTile % 2 != 0 and yTile % 2 == 0 or xTile % 2 == 0 and yTile % 2 != 0) ):  # Inverted Checkers
                    painter.drawPixmap(xTile * 60, yTile * 60, self.image)

        aux = self.aux2
        aux[0].paint(painter, None, None)

        painter.restore()


class SpriteImage_BigFloatingLog(SLib.SpriteImage_Static):  # 240
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigFloatingLog'],
            (-160, -40),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigFloatingLog', 'big_floating_log.png')


class SpriteImage_PricklyGoomba(SLib.SpriteImage_Static):  # 247
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PricklyGoomba'],
            (-8, -12),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PricklyGoomba', 'prickly_goomba.png')


class SpriteImage_GhostHouseBoxFrame(SLib.SpriteImage_Static):  # 248
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GhostHouseBoxFrame'],
            (-144, -144),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GhostHouseBoxFrame', 'ghost_house_box_frame.png')


class SpriteImage_Wiggler(SLib.SpriteImage_Static):  # 249, 702
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


class SpriteImage_GreyBlock(SLib.SpriteImage_StaticMultiple):  # 250
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GrayBlock', 'gray_block.png')

    def dataChanged(self):
        width = self.parent.spritedata[8] & 0xF
        height = self.parent.spritedata[9] & 0xF

        if width == 0 or height == 0:
            self.spritebox.shown = True
            self.image = None
        else:
            self.spritebox.shown = False
            self.image = ImageCache['GrayBlock'].transformed(QTransform().scale(width, height))
        super().dataChanged()


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


class SpriteImage_RopeLadder(SLib.SpriteImage_StaticMultiple):  # 252
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -8

    @staticmethod
    def loadImages():
        for i in [0, 1, 2]:
            SLib.loadIfNotInImageCache('RopeLadder%d' % i, 'rope_ladder_%d.png' % i)

    def dataChanged(self):
        size = self.parent.spritedata[5] & 0xF; size = 0 if size > 2 else size
        self.image = ImageCache['RopeLadder%d' % size]

        super().dataChanged()


class SpriteImage_LightCircle(SLib.SpriteImage):  # 253
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.aux.append(SLib.AuxiliaryCircleOutline(parent, 60, Qt.AlignCenter))

    def dataChanged(self):
        self.aux[0].setSize(((self.parent.spritedata[3] & 0xF) + 2) * 48)
        self.aux[0].setPos(self.aux[0].x() - 30, self.aux[0].y() - 30)
        super().dataChanged()


class SpriteImage_UnderwaterLamp(SLib.SpriteImage_Static):  # 254
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['UnderwaterLamp'],
            (-24, -24),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('UnderwaterLamp', 'lamp_underwater.png')


class SpriteImage_MicroGoomba(SLib.SpriteImage_Static):  # 255
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MicroGoomba'],
            (0, 4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MicroGoomba', 'micro_goomba.png')


class SpriteImage_StretchingMushroomPlatform(SLib.SpriteImage):  # 257, 258
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StretchL', 'stretching_mushroom_l.png')
        SLib.loadIfNotInImageCache('StretchM', 'stretching_mushroom_m.png')
        SLib.loadIfNotInImageCache('StretchR', 'stretching_mushroom_r.png')
        SLib.loadIfNotInImageCache('StretchT', 'stretching_mushroom_t.png')
        SLib.loadIfNotInImageCache('StretchS', 'stretching_mushroom_s.png')

    def dataChanged(self):
        super().dataChanged()
        
        self.minLen = self.parent.spritedata[4] & 0x10
        self.maxLen = self.parent.spritedata[4] & 1
        self.startStretched = self.parent.spritedata[5] & 0x10
        self.stemLen = self.parent.spritedata[5] & 0xF
       
        if self.maxLen == 0:
             self.xOffset = -16 * 4.5
             self.width = 16 * 10

        else:
             self.xOffset = -16 * 2.5
             self.width = 16 * 6

        self.height = 16 * (self.stemLen + 3)

    def paint(self, painter):
        super().paint(painter)

        # Draw Max Len
        if self.startStretched == 0:
            painter.setOpacity(0.5)
            
        painter.drawPixmap(0, 0, ImageCache['StretchL'])
        painter.drawTiledPixmap(60, 0, 60 * (self.width / 16 - 2), 60, ImageCache['StretchM'])
        painter.drawPixmap(60 * (self.width / 16 - 1), 0, ImageCache['StretchR'])
        
        if self.startStretched == 0:
            painter.setOpacity(1)

            # Draw Min Len
            if self.minLen == 0:
                painter.drawPixmap(60 * ((self.width / 16) / 2 - 1), 0, ImageCache['StretchL'])
                painter.drawPixmap(60 * (self.width / 16) / 2, 0, ImageCache['StretchR'])

            else:
                painter.drawPixmap(60 * ((self.width / 16) / 2 - 1.5), 0, ImageCache['StretchL'])
                painter.drawPixmap(60 * ((self.width / 16) / 2 - 0.5), 0, ImageCache['StretchM']) 
                painter.drawPixmap(60 * ((self.width / 16) / 2 + 0.5), 0, ImageCache['StretchR'])

        # Draw Stem
        painter.drawPixmap(60 * ((self.width / 16) / 2 - 0.5), 60, ImageCache['StretchT'])
        painter.drawTiledPixmap(60 * ((self.width / 16) / 2 - 0.5), 180, 60, 60 * self.stemLen, ImageCache['StretchS'])


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


class SpriteImage_BigCannon(SLib.SpriteImage):  # 260
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.yOffset = -2
        self.height = 36
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigCannonBase', 'big_cannon_base.png')
        SLib.loadIfNotInImageCache('BigCannonPiece', 'big_cannon_piece.png')
        SLib.loadIfNotInImageCache('BigCannonFront1', 'big_cannon_front1.png')
        SLib.loadIfNotInImageCache('BigCannonFront2', 'big_cannon_front2.png')

        if 'BigCannonBaseInverted' not in ImageCache:
            ImageCache['BigCannonBaseInverted'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('big_cannon_base.png', True).mirrored(True, False))

        if 'BigCannonFront1Inverted' not in ImageCache:
            ImageCache['BigCannonFront1Inverted'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('big_cannon_front1.png', True).mirrored(True, False))

        if 'BigCannonFront2Inverted' not in ImageCache:
            ImageCache['BigCannonFront2Inverted'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('big_cannon_front2.png', True).mirrored(True, False))

    def dataChanged(self):
        self.direction = self.parent.spritedata[5] & 1
        self.length = self.parent.spritedata[4] & 0xF
        self.width = 50 + self.length * 16
       
        if self.direction == 0:
             self.xOffset = -self.width + 16

        else:
             self.xOffset = -2

    def paint(self, painter):
        super().paint(painter)

        if not self.direction:
            painter.drawTiledPixmap(66, 0, 60 * self.length, 134, ImageCache['BigCannonPiece'])
            painter.drawPixmap(0, 0, 72, 134, ImageCache['BigCannonBase'])
            painter.drawPixmap(66 + 60 * self.length, 0, 60, 134, ImageCache['BigCannonFront1'])
            painter.drawPixmap(126 + 60 * self.length, 0, 60, 134, ImageCache['BigCannonFront2'])

        else:
            painter.drawTiledPixmap(120, 0, 60 * self.length, 134, ImageCache['BigCannonPiece'])
            painter.drawPixmap(114 + 60 * self.length, 0, 72, 134, ImageCache['BigCannonBaseInverted'])
            painter.drawPixmap(60, 0, 60, 134, ImageCache['BigCannonFront1Inverted'])
            painter.drawPixmap(0, 0, 60, 134, ImageCache['BigCannonFront2Inverted'])


class SpriteImage_Parabeetle(SLib.SpriteImage_Static):  # 261, 652
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Parabeetle'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Parabeetle', 'parabeetle.png')


class SpriteImage_HeavyParabeetle(SLib.SpriteImage_StaticMultiple):  # 262
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['HeavyParabeetleL'],
            (-40, -64),
        )

    @staticmethod
    def loadImages():
        if "HeavyParabeetleR" not in ImageCache:
            image = SLib.GetImg('heavy_parabeetle.png', True)
            ImageCache['HeavyParabeetleR'] = QtGui.QPixmap.fromImage(image)
            ImageCache['HeavyParabeetleL'] = QtGui.QPixmap.fromImage(image.mirrored(True, False))

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 0x1
        self.image = ImageCache['HeavyParabeetleL' if direction else 'HeavyParabeetleR']

        super().dataChanged()


class SpriteImage_PipeBubbles(SLib.SpriteImage_StaticMultiple):  # 263
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeBubbles0', 'pipe_bubbles.png')
        ImageCache['PipeBubbles1'] = ImageCache['PipeBubbles0'].transformed(QTransform().scale(1, -1))
        ImageCache['PipeBubbles2'] = ImageCache['PipeBubbles0'].transformed(QTransform().rotate(90))
        ImageCache['PipeBubbles3'] = ImageCache['PipeBubbles2'].transformed(QTransform().scale(-1, 1))

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 3
        self.image = ImageCache['PipeBubbles%d' % direction]

        if direction == 1:
            self.offset = (0, 16)
        elif direction == 2:
            self.offset = (16, -16)
        elif direction == 3:
            self.offset = (-96, -16)
        else:
            self.offset = (0, -96)
        
        super().dataChanged()


class SpriteImage_WaterGeyserBoss(SLib.SpriteImage_Static):  # 264
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['WaterGeyserBoss'],
            (-184, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WaterGeyserBoss', 'water_geyser_boss.png')


class SpriteImage_RollingHill(SLib.SpriteImage):  # 265
    RollingHillSizes = [0, 18 * 16, 32 * 16, 50 * 16, 64 * 16, 10 * 16, 14 * 16, 20 * 16, 18 * 16, 0, 30 * 16, 44 * 16]

    def __init__(self, parent):
        super().__init__(parent, 3.75)

        size = (self.parent.spritedata[3] >> 4) & 0xF
        if size in [0, 9]:
            realSize = 32 * (self.parent.spritedata[4] + 1)

        elif size <= 11:
            realSize = self.RollingHillSizes[size]

        else:
            realSize = 0

        self.aux.append(SLib.AuxiliaryCircleOutline(parent, realSize))

    def dataChanged(self):
        super().dataChanged()

        size = (self.parent.spritedata[3] >> 4) & 0xF
        if size in [0, 9]:
            realSize = 32 * (self.parent.spritedata[4] + 1)

        elif size <= 11:
            realSize = self.RollingHillSizes[size]

        else:
            realSize = 0

        self.aux[0].setSize(realSize)
        self.aux[0].update()


class SpriteImage_MovingGhostHouseBlock(SLib.SpriteImage):  # 266, 696
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GhostHouseBlockT', 'ghost_house_block_t.png')
        SLib.loadIfNotInImageCache('GhostHouseBlockTL', 'ghost_house_block_tl.png')
        SLib.loadIfNotInImageCache('GhostHouseBlockTR', 'ghost_house_block_tr.png')
        SLib.loadIfNotInImageCache('GhostHouseBlockL', 'ghost_house_block_l.png')
        SLib.loadIfNotInImageCache('GhostHouseBlockM', 'ghost_house_block_m.png')
        SLib.loadIfNotInImageCache('GhostHouseBlockR', 'ghost_house_block_r.png')
        SLib.loadIfNotInImageCache('GhostHouseBlockB', 'ghost_house_block_b.png')
        SLib.loadIfNotInImageCache('GhostHouseBlockBL', 'ghost_house_block_bl.png')
        SLib.loadIfNotInImageCache('GhostHouseBlockBR', 'ghost_house_block_br.png')

    def dataChanged(self):
        super().dataChanged()

        self.w = (self.parent.spritedata[8] & 0xF) + 3
        self.h = (self.parent.spritedata[9] & 0xF) + 3
        self.width = self.w << 4
        self.height = self.h << 4

    def paint(self, painter):
        super().paint(painter)

        # Draw middle
        painter.drawTiledPixmap(60, 60, (self.w - 2) * 60, (self.h - 2) * 60, ImageCache['GhostHouseBlockM'], 15, ImageCache['GhostHouseBlockM'].height() - (((self.h - 2) * 60) % ImageCache['GhostHouseBlockM'].height()))

        # Draw top row
        painter.drawPixmap(0, 0, ImageCache['GhostHouseBlockTL'])
        painter.drawTiledPixmap(60, 0, (self.w - 2) * 60, 60, ImageCache['GhostHouseBlockT'])
        painter.drawPixmap((self.w - 1) * 60, 0, ImageCache['GhostHouseBlockTR'])

        # Draw left and right side
        painter.drawTiledPixmap(0, 60, 60, (self.h - 2) * 60, ImageCache['GhostHouseBlockL'])
        painter.drawTiledPixmap((self.w - 1) * 60, 60, 60, (self.h - 2) * 60, ImageCache['GhostHouseBlockR'])

        # Draw bottom row
        painter.drawPixmap(0, (self.h - 1) * 60, ImageCache['GhostHouseBlockBL'])
        painter.drawTiledPixmap(60, (self.h - 1) * 60, (self.w - 2) * 60, 60, ImageCache['GhostHouseBlockB'])
        painter.drawPixmap((self.w - 1) * 60, (self.h - 1) * 60, ImageCache['GhostHouseBlockBR'])


class SpriteImage_CustomizableIceBlock(SLib.SpriteImage_StaticMultiple):  # 268
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('IceBlock1x1', 'ice_block_1x1.png')
        SLib.loadIfNotInImageCache('IceBlock2x1', 'ice_block_2x1.png')

    def dataChanged(self):
        blockType = self.parent.spritedata[5] & 0xF

        if blockType == 1:
            self.image = ImageCache['IceBlock2x1']
            self.xOffset = 0
        else:
            self.image = ImageCache['IceBlock1x1']
            self.xOffset = 8

        super().dataChanged()


class SpriteImage_Gear(SLib.SpriteImage_StaticMultiple):  # 269
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.parent.setZValue(-50000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GearStoneS', 'gear_stone_small.png')
        SLib.loadIfNotInImageCache('GearStoneM', 'gear_stone_medium.png')
        SLib.loadIfNotInImageCache('GearStoneL', 'gear_stone_large.png')
        SLib.loadIfNotInImageCache('GearMetalS', 'gear_metal_small.png')
        SLib.loadIfNotInImageCache('GearMetalM', 'gear_metal_medium.png')
        SLib.loadIfNotInImageCache('GearMetalL', 'gear_metal_large.png')

    def dataChanged(self):
        size = self.parent.spritedata[4] & 0xF
        metal = (self.parent.spritedata[5] & 1) != 0
        sizeStr = 'Metal' if metal else 'Stone'

        if size == 1:
            self.image = ImageCache['Gear%sL' % sizeStr]
            self.xOffset = -140
            self.yOffset = -140
        elif size == 2:
            self.image = ImageCache['Gear%sS' % sizeStr]
            self.xOffset = -96
            self.yOffset = -96
        else:
            self.image = ImageCache['Gear%sM' % sizeStr]
            self.xOffset = -92
            self.yOffset = -96

        super().dataChanged()


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


class SpriteImage_MetalBridgePlatform(SLib.SpriteImage_StaticMultiple):  # 271
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MetalBridgePlatform0', 'metal_bridge_platform0.png')
        SLib.loadIfNotInImageCache('MetalBridgePlatform1', 'metal_bridge_platform1.png')
        SLib.loadIfNotInImageCache('MetalBridgePlatform2', 'metal_bridge_platform2.png')

    def dataChanged(self):
        model = self.parent.spritedata[4] & 3

        if model == 1:
            self.xOffset = 0
            self.image = ImageCache['MetalBridgePlatform1']
        elif model == 2:
            self.xOffset = -4
            self.image = ImageCache['MetalBridgePlatform2']
        else:
            self.xOffset = 0
            self.image = ImageCache['MetalBridgePlatform0']
            
        super().dataChanged()


class SpriteImage_MetalBridgeStem(SLib.SpriteImage_StaticMultiple):  # 272
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MetalBridgeStem', 'metal_bridge_stem.png')
        SLib.loadIfNotInImageCache('MetalBridgeStemUnused', 'metal_bridge_stem_unused.png')

    def dataChanged(self):
        if (self.parent.spritedata[5] & 1) == 0:
            self.xOffset = -16
            self.image = ImageCache['MetalBridgeStemUnused']
        else:
            self.xOffset = -24
            self.image = ImageCache['MetalBridgeStem']
            
        super().dataChanged()


class SpriteImage_MetalBridgeBase(SLib.SpriteImage_Static):  # 273
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MetalBridgeBase'],
            (-24, -24),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MetalBridgeBase', 'metal_bridge_base.png')


class SpriteImage_CastlePlatform(SLib.SpriteImage_StaticMultiple):  # 275, 676
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.yOffset = -12

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CastlePlatform0', 'castle_platform_0.png')
        SLib.loadIfNotInImageCache('CastlePlatform1', 'castle_platform_1.png')
        SLib.loadIfNotInImageCache('CastlePlatform2', 'castle_platform_2.png')

    def dataChanged(self):
        super().dataChanged()

        size = self.parent.spritedata[4] & 0xF

        if size == 1:
            self.image = ImageCache['CastlePlatform1']
        elif size == 2:
            self.image = ImageCache['CastlePlatform2']
        else:
            self.image = ImageCache['CastlePlatform0']
            
        self.width = (self.image.width() / 60) * 16
        self.height = (self.image.height() / 60) * 16
        self.xOffset = -(self.image.width() / 120) * 16 + 8


class SpriteImage_Jellybeam(SLib.SpriteImage_Static):  # 276
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Jellybeam'],
            (-8, -12),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Jellybeam', 'jellybeam.png')


class SpriteImage_SeesawMushroom(SLib.SpriteImage):  # 278
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False
        self.yOffset = -8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SeesawMushroomL', 'seesaw_mushroom_left.png')
        SLib.loadIfNotInImageCache('SeesawMushroomM', 'seesaw_mushroom_middle.png')
        SLib.loadIfNotInImageCache('SeesawMushroomR', 'seesaw_mushroom_right.png')
        SLib.loadIfNotInImageCache('SeesawMushroomStem', 'seesaw_mushroom_stem.png')
        SLib.loadIfNotInImageCache('SeesawMushroomStemTop', 'seesaw_mushroom_stem_top.png')
        SLib.loadIfNotInImageCache('SeesawMushroomPivot', 'seesaw_mushroom_pivot.png')

    def dataChanged(self):
        self.stemLength = (self.parent.spritedata[9] & 0xF) * 2
        self.mushroomWidth = (self.parent.spritedata[8] & 0xF) * 2 - 2

        if self.mushroomWidth < 0:
            self.mushroomWidth = 14
        
        self.height = 48 + 16 * self.stemLength
        self.width = 32 + 16 * self.mushroomWidth
        self.xOffset = 16 * 7 - (self.mushroomWidth / 2) * 16
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(0, 0, ImageCache['SeesawMushroomL'])
        painter.drawTiledPixmap(60, 0, self.mushroomWidth * 60, 60, ImageCache['SeesawMushroomM'])
        painter.drawPixmap(60 + self.mushroomWidth * 60, 0, ImageCache['SeesawMushroomR'])
        painter.drawPixmap(30 + self.mushroomWidth * 30, 0, ImageCache['SeesawMushroomPivot'])
        painter.drawPixmap(30 + self.mushroomWidth * 30, 60, ImageCache['SeesawMushroomStemTop'])
        painter.drawTiledPixmap(30 + self.mushroomWidth * 30, 180, 60, self.stemLength * 60, ImageCache['SeesawMushroomStem'])


class SpriteImage_BoltPlatform(SLib.SpriteImage_Static):  # 280
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BoltPlatform'],
            (0, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoltPlatform', 'bolt_platform.png')


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


class SpriteImage_KingBill(SLib.SpriteImage_StaticMultiple):  # 282, 653
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


class SpriteImage_StretchBlock(SLib.SpriteImage):  # 284
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.height = 16
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StretchBlock', 'stretch_block.png')

    def dataChanged(self):
        super().dataChanged()

        length = self.parent.spritedata[5] & 0xF

        if not length:
            length = 8

        self.width = length * 16
        self.xOffset = -(self.width / 2) + 8

    def paint(self, painter):
        super().paint(painter)
        painter.drawTiledPixmap(0, 0, self.width * 3.75, 60, ImageCache['StretchBlock'])


class SpriteImage_VerticalStretchBlock(SLib.SpriteImage):  # 285
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.width = 16
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StretchBlock', 'stretch_block.png')

    def dataChanged(self):
        super().dataChanged()

        length = (self.parent.spritedata[5] & 0xF0) >> 4

        if not length:
            length = 8

        self.height = length * 16
        self.yOffset = -(self.height / 2) + 8

    def paint(self, painter):
        super().paint(painter)
        painter.drawTiledPixmap(0, 0, 60, self.height * 3.75, ImageCache['StretchBlock'])


class SpriteImage_LavaBubble(SLib.SpriteImage_Static):  # 286, 643, 644
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


class SpriteImage_WheelPlatform(SLib.SpriteImage_Static):  # 287
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['WheelPlatform'],
        )

        self.yOffset = -48
        self.xOffset = -64

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WheelPlatform', 'wheel_platform.png')


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


class SpriteImage_ContinuousBurner(SLib.SpriteImage_StaticMultiple):  # 289
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.imgName = 'ContinuousBurner'

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ContinuousBurner', 'continuous_burner.png')

    def dataChanged(self):
        super().dataChanged()
        
        self.direction = self.parent.spritedata[5] & 3
        self.xOffset = 0
        self.yOffset = 0

        if self.direction == 1:
            self.image = ImageCache[self.imgName].transformed(QTransform().scale(-1, 1))
            self.xOffset = -(self.image.width() / 60) * 16 + 16
            
        elif self.direction == 2:
            self.image = ImageCache[self.imgName].transformed(QTransform().rotate(-90))
            self.yOffset = -(self.image.height() / 60) * 16 + 16
            
        elif self.direction == 3:
            self.image = ImageCache[self.imgName].transformed(QTransform().rotate(-90).scale(-1, 1))

        else:
            self.image = ImageCache[self.imgName]

        self.width = (self.image.width() / 60) * 16
        self.height = (self.image.height() / 60) * 16


class SpriteImage_ContinuousBurnerLong(SpriteImage_ContinuousBurner):  # 290
    def __init__(self, parent):
        super().__init__(parent)
        self.imgName = 'ContinuousBurnerLong'

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ContinuousBurnerLong', 'continuous_burner_long.png')


class SpriteImage_PurplePole(SLib.SpriteImage):  # 309
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False
        self.yOffset = -8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PurplePoleT', 'purple_pole_t.png')
        SLib.loadIfNotInImageCache('PurplePoleM', 'purple_pole_m.png')
        SLib.loadIfNotInImageCache('PurplePoleB', 'purple_pole_b.png')


    def dataChanged(self):
        super().dataChanged()
        self.height = ((self.parent.spritedata[5] + 1) << 4) + 48

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['PurplePoleT'])
        painter.drawTiledPixmap(0, 90, 60, self.height * 3.75 - 180, ImageCache['PurplePoleM'])
        painter.drawPixmap(0, self.height * 3.75 - 90, ImageCache['PurplePoleB'])


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


class SpriteImage_GirderRisingController(SLib.SpriteImage_Static):  # 299
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GirderRisingController'],
            (-4, -12),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GirderRisingController', 'girder_rising_controller.png')


class SpriteImage_GirderRising(SLib.SpriteImage_Static):  # 300, 633
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GirderRising'],
            (-32, -12),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GirderRising', 'girder_rising.png')


class SpriteImage_GiantWiggler(SLib.SpriteImage_Static):  # 301
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GiantWiggler'],
            (-16, -72),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantWiggler', 'giant_wiggler.png')


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


class SpriteImage_WobbleRock(SLib.SpriteImage_Static):  # 304
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['WobbleRock'],
            (-4, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WobbleRock', 'wobble_rock.png')


class SpriteImage_Poltergeist(SLib.SpriteImage_Static):  # 305
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Poltergeist'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Poltergeist', 'poltergeist.png')


class SpriteImage_MovingFence(SLib.SpriteImage):  # 307
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovFenceTL', 'mov_fence_tl.png')
        SLib.loadIfNotInImageCache('MovFenceT', 'mov_fence_t.png')
        SLib.loadIfNotInImageCache('MovFenceTR', 'mov_fence_tr.png')
        SLib.loadIfNotInImageCache('MovFenceL', 'mov_fence_l.png')
        SLib.loadIfNotInImageCache('MovFenceM', 'mov_fence_m.png')
        SLib.loadIfNotInImageCache('MovFenceR', 'mov_fence_r.png')
        SLib.loadIfNotInImageCache('MovFenceBL', 'mov_fence_bl.png')
        SLib.loadIfNotInImageCache('MovFenceB', 'mov_fence_b.png')
        SLib.loadIfNotInImageCache('MovFenceBR', 'mov_fence_br.png')

    def dataChanged(self):
        super().dataChanged()

        self.w = ((self.parent.spritedata[8] & 0xF) << 1) + 2
        self.h = ((self.parent.spritedata[9] & 0xF) << 1) + 2
        self.width = (self.w + 2) << 4
        self.height = (self.h + 2) << 4
        self.xOffset = -(self.width >> 1)
        self.yOffset = -(self.height >> 1)

    def paint(self, painter):
        super().paint(painter)

        # Draw top row
        painter.drawPixmap(0, 0, ImageCache['MovFenceTL'])
        painter.drawTiledPixmap(60, 0, self.w * 60, 60, ImageCache['MovFenceT'])
        painter.drawPixmap((self.w + 1) * 60, 0, ImageCache['MovFenceTR'])

        # Draw left, middle and right
        painter.drawTiledPixmap(0, 60, 60, self.h * 60, ImageCache['MovFenceL'])
        painter.drawTiledPixmap(60, 60, self.w * 60, self.h * 60, ImageCache['MovFenceM'])
        painter.drawTiledPixmap((self.w + 1) * 60, 60, 60, self.h * 60, ImageCache['MovFenceR'])

        # Draw bottom row
        painter.drawPixmap(0, (self.h + 1) * 60, ImageCache['MovFenceBL'])
        painter.drawTiledPixmap(60, (self.h + 1) * 60, self.w * 60, 60, ImageCache['MovFenceB'])
        painter.drawPixmap((self.w + 1) * 60, (self.h + 1) * 60, ImageCache['MovFenceBR'])


class SpriteImage_ScalePlatform(SLib.SpriteImage):  # 309
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False
        self.yOffset = -12

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ScaleRopeV', 'scale_rope_v.png')
        SLib.loadIfNotInImageCache('ScaleRopeH', 'scale_rope_h.png')
        SLib.loadIfNotInImageCache('ScaleWheel', 'scale_wheel.png')
        SLib.loadIfNotInImageCache('MovPlatNL', 'wood_platform_left.png')
        SLib.loadIfNotInImageCache('MovPlatNM', 'wood_platform_middle.png')
        SLib.loadIfNotInImageCache('MovPlatNR', 'wood_platform_right.png')
        SLib.loadIfNotInImageCache('MovPlatSL', 'wood_platform_snow_left.png')
        SLib.loadIfNotInImageCache('MovPlatSM', 'wood_platform_snow_middle.png')
        SLib.loadIfNotInImageCache('MovPlatSR', 'wood_platform_snow_right.png')


    def dataChanged(self):
        super().dataChanged()
        self.leftRopeLength = self.parent.spritedata[4] & 0xF
        self.leftRopeLength = 0.5 if self.leftRopeLength < 1 else self.leftRopeLength
        self.rightRopeLength = self.parent.spritedata[5] >> 4
        self.rightRopeLength = 0.5 if self.rightRopeLength < 1 else self.rightRopeLength
        self.snowy = self.parent.spritedata[4] & 0x10 != 0
        self.middleRopeLength = (self.parent.spritedata[5] & 0xF) + ((self.parent.spritedata[3] & 0xF) << 4)
        self.leftPlatfromWidth = (self.parent.spritedata[8] & 0xF) + 3
        self.rightPlatfromWidth = (self.parent.spritedata[9] >> 4) + 3

        self.leftPlatformOffset = (self.leftPlatfromWidth + 0.5) / 2
        self.rightPlatformOffset = (self.rightPlatfromWidth + 0.5) / 2

        if self.middleRopeLength + self.leftPlatformOffset < self.rightPlatformOffset:
            self.width = self.rightPlatformOffset * 2 * 16
            self.xOffset = -(self.rightPlatformOffset - self.middleRopeLength) * 16
        elif self.middleRopeLength + self.rightPlatformOffset < self.leftPlatformOffset:
            self.width = self.leftPlatformOffset * 2 * 16
            self.xOffset = -self.leftPlatformOffset * 16
        else:
            self.width = (self.leftPlatformOffset + self.middleRopeLength + self.rightPlatformOffset) * 16
            self.xOffset = -self.leftPlatformOffset * 16

        self.height = (self.leftRopeLength if self.leftRopeLength > self.rightRopeLength else self.rightRopeLength) * 16 + 20

    def paint(self, painter):
        super().paint(painter)

        leftSideOffset = self.leftPlatformOffset * 60 - 15
        if self.middleRopeLength + self.leftPlatformOffset < self.rightPlatformOffset:
            leftSideOffset = (self.rightPlatformOffset - self.middleRopeLength) * 60 - 15

        #Draw ropes and wheels
        painter.drawTiledPixmap(leftSideOffset, 30, 30, self.leftRopeLength * 60 - 15, ImageCache['ScaleRopeV'])
        painter.drawTiledPixmap(leftSideOffset + self.middleRopeLength * 60, 30, 30, self.rightRopeLength * 60 - 15, ImageCache['ScaleRopeV'])
        painter.drawTiledPixmap(leftSideOffset + 30, 0, self.middleRopeLength * 60 - 30, 30, ImageCache['ScaleRopeH'])
        painter.drawPixmap(leftSideOffset, 0, ImageCache['ScaleWheel'])
        painter.drawPixmap(leftSideOffset + self.middleRopeLength * 60 - 30, 0, ImageCache['ScaleWheel'])

        imgType = 'MovPlat%s' % ('S' if self.snowy else 'N')
        
        # Draw left platform
        painter.drawPixmap(leftSideOffset + 15 - self.leftPlatformOffset * 60 + 75 - ImageCache[imgType + 'L'].width(), self.leftRopeLength * 60 + 15, ImageCache[imgType + 'L'])
        painter.drawTiledPixmap(leftSideOffset + 15 - self.leftPlatformOffset * 60 + 75, self.leftRopeLength * 60 + 15, (self.leftPlatfromWidth - 2) * 60, 60, ImageCache[imgType + 'M'])
        painter.drawPixmap(leftSideOffset + 15 - self.leftPlatformOffset * 60 + 75 + (self.leftPlatfromWidth - 2) * 60, self.leftRopeLength * 60 + 15, ImageCache[imgType + 'R'])

        # Draw right platform
        painter.drawPixmap(10 + leftSideOffset + 15 + (self.middleRopeLength - self.rightPlatformOffset) * 60 + 75 - ImageCache[imgType + 'L'].width(), self.rightRopeLength * 60 + 15, ImageCache[imgType + 'L'])
        painter.drawTiledPixmap(9 + leftSideOffset + 15 + (self.middleRopeLength - self.rightPlatformOffset) * 60 + 75, self.rightRopeLength * 60 + 15, (self.rightPlatfromWidth - 2) * 60, 60, ImageCache[imgType + 'M'])
        painter.drawPixmap(7 + leftSideOffset + 15 + (self.middleRopeLength - self.rightPlatformOffset) * 60 + 75 + (self.rightPlatfromWidth - 2) * 60, self.rightRopeLength * 60 + 15, ImageCache[imgType + 'R'])


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


class SpriteImage_Bulber(SLib.SpriteImage_Static):  # 321
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Bulber'],
            (-16, -12),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Bulber', 'bulber.png')


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
            (-4, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Barrel', 'barrel.png')


class SpriteImage_GhostHouseBlock(SpriteImage_MovingGhostHouseBlock):  # 324
    def __init__(self, parent):
        super().__init__(parent)

    def dataChanged(self):
        super().dataChanged()

        self.w = (self.parent.spritedata[8] & 0xF) + 2
        self.h = (self.parent.spritedata[4] >> 4) + 2
        self.width = self.w << 4
        self.height = self.h << 4


class SpriteImage_SledgeBlock(SLib.SpriteImage_Static):  # 327
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SledgeBlock'],
            (-28, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SledgeBlock', 'sledge_block.png')


SpikePillar_MoveDistance = [16*60, 7*60, 14*60, 10*60]


class SpriteImage_SpikePillarDown(SLib.SpriteImage_Static):  # 329
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SpikePillarDown'],
            (0, -432),
        )

        self.aux.append(SLib.AuxiliaryImage(parent, 240, 1680))
        self.aux[0].image = ImageCache['SpikePillarDown']
        self.aux[0].hover = False
        self.aux[0].alpha = 0.2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpikePillarDown', 'spike_pillar_down.png')

    def dataChanged(self):
        super().dataChanged()
        
        move = (self.parent.spritedata[3] >> 4) & 3
        self.aux[0].setPos(0, SpikePillar_MoveDistance[move])


class SpriteImage_EnemyRaft(SLib.SpriteImage_StaticMultiple):  # 330
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.yOffset = -8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('EnemyRaftStone', 'enemy_raft_stone.png')
        SLib.loadIfNotInImageCache('EnemyRaftWood', 'enemy_raft_wood.png')

    def dataChanged(self):
        raftType = self.parent.spritedata[5] & 1
        self.image = ImageCache['EnemyRaftWood' if raftType != 0 else 'EnemyRaftStone']
        super().dataChanged()


class SpriteImage_SpikePillarUp(SLib.SpriteImage_Static):  # 331
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SpikePillarUp'],
            (0, 0),
        )

        self.aux.append(SLib.AuxiliaryImage(parent, 240, 1680))
        self.aux[0].image = ImageCache['SpikePillarUp']
        self.aux[0].hover = False
        self.aux[0].alpha = 0.2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpikePillarUp', 'spike_pillar_up.png')

    def dataChanged(self):
        super().dataChanged()
        
        move = (self.parent.spritedata[3] >> 4) & 3
        self.aux[0].setPos(0, -SpikePillar_MoveDistance[move])


class SpriteImage_SpikePillarRight(SLib.SpriteImage_Static):  # 332
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SpikePillarRight'],
            (-432, 0),
        )

        self.aux.append(SLib.AuxiliaryImage(parent, 1680, 240))
        self.aux[0].image = ImageCache['SpikePillarRight']
        self.aux[0].hover = False
        self.aux[0].alpha = 0.2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpikePillarRight', 'spike_pillar_right.png')

    def dataChanged(self):
        super().dataChanged()
        
        move = (self.parent.spritedata[3] >> 4) & 3
        self.aux[0].setPos(SpikePillar_MoveDistance[move], 0)


class SpriteImage_SpikePillarLeft(SLib.SpriteImage_Static):  # 333
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SpikePillarLeft'],
            (0, 0),
        )

        self.aux.append(SLib.AuxiliaryImage(parent, 1680, 240))
        self.aux[0].image = ImageCache['SpikePillarLeft']
        self.aux[0].hover = False
        self.aux[0].alpha = 0.2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpikePillarLeft', 'spike_pillar_left.png')

    def dataChanged(self):
        super().dataChanged()
        
        move = (self.parent.spritedata[3] >> 4) & 3
        self.aux[0].setPos(-SpikePillar_MoveDistance[move], 0)


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


class SpriteImage_CheepChomp(SLib.SpriteImage_Static):  # 337
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['CheepChomp'],
            (-40, -28),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CheepChomp', 'cheep_chomp.png')


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


class SpriteImage_AirshipNutPlatform(SLib.SpriteImage_Static):  # 341
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['AirshipNutPlatform'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('AirshipNutPlatform', 'airship_nut_platform.png')


class SpriteImage_SpikePillarLongRight(SLib.SpriteImage_Static):  # 342
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SpikePillarLongRight'],
            (-1332, -4),
        )

        self.aux.append(SLib.AuxiliaryImage(parent, 5055, 270))
        self.aux[0].image = ImageCache['SpikePillarLongRight']
        self.aux[0].hover = False
        self.aux[0].alpha = 0.2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpikePillarLongRight', 'spike_pillar_long_right.png')

    def dataChanged(self):
        super().dataChanged()
        
        moveShort = self.parent.spritedata[3] & 0x10
        self.aux[0].setPos(24*60 if moveShort != 0 else 80*60, 0)


class SpriteImage_SpikePillarLongLeft(SLib.SpriteImage_Static):  # 343
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SpikePillarLongLeft'],
            (0, -4),
        )

        self.aux.append(SLib.AuxiliaryImage(parent, 5055, 270))
        self.aux[0].image = ImageCache['SpikePillarLongLeft']
        self.aux[0].hover = False
        self.aux[0].alpha = 0.2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpikePillarLongLeft', 'spike_pillar_long_left.png')

    def dataChanged(self):
        super().dataChanged()
        
        moveShort = self.parent.spritedata[3] & 0x10
        self.aux[0].setPos(-(24*60 if moveShort != 0 else 80*60), 0)


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


class SpriteImage_GirderLine(SLib.SpriteImage_Static):  # 349
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GirderLine'],
            (-8, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GirderLine', 'girder_line.png')


class SpriteImage_MovingStoneBlock(SLib.SpriteImage_Static):  # 350
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MovingStoneBlock'],
            (-4, 0),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovingStoneBlock', 'moving_stone_block.png')


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


class SpriteImage_SpikeTop(SLib.SpriteImage_StaticMultiple):  # 352, 447
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpikeTop0', 'spike_top.png')
        SLib.loadIfNotInImageCache('SpikeTop1', 'spike_top_left.png')
        SLib.loadIfNotInImageCache('SpikeTop2', 'spike_top_down.png')
        SLib.loadIfNotInImageCache('SpikeTop3', 'spike_top_right.png')

    def dataChanged(self):
        orientation = (self.parent.spritedata[5] >> 4) & 3
        direction = self.parent.spritedata[5] & 1
        
        if orientation & 1 == 1: #Wall
            self.yOffset = 0
                                                                                
            if orientation & 2 == 2: #Right Wall
                self.xOffset = 0
            else: #Left Wall
                self.xOffset = -8
                                                                                
        else: #Floor/Ceiling
            self.xOffset = 0
            
            if orientation & 2 == 2: #Ceiling
                self.yOffset = 0
            else: #Ground
                self.yOffset = -8
                
        t = QTransform()
        
        if direction == 1:
            if orientation & 1 == 1: #Wall
                t.scale(1, -1)
            else:
                t.scale(-1, 1)
        
        self.image = ImageCache['SpikeTop%d' % orientation].transformed(t)
        super().dataChanged()


class SpriteImage_ParachuteCoin(SLib.SpriteImage_StaticMultiple):  # 353
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ParachuteCoin0', 'parachute_coin_0.png')
        SLib.loadIfNotInImageCache('ParachuteCoin1', 'parachute_coin_1.png')
        SLib.loadIfNotInImageCache('ParachuteCoin2', 'parachute_coin_2.png')
        SLib.loadIfNotInImageCache('ParachuteCoin3', 'parachute_coin_3.png')

    def dataChanged(self):
        coinNum = self.parent.spritedata[8] & 3
        self.image = ImageCache['ParachuteCoin%d' % coinNum]

        if coinNum == 0:
            self.xOffset = -4
        else:
            self.xOffset = -8
            
        super().dataChanged()


class SpriteImage_RotatableIronPlatform(SLib.SpriteImage):  # 354
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovITopL', 'mov_iron_top_l.png')
        SLib.loadIfNotInImageCache('MovITopM', 'mov_iron_top_m.png')
        SLib.loadIfNotInImageCache('MovITopR', 'mov_iron_top_r.png')

    def dataChanged(self):
        super().dataChanged()

        self.width = ((self.parent.spritedata[8] & 0xF) + 1) << 4
        if self.width < 32:
            self.width = 32

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(0, 0, ImageCache['MovITopL'])
        painter.drawTiledPixmap(60, 0, ((self.width * 3.75) - 120), 60, ImageCache['MovITopM'])
        painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['MovITopR'])


class SpriteImage_RollingHillPipe(SLib.SpriteImage):  # 355
    def __init__(self, parent):
        super().__init__(parent, 3.75)

        self.aux.append(SLib.AuxiliaryCircleOutline(parent, 50 * 16))


class SpriteImage_MovingFirePiranha(SLib.SpriteImage_StaticMultiple):  # 362
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaUpFire', 'firetrap_pipe_up.png')
        SLib.loadIfNotInImageCache('PipePiranhaDownFire', 'firetrap_pipe_down.png')
        SLib.loadIfNotInImageCache('PipePiranhaLeftFire', 'firetrap_pipe_left.png')
        SLib.loadIfNotInImageCache('PipePiranhaRightFire', 'firetrap_pipe_right.png')

    def dataChanged(self):
        direction = (self.parent.spritedata[2] >> 4) & 3
        
        if direction == 1:
            self.image = ImageCache['PipePiranhaDownFire']
            self.xOffset = -8
            self.yOffset = 16
        elif direction == 2:
            self.image = ImageCache['PipePiranhaRightFire']
            self.xOffset = 8
            self.yOffset = 0
        elif direction == 3:
            self.image = ImageCache['PipePiranhaLeftFire']
            self.xOffset = -24
            self.yOffset = 0
        else:
            self.image = ImageCache['PipePiranhaUpFire']
            self.xOffset = -8
            self.yOffset = -16
        
        super().dataChanged()


class SpriteImage_Chest(SLib.SpriteImage_Static):  # 363
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Chest'],
            (-12, -12),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Chest', 'chest.png')


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


class SpriteImage_MoveWhenOnPlatform(SLib.SpriteImage):  # 367
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovWhenOnL', 'mov_when_on_l.png')
        SLib.loadIfNotInImageCache('MovWhenOnM', 'mov_when_on_m.png')
        SLib.loadIfNotInImageCache('MovIWhenOnR', 'mov_when_on_r.png')
        SLib.loadIfNotInImageCache('MovIWhenOnR', 'mov_when_on_arrow.png')
        SLib.loadIfNotInImageCache('MovIWhenOnArrowR', 'mov_when_on_arrow_r.png')
        SLib.loadIfNotInImageCache('MovIWhenOnArrowL', 'mov_when_on_arrow_l.png')
        SLib.loadIfNotInImageCache('MovIWhenOnArrowU', 'mov_when_on_arrow_u.png')
        SLib.loadIfNotInImageCache('MovIWhenOnArrowD', 'mov_when_on_arrow_d.png')

    def dataChanged(self):
        super().dataChanged()
        self.w = (self.parent.spritedata[8] & 0xF) * 60 + 30
        self.width = ((self.parent.spritedata[8] & 0xF) << 4) + 8
        self.xOffset = -4
        
        if self.width < 16:
            self.width = 32
            self.xOffset = -16

        direction = (self.parent.spritedata[3] >> 4) & 7
        self.dirStr = 'D'
        
        if direction == 0:
            self.dirStr = 'R'
        elif direction == 1:
            self.dirStr = 'L'
        elif direction == 2:
            self.dirStr = 'U'

    def paint(self, painter):
        super().paint(painter)
        painter.drawTiledPixmap(75, 0, self.w - 150, 60, ImageCache['MovWhenOnM'])

        if self.w >= 60:
            painter.drawPixmap(0, 0, ImageCache['MovWhenOnL'])
            painter.drawPixmap(self.w - 75, 0, ImageCache['MovIWhenOnR'])
        else:
            painter.drawPixmap(45, 0, ImageCache['MovWhenOnL'])
            painter.drawPixmap(0, 0, ImageCache['MovIWhenOnR'])
        
        painter.drawPixmap(self.width * 1.875 - 30, 0, ImageCache['MovIWhenOnArrow%s' % self.dirStr])

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


class SpriteImage_GreyBlock2(SLib.SpriteImage_StaticMultiple):  # 371, 373
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GrayBlock', 'gray_block.png')

    def dataChanged(self):
        width = (self.parent.spritedata[8] & 0xF) + 1
        height = (self.parent.spritedata[9] & 0xF) + 1
        self.image = ImageCache['GrayBlock'].transformed(QTransform().scale(width, height))
        super().dataChanged()

class SpriteImage_MovingOneWayPlatform(SpriteImage_PlatformBase):  # 372
    def __init__(self, parent):
        super().__init__(parent)

    def getPlatformWidth(self):
        width = (self.parent.spritedata[8] & 0xF) << 1

        if not width:
            return 4.5
        else:
            return width + 2.5

    def getPlatformOffset(self):
        return (-self.getPlatformWidth() * 8, 0)


class SpriteImage_ChainHolder(SLib.SpriteImage_Static):  # 374
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ChainHolder'],
            (0, -16)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ChainHolder', 'chain_holder.png')


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


class SpriteImage_TorpedoTed(SLib.SpriteImage_StaticMultiple):  # 379
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.xOffset = -24
        self.yOffset = -12

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TorpedoTedL', 'torpedo_ted.png')
        ImageCache['TorpedoTedR'] = ImageCache['TorpedoTedL'].transformed(QTransform().scale(-1, 1))

    def dataChanged(self):
        direction = self.parent.spritedata[4] & 3
        if direction == 2:
            self.image = ImageCache['TorpedoTedR']
        else:
            self.image = ImageCache['TorpedoTedL']
            
        super().dataChanged()


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

        color = self.parent.spritedata[9] & 0xF

        if color == 1:
            self.image = ImageCache['PinkBYoshi']
        elif color == 2:
            self.image = ImageCache['YellBYoshi']
        else:
            self.image = ImageCache['BlueBYoshi']


class SpriteImage_Dragoneel(SLib.SpriteImage_StaticMultiple):  # 382, 442, 488, 638
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.yOffset = -12

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('DragoneelBlueR', 'dragoneel_blue.png')
        SLib.loadIfNotInImageCache('DragoneelRedR', 'dragoneel_red.png')
        ImageCache['DragoneelBlueL'] = ImageCache['DragoneelBlueR'].transformed(QTransform().scale(-1, 1))
        ImageCache['DragoneelRedL'] = ImageCache['DragoneelRedR'].transformed(QTransform().scale(-1, 1))

    def dataChanged(self):
        isRight = (self.parent.spritedata[3] & 0x10) != 0
        color = self.parent.spritedata[5] & 3
        
        if color == 0:
            if isRight:
                self.image = ImageCache['DragoneelBlueR']
                self.xOffset = -248
            else:
                self.image = ImageCache['DragoneelBlueL']
                self.xOffset = -16
        else:
            if isRight:
                self.image = ImageCache['DragoneelRedR']
                self.xOffset = -548
            else:
                self.image = ImageCache['DragoneelRedL']
                self.xOffset = -16
        
        super().dataChanged()


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


class SpriteImage_MeltableIceChunk(SLib.SpriteImage_Static):  # 386
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MeltableIceChunk'],
            (-8, 0)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MeltableIceChunk', 'meltable_ice_chunk.png')


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


class SpriteImage_JungleBridge(SLib.SpriteImage):  # 390, 645
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False
        self.xOffset = -4
        self.yOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('JungleBridgeL', 'jungle_bridge_l.png')
        SLib.loadIfNotInImageCache('JungleBridgeM', 'jungle_bridge_m.png')
        SLib.loadIfNotInImageCache('JungleBridgeR', 'jungle_bridge_r.png')
        SLib.loadIfNotInImageCache('JungleBridgePillar', 'jungle_bridge_pillar.png')
        SLib.loadIfNotInImageCache('JungleBridgePillarTop', 'jungle_bridge_pillar_top.png')

    def dataChanged(self):
        super().dataChanged()
        self.width = ((self.parent.spritedata[8] & 0x1F) << 4) + 8
        self.height = 220

        if self.width == 8:
            self.width = 24

    def paint(self, painter):
        super().paint(painter)
        painter.drawTiledPixmap(15, 15, self.width * 3.75 - 30, 60, ImageCache['JungleBridgeM'], (ImageCache['JungleBridgeM'].width() - (self.width * 3.75 - 30)) * 0.5)
        painter.drawPixmap(0, 0, ImageCache['JungleBridgeL'])
        painter.drawPixmap(self.width * 3.75 - 75, 0, ImageCache['JungleBridgeR'])
        painter.drawPixmap(self.width * 1.875 - 45, 0, ImageCache['JungleBridgePillarTop'])
        painter.drawTiledPixmap(self.width * 1.875 - 30, 175, 60, self.height * 3.75 - 175, ImageCache['JungleBridgePillar'])


class SpriteImage_GrayCrystal(SLib.SpriteImage_StaticMultiple):  # 391
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GrayCrystalH0', 'crystal_gray_h_0.png')
        SLib.loadIfNotInImageCache('GrayCrystalH1', 'crystal_gray_h_1.png')
        SLib.loadIfNotInImageCache('GrayCrystalH2', 'crystal_gray_h_2.png')
        SLib.loadIfNotInImageCache('GrayCrystalH3', 'crystal_gray_h_3.png')
        SLib.loadIfNotInImageCache('GrayCrystalV0', 'crystal_gray_v_0.png')
        SLib.loadIfNotInImageCache('GrayCrystalV1', 'crystal_gray_v_1.png')
        SLib.loadIfNotInImageCache('GrayCrystalV2', 'crystal_gray_v_2.png')
        SLib.loadIfNotInImageCache('GrayCrystalV3', 'crystal_gray_v_3.png')

    def dataChanged(self):
        crystalType = self.parent.spritedata[4] & 0x3
        crystalRot = 'V' if ((self.parent.spritedata[5] >> 4) & 1) != 0 else 'H'
        self.image = ImageCache['GrayCrystal%s%d' % (crystalRot, crystalType)]

        if crystalRot == 'H':
            self.xOffset = -4
            self.yOffset = -4
        elif crystalType == 0:
            self.xOffset = 4
            self.yOffset = -12
        elif crystalType == 2:
            self.xOffset = 44
            self.yOffset = -52
        else:
            self.xOffset = 28
            self.yOffset = -36
        
        super().dataChanged()


class SpriteImage_3x3IceBlock(SLib.SpriteImage_StaticMultiple):  # 393
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('3x3IceBlock', '3x3_ice_block.png')

    def dataChanged(self):
        super().dataChanged()

        typeTemp = self.parent.spritedata[8] & 0xF

        if typeTemp == 1:
            self.width = 86.4
            self.height = 48
            self.image = ImageCache['3x3IceBlock'].transformed(QTransform().scale(1.8, 1))

        else:
            self.width = 48
            self.height = 48
            self.image = ImageCache['3x3IceBlock']


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
            self.yOffset = -36
        elif direction == 16:
            self.image = ImageCache['StarmanB']
            self.xOffset = -64
            self.yOffset = -60
        elif direction == 32:
            self.image = ImageCache['StarmanG']
            self.xOffset = -96
            self.yOffset = -92
        else:
            self.image = ImageCache['StarmanS']
            self.xOffset = -44
            self.yOffset = -36

        super().dataChanged()


class SpriteImage_BeanstalkLeaf(SLib.SpriteImage_StaticMultiple):  # 396
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.parent.setZValue(-20000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BeanstalkLeafGL0', 'beanstalk_leaf_l_s.png')
        SLib.loadIfNotInImageCache('BeanstalkLeafGL1', 'beanstalk_leaf_l_m.png')
        SLib.loadIfNotInImageCache('BeanstalkLeafGL2', 'beanstalk_leaf_l_l.png')
        SLib.loadIfNotInImageCache('BeanstalkLeafGR0', 'beanstalk_leaf_r_s.png')
        SLib.loadIfNotInImageCache('BeanstalkLeafGR1', 'beanstalk_leaf_r_m.png')
        SLib.loadIfNotInImageCache('BeanstalkLeafGR2', 'beanstalk_leaf_r_l.png')
        SLib.loadIfNotInImageCache('BeanstalkLeafRL0', 'beanstalk_leaf_l_s_red.png')
        SLib.loadIfNotInImageCache('BeanstalkLeafRL1', 'beanstalk_leaf_l_m_red.png')
        SLib.loadIfNotInImageCache('BeanstalkLeafRL2', 'beanstalk_leaf_l_l_red.png')
        SLib.loadIfNotInImageCache('BeanstalkLeafRR0', 'beanstalk_leaf_r_s_red.png')
        SLib.loadIfNotInImageCache('BeanstalkLeafRR1', 'beanstalk_leaf_r_m_red.png')
        SLib.loadIfNotInImageCache('BeanstalkLeafRR2', 'beanstalk_leaf_r_l_red.png')


    def dataChanged(self):
        color = 'G' if (self.parent.spritedata[5] & 0x10) != 0 else 'R'
        direction = 'R' if (self.parent.spritedata[5] & 1) != 0 else 'L'
        size = self.parent.spritedata[8] & 0xF
        if size > 2:
            size = 0

        if size == 0:
            self.yOffset = -8
        elif size == 1:
            self.yOffset = -12
        else:
            self.yOffset = -16
            
        if direction == 'R':
            self.xOffset = 0
        elif size == 0:
            self.xOffset = -44
        elif size == 1:
            self.xOffset = -92
        else:
            self.xOffset = -140
            
        self.image = ImageCache['BeanstalkLeaf%s%s%d' % (color, direction, size)] 
        super().dataChanged()


class SpriteImage_LanternPlatform(SLib.SpriteImage):  # 400
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False
        self.height = 24
        self.xOffset = -4
        self.yOffset = -4

    @staticmethod
    def loadImages():
        ImageCache['LanternPlatformLeft'] = SLib.GetImg('lantern_platform_l.png')
        ImageCache['LanternPlatformMiddle'] = SLib.GetImg('lantern_platform_m.png')
        ImageCache['LanternPlatformRight'] = SLib.GetImg('lantern_platform_r.png')
        ImageCache['LanternPlatformLeftLamp'] = SLib.GetImg('lantern_platform_l_lamp.png')
        ImageCache['LanternPlatformMiddleScrew'] = SLib.GetImg('lantern_platform_m_screw.png')
        ImageCache['LanternPlatformRightLamp'] = SLib.GetImg('lantern_platform_r_lamp.png')

    def dataChanged(self):
        super().dataChanged()

        self.screwPlacement = ((self.parent.spritedata[4] & 0x1) << 4) + ((self.parent.spritedata[5] & 0xF0) >> 4) # <- max length is 31
        self.platformLength = self.parent.spritedata[8] & 0b00011111 # <- max length is 31
        self.lanternPlacement = self.parent.spritedata[5] & 0x3 # values repeat after 3

        if self.lanternPlacement == 0:
            self.width = ((self.platformLength + 2) << 4) + 8
        elif self.lanternPlacement == 1 or self.lanternPlacement == 2:
            self.width = ((self.platformLength + 3) << 4) + 8
        else:
            self.width = ((self.platformLength + 4) << 4) + 8

    def paint(self, painter):
        super().paint(painter)

        if self.lanternPlacement < 2:
            painter.drawPixmap(0, 0, ImageCache['LanternPlatformLeft'])
            painter.drawTiledPixmap(75, 15, self.platformLength * 60, 60, ImageCache['LanternPlatformMiddle'])

            if self.screwPlacement > 0 and self.screwPlacement <= self.platformLength:
                painter.drawPixmap(self.screwPlacement * 60 + 15, 15, ImageCache['LanternPlatformMiddleScrew'])

            if self.lanternPlacement == 0:
                painter.drawPixmap(75 + self.platformLength * 60, 0, ImageCache['LanternPlatformRight'])
            else:
                painter.drawPixmap(75 + self.platformLength * 60, 0, ImageCache['LanternPlatformRightLamp'])
        else:
            painter.drawPixmap(0, 0, ImageCache['LanternPlatformLeftLamp'])
            painter.drawTiledPixmap(135, 15, self.platformLength * 60, 60, ImageCache['LanternPlatformMiddle'])
            
            if self.screwPlacement > 1 and self.screwPlacement <= self.platformLength + 1:
                painter.drawPixmap(self.screwPlacement * 60 + 15, 15, ImageCache['LanternPlatformMiddleScrew'])

            if self.lanternPlacement == 2:
                painter.drawPixmap(135 + self.platformLength * 60, 0, ImageCache['LanternPlatformRight'])
            else:
                painter.drawPixmap(135 + self.platformLength * 60, 0, ImageCache['LanternPlatformRightLamp'])


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


class SpriteImage_Toad(SLib.SpriteImage_StaticMultiple):  # 408
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.yOffset = -32

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ToadL', 'toad.png')
        ImageCache['ToadR'] = ImageCache['ToadL'].transformed(QTransform().scale(-1, 1))

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 3

        if direction == 1:
            self.image = ImageCache['ToadR']
            self.xOffset = -12
        else:
            self.image = ImageCache['ToadL']
            self.xOffset = -8

        super().dataChanged()


class SpriteImage_ChainChomp(SLib.SpriteImage_StaticMultiple):  # 409
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.yOffset = -36

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ChainChomp0', 'chain_chomp_0.png')
        SLib.loadIfNotInImageCache('ChainChomp1', 'chain_chomp_1.png')

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 1

        if direction == 1:
            self.image = ImageCache['ChainChomp1']
            self.xOffset = -4
        else:
            self.image = ImageCache['ChainChomp0']
            self.xOffset = -36

        super().dataChanged()


class SpriteImage_CastlePlatformLudwig(SLib.SpriteImage_StaticMultiple):  # 410
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.xOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CastlePlatformLudwig0', 'castle_platform_ludwig_0.png')
        SLib.loadIfNotInImageCache('CastlePlatformLudwig1', 'castle_platform_ludwig_1.png')
        SLib.loadIfNotInImageCache('CastlePlatformLudwig2', 'castle_platform_ludwig_2.png')

    def dataChanged(self):
        platformType = self.parent.spritedata[4]
        if platformType > 2:
            platformType = 0
            
        self.image = ImageCache['CastlePlatformLudwig%d' % platformType]
        super().dataChanged()


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


class SpriteImage_BeanstalkTendril(SLib.SpriteImage_StaticMultiple):  # 425
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.parent.setZValue(-20000)
        self.yOffset = -36
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].alpha = 0.4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BeanstalkTendril0', 'beanstalk_tendril_0.png')
        SLib.loadIfNotInImageCache('BeanstalkTendril1', 'beanstalk_tendril_1.png')
        SLib.loadIfNotInImageCache('BeanstalkTendrilStretched0L', 'beanstalk_tendril_stretched_0_long.png')
        SLib.loadIfNotInImageCache('BeanstalkTendrilStretched1L', 'beanstalk_tendril_stretched_1_long.png')
        SLib.loadIfNotInImageCache('BeanstalkTendrilStretched0S', 'beanstalk_tendril_stretched_0_short.png')
        SLib.loadIfNotInImageCache('BeanstalkTendrilStretched1S', 'beanstalk_tendril_stretched_1_short.png')

    def dataChanged(self):
        direction = (self.parent.spritedata[4] >> 4) & 1
        tendrilType = 'S' if (self.parent.spritedata[4] & 1) != 0 else 'L'
        self.image = ImageCache['BeanstalkTendril%d' % direction]

        self.aux[0].image = ImageCache['BeanstalkTendrilStretched%d%s' % (direction, tendrilType)]
        self.aux[0].setSize(self.aux[0].image.width(), self.aux[0].image.height())

        if direction == 0:
            self.xOffset = -8
            self.aux[0].setPos(0, 120)
        else:
            self.xOffset = -36
            self.aux[0].setPos(self.image.width() - self.aux[0].image.width(), 120)
            
        super().dataChanged()


class SpriteImage_Ballon(SLib.SpriteImage):  # 426
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False
        self.xOffset = -4
        self.width = 24

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Balloon0', 'balloon_0.png')
        SLib.loadIfNotInImageCache('Balloon1', 'balloon_1.png')
        SLib.loadIfNotInImageCache('Balloon2', 'balloon_2.png')
        SLib.loadIfNotInImageCache('Balloon3', 'balloon_3.png')
        SLib.loadIfNotInImageCache('BalloonGoomba', 'balloon_goomba.png')

    def dataChanged(self):
        self.color = (self.parent.spritedata[5] >> 4) & 3
        self.isCoin = (self.parent.spritedata[5] & 2) != 0
        self.height = 68 if self.isCoin else 60
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(0, 0, ImageCache['Balloon%d' % self.color])

        if self.isCoin:
            painter.drawPixmap(15, 195, SLib.Tiles[30].main)
        else:
            painter.drawPixmap(0, 150, ImageCache['BalloonGoomba'])


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


class SpriteImage_CastleRailLudwig(SLib.SpriteImage):  # 428
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False
        self.yOffset = -4
        self.height = 40

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CastleRailLudwigL', 'castle_rail_ludwig_l.png')
        SLib.loadIfNotInImageCache('CastleRailLudwigM', 'castle_rail_ludwig_m.png')
        SLib.loadIfNotInImageCache('CastleRailLudwigR0', 'castle_rail_ludwig_r_0.png')
        SLib.loadIfNotInImageCache('CastleRailLudwigR1', 'castle_rail_ludwig_r_1.png')

    def dataChanged(self):
        width_ = (self.parent.spritedata[8] + 3)
        
        self.endType = width_ & 1
        self.width = width_ << 4
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        painter.drawTiledPixmap(60, 15, self.width * 3.75 - 120, 120, ImageCache['CastleRailLudwigM'])
        painter.drawPixmap(0, 0, ImageCache['CastleRailLudwigL'])
        painter.drawPixmap(self.width * 3.75 - 75, 0, ImageCache['CastleRailLudwigR%d' % self.endType])


class SpriteImage_MetalBar(SLib.SpriteImage_StaticMultiple):  # 429
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.parent.setZValue(-20000)
        self.xOffset = -4
        self.yOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MetalBar0', 'metal_bar_0.png')
        SLib.loadIfNotInImageCache('MetalBar1', 'metal_bar_1.png')
        SLib.loadIfNotInImageCache('MetalBar2', 'metal_bar_2.png')
        SLib.loadIfNotInImageCache('MetalBar3', 'metal_bar_3.png')
        SLib.loadIfNotInImageCache('MetalBar4', 'metal_bar_4.png')
        SLib.loadIfNotInImageCache('MetalBar5', 'metal_bar_5.png')
        SLib.loadIfNotInImageCache('MetalBar6', 'metal_bar_6.png')

    def dataChanged(self):
        barType = self.parent.spritedata[5] & 7
        if barType > 6:
            barType = 0

        self.image = ImageCache['MetalBar%d' % barType]
        super().dataChanged()


class SpriteImage_MortonStoneBlock(SLib.SpriteImage):  # 431
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MortonStoneBlockT', 'morton_stone_block_t.png')
        SLib.loadIfNotInImageCache('MortonStoneBlockTL', 'morton_stone_block_tl.png')
        SLib.loadIfNotInImageCache('MortonStoneBlockTR', 'morton_stone_block_tr.png')
        SLib.loadIfNotInImageCache('MortonStoneBlockL', 'morton_stone_block_l.png')
        SLib.loadIfNotInImageCache('MortonStoneBlockM', 'morton_stone_block_m.png')
        SLib.loadIfNotInImageCache('MortonStoneBlockR', 'morton_stone_block_r.png')
        SLib.loadIfNotInImageCache('MortonStoneBlockB', 'morton_stone_block_b.png')
        SLib.loadIfNotInImageCache('MortonStoneBlockBL', 'morton_stone_block_bl.png')
        SLib.loadIfNotInImageCache('MortonStoneBlockBR', 'morton_stone_block_br.png')

    def dataChanged(self):
        super().dataChanged()

        self.w = self.parent.spritedata[8] + 1
        self.h = self.parent.spritedata[9] + 1

        if self.w < 2:
            self.w = 2
        if self.h < 2:
            self.h = 2

        self.width = self.w << 4
        self.height = self.h << 4

    def paint(self, painter):
        super().paint(painter)

        # Draw middle
        painter.drawTiledPixmap(30, 30, (self.w - 1) * 60, (self.h - 1) * 60, ImageCache['MortonStoneBlockM'], ImageCache['MortonStoneBlockM'].width() / 2 - ((self.w - 1) / 2) * 60, ImageCache['MortonStoneBlockM'].height() / 2 - ((self.h - 1) / 2) * 60)

        # Draw top row
        painter.drawPixmap(0, 0, ImageCache['MortonStoneBlockTL'])
        painter.drawTiledPixmap(60, 0, (self.w - 2) * 60, 60, ImageCache['MortonStoneBlockT'])
        painter.drawPixmap((self.w - 1) * 60, 0, ImageCache['MortonStoneBlockTR'])

        # Draw left and right side
        painter.drawTiledPixmap(0, 60, 60, (self.h - 2) * 60, ImageCache['MortonStoneBlockL'])
        painter.drawTiledPixmap((self.w - 1) * 60, 60, 60, (self.h - 2) * 60, ImageCache['MortonStoneBlockR'])

        # Draw bottom row
        painter.drawPixmap(0, (self.h - 1) * 60, ImageCache['MortonStoneBlockBL'])
        painter.drawTiledPixmap(60, (self.h - 1) * 60, (self.w - 2) * 60, 60, ImageCache['MortonStoneBlockB'])
        painter.drawPixmap((self.w - 1) * 60, (self.h - 1) * 60, ImageCache['MortonStoneBlockBR'])


class SpriteImage_RotatingIronBlock(SpriteImage_MovingIronBlock):  # 434, 709, 711
    def __init__(self, parent):
        super().__init__(parent)

    def dataChanged(self):
        super().dataChanged()
        self.width = (self.parent.spritedata[8] & 0xF) * 16 + 48
        self.height = (self.parent.spritedata[9] & 0xF) * 16 + 48


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


class SpriteImage_GoldenPipeDown(SLib.SpriteImage_Static):  # 458
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GoldenPipeDown'],
            (0, -96),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GoldenPipeDown', 'golden_pipe_down.png')


class SpriteImage_WobbyBonePlatform(SLib.SpriteImage):  # 457
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WobbyBoneL', 'wobby_bone_l.png')
        SLib.loadIfNotInImageCache('WobbyBoneM', 'wobby_bone_m.png')
        SLib.loadIfNotInImageCache('WobbyBoneR', 'wobby_bone_r.png')

    def dataChanged(self):
        super().dataChanged()

        self.length = self.parent.spritedata[8]

        if not self.length:
            self.spritebox.shown = True
            self.width, self.height = 16, 16

        else:
            self.spritebox.shown = False
            self.width = self.length * 16
            self.height = 32

    def paint(self, painter):
        super().paint(painter)

        if self.length == 1:
            painter.drawPixmap(0, 0, ImageCache['WobbyBoneL'])

        elif self.length:
            painter.drawPixmap(0, 0, ImageCache['WobbyBoneL'])
            painter.drawTiledPixmap(60, 0, (self.width - 32) * 3.75, 120, ImageCache['WobbyBoneM'])
            painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['WobbyBoneR'])


class SpriteImage_Bowser(SLib.SpriteImage_Static):  # 462
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Bowser'],
            (-56, -80),
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


class SpriteImage_KamekFloor(SLib.SpriteImage_StaticMultiple):  # 465
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('KamekFloor0', 'kamek_floor_0.png')
        SLib.loadIfNotInImageCache('KamekFloor1', 'kamek_floor_1.png')
        SLib.loadIfNotInImageCache('KamekFloor2', 'kamek_floor_2.png')
        SLib.loadIfNotInImageCache('KamekFloor3', 'kamek_floor_3.png')

    def dataChanged(self):
        floorType = self.parent.spritedata[5] & 0x3
        self.image = ImageCache['KamekFloor%d' % floorType]
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


class SpriteImage_Peach(SLib.SpriteImage_Static):  # 469
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Peach'],
            (-16, -48),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Peach', 'peach.png')


class SpriteImage_MediumGoomba(SLib.SpriteImage_Static):  # 471
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MediumGoomba'],
            (-8, -20)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MediumGoomba', 'medium_goomba.png')


class SpriteImage_BigGoomba(SLib.SpriteImage_Static):  # 472
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigGoomba'],
            (-16, -36)
        )

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


class SpriteImage_ToadHouseCannon(SLib.SpriteImage_StaticMultiple):  # 474
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.xOffset = -28
        self.yOffset = -48

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ToadHouseCannonL', 'toad_house_cannon.png')
        ImageCache['ToadHouseCannonR'] = ImageCache['ToadHouseCannonL'].transformed(QTransform().scale(-1, 1))

    def dataChanged(self):
        direction = 'R' if (self.parent.spritedata[5] & 1) != 0 else 'L'
        self.image = ImageCache['ToadHouseCannon%s' % direction]
        super().dataChanged()


class SpriteImage_BigQBlock(SLib.SpriteImage):  # 475
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

        self.dimensions = (0, 16, 32, 32)

    def dataChanged(self):
        super().dataChanged()

        self.contents = self.parent.spritedata[9] & 0xF
        self.acorn = (self.parent.spritedata[6] >> 4) & 1

        items = {0: 0x800 + len(globals.Overrides) - 1, 1: 49, 2: 32, 3: 32, 4: 37, 5: 38, 6: 36, 7: 33, 8: 34, 9: 41, 12: 35, 13: 42, 15: 39}

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


class SpriteImage_BowserJrBlock(SLib.SpriteImage_Static):  # 478
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BowserJrBlock'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BowserJrBlock', 'bowser_jr_block.png')


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


class SpriteImage_MechaCheep(SLib.SpriteImage_Static):  # 482
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MechaCheep'],
            (0, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MechaCheep', 'cheep_mecha.png')


class SpriteImage_MetalBarGearbox(SLib.SpriteImage_StaticMultiple):  # 485
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.xOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MetalBarGearbox0', 'metal_bar_gearbox_0.png')
        SLib.loadIfNotInImageCache('MetalBarGearbox1', 'metal_bar_gearbox_1.png')
        SLib.loadIfNotInImageCache('MetalBarGearbox2', 'metal_bar_gearbox_2.png')

    def dataChanged(self):
        barType = self.parent.spritedata[5] & 3
        if barType > 2:
            barType = 0

        if barType == 2:
            self.yOffset = -64
        else:
            self.yOffset = -4
            
        self.image = ImageCache['MetalBarGearbox%d' % barType]
        super().dataChanged()


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


class SpriteImage_MovingBonePlatform(SpriteImage_PlatformBase):  # 491, 492, 627
    def __init__(self, parent):
        super().__init__(parent)
        
    def getPlatformWidth(self):
        width = (self.parent.spritedata[8] & 0xF) + 1
        if width == 1:
            width = 2
            
        return width + 0.5

    def getPlatformType(self):
        return 'B'


class SpriteImage_World7Platform(SLib.SpriteImage_StaticMultiple):  # 493
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('W7PlatformThin', 'w7_platform_thin.png')
        SLib.loadIfNotInImageCache('W7PlatformThick', 'w7_platform_thick.png')

    def dataChanged(self):
        platformType = self.parent.spritedata[5]

        if not platformType:
            self.image = ImageCache['W7PlatformThin']
            self.xOffset = -32
        else:
            self.image = ImageCache['W7PlatformThick']
            self.xOffset = -64

        super().dataChanged()


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


class SpriteImage_BowserAmp(SLib.SpriteImage_Static):  # 500
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BowserAmp'],
            (-4, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BowserAmp', 'bowser_amp.png')


class SpriteImage_ChallengeOnlyBlock(SLib.SpriteImage):  # 506
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('NabbitMetal', 'nabbit_metal.png')

    def dataChanged(self):
        self.width = ((self.parent.spritedata[8] & 3) + 1) << 4
        self.height = ((self.parent.spritedata[9] & 0x1F) + 1) << 4
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        painter.drawTiledPixmap(0, 0, self.width * 3.75, self.height * 3.75, ImageCache['NabbitMetal'])


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


class SpriteImage_CloudPlatform(SLib.SpriteImage_Static):  # 508
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['CloudPlatform'],
            (-160, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CloudPlatform', 'cloud_platform.png')


class SpriteImage_GhostShipBlock(SLib.SpriteImage):  # 512
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GhostShipBlockT', 'ghost_ship_block_t.png')
        SLib.loadIfNotInImageCache('GhostShipBlockTL', 'ghost_ship_block_tl.png')
        SLib.loadIfNotInImageCache('GhostShipBlockTR', 'ghost_ship_block_tr.png')
        SLib.loadIfNotInImageCache('GhostShipBlockL', 'ghost_ship_block_l.png')
        SLib.loadIfNotInImageCache('GhostShipBlockM', 'ghost_ship_block_m.png')
        SLib.loadIfNotInImageCache('GhostShipBlockR', 'ghost_ship_block_r.png')
        SLib.loadIfNotInImageCache('GhostShipBlockB', 'ghost_ship_block_b.png')
        SLib.loadIfNotInImageCache('GhostShipBlockBL', 'ghost_ship_block_bl.png')
        SLib.loadIfNotInImageCache('GhostShipBlockBR', 'ghost_ship_block_br.png')

    def dataChanged(self):
        super().dataChanged()

        self.w = self.parent.spritedata[8] + 3
        self.h = self.parent.spritedata[9] + 3
        self.width = self.w << 4
        self.height = self.h << 4

    def paint(self, painter):
        super().paint(painter)

        # Draw middle
        painter.drawTiledPixmap(60, 60, (self.w - 2) * 60, (self.h - 2) * 60, ImageCache['GhostShipBlockM'], 15, ImageCache['GhostShipBlockM'].height() - (((self.h - 2) * 60) % ImageCache['GhostShipBlockM'].height()))

        # Draw top row
        painter.drawPixmap(0, 0, ImageCache['GhostShipBlockTL'])
        painter.drawTiledPixmap(60, 0, (self.w - 2) * 60, 60, ImageCache['GhostShipBlockT'])
        painter.drawPixmap((self.w - 1) * 60, 0, ImageCache['GhostShipBlockTR'])

        # Draw left and right side
        painter.drawTiledPixmap(0, 60, 60, (self.h - 2) * 60, ImageCache['GhostShipBlockL'])
        painter.drawTiledPixmap((self.w - 1) * 60, 60, 60, (self.h - 2) * 60, ImageCache['GhostShipBlockR'])

        # Draw bottom row
        painter.drawPixmap(0, (self.h - 1) * 60, ImageCache['GhostShipBlockBL'])
        painter.drawTiledPixmap(60, (self.h - 1) * 60, (self.w - 2) * 60, 60, ImageCache['GhostShipBlockB'])
        painter.drawPixmap((self.w - 1) * 60, (self.h - 1) * 60, ImageCache['GhostShipBlockBR'])


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


class SpriteImage_MovingCastleGround(SLib.SpriteImage):  # 515
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False
        self.height = 256

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovCastle0TL', 'mov_castle_tl_0.png')
        SLib.loadIfNotInImageCache('MovCastle0TM', 'mov_castle_tm_0.png')
        SLib.loadIfNotInImageCache('MovCastle0TR', 'mov_castle_tr_0.png')
        SLib.loadIfNotInImageCache('MovCastle0L', 'mov_castle_l_0.png')
        SLib.loadIfNotInImageCache('MovCastle0M', 'mov_castle_m_0.png')
        SLib.loadIfNotInImageCache('MovCastle0R', 'mov_castle_r_0.png')
        SLib.loadIfNotInImageCache('MovCastle1TL', 'mov_castle_tl_1.png')
        SLib.loadIfNotInImageCache('MovCastle1TM', 'mov_castle_tm_1.png')
        SLib.loadIfNotInImageCache('MovCastle1TR', 'mov_castle_tr_1.png')
        SLib.loadIfNotInImageCache('MovCastle1L', 'mov_castle_l_1.png')
        SLib.loadIfNotInImageCache('MovCastle1M', 'mov_castle_m_1.png')
        SLib.loadIfNotInImageCache('MovCastle1R', 'mov_castle_r_1.png')

    def dataChanged(self):
        widthArray = [5, 7, 10, 11, 16, 64]
        idx = self.parent.spritedata[5]
        if idx > 5:
            idx = 0
        
        self.width = widthArray[idx] << 4
        self.groundType = widthArray[idx] & 1
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        sideWidth = ImageCache['MovCastle%dTL' % self.groundType].width()
        midWidth = self.width * 3.75 - sideWidth * 2
        
        # Draw top row
        painter.drawPixmap(0, 0, ImageCache['MovCastle%dTL' % self.groundType])
        painter.drawTiledPixmap(sideWidth, 0, midWidth, 60, ImageCache['MovCastle%dTM' % self.groundType])
        painter.drawPixmap(sideWidth + midWidth, 0, ImageCache['MovCastle%dTR' % self.groundType])

        # Draw middle
        painter.drawTiledPixmap(0,                    60, sideWidth, self.height * 3.75, ImageCache['MovCastle%dL' % self.groundType])
        painter.drawTiledPixmap(sideWidth,            60, midWidth,  self.height * 3.75, ImageCache['MovCastle%dM' % self.groundType])
        painter.drawTiledPixmap(sideWidth + midWidth, 60, sideWidth, self.height * 3.75, ImageCache['MovCastle%dR' % self.groundType])


class SpriteImage_BowserSwitch(SLib.SpriteImage_Static):  # 520
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BowserSwitch'],
            (-44, -56),
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
        painter.drawPixmap(45, 57.5, SLib.Tiles[0x800 + len(globals.Overrides) - 1].main)


class SpriteImage_MovementControlledTowerBlock(SLib.SpriteImage_Static):  # 524, 669
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['TowerBlock'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TowerBlock', 'tower_block.png')


class SpriteImage_BoltStoneBlock(SLib.SpriteImage_StaticMultiple):  # 530, 625
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        for i in range(0, 7):
            SLib.loadIfNotInImageCache('BoltStoneBlock%d' % i, 'bolt_stone_block_%d.png' % i)

    def dataChanged(self):
        size = self.parent.spritedata[5] & 0xF; size = 0 if size > 6 else size
        self.image = ImageCache['BoltStoneBlock%d' % size]
        super().dataChanged()


class SpriteImage_WendyIcicle(SLib.SpriteImage_Static):  # 533
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['WendyIcicle'],
            (-8, -4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WendyIcicle', 'wendy_icicle.png')


class SpriteImage_MovingGroupedPlatform(SpriteImage_PlatformBase):  # 534, 535
    def __init__(self, parent):
        super().__init__(parent)

    def getPlatformWidth(self):
        if self.getPlatformType() == 'C':
            return 2.5
        
        width = (self.parent.spritedata[8] & 0xF) + 1
        if width < 2:
            width = 2

        return width + 0.5

    def getPlatformType(self):
        type_ = self.parent.spritedata[3] >> 4

        if type_ == 1:
            return 'R'
        elif type_ == 3:
            return 'S'
        elif type_ == 4:
            return 'C'
        else:
            return 'N'

    def getPlatformOffset(self):
        if self.getPlatformType() == 'C':
            return (-4, -4)
        else:
            return (-4, 0)


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


class SpriteImage_Wrench(SLib.SpriteImage_Static):  # 537
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Wrench'],
            (0, -4), # Aligned with the y-pos it moves to, not where is spawns
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Wrench', 'wrench.png')


class SpriteImage_MushroomMovingPlatform(SLib.SpriteImage):  # 544
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        for i in range(3):
            SLib.loadIfNotInImageCache('WobbleMushL%d' % i, 'wobble_mushroom_l_%d.png' % i)
            SLib.loadIfNotInImageCache('WobbleMushM%d' % i, 'wobble_mushroom_m_%d.png' % i)
            SLib.loadIfNotInImageCache('WobbleMushR%d' % i, 'wobble_mushroom_r_%d.png' % i)
            SLib.loadIfNotInImageCache('WobbleMushStemTop%d' % i, 'wobble_mushroom_stem_top_%d.png' % i)
            SLib.loadIfNotInImageCache('WobbleMushStem%d' % i, 'wobble_mushroom_stem_%d.png' % i)

    def dataChanged(self):
        self.color = (self.parent.spritedata[7] & 0x30) >> 4
        if self.color > 2:
            self.color = 0

        self.wobbleUpDown = (self.parent.spritedata[3] & 0x20) != 0
        self.oppositeDir = (self.parent.spritedata[6] & 1) != 0
        self.width = ((self.parent.spritedata[4] >> 4) + 3) << 4
        self.xOffset = -0.5 * (self.width - 16)

        if self.wobbleUpDown:
            self.minHeight = ((self.parent.spritedata[6] >> 4) + 2.5) * 16
            self.height = ((self.parent.spritedata[3] & 0x7) + (self.parent.spritedata[6] >> 4) + 2.5) * 16
            self.yOffset = -((self.parent.spritedata[3] & 0x7) << 4)
        else:
            self.minHeight = ((self.parent.spritedata[3] & 0x7) + 5) << 4
            self.height = ((self.parent.spritedata[3] & 0x7) + 5) << 4
            self.yOffset = 0
        
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        ghostOffset = 0
        regularOffset = (self.height - self.minHeight) * 3.75
        
        if self.oppositeDir:
            ghostOffset = regularOffset
            regularOffset = 0

        # Top
        painter.drawPixmap(0, regularOffset, ImageCache['WobbleMushL%d' % self.color])
        painter.drawTiledPixmap(60, regularOffset, (self.width - 32) * 3.75, 60, ImageCache['WobbleMushM%d' % self.color])
        painter.drawPixmap((self.width - 16) * 3.75, regularOffset, ImageCache['WobbleMushR%d' % self.color])

        # Stem
        painter.drawPixmap((self.width - 16) * 1.875 - 15, regularOffset + 60, ImageCache['WobbleMushStemTop%d' % self.color])
        painter.drawTiledPixmap((self.width - 16) * 1.875, (self.height - 8) * 3.75, 60, 30, ImageCache['WobbleMushStem%d' % self.color], 0, 30 if self.wobbleUpDown else 0)
        painter.drawTiledPixmap((self.width - 16) * 1.875, regularOffset + 120, 60, (self.height - 40) * 3.75 - regularOffset, ImageCache['WobbleMushStem%d' % self.color])

        # Ghost
        if self.wobbleUpDown and self.height - self.minHeight > 0:
            painter.setOpacity(0.5)
            painter.drawPixmap(0, ghostOffset, ImageCache['WobbleMushL%d' % self.color])
            painter.drawTiledPixmap(60, ghostOffset, (self.width - 32) * 3.75, 60, ImageCache['WobbleMushM%d' % self.color])
            painter.drawPixmap((self.width - 16) * 3.75, ghostOffset, ImageCache['WobbleMushR%d' % self.color])
            painter.drawPixmap((self.width - 16) * 1.875 - 15, ghostOffset + 60, ImageCache['WobbleMushStemTop%d' % self.color])
            painter.drawTiledPixmap((self.width - 16) * 1.875, ghostOffset + 120, 60, (self.height - self.minHeight) * 3.75, ImageCache['WobbleMushStem%d' % self.color])
            painter.setOpacity(1)


class SpriteImage_Flowers(SLib.SpriteImage):  # 546
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.height = 16
        self.spritebox.shown = False

    def dataChanged(self):
        super().dataChanged()

        self.type = self.parent.spritedata[5] & 0xF
        if self.type == 0:
            self.type = 1

        if self.type < 6 or self.type == 7:
            self.width = 64

        elif self.type == 6 or self.type > 13:
            self.width = 48

        elif self.type == 8:
            self.width = 80

        elif self.type < 12:
            self.width = 16

        else:
            self.width = 32

        self.xOffset = -(self.width / 2) + 8

    def paint(self, painter):
        super().paint(painter)

        # Draw the first tile
        if self.type < 9:
            painter.drawPixmap(0, 0, SLib.Tiles[178].main)

        elif self.type in [9, 12, 14]:
            painter.drawPixmap(0, 0, SLib.Tiles[211].main)

        elif self.type in [10, 15]:
            painter.drawPixmap(0, 0, SLib.Tiles[212].main)

        else:
            painter.drawPixmap(0, 0, SLib.Tiles[210].main)

        # Draw the second tile
        if self.type < 3:
            painter.drawPixmap(60, 0, SLib.Tiles[214].main)

        elif self.type < 5:
            painter.drawPixmap(60, 0, SLib.Tiles[213].main)

        elif self.type < 9:
            painter.drawPixmap(60, 0, SLib.Tiles[179].main)

        elif self.type > 11 and self.type < 14:
            painter.drawPixmap(60, 0, SLib.Tiles[212].main)

        elif self.type > 11:
            painter.drawPixmap(60, 0, SLib.Tiles[210].main)

        # Draw the third tile
        if self.type in [1, 3]:
            painter.drawPixmap(120, 0, SLib.Tiles[215].main)

        elif self.type == 2:
            painter.drawPixmap(120, 0, SLib.Tiles[213].main)

        elif self.type < 6:
            painter.drawPixmap(120, 0, SLib.Tiles[214].main)

        elif self.type == 6:
            painter.drawPixmap(120, 0, SLib.Tiles[182].main)

        elif self.type < 9:
            painter.drawPixmap(120, 0, SLib.Tiles[180].main)

        elif self.type == 14:
            painter.drawPixmap(120, 0, SLib.Tiles[212].main)

        elif self.type == 15:
            painter.drawPixmap(120, 0, SLib.Tiles[211].main)

        # Draw the fourth tile
        if self.type < 8 and self.type != 6:
            painter.drawPixmap(180, 0, SLib.Tiles[182].main)

        elif self.type == 8:
            painter.drawPixmap(180, 0, SLib.Tiles[179].main)

        # Draw the fifth tile
        if self.type == 8:
            painter.drawPixmap(240, 0, SLib.Tiles[182].main)


class SpriteImage_Sprite548(SLib.SpriteImage_Static):  # 548
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Sprite548'],
            (4, 0),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Sprite548', 'sprite548.png')


class SpriteImage_DesertBlock(SLib.SpriteImage_Static):  # 549
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['DesertBlock'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('DesertBlock', 'desert_block.png')
        

class SpriteImage_GiantPipePiranha(SLib.SpriteImage_StaticMultiple):  # 550
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantPipePiranhaUp', 'pipe_piranha_big.png')
        SLib.loadIfNotInImageCache('GiantPipePiranhaDown', 'pipe_piranha_big_down.png')
        SLib.loadIfNotInImageCache('GiantPipePiranhaRight', 'pipe_piranha_big_right.png')
        SLib.loadIfNotInImageCache('GiantPipePiranhaLeft', 'pipe_piranha_big_left.png')

    def dataChanged(self):

        direction = (self.parent.spritedata[2] >> 4) & 3

        if direction == 0:
            self.image = ImageCache['GiantPipePiranhaUp']
            self.offset = (-24, -128)
        elif direction == 1:
            self.image = ImageCache['GiantPipePiranhaDown']
            self.offset = (-24, 64)
        elif direction == 2:
            self.image = ImageCache['GiantPipePiranhaRight']
            self.offset = (64, -24)
        else:
            self.image = ImageCache['GiantPipePiranhaLeft']
            self.offset = (-128, -24)

        super().dataChanged()


class SpriteImage_SteerablePlatform(SLib.SpriteImage_StaticMultiple):  # 553
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.xOffset = -4
        self.yOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SteerablePlatform0', 'steerable_platform_0.png')
        SLib.loadIfNotInImageCache('SteerablePlatform1', 'steerable_platform_1.png')
        SLib.loadIfNotInImageCache('SteerablePlatform2', 'steerable_platform_2.png')
        SLib.loadIfNotInImageCache('SteerablePlatform3', 'steerable_platform_3.png')

    def dataChanged(self):
        size = self.parent.spritedata[8] & 3
        self.image = ImageCache['SteerablePlatform%d' % size]
        super().dataChanged()


class SpriteImage_NabbitRefugeLocation(SLib.SpriteImage):  # 559
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def dataChanged(self):
        super().dataChanged()

        h = self.parent.spritedata[5] >> 4
        w = self.parent.spritedata[5] & 0xF
        if w == 0:
            w = 1
        if h == 0:
            h = 1
        
        if w == 1 and h == 1:  # no point drawing a 1x1 outline behind the self.parent
            self.aux[0].setSize(0, 0)
            return
        self.aux[0].setSize(w * 60, h * 60)

class SpriteImage_WendyFloor(SLib.SpriteImage):  # 560
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].image = ImageCache['WendyFloor']
        self.aux[0].alpha = 0.5
        self.aux[0].setSize(self.aux[0].image.width(), self.aux[0].image.height(), -self.aux[0].image.width() * 0.5, 180 - self.aux[0].image.height())
        self.aux[0].setZValue(-50000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WendyFloor', 'wendy_floor.png')


class SpriteImage_RecordSignboard(SLib.SpriteImage):  # 561
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def dataChanged(self):
        super().dataChanged()

        w = ((self.parent.spritedata[2] >> 4) & 0xF) + 1
        self.xOffset = -0.5 * (w - 1) * 16
        self.aux[0].setSize(w * 60, 60)


class SpriteImage_MovingSkyBlock(SLib.SpriteImage):  # 562, 563
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovSkyTL', 'mov_sky_top_l.png')
        SLib.loadIfNotInImageCache('MovSkyTM', 'mov_sky_top_m.png')
        SLib.loadIfNotInImageCache('MovSkyTR', 'mov_sky_top_r.png')
        SLib.loadIfNotInImageCache('MovSkyML', 'mov_sky_middle_l.png')
        SLib.loadIfNotInImageCache('MovSkyMM', 'mov_sky_middle_m.png')
        SLib.loadIfNotInImageCache('MovSkyMR', 'mov_sky_middle_r.png')
        SLib.loadIfNotInImageCache('MovSkyBL', 'mov_sky_bottom_l.png')
        SLib.loadIfNotInImageCache('MovSkyBM', 'mov_sky_bottom_m.png')
        SLib.loadIfNotInImageCache('MovSkyBR', 'mov_sky_bottom_r.png')

    def dataChanged(self):
        super().dataChanged()

        self.w = (self.parent.spritedata[8] & 0xF) + 1
        self.h = (self.parent.spritedata[9] & 0xF) + 1

        if self.w < 2:
            self.w = 2
        if self.h < 2:
            self.h = 2
        
        self.width = self.w << 4
        self.height = self.h << 4

    def paint(self, painter):
        super().paint(painter)
        # Draw top row
        painter.drawPixmap(0, 0, ImageCache['MovSkyTL'])
        painter.drawTiledPixmap(60, 0, (self.w - 2) * 60, 60, ImageCache['MovSkyTM'])
        painter.drawPixmap((self.w - 1) * 60, 0, ImageCache['MovSkyTR'])

        # Draw middle
        painter.drawTiledPixmap(0, 60, 60, (self.h - 2) * 60, ImageCache['MovSkyML'], 0, (0 if (self.h & 1) == 0 else 60))
        painter.drawTiledPixmap(60, 60, (self.w - 2) * 60, (self.h - 2) * 60, ImageCache['MovSkyMM'])
        painter.drawTiledPixmap((self.w - 1) * 60, 60, 60, (self.h - 2) * 60, ImageCache['MovSkyMR'], 0, (0 if (self.h & 1) == 0 else 60))

        # Draw bottom row
        painter.drawPixmap(0, (self.h - 1) * 60, ImageCache['MovSkyBL'])
        painter.drawTiledPixmap(60, (self.h - 1) * 60, (self.w - 2) * 60, 60, ImageCache['MovSkyBM'])
        painter.drawPixmap((self.w - 1) * 60, (self.h - 1) * 60, ImageCache['MovSkyBR'])


class SpriteImage_Magmaw(SLib.SpriteImage_Static):  # 565
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Magmaw'],
            (-28, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Magmaw', 'magmaw.png')


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


class SpriteImage_PeachWaiting(SLib.SpriteImage_Static):  # 571
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PeachWaiting'],
            (-12, -48),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PeachWaiting', 'peach_waiting.png')


class SpriteImage_GoldenPipeUp(SLib.SpriteImage_Static):  # 574
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GoldenPipeUp'],
            (0, -64),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GoldenPipeUp', 'golden_pipe_up.png')



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


class SpriteImage_MetalBox(SLib.SpriteImage_StaticMultiple):  # 584, 688, 697
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MetalBox0', 'metal_box_0.png')
        SLib.loadIfNotInImageCache('MetalBox1', 'metal_box_1.png')
        SLib.loadIfNotInImageCache('MetalBox2', 'metal_box_2.png')
        SLib.loadIfNotInImageCache('MetalBox3', 'metal_box_3.png')

    def dataChanged(self):
        boxType = (self.parent.spritedata[5] >> 4) & 3
        self.image = ImageCache['MetalBox%d' % boxType]
        super().dataChanged()


class SpriteImage_JumpingMechaCheep(SLib.SpriteImage_StaticMultiple):  # 587
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.yOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('JumpingMechaCheep0', 'jumping_mecha_cheep_0.png')
        SLib.loadIfNotInImageCache('JumpingMechaCheep1', 'jumping_mecha_cheep_1.png')

    def dataChanged(self):
        direction = (self.parent.spritedata[2] >> 4) & 1
        self.image = ImageCache['JumpingMechaCheep%d' % direction]

        self.xOffset = -4 if direction == 0 else -8
        super().dataChanged()


class SpriteImage_DeepCheep(SLib.SpriteImage_Static):  # 588
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['DeepCheep'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('DeepCheep', 'cheep_deep.png')


class SpriteImage_MediumDeepCheep(SLib.SpriteImage_Static):  # 589
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MediumDeepCheep'],
            (-8, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MediumDeepCheep', 'medium_deep_cheep.png')


class SpriteImage_EepCheep(SLib.SpriteImage_Static):  # 590
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['EepCheep'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('EepCheep', 'cheep_eep.png')


class SpriteImage_MediumEepCheep(SLib.SpriteImage_Static):  # 591
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MediumEepCheep'],
            (-8, -8),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MediumEepCheep', 'medium_eep_cheep.png')


class SpriteImage_SumoBro(SLib.SpriteImage_Static):  # 593, 626, 661
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
            (-4, -4)
        )

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


class SpriteImage_SwingingChain(SLib.SpriteImage_Static):  # 602
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SwingingChain'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SwingingChain', 'swinging_chain.png')


class SpriteImage_BigBuzzyBeetle(SLib.SpriteImage_Static):  # 606
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigBuzzyBeetle'],
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigBuzzyBeetle', 'big_buzzy_beetle.png')


class SpriteImage_IggyRoom(SLib.SpriteImage):  # 609
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].image = ImageCache['IggyRoom']
        self.aux[0].alpha = 0.5
        self.aux[0].setSize(self.aux[0].image.width(), self.aux[0].image.height(), -self.aux[0].image.width() * 0.5, 540 - self.aux[0].image.height())
        self.aux[0].setZValue(-50000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('IggyRoom', 'iggy_room.png')


class SpriteImage_PacornBlock(SLib.SpriteImage):  # 612
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PAcorn0', 'pacorn_bottom.png')
        SLib.loadIfNotInImageCache('PAcorn1', 'pacorn_top.png')
        SLib.loadIfNotInImageCache('PAcorn2', 'pacorn_right.png')
        SLib.loadIfNotInImageCache('PAcorn3', 'pacorn_left.png')

    def dataChanged(self):
        self.direction = self.parent.spritedata[5] & 3
        length = self.parent.spritedata[5] & 0xF0

        if self.direction == 2 or self.direction == 3:
            self.height = length + 16
            self.width = 20
        else:
            self.height = 20
            self.width = length + 16

        if self.direction == 1:
            self.xOffset = 0
            self.yOffset = -16
        elif self.direction == 2:
            self.xOffset = -4
            self.yOffset = 0
        elif self.direction == 3:
            self.xOffset = -16
            self.yOffset = 0
        else:
            self.xOffset = 0
            self.yOffset = -4
        
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        painter.drawTiledPixmap(0, 0, self.width * 3.75, self.height * 3.75, ImageCache['PAcorn%d' % self.direction])


class SpriteImage_GoldenPipeLeft(SLib.SpriteImage_Static):  # 613
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GoldenPipeLeft'],
            (-64, 0),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GoldenPipeLeft', 'golden_pipe_left.png')


class SpriteImage_GoldenPipeRight(SLib.SpriteImage_Static):  # 614
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GoldenPipeRight'],
            (-64, 0),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GoldenPipeRight', 'golden_pipe_right.png')


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


class SpriteImage_WoodBlock(SLib.SpriteImage_Static):  # 619
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    def paint(self, painter):
        super().paint(painter)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.drawPixmap(self.yOffset, self.xOffset, 60, 60, SLib.Tiles[51].main)


class SpriteImage_SeesawMushroomBlue(SLib.SpriteImage):  # 632
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False
        self.yOffset = -8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SeesawMushroomBlueL', 'seesaw_mushroom_blue_left.png')
        SLib.loadIfNotInImageCache('SeesawMushroomBlueM', 'seesaw_mushroom_blue_middle.png')
        SLib.loadIfNotInImageCache('SeesawMushroomBlueR', 'seesaw_mushroom_blue_right.png')
        SLib.loadIfNotInImageCache('SeesawMushroomBlueStem', 'seesaw_mushroom_blue_stem.png')
        SLib.loadIfNotInImageCache('SeesawMushroomBlueStemTop', 'seesaw_mushroom_blue_stem_top.png')
        SLib.loadIfNotInImageCache('SeesawMushroomBluePivot', 'seesaw_mushroom_blue_pivot.png')

    def dataChanged(self):
        self.stemLength = (self.parent.spritedata[9] & 0xF) * 2
        self.mushroomWidth = (self.parent.spritedata[8] & 0xF) * 2 - 2

        if self.mushroomWidth < 0:
            self.mushroomWidth = 14
        
        self.height = 48 + 16 * self.stemLength
        self.width = 32 + 16 * self.mushroomWidth
        self.xOffset = 16 * 7 - (self.mushroomWidth / 2) * 16
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(0, 0, ImageCache['SeesawMushroomBlueL'])
        painter.drawTiledPixmap(60, 0, self.mushroomWidth * 60, 60, ImageCache['SeesawMushroomBlueM'])
        painter.drawPixmap(60 + self.mushroomWidth * 60, 0, ImageCache['SeesawMushroomBlueR'])
        painter.drawPixmap(30 + self.mushroomWidth * 30, 0, ImageCache['SeesawMushroomBluePivot'])
        painter.drawPixmap(30 + self.mushroomWidth * 30, 60, ImageCache['SeesawMushroomBlueStemTop'])
        painter.drawTiledPixmap(30 + self.mushroomWidth * 30, 180, 60, self.stemLength * 60, ImageCache['SeesawMushroomBlueStem'])


class SpriteImage_SuperGuideNSLU(SLib.SpriteImage_Static):  # 634
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SuperGuideNSLU'],
            (-4, -4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SuperGuideNSLU', 'guide_block_nslu.png')


class SpriteImage_BanzaiBillCannonLuigi(SLib.SpriteImage_Static):  # 646, 648
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BanzaiBillCannonLuigi'],
            (-32, -68),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BanzaiBillCannonLuigi', 'banzai_bill_cannon_luigi.png')



class SpriteImage_BanzaiBillCannonLuigiU(SLib.SpriteImage_Static):  # 647, 649
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BanzaiBillCannonLuigiU'],
            (-32, 16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BanzaiBillCannonLuigiU', 'banzai_bill_cannon_luigi_u.png')


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


class SpriteImage_GearLuigi(SLib.SpriteImage_StaticMultiple):  # 675
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.parent.setZValue(-50000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GearStoneLuigiS', 'gear_stone_luigi_small.png')
        SLib.loadIfNotInImageCache('GearStoneLuigiM', 'gear_stone_luigi_medium.png')
        SLib.loadIfNotInImageCache('GearStoneLuigiL', 'gear_stone_luigi_large.png')
        SLib.loadIfNotInImageCache('GearMetalLuigiS', 'gear_metal_small.png')
        SLib.loadIfNotInImageCache('GearMetalLuigiM', 'gear_metal_medium.png')
        SLib.loadIfNotInImageCache('GearMetalLuigiL', 'gear_metal_large.png')

    def dataChanged(self):
        size = self.parent.spritedata[4] & 0xF
        metal = (self.parent.spritedata[5] & 1) != 0
        sizeStr = 'Metal' if metal else 'Stone'

        if size == 1:
            self.image = ImageCache['Gear%sLuigiL' % sizeStr]
            self.xOffset = -140
            self.yOffset = -140
        elif size == 2:
            self.image = ImageCache['Gear%sLuigiS' % sizeStr]
            self.xOffset = -96
            self.yOffset = -96
        else:
            self.image = ImageCache['Gear%sLuigiM' % sizeStr]
            self.xOffset = -92
            self.yOffset = -96

        super().dataChanged()


class SpriteImage_ThankYouSign(SLib.SpriteImage):  # 691
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].image = ImageCache['ThankYouSign']
        self.aux[0].alpha = 0.5
        self.aux[0].setSize(self.aux[0].image.width(), self.aux[0].image.height(), -495, -810)
        self.aux[0].setZValue(-50000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ThankYouSign', 'thank_you_sign.png')


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
    24: SpriteImage_SpinyU,
    25: SpriteImage_MidwayFlag,
    26: SpriteImage_ZoomArea,
    29: SpriteImage_LimitU,
    30: SpriteImage_LimitD,
    31: SpriteImage_Flagpole,
    32: SpriteImage_ArrowSignboard,
    33: SpriteImage_Grrrol,
    34: SpriteImage_BigGrrrol,
    35: SpriteImage_Seaweed,
    36: SpriteImage_ZoneTrigger,
    37: SpriteImage_EventControllerAnd,
    38: SpriteImage_EventControllerOr,
    39: SpriteImage_EventControllerRandom,
    40: SpriteImage_EventControllerChainer,
    41: SpriteImage_LocationTrigger,
    42: SpriteImage_EventControllerMultiChainer,
    43: SpriteImage_EventControllerTimer,
    44: SpriteImage_RedRing,
    45: SpriteImage_StarCoin,
    46: SpriteImage_LineControlledStarCoin,
    47: SpriteImage_BoltControlledStarCoin,
    48: SpriteImage_MvmtRotControlledStarCoin,
    49: SpriteImage_RedCoin,
    50: SpriteImage_GreenCoin,
    51: SpriteImage_MontyMole,
    52: SpriteImage_GrrrolPassage,
    53: SpriteImage_Porcupuffer,
    54: SpriteImage_YoshiBerry,
    55: SpriteImage_KoopaTroopa,
    57: SpriteImage_FishBone,
    59: SpriteImage_QBlock,
    60: SpriteImage_BrickBlock,
    61: SpriteImage_InvisiBlock,
    62: SpriteImage_PipePiranhaUp,
    63: SpriteImage_StalkingPiranha,
    64: SpriteImage_WaterPlant,
    65: SpriteImage_Coin,
    66: SpriteImage_Coin,
    67: SpriteImage_Swooper,
    68: SpriteImage_ControllerSwaying,
    69: SpriteImage_ControllerSpinning,
    70: SpriteImage_TwoWay,
    71: SpriteImage_MovingIronBlock,
    72: SpriteImage_MovingLandBlock,
    73: SpriteImage_CoinSpawner,
    74: SpriteImage_HuckitCrab,
    75: SpriteImage_BroIce,
    76: SpriteImage_BroHammer,
    77: SpriteImage_BroSledge,
    78: SpriteImage_BroBoomerang,
    79: SpriteImage_BroFire,
    80: SpriteImage_MovingIronBlock,
    81: SpriteImage_MovingLandBlock,
    82: SpriteImage_PipePiranhaDown,
    83: SpriteImage_PipePiranhaLeft,
    84: SpriteImage_PipePiranhaRight,
    85: SpriteImage_FlameChomp,
    86: SpriteImage_Urchin,
    87: SpriteImage_MovingCoin,
    88: SpriteImage_Water,
    89: SpriteImage_Lava,
    90: SpriteImage_Poison,
    91: SpriteImage_Quicksand,
    92: SpriteImage_Fog,
    94: SpriteImage_BouncyCloud,
    95: SpriteImage_BouncyCloudL,
    96: SpriteImage_Lamp,
    97: SpriteImage_BackCenter,
    98: SpriteImage_PipeEnemyGenerator,
    99: SpriteImage_MegaUrchin,
    101: SpriteImage_CheepCheep,
    102: SpriteImage_Useless,
    103: SpriteImage_RotatingBillCanon,
    104: SpriteImage_QuestionSwitch,
    105: SpriteImage_PSwitch,
    107: SpriteImage_PeachCastleDoor,
    108: SpriteImage_GhostHouseDoor,
    109: SpriteImage_TowerBossDoor,
    110: SpriteImage_CastleBossDoor,
    111: SpriteImage_BowserBossDoor,
    112: SpriteImage_RotatingBillCanon,
    113: SpriteImage_MediumCheepCheep,
    114: SpriteImage_CheepCheep,
    115: SpriteImage_SpecialExit,
    116: SpriteImage_ControllerSwaying,
    117: SpriteImage_Spinner,
    118: SpriteImage_ControllerSpinning,
    119: SpriteImage_Lakitu,
    120: SpriteImage_SpinyCheep,
    123: SpriteImage_SandPillar,
    124: SpriteImage_SandPillar,
    125: SpriteImage_BulletBill,
    126: SpriteImage_BanzaiBill,
    127: SpriteImage_HomingBulletBill,
    128: SpriteImage_HomingBanzaiBill,
    129: SpriteImage_JumpingCheepCheep,
    132: SpriteImage_ShiftingRectangle,
    133: SpriteImage_SpineCoaster,
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
    149: SpriteImage_Coin,
    150: SpriteImage_StoneEye,
    152: SpriteImage_POWBlock,
    153: SpriteImage_Spotlight,
    154: SpriteImage_FlyingQBlock,
    155: SpriteImage_PipeCannon,
    156: SpriteImage_WaterGeyser,
    157: SpriteImage_BarCenter,
    158: SpriteImage_CoinOutline,
    159: SpriteImage_ExpandingPipeRight,
    160: SpriteImage_ExpandingPipeLeft,
    161: SpriteImage_ExpandingPipeUp,
    162: SpriteImage_ExpandingPipeDown,
    163: SpriteImage_WaterGeyserLocation,
    164: SpriteImage_BobOmb,
    165: SpriteImage_CoinCircle,
    166: SpriteImage_CoinOutlineCircle,
    167: SpriteImage_CoinBlue,
    168: SpriteImage_ClapCoin,
    169: SpriteImage_ClapCoin,
    170: SpriteImage_Parabomb,
    171: SpriteImage_BulletBillCannon,
    172: SpriteImage_RisingLoweringBulletBillCannon,
    173: SpriteImage_BanzaiBillCannon,
    174: SpriteImage_BanzaiBillCannonU,
    175: SpriteImage_Mechakoopa,
    176: SpriteImage_AirshipCannon,
    177: SpriteImage_Crash,
    178: SpriteImage_Crash,
    179: SpriteImage_Cannonball,
    180: SpriteImage_Spike,
    181: SpriteImage_Spike,
    182: SpriteImage_MovingPlatform,
    183: SpriteImage_FallingIcicle,
    184: SpriteImage_GiantIcicle,
    185: SpriteImage_FallingIcicle,
    186: SpriteImage_MovingPlatform,
    187: SpriteImage_ScaredyRat,
    190: SpriteImage_QBlock,
    191: SpriteImage_BrickBlock,
    192: SpriteImage_MovingPlatformSpawner,
    193: SpriteImage_MovingLinePlatform,
    194: SpriteImage_FireSnake,
    195: SpriteImage_RouletteBlock,
    198: SpriteImage_SnowEffect,
    200: SpriteImage_MushroomPlatform,
    201: SpriteImage_LavaParticles,
    203: SpriteImage_IceBlock,
    204: SpriteImage_Fuzzy,
    205: SpriteImage_QBlock,
    206: SpriteImage_BoomBoom,
    207: SpriteImage_LavaGeyser,
    208: SpriteImage_Block_QuestionSwitch,
    209: SpriteImage_Block_PSwitch,
    210: SpriteImage_MushroomMovingPlatform,
    211: SpriteImage_GreyTestPlatform,
    212: SpriteImage_ControllerAutoscroll,
    213: SpriteImage_SwingingVine,
    214: SpriteImage_ControllerSpinOne,
    215: SpriteImage_Springboard,
    217: SpriteImage_WiiTowerBlock,
    218: SpriteImage_Boo,
    219: SpriteImage_BigBoo,
    220: SpriteImage_Boo,
    221: SpriteImage_BooCircle,
    222: SpriteImage_SnakeBlock,
    223: SpriteImage_BoomBoom,
    224: SpriteImage_BalloonYoshi,
    225: SpriteImage_BoomBoom,
    226: SpriteImage_IceFloe,
    227: SpriteImage_IceFloe,
    228: SpriteImage_Scaffold,
    229: SpriteImage_Foo,
    230: SpriteImage_Larry,
    231: SpriteImage_IceFloe,
    232: SpriteImage_LightBlock,
    233: SpriteImage_QBlock,
    234: SpriteImage_BrickBlock,
    235: SpriteImage_SpinningFirebar,
    236: SpriteImage_BigFirebar,
    237: SpriteImage_TileGod,
    238: SpriteImage_Bolt,
    239: SpriteImage_BoltIronPlatform,
    240: SpriteImage_BigFloatingLog,
    241: SpriteImage_BoltMushroom,
    242: SpriteImage_BoltMushroomNoBolt,
    243: SpriteImage_BubbleYoshi,
    244: SpriteImage_Useless,
    246: SpriteImage_BoomBoom,
    247: SpriteImage_PricklyGoomba,
    248: SpriteImage_GhostHouseBoxFrame,
    249: SpriteImage_Wiggler,
    250: SpriteImage_GreyBlock,
    251: SpriteImage_GiantBubble,
    252: SpriteImage_RopeLadder,
    253: SpriteImage_LightCircle,
    254: SpriteImage_UnderwaterLamp,
    255: SpriteImage_MicroGoomba,
    256: SpriteImage_Crash,
    257: SpriteImage_StretchingMushroomPlatform,
    258: SpriteImage_StretchingMushroomPlatform,
    259: SpriteImage_Muncher,
    260: SpriteImage_BigCannon,
    261: SpriteImage_Parabeetle,
    262: SpriteImage_HeavyParabeetle,
    263: SpriteImage_PipeBubbles,
    264: SpriteImage_WaterGeyserBoss,
    265: SpriteImage_RollingHill,
    266: SpriteImage_MovingGhostHouseBlock,
    268: SpriteImage_CustomizableIceBlock,
    269: SpriteImage_Gear,
    270: SpriteImage_Amp,
    271: SpriteImage_MetalBridgePlatform,
    272: SpriteImage_MetalBridgeStem,
    273: SpriteImage_MetalBridgeBase,
    275: SpriteImage_CastlePlatform,
    276: SpriteImage_Jellybeam,
    278: SpriteImage_SeesawMushroom,
    279: SpriteImage_Coin,
    280: SpriteImage_BoltPlatform,
    281: SpriteImage_CoinBubble,
    282: SpriteImage_KingBill,
    284: SpriteImage_StretchBlock,
    285: SpriteImage_VerticalStretchBlock,
    286: SpriteImage_LavaBubble,
    287: SpriteImage_WheelPlatform,
    288: SpriteImage_Bush,
    289: SpriteImage_ContinuousBurner,
    290: SpriteImage_ContinuousBurnerLong,
    294: SpriteImage_PurplePole,
    295: SpriteImage_NoteBlock,
    298: SpriteImage_Clampy,
    296: SpriteImage_Lemmy,
    299: SpriteImage_GirderRisingController,
    300: SpriteImage_GirderRising,
    301: SpriteImage_GiantWiggler,
    302: SpriteImage_BoomBoom,
    303: SpriteImage_Thwimp,
    304: SpriteImage_WobbleRock,
    305: SpriteImage_Poltergeist,
    306: SpriteImage_Crash,
    307: SpriteImage_MovingFence,
    308: SpriteImage_ScalePlatform,
    309: SpriteImage_ScalePlatform,
    310: SpriteImage_Crash,
    311: SpriteImage_WiiTowerBlock,
    312: SpriteImage_Crash,
    313: SpriteImage_Blooper,
    314: SpriteImage_Crash,
    316: SpriteImage_Crystal,
    317: SpriteImage_BoomBoom,
    318: SpriteImage_LavaBubble,
    319: SpriteImage_Crash,
    320: SpriteImage_Broozer,
    321: SpriteImage_Bulber,
    322: SpriteImage_BlooperBabies,
    323: SpriteImage_Barrel,
    324: SpriteImage_GhostHouseBlock,
    325: SpriteImage_Coin,
    326: SpriteImage_MovingCoin,
    327: SpriteImage_SledgeBlock,
    328: SpriteImage_Coin,
    329: SpriteImage_SpikePillarDown,
    330: SpriteImage_EnemyRaft,
    331: SpriteImage_SpikePillarUp,
    332: SpriteImage_SpikePillarRight,
    333: SpriteImage_SpikePillarLeft,
    334: SpriteImage_Cooligan,
    335: SpriteImage_PipeCooliganGenerator,
    336: SpriteImage_Bramball,
    337: SpriteImage_CheepChomp,
    338: SpriteImage_WoodenBox,
    341: SpriteImage_AirshipNutPlatform,
    342: SpriteImage_SpikePillarLongRight,
    343: SpriteImage_SpikePillarLongLeft,
    345: SpriteImage_Crash,
    346: SpriteImage_Thwimp,
    347: SpriteImage_StoneBlock,
    348: SpriteImage_SuperGuide,
    349: SpriteImage_GirderLine,
    350: SpriteImage_MovingStoneBlock,
    351: SpriteImage_Pokey,
    352: SpriteImage_SpikeTop,
    353: SpriteImage_ParachuteCoin,
    354: SpriteImage_RotatableIronPlatform,
    355: SpriteImage_RollingHillPipe,
    356: SpriteImage_RotatableIronPlatform,
    357: SpriteImage_Fuzzy,
    358: SpriteImage_Crash,
    360: SpriteImage_Crash,
    362: SpriteImage_MovingFirePiranha,
    363: SpriteImage_Chest,
    365: SpriteImage_GoldenYoshi,
    367: SpriteImage_MoveWhenOnPlatform,
    368: SpriteImage_Morton,
    371: SpriteImage_GreyBlock2,
    372: SpriteImage_MovingOneWayPlatform,
    373: SpriteImage_GreyBlock2,
    374: SpriteImage_ChainHolder,
    376: SpriteImage_Crash,
    377: SpriteImage_Crash,
    378: SpriteImage_TorpedoLauncher,
    379: SpriteImage_TorpedoTed,
    380: SpriteImage_QBlockBYoshi,
    382: SpriteImage_Dragoneel,
    383: SpriteImage_Wendy,
    385: SpriteImage_Ludwig,
    386: SpriteImage_MeltableIceChunk,
    389: SpriteImage_Roy,
    390: SpriteImage_JungleBridge,
    391: SpriteImage_GrayCrystal,
    393: SpriteImage_3x3IceBlock,
    395: SpriteImage_Starman,
    396: SpriteImage_BeanstalkLeaf,
    397: SpriteImage_QBlock,
    398: SpriteImage_BrickBlock,
    400: SpriteImage_LanternPlatform,
    402: SpriteImage_GreenRing,
    403: SpriteImage_Iggy,
    404: SpriteImage_PipeUpEnterable,
    405: SpriteImage_Crash,
    407: SpriteImage_BumpPlatform,
    408: SpriteImage_Toad,
    409: SpriteImage_ChainChomp,
    410: SpriteImage_CastlePlatformLudwig,
    422: SpriteImage_BigBrickBlock,
    424: SpriteImage_ToAirshipCannon,
    425: SpriteImage_BeanstalkTendril,
    426: SpriteImage_Ballon,
    427: SpriteImage_SnowyBoxes,
    428: SpriteImage_CastleRailLudwig,
    429: SpriteImage_MetalBar,
    430: SpriteImage_MovingIronBlock,
    431: SpriteImage_MortonStoneBlock,
    434: SpriteImage_RotatingIronBlock,
    436: SpriteImage_Crash,
    439: SpriteImage_Crash,
    441: SpriteImage_Fliprus,
    442: SpriteImage_Dragoneel,
    443: SpriteImage_BonyBeetle,
    446: SpriteImage_FliprusSnowball,
    447: SpriteImage_SpikeTop,
    449: SpriteImage_Useless,
    451: SpriteImage_NabbitPlacement,
    452: SpriteImage_Crash,
    455: SpriteImage_ClapCrowd,
    456: SpriteImage_Useless,
    457: SpriteImage_WobbyBonePlatform,
    458: SpriteImage_GoldenPipeDown,
    462: SpriteImage_Bowser,
    464: SpriteImage_BowserBridge,
    465: SpriteImage_KamekFloor,
    467: SpriteImage_BowserShutter,
    469: SpriteImage_Peach,
    471: SpriteImage_MediumGoomba,
    472: SpriteImage_BigGoomba,
    473: SpriteImage_MegaBowser,
    474: SpriteImage_ToadHouseCannon,
    475: SpriteImage_BigQBlock,
    476: SpriteImage_BigKoopaTroopa,
    478: SpriteImage_BowserJrBlock,
    479: SpriteImage_Crash,
    480: SpriteImage_MvmtRotControlledStarCoin,
    481: SpriteImage_WaddleWing,
    482: SpriteImage_MechaCheep,
    483: SpriteImage_SpinningFirebar,
    484: SpriteImage_ControllerSpinning,
    485: SpriteImage_MetalBarGearbox,
    486: SpriteImage_FrameSetting,
    488: SpriteImage_Dragoneel,
    491: SpriteImage_MovingBonePlatform,
    492: SpriteImage_MovingBonePlatform,
    493: SpriteImage_World7Platform,
    496: SpriteImage_Coin,
    499: SpriteImage_MovingGrassPlatform,
    500: SpriteImage_BowserAmp,
    503: SpriteImage_PaintGoal,
    504: SpriteImage_Grrrol,
    505: SpriteImage_BigGrrrol,
    506: SpriteImage_ChallengeOnlyBlock,
    507: SpriteImage_ShootingStar,
    508: SpriteImage_CloudPlatform,
    509: SpriteImage_PipeRight,
    510: SpriteImage_PipeLeft,
    511: SpriteImage_PipeDown,
    512: SpriteImage_GhostShipBlock,
    513: SpriteImage_PipeJoint,
    514: SpriteImage_PipeJointSmall,
    515: SpriteImage_MovingCastleGround,
    516: SpriteImage_MiniPipeRight,
    517: SpriteImage_MiniPipeLeft,
    518: SpriteImage_MiniPipeUp,
    519: SpriteImage_MiniPipeDown,
    520: SpriteImage_BowserSwitch,
    521: SpriteImage_Crash,
    522: SpriteImage_Crash,
    523: SpriteImage_FlyingQBlockAmbush,
    524: SpriteImage_MovementControlledTowerBlock,
    525: SpriteImage_QBlock,
    526: SpriteImage_BrickBlock,
    529: SpriteImage_Crash,
    530: SpriteImage_BoltStoneBlock,
    533: SpriteImage_WendyIcicle,
    534: SpriteImage_MovingGroupedPlatform,
    535: SpriteImage_MovingGroupedPlatform,
    536: SpriteImage_RockyWrench,
    537: SpriteImage_Wrench,
    538: SpriteImage_Crash,
    542: SpriteImage_MushroomPlatform,
    544: SpriteImage_MushroomMovingPlatform,
    546: SpriteImage_Flowers,
    548: SpriteImage_Sprite548,
    549: SpriteImage_DesertBlock,
    550: SpriteImage_GiantPipePiranha,
    551: SpriteImage_Useless,
    552: SpriteImage_Muncher,
    553: SpriteImage_SteerablePlatform,
    555: SpriteImage_Crash,
    556: SpriteImage_Crash,
    559: SpriteImage_NabbitRefugeLocation,
    560: SpriteImage_WendyFloor,
    561: SpriteImage_RecordSignboard,
    562: SpriteImage_MovingSkyBlock,
    563: SpriteImage_MovingSkyBlock,
    565: SpriteImage_Magmaw,
    566: SpriteImage_NabbitMetal,
    569: SpriteImage_NabbitPrize,
    571: SpriteImage_PeachWaiting,
    572: SpriteImage_Crash,
    573: SpriteImage_MovingLinePlatform,
    574: SpriteImage_GoldenPipeUp,
    575: SpriteImage_PipeLeft,
    576: SpriteImage_PipeRight,
    577: SpriteImage_PipeUp,
    578: SpriteImage_PipeDown,
    579: SpriteImage_StoneSpike,
    580: SpriteImage_StoneSpike,
    581: SpriteImage_BulletBillCannon,
    582: SpriteImage_BanzaiBillCannon,
    583: SpriteImage_BanzaiBillCannonU,
    584: SpriteImage_MetalBox,
    587: SpriteImage_JumpingMechaCheep,
    588: SpriteImage_DeepCheep,
    589: SpriteImage_MediumDeepCheep,
    590: SpriteImage_EepCheep,
    591: SpriteImage_MediumEepCheep,
    593: SpriteImage_SumoBro,
    595: SpriteImage_Goombrat,
    600: SpriteImage_MoonBlock,
    602: SpriteImage_SwingingChain,
    606: SpriteImage_BigBuzzyBeetle,
    607: SpriteImage_LineControlledStarCoin,
    609: SpriteImage_IggyRoom,
    612: SpriteImage_PacornBlock,
    613: SpriteImage_GoldenPipeLeft,
    614: SpriteImage_GoldenPipeRight,
    615: SpriteImage_CheepCheep,
    618: SpriteImage_SteelBlock,
    619: SpriteImage_WoodBlock,
    625: SpriteImage_BoltStoneBlock,
    626: SpriteImage_SumoBro,
    627: SpriteImage_MovingBonePlatform,
    630: SpriteImage_Flagpole,
    631: SpriteImage_PaintGoal,
    632: SpriteImage_SeesawMushroomBlue,
    633: SpriteImage_GirderRising,
    634: SpriteImage_SuperGuideNSLU,
    635: SpriteImage_CastleBossDoor,
    636: SpriteImage_TowerBossDoor,
    637: SpriteImage_BowserBossDoor,
    638: SpriteImage_Dragoneel,
    640: SpriteImage_FlameChomp,
    642: SpriteImage_TwoWay,
    643: SpriteImage_LavaBubble,
    644: SpriteImage_LavaBubble,
    645: SpriteImage_JungleBridge,
    646: SpriteImage_BanzaiBillCannonLuigi,
    647: SpriteImage_BanzaiBillCannonLuigiU,
    648: SpriteImage_BanzaiBillCannonLuigi,
    649: SpriteImage_BanzaiBillCannonLuigiU,
    651: SpriteImage_Spike,
    652: SpriteImage_Parabeetle,
    653: SpriteImage_KingBill,
    655: SpriteImage_SnakeBlock,
    658: SpriteImage_MovingLinePlatform,
    659: SpriteImage_BigGrrrol,
    661: SpriteImage_SumoBro,
    662: SpriteImage_BlueRing,
    663: SpriteImage_Coin,
    667: SpriteImage_PipeCannon,
    669: SpriteImage_MovementControlledTowerBlock,
    671: SpriteImage_GrrrolPassage,
    673: SpriteImage_TileGod,
    675: SpriteImage_GearLuigi,
    676: SpriteImage_CastlePlatform,
    678: SpriteImage_InvisiBlock,
    679: SpriteImage_MovPipe,
    681: SpriteImage_ArrowSignboard,
    682: SpriteImage_WaterPlant,
    683: SpriteImage_QBlock,
    686: SpriteImage_PSwitch,
    687: SpriteImage_Parabomb,
    688: SpriteImage_MetalBox,
    691: SpriteImage_ThankYouSign,
    692: SpriteImage_BrickBlock,
    693: SpriteImage_Spinner,
    695: SpriteImage_Urchin,
    696: SpriteImage_MovingGhostHouseBlock,
    697: SpriteImage_MetalBox,
    698: SpriteImage_GroundPiranha,
    699: SpriteImage_SpineCoaster,
    700: SpriteImage_SpineCoaster,
    701: SpriteImage_BrickBlock,
    702: SpriteImage_Wiggler,
    703: SpriteImage_BooCircle,
    704: SpriteImage_BrickBlock,
    705: SpriteImage_WaterGeyserLocation,
    706: SpriteImage_BrickBlock,
    707: SpriteImage_QBlock,
    709: SpriteImage_RotatingIronBlock,
    710: SpriteImage_PSwitch,
    711: SpriteImage_RotatingIronBlock,
    712: SpriteImage_GroundPiranha,
    713: SpriteImage_Urchin,
    714: SpriteImage_Scaffold,
    716: SpriteImage_Foo,
    717: SpriteImage_SnakeBlock,
    719: SpriteImage_StoneEye,
    722: SpriteImage_ArrowSignboard,
}
