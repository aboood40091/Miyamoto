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


class SpriteImage_Pipe(SLib.SpriteImage_MovementControlled):
    types = {
        'Normal': (
            '',
            ('Green', 'green'),
            ('Red', 'red'),
            ('Yellow', 'yellow'),
            ('Purple', 'purple'),
        ),
        'Painted': (
            '_painted',
            ('Green', 'green'),
            ('Red', 'red'),
            ('Yellow', 'yellow'),
            ('Blue', 'blue'),
        ),
        'Big': (
            '_big',
            ('Green', 'green'),
        ),
        'Mini': (
            '_mini',
            ('Green', 'green'),
        ),
    }

    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)

        self.hasTop = True
        self.direction = 0  # 0: Up, 1: Down, 2: Left, 3: Right
        self.type = 'Normal'
        self.color = 'Green'

        self.width, self.height = 32, 32
        self.pipeWidth, self.pipeHeight = 120, 60

        self.topX, self.topY = 0, 0
        self.middleX, self.middleY = 0, 0

        self.parent.setZValue(24999)

    @staticmethod
    def loadImages():
        if 'PipeVTopNormalGreen' not in ImageCache:
            for typeName in SpriteImage_Pipe.types:
                type = SpriteImage_Pipe.types[typeName]; suffix = type[0]
                for C, c in type[1:]:
                    for D, d in (('V', ''), ('H', '_horizontal')):
                        ImageCache['Pipe%sTop%s%s' % (D, typeName, C)] = SLib.GetImg('pipe%s_top%s_%s.png' % (d, suffix, c))
                        ImageCache['Pipe%sTopMiddle%s%s' % (D, typeName, C)] = SLib.GetImg('pipe%s_middle%s_%s.png' % (d, suffix, c))
                        ImageCache['Pipe%sBottom%s%s' % (D, typeName, C)] = SLib.GetImg('pipe%s_bottom%s_%s.png' % (d, suffix, c))
                        ImageCache['Pipe%sBottomMiddle%s%s' % (D, typeName, C)] = ImageCache['Pipe%sTopMiddle%s%s' % (D, typeName, C)].transformed(
                            QTransform().scale(1, -1) if D == 'V' else QTransform().scale(-1, 1)
                        )

    def getMovementID(self):
        return 0

    def allowedMovementControllers(self):
        return tuple()

    def getParamsForDirection(self):
        direction = self.direction
        if direction == 0:
            return 'V', 'Top'

        elif direction == 1:
            return 'V', 'Bottom'

        elif direction == 2:
            return 'H', 'Top'

        return 'H', 'Bottom'

    def dataChanged(self):
        d, t = self.getParamsForDirection()

        pix = QtGui.QPixmap(self.width * 3.75, self.height * 3.75)
        pix.fill(Qt.transparent)

        painter = QtGui.QPainter(pix)
        painter.drawTiledPixmap(self.middleX, self.middleY, self.pipeWidth, self.pipeHeight, ImageCache['Pipe%s%sMiddle%s%s' % (d, t, self.type, self.color)])
        if self.hasTop:
            painter.drawPixmap(self.topX, self.topY, ImageCache['Pipe%s%s%s%s' % (d, t, self.type, self.color)])

        painter.end()
        del painter

        self.image = pix

        super().dataChanged()


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


class SpriteImage_LiquidOrFog(SLib.SpriteImage):  # 88, 89, 90, 91, 92, 93, 198, 201
    def __init__(self, parent):
        super().__init__(parent)

        self.crest = None
        self.mid = None
        self.rise = None
        self.riseCrestless = None

        self.top = 0

        self.drawCrest = False
        self.risingHeight = 0

        self.locId = 0
        self.findZone()

    def findZone(self):
        self.zoneId = SLib.MapPositionToZoneID(globals.Area.zones, self.parent.objx, self.parent.objy, True)

    def positionChanged(self):
        self.findZone()
        self.parent.scene().update()
        super().positionChanged()

    def dataChanged(self):
        self.parent.scene().update()
        super().dataChanged()

    def paintZone(self):
        return self.locId == 0 and self.zoneId != -1

    def realViewZone(self, painter, zoneRect):
        """
        Real view zone painter for liquids/fog
        """
        # (0, 0) is the top-left corner of the zone

        _, zy, zw, zh = zoneRect.getRect()

        drawRise = self.risingHeight != 0
        drawCrest = self.drawCrest

        # Get positions
        offsetFromTop = (self.top * 3.75) - zy
        if offsetFromTop > zh:
            # the sprite is below the zone; don't draw anything
            return

        if offsetFromTop <= 4:
            offsetFromTop = 4
            drawCrest = False  # off the top of the zone; no crest

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

    def realViewLocation(self, painter, zoneRect):
        """
        Real view location painter for liquids/fog
        """
        zoneId = self.zoneId
        if zoneId == -1:
            return

        for zone in globals.Area.zones:
            if zone.id == zoneId:
                break

        zx, zy = zoneRect.x(), zoneRect.y()
        zoneRect &= zone.sceneBoundingRect()
        zx, zy = zoneRect.x() - zx, zoneRect.y() - zy
        zw, zh = zoneRect.width(), zoneRect.height()
        if zw <= 0 or zh <= 0:
            return

        drawCrest = False
        crestHeight = 0

        if self.drawCrest:
            crestHeight = self.crest.height()
            drawCrest = zy < crestHeight

        if drawCrest:
            crestHeight -= zy
            if crestHeight >= zh:
                painter.drawTiledPixmap(zx, zy, zw, zh, self.crest, zx, zy)
            else:
                painter.drawTiledPixmap(zx, zy, zw, crestHeight, self.crest, zx, zy)
                painter.drawTiledPixmap(zx, zy + crestHeight, zw, zh - crestHeight, self.mid, zx)
        else:
            painter.drawTiledPixmap(zx, zy, zw, zh, self.mid, zx, zy - crestHeight)


class SpriteImage_PlatformBase(SLib.SpriteImage):  # X
    def __init__(self, parent, hasAux=False):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False
        self.hasAux = hasAux

        if self.hasAux:
            self.aux.append(SLib.AuxiliaryTrackObject(parent, 0, 0, 0))
            self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
            self.aux[1].alpha = 0.5

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

    def getPlatformMoveDir(self):
        """
        Return a string with 'U', 'D', 'L' or 'R' specifying the movement direction of the platform.
        """
        return 'U'

    def getPlatformMoveDist(self):
        """
        Return an integer specifying the movement distance of the platform.
        """
        return 0

    def paintPlatform(self, painter):
        left = ImageCache['MovPlat%sL' % self.imgType]
        mid = ImageCache['MovPlat%sM' % self.imgType]
        right = ImageCache['MovPlat%sR' % self.imgType]
        
        painter.drawPixmap(0, 0, left)
        painter.drawPixmap(self.width * 3.75 - right.width(), 0, right)

        if self.width > (left.width() + right.width()) / 3.75:
            painter.drawTiledPixmap(int(left.width()), 0, self.width * 3.75 - (left.width() + right.width()), mid.height(), mid)

    def dataChanged(self):
        self.offset = self.getPlatformOffset()
        self.imgType = self.getPlatformType()
        self.width = self.getPlatformWidth() * 16
        self.height = max(ImageCache['MovPlat%sL' % self.imgType].height(), ImageCache['MovPlat%sM' % self.imgType].height(), ImageCache['MovPlat%sR' % self.imgType].height()) / 3.75

        if self.hasAux:
            pix = QtGui.QPixmap(self.width * 3.75, self.height * 3.75)
            pix.fill(Qt.transparent)
            painter = QtGui.QPainter(pix)
            self.paintPlatform(painter)
            painter = None

            moveDir = self.getPlatformMoveDir()
            moveDist = self.getPlatformMoveDist()

            if moveDir == 'L' or moveDir == 'R':
                self.aux[0].setSize((moveDist + 1) * 16, 16)
                self.aux[0].direction = SLib.AuxiliaryTrackObject.Horizontal
            else:
                self.aux[0].setSize(16, (moveDist + 1) * 16)
                self.aux[0].direction = SLib.AuxiliaryTrackObject.Vertical
            
            xOffset = 0
            yOffset = 0
            
            if moveDir == 'L':
                xOffset = -moveDist * 16
            elif moveDir == 'U':
                yOffset = -moveDist * 16
                
            self.aux[0].setPos((xOffset + self.width * 0.5 - 8) * 3.75, yOffset * 3.75)
            
            if moveDir == 'R':
                xOffset = moveDist * 16
            elif moveDir == 'D':
                yOffset = moveDist * 16
                
            self.aux[1].setImage(pix, xOffset, yOffset, True)
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        self.paintPlatform(painter)


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
        self.xOffset = -16

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


class SpriteImage_KoopaTroopa(SLib.SpriteImage_StaticMultiple):  # 19, 55
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
        self.aux.append(SLib.AuxiliaryTrackObject(parent, 0, 0, 0))

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('KoopaParatroopaG', 'koopa_paratroopa_green.png')
        SLib.loadIfNotInImageCache('KoopaParatroopaR', 'koopa_paratroopa_red.png')

    def dataChanged(self):
        color = self.parent.spritedata[5] & 1
        mode = self.parent.spritedata[5] >> 4 & 3
        direction = self.parent.spritedata[4] >> 4 & 3

        if color == 0:
            self.image = ImageCache['KoopaParatroopaG']

        else:
            self.image = ImageCache['KoopaParatroopaR']

        track = self.aux[0]

        if mode not in (1, 2) or direction not in (1, 2):
            track.setSize(0, 0)

        else:
            onEdge = self.parent.spritedata[4] & 1

            width = self.width * 3.75
            height = self.height * 3.75

            if mode == 1:
                track.direction = SLib.AuxiliaryTrackObject.Horizontal
                track.setSize(9 * 16, 16)

                if onEdge:
                    if direction == 1:
                        track.setPos(-0.625 * 60 + width / 2, -0.625 * 60 + height / 2)

                    else:
                        track.setPos(-8.625 * 60 + width / 2, -0.625 * 60 + height / 2)

                else:
                    track.setPos(-4.625 * 60 + width / 2, -0.625 * 60 + height / 2)

            else:
                track.direction = SLib.AuxiliaryTrackObject.Vertical
                track.setSize(16, 9 * 16)

                if onEdge:
                    if direction == 1:
                        track.setPos(-0.625 * 60 + width / 2, -9.125 * 60 + height / 2)

                    else:
                        track.setPos(-0.625 * 60 + width / 2, -0.125 * 60 + height / 2)

                else:
                    track.setPos(-0.625 * 60 + width / 2, -4.125 * 60 + height / 2)

        super().dataChanged()


class SpriteImage_BuzzyBeetle(SLib.SpriteImage_StaticMultiple):  # 22
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
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
        self.yOffset = -4 if type_ == 1 else 0
        super().dataChanged()


class SpriteImage_Spiny(SLib.SpriteImage_StaticMultiple):  # 23
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Spiny', 'spiny.png')
        SLib.loadIfNotInImageCache('SpinyBall', 'spiny_ball.png')
        SLib.loadIfNotInImageCache('SpinyShell', 'spiny_shell.png')
        SLib.loadIfNotInImageCache('SpinyShellU', 'spiny_shell_u.png')

    def dataChanged(self):
        spawntype = self.parent.spritedata[5]

        if spawntype == 1:
            self.image = ImageCache['SpinyBall']
            self.xOffset = 0
            self.yOffset = 4
        elif spawntype == 2:
            self.image = ImageCache['SpinyShell']
            self.xOffset = -4
            self.yOffset = -4
        elif spawntype == 3:
            self.image = ImageCache['SpinyShellU']
            self.xOffset = -4
            self.yOffset = 0
        else:
            self.image = ImageCache['Spiny']
            self.xOffset = -4
            self.yOffset = -4

        super().dataChanged()


class SpriteImage_SpinyU(SLib.SpriteImage_Static):  # 24
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['SpinyU'],
            (-4, 0),
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
            (0, -40),
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


class SpriteImage_Flagpole(SLib.SpriteImage_StaticMultiple):  # 31, 503, 630, 631
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

        self.aux.append(SLib.AuxiliaryImage(parent, 390, 375))
        self.aux[1].setImage(ImageCache['Chest'], 488, 132, True)
        self.aux[1].alpha = 0.5

        self.aux.append(SLib.AuxiliaryImage(parent, 390, 375))
        self.aux[2].setImage(ImageCache['ToadL'], 540, 128, True)
        self.aux[2].alpha = 0.5

        self.painted = self.parent.type in (503, 631)
        self.dataChanged()

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FlagPole', 'flag_pole.png')
        SLib.loadIfNotInImageCache('FlagPolePaint', 'flag_pole_paint.png')
        SLib.loadIfNotInImageCache('FlagPoleSecret', 'flag_pole_secret.png')
        SLib.loadIfNotInImageCache('FlagPoleSecretPaint', 'flag_pole_secret_paint.png')
        SLib.loadIfNotInImageCache('Castle', 'castle.png')
        SLib.loadIfNotInImageCache('CastlePaint', 'castle_paint.png')
        SLib.loadIfNotInImageCache('CastleSnow', 'castle_snow.png')
        SLib.loadIfNotInImageCache('CastleSecret', 'castle_secret.png')
        SLib.loadIfNotInImageCache('CastleSecretPaint', 'castle_secret_paint.png')
        SLib.loadIfNotInImageCache('CastleSecretSnow', 'castle_secret_snow.png')

        SLib.loadIfNotInImageCache('Chest', 'chest.png')
        SLib.loadIfNotInImageCache('ToadL', 'toad.png')

    def dataChanged(self):
        super().dataChanged()

        secret = (self.parent.spritedata[2] & 0x10) != 0
        castle = (self.parent.spritedata[5] & 0x10) == 0
        snow =   (self.parent.spritedata[5] & 1)    != 0

        if secret:
            self.image = ImageCache['FlagPoleSecret' + ('Paint' if self.painted else '')]
            
            if snow and not self.painted:
                self.aux[0].image = ImageCache['CastleSecretSnow']
            else:
                self.aux[0].image = ImageCache['CastleSecret' + ('Paint' if self.painted else '')]
        else:
            self.image = ImageCache['FlagPole' + ('Paint' if self.painted else '')]
            
            if snow and not self.painted:
                self.aux[0].image = ImageCache['CastleSnow']
            else:
                self.aux[0].image = ImageCache['Castle' + ('Paint' if self.painted else '')]

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


class SpriteImage_Grrrol(SLib.SpriteImage_Static):  # 33, 58, 504
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


class SpriteImage_EventController(SLib.SpriteImage):  # X
    font = QtGui.QFont(globals.NumberFont)
    font.setPixelSize((9 / 24) * globals.TileWidth)
    font.setBold(True)
    
    def __init__(self, parent, text):
        super().__init__(
            parent,
            3.75,
        )

        self.text = text
        self.spritebox.shown = False

    def paint(self, painter):
        super().paint(painter)

        rect = self.spritebox.RoundedRect

        oldB = painter.brush()
        oldP = painter.pen()

        if self.parent.isSelected():
            painter.setPen(QtGui.QPen(QtGui.QColor(255, 255, 255), 1 / 24 * globals.TileWidth))
        else:
            painter.setPen(QtGui.QPen(QtGui.QColor(0, 0, 0), 1 / 24 * globals.TileWidth))

        painter.setBrush(QtGui.QBrush(QtGui.QColor(230, 115, 0)))
        painter.drawRoundedRect(rect, 4, 4)
        painter.setFont(SpriteImage_EventController.font)
        painter.drawText(rect, Qt.AlignCenter, self.text)

        painter.setBrush(oldB)
        painter.setPen(oldP)
        

class SpriteImage_EventControllerZone(SpriteImage_EventController):  # 36
    def __init__(self, parent):
        super().__init__(parent, 'Event\nZONE')


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


class SpriteImage_EventControllerMultiChainer(SpriteImage_EventController):  # 42
    def __init__(self, parent):
        super().__init__(parent, 'Event\nCHNR')


class SpriteImage_EventControllerTimer(SpriteImage_EventController):  # 43
    def __init__(self, parent):
        super().__init__(parent, 'Event\nTMR')


class SpriteImage_CoinRing(SLib.SpriteImage_Static):  # 44, 402, 470, 662
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.parent.setZValue(200000)

        if self.parent.type == 402:
            self.image = ImageCache['GreenRing']

        elif self.parent.type == 662:
            self.image = ImageCache['BlueRing']

        else:
            self.image = ImageCache['RedRing']

        self.yOffset = -12

    @staticmethod
    def loadImages():
        if 'RedRing' in ImageCache: return
        for C, c in (('Red', 'red'), ('Green', 'green'), ('Blue', 'blue')):
            SLib.loadIfNotInImageCache('%sRing' % C, '%s_ring.png' % c)

    def dataChanged(self):
        self.xOffset = -12
        if self.parent.spritedata[5] & 1:
            self.xOffset += 8

        super().dataChanged()


class SpriteImage_StarCoin(SLib.SpriteImage_Static):  # 45, 47, 480
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
            ImageCache['StarCoin'],
            (-16, -12),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StarCoin', 'star_coin.png')

class SpriteImage_MovementStarCoin(SLib.SpriteImage_MovementControlled):  # 48
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.previousType = 0

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StarCoin', 'star_coin.png')

    def getMovementType(self):
        return self.parent.spritedata[9] >> 4 & 3

    def allowedMovementControllers(self):
        if self.getMovementType() == 0:
            return 68, 116, 69, 118

        return tuple()

    def dataChanged(self):
        type = self.getMovementType()
        if type != self.previousType:
            self.previousType = type
            self.unhookController()

        if type == 0:
            self.offset = (-16, -8)

        else:
            self.offset = (0, 0)

        self.image = ImageCache['StarCoin']

        super().dataChanged()


class SpriteImage_PivotCoinBase(SLib.SpriteImage_PivotRotationControlled):  # X
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.affectedByIdZero = False

    def updateImage(self, old_image):
        upsideDown = (self.parent.spritedata[2] & 1) != 0
        gyro = (self.parent.spritedata[2] & 2) != 0
        tilt = (self.parent.spritedata[2] & 4) != 0

        if tilt and not gyro and self.controller:
            pivotX, pivotY = self.controller.getPivot()
            imageAngle = math.degrees(math.atan2(pivotY - (self.parent.objy + 8), pivotX - (self.parent.objx + 8))) - 90

            if upsideDown:
                imageAngle += 180

            self.image = old_image.transformed(QTransform().rotate(imageAngle))
            self.xOffset = (old_image.width() - self.image.width()) / (2 * self.scale)
            self.yOffset = (old_image.height() - self.image.height()) / (2 * self.scale)
            self.affectImage = True
        else:
            self.image = old_image
            self.xOffset = 0
            self.yOffset = 0
            self.affectImage = not gyro


class SpriteImage_RedCoin(SpriteImage_PivotCoinBase):  # 49
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.previousType = 0

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RedCoin', 'red_coin.png')

    def getMovementType(self):
        return self.parent.spritedata[9] >> 4

    def allowedMovementControllers(self):
        if self.getMovementType() == 1:
            return 68, 116, 69, 118

        return tuple()

    def dataChanged(self):
        type = self.getMovementType()
        if type != self.previousType:
            self.previousType = type
            self.unhookController()

        self.updateImage(ImageCache['RedCoin'])
        super().dataChanged()


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
        self.aux.append(SLib.AuxiliaryTrackObject(
            parent, 16, 16, SLib.AuxiliaryTrackObject.Horizontal
        ))

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FishBoneR', 'fish_bone.png')

        if 'FishBoneL' not in ImageCache:
            ImageCache['FishBoneL'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('fish_bone.png', True).mirrored(True, False))

    def dataChanged(self):
        direction = (self.parent.spritedata[5] >> 4) & 1
        distance = self.parent.spritedata[5] & 0xF
        if distance == 0:
            distance = 5
        elif distance == 1:
            distance = 7
        else:
            distance = 9

        self.aux[0].setSize(distance * 16, 16)

        if direction == 1:
            self.image = ImageCache['FishBoneL']
            self.xOffset = -8
            self.aux[0].setPos(distance * -30 + 60, 15)

        else:
            self.image = ImageCache['FishBoneR']
            self.xOffset = -4
            self.aux[0].setPos(distance * -30 + 45, 15)

        super().dataChanged()


