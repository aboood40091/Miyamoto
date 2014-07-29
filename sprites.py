#!/usr/bin/python
# -*- coding: latin-1 -*-

# Reggie! - New Super Mario Bros. Wii Level Editor
# Version Next Milestone 2 Alpha 0
# Copyright (C) 2009-2014 Treeki, Tempus, angelsl, JasonP27, Kamek64,
# MalStar1000, RoadrunnerWMC

# This file is part of Reggie!.

# Reggie! is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Reggie! is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Reggie!.  If not, see <http://www.gnu.org/licenses/>.



# sprites.py
# Contains code to render NSMBW sprite images


################################################################
################################################################

# Imports
import math
import random

from PyQt5 import QtCore, QtGui
Qt = QtCore.Qt


import spritelib as SLib
ImageCache = SLib.ImageCache



# ---- Low-Level Classes ----


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

    def updateSize(self):
        super().updateSize()

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

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1

        if not upsideDown:
            self.image = ImageCache[self.switchType + 'Switch']
        else:
            self.image = ImageCache[self.switchType + 'SwitchU']

        super().updateSize()


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

    def updateSize(self):
        super().updateSize()

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
    def __init__(self, parent):
        super().__init__(parent)
        self.updateSceneAfterPaint = True

        self.crest = None
        self.mid = None
        self.rise = None
        self.riseCrestless = None

        self.top = 0

        self.drawCrest = False
        self.risingHeight = 0

        self.paintZone = False
        self.paintLoc = False

    def updateSize(self):
        super().updateSize()
        self.parent.updateScene()

    def realViewZone(self, painter, zoneRect, viewRect):
        """
        Real view zone painter for liquids/fog
        """
        if not self.paintZone: return

        # (0, 0) is the top-left corner of the zone

        zx, zy, zw, zh = zoneRect.topLeft().x(), zoneRect.topLeft().y(), zoneRect.width(), zoneRect.height()

        drawRise = self.risingHeight != 0
        drawCrest = self.drawCrest

        # Get positions
        offsetFromTop = (self.top * 1.5) - zy
        if offsetFromTop <= 4:
            offsetFromTop = 4
            drawCrest = False # off the top of the zone; no crest
        if self.top > (zy + zh) / 1.5:
            # the sprite is below the zone; don't draw anything
            return

        # If all that fits in the zone is some of the crest, determine how much
        if drawCrest:
            crestSizeRemoval = (zy + offsetFromTop + self.crest.height()) - (zy + zh) + 4
            if crestSizeRemoval < 0: crestSizeRemoval = 0
            crestHeight = self.crest.height() - crestSizeRemoval

        # Determine where to put the rise image
        offsetRise = offsetFromTop - (self.risingHeight * 24)
        riseToDraw = self.rise
        if offsetRise < 4: # close enough to the top zone border
            offsetRise = 4
            riseToDraw = self.riseCrestless
        if not drawCrest:
            riseToDraw = self.riseCrestless

        if drawCrest:
            painter.drawTiledPixmap(4, offsetFromTop, zw - 8, crestHeight, self.crest)
            painter.drawTiledPixmap(4, offsetFromTop + crestHeight, zw - 8, zh - crestHeight - offsetFromTop - 4, self.mid)
        else:
            painter.drawTiledPixmap(4, offsetFromTop, zw - 8, zh - offsetFromTop - 4, self.mid)
        if drawRise:
            painter.drawTiledPixmap(4, offsetRise, zw - 8, riseToDraw.height(), riseToDraw)


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

    def updateSize(self):
        super().updateSize()

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

    def updateSize(self):
        super().updateSize()

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

    def updateSize(self):
        super().updateSize()

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

    def updateSize(self):
        super().updateSize()

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

    def updateSize(self):
        super().updateSize()

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

    def updateSize(self):
        super().updateSize()
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

    def updateSize(self):
        self.color = (
            'Green', 'Red', 'Yellow', 'Blue',
            )[(self.parent.spritedata[5] >> 4) % 4]

        self.length1 = self.length
        self.length2 = self.length
        
        super().updateSize()


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

    def updateSize(self):

        self.image = ImageCache['ToadHouseBalloon' + ('Handle' if self.hasHandle else '') + str(self.livesNum)]

        self.xOffset = 8 - (self.image.width() / 3)

        super().updateSize()


# ---- High-Level Classes ----


class SpriteImage_CharacterSpawner(SLib.SpriteImage_StaticMultiple): # 9
    def updateSize(self):

        direction = self.parent.spritedata[2] & 1
        character = (self.parent.spritedata[5] & 0xF) % 4

        directionstr = 'L' if direction else 'R'

        self.image = ImageCache['Character' + str(character + 1) + directionstr]

        self.offset = (
            -(self.image.width() / 3),
            -(self.image.height() / 1.5),
            )

        super().updateSize()


class SpriteImage_Goomba(SLib.SpriteImage_Static): # 20
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Goomba'],
            (-1, -4),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Goomba', 'goomba.png')


class SpriteImage_Paragoomba(SLib.SpriteImage_Static): # 21
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Paragoomba'],
            (1, -10),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Paragoomba', 'paragoomba.png')


class SpriteImage_HorzMovingPlatform(SpriteImage_WoodenPlatform): # 23
    def __init__(self, parent):
        super().__init__(parent)

        self.width = ((self.parent.spritedata[5] & 0xF) + 1) << 4
        self.aux.append(SLib.AuxiliaryTrackObject(parent, self.width, 16, SLib.AuxiliaryTrackObject.Horizontal))

    def updateSize(self):
        super().updateSize()

        # get width and distance
        self.width = ((self.parent.spritedata[5] & 0xF) + 1) << 4
        if self.width == 16: self.width = 32

        distance = (self.parent.spritedata[4] & 0xF) << 4

        # update the track
        self.aux[0].setSize(self.width + distance, 16)

        if (self.parent.spritedata[3] & 1) == 0:
            # platform goes right
            self.aux[0].setPos(0, 0)
        else:
            # platform goes left
            self.aux[0].setPos(-distance*1.5, 0)

        # set color
        self.color = (self.parent.spritedata[3] >> 4) & 1

        self.aux[0].update()


class SpriteImage_BuzzyBeetle(SLib.SpriteImage_StaticMultiple): # 24
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BuzzyBeetle', 'buzzy_beetle.png')
        SLib.loadIfNotInImageCache('BuzzyBeetleU', 'buzzy_beetle_u.png')
        SLib.loadIfNotInImageCache('BuzzyBeetleShell', 'buzzy_beetle_shell.png')
        SLib.loadIfNotInImageCache('BuzzyBeetleShellU', 'buzzy_beetle_shell_u.png')

    def updateSize(self):

        orient = self.parent.spritedata[5] & 15
        if orient == 1:
            self.image = ImageCache['BuzzyBeetleU']
            self.yOffset = 0
        elif orient == 2:
            self.image = ImageCache['BuzzyBeetleShell']
            self.yOffset = 2
        elif orient == 3:
            self.image = ImageCache['BuzzyBeetleShellU']
            self.yOffset = 2
        else:
            self.image = ImageCache['BuzzyBeetle']
            self.yOffset = 0

        super().updateSize()


class SpriteImage_Spiny(SLib.SpriteImage_StaticMultiple): # 25
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Spiny', 'spiny.png')
        SLib.loadIfNotInImageCache('SpinyShell', 'spiny_shell.png')
        SLib.loadIfNotInImageCache('SpinyShellU', 'spiny_shell_u.png')
        SLib.loadIfNotInImageCache('SpinyBall', 'spiny_ball.png')

    def updateSize(self):

        orient = self.parent.spritedata[5] & 15
        if orient == 1:
            self.image = ImageCache['SpinyBall']
            self.yOffset = -2
        elif orient == 2:
            self.image = ImageCache['SpinyShell']
            self.yOffset = 1
        elif orient == 3:
            self.image = ImageCache['SpinyShellU']
            self.yOffset = 2
        else:
            self.image = ImageCache['Spiny']
            self.yOffset = 0

        super().updateSize()


class SpriteImage_UpsideDownSpiny(SLib.SpriteImage_Static): # 26
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SpinyU'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpinyU', 'spiny_u.png')


class SpriteImage_DSStoneBlock_Vert(SpriteImage_DSStoneBlock): # 27
    def __init__(self, parent):
        super().__init__(parent)

        self.aux.append(SLib.AuxiliaryTrackObject(parent, 32, 16, SLib.AuxiliaryTrackObject.Vertical))
        self.size = (32, 16)

    def updateSize(self):
        super().updateSize()

        # get height and distance
        byte5 = self.parent.spritedata[4]
        distance = (byte5 & 0xF) << 4

        # update the track
        self.aux[0].setSize(self.width, distance + self.height)

        if (self.parent.spritedata[3] & 1) == 0:
            # block goes up
            self.aux[0].setPos(0, -distance * 1.5)
        else:
            # block goes down
            self.aux[0].setPos(0, 0)

        self.aux[0].update()


class SpriteImage_DSStoneBlock_Horz(SpriteImage_DSStoneBlock): # 28
    def __init__(self, parent):
        super().__init__(parent)

        self.aux.append(SLib.AuxiliaryTrackObject(parent, 32, 16, SLib.AuxiliaryTrackObject.Horizontal))
        self.size = (32, 16)

    def updateSize(self):
        super().updateSize()

        # get height and distance
        byte5 = self.parent.spritedata[4]
        distance = (byte5 & 0xF) << 4

        # update the track
        self.aux[0].setSize(distance + self.width, self.height)

        if (self.parent.spritedata[3] & 1) == 0:
            # block goes right
            self.aux[0].setPos(0, 0)
        else:
            # block goes left
            self.aux[0].setPos(-distance * 1.5, 0)

        self.aux[0].update()


class SpriteImage_OldStoneBlock_NoSpikes(SpriteImage_OldStoneBlock): # 30
    pass


class SpriteImage_VertMovingPlatform(SpriteImage_WoodenPlatform): # 31
    def __init__(self, parent):
        super().__init__(parent)

        self.width = ((self.parent.spritedata[5] & 0xF) + 1) << 4
        self.aux.append(SLib.AuxiliaryTrackObject(parent, self.width, 16, SLib.AuxiliaryTrackObject.Vertical))


    def updateSize(self):
        super().updateSize()

        # get width and distance
        self.width = ((self.parent.spritedata[5] & 0xF) + 1) << 4
        if self.width == 16: self.width = 32

        distance = (self.parent.spritedata[4] & 0xF) << 4

        # update the track
        self.aux[0].setSize(self.width, distance + 16)

        if (self.parent.spritedata[3] & 1) == 0:
            # platform goes up
            self.aux[0].setPos(0, -distance * 1.5)
        else:
            # platform goes down
            self.aux[0].setPos(0, 0)

        # set color
        self.color = (self.parent.spritedata[3] >> 4) & 1

        self.aux[0].update()


class SpriteImage_StarCoinRegular(SpriteImage_StarCoin): # 32
    pass


class SpriteImage_QuestionSwitch(SpriteImage_Switch): # 40
    def __init__(self, parent):
        super().__init__(parent)
        self.switchType = 'Q'


class SpriteImage_PSwitch(SpriteImage_Switch): # 41
    def __init__(self, parent):
        super().__init__(parent)
        self.switchType = 'P'


class SpriteImage_ExcSwitch(SpriteImage_Switch): # 42
    def __init__(self, parent):
        super().__init__(parent)
        self.switchType = 'E'


class SpriteImage_QuestionSwitchBlock(SLib.SpriteImage_Static): # 43
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['QSwitchBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('QSwitchBlock', 'q_switch_block.png')


class SpriteImage_PSwitchBlock(SLib.SpriteImage_Static): # 44
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PSwitchBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PSwitchBlock', 'p_switch_block.png')


class SpriteImage_ExcSwitchBlock(SLib.SpriteImage_Static): # 45
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ESwitchBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ESwitchBlock', 'e_switch_block.png')


class SpriteImage_Podoboo(SLib.SpriteImage_Static): # 46
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Podoboo'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Podoboo', 'podoboo.png')


class SpriteImage_Thwomp(SLib.SpriteImage_Static): # 47
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Thwomp'],
            (-6, -6),
            )

        @staticmethod
        def loadImages():
            SLib.loadIfNotInImageCache('Thwomp', 'thwomp.png')


class SpriteImage_GiantThwomp(SLib.SpriteImage_Static): # 48
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['GiantThwomp'],
            (-8, -8),
            )

        @staticmethod
        def loadImages():
            SLib.loadIfNotInImageCache('GiantThwomp', 'giant_thwomp.png')


class SpriteImage_UnusedSeesaw(SLib.SpriteImage): # 49
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryRotationAreaOutline(parent, 48))
        self.aux[0].setPos(128, -36)

        self.image = ImageCache['UnusedPlatformDark']
        self.dimensions = (0, -8, 256, 16)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('UnusedPlatformDark', 'unused_platform_dark.png')

    def updateSize(self):
        w = self.parent.spritedata[5] & 15
        if w == 0:
            self.width = 16 * 16 # 16 blocks wide
        else:
            self.width = w * 32
        self.image = ImageCache['UnusedPlatformDark'].scaled(
            self.width * 1.5, self.height * 1.5,
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation,
            )
        self.xOffset = (8 * 16) - (self.width / 2)

        swingArc = self.parent.spritedata[5] >> 4
        swingArcs = (
            45,
            4.5,
            9,
            18,
            65,
            80,
            )
        if swingArc <= 5:
            realSwingArc = swingArcs[swingArc]
        else:
            realSwingArc = 100 # infinite

        # angle starts at the right position (3 o'clock)
        # negative = clockwise, positive = counter-clockwise
        startAngle = 90 - realSwingArc
        spanAngle = realSwingArc * 2

        self.aux[0].SetAngle(startAngle, spanAngle)
        self.aux[0].setPos((self.width / 1.5) - 36, -36)
        self.aux[0].update()

        super().updateSize()

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, self.image)


class SpriteImage_FallingPlatform(SpriteImage_WoodenPlatform): # 50
    def __init__(self, parent):
        super().__init__(parent)

    def updateSize(self):
        super().updateSize()

        # get width
        self.width = ((self.parent.spritedata[5] & 0xF) + 1) << 4

        # override this for the "glitchy" effect caused by length=0
        if self.width == 16: self.width = 24

        # set color
        color = (self.parent.spritedata[3] >> 4)
        if color == 1:
            self.color = 1
        elif color == 3:
            self.color = 2
        else:
            self.color = 0


class SpriteImage_TiltingGirder(SLib.SpriteImage_Static): # 51
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['TiltingGirder'],
            (0, -18),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TiltingGirder', 'tilting_girder.png')


class SpriteImage_UnusedRotPlatforms(SLib.SpriteImage): # 52
    def __init__(self, parent):
        super().__init__(parent)

        self.aux.append(SLib.AuxiliaryImage(parent, 432, 312))
        self.aux[0].image = ImageCache['UnusedRotPlatforms']
        self.aux[0].setPos(-144 - 72, -104 - 52) # It actually isn't centered correctly in-game

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('UnusedPlatformDark', 'unused_platform_dark.png')

        platform = ImageCache['UnusedPlatformDark'].scaled(
            144, 24,
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation,
            )
        img = QtGui.QPixmap(432, 312)
        img.fill(Qt.transparent)
        paint = QtGui.QPainter(img)
        paint.setOpacity(0.8)
        paint.drawPixmap(144, 0,   platform) # top
        paint.drawPixmap(144, 288, platform) # bottom
        paint.drawPixmap(0,   144, platform) # left
        paint.drawPixmap(288, 144, platform) # right
        del paint
        ImageCache['UnusedRotPlatforms'] = img


class SpriteImage_Lakitu(SLib.SpriteImage_Static): # 54
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Lakitu'],
            (-16, -24),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Lakitu', 'lakitu.png')


class SpriteImage_UnusedRisingSeesaw(SLib.SpriteImage_Static): # 55
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['UnusedPlatformDark'].scaled(
                377, 24,
                Qt.IgnoreAspectRatio, Qt.SmoothTransformation,
                ),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('UnusedPlatformDark', 'unused_platform_dark.png')


class SpriteImage_RisingTiltGirder(SLib.SpriteImage_Static): # 56
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['RisingTiltGirder'],
            (-32, -10),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RisingTiltGirder', 'rising_girder.png')


class SpriteImage_KoopaTroopa(SLib.SpriteImage_StaticMultiple): # 57
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = (-7, -15)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('KoopaG', 'koopa_green.png')
        SLib.loadIfNotInImageCache('KoopaR', 'koopa_red.png')
        SLib.loadIfNotInImageCache('KoopaShellG', 'koopa_green_shell.png')
        SLib.loadIfNotInImageCache('KoopaShellR', 'koopa_red_shell.png')

    def updateSize(self):
        # get properties
        props = self.parent.spritedata[5]
        shell = (props >> 4) & 1
        color = props & 1

        if shell == 0:
            self.offset = (-7, -15)

            if color == 0:
                self.image = ImageCache['KoopaG']
            else:
                self.image = ImageCache['KoopaR']
        else:
            del self.offset

            if color == 0:
                self.image = ImageCache['KoopaShellG']
            else:
                self.image = ImageCache['KoopaShellR']

        super().updateSize()


class SpriteImage_KoopaParatroopa(SLib.SpriteImage_StaticMultiple): # 58
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = (-7, -12)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ParakoopaG', 'parakoopa_green.png')
        SLib.loadIfNotInImageCache('ParakoopaR', 'parakoopa_red.png')

    def updateSize(self):

        # get properties
        color = self.parent.spritedata[5] & 1

        if color == 0:
            self.image = ImageCache['ParakoopaG']
        else:
            self.image = ImageCache['ParakoopaR']

        super().updateSize()


class SpriteImage_LineTiltGirder(SLib.SpriteImage_Static): # 59
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['LineGirder'],
            (-8, -10),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LineGirder', 'line_tilt_girder.png')


class SpriteImage_SpikeTop(SLib.SpriteImage_StaticMultiple): # 60
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SpikeTop00'],
            (0, -4),
            )

    @staticmethod
    def loadImages():
        if 'SpikeTop00' in ImageCache: return
        SpikeTop = SLib.GetImg('spiketop.png', True)

        Transform = QtGui.QTransform()
        ImageCache['SpikeTop00'] = QtGui.QPixmap.fromImage(SpikeTop.mirrored(True, False))
        Transform.rotate(90)
        ImageCache['SpikeTop10'] = ImageCache['SpikeTop00'].transformed(Transform)
        Transform.rotate(90)
        ImageCache['SpikeTop20'] = ImageCache['SpikeTop00'].transformed(Transform)
        Transform.rotate(90)
        ImageCache['SpikeTop30'] = ImageCache['SpikeTop00'].transformed(Transform)

        Transform = QtGui.QTransform()
        ImageCache['SpikeTop01'] = QtGui.QPixmap.fromImage(SpikeTop)
        Transform.rotate(90)
        ImageCache['SpikeTop11'] = ImageCache['SpikeTop01'].transformed(Transform)
        Transform.rotate(90)
        ImageCache['SpikeTop21'] = ImageCache['SpikeTop01'].transformed(Transform)
        Transform.rotate(90)
        ImageCache['SpikeTop31'] = ImageCache['SpikeTop01'].transformed(Transform)

    def updateSize(self):

        orientation = (self.parent.spritedata[5] >> 4) % 4
        direction = self.parent.spritedata[5] & 1

        self.image = ImageCache['SpikeTop%d%d' % (orientation, direction)]

        self.offset = (
            (0, -4),
            (0, 0),
            (0, 0),
            (-4, 0),
            )[orientation]

        super().updateSize()


class SpriteImage_BigBoo(SLib.SpriteImage): # 61
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryImage(parent, 243, 248))
        self.aux[0].image = ImageCache['BigBoo']
        self.aux[0].setPos(-48, -48)
        self.aux[0].hover = False

        self.dimensions = (-38, -80, 98, 102)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigBoo', 'bigboo.png')


class SpriteImage_SpikeBall(SLib.SpriteImage_Static): # 63
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SpikeBall'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpikeBall', 'spike_ball.png')


class SpriteImage_OutdoorsFog(SpriteImage_LiquidOrFog): # 64
    def __init__(self, parent):
        super().__init__(parent)
        self.mid = ImageCache['OutdoorsFog']

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('OutdoorsFog', 'fog_outdoors.png')

    def updateSize(self):
        super().updateSize()
        self.parent.updateScene()

    def realViewZone(self, painter, zoneRect, viewRect):

        self.paintZone = self.parent.spritedata[5] == 0

        self.top = self.parent.objy

        # Get pixmaps
        mid = ImageCache['OutdoorsFog']

        super().realViewZone(painter, zoneRect, viewRect)


class SpriteImage_PipePiranhaUp(SLib.SpriteImage_Static): # 65
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipePlantUp'],
            (2, -32),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePlantUp', 'piranha_pipe_up.png')


class SpriteImage_PipePiranhaDown(SLib.SpriteImage_Static): # 66
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipePlantDown'],
            (2, 32),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePlantDown', 'piranha_pipe_down.png')


class SpriteImage_PipePiranhaRight(SLib.SpriteImage_Static): # 67
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipePlantRight'],
            (32, 2),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePlantRight', 'piranha_pipe_right.png')


class SpriteImage_PipePiranhaLeft(SLib.SpriteImage_Static): # 68
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipePlantLeft'],
            (-32, 2),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipePlantLeft', 'piranha_pipe_left.png')


class SpriteImage_PipeFiretrapUp(SLib.SpriteImage_Static): # 69
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipeFiretrapUp'],
            (-4, -29),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeFiretrapUp', 'firetrap_pipe_up.png')


class SpriteImage_PipeFiretrapDown(SLib.SpriteImage_Static): # 70
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipeFiretrapDown'],
            (-4, 32),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeFiretrapDown', 'firetrap_pipe_down.png')


class SpriteImage_PipeFiretrapRight(SLib.SpriteImage_Static): # 71
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipeFiretrapRight'],
            (32, 6),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeFiretrapRight', 'firetrap_pipe_right.png')


class SpriteImage_PipeFiretrapLeft(SLib.SpriteImage_Static): # 72
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipeFiretrapLeft'],
            (-29, 6),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PipeFiretrapLeft', 'firetrap_pipe_left.png')


class SpriteImage_GroundPiranha(SLib.SpriteImage_StaticMultiple): # 73
    def __init__(self, parent):
        super().__init__(parent)
        self.xOffset = -20

    @staticmethod
    def loadImages():
        if 'GroundPiranha' in ImageCache: return
        GP = SLib.GetImg('ground_piranha.png', True)
        ImageCache['GroundPiranha'] = QtGui.QPixmap.fromImage(GP)
        ImageCache['GroundPiranhaU'] = QtGui.QPixmap.fromImage(GP.mirrored(False, True))

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1
        if not upsideDown:
            self.yOffset = 6
            self.image = ImageCache['GroundPiranha']
        else:
            self.yOffset = 0
            self.image = ImageCache['GroundPiranhaU']

        super().updateSize()


class SpriteImage_BigGroundPiranha(SLib.SpriteImage_StaticMultiple): # 74
    def __init__(self, parent):
        super().__init__(parent)
        self.xOffset = -65

    @staticmethod
    def loadImages():
        if 'BigGroundPiranha' in ImageCache: return
        BGP = SLib.GetImg('big_ground_piranha.png', True)
        ImageCache['BigGroundPiranha'] = QtGui.QPixmap.fromImage(BGP)
        ImageCache['BigGroundPiranhaU'] = QtGui.QPixmap.fromImage(BGP.mirrored(False, True))

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1
        if not upsideDown:
            self.yOffset = -32
            self.image = ImageCache['BigGroundPiranha']
        else:
            self.yOffset = 0
            self.image = ImageCache['BigGroundPiranhaU']

        super().updateSize()


