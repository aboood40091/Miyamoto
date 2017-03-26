#!/usr/bin/python
# -*- coding: latin-1 -*-

# Miyamoto! Next - New Super Mario Bros. U Level Editor
# Version v0.6
# Copyright (C) 2009-2016 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop

# This file is part of Miyamoto! Next.

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


################################################################
################################################################

# Imports

from PyQt5 import QtCore, QtGui
Qt = QtCore.Qt


import spritelib as SLib
ImageCache = SLib.ImageCache


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

class SpriteImage_Block(SLib.SpriteImage):
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

class SpriteImage_Pipe(SLib.SpriteImage):
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.spritebox.shown = self.mini = self.big = self.typeinfluence = False
        self.hasTop = True
        self.direction = 'U'
        self.colours = ("Green", "Red", "Yellow", "Blue")
        self.topY = self.topX = self.colour = self.extraLength = self.x = self.y = 0
        self.width = self.height = 32
        self.pipeHeight = self.pipeWidth = 120
        self.parent.setZValue(24999)

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

                # BIG
                ImageCache['PipeBigTop%s' % colour] = ImageCache['PipeRight%s' % colour].scaled(240,240,QtCore.Qt.KeepAspectRatio)
                ImageCache['PipeBigMiddleV%s' % colour] = ImageCache['PipeRight%s' % colour].scaled(60,240)
                ImageCache['PipeBigMiddleH%s' % colour] = ImageCache['PipeRight%s' % colour].scaled(60,240)
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
        rawlength = (self.parent.spritedata[5] & 0x0F) + 1
        if not self.mini:
            rawtop = (self.parent.spritedata[2] >> 4) & 3
            rawcolour = (self.parent.spritedata[5] >> 4) & 3
            if self.typeinfluence and rawtop == 0:
                rawtype = self.parent.spritedata[3] & 3
            else:
                rawtype = 0

            if rawtop == 1:
                pipeLength = rawlength + rawtype + self.extraLength + 1
            else:
                pipeLength = rawlength + rawtype + self.extraLength

            self.hasTop = (rawtop != 3)
            self.big = (rawtype == 3)
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
            elif not self.mini:
                self.middle = ImageCache['PipeMiddleH%s' % self.colour]
            else:
                self.middle = ImageCache['MiniPipeMiddleH%s' % self.colour]
                self.height = 16
                self.pipeHeight = 60

            if self.direction == 'R': # faces right
                if self.big:
                    self.top = ImageCache['PipeBigRight%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeRight%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeRight%s' % self.colour]
                self.topX = self.pipeWidth - 60
            else: # faces left
                if self.big:
                    self.top = ImageCache['PipeBigLeft%s' % self.colour]
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
            elif not self.mini:
                self.middle = ImageCache['PipeMiddleV%s' % self.colour]
            else:
                self.middle = ImageCache['MiniPipeMiddleV%s' % self.colour]
                self.width = 16
                self.pipeWidth = 60

            if self.direction == 'D': # faces down
                if self.big:
                    self.top = ImageCache['PipeBigBottom%s' % self.colour]
                elif not self.mini:
                    self.top = ImageCache['PipeBottom%s' % self.colour]
                else:
                    self.top = ImageCache['MiniPipeBottom%s' % self.colour]
                self.topY = self.pipeHeight - 60
            else: # faces up
                if self.big:
                    self.top = ImageCache['PipeBigTop%s' % self.colour]
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
        
        self.yOffset = -41

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MidwayFlag', 'midway_flag.png')

class SpriteImage_Flagpole(SLib.SpriteImage_Static): # 31
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Flagpole'],
            )
        
        #self.yOffset = -4.5 # close enough, it can't be a whole number
        #self.xOffset = -10

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Flagpole', 'flagpole.png')  

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

class SpriteImage_Coin(SLib.SpriteImage_Static): # 65
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Coin'],
            )
        self.parent.setZValue(20000)

class SpriteImage_ControllerSwaying(SLib.SpriteImage_Static): # 68
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerSwaying'],
            )
        self.parent.setZValue(20000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerSwaying', 'controller_swaying.png') 

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

 
#EDDDIITTT THISS NOWOWOOWOWOWO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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

        self.xOffset = -14
        self.yOffset = -16

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

class SpriteImage_PipeDown(SpriteImage_Pipe): # 140
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'D'
        self.typeinfluence = True

class SpriteImage_PipeLeft(SpriteImage_Pipe): # 141
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'L'
        self.typeinfluence = True
        
class SpriteImage_PipeRight(SpriteImage_Pipe): # 142
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 'R'
        self.typeinfluence = True

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

class SpriteImage_CrashBattery(SLib.SpriteImage_StaticMultiple): # 177
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Crash', 'crash.png')

class SpriteImage_CrashBatteryS(SLib.SpriteImage_Static): # 178
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

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
        height = self.parent.spritedata[5] >> 4
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

class SpriteImage_CrashMushroom(SLib.SpriteImage_Static): # 256
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)     

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

