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

# sprites.py
# Contains code to render NSMBU sprite images
# not even close to done...


#IMPORTANT!!!! An offset value of 16 is one block!


################################################################
################################################################

# Imports

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
Qt = QtCore.Qt

from miyamoto import *

import spritelib as SLib
ImageCache = SLib.ImageCache

#Global varible for rotations.
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

class SpriteImage_Block(SLib.SpriteImage_Static):
    def __init__(self, parent, scale=1.5):
        super().__init__(parent, scale)
        self.spritebox.shown = False
        self.contentsOverride = None

        self.tilenum = 1315
        self.tileheight = 1
        self.tilewidth = 1
        self.yOffset = 0
        self.xOffset = 0
        self.invisiblock = False

    def dataChanged(self):
        super().dataChanged()

        if self.contentsOverride is not None:
            self.image = ImageCache['Items'][self.contentsOverride]
        else:
            self.contents = self.parent.spritedata[9] & 0xF
            self.acorn = (self.parent.spritedata[6] >> 4) & 1

            if self.acorn:
                self.image = ImageCache['Items'][15]
            elif self.contents != 0:
                self.image = ImageCache['Items'][self.contents-1]
            else:
                self.image = None

    def paint(self, painter):
        super().paint(painter)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if self.tilenum < len(SLib.Tiles):
            if self.invisiblock:
                painter.drawPixmap(0, 0, ImageCache['InvisiBlock'])
            else:
                painter.drawPixmap(self.yOffset, self.xOffset, self.tilewidth*60, self.tileheight*60, SLib.Tiles[self.tilenum].main)
        if self.image is not None:
            painter.drawPixmap(0, 0, self.image)

class SpriteImage_WaterRender(SLib.SpriteImage_Static):

    def __init__(self, parent, scale=3.75, image='None'):
        super().__init__(parent, scale, image)



    """
        top = QPixmap('miyamotodata/sprites/water_top.png')
        base = QPixmap('miyamotodata/sprites/water.png')

        currY = self.dimensions[1] - 20
        x = Waterlocationx
        y = Waterlocationy
        w = Waterlocationw
        h = Waterlocationh
        tempx = Waterlocationx
        tempxx = Waterlocationx
 
        painter = QPainter()

        for tempx in range(x+w):
            rect = QRect(tempx, currY, min(x + w - tempx, top.width()), min(y + h - currY, top.height()));
            painter.drawPixmap(rect, top, QRect(0, 0, rect.right()-rect.left(), rect.bottom()-rect.top()));
            tempx = tempx+top.width()

        currY += top.height();

        for currY in range(y+h): 
            for tempxx in range(x+w):
                tempxx = tempxx + base.width()
                rect = QRect(tempxx, currY, min(x + w - tempxx, base.width()), min(y + h - currY, base.height()));
                painter.drawPixmap(rect, base, QRect(0, 0, rect.right()-rect.left(), rect.bottom()-rect.top()));
            currY = currY + base.height()
    """

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

                #Paint
                ImageCache['PipePaintedTop%s' % colour] = SLib.GetImg('pipe_painted_%s_top.png' % colour.lower())
                ImageCache['PipePaintedMiddleV%s' % colour] = SLib.GetImg('pipe_painted_%s_middleV.png' % colour.lower())
                ImageCache['PipePaintedMiddleH%s' % colour] = SLib.GetImg('pipe_painted_%s_middleH.png' % colour.lower())
                ImageCache['PipePaintedBottom%s' % colour] = SLib.GetImg('pipe_painted_%s_bottom.png' % colour.lower())
                ImageCache['PipePaintedLeft%s' % colour] = SLib.GetImg('pipe_painted_%s_left.png' % colour.lower())
                ImageCache['PipePaintedRight%s' % colour] = SLib.GetImg('pipe_painted_%s_right.png' % colour.lower())

                # BIG
                ImageCache['PipeBigTop%s' % colour] = ImageCache['PipeTop%s' % colour].scaled(240,240,QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigMiddleV%s' % colour] = ImageCache['PipeMiddleV%s' % colour].scaled(240,240)
                ImageCache['PipeBigMiddleH%s' % colour] = ImageCache['PipeMiddleH%s' % colour].scaled(240,240)
                ImageCache['PipeBigBottom%s' % colour] = ImageCache['PipeBottom%s' % colour].scaled(240,240,QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigLeft%s' % colour] = ImageCache['PipeLeft%s' % colour].scaled(240,240,QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigRight%s' % colour] = ImageCache['PipeRight%s' % colour].scaled(240,240,QtCore.Qt.KeepAspectRatio)

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

        #if self.moving: rawlength = (self.parent.spritedata[4] & 0x0F) + 1
        #else:
        rawlength = (self.parent.spritedata[5] & 0x0F) + 1

        if not self.mini:
            rawtop = (self.parent.spritedata[2] >> 4) & 3

        #if self.moving:
            #rawtop = 0 & 3

            #if self.expandable: rawcolour = (self.parent.spritedata[3]) & 3
            #elif self.moving: rawcolour = (self.parent.spritedata[3]) & 3
#            else:
            rawcolour = (self.parent.spritedata[5] >> 4) & 3

            if self.typeinfluence and rawtop == 0:
                #if self.expandable: rawtype = self.parent.spritedata[4] & 3
                #elif self.moving: rawtype = self.parent.spritedata[5] >> 4
                #else: 
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

        if self.direction in 'LR': # horizontal
            self.pipeWidth = pipeLength * 60
            self.width = (self.pipeWidth/3.75)
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

            if self.direction == 'R': # faces right
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
            else: # faces left
                if self.big:
                    self.top = ImageCache['PipeBigLeft%s' % self.colour]
                elif self.painted:
                    self.top = ImageCache['PipePaintedLeft%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeLeft%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeLeft%s' % self.colour]
                self.xOffset = 16 - self.width

        if self.direction in 'UD': # vertical
            self.pipeHeight = pipeLength * 60
            self.height = (self.pipeHeight/3.75)
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

            if self.direction == 'D': # faces down
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
            else: # faces up
                if self.big:
                    self.top = ImageCache['PipeBigTop%s' % self.colour]
                elif self.painted:
                    self.top = ImageCache['PipePaintedTop%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeTop%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeTop%s' % self.colour]
                self.yOffset = 16 - (self.pipeHeight/3.75)

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


class SpriteImage_Useless(SLib.SpriteImage_Static): # X
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Useless'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Useless', 'useless.png')

class SpriteImage_Goomba(SLib.SpriteImage_Static): # 0
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Goomba'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Goomba', 'goomba.png')

class SpriteImage_Paragoomba(SLib.SpriteImage_Static): # 1
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

class SpriteImage_PipePiranhaUp(SLib.SpriteImage_Static): # 2
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaUp'],
            (7, -32),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaUp', 'pipe_piranha.png')

class SpriteImage_PipePiranhaDown(SLib.SpriteImage_Static): # 3
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaDown'],
            (7, 32),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaDown', 'pipe_piranha_down.png')

class SpriteImage_PipePiranhaLeft(SLib.SpriteImage_Static): # 4
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaLeft'],
            (-32, 7),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaLeft', 'pipe_piranha_left.png')
        
class SpriteImage_PipePiranhaRight(SLib.SpriteImage_Static): # 5
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaRight'],
            (18, 5),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaRight', 'pipe_piranha_right.png')

class SpriteImage_PipePiranhaUpFire(SLib.SpriteImage_Static): # 6
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PipePiranhaUpFire'],
            )

        self.xOffset = -6
        self.yOffset = -32

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePiranhaUpFire', 'firetrap_pipe_up.png')
  
# Image needs to be improved
class SpriteImage_KoopaTroopa(SLib.SpriteImage_StaticMultiple): # 19
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['KoopaG'],
            (-8,-8),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('KoopaG', 'koopa_green.png')
        SLib.loadIfNotInImageCache('KoopaR', 'koopa_red.png')

    def dataChanged(self):
        shellcolour = self.parent.spritedata[5] & 1

        if shellcolour == 0:
            self.image = ImageCache['KoopaG']
        else:
            self.image = ImageCache['KoopaR']
            
        super().dataChanged()

# Image needs to be improved
class SpriteImage_KoopaParatroopa(SLib.SpriteImage_StaticMultiple): # 20
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['KoopaGWings'],
            (-8,-8),
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

class SpriteImage_BuzzyBeetle(SLib.SpriteImage_StaticMultiple): # 22
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BuzzyL', 'buzzy_beetle.png')
        SLib.loadIfNotInImageCache('BuzzyR', 'buzzy_beetle_right.png')
        SLib.loadIfNotInImageCache('BuzzyDL', 'buzzy_beetle_down.png')
        SLib.loadIfNotInImageCache('BuzzyDR', 'buzzy_beetle_down_right.png')
        SLib.loadIfNotInImageCache('BuzzyS', 'buzzy_beetle_shell.png')
        SLib.loadIfNotInImageCache('BuzzyDS', 'buzzy_beetle_down_shell.png')

    def dataChanged(self):
        
        loldirection = self.parent.spritedata[4] & 0xF
        mytype = self.parent.spritedata[5] & 0xF

        direction = left

        if loldirection == 1:
            direction = right
        else:
            direction = left

        if mytype == 0:
            if direction == left:
                self.image = ImageCache['BuzzyL']
            else:
                self.image = ImageCache['BuzzyR']

        elif mytype == 1:
            if direction == left:
                self.image = ImageCache['BuzzyDL']
            else:
                self.image = ImageCache['BuzzyDR']

        elif mytype == 2:
            self.image = ImageCache['BuzzyS']

        elif mytype == 3:
            self.image = ImageCache['BuzzyDS']

        else:
            self.image = ImageCache['BuzzyL']

        super().dataChanged()

