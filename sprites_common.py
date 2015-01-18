#!/usr/bin/python
# -*- coding: latin-1 -*-

# Reggie Next - New Super Mario Bros. Wii / New Super Mario Bros 2 Level Editor
# Milestone 2 Alpha 4
# Copyright (C) 2009-2014 Treeki, Tempus, angelsl, JasonP27, Kamek64,
# MalStar1000, RoadrunnerWMC

# This file is part of Reggie Next.

# Reggie Next is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Reggie Next is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Reggie Next.  If not, see <http://www.gnu.org/licenses/>.


# sprites_common.py
# Contains code to render sprite images common to many Mario games


################################################################
################################################################

# Imports
import math
import random

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt


import spritelib as SLib
ImageCache = SLib.ImageCache



class SpriteImage_WoodenPlatform(SLib.SpriteImage): # 23, 31, 50, 103, 106, 122
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        # Load the two batches separately because another sprite only
        # loads the first three.
        if 'WoodenPlatformL' not in ImageCache:
            ImageCache['WoodenPlatformL'] = SLib.GetImg('wood_platform_left.png')
            ImageCache['WoodenPlatformM'] = SLib.GetImg('wood_platform_middle.png')
            ImageCache['WoodenPlatformR'] = SLib.GetImg('wood_platform_right.png')
        if 'StonePlatformL' not in ImageCache:
            ImageCache['StonePlatformL'] = SLib.GetImg('stone_platform_left.png')
            ImageCache['StonePlatformM'] = SLib.GetImg('stone_platform_middle.png')
            ImageCache['StonePlatformR'] = SLib.GetImg('stone_platform_right.png')
            ImageCache['BonePlatformL'] = SLib.GetImg('bone_platform_left.png')
            ImageCache['BonePlatformM'] = SLib.GetImg('bone_platform_middle.png')
            ImageCache['BonePlatformR'] = SLib.GetImg('bone_platform_right.png')

    def paint(self, painter):
        super().paint(painter)

        if self.color == 0:
            color = 'Wooden'
        elif self.color == 1:
            color = 'Stone'
        elif self.color == 2:
            color = 'Bone'

        if self.width > 32:
            painter.drawTiledPixmap(27, 0, ((self.width * 1.5) - 51), 24, ImageCache[color + 'PlatformM'])

        if self.width == 24:
            # replicate glitch effect foRotControlled by sprite 50
            painter.drawPixmap(0, 0, ImageCache[color + 'PlatformR'])
            painter.drawPixmap(8, 0, ImageCache[color + 'PlatformL'])
        else:
            # normal rendering
            painter.drawPixmap((self.width - 16) * 1.5, 0, ImageCache[color + 'PlatformR'])
            painter.drawPixmap(0, 0, ImageCache[color + 'PlatformL'])


class SpriteImage_DSStoneBlock(SLib.SpriteImage): # 27, 28
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'DSBlockTopLeft' in ImageCache: return
        ImageCache['DSBlockTopLeft'] = SLib.GetImg('dsblock_topleft.png')
        ImageCache['DSBlockTop'] = SLib.GetImg('dsblock_top.png')
        ImageCache['DSBlockTopRight'] = SLib.GetImg('dsblock_topright.png')
        ImageCache['DSBlockLeft'] = SLib.GetImg('dsblock_left.png')
        ImageCache['DSBlockRight'] = SLib.GetImg('dsblock_right.png')
        ImageCache['DSBlockBottomLeft'] = SLib.GetImg('dsblock_bottomleft.png')
        ImageCache['DSBlockBottom'] = SLib.GetImg('dsblock_bottom.png')
        ImageCache['DSBlockBottomRight'] = SLib.GetImg('dsblock_bottomright.png')

    def dataChanged(self):
        super().dataChanged()

        # get size
        width = self.parent.spritedata[5] & 7
        if width == 0: width = 1
        byte5 = self.parent.spritedata[4]
        self.width = (16 + (width << 4))
        self.height = (16 << ((byte5 & 0x30) >> 4)) - 4

    def paint(self, painter):
        super().paint(painter)

        middle_width = (self.width - 32) * 1.5
        middle_height = (self.height * 1.5) - 16
        bottom_y = (self.height * 1.5) - 8
        right_x = (self.width - 16) * 1.5

        painter.drawPixmap(0, 0, ImageCache['DSBlockTopLeft'])
        painter.drawTiledPixmap(24, 0, middle_width, 8, ImageCache['DSBlockTop'])
        painter.drawPixmap(right_x, 0, ImageCache['DSBlockTopRight'])

        painter.drawTiledPixmap(0, 8, 24, middle_height, ImageCache['DSBlockLeft'])
        painter.drawTiledPixmap(right_x, 8, 24, middle_height, ImageCache['DSBlockRight'])

        painter.drawPixmap(0, bottom_y, ImageCache['DSBlockBottomLeft'])
        painter.drawTiledPixmap(24, bottom_y, middle_width, 8, ImageCache['DSBlockBottom'])
        painter.drawPixmap(right_x, bottom_y, ImageCache['DSBlockBottomRight'])


