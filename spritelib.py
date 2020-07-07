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

# spritelib.py
# Contains general code to render sprite images


################################################################
################################################################

############ Imports ############

from math import sin, cos, radians
import os.path

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt
QTransform = QtGui.QTransform

import globals

#################################

OutlineColor = None
OutlinePen = None
OutlineBrush = None
ImageCache = {}
Tiles = {}
TileWidth = 60
SpriteImagesLoaded = set()
MapPositionToZoneID = None

SpritesFolders = []
RealViewEnabled = False
Area = None


################################################################
################################################################
################################################################
########################## Functions ###########################

def loadVines():
    """
    Loads vines
    """
    loadIfNotInImageCache('VineTop', 'vine_top.png')
    loadIfNotInImageCache('VineMid', 'vine_mid.png')
    loadIfNotInImageCache('VineBtm', 'vine_btm.png')


def main():
    """
    Resets Sprites.py to its original settings
    """
    global OutlineColor, OutlinePen, OutlineBrush, ImageCache, SpritesFolders
    OutlinePen = QtGui.QPen(OutlineColor, 4 * (TileWidth/24))
    OutlineBrush = QtGui.QBrush(OutlineColor)

    for i in range(256):
        Tiles[i] = None

    # Don't make a new dict instance for ImageCache because sprites.py
    # won't receive it, which causes bugs.
    ImageCache.clear()
    SpriteImagesLoaded.clear()

    loadVines()

    SpritesFolders = []


def GetImg(imgname, image=False):
    """
    Returns the image path from the PNG filename imgname
    """
    imgname = str(imgname)

    # Try to find the best path
    path = 'miyamotodata/sprites/' + imgname

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

def MapPositionToZoneID(zones, x, y, useid=False):
    """
    Returns the zone ID containing or nearest the specified position
    """
    id = 0
    minimumdist = -1
    rval = -1

    for zone in zones:
        r = zone.ZoneRect
        if r.contains(x, y) and useid:
            return zone.id
        elif r.contains(x, y) and not useid:
            return id

        xdist = 0
        ydist = 0
        if x <= r.left(): xdist = r.left() - x
        if x >= r.right(): xdist = x - r.right()
        if y <= r.top(): ydist = r.top() - y
        if y >= r.bottom(): ydist = y - r.bottom()

        dist = (xdist ** 2 + ydist ** 2) ** 0.5
        if dist < minimumdist or minimumdist == -1:
            minimumdist = dist
            rval = zone.id

        id += 1

    return rval


def rotatePoint(x, y, angle, pivotX=0, pivotY=0):
    """
    Rotate the point (x, y) about (pivotX, pivotY)
    angle must be in radians!
    """
    # Move the pivot to origin
    x -= pivotX
    y -= pivotY

    # Calculate the sine and cosine of angle
    s = sin(angle)
    c = cos(angle)

    # Rotate the point
    x_rotated = x * c - y * s
    y_rotated = x * s + y * c

    # Move the pivot back
    x = x_rotated + pivotX
    y = y_rotated + pivotY

    return x, y


################################################################
################################################################
################################################################
##################### SpriteImage Classes ######################

class SpriteImage:
    """
    Class that contains information about a sprite image
    """
    def __init__(self, parent, scale=None):
        """
        Intializes the sprite image
        """
        self.parent = parent

        if scale is None: scale = TileWidth / 16

        self.alpha = 1.0
        self.image = None
        self.spritebox = Spritebox(scale)
        self.dimensions = 0, 0, 16, 16
        self.scale = scale
        self.aux = []

    @staticmethod
    def loadImages():
        """
        Loads all images needed by the sprite
        """
        pass

    def dataChanged(self):
        """
        Called whenever the sprite data changes
        """
        pass

    def positionChanged(self):
        """
        Called whenever the sprite position changes
        """
        pass

    def paint(self, painter):
        """
        Paints the sprite
        """
        pass

    def delete(self):
        """
        Called when the sprite is deleted
        """
        pass

    # Offset property
    def getOffset(self):
        return (self.xOffset, self.yOffset)
    def setOffset(self, new):
        self.xOffset, self.yOffset = new[0], new[1]
    def delOffset(self):
        self.xOffset, self.yOffset = 0, 0
    offset = property(
        getOffset, setOffset, delOffset,
        'Convenience property that provides access to self.xOffset and self.yOffset in one tuple',
        )

    # Size property
    def getSize(self):
        return (self.width, self.height)
    def setSize(self, new):
        self.width, self.height = new[0], new[1]
    def delSize(self):
        self.width, self.height = 16, 16
    size = property(
        getSize, setSize, delSize,
        'Convenience property that provides access to self.width and self.height in one tuple',
        )

    # Dimensions property
    def getDimensions(self):
        return (self.xOffset, self.yOffset, self.width, self.height)
    def setDimensions(self, new):
        self.xOffset, self.yOffset, self.width, self.height = new[0], new[1], new[2], new[3]
    def delDimensions(self):
        self.xOffset, self.yOffset, self.width, self.height = 0, 0, 16, 16
    dimensions = property(
        getDimensions, setDimensions, delDimensions,
        'Convenience property that provides access to self.xOffset, self.yOffset, self.width and self.height in one tuple',
        )