class SpriteImage_ArrowSignboard(SLib.SpriteImage_StaticMultiple): # 32
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ArrowSign0'],
            (-7,-18),
            )

    @staticmethod
    def loadImages():
        for i in range(0,8):
            for j in ('', 's'):
                SLib.loadIfNotInImageCache('ArrowSign{0}{1}'.format(i, j), 'sign{0}{1}.png'.format(i, j))

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 0xF
        if direction > 7: direction -= 8
        appear_raw = self.parent.spritedata[3] >> 4
        appear = ''
        if appear_raw == 1:
            appear = 's'

        self.image = ImageCache['ArrowSign{0}{1}'.format(direction, appear)]

        super().dataChanged()

class SpriteImage_Spiny(SLib.SpriteImage_StaticMultiple): # 23
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

class SpriteImage_MidwayFlag(SLib.SpriteImage_StaticMultiple): # 25
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MidwayFlag'],
            )
        
        self.yOffset = -44

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MidwayFlag', 'midway_flag.png')

class SpriteImage_LimitU(SLib.SpriteImage_StaticMultiple): # 29
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

class SpriteImage_LimitD(SLib.SpriteImage_StaticMultiple): # 30
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

class SpriteImage_Flagpole(SLib.SpriteImage_StaticMultiple): # 31
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        
        self.xOffset = -32
        self.yOffset = -144

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

        if snowno == 16: nob = True
        else: nob = False
        if snowno == 1: snowb = True
        else: snowb = False
        if secret == 16: secretb = True
        else: secretb = False
        if snowno == 17:
            nob = True
            snowb = True

#print("Snow: "+str(snowb) + "   Secret: "+str(secretb) + "   No: "+str(nob) + "     SecretN:" + str(secret)+ "     SnowNo:"+str(snowno))
#That was a coding challenge

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


class SpriteImage_ZoneTrigger(SLib.SpriteImage_Static): # 36
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ZoneTrigger'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ZoneTrigger', 'zone_trigger.png')

class SpriteImage_LocationTrigger(SLib.SpriteImage_Static): # 41
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['LocationTrigger'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LocationTrigger', 'location_trigger.png')

class SpriteImage_RedRing(SLib.SpriteImage_Static): # 44
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

class SpriteImage_StarCoin(SLib.SpriteImage_Static): # 45
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['StarCoin'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StarCoin', 'star_coin.png')

class SpriteImage_LineControlledStarCoin(SLib.SpriteImage_Static): # 46
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['LineStarCoin'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LineStarCoin', 'star_coin.png')

class SpriteImage_BoltControlledStarCoin(SLib.SpriteImage_Static): # 47
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BoltStarCoin'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoltStarCoin', 'star_coin.png')

class SpriteImage_MvmtRotControlledStarCoin(SLib.SpriteImage_Static): # 48
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

class SpriteImage_RedCoin(SLib.SpriteImage_Static): # 49
    # Red Coin
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['RedCoin'],
            )

        self.xOffset = 2

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RedCoin', 'red_coin.png')

class SpriteImage_GreenCoin(SLib.SpriteImage_Static): # 50
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

class SpriteImage_MontyMole(SLib.SpriteImage_Static): # 51
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

class SpriteImage_YoshiBerry(SLib.SpriteImage_Static): # 54
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['YoshiBerry'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('YoshiBerry', 'yoshi_berry.png')

class SpriteImage_QBlock(SpriteImage_Block): # 59
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        self.tilenum = 49

class SpriteImage_BrickBlock(SpriteImage_Block): # 60
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        self.tilenum = 48

class SpriteImage_InvisiBlock(SpriteImage_Block): # 61
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        self.invisiblock = True

class SpriteImage_StalkingPiranha(SLib.SpriteImage_StaticMultiple): # 63
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['StalkingPiranha'],
            )
        
        self.yOffset = -17
        #self.xOffset = -10

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StalkingPiranha', 'stalking_piranha.png')    

class SpriteImage_WaterPlant(SLib.SpriteImage_Static): # 64
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

class SpriteImage_Coin(SLib.SpriteImage_Static): # 65
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Coin'],
            )
        self.parent.setZValue(20000)

class SpriteImage_Swooper(SLib.SpriteImage_Static): # 67
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Swooper'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Swooper', 'swooper.png')

class SpriteImage_ControllerSwaying(SLib.SpriteImage_Static): # 68
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
        
        rotid = self.parent.spritedata[10]

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
#        func = SpriteImage_StoneEye(SLib.SpriteImage_StaticMultiple)
#        func.translateImage()



class SpriteImage_ControllerSpinning(SLib.SpriteImage_StaticMultiple): # 69
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerSpinning'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerSpinning', 'controller_spinning.png')

class SpriteImage_TwoWay(SLib.SpriteImage_StaticMultiple): # 70
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

class SpriteImage_MovingLandBlock(SLib.SpriteImage): # 72
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        #self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

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

        self.width = (self.parent.spritedata[8] & 0xF)*16
        self.height = (self.parent.spritedata[9] & 0xF)*16
        if self.width/16 == 0: self.width = 1
        if self.height/16 == 0: self.height = 1


    def paint(self, painter):
        super().paint(painter)

        #Time to code this lazily.

        #Top of sprite.
        if self.width/16 == 0:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopM'])
        elif self.width/16 == 1:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopM'])
        elif self.width/16 == 2:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopL'])
            painter.drawPixmap(60, 0, 60, 60, ImageCache['MovLTopR'])
        elif self.width/16 == 3:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopL'
])
            painter.drawPixmap(60, 0, 60, 60, ImageCache['MovLTopM'])
            painter.drawPixmap(120, 0, 60, 60, ImageCache['MovLTopR'])
        else:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopL'
])
            painter.drawTiledPixmap(60, 0, (self.width/16-2)*60, 60, ImageCache['MovLTopM'])
            painter.drawPixmap(60+((self.width/16-2)*60), 0, 60, 60, ImageCache['MovLTopR'])


        #Bottom
        if self.height/16 > 1:
            if self.width/16 == 0:
                painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLBottomM'])
            elif self.width/16 == 1:
                painter.drawPixmap(0, (self.height/16)*60-60, 60, 60, ImageCache['MovLBottomM'])
            elif self.width/16 == 2:
                painter.drawPixmap(0, (self.height/16)*60-60, 60, 60, ImageCache['MovLBottomL'])
                painter.drawPixmap(60, (self.height/16)*60-60, 60, 60, ImageCache['MovLBottomR'])
            elif self.width/16 == 3:
                painter.drawPixmap(0, (self.height/16)*60-60, 60, 60, ImageCache['MovLBottomL'
])
                painter.drawPixmap(60, (self.height/16)*60-60, 60, 60, ImageCache['MovLBottomM'])
                painter.drawPixmap(120, (self.height/16)*60-60, 60, 60, ImageCache['MovLBottomR'])
            else:
                painter.drawPixmap(0, (self.height/16)*60-60, 60, 60, ImageCache['MovLBottomL'
])
                painter.drawTiledPixmap(60, (self.height/16)*60-60, (self.width/16-2)*60, 60, ImageCache['MovLBottomM'])
                painter.drawPixmap(60+((self.width/16-2)*60), (self.height/16)*60-60, 60, 60, ImageCache['MovLBottomR'])

        #Left
        if self.height/16 == 3:
            painter.drawPixmap(0, 60, 60, 60, ImageCache['MovLMiddleL'])
        elif self.height/16 > 3:
            painter.drawPixmap(0, 60, 60, 60, ImageCache['MovLMiddleL'])
            painter.drawTiledPixmap(0, 120, 60, (self.height/16-3)*60, ImageCache['MovLMiddleL'])

        #Right
        if self.height/16 == 3:
            painter.drawPixmap((self.width/16*60)-60, 60, 60, 60, ImageCache['MovLMiddleR'])
        elif self.height/16 > 3:
            painter.drawPixmap((self.width/16*60)-60, 60, 60, 60, ImageCache['MovLMiddleR'])
            painter.drawTiledPixmap((self.width/16*60)-60, 120, 60, (self.height/16-3)*60, ImageCache['MovLMiddleR'])

        #Middle
        if self.width/16 > 2:
            if self.height/16 > 2:
                painter.drawTiledPixmap(60, 60, ((self.width/16)-2)*60, ((self.height/16)-2)*60, ImageCache['MovLMiddleM'])

        #1 Glitch
        if self.width/16 < 2:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopM'])
            painter.drawTiledPixmap(0, 60, 60, ((self.height/16)-2)*60, ImageCache['MovLMiddleM'])
            if self.height > 1:
                painter.drawPixmap(0, (self.height/16)*60-60, 60, 60, ImageCache['MovLBottomM'])
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovLTopM'])


class SpriteImage_CoinSpawner(SLib.SpriteImage_Liquid): # 73
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

class SpriteImage_HuckitCrab(SLib.SpriteImage_StaticMultiple): # 74
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['HuckitCrab'],
            )
        
        self.yOffset = -4.5 # close enough, it can't be a whole number
        self.xOffset = -10

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('HuckitCrab', 'huckit_crab.png')   

class SpriteImage_BroIce(SLib.SpriteImage_Static): # 75
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

class SpriteImage_BroHammer(SLib.SpriteImage_Static): # 76
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

class SpriteImage_BroBoomerang(SLib.SpriteImage_Static): # 78
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

class SpriteImage_BroFire(SLib.SpriteImage_Static): # 79
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

class SpriteImage_MovingCoin(SLib.SpriteImage_Static): # 87
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

"""
# Time to see if I can actually get something to work.
class SpriteImage_Water(SpriteImage_WaterRender): #88
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Water'].scaled(Waterlocationw,Waterlocationh,QtCore.Qt.KeepAspectRatio),
            )
    
#        size = Waterlocationw, Waterlocationh

#       Draw a shitty rect.
        self.width = Waterlocationw
        self.height = Waterlocationh
#        self.yOffset = -300


    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Water', 'water_top.png')
"""

class SpriteImage_Water(SLib.SpriteImage_Liquid): # 88
    def __init__(self, parent):
        super().__init__(parent, 3.75, ImageCache['Water'].scaled(180,180,QtCore.Qt.KeepAspectRatio))
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.parent.setZValue(500000)

    def dataChanged(self):
        super().dataChanged()
        self.aux[0].setSize(Waterlocationw * 60, Waterlocationh * 60)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Water', 'water.png')