class SpriteImage_GroundFiretrap(SLib.SpriteImage_StaticMultiple): # 75
    def __init__(self, parent):
        super().__init__(parent)
        self.xOffset = 5

    @staticmethod
    def loadImages():
        if 'GroundFiretrap' in ImageCache: return
        GF = SLib.GetImg('ground_firetrap.png', True)
        ImageCache['GroundFiretrap'] = QtGui.QPixmap.fromImage(GF)
        ImageCache['GroundFiretrapU'] = QtGui.QPixmap.fromImage(GF.mirrored(False, True))

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1
        if not upsideDown:
            self.yOffset = -10
            self.image = ImageCache['GroundFiretrap']
        else:
            self.yOffset = 0
            self.image = ImageCache['GroundFiretrapU']

        super().updateSize()


class SpriteImage_BigGroundFiretrap(SLib.SpriteImage_StaticMultiple): # 76
    def __init__(self, parent):
        super().__init__(parent)
        self.xOffset = -14

    @staticmethod
    def loadImages():
        if 'BigGroundFiretrap' in ImageCache: return
        BGF = SLib.GetImg('big_ground_firetrap.png', True)
        ImageCache['BigGroundFiretrap'] = QtGui.QPixmap.fromImage(BGF)
        ImageCache['BigGroundFiretrapU'] = QtGui.QPixmap.fromImage(BGF.mirrored(False, True))

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1
        if not upsideDown:
            self.yOffset = -68
            self.image = ImageCache['BigGroundFiretrap']
        else:
            self.yOffset = 0
            self.image = ImageCache['BigGroundFiretrapU']

        super().updateSize()


class SpriteImage_ShipKey(SLib.SpriteImage_Static): # 77
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ShipKey'],
            (-1, -8),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ShipKey', 'ship_key.png')


class SpriteImage_CloudTrampoline(SLib.SpriteImage_StaticMultiple): # 78
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['CloudTrSmall'],
            (-2, -2),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CloudTrBig', 'cloud_trampoline_big.png')
        SLib.loadIfNotInImageCache('CloudTrSmall', 'cloud_trampoline_small.png')

    def updateSize(self):

        size = (self.parent.spritedata[4] & 0x10) >> 4
        if size == 0:
            self.image = ImageCache['CloudTrSmall']
            self.size = (68, 27)
        else:
            self.image = ImageCache['CloudTrBig']
            self.size = (132, 32)

        super().updateSize()


class SpriteImage_FireBro(SLib.SpriteImage_Static): # 80
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['FireBro'],
            (-8, -22),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FireBro', 'firebro.png')


class SpriteImage_OldStoneBlock_SpikesLeft(SpriteImage_OldStoneBlock): # 81
    def __init__(self, parent):
        super().__init__(parent)
        self.spikesL = True


class SpriteImage_OldStoneBlock_SpikesRight(SpriteImage_OldStoneBlock): # 82
    def __init__(self, parent):
        super().__init__(parent)
        self.spikesR = True


class SpriteImage_OldStoneBlock_SpikesLeftRight(SpriteImage_OldStoneBlock): # 83
    def __init__(self, parent):
        super().__init__(parent)
        self.spikesL = True
        self.spikesR = True


class SpriteImage_OldStoneBlock_SpikesTop(SpriteImage_OldStoneBlock): # 84
    def __init__(self, parent):
        super().__init__(parent)
        self.spikesT = True


class SpriteImage_OldStoneBlock_SpikesBottom(SpriteImage_OldStoneBlock): # 85
    def __init__(self, parent):
        super().__init__(parent)
        self.spikesB = True


class SpriteImage_OldStoneBlock_SpikesTopBottom(SpriteImage_OldStoneBlock): # 86
    def __init__(self, parent):
        super().__init__(parent)
        self.spikesT = True
        self.spikesB = True


class SpriteImage_TrampolineWall(SLib.SpriteImage_StaticMultiple): # 87
    def __init__(self, parent):
        super().__init__(parent)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('UnusedPlatformDark', 'unused_platform_dark.png')

    def updateSize(self):
        height = (self.parent.spritedata[5] & 15) + 1

        self.image = ImageCache['UnusedPlatformDark'].scaled(
            24, height * 24,
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation,
            )
        self.height = height * 16

        super().updateSize()


class SpriteImage_BulletBillLauncher(SLib.SpriteImage): # 92
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BBLauncherT', 'bullet_launcher_top.png')
        SLib.loadIfNotInImageCache('BBLauncherM', 'bullet_launcher_middle.png')

    def updateSize(self):
        super().updateSize()
        height = (self.parent.spritedata[5] & 0xF0) >> 4

        self.height = (height + 2) * 16
        self.yOffset = (height + 1) * -16

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['BBLauncherT'])
        painter.drawTiledPixmap(0, 48, 24, self.height*1.5 - 48, ImageCache['BBLauncherM'])


class SpriteImage_BanzaiBillLauncher(SLib.SpriteImage_Static): # 93
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['BanzaiLauncher'],
            (-32, -68),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BanzaiLauncher', 'banzai_launcher.png')


class SpriteImage_BoomerangBro(SLib.SpriteImage_Static): # 94
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['BoomerangBro'],
            (-8, -22),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoomerangBro', 'boomerangbro.png')


class SpriteImage_HammerBroNormal(SpriteImage_HammerBro): # 95
    pass


class SpriteImage_RotationControllerSwaying(SLib.SpriteImage): # 96
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.setZValue(100000)
        self.aux.append(SLib.AuxiliaryRotationAreaOutline(parent, 48))

    def updateSize(self):
        super().updateSize()
        # get the swing arc: 4 == 90 degrees (45 left from the origin, 45 right)
        swingArc = self.parent.spritedata[2] >> 4
        realSwingArc = swingArc * 11.25

        # angle starts at the right position (3 o'clock)
        # negative = clockwise, positive = counter-clockwise
        startAngle = 90 - realSwingArc
        spanAngle = realSwingArc * 2

        self.aux[0].SetAngle(startAngle, spanAngle)
        self.aux[0].update()


class SpriteImage_RotationControlledSolidBetaPlatform(SpriteImage_UnusedBlockPlatform): # 97
    def __init__(self, parent):
        super().__init__(parent)
        self.isDark = True

    def updateSize(self):
        size = self.parent.spritedata[4]
        width = size >> 4
        height = size & 0xF

        if width == 0 or height == 0:
            self.spritebox.shown = True
            self.drawPlatformImage = False
            del self.size
        else:
            self.spritebox.shown = False
            self.drawPlatformImage = True
            self.size = (width * 16, height * 16)

        super().updateSize()


class SpriteImage_GiantSpikeBall(SLib.SpriteImage_Static): # 98
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['GiantSpikeBall'],
            (-32, -16),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantSpikeBall', 'giant_spike_ball.png')


class SpriteImage_PipeEnemyGenerator(SLib.SpriteImage): # 99
    def __init__(self, parent):
        super().__init__(parent)
    def updateSize(self):
        super().updateSize()

        direction = (self.parent.spritedata[5] & 0xF) % 4
        if direction in (0, 1): # vertical pipe
            self.spritebox.size = (48, 24)
        else: # horizontal pipe
            self.spritebox.size = (24, 48)


class SpriteImage_Swooper(SLib.SpriteImage_Static): # 100
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Swooper'],
            (2, 0),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Swooper', 'swooper.png')


class SpriteImage_Bobomb(SLib.SpriteImage_Static): # 101
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Bobomb'],
            (-8, -8),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Bobomb', 'bobomb.png')


class SpriteImage_Broozer(SLib.SpriteImage_Static): # 102
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Broozer'],
            (-9, -17),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Broozer', 'broozer.png')


class SpriteImage_PlatformGenerator(SpriteImage_WoodenPlatform): # 103
    # TODO: Add arrows
    def updateSize(self):
        super().updateSize()
        # get width
        self.width = (((self.parent.spritedata[5] & 0xF0) >> 4) + 1) << 4

        # length=0 becomes length=4
        if self.width == 16: self.width = 64

        # override this for the "glitchy" effect caused by length=0
        if self.width == 32: self.width = 24

        self.color = 0


class SpriteImage_AmpNormal(SpriteImage_Amp): # 104
    pass


class SpriteImage_Pokey(SLib.SpriteImage): # 105
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.dimensions = (-4, 0, 24, 32)

    @staticmethod
    def loadImages():
        if 'PokeyTop' in ImageCache: return
        ImageCache['PokeyTop'] = SLib.GetImg('pokey_top.png')
        ImageCache['PokeyMiddle'] = SLib.GetImg('pokey_middle.png')
        ImageCache['PokeyBottom'] = SLib.GetImg('pokey_bottom.png')

    def updateSize(self):
        super().updateSize()

        # get the height
        height = self.parent.spritedata[5] & 0xF
        self.height = (height * 16) + 16 + 25
        self.yOffset = 0 - self.height + 16

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['PokeyTop'])
        painter.drawTiledPixmap(0, 37, 36, self.height*1.5 - 61, ImageCache['PokeyMiddle'])
        painter.drawPixmap(0, self.height*1.5 - 24, ImageCache['PokeyBottom'])


class SpriteImage_LinePlatform(SpriteImage_WoodenPlatform): # 106
    def __init__(self, parent):
        super().__init__(parent)
        self.yOffset = 8

    def updateSize(self):
        super().updateSize()

        # get width
        self.width = (self.parent.spritedata[5] & 0xF) << 4

        # length=0 becomes length=4
        if self.width == 0: self.width = 64

        # override this for the "glitchy" effect caused by length=0
        if self.width == 16: self.width = 24

        color = (self.parent.spritedata[4] & 0xF0) >> 4
        if color > 1: color = 0
        self.color = color


class SpriteImage_RotationControlledPassBetaPlatform(SpriteImage_UnusedBlockPlatform): # 107
    def __init__(self, parent):
        super().__init__(parent)
        self.isDark = True
        self.width = 16

    def updateSize(self):
        size = self.parent.spritedata[4]
        height = (size & 0xF) + 1

        self.yOffset = -(height - 1) * 8
        self.height = height * 16

        super().updateSize()


class SpriteImage_AmpLine(SpriteImage_Amp): # 108
    pass


class SpriteImage_ChainBall(SLib.SpriteImage_StaticMultiple): # 109
    def __init__(self, parent):
        super().__init__(parent)

    @staticmethod
    def loadImages():
        if 'ChainBallU' in ImageCache: return
        ImageCache['ChainBallU'] = SLib.GetImg('chainball_up.png')
        ImageCache['ChainBallR'] = SLib.GetImg('chainball_right.png')
        ImageCache['ChainBallD'] = SLib.GetImg('chainball_down.png')
        ImageCache['ChainBallL'] = SLib.GetImg('chainball_left.png')

    def updateSize(self):
        direction = self.parent.spritedata[5] & 3
        if direction > 3: direction = 0

        if direction % 2 == 0: # horizontal
            self.size = (96, 38)
        else: # vertical
            self.size = (37, 96)

        if direction == 0: # right
            self.image = ImageCache['ChainBallR']
            self.offset = (3, -8.5)
        elif direction == 1: # up
            self.image = ImageCache['ChainBallU']
            self.offset = (-8.5, -81.5)
        elif direction == 2: # left
            self.image = ImageCache['ChainBallL']
            self.offset = (-83, -11)
        elif direction == 3: # down
            self.image = ImageCache['ChainBallD']
            self.offset = (-11, 3.5)

        super().updateSize()


class SpriteImage_Sunlight(SLib.SpriteImage): # 110
    def __init__(self, parent):
        super().__init__(parent)

        i = ImageCache['Sunlight']
        self.aux.append(SLib.AuxiliaryImage_FollowsRect(parent, i.width(), i.height()))
        self.aux[0].realimage = i
        self.aux[0].alignment = Qt.AlignTop | Qt.AlignRight
        self.parent.scene().views()[0].repaint.connect(lambda: self.moveSunlight())
        self.aux[0].hover = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Sunlight', 'sunlight.png')

    def moveSunlight(self):
        if SLib.RealViewEnabled:
            self.aux[0].realimage = ImageCache['Sunlight']
        else:
            self.aux[0].realimage = None
            return
        zone = self.parent.getZone(True)
        if zone is None:
            self.aux[0].realimage = None
            return
        zoneRect = QtCore.QRectF(zone.objx * 1.5, zone.objy * 1.5, zone.width * 1.5, zone.height * 1.5)
        view = self.parent.scene().views()[0]
        viewRect = view.mapToScene(view.viewport().rect()).boundingRect()
        bothRect = zoneRect & viewRect

        self.aux[0].move(bothRect.x(), bothRect.y(), bothRect.width(), bothRect.height())


class SpriteImage_Blooper(SLib.SpriteImage_Static): # 111
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Blooper'],
            (-3, -2),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Blooper', 'blooper.png')


class SpriteImage_BlooperBabies(SLib.SpriteImage_Static): # 112
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['BlooperBabies'],
            (-5, -2),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BlooperBabies', 'blooper_babies.png')


class SpriteImage_Flagpole(SLib.SpriteImage): # 113
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.image = ImageCache['Flagpole']

        self.aux.append(SLib.AuxiliaryImage(parent, 144, 149))
        self.offset = (-30, -144)
        self.size = (self.image.width() / 1.5, self.image.height() / 1.5)

    @staticmethod
    def loadImages():
        if 'Flagpole' in ImageCache: return
        ImageCache['Flagpole'] = SLib.GetImg('flagpole.png')
        ImageCache['FlagpoleSecret'] = SLib.GetImg('flagpole_secret.png')
        ImageCache['Castle'] = SLib.GetImg('castle.png')
        ImageCache['CastleSecret'] = SLib.GetImg('castle_secret.png')
        ImageCache['SnowCastle'] = SLib.GetImg('snow_castle.png')
        ImageCache['SnowCastleSecret'] = SLib.GetImg('snow_castle_secret.png')

    def updateSize(self):

        # get the info
        exit = (self.parent.spritedata[2] >> 4) & 1
        snow = self.parent.spritedata[5] & 1

        if snow == 0:
            self.aux[0].setPos(356, 97)
        else:
            self.aux[0].setPos(356, 91)

        if exit == 0:
            self.image = ImageCache['Flagpole']
            if snow == 0:
                self.aux[0].image = ImageCache['Castle']
            else:
                self.aux[0].image = ImageCache['SnowCastle']
        else:
            self.image = ImageCache['FlagpoleSecret']
            if snow == 0:
                self.aux[0].image = ImageCache['CastleSecret']
            else:
                self.aux[0].image = ImageCache['SnowCastleSecret']

        super().updateSize()

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(0, 0, self.image)


class SpriteImage_FlameCannon(SLib.SpriteImage_StaticMultiple): # 114
    def __init__(self, parent):
        super().__init__(parent)

        self.height = 64

    @staticmethod
    def loadImages():
        if 'FlameCannonR' in ImageCache: return
        transform90 = QtGui.QTransform()
        transform270 = QtGui.QTransform()
        transform90.rotate(90)
        transform270.rotate(270)

        image = SLib.GetImg('continuous_flame_cannon.png', True)
        ImageCache['FlameCannonR'] = QtGui.QPixmap.fromImage(image)
        ImageCache['FlameCannonD'] = QtGui.QPixmap.fromImage(image.transformed(transform90))
        ImageCache['FlameCannonL'] = QtGui.QPixmap.fromImage(image.mirrored(True, False))
        ImageCache['FlameCannonU'] = QtGui.QPixmap.fromImage(image.transformed(transform270).mirrored(True, False))

    def updateSize(self):
        direction = self.parent.spritedata[5] & 15
        if direction > 3: direction = 0

        if direction == 0: # right
            del self.offset
        elif direction == 1: # left
            self.offset = (-48, 0)
        elif direction == 2: # up
            self.offset = (0, -48)
        elif direction == 3: # down
            del self.offset

        directionstr = 'RLUD'[direction]
        self.image = ImageCache['FlameCannon%s' % directionstr]

        super().updateSize()


class SpriteImage_Cheep(SLib.SpriteImage): # 115
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryTrackObject(self.parent, 24, 24, SLib.AuxiliaryTrackObject.Horizontal))

    @staticmethod
    def loadImages():
        if 'CheepGreen' in ImageCache: return
        ImageCache['CheepRedLeft'] = SLib.GetImg('cheep_red.png')
        ImageCache['CheepRedRight'] = QtGui.QPixmap.fromImage(SLib.GetImg('cheep_red.png', True).mirrored(True, False))
        ImageCache['CheepRedAtYou'] = SLib.GetImg('cheep_red_atyou.png')
        ImageCache['CheepGreen'] = SLib.GetImg('cheep_green.png')
        ImageCache['CheepYellow'] = SLib.GetImg('cheep_yellow.png')

    def updateSize(self):

        type = self.parent.spritedata[5] & 0xF
        if type in (1, 7):
            self.image = ImageCache['CheepGreen']
        elif type == 8:
            self.image = ImageCache['CheepYellow']
        elif type == 5:
            self.image = ImageCache['CheepRedAtYou']
        else:
            self.image = ImageCache['CheepRedLeft']
        self.size = (self.image.width() / 1.5, self.image.height() / 1.5)

        if type == 3:
            distance = ((self.parent.spritedata[3] & 0xF) + 1) * 16
            self.aux[0].setSize((distance * 2) + 16, 16)
            self.aux[0].setPos(-distance * 1.5, 0)
        else:
            self.aux[0].setSize(0, 24)

        super().updateSize()

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(0, 0, self.image)


class SpriteImage_CoinCheep(SLib.SpriteImage): # 116
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'CheepRedLeft' in ImageCache: return
        ImageCache['CheepRedLeft'] = SLib.GetImg('cheep_red.png')
        ImageCache['CheepRedRight'] = QtGui.QPixmap.fromImage(SLib.GetImg('cheep_red.png', True).mirrored(True, False))
        ImageCache['CheepRedAtYou'] = SLib.GetImg('cheep_red_atyou.png')
        ImageCache['CheepGreen'] = SLib.GetImg('cheep_green.png')
        ImageCache['CheepYellow'] = SLib.GetImg('cheep_yellow.png')

    def updateSize(self):

        waitFlag = self.parent.spritedata[5] & 1
        if waitFlag:
            self.spritebox.shown = False
            self.image = ImageCache['CheepRedAtYou']
        else:
            type = self.parent.spritedata[2] >> 4
            if type % 4 == 3:
                self.spritebox.shown = True
                self.image = None
            elif type < 7:
                self.spritebox.shown = False
                self.image = self.image = ImageCache['CheepRedRight']
            else:
                self.spritebox.shown = False
                self.image = self.image = ImageCache['CheepRedLeft']

        if self.image is not None:
            self.size = (self.image.width() / 1.5, self.image.height() / 1.5)
        super().updateSize()

    def paint(self, painter):
        super().paint(painter)
        if self.image is None: return
        painter.drawPixmap(0, 0, self.image)


class SpriteImage_PulseFlameCannon(SLib.SpriteImage_StaticMultiple): # 117
    def __init__(self, parent):
        super().__init__(parent)
        self.height = 112

    @staticmethod
    def loadImages():
        if 'PulseFlameCannonR' in ImageCache: return
        transform90 = QtGui.QTransform()
        transform270 = QtGui.QTransform()
        transform90.rotate(90)
        transform270.rotate(270)

        onImage = SLib.GetImg('synchro_flame_jet.png', True)
        ImageCache['PulseFlameCannonR'] = QtGui.QPixmap.fromImage(onImage)
        ImageCache['PulseFlameCannonD'] = QtGui.QPixmap.fromImage(onImage.transformed(transform90))
        ImageCache['PulseFlameCannonL'] = QtGui.QPixmap.fromImage(onImage.mirrored(True, False))
        ImageCache['PulseFlameCannonU'] = QtGui.QPixmap.fromImage(onImage.transformed(transform270).mirrored(True, False))

    def updateSize(self):

        direction = self.parent.spritedata[5] & 15
        if direction > 3: direction = 0

        if direction == 0:
            del self.offset
        elif direction == 1:
            self.offset = (-96, 0)
        elif direction == 2:
            self.offset = (0, -96)
        elif direction == 3:
            del self.offset

        directionstr = 'RLUD'[direction]
        self.image = ImageCache['PulseFlameCannon%s' % directionstr]

        super().updateSize()


class SpriteImage_DryBones(SLib.SpriteImage_Static): # 118
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['DryBones'],
            (-7, -16),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('DryBones', 'drybones.png')


class SpriteImage_GiantDryBones(SLib.SpriteImage_Static): # 119
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['GiantDryBones'],
            (-13, -24),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantDryBones', 'giant_drybones.png')


class SpriteImage_SledgeBro(SLib.SpriteImage_Static): # 120
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SledgeBro'],
            (-8, -28.5),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SledgeBro', 'sledgebro.png')


class SpriteImage_OneWayPlatform(SpriteImage_WoodenPlatform): # 122
    def updateSize(self):
        super().updateSize()
        width = self.parent.spritedata[5] & 0xF
        if width < 2: width = 2
        self.width = width * 32 + 32

        self.xOffset = self.width * -0.5

        color = (self.parent.spritedata[4] & 0xF0) >> 4
        if color > 1: color = 0
        self.color = color


class SpriteImage_UnusedCastlePlatform(SLib.SpriteImage_StaticMultiple): # 123
    def __init__(self, parent):
        super().__init__(parent)

        self.image = ImageCache['UnusedCastlePlatform']
        self.size = (255, 255)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('UnusedCastlePlatform', 'unused_castle_platform.png')

    def updateSize(self):
        rawSize = self.parent.spritedata[4] >> 4

        if rawSize != 0:
            widthInBlocks = rawSize * 4
        else:
            widthInBlocks = 8

        topRadiusInBlocks = widthInBlocks / 10
        heightInBlocks = widthInBlocks + topRadiusInBlocks

        self.image = ImageCache['UnusedCastlePlatform'].scaled(widthInBlocks * 24, heightInBlocks * 24)

        self.offset = (
            -(self.image.width() / 1.5) / 2,
            -topRadiusInBlocks * 16,
            )

        super().updateSize()


class SpriteImage_FenceKoopaHorz(SLib.SpriteImage_StaticMultiple): # 125
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = (-3, -12)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FenceKoopaHG', 'fencekoopa_horz.png')
        SLib.loadIfNotInImageCache('FenceKoopaHR', 'fencekoopa_horz_red.png')

    def updateSize(self):

        color = self.parent.spritedata[5] >> 4
        if color == 1:
            self.image = ImageCache['FenceKoopaHR']
        else:
            self.image = ImageCache['FenceKoopaHG']

        super().updateSize()


class SpriteImage_FenceKoopaVert(SLib.SpriteImage_StaticMultiple): # 126
    def __init__(self, parent):
        super().__init__(parent)

        self.offset = (-2, -12)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FenceKoopaVG', 'fencekoopa_vert.png')
        SLib.loadIfNotInImageCache('FenceKoopaVR', 'fencekoopa_vert_red.png')

    def updateSize(self):

        color = self.parent.spritedata[5] >> 4
        if color == 1:
            self.image = ImageCache['FenceKoopaVR']
        else:
            self.image = ImageCache['FenceKoopaVG']

        super().updateSize()


class SpriteImage_FlipFence(SLib.SpriteImage_Static): # 127
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['FlipFence'],
            (-4, -8),
            )
        parent.setZValue(24999)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FlipFence', 'flipfence.png')