class SpriteImage_StarCoin(SLib.SpriteImage_Static): # 32, 155, 389
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['StarCoin'],
            (0, 3),
            )


class SpriteImage_Switch(SLib.SpriteImage_StaticMultiple): # 40, 41, 42, 153
    def __init__(self, parent):
        super().__init__(parent)
        self.switchType = ''

    @staticmethod
    def loadImages():

        if 'QSwitch' not in ImageCache:
            q = SLib.GetImg('q_switch.png', True)
            ImageCache['QSwitch'] = QtGui.QPixmap.fromImage(q)
            ImageCache['QSwitchU'] = QtGui.QPixmap.fromImage(q.mirrored(True, True))
        
        if 'PSwitch' not in ImageCache:
            p = SLib.GetImg('p_switch.png', True)
            ImageCache['PSwitch'] = QtGui.QPixmap.fromImage(p)
            ImageCache['PSwitchU'] = QtGui.QPixmap.fromImage(p.mirrored(True, True))

        if 'ESwitch' not in ImageCache:
            e = SLib.GetImg('e_switch.png', True)
            ImageCache['ESwitch'] = QtGui.QPixmap.fromImage(e)
            ImageCache['ESwitchU'] = QtGui.QPixmap.fromImage(e.mirrored(True, True))

    def dataChanged(self):

        upsideDown = self.parent.spritedata[5] & 1

        if not upsideDown:
            self.image = ImageCache[self.switchType + 'Switch']
        else:
            self.image = ImageCache[self.switchType + 'SwitchU']

        super().dataChanged()


class SpriteImage_OldStoneBlock(SLib.SpriteImage): # 30, 81, 82, 83, 84, 85, 86
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryTrackObject(parent, 16, 16, SLib.AuxiliaryTrackObject.Horizontal))
        self.spikesL = False
        self.spikesR = False
        self.spikesT = False
        self.spikesB = False

        self.hasMovementAux = True

    @staticmethod
    def loadImages():
        if 'OldStoneTL' in ImageCache: return
        ImageCache['OldStoneTL'] = SLib.GetImg('oldstone_tl.png')
        ImageCache['OldStoneT'] = SLib.GetImg('oldstone_t.png')
        ImageCache['OldStoneTR'] = SLib.GetImg('oldstone_tr.png')
        ImageCache['OldStoneL'] = SLib.GetImg('oldstone_l.png')
        ImageCache['OldStoneM'] = SLib.GetImg('oldstone_m.png')
        ImageCache['OldStoneR'] = SLib.GetImg('oldstone_r.png')
        ImageCache['OldStoneBL'] = SLib.GetImg('oldstone_bl.png')
        ImageCache['OldStoneB'] = SLib.GetImg('oldstone_b.png')
        ImageCache['OldStoneBR'] = SLib.GetImg('oldstone_br.png')
        ImageCache['SpikeU'] = SLib.GetImg('spike_up.png')
        ImageCache['SpikeL'] = SLib.GetImg('spike_left.png')
        ImageCache['SpikeR'] = SLib.GetImg('spike_right.png')
        ImageCache['SpikeD'] = SLib.GetImg('spike_down.png')

    def dataChanged(self):
        super().dataChanged()

        size = self.parent.spritedata[5]
        height = (size & 0xF0) >> 4
        width = size & 0xF
        if self.parent.type == 30:
            height = 1 if height == 0 else height
            width = 1 if width == 0 else width
        self.width = width * 16 + 16
        self.height = height * 16 + 16

        if self.spikesL: # left spikes
            self.xOffset = -16
            self.width += 16
        if self.spikesT: # top spikes
            self.yOffset = -16
            self.height += 16
        if self.spikesR: # right spikes
            self.width += 16
        if self.spikesB: # bottom spikes
            self.height += 16

        # now set up the track
        if self.hasMovementAux:
            direction = self.parent.spritedata[2] & 3
            distance = (self.parent.spritedata[4] & 0xF0) >> 4
            if direction > 3: direction = 0

            if direction <= 1: # horizontal
                self.aux[0].direction = 1
                self.aux[0].setSize(self.width + (distance * 16), self.height)
            else: # vertical
                self.aux[0].direction = 2
                self.aux[0].setSize(self.width, self.height + (distance * 16))

            if direction == 0 or direction == 3: # right, down
                self.aux[0].setPos(0, 0)
            elif direction == 1: # left
                self.aux[0].setPos(-distance * 24, 0)
            elif direction == 2: # up
                self.aux[0].setPos(0, -distance * 24)
        else:
            self.aux[0].setSize(0, 0)

    def paint(self, painter):
        super().paint(painter)

        blockX = 0
        blockY = 0
        type = self.parent.type
        width = self.width * 1.5
        height = self.height * 1.5

        if self.spikesL: # left spikes
            painter.drawTiledPixmap(0, 0, 24, height, ImageCache['SpikeL'])
            blockX = 24
            width -= 24
        if self.spikesT: # top spikes
            painter.drawTiledPixmap(0, 0, width, 24, ImageCache['SpikeU'])
            blockY = 24
            height -= 24
        if self.spikesR: # right spikes
            painter.drawTiledPixmap(blockX + width-24, 0, 24, height, ImageCache['SpikeR'])
            width -= 24
        if self.spikesB: # bottom spikes
            painter.drawTiledPixmap(0, blockY + height-24, width, 24, ImageCache['SpikeD'])
            height -= 24

        column2x = blockX + 24
        column3x = blockX + width - 24
        row2y = blockY + 24
        row3y = blockY + height - 24

        painter.drawPixmap(blockX, blockY, ImageCache['OldStoneTL'])
        painter.drawTiledPixmap(column2x, blockY, width - 48, 24, ImageCache['OldStoneT'])
        painter.drawPixmap(column3x, blockY, ImageCache['OldStoneTR'])

        painter.drawTiledPixmap(blockX, row2y, 24, height - 48, ImageCache['OldStoneL'])
        painter.drawTiledPixmap(column2x, row2y, width - 48, height-48, ImageCache['OldStoneM'])
        painter.drawTiledPixmap(column3x, row2y, 24, height - 48, ImageCache['OldStoneR'])

        painter.drawPixmap(blockX, row3y, ImageCache['OldStoneBL'])
        painter.drawTiledPixmap(column2x, row3y, width - 48, 24, ImageCache['OldStoneB'])
        painter.drawPixmap(column3x, row3y, ImageCache['OldStoneBR'])


