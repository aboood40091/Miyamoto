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



# spritelib.py
# Contains general code to render sprite images


################################################################
################################################################

# Imports
import os.path

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

OutlineColor = None
OutlinePen = None
OutlineBrush = None
ImageCache = {}
Tiles = {}
SpriteImagesLoaded = set()

SpritesFolders = []
RealViewEnabled = False


################################################################
################################################################
################################################################
########################## Functions ###########################

def main():
    """Resets Sprites.py to its original settings"""
    global OutlineColor, OutlinePen, OutlineBrush, ImageCache, SpritesFolders
    OutlinePen = QtGui.QPen(OutlineColor, 4)
    OutlineBrush = QtGui.QBrush(OutlineColor)

    # Don't make a new dict instance for ImageCache because sprites.py
    # won't receive it, which causes bugs.
    ImageCache.clear()
    SpriteImagesLoaded.clear()
    LoadBasicSuite()

    SpritesFolders = []


def GetImg(imgname, image=False):
    """Returns the image path from the PNG filename imgname"""
    imgname = str(imgname)

    # Try to find the best path
    path = 'reggiedata/sprites/' + imgname

    for folder in reversed(SpritesFolders): # find the most recent copy
        tryPath = folder + '/' + imgname
        if os.path.isfile(tryPath):
            path = tryPath
            break

    # Return the appropriate object
    if os.path.isfile(path):
        if image: return QtGui.QImage(path)
        else: return QtGui.QPixmap(path)


def loadIfNotInImageCache(name, filename):
    """
    If name is not in ImageCache, loads the image
    referenced by 'filename' and puts it there
    """
    if name not in ImageCache:
        ImageCache[name] = GetImg(filename)


def LoadBasicSuite():

    # Load some coins, because coins are in almost every Mario level ever
    ImageCache['Coin'] = GetImg('coin.png')
    ImageCache['SpecialCoin'] = GetImg('special_coin.png')
    ImageCache['PCoin'] = GetImg('p_coin.png')
    ImageCache['RedCoin'] = GetImg('redcoin.png')
    ImageCache['RedCoinRing'] = GetImg('redcoinring.png')
    ImageCache['StarCoin'] = GetImg('starcoin.png')

    # Load blocks
    BlockImage = GetImg('blocks.png')
    Blocks = []
    count = BlockImage.width() // 24
    for i in range(count):
        Blocks.append(BlockImage.copy(i * 24, 0, 24, 24))
    ImageCache['Blocks'] = Blocks

    # Load the overrides
    Overrides = QtGui.QPixmap('reggiedata/overrides.png')
    Blocks = []
    x = Overrides.width() // 24
    y = Overrides.height() // 24
    for i in range(y):
        for j in range(x):
            Blocks.append(Overrides.copy(j * 24, i * 24, 24, 24))
    ImageCache['Overrides'] = Blocks

    # Load the characters
    for num in range(4):
        for direction in 'lr':
            ImageCache['Character%d%s' % (num + 1, direction.upper())] = \
                GetImg('character_%d_%s.png' % (num + 1, direction))



################################################################
################################################################
################################################################
##################### SpriteImage Classes ######################

class SpriteImage():
    """
    Class that contains information about a sprite image
    """
    def __init__(self, parent):
        self.parent = parent
        self.alpha = 1.0
        self.image = None
        self.spritebox = Spritebox()
        self.xOffset = 0
        self.yOffset = 0
        self.width = 16
        self.height = 16
        self.aux = []
        self.updateSceneAfterPaint = False

    @staticmethod
    def loadImages():
        pass
    def updateSize(self):
        pass
    def paint(self, painter):
        pass
    def realViewZone(self, painter, zoneRect, viewRect):
        pass

    def getOffset(self):
        return (self.xOffset, self.yOffset)
    def setOffset(self, new):
        self.xOffset, self.yOffset = new[0], new[1]
    def delOffset(self):
        self.xOffset, self.yOffset = [0, 0]
    def getSize(self):
        return (self.width, self.height)
    def setSize(self, new):
        self.width, self.height = new[0], new[1]
    def delSize(self):
        self.width, self.height = [16, 16]
    def getDimensions(self):
        return (self.xOffset, self.yOffset, self.width, self.height)
    def setDimensions(self, new):
        self.xOffset, self.yOffset, self.width, self.height = new[0], new[1], new[2], new[3]
    def delDimensions(self):
        self.xOffset, self.yOffset, self.width, self.height = [0, 0, 16, 16]

    offset = property(getOffset, setOffset, delOffset,
        'Convenience property that provides access to self.xOffset and self.yOffset in one tuple')
    size = property(getSize, setSize, delSize,
        'Convenience property that provides access to self.width and self.height in one tuple')
    dimensions = property(getDimensions, setDimensions, delDimensions,
        'Convenience property that provides access to self.xOffset, self.yOffset, self.width and self.height in one tuple')