class SpriteImage_Lava(SLib.SpriteImage_Liquid): # 89
    def __init__(self, parent):
        super().__init__(parent, 3.75, ImageCache['Lava'].scaled(180,180,QtCore.Qt.KeepAspectRatio))
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.parent.setZValue(500000)

    def dataChanged(self):
        super().dataChanged()
        self.aux[0].setSize(Waterlocationw * 60, Waterlocationh * 60)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Lava', 'lava.png')

class SpriteImage_Poison(SLib.SpriteImage_Liquid): # 90
    def __init__(self, parent):
        super().__init__(parent, 3.75, ImageCache['Soda'].scaled(180,180,QtCore.Qt.KeepAspectRatio))
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.xOffset = Waterlocationx
        self.yOffset = Waterlocationy
        self.parent.setZValue(500000)

    def dataChanged(self):
        super().dataChanged()
        self.aux[0].setSize(Waterlocationw * 60, Waterlocationh * 60)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Soda', 'poison.png')

class SpriteImage_Quicksand(SLib.SpriteImage_Static): # 91
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Quicksand'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Quicksand', 'quicksand.png')

class SpriteImage_Fog(SLib.SpriteImage_Static): # 92
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Fog'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Fog', 'fog.png')

class SpriteImage_BouncyCloud(SLib.SpriteImage_StaticMultiple): # 94
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BouncyCloudS'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BouncyCloudS', 'bouncy_cloud_small.png')
        SLib.loadIfNotInImageCache('BouncyCloudL', 'bouncy_cloud_large.png')

    def dataChanged(self):
        size = self.parent.spritedata[8] & 1

        if size == 1:
            self.xOffset = -2
            self.yOffset = 2
            self.image = ImageCache['BouncyCloudL']
        else:
            self.xOffset = -2
            self.yOffset = -8
            self.image = ImageCache['BouncyCloudS']
            
        super().dataChanged()

class SpriteImage_BackCenter(SLib.SpriteImage_Static): # 97
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BackCenter'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BackCenter', 'back_center.png')

class SpriteImage_CheepCheep(SLib.SpriteImage_Liquid): # 101
    def __init__(self, parent):
        super().__init__(parent, 3.75, ImageCache['CheepCheep'])
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def dataChanged(self):
        super().dataChanged()

        nybbleWidth = self.parent.spritedata[3]
        height = 60

        width = nybbleWidth*60+60

        offsetX = ((-1)*(nybbleWidth*60))

        self.aux[0].setSize(width, height, offsetX, 0)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CheepCheep', 'cheep_cheep.png')

class SpriteImage_QuestionSwitch(SLib.SpriteImage_Static): # 104
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
                  

class SpriteImage_PSwitch(SLib.SpriteImage_Static): # 105
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

class SpriteImage_GhostHouseDoor(SLib.SpriteImage_Static): # 108
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GhostHouseDoor'],
            )

        self.xOffset = 0
        self.yOffset = 6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GhostHouseDoor', 'ghost_house_door.png')

class SpriteImage_TowerBossDoor(SLib.SpriteImage_Static): # 109
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

class SpriteImage_CastleBossDoor(SLib.SpriteImage_Static): # 110
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

class SpriteImage_SandPillar(SLib.SpriteImage_Static): # 123
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SandPillar'],
            )

        self.yOffset = -143 # what
        self.xOffset = -18

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SandPillar', 'sand_pillar.png')

class SpriteImage_Thwomp(SLib.SpriteImage_Static): # 135
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Thwomp'],
            )
        
        self.xOffset = -3
        self.yOffset = 0

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Thwomp', 'thwomp.png')

class SpriteImage_GiantThwomp(SLib.SpriteImage_Static): # 136
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GiantThwomp'],
            )
        
        self.xOffset = -3
        self.yOffset = 0

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantThwomp', 'thwomp_giant.png')

class SpriteImage_DryBones(SLib.SpriteImage_StaticMultiple): # 137
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
                  

class SpriteImage_BigDryBones(SLib.SpriteImage_StaticMultiple): # 138
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
                  
class SpriteImage_PipeUp(SpriteImage_Pipe): # 139
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'U'
        self.typeinfluence = True

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

class SpriteImage_PipeDown(SpriteImage_Pipe): # 140
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'D'
        self.typeinfluence = True

    def dataChanged(self):
        
        size = self.parent.spritedata[3]
        
        if size == 0:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0
            self.yOffset = 0
        elif size == 1:
            self.big = False
            self.painted = True
            self.width = 32
            self.xOffset = 0
            self.yOffset = -16
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

class SpriteImage_PipeLeft(SpriteImage_Pipe): # 141
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'L'
        self.typeinfluence = True

    def dataChanged(self):
        
        size = self.parent.spritedata[3]
        
        if size == 0:
            self.big = False
            self.painted = False
            self.height = 32
            self.yOffset = 0
            self.xOffset = 0
        elif size == 1:
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
        
class SpriteImage_PipeRight(SpriteImage_Pipe): # 142
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'R'
        self.typeinfluence = True

    def dataChanged(self):
        
        size = self.parent.spritedata[3]
        
        if size == 0:
            self.big = False
            self.painted = False
            self.height = 32
            self.yOffset = 0
        elif size == 1:
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

class SpriteImage_BubbleYoshi(SLib.SpriteImage_Static): # 143, 243
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BubbleYoshi'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BubbleYoshi', 'babyyoshibubble.png')

class SpriteImage_MovPipe(SpriteImage_Pipe): # 146
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'U'
        self.typeinfluence = True

    def dataChanged(self):
        
        size = self.parent.spritedata[5] >> 4
        direction = self.parent.spritedata[3] >> 4
        self.moving = True
        
        if direction == 1:
            self.direction = 'L'
            self.height = 32
            self.topX = 0
            self.topY = 0
        elif direction == 2:
            self.direction = 'U'
            self.width = 32
            self.topY = 0
            self.topX = 0
        elif direction == 3:
            self.direction = 'D'
            self.width = 32
            self.topY = self.pipeHeight - 60
            self.topX = 0
        else:
            self.direction = 'R'
            self.height = 32
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

class SpriteImage_StoneEye(SLib.SpriteImage_StaticMultiple): # 150
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
        ImageCache['BigStoneRightUp'] = ImageCache['StoneRightUp'].scaled(439*1.5, 821*1.5,QtCore.Qt.KeepAspectRatio)
        ImageCache['BigStoneLeftUp'] = ImageCache['StoneLeftUp'].scaled(439*1.5, 821*1.5,QtCore.Qt.KeepAspectRatio)
        ImageCache['BigStoneFront'] = ImageCache['StoneFront'].scaled(354*1.5, 745*1.5,QtCore.Qt.KeepAspectRatio)
        ImageCache['BigStoneRight'] = ImageCache['StoneRight'].scaled(478*1.5, 747*1.5,QtCore.Qt.KeepAspectRatio)
        ImageCache['BigStoneLeft'] = ImageCache['StoneLeft'].scaled(487*1.5, 747*1.5,QtCore.Qt.KeepAspectRatio)

    def dataChanged(self):
        
        direction = self.parent.spritedata[4]
        movID = self.parent.spritedata[10]

        trueDirection = "Front"

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
            self.xOffset = -48.5+17.5
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
            self.xOffset = -41.5+(-16*3)
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
#        self.translateImage()

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


       
class SpriteImage_POWBlock(SLib.SpriteImage_Static): # 152
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['POWBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('POWBlock', 'block_pow.png')  

class SpriteImage_FlyingQBlock(SLib.SpriteImage_Static): # 154
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['FlyingQBlock'],
            )

        self.xOffset = -6.5
        self.yOffset = -11.5

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FlyingQBlock', 'flying_qblock.png') 

class SpriteImage_WaterGeyser(SpriteImage_StackedSprite): # 156
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
        rawlengthminus = self.parent.spritedata[4]

        if rawlengthones == 0: rawlengthones = 0
        elif rawlengthones == 16: rawlengthones = 1
        elif rawlengthones == 32: rawlengthones = 2
        elif rawlengthones == 48: rawlengthones = 3
        elif rawlengthones == 64: rawlengthones = 4
        elif rawlengthones == 80: rawlengthones = 5
        elif rawlengthones == 96: rawlengthones = 6
        elif rawlengthones == 112: rawlengthones = 7
        elif rawlengthones == 128: rawlengthones = 8
        elif rawlengthones == 144: rawlengthones = 9
        elif rawlengthones == 160: rawlengthones = 10
        elif rawlengthones == 176: rawlengthones = 11
        elif rawlengthones == 192: rawlengthones = 12
        elif rawlengthones == 208: rawlengthones = 13
        elif rawlengthones == 224: rawlengthones = 14
        elif rawlengthones == 240: rawlengthones = 15
        elif rawlengthones == 256: rawlengthones = 16

        rawlengthtwos = rawlengthtwos * 16

#        if rawlengthtwos > 255: rawlengthtwos = rawlengthtwos - 256

        rawlength = rawlengthones + rawlengthtwos

        rawtype = self.parent.spritedata[3] & 3

        pipeLength = rawlength

#        print(rawlengthones, rawlengthtwos, pipeLength)

        self.hasTop = True
        self.hasBottom = False

        self.pipeHeight = (pipeLength + 1) * 60
        self.height = (self.pipeHeight/3.75)
        self.pipeHeight = (pipeLength) * 60


        self.middle = ImageCache['WaterGeyserMiddle']
        self.top = ImageCache['WaterGeyserTop']

        self.pipeWidth = 360
        self.width = 96
        
        self.yOffset = 8 + (-6*16) + (-1*((rawlength-2)*8))
#        self.yOffset = -12 * 16
        self.xOffset = -40

    def paint(self, painter):
        super().paint(painter)

        painter.drawTiledPixmap(self.x, self.y, self.pipeWidth, self.pipeHeight, self.middle)
        if self.hasTop:
            painter.drawPixmap(self.topX, self.topY, self.top)

class SpriteImage_CoinOutline(SLib.SpriteImage_StaticMultiple): # 158
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75, # native res (3.75*16=60)
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