class SpriteImage_FlipFenceLong(SLib.SpriteImage_Static): # 128
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['FlipFenceLong'],
            (6, 0),
            )
        parent.setZValue(24999)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FlipFenceLong', 'flipfence_long.png')


class SpriteImage_4Spinner(SLib.SpriteImage_Static): # 129
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['4Spinner'],
            (-62, -48),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('4Spinner', '4spinner.png')

    def updateSize(self):
        super().updateSize()
        self.alpha = 0.6 if (self.parent.spritedata[2] >> 4) & 1 else 1


class SpriteImage_Wiggler(SLib.SpriteImage_Static): # 130
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Wiggler'],
            (0, -12),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Wiggler', 'wiggler.png')


class SpriteImage_Boo(SLib.SpriteImage): # 131
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryImage(parent, 50, 51))
        self.aux[0].image = ImageCache['Boo1']
        self.aux[0].setPos(-6, -6)

        self.dimensions = (-1, -4, 22, 22)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Boo1', 'boo1.png')


class SpriteImage_UnusedBlockPlatform1(SpriteImage_UnusedBlockPlatform): # 132
    def updateSize(self):
        self.width = ((self.parent.spritedata[5] & 0xF) + 1) * 16
        self.height = ((self.parent.spritedata[5] >> 4)  + 1) * 16
        super().updateSize()


class SpriteImage_StalagmitePlatform(SLib.SpriteImage): # 133
    def __init__(self, parent):
        super().__init__(parent)

        self.aux.append(SLib.AuxiliaryImage(parent, 48, 156))
        self.aux[0].image = ImageCache['StalagmitePlatformBottom']
        self.aux[0].setPos(24, 60)

        self.image = ImageCache['StalagmitePlatformTop']
        self.dimensions = (0, -8, 64, 40)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('StalagmitePlatformTop', 'stalagmite_platform_top.png')
        SLib.loadIfNotInImageCache('StalagmitePlatformBottom', 'stalagmite_platform_bottom.png')

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(0, 0, self.image)


class SpriteImage_Crow(SLib.SpriteImage_Static): # 134
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Crow'],
            (-3, -2),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Crow', 'crow.png')


class SpriteImage_HangingPlatform(SLib.SpriteImage_Static): # 135
    def __init__(self, parent):
        super().__init__(parent)

        self.aux.append(SLib.AuxiliaryImage(parent, 11, 378))
        self.aux[0].image = ImageCache['HangingPlatformTop']
        self.aux[0].setPos(138, -378)

        self.image = ImageCache['HangingPlatformBottom']
        self.size = (192, 32)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('HangingPlatformTop', 'hanging_platform_top.png')
        SLib.loadIfNotInImageCache('HangingPlatformBottom', 'hanging_platform_bottom.png')


class SpriteImage_RotBulletLauncher(SLib.SpriteImage): # 136
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.dimensions = (-4, 0, 24, 16)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RotLauncherCannon', 'bullet_cannon_rot_0.png')
        SLib.loadIfNotInImageCache('RotLauncherPivot', 'bullet_cannon_rot_1.png')

    def updateSize(self):
        super().updateSize()
        pieces = self.parent.spritedata[3] & 15
        self.yOffset = -pieces * 16
        self.height = (pieces + 1) * 16

    def paint(self, painter):
        super().paint(painter)

        pieces = (self.parent.spritedata[3] & 15) + 1
        pivot1_4 = self.parent.spritedata[4] & 15
        pivot5_8 = self.parent.spritedata[4] >> 4
        startleft1_4 = self.parent.spritedata[5] & 15
        startleft5_8 = self.parent.spritedata[5] >> 4

        pivots = [pivot1_4, pivot5_8]
        startleft = [startleft1_4, startleft5_8]

        ysize = self.height * 1.5

        for piece in range(pieces):
            bitpos = 2 ** (piece % 4)
            if pivots[int(piece / 4)] & bitpos:
                painter.drawPixmap(5, ysize - (piece * 24) - 24, ImageCache['RotLauncherPivot'])
            else:
                xo = 6
                image = ImageCache['RotLauncherCannon']
                if startleft[int(piece / 4)] & bitpos:
                    transform = QtGui.QTransform()
                    transform.rotate(180)
                    image = QtGui.QPixmap(image.transformed(transform))
                    xo = 0
                painter.drawPixmap(xo, ysize - (piece + 1) * 24, image)


class SpriteImage_SpikedStakeDown(SpriteImage_SpikedStake): # 137
    def __init__(self, parent):
        super().__init__(parent)
        self.dir = 'down'
        self.aux.append(SLib.AuxiliaryTrackObject(parent, 16, 64, SLib.AuxiliaryTrackObject.Vertical))

        self.dimensions = (0, 16 - self.SpikeLength, 66, self.SpikeLength)


class SpriteImage_Water(SpriteImage_LiquidOrFog): # 138
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

    def realViewZone(self, painter, zoneRect, viewRect):

        self.paintZone = self.parent.spritedata[5] == 0
        self.top = self.parent.objy
        self.drawCrest = self.parent.spritedata[4] & 15 == 0
        self.risingHeight = (self.parent.spritedata[3] & 0xF) << 4
        self.risingHeight |= self.parent.spritedata[4] >> 4

        if self.parent.spritedata[2] > 7: # falling
            self.risingHeight = -self.risingHeight

        super().realViewZone(painter, zoneRect, viewRect)


class SpriteImage_Lava(SpriteImage_LiquidOrFog): # 139
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

    def realViewZone(self, painter, zoneRect, viewRect):

        self.paintZone = self.parent.spritedata[5] == 0
        self.top = self.parent.objy
        self.drawCrest = self.parent.spritedata[4] & 15 == 0
        self.risingHeight = (self.parent.spritedata[3] & 0xF) << 4
        self.risingHeight |= self.parent.spritedata[4] >> 4

        if self.parent.spritedata[2] > 7: # falling
            self.risingHeight = -self.risingHeight

        super().realViewZone(painter, zoneRect, viewRect)


class SpriteImage_SpikedStakeUp(SpriteImage_SpikedStake): # 140
    def __init__(self, parent):
        super().__init__(parent)
        self.dir = 'up'
        self.aux.append(SLib.AuxiliaryTrackObject(parent, 16, 64, SLib.AuxiliaryTrackObject.Vertical))

        self.dimensions = (0, 0, 66, self.SpikeLength)


class SpriteImage_SpikedStakeRight(SpriteImage_SpikedStake): # 141
    def __init__(self, parent):
        super().__init__(parent)
        self.dir = 'right'
        self.aux.append(SLib.AuxiliaryTrackObject(parent, 64, 16, SLib.AuxiliaryTrackObject.Horizontal))

        self.dimensions = (16 - self.SpikeLength, 0, self.SpikeLength, 66)


class SpriteImage_SpikedStakeLeft(SpriteImage_SpikedStake): # 142
    def __init__(self, parent):
        super().__init__(parent)
        self.dir = 'left'
        self.aux.append(SLib.AuxiliaryTrackObject(parent, 64, 16, SLib.AuxiliaryTrackObject.Horizontal))

        self.dimensions = (0, 0, self.SpikeLength, 66)


class SpriteImage_Arrow(SLib.SpriteImage_StaticMultiple): # 143
    def __init__(self, parent):
        super().__init__(parent)

    @staticmethod
    def loadImages():
        if 'Arrow0' in ImageCache: return
        for i in range(8):
            ImageCache['Arrow%d' % i] = SLib.GetImg('arrow_%d.png' % i)

    def updateSize(self):
        ArrowOffsets = [(3,0), (5,4), (1,3), (5,-1), (3,0), (-1,-1), (0,3), (-1,4)]

        direction = self.parent.spritedata[5] & 7
        self.image = ImageCache['Arrow%d' % direction]

        self.width = self.image.width() / 1.5
        self.height = self.image.height() / 1.5
        self.offset = ArrowOffsets[direction]

        super().updateSize()


class SpriteImage_RedCoin(SLib.SpriteImage_Static): # 144
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['RedCoin'],
            )


class SpriteImage_FloatingBarrel(SLib.SpriteImage_Static): # 145
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['FloatingBarrel'],
            (-16, -9),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FloatingBarrel', 'barrel_floating.png')


class SpriteImage_ChainChomp(SLib.SpriteImage_Static): # 146
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ChainChomp'],
            (-90, -32),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ChainChomp', 'chain_chomp.png')


class SpriteImage_Coin(SLib.SpriteImage_StaticMultiple): # 147
    @staticmethod
    def loadImages():
        if 'CoinF' in ImageCache: return

        pix = QtGui.QPixmap(24, 24)
        pix.fill(Qt.transparent)
        paint = QtGui.QPainter(pix)
        paint.setOpacity(0.9)
        paint.drawPixmap(0, 0, SLib.GetImg('iceblock00.png'))
        paint.setOpacity(0.6)
        paint.drawPixmap(0, 0, ImageCache['Coin'])
        del paint
        ImageCache['CoinF'] = pix

        ImageCache['CoinBubble'] = SLib.GetImg('coin_bubble.png')

    def updateSize(self):
        type = self.parent.spritedata[5] & 0xF

        if type == 0:
            self.image = ImageCache['Coin']
            self.offset = (0, 0)
        elif type == 0xF:
            self.image = ImageCache['CoinF']
            self.offset = (0, 0)
        elif type in (1, 2, 4):
            self.image = ImageCache['CoinBubble']
            self.offset = (-4, -4)
        else:
            self.image = ImageCache['SpecialCoin']
            self.offset = (0, 0)

        super().updateSize()


class SpriteImage_Spring(SLib.SpriteImage_Static): # 148
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Spring'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Spring', 'spring.png')


class SpriteImage_RotationControllerSpinning(SLib.SpriteImage): # 149
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.setZValue(100000)


class SpriteImage_Porcupuffer(SLib.SpriteImage_Static): # 151
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Porcupuffer'],
            (-16, -18),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Porcupuffer', 'porcu_puffer.png')


class SpriteImage_QuestionSwitchUnused(SpriteImage_Switch): # 153
    def __init__(self, parent):
        super().__init__(parent)
        self.switchType = 'Q'


class SpriteImage_StarCoinLineControlled(SpriteImage_StarCoin): # 155
    pass


class SpriteImage_RedCoinRing(SLib.SpriteImage): # 156
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryImage(parent, 243, 248))
        self.aux[0].image = ImageCache['RedCoinRing']
        self.aux[0].setPos(-10, -15)
        self.aux[0].hover = False

        self.dimensions = (-10, -8, 37, 48)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RedCoinRing', 'redcoinring.png')


class SpriteImage_BigBrick(SLib.SpriteImage_StaticMultiple): # 157
    def __init__(self, parent):
        super().__init__(parent)
        self.size = (48, 48)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigBrick', 'big_brick.png')
        SLib.loadIfNotInImageCache('ShipKey', 'ship_key.png')
        SLib.loadIfNotInImageCache('5Coin', '5_coin.png')
        if 'YoshiFire' not in ImageCache:
            pix = QtGui.QPixmap(48, 24)
            pix.fill(Qt.transparent)
            paint = QtGui.QPainter(pix)
            paint.drawPixmap(0, 0, ImageCache['Blocks'][9])
            paint.drawPixmap(24, 0, ImageCache['Blocks'][3])
            del paint
            ImageCache['YoshiFire'] = pix

    def paint(self, painter):
        super().paint(painter)

        power = self.parent.spritedata[5] & 15

        images = [
            None,                     # empty
            ImageCache['Blocks'][1],  # coin
            ImageCache['Blocks'][2],  # mushroom
            ImageCache['Blocks'][3],  # fire
            ImageCache['Blocks'][4],  # propeller
            ImageCache['Blocks'][5],  # penguin
            ImageCache['Blocks'][6],  # mini
            ImageCache['Blocks'][7],  # star
            None,                     # empty
            ImageCache['YoshiFire'],  # yoshi + fire
            ImageCache['5Coin'],      # 5coin
            ImageCache['Blocks'][11], # 1up
            None,                     # empty
            None,                     # empty
            ImageCache['ShipKey'],    # key
            ImageCache['Blocks'][15], # ice
            ]

        # Make sure we have the correct offsets for the non-24x24 powerup overlays
        if power == 9:
            x = 12
            y = 24
        elif power == 14:
            x = 22
            y = 18
        else:
            x = 24
            y = 24

        painter.drawPixmap(0, 0, ImageCache['BigBrick'])
        if images[power] != None:
            painter.drawPixmap(x, y, images[power])


class SpriteImage_FireSnake(SLib.SpriteImage_StaticMultiple): # 158
    def __init__(self, parent):
        super().__init__(parent)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FireSnakeWait', 'fire_snake_0.png')
        SLib.loadIfNotInImageCache('FireSnake', 'fire_snake_1.png')

    def updateSize(self):

        move = self.parent.spritedata[5] & 15
        if move == 1:
            del self.size
            self.yOffset = 0
            self.image = ImageCache['FireSnakeWait']
        else:
            self.size = (20, 32)
            self.yOffset = -16
            self.image = ImageCache['FireSnake']

        super().updateSize()


class SpriteImage_UnusedBlockPlatform2(SpriteImage_UnusedBlockPlatform): # 160
    def updateSize(self):
        self.width = ((self.parent.spritedata[4] & 0xF) + 1) * 16
        self.height = ((self.parent.spritedata[4] >> 4)  + 1) * 16
        super().updateSize()


class SpriteImage_PipeBubbles(SLib.SpriteImage_StaticMultiple): # 161
    @staticmethod
    def loadImages():
        if 'PipeBubblesU' in ImageCache: return
        transform90 = QtGui.QTransform()
        transform180 = QtGui.QTransform()
        transform270 = QtGui.QTransform()
        transform90.rotate(90)
        transform180.rotate(180)
        transform270.rotate(270)

        image = SLib.GetImg('pipe_bubbles.png', True)
        ImageCache['PipeBubbles' + 'U'] = QtGui.QPixmap.fromImage(image)
        ImageCache['PipeBubbles' + 'R'] = QtGui.QPixmap.fromImage(image.transformed(transform90))
        ImageCache['PipeBubbles' + 'D'] = QtGui.QPixmap.fromImage(image.transformed(transform180))
        ImageCache['PipeBubbles' + 'L'] = QtGui.QPixmap.fromImage(image.transformed(transform270))

    def updateSize(self):

        direction = self.parent.spritedata[5] & 15
        if direction == 0 or direction > 3:
            self.dimensions = (0, -52, 32, 53)
            direction = 'U'
        elif direction == 1:
            self.dimensions = (0, 16, 32, 53)
            direction = 'D'
        elif direction == 2:
            self.dimensions = (16, -16, 53, 32)
            direction = 'R'
        elif direction == 3:
            self.dimensions = (-52, -16, 53, 32)
            direction = 'L'

        self.image = ImageCache['PipeBubbles%s' % direction]

        super().updateSize()


class SpriteImage_BlockTrain(SLib.SpriteImage): # 166
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BlockTrain', 'block_train.png')

    def updateSize(self):
        super().updateSize()
        length = self.parent.spritedata[5] & 15
        self.width = (length + 3) * 16

    def paint(self, painter):
        super().paint(painter)

        endpiece = ImageCache['BlockTrain']
        painter.drawPixmap(0, 0, endpiece)
        painter.drawTiledPixmap(24, 0, (self.width * 1.5) - 48, 24, ImageCache['BlockTrain'])
        painter.drawPixmap((self.width * 1.5) - 24, 0, endpiece)


class SpriteImage_ChestnutGoomba(SLib.SpriteImage_Static): # 170
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ChestnutGoomba'],
            (-6, -8),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ChestnutGoomba', 'chestnut_goomba.png')


class SpriteImage_PowerupBubble(SLib.SpriteImage_Static): # 171
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MushroomBubble'],
            (-8, -8),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MushroomBubble', 'powerup_bubble.png')


class SpriteImage_ScrewMushroomWithBolt(SpriteImage_ScrewMushroom): # 172
    def __init__(self, parent):
        super().__init__(parent)
        self.hasBolt = True


class SpriteImage_GiantFloatingLog(SLib.SpriteImage_Static): # 173
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['GiantFloatingLog'],
            (-152, -32),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantFloatingLog', 'giant_floating_log.png')


class SpriteImage_OneWayGate(SLib.SpriteImage_StaticMultiple): # 174
    @staticmethod
    def loadImages():
        if '1WayGate00' in ImageCache: return

        # This loop generates all 1-way gate images from a single image
        gate = SLib.GetImg('1_way_gate.png', True)
        for flip in (0, 1):
            for direction in range(4):
                if flip:
                    newgate = QtGui.QPixmap.fromImage(gate.mirrored(True, False))
                else:
                    newgate = QtGui.QPixmap.fromImage(gate)

                width = 24
                height = 60 # constants, from the PNG
                xsize = width if direction in (0, 1) else height
                ysize = width if direction in (2, 3) else height
                if direction == 0:
                    rotValue = 0
                    xpos = 0
                    ypos = 0
                elif direction == 1:
                    rotValue = 180
                    xpos = -width
                    ypos = -height
                elif direction == 2:
                    rotValue = 270
                    xpos = -width
                    ypos = 0
                elif direction == 3:
                    rotValue = 90
                    xpos = 0
                    ypos = -height

                dest = QtGui.QPixmap(xsize, ysize)
                dest.fill(Qt.transparent)
                p = QtGui.QPainter(dest)
                p.rotate(rotValue)
                p.drawPixmap(xpos, ypos, newgate)
                del p

                ImageCache['1WayGate%d%d' % (flip, direction)] = dest

    def updateSize(self):

        flag = (self.parent.spritedata[5] >> 4) & 1
        direction = self.parent.spritedata[5] & 3
        self.image = ImageCache['1WayGate%d%d' % (flag, direction)]

        if direction > 3: direction = 3
        self.offset = (
            (0, -24),
            (0, 0),
            (-24, 0),
            (0, 0),
            )[direction]

        super().updateSize()


class SpriteImage_FlyingQBlock(SLib.SpriteImage): # 175
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.dimensions = (-12, -16, 42, 32)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FlyingQBlock', 'flying_qblock.png')

    def paint(self, painter):
        super().paint(painter)

        color = self.parent.spritedata[4] >> 4
        if color == 0 or color > 3:
            block = 9
        elif color == 1:
            block = 59
        elif color == 2:
            block = 109
        elif color == 3:
            block = 159

        painter.drawPixmap(0, 0, ImageCache['FlyingQBlock'])
        painter.drawPixmap(18, 23, ImageCache['Overrides'][block])


class SpriteImage_RouletteBlock(SLib.SpriteImage_Static): # 176
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['RouletteBlock'],
            (-6, -6),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RouletteBlock', 'roulette.png')


class SpriteImage_FireChomp(SLib.SpriteImage_Static): # 177
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['FireChomp'],
            (-2, -20),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FireChomp', 'fire_chomp.png')


class SpriteImage_ScalePlatform(SLib.SpriteImage): # 178
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'WoodenPlatformL' not in ImageCache:
            ImageCache['WoodenPlatformL'] = SLib.GetImg('wood_platform_left.png')
            ImageCache['WoodenPlatformM'] = SLib.GetImg('wood_platform_middle.png')
            ImageCache['WoodenPlatformR'] = SLib.GetImg('wood_platform_right.png')
        if 'ScaleRopeH' not in ImageCache:
            ImageCache['ScaleRopeH'] = SLib.GetImg('scale_rope_horz.png')
            ImageCache['ScaleRopeV'] = SLib.GetImg('scale_rope_vert.png')
            ImageCache['ScalePulley'] = SLib.GetImg('scale_pulley.png')

    def updateSize(self):
        super().updateSize()

        info1 = self.parent.spritedata[4]
        info2 = self.parent.spritedata[5]
        self.parent.platformWidth = (info1 & 0xF0) >> 4
        if self.parent.platformWidth > 12: self.parent.platformWidth = -1

        self.parent.ropeLengthLeft = info1 & 0xF
        self.parent.ropeLengthRight = (info2 & 0xF0) >> 4
        self.parent.ropeWidth = info2 & 0xF

        ropeWidth = self.parent.ropeWidth * 16
        platformWidth = (self.parent.platformWidth + 3) * 16
        self.width = ropeWidth + platformWidth

        maxRopeHeight = max(self.parent.ropeLengthLeft, self.parent.ropeLengthRight)
        self.height = maxRopeHeight * 16 + 19
        if maxRopeHeight == 0: self.height += 8

        self.xOffset = -(self.parent.platformWidth + 3) * 8

    def paint(self, painter):
        super().paint(painter)

        # this is FUN!! (not)
        ropeLeft = self.parent.ropeLengthLeft * 24 + 4
        if self.parent.ropeLengthLeft == 0: ropeLeft += 12

        ropeRight = self.parent.ropeLengthRight * 24 + 4
        if self.parent.ropeLengthRight == 0: ropeRight += 12

        ropeWidth = self.parent.ropeWidth * 24 + 8
        platformWidth = (self.parent.platformWidth + 3) * 24

        ropeX = platformWidth / 2 - 4

        painter.drawTiledPixmap(ropeX + 8, 0, ropeWidth - 16, 8, ImageCache['ScaleRopeH'])

        ropeVertImage = ImageCache['ScaleRopeV']
        painter.drawTiledPixmap(ropeX, 8, 8, ropeLeft - 8, ropeVertImage)
        painter.drawTiledPixmap(ropeX + ropeWidth - 8, 8, 8, ropeRight - 8, ropeVertImage)

        pulleyImage = ImageCache['ScalePulley']
        painter.drawPixmap(ropeX, 0, pulleyImage)
        painter.drawPixmap(ropeX + ropeWidth - 20, 0, pulleyImage)

        platforms = [(0, ropeLeft), (ropeX + ropeWidth - int(platformWidth / 2) - 4, ropeRight)]
        for x, y in platforms:
            painter.drawPixmap(x, y, ImageCache['WoodenPlatformL'])
            painter.drawTiledPixmap(x + 27, y, (platformWidth - 51), 24, ImageCache['WoodenPlatformM'])
            painter.drawPixmap(x + platformWidth - 24, y, ImageCache['WoodenPlatformR'])


class SpriteImage_SpecialExit(SLib.SpriteImage): # 179
    def __init__(self, parent):
        super().__init__(parent)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def updateSize(self):
        super().updateSize()

        w = (self.parent.spritedata[4] & 15) + 1
        h = (self.parent.spritedata[5] >> 4) + 1
        if w == 1 and h == 1: # no point drawing a 1x1 outline behind the self.parent
            self.aux[0].setSize(0,0)
            return
        self.aux[0].setSize(w * 24, h * 24)


class SpriteImage_CheepChomp(SLib.SpriteImage_Static): # 180
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['CheepChomp'],
            (-32, -16),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CheepChomp', 'cheep_chomp.png')


class SpriteImage_EventDoor(SpriteImage_Door): # 182
    def __init__(self, parent):
        super().__init__(parent)
        self.alpha = 0.5


class SpriteImage_ToadBalloon(SLib.SpriteImage_Static): # 185
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ToadBalloon'],
            (-4, -4),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ToadBalloon', 'toad_balloon.png')


class SpriteImage_PlayerBlock(SLib.SpriteImage_Static): # 187
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PlayerBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PlayerBlock', 'playerblock.png')


class SpriteImage_MidwayPoint(SLib.SpriteImage_Static): # 188
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MidwayFlag'],
            (0, -37),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MidwayFlag', 'midway_flag.png')


class SpriteImage_LarryKoopa(SLib.SpriteImage_Static): # 189
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['LarryKoopa'],
            (-17, -33),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LarryKoopa', 'Larry_Koopa.png')


class SpriteImage_TiltingGirderUnused(SLib.SpriteImage_Static): # 190
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['TiltingGirder'],
            (0, -18),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('TiltingGirder', 'tilting_girder.png')