class SpriteImage_Static(SpriteImage):
    """
    A simple class for drawing a static sprite image
    """
    def __init__(self, parent, image=None, offset=None):
        super().__init__(parent)
        self.image = image
        self.spritebox.shown = False
        if self.image is not None:
            self.width = (self.image.width() / 1.5) + 1
            self.height = (self.image.height() / 1.5) + 2
        if offset is not None:
            self.xOffset = offset[0]
            self.yOffset = offset[1]
    def updateSize(self):
        super().updateSize()

        if self.image is not None:
            self.size = (
                (self.image.width() / 1.5) + 1,
                (self.image.height() / 1.5) + 2,
                )
        else:
            del self.size

    def paint(self, painter):
        super().paint(painter)

        if self.image is None: return
        painter.save()
        painter.setOpacity(self.alpha)
        painter.drawPixmap(0, 0, self.image)
        painter.restore()


class SpriteImage_StaticMultiple(SpriteImage_Static):
    """
    A class that acts like a SpriteImage_Static but lets you change
    the image with the updateSize() function
    """
    def __init__(self, parent, image=None, offset=None):
        super().__init__(parent, image, offset)
    # no other changes needed yet


################################################################
################################################################
################################################################
####################### Spritebox Class ########################

class Spritebox():
    """
    Contains size and other information for a spritebox
    """
    def __init__(self):
        super().__init__()
        self.shown = True
        self.xOffset = 0
        self.yOffset = 0
        self.width = 24
        self.height = 24

    def getOffset(self):
        return (self.xOffset, self.yOffset)
    def setOffset(self, new):
        self.xOffset, self.yOffset = new[0], new[1]
    def delOffset(self):
        self.xOffset, self.yOffset = [0, 0]
    def getSize(self):
        return (self.width, self.height)
    def setSize(self, new):
        self.width, self.height = new[0], new[1]
    def delSize(self):
        self.width, self.height = [16, 16]
    def getDimensions(self):
        return (self.xOffset, self.yOffset, self.width, self.height)
    def setDimensions(self, new):
        self.xOffset, self.yOffset, self.width, self.height = new[0], new[1], new[2], new[3]
    def delDimensions(self):
        self.xOffset, self.yOffset, self.width, self.height = [0, 0, 16, 16]

    offset = property(getOffset, setOffset, delOffset,
        'Convenience property that provides access to self.xOffset and self.yOffset in one tuple')
    size = property(getSize, setSize, delSize,
        'Convenience property that provides access to self.width and self.height in one tuple')
    dimensions = property(getDimensions, setDimensions, delDimensions,
        'Convenience property that provides access to self.xOffset, self.yOffset, self.width and self.height in one tuple')

    def getRR(self):
        return QtCore.QRectF(
            self.xOffset + 1,
            self.yOffset + 1,
            self.width - 2,
            self.height - 2,
            )
    def setRR(self, new):
        self.dimensions = (
            new.x() - 1,
            new.y() - 1,
            new.width() + 2,
            new.height() + 2,
            )
    def delRR(self):
        self.dimensions = (0, 0, 24, 24)

    RoundedRect = property(getRR, setRR, delRR,
        'Property that contains the rounded rect for the spritebox')

    def getBR(self):
        return QtCore.QRectF(
            self.xOffset,
            self.yOffset,
            self.width,
            self.height,
            )
    def setBR(self, new):
        self.dimensions = (
            new.x(),
            new.y(),
            new.width(),
            new.height(),
            )
    def delBR(self):
        self.dimensions = (0, 0, 24, 24)

    BoundingRect = property(getBR, setBR, delBR,
        'Property that contains the bounding rect for the spritebox')


################################################################
################################################################
################################################################
#################### AuxiliaryItem Classes #####################

class AuxiliaryItem(QtWidgets.QGraphicsItem):
    """
    Base class for auxiliary objects that accompany specific sprite types
    """
    def __init__(self, parent):
        """
        Generic constructor for auxiliary items
        """
        super().__init__(parent)
        self.parent = parent
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, True)
        self.setParentItem(parent)
        self.hover = False

    def setIsBehindSprite(self, behind):
        """
        This allows you to choose whether the auiliary item will display
        behind the sprite or in front of it. Default is for the item to
        be behind the sprite.
        """
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, behind)

    def boundingRect(self):
        """
        Required for Qt
        """
        return self.BoundingRect


class AuxiliaryTrackObject(AuxiliaryItem):
    """Track shown behind moving platforms to show where they can move"""
    Horizontal = 1
    Vertical = 2

    def __init__(self, parent, width, height, direction):
        """Constructor"""
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0, 0, width * 1.5, height * 1.5)
        self.setPos(0,0)
        self.width = width
        self.height = height
        self.direction = direction
        self.hover = False

    def setSize(self, width, height):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0, 0, width * 1.5, height * 1.5)
        self.width = width
        self.height = height

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)

        if self.direction == self.Horizontal:
            lineY = self.height * 0.75
            painter.drawLine(20, lineY, (self.width * 1.5) - 20, lineY)
            painter.drawEllipse(8, lineY - 4, 8, 8)
            painter.drawEllipse((self.width * 1.5) - 16, lineY - 4, 8, 8)
        else:
            lineX = self.width * 0.75
            painter.drawLine(lineX, 20, lineX, (self.height * 1.5) - 20)
            painter.drawEllipse(lineX - 4, 8, 8, 8)
            painter.drawEllipse(lineX - 4, (self.height * 1.5) - 16, 8, 8)