class SpriteImage_Liquid(SpriteImage):
    """
    Modified image function to support liquids
    """
    def __init__(self, parent, scale=None, image=None, offset=None):
        super().__init__(parent, scale)
        self.image = image
        self.spritebox.shown = False

        if offset is not None:
            self.xOffset = offset[0]
            self.yOffset = offset[1]

    def dataChanged(self):
        super().dataChanged()

        if self.image is not None:
            self.size = (
                (self.image.width() / self.scale) + 1,
                (self.image.height() / self.scale) + 2,
                )
        else:
            del self.size

    def paint(self, painter):
        super().paint(painter)

        if self.image is None: return
        painter.save()
        painter.setOpacity(self.alpha)
        painter.scale(16 * self.scale / TileWidth, 16 * self.scale / TileWidth) # rescale images not based on a 60x60 block size
        painter.setRenderHint(painter.SmoothPixmapTransform)
        painter.drawPixmap(0, 0, self.image)
        painter.restore()


class SpriteImage_Static(SpriteImage):
    """
    A simple class for drawing a static sprite image
    """
    def __init__(self, parent, scale=None, image=None, offset=None):
        super().__init__(parent, scale)
        self.image = image
        self.spritebox.shown = False

        if self.image is not None:
            self.width = (self.image.width() / self.scale) + 1
            self.height = (self.image.height() / self.scale) + 2
        if offset is not None:
            self.xOffset = offset[0]
            self.yOffset = offset[1]

    def dataChanged(self):
        super().dataChanged()

        if self.image is not None:
            self.size = (
                (self.image.width() / self.scale) + 1,
                (self.image.height() / self.scale) + 2,
                )
        else:
            del self.size

    def paint(self, painter):
        super().paint(painter)

        if self.image is None: return
        painter.save()
        painter.setOpacity(self.alpha)
        painter.scale(16 * self.scale / TileWidth, 16 * self.scale / TileWidth) # rescale images not based on a 60x60 block size
        painter.setRenderHint(painter.SmoothPixmapTransform)
        painter.drawPixmap(0, 0, self.image)
        painter.restore()


class SpriteImage_StaticMultiple(SpriteImage_Static):
    """
    A class that acts like a SpriteImage_Static but lets you change
    the image with the dataChanged() function
    """
    def __init__(self, parent, scale=None, image=None, offset=None):
        super().__init__(parent, scale, image, offset)
    # no other changes needed yet


class SpriteImage_MovementController(SpriteImage_StaticMultiple):
    """
    A special class for movement controllers
    """
    def __init__(self, parent, scale=None, image=None):
        super().__init__(parent, scale, image)

        self.controlled = []
        self.previousId = 0

        self.parent.setZValue(500000)

    def getMovementID(self):
        return self.parent.spritedata[10]

    def getStartRotation(self):
        return 0

    def getPivot(self):
        return (self.parent.objx + 8, self.parent.objy + 8)

    def updateControlled(self):
        for controlled in self.controlled:
            controlled.parent.UpdateDynamicSizing()

    def detachControlled(self):
        if self.controlled:
            for controlled in self.controlled:
                controlled.controller = None
                controlled.parent.UpdateDynamicSizing()

            self.controlled = []

        for sprite in globals.Area.sprites:
            if isinstance(sprite.ImageObj, SpriteImage_MovementControlled) and not sprite.ImageObj.controller:
                sprite.UpdateDynamicSizing()

    def dataChanged(self):
        id = self.getMovementID()
        if id != self.previousId:
            self.previousId = id
            self.detachControlled()

        else:
            self.updateControlled()

        super().dataChanged()

    def positionChanged(self):
        self.updateControlled()

    def delete(self):
        self.detachControlled()