class SpriteImage_ExpandingPipeUp(SpriteImage_Pipe): # 161
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.direction = 'U'
        self.typeinfluence = True

    def dataChanged(self):
        
        size = self.parent.spritedata[4]
        self.expandable = True

        bigSize = self.parent.spritedata[5]

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
            addSize = 2
        elif size == 2:
            self.big = True
            self.painted = False
            self.width = 64
            self.xOffset = -16
            addSize = 3
        else:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0
            addSize = 1


        totalHeight = (bigSize/16) + addSize

        yOff = -(bigSize/16)

        self.aux[0].setSize(self.width/16*60, totalHeight*60, 0, yOff*60)

        super().dataChanged()

class SpriteImage_ExpandingPipeDown(SpriteImage_Pipe): # 162
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.direction = 'D'
        self.typeinfluence = True

    def dataChanged(self):
        
        size = self.parent.spritedata[4]
        self.expandable = True

        bigSize = self.parent.spritedata[5]

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
            addSize = 2
        elif size == 2:
            self.big = True
            self.painted = False
            self.width = 64
            self.xOffset = -16
            addSize = 3
        else:
            self.big = False
            self.painted = False
            self.width = 32
            self.xOffset = 0
            addSize = 1


        totalHeight = (bigSize/16) + addSize

        self.aux[0].setSize(self.width/16*60, totalHeight*60)

        super().dataChanged()


class SpriteImage_WaterGeyserLocation(SpriteImage_StackedSprite): # 163
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
        rawlengthminus = self.parent.spritedata[4]

        if rawlengthones == 0: rawlengthones = 0
        elif rawlengthones == 16: rawlengthones = 1
        elif rawlengthones == 32: rawlengthones = 2
        elif rawlengthones == 48: rawlengthones = 3
        elif rawlengthones == 64: rawlengthones = 4
        elif rawlengthones == 80: rawlengthones = 5
        elif rawlengthones == 96: rawlengthones = 6
        elif rawlengthones == 112: rawlengthones = 7
        elif rawlengthones == 128: rawlengthones = 8
        elif rawlengthones == 144: rawlengthones = 9
        elif rawlengthones == 160: rawlengthones = 10
        elif rawlengthones == 176: rawlengthones = 11
        elif rawlengthones == 192: rawlengthones = 12
        elif rawlengthones == 208: rawlengthones = 13
        elif rawlengthones == 224: rawlengthones = 14
        elif rawlengthones == 240: rawlengthones = 15
        elif rawlengthones == 256: rawlengthones = 16

        rawlengthtwos = rawlengthtwos * 16

#        if rawlengthtwos > 255: rawlengthtwos = rawlengthtwos - 256

        rawlength = rawlengthones

        rawtype = self.parent.spritedata[3] & 3

        pipeLength = rawlength

#        print(rawlengthones, rawlengthtwos, pipeLength)

        self.hasTop = True
        self.hasBottom = False

        self.pipeHeight = (pipeLength + 1) * 60
        self.height = (self.pipeHeight/3.75)
        self.pipeHeight = (pipeLength) * 60


        self.middle = ImageCache['WaterGeyserMiddle']
        self.top = ImageCache['WaterGeyserTop']

        self.pipeWidth = 360
        self.width = 96
        
        self.yOffset = 8 + (-6*16) + (-1*((rawlength-2)*8))
#        self.yOffset = -12 * 16
        self.xOffset = -40

    def paint(self, painter):
        super().paint(painter)

        painter.drawTiledPixmap(self.x, self.y, self.pipeWidth, self.pipeHeight, self.middle)
        if self.hasTop:
            painter.drawPixmap(self.topX, self.topY, self.top)

class SpriteImage_CoinBlue(SLib.SpriteImage_Static): # 167
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['CoinBlue'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CoinBlue', 'coin_blue.png')

class SpriteImage_ClapCoin(SLib.SpriteImage_Static): # 168
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ClapCoin'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ClapCoin', 'clap_coin.png')

class SpriteImage_ControllerIf(SLib.SpriteImage_StaticMultiple): # 169
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerIf'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerIf', 'controller_if.png')

class SpriteImage_Parabomb(SLib.SpriteImage_StaticMultiple): # 170
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Parabomb'],
            )
        
        self.yOffset = -16
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Parabomb', 'parabomb.png')          

class SpriteImage_Mechakoopa(SLib.SpriteImage_StaticMultiple): # 175
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

        
class SpriteImage_AirshipCannon(SLib.SpriteImage_StaticMultiple): # 176
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )

        self.yOffset = -7

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CannonL', 'Cannon_L.png')
        SLib.loadIfNotInImageCache('CannonR', 'Cannon_R.png')

    def dataChanged(self):          
        
        direction = self.parent.spritedata[5]
        
        if direction == 0:
            self.image = ImageCache['CannonL']
        elif direction == 1:
            self.image = ImageCache['CannonR']
        else:
            self.image = ImageCache['CannonL']
            
        super().dataChanged()

class SpriteImage_Crash(SLib.SpriteImage_StaticMultiple): # 177
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Crash', 'crash.png')

class SpriteImage_FallingIcicle(SLib.SpriteImage_StaticMultiple): # 183
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

class SpriteImage_GiantIcicle(SLib.SpriteImage_Static): # 184
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

class SpriteImage_MovQBlock(SLib.SpriteImage_StaticMultiple): # 190
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MovQBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovQBlock', 'mov_qblock.png')

class SpriteImage_RouletteBlock(SLib.SpriteImage_StaticMultiple): # 195
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['RouletteBlock'],
            )
        
        #self.yOffset = -17
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RouletteBlock', 'block_roulette.png') 


class SpriteImage_MushroomPlatform(SLib.SpriteImage): # 200
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        self.spritebox.shown = False
        
    @staticmethod
    def loadImages():
        ImageCache['SkinnyOrangeL'] = SLib.GetImg('orange_mushroom_skinny_l.png')
        ImageCache['SkinnyOrangeM'] = SLib.GetImg('orange_mushroom_skinny_m.png')
        ImageCache['SkinnyOrangeR'] = SLib.GetImg('orange_mushroom_skinny_r.png')
        ImageCache['SkinnyGreenL'] = SLib.GetImg('green_mushroom_skinny_l.png')
        ImageCache['SkinnyGreenM'] = SLib.GetImg('green_mushroom_skinny_m.png')
        ImageCache['SkinnyGreenR'] = SLib.GetImg('green_mushroom_skinny_r.png')
        ImageCache['ThickBlueL'] = SLib.GetImg('blue_mushroom_thick_l.png')
        ImageCache['ThickBlueM'] = SLib.GetImg('blue_mushroom_thick_m.png')
        ImageCache['ThickBlueR'] = SLib.GetImg('blue_mushroom_thick_r.png')
        ImageCache['ThickRedL'] = SLib.GetImg('red_mushroom_thick_l.png')
        ImageCache['ThickRedM'] = SLib.GetImg('red_mushroom_thick_m.png')
        ImageCache['ThickRedR'] = SLib.GetImg('red_mushroom_thick_r.png')               


    def dataChanged(self):
        super().dataChanged()

        self.color = self.parent.spritedata[4] & 1
        self.girth = self.parent.spritedata[5] >> 4 & 1


        if self.girth == 0:
#            self.width = ((self.parent.spritedata[8] & 0xF) + 3) << 4 # because default crapo
            self.height = 60


            if self.parent.spritedata[8] % 2 == 1:
                self.width = (self.parent.spritedata[8]) + (self.parent.spritedata[8]-1)
            else:
                self.width = (self.parent.spritedata[8]) + 2

            self.xOffset = 16 + (-1*((self.width)*8))

        else:
            self.height = 120
            if self.parent.spritedata[8] % 2 == 1:
#                self.width = (self.parent.spritedata[8]) + (self.parent.spritedata[8]-1)
                self.width = ((self.parent.spritedata[8]) * 2) + 4
            else:
                self.width = ((self.parent.spritedata[8]) * 2) + 4

            self.xOffset = 16 + (-1*((self.width)*8))

            self.yOffset = -16



        self.width = self.width * 16

#        self.xOffset = (-1*((self.width/16)*16))
#        self.xOffset = (-1*((self.width/16)*8))
#        self.xOffset = self.xOffset + (-8 * (self.parent.spritedata[8]))

#        print(self.parent.spritedata[8], self.xOffset)

    def paint(self, painter):
        super().paint(painter)

        # this is coded so horribly
        
        if self.width > 32:
            if self.color == 0 and self.girth == 0:
                painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['SkinnyOrangeM'])
            elif self.color == 1 and self.girth == 0:
                painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['SkinnyGreenM'])
            elif self.color == 0 and self.girth == 1:
                painter.drawTiledPixmap(120, 0, ((self.width * 3.75)-240), 120, ImageCache['ThickRedM'])
            elif self.color == 1 and self.girth == 1:
                painter.drawTiledPixmap(120, 0, ((self.width * 3.75)-240), 120, ImageCache['ThickBlueM'])                    
            else:
                painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['SkinnyOrangeM'])

        if self.width == 24:
            if self.color == 0 and self.girth == 0:
                painter.drawPixmap(0, 0, ImageCache['SkinnyOrangeR'])
                painter.drawPixmap(8, 0, ImageCache['SkinnyOrangeL'])
            elif self.color == 1 and self.girth == 0:
                painter.drawPixmap(0, 0, ImageCache['SkinnyGreenR'])
                painter.drawPixmap(8, 0, ImageCache['SkinnyGreenL'])
            elif self.color == 0 and self.girth == 1:
                painter.drawPixmap(0, 0, ImageCache['ThickRedR'])
                painter.drawPixmap(8, 0, ImageCache['ThickRedL'])
            elif self.color == 1 and self.girth == 1:
                painter.drawPixmap(0, 0, ImageCache['ThickBlueR'])
                painter.drawPixmap(8, 0, ImageCache['ThickBlueL'])                    
            else:
                painter.drawPixmap(0, 0, ImageCache['SkinnyOrangeR'])
                painter.drawPixmap(8, 0, ImageCache['SkinnyOrangeL'])                
        else:
            if self.color == 0 and self.girth == 0:
                painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['SkinnyOrangeR'])
                painter.drawPixmap(0, 0, ImageCache['SkinnyOrangeL'])
            elif self.color == 1 and self.girth == 0:
                painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['SkinnyGreenR'])
                painter.drawPixmap(0, 0, ImageCache['SkinnyGreenL'])
            elif self.color == 0 and self.girth == 1:
                painter.drawPixmap((self.width - 32) * 3.75, 0, ImageCache['ThickRedR'])
                painter.drawPixmap(0, 0, ImageCache['ThickRedL'])
            elif self.color == 1 and self.girth == 1:
                painter.drawPixmap((self.width - 32) * 3.75, 0, ImageCache['ThickBlueR'])
                painter.drawPixmap(0, 0, ImageCache['ThickBlueL'])                 
            else:
                painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['SkinnyOrangeR'])
                painter.drawPixmap(0, 0, ImageCache['SkinnyOrangeL'])