class AuxiliaryCircleOutline(AuxiliaryItem):
    def __init__(self, parent, width):
        """Constructor"""
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0, 0, width * 1.5, width * 1.5)
        self.setPos((8 - (width / 2)) * 1.5, 0)
        self.width = width
        self.hover = False

    def setSize(self, width):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0, 0, width * 1.5, width * 1.5)
        self.setPos((8 - (width / 2)) * 1.5, 0)
        self.width = width

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)
        painter.setBrush(OutlineBrush)
        painter.drawEllipse(self.BoundingRect)


class AuxiliaryRotationAreaOutline(AuxiliaryItem):
    def __init__(self, parent, width):
        """Constructor"""
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0,0,width*1.5,width*1.5)
        self.setPos((8 - (width / 2)) * 1.5, (8 - (width / 2)) * 1.5)
        self.width = width
        self.startAngle = 0
        self.spanAngle = 0
        self.hover = False

    def SetAngle(self, startAngle, spanAngle):
        self.startAngle = startAngle * 16
        self.spanAngle = spanAngle * 16

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)
        painter.setBrush(OutlineBrush)
        painter.drawPie(self.BoundingRect, self.startAngle, self.spanAngle)


class AuxiliaryRectOutline(AuxiliaryItem):
    def __init__(self, parent, width, height, xoff=0, yoff=0):
        """Constructor"""
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.setPos(xoff, yoff)
        self.hover = False

    def setSize(self, width, height, xoff=0, yoff=0):
        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.setPos(xoff, yoff)

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)
        painter.setBrush(OutlineBrush)
        painter.drawRect(self.BoundingRect)


class AuxiliaryPainterPath(AuxiliaryItem):
    def __init__(self, parent, path, width, height, xoff=0, yoff=0):
        """Constructor"""
        super().__init__(parent)

        self.PainterPath = path
        self.setPos(xoff, yoff)
        self.fillFlag = True

        self.BoundingRect = QtCore.QRectF(0, 0, width, height)
        self.hover = False

    def SetPath(self, path):
        self.PainterPath = path

    def setSize(self, width, height, xoff=0, yoff=0):
        self.BoundingRect = QtCore.QRectF(0, 0, width, height)
        self.setPos(xoff, yoff)

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)
        if self.fillFlag: painter.setBrush(OutlineBrush)
        painter.drawPath(self.PainterPath)


class AuxiliaryImage(AuxiliaryItem):
    def __init__(self, parent, width, height):
        """Constructor"""
        super().__init__(parent)
        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.width = width
        self.height = height
        self.image = None
        self.hover = True

    def setSize(self, width, height, xoff=0, yoff=0):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.setPos(xoff, yoff)
        self.width = width
        self.height = height

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        if self.image != None:
            painter.drawPixmap(0, 0, self.image)


class AuxiliaryImage_FollowsRect(AuxiliaryImage):
    def __init__(self, parent, width, height):
        """Constructor"""
        super().__init__(parent, width, height)
        self.alignment = Qt.AlignTop | Qt.AlignLeft
        self.realwidth = self.width
        self.realheight = self.height
        self.realimage = None
        # Doing it this way may provide a slight speed boost?
        self.flagPresent = lambda flags, flag: flags | flag == flags

    def setSize(self, width, height):
        super().setSize(width, height)
        self.realwidth = width
        self.realheight = height

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.realimage == None:
            try: self.realimage = self.image
            except: pass

    def move(self, x, y, w, h):
        """Repositions the auxiliary image"""

        # This will be used later
        oldx, oldy = self.x(), self.y()

        # Decide on the height to use
        # This solves the problem of "what if
        # agument w is smaller than self.width?"
        self.width = self.realwidth
        self.height = self.realheight
        changedSize = False
        if w < self.width:
            self.width = w
            changedSize = True
        if h < self.height:
            self.height = h
            changedSize = True
        if self.realimage != None:
            if changedSize:
                self.image = self.realimage.copy(0, 0, w, h)
            else:
                self.image = self.realimage
        

        # Find the absolute X-coord
        if self.flagPresent(self.alignment, Qt.AlignLeft):
            newx = x
        elif self.flagPresent(self.alignment, Qt.AlignRight):
            newx = x + w - self.width
        else:
            newx = x + (w/2) - (self.width/2)

        # Find the absolute Y-coord
        if self.flagPresent(self.alignment, Qt.AlignTop):
            newy = y
        elif self.flagPresent(self.alignment, Qt.AlignBottom):
            newy = y + h - self.height
        else:
            newy = y + (h/2) - (self.height/2)

        # Translate that to relative coords
        parent = self.parent
        newx = newx - parent.x()
        newy = newy - parent.y()

        # Set the pos
        self.setPos(newx, newy)

        # Update the affected area of the scene
        if self.scene() != None:
            self.scene().update(oldx + parent.x(), oldy + parent.y(), self.width, self.height)