class SpriteImage_MovementControlled(SpriteImage_StaticMultiple):
    """
    A class to handle movement-controlled sprites
    and apply the movement to them (rotation, for now)

    Only self.image and AuxiliaryImage objects will be affected

    Make sure you always reset the self.offset,
    self.image and aux.image (if existent) in your dataChanged()!

    If you have a sprite with an aux image and no self.image,
    it is recommended that you make the selection rectangle
    (self.width, self.height) a square
    """

    # If set to false, the image will be moved around but not rotated
    affectImage = True
    affectAUXImage = True

    def __init__(self, parent, scale=None, image=None):
        super().__init__(parent, scale, image)

        self.controller = None

    def getMovementID(self):
        return self.parent.spritedata[10]

    def allowedMovementControllers(self):
        return tuple()

    def findController(self):
        zoneId = self.parent.nearestZone()
        if zoneId == -1:
            self.controller = None
            return

        types = self.allowedMovementControllers()
        if not types:
            self.controller = None
            return

        id = self.getMovementID()
        if id == 0:
            self.controller = None
            return

        for sprite in globals.Area.sprites:
            if ( sprite.nearestZone() == zoneId and sprite.type in types
                 and isinstance(sprite.ImageObj, SpriteImage_MovementController) ):
                if sprite.ImageObj.getMovementID() == id:
                    self.controller = sprite.ImageObj
                    sprite.ImageObj.controlled.append(self)
                    break

        else:
            self.controller = None

    def unhookController(self):
        if self.controller:
            self.controller.controlled.remove(self)
            self.controller = None

    def dataChanged(self):
        id = self.getMovementID()
        if not self.controller or self.controller.getMovementID() != id or id == 0:
            self.unhookController()
            self.findController()

        if self.controller and globals.RotationShown:
            angle = self.controller.getStartRotation()
            angle_radian = radians(angle)
            pivot = self.controller.getPivot()

            xOffset = self.xOffset
            yOffset = self.yOffset

            if not self.image:
                centerX = (self.parent.objx + self.width / 2) + xOffset
                centerY = (self.parent.objy + self.height / 2) + yOffset

                centerX, centerY = rotatePoint(centerX, centerY, angle_radian, *pivot)

                self.xOffset = centerX - (self.parent.objx + self.width / 2)
                self.yOffset = centerY - (self.parent.objy + self.height / 2)

            else:
                old_image = self.image
                if self.affectImage:
                    image = old_image.transformed(QTransform().rotate(angle))

                else:
                    image = old_image

                centerX = self.parent.objx + xOffset + old_image.width() / (2 * self.scale)
                centerY = self.parent.objy + yOffset + old_image.height() / (2 * self.scale)

                centerX, centerY = rotatePoint(centerX, centerY, angle_radian, *pivot)
        
                self.xOffset = centerX - image.width() / (2 * self.scale) - self.parent.objx
                self.yOffset = centerY - image.height() / (2 * self.scale) - self.parent.objy

                self.width = image.width() / self.scale
                self.height = image.height() / self.scale
                self.image = image

            for aux in self.aux:
                if not isinstance(aux, AuxiliaryImage) or not aux.image:
                    continue

                old_image = aux.image
                if self.affectAUXImage:
                    image = old_image.transformed(QTransform().rotate(angle))

                else:
                    image = old_image

                centerX = self.parent.objx + xOffset + aux.x() / self.scale + old_image.width() / (2 * self.scale)
                centerY = self.parent.objy + yOffset + aux.y() / self.scale + old_image.height() / (2 * self.scale)

                centerX, centerY = rotatePoint(centerX, centerY, angle_radian, *pivot)
        
                aux_xOffset = centerX - image.width() / (2 * self.scale) - (self.parent.objx + self.xOffset)
                aux_yOffset = centerY - image.height() / (2 * self.scale) - (self.parent.objy + self.yOffset)

                aux.setImage(image, aux_xOffset, aux_yOffset, True)

            self.parent.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)

        else:
            if self.image:
                super().dataChanged()

            self.parent.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, not globals.SpritesFrozen)

    def positionChanged(self):
        self.parent.UpdateDynamicSizing()

    def delete(self):
        self.unhookController()