class SpriteImage_TileEvent(SLib.SpriteImage): # 191
    def __init__(self, parent):
        super().__init__(parent)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def updateSize(self):
        super().updateSize()

        w = self.parent.spritedata[5] >> 4
        h = self.parent.spritedata[5] & 0xF
        if w == 0: w = 1
        if h == 0: h = 1
        if w == 1 and h == 1: # no point drawing a 1x1 outline behind the self.parent
            self.aux[0].setSize(0,0)
            return
        self.aux[0].setSize(w * 24, h * 24)


class SpriteImage_Urchin(SLib.SpriteImage_Static): # 193
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Urchin'],
            (-12, -14),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Urchin', 'urchin.png')


class SpriteImage_MegaUrchin(SLib.SpriteImage_Static): # 194
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MegaUrchin'],
            (-40, -46),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MegaUrchin', 'mega_urchin.png')


class SpriteImage_HuckitCrab(SLib.SpriteImage_StaticMultiple): # 195
    @staticmethod
    def loadImages():
        if 'HuckitCrabR' in ImageCache: return
        Huckitcrab = SLib.GetImg('huckit_crab.png', True)
        ImageCache['HuckitCrabL'] = QtGui.QPixmap.fromImage(Huckitcrab)
        ImageCache['HuckitCrabR'] = QtGui.QPixmap.fromImage(Huckitcrab.mirrored(True, False))

    def updateSize(self):
        info = self.parent.spritedata[5]

        if info == 1:
            self.image = ImageCache['HuckitCrabR']
            self.xOffset = 0
        else:
            if info == 13:
                self.image = ImageCache['HuckitCrabR']
                self.xOffset = 0
            else:
                self.image = ImageCache['HuckitCrabL']
                self.xOffset = -16

        super().updateSize()


class SpriteImage_Fishbones(SLib.SpriteImage_StaticMultiple): # 196
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = (0, -2)

    def updateSize(self):

        direction = self.parent.spritedata[5] >> 4
        if direction == 1:
            self.image = ImageCache['FishbonesR']
        else:
            self.image = ImageCache['FishbonesL']

        super().updateSize()

    @staticmethod
    def loadImages():
        if 'FishbonesL' in ImageCache: return
        Fishbones = SLib.GetImg('fishbones.png', True)
        ImageCache['FishbonesL'] = QtGui.QPixmap.fromImage(Fishbones)
        ImageCache['FishbonesR'] = QtGui.QPixmap.fromImage(Fishbones.mirrored(True, False))


class SpriteImage_Clam(SLib.SpriteImage_StaticMultiple): # 197
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = (-26, -53)

    @staticmethod
    def loadImages():
        if 'ClamEmpty' in ImageCache: return

        if 'PSwitch' not in ImageCache:
            p = SLib.GetImg('p_switch.png', True)
            ImageCache['PSwitch'] = QtGui.QPixmap.fromImage(p)
            ImageCache['PSwitchU'] = QtGui.QPixmap.fromImage(p.mirrored(True, True))

        SLib.loadIfNotInImageCache('ClamEmpty', 'clam.png')

        overlays = (
            (26, 22, 'Star', ImageCache['StarCoin']),
            (40, 42, '1Up', ImageCache['Blocks'][11]),
            (40, 42, 'PSwitch', ImageCache['PSwitch']),
            (40, 42, 'PSwitchU', ImageCache['PSwitchU']),
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
        painter.drawPixmap(28, 42, ImageCache['Coin'])
        painter.drawPixmap(52, 42, ImageCache['Coin'])
        del painter
        ImageCache['Clam2Coin'] = newPix

    def updateSize(self):

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

        super().updateSize()


class SpriteImage_Giantgoomba(SLib.SpriteImage_Static): # 198
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Giantgoomba'],
            (-6, -19),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Giantgoomba', 'giantgoomba.png')


class SpriteImage_Megagoomba(SLib.SpriteImage_Static): # 199
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Megagoomba'],
            (-11, -37),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Megagoomba', 'megagoomba.png')


class SpriteImage_Microgoomba(SLib.SpriteImage_Static): # 200
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Microgoomba'],
            (4, 8),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Microgoomba', 'microgoomba.png')


class SpriteImage_Icicle(SLib.SpriteImage_StaticMultiple): # 201
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('IcicleSmallS', 'icicle_small_static.png')
        SLib.loadIfNotInImageCache('IcicleLargeS', 'icicle_large_static.png')

    def updateSize(self):

        size = self.parent.spritedata[5] & 1
        if size == 0:
            self.image = ImageCache['IcicleSmallS']
        else:
            self.image = ImageCache['IcicleLargeS']

        super().updateSize()


class SpriteImage_MGCannon(SLib.SpriteImage_Static): # 202
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MGCannon'],
            (-12, -42),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MGCannon', 'mg_cannon.png')


class SpriteImage_MGChest(SLib.SpriteImage_Static): # 203
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MGChest'],
            (-12, -11),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MGChest', 'mg_chest.png')


class SpriteImage_GiantBubbleNormal(SpriteImage_GiantBubble): # 205
    pass


class SpriteImage_Zoom(SLib.SpriteImage): # 206
    def __init__(self, parent):
        super().__init__(parent)
        self.aux.append(SLib.AuxiliaryRectOutline(parent, 0, 0))

    def updateSize(self):
        super().updateSize()

        w = self.parent.spritedata[5]+1
        h = self.parent.spritedata[4]+1
        if w == 1 and h == 1: # no point drawing a 1x1 outline behind the self.parent
            self.aux[0].setSize(0,0,0,0)
            return
        self.aux[0].setSize(w*24, h*24, 0, 24-(h*24))


class SpriteImage_QBlock(SpriteImage_Block): # 207
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 49


class SpriteImage_QBlockUnused(SpriteImage_Block): # 208
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 49
        self.eightIsMushroom = True
        self.twelveIsMushroom = True


class SpriteImage_BrickBlock(SpriteImage_Block): # 209
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 48


class SpriteImage_RollingHill(SLib.SpriteImage): # 212
    RollingHillSizes = [0, 18*16, 32*16, 50*16, 64*16, 10*16, 14*16, 20*16, 0, 0, 0, 0, 0, 0, 0, 0]
    def __init__(self, parent):
        super().__init__(parent)

        size = (self.parent.spritedata[3] >> 4) & 0xF
        realSize = self.RollingHillSizes[size]

        self.aux.append(SLib.AuxiliaryCircleOutline(parent, realSize))

    def updateSize(self):
        super().updateSize()

        size = (self.parent.spritedata[3] >> 4) & 0xF
        if size != 0: realSize = self.RollingHillSizes[size]
        else:
            adjust = self.parent.spritedata[4] & 0xF
            realSize = 32 * (adjust + 1)

        self.aux[0].setSize(realSize)
        self.aux[0].update()


class SpriteImage_FreefallPlatform(SLib.SpriteImage_Static): # 214
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['FreefallGH'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FreefallGH', 'freefall_gh_platform.png')


class SpriteImage_Poison(SpriteImage_LiquidOrFog): # 216
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

    def realViewZone(self, painter, zoneRect, viewRect):

        self.paintZone = self.parent.spritedata[5] == 0
        self.top = self.parent.objy
        self.drawCrest = self.parent.spritedata[4] & 15 == 0
        self.risingHeight = (self.parent.spritedata[3] & 0xF) << 4
        self.risingHeight |= self.parent.spritedata[4] >> 4

        if self.parent.spritedata[2] > 7: # falling
            self.risingHeight = -self.risingHeight

        super().realViewZone(painter, zoneRect, viewRect)


class SpriteImage_LineBlock(SLib.SpriteImage): # 219
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryImage(parent, 24, 24))
        self.aux[0].setPos(0, 32)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LineBlock', 'lineblock.png')

    def updateSize(self):

        direction = self.parent.spritedata[4] >> 4
        widthA = self.parent.spritedata[5] & 15
        widthB = self.parent.spritedata[5] >> 4
        distance = self.parent.spritedata[4] & 0xF

        if direction & 1:
            # reverse them if going down
            widthA, widthB = widthB, widthA

        noWidthA = False
        aA = 1
        if widthA == 0:
            widthA = 1
            noWidthA = True
            aA = 0.25
        noWidthB = False
        aB = 0.5
        if widthB == 0:
            widthB = 1
            noWidthB = True
            aB = 0.25

        blockimg = ImageCache['LineBlock']

        if widthA > widthB:
            totalWidth = widthA
        else:
            totalWidth = widthB

        imgA = QtGui.QPixmap(widthA * 24, 24)
        imgB = QtGui.QPixmap(widthB * 24, 24)
        imgA.fill(Qt.transparent)
        imgB.fill(Qt.transparent)
        painterA = QtGui.QPainter(imgA)
        painterB = QtGui.QPainter(imgB)
        painterA.setOpacity(aA)
        painterB.setOpacity(1)

        if totalWidth > 1:
            for i in range(totalWidth):
                # 'j' is just 'i' out of order.
                # This causes the lineblock to be painted from the
                # sides in, rather than linearly.
                if i & 1:
                    j = totalWidth - (i // 2) - 1
                else:
                    j = i // 2
                xA = j * 24 * ((widthA - 1) / (totalWidth - 1))
                xB = j * 24 * ((widthB - 1) / (totalWidth - 1))

                # now actually paint it
                painterA.drawPixmap(xA, 0, blockimg)
                painterB.drawPixmap(xB, 0, blockimg)
        else:
            # special-case to avoid ZeroDivisionError
            painterA.drawPixmap(0, 0, blockimg)
            painterB.drawPixmap(0, 0, blockimg)

        del painterA, painterB

        if widthA >= 1:
            self.width = widthA * 16
        else:
            self.width = 16

        xposA = (widthA * -8) + 8
        if widthA == 0: xposA = 0
        xposB = (widthA - widthB) * 12
        if widthA == 0: xposB = 0
        if direction & 1:
            # going down
            yposB = distance * 24
        else:
            # going up
            yposB = -distance * 24

        newImgB = QtGui.QPixmap(imgB.width(), imgB.height())
        newImgB.fill(Qt.transparent)
        painterB2 = QtGui.QPainter(newImgB)
        painterB2.setOpacity(aB)
        painterB2.drawPixmap(0, 0, imgB)
        del painterB2
        imgB = newImgB

        self.image = imgA
        self.xOffset = xposA
        self.aux[0].setSize(imgB.width(), imgB.height())
        self.aux[0].image = imgB
        self.aux[0].setPos(xposB, yposB)

        super().updateSize()

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(0, 0, self.image)


class SpriteImage_InvisibleBlock(SpriteImage_Block): # 221
    def __init__(self, parent):
        super().__init__(parent)
        self.eightIsMushroom = True


class SpriteImage_ConveyorSpike(SLib.SpriteImage_Static): # 222
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SpikeU'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpikeU', 'spike_up.png')


class SpriteImage_SpringBlock(SLib.SpriteImage_StaticMultiple): # 223
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpringBlock1', 'spring_block.png')
        SLib.loadIfNotInImageCache('SpringBlock2', 'spring_block_alt.png')

    def updateSize(self):

        type = self.parent.spritedata[5] & 1
        self.image = ImageCache['SpringBlock2'] if type else ImageCache['SpringBlock1']

        super().updateSize()


class SpriteImage_JumboRay(SLib.SpriteImage_StaticMultiple): # 224
    @staticmethod
    def loadImages():
        if 'JumboRayL' in ImageCache: return
        Ray = SLib.GetImg('jumbo_ray.png', True)
        ImageCache['JumboRayL'] = QtGui.QPixmap.fromImage(Ray)
        ImageCache['JumboRayR'] = QtGui.QPixmap.fromImage(Ray.mirrored(True, False))

    def updateSize(self):

        flyleft = self.parent.spritedata[4] & 15
        if flyleft:
            self.xOffset = 0
            self.image = ImageCache['JumboRayL']
        else:
            self.xOffset = -152
            self.image = ImageCache['JumboRayR']

        super().updateSize()


class SpriteImage_FloatingCoin(SpriteImage_SpecialCoin): # 225
    pass


class SpriteImage_GiantBubbleUnused(SpriteImage_GiantBubble): # 226
    pass


class SpriteImage_PipeCannon(SLib.SpriteImage): # 227
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        # self.aux[0] is the pipe image
        self.aux.append(SLib.AuxiliaryImage(parent, 24, 24))
        self.aux[0].hover = False

        # self.aux[1] is the trajectory indicator
        self.aux.append(SLib.AuxiliaryPainterPath(parent, QtGui.QPainterPath(), 24, 24))
        self.aux[1].fillFlag = False

        self.aux[0].setZValue(self.aux[1].zValue() + 1)

        self.size = (32, 64)

    @staticmethod
    def loadImages():
        if 'PipeCannon0' in ImageCache: return
        for i in range(7):
            ImageCache['PipeCannon%d' % i] = SLib.GetImg('pipe_cannon_%d.png' % i)

    def updateSize(self):
        super().updateSize()

        fireDirection = (self.parent.spritedata[5] & 0xF) % 7

        self.aux[0].image = ImageCache['PipeCannon%d' % (fireDirection)]

        if fireDirection == 0:
            # 30 deg to the right
            self.aux[0].setSize(84, 101, 0, -5)
            path = QtGui.QPainterPath(QtCore.QPoint(0, 184))
            path.cubicTo(QtCore.QPoint(152, -24), QtCore.QPoint(168, -24), QtCore.QPoint(264, 48))
            path.lineTo(QtCore.QPoint(480, 216))
            self.aux[1].setSize(480, 216, 24, -120)
        elif fireDirection == 1:
            # 30 deg to the left
            self.aux[0].setSize(85, 101, -36, -5)
            path = QtGui.QPainterPath(QtCore.QPoint(480 - 0, 184))
            path.cubicTo(QtCore.QPoint(480 - 152, -24), QtCore.QPoint(480 - 168, -24), QtCore.QPoint(480 - 264, 48))
            path.lineTo(QtCore.QPoint(480 - 480, 216))
            self.aux[1].setSize(480, 216, -480 + 24, -120)
        elif fireDirection == 2:
            # 15 deg to the right
            self.aux[0].setSize(60, 102, 0, -6)
            path = QtGui.QPainterPath(QtCore.QPoint(0, 188))
            path.cubicTo(QtCore.QPoint(36, -36), QtCore.QPoint(60, -36), QtCore.QPoint(96, 84))
            path.lineTo(QtCore.QPoint(144, 252))
            self.aux[1].setSize(144, 252, 30, -156)
        elif fireDirection == 3:
            # 15 deg to the left
            self.aux[0].setSize(61, 102, -12, -6)
            path = QtGui.QPainterPath(QtCore.QPoint(144 - 0, 188))
            path.cubicTo(QtCore.QPoint(144 - 36, -36), QtCore.QPoint(144 - 60, -36), QtCore.QPoint(144 - 96, 84))
            path.lineTo(QtCore.QPoint(144 - 144, 252))
            self.aux[1].setSize(144, 252, -144 + 18, -156)
        elif fireDirection == 4:
            # Straight up
            self.aux[0].setSize(135, 132, -43, -35)
            path = QtGui.QPainterPath(QtCore.QPoint(26, 0))
            path.lineTo(QtCore.QPoint(26, 656))
            self.aux[1].setSize(48, 656, 0, -632)
        elif fireDirection == 5:
            # 45 deg to the right
            self.aux[0].setSize(90, 98, 0, -1)
            path = QtGui.QPainterPath(QtCore.QPoint(0, 320))
            path.lineTo(QtCore.QPoint(264, 64))
            path.cubicTo(QtCore.QPoint(348, -14), QtCore.QPoint(420, -14), QtCore.QPoint(528, 54))
            path.lineTo(QtCore.QPoint(1036, 348))
            self.aux[1].setSize(1036, 348, 24, -252)
        elif fireDirection == 6:
            # 45 deg to the left
            self.aux[0].setSize(91, 98, -42, -1)
            path = QtGui.QPainterPath(QtCore.QPoint(1036 - 0, 320))
            path.lineTo(QtCore.QPoint(1036 - 264, 64))
            path.cubicTo(QtCore.QPoint(1036 - 348, -14), QtCore.QPoint(1036 - 420, -14), QtCore.QPoint(1036 - 528, 54))
            path.lineTo(QtCore.QPoint(1036 - 1036, 348))
            self.aux[1].setSize(1036, 348, -1036 + 24, -252)
        self.aux[1].SetPath(path)


class SpriteImage_ExtendShroom(SLib.SpriteImage): # 228
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False
        self.parent.setZValue(24999)

    @staticmethod
    def loadImages():
        if 'ExtendShroomB' in ImageCache: return
        ImageCache['ExtendShroomB'] = SLib.GetImg('extend_shroom_big.png')
        ImageCache['ExtendShroomS'] = SLib.GetImg('extend_shroom_small.png')
        ImageCache['ExtendShroomC'] = SLib.GetImg('extend_shroom_cont.png')
        ImageCache['ExtendShroomStem'] = SLib.GetImg('extend_shroom_stem.png')

    def updateSize(self):

        props = self.parent.spritedata[5]
        width = self.parent.spritedata[4] & 1
        start = (props & 0x10) >> 4
        stemlength = props & 0xF

        if start == 0: # contracted
            self.image = ImageCache['ExtendShroomC']
            self.width = 32
        else:
            if width == 0: # big
                self.image = ImageCache['ExtendShroomB']
                self.width = 160
            else: # small
                self.image = ImageCache['ExtendShroomS']
                self.width = 96

        self.xOffset = 8 - (self.width / 2)
        self.height = (stemlength * 16) + 48

        super().updateSize()

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, self.image)
        painter.drawTiledPixmap(
            (self.width * 1.5) / 2 - 14,
            48,
            28,
            (self.height * 1.5) - 48,
            ImageCache['ExtendShroomStem'],
            )


class SpriteImage_SandPillar(SLib.SpriteImage_Static): # 229
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SandPillar'],
            (-33, -150),
            )
        self.alpha = 0.65

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SandPillar', 'sand_pillar.png')


class SpriteImage_Bramball(SLib.SpriteImage_Static): # 230
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Bramball'],
            (-32, -48),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Bramball', 'bramball.png')


class SpriteImage_WiggleShroom(SLib.SpriteImage): # 231
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'WiggleShroomL' in ImageCache: return
        ImageCache['WiggleShroomL'] = SLib.GetImg('wiggle_shroom_left.png')
        ImageCache['WiggleShroomM'] = SLib.GetImg('wiggle_shroom_middle.png')
        ImageCache['WiggleShroomR'] = SLib.GetImg('wiggle_shroom_right.png')
        ImageCache['WiggleShroomS'] = SLib.GetImg('wiggle_shroom_stem.png')

    def updateSize(self):
        super().updateSize()

        width = (self.parent.spritedata[4] & 0xF0) >> 4
        stemlength = self.parent.spritedata[3] & 3

        self.xOffset = -(width * 8) - 20
        self.width = (width * 16) + 56
        self.height = (stemlength * 16) + 64

        self.parent.setZValue(24999)

    def paint(self, painter):
        super().paint(painter)

        xsize = self.width * 1.5
        painter.drawPixmap(0, 0, ImageCache['WiggleShroomL'])
        painter.drawTiledPixmap(18, 0, xsize - 36, 24, ImageCache['WiggleShroomM'])
        painter.drawPixmap(xsize - 18, 0, ImageCache['WiggleShroomR'])
        painter.drawTiledPixmap((xsize / 2) - 12, 24, 24, (self.height * 1.5) - 24, ImageCache['WiggleShroomS'])


class SpriteImage_MechaKoopa(SLib.SpriteImage_Static): # 232
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MechaKoopa'],
            (-8, -14),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MechaKoopa', 'mechakoopa.png')


class SpriteImage_Bulber(SLib.SpriteImage): # 233
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryImage(parent, 243, 248))
        self.aux[0].image = ImageCache['Bulber']
        self.aux[0].setPos(-8, 0)

        self.dimensions = (2, -4, 50, 43)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Bulber', 'bulber.png')


class SpriteImage_PCoin(SLib.SpriteImage_Static): # 237
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PCoin'],
            )


class SpriteImage_Foo(SLib.SpriteImage_Static): # 238
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Foo'],
            (-8, -16),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Foo', 'foo.png')


class SpriteImage_GiantWiggler(SLib.SpriteImage_Static): # 240
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['GiantWiggler'],
            (-24, -64),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantWiggler', 'giant_wiggler.png')


class SpriteImage_FallingLedgeBar(SLib.SpriteImage_Static): # 242
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['FallingLedgeBar'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FallingLedgeBar', 'falling_ledge_bar.png')


class SpriteImage_EventDeactivBlock(SLib.SpriteImage_Static): # 252
    def __init__(self, parent):
        super().__init__(self)
        self.image = SLib.Tiles[49].main # ? block


class SpriteImage_RotControlledCoin(SpriteImage_SpecialCoin): # 253
    pass


class SpriteImage_RotControlledPipe(SpriteImage_PipeStationary): # 254
    def updateSize(self):
        self.length = (self.parent.spritedata[4] >> 4) + 2
        super().updateSize()


class SpriteImage_RotatingQBlock(SpriteImage_Block): # 255
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 49
        self.contentsNybble = 4
        self.twelveIsMushroom = True
        self.rotates = True


class SpriteImage_RotatingBrickBlock(SpriteImage_Block): # 256
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 48
        self.contentsNybble = 4
        self.twelveIsMushroom = True
        self.rotates = True


class SpriteImage_MoveWhenOnMetalLavaBlock(SLib.SpriteImage_StaticMultiple): # 257
    @staticmethod
    def loadImages():
        if 'MetalLavaBlock0' in ImageCache: return
        ImageCache['MetalLavaBlock0'] = SLib.GetImg('lava_iron_block_0.png')
        ImageCache['MetalLavaBlock1'] = SLib.GetImg('lava_iron_block_1.png')
        ImageCache['MetalLavaBlock2'] = SLib.GetImg('lava_iron_block_2.png')

    def updateSize(self):

        size = (self.parent.spritedata[5] & 0xF) % 3
        self.image = ImageCache['MetalLavaBlock%d' % size]

        super().updateSize()


class SpriteImage_RegularDoor(SpriteImage_Door): # 259
    pass


class SpriteImage_MovementController_TwoWayLine(SLib.SpriteImage): # 260
    def __init__(self, parent):
        super().__init__(parent)
        self.aux.append(SLib.AuxiliaryTrackObject(parent, 16, 16, SLib.AuxiliaryTrackObject.Horizontal))

    def updateSize(self):
        super().updateSize()

        direction = (self.parent.spritedata[3] & 0xF) % 4
        distance = (self.parent.spritedata[5] >> 4) + 1

        if direction <= 1: # horizontal
            self.aux[0].direction = 1
            self.aux[0].setSize(distance * 16, 16)
        else: # vertical
            self.aux[0].direction = 2
            self.aux[0].setSize(16, distance * 16)

        if direction == 0 or direction == 3: # right, down
            self.aux[0].setPos(0, 0)
        elif direction == 1: # left
            self.aux[0].setPos((-distance * 24) + 24, 0)
        elif direction == 2: # up
            self.aux[0].setPos(0, (-distance * 24) + 24)


class SpriteImage_OldStoneBlock_MovementControlled(SpriteImage_OldStoneBlock): # 261
    def __init__(self, parent):
        super().__init__(parent)
        self.hasMovementAux = False


class SpriteImage_PoltergeistItem(SLib.SpriteImage): # 262
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryImage(parent, 60, 60))
        self.aux[0].image = ImageCache['PolterQBlock']
        self.aux[0].setPos(-18, -18)
        self.aux[0].hover = False

    @staticmethod
    def loadImages():
        if 'PolterQBlock' in ImageCache: return

        SLib.loadIfNotInImageCache('GhostHouseStand', 'ghost_house_stand.png')

        polterstand = SLib.GetImg('polter_stand.png')
        polterblock = SLib.GetImg('polter_qblock.png')

        standpainter = QtGui.QPainter(polterstand)
        blockpainter = QtGui.QPainter(polterblock)

        standpainter.drawPixmap(18, 18, ImageCache['GhostHouseStand'])
        blockpainter.drawPixmap(18, 18, ImageCache['Overrides'][9])

        del standpainter
        del blockpainter

        ImageCache['PolterStand'] = polterstand
        ImageCache['PolterQBlock'] = polterblock

    def updateSize(self):

        style = self.parent.spritedata[5] & 15
        if style == 0:
            self.yOffset = 0
            self.height = 16
            self.aux[0].setSize(60, 60)
            self.aux[0].image = ImageCache['PolterQBlock']
        else:
            self.yOffset = -16
            self.height = 32
            self.aux[0].setSize(60, 84)
            self.aux[0].image = ImageCache['PolterStand']

        self.aux[0].setPos(-18, -18)

        super().updateSize()


