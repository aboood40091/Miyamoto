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

import base64
import random

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

if not hasattr(QtWidgets.QGraphicsItem, 'ItemSendsGeometryChanges'):
    # enables itemChange being called on QGraphicsItem
    QtWidgets.QGraphicsItem.ItemSendsGeometryChanges = QtWidgets.QGraphicsItem.GraphicsItemFlag(0x800)

import globals
import spritelib as SLib
from tileset import RenderObject
from ui import GetIcon
from verifications import SetDirty

#################################


class LevelEditorItem(QtWidgets.QGraphicsItem):
    """
    Class for any type of item that can show up in the level editor control
    """
    positionChanged = None  # Callback: positionChanged(LevelEditorItem obj, int oldx, int oldy, int x, int y)
    autoPosChange = False
    dragoffsetx = 0
    dragoffsety = 0

    def __init__(self):
        """
        Generic constructor for level editor items
        """
        super().__init__()
        self.setFlag(self.ItemSendsGeometryChanges, True)

    def __lt__(self, other):
        return (self.objx * 100000 + self.objy) < (other.objx * 100000 + other.objy)

    def itemChange(self, change, value):
        """
        Makes sure positions don't go out of bounds and updates them as necessary
        """

        tileWidthMult = globals.TileWidth / 16
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # snap to 24x24
            newpos = value

            # snap even further if Alt isn't held
            # but -only- if globals.OverrideSnapping is off
            doSnap = False
            if (not globals.OverrideSnapping) and (not self.autoPosChange):
                doSnap = True

            if hasattr(self, 'dragging') and self.dragging:
                doSnap = False

            if doSnap:
                if self.scene() is None:
                    objectsSelected = False
                else:
                    objectsSelected = any([isinstance(thing, ObjectItem) for thing in globals.mainWindow.CurrentSelection])
                if QtWidgets.QApplication.keyboardModifiers() == Qt.AltModifier and not isinstance(self, LocationItem):
                    # Alt is held; don't snap
                    newpos.setX(int(int((newpos.x() + 0.75) / tileWidthMult) * tileWidthMult))
                    newpos.setY(int(int((newpos.y() + 0.75) / tileWidthMult) * tileWidthMult))
                elif not objectsSelected and self.isSelected() and len(globals.mainWindow.CurrentSelection) > 1:
                    # Snap to 8x8, but with the dragoffsets
                    dragoffsetx, dragoffsety = int(self.dragoffsetx), int(self.dragoffsety)
                    if dragoffsetx < -(globals.TileWidth / 2): dragoffsetx += globals.TileWidth / 2
                    if dragoffsety < -(globals.TileWidth / 2): dragoffsety += globals.TileWidth / 2
                    if dragoffsetx == 0: dragoffsetx = -(globals.TileWidth / 2)
                    if dragoffsety == 0: dragoffsety = -(globals.TileWidth / 2)
                    referenceX = int(
                        (newpos.x() + globals.TileWidth / 4 + globals.TileWidth / 2 + dragoffsetx) / (globals.TileWidth / 2)) * globals.TileWidth / 2
                    referenceY = int(
                        (newpos.y() + globals.TileWidth / 4 + globals.TileWidth / 2 + dragoffsety) / (globals.TileWidth / 2)) * globals.TileWidth / 2
                    newpos.setX(referenceX - (globals.TileWidth / 2 + dragoffsetx))
                    newpos.setY(referenceY - (globals.TileWidth / 2 + dragoffsety))
                elif objectsSelected and self.isSelected():
                    # Objects are selected, too; move in sync by snapping to whole blocks
                    dragoffsetx, dragoffsety = int(self.dragoffsetx), int(self.dragoffsety)
                    if dragoffsetx == 0: dragoffsetx = -globals.TileWidth
                    if dragoffsety == 0: dragoffsety = -globals.TileWidth
                    referenceX = int((newpos.x() + globals.TileWidth / 2 + globals.TileWidth + dragoffsetx) / globals.TileWidth) * globals.TileWidth
                    referenceY = int((newpos.y() + globals.TileWidth / 2 + globals.TileWidth + dragoffsety) / globals.TileWidth) * globals.TileWidth
                    newpos.setX(referenceX - (globals.TileWidth + dragoffsetx))
                    newpos.setY(referenceY - (globals.TileWidth + dragoffsety))
                else:
                    # Snap to 8x8
                    newpos.setX(int(int((newpos.x() + globals.TileWidth / 4) / (globals.TileWidth / 2)) * globals.TileWidth / 2))
                    newpos.setY(int(int((newpos.y() + globals.TileWidth / 4) / (globals.TileWidth / 2)) * globals.TileWidth / 2))

            x = newpos.x()
            y = newpos.y()

            # don't let it get out of the boundaries
            if x < 0: newpos.setX(0)
            if x > 1023 * globals.TileWidth: newpos.setX(1023 * globals.TileWidth)
            if y < 0: newpos.setY(0)
            if y > 511 * globals.TileWidth: newpos.setY(511 * globals.TileWidth)

            # update the data
            x = int(newpos.x() / tileWidthMult)
            y = int(newpos.y() / tileWidthMult)
            if x != self.objx or y != self.objy:
                updRect = QtCore.QRectF(
                    self.x() + self.BoundingRect.x(),
                    self.y() + self.BoundingRect.y(),
                    self.BoundingRect.width(),
                    self.BoundingRect.height(),
                )
                if self.scene() is not None:
                    self.scene().update(updRect)

                oldx = self.objx
                oldy = self.objy
                self.objx = x
                self.objy = y
                if self.positionChanged is not None:
                    self.positionChanged(self, oldx, oldy, x, y)

                SetDirty()

            return newpos

        return QtWidgets.QGraphicsItem.itemChange(self, change, value)

    def getFullRect(self):
        """
        Basic implementation that returns self.BoundingRect
        """
        return self.BoundingRect.translated(self.pos())

    def UpdateListItem(self, updateTooltipPreview=False):
        """
        Updates the list item
        """
        if not hasattr(self, 'listitem'): return
        if self.listitem is None: return

        if updateTooltipPreview:
            # It's just like Qt to make this overly complicated. XP
            img = self.renderInLevelIcon()
            byteArray = QtCore.QByteArray()
            buf = QtCore.QBuffer(byteArray)
            img.save(buf, 'PNG')
            byteObj = bytes(byteArray)
            b64 = base64.b64encode(byteObj).decode('utf-8')

            self.listitem.setToolTip('<img src="data:image/png;base64,' + b64 + '" />')

        self.listitem.setText(self.ListString())

    def renderInLevelIcon(self):
        """
        Renders an icon of this item as it appears in the level
        """
        # Constants:
        # Maximum size of the preview (it will be shrunk if it exceeds this)
        maxSize = QtCore.QSize(256, 256)
        # Percentage of the size to use for margins
        marginPct = 0.75
        # Maximum margin (24 = 1 block)
        maxMargin = 96

        # Get the full bounding rectangle
        br = self.getFullRect()

        # Expand the rect to add extra margins around the edges
        marginX = br.width() * marginPct
        marginY = br.height() * marginPct
        marginX = min(marginX, maxMargin)
        marginY = min(marginY, maxMargin)
        br.setX(br.x() - marginX)
        br.setY(br.y() - marginY)
        br.setWidth(br.width() + marginX)
        br.setHeight(br.height() + marginY)

        # Take the screenshot
        ScreenshotImage = QtGui.QImage(br.width(), br.height(), QtGui.QImage.Format_ARGB32)
        ScreenshotImage.fill(Qt.transparent)

        RenderPainter = QtGui.QPainter(ScreenshotImage)
        globals.mainWindow.scene.render(
            RenderPainter,
            QtCore.QRectF(0, 0, br.width(), br.height()),
            br,
        )
        RenderPainter.end()

        # Shrink it if it's too big
        final = ScreenshotImage
        if ScreenshotImage.width() > maxSize.width() or ScreenshotImage.height() > maxSize.height():
            final = ScreenshotImage.scaled(
                maxSize,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )

        return final

    def boundingRect(self):
        """
        Required for Qt
        """
        return self.BoundingRect