class SpriteImage_QBlock(SLib.SpriteImage_StaticMultiple):  # 59
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


class SpriteImage_BrickBlock(SLib.SpriteImage_StaticMultiple):  # 60
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


class SpriteImage_InvisiBlock(SLib.SpriteImage_StaticMultiple):  # 61
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


class SpriteImage_PivotPipePiranhaUp(SLib.SpriteImage_PivotRotationControlled):  # 62
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


class SpriteImage_StalkingPiranha(SLib.SpriteImage_Static):  # 63
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['StalkingPiranha'],
            (-4, -24),
        )

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setImage(ImageCache['StalkingPiranhaExt'], 0, -26, True)
        self.aux[0].alpha = 0.5

        self.aux.append(SLib.AuxiliaryTrackObject(
            parent, 16, 16, SLib.AuxiliaryTrackObject.Horizontal
        ))

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StalkingPiranha', 'stalking_piranha.png')
        SLib.loadIfNotInImageCache('StalkingPiranhaExt', 'stalking_piranha_extending.png')

    def dataChanged(self):
        distance = (self.parent.spritedata[5] & 0xF) * 2 + 3

        self.aux[1].setSize(distance * 16, 16)
        self.aux[1].setPos(distance * -30 + 45, 90)


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


class SpriteImage_Swooper(SLib.SpriteImage_StaticMultiple):  # 67
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Swooper', 'swooper.png')
        SLib.loadIfNotInImageCache('SwooperFlying', 'swooper_flying.png')

    def dataChanged(self):
        self.image = ImageCache['SwooperFlying' if self.parent.initialState == 1 else 'Swooper']

        super().dataChanged()


class SpriteImage_ControllerSwaying(SLib.SpriteImage_MovementController):  # 68, 116
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerSwaying'],
        )

        self.aux.append(SLib.AuxiliaryRotationAreaOutline(parent, 60))
        self.aux.append(SLib.AuxiliaryRotationAreaOutline(parent, 120))

        self.rotation = 0
        self.startOffset = 0
        self.arc = 0
        self.eventActivated = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerSwaying', 'controller_swaying.png')

    def dataChanged(self):
        self.startOffset = (self.parent.spritedata[2] & 0xF) * 22.5 + 90
        self.eventActivated = (self.parent.spritedata[4] & 0x40) != 0
        reversedDir = ((self.parent.spritedata[4] >> 4) & 1) != 0
        self.arcMiddleRotation = (self.parent.spritedata[4] & 0xF) * 22.5
        self.delay = self.parent.spritedata[6] & 0xF0
        self.arc = (self.parent.spritedata[7] >> 4) * 22.5
        self.rotationSpeed = ((self.parent.spritedata[7] & 0xF) / 0x800) * 360

        if reversedDir:
            self.startOffset += 180
        
        self.rotation = math.cos(math.radians(self.startOffset))
            
        self.aux[0].SetAngle(90 + self.arcMiddleRotation - self.arc * 0.5, self.arc)
        self.aux[1].SetAngle(90 + self.arcMiddleRotation - self.rotation * self.arc * 0.5, 0)

        super().dataChanged()

    def active(self):
        return not self.eventActivated

    def getStartRotation(self):
        if not self.eventActivated:
            self.rotation = math.cos(math.radians(self.startOffset - SLib.RotationFrame * self.rotationSpeed * (60 / SLib.RotationFPS)))

        return -self.arcMiddleRotation + self.rotation * self.arc * 0.5


class SpriteImage_ControllerSpinning(SLib.SpriteImage_MovementController):  # 69, 118
    Speeds = [0x400000, 0x800000, 0xc00000, 0x1000000, 0x200000, 0x2000000, 0x4000000, 0x100000]

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['ControllerSpinning'],
        )
        self.aux.append(SLib.AuxiliaryRotationAreaOutline(parent, 60))
        self.aux.append(SLib.AuxiliaryRotationAreaOutline(parent, 120))

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ControllerSpinning', 'controller_spinning.png')

    def dataChanged(self):
        self.rotation = (self.parent.spritedata[2] >> 4) * 22.5
        arc = (self.parent.spritedata[2] & 0xF) * 22.5
        self.spinMode = self.parent.spritedata[3] & 3
        reversedDir = ((self.parent.spritedata[4] >> 4) & 1) != 0
        speedValue = self.parent.spritedata[7] & 0xF

        if speedValue > 7:
            speedValue = 4

        self.rotationSpeed = (SpriteImage_ControllerSpinning.Speeds[speedValue] / 0x100000000) * 360

        if reversedDir:
            self.rotation = -self.rotation
            self.rotationSpeed = -self.rotationSpeed

        if self.spinMode == 1:
            arc = 360

        self.aux[0].SetAngle(90 + self.rotation - (arc if reversedDir else 0), arc)
        self.aux[1].SetAngle(90 + self.rotation, 0)
        self.parent.updateScene()
        super().dataChanged()

    def active(self):
        return self.spinMode == 1

    def getStartRotation(self):
        if self.spinMode == 1:
            return -self.rotation - SLib.RotationFrame * self.rotationSpeed * (60 / SLib.RotationFPS)
        else:
            return -self.rotation
        