class SpriteImage_PivotRotationControlled(SpriteImage_MovementControlled):
    def allowedMovementControllers(self):
        return 68, 116, 69, 118


################################################################
################################################################
################################################################
####################### Spritebox Class ########################

class Spritebox:
    """
    Contains size and other information for a spritebox
    """
    def __init__(self, scale=None):
        super().__init__()
        self.shown = True
        self.xOffset = 0
        self.yOffset = 0
        self.width = 16
        self.height = 16

        if scale is None: scale = TileWidth / 16
        self.scale = scale

    # Offset property
    def getOffset(self):
        return (self.xOffset, self.yOffset)
    def setOffset(self, new):
        self.xOffset, self.yOffset = new[0], new[1]
    def delOffset(self):
        self.xOffset, self.yOffset = 0, 0
    offset = property(
        getOffset, setOffset, delOffset,
        'Convenience property that provides access to self.xOffset and self.yOffset in one tuple',
        )

    # Size property
    def getSize(self):
        return (self.width, self.height)
    def setSize(self, new):
        self.width, self.height = new[0], new[1]
    def delSize(self):
        self.width, self.height = 16, 16
    size = property(
        getSize, setSize, delSize,
        'Convenience property that provides access to self.width and self.height in one tuple',
        )

    # Dimensions property
    def getDimensions(self):
        return (self.xOffset, self.yOffset, self.width, self.height)
    def setDimensions(self, new):
        self.xOffset, self.yOffset, self.width, self.height = new[0], new[1], new[2], new[3]
    def delDimensions(self):
        self.xOffset, self.yOffset, self.width, self.height = 0, 0, 16, 16
    dimensions = property(
        getDimensions, setDimensions, delDimensions,
        'Convenience property that provides access to self.xOffset, self.yOffset, self.width and self.height in one tuple',
        )

    # Rect property
    def getRR(self):
        return QtCore.QRectF(
            self.xOffset * self.scale + 1,
            self.yOffset * self.scale + 1,
            self.width * self.scale - 2,
            self.height * self.scale - 2,
            )
    def setRR(self, new):
        self.dimensions = (
            new.x() / self.scale,
            new.y() / self.scale,
            new.width() / self.scale,
            new.height() / self.scale,
            )
    def delRR(self):
        self.dimensions = 0, 0, 16, 16

    RoundedRect = property(
        getRR, setRR, delRR,
        'Property that contains the rect for the spritebox',
        )

    # BoundingRect property
    def getBR(self):
        return QtCore.QRectF(
            self.xOffset * self.scale,
            self.yOffset * self.scale,
            self.width * self.scale,
            self.height * self.scale,
            )
    def setBR(self, new):
        self.dimensions = (
            new.x() * self.scale,
            new.y() * self.scale,
            new.width() * self.scale,
            new.height() * self.scale,
            )
    def delBR(self):
        self.dimensions = 0, 0, 16, 16
    BoundingRect = property(
        getBR, setBR, delBR,
        'Property that contains the bounding rect for the spritebox',
        )


################################################################
################################################################
################################################################
################# AuxiliarySpriteItem Classes ##################


class AuxiliaryItem:
    """
    Base class for all auxiliary things
    """
    pass


class AuxiliarySpriteItem(AuxiliaryItem, QtWidgets.QGraphicsItem):
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

        self.BoundingRect = QtCore.QRectF(0, 0, TileWidth, TileWidth)

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


class AuxiliaryTrackObject(AuxiliarySpriteItem):
    """
    Track shown behind moving platforms to show where they can move
    """
    Horizontal = 1
    Vertical = 2

    def __init__(self, parent, width, height, direction):
        """
        Constructor
        """
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0, 0, width * (TileWidth/16), height * (TileWidth/16))
        self.setPos(0, 0)
        self.width = width
        self.height = height
        self.direction = direction
        self.hover = False

    def setSize(self, width, height):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0, 0, width * (TileWidth/16), height * (TileWidth/16))
        self.width = width
        self.height = height

    def paint(self, painter, option, widget=None):

        if option is not None:
            painter.setClipRect(option.exposedRect)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(OutlinePen)

        if self.direction == self.Horizontal:
            lineY = self.height * 0.75 * (TileWidth/24)
            painter.drawLine(20 * (TileWidth/24), lineY, (self.width * (TileWidth/16)) - 20 * (TileWidth/24), lineY)
            painter.drawEllipse(8 * (TileWidth/24), lineY - 4 * (TileWidth/24), 8 * (TileWidth/24), 8 * (TileWidth/24))
            painter.drawEllipse((self.width * (TileWidth/16)) - 16 * (TileWidth/24), lineY - 4 * (TileWidth/24), 8 * (TileWidth/24), 8 * (TileWidth/24))
        else:
            lineX = self.width * 0.75 * (TileWidth/24)
            painter.drawLine(lineX, 20 * (TileWidth/24), lineX, (self.height * (TileWidth/16)) - 20 * (TileWidth/24))
            painter.drawEllipse(lineX - 4 * (TileWidth/24), 8 * (TileWidth/24), 8 * (TileWidth/24), 8 * (TileWidth/24))
            painter.drawEllipse(lineX - 4 * (TileWidth/24), (self.height * (TileWidth/16)) - 16 * (TileWidth/24), 8 * (TileWidth/24), 8 * (TileWidth/24))