class SpriteImage_WaterPiranha(SLib.SpriteImage_Static): # 263
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['WaterPiranha'],
            (-5, -145),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WaterPiranha', 'water_piranha.png')


class SpriteImage_WalkingPiranha(SLib.SpriteImage_Static): # 264
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['WalkPiranha'],
            (-4, -50),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WalkPiranha', 'walk_piranha.png')


class SpriteImage_FallingIcicle(SLib.SpriteImage_StaticMultiple): # 265
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('IcicleSmall', 'icicle_small.png')
        SLib.loadIfNotInImageCache('IcicleLarge', 'icicle_large.png')

    def updateSize(self):
        super().updateSize()

        size = self.parent.spritedata[5] & 1
        if size == 0:
            self.image = ImageCache['IcicleSmall']
            self.height = 19
        else:
            self.image = ImageCache['IcicleLarge']
            self.height = 36


class SpriteImage_RotatingChainLink(SLib.SpriteImage_Static): # 266
    def __init__(self, parent):
        w, h = ImageCache['RotatingChainLink'].width(), ImageCache['RotatingChainLink'].height()
        super().__init__(
            parent,
            ImageCache['RotatingChainLink'],
            (
                -((w / 2) - 12) / 1.5,
                -((h / 2) - 12) / 1.5,
                ),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RotatingChainLink', 'rotating_chainlink.png')


class SpriteImage_TiltGrate(SLib.SpriteImage_StaticMultiple): # 267
    @staticmethod
    def loadImages():
        if 'TiltGrateU' in ImageCache: return
        ImageCache['TiltGrateU'] = SLib.GetImg('tilt_grate_up.png')
        ImageCache['TiltGrateD'] = SLib.GetImg('tilt_grate_down.png')
        ImageCache['TiltGrateL'] = SLib.GetImg('tilt_grate_left.png')
        ImageCache['TiltGrateR'] = SLib.GetImg('tilt_grate_right.png')

    def updateSize(self):
        direction = self.parent.spritedata[5] & 3
        if direction > 3: direction = 3

        if direction < 2:
            self.size = (69, 166)
        else:
            self.size = (166, 69)

        if direction == 0:
            self.offset = (-36, -115)
            self.image = ImageCache['TiltGrateU']
        elif direction == 1:
            self.offset = (-36, 12)
            self.image = ImageCache['TiltGrateD']
        elif direction == 2:
            self.offset = (-144, 0)
            self.image = ImageCache['TiltGrateL']
        elif direction == 3:
            self.offset = (-20, 0)
            self.image = ImageCache['TiltGrateR']

        super().updateSize()


class SpriteImage_LavaGeyser(SLib.SpriteImage_StaticMultiple): # 268
    def __init__(self, parent):
        super().__init__(parent)

        self.parent.setZValue(24999)
        self.dimensions = (-37, -186, 69, 200)

    @staticmethod
    def loadImages():
        if 'LavaGeyser0' in ImageCache: return
        for i in range(7):
            ImageCache['LavaGeyser%d' % i] = SLib.GetImg('lava_geyser_%d.png' % i)

    def updateSize(self):

        height = self.parent.spritedata[4] >> 4
        startsOn = self.parent.spritedata[5] & 1

        if height > 6: height = 0
        self.offset = (
            (-30, -170),
            (-28, -155),
            (-30, -155),
            (-43, -138),
            (-32, -105),
            (-26, -89),
            (-32, -34),
            )[height]

        self.parent.alpha = 0.75 if startsOn else 0.5

        self.image = ImageCache['LavaGeyser%d' % height]

        super().updateSize()


class SpriteImage_Parabomb(SLib.SpriteImage_Static): # 269
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Parabomb'],
            (-2, -16),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Parabomb', 'parabomb.png')


class SpriteImage_Mouser(SLib.SpriteImage): # 271
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Mouser', 'mouser.png')

    def updateSize(self):
        super().updateSize()

        number = self.parent.spritedata[5] >> 4
        direction = self.parent.spritedata[5] & 0xF

        self.width = (number + 1) * (ImageCache['Mouser'].width() / 1.5)

        if direction == 0: # Facing right
            self.xOffset = -self.width + 16
        else:
            self.xOffset = 0

    def paint(self, painter):
        super().paint(painter)

        direction = self.parent.spritedata[5] & 0xF

        mouser = ImageCache['Mouser']
        if direction == 1:
            mouser = QtGui.QImage(mouser)
            mouser = QtGui.QPixmap.fromImage(mouser.mirrored(True, False))

        painter.drawTiledPixmap(0, 0, self.width * 1.5, 24, mouser)


class SpriteImage_IceBro(SLib.SpriteImage_Static): # 272
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['IceBro'],
            (-5, -23),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('IceBro', 'icebro.png')


class SpriteImage_CastleGear(SLib.SpriteImage_StaticMultiple): # 274
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CastleGearL', 'castle_gear_large.png')
        SLib.loadIfNotInImageCache('CastleGearS', 'castle_gear_small.png')

    def updateSize(self):
        
        isBig = (self.parent.spritedata[4] & 0xF) == 1
        self.image = ImageCache['CastleGearL'] if isBig else ImageCache['CastleGearS']
        self.offset = (
            -(((self.image.width()  / 2) - 12) * (2 / 3)),
            -(((self.image.height() / 2) - 12) * (2 / 3)),
            )

        super().updateSize()


class SpriteImage_FiveEnemyRaft(SLib.SpriteImage_Static): # 275
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['FiveEnemyRaft'],
            (0, -8),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FiveEnemyRaft', '5_enemy_max_raft.png')


class SpriteImage_GhostDoor(SpriteImage_Door): # 276
    def __init__(self, parent):
        super().__init__(parent)
        self.doorName = 'GhostDoor'
        self.doorDimensions = (0, 0, 32, 48)


class SpriteImage_TowerDoor(SpriteImage_Door): # 277
    def __init__(self, parent):
        super().__init__(parent)
        self.doorName = 'TowerDoor'
        self.doorDimensions = (-2, -10.5, 53, 59)
        self.entranceOffset = (0, 64)


class SpriteImage_CastleDoor(SpriteImage_Door): # 278
    def __init__(self, parent):
        super().__init__(parent)
        self.doorName = 'CastleDoor'
        self.doorDimensions = (-2, -13, 53, 62)
        self.entranceOffset = (0, 68)


class SpriteImage_GiantIceBlock(SLib.SpriteImage_StaticMultiple): # 280
    @staticmethod
    def loadImages():
        if 'BigIceBlockEmpty' in ImageCache: return
        ImageCache['BigIceBlockEmpty'] = SLib.GetImg('big_ice_block_empty.png')
        ImageCache['BigIceBlockBobomb'] = SLib.GetImg('big_ice_block_bobomb.png')
        ImageCache['BigIceBlockSpikeBall'] = SLib.GetImg('big_ice_block_spikeball.png')

    def updateSize(self):

        item = self.parent.spritedata[5] & 3
        if item > 2: item = 0

        if item == 0:
            self.image = ImageCache['BigIceBlockEmpty']
        elif item == 1:
            self.image = ImageCache['BigIceBlockBobomb']
        elif item == 2:
            self.image = ImageCache['BigIceBlockSpikeBall']

        super().updateSize()


class SpriteImage_WoodCircle(SLib.SpriteImage_StaticMultiple): # 286
    @staticmethod
    def loadImages():
        if 'WoodCircle0' in ImageCache: return
        ImageCache['WoodCircle0'] = SLib.GetImg('wood_circle_0.png')
        ImageCache['WoodCircle1'] = SLib.GetImg('wood_circle_1.png')
        ImageCache['WoodCircle2'] = SLib.GetImg('wood_circle_2.png')

    def updateSize(self):
        super().updateSize()
        size = self.parent.spritedata[5] & 3

        self.image = ImageCache['WoodCircle%d' % size]

        if size > 2: size = 0
        self.dimensions = (
            (-24, -24, 64, 64),
            (-40, -40, 96, 96),
            (-56, -56, 128, 128),
            )[size]


class SpriteImage_PathIceBlock(SLib.SpriteImage_StaticMultiple): # 287
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False
        self.alpha = 0.8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PathIceBlock', 'unused_path_ice_block.png')

    def updateSize(self):

        width = (self.parent.spritedata[5] & 0xF) + 1
        height = (self.parent.spritedata[5] >> 4) + 1

        self.image = ImageCache['PathIceBlock'].scaled(width * 24, height * 24)

        super().updateSize()


class SpriteImage_OldBarrel(SLib.SpriteImage_Static): # 288
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['OldBarrel'],
            (1, -7),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('OldBarrel', 'old_barrel.png')


class SpriteImage_Box(SLib.SpriteImage_StaticMultiple): # 289
    @staticmethod
    def loadImages():
        if 'Box00' in ImageCache: return
        for style, stylestr in ((0, 'wood'), (1, 'metal')):
            for size, sizestr in zip(range(4), ('small', 'wide', 'tall', 'big')):
                ImageCache['Box%d%d' % (style, size)] = SLib.GetImg('box_%s_%s.png' % (stylestr, sizestr))

    def updateSize(self):

        style = self.parent.spritedata[4] & 1
        size = (self.parent.spritedata[5] >> 4) % 4

        self.image = ImageCache['Box%d%d' % (style, size)]

        super().updateSize()


class SpriteImage_Parabeetle(SLib.SpriteImage_StaticMultiple): # 291
    @staticmethod
    def loadImages():
        if 'Parabeetle0' in ImageCache: return
        ImageCache['Parabeetle0'] = SLib.GetImg('parabeetle_right.png')
        ImageCache['Parabeetle1'] = SLib.GetImg('parabeetle_left.png')
        ImageCache['Parabeetle2'] = SLib.GetImg('parabeetle_moreright.png')
        ImageCache['Parabeetle3'] = SLib.GetImg('parabeetle_atyou.png')

    def updateSize(self):

        direction = self.parent.spritedata[5] & 3
        self.image = ImageCache['Parabeetle%d' % direction]

        if direction == 0 or direction > 3: # right
            self.xOffset = -12
        elif direction == 1: # left
            self.xOffset = -10
        elif direction == 2: # more right
            self.xOffset = -12
        elif direction == 3: # at you
            self.xOffset = -26

        super().updateSize()


class SpriteImage_HeavyParabeetle(SLib.SpriteImage_StaticMultiple): # 292
    @staticmethod
    def loadImages():
        if 'HeavyParabeetle0' in ImageCache: return
        ImageCache['HeavyParabeetle0'] = SLib.GetImg('heavy_parabeetle_right.png')
        ImageCache['HeavyParabeetle1'] = SLib.GetImg('heavy_parabeetle_left.png')
        ImageCache['HeavyParabeetle2'] = SLib.GetImg('heavy_parabeetle_moreright.png')
        ImageCache['HeavyParabeetle3'] = SLib.GetImg('heavy_parabeetle_atyou.png')

    def updateSize(self):

        direction = self.parent.spritedata[5] & 3
        self.image = ImageCache['HeavyParabeetle%d' % direction]

        if direction == 0 or direction > 3: # right
            self.xOffset = -38
        elif direction == 1: # left
            self.xOffset = -38
        elif direction == 2: # more right
            self.xOffset = -38
        elif direction == 3: # at you
            self.xOffset = -52

        super().updateSize()


class SpriteImage_IceCube(SLib.SpriteImage_Static): # 294
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['IceCube'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('IceCube', 'ice_cube.png')


class SpriteImage_NutPlatform(SLib.SpriteImage_StaticMultiple): # 295
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('NutPlatform', 'nut_platform.png')

    def updateSize(self):
        offsetUp = self.parent.spritedata[5] >> 4
        offsetRight = self.parent.spritedata[5] & 15

        if offsetUp == 0:
            self.yOffset = -8
        else:
            self.yOffset = 0

        newOffsetRight = offsetRight % 8
        self.xOffset = (
            -16,
            -8,
            0,
            8,
            16,
            24,
            32,
            40,
            )[newOffsetRight]

        self.image = ImageCache['NutPlatform']

        super().updateSize()


class SpriteImage_MegaBuzzy(SLib.SpriteImage_StaticMultiple): # 296
    @staticmethod
    def loadImages():
        if 'MegaBuzzyL' in ImageCache: return
        ImageCache['MegaBuzzyL'] = SLib.GetImg('megabuzzy_left.png')
        ImageCache['MegaBuzzyF'] = SLib.GetImg('megabuzzy_front.png')
        ImageCache['MegaBuzzyR'] = SLib.GetImg('megabuzzy_right.png')

    def updateSize(self):

        dir = self.parent.spritedata[5] & 3
        if dir == 0 or dir > 2:
            self.image = ImageCache['MegaBuzzyR']
        elif dir == 1:
            self.image = ImageCache['MegaBuzzyL']
        elif dir == 2:
            self.image = ImageCache['MegaBuzzyF']

        super().updateSize()


class SpriteImage_DragonCoaster(SLib.SpriteImage): # 297
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'DragonHead' in ImageCache: return
        ImageCache['DragonHead'] = SLib.GetImg('dragon_coaster_head.png')
        ImageCache['DragonBody'] = SLib.GetImg('dragon_coaster_body.png')
        ImageCache['DragonTail'] = SLib.GetImg('dragon_coaster_tail.png')

    def updateSize(self):
        super().updateSize()

        raw_size = self.parent.spritedata[5] & 7

        if raw_size == 0 or raw_size == 8:
            self.width = 32
            self.xOffset = 0
        else:
            self.width = (raw_size * 32) + 32
            self.xOffset = -(self.width - 32)

    def paint(self, painter):
        super().paint(painter)

        raw_size = self.parent.spritedata[5] & 15

        if raw_size == 0 or raw_size == 8:
            # just the head
            painter.drawPixmap(0, 0, ImageCache['DragonHead'])
        elif raw_size == 1:
            # head and tail only
            painter.drawPixmap(48, 0, ImageCache['DragonHead'])
            painter.drawPixmap(0, 0, ImageCache['DragonTail'])
        else:
            painter.drawPixmap((self.width*1.5)-48, 0, ImageCache['DragonHead'])
            if raw_size > 1:
                painter.drawTiledPixmap(48, 0, (self.width*1.5)-96, 24, ImageCache['DragonBody'])
            painter.drawPixmap(0, 0, ImageCache['DragonTail'])


class SpriteImage_CannonMulti(SLib.SpriteImage_StaticMultiple): # 299
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = (-8, -11)

    @staticmethod
    def loadImages():
        if 'CannonMultiUR' in ImageCache: return
        ImageCache['CannonMultiUR'] = SLib.GetImg('cannon_multi_0.png')
        ImageCache['CannonMultiUL'] = SLib.GetImg('cannon_multi_1.png')
        ImageCache['CannonMultiDR'] = SLib.GetImg('cannon_multi_10.png')
        ImageCache['CannonMultiDL'] = SLib.GetImg('cannon_multi_11.png')

    def updateSize(self):

        number = self.parent.spritedata[5]
        direction = 'UR'

        if number == 0:
            direction = 'UR'
        elif number == 1:
            direction = 'UL'
        elif number == 10:
            direction = 'DR'
        elif number == 11:
            direction = 'DL'
        else:
            direction = 'UR'

        self.image = ImageCache['CannonMulti%s' % direction]

        super().updateSize()


class SpriteImage_RotCannon(SLib.SpriteImage_StaticMultiple): # 300
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RotCannon', 'rot_cannon.png')
        SLib.loadIfNotInImageCache('RotCannonU', 'rot_cannon_u.png')

    def updateSize(self):

        upsideDown = (self.parent.spritedata[5] >> 4) & 1
        if not upsideDown:
            self.image = ImageCache['RotCannon']
            self.offset = (-12, -29)
        else:
            self.image = ImageCache['RotCannonU']
            self.offset = (-12, 0)

        super().updateSize()


class SpriteImage_RotCannonPipe(SLib.SpriteImage_StaticMultiple): # 301
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RotCannonPipe', 'rot_cannon_pipe.png')
        SLib.loadIfNotInImageCache('RotCannonPipeU', 'rot_cannon_pipe_u.png')

    def updateSize(self):

        upsideDown = (self.parent.spritedata[5] >> 4) & 1
        if not upsideDown:
            self.image = ImageCache['RotCannonPipe']
            self.size = (-40, -74)
        else:
            self.image = ImageCache['RotCannonPipeU']
            self.size = (-40, 0)

        super().updateSize()


class SpriteImage_MontyMole(SLib.SpriteImage_StaticMultiple): # 303
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Mole', 'monty_mole.png')
        SLib.loadIfNotInImageCache('MoleCave', 'monty_mole_hole.png')

    def updateSize(self):

        notInCave = self.parent.spritedata[5] & 1
        if not notInCave: # wow, that looks weird
            self.image = ImageCache['Mole']
            self.offset = (3.5, 0)
        else:
            self.image = ImageCache['MoleCave']
            del self.offset

        super().updateSize()


class SpriteImage_RotFlameCannon(SLib.SpriteImage_StaticMultiple): # 304
    @staticmethod
    def loadImages():
        if 'RotFlameCannon0' in ImageCache: return
        for i in range(5):
            ImageCache['RotFlameCannon%d' % i] = SLib.GetImg('rotating_flame_cannon_%d.png' % i)
            originalImg = SLib.GetImg('rotating_flame_cannon_%d.png' % i, True)
            ImageCache['RotFlameCannonFlipped%d' % i] = QtGui.QPixmap.fromImage(originalImg.mirrored(False, True))

    def updateSize(self):

        orientation = self.parent.spritedata[5] >> 4
        length = self.parent.spritedata[5] & 15
        orientation = '' if orientation == 0 else 'Flipped'

        if length > 4: length = 0
        if not orientation:
            self.yOffset = -2
        else:
            self.yOffset = 0

        self.image = ImageCache['RotFlameCannon%s%d' % (orientation, length)]

        super().updateSize()


class SpriteImage_LightCircle(SLib.SpriteImage): # 305
    def __init__(self, parent):
        super().__init__(parent)

        self.aux.append(SLib.AuxiliaryImage(parent, 128, 128))
        self.aux[0].image = ImageCache['LightCircle']
        self.aux[0].setPos(-48, -48)
        self.aux[0].hover = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LightCircle', 'light_circle.png')


class SpriteImage_RotSpotlight(SLib.SpriteImage_StaticMultiple): # 306
    def __init__(self, parent):
        super().__init__(self)
        self.offset = (-24, -64)

    @staticmethod
    def loadImages():
        if 'RotSpotlight0' in ImageCache: return
        for i in range(16):
            ImageCache['RotSpotlight%d' % i] = SLib.GetImg('rotational_spotlight_%d.png' % i)

    def updateSize(self):

        angle = self.parent.spritedata[3] & 15
        self.image = ImageCache['RotSpotlight%d' % angle]

        super().updateSize()


class SpriteImage_HammerBroPlatform(SpriteImage_HammerBro): # 308
    pass


class SpriteImage_SynchroFlameJet(SLib.SpriteImage_StaticMultiple): # 309
    @staticmethod
    def loadImages():
        if 'SynchroFlameJetOnR' in ImageCache: return
        transform90 = QtGui.QTransform()
        transform270 = QtGui.QTransform()
        transform90.rotate(90)
        transform270.rotate(270)

        onImage = SLib.GetImg('synchro_flame_jet.png', True)
        offImage = SLib.GetImg('synchro_flame_jet_off.png', True)
        ImageCache['SynchroFlameJetOnR'] = QtGui.QPixmap.fromImage(onImage)
        ImageCache['SynchroFlameJetOnD'] = QtGui.QPixmap.fromImage(onImage.transformed(transform90))
        ImageCache['SynchroFlameJetOnL'] = QtGui.QPixmap.fromImage(onImage.mirrored(True, False))
        ImageCache['SynchroFlameJetOnU'] = QtGui.QPixmap.fromImage(onImage.transformed(transform270).mirrored(True, False))
        ImageCache['SynchroFlameJetOffR'] = QtGui.QPixmap.fromImage(offImage)
        ImageCache['SynchroFlameJetOffD'] = QtGui.QPixmap.fromImage(offImage.transformed(transform90))
        ImageCache['SynchroFlameJetOffL'] = QtGui.QPixmap.fromImage(offImage.mirrored(True, False))
        ImageCache['SynchroFlameJetOffU'] = QtGui.QPixmap.fromImage(offImage.transformed(transform270).mirrored(True, False))

    def updateSize(self):

        mode = (self.parent.spritedata[4] & 15) % 2
        direction = (self.parent.spritedata[5] & 15) % 4

        mode = 'Off' if mode else 'On'
        self.offset = (
            (0, 0),
            (-96, 0),
            (0, -96),
            (0, 0),
            )[direction]
        directionstr = 'RLUD'[direction]

        self.image = ImageCache['SynchroFlameJet%s%s' % (mode, directionstr)]

        super().updateSize()


class SpriteImage_ArrowSign(SLib.SpriteImage_StaticMultiple): # 310
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = (-8, -16)

    @staticmethod
    def loadImages():
        if 'ArrowSign0' in ImageCache: return
        for i in range(8):
            ImageCache['ArrowSign%d' % i] = SLib.GetImg('arrow_sign_%d.png' % i)

    def updateSize(self):

        direction = self.parent.spritedata[5] & 0xF
        self.image = ImageCache['ArrowSign%d' % direction]

        super().updateSize()


class SpriteImage_MegaIcicle(SLib.SpriteImage_Static): # 311
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MegaIcicle'],
            (-24, -3),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MegaIcicle', 'mega_icicle.png')


class SpriteImage_BubbleGen(SLib.SpriteImage): # 314
    def __init__(self, parent):
        super().__init__(parent)
        self.updateSceneAfterPaint = True

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BubbleGenEffect', 'bubble_gen.png')

    def updateSize(self):
        super().updateSize()
        self.parent.updateScene()

    def realViewZone(self, painter, zoneRect, viewRect):
        # Constants (change these if you want)
        bubbleFrequency = .01
        bubbleEccentricityX = 16
        bubbleEccentricityY = 48

        size = self.parent.spritedata[5] & 0xF
        if size > 3: return

        Image = ImageCache['BubbleGenEffect']

        if size == 0: pct = 50.0
        elif size == 1: pct = 60.0
        elif size == 2: pct = 80.0
        else: pct = 70.0
        Image = Image.scaledToWidth(int(Image.width() * pct / 100))

        distanceFromTop = (self.parent.objy * 1.5) - zoneRect.topLeft().y()
        random.seed(distanceFromTop + self.parent.objx) # looks ridiculous without this

        coords = []
        numOfBubbles = int(distanceFromTop * bubbleFrequency)
        for num in range(numOfBubbles):
            xmod = (random.random() * 2 * bubbleEccentricityX) - bubbleEccentricityX
            ymod = (random.random() * 2 * bubbleEccentricityY) - bubbleEccentricityY
            x = ((self.parent.objx * 1.5) - zoneRect.topLeft().x()) + xmod + 12 - (Image.width() / 2.0)
            y = ((num * 1.0 / numOfBubbles) * distanceFromTop) + ymod
            if not (0 < y < self.parent.objy * 1.5): continue
            coords.append([x, y])

        for x, y in coords:
            painter.drawPixmap(x, y, Image)


class SpriteImage_Bolt(SLib.SpriteImage_Static): # 315
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Bolt'],
            (2, 0),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Bolt', 'bolt.png')


class SpriteImage_BoltBox(SLib.SpriteImage): # 316
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'BoltBoxTL' in ImageCache: return
        ImageCache['BoltBoxTL'] = SLib.GetImg('boltbox_tl.png')
        ImageCache['BoltBoxT'] = SLib.GetImg('boltbox_t.png')
        ImageCache['BoltBoxTR'] = SLib.GetImg('boltbox_tr.png')
        ImageCache['BoltBoxL'] = SLib.GetImg('boltbox_l.png')
        ImageCache['BoltBoxM'] = SLib.GetImg('boltbox_m.png')
        ImageCache['BoltBoxR'] = SLib.GetImg('boltbox_r.png')
        ImageCache['BoltBoxBL'] = SLib.GetImg('boltbox_bl.png')
        ImageCache['BoltBoxB'] = SLib.GetImg('boltbox_b.png')
        ImageCache['BoltBoxBR'] = SLib.GetImg('boltbox_br.png')

    def updateSize(self):
        super().updateSize()

        size = self.parent.spritedata[5]
        self.width = (size & 0xF) * 16 + 32
        self.height = ((size & 0xF0) >> 4) * 16 + 32

    def paint(self, painter):
        super().paint(painter)

        xsize = self.width * 1.5
        ysize = self.height * 1.5

        painter.drawPixmap(0, 0, ImageCache['BoltBoxTL'])
        painter.drawTiledPixmap(24, 0, xsize - 48, 24, ImageCache['BoltBoxT'])
        painter.drawPixmap(xsize - 24, 0, ImageCache['BoltBoxTR'])

        painter.drawTiledPixmap(0, 24, 24, ysize-48, ImageCache['BoltBoxL'])
        painter.drawTiledPixmap(24, 24, xsize - 48, ysize - 48, ImageCache['BoltBoxM'])
        painter.drawTiledPixmap(xsize - 24, 24, 24, ysize - 48, ImageCache['BoltBoxR'])

        painter.drawPixmap(0, ysize - 24, ImageCache['BoltBoxBL'])
        painter.drawTiledPixmap(24, ysize - 24, xsize - 48, 24, ImageCache['BoltBoxB'])
        painter.drawPixmap(xsize - 24, ysize - 24, ImageCache['BoltBoxBR'])


class SpriteImage_BoxGenerator(SLib.SpriteImage_Static): # 318
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['BoxGenerator'],
            (0, -64),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoxGenerator', 'box_generator.png')


class SpriteImage_UnusedWiimoteDoor(SpriteImage_UnusedGiantDoor): # 319
    pass


class SpriteImage_UnusedSlidingWiimoteDoor(SpriteImage_UnusedGiantDoor): # 320
    pass


class SpriteImage_ArrowBlock(SLib.SpriteImage_StaticMultiple): # 321
    @staticmethod
    def loadImages():
        if 'ArrowBlock0' in ImageCache: return
        ImageCache['ArrowBlock0'] = SLib.GetImg('arrow_block_up.png')
        ImageCache['ArrowBlock1'] = SLib.GetImg('arrow_block_down.png')
        ImageCache['ArrowBlock2'] = SLib.GetImg('arrow_block_left.png')
        ImageCache['ArrowBlock3'] = SLib.GetImg('arrow_block_right.png')

    def updateSize(self):

        direction = (self.parent.spritedata[5] & 3) % 4
        self.image = ImageCache['ArrowBlock%d' % direction]

        super().updateSize()


class SpriteImage_BooCircle(SLib.SpriteImage): # 323
    def __init__(self, parent):
        super().__init__(parent)

        self.BooAuxImage = QtGui.QPixmap(1024, 1024)
        self.BooAuxImage.fill(Qt.transparent)
        self.aux.append(SLib.AuxiliaryImage(parent, 1024, 1024))
        self.aux[0].image = self.BooAuxImage
        offsetX = ImageCache['Boo1'].width() / 4
        offsetY = ImageCache['Boo1'].height() / 4
        self.aux[0].setPos(-512 + offsetX, -512 + offsetY)
        self.aux[0].hover = False

    @staticmethod
    def loadImages():
        if 'Boo2' in ImageCache: return
        ImageCache['Boo1'] = SLib.GetImg('boo1.png')
        ImageCache['Boo2'] = SLib.GetImg('boo2.png')
        ImageCache['Boo3'] = SLib.GetImg('boo3.png')
        ImageCache['Boo4'] = SLib.GetImg('boo4.png')

    def updateSize(self):
        # Constants (change these to fine-tune the boo positions)
        radiusMultiplier = 24 # pixels between boos per distance value
        radiusConstant = 24 # add to all radius values
        opacity = 0.5

        # Read the data
        outrad = self.parent.spritedata[2] & 15
        inrad = self.parent.spritedata[3] >> 4
        ghostnum = 1 + (self.parent.spritedata[3] & 15)
        differentRads = not (inrad == outrad)

        # Give up if the data is invalid
        if inrad > outrad:
            null = QtGui.QPixmap(2,2)
            null.fill(Qt.transparent)
            self.aux[0].image = null
            return

        # Create a pixmap
        pix = QtGui.QPixmap(1024, 1024)
        pix.fill(Qt.transparent)
        paint = QtGui.QPainter(pix)
        paint.setOpacity(opacity)

        # Paint each boo
        for i in range(ghostnum):
            # Find the angle at which to place the ghost from the center
            MissingGhostWeight = 0.75 - (1 / ghostnum) # approximate
            angle = math.radians(-360 * i / (ghostnum + MissingGhostWeight)) + 89.6

            # Since the origin of the boo img is in the top left, account for that
            offsetX = ImageCache['Boo1'].width() / 2
            offsetY = (ImageCache['Boo1'].height() / 2) + 16 # the circle is not centered

            # Pick a pixmap
            boo = ImageCache['Boo%d' % (1 if i == 0 else ((i - 1) % 3) + 2)] # 1  2 3 4  2 3 4  2 3 4 ...

            # Find the abs pos, and paint the ghost at its inner position
            x = math.sin(angle) * ((inrad * radiusMultiplier) + radiusConstant) - offsetX
            y = -(math.cos(angle) * ((inrad * radiusMultiplier) + radiusConstant)) - offsetY
            paint.drawPixmap(x + 512, y + 512, boo)

            # Paint it at its outer position if it has one
            if differentRads:
                x = math.sin(angle) * ((outrad * radiusMultiplier) + radiusConstant) - offsetX
                y = -(math.cos(angle) * ((outrad * radiusMultiplier) + radiusConstant)) - offsetY
                paint.drawPixmap(x + 512, y + 512, boo)

        # Finish it
        paint = None
        self.aux[0].image = pix


class SpriteImage_GhostHouseStand(SLib.SpriteImage_Static): # 325
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['GhostHouseStand'],
            (0, -16),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GhostHouseStand', 'ghost_house_stand.png')


class SpriteImage_KingBill(SLib.SpriteImage): # 326
    def __init__(self, parent):
        super().__init__(parent)

        self.aux.append(SLib.AuxiliaryPainterPath(parent, QtGui.QPainterPath(), 24, 24))
        self.aux[0].setSize(24 * 17, 24 * 17)

        self.paths = []
        for direction in range(4):

            # This has to be within the loop because the
            # following commands transpose them
            PointsRects = ( # These form a LEFT-FACING bullet
                QtCore.QPointF(192,         -180+180),
                QtCore.QRectF( 0,           -180+180, 384, 384),
                QtCore.QPointF(192+72,       204+180),
                QtCore.QPointF(192+72+6,     204-24+180),
                QtCore.QPointF(192+72+42,    204-24+180),
                QtCore.QPointF(192+72+48,    204+180),
                QtCore.QPointF(192+72+96,    204+180),
                QtCore.QPointF(192+72+96+6,  204-6+180),
                QtCore.QPointF(192+72+96+6, -180+6+180),
                QtCore.QPointF(192+72+96,   -180+180),
                QtCore.QPointF(192+72+48,   -180+180),
                QtCore.QPointF(192+72+42,   -180+24+180),
                QtCore.QPointF(192+72+6,    -180+24+180),
                QtCore.QPointF(192+72,      -180+180),
                )

            for thing in PointsRects: # translate each point to flip the image
                if direction == 0:   # faces left
                    arc = 'LR'
                elif direction == 1: # faces right
                    arc = 'LR'
                    if isinstance(thing, QtCore.QPointF):
                        thing.setX(408 - thing.x())
                    else:
                        thing.setRect(408 - thing.x(), thing.y(), -thing.width(), thing.height())
                elif direction == 2: # faces down
                    arc = 'UD'
                    if isinstance(thing, QtCore.QPointF):
                        x = thing.y()
                        y = 408 - thing.x()
                        thing.setX(x)
                        thing.setY(y)
                    else:
                        x = thing.y()
                        y = 408 - thing.x()
                        thing.setRect(x, y, thing.height(), -thing.width())
                else: # faces up
                    arc = 'UD'
                    if isinstance(thing, QtCore.QPointF):
                        x = thing.y()
                        y = thing.x()
                        thing.setX(x)
                        thing.setY(y)
                    else:
                        x = thing.y()
                        y = thing.x()
                        thing.setRect(x, y, thing.height(), thing.width())

            PainterPath = QtGui.QPainterPath()
            PainterPath.moveTo(PointsRects[0])
            if arc == 'LR': PainterPath.arcTo(PointsRects[1],  90,  180)
            else: PainterPath.arcTo(PointsRects[1], 180, -180)
            for point in PointsRects[2:]:
                PainterPath.lineTo(point)
            PainterPath.closeSubpath()
            self.paths.append(PainterPath)

    def updateSize(self):

        direction = (self.parent.spritedata[5] & 15) % 4

        self.aux[0].SetPath(self.paths[direction])

        newx, newy = (
            (0, (-8*24) + 12),
            ((-24*16), (-8*24) + 12),
            ((-24*10), (-24*16)),
            ((-24*5), 0),
            )[direction]
        self.aux[0].setPos(newx, newy)

        super().updateSize()


class SpriteImage_LinePlatformBolt(SLib.SpriteImage_Static): # 327
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['LinePlatformBolt'],
            (0, -16),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LinePlatformBolt', 'line_platform_with_bolt.png')


class SpriteImage_RopeLadder(SLib.SpriteImage_StaticMultiple): # 330
    @staticmethod
    def loadImages():
        if 'RopeLadder0' in ImageCache: return
        ImageCache['RopeLadder0'] = SLib.GetImg('ropeladder_0.png')
        ImageCache['RopeLadder1'] = SLib.GetImg('ropeladder_1.png')
        ImageCache['RopeLadder2'] = SLib.GetImg('ropeladder_2.png')

    def updateSize(self):

        size = self.parent.spritedata[5]
        if size > 2: size = 0

        self.image = ImageCache['RopeLadder%d' % size]

        super().updateSize()


class SpriteImage_DishPlatform(SLib.SpriteImage_StaticMultiple): # 331
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('DishPlatform0', 'dish_platform_short.png')
        SLib.loadIfNotInImageCache('DishPlatform1', 'dish_platform_long.png')

    def updateSize(self):

        size = self.parent.spritedata[4] & 15
        if size == 0:
            self.xOffset = -144
            self.width = 304
        else:
            self.xOffset = -208
            self.width = 433

        self.image = ImageCache['DishPlatform%d' % size]

        super().updateSize()


class SpriteImage_PlayerBlockPlatform(SLib.SpriteImage_Static): # 333
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PlayerBlockPlatform'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PlayerBlockPlatform', 'player_block_platform.png')


class SpriteImage_CheepGiant(SLib.SpriteImage): # 334
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryTrackObject(self.parent, 24, 24, SLib.AuxiliaryTrackObject.Horizontal))

    @staticmethod
    def loadImages():
        if 'CheepGiantRedLeft' in ImageCache: return
        ImageCache['CheepGiantRedLeft'] = SLib.GetImg('cheep_giant_red.png')
        ImageCache['CheepGiantRedAtYou'] = SLib.GetImg('cheep_giant_red_atyou.png')
        ImageCache['CheepGiantGreen'] = SLib.GetImg('cheep_giant_green.png')
        ImageCache['CheepGiantYellow'] = SLib.GetImg('cheep_giant_yellow.png')

    def updateSize(self):

        type = self.parent.spritedata[5] & 0xF
        if type in (1, 7):
            self.image = ImageCache['CheepGiantGreen']
        elif type == 8:
            self.image = ImageCache['CheepGiantYellow']
        elif type == 5:
            self.image = ImageCache['CheepGiantRedAtYou']
        else:
            self.image = ImageCache['CheepGiantRedLeft']
        self.size = (self.image.width() / 1.5, self.image.height() / 1.5)
        self.xOffset = 0 if type != 5 else -8

        if type == 3:
            distance = ((self.parent.spritedata[3] & 0xF) + 1) * 16
            self.aux[0].setSize((distance * 2) + 16, 16)
            self.aux[0].setPos(-distance * 1.5, 8)
        else:
            self.aux[0].setSize(0, 24)

        super().updateSize()

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(0, 0, self.image)