class SpriteImage_CrashOne(SLib.SpriteImage_Static): # 306
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashTwo(SLib.SpriteImage_Static): # 310
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashThree(SLib.SpriteImage_Static): # 312
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashFour(SLib.SpriteImage_Static): # 314
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashRaft(SLib.SpriteImage_Static): # 319
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

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

class SpriteImage_CrashSeesaw(SLib.SpriteImage_Static): # 345
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)
   
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

class SpriteImage_CrashHill(SLib.SpriteImage_Static): # 355
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashFive(SLib.SpriteImage_Static): # 358
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashSix(SLib.SpriteImage_Static): # 360
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

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

class SpriteImage_CrashSeven(SLib.SpriteImage_Static): # 376
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashEight(SLib.SpriteImage_Static): # 377
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

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
            self.xOffset = -43
            self.yOffset = -33
        elif direction == 16:
            self.image = ImageCache['StarmanB']
            self.xOffset = -62
            self.yOffset = -51
        elif direction == 32:
            self.image = ImageCache['StarmanG']
            self.xOffset = -100
            self.yOffset = -100
        else:
            self.image = ImageCache['StarmanS']
            self.xOffset = -43
            self.yOffset = -33

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

class SpriteImage_CrashNine(SLib.SpriteImage_Static): # 405
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

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

class SpriteImage_CrashTen(SLib.SpriteImage_Static): # 436
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashEleven(SLib.SpriteImage_Static): # 439
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

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

class SpriteImage_CrashBYoshi(SLib.SpriteImage_Static): # 452
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)       

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

class SpriteImage_CrashTwelve(SLib.SpriteImage_Static): # 479
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_MovementControlledStarCoin(SLib.SpriteImage_Static): # 480
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MovementStarCoin'],
            )

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
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.parent.setZValue(24999)

    def dataChanged(self):
        super().dataChanged()

        width = (self.parent.spritedata[8] & 0xF) + 1
        height = (self.parent.spritedata[9] & 0xF) + 1
        if width == 1 and height == 1:
            self.aux[0].setSize(0,0)
            return
        self.aux[0].setSize(width * 60, height * 60)

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

class SpriteImage_CrashThirteen(SLib.SpriteImage_Static): # 521
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashBarrel(SLib.SpriteImage_Static): # 522
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashFourteen(SLib.SpriteImage_Static): # 529
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashFifteen(SLib.SpriteImage_Static): # 538
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

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

class SpriteImage_CrashSixteen(SLib.SpriteImage_Static): # 555
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashBubbleYoshi(SLib.SpriteImage_Static): # 556
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

class SpriteImage_CrashSeventeen(SLib.SpriteImage_Static): # 572
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Crash'],
            )
        self.parent.setZValue(20000)

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
    19: SpriteImage_KoopaTroopa,
    23: SpriteImage_Spiny,
    25: SpriteImage_MidwayFlag,