class AuxiliaryCircleOutline(AuxiliarySpriteItem):
    def __init__(self, parent, width, alignMode=Qt.AlignHCenter):
        """
        Constructor
        """
        super().__init__(parent)

        self.hover = False
        self.alignMode = alignMode
        self.setSize(width)

    def setSize(self, width):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0, 0, width * (TileWidth/16), width * (TileWidth/16))

        centerOffset = (8 - (width / 2)) * (TileWidth/16)
        fullOffset = -(width * (TileWidth/16)) + TileWidth

        xval = 0
        if self.alignMode & Qt.AlignHCenter:
            xval = centerOffset
        elif self.alignMode & Qt.AlignRight:
            xval = fullOffset

        yval = 0
        if self.alignMode & Qt.AlignVCenter:
            yval = centerOffset
        elif self.alignMode & Qt.AlignBottom:
            yval = fullOffset

        self.setPos(xval, yval)
        self.width = width

    def paint(self, painter, option, widget=None):

        if option is not None:
            painter.setClipRect(option.exposedRect)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(OutlinePen)
        painter.setBrush(OutlineBrush)
        painter.drawEllipse(self.BoundingRect)


class AuxiliaryRotationAreaOutline(AuxiliarySpriteItem):
    def __init__(self, parent, width):
        """
        Constructor
        """
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0, 0, width * (TileWidth/16), width * (TileWidth/16))
        self.setPos((8 - (width / 2)) * (TileWidth/16), (8 - (width / 2)) * (TileWidth/16))
        self.width = width
        self.startAngle = 0
        self.spanAngle = 0
        self.hover = False

    def SetAngle(self, startAngle, spanAngle):
        self.startAngle = startAngle * 16
        self.spanAngle = spanAngle * 16

    def paint(self, painter, option, widget=None):

        if option is not None:
            painter.setClipRect(option.exposedRect)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(OutlinePen)
        painter.setBrush(OutlineBrush)
        painter.drawPie(self.BoundingRect, self.startAngle, self.spanAngle)


class AuxiliaryRectOutline(AuxiliarySpriteItem):
    def __init__(self, parent, width, height, xoff=0, yoff=0):
        """
        Constructor
        """
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0, 0, width, height)
        self.setPos(xoff, yoff)
        self.hover = False

    def setSize(self, width, height, xoff=0, yoff=0):
        self.BoundingRect = QtCore.QRectF(0, 0, width, height)
        self.setPos(xoff, yoff)

    def paint(self, painter, option, widget=None):

        if option is not None:
            painter.setClipRect(option.exposedRect)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(OutlinePen)
        painter.setBrush(OutlineBrush)
        painter.drawRect(self.BoundingRect)


class AuxiliaryPainterPath(AuxiliarySpriteItem):
    def __init__(self, parent, path, width, height, xoff=0, yoff=0):
        """
        Constructor
        """
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

    def paint(self, painter, option, widget=None):

        if option is not None:
            painter.setClipRect(option.exposedRect)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        painter.setPen(OutlinePen)
        if self.fillFlag: painter.setBrush(OutlineBrush)
        painter.drawPath(self.PainterPath)