class SpriteImage_WendyKoopa(SLib.SpriteImage_Static): # 336
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['WendyKoopa'],
            (-23, -23),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WendyKoopa', 'Wendy_Koopa.png')


class SpriteImage_IggyKoopa(SLib.SpriteImage_Static): # 337
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['IggyKoopa'],
            (-17, -46),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('IggyKoopa', 'Iggy_Koopa.png')


class SpriteImage_Pipe_MovingUp(SpriteImage_Pipe): # 339
    def updateSize(self):
        self.length1 = (self.parent.spritedata[5] >> 4) + 2
        self.length2 = (self.parent.spritedata[5] & 0xF) + 2
        self.color = (
            'Green', 'Red', 'Yellow', 'Blue',
            )[(self.parent.spritedata[3] & 0xF) % 4]

        super().updateSize()


class SpriteImage_LemmyKoopa(SLib.SpriteImage_Static): # 340
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['LemmyKoopa'],
            (-16, -53),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LemmyKoopa', 'Lemmy_Koopa.png')


class SpriteImage_BigShell(SLib.SpriteImage_StaticMultiple): # 341
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigShell', 'bigshell.png')
        SLib.loadIfNotInImageCache('BigShellGrass', 'bigshell_grass.png')

    def updateSize(self):
        
        style = self.parent.spritedata[5] & 1
        if style == 0:
            self.image = ImageCache['BigShellGrass']
        else:
            self.image = ImageCache['BigShell']

        super().updateSize()


class SpriteImage_Muncher(SLib.SpriteImage_StaticMultiple): # 342
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Muncher', 'muncher.png')
        SLib.loadIfNotInImageCache('MuncherF', 'muncher_frozen.png')

    def updateSize(self):

        frozen = self.parent.spritedata[5] & 1
        if frozen == 1:
            self.image = ImageCache['MuncherF']
        else:
            self.image = ImageCache['Muncher']

        super().updateSize()


class SpriteImage_Fuzzy(SLib.SpriteImage_StaticMultiple): # 343
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Fuzzy', 'fuzzy.png')
        SLib.loadIfNotInImageCache('FuzzyGiant', 'fuzzy_giant.png')

    def updateSize(self):

        giant = self.parent.spritedata[4] & 1

        self.image = ImageCache['FuzzyGiant'] if giant else ImageCache['Fuzzy']
        self.offset = (-18, -18) if giant else (-7, -7)

        super().updateSize()


class SpriteImage_MortonKoopa(SLib.SpriteImage_Static): # 344
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MortonKoopa'],
            (-17, -34),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MortonKoopa', 'Morton_Koopa.png')


class SpriteImage_ChainHolder(SLib.SpriteImage_Static): # 345
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ChainHolder']
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ChainHolder', 'chain_holder.png')


class SpriteImage_HangingChainPlatform(SLib.SpriteImage_StaticMultiple): # 346
    @staticmethod
    def loadImages():
        if 'HangingChainPlatformS' in ImageCache: return
        ImageCache['HangingChainPlatformS'] = SLib.GetImg('hanging_chain_platform_small.png')
        ImageCache['HangingChainPlatformM'] = SLib.GetImg('hanging_chain_platform_medium.png')
        ImageCache['HangingChainPlatformL'] = SLib.GetImg('hanging_chain_platform_large.png')

    def updateSize(self):

        size = ((self.parent.spritedata[4] & 0xF) % 4) % 3
        size, self.xOffset = (
            ('S', -26),
            ('M', -42),
            ('L', -58),
            )[size]

        self.image = ImageCache['HangingChainPlatform%s' % size]

        super().updateSize()


class SpriteImage_RoyKoopa(SLib.SpriteImage_Static): # 347
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['RoyKoopa'],
            (-27, -24)
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RoyKoopa', 'Roy_Koopa.png')


class SpriteImage_LudwigVonKoopa(SLib.SpriteImage_Static): # 348
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['LudwigVonKoopa'],
            (-20, -30),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LudwigVonKoopa', 'Ludwig_Von_Koopa.png')


class SpriteImage_RockyWrench(SLib.SpriteImage_Static): # 352
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['RockyWrench'],
            (4, -41),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RockyWrench', 'rocky_wrench.png')


class SpriteImage_Pipe_MovingDown(SpriteImage_Pipe): # 353
    def __init__(self, parent):
        super().__init__(parent)
        self.direction = 'D'

    def updateSize(self):
        self.length1 = (self.parent.spritedata[5] >> 4) + 2
        self.length2 = (self.parent.spritedata[5] & 0xF) + 2
        self.color = (
            'Green', 'Red', 'Yellow', 'Blue',
            )[(self.parent.spritedata[3] & 0xF) % 4]

        super().updateSize()


class SpriteImage_RollingHillWith1Pipe(SpriteImage_RollingHillWithPipe): # 355
    pass


class SpriteImage_BrownBlock(SLib.SpriteImage): # 356
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryTrackObject(parent, 16, 16, SLib.AuxiliaryTrackObject.Horizontal))

    @staticmethod
    def loadImages():
        if 'BrownBlockTL' in ImageCache: return
        for vert in 'TMB':
            for horz in 'LMR':
                ImageCache['BrownBlock' + vert + horz] = \
                    SLib.GetImg('brown_block_%s%s.png' % (vert.lower(), horz.lower()))

    def updateSize(self):
        super().updateSize()

        size = self.parent.spritedata[5]
        height = size >> 4
        width = size & 0xF
        height = 1 if height == 0 else height
        width = 1 if width == 0 else width
        self.width = width * 16 + 16
        self.height = height * 16 + 16

        # now set up the track
        direction = self.parent.spritedata[2] & 3
        distance = (self.parent.spritedata[4] & 0xF0) >> 4

        if direction <= 1: # horizontal
            self.aux[0].direction = 1
            self.aux[0].setSize(self.width + (distance * 16), self.height)
        else: # vertical
            self.aux[0].direction = 2
            self.aux[0].setSize(self.width, self.height + (distance * 16))

        if (direction in (0, 3)) or (direction not in (1, 2)): # right, down
            self.aux[0].setPos(0,0)
        elif direction == 1: # left
            self.aux[0].setPos(-distance * 24,0)
        elif direction == 2: # up
            self.aux[0].setPos(0,-distance * 24)

    def paint(self, painter):
        super().paint(painter)

        blockX = 0
        blockY = 0

        width = self.width * 1.5
        height = self.height * 1.5

        column2x = blockX + 24
        column3x = blockX + width - 24
        row2y = blockY + 24
        row3y = blockY + height - 24

        painter.drawPixmap(blockX, blockY, ImageCache['BrownBlockTL'])
        painter.drawTiledPixmap(column2x, blockY, width - 48, 24, ImageCache['BrownBlockTM'])
        painter.drawPixmap(column3x, blockY, ImageCache['BrownBlockTR'])

        painter.drawTiledPixmap(blockX, row2y, 24, height - 48, ImageCache['BrownBlockML'])
        painter.drawTiledPixmap(column2x, row2y, width - 48, height - 48, ImageCache['BrownBlockMM'])
        painter.drawTiledPixmap(column3x, row2y, 24, height - 48, ImageCache['BrownBlockMR'])

        painter.drawPixmap(blockX, row3y, ImageCache['BrownBlockBL'])
        painter.drawTiledPixmap(column2x, row3y, width - 48, 24, ImageCache['BrownBlockBM'])
        painter.drawPixmap(column3x, row3y, ImageCache['BrownBlockBR'])


class SpriteImage_Fruit(SLib.SpriteImage_StaticMultiple): # 357
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Fruit', 'fruit.png')
        SLib.loadIfNotInImageCache('Cookie', 'cookie.png')

    def updateSize(self):

        style = self.parent.spritedata[5] & 1
        if style == 0:
            self.image = ImageCache['Fruit']
        else:
            self.image = ImageCache['Cookie']

        super().updateSize()


class SpriteImage_LavaParticles(SpriteImage_LiquidOrFog): # 358
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


class SpriteImage_WallLantern(SLib.SpriteImage): # 359
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryImage(parent, 128, 128))
        self.aux[0].image = ImageCache['WallLanternAux']
        self.aux[0].setPos(-48, -48)
        self.aux[0].hover = False

        self.image = ImageCache['WallLantern']
        self.yOffset = 8

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WallLantern', 'wall_lantern.png')
        SLib.loadIfNotInImageCache('WallLanternAux', 'wall_lantern_aux.png')

    def paint(self, painter):
        super().paint(painter)
        painter.drawPixmap(0, 0, self.image)


class SpriteImage_RollingHillWith8Pipes(SpriteImage_RollingHillWithPipe): # 360
    pass


class SpriteImage_CrystalBlock(SLib.SpriteImage_StaticMultiple): # 361
    @staticmethod
    def loadImages():
        if 'CrystalBlock0' in ImageCache: return
        for size in range(3):
            ImageCache['CrystalBlock%d' % size] = SLib.GetImg('crystal_block_%d.png' % size)

    def updateSize(self):

        size = (self.parent.spritedata[4] & 15) & 3
        self.image = ImageCache['CrystalBlock%d' % size]

        super().updateSize()