#    31: SpriteImage_Flagpole, Needs work.
    32: SpriteImage_ArrowSignboard,
    36: SpriteImage_ZoneTrigger,
    44: SpriteImage_RedRing,
    45: SpriteImage_StarCoin,
    46: SpriteImage_LineControlledStarCoin,
    47: SpriteImage_BoltControlledStarCoin,
    48: SpriteImage_MvmtRotControlledStarCoin,
    49: SpriteImage_RedCoin,
    50: SpriteImage_GreenCoin,
    54: SpriteImage_YoshiBerry,
    59: SpriteImage_QBlock,
    60: SpriteImage_BrickBlock,
    61: SpriteImage_InvisiBlock,
    63: SpriteImage_StalkingPiranha,
    65: SpriteImage_Coin,
    66: SpriteImage_Coin,
    68: SpriteImage_ControllerSwaying,
    74: SpriteImage_HuckitCrab,
    87: SpriteImage_MovingCoin,
    94: SpriteImage_BouncyCloud,
    104: SpriteImage_QuestionSwitch,
    105: SpriteImage_PSwitch,
    108: SpriteImage_GhostHouseDoor,
    109: SpriteImage_TowerBossDoor,
    110: SpriteImage_CastleBossDoor,
    123: SpriteImage_SandPillar,
    135: SpriteImage_Thwomp,
    136: SpriteImage_GiantThwomp,
    137: SpriteImage_DryBones,
    138: SpriteImage_BigDryBones,
    139: SpriteImage_PipeUp,
    140: SpriteImage_PipeDown,
    141: SpriteImage_PipeLeft,
    142: SpriteImage_PipeRight,
    143: SpriteImage_BubbleYoshi,
    152: SpriteImage_POWBlock,
    158: SpriteImage_CoinOutline,
    169: SpriteImage_ControllerIf,
    170: SpriteImage_Parabomb,
    175: SpriteImage_Mechakoopa,
    176: SpriteImage_AirshipCannon,
    177: SpriteImage_CrashBattery,
    178: SpriteImage_CrashBatteryS,
    183: SpriteImage_FallingIcicle,
    184: SpriteImage_GiantIcicle,
    195: SpriteImage_RouletteBlock,
    212: SpriteImage_ControllerAutoscroll,
    214: SpriteImage_ControllerSpinOne,
    215: SpriteImage_Springboard,
    224: SpriteImage_BalloonYoshi,
    229: SpriteImage_Foo,
    235: SpriteImage_SpinningFirebar,
    237: SpriteImage_TileGod,
    238: SpriteImage_Bolt,
    243: SpriteImage_BubbleYoshi,
    247: SpriteImage_PricklyGoomba,
    249: SpriteImage_Wiggler,
    256: SpriteImage_CrashMushroom,
    259: SpriteImage_Muncher,
    261: SpriteImage_Parabeetle,
    282: SpriteImage_KingBill,
    295: SpriteImage_NoteBlock,
    306: SpriteImage_CrashOne,
    310: SpriteImage_CrashTwo,
    312: SpriteImage_CrashThree,
    314: SpriteImage_CrashFour,
    319: SpriteImage_CrashRaft,
    320: SpriteImage_Broozer,
    323: SpriteImage_Barrel,
    325: SpriteImage_RotationControlledCoin,
    326: SpriteImage_MovementControlledCoin,
    328: SpriteImage_BoltControlledCoin,
    334: SpriteImage_Cooligan,
    336: SpriteImage_Bramball,
    338: SpriteImage_WoodenBox,
    345: SpriteImage_CrashSeesaw,    
    348: SpriteImage_SuperGuide,
    355: SpriteImage_CrashHill,
    358: SpriteImage_CrashFive,
    360: SpriteImage_CrashSix,
    365: SpriteImage_GoldenYoshi,
    376: SpriteImage_CrashSeven,
    377: SpriteImage_CrashEight,
    378: SpriteImage_TorpedoLauncher,
    395: SpriteImage_Starman,
    398: SpriteImage_BrickMovement,
    402: SpriteImage_GreenRing,
    404: SpriteImage_PipeUpEnterable,
    405: SpriteImage_CrashNine,
    407: SpriteImage_BumpPlatform,
    422: SpriteImage_BigBrickBlock,
    436: SpriteImage_CrashTen,
    439: SpriteImage_CrashEleven,
    441: SpriteImage_Fliprus,
    446: SpriteImage_FliprusSnowball,
    451: SpriteImage_NabbitPlacement,
    452: SpriteImage_CrashBYoshi,
    472: SpriteImage_BigGoomba,
    473: SpriteImage_MegaBowser,
    475: SpriteImage_BigQBlock,
    476: SpriteImage_BigKoopaTroopa,
    479: SpriteImage_CrashTwelve,
    480: SpriteImage_MovementControlledStarCoin,
    481: SpriteImage_WaddleWing,
    483: SpriteImage_MultiSpinningFirebar,
    484: SpriteImage_ControllerSpinning,
    486: SpriteImage_FrameSetting,
    496: SpriteImage_BoltControlledMovingCoin,
    499: SpriteImage_MovingGrassPlatform,
    504: SpriteImage_Grrrol,
    511: SpriteImage_PipeDown,
    513: SpriteImage_PipeJoint,
    514: SpriteImage_PipeJointSmall,
    516: SpriteImage_MiniPipeRight,
    517: SpriteImage_MiniPipeLeft,
    518: SpriteImage_MiniPipeUp,
    519: SpriteImage_MiniPipeDown,
    521: SpriteImage_CrashThirteen,
    522: SpriteImage_CrashBarrel,
    529: SpriteImage_CrashFourteen,
    538: SpriteImage_CrashFifteen,
    542: SpriteImage_BouncyMushroomPlatform,
    555: SpriteImage_CrashSixteen,
    556: SpriteImage_CrashBubbleYoshi,
    572: SpriteImage_CrashSeventeen,
    593: SpriteImage_SumoBro,
    595: SpriteImage_Goombrat,
    600: SpriteImage_MoonBlock,
    662: SpriteImage_BlueRing,
}