class SpriteImage_IceBlock(SLib.SpriteImage_StaticMultiple): # 203
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

class SpriteImage_ControllerAutoscroll(SLib.SpriteImage_Static): # 212
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerAutoscroll'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerAutoscroll', 'controller_autoscroll.png')    

class SpriteImage_ControllerSpinOne(SLib.SpriteImage_Static): # 214
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerSpinOne'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerSpinOne', 'controller_spinning_one.png')  

class SpriteImage_Springboard(SLib.SpriteImage_Static): # 215
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Springboard'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Springboard', 'springboard.png')         

class SpriteImage_BalloonYoshi(SLib.SpriteImage_Static): # 224
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BalloonYoshi'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BalloonYoshi', 'balloonbabyyoshi.png')

class SpriteImage_Foo(SLib.SpriteImage_Static): # 229
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

class SpriteImage_SpinningFirebar(SLib.SpriteImage): # 235
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

class SpriteImage_Bolt(SLib.SpriteImage_StaticMultiple): # 238
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

class SpriteImage_TileGod(SLib.SpriteImage): # 237
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def dataChanged(self):
        super().dataChanged()

        width = self.parent.spritedata[8] & 0xF
        height = self.parent.spritedata[9] & 0xF
        if width == 0: width = 1
        if height == 0: height = 1
        if width == 1 and height == 1:
            self.aux[0].setSize(0,0)
            return
        self.aux[0].setSize(width * 60, height * 60)

class SpriteImage_PricklyGoomba(SLib.SpriteImage_StaticMultiple): # 247
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PricklyGoomba'],
            )
        
        self.yOffset = -13
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PricklyGoomba', 'prickly_goomba.png')           

class SpriteImage_Wiggler(SLib.SpriteImage_StaticMultiple): # 249
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Wiggler'],
            )
        
        self.yOffset = -17
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Wiggler', 'wiggler.png') 

class SpriteImage_MicroGoomba(SLib.SpriteImage_Static): # 255
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MicroGoomba'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MicroGoomba', 'micro_goomba.png')    

class SpriteImage_Muncher(SLib.SpriteImage_StaticMultiple): # 259
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

class SpriteImage_Parabeetle(SLib.SpriteImage_Static): # 261
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Parabeetle'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Parabeetle', 'parabeetle.png')

class SpriteImage_RollingHill(SLib.SpriteImage): # 265
    RollingHillSizes = [2*40, 18*40, 32*40, 50*40, 64*40, 0, 0, 0, 18*40, 2*40, 30*40]
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.xOffset = 5

        size = (self.parent.spritedata[3] >> 4) & 0xF
        if (size == 0 or size == 9):
            increase = self.parent.spritedata[4] & 0xF
            realSize = self.RollingHillSizes[size] * (increase + 1)
        elif size > 10:
            realSize = 0
        else:
            realSize = self.RollingHillSizes[size]

        self.aux.append(SLib.AuxiliaryCircleOutline(parent, realSize))

    def dataChanged(self):
        super().dataChanged()

        size = (self.parent.spritedata[3] >> 4) & 0xF
        if (size == 0 or size == 9):
            increase = self.parent.spritedata[4] & 0xF
            realSize = self.RollingHillSizes[size] * (increase + 1)
        elif size > 10:
            realSize = 0
        else:
            realSize = self.RollingHillSizes[size]

        self.aux[0].setSize(realSize)
        self.aux[0].update()

class SpriteImage_TowerCog(SLib.SpriteImage_StaticMultiple): # 269
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
            self.xOffset = -140
            self.yOffset = -144
        else:
            self.image = ImageCache['TowerCogS']
            self.xOffset = -88
            self.yOffset = -96
            
        super().dataChanged()
        self.parent.setZValue(-50000)

class SpriteImage_Amp(SLib.SpriteImage_StaticMultiple): # 334
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Amp', 'amp.png')
        SLib.loadIfNotInImageCache('AmpB', 'amp_big.png')

    def dataChanged(self):
        
        big = self.parent.spritedata[4]

        if big == 0:
            self.image = ImageCache['Amp']
            self.xOffset = -2
            self.yOffset = -4
        elif big == 1:
            self.image = ImageCache['AmpB']
        else:
            self.image = ImageCache['Amp']
            self.xOffset = -2
            self.yOffset = -4

        super().dataChanged()

class SpriteImage_CoinBubble(SLib.SpriteImage_Static): # 281
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['CoinBubble'],
            )
        
        self.yOffset = -4
        self.xOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CoinBubble', 'coin_bubble.png')

class SpriteImage_KingBill(SLib.SpriteImage_StaticMultiple): # 282
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        
        #self.xOffset = -7
        #self.yOffset = -2

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
            self.yOffset= -120
        elif direction == 1 or direction == 17 or direction == 33 or direction == 49 or direction == 65 or direction == 86 or direction == 97 or direction == 113 or direction == 129 or direction == 145 or direction == 161 or direction == 177 or direction == 193 or direction == 209 or direction == 225 or direction == 241:
            self.image = ImageCache['KingR']
            self.yOffset= -120
        elif direction == 2 or direction == 18 or direction == 34 or direction == 50 or direction == 66 or direction == 82 or direction == 98 or direction == 114 or direction == 129 or direction == 146 or direction == 162 or direction == 178 or direction == 194 or direction == 210 or direction == 226 or direction == 242:
            self.image = ImageCache['KingD']
            self.xOffset= -85
        elif direction == 3 or direction == 19 or direction == 35 or direction == 51 or direction == 67 or direction == 83 or direction == 99 or direction == 115 or direction == 130 or direction == 147 or direction == 163 or direction == 179 or direction == 195 or direction == 211 or direction == 227 or direction == 243:
            self.image = ImageCache['KingU']
            self.xOffset= -85
        else:
            self.image = ImageCache['KingR']
            self.yOffset= -120

        super().dataChanged()

class SpriteImage_NoteBlock(SLib.SpriteImage_Static): # 295
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['NoteBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('NoteBlock', 'noteblock.png')

class SpriteImage_Broozer(SLib.SpriteImage_Static): # 320
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

class SpriteImage_Barrel(SLib.SpriteImage_Static): # 323 -- BARRELS
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

class SpriteImage_RotationControlledCoin(SLib.SpriteImage_Static): # 325
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Coin'],
            )
        self.parent.setZValue(20000)

class SpriteImage_MovementControlledCoin(SLib.SpriteImage_Static): # 326
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Coin'],
            )
        self.parent.setZValue(20000)

class SpriteImage_BoltControlledCoin(SLib.SpriteImage_Static): # 328
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Coin'],
            )
        self.parent.setZValue(20000)

class SpriteImage_Cooligan(SLib.SpriteImage_StaticMultiple): # 334
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

class SpriteImage_Bramball(SLib.SpriteImage_Static): # 336
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

class SpriteImage_WoodenBox(SLib.SpriteImage_StaticMultiple): # 338
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
            self.image = ImageCache['Reg2x2'] # let's not make some nonsense out of this
            
        super().dataChanged()

class SpriteImage_StoneBlock(SLib.SpriteImage_Static): # 347
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['StoneBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StoneBlock', 'stone_block.png')
   
class SpriteImage_SuperGuide(SLib.SpriteImage_Static): # 348
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SuperGuide'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SuperGuide', 'guide_block.png')

class SpriteImage_Pokey(SLib.SpriteImage): # 351
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

        self.length = self.rawlength*60

        self.width = 27
        self.xOffset = -5.33
        
        self.height = (self.rawlength-1)*16+25
        self.yOffset = -1*(self.rawlength*16)+32-25+1.33

        if self.upsideDown == 1:

            self.length = self.rawlength*60

            self.width = 27
            self.xOffset = -5.33
        
            self.height = (self.rawlength-1)*16+25
            self.yOffset = 0


        super().dataChanged()


    def paint(self, painter):
        super().paint(painter)

        #Not upside-down:
        if self.upsideDown is not 1:
            painter.drawPixmap(0, 0+(self.length-120)+91, 100, 60, ImageCache['PokeyBottom'])
            painter.drawTiledPixmap(0, 91, 100, (self.length-120), ImageCache['PokeyMiddle'])
            painter.drawPixmap(0, 0, 100, 91, ImageCache['PokeyTop'])

        #Upside Down
        else:
            painter.drawPixmap(0, 0+(self.length-120)+60, 100, 91, ImageCache['PokeyTopD'])
            painter.drawTiledPixmap(0, 60, 100, (self.length-120), ImageCache['PokeyMiddleD'])
            painter.drawPixmap(0, 0, 100, 60, ImageCache['PokeyBottomD'])

class SpriteImage_GoldenYoshi(SLib.SpriteImage_Static): # 365
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GoldenYoshi'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GoldenYoshi', 'babyyoshiglowing.png')

class SpriteImage_TorpedoLauncher(SLib.SpriteImage_StaticMultiple): # 378
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['TorpedoLauncher'],
            )
        
        #self.yOffset = -17
        self.xOffset = -22

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TorpedoLauncher', 'torpedo_launcher.png')

class SpriteImage_Starman(SLib.SpriteImage_StaticMultiple): # 395
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