class SpriteImage_LiquidOrFog(SLib.SpriteImage): # 64, 138, 139, 216, 358, 374, 435
    
    class FreeAuxiliaryItem_LiquidOrFog(QtWidgets.QGraphicsItem):
        """
        An item that acts sort of like an auxiliary item, but isn't one. Biggest difference is that the sprite isn't its parent.
        It paints liquid or fog in a zone or location.
        """
        def __init__(self, imageObj):
            super().__init__()
            self.ImageObj = imageObj

            self.OuterRect = None
            self.BoundingRect = QtCore.QRectF(0, 0, 0, 0)
            self.mode = 'z' # 'z' = zones, 'l' = locations

        def boundingRect(self):
            """
            Required by Qt
            """
            return self.BoundingRect

        def paint(self, painter, option, widget=None):
            painter.setClipRect(option.rect)

            y, h = self.y(), self.OuterRect.height()

            # Get info
            selfTop = self.OuterRect.y()
            spriteTop = self.ImageObj.parent.y()
            y = spriteTop
            h -= spriteTop - selfTop

            # Create the new bounding rect
            print(h)
            y = max(0, y)
            h = max(0, h)
            self.BoundingRect = QtCore.QRectF(self.OuterRect)
            self.setY(y)
            self.BoundingRect.setHeight(h)

            # # Determine the rise and top to be drawn, if any
            # riseToDraw = self.ImageObj.rise if self.ImageObj.drawCrest else self.ImageObj.riseCrestless          

            # Temp stuff: paint the bounding rect
            painter.setBrush(QtGui.QBrush(Qt.red))
            painter.save()
            painter.setOpacity(0.2)
            painter.drawRect(0, 0, self.BoundingRect.width(), self.BoundingRect.height())
            painter.restore()
            self.scene().update()

            # # Paint the water top
            # if self.waterTopUsesRise:
            #     wTNRPH = self.waterTopNonRisePartHeight
            #     crestToDraw = self.imageObj.crest if self.imageObj.drawCrest else self.imageObj.mid
            #     painter.drawTiledPixmap(0, self.waterTop, self.BoundingRect.width(), wTNRPH, crestToDraw)
            #     painter.drawTiledPixmap(0, self.waterTop + wTNRPH, self.BoundingRect.width(), riseToDraw.height() - wTNRPH, riseToDraw, 0, wTNRPH)
            # else:
            #     drawCrest = self.imageObj.drawCrest
            #     if self.waterTopCrestOverride is not None:
            #         drawCrest = self.waterTopCrestOverride
            #     if drawCrest:
            #         painter.drawTiledPixmap(0, self.waterTop, self.BoundingRect.width(), min(self.waterDepth, self.imageObj.crest.height()), self.imageObj.crest)
            #         painter.drawTiledPixmap(0, self.waterTop + self.imageObj.crest.height(), self.BoundingRect.width(), max(0, self.waterDepth - self.imageObj.crest.height()), self.imageObj.mid)
            #     else:
            #         painter.drawTiledPixmap(0, self.waterTop, self.BoundingRect.width(), self.waterDepth, self.imageObj.mid)

            # # Paint the rise, if going up
            # if self.imageObj.risingHeight > 0:
            #     painter.drawTiledPixmap(0, 0, self.BoundingRect.width(), riseToDraw.height(), riseToDraw)

            # # Paint the rise, if going down
            # if self.imageObj.risingHeight < 0:
            #     painter.drawTiledPixmap(0, -self.imageObj.risingHeight, self.BoundingRect.width(), riseToDraw.height(), riseToDraw)


        def updateSize(self):
            """
            Updates the size and position of the aux
            """
            if None in (self.OuterRect, self.ImageObj.rise, self.ImageObj.riseCrestless): return

            # # Reset stuff
            # self.waterTop = 0
            # self.waterDepth = 0
            # self.riseTop = 0
            # self.waterTopUsesRise = False
            # self.waterTopNonRisePartHeight = 0
            # self.waterTopCrestOverride = None

            # # Determine the rise to be drawn, if any
            # riseToDraw = self.imageObj.rise if self.imageObj.drawCrest else self.imageObj.riseCrestless

            # # Realign
            # self.alignToZone()
            # width = self.BoundingRect.width()

            # # Keep track of the old position
            # oldy, oldh = self.y(), self.BoundingRect.height()

            # # First, calculate simple offsets
            # self.waterTop = 0
            # if self.imageObj.top < 0:
            #     self.waterTop = 0
            #     self.waterTopCrestOverride = False
            #     if self.imageObj.risingHeight > 0:
            #         self.waterTop += self.imageObj.risingHeight
            # self.waterDepth = self.BoundingRect.height() - self.imageObj.top
            # if self.waterDepth < riseToDraw.height():
            #     self.waterDepth = riseToDraw.height()
            # if self.imageObj.risingHeight > 0:
            #     self.waterTop = self.imageObj.risingHeight
            #     if self.imageObj.top < 0:
            #         self.waterTop += self.imageObj.top
            # elif self.imageObj.risingHeight < 0:
            #     self.riseTop = -self.imageObj.risingHeight
            # if self.BoundingRect.height() - self.imageObj.top < riseToDraw.height():
            #     self.waterTopUsesRise = True
            #     self.waterTopNonRisePartHeight = self.BoundingRect.height() - self.imageObj.top
            #     self.waterTopNonRisePartHeight = max(0, self.waterTopNonRisePartHeight)

            # print('------------------')
            # print(self.waterTop)
            # print(self.waterDepth)
            # print(self.riseTop)
            # print(self.waterTopUsesRise)
            # print(self.waterTopNonRisePartHeight)
            # print(self.waterTopCrestOverride)

            # # Determine the top edge
            # y = self.imageObj.top

            # # Don't allow negative y
            # y = max(0, y)

            # # Determine the height
            # h = self.BoundingRect.height() - y

            # # Special case: if there is a rise going up
            # if self.imageObj.risingHeight > 0:
            #     y = self.imageObj.top - self.imageObj.risingHeight
            #     h += self.imageObj.risingHeight

            # # Don't allow negative height
            # h = max(h, 0)

            # # Special case: if the water to be drawn is smaller than the rise image
            # if y + self.waterTop > self.BoundingRect.height() - riseToDraw.height():
            #     h = riseToDraw.height()
            #     if self.imageObj.risingHeight > 0:
            #         h += self.imageObj.risingHeight

            # # Special case: if there is a rise going down
            # if self.imageObj.risingHeight < 0:
            #     h = max(h, -self.imageObj.risingHeight + riseToDraw.height())

            # # Set the settings
            # self.setPos(0, y)
            # self.BoundingRect.setHeight(h)

            # # Update the old area
            # self.parent.scene().update(self.parent.x(), self.parent.y() + oldy, width, oldh)

        def paintLiquidInRect(self, painter, rect):
            """
            Generic liquid-in-rect painter
            """
            return
        #     rx, ry, rw, rh = rect.topLeft().x(), rect.topLeft().y(), rect.width(), rect.height()

        #     drawRise = self.risingHeight != 0
        #     drawCrest = self.drawCrest
        #     drawRiseCrest = drawCrest

        #     # Get positions
        #     offsetFromTop = self.top
        #     if offsetFromTop < 0:
        #         offsetFromTop = 0
        #         drawCrest = False # off the top of the rect; no crest
        #     if self.top > rh:
        #         # the sprite is below the rect; don't draw anything
        #         return

        #     # If all that fits in the rect is some of the crest, determine how much
        #     if drawCrest:
        #         crestSizeRemoval = (ry + offsetFromTop + self.crest.height()) - (ry + rh)
        #         if crestSizeRemoval < 0: crestSizeRemoval = 0
        #         crestHeight = self.crest.height() - crestSizeRemoval

        #     # Determine where to put the rise image
        #     offsetRise = offsetFromTop - self.risingHeight
        #     riseToDraw = self.rise
        #     if not drawRiseCrest:
        #         riseToDraw = self.riseCrestless

        #     # Draw everything!
        #     if drawCrest:
        #         painter.drawTiledPixmap(0, offsetFromTop, rw, crestHeight, self.crest)
        #         painter.drawTiledPixmap(0, offsetFromTop + crestHeight, rw, rh - crestHeight - offsetFromTop, self.mid)
        #     else:
        #         painter.drawTiledPixmap(0, offsetFromTop, rw, rh - offsetFromTop - 4, self.mid)
        #     if drawRise:
        #         painter.drawTiledPixmap(0, offsetRise, rw, riseToDraw.height(), riseToDraw)

    def __init__(self, parent):
        super().__init__(parent)

        self.updateSceneAfterZoneMoved = True
        self.updateSceneAfterLocationMoved = True

        self.crest = None
        self.mid = None
        self.rise = None
        self.riseCrestless = None

        self.top = 0

        self.drawCrest = False
        self.risingHeight = 0

        self.paintZone = False

        self.LiqOrFogAux = self.FreeAuxiliaryItem_LiquidOrFog(self)
        self.parent.scene().addItem(self.LiqOrFogAux)

    def dataChanged(self):
        super().dataChanged()
        
        z = SLib.getNearestZoneTo(self.parent.objx, self.parent.objy)
        if z is not None:
            self.LiqOrFogAux.OuterRect = QtCore.QRectF(z.BoundingRect)

            self.LiqOrFogAux.setX(z.x() + 4)
            self.LiqOrFogAux.setY(z.y())
            self.LiqOrFogAux.OuterRect.setWidth(z.BoundingRect.width() - 8)
            self.LiqOrFogAux.OuterRect.setHeight(z.BoundingRect.height())

            self.LiqOrFogAux.updateSize()

    def positionChanged(self):
        super().positionChanged()

        z = SLib.getNearestZoneTo(self.parent.objx, self.parent.objy)
        if z is not None:
            self.LiqOrFogAux.OuterRect = QtCore.QRectF(z.BoundingRect)

            self.LiqOrFogAux.setX(z.x() + 4)
            self.LiqOrFogAux.setY(z.y())
            self.LiqOrFogAux.OuterRect.setWidth(z.BoundingRect.width() - 8)
            self.LiqOrFogAux.OuterRect.setHeight(z.BoundingRect.height())

            self.LiqOrFogAux.updateSize()