class SpriteImage_TwoWay(SLib.SpriteImage_StaticMultiple):  # 70, 642
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TwoWay0', 'twoway_hor.png')
        SLib.loadIfNotInImageCache('TwoWay1', 'twoway_ver.png')

    def dataChanged(self):
        self.image = ImageCache['TwoWay%d' % ((self.parent.spritedata[3] & 3) // 2)]
        super().dataChanged()


class SpriteImage_MovingIronBlock(SLib.SpriteImage):  # 71, 80, 430
    def __init__(self, parent, rotatable=True):
        super().__init__(parent, 3.75)

        self.rotatable = rotatable
        self.hasTrack = self.parent.type == 80
        if self.hasTrack:
            self.aux.append(SLib.AuxiliaryTrackObject(parent, 0, 0, 0))
            self.aux[0].setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

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

    def setWidth(self):
        self.width = (self.parent.spritedata[8] & 0xF) * 16 + 16
        self.height = (self.parent.spritedata[9] & 0xF) * 16 + 16

        if self.width < 32:
            self.width = 32

        if self.height < 32:
            self.height = 32

    def dataChanged(self):
        self.setWidth()

        pix = QtGui.QPixmap(self.width * 3.75, self.height * 3.75)
        pix.fill(Qt.transparent)
        painter = QtGui.QPainter(pix)

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

        painter = None
        
        if not self.rotatable:
            self.transformed = pix
            self.imgxOffset = 0
            self.imgyOffset = 0

        else:
            rotation = (self.parent.spritedata[3] >> 4) * 22.5
            self.transformed = pix.transformed(QTransform().rotate(-rotation))
            
            oldxOffset = (pix.width() - self.transformed.width()) / 7.5
            oldyOffset = (pix.height() - self.transformed.height()) / 7.5
            self.xOffset = math.floor(oldxOffset / 4) * 4
            self.yOffset = math.floor(oldyOffset / 4) * 4

            self.imgxOffset = (oldxOffset - self.xOffset)
            self.imgyOffset = (oldyOffset - self.yOffset)
            self.width = self.transformed.width() / 3.75 + self.imgxOffset
            self.height = self.transformed.height() / 3.75 + self.imgyOffset

        if self.hasTrack:
            track = self.aux[0]

            distance = (self.parent.spritedata[7] >> 4) + 1
            if distance == 1:
                track.setSize(0, 0)

            direction = self.parent.spritedata[2] & 3
            xOffset = -self.xOffset * 3.75
            yOffset = -self.yOffset * 3.75

            if direction & 2:
                track.direction = SLib.AuxiliaryTrackObject.Vertical
                if distance != 1:
                    track.setSize(16, distance * 16)

            else:
                track.direction = SLib.AuxiliaryTrackObject.Horizontal
                if distance != 1:
                    track.setSize(distance * 16, 16)

            if direction == 1:
                xOffset += (-distance + 1) * 60

            elif direction == 2:
                yOffset += (-distance + 1) * 60

            track.setPos(xOffset, yOffset)

        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(self.imgxOffset * 3.75, self.imgyOffset * 3.75, self.transformed)


class SpriteImage_MovingLandBlock(SLib.SpriteImage):  # 72, 81
    def __init__(self, parent):
        super().__init__(parent, 3.75)

        self.hasTrack = self.parent.type == 81
        if self.hasTrack:
            self.aux.append(SLib.AuxiliaryTrackObject(parent, 0, 0, 0))
            self.aux[0].setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

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
        self.width = (self.parent.spritedata[8] & 0xF) * 16 + 16
        self.height = (self.parent.spritedata[9] & 0xF) * 16 + 16

        if self.width < 32:
            self.width = 32

        if self.height < 32:
            self.height = 32

        pix = QtGui.QPixmap(self.width * 3.75, self.height * 3.75)
        pix.fill(Qt.transparent)
        painter = QtGui.QPainter(pix)

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

        painter = None
        rotation = (self.parent.spritedata[3] >> 4) * 22.5
        self.transformed = pix.transformed(QTransform().rotate(-rotation))
        
        oldxOffset = (pix.width() - self.transformed.width()) / 7.5
        oldyOffset = (pix.height() - self.transformed.height()) / 7.5
        self.xOffset = math.floor(oldxOffset / 4) * 4
        self.yOffset = math.floor(oldyOffset / 4) * 4

        self.imgxOffset = (oldxOffset - self.xOffset)
        self.imgyOffset = (oldyOffset - self.yOffset)
        self.width = self.transformed.width() / 3.75 + self.imgxOffset
        self.height = self.transformed.height() / 3.75 + self.imgyOffset

        if self.hasTrack:
            track = self.aux[0]

            distance = (self.parent.spritedata[7] >> 4) + 1
            if distance == 1:
                track.setSize(0, 0)

            direction = self.parent.spritedata[2] & 3
            xOffset = -self.xOffset * 3.75
            yOffset = -self.yOffset * 3.75

            if direction & 2:
                track.direction = SLib.AuxiliaryTrackObject.Vertical
                if distance != 1:
                    track.setSize(16, distance * 16)

            else:
                track.direction = SLib.AuxiliaryTrackObject.Horizontal
                if distance != 1:
                    track.setSize(distance * 16, 16)

            if direction == 1:
                xOffset += (-distance + 1) * 60

            elif direction == 2:
                yOffset += (-distance + 1) * 60

            track.setPos(xOffset, yOffset)

        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(self.imgxOffset * 3.75, self.imgyOffset * 3.75, self.transformed)


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
            (-8, -24),
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
            (-8, -24),
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
            (-16, -28),
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
            (-8, -24),
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
            (-8, -24),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BroFire', 'bro_fire.png')


class SpriteImage_PivotPipePiranhaDown(SLib.SpriteImage_PivotRotationControlled):  # 82
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


class SpriteImage_PivotPipePiranhaLeft(SLib.SpriteImage_PivotRotationControlled):  # 83
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


class SpriteImage_PivotPipePiranhaRight(SLib.SpriteImage_PivotRotationControlled):  # 84
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
            (-4, -4),
        )
        self.aux.append(SLib.AuxiliaryTrackObject(parent, 0, 0, 0))

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Urchin', 'urchin.png')
        
    def dataChanged(self):
        behavior = self.parent.spritedata[4] >> 4
        dirType = self.parent.spritedata[5] & 0xF
        distance = self.parent.spritedata[5] >> 4

        if distance > 0:
            distance = (distance + 1) * 2 + 1

        if dirType == 1:
            self.aux[0].direction = SLib.AuxiliaryTrackObject.Horizontal
            self.aux[0].setSize(distance * 16, 16)
            self.aux[0].setPos(-distance * 30 + self.width * 1.875, self.height * 1.875 - 30)
        elif dirType != 2 or (dirType == 2 and behavior == 0):
            self.aux[0].direction = SLib.AuxiliaryTrackObject.Vertical
            self.aux[0].setSize(16, distance * 16)
            self.aux[0].setPos(self.width * 1.875 - 30, -distance * 30 + self.height * 1.875)
        else:
            self.aux[0].setSize(0, 0)
        
        super().dataChanged()


class SpriteImage_PivotCoin(SpriteImage_PivotCoinBase):  # 87
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.parent.setZValue(20000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovCoin', 'mov_coin.png')

    def dataChanged(self):
        self.updateImage(ImageCache['MovCoin'])
        super().dataChanged()


class SpriteImage_Water(SpriteImage_LiquidOrFog):  # 88
    def __init__(self, parent):
        super().__init__(parent)

        self.crest = ImageCache['LiquidWaterCrest']
        self.mid = ImageCache['LiquidWater']
        self.rise = ImageCache['LiquidWaterRiseCrest']
        self.riseCrestless = ImageCache['LiquidWaterRise']

        self.top = self.parent.objy

    @staticmethod
    def loadImages():
        if 'LiquidWater' in ImageCache: return
        ImageCache['LiquidWater'] = SLib.GetImg('liquid_water.png')
        ImageCache['LiquidWaterCrest'] = SLib.GetImg('liquid_water_crest.png')
        ImageCache['LiquidWaterRise'] = SLib.GetImg('liquid_water_rise.png')
        ImageCache['LiquidWaterRiseCrest'] = SLib.GetImg('liquid_water_rise_crest.png')

    def dataChanged(self):
        self.locId = self.parent.spritedata[5]
        self.drawCrest = self.parent.spritedata[4] & 8 == 0

        self.risingHeight = (self.parent.spritedata[3] & 0xF) << 4
        self.risingHeight |= self.parent.spritedata[4] >> 4
        if self.parent.spritedata[2] & 15 > 7:  # falling
            self.risingHeight = -self.risingHeight

        super().dataChanged()

    def positionChanged(self):
        self.top = self.parent.objy
        super().positionChanged()


class SpriteImage_Lava(SpriteImage_LiquidOrFog):  # 89
    def __init__(self, parent):
        super().__init__(parent)

        self.crest = ImageCache['LiquidLavaCrest']
        self.mid = ImageCache['LiquidLava']
        self.rise = ImageCache['LiquidLavaRiseCrest']
        self.riseCrestless = ImageCache['LiquidLavaRise']

        self.top = self.parent.objy

    @staticmethod
    def loadImages():
        if 'LiquidLava' in ImageCache: return
        ImageCache['LiquidLava'] = SLib.GetImg('liquid_lava.png')
        ImageCache['LiquidLavaCrest'] = SLib.GetImg('liquid_lava_crest.png')
        ImageCache['LiquidLavaRise'] = SLib.GetImg('liquid_lava_rise.png')
        ImageCache['LiquidLavaRiseCrest'] = SLib.GetImg('liquid_lava_rise_crest.png')

    def dataChanged(self):
        self.locId = self.parent.spritedata[5]
        self.drawCrest = self.parent.spritedata[4] & 8 == 0

        self.risingHeight = (self.parent.spritedata[3] & 0xF) << 4
        self.risingHeight |= self.parent.spritedata[4] >> 4
        if self.parent.spritedata[2] & 15 > 7:  # falling
            self.risingHeight = -self.risingHeight

        super().dataChanged()

    def positionChanged(self):
        self.top = self.parent.objy
        super().positionChanged()


class SpriteImage_Poison(SpriteImage_LiquidOrFog):  # 90
    def __init__(self, parent):
        super().__init__(parent)

        self.crest = ImageCache['LiquidPoisonCrest']
        self.mid = ImageCache['LiquidPoison']
        self.rise = ImageCache['LiquidPoisonRiseCrest']
        self.riseCrestless = ImageCache['LiquidPoisonRise']

        self.top = self.parent.objy

    @staticmethod
    def loadImages():
        if 'LiquidPoison' in ImageCache: return
        ImageCache['LiquidPoison'] = SLib.GetImg('liquid_poison.png')
        ImageCache['LiquidPoisonCrest'] = SLib.GetImg('liquid_poison_crest.png')
        ImageCache['LiquidPoisonRise'] = SLib.GetImg('liquid_poison_rise.png')
        ImageCache['LiquidPoisonRiseCrest'] = SLib.GetImg('liquid_poison_rise_crest.png')

    def dataChanged(self):
        self.locId = self.parent.spritedata[5]
        self.drawCrest = self.parent.spritedata[4] & 8 == 0

        self.risingHeight = (self.parent.spritedata[3] & 0xF) << 4
        self.risingHeight |= self.parent.spritedata[4] >> 4
        if self.parent.spritedata[2] & 15 > 7:  # falling
            self.risingHeight = -self.risingHeight

        super().dataChanged()

    def positionChanged(self):
        self.top = self.parent.objy
        super().positionChanged()


class SpriteImage_Quicksand(SpriteImage_LiquidOrFog):  # 91
    def __init__(self, parent):
        super().__init__(parent)

        self.crest = ImageCache['LiquidSandCrest']
        self.mid = ImageCache['LiquidSand']

        self.top = self.parent.objy

    @staticmethod
    def loadImages():
        if 'LiquidSand' in ImageCache: return
        ImageCache['LiquidSand'] = SLib.GetImg('liquid_sand.png')
        ImageCache['LiquidSandCrest'] = SLib.GetImg('liquid_sand_crest.png')

    def dataChanged(self):
        self.locId = self.parent.spritedata[5]
        self.drawCrest = self.parent.spritedata[4] & 8 == 0

        super().dataChanged()

    def positionChanged(self):
        self.top = self.parent.objy
        super().positionChanged()


class SpriteImage_Fog(SpriteImage_LiquidOrFog):  # 92
    def __init__(self, parent):
        super().__init__(parent)
        self.mid = ImageCache['Fog']
        self.top = self.parent.objy

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Fog', 'fog.png')

    def dataChanged(self):
        self.locId = self.parent.spritedata[5]
        super().dataChanged()

    def positionChanged(self):
        self.top = self.parent.objy
        super().positionChanged()


class SpriteImage_GhostFog(SpriteImage_LiquidOrFog):  # 93
    def __init__(self, parent):
        super().__init__(parent)
        self.mid = ImageCache['GhostFog']
        self.top = self.parent.objy

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GhostFog', 'fog_ghost.png')

    def dataChanged(self):
        self.locId = self.parent.spritedata[5]
        super().dataChanged()

    def positionChanged(self):
        self.top = self.parent.objy
        super().positionChanged()


class SpriteImage_BouncyCloud(SLib.SpriteImage_StaticMultiple):  # 94
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -4
        self.aux.append(SLib.AuxiliaryTrackObject(parent, 0, 0, 0))
        self.aux[0].setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BouncyCloudS', 'bouncy_cloud_small.png')
        SLib.loadIfNotInImageCache('BouncyCloudL', 'bouncy_cloud_large.png')

    def dataChanged(self):
        track = self.aux[0]

        distance = (self.parent.spritedata[7] >> 4) + 1
        if distance == 1:
            track.setSize(0, 0)

        direction = self.parent.spritedata[2] & 3
        xOffset = 0
        yOffset = 0

        if direction & 2:
            track.direction = SLib.AuxiliaryTrackObject.Vertical
            if distance != 1:
                track.setSize(16, distance * 16)

        else:
            track.direction = SLib.AuxiliaryTrackObject.Horizontal
            if distance != 1:
                track.setSize(distance * 16, 16)

        if direction == 1:
            xOffset = (-distance + 1) * 60

        elif direction == 2:
            yOffset = (-distance + 1) * 60

        size = self.parent.spritedata[8] & 0xF
        if size == 1:
            self.image = ImageCache['BouncyCloudL']
            self.yOffset = -8
            if direction & 2:
                xOffset += 3.5 * 60
            track.setPos(15 + xOffset, 30 + yOffset)

        else:
            self.image = ImageCache['BouncyCloudS']
            self.yOffset = -4
            if direction & 2:
                xOffset += 1.5 * 60
            track.setPos(15 + xOffset, 15 + yOffset)

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


class SpriteImage_Lamp(SLib.SpriteImage_PivotRotationControlled):  # 96
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.aux.append(SLib.AuxiliaryImage(parent, 1, 1))

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Lamp', 'light_lamp.png')
        SLib.loadIfNotInImageCache('Candle', 'light_candle.png')

    def dataChanged(self):
        if self.parent.spritedata[5] & 1:
            self.dimensions = (-8, 0, 32, 32)
            self.aux[0].setImage(ImageCache['Candle'], -105 + 30, -105)

        else:
            self.dimensions = (-4, -4, 24, 24)
            self.aux[0].setImage(ImageCache['Lamp'], -120, -120)

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
        direction = self.parent.spritedata[5] & 3

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

        self.pieces = (self.parent.spritedata[3] & 7) + 1
        
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


class SpriteImage_Pendulum(SLib.SpriteImage_PivotRotationControlled):  # 117, 693
    offsets = (
        (-12,  -4), (-16,  -4),
        (-16,  -4), (-16,  -4),
        (-20,  -4), (-20,  -8),
        (-24,  -8), (-24,  -8),
        (-28,  -8), (-32,  -8),
        (-32,  -8), (-36, -12),
        (-36, -12), (-40, -12),
        (-40, -12), (-44, -12),
    )

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.spritebox.shown = True
        self.aux.append(SLib.AuxiliaryImage(parent, 1, 1))

    @staticmethod
    def loadImages():
        for i in range(16):
            SLib.loadIfNotInImageCache('Pendulum%d' % i, 'pendulum_%d.png' % i)

    def dataChanged(self):
        size = self.parent.spritedata[4] & 0xF

        self.aux[0].setImage(ImageCache['Pendulum%d' % size], *SpriteImage_Pendulum.offsets[size], True)
        self.aux[0].alpha = 0.5

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


class SpriteImage_BulletBill(SLib.SpriteImage_StaticMultiple):  # 125, 127
    offsets = (
        ( 0, 8),
        (-8, 8),
        ( 0, 8),
        ( 0, 0),
        (-4, 4),
        (-4, 4),
        (-4, 4),
        (-4, 4),
    )

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        for i in range(8):
            SLib.loadIfNotInImageCache('BulletBill%d' % i, 'bullet_bill_%d.png' % i)

        for i in range(2):
            SLib.loadIfNotInImageCache('HomingBulletBill%d' % i, 'homing_bullet_bill_%d.png' % i)

    def getType(self):
        if self.parent.type == 125:
            return 0

        return 1

    def getDirection(self, type):
        if type == 0:
            direction = self.parent.spritedata[5] & 0xF
            if direction == 11:
                direction = self.parent.spritedata[5] >> 4
                if direction > 1:
                    direction = 0

            elif direction > 7:
                direction = 0

        else:
            direction = self.parent.spritedata[5] >> 4
            if direction > 1:
                direction = 0

        return direction

    def dataChanged(self):
        type = self.getType()
        direction = self.getDirection(type)

        self.image = ImageCache[('BulletBill%d' % direction) if type == 0 else ('HomingBulletBill%d' % direction)]
        self.offset = self.offsets[direction]

        super().dataChanged()


class SpriteImage_BanzaiBill(SLib.SpriteImage_StaticMultiple):  # 126
    offsets = (
        (-36, -16),
        (-40, -16),
        (-24, -28),
        (-24, -32),
        (-32, -36),
        (-44, -36),
        (-44, -24),
        (-32, -24),
    )

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        for i in range(8):
            SLib.loadIfNotInImageCache('BanzaiBill%d' % i, 'banzai_bill_%d.png' % i)

    def getDirection(self):
        direction = self.parent.spritedata[5] & 0xF
        if direction == 11:
            direction = self.parent.spritedata[5] >> 4
            if direction > 1:
                direction = 0

        elif direction > 7:
            direction = 0

        return direction

    def dataChanged(self):
        direction = self.getDirection()

        self.image = ImageCache['BanzaiBill%d' % direction]
        self.offset = self.offsets[direction]

        super().dataChanged()


class SpriteImage_HomingBanzaiBill(SLib.SpriteImage_Static):  # 128, 416
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['HomingBanzaiBill'],
            (-40, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('HomingBanzaiBill', 'homing_banzai_bill.png')


class SpriteImage_JumpingCheepCheep(SLib.SpriteImage_StaticMultiple):  # 129
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.yOffset = 4

    @staticmethod
    def loadImages():
        for i in range(2):
            SLib.loadIfNotInImageCache('JumpingCheepCheep%d' % i, 'jumping_cheep_cheep_%d.png' % i)

    def dataChanged(self):
        direction = self.parent.spritedata[2] >> 4 & 1
        self.image = ImageCache['JumpingCheepCheep%d' % direction]
        self.xOffset = 0 if direction == 1 else -4

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
            (-8, -4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Thwomp', 'thwomp.png')


class SpriteImage_GiantThwomp(SLib.SpriteImage_Static):  # 136
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['GiantThwomp'],
            (-12, -4),
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
            ImageCache['DryBonesBig'],
            (-16, -28),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('DryBonesBig', 'dry_bones_big.png')


class SpriteImage_PipeUp(SpriteImage_Pipe):  # 139, 404, 577
    def dataChanged(self):
        if self.parent.type == 577:
            self.hasTop = (self.parent.spritedata[2] >> 4) > 0
        else:
            self.hasTop = (self.parent.spritedata[2] >> 4 & 2) != 2

        self.middleY = 0

        type = self.parent.spritedata[3] & 0xF
        if type > 2:
            type = 0

        if type != 2:
            self.type = 'Painted' if type == 1 else 'Normal'
            self.width, self.pipeWidth = 32, 120
            self.xOffset = 0
            self.color = SpriteImage_Pipe.types[self.type][(self.parent.spritedata[5] >> 4 & 3) + 1][0]

        else:
            self.type = 'Big'
            self.width, self.pipeWidth = 64, 240
            self.xOffset = -16
            self.color = 'Green'

        length = (self.parent.spritedata[5] & 0xF) + 1
        self.height, self.pipeHeight = length * 16, length * 60

        if self.hasTop:
            self.height += 16 if type != 2 else 32
            self.middleY += 60 if type != 2 else 120

        self.yOffset = -self.height + 16

        super().dataChanged()


class SpriteImage_PipeDown(SpriteImage_Pipe):  # 140, 511, 578
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 1

    def dataChanged(self):
        self.yOffset = 0
        if self.parent.type == 578:
            self.hasTop = (self.parent.spritedata[2] >> 4) > 0
        else:
            self.hasTop = (self.parent.spritedata[2] >> 4 & 2) != 2

        type = self.parent.spritedata[3] & 0xF
        if type > 2:
            type = 0

        if type != 2:
            self.type = 'Painted' if type == 1 else 'Normal'
            self.width, self.pipeWidth = 32, 120
            self.xOffset = 0
            self.color = SpriteImage_Pipe.types[self.type][(self.parent.spritedata[5] >> 4 & 3) + 1][0]

        else:
            self.type = 'Big'
            self.width, self.pipeWidth = 64, 240
            self.xOffset = -16
            self.color = 'Green'

        length = (self.parent.spritedata[5] & 0xF) + 1
        self.height, self.pipeHeight = length * 16, length * 60

        if self.hasTop:
            self.height += 16 if type != 2 else 32
            self.topY = self.pipeHeight

        super().dataChanged()


class SpriteImage_PipeLeft(SpriteImage_Pipe):  # 141, 510, 575
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 2

    def dataChanged(self):
        if self.parent.type == 575:
            self.hasTop = (self.parent.spritedata[2] >> 4) > 0
        else:
            self.hasTop = (self.parent.spritedata[2] >> 4 & 2) != 2

        self.middleX = 0

        type = self.parent.spritedata[3] & 0xF
        if type > 2:
            type = 0

        if type != 2:
            self.type = 'Painted' if type == 1 else 'Normal'
            self.height, self.pipeHeight = 32, 120
            self.yOffset = 0
            self.color = SpriteImage_Pipe.types[self.type][(self.parent.spritedata[5] >> 4 & 3) + 1][0]

        else:
            self.type = 'Big'
            self.height, self.pipeHeight = 64, 240
            self.yOffset = -16
            self.color = 'Green'

        length = (self.parent.spritedata[5] & 0xF) + 1
        self.width, self.pipeWidth = length * 16, length * 60

        if self.hasTop:
            self.width += 16 if type != 2 else 32
            self.middleX += 60 if type != 2 else 120

        self.xOffset = -self.width + 16

        super().dataChanged()


class SpriteImage_PipeRight(SpriteImage_Pipe):  # 142, 509, 576
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)
        self.direction = 3

    def dataChanged(self):
        self.xOffset = 0
        if self.parent.type == 576:
            self.hasTop = (self.parent.spritedata[2] >> 4) > 0
        else:
            self.hasTop = (self.parent.spritedata[2] >> 4 & 2) != 2

        type = self.parent.spritedata[3] & 0xF
        if type > 2:
            type = 0

        if type != 2:
            self.type = 'Painted' if type == 1 else 'Normal'
            self.height, self.pipeHeight = 32, 120
            self.yOffset = 0
            self.color = SpriteImage_Pipe.types[self.type][(self.parent.spritedata[5] >> 4 & 3) + 1][0]

        else:
            self.type = 'Big'
            self.height, self.pipeHeight = 64, 240
            self.yOffset = -16
            self.color = 'Green'

        length = (self.parent.spritedata[5] & 0xF) + 1
        self.width, self.pipeWidth = length * 16, length * 60

        if self.hasTop:
            self.width += 16 if type != 2 else 32
            self.topX = self.pipeWidth

        super().dataChanged()


class SpriteImage_BabyYoshi(SLib.SpriteImage_Static):  # 143, 224, 243, 365
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.offset = (-4, -8)

        if parent.type in (143, 243):
            self.image = ImageCache['BabyYoshiBubble']

        elif parent.type == 224:
            self.image = ImageCache['BabyYoshiBalloon']

        else:
            self.image = ImageCache['BabyYoshiGlow']

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BabyYoshiBubble', 'baby_yoshi_bubble.png')
        SLib.loadIfNotInImageCache('BabyYoshiBalloon', 'baby_yoshi_balloon.png')
        SLib.loadIfNotInImageCache('BabyYoshiGlow', 'baby_yoshi_glow.png')


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


class SpriteImage_MovementPipe(SpriteImage_Pipe):  # 146, 679
    def getMovementID(self):
        return self.parent.spritedata[10]

    def allowedMovementControllers(self):
        return 68, 116, 69, 118

    def dataChanged(self):
        self.type = 'Painted' if self.parent.spritedata[5] & 0x10 else 'Normal'
        self.color = SpriteImage_Pipe.types[self.type][(self.parent.spritedata[3] & 3) + 1][0]

        length = self.parent.spritedata[4] + 1
        direction = self.parent.spritedata[3] >> 4 & 3

        if direction == 0:
            self.direction = 3
            self.width, self.pipeWidth = (length+1) * 16, length * 60
            self.height, self.pipeHeight = 32, 120
            self.topX = self.pipeWidth
            self.topY = 0
            self.middleX = 0
            self.middleY = 0
            self.xOffset = 0
            self.yOffset = 0

        elif direction == 1:
            self.direction = 2
            self.width, self.pipeWidth = (length+1) * 16, length * 60
            self.height, self.pipeHeight = 32, 120
            self.topX = 0
            self.topY = 0
            self.middleX = 60
            self.middleY = 0
            self.xOffset = -self.width + 16
            self.yOffset = 0

        elif direction == 2:
            self.direction = 0
            self.width, self.pipeWidth = 32, 120
            self.height, self.pipeHeight = (length+1) * 16, length * 60
            self.topX = 0
            self.topY = 0
            self.middleX = 0
            self.middleY = 60
            self.xOffset = 0
            self.yOffset = -self.height + 16

        else:
            self.direction = 1
            self.width, self.pipeWidth = 32, 120
            self.height, self.pipeHeight = (length+1) * 16, length * 60
            self.topX = 0
            self.topY = self.pipeHeight
            self.middleX = 0
            self.middleY = 0
            self.xOffset = 0
            self.yOffset = 0

        super().dataChanged()


class SpriteImage_StoneEye(SLib.SpriteImage_PivotRotationControlled):  # 150, 719
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


class SpriteImage_Spotlight(SLib.SpriteImage_PivotRotationControlled):  # 153
    def __init__(self, parent):
        super().__init__(parent, 3.75)

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))

        self.aux[1].alpha = 0.5
        self.aux[1].gyro = True
        self.aux[1].setImage(ImageCache['SpotlightHolder'], 90, -150)

        self.previousType = 0

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpotlightHolder', 'spotlight_holder.png')
        SLib.loadIfNotInImageCache('SpotlightLamp', 'spotlight_lamp.png')
        SLib.loadIfNotInImageCache('SpotlightScrew', 'spotlight_screw.png')

    def getMovementType(self):
        type = self.parent.spritedata[4] & 3
        if type > 2:
            type = 2

        return type

    def allowedMovementControllers(self):
        if self.getMovementType() == 2:
            return 68, 116, 69, 118

        return tuple()

    def dataChanged(self):
        self.dimensions = (-24, -24, 64, 64)

        type = self.getMovementType()
        if type != self.previousType:
            self.previousType = type
            self.unhookController()

        rotation = (self.parent.spritedata[3] & 0xF) * 22.5

        pix = ImageCache['SpotlightLamp']
        transformed = pix.transformed(QTransform().rotate(rotation))
        
        aux_xOffset = (pix.width() - transformed.width()) / 2
        aux_yOffset = (pix.height() - transformed.height()) / 2

        self.aux[0].setImage(transformed, aux_xOffset, aux_yOffset)

        pix = ImageCache['SpotlightScrew']
        transformed = pix.transformed(QTransform().rotate(rotation))
        
        aux_xOffset = (pix.width() - transformed.width()) / 2
        aux_yOffset = (pix.height() - transformed.height()) / 2

        self.aux[2].setImage(transformed, 90 + aux_xOffset, 90 + aux_yOffset)

        super().dataChanged()


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


class SpriteImage_PipeCannon(SpriteImage_Pipe):  # 155, 667
    aux_offsets = (
        (0, 0),
        (-32, 0),
        (0, -4),
        (-12, -4),
        (-24, -60),
        (0, 0),
        (-36, 0),
    )

    def __init__(self, parent):
        super().__init__(parent, 3.75)

        self.middleY = 60

        # self.aux[0] is the pipe image
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)
        self.aux[0].hover = False

        # self.aux[1] is the trajectory indicator
        self.aux.append(SLib.AuxiliaryPainterPath(parent, QtGui.QPainterPath(), 60, 60))
        self.aux[1].fillFlag = False

        self.aux[0].setZValue(self.aux[1].zValue() + 1)

    @staticmethod
    def loadImages():
        if 'PipeCannon0' in ImageCache:
            return

        SpriteImage_Pipe.loadImages()
        for i in range(7):
            ImageCache['PipeCannon%d' % i] = SLib.GetImg('pipe_cannon_%d.png' % i)

    def dataChanged(self):
        self.xOffset = 0
        self.width, self.pipeWidth = 32, 120

        length = (self.parent.spritedata[4] & 0xF) + 3
        self.height, self.pipeHeight = (length+1) * 16, length * 60
        self.yOffset = -(length-3) * 16

        fireDirection = self.parent.spritedata[5] & 0xF
        if fireDirection > 10:
            fireDirection = 0

        imgDirection = fireDirection
        if fireDirection in (7, 8):
            imgDirection -= 2

        elif fireDirection in (9, 10):
            imgDirection -= 7

        self.aux[0].setImage(ImageCache['PipeCannon%d' % imgDirection], *SpriteImage_PipeCannon.aux_offsets[imgDirection], True)
        self.aux[0].alpha = 1 if fireDirection == 4 else 0.5

        # TODO: CLEAN ME UP

        # 30 deg to the right
        if fireDirection == 0:
            path = QtGui.QPainterPath(QtCore.QPoint(0, 184 * 2.5))
            path.cubicTo(QtCore.QPoint(152 * 2.5, -24 * 2.5), QtCore.QPoint(168 * 2.5, -24 * 2.5),
                         QtCore.QPoint(264 * 2.5, 48 * 2.5))
            path.lineTo(QtCore.QPoint(480 * 2.5, 216 * 2.5))
            self.aux[1].setSize(480 * 2.5, 216 * 2.5, 24 * 2.5, -120 * 2.5 + 30)

        # 30 deg to the left
        elif fireDirection == 1:
            path = QtGui.QPainterPath(QtCore.QPoint(480 * 2.5 - 0, 184 * 2.5))
            path.cubicTo(QtCore.QPoint(480 * 2.5 - 152 * 2.5, -24 * 2.5),
                         QtCore.QPoint(480 * 2.5 - 168 * 2.5, -24 * 2.5),
                         QtCore.QPoint(480 * 2.5 - 264 * 2.5, 48 * 2.5))
            path.lineTo(QtCore.QPoint(480 * 2.5 - 480 * 2.5, 216 * 2.5))
            self.aux[1].setSize(480 * 2.5, 216 * 2.5, -480 * 2.5 + 24 * 2.5, -120 * 2.5 + 30)

        # 15 deg to the right
        elif fireDirection == 2:
            path = QtGui.QPainterPath(QtCore.QPoint(0, 188 * 2.5))
            path.cubicTo(QtCore.QPoint(36 * 2.5, -36 * 2.5), QtCore.QPoint(60 * 2.5, -36 * 2.5),
                         QtCore.QPoint(96 * 2.5, 84 * 2.5))
            path.lineTo(QtCore.QPoint(144 * 2.5, 252 * 2.5))
            self.aux[1].setSize(144 * 2.5, 252 * 2.5, 30 * 2.5 + 15, -156 * 2.5 + 15)

        # 15 deg to the left
        elif fireDirection == 3:
            path = QtGui.QPainterPath(QtCore.QPoint(144 * 2.5 - 0, 188 * 2.5))
            path.cubicTo(QtCore.QPoint(144 * 2.5 - 36 * 2.5, -36 * 2.5), QtCore.QPoint(144 * 2.5 - 60 * 2.5, -36 * 2.5),
                         QtCore.QPoint(144 * 2.5 - 96 * 2.5, 84 * 2.5))
            path.lineTo(QtCore.QPoint(144 * 2.5 - 144 * 2.5, 252 * 2.5))
            self.aux[1].setSize(144 * 2.5, 252 * 2.5, -144 * 2.5 + 30 * 2.5 - 45, -156 * 2.5 + 15)

        # Straight up
        elif fireDirection == 4:
            path = QtGui.QPainterPath(QtCore.QPoint(26 * 2.5, 0))
            path.lineTo(QtCore.QPoint(26 * 2.5, 656 * 2.5))
            self.aux[1].setSize(48 * 2.5, 656 * 2.5, 0, -632 * 2.5)

        # 45 deg to the right
        elif fireDirection == 5:
            path = QtGui.QPainterPath(QtCore.QPoint(0, 320 * 2.5))
            path.lineTo(QtCore.QPoint(264 * 2.5, 64 * 2.5))
            path.cubicTo(QtCore.QPoint(348 * 2.5, -14 * 2.5), QtCore.QPoint(420 * 2.5, -14 * 2.5),
                         QtCore.QPoint(528 * 2.5, 54 * 2.5))
            path.lineTo(QtCore.QPoint(1036 * 2.5, 348 * 2.5 + 60))
            self.aux[1].setSize(1036 * 2.5, 348 * 2.5 + 30, 24 * 2.5, -252 * 2.5 + 30)

        # 45 deg to the left
        elif fireDirection == 6:
            path = QtGui.QPainterPath(QtCore.QPoint(1036 * 2.5 - 0 * 2.5, 320 * 2.5))
            path.lineTo(QtCore.QPoint(1036 * 2.5 - 264 * 2.5, 64 * 2.5))
            path.cubicTo(QtCore.QPoint(1036 * 2.5 - 348 * 2.5, -14 * 2.5),
                         QtCore.QPoint(1036 * 2.5 - 420 * 2.5, -14 * 2.5),
                         QtCore.QPoint(1036 * 2.5 - 528 * 2.5, 54 * 2.5))
            path.lineTo(QtCore.QPoint(1036 * 2.5 - 1036 * 2.5, 348 * 2.5 + 60))
            self.aux[1].setSize(1036 * 2.5, 348 * 2.5 - 60, -1036 * 2.5 + 24 * 2.5, -252 * 2.5 + 30)

        # 45 deg to the right (lower initial velocity)
        elif fireDirection == 7:
            path = QtGui.QPainterPath(QtCore.QPoint(1.5 * 24 * 2.5, 320 * 2.5 - 1.5 * 24 * 2.5))
            path.lineTo(QtCore.QPoint(264 * 2.5, 64 * 2.5))
            path.cubicTo(QtCore.QPoint(348 * 2.5, -14 * 2.5), QtCore.QPoint(420 * 2.5, -14 * 2.5),
                         QtCore.QPoint(528 * 2.5, 54 * 2.5))
            path.lineTo(QtCore.QPoint(1036 * 2.5, 348 * 2.5 + 60))
            self.aux[1].setSize(1036 * 2.5, 348 * 2.5 - 60, 24 * 2.5 - 90, -252 * 2.5 + 30 + 30 + 60)

        # 45 deg to the left (lower initial velocity)
        elif fireDirection == 8:
            path = QtGui.QPainterPath(QtCore.QPoint(1036 * 2.5 - 0 * 2.5 - 1.5 * 24 * 2.5, 320 * 2.5 - 1.5 * 24 * 2.5))
            path.lineTo(QtCore.QPoint(1036 * 2.5 - 264 * 2.5, 64 * 2.5))
            path.cubicTo(QtCore.QPoint(1036 * 2.5 - 348 * 2.5, -14 * 2.5),
                         QtCore.QPoint(1036 * 2.5 - 420 * 2.5, -14 * 2.5),
                         QtCore.QPoint(1036 * 2.5 - 528 * 2.5, 54 * 2.5))
            path.lineTo(QtCore.QPoint(1036 * 2.5 - 1036 * 2.5, 348 * 2.5 + 60))
            self.aux[1].setSize(1036 * 2.5, 348 * 2.5 - 60, -1036 * 2.5 + 24 * 2.5 + 90, -252 * 2.5 + 30 + 30 + 60)

        # 15 deg to the right (higher initial velocity)
        elif fireDirection == 9:
            path = QtGui.QPainterPath(QtCore.QPoint(30, 252 * 2.5 + 5*60))
            path.cubicTo(QtCore.QPoint(36 * 2.5 + 90, -36 * 2.5), QtCore.QPoint(60 * 2.5 + 90, -36 * 2.5), QtCore.QPoint(96 * 2.5 + 90, 84 * 2.5))
            path.lineTo(QtCore.QPoint(144 * 2.5 + 4*60, 252 * 2.5 + 8*60))
            self.aux[1].setSize(144 * 2.5 + 4*60, 252 * 2.5 + 8*60, 30 * 2.5 - 15, -156 * 2.5 - 7.5*60)

        # 15 deg to the left (higher initial velocity)
        else:
            path = QtGui.QPainterPath(QtCore.QPoint(144 * 2.5 - 0 + 4*60, 252 * 2.5 + 5*60))
            path.cubicTo(QtCore.QPoint(144 * 2.5 - 36 * 2.5 + 4*60 - 60, -36 * 2.5), QtCore.QPoint(144 * 2.5 - 60 * 2.5 + 4*60 - 60, -36 * 2.5),
                         QtCore.QPoint(144 * 2.5 - 96 * 2.5 + 4*60 - 60, 84 * 2.5))
            path.lineTo(QtCore.QPoint(144 * 2.5 - 144 * 2.5 + 30, 252 * 2.5 + 8*60))
            self.aux[1].setSize(144 * 2.5 + 4*60, 252 * 2.5 + 8*60, -144 * 2.5 + 30 * 2.5 - 45 - 4*60, -156 * 2.5 - 7.5*60)

        self.aux[1].SetPath(path)

        super().dataChanged()