class SpriteImage_BrickMovement(SLib.SpriteImage_StaticMultiple): # 398
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BrickMovement'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BrickMovement', 'brick_movement.png') 

class SpriteImage_GreenRing(SLib.SpriteImage_Static): # 402
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

class SpriteImage_PipeUpEnterable(SpriteImage_Pipe): # 404
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

class SpriteImage_BumpPlatform(SLib.SpriteImage): # 407
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

        self.width = ((self.parent.spritedata[8] & 0xF) + 1) << 4

    def paint(self, painter):
        super().paint(painter)
        
        if self.width > 32:
            painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['BumpPlatformM'])

        if self.width == 24:
            painter.drawPixmap(0, 0, ImageCache['BumpPlatformR'])
            painter.drawPixmap(8, 0, ImageCache['BumpPlatformL'])
        else:
            # normal rendering
            painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['BumpPlatformR'])
            painter.drawPixmap(0, 0, ImageCache['BumpPlatformL'])

class SpriteImage_BigBrickBlock(SLib.SpriteImage_Static): # 422
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigBrick'],
            )
        
        self.yOffset = 16

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigBrick', 'big_brickblock.png')

class SpriteImage_SnowyBoxes(SLib.SpriteImage_StaticMultiple): # 427
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

class SpriteImage_Fliprus(SLib.SpriteImage_StaticMultiple): # 441
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
        
class SpriteImage_BonyBeetle(SLib.SpriteImage_Static): # 443
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BonyBeetle'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BonyBeetle', 'bony_beetle.png')

class SpriteImage_FliprusSnowball(SLib.SpriteImage_StaticMultiple): # 446
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Snowball'],
            )
        
        self.yOffset = -10
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Snowball', 'snowball.png') 

class SpriteImage_NabbitPlacement(SLib.SpriteImage_Static): # 451
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['NabbitP'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('NabbitP', 'nabbit_placement.png') 

class SpriteImage_ClapCrowd(SLib.SpriteImage_Static): # 455
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ClapCrowd'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ClapCrowd', 'clap_crowd.png')       

class SpriteImage_BigGoomba(SLib.SpriteImage_StaticMultiple): # 472
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

class SpriteImage_MegaBowser(SLib.SpriteImage_Static): # 473
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MegaBowser'],
            )

        self.yOffset = -310
        self.xOffset = -210

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MegaBowser', 'mega_bowser.png')

class SpriteImage_BigQBlock(SLib.SpriteImage_Static): # 475
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BigQBlock'],
            )

        self.yOffset = 16  

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigQBlock', 'big_qblock.png')

class SpriteImage_BigKoopaTroopa(SLib.SpriteImage_StaticMultiple): # 476
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

class SpriteImage_MovementControlledStarCoin(SLib.SpriteImage_Static): # 480
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MovementStarCoin'],
            )

        yOffset = -8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovementStarCoin', 'star_coin.png')

class SpriteImage_WaddleWing(SLib.SpriteImage_StaticMultiple): # 481
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ) #What image to load is taken care of later

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

class SpriteImage_MultiSpinningFirebar(SLib.SpriteImage): # 483
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

class SpriteImage_ControllerSpinning(SLib.SpriteImage_Static): # 484
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerSpinning'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerSpinning', 'controller_spinning.png')

class SpriteImage_FrameSetting(SLib.SpriteImage_Static): # 486
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['FrameSetting'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FrameSetting', 'frame_setting.png')

class SpriteImage_BoltControlledMovingCoin(SLib.SpriteImage_Static): # 496
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Coin'],
            )
        self.parent.setZValue(20000)