class SpriteImage_ColoredBox(SLib.SpriteImage): # 362
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'CBox0TL' in ImageCache: return
        for color in range(4):
            for direction in ('TL', 'T', 'TR', 'L', 'M', 'R', 'BL', 'B', 'BR'):
                ImageCache['CBox%d%s' % (color, direction)] = SLib.GetImg('cbox_%s_%d.png' % (direction, color))

    def updateSize(self):
        super().updateSize()
        self.color = (self.parent.spritedata[3] >> 4) & 3

        size = self.parent.spritedata[4]
        width = size >> 4
        height = size & 0xF

        self.width = (width + 3) * 16
        self.height = (height + 3) * 16

    def paint(self, painter):
        super().paint(painter)

        prefix = 'CBox%d' % self.color
        xsize = self.width * 1.5
        ysize = self.height * 1.5

        painter.drawPixmap(0, 0, ImageCache[prefix + 'TL'])
        painter.drawPixmap(xsize - 25, 0, ImageCache[prefix + 'TR'])
        painter.drawPixmap(0, ysize - 25, ImageCache[prefix + 'BL'])
        painter.drawPixmap(xsize - 25, ysize - 25, ImageCache[prefix + 'BR'])

        painter.drawTiledPixmap(25, 0, xsize - 50, 25, ImageCache[prefix + 'T'])
        painter.drawTiledPixmap(25, ysize - 25, xsize - 50, 25, ImageCache[prefix + 'B'])
        painter.drawTiledPixmap(0, 25, 25, ysize - 50, ImageCache[prefix + 'L'])
        painter.drawTiledPixmap(xsize - 25, 25, 25, ysize - 50, ImageCache[prefix + 'R'])

        painter.drawTiledPixmap(25, 25, xsize - 50, ysize - 50, ImageCache[prefix + 'M'])


class SpriteImage_CubeKinokoRot(SLib.SpriteImage_StaticMultiple): # 366
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CubeKinokoG', 'cube_kinoko_g.png')
        SLib.loadIfNotInImageCache('CubeKinokoR', 'cube_kinoko_r.png')

    def updateSize(self):

        style = self.parent.spritedata[4] & 1
        if style == 0:
            self.image = ImageCache['CubeKinokoR']
        else:
            self.image = ImageCache['CubeKinokoG']

        super().updateSize()


class SpriteImage_CubeKinokoLine(SLib.SpriteImage_Static): # 367
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['CubeKinokoP'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CubeKinokoP', 'cube_kinoko_p.png')


class SpriteImage_FlashRaft(SLib.SpriteImage_Static): # 368
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['FlashlightRaft'],
            (-16, -96),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FlashlightRaft', 'flashraft.png')

    def updateSize(self):
        midway = (self.parent.spritedata[5] >> 4) & 1
        self.alpha = 0.5 if midway else 1
        super().updateSize()


class SpriteImage_SlidingPenguin(SLib.SpriteImage_StaticMultiple): # 369
    @staticmethod
    def loadImages():
        if 'PenguinL' in ImageCache: return
        penguin = SLib.GetImg('sliding_penguin.png', True)
        ImageCache['PenguinL'] = QtGui.QPixmap.fromImage(penguin)
        ImageCache['PenguinR'] = QtGui.QPixmap.fromImage(penguin.mirrored(True, False))

    def updateSize(self):
        
        direction = self.parent.spritedata[5] & 1
        if direction == 0:
            self.image = ImageCache['PenguinL']
        else:
            self.image = ImageCache['PenguinR']

        super().updateSize()


class SpriteImage_CloudBlock(SLib.SpriteImage_Static): # 370
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['CloudBlock'],
            (-4, -8),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CloudBlock', 'cloud_block.png')


class SpriteImage_RollingHillCoin(SpriteImage_SpecialCoin): # 371
    pass


class SpriteImage_SnowWind(SpriteImage_LiquidOrFog): # 374
    def __init__(self, parent):
        super().__init__(parent)
        self.mid = ImageCache['SnowEffect']

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SnowEffect', 'snow.png')

    def realViewZone(self, painter, zoneRect, viewRect):

        # For now, we only paint snow
        self.paintZone = self.parent.spritedata[5] == 0

        super().realViewZone(painter, zoneRect, viewRect)


class SpriteImage_MovingChainLink(SLib.SpriteImage_StaticMultiple): # 376
    @staticmethod
    def loadImages():
        if 'MovingChainLink0' in ImageCache: return
        for shape in range(4):
            ImageCache['MovingChainLink%d' % shape] = SLib.GetImg('moving_chain_link_%d.png' % shape)

    def updateSize(self):
        
        self.shape = (self.parent.spritedata[4] >> 4) % 4
        arrow = None

        size = (
            (64, 64),
            (64, 128),
            (64, 224),
            (192, 64),
            )[self.shape]

        self.xOffset = -size[0] / 2
        self.yOffset = -size[1] / 2
        self.image = ImageCache['MovingChainLink%d' % self.shape]

        super().updateSize()


class SpriteImage_Pipe_Up(SpriteImage_PipeStationary): # 377
    def updateSize(self):
        self.length = (self.parent.spritedata[5] & 0xF) + 2
        super().updateSize()


class SpriteImage_Pipe_Down(SpriteImage_PipeStationary): # 378
    def __init__(self, parent):
        super().__init__(parent)
        self.direction = 'D'

    def updateSize(self):
        self.length = (self.parent.spritedata[5] & 0xF) + 2
        super().updateSize()


class SpriteImage_Pipe_Right(SpriteImage_PipeStationary): # 379
    def __init__(self, parent):
        super().__init__(parent)
        self.direction = 'R'

    def updateSize(self):
        self.length = (self.parent.spritedata[5] & 0xF) + 2
        super().updateSize()


class SpriteImage_Pipe_Left(SpriteImage_PipeStationary): # 380
    def __init__(self, parent):
        super().__init__(parent)
        self.direction = 'L'

    def updateSize(self):
        self.length = (self.parent.spritedata[5] & 0xF) + 2
        super().updateSize()


class SpriteImage_ScrewMushroomNoBolt(SpriteImage_ScrewMushroom): # 382
    def __init__(self, parent):
        super().__init__(parent)
        self.hasBolt = False


class SpriteImage_PipeCooliganGenerator(SLib.SpriteImage): # 384
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.size = (24, 48)
        self.spritebox.yOffset = -24


class SpriteImage_IceBlock(SLib.SpriteImage_StaticMultiple): # 385
    @staticmethod
    def loadImages():
        if 'IceBlock00' in ImageCache: return
        for i in range(4):
            for j in range(4):
                ImageCache['IceBlock%d%d' % (i, j)] = SLib.GetImg('iceblock%d%d.png' % (i, j))

    def updateSize(self):

        size = self.parent.spritedata[5]
        height = (size & 0x30) >> 4
        width = size & 3

        self.image = ImageCache['IceBlock%d%d' % (width, height)]
        self.xOffset = width * -4
        self.yOffset = height * -8
        
        super().updateSize()


class SpriteImage_PowBlock(SLib.SpriteImage_Static): # 386
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['POW']
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('POW', 'pow.png')


class SpriteImage_Bush(SLib.SpriteImage_StaticMultiple): # 387
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.setZValue(24999)

    @staticmethod
    def loadImages():
        if 'Bush00' in ImageCache: return
        for typenum, typestr in zip((0, 1), ('green', 'yellow')):
            for sizenum, sizestr in zip(range(4), ('small', 'med', 'large', 'xlarge')):
                ImageCache['Bush%d%d' % (typenum, sizenum)] = SLib.GetImg('bush_%s_%s.png' % (typestr, sizestr))

    def updateSize(self):

        props = self.parent.spritedata[5]
        style = (props >> 4) & 1
        size = (props & 3) % 4

        self.offset = (
            (-22, -25),
            (-29, -45),
            (-41, -61),
            (-52, -80),
            )[size]

        self.image = ImageCache['Bush%d%d' % (style, size)]

        super().updateSize()


class SpriteImage_Barrel(SLib.SpriteImage_Static): # 388
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Barrel'],
            (-4, -8),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Barrel', 'barrel.png')


class SpriteImage_StarCoinBoltControlled(SpriteImage_StarCoin): # 389
    pass


class SpriteImage_BoltControlledCoin(SpriteImage_SpecialCoin): # 390
    pass


class SpriteImage_GlowBlock(SLib.SpriteImage): # 391
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryImage(parent, 48, 48))
        self.aux[0].image = ImageCache['GlowBlock']
        self.aux[0].setPos(-12, -12)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GlowBlock', 'glow_block.png')


class SpriteImage_PropellerBlock(SLib.SpriteImage_Static): # 393
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PropellerBlock'],
            (-1, -6),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PropellerBlock', 'propeller_block.png')


class SpriteImage_LemmyBall(SLib.SpriteImage_Static): # 394
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['LemmyBall'],
            (-6, 0),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LemmyBall', 'lemmyball.png')


class SpriteImage_SpinyCheep(SLib.SpriteImage_Static): # 395
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SpinyCheep'],
            (-1, -2),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpinyCheep', 'cheep_spiny.png')


class SpriteImage_MoveWhenOn(SLib.SpriteImage): # 396
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'MoveWhenOnL' in ImageCache: return
        ImageCache['MoveWhenOnL'] = SLib.GetImg('mwo_left.png')
        ImageCache['MoveWhenOnM'] = SLib.GetImg('mwo_middle.png')
        ImageCache['MoveWhenOnR'] = SLib.GetImg('mwo_right.png')
        ImageCache['MoveWhenOnC'] = SLib.GetImg('mwo_circle.png')

        transform90 = QtGui.QTransform()
        transform180 = QtGui.QTransform()
        transform270 = QtGui.QTransform()
        transform90.rotate(90)
        transform180.rotate(180)
        transform270.rotate(270)

        for direction in ['R''L''U''D']:
            image = SLib.GetImg('sm_arrow.png', True)
            ImageCache['SmArrow'+'R'] = QtGui.QPixmap.fromImage(image)
            ImageCache['SmArrow'+'D'] = QtGui.QPixmap.fromImage(image.transformed(transform90))
            ImageCache['SmArrow'+'L'] = QtGui.QPixmap.fromImage(image.transformed(transform180))
            ImageCache['SmArrow'+'U'] = QtGui.QPixmap.fromImage(image.transformed(transform270))

    def updateSize(self):
        super().updateSize()

        # get width
        raw_size = self.parent.spritedata[5] & 0xF
        if raw_size == 0:
            self.xOffset = -16
            self.width = 32
        else:
            self.xOffset = 0
            self.width = raw_size * 16

        # set direction
        self.direction = (self.parent.spritedata[3] >> 4) % 5

    def paint(self, painter):
        super().paint(painter)

        if self.direction == 0:
            direction = 'R'
        elif self.direction == 1:
            direction = 'L'
        elif self.direction == 2:
            direction = 'U'
        elif self.direction == 3:
            direction = 'D'
        else:
            direction = None

        raw_size = self.parent.spritedata[5] & 0xF

        if raw_size == 0:
            # hack for the glitchy version
            painter.drawPixmap(0, 2, ImageCache['MoveWhenOnR'])
            painter.drawPixmap(24, 2, ImageCache['MoveWhenOnL'])
        elif raw_size == 1:
            painter.drawPixmap(0, 2, ImageCache['MoveWhenOnM'])
        else:
            painter.drawPixmap(0, 2, ImageCache['MoveWhenOnL'])
            if raw_size > 2:
                painter.drawTiledPixmap(24, 2, (raw_size-2)*24, 24, ImageCache['MoveWhenOnM'])
            painter.drawPixmap((self.width*1.5)-24, 2, ImageCache['MoveWhenOnR'])

        center = (self.width / 2) * 1.5
        painter.drawPixmap(center - 14, 0, ImageCache['MoveWhenOnC'])
        if direction is not None:
            painter.drawPixmap(center - 12, 1, ImageCache['SmArrow%s' % direction])


class SpriteImage_GhostHouseBox(SLib.SpriteImage): # 397
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'GHBoxTL' in ImageCache: return
        for direction in ('TL', 'T', 'TR', 'L', 'M', 'R', 'BL', 'B', 'BR'):
            ImageCache['GHBox%s' % direction] = SLib.GetImg('ghbox_%s.png' % direction)

    def updateSize(self):
        super().updateSize()

        height = self.parent.spritedata[4] >> 4
        width = self.parent.spritedata[5] & 15

        self.width = (width + 2) * 16
        self.height = (height + 2) * 16

    def paint(self, painter):
        super().paint(painter)

        prefix = 'GHBox'
        xsize = self.width * 1.5
        ysize = self.height * 1.5

        # Corners
        painter.drawPixmap(0, 0, ImageCache[prefix + 'TL'])
        painter.drawPixmap(xsize - 24, 0, ImageCache[prefix + 'TR'])
        painter.drawPixmap(0, ysize - 24, ImageCache[prefix + 'BL'])
        painter.drawPixmap(xsize - 24, ysize - 24, ImageCache[prefix + 'BR'])

        # Edges
        painter.drawTiledPixmap(24, 0, xsize - 48, 24, ImageCache[prefix + 'T'])
        painter.drawTiledPixmap(24, ysize - 24, xsize - 48, 24, ImageCache[prefix + 'B'])
        painter.drawTiledPixmap(0, 24, 24, ysize - 48, ImageCache[prefix + 'L'])
        painter.drawTiledPixmap(xsize - 24, 24, 24, ysize - 48, ImageCache[prefix + 'R'])

        # Middle
        painter.drawTiledPixmap(24, 24, xsize - 48, ysize - 48, ImageCache[prefix + 'M'])


class SpriteImage_LineQBlock(SpriteImage_Block): # 402
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 49
        self.twelveIsMushroom = True


class SpriteImage_LineBrickBlock(SpriteImage_Block): # 403
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 48


class SpriteImage_ToadHouseBalloonUnused(SpriteImage_ToadHouseBalloon): # 411
    def updateSize(self):

        self.livesNum = (self.parent.spritedata[4] >> 4) % 4

        super().updateSize()

        self.yOffset = 8 - (self.image.height() / 3)


class SpriteImage_ToadHouseBalloonUsed(SpriteImage_ToadHouseBalloon): # 412
    def updateSize(self):

        self.livesNum = (self.parent.spritedata[4] >> 4) % 4
        self.hasHandle = not ((self.parent.spritedata[5] >> 4) & 1)

        super().updateSize()

        if self.hasHandle:
            self.yOffset = 12
        else:
            self.yOffset = 16 - (self.image.height() / 3)


class SpriteImage_WendyRing(SLib.SpriteImage_Static): # 413
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['WendyRing'],
            (-4, 4),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('WendyRing', 'wendy_ring.png')


class SpriteImage_Gabon(SLib.SpriteImage_StaticMultiple): # 414
    @staticmethod
    def loadImages():
        if 'GabonLeft' in ImageCache: return
        ImageCache['GabonLeft'] = SLib.GetImg('gabon_l.png')
        ImageCache['GabonRight'] = SLib.GetImg('gabon_r.png')
        ImageCache['GabonDown'] = SLib.GetImg('gabon_d.png')

    def updateSize(self):

        throwdir = self.parent.spritedata[5] & 1
        if throwdir == 0: # down
            self.image = ImageCache['GabonDown']
            self.offset = (-5, -29)
        else: # left/right

            facing = self.parent.spritedata[4] & 1
            self.image = (
                ImageCache['GabonLeft'],
                ImageCache['GabonRight'],
                )[facing]
            self.offset = (-7, -31)

        super().updateSize()


class SpriteImage_BetaLarryKoopa(SLib.SpriteImage_Static): # 415
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['LarryKoopaBeta'],
            (-13, -22.5),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LarryKoopaBeta', 'Larry_Koopa_Unused.png')


class SpriteImage_InvisibleOneUp(SLib.SpriteImage_Static): # 416
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['InvisibleOneUp'],
            (3, 5),
            ) 
        self.alpha = 0.65

    @staticmethod
    def loadImages():
        if 'InvisibleOneUp' in ImageCache: return
        ImageCache['InvisibleOneUp'] = ImageCache['Blocks'][11].scaled(16, 16)


class SpriteImage_SpinjumpCoin(SLib.SpriteImage_Static): # 417
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SpecialCoin'],
            )
        self.alpha = 0.55


class SpriteImage_Bowser(SLib.SpriteImage_Static): # 419
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Bowser'],
            (-43, -70),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Bowser', 'Bowser.png')


class SpriteImage_GiantGlowBlock(SLib.SpriteImage): # 420
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryImage(parent, 100, 100))
        self.size = (32, 32)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GiantGlowBlockOn', 'giant_glow_block.png')
        SLib.loadIfNotInImageCache('GiantGlowBlockOff', 'giant_glow_block_off.png')

    def updateSize(self):
        super().updateSize()

        type = self.parent.spritedata[4] >> 4
        if type == 0:
            self.aux[0].image = ImageCache['GiantGlowBlockOn']
            self.aux[0].setSize(100, 100, -25, -30)
        else:
            self.aux[0].image = ImageCache['GiantGlowBlockOff']
            self.aux[0].setSize(48, 48)


class SpriteImage_UnusedGhostDoor(SLib.SpriteImage_Static): # 421
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['GhostDoorU'],
            )
    
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GhostDoorU', 'ghost_door.png')


class SpriteImage_ToadQBlock(SpriteImage_Block): # 422
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 49
        self.contentsOverride = 16


class SpriteImage_ToadBrickBlock(SpriteImage_Block): # 423
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 48
        self.contentsOverride = 16


class SpriteImage_PalmTree(SLib.SpriteImage_StaticMultiple): # 424
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.setZValue(24999)

    @staticmethod
    def loadImages():
        if 'PalmTree0' in ImageCache: return
        for i in range(8):
            ImageCache['PalmTree%d' % i] = SLib.GetImg('palmtree_%d.png' % i)

    def updateSize(self):

        size = self.parent.spritedata[5] & 7
        self.image = ImageCache['PalmTree%d' % size]
        self.yOffset = 16 - (self.image.height() / 1.5)

        super().updateSize()


class SpriteImage_Jellybeam(SLib.SpriteImage_Static): # 425
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Jellybeam'],
            (-6, 0),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Jellybeam', 'jellybeam.png')


class SpriteImage_Kamek(SLib.SpriteImage_Static): # 427
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Kamek'],
            (-10, -26),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Kamek', 'Kamek.png')


class SpriteImage_MGPanel(SLib.SpriteImage_Static): # 428
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MGPanel'],
            (0, -4),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MGPanel', 'minigame_flip_panel.png')


class SpriteImage_Toad(SLib.SpriteImage_Static): # 432
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Toad'],
            (-1, -16),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Toad', 'toad.png')


class SpriteImage_FloatingQBlock(SLib.SpriteImage_Static): # 433
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['FloatingQBlock'],
            (-6, -6),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FloatingQBlock', 'floating_qblock.png')


class SpriteImage_WarpCannon(SLib.SpriteImage_StaticMultiple): # 434
    @staticmethod
    def loadImages():
        if 'Warp0' in ImageCache: return
        ImageCache['Warp0'] = SLib.GetImg('warp_w5.png')
        ImageCache['Warp1'] = SLib.GetImg('warp_w6.png')
        ImageCache['Warp2'] = SLib.GetImg('warp_w8.png')

    def updateSize(self):

        dest = self.parent.spritedata[5] & 3
        if dest == 3: dest = 0
        self.image = ImageCache['Warp%d' % dest]

        super().updateSize()


class SpriteImage_GhostFog(SpriteImage_LiquidOrFog): # 435
    def __init__(self, parent):
        super().__init__(parent)

        self.mid = ImageCache['GhostFog']

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GhostFog', 'fog_ghost.png')

    def realViewZone(self, painter, zoneRect, viewRect):

        self.paintZone = self.parent.spritedata[5] == 0
        self.top = self.parent.objy

        super().realViewZone(painter, zoneRect, viewRect)


class SpriteImage_PurplePole(SLib.SpriteImage): # 437
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'VertPole' in ImageCache: return
        ImageCache['VertPoleTop'] = SLib.GetImg('purple_pole_top.png')
        ImageCache['VertPole'] = SLib.GetImg('purple_pole_middle.png')
        ImageCache['VertPoleBottom'] = SLib.GetImg('purple_pole_bottom.png')

    def updateSize(self):
        super().updateSize()

        length = self.parent.spritedata[5]
        self.height = (length + 3) * 16

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['VertPoleTop'])
        painter.drawTiledPixmap(0, 24, 24, self.height * 1.5 - 48, ImageCache['VertPole'])
        painter.drawPixmap(0, self.height * 1.5 - 24, ImageCache['VertPoleBottom'])


class SpriteImage_CageBlocks(SLib.SpriteImage_StaticMultiple): # 438
    @staticmethod
    def loadImages():
        if 'CageBlock0' in ImageCache: return
        for type in range(8):
            ImageCache['CageBlock%d' % type] = SLib.GetImg('cage_block_%d.png' % type)

    def updateSize(self):

        type = (self.parent.spritedata[4] & 15) % 5

        self.offset = (
            (-112, -112),
            (-112, -112),
            (-97, -81),
            (-80, -96),
            (-112, -112),
            )[type]

        self.image = ImageCache['CageBlock%d' % type]

        super().updateSize()


class SpriteImage_CagePeachFake(SLib.SpriteImage_Static): # 439
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['CagePeachFake'],
            (-18, -106),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CagePeachFake', 'cage_peach_fake.png')


class SpriteImage_HorizontalRope(SLib.SpriteImage): # 440
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('HorzRope', 'horizontal_rope_middle.png')
        SLib.loadIfNotInImageCache('HorzRopeEnd', 'horizontal_rope_end.png')

    def updateSize(self):
        super().updateSize()

        length = self.parent.spritedata[5]
        self.width = (length + 3) * 16

    def paint(self, painter):
        super().paint(painter)

        endpiece = ImageCache['HorzRopeEnd']
        painter.drawPixmap(0, 0, endpiece)
        painter.drawTiledPixmap(24, 0, self.width * 1.5 - 48, 24, ImageCache['HorzRope'])
        painter.drawPixmap(self.width * 1.5 - 24, 0, endpiece)


class SpriteImage_MushroomPlatform(SLib.SpriteImage): # 441
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

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

    def updateSize(self):
        super().updateSize()

        # get size/color
        self.color = self.parent.spritedata[4] & 1
        self.shroomsize = (self.parent.spritedata[5] >> 4) & 1
        self.height = 16 * (self.shroomsize + 1)

        # get width
        width = self.parent.spritedata[5] & 0xF
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

        tilesize = 24 + (self.shroomsize * 24)
        if self.shroomsize == 0:
            if self.color == 0:
                color = 'Orange'
            else:
                color = 'Blue'
        else:
            if self.color == 0:
                color = 'Red'
            else:
                color = 'Green'

        painter.drawPixmap(0, 0, ImageCache[color + 'ShroomL'])
        painter.drawTiledPixmap(tilesize, 0, (self.width * 1.5) - (tilesize * 2), tilesize, ImageCache[color + 'ShroomM'])
        painter.drawPixmap((self.width * 1.5) - tilesize, 0, ImageCache[color + 'ShroomR'])


class SpriteImage_ReplayBlock(SLib.SpriteImage_Static): # 443
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ReplayBlock'],
            (-8, -16),
            )

        @staticmethod
        def loadImages():
            SLib.loadIfNotInImageCache('ReplayBlock', 'replay_block.png')


class SpriteImage_PreSwingingVine(SLib.SpriteImage_Static): # 444
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SwingVine'],
            )

        @staticmethod
        def loadImages():
            SLib.loadIfNotInImageCache('SwingVine', 'swing_vine.png')


class SpriteImage_CagePeachReal(SLib.SpriteImage_Static): # 445
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['CagePeachReal'],
            (-18, -106),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CagePeachReal', 'cage_peach_real.png')


class SpriteImage_UnderwaterLamp(SLib.SpriteImage): # 447
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

        self.aux.append(SLib.AuxiliaryImage(parent, 105, 105))
        self.aux[0].image = ImageCache['UnderwaterLamp']
        self.aux[0].setPos(-34, -34)

        self.dimensions = (-4, -4, 24, 26)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('UnderwaterLamp', 'underwater_lamp.png')


class SpriteImage_MetalBar(SLib.SpriteImage_Static): # 448
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MetalBar'],
            (0, -32),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MetalBar', 'metal_bar.png')


class SpriteImage_Pipe_EnterableUp(SpriteImage_PipeStationary): # 450
    def updateSize(self):
        self.length = (self.parent.spritedata[5] & 0xF) + 2
        super().updateSize()