class SpriteImage_WaterGeyser(SLib.SpriteImage_StaticMultiple):  # 156
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

        painter.drawTiledPixmap(0, 15, self.width * (60/16), self.height * (60/16) - 15, self.middle.scaledToWidth(self.width * (60/16), Qt.SmoothTransformation))
        painter.drawPixmap(0, 0, self.width * (60/16), 180, self.top)


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


class SpriteImage_CoinOutline(SpriteImage_PivotCoinBase):  # 158
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.parent.setZValue(20000)

    def dataChanged(self):
        multi = (self.parent.spritedata[2] >> 4) & 1
        self.updateImage(SLib.Tiles[28 if multi else 31].main)
        super().dataChanged()


class SpriteImage_ExpandingPipeRight(SpriteImage_Pipe):  # 159
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)

        self.direction = 3

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)
        self.aux[0].alpha = 0.5

    def dataChanged(self):
        self.offset = (0, 0)
        self.height, self.pipeHeight = 32, 120

        self.type = 'Painted' if self.parent.spritedata[4] & 1 else 'Normal'
        self.color = SpriteImage_Pipe.types[self.type][(self.parent.spritedata[3] & 3) + 1][0]

        length = (self.parent.spritedata[5] & 0xF) + 1
        self.width, self.pipeWidth = (length+1) * 16, length * 60
        self.topX = self.pipeWidth

        length = (self.parent.spritedata[5] >> 4) + 1

        aux = self.aux[0]
        if aux.image:
            image = aux.image
            del image
            aux.image = None

        pix = QtGui.QPixmap((length+1) * 60, 120)
        pix.fill(Qt.transparent)

        painter = QtGui.QPainter(pix)
        painter.drawTiledPixmap(0, 0, length * 60, 120, ImageCache['PipeHBottomMiddle%s%s' % (self.type, self.color)])
        painter.drawPixmap(length * 60, 0, ImageCache['PipeHBottom%s%s' % (self.type, self.color)])
        painter.end()
        del painter

        aux.setImage(pix, 0, 0)

        super().dataChanged()


class SpriteImage_ExpandingPipeLeft(SpriteImage_Pipe):  # 160
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)

        self.direction = 2
        self.middleX = 60

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)
        self.aux[0].alpha = 0.5

    def dataChanged(self):
        self.yOffset = 0
        self.height, self.pipeHeight = 32, 120

        self.type = 'Painted' if self.parent.spritedata[4] & 1 else 'Normal'
        self.color = SpriteImage_Pipe.types[self.type][(self.parent.spritedata[3] & 3) + 1][0]

        length = (self.parent.spritedata[5] & 0xF) + 1
        self.width, self.pipeWidth = (length+1) * 16, length * 60
        self.xOffset = -self.width + 16

        length = (self.parent.spritedata[5] >> 4) + 1

        aux = self.aux[0]
        if aux.image:
            image = aux.image
            del image
            aux.image = None

        pix = QtGui.QPixmap((length+1) * 60, 120)
        pix.fill(Qt.transparent)

        painter = QtGui.QPainter(pix)
        painter.drawTiledPixmap(60, 0, length * 60, 120, ImageCache['PipeHTopMiddle%s%s' % (self.type, self.color)])
        painter.drawPixmap(0, 0, ImageCache['PipeHTop%s%s' % (self.type, self.color)])
        painter.end()
        del painter

        aux.setImage(pix, self.width - (length+1) * 16, 0, True)

        super().dataChanged()


class SpriteImage_ExpandingPipeUp(SpriteImage_Pipe):  # 161
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)

        self.middleY = 60

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)
        self.aux[0].alpha = 0.5

    def dataChanged(self):
        self.xOffset = 0
        self.width, self.pipeWidth = 32, 120

        self.type = 'Painted' if self.parent.spritedata[4] & 1 else 'Normal'
        self.color = SpriteImage_Pipe.types[self.type][(self.parent.spritedata[3] & 3) + 1][0]

        length = (self.parent.spritedata[5] & 0xF) + 1
        self.height, self.pipeHeight = (length+1) * 16, length * 60
        self.yOffset = -self.height + 16

        length = (self.parent.spritedata[5] >> 4) + 1

        aux = self.aux[0]
        if aux.image:
            image = aux.image
            del image
            aux.image = None

        pix = QtGui.QPixmap(120, (length+1) * 60)
        pix.fill(Qt.transparent)

        painter = QtGui.QPainter(pix)
        painter.drawTiledPixmap(0, 60, 120, length * 60, ImageCache['PipeVTopMiddle%s%s' % (self.type, self.color)])
        painter.drawPixmap(0, 0, ImageCache['PipeVTop%s%s' % (self.type, self.color)])
        painter.end()
        del painter

        aux.setImage(pix, 0, self.height - (length+1) * 16, True)

        super().dataChanged()


class SpriteImage_ExpandingPipeDown(SpriteImage_Pipe):  # 162
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)

        self.direction = 1

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)
        self.aux[0].alpha = 0.5

    def dataChanged(self):
        self.offset = (0, 0)
        self.width, self.pipeWidth = 32, 120

        self.type = 'Painted' if self.parent.spritedata[4] & 1 else 'Normal'
        self.color = SpriteImage_Pipe.types[self.type][(self.parent.spritedata[3] & 3) + 1][0]

        length = (self.parent.spritedata[5] & 0xF) + 1
        self.height, self.pipeHeight = (length+1) * 16, length * 60
        self.topY = self.pipeHeight

        length = (self.parent.spritedata[5] >> 4) + 1

        aux = self.aux[0]
        if aux.image:
            image = aux.image
            del image
            aux.image = None

        pix = QtGui.QPixmap(120, (length+1) * 60)
        pix.fill(Qt.transparent)

        painter = QtGui.QPainter(pix)
        painter.drawTiledPixmap(0, 0, 120, length * 60, ImageCache['PipeVBottomMiddle%s%s' % (self.type, self.color)])
        painter.drawPixmap(0, length * 60, ImageCache['PipeVBottom%s%s' % (self.type, self.color)])
        painter.end()
        del painter

        aux.setImage(pix, 0, 0)

        super().dataChanged()


class SpriteImage_WaterGeyserLocation(SLib.SpriteImage_StaticMultiple):  # 163, 705
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

        painter.drawTiledPixmap(0, 15, self.width * (60/16), self.height * (60/16) - 15, self.middle.scaledToWidth(self.width * (60/16), Qt.SmoothTransformation))
        painter.drawPixmap(0, 0, self.width * (60/16), 180, self.top)


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


class SpriteImage_CoinCircle(SLib.SpriteImage_PivotRotationControlled):  # 165
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = True
        self.tileIdx = 30
        self.lastCoinAmount = 0

    def dataChanged(self):
        upsideDown = (self.parent.spritedata[2] & 1) != 0
        gyro = (self.parent.spritedata[2] & 2) != 0
        tilt = ((self.parent.spritedata[2] & 4) | (self.parent.spritedata[3] & 0x11)) != 0
        arc = (self.parent.spritedata[6] >> 4) * 22.5 + 22.5
        offset = (self.parent.spritedata[6] & 0xF) * 22.5
        coinAmount = 1 + self.parent.spritedata[8]
        diameter = self.parent.spritedata[9]
        movementID = self.parent.spritedata[10]

        tiltX = self.parent.objx
        tiltY = self.parent.objy
        angle = offset

        if coinAmount != self.lastCoinAmount:
            if coinAmount > self.lastCoinAmount:
                for _ in range(coinAmount - self.lastCoinAmount):
                    self.aux.append(SLib.AuxiliaryImage(self.parent, 60, 60))
                    self.aux[-1].hover = False
                    self.aux[-1].alpha = 0.5
            else:
                for _ in range(self.lastCoinAmount - coinAmount):
                    coinAux = self.aux.pop()
                    coinAux.scene().removeItem(coinAux)
                    del coinAux

        for i, coinAux in enumerate(self.aux):
            if arc == 360:
                angle = math.radians(-arc * i / coinAmount - offset)
            elif coinAmount > 1:
                angle = math.radians(arc * 0.5 - arc * i / (coinAmount - 1) - offset)

            x = math.sin(angle) * ((diameter * 30) + 30) - 30
            y = -(math.cos(angle) * ((diameter * 30) + 30)) - 30

            if tilt and not gyro:
                imageAngle = math.degrees(math.atan2(tiltY - (self.parent.objy + (y / 60) * 16 + 8), tiltX - (self.parent.objx + (x / 60) * 16 + 8))) - 90
                if upsideDown:
                    imageAngle += 180
                img = SLib.Tiles[self.tileIdx].main.transformed(QTransform().rotate(imageAngle))
                coinAux.setImage(img, x + 60 - img.width() / 2, y + 60 - img.height() / 2)
            else:
                coinAux.setImage(SLib.Tiles[self.tileIdx].main, x + 30, y + 30)

        self.affectAUXImage = not gyro
        self.lastCoinAmount = coinAmount
        super().dataChanged()


class SpriteImage_CoinOutlineCircle(SpriteImage_CoinCircle):  # 166
    def __init__(self, parent):
        super().__init__(parent)

    def dataChanged(self):
        multi = (self.parent.spritedata[2] >> 4) & 1
        self.tileIdx = 28 if multi else 31
        super().dataChanged()


class SpriteImage_CoinBlue(SpriteImage_PivotCoinBase):  # 167
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.parent.setZValue(20000)

    def dataChanged(self):
        self.updateImage(SLib.Tiles[46].main)
        super().dataChanged()


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


class SpriteImage_BulletBillCannon(SpriteImage_BulletBill):  # 171, 581
    offsets = (
        ( 0, 0),
        (-8, 0),
    )

    @staticmethod
    def loadImages():
        SpriteImage_BulletBill.loadImages()

        SLib.loadIfNotInImageCache('BulletBillCannon', 'bullet_bill_cannon.png')
        SLib.loadIfNotInImageCache('BulletBillCannonPiece', 'bullet_bill_cannon_piece.png')

        if 'BulletBillCannonInverted' not in ImageCache:
            ImageCache['BulletBillCannonInverted'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('bullet_bill_cannon.png', True).mirrored(False, True))

    def getType(self):
        if self.parent.type == 171:
            return 0

        return 1

    def getDirection(self, type):
        if self.parent.spritedata[4] & 0xF == 2:
            return 0

        return 1

    def dataChanged(self):
        if self.parent.initialState == 1:
            return SpriteImage_BulletBill.dataChanged(self)

        SLib.SpriteImage_Static.dataChanged(self)

        self.image = None
        self.xOffset = 0
        self.width = 16

        self.inverted = ((self.parent.spritedata[2] & 0xF0) >> 4) & 1
        self.cannonHeight = (self.parent.spritedata[5] & 0xF0) >> 4
        self.height = (self.cannonHeight + 2) * 16

        if self.inverted == 1:
            self.yOffset = 0

        else:
            self.yOffset = -(self.cannonHeight + 1) * 16

    def paint(self, painter):
        if self.parent.initialState != 1:
            if self.inverted == 1:
                painter.drawTiledPixmap(0, 0, 60, 60 * self.cannonHeight, ImageCache['BulletBillCannonPiece'])
                painter.drawPixmap(0, 60 * self.cannonHeight, 60, 120, ImageCache['BulletBillCannonInverted'])

            else:
                painter.drawPixmap(0, 0, 60, 120, ImageCache['BulletBillCannon'])
                painter.drawTiledPixmap(0, 120, 60, 60 * self.cannonHeight, ImageCache['BulletBillCannonPiece'])
        
        SLib.SpriteImage_Static.paint(self, painter)


class SpriteImage_RisingLoweringBulletBillCannon(SpriteImage_BulletBill):  # 172
    offsets = (
        ( 0, 0),
        (-8, 0),
    )

    @staticmethod
    def loadImages():
        SpriteImage_BulletBill.loadImages()

        SLib.loadIfNotInImageCache('BulletBillCannon', 'bullet_bill_cannon.png')
        SLib.loadIfNotInImageCache('BulletBillCannonPiece', 'bullet_bill_cannon_piece.png')

        if 'BulletBillCannonInverted' not in ImageCache:
            ImageCache['BulletBillCannonInverted'] = QtGui.QPixmap.fromImage(
                SLib.GetImg('bullet_bill_cannon.png', True).mirrored(False, True))

    def getType(self):
        return 0

    def getDirection(self, type):
        if self.parent.spritedata[3] >> 4 == 2:
            return 0

        return 1

    def dataChanged(self):
        if self.parent.initialState == 1:
            return SpriteImage_BulletBill.dataChanged(self)

        SLib.SpriteImage_Static.dataChanged(self)

        self.image = None
        self.xOffset = 0
        self.width = 16

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
        if self.parent.initialState != 1:
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
        
        SLib.SpriteImage_Static.paint(self, painter)


class SpriteImage_BanzaiBillCannon(SpriteImage_BanzaiBill):  # 173, 174, 646, 647
    offsets = (
        (-36, -64),
        (-40, -64),
    )

    @staticmethod
    def loadImages():
        SpriteImage_BanzaiBill.loadImages()

        SLib.loadIfNotInImageCache('BanzaiBillCannon', 'banzai_bill_cannon.png')
        SLib.loadIfNotInImageCache('BanzaiBillCannonU', 'banzai_bill_cannon_u.png')
        SLib.loadIfNotInImageCache('BanzaiBillCannonLuigi', 'banzai_bill_cannon_luigi.png')
        SLib.loadIfNotInImageCache('BanzaiBillCannonLuigiU', 'banzai_bill_cannon_luigi_u.png')

    def getDirection(self):
        if self.parent.spritedata[4] & 0xF == 2:
            return 0

        return 1

    def dataChanged(self):
        if self.parent.initialState == 1:
            return SpriteImage_BanzaiBill.dataChanged(self)

        if self.parent.type == 173:
            self.offset = (-32, -68)
            self.image = ImageCache['BanzaiBillCannon']

        elif self.parent.type == 174:
            self.offset = (-32, 16)
            self.image = ImageCache['BanzaiBillCannonU']

        elif self.parent.type == 646:
            self.offset = (-32, -68)
            self.image = ImageCache['BanzaiBillCannonLuigi']

        else:
            self.offset = (-32, 16)
            self.image = ImageCache['BanzaiBillCannonLuigiU']

        SLib.SpriteImage_Static.dataChanged(self)