class SpriteImage_MovingGrassPlatform(SLib.SpriteImage): # 499
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        #self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
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
        ImageCache['MovGMiddle2L'] = SLib.GetImg('mov_grass_middle2_l.png')
        ImageCache['MovGMiddle2M'] = SLib.GetImg('mov_grass_middle2_m.png')
        ImageCache['MovGMiddle2R'] = SLib.GetImg('mov_grass_middle2_r.png')
        ImageCache['MovGMiddle3L'] = SLib.GetImg('mov_grass_middle3_l.png')
        ImageCache['MovGMiddle3M'] = SLib.GetImg('mov_grass_middle3_m.png')
        ImageCache['MovGMiddle3R'] = SLib.GetImg('mov_grass_middle3_r.png')
        ImageCache['MovGMiddle4L'] = SLib.GetImg('mov_grass_middle4_l.png')
        ImageCache['MovGMiddle4R'] = SLib.GetImg('mov_grass_middle4_r.png')
        ImageCache['MovGMiddle5L'] = SLib.GetImg('mov_grass_middle5_l.png')
        ImageCache['MovGMiddle5R'] = SLib.GetImg('mov_grass_middle5_r.png')
        ImageCache['MovGMiddle6L'] = SLib.GetImg('mov_grass_middle6_l.png')
        ImageCache['MovGMiddle6R'] = SLib.GetImg('mov_grass_middle6_r.png')
        ImageCache['MovGMiddle7L'] = SLib.GetImg('mov_grass_middle7_l.png')
        ImageCache['MovGMiddle7R'] = SLib.GetImg('mov_grass_middle7_r.png')
        ImageCache['MovGMiddle8L'] = SLib.GetImg('mov_grass_middle8_l.png')
        ImageCache['MovGMiddle8R'] = SLib.GetImg('mov_grass_middle8_r.png')
        ImageCache['MovGMiddle9L'] = SLib.GetImg('mov_grass_middle9_l.png')
        ImageCache['MovGMiddle9R'] = SLib.GetImg('mov_grass_middle9_r.png')

    def dataChanged(self):
        super().dataChanged()

        self.width = (self.parent.spritedata[8] & 0xF)*16+16
        self.height = (self.parent.spritedata[9] & 0xF)*16+16

       # if self.width/16 == 1 and self.height/16 == 1:
            #self.aux[0].setSize(0,0)
            #return
        #self.aux[0].setSize(self.width/16*60, self.height/16*60)

    def paint(self, painter):
        super().paint(painter)

        #Time to code this lazily.

        #Top of sprite.
        if self.width/16 == 1:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovGTopM'])
        elif self.width/16 == 2:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovGTopL'])
            painter.drawPixmap(60, 0, 60, 60, ImageCache['MovGTopR'])
        elif self.width/16 == 3:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovGTopL'])
            painter.drawPixmap(60, 0, 60, 60, ImageCache['MovGTopM'])
            painter.drawPixmap(120, 0, 60, 60, ImageCache['MovGTopR'])
        else:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovGTopL'])
            painter.drawTiledPixmap(60, 0, (self.width/16-2)*60, 60, ImageCache['MovGTopM'])
            painter.drawPixmap(60+((self.width/16-2)*60), 0, 60, 60, ImageCache['MovGTopR'])



        #Middle
        if self.width/16 > 1:
            if self.height/16 > 0:
                painter.drawTiledPixmap(60, 60, ((self.width/16)-2)*60, ((self.height/16)-1)*60, ImageCache['MovGMiddleM'])

        #Panic for insufficiant width
        if self.height/16 > 1:
            if self.width/16 > 1:
                if self.width/16 < 6:
                    painter.drawTiledPixmap(0, 60, 60, ((self.height/16)-1)*60, ImageCache['MovGMiddleL'])
                    painter.drawTiledPixmap((self.width/16*60)-60, 60, 60, ((self.height/16)-1)*60, ImageCache['MovGMiddleR'])

        #Middle decoration
        if self.height/16 > 0:
            if self.width/16 > 8:
                painter.drawTiledPixmap(240, 60, 120, 60, ImageCache['MovGMiddle2M'])

            if self.width/16 > 14:
                painter.drawTiledPixmap(660, 60, 60, 60, ImageCache['MovGMiddle3M'])


        #Layers - (Are like onions)
        if self.width/16 > 5:
            if self.height/16 > 1:
                painter.drawTiledPixmap(0, 60, 60, 60, ImageCache['MovGMiddleL'])
                painter.drawTiledPixmap((self.width/16*60)-60, 60, 60, 60, ImageCache['MovGMiddleR'])

            if self.height/16 > 2:
                painter.drawTiledPixmap(0, 120, 180, 60, ImageCache['MovGMiddle2L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 120, 180, 60, ImageCache['MovGMiddle2R'])

            if self.height/16 > 3:
                painter.drawTiledPixmap(0, 180, 180, 60, ImageCache['MovGMiddle3L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 180, 180, 60, ImageCache['MovGMiddle3R'])

            if self.height/16 > 4:
                painter.drawTiledPixmap(0, 240, 180, 60, ImageCache['MovGMiddle4L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 240, 180, 60, ImageCache['MovGMiddle4R'])

            if self.height/16 > 5:
                painter.drawTiledPixmap(0, 300, 180, 60, ImageCache['MovGMiddle5L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 300, 180, 60, ImageCache['MovGMiddle5R'])

            if self.height/16 > 6:
                painter.drawTiledPixmap(0, 360, 180, 60, ImageCache['MovGMiddle6L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 360, 180, 60, ImageCache['MovGMiddle6R'])

            if self.height/16 > 7:
                painter.drawTiledPixmap(0, 420, 180, 60, ImageCache['MovGMiddle7L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 420, 180, 60, ImageCache['MovGMiddle7R'])

            if self.height/16 > 8:
                painter.drawTiledPixmap(0, 480, 180, 60, ImageCache['MovGMiddle8L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 480, 180, 60, ImageCache['MovGMiddle8R'])

            if self.height/16 > 9:
                painter.drawTiledPixmap(0, 540, 180, 60, ImageCache['MovGMiddle9L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 540, 180, 60, ImageCache['MovGMiddle9R'])

            if self.height/16 > 10:
                painter.drawTiledPixmap(0, 600, 180, 60, ImageCache['MovGMiddle2L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 600, 180, 60, ImageCache['MovGMiddle2R'])

            if self.height/16 > 11:
                painter.drawTiledPixmap(0, 660, 180, 60, ImageCache['MovGMiddle3L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 660, 180, 60, ImageCache['MovGMiddle3R'])

            if self.height/16 > 12:
                painter.drawTiledPixmap(0, 720, 180, 60, ImageCache['MovGMiddle4L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 720, 180, 60, ImageCache['MovGMiddle4R'])

            if self.height/16 > 13:
                painter.drawTiledPixmap(0, 780, 180, 60, ImageCache['MovGMiddle5L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 780, 180, 60, ImageCache['MovGMiddle5R'])

            if self.height/16 > 14:
                painter.drawTiledPixmap(0, 840, 180, 60, ImageCache['MovGMiddle6L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 840, 180, 60, ImageCache['MovGMiddle6R'])

            if self.height/16 > 15:
                painter.drawTiledPixmap(0, 900, 180, 60, ImageCache['MovGMiddle7L'])
                painter.drawTiledPixmap((self.width/16*60)-180, 900, 180, 60, ImageCache['MovGMiddle7R'])




        #1 Glitch
        if self.width/16 < 1:
            painter.drawPixmap(0, 0, 60, 60, ImageCache['MovGTopM'])
            painter.drawTiledPixmap(0, 60, 60, ((self.height/16)-1)*60, ImageCache['MovGMiddleM'])



class SpriteImage_PaintGoal(SLib.SpriteImage_StaticMultiple): # 503
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        
        self.xOffset = -32
        self.yOffset = -144

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PaintFlagReg', 'flag_paint_reg.png')
        SLib.loadIfNotInImageCache('PaintFlagSec', 'flag_paint_sec.png')

    def dataChanged(self):
        
        secret = self.parent.spritedata[2] >> 4

        if secret == 1: self.image = ImageCache['PaintFlagSec']
        else: self.image = ImageCache['PaintFlagReg']

        super().dataChanged()

class SpriteImage_Grrrol(SLib.SpriteImage_StaticMultiple): # 504
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GrrrolSmall'],
            )
        
        self.yOffset = -12
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GrrrolSmall', 'grrrol_small.png')

class SpriteImage_ShootingStar(SLib.SpriteImage_StaticMultiple): # 507
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ShootingStar'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ShootingStar', 'shooting_star.png')

class SpriteImage_PipeJoint(SLib.SpriteImage_Static): # 513
    def __init__(self, parent, scale=3.75):
        super().__init__(
            parent,
            scale,
            ImageCache['PipeJoint'])

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeJoint', 'pipe_joint.png')

class SpriteImage_PipeJointSmall(SLib.SpriteImage_Static): # 514
    def __init__(self, parent, scale=3.75):
        super().__init__(
            parent,
            scale,
            ImageCache['PipeJointSmall'])

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeJointSmall', 'pipe_joint_mini.png')

class SpriteImage_MiniPipeRight(SpriteImage_Pipe): # 516
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.mini = True
        self.direction = 'R'

class SpriteImage_MiniPipeLeft(SpriteImage_Pipe): # 517
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.mini = True
        self.direction = 'L'

class SpriteImage_MiniPipeUp(SpriteImage_Pipe): # 518
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.mini = True
        self.direction = 'U'

class SpriteImage_MiniPipeDown(SpriteImage_Pipe): # 519
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.mini = True
        self.direction = 'D'

class SpriteImage_FlyingQBlockAmbush(SLib.SpriteImage_Static): # 523
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['FlyingQBlockAmbush'],
            )

        self.xOffset = -6.5
        self.yOffset = -11.5

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FlyingQBlockAmbush', 'flying_qblock.png') 

class SpriteImage_BouncyMushroomPlatform(SLib.SpriteImage): # 542
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        self.spritebox.shown = False
 
    @staticmethod
    def loadImages():
        ImageCache['SkinnyOrangeL'] = SLib.GetImg('orange_mushroom_skinny_l.png')
        ImageCache['SkinnyOrangeM'] = SLib.GetImg('orange_mushroom_skinny_m.png')
        ImageCache['SkinnyOrangeR'] = SLib.GetImg('orange_mushroom_skinny_r.png')
        ImageCache['SkinnyGreenL'] = SLib.GetImg('green_mushroom_skinny_l.png')
        ImageCache['SkinnyGreenM'] = SLib.GetImg('green_mushroom_skinny_m.png')
        ImageCache['SkinnyGreenR'] = SLib.GetImg('green_mushroom_skinny_r.png')
        ImageCache['ThickBlueL'] = SLib.GetImg('blue_mushroom_thick_l.png')
        ImageCache['ThickBlueM'] = SLib.GetImg('blue_mushroom_thick_m.png')
        ImageCache['ThickBlueR'] = SLib.GetImg('blue_mushroom_thick_r.png')
        ImageCache['ThickRedL'] = SLib.GetImg('red_mushroom_thick_l.png')
        ImageCache['ThickRedM'] = SLib.GetImg('red_mushroom_thick_m.png')
        ImageCache['ThickRedR'] = SLib.GetImg('red_mushroom_thick_r.png')               

    def dataChanged(self):
        super().dataChanged()

        self.color = self.parent.spritedata[4] & 1
        self.girth = self.parent.spritedata[5] >> 4 & 1
        if self.girth == 1:
            self.width = ((self.parent.spritedata[8] & 0xF) + 3) << 4 # because default crapo
            self.height = 30
        else:
            self.width = ((self.parent.spritedata[8] & 0xF) + 2) << 4

    def paint(self, painter):
        super().paint(painter)

        # this is coded so horribly
        
        if self.width > 32:
            if self.color == 0 and self.girth == 0:
                painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['SkinnyOrangeM'])
            elif self.color == 1 and self.girth == 0:
                painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['SkinnyGreenM'])
            elif self.color == 0 and self.girth == 1:
                painter.drawTiledPixmap(120, 0, ((self.width * 3.75)-240), 120, ImageCache['ThickRedM'])
            elif self.color == 1 and self.girth == 1:
                painter.drawTiledPixmap(120, 0, ((self.width * 3.75)-240), 120, ImageCache['ThickBlueM'])                    
            else:
                painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['SkinnyOrangeM'])

        if self.width == 24:
            if self.color == 0 and self.girth == 0:
                painter.drawPixmap(0, 0, ImageCache['SkinnyOrangeR'])
                painter.drawPixmap(8, 0, ImageCache['SkinnyOrangeL'])
            elif self.color == 1 and self.girth == 0:
                painter.drawPixmap(0, 0, ImageCache['SkinnyGreenR'])
                painter.drawPixmap(8, 0, ImageCache['SkinnyGreenL'])
            elif self.color == 0 and self.girth == 1:
                painter.drawPixmap(0, 0, ImageCache['ThickRedR'])
                painter.drawPixmap(8, 0, ImageCache['ThickRedL'])
            elif self.color == 1 and self.girth == 1:
                painter.drawPixmap(0, 0, ImageCache['ThickBlueR'])
                painter.drawPixmap(8, 0, ImageCache['ThickBlueL'])                    
            else:
                painter.drawPixmap(0, 0, ImageCache['SkinnyOrangeR'])
                painter.drawPixmap(8, 0, ImageCache['SkinnyOrangeL'])                
        else:
            if self.color == 0 and self.girth == 0:
                painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['SkinnyOrangeR'])
                painter.drawPixmap(0, 0, ImageCache['SkinnyOrangeL'])
            elif self.color == 1 and self.girth == 0:
                painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['SkinnyGreenR'])
                painter.drawPixmap(0, 0, ImageCache['SkinnyGreenL'])
            elif self.color == 0 and self.girth == 1:
                painter.drawPixmap((self.width - 32) * 3.75, 0, ImageCache['ThickRedR'])
                painter.drawPixmap(0, 0, ImageCache['ThickRedL'])
            elif self.color == 1 and self.girth == 1:
                painter.drawPixmap((self.width - 32) * 3.75, 0, ImageCache['ThickBlueR'])
                painter.drawPixmap(0, 0, ImageCache['ThickBlueL'])                 
            else:
                painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['SkinnyOrangeR'])
                painter.drawPixmap(0, 0, ImageCache['SkinnyOrangeL'])

class SpriteImage_MushroomMovingPlatform(SLib.SpriteImage): # 544
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            )
        self.spritebox.shown = False
        
    @staticmethod
    def loadImages():
        ImageCache['SkinnyPinkL'] = SLib.GetImg('pink_mushroom_skinny_l.png')
        ImageCache['SkinnyPinkM'] = SLib.GetImg('pink_mushroom_skinny_m.png')
        ImageCache['SkinnyPinkR'] = SLib.GetImg('pink_mushroom_skinny_r.png')
        ImageCache['SkinnyCyanL'] = SLib.GetImg('cyan_mushroom_skinny_l.png')
        ImageCache['SkinnyCyanM'] = SLib.GetImg('cyan_mushroom_skinny_m.png')
        ImageCache['SkinnyCyanR'] = SLib.GetImg('cyan_mushroom_skinny_r.png')
        ImageCache['ThickBlueL'] = SLib.GetImg('blue_mushroom_thick_l.png')
        ImageCache['ThickBlueM'] = SLib.GetImg('blue_mushroom_thick_m.png')
        ImageCache['ThickBlueR'] = SLib.GetImg('blue_mushroom_thick_r.png')
        ImageCache['ThickRedL'] = SLib.GetImg('red_mushroom_thick_l.png')
        ImageCache['ThickRedM'] = SLib.GetImg('red_mushroom_thick_m.png')
        ImageCache['ThickRedR'] = SLib.GetImg('red_mushroom_thick_r.png')
        ImageCache['PinkStem'] = SLib.GetImg('pink_mushroom_stem.png')
        ImageCache['CyanStem'] = SLib.GetImg('cyan_mushroom_stem.png')

    def dataChanged(self):
        super().dataChanged()

        self.color = self.parent.spritedata[7]

        if self.color > 0:
            self.color = 1

        self.girth = 0


        self.height = 120


        self.width = (self.parent.spritedata[4]/16) + 3



        self.xOffset = 8 + (-1*((self.width)*8))



        self.width = self.width * 16

#        self.xOffset = (-1*((self.width/16)*16))
#        self.xOffset = (-1*((self.width/16)*8))
#        self.xOffset = self.xOffset + (-8 * (self.parent.spritedata[8]))

#        print(self.parent.spritedata[8], self.xOffset)

    def paint(self, painter):
        super().paint(painter)

        # this is coded so horribly
        
        if self.width > 32:
            if self.color == 0 and self.girth == 0:
                painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['SkinnyPinkM'])
                painter.drawPixmap(((self.width/2)-12) * 3.75, 60, ImageCache['PinkStem'])
            elif self.color == 1 and self.girth == 0:
                painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['SkinnyCyanM'])
                painter.drawPixmap(((self.width/2)-12) * 3.75, 60, ImageCache['CyanStem'])
            elif self.color == 0 and self.girth == 1:
                painter.drawTiledPixmap(120, 0, ((self.width * 3.75)-240), 120, ImageCache['ThickRedM'])
            elif self.color == 1 and self.girth == 1:
                painter.drawTiledPixmap(120, 0, ((self.width * 3.75)-240), 120, ImageCache['ThickBlueM'])                    
            else:
                painter.drawTiledPixmap(60, 0, ((self.width * 3.75)-120), 60, ImageCache['SkinnyPinkM'])

        if self.width == 24:
            if self.color == 0 and self.girth == 0:
                painter.drawPixmap(0, 0, ImageCache['SkinnyPinkR'])
                painter.drawPixmap(8, 0, ImageCache['SkinnyPinkL'])
            elif self.color == 1 and self.girth == 0:
                painter.drawPixmap(0, 0, ImageCache['SkinnyCyanR'])
                painter.drawPixmap(8, 0, ImageCache['SkinnyCyanL'])
            elif self.color == 0 and self.girth == 1:
                painter.drawPixmap(0, 0, ImageCache['ThickRedR'])
                painter.drawPixmap(8, 0, ImageCache['ThickRedL'])
            elif self.color == 1 and self.girth == 1:
                painter.drawPixmap(0, 0, ImageCache['ThickBlueR'])
                painter.drawPixmap(8, 0, ImageCache['ThickBlueL'])                    
            else:
                painter.drawPixmap(0, 0, ImageCache['SkinnyPinkR'])
                painter.drawPixmap(8, 0, ImageCache['SkinnyPinkL'])                
        else:
            if self.color == 0 and self.girth == 0:
                painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['SkinnyPinkR'])
                painter.drawPixmap(0, 0, ImageCache['SkinnyPinkL'])
            elif self.color == 1 and self.girth == 0:
                painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['SkinnyCyanR'])
                painter.drawPixmap(0, 0, ImageCache['SkinnyCyanL'])
            elif self.color == 0 and self.girth == 1:
                painter.drawPixmap((self.width - 32) * 3.75, 0, ImageCache['ThickRedR'])
                painter.drawPixmap(0, 0, ImageCache['ThickRedL'])
            elif self.color == 1 and self.girth == 1:
                painter.drawPixmap((self.width - 32) * 3.75, 0, ImageCache['ThickBlueR'])
                painter.drawPixmap(0, 0, ImageCache['ThickBlueL'])                 
            else:
                painter.drawPixmap((self.width - 16) * 3.75, 0, ImageCache['SkinnyPinkR'])
                painter.drawPixmap(0, 0, ImageCache['SkinnyPinkL'])


class SpriteImage_Flowers(SLib.SpriteImage_StaticMultiple): # 546
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
        
        id = self.parent.spritedata[3]
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

class SpriteImage_NabbitMetal(SLib.SpriteImage_Static): # 566
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['NabbitMetal'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('NabbitMetal', 'nabbit_metal.png')

class SpriteImage_NabbitPrize(SLib.SpriteImage_Static): # 569
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['NabbitPrize'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('NabbitPrize', 'nabbit_prize.png')

class SpriteImage_SumoBro(SLib.SpriteImage_Static): # 593
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SumoBro'],
            )

        self.xOffset = -18
        self.yOffset = -18

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SumoBro', 'sumo_bro.png')

class SpriteImage_Goombrat(SLib.SpriteImage_StaticMultiple): # 595
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Goombrat'],
            )
        
        #self.yOffset = -17
        #self.xOffset = -6

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Goombrat', 'goombrat.png')

class SpriteImage_MoonBlock(SLib.SpriteImage_StaticMultiple): # 600
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MoonBlock'],
            )
        
        #self.yOffset = -17
        self.xOffset = -3

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MoonBlock', 'moon_block.png') 

class SpriteImage_PacornBlock(SLib.SpriteImage_Static): # 612
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['PacornBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PacornBlock', 'pacorn_block.png')

class SpriteImage_SteelBlock(SLib.SpriteImage_Static): # 618
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SteelBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SteelBlock', 'steel_block.png')

class SpriteImage_BlueRing(SLib.SpriteImage_Static): # 662
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
    19: SpriteImage_KoopaTroopa,
    20: SpriteImage_KoopaParatroopa,
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
    97: SpriteImage_BackCenter,
    101: SpriteImage_CheepCheep,
    102: SpriteImage_Useless,
    104: SpriteImage_QuestionSwitch,
    105: SpriteImage_PSwitch,
    108: SpriteImage_GhostHouseDoor,
    109: SpriteImage_TowerBossDoor,
    110: SpriteImage_CastleBossDoor,
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
#    146: SpriteImage_MovPipe,
    150: SpriteImage_StoneEye,
    152: SpriteImage_POWBlock,
    154: SpriteImage_FlyingQBlock,
    156: SpriteImage_WaterGeyser,
    158: SpriteImage_CoinOutline,
#    161: SpriteImage_ExpandingPipeUp,
#    162: SpriteImage_ExpandingPipeDown, --Glitches with pipe length area thing.
    163: SpriteImage_WaterGeyserLocation,
    166: SpriteImage_CoinOutline,
    167: SpriteImage_CoinBlue,
    168: SpriteImage_ClapCoin,
    169: SpriteImage_ControllerIf,
    170: SpriteImage_Parabomb,
    175: SpriteImage_Mechakoopa,
    176: SpriteImage_AirshipCannon,
    177: SpriteImage_Crash,
    178: SpriteImage_Crash,
    183: SpriteImage_FallingIcicle,
    184: SpriteImage_GiantIcicle,
    190: SpriteImage_MovQBlock,
    195: SpriteImage_RouletteBlock,
    200: SpriteImage_MushroomPlatform,
    203: SpriteImage_IceBlock,
    212: SpriteImage_ControllerAutoscroll,
    214: SpriteImage_ControllerSpinOne,
    215: SpriteImage_Springboard,
    224: SpriteImage_BalloonYoshi,
    229: SpriteImage_Foo,
    235: SpriteImage_SpinningFirebar,
    237: SpriteImage_TileGod,
    238: SpriteImage_Bolt,
    243: SpriteImage_BubbleYoshi,
    244: SpriteImage_Useless,
    247: SpriteImage_PricklyGoomba,
    249: SpriteImage_Wiggler,
    255: SpriteImage_MicroGoomba,
    256: SpriteImage_Crash,
    259: SpriteImage_Muncher,
    261: SpriteImage_Parabeetle,
    265: SpriteImage_RollingHill,
    269: SpriteImage_TowerCog,
    270: SpriteImage_Amp,
    281: SpriteImage_CoinBubble,
    282: SpriteImage_KingBill,
    295: SpriteImage_NoteBlock,
    306: SpriteImage_Crash,
    310: SpriteImage_Crash,
    312: SpriteImage_Crash,
    314: SpriteImage_Crash,
    319: SpriteImage_Crash,
    320: SpriteImage_Broozer,
    323: SpriteImage_Barrel,
    325: SpriteImage_RotationControlledCoin,
    326: SpriteImage_MovementControlledCoin,
    328: SpriteImage_BoltControlledCoin,
    334: SpriteImage_Cooligan,
    336: SpriteImage_Bramball,
    338: SpriteImage_WoodenBox,
    345: SpriteImage_Crash,   
    347: SpriteImage_StoneBlock, 
    348: SpriteImage_SuperGuide,
    351: SpriteImage_Pokey,
    355: SpriteImage_Crash,
    358: SpriteImage_Crash,
    360: SpriteImage_Crash,
    365: SpriteImage_GoldenYoshi,
    376: SpriteImage_Crash,
    377: SpriteImage_Crash,
    378: SpriteImage_TorpedoLauncher,
    395: SpriteImage_Starman,
    398: SpriteImage_BrickMovement,
    402: SpriteImage_GreenRing,
    404: SpriteImage_PipeUpEnterable,
    405: SpriteImage_Crash,
    407: SpriteImage_BumpPlatform,
    422: SpriteImage_BigBrickBlock,
    427: SpriteImage_SnowyBoxes,
    436: SpriteImage_Crash,
    439: SpriteImage_Crash,
    441: SpriteImage_Fliprus,
    446: SpriteImage_FliprusSnowball,
    449: SpriteImage_Useless,
    451: SpriteImage_NabbitPlacement,
    452: SpriteImage_Crash,
    455: SpriteImage_ClapCrowd,
    456: SpriteImage_Useless,
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
    496: SpriteImage_BoltControlledMovingCoin,
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
    521: SpriteImage_Crash,
    522: SpriteImage_Crash,
    523: SpriteImage_FlyingQBlockAmbush,
    529: SpriteImage_Crash,
    538: SpriteImage_Crash,
    542: SpriteImage_BouncyMushroomPlatform,
    544: SpriteImage_MushroomMovingPlatform,
    546: SpriteImage_Flowers,
    551: SpriteImage_Useless,
    555: SpriteImage_Crash,
    556: SpriteImage_Crash,
    566: SpriteImage_NabbitMetal,
    569: SpriteImage_NabbitPrize,
    572: SpriteImage_Crash,
    593: SpriteImage_SumoBro,
    595: SpriteImage_Goombrat,
    600: SpriteImage_MoonBlock,
    612: SpriteImage_PacornBlock,
    618: SpriteImage_SteelBlock,
    630: SpriteImage_Flagpole,
    631: SpriteImage_PaintGoal,
    662: SpriteImage_BlueRing,
}