class SpriteImage_HammerBro(SLib.SpriteImage_Static): # 95, 308
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['HammerBro'],
            (-8, -24),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('HammerBro', 'hammerbro.png')


class SpriteImage_UnusedBlockPlatform(SLib.SpriteImage): # 97, 107, 132, 160
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.size = (48, 48)
        self.isDark = False
        self.drawPlatformImage = True

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('UnusedPlatform', 'unused_platform.png')
        SLib.loadIfNotInImageCache('UnusedPlatformDark', 'unused_platform_dark.png')

    def paint(self, painter):
        super().paint(painter)
        if not self.drawPlatformImage: return

        pixmap = ImageCache['UnusedPlatformDark'] if self.isDark else ImageCache['UnusedPlatform']
        pixmap = pixmap.scaled(
            self.width * 1.5, self.height * 1.5,
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation,
            )
        painter.drawPixmap(0, 0, pixmap)


class SpriteImage_Amp(SLib.SpriteImage_Static): # 104, 108
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Amp'],
            (-8, -8),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Amp', 'amp.png')


class SpriteImage_SpikedStake(SLib.SpriteImage): # 137, 140, 141, 142
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.SpikeLength = ((37 * 16) + 41) / 1.5
        # (16 mid sections + an end section), accounting for image/sprite size difference
        self.dir = 'down'

    @staticmethod
    def loadImages():
        if 'StakeM0up' not in ImageCache:
            for dir in ['up', 'down', 'left', 'right']:
                ImageCache['StakeM0' + dir] = SLib.GetImg('stake_%s_m_0.png' % dir)
                ImageCache['StakeM1' + dir] = SLib.GetImg('stake_%s_m_1.png' % dir)
                ImageCache['StakeE0' + dir] = SLib.GetImg('stake_%s_e_0.png' % dir)
                ImageCache['StakeE1' + dir] = SLib.GetImg('stake_%s_e_1.png' % dir)

    def dataChanged(self):
        super().dataChanged()

        distance = self.parent.spritedata[3] >> 4
        if distance == 0:
            x = 16
        elif distance == 1:
            x = 7
        elif distance == 2:
            x = 14
        elif distance == 3:
            x = 10
        elif distance >= 8:
            x = 20
        else:
            x = 0
        distance = x + 1 # In order to hide one side of the track behind the image.

        w = 66
        L = ((37 * 16) + 41) / 1.5 # (16 mid sections + an end section), accounting for image/sprite size difference

        if self.dir == 'up':
            self.aux[0].setPos(36, 24 - (distance * 24))
            self.aux[0].setSize(16, distance*16)
        elif self.dir == 'down':
            self.aux[0].setPos(36, (L * 1.5) - 24)
            self.aux[0].setSize(16, distance*16)
        elif self.dir == 'left':
            self.aux[0].setPos(24 - (distance * 24), 36)
            self.aux[0].setSize(distance * 16, 16)
        elif self.dir == 'right':
            self.aux[0].setPos((L * 1.5) - 24, 36)
            self.aux[0].setSize(distance * 16, 16)

    def paint(self, painter):
        super().paint(painter)

        color = self.parent.spritedata[3] & 15
        if color == 2 or color == 3 or color == 7:
            mid = ImageCache['StakeM1' + self.dir]
            end = ImageCache['StakeE1' + self.dir]
        else:
            mid = ImageCache['StakeM0' + self.dir]
            end = ImageCache['StakeE0' + self.dir]

        tiles = 16
        tilesize = 37
        endsize = 41
        width = 100

        if self.dir == 'up':
            painter.drawPixmap(0, 0, end)
            painter.drawTiledPixmap(0, endsize, width, tilesize * tiles, mid)
        elif self.dir == 'down':
            painter.drawTiledPixmap(0, 0, width, tilesize * tiles, mid)
            painter.drawPixmap(0, (self.height * 1.5) - endsize, end)
        elif self.dir == 'left':
            painter.drawPixmap(0, 0, end)
            painter.drawTiledPixmap(endsize, 0, tilesize * tiles, width, mid)
        elif self.dir == 'right':
            painter.drawTiledPixmap(0, 0, tilesize * tiles, width, mid)
            painter.drawPixmap((self.width * 1.5) - endsize, 0, end)