class SpriteImage_HomingBanzaiBillCannon(SLib.SpriteImage_StaticMultiple):  # 582, 583, 648, 649
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('HomingBanzaiBill', 'homing_banzai_bill.png')

        SLib.loadIfNotInImageCache('BanzaiBillCannon', 'banzai_bill_cannon.png')
        SLib.loadIfNotInImageCache('BanzaiBillCannonU', 'banzai_bill_cannon_u.png')
        SLib.loadIfNotInImageCache('BanzaiBillCannonLuigi', 'banzai_bill_cannon_luigi.png')
        SLib.loadIfNotInImageCache('BanzaiBillCannonLuigiU', 'banzai_bill_cannon_luigi_u.png')

    def dataChanged(self):
        if self.parent.initialState == 1:
            self.offset = (-40, -64)
            self.image = ImageCache['HomingBanzaiBill']

        elif self.parent.type == 582:
            self.offset = (-32, -68)
            self.image = ImageCache['BanzaiBillCannon']

        elif self.parent.type == 583:
            self.offset = (-32, 16)
            self.image = ImageCache['BanzaiBillCannonU']

        elif self.parent.type == 648:
            self.offset = (-32, -68)
            self.image = ImageCache['BanzaiBillCannonLuigi']

        else:
            self.offset = (-32, 16)
            self.image = ImageCache['BanzaiBillCannonLuigiU']

        super().dataChanged()

class SpriteImage_Mechakoopa(SLib.SpriteImage_StaticMultiple):  # 175
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Mechakoopa', 'mechakoopa.png')
        SLib.loadIfNotInImageCache('MechakoopaDown', 'mechakoopa_down.png')

    def dataChanged(self):
        self.image = ImageCache['MechakoopaDown' if self.parent.initialState == 1 else 'Mechakoopa']
        self.yOffset = -4 if self.parent.initialState == 1 else -16

        super().dataChanged()


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


class SpriteImage_Spike(SLib.SpriteImage_StaticMultiple):  # 180, 181, 651
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Spike'],
            (-8, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Spike', 'spike.png')
        SLib.loadIfNotInImageCache('SpikeR', 'spike_right.png')

    def dataChanged(self):
        direction = self.parent.spritedata[4] & 3
        
        if direction == 1:
            self.image = ImageCache['SpikeR'];
            self.xOffset = -4
        else:
            self.image = ImageCache['Spike'];
            self.xOffset = -8

        super().dataChanged()


class SpriteImage_MovingPlatform(SpriteImage_PlatformBase):  # 182, 186, 534, 535
    def __init__(self, parent):
        super().__init__(parent, hasAux=True)

    def getPlatformWidth(self):
        if self.getPlatformType() == 'C':
            return 2.5

        width = (self.parent.spritedata[8] & 0xF) + 1
        if width == 1:
            width = 2
            
        return width + 0.5

    def getPlatformType(self):
        type_ = self.parent.spritedata[3] >> 4
        imgType = 'N'

        if type_ == 1:
            imgType = 'R'
        elif type_ == 3:
            imgType = 'S'
        elif type_ == 4:
            imgType = 'C'
            
        return imgType

    def getPlatformOffset(self):
        if self.getPlatformType() == 'C':
            return (-4, -4)
        else:
            return (-4, 0)

    def getPlatformMoveDir(self):
        if self.parent.spritedata[3] & 1:
            return 'D' if self.parent.type == 182 or self.parent.type == 535 else 'L'
        else:
            return 'U' if self.parent.type == 182 or self.parent.type == 535 else 'R'

    def getPlatformMoveDist(self):
        return self.parent.spritedata[7] >> 4


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


class SpriteImage_GrrrolSpawner(SLib.SpriteImage):  # 188
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'GrrrolSpawnerL' not in ImageCache:
            for D, d in (('R', 'right'), ('L', 'left'), ('D', 'down')):
                SLib.loadIfNotInImageCache('GrrrolSpawner%s' % D, 'grrrol_spawner_%s.png' % d)
                SLib.loadIfNotInImageCache('GrrrolSpawnerM%s0' % D, 'grrrol_spawner_middle_%s_0.png' % d)
                SLib.loadIfNotInImageCache('GrrrolSpawnerM%s1' % D, 'grrrol_spawner_middle_%s_1.png' % d)

    def dataChanged(self):
        length = (self.parent.spritedata[2] & 0xF) + 3
        direction = self.parent.spritedata[3] >> 4 & 3
        if direction > 2:
            direction = 0

        if direction == 2:
            self.width = 2.5 * 16
            self.height = length * 16
            self.offset = (-4, -self.height + 8)

        else:
            self.width = length * 16
            self.height = 2.5 * 16
            self.offset = ((-(length - 1) * 16) if direction == 1 else 0, -12)

        self.length = length
        self.direction = direction

        super().dataChanged()

    def paint(self, painter):
        if self.direction == 0:
            painter.drawPixmap(0, 0, ImageCache['GrrrolSpawnerL'])
            for i in range(3, self.length):
                painter.drawPixmap(i * 60, 0, ImageCache['GrrrolSpawnerML%d' % ((i-1)%2)])

        elif self.direction == 1:
            painter.drawPixmap((self.length-3) * 60, 0, ImageCache['GrrrolSpawnerR'])
            for i in range(3, self.length):
                painter.drawPixmap((self.length-i-1) * 60, 0, ImageCache['GrrrolSpawnerMR%d' % ((i-1)%2)])

        else:
            painter.drawPixmap(0, (self.length-3) * 60, ImageCache['GrrrolSpawnerD'])
            for i in range(3, self.length):
                painter.drawPixmap(0, (self.length-i-1) * 60, ImageCache['GrrrolSpawnerMD%d' % ((i-1)%2)])

        super().paint(painter)


class SpriteImage_PivotQBlock(SLib.SpriteImage_PivotRotationControlled):  # 190, 707
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.items = {0: 0x800 + len(globals.Overrides) - 1, 1: 49, 2: 32, 3: 32, 4: 37, 5: 38, 6: 36, 7: 33, 8: 34, 9: 41, 12: 35, 13: 42, 15: 39}

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Q10', 'block_q_10.png')
        SLib.loadIfNotInImageCache('QKinokoUP', 'block_q_kinoko_up.png')
        SLib.loadIfNotInImageCache('QKinoko', 'block_q_kinoko_coin.png')

    def dataChanged(self):
        item = self.parent.spritedata[9] & 0xF
        acorn = (self.parent.spritedata[6] >> 4) & 1

        if acorn:
            self.image = SLib.Tiles[40].main

        elif item in self.items:
            self.image = SLib.Tiles[self.items[item]].main

        elif item == 10:
            self.image = ImageCache['Q10']

        elif item == 11:
            self.image = ImageCache['QKinokoUP']

        elif item == 14:
            self.image = ImageCache['QKinoko']

        else:
            self.image = SLib.Tiles[49].main

        super().dataChanged()


class SpriteImage_PivotBrickBlock(SLib.SpriteImage_PivotRotationControlled):  # 191, 706
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.items = {0: 48, 1: 26, 2: 16, 3: 16, 4: 21, 5: 22, 6: 20, 7: 17, 9: 25, 10: 27, 11: 18, 12: 19, 15: 23}

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BCstar', 'block_c_star.png')
        SLib.loadIfNotInImageCache('BSpring', 'block_spring.png')
        SLib.loadIfNotInImageCache('BKinoko', 'block_kinoko_coin.png')

    def dataChanged(self):
        item = self.parent.spritedata[9] & 0xF
        acorn = (self.parent.spritedata[6] >> 4) & 1

        if acorn:
            self.image = SLib.Tiles[24].main

        elif item in self.items:
            self.image = SLib.Tiles[self.items[item]].main

        elif item == 8:
            self.image = ImageCache['BCstar']

        elif item == 13:
            self.image = ImageCache['BSpring']

        elif item == 14:
            self.image = ImageCache['BKinoko']

        else:
            self.image = SLib.Tiles[49].main

        super().dataChanged()


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
    @staticmethod
    def loadImages():
        if 'LavaParticlesA' in ImageCache: return
        ImageCache['LavaParticlesA'] = SLib.GetImg('lava_particles_a.png')
        ImageCache['LavaParticlesB'] = SLib.GetImg('lava_particles_b.png')
        ImageCache['LavaParticlesC'] = SLib.GetImg('lava_particles_c.png')

    def dataChanged(self):
        type = (self.parent.spritedata[5] & 0xF) % 3
        self.mid = (
            ImageCache['LavaParticlesA'],
            ImageCache['LavaParticlesB'],
            ImageCache['LavaParticlesC'],
        )[type]

        super().dataChanged()


class SpriteImage_IceBlock(SLib.SpriteImage_StaticMultiple):  # 203
    def __init__(self, parent):
        super().__init__(parent, 3.75)

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('IceBlock', 'block_ice.png')
        SLib.loadIfNotInImageCache('IceBlockCoin', 'block_ice_coin.png')

    def dataChanged(self):
        self.aux[0].setImage(ImageCache['IceBlockCoin' if self.parent.spritedata[4] & 1 else 'IceBlock'], -4, -4, True)
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
        self.offset = (-24, -20) if giant else (-12, -8)

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
        for i in range(6):
            SLib.loadIfNotInImageCache('LavaGeyser%d' % i, 'lava_geyser_%d.png' % i)

    def dataChanged(self):
        size = (self.parent.spritedata[4] >> 4) & 7; size = 0 if size > 5 else size
        self.image = ImageCache['LavaGeyser%d' % size]

        startsOn = self.parent.spritedata[5] & 3
        self.alpha = (startsOn + 1) / 4.0

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

        else:
            self.yOffset = -160

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


class SpriteImage_GreyTestPlatform(SLib.SpriteImage_PivotRotationControlled):  # 211
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
            self.size = (16, 16)
            self.image = None

        else:
            self.image = ImageCache['GrayBlock'].transformed(QTransform().scale(width, 0.5))

        self.spritebox.shown = width == 0

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


class SpriteImage_ControllerSpinOne(SLib.SpriteImage_Static):  # 214, 484
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


class SpriteImage_BigBoo(SLib.SpriteImage):  # 219
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.spritebox.shown = False
        self.dimensions = (-48, -80, 108, 96)

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setImage(ImageCache['BigBoo'], -24, -40, True)

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


class SpriteImage_Scaffold(SLib.SpriteImage_PivotRotationControlled):  # 228, 714
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

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
            (-20, -32)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Larry', 'larry.png')


class SpriteImage_IceFloe(SLib.SpriteImage_StaticMultiple):  # 226, 227, 231
    offsets = (
        ( 0, -4),
        (-4,  0),
        (-4,  0),
        (-4, -4),
        (-4,  0),
        (-4,  0),
        (-4, -4),
        (-4, -4),
        (-4,  0),
        (-4,  0),
        ( 4,  0),
        (-4,  0),
        (-4,  0),
        (-4,  0),
    )

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        for i in range(14):
            SLib.loadIfNotInImageCache('IceFloe%d' % i, 'ice_floe_%d.png' % i)

    def dataChanged(self):
        size = self.parent.spritedata[5] & 0xF
        if size > 13:
            size = 0

        self.image = ImageCache['IceFloe%d' % size]
        self.offset = SpriteImage_IceFloe.offsets[size]

        super().dataChanged()


class SpriteImage_LightBlock(SLib.SpriteImage_PivotRotationControlled):  # 232
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['LightBlock'],
        )

        self.previousType = 0

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LightBlock', 'lightblock.png')

    def getMovementType(self):
        type = self.parent.spritedata[4] & 3
        if type > 2:
            type = 2

        return type

    def allowedMovementControllers(self):
        if self.getMovementType() == 2:
            return 68, 116, 69, 118

        return tuple()

    def dataChanged(self):
        type = self.getMovementType()
        if type != self.previousType:
            self.previousType = type
            self.unhookController()

        super().dataChanged()


class SpriteImage_SpinningFirebar(SLib.SpriteImage_StaticMultiple):  # 235, 483
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75
        )

        self.parent.setZValue(500000)
        self.aux.append(SLib.AuxiliaryCircleOutline(parent, 0))
        self.fireballs = [SLib.AuxiliaryImage(parent, 135, 135) for i in range(60)]
        self.aux.extend(self.fireballs)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FirebarBall', 'firebar_fireball.png')
        SLib.loadIfNotInImageCache('FirebarBase0', 'firebar_base.png')
        SLib.loadIfNotInImageCache('FirebarBaseLong0', 'firebar_base_long.png')

        for i in range(1, 5):
            SLib.loadIfNotInImageCache('FirebarBase%d' % i, 'firebar_base_%d.png' % i)
            SLib.loadIfNotInImageCache('FirebarBaseLong%d' % i, 'firebar_base_long_%d.png' % i)

    def dataChanged(self):
        size = self.parent.spritedata[5] & 0xF
        wideBase = (self.parent.spritedata[3] >> 4) & 1

        nFireBar = (self.parent.spritedata[5] >> 4) + 1
        if size == 0:
            nFireBar = 0

        elif nFireBar > 4:
            nFireBar = 4

        width = ((size << 1) + 1) << 4
        self.aux[0].setSize(width)
        self.aux[0].setPos(-width * 1.875 + (60 if wideBase else 30), -width * 1.875 + 30)

        self.image = ImageCache['FirebarBase%d' % nFireBar] if not wideBase else ImageCache['FirebarBaseLong%d' % nFireBar]
        self.xOffset = 0 if not wideBase else -8

        nFireBall = size * nFireBar

        for i in range(nFireBall, 60):
            self.fireballs[i].image = None

        if nFireBar:
            xOffs = (30 if wideBase else 0)

            for j in range(size):
                nFireBall -= 1
                aux = self.fireballs[nFireBall]
                aux.setPos(60*(j+1) + xOffs - 37.5, -37.5)
                aux.image = ImageCache['FirebarBall']
                aux.alpha = 0.5
                aux.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)


            if nFireBar in (2, 4):
                for j in range(size):
                    nFireBall -= 1
                    aux = self.fireballs[nFireBall]
                    aux.setPos(-60*(j+1) + xOffs - 37.5, -37.5)
                    aux.image = ImageCache['FirebarBall']
                    aux.alpha = 0.5
                    aux.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

            if nFireBar == 3:
                for j in range(size):
                    nFireBall -= 1
                    aux = self.fireballs[nFireBall]
                    aux.setPos(-30*(j+1) + xOffs - 37.5, -(52.5*(j+1) + 37.5))
                    aux.image = ImageCache['FirebarBall']
                    aux.alpha = 0.5
                    aux.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

                    nFireBall -= 1
                    aux = self.fireballs[nFireBall]
                    aux.setPos(-30*(j+1) + xOffs - 37.5, 52.5*(j+1) - 37.5)
                    aux.image = ImageCache['FirebarBall']
                    aux.alpha = 0.5
                    aux.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

            if nFireBar == 4:
                for j in range(size):
                    nFireBall -= 1
                    aux = self.fireballs[nFireBall]
                    aux.setPos(xOffs - 37.5, 60*(j+1) - 37.5)
                    aux.image = ImageCache['FirebarBall']
                    aux.alpha = 0.5
                    aux.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

                    nFireBall -= 1
                    aux = self.fireballs[nFireBall]
                    aux.setPos(xOffs - 37.5, -(60*(j+1) + 37.5))
                    aux.image = ImageCache['FirebarBall']
                    aux.alpha = 0.5
                    aux.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

        super().dataChanged()