class AuxiliaryImage(AuxiliarySpriteItem):
    def __init__(self, parent, width, height):
        """
        Constructor
        """
        super().__init__(parent)
        self.BoundingRect = QtCore.QRectF(0, 0, width, height)
        self.width = width
        self.height = height
        self.image = None
        self.hover = True
        self.alpha = 1.0

    def setSize(self, width, height, xoff=0, yoff=0):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0, 0, width, height)
        self.setPos(xoff, yoff)
        self.width = width
        self.height = height

    def setImage(self, image, xoff=0, yoff=0, doScale=False):
        if doScale:
            xoff *= TileWidth / 16
            yoff *= TileWidth / 16

        width, height = image.width(), image.height()
        self.setSize(width, height, xoff, yoff)
        self.image = image

    def paint(self, painter, option, widget=None):

        if option is not None:
            painter.setClipRect(option.exposedRect)

        if self.image is not None:
            painter.setOpacity(self.alpha)
            painter.drawPixmap(0, 0, self.image)
            painter.setOpacity(1)


class AuxiliaryImage_FollowsRect(AuxiliaryImage):
    def __init__(self, parent, width, height):
        """
        Constructor
        """
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

    def paint(self, painter, option, widget=None):

        if not RealViewEnabled: return
        super().paint(painter, option, widget)

        if self.realimage is None:
            try: self.realimage = self.image
            except: pass

    def move(self, x, y, w, h):
        """
        Repositions the auxiliary image
        """

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
        if self.realimage is not None:
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
            newy = y + (h / 2) - (self.height / 2)

        # Translate that to relative coords
        parent = self.parent
        newx = newx - parent.x()
        newy = newy - parent.y()

        # Set the pos
        self.setPos(newx, newy)

        # Update the affected area of the scene
        if self.scene() is not None:
            self.scene().update(oldx + parent.x(), oldy + parent.y(), self.width, self.height)


class AuxiliaryZoneItem(AuxiliaryItem, QtWidgets.QGraphicsItem):
    """
    An auxiliary item that can have a zone as its parent
    """
    def __init__(self, parent, imageObj):
        """
        Generic constructor for auxiliary zone items
        """
        super().__init__(parent)
        self.parent = parent
        self.imageObj = imageObj
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)
        self.setParentItem(parent)
        self.hover = False

        if parent is not None:
            parent.aux.add(self)

        self.BoundingRect = QtCore.QRectF(0, 0, TileWidth, TileWidth)

    def setIsBehindZone(self, behind):
        """
        This allows you to choose whether the auiliary item will display
        behind the zone or in front of it. Default is for the item to
        be in front of the zone.
        """
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, behind)

    def setZoneID(self, id):
        """
        Changes this aux item's parent to zone with the given id.
        Raises ValueError if no zone with this id exists.
        """

        if not hasattr(Area, 'zones'): return

        z = None
        for iterz in Area.zones:
            if iterz.id == id: z = iterz
        if z is None:
            raise ValueError('No zone with this ID exists.')
        
        if self.parent is not None:
            self.parent.aux.remove(self)
        self.setParentItem(z)
        self.parent = z
        z.aux.add(self)

    def alignToZone(self):
        """
        Resets the position and size of the AuxiliaryZoneItem to that of the zone
        """
        self.setPos(0, 0)
        if self.parent is not None:
            self.BoundingRect = QtCore.QRectF(self.parent.BoundingRect)
        else:
            self.BoundingRect = QtCore.QRectF(0, 0, TileWidth, TileWidth)

    def zoneRepositioned(self):
        """
        Called when the zone is repositioned or resized
        """
        pass

    def boundingRect(self):
        """
        Required for Qt
        """
        return self.BoundingRect


class AuxiliaryLocationItem(AuxiliaryItem, QtWidgets.QGraphicsItem):
    """
    An auxiliary item that can have a location as its parent
    """
    def __init__(self, parent, imageObj):
        """
        Generic constructor for auxiliary items
        """
        super().__init__(parent)
        self.parent = parent
        self.imageObj = imageObj
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, False)
        self.setParentItem(parent)
        self.hover = False
        self.BoundingRect = QtCore.QRectF(0, 0, TileWidth, TileWidth)

    def setIsBehindLocation(self, behind):
        """
        This allows you to choose whether the auiliary item will display
        behind the zone or in front of it. Default is for the item to
        be in front of the location.
        """
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, behind)

    def alignToLocation(self):
        """
        Resets the position and size of the AuxiliaryLocationItem to that of the location
        """
        self.setPos(0, 0)
        self.setSize(self.parent.width(), self.parent.height())

    def boundingRect(self):
        """
        Required for Qt
        """
        return self.BoundingRect