class SpriteImage_ScrewMushroom(SLib.SpriteImage): # 172, 382
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.hasBolt = False
        self.size = (122, 190)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Bolt', 'bolt.png')
        if 'ScrewShroomT' not in ImageCache:
            ImageCache['ScrewShroomT'] = SLib.GetImg('screw_shroom_top.png')
            ImageCache['ScrewShroomM'] = SLib.GetImg('screw_shroom_middle.png')
            ImageCache['ScrewShroomB'] = SLib.GetImg('screw_shroom_bottom.png')

    def dataChanged(self):
        super().dataChanged()

        # I wish I knew what this does
        SomeOffset = self.parent.spritedata[3]
        if SomeOffset == 0 or SomeOffset > 8: SomeOffset = 8

        self.height = 206 if self.hasBolt else 190
        self.yOffset = SomeOffset * -16
        if self.hasBolt:
            self.yOffset -= 16

    def paint(self, painter):
        super().paint(painter)

        y = 0
        if self.hasBolt:
            painter.drawPixmap(70, 0, ImageCache['Bolt'])
            y += 24
        painter.drawPixmap(0, y, ImageCache['ScrewShroomT'])
        painter.drawTiledPixmap(76, y + 93, 31, 172, ImageCache['ScrewShroomM'])
        painter.drawPixmap(76, y + 253, ImageCache['ScrewShroomB'])