class SpriteImage_BigFirebar(SLib.SpriteImage_Static):  # 236
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.parent.setZValue(500000)
        self.aux.append(SLib.AuxiliaryCircleOutline(parent, 0))
        self.fireballs = [SLib.AuxiliaryImage(parent, 1, 1) for i in range(60)]
        self.aux.extend(self.fireballs)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FirebarBall', 'firebar_fireball.png')
        SLib.loadIfNotInImageCache('FirebarBallBig', 'firebar_fireball_big.png')
        SLib.loadIfNotInImageCache('FirebarBaseBig0', 'firebar_base_big.png')
        SLib.loadIfNotInImageCache('FirebarBaseBigger0', 'firebar_base_bigger.png')

        for i in range(1, 5):
            SLib.loadIfNotInImageCache('FirebarBaseBig%d' % i, 'firebar_base_big_%d.png' % i)
            SLib.loadIfNotInImageCache('FirebarBaseBigger%d' % i, 'firebar_base_bigger_%d.png' % i)

    def dataChanged(self):
        isBig = self.parent.spritedata[2] & 1
        size = self.parent.spritedata[5] & 0xF

        nFireBar = (self.parent.spritedata[5] >> 4) + 1
        if size == 0:
            nFireBar = 0

        elif nFireBar > 4:
            nFireBar = 4

        width = (((size << (2 if isBig else 1)) + 1) << 4) + (16 if isBig else 0)
        self.aux[0].setSize(width)
        self.aux[0].setPos(-width * 1.875 + (60 if isBig else 45), -width * 1.875 + (60 if isBig else 45))

        self.image = ImageCache['FirebarBaseBig%d' % nFireBar] if not isBig else ImageCache['FirebarBaseBigger%d' % nFireBar]
        self.offset = (-4, -4) if not isBig else (-8, -8)

        nFireBall = size * nFireBar

        for i in range(nFireBall, 60):
            self.fireballs[i].image = None

        if nFireBar:
            offs = 30 if isBig else 15
            imgOffs = 97.5 if isBig else 37.5
            step = 120 if isBig else 60
            img = ImageCache['FirebarBallBig'] if isBig else ImageCache['FirebarBall']

            for j in range(size):
                nFireBall -= 1
                aux = self.fireballs[nFireBall]
                aux.setImage(img, step*(j+1) + offs - imgOffs, offs - imgOffs)
                aux.alpha = 0.5
                aux.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)


            if nFireBar in (2, 4):
                for j in range(size):
                    nFireBall -= 1
                    aux = self.fireballs[nFireBall]
                    aux.setImage(img, -step*(j+1) + offs - imgOffs, offs - imgOffs)
                    aux.alpha = 0.5
                    aux.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

            if nFireBar == 3:
                for j in range(size):
                    nFireBall -= 1
                    aux = self.fireballs[nFireBall]
                    aux.setImage(img, -(step//2)*(j+1) + offs - imgOffs, -(step*0.875)*(j+1) + offs - imgOffs)
                    aux.alpha = 0.5
                    aux.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

                    nFireBall -= 1
                    aux = self.fireballs[nFireBall]
                    aux.setImage(img, -(step//2)*(j+1) + offs - imgOffs, (step*0.875)*(j+1) + offs - imgOffs)
                    aux.alpha = 0.5
                    aux.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

            if nFireBar == 4:
                for j in range(size):
                    nFireBall -= 1
                    aux = self.fireballs[nFireBall]
                    aux.setImage(img, offs - imgOffs, step*(j+1) + offs - imgOffs)
                    aux.alpha = 0.5
                    aux.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

                    nFireBall -= 1
                    aux = self.fireballs[nFireBall]
                    aux.setImage(img, offs - imgOffs, -step*(j+1) + offs - imgOffs)
                    aux.alpha = 0.5
                    aux.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)

        super().dataChanged()


class SpriteImage_Bolt(SLib.SpriteImage_StaticMultiple):  # 238
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Bolt', 'bolt.png')
        SLib.loadIfNotInImageCache('BoltStone', 'bolt_stone.png')

    def dataChanged(self):
        if self.parent.spritedata[4] & 1:
            self.image = ImageCache['BoltStone']
            self.xOffset = -8

        else:
            self.image = ImageCache['Bolt']
            self.xOffset = -4

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

        image = ImageCache['BoltMushroomSpring']
        if stretchable:
            image = image.transformed(QTransform().scale(1, stretchMultiplier))

        self.aux[0].setImage(image, auxOffset, 180)
            
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

        image = ImageCache['BoltMushroomSpring']
        if stretchable:
            image = image.transformed(QTransform().scale(1, stretchMultiplier))

        self.aux[0].setImage(image, auxOffset, 120)
            
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


class SpriteImage_GhostHouseBoxFrame(SLib.SpriteImage_PivotRotationControlled):  # 248
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
            (-4, -12),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Wiggler', 'wiggler.png')


class SpriteImage_GreyBlock(SLib.SpriteImage_PivotRotationControlled):  # 250
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
            self.size = (16, 16)
            self.image = None

        else:
            self.spritebox.shown = False
            self.image = ImageCache['GrayBlock'].transformed(QTransform().scale(width, height))

        super().dataChanged()


class SpriteImage_FloatingBubble(SLib.SpriteImage_StaticMultiple):  # 251
    offsets = (
        (-56, -64),
        (-32, -80),
        (-68, -36),
    )

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        if 'FloatingBubble0' not in ImageCache:
            for shape in range(4):
                ImageCache['FloatingBubble%d' % shape] = SLib.GetImg('floating_bubble_%d.png' % shape)

    def dataChanged(self):
        shape = self.parent.spritedata[4] >> 4
        if shape > 2: shape = 0

        self.image = ImageCache['FloatingBubble%d' % shape]
        self.offset = SpriteImage_FloatingBubble.offsets[shape]

        super().dataChanged()


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


class SpriteImage_LightCircle(SLib.SpriteImage_PivotRotationControlled):  # 253
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.offset = (-8, -8)

        self.spritebox.shown = True
        self.aux.append(SLib.AuxiliaryCircleOutline(parent, 60, Qt.AlignCenter))

        self.previousType = 0

    def getMovementType(self):
        type = self.parent.spritedata[4] & 3
        if type > 2:
            type = 2

        return type

    def allowedMovementControllers(self):
        if self.getMovementType() == 2:
            return 68, 116, 69, 118

        return tuple()

    def dataChanged(self):
        type = self.getMovementType()
        if type != self.previousType:
            self.previousType = type
            self.unhookController()

        self.aux[0].setSize(((self.parent.spritedata[3] & 0xF) + 2) * 48)
        self.aux[0].setPos(self.aux[0].x(), self.aux[0].y())

        super().dataChanged()


class SpriteImage_UnderwaterLamp(SLib.SpriteImage):  # 254
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.spritebox.shown = False
        self.dimensions = (-4, -4, 24, 24)

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setImage(ImageCache['UnderwaterLamp'], -36, -36, True)

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


class SpriteImage_Parabeetle(SLib.SpriteImage_StaticMultiple):  # 261, 652
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.xOffset = 4
        self.yOffset = 4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Parabeetle0', 'parabeetle2.png')
        SLib.loadIfNotInImageCache('Parabeetle1', 'parabeetle.png')

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 0xF
        if direction > 1:
            direction = 0
        
        self.image = ImageCache['Parabeetle%d' % direction]
        super().dataChanged()


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


class SpriteImage_MovingGhostHouseBlock(SLib.SpriteImage_PivotRotationControlled):  # 266, 696
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

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
        self.updateSize()

        pix = QtGui.QPixmap(self.width * 3.75, self.height * 3.75)
        pix.fill(Qt.transparent)

        painter = QtGui.QPainter(pix)

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

        painter.end()
        del painter

        self.image = pix

        super().dataChanged()

    def updateSize(self):
        self.w = (self.parent.spritedata[8] & 0x1F) + 3
        self.h = (self.parent.spritedata[9] & 0x1F) + 3
        self.width = self.w << 4
        self.height = self.h << 4


class SpriteImage_CustomizableIceBlock(SLib.SpriteImage_StaticMultiple):  # 268
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.yOffset = -16

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('IceBlock1x1', 'ice_block_1x1.png')
        SLib.loadIfNotInImageCache('IceBlock2x1', 'ice_block_2x1.png')

    def dataChanged(self):
        blockType = self.parent.spritedata[5] & 0xF

        if blockType == 1:
            self.image = ImageCache['IceBlock2x1']
            self.xOffset = -16
        else:
            self.image = ImageCache['IceBlock1x1']
            self.xOffset = -8

        super().dataChanged()


class SpriteImage_Gear(SLib.SpriteImage_PivotRotationControlled):  # 269
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
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Amp', 'amp.png')
        SLib.loadIfNotInImageCache('AmpBig', 'amp_big.png')

    def dataChanged(self):
        if self.parent.spritedata[4] & 1:
            self.offset = (-32, -32)
            self.image = ImageCache['AmpBig']

        else:
            self.offset = (-16, -16)
            self.image = ImageCache['Amp']

        shift = (self.parent.spritedata[5] >> 4) & 3
        if shift & 1:
            self.xOffset += 8

        if shift & 2:
            self.yOffset += 8

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


class SpriteImage_CastlePlatform(SLib.SpriteImage_PivotRotationControlled):  # 275, 676
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
        size = self.parent.spritedata[4] & 0xF

        if size == 1:
            self.image = ImageCache['CastlePlatform1']
        elif size == 2:
            self.image = ImageCache['CastlePlatform2']
        else:
            self.image = ImageCache['CastlePlatform0']

        self.xOffset = -(self.image.width() / 120) * 16 + 8

        super().dataChanged()


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


class SpriteImage_KingBill(SLib.SpriteImage):  # 282, 653
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].alpha = 0.4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('KingR', 'king_bill_r.png')
        SLib.loadIfNotInImageCache('KingL', 'king_bill_l.png')
        SLib.loadIfNotInImageCache('KingU', 'king_bill_u.png')
        SLib.loadIfNotInImageCache('KingD', 'king_bill_d.png')

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 3

        if direction == 1:
            self.aux[0].setImage(ImageCache['KingR'], 0, -465)
        elif direction == 2:
            self.aux[0].setImage(ImageCache['KingD'], -315, 0)
        elif direction == 3:
            self.aux[0].setImage(ImageCache['KingU'], -315, 0)
        else:
            self.aux[0].setImage(ImageCache['KingL'], 0, -465)

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
            (-4, 4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LavaBubble', 'lava_bubble.png')


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
    colors = (
        ('Green', 'green'),
        ('Yellow', 'yellow'),
    )

    offsets = (
        (-28, -32),
        (-36, -44),
        (-32, -60),
        (-40, -76),
    )

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.parent.setZValue(24000)

    @staticmethod
    def loadImages():
        for C, c in SpriteImage_Bush.colors:
            for i in range(4):
                SLib.loadIfNotInImageCache('Bush%s%d' % (C, i), 'bush_%d_%s.png' % (i, c))

    def dataChanged(self):
        type = self.parent.spritedata[5] & 3
        isYellow = self.parent.spritedata[5] >> 4 & 1

        self.image = ImageCache['Bush%s%d' % (SpriteImage_Bush.colors[isYellow][0], type)]
        self.offset = SpriteImage_Bush.offsets[type]

        super().dataChanged()


class SpriteImage_ContinuousBurner(SLib.SpriteImage):  # 289
    offsets = (
        (-24, -28),
        (-40, -28),
        (-28, -40),
        (-28, -24),
    )

    dims = (
        (0, 0, 64, 16),
        (-48, 0, 64, 16),
        (0, -48, 16, 64),
        (0, 0, 16, 48),
    )

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.spritebox.shown = False
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))

    @staticmethod
    def loadImages():
        for i in range(4):
            SLib.loadIfNotInImageCache('Burner%d' % i, 'burner_%d.png' % i)

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 3

        self.dimensions = SpriteImage_ContinuousBurner.dims[direction]
        self.aux[0].setImage(ImageCache['Burner%d' % direction], *SpriteImage_ContinuousBurner.offsets[direction], True)

        super().dataChanged()


class SpriteImage_ContinuousBurnerLong(SLib.SpriteImage):  # 290
    offsets = (
        (0, -28),
        (-16, -28),
        (-28, -16),
        (-28, 0),
    )

    dims = (
        (0, 0, 112, 16),
        (-96, 0, 112, 16),
        (0, -96, 16, 112),
        (0, 0, 16, 112),
    )

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.spritebox.shown = False
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))

    @staticmethod
    def loadImages():
        for i in range(4):
            SLib.loadIfNotInImageCache('BurnerLong%d' % i, 'burner_long_%d.png' % i)

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 3

        self.dimensions = SpriteImage_ContinuousBurnerLong.dims[direction]
        self.aux[0].setImage(ImageCache['BurnerLong%d' % direction], *SpriteImage_ContinuousBurnerLong.offsets[direction], True)

        super().dataChanged()


class SpriteImage_SyncBurner(SLib.SpriteImage_StaticMultiple):  # 292
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        for i in range(4):
            SLib.loadIfNotInImageCache('SyncBurner%d' % i, 'burner_sync_%d.png' % i)

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 3
        self.image = ImageCache['SyncBurner%d' % direction]

        super().dataChanged()


class SpriteImage_RotatingBurner(SLib.SpriteImage_StaticMultiple):  # 293
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        for i in range(4):
            SLib.loadIfNotInImageCache('RotatingBurner%d' % i, 'burner_rot_%d.png' % i)

    def dataChanged(self):
        direction = self.parent.spritedata[5] >> 4 & 3
        self.image = ImageCache['RotatingBurner%d' % direction]

        self.offset = (0, 0)
        if direction == 0:
            self.yOffset = -8

        elif direction == 3:
            self.xOffset = -8

        super().dataChanged()


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
        self.offset = (-28, -52)

    @staticmethod
    def loadImages():
        if 'ClamEmpty' in ImageCache: return

        SLib.loadIfNotInImageCache('StarCoin', 'star_coin.png')
        SLib.loadIfNotInImageCache('PSwitch', 'p_switch.png')
        SLib.loadIfNotInImageCache('ClamEmpty', 'clam.png')
        SLib.loadIfNotInImageCache('1Up', '1up.png')

        overlays = (
            (65, 55, 'Star', ImageCache['StarCoin']),
            (100, 105, '1Up', ImageCache['1Up']),
            (82, 96, 'PSwitch', ImageCache['PSwitch']),
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
        painter.drawPixmap(70, 105, SLib.Tiles[0x200 * 4 + 30].main)
        painter.drawPixmap(130, 105, SLib.Tiles[0x200 * 4 + 30].main)
        del painter
        ImageCache['Clam2Coin'] = newPix

    def dataChanged(self):
        holds = self.parent.spritedata[5] & 0xF
        if holds == 1:
            holdsStr = 'Star'
        elif holds == 2:
            holdsStr = '2Coin'
        elif holds == 3:
            holdsStr = '1Up'
        elif holds == 4:
            holdsStr = 'PSwitch'
        else:
            holdsStr = 'Empty'

        self.image = ImageCache['Clam' + holdsStr]

        super().dataChanged()


class SpriteImage_Lemmy(SLib.SpriteImage_Static):  # 296
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Lemmy'],
            (-8, -56),
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
            (-4, -4),
        )

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
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].alpha = 0.5

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
        leftRopeLength = self.parent.spritedata[4] & 0xF
        leftRopeLength = 0.5 if leftRopeLength < 1 else leftRopeLength
        rightRopeLength = self.parent.spritedata[5] >> 4
        rightRopeLength = 0.5 if rightRopeLength < 1 else rightRopeLength
        snowy = self.parent.spritedata[4] & 0x10 != 0
        middleRopeLength = (self.parent.spritedata[5] & 0xF) + ((self.parent.spritedata[3] & 0xF) << 4)
        leftPlatfromWidth = (self.parent.spritedata[8] & 0xF) + 3
        rightPlatfromWidth = (self.parent.spritedata[9] >> 4) + 3

        leftPlatformOffset = (leftPlatfromWidth + 0.5) / 2
        rightPlatformOffset = (rightPlatfromWidth + 0.5) / 2

        xOffset = 0

        if middleRopeLength + leftPlatformOffset < rightPlatformOffset:
            width = rightPlatformOffset * 2 * 60
            xOffset = -(rightPlatformOffset - middleRopeLength) * 60
        elif middleRopeLength + rightPlatformOffset < leftPlatformOffset:
            width = leftPlatformOffset * 2 * 60
            xOffset = -leftPlatformOffset * 60
        else:
            width = (leftPlatformOffset + middleRopeLength + rightPlatformOffset) * 60
            xOffset = -leftPlatformOffset * 60

        height = (leftRopeLength if leftRopeLength > rightRopeLength else rightRopeLength) * 60 + 75

        pix = QtGui.QPixmap(width, height)
        pix.fill(Qt.transparent)
        painter = QtGui.QPainter(pix)

        leftSideOffset = leftPlatformOffset * 60 - 15
        if middleRopeLength + leftPlatformOffset < rightPlatformOffset:
            leftSideOffset = (rightPlatformOffset - middleRopeLength) * 60 - 15

        #Draw ropes and wheels
        painter.drawTiledPixmap(leftSideOffset, 30, 30, leftRopeLength * 60 - 15, ImageCache['ScaleRopeV'])
        painter.drawTiledPixmap(leftSideOffset + middleRopeLength * 60, 30, 30, rightRopeLength * 60 - 15, ImageCache['ScaleRopeV'])
        painter.drawTiledPixmap(leftSideOffset + 30, 0, middleRopeLength * 60 - 30, 30, ImageCache['ScaleRopeH'])
        painter.drawPixmap(leftSideOffset, 0, ImageCache['ScaleWheel'])
        painter.drawPixmap(leftSideOffset + middleRopeLength * 60 - 30, 0, ImageCache['ScaleWheel'])

        imgType = 'MovPlat%s' % ('S' if snowy else 'N')
        
        # Draw left platform
        painter.drawPixmap(leftSideOffset + 15 - leftPlatformOffset * 60 + 75 - ImageCache[imgType + 'L'].width(), leftRopeLength * 60 + 15, ImageCache[imgType + 'L'])
        painter.drawTiledPixmap(leftSideOffset + 15 - leftPlatformOffset * 60 + 75, leftRopeLength * 60 + 15, (leftPlatfromWidth - 2) * 60, 60, ImageCache[imgType + 'M'])
        painter.drawPixmap(leftSideOffset + 15 - leftPlatformOffset * 60 + 75 + (leftPlatfromWidth - 2) * 60, leftRopeLength * 60 + 15, ImageCache[imgType + 'R'])

        # Draw right platform
        painter.drawPixmap(10 + leftSideOffset + 15 + (middleRopeLength - rightPlatformOffset) * 60 + 75 - ImageCache[imgType + 'L'].width(), rightRopeLength * 60 + 15, ImageCache[imgType + 'L'])
        painter.drawTiledPixmap(9 + leftSideOffset + 15 + (middleRopeLength - rightPlatformOffset) * 60 + 75, rightRopeLength * 60 + 15, (rightPlatfromWidth - 2) * 60, 60, ImageCache[imgType + 'M'])
        painter.drawPixmap(7 + leftSideOffset + 15 + (middleRopeLength - rightPlatformOffset) * 60 + 75 + (rightPlatfromWidth - 2) * 60, rightRopeLength * 60 + 15, ImageCache[imgType + 'R'])

        painter = None
        self.aux[0].setImage(pix, xOffset, -45)
        super().dataChanged()


class SpriteImage_Blooper(SLib.SpriteImage_StaticMultiple):  # 313, 322
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.offset = (-4, -12)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Blooper', 'blooper.png')
        SLib.loadIfNotInImageCache('BlooperL', 'blooper_l.png')
        SLib.loadIfNotInImageCache('BlooperR', 'blooper_r.png')

    def dataChanged(self):
        direction = self.parent.spritedata[2] >> 4
        if direction == 2:
            self.image = ImageCache['BlooperR']

        elif direction == 3:
            self.image = ImageCache['BlooperL']

        else:
            self.image = ImageCache['Blooper']

        super().dataChanged()


class SpriteImage_Crystal(SLib.SpriteImage_PivotRotationControlled):  # 316
    offsets = (
        ( -4,   -4),
        ( -4,   -4),
        ( -4,   -4),
        ( -4,   -4),
        ( -8,   -4),
        ( -8,   -4),
        (-24,   -8),
        ( -8, -100),
        ( -4,   -4),
        ( -4,   -4),
        ( -8,   -4),
    )

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        for i in range(11):
            SLib.loadIfNotInImageCache('Crystal%d' % i, 'crystal_%d.png' % i)

    def dataChanged(self):
        size = self.parent.spritedata[4] & 0xF
        if size > 10:
            size = 0

        self.affectImage = (self.parent.spritedata[3] & 1) != 1

        self.image = ImageCache['Crystal%d' % size]
        self.offset = SpriteImage_Crystal.offsets[size]

        super().dataChanged()


class SpriteImage_Broozer(SLib.SpriteImage_Static):  # 320
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Broozer'],
            (-16, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Broozer', 'broozer.png')


class SpriteImage_Bulber(SLib.SpriteImage):  # 321
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.spritebox.shown = False
        self.dimensions = (-20, -12, 52, 44)

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setImage(ImageCache['Bulber'], -32, -24, True)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Bulber', 'bulber.png')


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

    def updateSize(self):
        self.w = (self.parent.spritedata[8] & 0xF) + 2
        self.h = (self.parent.spritedata[4] >> 4) + 2
        self.width = self.w << 4
        self.height = self.h << 4


class SpriteImage_MovingCoin(SLib.SpriteImage_Static):  # 326
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


class SpriteImage_SledgeBlock(SLib.SpriteImage_PivotRotationControlled):  # 327
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

        self.offset = (-12, -4)

    @staticmethod
    def loadImages():
        for i in range(2):
            SLib.loadIfNotInImageCache('Cooligan%d' % i, 'cooligan_%d.png' % i)

    def dataChanged(self):
        direction = self.parent.spritedata[5] & 0xF
        if direction > 1:
            direction = 0

        self.image = ImageCache['Cooligan%d' % direction]

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
            (-36, -48),
        )

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
        elif boxsize == 0 and (boxcolor == 1 or boxcolor == 2):
            self.image = ImageCache['Inv2x2']
        elif boxsize == 1 and (boxcolor == 1 or boxcolor == 2):
            self.image = ImageCache['Inv2x4']
        elif boxsize == 2 and (boxcolor == 1 or boxcolor == 2):
            self.image = ImageCache['Inv4x2']
        elif boxsize == 3 and (boxcolor == 1 or boxcolor == 2):
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
            (-4, -4)
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


class SpriteImage_MovingStoneBlock(SLib.SpriteImage_PivotRotationControlled):  # 350
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['MovingStoneBlock'],
            (-4, -4),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovingStoneBlock', 'moving_stone_block.png')