class SpriteImage_MouserDespawner(SLib.SpriteImage_Static): # 451
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MouserDespawner'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MouserDespawner', 'mouser_despawner.png')


class SpriteImage_BowserDoor(SpriteImage_Door): # 452
    def __init__(self, parent):
        super().__init__(parent)
        self.doorName = 'BowserDoor'
        self.doorDimensions = (-53, -134, 156, 183)
        self.entranceOffset = (104, 250)


class SpriteImage_Seaweed(SLib.SpriteImage_StaticMultiple): # 453
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.setZValue(24998)

    @staticmethod
    def loadImages():
        if 'Seaweed0' in ImageCache: return
        for i in range(4):
            ImageCache['Seaweed%d' % i] = SLib.GetImg('seaweed_%d.png' % i)

    def updateSize(self):
        SeaweedSizes = [0, 1, 2, 2, 3]
        SeaweedXOffsets = [-26, -22, -31, -42]

        style = (self.parent.spritedata[5] & 0xF) % 6
        size = SeaweedSizes[style]

        self.image = ImageCache['Seaweed%d' % size]
        self.offset = (
            SeaweedXOffsets[size],
            17 - (self.image.height() / 1.5),
            )

        super().updateSize()


class SpriteImage_HammerPlatform(SLib.SpriteImage_Static): # 455
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['HammerPlatform'],
            (-24, -8),
            )
        self.parent.setZValue(24999)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('HammerPlatform', 'hammer_platform.png')


class SpriteImage_BossBridge(SLib.SpriteImage_StaticMultiple): # 456
    @staticmethod
    def loadImages():
        if 'BossBridgeL' in ImageCache: return
        ImageCache['BossBridgeL'] = SLib.GetImg('boss_bridge_left.png')
        ImageCache['BossBridgeM'] = SLib.GetImg('boss_bridge_middle.png')
        ImageCache['BossBridgeR'] = SLib.GetImg('boss_bridge_right.png')

    def updateSize(self):

        style = (self.parent.spritedata[5] & 3) % 3
        self.image = (
            ImageCache['BossBridgeM'],
            ImageCache['BossBridgeR'],
            ImageCache['BossBridgeL'],
            )[style]

        super().updateSize()


class SpriteImage_SpinningThinBars(SLib.SpriteImage_Static): # 457
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SpinningThinBars'],
            (-114, -112),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SpinningThinBars', 'spinning_thin_bars.png')


class SpriteImage_SwingingVine(SLib.SpriteImage_StaticMultiple): # 464
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SwingVine', 'swing_vine.png')
        SLib.loadIfNotInImageCache('SwingChain', 'swing_chain.png')

    def updateSize(self):

        style = self.parent.spritedata[5] & 1
        self.image = ImageCache['SwingVine'] if not style else ImageCache['SwingChain']

        super().updateSize()


class SpriteImage_LavaIronBlock(SLib.SpriteImage_Static): # 466
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['LavaIronBlock'],
            (-2, -1),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('LavaIronBlock', 'lava_iron_block.png')


class SpriteImage_MovingGemBlock(SLib.SpriteImage_Static): # 467
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MovingGemBlock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('MovingGemBlock', 'moving_gem_block.png')


class SpriteImage_BoltPlatform(SLib.SpriteImage): # 469
    def __init__(self, parent):
        super().__init__(parent)
        self.spritebox.shown = False

    @staticmethod
    def loadImages():
        if 'BoltPlatformL' in ImageCache: return
        ImageCache['BoltPlatformL'] = SLib.GetImg('bolt_platform_left.png')
        ImageCache['BoltPlatformM'] = SLib.GetImg('bolt_platform_middle.png')
        ImageCache['BoltPlatformR'] = SLib.GetImg('bolt_platform_right.png')

    def updateSize(self):
        super().updateSize()

        length = self.parent.spritedata[5] & 0xF
        self.width = (length + 2) * 16

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['BoltPlatformL'])
        painter.drawTiledPixmap(24, 3, self.width * 1.5 - 48, 24, ImageCache['BoltPlatformM'])
        painter.drawPixmap(self.width * 1.5 - 24, 0, ImageCache['BoltPlatformR'])


class SpriteImage_BoltPlatformWire(SLib.SpriteImage_Static): # 470
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['BoltPlatformWire'],
            (5, -240),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BoltPlatformWire', 'bolt_platform_wire.png')


class SpriteImage_PotPlatform(SLib.SpriteImage_Static): # 471
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PotPlatform'],
            (-12, -2),
            )

    @staticmethod
    def loadImages():
        if 'PotPlatform' in ImageCache: return
        top = SLib.GetImg('pot_platform_top.png')
        mid = SLib.GetImg('pot_platform_middle.png')
        full = QtGui.QPixmap(77, 722)

        full.fill(Qt.transparent)
        painter = QtGui.QPainter(full)
        painter.drawPixmap(0, 0, top)
        painter.drawTiledPixmap(12, 143, 52, 579, mid)
        del painter

        ImageCache['PotPlatform'] = full


class SpriteImage_IceFloe(SLib.SpriteImage_StaticMultiple): # 475
    def __init__(self, parent):
        super().__init__(parent)
        self.alpha = 0.65

    @staticmethod
    def loadImages():
        if 'IceFloe0' in ImageCache: return
        for size in range(16):
            ImageCache['IceFloe%d' % size] = SLib.GetImg('ice_floe_%d.png' % size)

    def updateSize(self):

        size = self.parent.spritedata[5] & 15
        self.offset = (
            (-1, -32), # 0: 3x3
            (-2, -48), # 1: 4x4
            (-2, -64), # 2: 5x5
            (-2, -32), # 3: 4x3
            (-2, -48), # 4: 5x4
            (-3, -80), # 5: 7x6
            (-3, -160), # 6: 16x11
            (-3, -112), # 7: 11x8
            (-1, -48), # 8: 2x4
            (-2, -48), # 9: 3x4
            (-2.5, -96), # 10: 6x7
            (-1, -64), # 11: 2x5
            (-1, -64), # 12: 3x5
            )[size]

        self.image = ImageCache['IceFloe%d' % size]

        super().updateSize()


class SpriteImage_FlyingWrench(SLib.SpriteImage_Static): # 476
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Wrench'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Wrench', 'wrench.png')


class SpriteImage_SuperGuideBlock(SLib.SpriteImage_Static): # 477
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SuperGuide'],
            (-4, -4),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SuperGuide', 'superguide_block.png')


class SpriteImage_BowserSwitchSm(SLib.SpriteImage_StaticMultiple): # 478
    @staticmethod
    def loadImages():
        if 'ESwitch' in ImageCache: return
        e = SLib.GetImg('e_switch.png', True)
        ImageCache['ESwitch'] = QtGui.QPixmap.fromImage(e)
        ImageCache['ESwitchU'] = QtGui.QPixmap.fromImage(e.mirrored(True, True))

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1
        if not upsideDown:
            self.image = ImageCache['ESwitch']
        else:
            self.image = ImageCache['ESwitchU']

        super().updateSize()


class SpriteImage_BowserSwitchLg(SLib.SpriteImage_StaticMultiple): # 479
    @staticmethod
    def loadImages():
        if 'ELSwitch' in ImageCache: return
        elg = SLib.GetImg('e_switch_lg.png', True)
        ImageCache['ELSwitch'] = QtGui.QPixmap.fromImage(elg)
        ImageCache['ELSwitchU'] = QtGui.QPixmap.fromImage(elg.mirrored(True, True))

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1
        if not upsideDown:
            self.image = ImageCache['ELSwitch']
            self.offset = (-16, -26)
        else:
            self.image = ImageCache['ELSwitchU']
            self.offset = (-16, 0)

        super().updateSize()


################################################################
################################################################
################################################################
################################################################


ImageClasses = {
        9: SpriteImage_CharacterSpawner,
        20: SpriteImage_Goomba,
        21: SpriteImage_Paragoomba,
        23: SpriteImage_HorzMovingPlatform,
        24: SpriteImage_BuzzyBeetle,
        25: SpriteImage_Spiny,
        26: SpriteImage_UpsideDownSpiny,
        27: SpriteImage_DSStoneBlock_Vert,
        28: SpriteImage_DSStoneBlock_Horz,
        30: SpriteImage_OldStoneBlock_NoSpikes,
        31: SpriteImage_VertMovingPlatform,
        32: SpriteImage_StarCoinRegular,
        40: SpriteImage_QuestionSwitch,
        41: SpriteImage_PSwitch,
        42: SpriteImage_ExcSwitch,
        43: SpriteImage_QuestionSwitchBlock,
        44: SpriteImage_PSwitchBlock,
        45: SpriteImage_ExcSwitchBlock,
        46: SpriteImage_Podoboo,
        47: SpriteImage_Thwomp,
        48: SpriteImage_GiantThwomp,
        49: SpriteImage_UnusedSeesaw,
        50: SpriteImage_FallingPlatform,
        51: SpriteImage_TiltingGirder,
        52: SpriteImage_UnusedRotPlatforms,
        54: SpriteImage_Lakitu,
        55: SpriteImage_UnusedRisingSeesaw,
        56: SpriteImage_RisingTiltGirder,
        57: SpriteImage_KoopaTroopa,
        58: SpriteImage_KoopaParatroopa,
        59: SpriteImage_LineTiltGirder,
        60: SpriteImage_SpikeTop,
        61: SpriteImage_BigBoo,
        63: SpriteImage_SpikeBall,
        64: SpriteImage_OutdoorsFog,
        65: SpriteImage_PipePiranhaUp,
        66: SpriteImage_PipePiranhaDown,
        67: SpriteImage_PipePiranhaRight,
        68: SpriteImage_PipePiranhaLeft,
        69: SpriteImage_PipeFiretrapUp,
        70: SpriteImage_PipeFiretrapDown,
        71: SpriteImage_PipeFiretrapRight,
        72: SpriteImage_PipeFiretrapLeft,
        73: SpriteImage_GroundPiranha,
        74: SpriteImage_BigGroundPiranha,
        75: SpriteImage_GroundFiretrap,
        76: SpriteImage_BigGroundFiretrap,
        77: SpriteImage_ShipKey,
        78: SpriteImage_CloudTrampoline,
        80: SpriteImage_FireBro,
        81: SpriteImage_OldStoneBlock_SpikesLeft,
        82: SpriteImage_OldStoneBlock_SpikesRight,
        83: SpriteImage_OldStoneBlock_SpikesLeftRight,
        84: SpriteImage_OldStoneBlock_SpikesTop,
        85: SpriteImage_OldStoneBlock_SpikesBottom,
        86: SpriteImage_OldStoneBlock_SpikesTopBottom,
        87: SpriteImage_TrampolineWall,
        92: SpriteImage_BulletBillLauncher,
        93: SpriteImage_BanzaiBillLauncher,
        94: SpriteImage_BoomerangBro,
        95: SpriteImage_HammerBroNormal,
        96: SpriteImage_RotationControllerSwaying,
        97: SpriteImage_RotationControlledSolidBetaPlatform,
        98: SpriteImage_GiantSpikeBall,
        99: SpriteImage_PipeEnemyGenerator,
        100: SpriteImage_Swooper,
        101: SpriteImage_Bobomb,
        102: SpriteImage_Broozer,
        103: SpriteImage_PlatformGenerator,
        104: SpriteImage_AmpNormal,
        105: SpriteImage_Pokey,
        106: SpriteImage_LinePlatform,
        107: SpriteImage_RotationControlledPassBetaPlatform,
        108: SpriteImage_AmpLine,
        109: SpriteImage_ChainBall,
        110: SpriteImage_Sunlight,
        111: SpriteImage_Blooper,
        112: SpriteImage_BlooperBabies,
        113: SpriteImage_Flagpole,
        114: SpriteImage_FlameCannon,
        115: SpriteImage_Cheep,
        116: SpriteImage_CoinCheep,
        117: SpriteImage_PulseFlameCannon,
        118: SpriteImage_DryBones,
        119: SpriteImage_GiantDryBones,
        120: SpriteImage_SledgeBro,
        122: SpriteImage_OneWayPlatform,
        123: SpriteImage_UnusedCastlePlatform,
        125: SpriteImage_FenceKoopaHorz,
        126: SpriteImage_FenceKoopaVert,
        127: SpriteImage_FlipFence,
        128: SpriteImage_FlipFenceLong,
        129: SpriteImage_4Spinner,
        130: SpriteImage_Wiggler,
        131: SpriteImage_Boo,
        132: SpriteImage_UnusedBlockPlatform1,
        133: SpriteImage_StalagmitePlatform,
        134: SpriteImage_Crow,
        135: SpriteImage_HangingPlatform,
        136: SpriteImage_RotBulletLauncher,
        137: SpriteImage_SpikedStakeDown,
        138: SpriteImage_Water,
        139: SpriteImage_Lava,
        140: SpriteImage_SpikedStakeUp,
        141: SpriteImage_SpikedStakeRight,
        142: SpriteImage_SpikedStakeLeft,
        143: SpriteImage_Arrow,
        144: SpriteImage_RedCoin,
        145: SpriteImage_FloatingBarrel,
        146: SpriteImage_ChainChomp,
        147: SpriteImage_Coin,
        148: SpriteImage_Spring,
        149: SpriteImage_RotationControllerSpinning,
        151: SpriteImage_Porcupuffer,
        153: SpriteImage_QuestionSwitchUnused,
        155: SpriteImage_StarCoinLineControlled,
        156: SpriteImage_RedCoinRing,
        157: SpriteImage_BigBrick,
        158: SpriteImage_FireSnake,
        160: SpriteImage_UnusedBlockPlatform2,
        161: SpriteImage_PipeBubbles,
        166: SpriteImage_BlockTrain,
        170: SpriteImage_ChestnutGoomba,
        171: SpriteImage_PowerupBubble,
        172: SpriteImage_ScrewMushroomWithBolt,
        173: SpriteImage_GiantFloatingLog,
        174: SpriteImage_OneWayGate,
        175: SpriteImage_FlyingQBlock,
        176: SpriteImage_RouletteBlock,
        177: SpriteImage_FireChomp,
        178: SpriteImage_ScalePlatform,
        179: SpriteImage_SpecialExit,
        180: SpriteImage_CheepChomp,
        182: SpriteImage_EventDoor,
        185: SpriteImage_ToadBalloon,
        187: SpriteImage_PlayerBlock,
        188: SpriteImage_MidwayPoint,
        189: SpriteImage_LarryKoopa,
        190: SpriteImage_TiltingGirderUnused,
        191: SpriteImage_TileEvent,
        193: SpriteImage_Urchin,
        194: SpriteImage_MegaUrchin,
        195: SpriteImage_HuckitCrab,
        196: SpriteImage_Fishbones,
        197: SpriteImage_Clam,
        198: SpriteImage_Giantgoomba,
        199: SpriteImage_Megagoomba,
        200: SpriteImage_Microgoomba,
        201: SpriteImage_Icicle,
        202: SpriteImage_MGCannon,
        203: SpriteImage_MGChest,
        205: SpriteImage_GiantBubbleNormal,
        206: SpriteImage_Zoom,
        207: SpriteImage_QBlock,
        208: SpriteImage_QBlockUnused,
        209: SpriteImage_BrickBlock,
        212: SpriteImage_RollingHill,
        214: SpriteImage_FreefallPlatform,
        216: SpriteImage_Poison,
        219: SpriteImage_LineBlock,
        221: SpriteImage_InvisibleBlock,
        222: SpriteImage_ConveyorSpike,
        223: SpriteImage_SpringBlock,
        224: SpriteImage_JumboRay,
        225: SpriteImage_FloatingCoin,
        226: SpriteImage_GiantBubbleUnused,
        227: SpriteImage_PipeCannon,
        228: SpriteImage_ExtendShroom,
        229: SpriteImage_SandPillar,
        230: SpriteImage_Bramball,
        231: SpriteImage_WiggleShroom,
        232: SpriteImage_MechaKoopa,
        233: SpriteImage_Bulber,
        237: SpriteImage_PCoin,
        238: SpriteImage_Foo,
        240: SpriteImage_GiantWiggler,
        242: SpriteImage_FallingLedgeBar,
        252: SpriteImage_EventDeactivBlock,
        253: SpriteImage_RotControlledCoin,
        254: SpriteImage_RotControlledPipe,
        255: SpriteImage_RotatingQBlock,
        257: SpriteImage_MoveWhenOnMetalLavaBlock,
        256: SpriteImage_RotatingBrickBlock,
        259: SpriteImage_RegularDoor,
        260: SpriteImage_MovementController_TwoWayLine,
        261: SpriteImage_OldStoneBlock_MovementControlled,
        262: SpriteImage_PoltergeistItem,
        263: SpriteImage_WaterPiranha,
        264: SpriteImage_WalkingPiranha,
        265: SpriteImage_FallingIcicle,
        266: SpriteImage_RotatingChainLink,
        267: SpriteImage_TiltGrate,
        268: SpriteImage_LavaGeyser,
        269: SpriteImage_Parabomb,
        271: SpriteImage_Mouser,
        272: SpriteImage_IceBro,
        274: SpriteImage_CastleGear,
        275: SpriteImage_FiveEnemyRaft,
        276: SpriteImage_GhostDoor,
        277: SpriteImage_TowerDoor,
        278: SpriteImage_CastleDoor,
        280: SpriteImage_GiantIceBlock,
        286: SpriteImage_WoodCircle,
        287: SpriteImage_PathIceBlock,
        288: SpriteImage_OldBarrel,
        289: SpriteImage_Box,
        291: SpriteImage_Parabeetle,
        292: SpriteImage_HeavyParabeetle,
        294: SpriteImage_IceCube,
        295: SpriteImage_NutPlatform,
        296: SpriteImage_MegaBuzzy,
        297: SpriteImage_DragonCoaster,
        299: SpriteImage_CannonMulti,
        300: SpriteImage_RotCannon,
        301: SpriteImage_RotCannonPipe,
        303: SpriteImage_MontyMole,
        304: SpriteImage_RotFlameCannon,
        305: SpriteImage_LightCircle,
        306: SpriteImage_RotSpotlight,
        308: SpriteImage_HammerBroPlatform,
        309: SpriteImage_SynchroFlameJet,
        310: SpriteImage_ArrowSign,
        311: SpriteImage_MegaIcicle,
        314: SpriteImage_BubbleGen,
        315: SpriteImage_Bolt,
        316: SpriteImage_BoltBox,
        318: SpriteImage_BoxGenerator,
        319: SpriteImage_UnusedWiimoteDoor,
        320: SpriteImage_UnusedSlidingWiimoteDoor,
        321: SpriteImage_ArrowBlock,
        323: SpriteImage_BooCircle,
        325: SpriteImage_GhostHouseStand,
        326: SpriteImage_KingBill,
        327: SpriteImage_LinePlatformBolt,
        330: SpriteImage_RopeLadder,
        331: SpriteImage_DishPlatform,
        333: SpriteImage_PlayerBlockPlatform,
        334: SpriteImage_CheepGiant,
        336: SpriteImage_WendyKoopa,
        337: SpriteImage_IggyKoopa,
        339: SpriteImage_Pipe_MovingUp,
        340: SpriteImage_LemmyKoopa,
        341: SpriteImage_BigShell,
        342: SpriteImage_Muncher,
        343: SpriteImage_Fuzzy,
        344: SpriteImage_MortonKoopa,
        345: SpriteImage_ChainHolder,
        346: SpriteImage_HangingChainPlatform,
        347: SpriteImage_RoyKoopa,
        348: SpriteImage_LudwigVonKoopa,
        352: SpriteImage_RockyWrench,
        353: SpriteImage_Pipe_MovingDown,
        354: SpriteImage_BrownBlock,
        355: SpriteImage_RollingHillWith1Pipe,
        356: SpriteImage_BrownBlock,
        357: SpriteImage_Fruit,
        358: SpriteImage_LavaParticles,
        359: SpriteImage_WallLantern,
        360: SpriteImage_RollingHillWith8Pipes,
        361: SpriteImage_CrystalBlock,
        362: SpriteImage_ColoredBox,
        366: SpriteImage_CubeKinokoRot,
        367: SpriteImage_CubeKinokoLine,
        368: SpriteImage_FlashRaft,
        369: SpriteImage_SlidingPenguin,
        370: SpriteImage_CloudBlock,
        371: SpriteImage_RollingHillCoin,
        374: SpriteImage_SnowWind,
        376: SpriteImage_MovingChainLink,
        377: SpriteImage_Pipe_Up,
        378: SpriteImage_Pipe_Down,
        379: SpriteImage_Pipe_Right,
        380: SpriteImage_Pipe_Left,
        382: SpriteImage_ScrewMushroomNoBolt,
        384: SpriteImage_PipeCooliganGenerator,
        385: SpriteImage_IceBlock,
        386: SpriteImage_PowBlock,
        387: SpriteImage_Bush,
        388: SpriteImage_Barrel,
        389: SpriteImage_StarCoinBoltControlled,
        390: SpriteImage_BoltControlledCoin,
        391: SpriteImage_GlowBlock,
        393: SpriteImage_PropellerBlock,
        394: SpriteImage_LemmyBall,
        395: SpriteImage_SpinyCheep,
        396: SpriteImage_MoveWhenOn,
        397: SpriteImage_GhostHouseBox,
        402: SpriteImage_LineQBlock,
        403: SpriteImage_LineBrickBlock,
        411: SpriteImage_ToadHouseBalloonUnused,
        412: SpriteImage_ToadHouseBalloonUsed,
        413: SpriteImage_WendyRing,
        414: SpriteImage_Gabon,
        415: SpriteImage_BetaLarryKoopa,
        416: SpriteImage_InvisibleOneUp,
        417: SpriteImage_SpinjumpCoin,
        419: SpriteImage_Bowser,
        420: SpriteImage_GiantGlowBlock,
        421: SpriteImage_UnusedGhostDoor,
        422: SpriteImage_ToadQBlock,
        423: SpriteImage_ToadBrickBlock,
        424: SpriteImage_PalmTree,
        425: SpriteImage_Jellybeam,
        427: SpriteImage_Kamek,
        428: SpriteImage_MGPanel,
        432: SpriteImage_Toad,
        433: SpriteImage_FloatingQBlock,
        434: SpriteImage_WarpCannon,
        435: SpriteImage_GhostFog,
        437: SpriteImage_PurplePole,
        438: SpriteImage_CageBlocks,
        439: SpriteImage_CagePeachFake,
        440: SpriteImage_HorizontalRope,
        441: SpriteImage_MushroomPlatform,
        443: SpriteImage_ReplayBlock,
        444: SpriteImage_SwingingVine,
        445: SpriteImage_CagePeachReal,
        447: SpriteImage_UnderwaterLamp,
        448: SpriteImage_MetalBar,
        450: SpriteImage_Pipe_EnterableUp,
        451: SpriteImage_MouserDespawner,
        452: SpriteImage_BowserDoor,
        453: SpriteImage_Seaweed,
        455: SpriteImage_HammerPlatform,
        456: SpriteImage_BossBridge,
        457: SpriteImage_SpinningThinBars,
        464: SpriteImage_SwingingVine,
        466: SpriteImage_LavaIronBlock,
        467: SpriteImage_MovingGemBlock,
        469: SpriteImage_BoltPlatform,
        470: SpriteImage_BoltPlatformWire,
        471: SpriteImage_PotPlatform,
        475: SpriteImage_IceFloe,
        476: SpriteImage_FlyingWrench,
        477: SpriteImage_SuperGuideBlock,
        478: SpriteImage_BowserSwitchSm,
        479: SpriteImage_BowserSwitchLg,
        }