class SpriteImage_Door(SLib.SpriteImage): # 182, 259, 276, 277, 278, 421, 452
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.doorName = 'Door'
        self.doorDimensions = (0, 0, 32, 48)
        self.entranceOffset = (0, 48)

        self.aux.append(SLib.AuxiliaryRectOutline(parent, 24, 24))
        self.aux[0].setIsBehindSprite(False)

    @staticmethod
    def loadImages():
        if 'DoorU' in ImageCache: return
        doors = {'Door': 'door', 'GhostDoor': 'ghost_door', 'TowerDoor': 'tower_door', 'CastleDoor': 'castle_door', 'BowserDoor': 'bowser_door'}
        transform90 = QtGui.QTransform()
        transform180 = QtGui.QTransform()
        transform270 = QtGui.QTransform()
        transform90.rotate(90)
        transform180.rotate(180)
        transform270.rotate(270)

        for door, filename in doors.items():
            image = SLib.GetImg('%s.png' % filename, True)
            ImageCache[door + 'U'] = QtGui.QPixmap.fromImage(image)
            ImageCache[door + 'R'] = QtGui.QPixmap.fromImage(image.transformed(transform90))
            ImageCache[door + 'D'] = QtGui.QPixmap.fromImage(image.transformed(transform180))
            ImageCache[door + 'L'] = QtGui.QPixmap.fromImage(image.transformed(transform270))

    def dataChanged(self):
        super().dataChanged()

        rotstatus = self.parent.spritedata[4]
        if rotstatus & 1 == 0:
            direction = 0
        else:
            direction = (rotstatus & 0x30) >> 4

        if direction > 3: direction = 0
        doorName = self.doorName
        doorSize = self.doorDimensions
        if direction == 0:
            self.image = ImageCache[doorName + 'U']
            self.dimensions = doorSize
            paintEntrancePos = True
        elif direction == 1:
            self.image = ImageCache[doorName + 'L']
            self.dimensions = (
                (doorSize[2] / 2) + doorSize[0] - doorSize[3],
                doorSize[1] + (doorSize[3] - (doorSize[2] / 2)),
                doorSize[3],
                doorSize[2],
                )
            paintEntrancePos = False
        elif direction == 2:
            self.image = ImageCache[doorName + 'D']
            self.dimensions = (
                doorSize[0],
                doorSize[1] + doorSize[3],
                doorSize[2],
                doorSize[3],
                )
            paintEntrancePos = False
        elif direction == 3:
            self.image = ImageCache[doorName + 'R']
            self.dimensions = (
                doorSize[0] + (doorSize[2] / 2),
                doorSize[1] + (doorSize[3] - (doorSize[2] / 2)),
                doorSize[3],
                doorSize[2],
                )
            paintEntrancePos = False

        self.aux[0].setSize(
            *(
                (0, 0, 0, 0),
                (24, 24) + self.entranceOffset,
                )[1 if paintEntrancePos else 0]
            )

    def paint(self, painter):
        super().paint(painter)
        painter.setOpacity(self.alpha)
        painter.drawPixmap(0, 0, self.image)
        painter.setOpacity(1)