class SpriteImage_Pokey(SLib.SpriteImage):  # 351
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.spritebox.shown = False

        self.width = 32
        self.xOffset = -8

    @staticmethod
    def loadImages():
        ImageCache['PokeyTop'] = SLib.GetImg('pokey_top.png')
        ImageCache['PokeyTopU'] = SLib.GetImg('pokey_top_u.png')
        ImageCache['PokeyBottom'] = SLib.GetImg('pokey_bottom.png')
        ImageCache['PokeyBottomU'] = SLib.GetImg('pokey_bottom_u.png')

        for i in range(1, 5):
            ImageCache['PokeyMiddle%d' % i] = SLib.GetImg('pokey_middle_%d.png' % i)
            ImageCache['PokeyMiddle%dU' % i] = SLib.GetImg('pokey_middle_%d_u.png' % i)

    def dataChanged(self):
        self.nPieces = (self.parent.spritedata[5] & 0xF) + 3
        self.height = self.nPieces * 16 + 10

        self.upsideDown = self.parent.spritedata[4] & 1
        if self.upsideDown:
            self.yOffset = 4

        else:
            self.yOffset = -(self.nPieces * 16) + 8

        super().dataChanged()

    def paint(self, painter):
        if self.upsideDown:
            painter.drawPixmap(0, 0, ImageCache['PokeyBottomU'])

            for i in range(self.nPieces-2):
                painter.drawPixmap(0, (i+1) * 60, ImageCache['PokeyMiddle%dU' % ((i % 3) + 1)])
            
            painter.drawPixmap(0, (self.nPieces-1) * 60, ImageCache['PokeyTopU'])

        else:
            painter.drawPixmap(QtCore.QPointF(0, 22.5 + (self.nPieces-1) * 60), ImageCache['PokeyBottom'])

            for i in range(self.nPieces-2):
                painter.drawPixmap(QtCore.QPointF(0, (self.nPieces-i-1) * 60 - 37.5), ImageCache['PokeyMiddle%d' % ((i % 3) + 1)])

            painter.drawPixmap(0, 0, ImageCache['PokeyTop'])

        super().paint(painter)


class SpriteImage_SpikeTop(SLib.SpriteImage_StaticMultiple):  # 352, 447
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpikeTop00', 'spike_top.png')
        SLib.loadIfNotInImageCache('SpikeTop01', 'spike_top_left.png')
        SLib.loadIfNotInImageCache('SpikeTop02', 'spike_top_down.png')
        SLib.loadIfNotInImageCache('SpikeTop03', 'spike_top_right.png')
        SLib.loadIfNotInImageCache('SpikeTop10', 'spike_top_inv.png')
        SLib.loadIfNotInImageCache('SpikeTop11', 'spike_top_inv_left.png')
        SLib.loadIfNotInImageCache('SpikeTop12', 'spike_top_inv_down.png')
        SLib.loadIfNotInImageCache('SpikeTop13', 'spike_top_inv_right.png')

    def dataChanged(self):
        orientation = (self.parent.spritedata[5] >> 4) & 3
        direction = self.parent.spritedata[5] & 1
        
        if orientation & 1 == 1: #Wall
            if orientation & 2 == 2: #Right Wall
                self.xOffset = 0
                self.yOffset = 0 if not direction else -4
            else: #Left Wall
                self.xOffset = -4
                self.yOffset = -4 if not direction else 0
                
        else: #Floor/Ceiling
            if orientation & 2 == 2: #Ceiling
                self.xOffset = -4 if not direction else 0
                self.yOffset = 0
            else: #Ground
                self.xOffset = 0 if not direction else -4
                self.yOffset = -4
        
        self.image = ImageCache['SpikeTop%d%d' % (direction, orientation)]
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


class SpriteImage_PivotPipePiranhaFire(SLib.SpriteImage_PivotRotationControlled):  # 362
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
            (-32, -40)
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
    directions = ['U', 'D', 'R', 'L']
    
    def __init__(self, parent):
        super().__init__(parent, hasAux=True)

    def getPlatformWidth(self):
        width = (self.parent.spritedata[8] & 0xF) << 1

        if not width:
            return 4.5
        else:
            return width + 2.5

    def getPlatformOffset(self):
        return (-self.getPlatformWidth() * 8, 0)

    def getPlatformMoveDir(self):
        return self.directions[self.parent.spritedata[3] & 3]

    def getPlatformMoveDist(self):
        distance = self.parent.spritedata[7] >> 4

        if distance == 1:
            return 14
        else:
            return distance << 4


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
            (-16, -16),
        )

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


class SpriteImage_PivotSpinningFirebar(SLib.SpriteImage_PivotRotationControlled):  # 381
    affectImage = affectAUXImage = False

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75
        )

        self.parent.setZValue(500000)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FirebarBase0', 'firebar_base.png')
        SLib.loadIfNotInImageCache('FirebarBaseLong0', 'firebar_base_long.png')

    def dataChanged(self):
        wideBase = self.parent.spritedata[3] & 1

        self.image = ImageCache['FirebarBase0'] if not wideBase else ImageCache['FirebarBaseLong0']
        self.xOffset = 0 if not wideBase else -8

        super().dataChanged()


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
            (-4, -28)
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
            (-24, -28)
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


class SpriteImage_PinkMultiPlatform(SLib.SpriteImage):  # 388
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].alpha = 0.5

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PinkMultiPlatL', 'pink_multi_platform_l.png')
        SLib.loadIfNotInImageCache('PinkMultiPlatM', 'pink_multi_platform_m.png')
        SLib.loadIfNotInImageCache('PinkMultiPlatR', 'pink_multi_platform_r.png')
        SLib.loadIfNotInImageCache('PinkMultiPlatPivot', 'pink_multi_platform_pivot.png')
        SLib.loadIfNotInImageCache('PinkMultiPlatChain', 'pink_multi_platform_chain.png')

    def dataChanged(self):
        platformCount = min((self.parent.spritedata[3] >> 4) + 2, 6)
        startRot = (self.parent.spritedata[5] >> 4) * 22.5
        radius = (self.parent.spritedata[5] & 0xF)
        platformWidth = (self.parent.spritedata[8] & 0xF) + 2
        drawCoins = (self.parent.spritedata[9] & 0xF0) != 0
        coinsOnPlatforms = self.parent.spritedata[9] >> 4
        coinAmount = self.parent.spritedata[9] & 0xF

        if radius == 0:
            radius = 6

        width = 0
        if not drawCoins or platformWidth + 0.5 > coinAmount:
            width = (radius * 2 + platformWidth + 0.5) * 60
        else:
            width = (radius * 2 + coinAmount) * 60
            
        height = (radius + 1) * 120
        xOffset = -(width - 60) * 0.5
        yOffset = -(height - 120) * 0.5 - 60

        # Create the aux image
        self.aux[0].setSize(width, height, xOffset, yOffset)
        pix = QtGui.QPixmap(width, height)
        pix.fill(Qt.transparent)

        # Create a painter with the image
        paint = QtGui.QPainter(pix)
        paintT = paint.transform()

        # Draw pivot in the middle
        paint.translate(width * 0.5, height * 0.5 + 30)
        paint.drawPixmap(-30, -30, ImageCache['PinkMultiPlatPivot'])
        
        paint.rotate(180 - startRot)

        # Draw all chains
        for i in range(int(platformCount)):
            paint.drawTiledPixmap(-radius * 60, -15, radius * 60 - 15, 30, ImageCache['PinkMultiPlatChain'], 15)
            paint.rotate(-(360.0 / platformCount))

        paint.setTransform(paintT) # Recover transform

        # Draw all platforms
        for i in range(int(platformCount)):
            angle = math.radians(-i * (360.0 / platformCount) - startRot)
            x = width * 0.5 + math.cos(angle) * radius * 60
            y = height * 0.5 + 30 + math.sin(angle) * radius * 60
            
            paint.drawPixmap(x - platformWidth * 30 - 14, y - 30, ImageCache['PinkMultiPlatL'])
            paint.drawTiledPixmap(x - platformWidth * 30 + 60, y - 30, (platformWidth - 2) * 60, 60, ImageCache['PinkMultiPlatM'])
            paint.drawPixmap(x + platformWidth * 30 - 61, y - 30, ImageCache['PinkMultiPlatR'])

            # Draw coins on platforms if needed
            if drawCoins and i % coinsOnPlatforms == 0:
                paint.drawTiledPixmap(x - coinAmount * 30, y - 90, coinAmount * 60, 60, SLib.Tiles[30].main)

        # Complete the image and send it the the aux
        paint = None
        self.aux[0].image = pix
        super().dataChanged()


class SpriteImage_Roy(SLib.SpriteImage_Static):  # 389
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Roy'],
            (-36, -44)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Roy', 'roy.png')


class SpriteImage_JungleBridge(SLib.SpriteImage_PivotRotationControlled):  # 390, 645
    affectAUXImage = False

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.offset = (-4, -4)

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)
        self.aux[0].alpha = 0.5

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[1].alpha = 0.5

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[2].alpha = 0.5

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('JungleBridgeL', 'jungle_bridge_l.png')
        SLib.loadIfNotInImageCache('JungleBridgeM', 'jungle_bridge_m.png')
        SLib.loadIfNotInImageCache('JungleBridgeR', 'jungle_bridge_r.png')
        SLib.loadIfNotInImageCache('JungleBridgePillar', 'jungle_bridge_pillar.png')
        SLib.loadIfNotInImageCache('JungleBridgePillarTop', 'jungle_bridge_pillar_top.png')
        SLib.loadIfNotInImageCache('JungleBridgePivot', 'jungle_bridge_pivot.png')

    def dataChanged(self):
        self.affectImage = (self.parent.spritedata[3] & 1) == 0
        self.width = ((self.parent.spritedata[8] & 0x1F) << 4) + 8
        self.height = 24

        if self.width == 8:
            self.width = 24

        pix = QtGui.QPixmap(self.width * 3.75, self.height * 3.75)
        pix.fill(Qt.transparent)

        painter = QtGui.QPainter(pix)
        painter.drawTiledPixmap(15, 15, self.width * 3.75 - 30, 60, ImageCache['JungleBridgeM'], (ImageCache['JungleBridgeM'].width() - (self.width * 3.75 - 30)) * 0.5)
        painter.drawPixmap(0, 0, ImageCache['JungleBridgeL'])
        painter.drawPixmap(self.width * 3.75 - 75, 0, ImageCache['JungleBridgeR'])
        painter.end()
        del painter

        self.image = pix

        self.aux[0].setImage(ImageCache['JungleBridgePivot'], self.width * 1.875 - 45, self.height * 1.875 - 45)
        self.aux[1].setImage(ImageCache['JungleBridgePillarTop'], self.width * 1.875 - 45, self.height * 1.875 - 45)

        pix = QtGui.QPixmap(60, 645)
        pix.fill(Qt.transparent)

        painter = QtGui.QPainter(pix)
        painter.drawTiledPixmap(0, 0, 60, 645, ImageCache['JungleBridgePillar'])
        painter.end()
        del painter

        self.aux[2].setImage(pix, self.width * 1.875 - 30, self.height * 1.875 - 45 + 175)

        super().dataChanged()


class SpriteImage_GrayCrystal(SLib.SpriteImage_PivotRotationControlled):  # 391
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

        self.yOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('3x3IceBlock0', '3x3_ice_block_0.png')
        SLib.loadIfNotInImageCache('3x3IceBlock1', '3x3_ice_block_1.png')

    def dataChanged(self):
        type = self.parent.spritedata[8] & 0xF
        if type > 1:
            type = 0

        self.image = ImageCache['3x3IceBlock%d' % type]
        self.xOffset = -28 if type == 1 else -8

        super().dataChanged()


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


class SpriteImage_LanternPlatform(SLib.SpriteImage_PivotRotationControlled):  # 400
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.offset = (-4, -4)

    @staticmethod
    def loadImages():
        ImageCache['LanternPlatformLeft'] = SLib.GetImg('lantern_platform_l.png')
        ImageCache['LanternPlatformMiddle'] = SLib.GetImg('lantern_platform_m.png')
        ImageCache['LanternPlatformRight'] = SLib.GetImg('lantern_platform_r.png')
        ImageCache['LanternPlatformLeftLamp'] = SLib.GetImg('lantern_platform_l_lamp.png')
        ImageCache['LanternPlatformMiddleScrew'] = SLib.GetImg('lantern_platform_m_screw.png')
        ImageCache['LanternPlatformRightLamp'] = SLib.GetImg('lantern_platform_r_lamp.png')

    def dataChanged(self):
        self.height = 24

        self.screwPlacement = ((self.parent.spritedata[4] & 0x1) << 4) + ((self.parent.spritedata[5] & 0xF0) >> 4) # <- max length is 31
        self.platformLength = self.parent.spritedata[8] & 0b00011111 # <- max length is 31
        self.lanternPlacement = self.parent.spritedata[5] & 0x3 # values repeat after 3

        if self.lanternPlacement == 0:
            self.width = ((self.platformLength + 2) << 4) + 8
        elif self.lanternPlacement == 1 or self.lanternPlacement == 2:
            self.width = ((self.platformLength + 3) << 4) + 8
        else:
            self.width = ((self.platformLength + 4) << 4) + 8

        pix = QtGui.QPixmap(self.width * 3.75, self.height * 3.75)
        pix.fill(Qt.transparent)

        painter = QtGui.QPainter(pix)

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

        painter.end()
        del painter

        self.image = pix

        super().dataChanged()


class SpriteImage_Iggy(SLib.SpriteImage_Static):  # 403
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Iggy'],
            (-20, -48)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Iggy', 'iggy.png')


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


class SpriteImage_Toad(SLib.SpriteImage_StaticMultiple):  # 408, 543
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.yOffset = -32

    @staticmethod
    def loadImages():
        if 'ToadR' in ImageCache:
            return

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
            (-8, -28),
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

        self.aux[0].setImage(ImageCache['BeanstalkTendrilStretched%d%s' % (direction, tendrilType)])

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

        self.xOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SnowyBoxes1', 'snowy_box_1.png')
        SLib.loadIfNotInImageCache('SnowyBoxes2', 'snowy_box_2.png')
        SLib.loadIfNotInImageCache('SnowyBoxes3', 'snowy_box_3.png')

    def dataChanged(self):

        amount = self.parent.spritedata[5]

        if amount == 2:
            self.image = ImageCache['SnowyBoxes2']
            self.yOffset = -48
        elif amount == 3:
            self.image = ImageCache['SnowyBoxes3']
            self.yOffset = -96
        else:
            self.image = ImageCache['SnowyBoxes1']
            self.yOffset = 0

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
        super().__init__(parent, rotatable=False)

    def setWidth(self):
        self.width = (self.parent.spritedata[8] & 0xF) * 16 + 48
        self.height = (self.parent.spritedata[9] & 0xF) * 16 + 48


class SpriteImage_Fliprus(SLib.SpriteImage_StaticMultiple):  # 441
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.yOffset = -12
        self.xOffset = -8

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


class SpriteImage_BigSnowyBoxes(SLib.SpriteImage_StaticMultiple):  # 444
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigSnowyBoxes1', 'snowy_box_big_1.png')
        SLib.loadIfNotInImageCache('BigSnowyBoxes2', 'snowy_box_big_2.png')
        SLib.loadIfNotInImageCache('BigSnowyBoxes3', 'snowy_box_big_3.png')

    def dataChanged(self):

        amount = self.parent.spritedata[5]

        if amount == 2:
            self.image = ImageCache['BigSnowyBoxes2']
            self.yOffset = -48
        elif amount == 3:
            self.image = ImageCache['BigSnowyBoxes3']
            self.yOffset = -96
        else:
            self.image = ImageCache['BigSnowyBoxes1']
            self.yOffset = 0

        super().dataChanged()


class SpriteImage_FliprusSnowball(SLib.SpriteImage_Static):  # 446
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Snowball'],
        )

        self.yOffset = -4

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Snowball', 'snowball.png')


class SpriteImage_NabbitPlacement(SLib.SpriteImage_Static):  # 451
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Nabbit'],
            (-8, -16)
        )

        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))
        self.aux[0].setSize(1410, 810, -1110, -570)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Nabbit', 'nabbit.png')


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


class SpriteImage_BowserJrCastle(SLib.SpriteImage_Static):  # 459
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['BowserJrCastle'],
            (-16, -20),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BowserJrCastle', 'bowser_jr_castle.png')


class SpriteImage_Bowser(SLib.SpriteImage_Static):  # 462
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['Bowser'],
            (-52, -80),
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


class SpriteImage_BowserFireball(SLib.SpriteImage):  # 468
    def __init__(self, parent):
        super().__init__(parent, 3.75)

        self.offset = (-12, -4)
        self.width = 24
        self.height = 24

        self.spritebox.shown = False
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setImage(ImageCache['BowserFireball'], -44, -52, True)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BowserFireball', 'bowser_fireball.png')


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
            (-196, -312)
        )

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


class SpriteImage_GiantKoopaTroopa(SLib.SpriteImage_StaticMultiple):  # 476
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantKoopaShellG', 'giant_koopatroopa_shell_green.png')
        SLib.loadIfNotInImageCache('GiantKoopaShellR', 'giant_koopatroopa_shell_red.png')
        SLib.loadIfNotInImageCache('GiantKoopatroopaG', 'giant_koopatroopa_green.png')
        SLib.loadIfNotInImageCache('GiantKoopatroopaR', 'giant_koopatroopa_red.png')

    def dataChanged(self):
        shellcolour = self.parent.spritedata[5] & 1
        inshell = (self.parent.spritedata[5] >> 4) & 1

        if inshell:
            self.offset = (-12, -16)
            self.image = ImageCache['GiantKoopaShellR' if shellcolour else 'GiantKoopaShellG']
        else:
            self.offset = (-24, -40)
            self.image = ImageCache['GiantKoopatroopaR' if shellcolour else 'GiantKoopatroopaG']

        super().dataChanged()