class ObjectItem(LevelEditorItem):
    """
    Level editor item that represents an ingame object
    """

    def __init__(self, tileset, type, layer, x, y, width, height, z, data=0):
        """
        Creates an object with specific data
        """
        super().__init__()

        # Specify the data value for each Item-containing block
        items = {16: 1, 17: 2, 18: 3, 19: 4, 20: 5, 21: 6, 22: 7, 23: 8,
                 24: 9, 25: 10, 26: 11, 27: 12, 28: data, 29: 14, 30: 15,
                 31: 16, 32: 17, 33: 18, 34: 19, 35: 20, 36: 21, 37: 22, 38: 23, 39: 24}

        self.tileset = tileset
        self.type = type
        self.original_type = type
        self.objx = x
        self.objy = y
        self.layer = layer
        self.width = width
        self.height = height

        if self.tileset == 0 and self.type in items:
            # Set the data value for
            # each Item-containing block.
            self.data = items[self.type]

            # Transform Item-containing blocks into
            # ? blocks with specific data values.

            # Technically, we don't even need to do this
            # but this is how Nintendo did it, so... ¯\_(ツ)_/¯
            self.type = 28

            # Nintendo didn't use value 0 for ?
            # blocks even though it's fully functional.
            # Let's use value 13, like them.
            if self.data == 0: self.data = 13

        else:
            # In NSMBU, you can transform *any* object
            # from *any* tileset into a brick/?/stone/etc.
            # block by changing its data value.
            # (from 0 to something else)

            # This was discovered by flzmx
            # and AboodXD by an accident.

            # The tiles' properties can also effect
            # what the object will turn into
            # when its data value is not 0.

            # Let's hardcode the object's data value to 0
            # to prevent funny stuff from happening ingame.
            if data > 0: SetDirty()
            self.data = 0

        self.objdata = None

        self.setFlag(self.ItemIsMovable, not globals.ObjectsFrozen)
        self.setFlag(self.ItemIsSelectable, not globals.ObjectsFrozen)
        self.UpdateRects()

        self.dragging = False
        self.dragstartx = -1
        self.dragstarty = -1
        self.objsDragging = {}

        globals.DirtyOverride += 1
        self.setPos(x * globals.TileWidth, y * globals.TileWidth)
        globals.DirtyOverride -= 1

        self.setZValue(z)
        self.UpdateTooltip()

        if layer == 0:
            self.setVisible(globals.Layer0Shown)
        elif layer == 1:
            self.setVisible(globals.Layer1Shown)
        elif layer == 2:
            self.setVisible(globals.Layer2Shown)

        self.updateObjCache()
        self.UpdateTooltip()

    def UpdateSearchDatabase(self):
        y = 0

        self.RemoveFromSearchDatabase()

        import quickpaint

        quickpaint.QuickPaintOperations.object_search_database[self] = []
        if self.width == 1 and self.height == 1:
            if not quickpaint.QuickPaintOperations.object_search_database.get((self.objx, self.objy, self.layer)):
                quickpaint.QuickPaintOperations.object_search_database[self.objx, self.objy, self.layer] = []

            if self not in quickpaint.QuickPaintOperations.object_search_database[(self.objx, self.objy, self.layer)]:
                quickpaint.QuickPaintOperations.object_search_database[(self.objx, self.objy, self.layer)].append(self)
                quickpaint.QuickPaintOperations.object_search_database[self].append((self.objx, self.objy, self.layer))

        elif self.objdata:
            for row in self.objdata:
                x = 0
                for tile in row:
                    if tile != -1:
                        if not quickpaint.QuickPaintOperations.object_search_database.get(
                                (self.objx + x, self.objy + y, self.layer)):
                            quickpaint.QuickPaintOperations.object_search_database[
                                self.objx + x, self.objy + y, self.layer] = []

                        if self not in quickpaint.QuickPaintOperations.object_search_database[
                            (self.objx + x, self.objy + y, self.layer)]:
                            quickpaint.QuickPaintOperations.object_search_database[
                                (self.objx + x, self.objy + y, self.layer)].append(self)
                            quickpaint.QuickPaintOperations.object_search_database[self].append(
                                (self.objx + x, self.objy + y, self.layer))

                    x += 1

                y += 1

        del quickpaint

    def RemoveFromSearchDatabase(self):
        import quickpaint

        if self in quickpaint.QuickPaintOperations.object_search_database:
            for t in quickpaint.QuickPaintOperations.object_search_database[self]:
                if (quickpaint.QuickPaintOperations.object_search_database.get(t)
                    and self in quickpaint.QuickPaintOperations.object_search_database[t]):
                    quickpaint.QuickPaintOperations.object_search_database[t].remove(self)

            del quickpaint.QuickPaintOperations.object_search_database[self]

        del quickpaint

    def SetType(self, tileset, type):
        """
        Sets the type of the object
        """
        self.tileset = tileset
        self.type = type
        self.updateObjCache()
        self.update()

        self.UpdateTooltip()

    def UpdateTooltip(self):
        """
        Updates the tooltip
        """
        self.setToolTip(
            globals.trans.string('Objects', 0, '[tileset]', self.tileset + 1, '[obj]', self.type, '[width]', self.width,
                         '[height]', self.height, '[layer]', self.layer))

    def updateObjCache(self):
        """
        Updates the rendered object data
        """
        self.objdata = RenderObject(self.tileset, self.type, self.width, self.height)
        self.randomise()
        self.UpdateSearchDatabase()
 
    def randomise(self, startx=0, starty=0, width=None, height=None):
        """
        Randomises (a part of) the self.objdata according to the loaded tileset
        info
        """
        # TODO: Make this work even on the edges of the object. This requires a
        # function that returns the tile on the block next to the current tile
        # on a specified layer. Maybe something for the Area class?

        if globals.ObjectDefinitions is None \
           or globals.ObjectDefinitions[self.tileset] is None \
           or globals.ObjectDefinitions[self.tileset][self.type] is None \
           or globals.ObjectDefinitions[self.tileset][self.type].rows is None \
           or globals.ObjectDefinitions[self.tileset][self.type].rows[0] is None \
           or globals.ObjectDefinitions[self.tileset][self.type].rows[0][0] is None \
           or len(globals.ObjectDefinitions[self.tileset][self.type].rows[0][0]) == 1:
            # no randomisation info -> exit
            return

        obj = globals.ObjectDefinitions[self.tileset][self.type]
        if (obj.width, obj.height) != (1, 1) or obj.randByte & 0xF < 2:
            # cannot randomise -> exit
            return

        if width is None:
            width = self.width

        if height is None:
            height = self.height

        direction = obj.randByte >> 4
        randLen = obj.randByte & 0xF

        tile = obj.rows[0][0][1] & 0xFF

        tiles = []
        for z in range(randLen):
            tiles.append(tile + z)

        # randomise every tile in this thing
        for y in range(starty, starty + height):
            for x in range(startx, startx + width):
                # should we randomise this tile?
                tiles_ = tiles[:]

                # Take direction into account - chosen tile must be different from
                # the tile to the left/right/top/bottom. Using try/except here
                # so the value has to be looked up only once.

                # direction is 2 bits:
                # highest := vertical direction; lowest := horizontal direction
                if direction & 0b01:
                    # only look at the left neighbour, since we will generate the
                    # right neighbour later
                    try:
                        tiles_.remove(self.objdata[y][x-1] & 0xFF)
                    except:
                        pass

                if direction & 0b10:
                    # only look at the above neighbour, since we will generate the
                    # neighbour below later
                    try:
                        tiles_.remove(self.objdata[y-1][x] & 0xFF)
                    except:
                        pass

                # if we removed all options, just use the original tiles
                if len(tiles_) == 0:
                    tiles_ = tiles

                choice = (self.tileset << 8) | random.choice(tiles_)
                self.objdata[y][x] = choice

    def updateObjCacheWH(self, width, height):
        """
        Updates the rendered object data with custom width and height
        """
        # if we don't have to randomise, simply rerender everything
        if globals.ObjectDefinitions is None \
           or globals.ObjectDefinitions[self.tileset] is None \
           or globals.ObjectDefinitions[self.tileset][self.type] is None \
           or globals.ObjectDefinitions[self.tileset][self.type].rows is None \
           or globals.ObjectDefinitions[self.tileset][self.type].rows[0] is None \
           or globals.ObjectDefinitions[self.tileset][self.type].rows[0][0] is None \
           or len(globals.ObjectDefinitions[self.tileset][self.type].rows[0][0]) == 1:
            # no randomisation info -> exit
            save = (self.width, self.height)
            self.width, self.height = width, height
            self.updateObjCache()
            self.width, self.height = save
            return

        obj = globals.ObjectDefinitions[self.tileset][self.type]
        if (obj.width, obj.height) != (1, 1) or obj.randByte & 0xF < 2:
            # cannot randomise -> exit
            save = (self.width, self.height)
            self.width, self.height = width, height
            self.updateObjCache()
            self.width, self.height = save
            return

        if width == self.width and height == self.height:
            return

        if height < self.height:
            self.objdata = self.objdata[:height]

        elif height > self.height:
            self.objdata += RenderObject(self.tileset, self.type, self.width, height - self.height)
            self.randomise(0, self.height, self.width, height - self.height)

        if width < self.width:
            for y in range(len(self.objdata)):
                self.objdata[y] = self.objdata[y][:width]

        elif width > self.width:
            new = RenderObject(self.tileset, self.type, width - self.width, height)
            for y in range(len(self.objdata)):
                self.objdata[y] += new[y]

            self.randomise(self.width, 0, width - self.width, height)

        self.UpdateSearchDatabase()

    def UpdateRects(self):
        """
        Recreates the bounding and selection rects
        """
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0, 0, globals.TileWidth * self.width, globals.TileWidth * self.height)
        self.SelectionRect = QtCore.QRectF(0, 0, (globals.TileWidth * self.width) - 1, (globals.TileWidth * self.height) - 1)

        GrabberSide = 4 * (globals.TileWidth / 15)
        self.GrabberRectTL = QtCore.QRectF(0, 0, GrabberSide, GrabberSide)
        self.GrabberRectTR = QtCore.QRectF((globals.TileWidth * self.width) - GrabberSide, 0, GrabberSide, GrabberSide)
        self.GrabberRectBL = QtCore.QRectF(0, (globals.TileWidth * self.height) - GrabberSide, GrabberSide, GrabberSide)
        self.GrabberRectBR = QtCore.QRectF((globals.TileWidth * self.width) - GrabberSide, (globals.TileWidth * self.height) - GrabberSide, GrabberSide, GrabberSide)
        self.GrabberRectMT = QtCore.QRectF(GrabberSide, 0, (globals.TileWidth * self.width) - GrabberSide * 2, GrabberSide)
        self.GrabberRectML = QtCore.QRectF(0, GrabberSide, GrabberSide, (globals.TileWidth * self.height) - GrabberSide * 2)
        self.GrabberRectMB = QtCore.QRectF(GrabberSide, (globals.TileWidth * self.height) - GrabberSide, (globals.TileWidth * self.width) - GrabberSide * 2, GrabberSide)
        self.GrabberRectMR = QtCore.QRectF((globals.TileWidth * self.width) - GrabberSide, GrabberSide, GrabberSide, (globals.TileWidth * self.height) - GrabberSide * 2)

        DrawGrabberSide = 4 * (globals.TileWidth / 20)
        self.DrawGrabberRectTL = QtCore.QRectF(0, 0, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectTR = QtCore.QRectF((globals.TileWidth * self.width) - DrawGrabberSide, 0, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectBL = QtCore.QRectF(0, (globals.TileWidth * self.height) - DrawGrabberSide, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectBR = QtCore.QRectF((globals.TileWidth * self.width) - DrawGrabberSide, (globals.TileWidth * self.height) - DrawGrabberSide, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectMT = QtCore.QRectF(((globals.TileWidth * self.width) - DrawGrabberSide) / 2, 0, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectML = QtCore.QRectF(0, ((globals.TileWidth * self.height) - DrawGrabberSide) / 2, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectMB = QtCore.QRectF(((globals.TileWidth * self.width) - DrawGrabberSide) / 2, (globals.TileWidth * self.height) - DrawGrabberSide, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectMR = QtCore.QRectF((globals.TileWidth * self.width) - DrawGrabberSide, ((globals.TileWidth * self.height) - DrawGrabberSide) / 2, DrawGrabberSide, DrawGrabberSide)

        self.LevelRect = QtCore.QRectF(self.objx, self.objy, self.width, self.height)

    def itemChange(self, change, value):
        """
        Makes sure positions don't go out of bounds and updates them as necessary
        """

        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            scene = self.scene()
            if scene is None: return value

            # snap to 24x24
            newpos = value
            newpos.setX(int((newpos.x() + globals.TileWidth / 2) / globals.TileWidth) * globals.TileWidth)
            newpos.setY(int((newpos.y() + globals.TileWidth / 2) / globals.TileWidth) * globals.TileWidth)
            x = newpos.x()
            y = newpos.y()

            # don't let it get out of the boundaries
            if x < 0: newpos.setX(0)
            if x > globals.TileWidth * 1023: newpos.setX(globals.TileWidth * 1023)
            if y < 0: newpos.setY(0)
            if y > globals.TileWidth * 511: newpos.setY(globals.TileWidth * 511)

            # update the data
            x = int(newpos.x() / globals.TileWidth)
            y = int(newpos.y() / globals.TileWidth)
            if x != self.objx or y != self.objy:
                self.LevelRect.moveTo(x, y)

                oldx = self.objx
                oldy = self.objy
                self.objx = x
                self.objy = y
                self.UpdateSearchDatabase()
                if self.positionChanged is not None:
                    self.positionChanged(self, oldx, oldy, x, y)

                SetDirty()

                # updRect = QtCore.QRectF(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())
                # scene.invalidate(updRect)

                scene.invalidate(self.x(), self.y(), self.width * globals.TileWidth, self.height * globals.TileWidth,
                                 QtWidgets.QGraphicsScene.BackgroundLayer)
                # scene.invalidate(newpos.x(), newpos.y(), self.width * globals.TileWidth, self.height * globals.TileWidth, QtWidgets.QGraphicsScene.BackgroundLayer)

            return newpos

        return QtWidgets.QGraphicsItem.itemChange(self, change, value)

    def paint(self, painter, option, widget):
        """
        Paints the object
        """
        if self.isSelected():
            painter.setPen(QtGui.QPen(globals.theme.color('object_lines_s'), 1, Qt.DotLine))
            painter.drawRect(self.SelectionRect)
            painter.fillRect(self.SelectionRect, globals.theme.color('object_fill_s'))

            painter.fillRect(self.DrawGrabberRectTL, globals.theme.color('object_lines_s'))
            painter.fillRect(self.DrawGrabberRectTR, globals.theme.color('object_lines_s'))
            painter.fillRect(self.DrawGrabberRectBL, globals.theme.color('object_lines_s'))
            painter.fillRect(self.DrawGrabberRectBR, globals.theme.color('object_lines_s'))
            painter.fillRect(self.DrawGrabberRectMT, globals.theme.color('object_lines_s'))
            painter.fillRect(self.DrawGrabberRectML, globals.theme.color('object_lines_s'))
            painter.fillRect(self.DrawGrabberRectMB, globals.theme.color('object_lines_s'))
            painter.fillRect(self.DrawGrabberRectMR, globals.theme.color('object_lines_s'))

    def mousePressEvent(self, event):
        """
        Overrides mouse pressing events if needed for resizing
        """
        if event.button() == Qt.LeftButton:
            if QtWidgets.QApplication.keyboardModifiers() == Qt.ControlModifier:
                layer = globals.Area.layers[self.layer]

                if len(layer) == 0:
                    newZ = (2 - self.layer) * 8192

                else:
                    newZ = layer[-1].zValue() + 1

                currentZ = self.zValue()
                self.setZValue(newZ)  # swap the Z values so it doesn't look like the cloned item is the old one

                newitem = ObjectItem(self.tileset, self.type, self.layer, self.objx, self.objy, self.width, self.height,
                                     currentZ, self.data)

                layer.append(newitem)
                globals.mainWindow.scene.addItem(newitem)
                globals.mainWindow.scene.clearSelection()
                self.setSelected(True)

                SetDirty()

        self.TLGrabbed = self.GrabberRectTL.contains(event.pos())
        self.TRGrabbed = self.GrabberRectTR.contains(event.pos())
        self.BLGrabbed = self.GrabberRectBL.contains(event.pos())
        self.BRGrabbed = self.GrabberRectBR.contains(event.pos())
        self.MTGrabbed = self.GrabberRectMT.contains(event.pos())
        self.MLGrabbed = self.GrabberRectML.contains(event.pos())
        self.MBGrabbed = self.GrabberRectMB.contains(event.pos())
        self.MRGrabbed = self.GrabberRectMR.contains(event.pos())

        if self.isSelected() and (
            self.TLGrabbed
            or self.TRGrabbed
            or self.BLGrabbed
            or self.BRGrabbed
            or self.MTGrabbed
            or self.MLGrabbed
            or self.MBGrabbed
            or self.MRGrabbed
        ):
            # start dragging
            self.dragging = True
            self.dragstartx = int((event.pos().x() - globals.TileWidth / 2) / globals.TileWidth)
            self.dragstarty = int((event.pos().y() - globals.TileWidth / 2) / globals.TileWidth)
            self.objsDragging = {}

            for selitem in globals.mainWindow.scene.selectedItems():
                if not isinstance(selitem, ObjectItem):
                    continue

                self.objsDragging[selitem] = [selitem.width, selitem.height]

            event.accept()

        else:
            LevelEditorItem.mousePressEvent(self, event)
            self.dragging = False
            self.objsDragging = {}

        self.UpdateTooltip()

    def UpdateObj(self, oldX, oldY):
        """
        Updates the object if the width/height/position has been changed
        """
        # Save the new dimensions for later
        newWidth = self.width
        newHeight = self.height

        # Replace the dimensions with the old ones
        self.width = int(self.BoundingRect.width() / globals.TileWidth)
        self.height = int(self.BoundingRect.height() / globals.TileWidth)

        # Update the object data
        self.updateObjCacheWH(newWidth, newHeight)

        # Update the dimensions
        self.width = newWidth
        self.height = newHeight

        # Update the object's Rects and scene
        oldrect = self.BoundingRect
        oldrect.translate(oldX * globals.TileWidth, oldY * globals.TileWidth)
        newrect = QtCore.QRectF(self.x(), self.y(), self.width * globals.TileWidth, self.height * globals.TileWidth)
        updaterect = oldrect.united(newrect)

        self.UpdateRects()
        self.scene().update(updaterect)

        globals.mainWindow.levelOverview.update()

    def mouseMoveEvent(self, event):
        """
        Overrides mouse movement events if needed for resizing
        """
        if event.buttons() != Qt.NoButton and self.dragging:
            # resize it
            dsx = self.dragstartx
            dsy = self.dragstarty

            clickedx = int((event.pos().x() - globals.TileWidth / 2) / globals.TileWidth)
            clickedy = int((event.pos().y() - globals.TileWidth / 2) / globals.TileWidth)

            cx = self.objx
            cy = self.objy

            if self.TLGrabbed:
                if clickedx != dsx or clickedy != dsy:
                    for obj in self.objsDragging:
                        oldWidth = self.objsDragging[obj][0] + 0
                        oldHeight = self.objsDragging[obj][1] + 0

                        self.objsDragging[obj][0] -= clickedx - dsx
                        self.objsDragging[obj][1] -= clickedy - dsy

                        newX = obj.objx + clickedx - dsx
                        newY = obj.objy + clickedy - dsy

                        newWidth = self.objsDragging[obj][0]
                        newHeight = self.objsDragging[obj][1]

                        if newWidth < 1:
                            newWidth = 1

                        if newHeight < 1:
                            newHeight = 1

                        if newX >= 0 and newX + newWidth == obj.objx + obj.width:
                            obj.objx = newX
                            obj.width = newWidth

                        else:
                            self.objsDragging[obj][0] = oldWidth

                        if newY >= 0 and newY + newHeight == obj.objy + obj.height:
                            obj.objy = newY
                            obj.height = newHeight

                        else:
                            self.objsDragging[obj][1] = oldHeight

                        obj.setPos(obj.objx * globals.TileWidth, obj.objy * globals.TileWidth)
                        obj.UpdateObj(cx, cy)

                    SetDirty()

            elif self.TRGrabbed:
                if clickedx < 0:
                    clickedx = 0

                if clickedx != dsx or clickedy != dsy:
                    self.dragstartx= clickedx

                    for obj in self.objsDragging:
                        oldHeight = self.objsDragging[obj][1] + 0

                        self.objsDragging[obj][0] += clickedx - dsx
                        self.objsDragging[obj][1] -= clickedy - dsy

                        newY = obj.objy + clickedy - dsy

                        newWidth = self.objsDragging[obj][0]
                        newHeight = self.objsDragging[obj][1]

                        if newWidth < 1:
                            newWidth = 1

                        if newHeight < 1:
                            newHeight = 1

                        if newY >= 0 and newY + newHeight == obj.objy + obj.height:
                            obj.objy = newY
                            obj.height = newHeight

                        else:
                            self.objsDragging[obj][1] = oldHeight

                        obj.width = newWidth

                        obj.setPos(obj.objx * globals.TileWidth, obj.objy * globals.TileWidth)
                        obj.UpdateObj(cx, cy)

                    SetDirty()

            elif self.BLGrabbed:
                if clickedy < 0:
                    clickedy = 0

                if clickedx != dsx or clickedy != dsy:
                    self.dragstarty = clickedy

                    for obj in self.objsDragging:
                        oldWidth = self.objsDragging[obj][0] + 0

                        self.objsDragging[obj][0] -= clickedx - dsx
                        self.objsDragging[obj][1] += clickedy - dsy

                        newX = obj.objx + clickedx - dsx

                        newWidth = self.objsDragging[obj][0]
                        newHeight = self.objsDragging[obj][1]

                        if newWidth < 1:
                            newWidth = 1

                        if newHeight < 1:
                            newHeight = 1

                        if newX >= 0 and newX + newWidth == obj.objx + obj.width:
                            obj.objx = newX
                            obj.width = newWidth

                        else:
                            self.objsDragging[obj][0] = oldWidth

                        obj.height = newHeight

                        obj.setPos(obj.objx * globals.TileWidth, obj.objy * globals.TileWidth)
                        obj.UpdateObj(cx, cy)

                    SetDirty()

            elif self.BRGrabbed:
                if clickedx < 0: clickedx = 0
                if clickedy < 0: clickedy = 0

                if clickedx != dsx or clickedy != dsy:
                    self.dragstartx = clickedx
                    self.dragstarty = clickedy

                    for obj in self.objsDragging:
                        self.objsDragging[obj][0] += clickedx - dsx
                        self.objsDragging[obj][1] += clickedy - dsy

                        newWidth = self.objsDragging[obj][0]
                        newHeight = self.objsDragging[obj][1]

                        if newWidth < 1:
                            newWidth = 1

                        if newHeight < 1:
                            newHeight = 1

                        obj.width = newWidth
                        obj.height = newHeight

                        obj.UpdateObj(cx, cy)

                    SetDirty()

            elif self.MTGrabbed:
                if clickedy != dsy:
                    for obj in self.objsDragging:
                        oldHeight = self.objsDragging[obj][1] + 0

                        self.objsDragging[obj][1] -= clickedy - dsy

                        newY = obj.objy + clickedy - dsy

                        newHeight = self.objsDragging[obj][1]
                        if newHeight < 1:
                            newHeight = 1

                        if newY >= 0 and newY + newHeight == obj.objy + obj.height:
                            obj.objy = newY
                            obj.height = newHeight

                        else:
                            self.objsDragging[obj][1] = oldHeight

                        obj.setPos(obj.objx * globals.TileWidth, obj.objy * globals.TileWidth)
                        obj.UpdateObj(cx, cy)

                    SetDirty()

            elif self.MLGrabbed:
                if clickedx != dsx:
                    for obj in self.objsDragging:
                        oldWidth = self.objsDragging[obj][0] + 0

                        self.objsDragging[obj][0] -= clickedx - dsx

                        newX = obj.objx + clickedx - dsx

                        newWidth = self.objsDragging[obj][0]
                        if newWidth < 1:
                            newWidth = 1

                        if newX >= 0 and newX + newWidth == obj.objx + obj.width:
                            obj.objx = newX
                            obj.width = newWidth

                        else:
                            self.objsDragging[obj][0] = oldWidth

                        obj.setPos(obj.objx * globals.TileWidth, obj.objy * globals.TileWidth)
                        obj.UpdateObj(cx, cy)

                    SetDirty()

            elif self.MBGrabbed:
                if clickedy < 0:
                    clickedy = 0

                if clickedy != dsy:
                    self.dragstarty = clickedy

                    for obj in self.objsDragging:
                        self.objsDragging[obj][1] += clickedy - dsy

                        newHeight = self.objsDragging[obj][1]
                        if newHeight < 1:
                            newHeight = 1

                        obj.height = newHeight
                        obj.UpdateObj(cx, cy)

                    SetDirty()

            elif self.MRGrabbed:
                if clickedx < 0:
                    clickedx = 0

                if clickedx != dsx:
                    self.dragstartx = clickedx

                    for obj in self.objsDragging:
                        self.objsDragging[obj][0] += clickedx - dsx

                        newWidth = self.objsDragging[obj][0]
                        if newWidth < 1:
                            newWidth = 1

                        obj.width = newWidth
                        obj.UpdateObj(cx, cy)

                    SetDirty()

            event.accept()

        else:
            LevelEditorItem.mouseMoveEvent(self, event)

        self.UpdateTooltip()

    def mouseReleaseEvent(self, event):
        """
        Disables "dragging" when the mouse is released
        """
        self.dragging = False
        LevelEditorItem.mouseReleaseEvent(self, event)

    def delete(self):
        """
        Delete the object from the level
        """
        self.RemoveFromSearchDatabase()
        globals.Area.RemoveFromLayer(self)
        self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())


class ZoneItem(LevelEditorItem):
    """
    Level editor item that represents a zone
    """

    def __init__(self, a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p, bounding=None, bg=None, id=None):
        """
        Creates a zone with specific data
        """
        super().__init__()

        self.font = globals.NumberFont
        self.TitlePos = QtCore.QPointF(10, 10 + QtGui.QFontMetrics(self.font).height())

        self.objx = a
        self.objy = b
        self.width = c
        self.height = d
        self.modeldark = e
        self.terraindark = f
        self.id = g
        self.block3id = h
        self.cammode = i
        self.camzoom = j
        self.visibility = k
        self.block5id = l
        self.camtrack = m
        self.music = n
        self.sfxmod = o
        self.type = p
        self.UpdateRects()

        self.aux = set()

        if id is not None:
            self.id = id

        self.UpdateTitle()

        if bounding is not None:
            self.yupperbound = bounding[0]
            self.ylowerbound = bounding[1]
            self.yupperbound2 = bounding[2]
            self.ylowerbound2 = bounding[3]
            self.entryid = bounding[4]
            self.unknownbnf = bounding[5]
        else:
            self.yupperbound = 0
            self.ylowerbound = 0
            self.yupperbound2 = 0
            self.ylowerbound2 = 0
            self.entryid = 0
            self.unknownbnf = 0

        if bg is not None:
            self.background = bg

        else:
            self.background = (0, 0, 0, 0, to_bytes('Black', 16), 0)

        self.dragging = False
        self.dragstartx = -1
        self.dragstarty = -1

        globals.DirtyOverride += 1
        self.setPos(int(a * globals.TileWidth / 16), int(b * globals.TileWidth / 16))
        globals.DirtyOverride -= 1
        self.setZValue(50000)

    def UpdateTitle(self):
        """
        Updates the zone's title
        """
        self.title = globals.trans.string('Zones', 0, '[num]', self.id + 1)

    def UpdateRects(self):
        """
        Updates the zone's bounding rectangle
        """
        self.prepareGeometryChange()
        mult = globals.TileWidth / 16
        self.BoundingRect = QtCore.QRectF(0, 0, self.width * mult, self.height * mult)
        self.ScalingRect = QtCore.QRectF(self.objx * mult, self.objy * mult, self.width * mult, self.height * mult)
        self.ZoneRect = QtCore.QRectF(self.objx, self.objy, self.width, self.height)
        self.DrawRect = QtCore.QRectF(3, 3, int(self.width * mult) - 6, int(self.height * mult) - 6)

        GrabberSide = 4 * (globals.TileWidth / 15)
        self.GrabberRectTL = QtCore.QRectF(0, 0, GrabberSide, GrabberSide)
        self.GrabberRectTR = QtCore.QRectF(int(self.width * mult) - GrabberSide, 0, GrabberSide, GrabberSide)
        self.GrabberRectBL = QtCore.QRectF(0, int(self.height * mult) - GrabberSide, GrabberSide, GrabberSide)
        self.GrabberRectBR = QtCore.QRectF(int(self.width * mult) - GrabberSide, int(self.height * mult) - GrabberSide, GrabberSide, GrabberSide)
        self.GrabberRectMT = QtCore.QRectF(GrabberSide, 0, int(self.width * mult) - GrabberSide * 2, GrabberSide)
        self.GrabberRectML = QtCore.QRectF(0, GrabberSide, GrabberSide, int(self.height * mult) - GrabberSide * 2)
        self.GrabberRectMB = QtCore.QRectF(GrabberSide, int(self.height * mult) - GrabberSide, int(self.width * mult) - GrabberSide * 2, GrabberSide)
        self.GrabberRectMR = QtCore.QRectF(int(self.width * mult) - GrabberSide, GrabberSide, GrabberSide, int(self.height * mult) - GrabberSide * 2)

        DrawGrabberSide = 4 * (globals.TileWidth / 20)
        self.DrawGrabberRectTL = QtCore.QRectF(0, 0, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectTR = QtCore.QRectF(int(self.width * mult) - DrawGrabberSide, 0, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectBL = QtCore.QRectF(0, int(self.height * mult) - DrawGrabberSide, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectBR = QtCore.QRectF(int(self.width * mult) - DrawGrabberSide, int(self.height * mult) - DrawGrabberSide, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectMT = QtCore.QRectF((int(self.width * mult) - DrawGrabberSide) / 2, 0, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectML = QtCore.QRectF(0, (int(self.height * mult) - DrawGrabberSide) / 2, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectMB = QtCore.QRectF((int(self.width * mult) - DrawGrabberSide) / 2, int(self.height * mult) - DrawGrabberSide, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectMR = QtCore.QRectF(int(self.width * mult) - DrawGrabberSide, (int(self.height * mult) - DrawGrabberSide) / 2, DrawGrabberSide, DrawGrabberSide)

    def paint(self, painter, option, widget):
        """
        Paints the zone on screen
        """
        # painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Paint liquids/fog
        if globals.SpritesShown and globals.RealViewEnabled:
            zoneRect = QtCore.QRectF(self.objx * globals.TileWidth / 16, self.objy * globals.TileWidth / 16, self.width * globals.TileWidth / 16, self.height * globals.TileWidth / 16)
            viewRect = globals.mainWindow.view.mapToScene(globals.mainWindow.view.viewport().rect()).boundingRect()

            for sprite in globals.Area.sprites:
                if sprite.type in [88, 89, 90, 92, 198, 201]:
                    spriteZoneID = SLib.MapPositionToZoneID(globals.Area.zones, sprite.objx, sprite.objy)

                    if self.id == spriteZoneID:
                        sprite.ImageObj.realViewZone(painter, zoneRect, viewRect)

        # Now paint the borders
        painter.setPen(QtGui.QPen(globals.theme.color('zone_lines'), 3 * globals.TileWidth / 24))
        if (self.visibility >= 32) and globals.RealViewEnabled:
            painter.setBrush(QtGui.QBrush(globals.theme.color('zone_dark_fill')))
        painter.drawRect(self.DrawRect)

        # And text
        painter.setPen(QtGui.QPen(globals.theme.color('zone_text'), 3 * globals.TileWidth / 24))
        painter.setFont(self.font)
        painter.drawText(self.TitlePos, self.title)

        # And corners ("grabbers")
        GrabberColor = globals.theme.color('zone_corner')
        painter.fillRect(self.DrawGrabberRectTL, GrabberColor)
        painter.fillRect(self.DrawGrabberRectTR, GrabberColor)
        painter.fillRect(self.DrawGrabberRectBL, GrabberColor)
        painter.fillRect(self.DrawGrabberRectBR, GrabberColor)
        painter.fillRect(self.DrawGrabberRectMT, GrabberColor)
        painter.fillRect(self.DrawGrabberRectML, GrabberColor)
        painter.fillRect(self.DrawGrabberRectMB, GrabberColor)
        painter.fillRect(self.DrawGrabberRectMR, GrabberColor)

    def mousePressEvent(self, event):
        """
        Overrides mouse pressing events if needed for resizing
        """

        if self.GrabberRectTL.contains(event.pos()):
            # start dragging
            self.dragging = True
            self.dragcorner = 1

        elif self.GrabberRectTR.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 2

        elif self.GrabberRectBL.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 3

        elif self.GrabberRectBR.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 4

        elif self.GrabberRectMT.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 5

        elif self.GrabberRectML.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 6

        elif self.GrabberRectMB.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 7

        elif self.GrabberRectMR.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 8

        else:
            self.dragging = False

        if self.dragging:
            self.dragstartx = int(event.scenePos().x() / globals.TileWidth * 16)
            self.dragstarty = int(event.scenePos().y() / globals.TileWidth * 16)
            self.draginitialx1 = self.objx
            self.draginitialy1 = self.objy
            self.draginitialx2 = self.objx + self.width
            self.draginitialy2 = self.objy + self.height
            event.accept()
            
        else:
            LevelEditorItem.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        Overrides mouse movement events if needed for resizing
        """

        if event.buttons() != Qt.NoButton and self.dragging:
            # resize it
            clickedx = int(event.scenePos().x() / globals.TileWidth * 16)
            clickedy = int(event.scenePos().y() / globals.TileWidth * 16)

            x1 = self.draginitialx1
            y1 = self.draginitialy1
            x2 = self.draginitialx2
            y2 = self.draginitialy2

            oldx = self.x()
            oldy = self.y()
            oldw = self.width * globals.TileWidth / 16
            oldh = self.height * globals.TileWidth / 16

            deltax = clickedx - self.dragstartx
            deltay = clickedy - self.dragstarty

            MIN_X = 16
            MIN_Y = 16
            MIN_W = 192
            MIN_H = 144

            if self.dragcorner == 1: # TL
                x1 += deltax
                y1 += deltay
                if x1 < MIN_X: x1 = MIN_X
                if y1 < MIN_Y: y1 = MIN_Y
                if x2 - x1 < MIN_W: x1 = x2 - MIN_W
                if y2 - y1 < MIN_H: y1 = y2 - MIN_H

            elif self.dragcorner == 2: # TR
                x2 += deltax
                y1 += deltay
                if y1 < MIN_Y: y1 = MIN_Y
                if x2 - x1 < MIN_W: x2 = x1 + MIN_W
                if y2 - y1 < MIN_H: y1 = y2 - MIN_H

            elif self.dragcorner == 3: # BL
                x1 += deltax
                y2 += deltay
                if x1 < MIN_X: x1 = MIN_X
                if x2 - x1 < MIN_W: x1 = x2 - MIN_W
                if y2 - y1 < MIN_H: y2 = y1 + MIN_H

            elif self.dragcorner == 4: # BR
                x2 += deltax
                y2 += deltay
                if x2 - x1 < MIN_W: x2 = x1 + MIN_W
                if y2 - y1 < MIN_H: y2 = y1 + MIN_H

            elif self.dragcorner == 5: # MT
                y1 += deltay
                if y1 < MIN_Y: y1 = MIN_Y
                if y2 - y1 < MIN_H: y2 = y1 + MIN_H

            elif self.dragcorner == 6: # ML
                x1 += deltax
                if x1 < MIN_X: x1 = MIN_X
                if x2 - x1 < MIN_W: x2 = x1 + MIN_W

            elif self.dragcorner == 7: # MB
                y2 += deltay
                if y2 - y1 < MIN_H: y2 = y1 + MIN_H

            elif self.dragcorner == 8: # MR
                x2 += deltax
                if x2 - x1 < MIN_W: x2 = x1 + MIN_W

            if QtWidgets.QApplication.keyboardModifiers() != Qt.AltModifier:
                # Snap to 8x8 grid

                if self.dragcorner in [1, 3, 6]:
                    if x1 % 8 < 4:
                        x1 -= (x1 % 8)
                    else:
                        x1 += 8 - (x1 % 8)
                elif self.dragcorner not in [5, 7]:
                    if x2 % 8 < 4:
                        x2 -= (x2 % 8)
                    else:
                        x2 += 8 - (x2 % 8)

                if self.dragcorner in [1, 2, 5]:
                    if y1 % 8 < 4:
                        y1 -= (y1 % 8)
                    else:
                        y1 += 8 - (y1 % 8)
                elif self.dragcorner not in [6, 8]:
                    if y2 % 8 < 4:
                        y2 -= (y2 % 8)
                    else:
                        y2 += 8 - (y2 % 8)

            self.objx = x1
            self.objy = y1
            self.width = x2 - x1
            self.height = y2 - y1

            oldrect = QtCore.QRectF(oldx, oldy, oldw, oldh)
            newrect = QtCore.QRectF(self.x(), self.y(), self.width * globals.TileWidth / 16, self.height * globals.TileWidth / 16)
            updaterect = oldrect.united(newrect)
            updaterect.setTop(updaterect.top() - 3)
            updaterect.setLeft(updaterect.left() - 3)
            updaterect.setRight(updaterect.right() + 3)
            updaterect.setBottom(updaterect.bottom() + 3)

            self.UpdateRects()
            self.setPos(int(self.objx * globals.TileWidth / 16), int(self.objy * globals.TileWidth / 16))
            self.scene().update(updaterect)

            globals.mainWindow.levelOverview.update()

            # Call the zoneRepositioned function of all
            # the sprite auxs for this zone
            for a in self.aux:
                a.zoneRepositioned()

            SetDirty()

            event.accept()
        else:
            LevelEditorItem.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Disables "dragging" when the mouse is released
        """
        self.dragging = False
        LevelEditorItem.mouseReleaseEvent(self, event)

    def itemChange(self, change, value):
        """
        Avoids snapping for zones
        """
        return QtWidgets.QGraphicsItem.itemChange(self, change, value)


class LocationItem(LevelEditorItem):
    """
    Level editor item that represents a sprite location
    """
    sizeChanged = None  # Callback: sizeChanged(SpriteItem obj, int width, int height)

    def __init__(self, x, y, width, height, id):
        """
        Creates a location with specific data
        """
        super().__init__()

        self.font = globals.NumberFont
        self.TitlePos = QtCore.QPointF(globals.TileWidth / 4, globals.TileWidth / 4)
        self.objx = x
        self.objy = y
        self.width = width
        self.height = height
        self.id = id
        self.listitem = None
        self.UpdateTitle()
        self.UpdateRects()

        self.setFlag(self.ItemIsMovable, not globals.LocationsFrozen)
        self.setFlag(self.ItemIsSelectable, not globals.LocationsFrozen)

        globals.DirtyOverride += 1
        self.setPos(int(x * globals.TileWidth / 16), int(y * globals.TileWidth / 16))
        globals.DirtyOverride -= 1

        self.dragging = False
        self.setZValue(24000)

    def ListString(self):
        """
        Returns a string that can be used to describe the location in a list
        """
        return globals.trans.string('Locations', 2, '[id]', self.id, '[width]', int(self.width), '[height]', int(self.height),
                            '[x]', int(self.objx), '[y]', int(self.objy))

    def UpdateTitle(self):
        """
        Updates the location's title
        """
        self.title = globals.trans.string('Locations', 0, '[id]', self.id)
        self.UpdateListItem()

    def __lt__(self, other):
        return self.id < other.id

    def UpdateRects(self):
        """
        Updates the location's bounding rectangle
        """
        self.prepareGeometryChange()
        if self.width == 0: self.width == 8
        if self.height == 0: self.height == 8
        mult = globals.TileWidth / 16

        self.BoundingRect = QtCore.QRectF(0, 0, self.width * mult, self.height * mult)
        self.SelectionRect = QtCore.QRectF(self.objx * mult, self.objy * mult, self.width * mult, self.height * mult)
        self.ZoneRect = QtCore.QRectF(self.objx, self.objy, self.width, self.height)
        self.DrawRect = QtCore.QRectF(1, 1, (self.width * mult) - 2, (self.height * mult) - 2)

        GrabberSide = 4 * (globals.TileWidth / 15)
        self.GrabberRectTL = QtCore.QRectF(0, 0, GrabberSide, GrabberSide)
        self.GrabberRectTR = QtCore.QRectF(int(self.width * mult) - GrabberSide, 0, GrabberSide, GrabberSide)
        self.GrabberRectBL = QtCore.QRectF(0, int(self.height * mult) - GrabberSide, GrabberSide, GrabberSide)
        self.GrabberRectBR = QtCore.QRectF(int(self.width * mult) - GrabberSide, int(self.height * mult) - GrabberSide, GrabberSide, GrabberSide)
        self.GrabberRectMT = QtCore.QRectF(GrabberSide, 0, int(self.width * mult) - GrabberSide * 2, GrabberSide)
        self.GrabberRectML = QtCore.QRectF(0, GrabberSide, GrabberSide, int(self.height * mult) - GrabberSide * 2)
        self.GrabberRectMB = QtCore.QRectF(GrabberSide, int(self.height * mult) - GrabberSide, int(self.width * mult) - GrabberSide * 2, GrabberSide)
        self.GrabberRectMR = QtCore.QRectF(int(self.width * mult) - GrabberSide, GrabberSide, GrabberSide, int(self.height * mult) - GrabberSide * 2)

        DrawGrabberSide = 4 * (globals.TileWidth / 20)
        self.DrawGrabberRectTL = QtCore.QRectF(0, 0, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectTR = QtCore.QRectF(int(self.width * mult) - DrawGrabberSide, 0, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectBL = QtCore.QRectF(0, int(self.height * mult) - DrawGrabberSide, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectBR = QtCore.QRectF(int(self.width * mult) - DrawGrabberSide, int(self.height * mult) - DrawGrabberSide, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectMT = QtCore.QRectF((int(self.width * mult) - DrawGrabberSide) / 2, 0, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectML = QtCore.QRectF(0, (int(self.height * mult) - DrawGrabberSide) / 2, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectMB = QtCore.QRectF((int(self.width * mult) - DrawGrabberSide) / 2, int(self.height * mult) - DrawGrabberSide, DrawGrabberSide, DrawGrabberSide)
        self.DrawGrabberRectMR = QtCore.QRectF(int(self.width * mult) - DrawGrabberSide, (int(self.height * mult) - DrawGrabberSide) / 2, DrawGrabberSide, DrawGrabberSide)

        self.UpdateListItem()

    def paint(self, painter, option, widget):
        """
        Paints the location on screen
        """
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Draw the purple rectangle
        if not self.isSelected():
            painter.setBrush(QtGui.QBrush(globals.theme.color('location_fill')))
            painter.setPen(QtGui.QPen(globals.theme.color('location_lines'), globals.TileWidth / 24))
        else:
            painter.setBrush(QtGui.QBrush(globals.theme.color('location_fill_s')))
            painter.setPen(QtGui.QPen(globals.theme.color('location_lines_s'), globals.TileWidth / 24, Qt.DotLine))
        painter.drawRect(self.DrawRect)

        # Draw the ID
        painter.setPen(QtGui.QPen(globals.theme.color('location_text')))
        painter.setFont(self.font)
        painter.drawText(QtCore.QRectF(0, 0, globals.TileWidth / 2, globals.TileWidth / 2), Qt.AlignCenter, self.title)

        # Draw the resizer rectangles, if selected
        if self.isSelected():
            GrabberColor = globals.theme.color('location_lines_s')
            painter.fillRect(self.DrawGrabberRectTL, GrabberColor)
            painter.fillRect(self.DrawGrabberRectTR, GrabberColor)
            painter.fillRect(self.DrawGrabberRectBL, GrabberColor)
            painter.fillRect(self.DrawGrabberRectBR, GrabberColor)
            painter.fillRect(self.DrawGrabberRectMT, GrabberColor)
            painter.fillRect(self.DrawGrabberRectML, GrabberColor)
            painter.fillRect(self.DrawGrabberRectMB, GrabberColor)
            painter.fillRect(self.DrawGrabberRectMR, GrabberColor)

    def mousePressEvent(self, event):
        """
        Overrides mouse pressing events if needed for resizing
        """

        if self.isSelected() and self.GrabberRectTL.contains(event.pos()):
            # start dragging
            self.dragging = True
            self.dragcorner = 1

        elif self.isSelected() and self.GrabberRectTR.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 2

        elif self.isSelected() and self.GrabberRectBL.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 3

        elif self.isSelected() and self.GrabberRectBR.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 4

        elif self.isSelected() and self.GrabberRectMT.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 5

        elif self.isSelected() and self.GrabberRectML.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 6

        elif self.isSelected() and self.GrabberRectMB.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 7

        elif self.isSelected() and self.GrabberRectMR.contains(event.pos()):
            self.dragging = True
            self.dragcorner = 8

        else:
            self.dragging = False

        if self.dragging:
            self.dragstartx = int(event.scenePos().x() / globals.TileWidth * 16)
            self.dragstarty = int(event.scenePos().y() / globals.TileWidth * 16)
            self.draginitialx1 = self.objx
            self.draginitialy1 = self.objy
            self.draginitialx2 = self.objx + self.width
            self.draginitialy2 = self.objy + self.height
            event.accept()
            
        else:
            LevelEditorItem.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        Overrides mouse movement events if needed for resizing
        """

        if event.buttons() != Qt.NoButton and self.dragging:
            # resize it
            clickedx = int(event.scenePos().x() / globals.TileWidth * 16)
            clickedy = int(event.scenePos().y() / globals.TileWidth * 16)

            x1 = self.draginitialx1
            y1 = self.draginitialy1
            x2 = self.draginitialx2
            y2 = self.draginitialy2

            oldx = self.x()
            oldy = self.y()
            oldw = self.width * globals.TileWidth / 16
            oldh = self.height * globals.TileWidth / 16

            deltax = clickedx - self.dragstartx
            deltay = clickedy - self.dragstarty

            MIN_X = 0
            MIN_Y = 0
            MIN_W = 8
            MIN_H = 8

            if self.dragcorner == 1: # TL
                x1 += deltax
                y1 += deltay
                if x1 < MIN_X: x1 = MIN_X
                if y1 < MIN_Y: y1 = MIN_Y
                if x2 - x1 < MIN_W: x1 = x2 - MIN_W
                if y2 - y1 < MIN_H: y1 = y2 - MIN_H

            elif self.dragcorner == 2: # TR
                x2 += deltax
                y1 += deltay
                if y1 < MIN_Y: y1 = MIN_Y
                if x2 - x1 < MIN_W: x2 = x1 + MIN_W
                if y2 - y1 < MIN_H: y1 = y2 - MIN_H

            elif self.dragcorner == 3: # BL
                x1 += deltax
                y2 += deltay
                if x1 < MIN_X: x1 = MIN_X
                if x2 - x1 < MIN_W: x1 = x2 - MIN_W
                if y2 - y1 < MIN_H: y2 = y1 + MIN_H

            elif self.dragcorner == 4: # BR
                x2 += deltax
                y2 += deltay
                if x2 - x1 < MIN_W: x2 = x1 + MIN_W
                if y2 - y1 < MIN_H: y2 = y1 + MIN_H

            elif self.dragcorner == 5: # MT
                y1 += deltay
                if y1 < MIN_Y: y1 = MIN_Y
                if y2 - y1 < MIN_H: y2 = y1 + MIN_H

            elif self.dragcorner == 6: # ML
                x1 += deltax
                if x1 < MIN_X: x1 = MIN_X
                if x2 - x1 < MIN_W: x2 = x1 + MIN_W

            elif self.dragcorner == 7: # MB
                y2 += deltay
                if y2 - y1 < MIN_H: y2 = y1 + MIN_H

            elif self.dragcorner == 8: # MR
                x2 += deltax
                if x2 - x1 < MIN_W: x2 = x1 + MIN_W

            if QtWidgets.QApplication.keyboardModifiers() != Qt.AltModifier:
                # Snap to 8x8 grid

                if self.dragcorner in [1, 3, 6]:
                    if x1 % 8 < 4:
                        x1 -= (x1 % 8)
                    else:
                        x1 += 8 - (x1 % 8)
                elif self.dragcorner not in [5, 7]:
                    if x2 % 8 < 4:
                        x2 -= (x2 % 8)
                    else:
                        x2 += 8 - (x2 % 8)

                if self.dragcorner in [1, 2, 5]:
                    if y1 % 8 < 4:
                        y1 -= (y1 % 8)
                    else:
                        y1 += 8 - (y1 % 8)
                elif self.dragcorner not in [6, 8]:
                    if y2 % 8 < 4:
                        y2 -= (y2 % 8)
                    else:
                        y2 += 8 - (y2 % 8)

            self.objx = x1
            self.objy = y1
            self.width = x2 - x1
            self.height = y2 - y1

            oldrect = QtCore.QRectF(oldx, oldy, oldw, oldh)
            newrect = QtCore.QRectF(self.x(), self.y(), self.width * globals.TileWidth / 16, self.height * globals.TileWidth / 16)
            updaterect = oldrect.united(newrect)
            updaterect.setTop(updaterect.top() - 3)
            updaterect.setLeft(updaterect.left() - 3)
            updaterect.setRight(updaterect.right() + 3)
            updaterect.setBottom(updaterect.bottom() + 3)

            self.UpdateRects()
            self.setPos(int(self.objx * globals.TileWidth / 16), int(self.objy * globals.TileWidth / 16))
            self.scene().update(updaterect)

            globals.mainWindow.levelOverview.update()
            SetDirty()

            if self.sizeChanged is not None:
                self.sizeChanged(self, self.width, self.height)

            event.accept()
        else:
            LevelEditorItem.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Disables "dragging" when the mouse is released
        """
        self.dragging = False
        LevelEditorItem.mouseReleaseEvent(self, event)

    def delete(self):
        """
        Delete the location from the level
        """
        loclist = globals.mainWindow.locationList
        globals.mainWindow.UpdateFlag = True
        loclist.takeItem(loclist.row(self.listitem))
        globals.mainWindow.UpdateFlag = False
        loclist.selectionModel().clearSelection()
        globals.Area.locations.remove(self)
        self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())


class SpriteItem(LevelEditorItem):
    """
    Level editor item that represents a sprite
    """
    BoundingRect = QtCore.QRectF(0, 0, globals.TileWidth, globals.TileWidth)
    SelectionRect = QtCore.QRectF(0, 0, globals.TileWidth - 1, globals.TileWidth - 1)

    def __init__(self, type, x, y, data, layer=0, initialState=0):
        """
        Creates a sprite with specific data
        """
        super().__init__()
        self.setZValue(26000)

        self.font = globals.NumberFont
        self.type = type
        self.objx = x
        self.objy = y
        self.spritedata = data
        self.layer = layer
        self.initialState = initialState
        self.listitem = None
        self.LevelRect = QtCore.QRectF(self.objx / 16, self.objy / 16, globals.TileWidth / 16, globals.TileWidth / 16)
        self.ChangingPos = False

        SLib.SpriteImage.loadImages()
        self.ImageObj = SLib.SpriteImage(self)

        try:
            sname = globals.Sprites[type].name
            self.name = sname
        except:
            self.name = 'UNKNOWN'

        self.InitializeSprite()

        self.setFlag(self.ItemIsMovable, not globals.SpritesFrozen)
        self.setFlag(self.ItemIsSelectable, not globals.SpritesFrozen)

        globals.DirtyOverride += 1
        if globals.SpriteImagesShown:
            self.setPos(
                int((self.objx + self.ImageObj.xOffset) * globals.TileWidth / 16),
                int((self.objy + self.ImageObj.yOffset) * globals.TileWidth / 16),
            )
        else:
            self.setPos(
                int(self.objx * globals.TileWidth / 16),
                int(self.objy * globals.TileWidth / 16),
            )
        globals.DirtyOverride -= 1

    def SetType(self, type):
        """
        Sets the type of the sprite
        """
        self.type = type
        self.InitializeSprite()

    def ListString(self):
        """
        Returns a string that can be used to describe the sprite in a list
        """
        baseString = globals.trans.string('Sprites', 1, '[name]', self.name, '[x]', self.objx, '[y]', self.objy)

        SpritesThatActivateAnEvent = set(globals.SpriteListData[0])
        SpritesThatActivateAnEventNyb0 = set(globals.SpriteListData[1])
        SpritesTriggeredByAnEventNyb1 = set(globals.SpriteListData[2])
        SpritesTriggeredByAnEventNyb0 = set(globals.SpriteListData[3])
        StarCoinNumbers = set(globals.SpriteListData[4])
        SpritesWithSetIDs = set(globals.SpriteListData[5])
        SpritesWithMovementIDsNyb2 = set(globals.SpriteListData[6])
        SpritesWithMovementIDsNyb3 = set(globals.SpriteListData[7])
        SpritesWithMovementIDsNyb5 = set(globals.SpriteListData[8])
        SpritesWithRotationIDs = set(globals.SpriteListData[9])
        SpritesWithLocationIDsNyb5 = set(globals.SpriteListData[10])
        SpritesWithLocationIDsNyb5and0xF = set(globals.SpriteListData[11])
        SpritesWithLocationIDsNyb4 = set(globals.SpriteListData[12])
        AndController = set(globals.SpriteListData[13])
        OrController = set(globals.SpriteListData[14])
        MultiChainer = set(globals.SpriteListData[15])
        Random = set(globals.SpriteListData[16])
        Clam = set(globals.SpriteListData[17])
        Coin = set(globals.SpriteListData[18])
        MushroomScrewPlatforms = set(globals.SpriteListData[19])
        SpritesWithMovementIDsNyb5Type2 = set(globals.SpriteListData[20])
        BowserFireballArea = set(globals.SpriteListData[21])
        CheepCheepArea = set(globals.SpriteListData[22])
        PoltergeistItem = set(globals.SpriteListData[23])

        # Triggered by an Event
        if self.type in SpritesTriggeredByAnEventNyb1 and self.spritedata[1] != '\0':
            baseString += globals.trans.string('Sprites', 2, '[event]', self.spritedata[1])
        elif self.type in SpritesTriggeredByAnEventNyb0 and self.spritedata[0] != '\0':
            baseString += globals.trans.string('Sprites', 2, '[event]', self.spritedata[0])
        elif self.type in AndController:
            baseString += globals.trans.string('Sprites', 3, '[event1]', self.spritedata[0], '[event2]', self.spritedata[2],
                                       '[event3]', self.spritedata[3], '[event4]', self.spritedata[4])
        elif self.type in OrController:
            baseString += globals.trans.string('Sprites', 4, '[event1]', self.spritedata[0], '[event2]', self.spritedata[2],
                                       '[event3]', self.spritedata[3], '[event4]', self.spritedata[4])

        # Activates an Event
        if (self.type in SpritesThatActivateAnEvent) and (self.spritedata[1] != '\0'):
            baseString += globals.trans.string('Sprites', 5, '[event]', self.spritedata[1])
        elif (self.type in SpritesThatActivateAnEventNyb0) and (self.spritedata[0] != '\0'):
            baseString += globals.trans.string('Sprites', 5, '[event]', self.spritedata[0])
        elif (self.type in MultiChainer):
            baseString += globals.trans.string('Sprites', 6, '[event1]', self.spritedata[0], '[event2]', self.spritedata[1])
        elif (self.type in Random):
            baseString += globals.trans.string('Sprites', 7, '[event1]', self.spritedata[0], '[event2]', self.spritedata[2],
                                       '[event3]', self.spritedata[3], '[event4]', self.spritedata[4])

        # Star Coin
        if (self.type in StarCoinNumbers):
            number = (self.spritedata[4] & 15) + 1
            baseString += globals.trans.string('Sprites', 8, '[num]', number)
        elif (self.type in Clam) and (self.spritedata[5] & 15) == 1:
            baseString += globals.trans.string('Sprites', 9)

        # Set ID
        if self.type in SpritesWithSetIDs:
            baseString += globals.trans.string('Sprites', 10, '[id]', self.spritedata[5] & 15)
        elif self.type in Coin and self.spritedata[2] != '\0':
            baseString += globals.trans.string('Sprites', 11, '[id]', self.spritedata[2])

        # Movement ID (Nybble 2)
        if self.type in SpritesWithMovementIDsNyb2 and self.spritedata[2] != '\0':
            baseString += globals.trans.string('Sprites', 12, '[id]', self.spritedata[2])
        elif self.type in MushroomScrewPlatforms and self.spritedata[2] >> 4 != '\0':
            baseString += globals.trans.string('Sprites', 12, '[id]', self.spritedata[2] >> 4)

        # Movement ID (Nybble 3)
        if self.type in SpritesWithMovementIDsNyb3 and self.spritedata[3] >> 4 != '\0':
            baseString += globals.trans.string('Sprites', 12, '[id]', (self.spritedata[3] >> 4))

        # Movement ID (Nybble 5)
        if self.type in SpritesWithMovementIDsNyb5 and self.spritedata[5] >> 4:
            baseString += globals.trans.string('Sprites', 12, '[id]', (self.spritedata[5] >> 4))
        elif self.type in SpritesWithMovementIDsNyb5Type2 and self.spritedata[5] != '\0':
            baseString += globals.trans.string('Sprites', 12, '[id]', self.spritedata[5])

        # Rotation ID
        if self.type in SpritesWithRotationIDs and self.spritedata[5] != '\0':
            baseString += globals.trans.string('Sprites', 13, '[id]', self.spritedata[5])

        # Location ID (Nybble 5)
        if self.type in SpritesWithLocationIDsNyb5 and self.spritedata[5] != '\0':
            baseString += globals.trans.string('Sprites', 14, '[id]', self.spritedata[5])
        elif self.type in SpritesWithLocationIDsNyb5and0xF and self.spritedata[5] & 15 != '\0':
            baseString += globals.trans.string('Sprites', 14, '[id]', self.spritedata[5] & 15)
        elif self.type in SpritesWithLocationIDsNyb4 and self.spritedata[4] != '\0':
            baseString += globals.trans.string('Sprites', 14, '[id]', self.spritedata[4])
        elif self.type in BowserFireballArea and self.spritedata[3] != '\0':
            baseString += globals.trans.string('Sprites', 14, '[id]', self.spritedata[3])
        elif self.type in CheepCheepArea:  # nybble 8-9
            if (((self.spritedata[3] & 0xF) << 4) | ((self.spritedata[4] & 0xF0) >> 4)) != '\0':
                baseString += globals.trans.string('Sprites', 14, '[id]',
                                           (((self.spritedata[3] & 0xF) << 4) | ((self.spritedata[4] & 0xF0) >> 4)))
        elif self.type in PoltergeistItem and (
            ((self.spritedata[4] & 0xF) << 4) | ((self.spritedata[5] & 0xF0) >> 4)) != '\0':  # nybble 10-11
            baseString += globals.trans.string('Sprites', 14, '[id]',
                                       (((self.spritedata[4] & 0xF) << 4) | ((self.spritedata[5] & 0xF0) >> 4)))

        # Add ')' to the end
        baseString += globals.trans.string('Sprites', 15)

        return baseString

    def __lt__(self, other):
        # Sort by objx, then objy, then sprite type
        score = lambda sprite: (sprite.objx * 100000 + sprite.objy) * 1000 + sprite.type

        return score(self) < score(other)

    def InitializeSprite(self):
        """
        Initializes sprite and creates any auxiliary objects needed
        """
        type = self.type

        if type > len(globals.Sprites): return

        self.name = globals.Sprites[type].name
        self.setToolTip(globals.trans.string('Sprites', 0, '[type]', self.type, '[name]', self.name))
        self.UpdateListItem()

        imgs = globals.gamedef.getImageClasses()
        if type in imgs:
            self.setImageObj(imgs[type])

    def setImageObj(self, obj):
        """
        Sets a new sprite image object for this SpriteItem
        """
        for auxObj in self.ImageObj.aux:
            if auxObj.scene() is None: continue
            auxObj.scene().removeItem(auxObj)

        self.setZValue(26000)
        self.resetTransform()

        if (self.type in globals.gamedef.getImageClasses()) and (self.type not in SLib.SpriteImagesLoaded):
            globals.gamedef.getImageClasses()[self.type].loadImages()
            SLib.SpriteImagesLoaded.add(self.type)

        self.ImageObj = obj(self)
        self.UpdateDynamicSizing()

    def UpdateDynamicSizing(self):
        """
        Updates the sizes for dynamically sized sprites
        """
        CurrentRect = QtCore.QRectF(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())
        CurrentAuxRects = []
        for auxObj in self.ImageObj.aux:
            CurrentAuxRects.append(QtCore.QRectF(
                auxObj.x() + self.x(),
                auxObj.y() + self.y(),
                auxObj.BoundingRect.width(),
                auxObj.BoundingRect.height(),
            ))

        self.ImageObj.dataChanged()

        if globals.SpriteImagesShown:
            self.UpdateRects()
            self.ChangingPos = True
            self.setPos(
                int((self.objx + self.ImageObj.xOffset) * globals.TileWidth / 16),
                int((self.objy + self.ImageObj.yOffset) * globals.TileWidth / 16),
            )
            self.ChangingPos = False

        if self.scene() is not None:
            self.scene().update(CurrentRect)
            self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())
            for auxUpdateRect in CurrentAuxRects:
                self.scene().update(auxUpdateRect)

    def UpdateRects(self):
        """
        Creates all the rectangles for the sprite
        """
        self.prepareGeometryChange()

        # Get rects
        imgRect = QtCore.QRectF(
            0, 0,
            self.ImageObj.width * globals.TileWidth / 16,
            self.ImageObj.height * globals.TileWidth / 16,
        )
        spriteboxRect = QtCore.QRectF(
            0, 0,
            self.ImageObj.spritebox.BoundingRect.width(),
            self.ImageObj.spritebox.BoundingRect.height(),
        )
        imgOffsetRect = imgRect.translated(
            (self.objx + self.ImageObj.xOffset) * (globals.TileWidth / 16),
            (self.objy + self.ImageObj.yOffset) * (globals.TileWidth / 16),
        )
        spriteboxOffsetRect = spriteboxRect.translated(
            (self.objx * (globals.TileWidth / 16)) + self.ImageObj.spritebox.BoundingRect.topLeft().x(),
            (self.objy * (globals.TileWidth / 16)) + self.ImageObj.spritebox.BoundingRect.topLeft().y(),
        )

        if globals.SpriteImagesShown:
            unitedRect = imgRect.united(spriteboxRect)
            unitedOffsetRect = imgOffsetRect.united(spriteboxOffsetRect)

            # SelectionRect: Used to determine the size of the
            # "this sprite is selected" translucent white box that
            # appears when a sprite with an image is selected.
            self.SelectionRect = QtCore.QRectF(
                0, 0,
                imgRect.width() - 1,
                imgRect.height() - 1,
            )

            # LevelRect: Used by the Level Overview to determine
            # the size and position of the sprite in the level.
            # Measured in blocks.
            self.LevelRect = QtCore.QRectF(
                unitedOffsetRect.topLeft().x() / globals.TileWidth,
                unitedOffsetRect.topLeft().y() / globals.TileWidth,
                unitedOffsetRect.width() / globals.TileWidth,
                unitedOffsetRect.height() / globals.TileWidth,
            )

            # BoundingRect: The sprite can only paint within
            # this area.
            self.BoundingRect = unitedRect.translated(
                self.ImageObj.spritebox.BoundingRect.topLeft().x(),
                self.ImageObj.spritebox.BoundingRect.topLeft().y(),
            )

        else:
            self.SelectionRect = QtCore.QRectF(0, 0, globals.TileWidth, globals.TileWidth)

            self.LevelRect = QtCore.QRectF(
                spriteboxOffsetRect.topLeft().x() / globals.TileWidth,
                spriteboxOffsetRect.topLeft().y() / globals.TileWidth,
                spriteboxOffsetRect.width() / globals.TileWidth,
                spriteboxOffsetRect.height() / globals.TileWidth,
            )

            # BoundingRect: The sprite can only paint within
            # this area.
            self.BoundingRect = spriteboxRect.translated(
                self.ImageObj.spritebox.BoundingRect.topLeft().x(),
                self.ImageObj.spritebox.BoundingRect.topLeft().y(),
            )

    def getFullRect(self):
        """
        Returns a rectangle that contains the sprite and all
        auxiliary objects.
        """
        self.UpdateRects()

        br = self.BoundingRect.translated(
            self.x(),
            self.y(),
        )
        for aux in self.ImageObj.aux:
            br = br.united(
                aux.BoundingRect.translated(
                    aux.x() + self.x(),
                    aux.y() + self.y(),
                )
            )

        return br

    def itemChange(self, change, value):
        """
        Makes sure positions don't go out of bounds and updates them as necessary
        """

        tileWidthMult = globals.TileWidth / 16
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            if self.scene() is None: return value
            if self.ChangingPos: return value

            if globals.SpriteImagesShown:
                xOffset, xOffsetAdjusted = self.ImageObj.xOffset, self.ImageObj.xOffset * tileWidthMult
                yOffset, yOffsetAdjusted = self.ImageObj.yOffset, self.ImageObj.yOffset * tileWidthMult
            else:
                xOffset, xOffsetAdjusted = 0, 0
                yOffset, yOffsetAdjusted = 0, 0

            # snap to 24x24
            newpos = value

            # snap even further if Shift isn't held
            # but -only- if globals.OverrideSnapping is off
            if not globals.OverrideSnapping:
                objectsSelected = any([isinstance(thing, ObjectItem) for thing in globals.mainWindow.CurrentSelection])
                if QtWidgets.QApplication.keyboardModifiers() == Qt.AltModifier:
                    # Alt is held; don't snap
                    newpos.setX((int((newpos.x() + 0.75) / tileWidthMult) * tileWidthMult))
                    newpos.setY((int((newpos.y() + 0.75) / tileWidthMult) * tileWidthMult))
                elif not objectsSelected and self.isSelected() and len(globals.mainWindow.CurrentSelection) > 1:
                    # Snap to 8x8, but with the dragoffsets
                    dragoffsetx, dragoffsety = int(self.dragoffsetx), int(self.dragoffsety)
                    if dragoffsetx < -(globals.TileWidth / 2): dragoffsetx += globals.TileWidth / 2
                    if dragoffsety < -(globals.TileWidth / 2): dragoffsety += globals.TileWidth / 2
                    if dragoffsetx == 0: dragoffsetx = -(globals.TileWidth / 2)
                    if dragoffsety == 0: dragoffsety = -(globals.TileWidth / 2)
                    referenceX = int(
                        (newpos.x() + (globals.TileWidth / 4) + (globals.TileWidth / 2) + dragoffsetx - xOffsetAdjusted) / (
                        globals.TileWidth / 2)) * (globals.TileWidth / 2)
                    referenceY = int(
                        (newpos.y() + (globals.TileWidth / 4) + (globals.TileWidth / 2) + dragoffsety - yOffsetAdjusted) / (
                        globals.TileWidth / 2)) * (globals.TileWidth / 2)
                    newpos.setX(referenceX - ((globals.TileWidth / 2) + dragoffsetx) + xOffsetAdjusted)
                    newpos.setY(referenceY - ((globals.TileWidth / 2) + dragoffsety) + yOffsetAdjusted)
                elif objectsSelected and self.isSelected():
                    # Objects are selected, too; move in sync by snapping to whole blocks
                    dragoffsetx, dragoffsety = int(self.dragoffsetx), int(self.dragoffsety)
                    if dragoffsetx == 0: dragoffsetx = -globals.TileWidth
                    if dragoffsety == 0: dragoffsety = -globals.TileWidth
                    referenceX = int((newpos.x() + (
                    globals.TileWidth / 2) + globals.TileWidth + dragoffsetx - xOffsetAdjusted) / globals.TileWidth) * globals.TileWidth
                    referenceY = int((newpos.y() + (
                    globals.TileWidth / 2) + globals.TileWidth + dragoffsety - yOffsetAdjusted) / globals.TileWidth) * globals.TileWidth
                    newpos.setX(referenceX - (globals.TileWidth + dragoffsetx) + xOffsetAdjusted)
                    newpos.setY(referenceY - (globals.TileWidth + dragoffsety) + yOffsetAdjusted)
                else:
                    # Snap to 8x8
                    newpos.setX(int(int((newpos.x() + (globals.TileWidth / 4) - xOffsetAdjusted) / (globals.TileWidth / 2)) * (
                    globals.TileWidth / 2) + xOffsetAdjusted))
                    newpos.setY(int(int((newpos.y() + (globals.TileWidth / 4) - yOffsetAdjusted) / (globals.TileWidth / 2)) * (
                    globals.TileWidth / 2) + yOffsetAdjusted))

            x = newpos.x()
            y = newpos.y()

            # don't let it get out of the boundaries
            if x < 0: newpos.setX(0)
            if x > 1023 * globals.TileWidth: newpos.setX(1023 * globals.TileWidth)
            if y < 0: newpos.setY(0)
            if y > 511 * globals.TileWidth: newpos.setY(511 * globals.TileWidth)

            # update the data
            x = int(newpos.x() / tileWidthMult - xOffset)
            y = int(newpos.y() / tileWidthMult - yOffset)

            if x != self.objx or y != self.objy:
                # oldrect = self.BoundingRect
                # oldrect.translate(self.objx*(globals.TileWidth/16), self.objy*(globals.TileWidth/16))
                updRect = QtCore.QRectF(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())
                # self.scene().update(updRect.united(oldrect))
                self.scene().update(updRect)

                self.LevelRect.moveTo((x + xOffset) / 16, (y + yOffset) / 16)

                for auxObj in self.ImageObj.aux:
                    auxUpdRect = QtCore.QRectF(
                        self.x() + auxObj.x(),
                        self.y() + auxObj.y(),
                        auxObj.BoundingRect.width(),
                        auxObj.BoundingRect.height(),
                    )
                    self.scene().update(auxUpdRect)

                self.scene().update(
                    self.x() + self.ImageObj.spritebox.BoundingRect.topLeft().x(),
                    self.y() + self.ImageObj.spritebox.BoundingRect.topLeft().y(),
                    self.ImageObj.spritebox.BoundingRect.width(),
                    self.ImageObj.spritebox.BoundingRect.height(),
                )

                oldx = self.objx
                oldy = self.objy
                self.objx = x
                self.objy = y
                if self.positionChanged is not None:
                    self.positionChanged(self, oldx, oldy, x, y)

                self.ImageObj.positionChanged()

                SetDirty()

            return newpos

        return QtWidgets.QGraphicsItem.itemChange(self, change, value)

    def setNewObjPos(self, newobjx, newobjy):
        """
        Sets a new position, through objx and objy
        """
        self.objx, self.objy = newobjx, newobjy
        if globals.SpriteImagesShown:
            self.setPos((newobjx + self.ImageObj.xOffset) * globals.TileWidth / 16, (newobjy + self.ImageObj.yOffset) * globals.TileWidth / 16)
        else:
            self.setPos(newobjx * globals.TileWidth / 16, newobjy * globals.TileWidth / 16)

    def mousePressEvent(self, event):
        """
        Overrides mouse pressing events if needed for cloning
        """
        if event.button() != Qt.LeftButton or QtWidgets.QApplication.keyboardModifiers() != Qt.ControlModifier:
            if not globals.SpriteImagesShown:
                oldpos = (self.objx, self.objy)

            LevelEditorItem.mousePressEvent(self, event)

            if not globals.SpriteImagesShown:
                self.setNewObjPos(oldpos[0], oldpos[1])

            return

        newitem = SpriteItem(self.type, self.objx, self.objy, self.spritedata)

        import widgets
        newitem.listitem = widgets.ListWidgetItem_SortsByOther(newitem, newitem.ListString())
        del widgets

        globals.mainWindow.spriteList.addItem(newitem.listitem)
        globals.Area.sprites.append(newitem)

        globals.mainWindow.scene.addItem(newitem)
        globals.mainWindow.scene.clearSelection()

        self.setSelected(True)

        newitem.UpdateListItem()
        SetDirty()

    def nearestZone(self, obj=False):
        """
        Calls a modified MapPositionToZoneID (if obj = True, it returns the actual ZoneItem object)
        """
        if not hasattr(globals.Area, 'zones'):
            return None

        id = SLib.MapPositionToZoneID(globals.Area.zones, self.objx, self.objy, True)

        if obj:
            for z in globals.Area.zones:
                if z.id == id:
                    return z
        else:
            return id

    def updateScene(self):
        """
        Calls self.scene().update()
        """
        # Some of the more advanced painters need to update the whole scene
        # and this is a convenient way to do it:
        # self.parent.updateScene()
        if self.scene() is not None: self.scene().update()

    def paint(self, painter, option=None, widget=None, overrideGlobals=False):
        """
        Paints the sprite
        """

        # Setup stuff
        if option is not None:
            painter.setClipRect(option.exposedRect)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Turn aux things on or off
        for aux in self.ImageObj.aux:
            aux.setVisible(globals.SpriteImagesShown)

        # Default spritebox
        drawSpritebox = True
        spriteboxRect = QtCore.QRectF(1, 1, globals.TileWidth - 2, globals.TileWidth - 2)

        if globals.SpriteImagesShown or overrideGlobals:
            self.ImageObj.paint(painter)

            drawSpritebox = self.ImageObj.spritebox.shown

            # Draw the selected-sprite-image overlay box
            if self.isSelected() and (not drawSpritebox or self.ImageObj.size != (16, 16)):
                painter.setPen(QtGui.QPen(globals.theme.color('sprite_lines_s'), 1, Qt.DotLine))
                painter.drawRect(self.SelectionRect)
                painter.fillRect(self.SelectionRect, globals.theme.color('sprite_fill_s'))

            # Determine the spritebox position
            if drawSpritebox:
                spriteboxRect = self.ImageObj.spritebox.RoundedRect

        # Draw the spritebox if applicable
        if drawSpritebox:
            if self.isSelected():
                painter.setBrush(QtGui.QBrush(globals.theme.color('spritebox_fill_s')))
                painter.setPen(QtGui.QPen(globals.theme.color('spritebox_lines_s'), 1 / 24 * globals.TileWidth))
            else:
                painter.setBrush(QtGui.QBrush(globals.theme.color('spritebox_fill')))
                painter.setPen(QtGui.QPen(globals.theme.color('spritebox_lines'), 1 / 24 * globals.TileWidth))
            painter.drawRoundedRect(spriteboxRect, 4, 4)

            painter.setFont(self.font)
            painter.drawText(spriteboxRect, Qt.AlignCenter, str(self.type))

    def scene(self):
        """
        Solves a small bug
        """
        return globals.mainWindow.scene

    def delete(self):
        """
        Delete the sprite from the level
        """
        sprlist = globals.mainWindow.spriteList
        globals.mainWindow.UpdateFlag = True
        sprlist.takeItem(sprlist.row(self.listitem))
        globals.mainWindow.UpdateFlag = False
        sprlist.selectionModel().clearSelection()
        globals.Area.sprites.remove(self)
        # self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())
        self.scene().update()  # The zone painters need for the whole thing to update


class EntranceItem(LevelEditorItem):
    """
    Level editor item that represents an entrance
    """
    BoundingRect = QtCore.QRectF(0, 0, globals.TileWidth, globals.TileWidth)
    RoundedRect = QtCore.QRectF(1, 1, globals.TileWidth - 2, globals.TileWidth - 2)
    EntranceImages = None

    class AuxEntranceItem(QtWidgets.QGraphicsItem):
        """
        Auxiliary item for drawing entrance things
        """
        BoundingRect = QtCore.QRectF(0, 0, globals.TileWidth, globals.TileWidth)

        def __init__(self, parent):
            """
            Initializes the auxiliary entrance thing
            """
            super().__init__(parent)
            self.parent = parent
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
            self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
            self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, True)
            self.setParentItem(parent)
            self.hover = False

        def TypeChange(self):
            """
            Handles type changes to the entrance
            """
            if self.parent.enttype == 20:
                # Jumping facing right
                self.setPos(0, -11.5 * globals.TileWidth)
                self.BoundingRect = QtCore.QRectF(0, 0, 4.0833333 * globals.TileWidth, 12.5 * globals.TileWidth)
            elif self.parent.enttype == 21:
                # Vine
                self.setPos(-0.5 * globals.TileWidth, -10 * globals.TileWidth)
                self.BoundingRect = QtCore.QRectF(0, 0, 2 * globals.TileWidth, 29 * globals.TileWidth)
            else:
                self.setPos(0, 0)
                self.BoundingRect = QtCore.QRectF(0, 0, globals.TileWidth, globals.TileWidth)

        def paint(self, painter, option, widget):
            """
            Paints the entrance aux
            """

            painter.setClipRect(option.exposedRect)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

            if self.parent.enttype == 20:
                # Jumping facing right

                path = QtGui.QPainterPath(QtCore.QPoint(globals.TileWidth / 2, 11.5 * globals.TileWidth))
                path.cubicTo(QtCore.QPoint(globals.TileWidth * 5 / 3, -globals.TileWidth),
                             QtCore.QPoint(2.0833333 * globals.TileWidth, -globals.TileWidth),
                             QtCore.QPoint(2.5 * globals.TileWidth, globals.TileWidth * 3 / 2))
                path.lineTo(QtCore.QPoint(4 * globals.TileWidth, 12.5 * globals.TileWidth))

                painter.setPen(SLib.OutlinePen)
                painter.drawPath(path)

            elif self.parent.enttype == 21:
                # Vine

                # Draw the top half
                painter.setOpacity(1)
                painter.drawPixmap(0, 0, SLib.ImageCache['VineTop'])
                painter.drawTiledPixmap(globals.TileWidth // 2, globals.TileWidth * 2, globals.TileWidth, 7 * globals.TileWidth,
                                        SLib.ImageCache['VineMid'])
                # Draw the bottom half
                # This is semi-transparent because you can't interact with it.
                painter.setOpacity(0.5)
                painter.drawTiledPixmap(globals.TileWidth // 2, globals.TileWidth * 9, globals.TileWidth, 19 * globals.TileWidth,
                                        SLib.ImageCache['VineMid'])
                painter.drawPixmap(globals.TileWidth // 2, 28 * globals.TileWidth, SLib.ImageCache['VineBtm'])

            elif self.parent.enttype == 24:
                # Jumping facing left

                path = QtGui.QPainterPath(QtCore.QPoint(3.5833333 * globals.TileWidth, 11.5 * globals.TileWidth))
                path.cubicTo(QtCore.QPoint(2.41666666 * globals.TileWidth, -globals.TileWidth),
                             QtCore.QPoint(globals.TileWidth / 2, -globals.TileWidth),
                             QtCore.QPoint(1.58333333 * globals.TileWidth, globals.TileWidth * 3 / 2))
                path.lineTo(QtCore.QPoint(globals.TileWidth / 12, globals.TileWidth * 12.5))

                painter.setPen(SLib.OutlinePen)
                painter.drawPath(path)

        def boundingRect(self):
            """
            Required by Qt
            """
            return self.BoundingRect

    def __init__(self, x, y, cameraX, cameraY, id, destarea, destentrance, type, players, zone, playerDistance, settings, otherID, coinOrder,
                 pathID, pathnodeindex, transition):
        """
        Creates an entrance with specific data
        """
        if EntranceItem.EntranceImages is None:
            ei = []
            src = QtGui.QPixmap('miyamotodata/entrances.png')
            for i in range(18):
                ei.append(src.copy(i * globals.TileWidth, 0, globals.TileWidth, globals.TileWidth))
            EntranceItem.EntranceImages = ei

        super().__init__()

        self.font = globals.NumberFont
        self.objx = x
        self.objy = y
        self.camerax = cameraX
        self.cameray = cameraY
        self.entid = id
        self.destarea = destarea
        self.destentrance = destentrance
        self.enttype = type
        self.players = players
        self.entzone = zone
        self.playerDistance = playerDistance
        self.entsettings = settings
        self.otherID = otherID
        self.coinOrder = coinOrder
        self.pathID = pathID
        self.pathnodeindex = pathnodeindex
        self.transition = transition
        self.listitem = None
        self.LevelRect = QtCore.QRectF(self.objx / 16, self.objy / 16, 1, 1)

        self.setFlag(self.ItemIsMovable, not globals.EntrancesFrozen)
        self.setFlag(self.ItemIsSelectable, not globals.EntrancesFrozen)

        globals.DirtyOverride += 1
        self.setPos(int(x * globals.TileWidth / 16), int(y * globals.TileWidth / 16))
        globals.DirtyOverride -= 1

        self.aux = self.AuxEntranceItem(self)

        self.setZValue(27000)
        self.UpdateTooltip()
        self.TypeChange()

    def UpdateTooltip(self):
        """
        Updates the entrance object's tooltip
        """
        if self.enttype >= len(globals.EntranceTypeNames):
            name = globals.trans.string('Entrances', 1)
        else:
            name = globals.EntranceTypeNames[self.enttype]

        if (self.entsettings & 0x80) != 0:
            destination = globals.trans.string('Entrances', 2)
        else:
            if self.destarea == 0:
                destination = globals.trans.string('Entrances', 3, '[id]', self.destentrance)
            else:
                destination = globals.trans.string('Entrances', 4, '[id]', self.destentrance, '[area]', self.destarea)

        self.name = name
        self.destination = destination
        self.setToolTip(globals.trans.string('Entrances', 0, '[ent]', self.entid, '[type]', name, '[dest]', destination))

    def ListString(self):
        """
        Returns a string that can be used to describe the entrance in a list
        """
        if self.enttype >= len(globals.EntranceTypeNames):
            name = globals.trans.string('Entrances', 1)
        else:
            name = globals.EntranceTypeNames[self.enttype]

        if (self.entsettings & 0x80) != 0:
            return globals.trans.string('Entrances', 5, '[id]', self.entid, '[name]', name, '[x]', self.objx, '[y]', self.objy)
        else:
            return globals.trans.string('Entrances', 6, '[id]', self.entid, '[name]', name, '[x]', self.objx, '[y]', self.objy)

    def __lt__(self, other):
        return self.entid < other.entid

    def TypeChange(self):
        """
        Handles the entrance's type changing
        """

        # Determine the size and position of the entrance
        x, y, w, h = 0, 0, 1, 1
        if self.enttype in (3, 4):
            # Vertical pipe
            w = 2
        elif self.enttype in (5, 6):
            # Horizontal pipe
            h = 2

        # Now make the rects
        self.RoundedRect = QtCore.QRectF(x * globals.TileWidth + 1, y * globals.TileWidth + 1, w * globals.TileWidth - 2, h * globals.TileWidth - 2)
        self.BoundingRect = QtCore.QRectF(x * globals.TileWidth, y * globals.TileWidth, w * globals.TileWidth, h * globals.TileWidth)

        # Update the aux thing
        self.aux.TypeChange()

    def paint(self, painter, option, widget):
        """
        Paints the entrance
        """
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        if self.isSelected():
            painter.setBrush(QtGui.QBrush(globals.theme.color('entrance_fill_s')))
            painter.setPen(QtGui.QPen(globals.theme.color('entrance_lines_s'), 1 / 24 * globals.TileWidth))
        else:
            painter.setBrush(QtGui.QBrush(globals.theme.color('entrance_fill')))
            painter.setPen(QtGui.QPen(globals.theme.color('entrance_lines'), 1 / 24 * globals.TileWidth))

        self.TypeChange()
        painter.drawRoundedRect(self.RoundedRect, 4, 4)

        icontype = 0
        enttype = self.enttype
        if enttype == 0 or enttype == 1: icontype = 1  # normal
        if enttype == 2: icontype = 2  # door exit
        if enttype == 3: icontype = 4  # pipe up
        if enttype == 4: icontype = 5  # pipe down
        if enttype == 5: icontype = 6  # pipe left
        if enttype == 6: icontype = 7  # pipe right
        if enttype == 8: icontype = 12  # ground pound
        if enttype == 9: icontype = 13  # sliding
        # 0F/15 is unknown?
        if enttype == 16: icontype = 8  # mini pipe up
        if enttype == 17: icontype = 9  # mini pipe down
        if enttype == 18: icontype = 10  # mini pipe left
        if enttype == 19: icontype = 11  # mini pipe right
        if enttype == 20: icontype = 15  # jump out facing right
        if enttype == 21: icontype = 17  # vine entrance
        if enttype == 23: icontype = 14  # boss battle entrance
        if enttype == 24: icontype = 16  # jump out facing left
        if enttype == 27: icontype = 3  # door entrance

        painter.drawPixmap(0, 0, EntranceItem.EntranceImages[icontype])

        painter.setFont(self.font)
        margin = globals.TileWidth / 10
        painter.drawText(QtCore.QRectF(margin, margin, globals.TileWidth / 2 - margin, globals.TileWidth / 2 - margin), Qt.AlignCenter,
                         str(self.entid))

    def delete(self):
        """
        Delete the entrance from the level
        """
        elist = globals.mainWindow.entranceList
        globals.mainWindow.UpdateFlag = True
        elist.takeItem(elist.row(self.listitem))
        globals.mainWindow.UpdateFlag = False
        elist.selectionModel().clearSelection()
        globals.Area.entrances.remove(self)
        self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())

    def itemChange(self, change, value):
        """
        Handle movement
        """
        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            if self.scene() is None: return value

            updRect = QtCore.QRectF(
                self.x() + self.aux.x(),
                self.y() + self.aux.y(),
                self.aux.BoundingRect.width(),
                self.aux.BoundingRect.height(),
            )
            self.scene().update(updRect)

        return super().itemChange(change, value)

    def getFullRect(self):
        """
        Returns a rectangle that contains the entrance and any
        auxiliary objects.
        """

        br = self.BoundingRect.translated(
            self.x(),
            self.y(),
        )
        br = br.united(
            self.aux.BoundingRect.translated(
                self.aux.x() + self.x(),
                self.aux.y() + self.y(),
            )
        )

        return br


class PathItem(LevelEditorItem):
    """
    Level editor item that represents a path node
    """
    BoundingRect = QtCore.QRectF(0, 0, globals.TileWidth, globals.TileWidth)
    SelectionRect = QtCore.QRectF(0, 0, globals.TileWidth, globals.TileWidth)
    RoundedRect = QtCore.QRectF(1, 1, globals.TileWidth - 2, globals.TileWidth - 2)

    def __init__(self, objx, objy, pathinfo, nodeinfo, unk1, unk2, unk3,
                 unk4):  # no idea what the unknowns are, so...placeholders!
        """
        Creates a path node with specific data
        """

        super().__init__()

        self.font = globals.NumberFont
        self.objx = objx
        self.objy = objy
        self.unk1 = unk1
        self.unk2 = unk2
        self.unk3 = unk3
        self.unk4 = unk4
        self.pathid = pathinfo['id']
        self.nodeid = pathinfo['nodes'].index(nodeinfo)
        self.pathinfo = pathinfo
        self.nodeinfo = nodeinfo
        self.listitem = None
        self.LevelRect = (QtCore.QRectF(self.objx / 16, self.objy / 16, globals.TileWidth / 16, globals.TileWidth / 16))
        self.setFlag(self.ItemIsMovable, not globals.PathsFrozen)
        self.setFlag(self.ItemIsSelectable, not globals.PathsFrozen)

        globals.DirtyOverride += 1
        self.setPos(int(objx * globals.TileWidth / 16), int(objy * globals.TileWidth / 16))
        globals.DirtyOverride -= 1

        self.setZValue(25002)
        self.UpdateTooltip()

        self.setVisible(globals.PathsShown)

        # now that we're inited, set
        self.nodeinfo['graphicsitem'] = self

    def UpdateTooltip(self):
        """
        Updates the path object's tooltip
        """
        self.setToolTip(globals.trans.string('Paths', 0, '[path]', self.pathid, '[node]', self.nodeid))

    def ListString(self):
        """
        Returns a string that can be used to describe the path in a list
        """
        return globals.trans.string('Paths', 1, '[path]', self.pathid, '[node]', self.nodeid)

    def __lt__(self, other):
        return (self.pathid * 10000 + self.nodeid) < (other.pathid * 10000 + other.nodeid)

    def updatePos(self):
        """
        Our x/y was changed, update pathinfo
        """
        self.pathinfo['nodes'][self.nodeid]['x'] = self.objx
        self.pathinfo['nodes'][self.nodeid]['y'] = self.objy

    def updateId(self):
        """
        Path was changed, find our new nodeid
        """
        # called when 1. add node 2. delete node 3. change node order
        # hacky code but it works. considering how pathnodes are stored.
        self.nodeid = self.pathinfo['nodes'].index(self.nodeinfo)
        self.UpdateTooltip()
        self.scene().update()
        self.UpdateListItem()

        # if node doesn't exist, let Miyamoto implode!

    def paint(self, painter, option, widget):
        """
        Paints the path
        """
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setClipRect(option.exposedRect)

        if self.isSelected():
            painter.setBrush(QtGui.QBrush(globals.theme.color('path_fill_s')))
            painter.setPen(QtGui.QPen(globals.theme.color('path_lines_s'), 1 / 24 * globals.TileWidth))
        else:
            painter.setBrush(QtGui.QBrush(globals.theme.color('path_fill')))
            painter.setPen(QtGui.QPen(globals.theme.color('path_lines'), 1 / 24 * globals.TileWidth))
        painter.drawRoundedRect(self.RoundedRect, 4, 4)

        painter.setFont(self.font)
        margin = globals.TileWidth / 10
        painter.drawText(QtCore.QRectF(margin, margin, globals.TileWidth / 2 - margin, globals.TileWidth / 2 - margin), Qt.AlignCenter,
                         str(self.pathid))
        painter.drawText(QtCore.QRectF(margin, globals.TileWidth / 2, globals.TileWidth / 2 - margin, globals.TileWidth / 2 - margin),
                         Qt.AlignCenter, str(self.nodeid))

    def delete(self):
        """
        Delete the path from the level
        """
        plist = globals.mainWindow.pathList
        globals.mainWindow.UpdateFlag = True
        plist.takeItem(plist.row(self.listitem))
        globals.mainWindow.UpdateFlag = False
        plist.selectionModel().clearSelection()
        globals.Area.paths.remove(self)
        self.pathinfo['nodes'].remove(self.nodeinfo)

        if (len(self.pathinfo['nodes']) < 1):
            globals.Area.pathdata.remove(self.pathinfo)
            self.scene().removeItem(self.pathinfo['peline'])

        # update other nodes' IDs
        for pathnode in self.pathinfo['nodes']:
            pathnode['graphicsitem'].updateId()

        self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())


class NabbitPathItem(LevelEditorItem):
    """
    Level editor item that represents a nabbit path node
    """
    BoundingRect = QtCore.QRectF(0, 0, globals.TileWidth, globals.TileWidth)
    SelectionRect = QtCore.QRectF(0, 0, globals.TileWidth, globals.TileWidth)
    RoundedRect = QtCore.QRectF(1, 1, globals.TileWidth - 2, globals.TileWidth - 2)

    def __init__(self, objx, objy, pathinfo, nodeinfo, unk1, unk2, unk3,
                 unk4):  # no idea what the unknowns are, so...placeholders!
        """
        Creates a nabbit path node with specific data
        """

        super().__init__()

        self.font = globals.NumberFont
        self.objx = objx - 8
        self.objy = objy - 8
        self.unk1 = unk1
        self.unk2 = unk2
        self.unk3 = unk3
        self.unk4 = unk4
        self.nodeid = pathinfo['nodes'].index(nodeinfo)
        self.pathinfo = pathinfo
        self.nodeinfo = nodeinfo
        self.listitem = None
        self.LevelRect = (QtCore.QRectF(self.objx / 16, self.objy / 16, globals.TileWidth / 16, globals.TileWidth / 16))
        self.setFlag(self.ItemIsMovable, not globals.PathsFrozen)
        self.setFlag(self.ItemIsSelectable, not globals.PathsFrozen)

        globals.DirtyOverride += 1
        self.setPos(int(self.objx * globals.TileWidth / 16), int(self.objy * globals.TileWidth / 16))
        globals.DirtyOverride -= 1

        self.setZValue(25002)
        self.UpdateTooltip()

        self.setVisible(globals.PathsShown)

        # now that we're inited, set
        self.nodeinfo['graphicsitem'] = self

    def UpdateTooltip(self):
        """
        Updates the path object's tooltip
        """
        self.setToolTip(globals.trans.string('Paths', 2, '[node]', self.nodeid))

    def ListString(self):
        """
        Returns a string that can be used to describe the path in a list
        """
        return globals.trans.string('Paths', 3, '[node]', self.nodeid)

    def __lt__(self, other):
        return self.nodeid < other.nodeid

    def updatePos(self):
        """
        Our x/y was changed, update pathinfo
        """
        self.pathinfo['nodes'][self.nodeid]['x'] = self.objx + 8
        self.pathinfo['nodes'][self.nodeid]['y'] = self.objy + 8

    def updateId(self):
        """
        Path was changed, find our new nodeid
        """
        # called when 1. add node 2. delete node 3. change node order
        # hacky code but it works. considering how pathnodes are stored.
        self.nodeid = self.pathinfo['nodes'].index(self.nodeinfo)
        self.UpdateTooltip()
        self.scene().update()
        self.UpdateListItem()

        # if node doesn't exist, let Miyamoto implode!

    def paint(self, painter, option, widget):
        """
        Paints the path
        """
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setClipRect(option.exposedRect)

        if self.isSelected():
            painter.setBrush(QtGui.QBrush(globals.theme.color('nabbit_path_fill_s')))
            painter.setPen(QtGui.QPen(globals.theme.color('nabbit_path_lines_s'), 1 / 24 * globals.TileWidth))
        else:
            painter.setBrush(QtGui.QBrush(globals.theme.color('nabbit_path_fill')))
            painter.setPen(QtGui.QPen(globals.theme.color('nabbit_path_lines'), 1 / 24 * globals.TileWidth))
        painter.drawRoundedRect(self.RoundedRect, 4, 4)

        painter.setFont(self.font)
        painter.drawText(self.RoundedRect, Qt.AlignCenter, str(self.nodeid))

    def delete(self):
        """
        Delete the path from the level
        """
        plist = globals.mainWindow.nabbitPathList
        globals.mainWindow.UpdateFlag = True
        plist.takeItem(plist.row(self.listitem))
        globals.mainWindow.UpdateFlag = False
        plist.selectionModel().clearSelection()
        globals.Area.nPaths.remove(self)
        self.pathinfo['nodes'].remove(self.nodeinfo)

        if (len(self.pathinfo['nodes']) < 1):
            globals.Area.nPathdata = []
            self.scene().removeItem(self.pathinfo['peline'])

        # update other nodes' IDs
        for pathnode in self.pathinfo['nodes']:
            pathnode['graphicsitem'].updateId()

        self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())


class PathEditorLineItem(LevelEditorItem):
    """
    Level editor item to draw a line between two path nodes
    """
    BoundingRect = QtCore.QRectF(0, 0, 1, 1)  # compute later

    def __init__(self, nodelist):
        """
        Creates a path line with specific data
        """

        super().__init__()

        self.objx = 0
        self.objy = 0
        self.nodelist = nodelist
        self.loops = False
        self.setFlag(self.ItemIsMovable, False)
        self.setFlag(self.ItemIsSelectable, False)
        self.computeBoundRectAndPos()
        self.setZValue(25002)
        self.UpdateTooltip()

        self.setVisible(globals.PathsShown)

    def UpdateTooltip(self):
        """
        For compatibility, just in case
        """
        self.setToolTip('')

    def ListString(self):
        """
        Returns an empty string
        """
        return ''

    def nodePosChanged(self):
        self.computeBoundRectAndPos()
        self.scene().update()

    def computeBoundRectAndPos(self):
        xcoords = []
        ycoords = []
        for node in self.nodelist:
            xcoords.append(int(node['x']) + 8)
            ycoords.append(int(node['y']) + 8)
        self.objx = (min(xcoords) - 4)
        self.objy = (min(ycoords) - 4)

        mywidth = (8 + (max(xcoords) - self.objx)) * (globals.TileWidth / 16)
        myheight = (8 + (max(ycoords) - self.objy)) * (globals.TileWidth / 16)
        globals.DirtyOverride += 1
        self.setPos(self.objx * (globals.TileWidth / 16), self.objy * (globals.TileWidth / 16))
        globals.DirtyOverride -= 1
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(-4, -4, mywidth, myheight)

    def paint(self, painter, option, widget):
        """
        Paints the path lines
        """
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setClipRect(option.exposedRect)

        color = globals.theme.color('path_connector')
        painter.setBrush(QtGui.QBrush(color))
        painter.setPen(QtGui.QPen(color, 3 * globals.TileWidth / 24, join=Qt.RoundJoin, cap=Qt.RoundCap))

        lines = []

        snl = self.nodelist
        mult = globals.TileWidth / 16
        for j, node in enumerate(snl):
            if ((j + 1) < len(snl)):
                a = QtCore.QPointF(float((snl[j]['x'] + 8) * mult) - self.x(), float((snl[j]['y'] + 8) * mult) - self.y())
                b = QtCore.QPointF(float((snl[j + 1]['x'] + 8) * mult) - self.x(), float((snl[j + 1]['y'] + 8) * mult) - self.y())
                lines.append(QtCore.QLineF(a, b))
            elif self.loops and (j + 1) == len(snl):
                a = QtCore.QPointF(float((snl[j]['x'] + 8) * mult) - self.x(), float((snl[j]['y'] + 8) * mult) - self.y())
                b = QtCore.QPointF(float((snl[0]['x'] + 8) * mult) - self.x(), float((snl[0]['y'] + 8) * mult) - self.y())
                lines.append(QtCore.QLineF(a, b))

        painter.drawLines(lines)

    def delete(self):
        """
        Delete the line from the level
        """
        self.scene().update()


class NabbitPathEditorLineItem(PathEditorLineItem):
    """
    Level editor item to draw a line between two nabbit path nodes
    """
    def computeBoundRectAndPos(self):
        xcoords = []
        ycoords = []
        for node in self.nodelist:
            xcoords.append(int(node['x']))
            ycoords.append(int(node['y']))
        self.objx = (min(xcoords) - 4)
        self.objy = (min(ycoords) - 4)

        mywidth = (8 + (max(xcoords) - self.objx)) * (globals.TileWidth / 16)
        myheight = (8 + (max(ycoords) - self.objy)) * (globals.TileWidth / 16)
        globals.DirtyOverride += 1
        self.setPos(self.objx * (globals.TileWidth / 16), self.objy * (globals.TileWidth / 16))
        globals.DirtyOverride -= 1
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(-4, -4, mywidth, myheight)

    def paint(self, painter, option, widget):
        """
        Paints the path lines
        """
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setClipRect(option.exposedRect)

        color = globals.theme.color('nabbit_path_connector')
        painter.setBrush(QtGui.QBrush(color))
        painter.setPen(QtGui.QPen(color, 3 * globals.TileWidth / 24, join=Qt.RoundJoin, cap=Qt.RoundCap))

        lines = []

        snl = self.nodelist
        mult = globals.TileWidth / 16
        for j, node in enumerate(snl):
            if ((j + 1) < len(snl)):
                a = QtCore.QPointF(float(snl[j]['x'] * mult) - self.x(), float(snl[j]['y'] * mult) - self.y())
                b = QtCore.QPointF(float(snl[j + 1]['x'] * mult) - self.x(), float(snl[j + 1]['y'] * mult) - self.y())
                lines.append(QtCore.QLineF(a, b))
            elif self.loops and (j + 1) == len(snl):
                a = QtCore.QPointF(float(snl[j]['x'] * mult) - self.x(), float(snl[j]['y'] * mult) - self.y())
                b = QtCore.QPointF(float(snl[0]['x'] * mult) - self.x(), float(snl[0]['y'] * mult) - self.y())
                lines.append(QtCore.QLineF(a, b))

        painter.drawLines(lines)


class CommentItem(LevelEditorItem):
    """
    Level editor item that represents a in-level comment
    """
    BoundingRect = QtCore.QRectF(-8 * globals.TileWidth / 24, -8 * globals.TileWidth / 24, 48 * globals.TileWidth / 24, 48 * globals.TileWidth / 24)
    SelectionRect = QtCore.QRectF(-4 * globals.TileWidth / 24, -4 * globals.TileWidth / 24, 4 * globals.TileWidth / 24, 4 * globals.TileWidth / 24)
    Circle = QtCore.QRectF(0, 0, 32 * globals.TileWidth / 24, 32 * globals.TileWidth / 24)

    def __init__(self, x, y, text=''):
        """
        Creates a in-level comment
        """
        super().__init__()
        zval = 50000
        self.zval = zval

        self.text = text

        self.objx = x
        self.objy = y
        self.listitem = None
        self.LevelRect = QtCore.QRectF(self.objx / 16, self.objy / 16, 2.25, 2.25)

        self.setFlag(self.ItemIsMovable, not globals.CommentsFrozen)
        self.setFlag(self.ItemIsSelectable, not globals.CommentsFrozen)

        globals.DirtyOverride += 1
        self.setPos(int(x * globals.TileWidth / 16), int(y * globals.TileWidth / 16))
        globals.DirtyOverride -= 1

        self.setZValue(zval + 1)
        self.UpdateTooltip()

        self.CreateTextEdit()

    def CreateTextEdit(self):
        """
        Make the text edit
        """
        self.TextEdit = QtWidgets.QPlainTextEdit()
        self.TextEditProxy = globals.mainWindow.scene.addWidget(self.TextEdit)
        self.TextEditProxy.setZValue(self.zval)
        self.TextEditProxy.setCursor(Qt.IBeamCursor)
        self.TextEditProxy.boundingRect = lambda self: QtCore.QRectF(0, 0, 4000, 4000)
        self.TextEdit.setVisible(False)
        self.TextEdit.setMinimumWidth(8 * globals.TileWidth)
        self.TextEdit.setMinimumHeight(16 * globals.TileWidth / 3)
        self.TextEdit.setMaximumWidth(8 * globals.TileWidth)
        self.TextEdit.setMaximumHeight(16 * globals.TileWidth / 3)
        self.TextEdit.setPlainText(self.text)
        self.TextEdit.textChanged.connect(self.handleTextChanged)
        self.TextEdit.zoomIn(13)
        self.reposTextEdit()

    def UpdateTooltip(self):
        """
        For compatibility, just in case
        """
        self.setToolTip(globals.trans.string('Comments', 1, '[x]', self.objx, '[y]', self.objy))

    def ListString(self):
        """
        Returns a string that can be used to describe the comment in a list
        """
        t = self.OneLineText()
        return globals.trans.string('Comments', 0, '[x]', self.objx, '[y]', self.objy, '[text]', t)

    def OneLineText(self):
        """
        Returns the text of this comment in a format that can be written on one line
        """
        t = str(self.text)
        if t.replace(' ', '').replace('\n', '') == '': t = globals.trans.string('Comments', 3)
        while '\n\n' in t: t = t.replace('\n\n', '\n')
        t = t.replace('\n', globals.trans.string('Comments', 2))

        f = None
        if self.listitem is not None: f = self.listitem.font()

        import misc
        t2 = misc.clipStr(t, 128, f)
        del misc

        if t2 is not None: t = t2 + '...'

        return t

    def paint(self, painter, option, widget):
        """
        Paints the comment
        """
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        if self.isSelected():
            painter.setBrush(QtGui.QBrush(globals.theme.color('comment_fill_s')))
            p = QtGui.QPen(globals.theme.color('comment_lines_s'))
            p.setWidth(3 * globals.TileWidth / 24)
            painter.setPen(p)

        else:
            painter.setBrush(QtGui.QBrush(globals.theme.color('comment_fill')))
            p = QtGui.QPen(globals.theme.color('comment_lines'))
            p.setWidth(3 * globals.TileWidth / 24)
            painter.setPen(p)

        painter.drawEllipse(self.Circle)

        if not self.isSelected():
            painter.setOpacity(.5)

        painter.drawPixmap(4 * globals.TileWidth / 24, 4 * globals.TileWidth / 24, GetIcon('comments', 24).pixmap(globals.TileWidth, globals.TileWidth))
        painter.setOpacity(1)

        # Set the text edit visibility
        try:
            shouldBeVisible = (len(globals.mainWindow.scene.selectedItems()) == 1) and self.isSelected()

        except RuntimeError:
            shouldBeVisible = False

        try:
            self.TextEdit.setVisible(shouldBeVisible)

        except RuntimeError:
            # Sometimes Qt deletes my text edit.
            # Therefore, I need to make a new one.
            self.CreateTextEdit()
            self.TextEdit.setVisible(shouldBeVisible)

    def handleTextChanged(self):
        """
        Handles the text being changed
        """
        self.text = str(self.TextEdit.toPlainText())
        if hasattr(self, 'textChanged'): self.textChanged(self)

    def reposTextEdit(self):
        """
        Repositions the text edit
        """
        self.TextEditProxy.setPos((self.objx * globals.TileWidth / 16) + globals.TileWidth, (self.objy * globals.TileWidth / 16) + globals.TileWidth)

    def handlePosChange(self, oldx, oldy):
        """
        Handles the position changing
        """
        self.reposTextEdit()

        # Manual scene update :(
        w = 192 * globals.TileWidth / 24 + globals.TileWidth
        h = 128 * globals.TileWidth / 24 + globals.TileWidth
        oldx *= globals.TileWidth / 16
        oldy *= globals.TileWidth / 16
        oldRect = QtCore.QRectF(oldx, oldy, w, h)
        self.scene().update(oldRect)

    def delete(self):
        """
        Delete the comment from the level
        """
        clist = globals.mainWindow.commentList
        globals.mainWindow.UpdateFlag = True
        clist.takeItem(clist.row(self.listitem))
        globals.mainWindow.UpdateFlag = False
        clist.selectionModel().clearSelection()
        p = self.TextEditProxy
        p.setSelected(False)
        globals.mainWindow.scene.removeItem(p)
        globals.Area.comments.remove(self)
        self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())
        globals.mainWindow.SaveComments()