class SpriteImage_GiantBubble(SLib.SpriteImage): # 205, 226
    def __init__(self, parent):
        super().__init__(parent)
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
        arrow = None

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



class SpriteImage_Block(SLib.SpriteImage): # 207, 208, 209, 221, 255, 256, 402, 403, 422, 423
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.tilenum = 1315
        self.contentsNybble = 5
        self.contentsOverride = None
        self.eightIsMushroom = False
        self.twelveIsMushroom = False
        self.rotates = False

    def dataChanged(self):
        super().dataChanged()

        # SET CONTENTS
        # In the blocks.png file:
        # 0 = Empty, 1 = Coin, 2 = Mushroom, 3 = Fire Flower, 4 = Propeller, 5 = Penguin Suit,
        # 6 = Mini Shroom, 7 = Star, 8 = Continuous Star, 9 = Yoshi Egg, 10 = 10 Coins,
        # 11 = 1-up, 12 = Vine, 13 = Spring, 14 = Shroom/Coin, 15 = Ice Flower, 16 = Toad

        if self.contentsOverride is not None:
            contents = self.contentsOverride
        else:
            contents = self.parent.spritedata[self.contentsNybble] & 0xF

        if contents == 2: # 1 and 2 are always fire flowers
            contents = 3

        if contents == 12 and self.twelveIsMushroom:
            contents = 2 # 12 is a mushroom on some types
        if contents == 8 and self.eightIsMushroom:
            contents = 2 # same as above, but for type 8

        self.image = ImageCache['Blocks'][contents]

        # SET UP ROTATION
        if self.rotates:
            transform = QtGui.QTransform()
            transform.translate(12, 12)

            angle = (self.parent.spritedata[4] & 0xF0) >> 4
            leftTilt = self.parent.spritedata[3] & 1

            angle *= (45.0 / 16.0)

            if leftTilt == 0:
                transform.rotate(angle)
            else:
                transform.rotate(360.0 - angle)

            transform.translate(-12, -12)
            self.parent.setTransform(transform)

    def paint(self, painter):
        super().paint(painter)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if self.tilenum < len(SLib.Tiles):
            painter.drawPixmap(0, 0, SLib.Tiles[self.tilenum].main)
        painter.drawPixmap(0, 0, self.image)


class SpriteImage_SpecialCoin(SLib.SpriteImage_Static): # 253, 371, 390
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SpecialCoin'],
            )