class SpriteImage_FinalBowserJr(SLib.SpriteImage_Static):  # 477
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['FinalBowserJr'],
            (-16, -16)
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FinalBowserJr', 'bowser_jr_final.png')


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

        self.yOffset = -8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WaddlewingWL', 'waddlewing_walk_left.png')
        SLib.loadIfNotInImageCache('WaddlewingWR', 'waddlewing_walk_right.png')
        SLib.loadIfNotInImageCache('WaddlewingFL', 'waddlewing_fly_left.png')
        SLib.loadIfNotInImageCache('WaddlewingFR', 'waddlewing_fly_right.png')
        SLib.loadIfNotInImageCache('WaddlewingWLA', 'waddlewing_walk_left_acorn.png')
        SLib.loadIfNotInImageCache('WaddlewingWRA', 'waddlewing_walk_right_acorn.png')
        SLib.loadIfNotInImageCache('WaddlewingFLA', 'waddlewing_fly_left_acorn.png')
        SLib.loadIfNotInImageCache('WaddlewingFRA', 'waddlewing_fly_right_acorn.png')

    def dataChanged(self):
        acorn = 'A' if self.parent.spritedata[4] & 1 else ''
        spawnAs = 'F' if (self.parent.spritedata[5] >> 4) & 1 else 'W'
        direction = 'R' if (self.parent.spritedata[5] & 3) == 2 else 'L'
        self.image = ImageCache['Waddlewing%s%s%s' % (spawnAs, direction, acorn)]

        if (direction == 'L' and acorn == 'A'):
            self.xOffset = -12
        elif (direction == 'L' and spawnAs == 'W' and acorn == '') or (direction == 'R' and spawnAs == 'F' and acorn == 'A'):
            self.xOffset = -4
        else:
            self.xOffset = -8
        
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
    rotations = [0, 11.25, 22.5, 33.75, 45, -11.25, -22.5, -33.75, -45]

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
        self.width = (self.parent.spritedata[8] & 0xF) * 16 + 16
        if self.width == 16: self.width *= 2

        if self.width / 16 < 3:
            self.height = 240
        else:
            self.height = 256

        zOrder = (self.parent.spritedata[5] & 0xF) + 1
        self.parent.setZValue(24999 // zOrder)

        pix = QtGui.QPixmap(self.width * 3.75, self.height * 3.75)
        pix.fill(Qt.transparent)
        painter = QtGui.QPainter(pix)

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

        painter = None
        rot = (self.parent.spritedata[3] >> 4)
        if rot > 8:
            rot = 0
        self.transformed = pix.transformed(QTransform().rotate(-self.rotations[rot]))
        
        oldxOffset = (pix.width() - self.transformed.width()) / 7.5
        oldyOffset = (pix.height() - self.transformed.height()) / 7.5
        self.xOffset = math.floor(oldxOffset / 4) * 4
        self.yOffset = math.floor(oldyOffset / 4) * 4

        self.imgxOffset = (oldxOffset - self.xOffset)
        self.imgyOffset = (oldyOffset - self.yOffset)
        self.width = self.transformed.width() / 3.75 + self.imgxOffset
        self.height = self.transformed.height() / 3.75 + self.imgyOffset
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(self.imgxOffset * 3.75, self.imgyOffset * 3.75, self.transformed)


class SpriteImage_MovingBonePlatform(SpriteImage_PlatformBase):  # 491, 492, 627
    def __init__(self, parent):
        super().__init__(parent, hasAux = parent.type != 627)
        
    def getPlatformWidth(self):
        width = (self.parent.spritedata[8] & 0xF) + 1
        if width == 1:
            width = 2
            
        return width + 0.5

    def getPlatformType(self):
        return 'B'

    def getPlatformMoveDir(self):
        if self.parent.spritedata[3] & 1:
            return 'D' if self.parent.type == 491 else 'L'
        else:
            return 'U' if self.parent.type == 491 else 'R'

    def getPlatformMoveDist(self):
        return self.parent.spritedata[7] >> 4


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


class SpriteImage_ShootingStar(SLib.SpriteImage):  # 507
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.spritebox.shown = False
        self.dimensions = (-4, -4, 24, 20)

        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setImage(ImageCache['ShootingStar'], -12, -52, True)

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


class SpriteImage_GhostShipBlock(SLib.SpriteImage_PivotRotationControlled):  # 512
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

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
        self.w = self.parent.spritedata[8] + 3
        self.h = self.parent.spritedata[9] + 3
        self.width = self.w << 4
        self.height = self.h << 4

        pix = QtGui.QPixmap(self.width * 3.75, self.height * 3.75)
        pix.fill(Qt.transparent)

        painter = QtGui.QPainter(pix)

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

        painter.end()
        del painter

        self.image = pix

        super().dataChanged()


class SpriteImage_PipeJoint(SLib.SpriteImage):  # 513
    def __init__(self, parent):
        super().__init__(parent, 3.75)

        self.spritebox.shown = False
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setImage(ImageCache['PipeJoint'], -4, -4, True)

        self.width = 32
        self.height = 32

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeJoint', 'pipe_joint.png')


class SpriteImage_PipeJointSmall(SLib.SpriteImage):  # 514
    def __init__(self, parent):
        super().__init__(parent, 3.75)

        self.spritebox.shown = False
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setImage(ImageCache['PipeJointMini'], -4, -4, True)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeJointMini', 'pipe_mini_joint.png')


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


class SpriteImage_MiniPipeRight(SpriteImage_Pipe):  # 516
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)

        self.direction = 3
        self.type = 'Mini'

    def dataChanged(self):
        self.offset = (0, 0)
        self.height, self.pipeHeight = 16, 60

        length = self.parent.spritedata[5]
        self.width, self.pipeWidth = length * 16, length * 60

        if self.hasTop:
            self.width += 16
            self.topX = self.pipeWidth

        super().dataChanged()


class SpriteImage_MiniPipeLeft(SpriteImage_Pipe):  # 517
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)

        self.direction = 2
        self.type = 'Mini'

    def dataChanged(self):
        self.yOffset = 0
        self.height, self.pipeHeight = 16, 60
        self.middleX = 0

        length = self.parent.spritedata[5]
        self.width, self.pipeWidth = length * 16, length * 60

        if self.hasTop:
            self.width += 16
            self.middleX += 60

        self.xOffset = -self.width + 16

        super().dataChanged()


class SpriteImage_MiniPipeUp(SpriteImage_Pipe):  # 518
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)

        self.type = 'Mini'

    def dataChanged(self):
        self.xOffset = 0
        self.width, self.pipeWidth = 16, 60
        self.middleY = 0

        length = self.parent.spritedata[5]
        self.height, self.pipeHeight = length * 16, length * 60

        if self.hasTop:
            self.height += 16
            self.middleY += 60

        self.yOffset = -self.height + 16

        super().dataChanged()


class SpriteImage_MiniPipeDown(SpriteImage_Pipe):  # 519
    def __init__(self, parent, scale=3.75):
        super().__init__(parent, scale)

        self.direction = 1
        self.type = 'Mini'

    def dataChanged(self):
        self.offset = (0, 0)
        self.width, self.pipeWidth = 16, 60

        length = self.parent.spritedata[5]
        self.height, self.pipeHeight = length * 16, length * 60

        if self.hasTop:
            self.height += 16
            self.topY = self.pipeHeight

        super().dataChanged()


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
            (-4, -4),
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


class SpriteImage_RockyWrench(SLib.SpriteImage_Static):  # 536
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['RockyWrench'],
            (-4, -20),
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

class SpriteImage_RollingIceBlock(SLib.SpriteImage_StaticMultiple):  # 539
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RollingIceBlock', 'ice_block_rolling.png')

    def dataChanged(self):
        width = (self.parent.spritedata[8] & 0xF) + 1
        height = (self.parent.spritedata[9] & 0xF) + 1

        self.image = ImageCache['RollingIceBlock'].scaled(width * 60, height * 60)
        self.yOffset = -height * 16

        super().dataChanged()


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
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))
        self.aux[0].setImage(ImageCache['NabbitMetal'], -15, 0)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Sprite548', 'sprite548.png')
        SLib.loadIfNotInImageCache('NabbitMetal', 'nabbit_metal.png')


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


class SpriteImage_RotatableMuncher(SLib.SpriteImage):  # 552
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False
        self.dimensions = (-4, -4, 24, 24)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MuncherReg', 'muncher.png')

    def dataChanged(self):
        self.rotation = (self.parent.spritedata[3] >> 4) * 22.5
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        oldT = painter.transform()
        painter.translate(45, 45)
        painter.rotate(-self.rotation)
        painter.drawPixmap(-30, -30, ImageCache['MuncherReg'])
        painter.setTransform(oldT)


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

        image = ImageCache['WendyFloor']
        self.aux[0].setImage(image, -image.width() * 0.5, 180 - image.height())
        self.aux[0].alpha = 0.5
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
        self.w = (self.parent.spritedata[8] & 0xF) + 1
        self.h = (self.parent.spritedata[9] & 0xF) + 1

        if self.w < 2:
            self.w = 2
        if self.h < 2:
            self.h = 2
        
        self.width = self.w << 4
        self.height = self.h << 4

        pix = QtGui.QPixmap(self.width * 3.75, self.height * 3.75)
        pix.fill(Qt.transparent)
        painter = QtGui.QPainter(pix)
        
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

        painter = None
        rotation = (self.parent.spritedata[3] >> 4) * 22.5
        self.transformed = pix.transformed(QTransform().rotate(-rotation))
        
        oldxOffset = (pix.width() - self.transformed.width()) / 7.5
        oldyOffset = (pix.height() - self.transformed.height()) / 7.5
        self.xOffset = math.floor(oldxOffset / 4) * 4
        self.yOffset = math.floor(oldyOffset / 4) * 4

        self.imgxOffset = (oldxOffset - self.xOffset)
        self.imgyOffset = (oldyOffset - self.yOffset)
        self.width = self.transformed.width() / 3.75 + self.imgxOffset
        self.height = self.transformed.height() / 3.75 + self.imgyOffset
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(self.imgxOffset * 3.75, self.imgyOffset * 3.75, self.transformed)


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
            (-76, -16)
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



class SpriteImage_StoneSpike(SLib.SpriteImage_Static):  # 579, 580
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['StoneSpike'],
            (-8, -16),
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


class SpriteImage_TorpedoLauncherRed(SLib.SpriteImage_Static):  # 596
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
            ImageCache['TorpedoLauncherRed'],
            (-16, -16),
        )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TorpedoLauncherRed', 'torpedo_launcher_red.png')


class SpriteImage_NoCoinArea(SLib.SpriteImage):  # 598
    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('NoCoinArea0', 'no_coin_area_platform.png')
        SLib.loadIfNotInImageCache('NoCoinArea1', 'no_coin_area.png')

    def dataChanged(self):
        self.areaType = self.parent.spritedata[4] & 1
        self.width = (self.parent.spritedata[8] & 0xF) * 16 + 16
        self.height = (self.parent.spritedata[9] & 0xF) * 16 + 16
        super().dataChanged()

    def paint(self, painter):
        super().paint(painter)
        painter.drawTiledPixmap(0, 0, self.width * 3.75, self.height * 3.75, ImageCache['NoCoinArea%d' % self.areaType])


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


class SpriteImage_BigBuzzyBeetle(SLib.SpriteImage_StaticMultiple):  # 606
    yOffsets = (0, 0, -4, 4)

    def __init__(self, parent):
        super().__init__(
            parent,
            3.75,
        )

        self.xOffset = -4

    @staticmethod
    def loadImages():
        for i in range(4):
            SLib.loadIfNotInImageCache('BigBuzzyBeetle%d' % i, 'big_buzzy_beetle_%d.png' % i)

    def dataChanged(self):
        type = self.parent.spritedata[5] & 3
        self.image = ImageCache['BigBuzzyBeetle%d' % type]
        self.yOffset = SpriteImage_BigBuzzyBeetle.yOffsets[type]

        super().dataChanged()


class SpriteImage_IggyRoom(SLib.SpriteImage):  # 609
    def __init__(self, parent):
        super().__init__(parent, 3.75)
        self.aux.append(SLib.AuxiliaryImage(parent, 0, 0))

        image = ImageCache['IggyRoom']
        self.aux[0].setImage(image, -image.width() * 0.5, 540 - image.height())
        self.aux[0].alpha = 0.5
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


class SpriteImage_GearLuigi(SLib.SpriteImage_PivotRotationControlled):  # 675
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
        self.aux[0].alpha = 0.5
        self.aux[0].setImage(ImageCache['ThankYouSign'], -495, -810)
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
    36: SpriteImage_EventControllerZone,
    37: SpriteImage_EventControllerAnd,
    38: SpriteImage_EventControllerOr,
    39: SpriteImage_EventControllerRandom,
    40: SpriteImage_EventControllerChainer,
    41: SpriteImage_LocationTrigger,
    42: SpriteImage_EventControllerMultiChainer,
    43: SpriteImage_EventControllerTimer,
    44: SpriteImage_CoinRing,
    45: SpriteImage_StarCoin,
    46: SpriteImage_LineControlledStarCoin,
    47: SpriteImage_StarCoin,
    48: SpriteImage_MovementStarCoin,
    49: SpriteImage_RedCoin,
    50: SpriteImage_GreenCoin,
    51: SpriteImage_MontyMole,
    52: SpriteImage_GrrrolPassage,
    53: SpriteImage_Porcupuffer,
    54: SpriteImage_YoshiBerry,
    55: SpriteImage_KoopaTroopa,
    57: SpriteImage_FishBone,
    58: SpriteImage_Grrrol,
    59: SpriteImage_QBlock,
    60: SpriteImage_BrickBlock,
    61: SpriteImage_InvisiBlock,
    62: SpriteImage_PivotPipePiranhaUp,
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
    82: SpriteImage_PivotPipePiranhaDown,
    83: SpriteImage_PivotPipePiranhaLeft,
    84: SpriteImage_PivotPipePiranhaRight,
    85: SpriteImage_FlameChomp,
    86: SpriteImage_Urchin,
    87: SpriteImage_PivotCoin,
    88: SpriteImage_Water,
    89: SpriteImage_Lava,
    90: SpriteImage_Poison,
    91: SpriteImage_Quicksand,
    92: SpriteImage_Fog,
    93: SpriteImage_GhostFog,
    94: SpriteImage_BouncyCloud,
    95: SpriteImage_BouncyCloudL,
    96: SpriteImage_Lamp,
    97: SpriteImage_BackCenter,
    98: SpriteImage_PipeEnemyGenerator,
    99: SpriteImage_MegaUrchin,
    101: SpriteImage_CheepCheep,
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
    117: SpriteImage_Pendulum,
    118: SpriteImage_ControllerSpinning,
    119: SpriteImage_Lakitu,
    120: SpriteImage_SpinyCheep,
    123: SpriteImage_SandPillar,
    124: SpriteImage_SandPillar,
    125: SpriteImage_BulletBill,
    126: SpriteImage_BanzaiBill,
    127: SpriteImage_BulletBill,
    128: SpriteImage_HomingBanzaiBill,
    129: SpriteImage_JumpingCheepCheep,
    132: SpriteImage_ShiftingRectangle,
    133: SpriteImage_SpineCoaster,
    135: SpriteImage_Thwomp,
    136: SpriteImage_GiantThwomp,
    137: SpriteImage_DryBones,
    138: SpriteImage_BigDryBones,
    139: SpriteImage_PipeUp,
    140: SpriteImage_PipeDown,
    141: SpriteImage_PipeLeft,
    142: SpriteImage_PipeRight,
    143: SpriteImage_BabyYoshi,
    145: SpriteImage_PalmTree,
    146: SpriteImage_MovementPipe,
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
    174: SpriteImage_BanzaiBillCannon,
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
    188: SpriteImage_GrrrolSpawner,
    190: SpriteImage_PivotQBlock,
    191: SpriteImage_PivotBrickBlock,
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
    224: SpriteImage_BabyYoshi,
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
    243: SpriteImage_BabyYoshi,
    246: SpriteImage_BoomBoom,
    247: SpriteImage_PricklyGoomba,
    248: SpriteImage_GhostHouseBoxFrame,
    249: SpriteImage_Wiggler,
    250: SpriteImage_GreyBlock,
    251: SpriteImage_FloatingBubble,
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
    292: SpriteImage_SyncBurner,
    293: SpriteImage_RotatingBurner,
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
    322: SpriteImage_Blooper,
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
    362: SpriteImage_PivotPipePiranhaFire,
    363: SpriteImage_Chest,
    365: SpriteImage_BabyYoshi,
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
    381: SpriteImage_PivotSpinningFirebar,
    382: SpriteImage_Dragoneel,
    383: SpriteImage_Wendy,
    385: SpriteImage_Ludwig,
    386: SpriteImage_MeltableIceChunk,
    388: SpriteImage_PinkMultiPlatform,
    389: SpriteImage_Roy,
    390: SpriteImage_JungleBridge,
    391: SpriteImage_GrayCrystal,
    393: SpriteImage_3x3IceBlock,
    395: SpriteImage_Starman,
    396: SpriteImage_BeanstalkLeaf,
    397: SpriteImage_QBlock,
    398: SpriteImage_BrickBlock,
    400: SpriteImage_LanternPlatform,
    402: SpriteImage_CoinRing,
    403: SpriteImage_Iggy,
    404: SpriteImage_PipeUp,
    405: SpriteImage_Crash,
    407: SpriteImage_BumpPlatform,
    408: SpriteImage_Toad,
    409: SpriteImage_ChainChomp,
    410: SpriteImage_CastlePlatformLudwig,
    416: SpriteImage_HomingBanzaiBill,
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
    444: SpriteImage_BigSnowyBoxes,
    446: SpriteImage_FliprusSnowball,
    447: SpriteImage_SpikeTop,
    451: SpriteImage_NabbitPlacement,
    452: SpriteImage_Crash,
    455: SpriteImage_ClapCrowd,
    457: SpriteImage_WobbyBonePlatform,
    458: SpriteImage_GoldenPipeDown,
    459: SpriteImage_BowserJrCastle,
    462: SpriteImage_Bowser,
    464: SpriteImage_BowserBridge,
    465: SpriteImage_KamekFloor,
    467: SpriteImage_BowserShutter,
    468: SpriteImage_BowserFireball,
    469: SpriteImage_Peach,
    470: SpriteImage_CoinRing,
    471: SpriteImage_MediumGoomba,
    472: SpriteImage_BigGoomba,
    473: SpriteImage_MegaBowser,
    474: SpriteImage_ToadHouseCannon,
    475: SpriteImage_BigQBlock,
    476: SpriteImage_GiantKoopaTroopa,
    477: SpriteImage_FinalBowserJr,
    478: SpriteImage_BowserJrBlock,
    479: SpriteImage_Crash,
    480: SpriteImage_StarCoin,
    481: SpriteImage_WaddleWing,
    482: SpriteImage_MechaCheep,
    483: SpriteImage_SpinningFirebar,
    484: SpriteImage_ControllerSpinOne,
    485: SpriteImage_MetalBarGearbox,
    486: SpriteImage_FrameSetting,
    488: SpriteImage_Dragoneel,
    491: SpriteImage_MovingBonePlatform,
    492: SpriteImage_MovingBonePlatform,
    493: SpriteImage_World7Platform,
    496: SpriteImage_Coin,
    499: SpriteImage_MovingGrassPlatform,
    500: SpriteImage_BowserAmp,
    502: SpriteImage_BowserAmp,
    503: SpriteImage_Flagpole,
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
    534: SpriteImage_MovingPlatform,
    535: SpriteImage_MovingPlatform,
    536: SpriteImage_RockyWrench,
    537: SpriteImage_Wrench,
    538: SpriteImage_Crash,
    539: SpriteImage_RollingIceBlock,
    542: SpriteImage_MushroomPlatform,
    543: SpriteImage_Toad,
    544: SpriteImage_MushroomMovingPlatform,
    546: SpriteImage_Flowers,
    548: SpriteImage_Sprite548,
    549: SpriteImage_DesertBlock,
    550: SpriteImage_GiantPipePiranha,
    552: SpriteImage_RotatableMuncher,
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
    582: SpriteImage_HomingBanzaiBillCannon,
    583: SpriteImage_HomingBanzaiBillCannon,
    584: SpriteImage_MetalBox,
    587: SpriteImage_JumpingMechaCheep,
    588: SpriteImage_DeepCheep,
    589: SpriteImage_MediumDeepCheep,
    590: SpriteImage_EepCheep,
    591: SpriteImage_MediumEepCheep,
    593: SpriteImage_SumoBro,
    595: SpriteImage_Goombrat,
    596: SpriteImage_TorpedoLauncherRed,
    598: SpriteImage_NoCoinArea,
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
    631: SpriteImage_Flagpole,
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
    646: SpriteImage_BanzaiBillCannon,
    647: SpriteImage_BanzaiBillCannon,
    648: SpriteImage_HomingBanzaiBillCannon,
    649: SpriteImage_HomingBanzaiBillCannon,
    651: SpriteImage_Spike,
    652: SpriteImage_Parabeetle,
    653: SpriteImage_KingBill,
    655: SpriteImage_SnakeBlock,
    658: SpriteImage_MovingLinePlatform,
    659: SpriteImage_BigGrrrol,
    661: SpriteImage_SumoBro,
    662: SpriteImage_CoinRing,
    663: SpriteImage_Coin,
    667: SpriteImage_PipeCannon,
    669: SpriteImage_MovementControlledTowerBlock,
    671: SpriteImage_GrrrolPassage,
    673: SpriteImage_TileGod,
    675: SpriteImage_GearLuigi,
    676: SpriteImage_CastlePlatform,
    678: SpriteImage_InvisiBlock,
    679: SpriteImage_MovementPipe,
    681: SpriteImage_ArrowSignboard,
    682: SpriteImage_WaterPlant,
    683: SpriteImage_QBlock,
    686: SpriteImage_PSwitch,
    687: SpriteImage_Parabomb,
    688: SpriteImage_MetalBox,
    691: SpriteImage_ThankYouSign,
    692: SpriteImage_BrickBlock,
    693: SpriteImage_Pendulum,
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
    706: SpriteImage_PivotBrickBlock,
    707: SpriteImage_PivotQBlock,
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