class SpriteImage_Pipe(SLib.SpriteImage): # 254, 339, 353, 377, 378, 379, 380, 450
    Top = 0
    Bottom = 1
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.parent.setZValue(24999)

        self.direction = 'U'
        self.color = 'Green'
        self.length1 = 4
        self.length2 = 4

    @staticmethod
    def loadImages():
        if 'PipeTopGreen' not in ImageCache:
            for color in ('Green', 'Red', 'Yellow', 'Blue'):
                ImageCache['PipeTop%s' % color] = SLib.GetImg('pipe_%s_top.png' % color)
                ImageCache['PipeMiddleV%s' % color] = SLib.GetImg('pipe_%s_middle.png' % color)
                ImageCache['PipeBottom%s' % color] = SLib.GetImg('pipe_%s_bottom.png' % color)
                ImageCache['PipeLeft%s' % color] = SLib.GetImg('pipe_%s_left.png' % color)
                ImageCache['PipeMiddleH%s' % color] = SLib.GetImg('pipe_%s_center.png' % color)
                ImageCache['PipeRight%s' % color] = SLib.GetImg('pipe_%s_right.png' % color)

    def dataChanged(self):
        super().dataChanged()
        # sprite types:
        # 339 = Moving Pipe Facing Up
        # 353 = Moving Pipe Facing Down
        # 377 = Pipe Up
        # 378 = Pipe Down
        # 379 = Pipe Right
        # 380 = Pipe Left
        # 450 = Enterable Pipe Up
        
        size = max(self.length1, self.length2) * 16

        if self.direction in 'LR': # horizontal
            self.width = size
            self.height = 32
            if self.direction == 'R': # faces right
                self.xOffset = 0
            else: # faces left
                self.xOffset = 16 - size
            self.yOffset = 0

        else: # vertical
            self.width = 32
            self.height = size
            if self.direction == 'D': # faces down
                self.yOffset = 0
            else: # faces up
                self.yOffset = 16 - size
            self.xOffset = 0

        if self.direction == 'U': # facing up
            self.yOffset = 16 - size
        else: # facing down
            self.yOffset = 0

    def paint(self, painter):
        super().paint(painter)

        color = self.color
        xsize = self.width * 1.5
        ysize = self.height * 1.5

        # Assume moving pipes
        length1 = self.length1 * 24
        length2 = self.length2 * 24
        low = min(length1, length2)
        high = max(length1, length2)

        if self.direction == 'U':
            y1 = ysize - low
            y2 = ysize - high

            if length1 != length2:
                # draw semi-transparent pipe
                painter.save()
                painter.setOpacity(0.5)
                painter.drawPixmap(0, y2, ImageCache['PipeTop%s' % color])
                painter.drawTiledPixmap(0, y2 + 24, 48, high - 24, ImageCache['PipeMiddleV%s' % color])
                painter.restore()

            # draw opaque pipe
            painter.drawPixmap(0, y1, ImageCache['PipeTop%s' % color])
            painter.drawTiledPixmap(0, y1 + 24, 48, low - 24, ImageCache['PipeMiddleV%s' % color])

        elif self.direction == 'D':

            if length1 != length2:
                # draw semi-transparent pipe
                painter.save()
                painter.setOpacity(0.5)
                painter.drawTiledPixmap(0, 0, 48, high - 24, ImageCache['PipeMiddleV%s' % color])
                painter.drawPixmap(0, high - 24, ImageCache['PipeBottom%s' % color])
                painter.restore()

            # draw opaque pipe
            painter.drawTiledPixmap(0, 0, 48, low - 24, ImageCache['PipeMiddleV%s' % color])
            painter.drawPixmap(0, low - 24, ImageCache['PipeBottom%s' % color])

        elif self.direction == 'R':

            if length1 != length2:
                # draw semi-transparent pipe
                painter.save()
                painter.setOpacity(0.5)
                painter.drawPixmap(high, 0, ImageCache['PipeRight%s' % color])
                painter.drawTiledPixmap(0, 0, high - 24, 48, ImageCache['PipeMiddleH%s' % color])
                painter.restore()

            # draw opaque pipe
            painter.drawPixmap(low - 24, 0, ImageCache['PipeRight%s' % color])
            painter.drawTiledPixmap(0, 0, low - 24, 48, ImageCache['PipeMiddleH%s' % color])

        else: # left

            if length1 != length2:
                # draw semi-transparent pipe
                painter.save()
                painter.setOpacity(0.5)
                painter.drawTiledPixmap(0, 0, high - 24, 48, ImageCache['PipeMiddleH%s' % color])
                painter.drawPixmap(high - 24, 0, ImageCache['PipeLeft%s' % color])
                painter.restore()

            # draw opaque pipe
            painter.drawTiledPixmap(24, 0, low - 24, 48, ImageCache['PipeMiddleH%s' % color])
            painter.drawPixmap(0, 0, ImageCache['PipeLeft%s' % color])


class SpriteImage_PipeStationary(SpriteImage_Pipe): # 254, 377, 378, 379, 380, 450
    def __init__(self, parent):
        super().__init__(parent)
        self.length = 4

    def dataChanged(self):
        self.color = (
            'Green', 'Red', 'Yellow', 'Blue',
            )[(self.parent.spritedata[5] >> 4) % 4]

        self.length1 = self.length
        self.length2 = self.length
        
        super().dataChanged()


class SpriteImage_UnusedGiantDoor(SLib.SpriteImage_Static): # 319, 320
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['UnusedGiantDoor'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('UnusedGiantDoor', 'unused_giant_door.png')


class SpriteImage_RollingHillWithPipe(SLib.SpriteImage): # 355, 360
    def __init__(self, parent):
        super().__init__(parent)
        self.aux.append(SLib.AuxiliaryCircleOutline(parent, 800))


class SpriteImage_ToadHouseBalloon(SLib.SpriteImage_StaticMultiple): # 411, 412
    def __init__(self, parent):
        super().__init__(parent)
        self.hasHandle = False
        self.livesNum = 0
        # self.livesnum: 0 = 1 life, 1 = 2 lives, etc (1 + value)

    @staticmethod
    def loadImages():
        if 'ToadHouseBalloon0' in ImageCache: return
        for handleCacheStr, handleFileStr in (('', ''), ('Handle', 'handle_')):
            for num in range(4):
                ImageCache['ToadHouseBalloon' + handleCacheStr + str(num)] = \
                    SLib.GetImg('mg_house_balloon_' + handleFileStr + str(num) + '.png')

    def dataChanged(self):

        self.image = ImageCache['ToadHouseBalloon' + ('Handle' if self.hasHandle else '') + str(self.livesNum)]

        self.xOffset = 8 - (self.image.width() / 3)

        super().dataChanged()
