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


################################################################
################################################################

import json

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

if not hasattr(QtWidgets.QGraphicsItem, 'ItemSendsGeometryChanges'):
    # enables itemChange being called on QGraphicsItem
    QtWidgets.QGraphicsItem.ItemSendsGeometryChanges = QtWidgets.QGraphicsItem.GraphicsItemFlag(0x800)

from bytes import *
import globals
from loading import *
import spritelib as SLib
from stamp import *
from ui import *


class LevelOverviewWidget(QtWidgets.QWidget):
    """
    Widget that shows an overview of the level and can be clicked to move the view
    """
    moveIt = QtCore.pyqtSignal(int, int)

    def __init__(self):
        """
        Constructor for the level overview widget
        """
        super().__init__()
        self.setSizePolicy(
            QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))

        self.bgbrush = QtGui.QBrush(globals.theme.color('bg'))
        self.objbrush = QtGui.QBrush(globals.theme.color('overview_object'))
        self.viewbrush = QtGui.QBrush(globals.theme.color('overview_zone_fill'))
        self.view = QtCore.QRectF(0, 0, 0, 0)
        self.spritebrush = QtGui.QBrush(globals.theme.color('overview_sprite'))
        self.entrancebrush = QtGui.QBrush(globals.theme.color('overview_entrance'))
        self.locationbrush = QtGui.QBrush(globals.theme.color('overview_location_fill'))

        self.scale = 0.375
        self.maxX = 1
        self.maxY = 1
        self.CalcSize()
        self.Rescale()

        self.Xposlocator = 0
        self.Yposlocator = 0
        self.Hlocator = 50
        self.Wlocator = 80
        self.mainWindowScale = 1

    def Reset(self):
        """
        Resets the max and scale variables
        """
        self.scale = 0.375
        self.maxX = 1
        self.maxY = 1
        self.CalcSize()
        self.Rescale()

    def CalcSize(self):
        """
        Calculates all the required sizes for this scale
        """
        self.posmult = globals.TileWidth / self.scale

    def mouseMoveEvent(self, event):
        """
        Handles mouse movement over the widget
        """
        QtWidgets.QWidget.mouseMoveEvent(self, event)

        if event.buttons() == Qt.LeftButton:
            self.moveIt.emit(event.pos().x() * self.posmult, event.pos().y() * self.posmult)

    def mousePressEvent(self, event):
        """
        Handles mouse pressing events over the widget
        """
        QtWidgets.QWidget.mousePressEvent(self, event)

        if event.button() == Qt.LeftButton:
            self.moveIt.emit(event.pos().x() * self.posmult, event.pos().y() * self.posmult)

    def paintEvent(self, event):
        """
        Paints the level overview widget
        """
        if not hasattr(globals.Area, 'layers'):
            # fixes race condition where this widget is painted after
            # the level is created, but before it's loaded
            return

        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)

        self.Rescale()
        painter.scale(self.scale, self.scale)
        painter.fillRect(0, 0, 1024, 512, self.bgbrush)

        maxX = self.maxX
        maxY = self.maxY
        dr = painter.drawRect
        fr = painter.fillRect

        maxX = 0
        maxY = 0

        b = self.viewbrush
        painter.setPen(QtGui.QPen(globals.theme.color('overview_zone_lines'), 1))

        for zone in globals.Area.zones:
            x = zone.objx / 16
            y = zone.objy / 16
            width = zone.width / 16
            height = zone.height / 16
            fr(x, y, width, height, b)
            dr(x, y, width, height)
            if x + width > maxX:
                maxX = x + width
            if y + height > maxY:
                maxY = y + height

        b = self.objbrush

        for layer in globals.Area.layers:
            for obj in layer:
                fr(obj.LevelRect, b)
                if obj.objx > maxX:
                    maxX = obj.objx
                if obj.objy > maxY:
                    maxY = obj.objy

        b = self.spritebrush

        for sprite in globals.Area.sprites:
            fr(sprite.LevelRect, b)
            if sprite.objx / 16 > maxX:
                maxX = sprite.objx / 16
            if sprite.objy / 16 > maxY:
                maxY = sprite.objy / 16

        b = self.entrancebrush

        for ent in globals.Area.entrances:
            fr(ent.LevelRect, b)
            if ent.objx / 16 > maxX:
                maxX = ent.objx / 16
            if ent.objy / 16 > maxY:
                maxY = ent.objy / 16

        b = self.locationbrush
        painter.setPen(QtGui.QPen(globals.theme.color('overview_location_lines'), 1))

        for location in globals.Area.locations:
            x = location.objx / 16
            y = location.objy / 16
            width = location.width / 16
            height = location.height / 16
            fr(x, y, width, height, b)
            dr(x, y, width, height)
            if x + width > maxX:
                maxX = x + width
            if y + height > maxY:
                maxY = y + height

        self.maxX = maxX
        self.maxY = maxY

        b = self.locationbrush
        painter.setPen(QtGui.QPen(globals.theme.color('overview_viewbox'), 1))
        painter.drawRect(self.Xposlocator / globals.TileWidth / self.mainWindowScale,
                         self.Yposlocator / globals.TileWidth / self.mainWindowScale,
                         self.Wlocator / globals.TileWidth / self.mainWindowScale,
                         self.Hlocator / globals.TileWidth / self.mainWindowScale)

    def Rescale(self):
        self.Xscale = (float(self.width()) / float(self.maxX + 45))
        self.Yscale = (float(self.height()) / float(self.maxY + 25))

        if self.Xscale <= self.Yscale:
            self.scale = self.Xscale
        else:
            self.scale = self.Yscale

        if self.scale < 0.002: self.scale = 0.002

        self.CalcSize()


class ObjectPickerWidget(QtWidgets.QListView):
    """
    Widget that shows a list of available objects
    """

    def __init__(self):
        """
        Initializes the widget
        """

        super().__init__()
        self.setFlow(QtWidgets.QListView.LeftToRight)
        self.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.setMovement(QtWidgets.QListView.Static)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.setWrapping(True)

        self.m0 = self.ObjectListModel()
        self.mall = self.ObjectListModel()
        self.m123 = self.ObjectListModel()
        self.setModel(self.m0)

        self.setItemDelegate(self.ObjectItemDelegate())

        self.clicked.connect(self.HandleObjReplace)

    def contextMenuEvent(self, event):
        """
        Creates and shows the right-click menu
        """
        self.menu = QtWidgets.QMenu(self)

        export = QtWidgets.QAction('Export', self)
        export.triggered.connect(self.HandleObjExport)

        delete = QtWidgets.QAction('Delete', self)
        delete.triggered.connect(self.HandleObjDelete)

        self.menu.addAction(export)
        self.menu.addAction(delete)

        self.menu.popup(QtGui.QCursor.pos())

    def LoadFromTilesets(self):
        """
        Renders all the object previews
        """
        self.m0.LoadFromTileset(0)
        self.m123.LoadFromTileset(1)

    def ShowTileset(self, id):
        """
        Shows a specific tileset in the picker
        """
        sel = self.currentIndex().row()
        if id == 0: self.setModel(self.m0)
        elif id == 1: self.setModel(self.mall)
        else: self.setModel(self.m123)
        self.setCurrentIndex(self.model().index(sel, 0, QtCore.QModelIndex()))

    @QtCore.pyqtSlot(QtCore.QModelIndex, QtCore.QModelIndex)
    def currentChanged(self, current, previous):
        """
        Throws a signal when the selected object changed
        """
        self.ObjChanged.emit(current.row())

    @QtCore.pyqtSlot(QtCore.QModelIndex)
    def HandleObjReplace(self, index):
        """
        Throws a signal when the selected object is used as a replacement
        """
        if QtWidgets.QApplication.keyboardModifiers() == Qt.AltModifier:
            self.ObjReplace.emit(index.row())

    def HandleObjExport(self, index):
        """
        Exports an object from the tileset
        """
        save_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Choose where to save the Object folder")
        if not save_path: return

        idx = globals.CurrentPaintType
        objNum = globals.CurrentObject

        tileoffset = idx * 256

        name = eval('Area.tileset%d' % idx)

        obj = globals.ObjectDefinitions[idx][objNum]

        jsonData = {}

        tex = QtGui.QPixmap(obj.width * 60, obj.height * 60)
        tex.fill(Qt.transparent)
        nml = QtGui.QPixmap(obj.width * 60, obj.height * 60)
        nml.fill(QtGui.QColor(128, 128, 255))
        painter = QtGui.QPainter(tex)
        nmlPainter = QtGui.QPainter(nml)

        # Checks if the slop is reversed and reverses the rows
        isSlope = obj.rows[0][0][0]
        if (isSlope & 0x80) and (isSlope & 0x2):
            colldata = []

            x = 0
            y = (obj.height - 1) * 60
            for row in obj.rows:
                colls = b''
                for tile in row:
                    if len(tile) == 3:
                        tileNum = (tile[1] & 0xFF) + tileoffset
                        painter.drawPixmap(x, y, globals.Tiles[tileNum].main)
                        nmlPainter.drawPixmap(x, y, globals.Tiles[tileNum].nml)
                        colls += bytes(globals.Tiles[tileNum].collData)
                        x += 60
                colldata.append(colls)
                y -= 60
                x = 0

            colldata = b''.join(reversed(colldata))

        else:
            colldata = b''

            x = 0
            y = 0
            for row in obj.rows:
                for tile in row:
                    if len(tile) == 3:
                        tileNum = (tile[1] & 0xFF) + tileoffset
                        painter.drawPixmap(x, y, globals.Tiles[tileNum].main)
                        nmlPainter.drawPixmap(x, y, globals.Tiles[tileNum].nml)
                        colldata += bytes(globals.Tiles[tileNum].collData)
                        x += 60
                y += 60
                x = 0

        painter.end()
        nmlPainter.end()

        if not os.path.exists(save_path + "/" + name):
            os.makedirs(save_path + "/" + name)

        tex.save(save_path + "/" + name + "/" + name + "_object_" + str(objNum) + ".png", "PNG")
        jsonData['img'] = name + "_object_" + str(objNum) + ".png"

        nml.save(save_path + "/" + name + "/" + name + "_object_" + str(objNum) + "_nml.png", "PNG")
        jsonData['nml'] = name + "_object_" + str(objNum) + "_nml.png"

        with open(save_path + "/" + name + "/" + name + "_object_" + str(objNum) + ".colls", "wb+") as colls:
                colls.write(colldata)

        jsonData['colls'] = name + "_object_" + str(objNum) + ".colls"

        deffile = b''

        for row in obj.rows:
            for tile in row:
                if len(tile) == 3:
                    byte0 = tile[0]
                    byte1 = tile[1] & 0xFF
                    byte2 = tile[2] << 2
                    byte2 |= idx  # Slot

                    deffile += bytes([byte0, byte1, byte2])

                else:
                    deffile += bytes(tile)

            deffile += b'\xFE'

        deffile += b'\xFF'

        with open(save_path + "/" + name + "/" + name + "_object_" + str(objNum) + ".objlyt", "wb+") as objlyt:
            objlyt.write(deffile)

        jsonData['objlyt'] = name + "_object_" + str(objNum) + ".objlyt"

        indexfile = struct.pack('>HBBxB', 0, obj.width, obj.height, 0)

        with open(save_path + "/" + name + "/" + name + "_object_" + str(objNum) + ".meta", "wb+") as meta:
            meta.write(indexfile)

        jsonData['meta'] = name + "_object_" + str(objNum) + ".meta"

        with open(save_path + "/" + name + "/" + name + "_object_" + str(objNum) + ".json", 'w+') as outfile:
            json.dump(jsonData, outfile)

    def HandleObjDelete(self, index):
        """
        Deletes an object from the tileset
        """
        idx = globals.CurrentPaintType
        objNum = globals.CurrentObject

        # From Satoru
        ## Checks if the object is deletable
        matchingObjs = []

        for layer in globals.Area.layers:
            for obj in layer:
                if obj.tileset == idx and obj.type == objNum:
                    matchingObjs.append(obj)

        if matchingObjs:
            where = [('(%d, %d)' % (obj.objx, obj.objy)) for obj in matchingObjs]
            dlgTxt = "You can't delete this object because there are instances of it at the following coordinates:\n"
            dlgTxt += ', '.join(where)
            dlgTxt += '\nPlease remove or replace them before deleting this object.'

            QtWidgets.QMessageBox.critical(self, 'Cannot Delete', dlgTxt)
            return

        del globals.ObjectDefinitions[idx][objNum]
        globals.ObjectDefinitions[idx].append(None)

        # Remove the object from globals.ObjectAddedtoEmbedded
        if len(globals.ObjectAddedtoEmbedded[globals.CurrentArea][globals.mainWindow.folderPicker.currentIndex()]):
            found = False
            for i in globals.ObjectAddedtoEmbedded[globals.CurrentArea][globals.mainWindow.folderPicker.currentIndex()]:
                obj = globals.ObjectAddedtoEmbedded[globals.CurrentArea][globals.mainWindow.folderPicker.currentIndex()][i]
                if obj == (idx, objNum):
                    found = True
                    tempidx, tempobjNum = globals.ObjectAddedtoEmbedded[globals.CurrentArea][globals.mainWindow.folderPicker.currentIndex()][i]
                    del globals.ObjectAddedtoEmbedded[globals.CurrentArea][globals.mainWindow.folderPicker.currentIndex()][i]
                    break

            if found:
                for i in globals.ObjectAddedtoEmbedded[globals.CurrentArea][globals.mainWindow.folderPicker.currentIndex()]:
                    obj = globals.ObjectAddedtoEmbedded[globals.CurrentArea][globals.mainWindow.folderPicker.currentIndex()][i]
                    if obj[0] == tempidx:
                        if obj[1] > tempobjNum:
                            globals.ObjectAddedtoEmbedded[globals.CurrentArea][globals.mainWindow.folderPicker.currentIndex()][i] = (obj[0], obj[1] - 1)

        if globals.ObjectDefinitions[idx] == [None] * 256:
            if idx == 1: globals.Area.tileset1 = ''
            elif idx == 2: globals.Area.tileset2 = ''
            elif idx == 3: globals.Area.tileset3 = ''

        for layer in globals.Area.layers:
            for obj in layer:
                if obj.tileset == idx:
                    if obj.type > objNum:
                        obj.type -= 1

        self.LoadFromTilesets()

        if not (globals.Area.tileset1 or globals.Area.tileset2 or globals.Area.tileset3):
            globals.mainWindow.objAllTab.setCurrentIndex(0)
            globals.mainWindow.objAllTab.setTabEnabled(2, False)

        globals.mainWindow.scene.update()
        SetDirty()

        globals.mainWindow.updateNumUsedTilesLabel()

    ObjChanged = QtCore.pyqtSignal(int)
    ObjReplace = QtCore.pyqtSignal(int)

    class ObjectItemDelegate(QtWidgets.QAbstractItemDelegate):
        """
        Handles tileset objects and their rendering
        """

        def paint(self, painter, option, index):
            """
            Paints an object
            """
            if option.state & QtWidgets.QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())

            p = index.model().data(index, Qt.DecorationRole)
            painter.drawPixmap(option.rect.x() + 2, option.rect.y() + 2, p)
            # painter.drawText(option.rect, str(index.row()))

        def sizeHint(self, option, index):
            """
            Returns the size for the object
            """
            p = index.model().data(index, Qt.UserRole)
            return p or QtCore.QSize(globals.TileWidth, globals.TileWidth)
            # return QtCore.QSize(76,76)

    class ObjectListModel(QtCore.QAbstractListModel):
        """
        Model containing all the objects in a tileset
        """

        def __init__(self):
            """
            Initializes the model
            """
            super().__init__()
            self.items = []
            self.ritems = []
            self.itemsize = []

            for i in range(256):
                self.items.append(None)
                self.ritems.append(None)

        def rowCount(self, parent=None):
            """
            Required by Qt
            """
            return len(self.items)

        def data(self, index, role=Qt.DisplayRole):
            """
            Get what we have for a specific row
            """
            if not index.isValid(): return None
            n = index.row()
            if n < 0: return None
            if n >= len(self.items): return None

            if role == Qt.DecorationRole and n < len(self.ritems):
                return self.ritems[n]

            if role == Qt.BackgroundRole:
                return QtGui.qApp.palette().base()

            if role == Qt.UserRole and n < len(self.itemsize):
                return self.itemsize[n]

            if role == Qt.ToolTipRole and n < len(self.tooltips):
                return self.tooltips[n]

            return None

        def LoadFromTileset(self, idx):
            """
            Renders all the object previews for the model
            """
            self.items = []
            self.ritems = []
            self.itemsize = []
            self.tooltips = []

            globals.numObj = []

            z = 0

            if idx != 0:
                numTileset = range(1, 4)
            else:
                numTileset = range(1)

            for idx in numTileset:
                if globals.ObjectDefinitions[idx] is None:
                    globals.numObj.append(z)
                    continue

                self.beginResetModel()
                defs = globals.ObjectDefinitions[idx]

                for i in range(256):
                    if defs[i] is None: break
                    obj = RenderObject(idx, i, defs[i].width, defs[i].height, True)
                    self.items.append(obj)

                    pm = QtGui.QPixmap(defs[i].width * globals.TileWidth, defs[i].height * globals.TileWidth)
                    pm.fill(Qt.transparent)
                    p = QtGui.QPainter()
                    p.begin(pm)
                    y = 0
                    isAnim = False

                    for row in obj:
                        x = 0
                        for tile in row:
                            if tile != -1:
                                try:
                                    if isinstance(globals.Tiles[tile].main, QtGui.QImage):
                                        p.drawImage(x, y, globals.Tiles[tile].main)
                                    else:
                                        p.drawPixmap(x, y, globals.Tiles[tile].main)
                                except AttributeError:
                                    break
                                if isinstance(globals.Tiles[tile], TilesetTile) and globals.Tiles[tile].isAnimated: isAnim = True
                            x += globals.TileWidth
                        y += globals.TileWidth
                    p.end()

                    pm = pm.scaledToWidth(pm.width() * 32 / globals.TileWidth, Qt.SmoothTransformation)
                    if pm.width() > 256:
                        pm = pm.scaledToWidth(256, Qt.SmoothTransformation)
                    if pm.height() > 256:
                        pm = pm.scaledToHeight(256, Qt.SmoothTransformation)

                    self.ritems.append(pm)
                    self.itemsize.append(QtCore.QSize(pm.width() + 4, pm.height() + 4))
                    if (idx == 0) and (i in globals.ObjDesc) and isAnim:
                        self.tooltips.append(globals.trans.string('Objects', 4, '[tileset]', idx+1, '[id]', i, '[desc]', globals.ObjDesc[i]))
                    elif (idx == 0) and (i in globals.ObjDesc):
                        self.tooltips.append(globals.trans.string('Objects', 3, '[tileset]', idx+1, '[id]', i, '[desc]', globals.ObjDesc[i]))
                    elif isAnim:
                        self.tooltips.append(globals.trans.string('Objects', 2, '[tileset]', idx+1, '[id]', i))
                    else:
                        self.tooltips.append(globals.trans.string('Objects', 1, '[tileset]', idx+1, '[id]', i))

                    z += 1

                self.endResetModel()

                globals.numObj.append(z)

        def LoadFromFolder(self):
            """
            Renders all the object previews for the model from a folder
            """
            globals.ObjectAllDefinitions = []
            globals.ObjectAllCollisions = []
            globals.ObjectAllImages = []

            self.items = []
            self.ritems = []
            self.itemsize = []
            self.tooltips = []

            z = 0

            self.beginResetModel()

            top_folder = os.path.join(setting('ObjPath'), globals.mainWindow.folderPicker.currentText())

            for file in os.listdir(top_folder):
                if file.endswith(".json"):
                    dir = top_folder + "/"

                    with open(dir + file) as inf:
                        jsonData = json.load(inf)

                    with open(dir + jsonData["colls"], "rb") as inf:
                        globals.ObjectAllCollisions.append(inf.read())

                    with open(dir + jsonData["meta"], "rb") as inf:
                        indexfile = inf.read()

                    with open(dir + jsonData["objlyt"], "rb") as inf:
                        deffile = inf.read()

                    indexstruct = struct.Struct('>HBBH')

                    data = indexstruct.unpack_from(indexfile, 0)
                    obj = ObjectDef()
                    obj.width = data[1]
                    obj.height = data[2]
                    obj.randByte = 0  # TODO
                    obj.load(deffile, 0)

                    globals.ObjectAllDefinitions.append(obj)

                    obj = RenderObjectAll(obj, obj.width, obj.height, True)
                    self.items.append(obj)

                    globals.ObjectAllImages.append([QtGui.QPixmap(dir + jsonData["img"]),
                                            QtGui.QPixmap(dir + jsonData["nml"])])

                    pm = globals.ObjectAllImages[-1][0]

                    pm = pm.scaledToWidth(pm.width() * 32/globals.TileWidth, Qt.SmoothTransformation)
                    if pm.width() > 256:
                        pm = pm.scaledToWidth(256, Qt.SmoothTransformation)
                    if pm.height() > 256:
                        pm = pm.scaledToHeight(256, Qt.SmoothTransformation)

                    self.ritems.append(pm)
                    self.itemsize.append(QtCore.QSize(pm.width() + 4, pm.height() + 4))
                    self.tooltips.append(globals.trans.string('Objects', 5, '[id]', z))

                    z += 1

                    self.endResetModel()


class StampChooserWidget(QtWidgets.QListView):
    """
    Widget that shows a list of available stamps
    """
    selectionChangedSignal = QtCore.pyqtSignal()

    def __init__(self):
        """
        Initializes the widget
        """
        super().__init__()

        self.setFlow(QtWidgets.QListView.LeftToRight)
        self.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.setMovement(QtWidgets.QListView.Static)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setWrapping(True)

        self.model = StampListModel()
        self.setModel(self.model)

        self.setItemDelegate(StampChooserWidget.StampItemDelegate())

    class StampItemDelegate(QtWidgets.QStyledItemDelegate):
        """
        Handles stamp rendering
        """

        def __init__(self):
            """
            Initializes the delegate
            """
            super().__init__()

        def createEditor(self, parent, option, index):
            """
            Creates a stamp name editor
            """
            return QtWidgets.QLineEdit(parent)

        def setEditorData(self, editor, index):
            """
            Sets the data for the stamp name editor from the data at index
            """
            editor.setText(index.model().data(index, Qt.UserRole + 1))

        def setModelData(self, editor, model, index):
            """
            Set the data in the model for the data at index
            """
            index.model().setData(index, editor.text())

        def paint(self, painter, option, index):
            """
            Paints a stamp
            """

            if option.state & QtWidgets.QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())

            painter.drawPixmap(option.rect.x() + 2, option.rect.y() + 2, index.model().data(index, Qt.DecorationRole))

        def sizeHint(self, option, index):
            """
            Returns the size for the stamp
            """
            return index.model().data(index, Qt.DecorationRole).size() + QtCore.QSize(4, 4)

    def addStamp(self, stamp):
        """
        Adds a stamp
        """
        self.model.addStamp(stamp)

    def removeStamp(self, stamp):
        """
        Removes a stamp
        """
        self.model.removeStamp(stamp)

    def currentlySelectedStamp(self):
        """
        Returns the currently selected stamp
        """
        idxobj = self.currentIndex()
        if idxobj.row() == -1: return
        return self.model.items[idxobj.row()]

    def selectionChanged(self, selected, deselected):
        """
        Called when the selection changes.
        """
        val = super().selectionChanged(selected, deselected)
        self.selectionChangedSignal.emit()
        return val


class SpritePickerWidget(QtWidgets.QTreeWidget):
    """
    Widget that shows a list of available sprites
    """

    def __init__(self):
        """
        Initializes the widget
        """
        super().__init__()
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setIndentation(16)
        self.currentItemChanged.connect(self.HandleItemChange)

        LoadSpriteData()
        LoadSpriteListData()
        LoadSpriteCategories()
        self.LoadItems()

    def LoadItems(self):
        """
        Loads tree widget items
        """
        self.clear()

        for viewname, view, nodelist in globals.SpriteCategories:
            for n in nodelist: nodelist.remove(n)
            for catname, category in view:
                cnode = QtWidgets.QTreeWidgetItem()
                cnode.setText(0, catname)
                cnode.setData(0, Qt.UserRole, -1)

                isSearch = (catname == globals.trans.string('Sprites', 16))
                if isSearch:
                    self.SearchResultsCategory = cnode
                    SearchableItems = []

                for id in category:
                    snode = QtWidgets.QTreeWidgetItem()
                    if id == 9999:
                        snode.setText(0, globals.trans.string('Sprites', 17))
                        snode.setData(0, Qt.UserRole, -2)
                        self.NoSpritesFound = snode
                    else:
                        snode.setText(0, globals.trans.string('Sprites', 18, '[id]', id, '[name]', globals.Sprites[id].name))
                        snode.setData(0, Qt.UserRole, id)

                    if isSearch:
                        SearchableItems.append(snode)

                    cnode.addChild(snode)

                self.addTopLevelItem(cnode)
                cnode.setHidden(True)
                nodelist.append(cnode)

        self.ShownSearchResults = SearchableItems
        self.NoSpritesFound.setHidden(True)

        self.itemClicked.connect(self.HandleSprReplace)

        self.SwitchView(globals.SpriteCategories[0])

    def SwitchView(self, view):
        """
        Changes the selected sprite view
        """
        for i in range(0, self.topLevelItemCount()):
            self.topLevelItem(i).setHidden(True)

        for node in view[2]:
            node.setHidden(False)

    def HandleItemChange(self, current, previous):
        """
        Throws a signal when the selected object changed
        """
        if current is None: return
        id = current.data(0, Qt.UserRole)
        if id != -1:
            self.SpriteChanged.emit(id)

    def SetSearchString(self, searchfor):
        """
        Shows the items containing that string
        """
        check = self.SearchResultsCategory

        rawresults = self.findItems(searchfor, Qt.MatchContains | Qt.MatchRecursive)
        results = list(filter((lambda x: x.parent() == check), rawresults))

        for x in self.ShownSearchResults: x.setHidden(True)
        for x in results: x.setHidden(False)
        self.ShownSearchResults = results

        self.NoSpritesFound.setHidden((len(results) != 0))
        self.SearchResultsCategory.setExpanded(True)

    def HandleSprReplace(self, item, column):
        """
        Throws a signal when the selected sprite is used as a replacement
        """
        if QtWidgets.QApplication.keyboardModifiers() == Qt.AltModifier:
            id = item.data(0, Qt.UserRole)
            if id != -1:
                self.SpriteReplace.emit(id)

    SpriteChanged = QtCore.pyqtSignal(int)
    SpriteReplace = QtCore.pyqtSignal(int)


class SpriteEditorWidget(QtWidgets.QWidget):
    """
    Widget for editing sprite data
    """
    DataUpdate = QtCore.pyqtSignal('PyQt_PyObject')

    def __init__(self, defaultmode=False):
        """
        Constructor
        """
        super().__init__()
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))

        # create the raw editor
        font = QtGui.QFont()
        font.setPointSize(8)
        editbox = QtWidgets.QLabel(globals.trans.string('SpriteDataEditor', 3))
        editbox.setFont(font)
        edit = QtWidgets.QLineEdit()
        edit.textEdited.connect(self.HandleRawDataEdited)
        self.raweditor = edit

        editboxlayout = QtWidgets.QHBoxLayout()
        editboxlayout.addWidget(editbox)
        editboxlayout.addWidget(edit)
        editboxlayout.setStretch(1, 1)

        # 'Editing Sprite #' label
        self.spriteLabel = QtWidgets.QLabel('-')
        self.spriteLabel.setWordWrap(True)

        self.noteButton = QtWidgets.QToolButton()
        self.noteButton.setIcon(GetIcon('note'))
        self.noteButton.setText(globals.trans.string('SpriteDataEditor', 4))
        self.noteButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.noteButton.setAutoRaise(True)
        self.noteButton.clicked.connect(self.ShowNoteTooltip)

        self.relatedObjFilesButton = QtWidgets.QToolButton()
        self.relatedObjFilesButton.setIcon(GetIcon('data'))
        self.relatedObjFilesButton.setText(globals.trans.string('SpriteDataEditor', 7))
        self.relatedObjFilesButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.relatedObjFilesButton.setAutoRaise(True)
        self.relatedObjFilesButton.clicked.connect(self.ShowRelatedObjFilesTooltip)

        toplayout = QtWidgets.QHBoxLayout()
        toplayout.addWidget(self.spriteLabel)
        toplayout.addStretch(1)
        toplayout.addWidget(self.relatedObjFilesButton)
        toplayout.addWidget(self.noteButton)

        subLayout = QtWidgets.QVBoxLayout()
        subLayout.setContentsMargins(0, 0, 0, 0)

        # create a layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(toplayout)
        mainLayout.addLayout(subLayout)

        layout = QtWidgets.QGridLayout()
        self.editorlayout = layout
        subLayout.addLayout(layout)
        subLayout.addLayout(editboxlayout)

        self.setLayout(mainLayout)

        self.spritetype = -1
        self.data = to_bytes(0, 12)
        self.fields = []
        self.UpdateFlag = False
        self.DefaultMode = defaultmode

        self.notes = None
        self.relatedObjFiles = None

    class PropertyDecoder(QtCore.QObject):
        """
        Base class for all the sprite data decoder/encoders
        """
        updateData = QtCore.pyqtSignal('PyQt_PyObject')

        def retrieve(self, data):
            """
            Extracts the value from the specified nybble(s)
            """
            nybble = self.nybble

            if isinstance(nybble, tuple):
                if nybble[1] == (nybble[0] + 2) and (nybble[0] | 1) == 0:
                    # optimize if it's just one byte
                    return data[nybble[0] >> 1]
                else:
                    # we have to calculate it sadly
                    # just do it by looping, shouldn't be that bad
                    value = 0
                    for n in range(nybble[0], nybble[1]):
                        value <<= 4
                        value |= (data[n >> 1] >> (0 if (n & 1) == 1 else 4)) & 15
                    return value
            else:
                # we just want one nybble
                if nybble >= (len(data) * 2): return 0
                return (data[nybble // 2] >> (0 if (nybble & 1) == 1 else 4)) & 15

        def insertvalue(self, data, value):
            """
            Assigns a value to the specified nybble(s)
            """
            nybble = self.nybble
            sdata = list(data)

            if isinstance(nybble, tuple):
                if nybble[1] == (nybble[0] + 2) and (nybble[0] | 1) == 0:
                    # just one byte, this is easier
                    sdata[nybble[0] >> 1] = value & 255
                else:
                    # AAAAAAAAAAA
                    for n in reversed(range(nybble[0], nybble[1])):
                        cbyte = sdata[n >> 1]
                        if (n & 1) == 1:
                            cbyte = (cbyte & 240) | (value & 15)
                        else:
                            cbyte = ((value & 15) << 4) | (cbyte & 15)
                        sdata[n >> 1] = cbyte
                        value >>= 4
            else:
                # only overwrite one nybble
                cbyte = sdata[nybble >> 1]
                if (nybble & 1) == 1:
                    cbyte = (cbyte & 240) | (value & 15)
                else:
                    cbyte = ((value & 15) << 4) | (cbyte & 15)
                sdata[nybble >> 1] = cbyte

            return bytes(sdata)

    class CheckboxPropertyDecoder(PropertyDecoder):
        """
        Class that decodes/encodes sprite data to/from a checkbox
        """

        def __init__(self, title, nybble, mask, comment, layout, row):
            """
            Creates the widget
            """
            super().__init__()

            self.widget = QtWidgets.QCheckBox(title)
            if comment is not None: self.widget.setToolTip(comment)
            self.widget.clicked.connect(self.HandleClick)

            if isinstance(nybble, tuple):
                length = nybble[1] - nybble[0] + 1
            else:
                length = 1

            xormask = 0
            for i in range(length):
                xormask |= 0xF << (i * 4)

            self.nybble = nybble
            self.mask = mask
            self.xormask = xormask
            layout.addWidget(self.widget, row, 0, 1, 2)

        def update(self, data):
            """
            Updates the value shown by the widget
            """
            value = ((self.retrieve(data) & self.mask) == self.mask)
            self.widget.setChecked(value)

        def assign(self, data):
            """
            Assigns the selected value to the data
            """
            value = self.retrieve(data) & (self.mask ^ self.xormask)
            if self.widget.isChecked():
                value |= self.mask
            return self.insertvalue(data, value)

        @QtCore.pyqtSlot(bool)
        def HandleClick(self, clicked=False):
            """
            Handles clicks on the checkbox
            """
            self.updateData.emit(self)

    class ListPropertyDecoder(PropertyDecoder):
        """
        Class that decodes/encodes sprite data to/from a combobox
        """

        def __init__(self, title, nybble, model, comment, layout, row):
            """
            Creates the widget
            """
            super().__init__()

            self.model = model
            self.widget = QtWidgets.QComboBox()
            self.widget.setModel(model)
            if comment is not None: self.widget.setToolTip(comment)
            self.widget.currentIndexChanged.connect(self.HandleIndexChanged)

            self.nybble = nybble
            layout.addWidget(QtWidgets.QLabel(title + ':'), row, 0, Qt.AlignRight)
            layout.addWidget(self.widget, row, 1)

        def update(self, data):
            """
            Updates the value shown by the widget
            """
            value = self.retrieve(data)
            if not self.model.existingLookup[value]:
                self.widget.setCurrentIndex(-1)
                return

            i = 0
            for x in self.model.entries:
                if x[0] == value:
                    self.widget.setCurrentIndex(i)
                    break
                i += 1

        def assign(self, data):
            """
            Assigns the selected value to the data
            """
            return self.insertvalue(data, self.model.entries[self.widget.currentIndex()][0])

        @QtCore.pyqtSlot(int)
        def HandleIndexChanged(self, index):
            """
            Handle the current index changing in the combobox
            """
            self.updateData.emit(self)

    class ValuePropertyDecoder(PropertyDecoder):
        """
        Class that decodes/encodes sprite data to/from a spinbox
        """

        def __init__(self, title, nybble, max, comment, layout, row):
            """
            Creates the widget
            """
            super().__init__()

            self.widget = QtWidgets.QSpinBox()
            self.widget.setRange(0, max - 1)
            if comment is not None: self.widget.setToolTip(comment)
            self.widget.valueChanged.connect(self.HandleValueChanged)

            self.nybble = nybble
            layout.addWidget(QtWidgets.QLabel(title + ':'), row, 0, Qt.AlignRight)
            layout.addWidget(self.widget, row, 1)

        def update(self, data):
            """
            Updates the value shown by the widget
            """
            value = self.retrieve(data)
            self.widget.setValue(value)

        def assign(self, data):
            """
            Assigns the selected value to the data
            """
            return self.insertvalue(data, self.widget.value())

        @QtCore.pyqtSlot(int)
        def HandleValueChanged(self, value):
            """
            Handle the value changing in the spinbox
            """
            self.updateData.emit(self)

    class BitfieldPropertyDecoder(PropertyDecoder):
        """
        Class that decodes/encodes sprite data to/from a bitfield
        """

        def __init__(self, title, startbit, bitnum, comment, layout, row):
            """
            Creates the widget
            """
            super().__init__()

            self.startbit = startbit
            self.bitnum = bitnum

            self.widgets = []
            CheckboxLayout = QtWidgets.QGridLayout()
            CheckboxLayout.setContentsMargins(0, 0, 0, 0)
            for i in range(bitnum):
                c = QtWidgets.QCheckBox()
                self.widgets.append(c)
                CheckboxLayout.addWidget(c, 0, i)
                if comment is not None: c.setToolTip(comment)
                c.toggled.connect(self.HandleValueChanged)

                L = QtWidgets.QLabel(str(i + 1))
                CheckboxLayout.addWidget(L, 1, i)
                CheckboxLayout.setAlignment(L, Qt.AlignHCenter)

            w = QtWidgets.QWidget()
            w.setLayout(CheckboxLayout)

            layout.addWidget(QtWidgets.QLabel(title + ':'), row, 0, Qt.AlignRight)
            layout.addWidget(w, row, 1)

        def update(self, data):
            """
            Updates the value shown by the widget
            """
            for bitIdx in range(self.bitnum):
                checkbox = self.widgets[bitIdx]

                adjustedIdx = bitIdx + self.startbit
                byteNum = adjustedIdx // 8
                bitNum = adjustedIdx % 8
                checkbox.setChecked((data[byteNum] >> (7 - bitNum) & 1))

        def assign(self, data):
            """
            Assigns the checkbox states to the data
            """
            data = bytearray(data)

            for idx in range(self.bitnum):
                checkbox = self.widgets[idx]

                adjustedIdx = idx + self.startbit
                byteIdx = adjustedIdx // 8
                bitIdx = adjustedIdx % 8

                origByte = data[byteIdx]
                origBit = (origByte >> (7 - bitIdx)) & 1
                newBit = 1 if checkbox.isChecked() else 0

                if origBit == newBit: continue
                if origBit == 0 and newBit == 1:
                    # Turn the byte on by OR-ing it in
                    newByte = (origByte | (1 << (7 - bitIdx))) & 0xFF
                else:
                    # Turn it off by:
                    # inverting it
                    # OR-ing in the new byte
                    # inverting it back
                    newByte = ~origByte & 0xFF
                    newByte = newByte | (1 << (7 - bitIdx))
                    newByte = ~newByte & 0xFF

                data[byteIdx] = newByte

            return bytes(data)

        @QtCore.pyqtSlot(int)
        def HandleValueChanged(self, value):
            """
            Handle any checkbox being changed
            """
            self.updateData.emit(self)

    def setSprite(self, type, reset=False):
        """
        Change the sprite type used by the data editor
        """
        if (self.spritetype == type) and not reset: return

        self.spritetype = type
        if type != 1000:
            sprite = globals.Sprites[type]
        else:
            sprite = None

        # remove all the existing widgets in the layout
        layout = self.editorlayout
        for row in range(2, layout.rowCount()):
            for column in range(0, layout.columnCount()):
                w = layout.itemAtPosition(row, column)
                if w is not None:
                    widget = w.widget()
                    layout.removeWidget(widget)
                    widget.setParent(None)

        if sprite is None:
            self.spriteLabel.setText(globals.trans.string('SpriteDataEditor', 5, '[id]', type))
            self.noteButton.setVisible(False)

            # use the raw editor if nothing is there
            self.raweditor.setVisible(True)
            if len(self.fields) > 0: self.fields = []

        else:
            self.spriteLabel.setText(globals.trans.string('SpriteDataEditor', 6, '[id]', type, '[name]', sprite.name))

            self.noteButton.setVisible(sprite.notes is not None)
            self.notes = sprite.notes

            self.relatedObjFilesButton.setVisible(sprite.relatedObjFiles is not None)
            self.relatedObjFiles = sprite.relatedObjFiles

            # create all the new fields
            fields = []
            row = 2

            for f in sprite.fields:
                if f[0] == 0:
                    nf = SpriteEditorWidget.CheckboxPropertyDecoder(f[1], f[2], f[3], f[4], layout, row)
                elif f[0] == 1:
                    nf = SpriteEditorWidget.ListPropertyDecoder(f[1], f[2], f[3], f[4], layout, row)
                elif f[0] == 2:
                    nf = SpriteEditorWidget.ValuePropertyDecoder(f[1], f[2], f[3], f[4], layout, row)
                elif f[0] == 3:
                    nf = SpriteEditorWidget.BitfieldPropertyDecoder(f[1], f[2], f[3], f[4], layout, row)

                nf.updateData.connect(self.HandleFieldUpdate)
                fields.append(nf)
                row += 1

            self.fields = fields

    def update(self):
        """
        Updates all the fields to display the appropriate info
        """
        self.UpdateFlag = True

        data = self.data
        self.raweditor.setText('%02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x' % (
        data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]))
        self.raweditor.setStyleSheet('')

        # Go through all the data
        for f in self.fields:
            f.update(data)

        self.UpdateFlag = False

    @QtCore.pyqtSlot()
    def ShowNoteTooltip(self):
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), self.notes, self)

    @QtCore.pyqtSlot()
    def ShowRelatedObjFilesTooltip(self):
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), self.relatedObjFiles, self)

    @QtCore.pyqtSlot('PyQt_PyObject')
    def HandleFieldUpdate(self, field):
        """
        Triggered when a field's data is updated
        """
        if self.UpdateFlag: return

        data = field.assign(self.data)
        self.data = data

        self.raweditor.setText('%02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x' % (
        data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]))
        self.raweditor.setStyleSheet('')

        for f in self.fields:
            if f != field: f.update(data)

        self.DataUpdate.emit(data)

    @QtCore.pyqtSlot(str)
    def HandleRawDataEdited(self, text):
        """
        Triggered when the raw data textbox is edited
        """

        raw = text.replace(' ', '')
        valid = False

        if len(raw) == 24:
            try:
                data = []
                for r in range(0, len(raw), 2):
                    data.append(int(raw[r:r + 2], 16))
                data = bytes(data)
                valid = True
            except Exception:
                pass

        # if it's valid, let it go
        if valid:
            self.raweditor.setStyleSheet('')
            self.data = data

            self.UpdateFlag = True
            for f in self.fields: f.update(data)
            self.UpdateFlag = False

            self.DataUpdate.emit(data)
            self.raweditor.setStyleSheet('QLineEdit { background-color: #ffffff; }')
        else:
            self.raweditor.setStyleSheet('QLineEdit { background-color: #ffd2d2; }')


class EntranceEditorWidget(QtWidgets.QWidget):
    """
    Widget for editing entrance properties
    """

    @QtCore.pyqtSlot()
    def __init__(self, defaultmode=False):
        """
        Constructor
        """
        super().__init__()
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))

        # create widgets
        self.entranceID = QtWidgets.QSpinBox()
        self.entranceID.setRange(0, 255)
        self.entranceID.setToolTip(globals.trans.string('EntranceDataEditor', 1))
        self.entranceID.valueChanged.connect(self.HandleEntranceIDChanged)

        self.entranceType = QtWidgets.QComboBox()
        LoadEntranceNames()
        self.entranceType.addItems(globals.EntranceTypeNames)
        self.entranceType.setToolTip(globals.trans.string('EntranceDataEditor', 3))
        self.entranceType.activated.connect(self.HandleEntranceTypeChanged)

        self.destArea = QtWidgets.QSpinBox()
        self.destArea.setRange(0, 4)
        self.destArea.setToolTip(globals.trans.string('EntranceDataEditor', 7))
        self.destArea.valueChanged.connect(self.HandleDestAreaChanged)

        self.destEntrance = QtWidgets.QSpinBox()
        self.destEntrance.setRange(0, 255)
        self.destEntrance.setToolTip(globals.trans.string('EntranceDataEditor', 5))
        self.destEntrance.valueChanged.connect(self.HandleDestEntranceChanged)

        self.allowEntryCheckbox = QtWidgets.QCheckBox(globals.trans.string('EntranceDataEditor', 8))
        self.allowEntryCheckbox.setToolTip(globals.trans.string('EntranceDataEditor', 9))
        self.allowEntryCheckbox.clicked.connect(self.HandleAllowEntryClicked)

        self.unk05 = QtWidgets.QSpinBox()
        self.unk05.setRange(0, 255)
        self.unk05.setToolTip('Unknown 0x05')
        self.unk05.valueChanged.connect(self.HandleUnk05)
        self.unk0C = QtWidgets.QSpinBox()
        self.unk0C.setRange(0, 255)
        self.unk0C.setToolTip('Ambush related')
        self.unk0C.setToolTip('Related to ambushes...')
        self.unk0C.valueChanged.connect(self.HandleUnk0C)
        self.unk0F = QtWidgets.QSpinBox()
        self.unk0F.setRange(0, 255)
        self.unk0F.setToolTip('Multiplayer Related')
        self.unk0F.setToolTip('Possibly related to multiplayer?')
        self.unk0F.valueChanged.connect(self.HandleUnk0F)
        self.unk12 = QtWidgets.QSpinBox()
        self.unk12.setRange(0, 255)
        self.unk12.setToolTip('Unknown 0x12')
        self.unk12.valueChanged.connect(self.HandleUnk12)
        self.camera = QtWidgets.QSpinBox()
        self.camera.setRange(0, 255)
        self.camera.setToolTip(
            'Related to camera movement. Value of 1 makes the camera zoom in if the value is < 0, or out if it\'s >= 0.')
        self.camera.valueChanged.connect(self.HandleCamera)

        self.pathID = QtWidgets.QSpinBox()
        self.pathID.setRange(0, 255)
        self.pathID.setToolTip('The Path ID, for autoscroll purposes.')
        self.pathID.valueChanged.connect(self.HandlePathID)

        self.pathnodeindex = QtWidgets.QSpinBox()
        self.pathnodeindex.setRange(0, 255)
        self.pathnodeindex.setToolTip('The Path Node Index, for autoscroll purposes.')
        self.pathnodeindex.valueChanged.connect(self.HandlePathNodeIndex)

        self.unk16 = QtWidgets.QSpinBox()
        self.unk16.setRange(0, 255)
        self.unk16.setToolTip('Unknown 0x16')
        self.unk16.valueChanged.connect(self.HandleUnk16)

        # create a layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # 'Editing Entrance #' label
        self.editingLabel = QtWidgets.QLabel('-')
        layout.addWidget(self.editingLabel, 0, 0, 1, 4, Qt.AlignTop)

        # add labels
        layout.addWidget(QtWidgets.QLabel(globals.trans.string('EntranceDataEditor', 2)), 1, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(globals.trans.string('EntranceDataEditor', 0)), 3, 0, 1, 1, Qt.AlignRight)

        layout.addWidget(createHorzLine(), 2, 0, 1, 4)

        layout.addWidget(QtWidgets.QLabel(globals.trans.string('EntranceDataEditor', 4)), 3, 2, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(globals.trans.string('EntranceDataEditor', 6)), 4, 2, 1, 1, Qt.AlignRight)

        # add the widgets
        layout.addWidget(self.entranceType, 1, 1, 1, 3)
        layout.addWidget(self.entranceID, 3, 1, 1, 1)

        layout.addWidget(self.destEntrance, 3, 3, 1, 1)
        layout.addWidget(self.destArea, 4, 3, 1, 1)
        layout.addWidget(createHorzLine(), 5, 0, 1, 4)
        layout.addWidget(self.allowEntryCheckbox, 6, 0, 1, 2)  # , Qt.AlignRight)
        layout.addWidget(createHorzLine(), 7, 0, 1, 4)

        layout.addWidget(QtWidgets.QLabel('Unknown 0x05:'), 8, 0)
        layout.addWidget(QtWidgets.QLabel('Ambush Related:'), 9, 0)
        layout.addWidget(QtWidgets.QLabel('Multiplayer Related:'), 10, 0)
        layout.addWidget(QtWidgets.QLabel('Unknown 0x12:'), 11, 0)
        layout.addWidget(QtWidgets.QLabel('Camera Related:'), 12, 0)
        layout.addWidget(QtWidgets.QLabel('Path ID:'), 13, 0)
        layout.addWidget(QtWidgets.QLabel('Path Node Index:'), 14, 0)
        layout.addWidget(QtWidgets.QLabel('Unknown 0x16:'), 15, 0)
        layout.addWidget(self.unk05, 8, 1)
        layout.addWidget(self.unk0C, 9, 1)
        layout.addWidget(self.unk0F, 10, 1)
        layout.addWidget(self.unk12, 11, 1)
        layout.addWidget(self.camera, 12, 1)
        layout.addWidget(self.pathID, 13, 1)
        layout.addWidget(self.pathnodeindex, 14, 1)
        layout.addWidget(self.unk16, 15, 1)

        self.ent = None
        self.UpdateFlag = False

    @QtCore.pyqtSlot()
    def setEntrance(self, ent):
        """
        Change the entrance being edited by the editor, update all fields
        """
        if self.ent == ent: return

        self.editingLabel.setText(globals.trans.string('EntranceDataEditor', 23, '[id]', ent.entid))
        self.ent = ent
        self.UpdateFlag = True

        self.entranceID.setValue(ent.entid)
        self.entranceType.setCurrentIndex(ent.enttype)
        self.destArea.setValue(ent.destarea)
        self.destEntrance.setValue(ent.destentrance)

        self.unk05.setValue(ent.unk05)
        self.unk0C.setValue(ent.unk0C)
        self.unk0F.setValue(ent.unk0F)
        self.unk12.setValue(ent.unk12)
        self.camera.setValue(ent.camera)
        self.pathID.setValue(ent.pathID)
        self.pathnodeindex.setValue(ent.pathnodeindex)
        self.unk16.setValue(ent.unk16)

        self.allowEntryCheckbox.setChecked(((ent.entsettings & 0x80) == 0))

        self.UpdateFlag = False

    @QtCore.pyqtSlot(int)
    def HandleEntranceIDChanged(self, i):
        """
        Handler for the entrance ID changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.ent.entid = i
        self.ent.update()
        self.ent.UpdateTooltip()
        self.ent.UpdateListItem()
        self.editingLabel.setText(globals.trans.string('EntranceDataEditor', 23, '[id]', i))

    @QtCore.pyqtSlot(int)
    def HandleEntranceTypeChanged(self, i):
        """
        Handler for the entrance type changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.ent.enttype = i
        self.ent.TypeChange()
        self.ent.update()
        self.ent.UpdateTooltip()
        globals.mainWindow.scene.update()
        self.ent.UpdateListItem()

    @QtCore.pyqtSlot(int)
    def HandleDestAreaChanged(self, i):
        """
        Handler for the destination area changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.ent.destarea = i
        self.ent.UpdateTooltip()
        self.ent.UpdateListItem()

    @QtCore.pyqtSlot(int)
    def HandleDestEntranceChanged(self, i):
        """
        Handler for the destination entrance changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.ent.destentrance = i
        self.ent.UpdateTooltip()
        self.ent.UpdateListItem()

    @QtCore.pyqtSlot(int)
    def HandleUnk05(self, i):
        if self.UpdateFlag: return
        SetDirty()
        self.ent.unk05 = i
        self.ent.UpdateTooltip()
        self.ent.UpdateListItem()

    @QtCore.pyqtSlot(int)
    def HandleUnk0C(self, i):
        if self.UpdateFlag: return
        SetDirty()
        self.ent.unk0C = i
        self.ent.UpdateTooltip()
        self.ent.UpdateListItem()

    @QtCore.pyqtSlot(int)
    def HandleUnk0F(self, i):
        if self.UpdateFlag: return
        SetDirty()
        self.ent.unk0F = i
        self.ent.UpdateTooltip()
        self.ent.UpdateListItem()

    @QtCore.pyqtSlot(int)
    def HandleUnk12(self, i):
        if self.UpdateFlag: return
        SetDirty()
        self.ent.unk12 = i
        self.ent.UpdateTooltip()
        self.ent.UpdateListItem()

    @QtCore.pyqtSlot(int)
    def HandleCamera(self, i):
        if self.UpdateFlag: return
        SetDirty()
        self.ent.camera = i
        self.ent.UpdateTooltip()
        self.ent.UpdateListItem()

    @QtCore.pyqtSlot(int)
    def HandlePathID(self, i):
        if self.UpdateFlag: return
        SetDirty()
        self.ent.pathID = i
        self.ent.UpdateTooltip()
        self.ent.UpdateListItem()

    @QtCore.pyqtSlot(int)
    def HandlePathNodeIndex(self, i):
        if self.UpdateFlag: return
        SetDirty()
        self.ent.pathnodeindex = i
        self.ent.UpdateTooltip()
        self.ent.UpdateListItem()

    @QtCore.pyqtSlot(int)
    def HandleUnk16(self, i):
        if self.UpdateFlag: return
        SetDirty()
        self.ent.unk16 = i
        self.ent.UpdateTooltip()
        self.ent.UpdateListItem()

    @QtCore.pyqtSlot(bool)
    def HandleAllowEntryClicked(self, checked):
        """
        Handle for the Allow Entry checkbox being clicked
        """
        if self.UpdateFlag: return
        SetDirty()
        if not checked:
            self.ent.entsettings |= 0x80
        else:
            self.ent.entsettings &= ~0x80
        self.ent.UpdateTooltip()
        self.ent.UpdateListItem()

    @QtCore.pyqtSlot(bool)
    def HandleUnknownFlagClicked(self, checked):
        """
        Handle for the Unknown Flag checkbox being clicked
        """
        if self.UpdateFlag: return
        SetDirty()
        if checked:
            self.ent.entsettings |= 2
        else:
            self.ent.entsettings &= ~2

    @QtCore.pyqtSlot(int)
    def HandleActiveLayerChanged(self, i):
        """
        Handle for the active layer changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.ent.entlayer = i


class PathNodeEditorWidget(QtWidgets.QWidget):
    """
    Widget for editing path node properties
    """

    def __init__(self, defaultmode=False):
        """
        Constructor
        """
        super().__init__()
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))

        # create widgets
        # [20:52:41]  [Angel-SL] 1. (readonly) pathid 2. (readonly) nodeid 3. x 4. y 5. speed (float spinner) 6. accel (float spinner)
        # not doing [20:52:58]  [Angel-SL] and 2 buttons - 7. 'Move Up' 8. 'Move Down'
        self.speed = QtWidgets.QDoubleSpinBox()
        self.speed.setRange(min(sys.float_info), max(sys.float_info))
        self.speed.setToolTip(globals.trans.string('PathDataEditor', 3))
        self.speed.setDecimals(int(sys.float_info.__getattribute__('dig')))
        self.speed.valueChanged.connect(self.HandleSpeedChanged)
        self.speed.setMaximumWidth(256)

        self.accel = QtWidgets.QDoubleSpinBox()
        self.accel.setRange(min(sys.float_info), max(sys.float_info))
        self.accel.setToolTip(globals.trans.string('PathDataEditor', 5))
        self.accel.setDecimals(int(sys.float_info.__getattribute__('dig')))
        self.accel.valueChanged.connect(self.HandleAccelChanged)
        self.accel.setMaximumWidth(256)

        self.delay = QtWidgets.QSpinBox()
        self.delay.setRange(0, 65535)
        self.delay.setToolTip(globals.trans.string('PathDataEditor', 7))
        self.delay.valueChanged.connect(self.HandleDelayChanged)
        self.delay.setMaximumWidth(256)

        self.loops = QtWidgets.QCheckBox()
        self.loops.setToolTip(globals.trans.string('PathDataEditor', 1))
        self.loops.stateChanged.connect(self.HandleLoopsChanged)

        self.unk1 = QtWidgets.QSpinBox()
        self.unk1.setRange(-127, 127)
        self.unk1.setToolTip(globals.trans.string('PathDataEditor', 12))
        self.unk1.valueChanged.connect(self.Handleunk1Changed)
        self.unk1.setMaximumWidth(256)

        # create a layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # 'Editing Path #' label
        self.editingLabel = QtWidgets.QLabel('-')
        self.editingPathLabel = QtWidgets.QLabel('-')
        layout.addWidget(self.editingLabel, 3, 0, 1, 2, Qt.AlignTop)
        layout.addWidget(self.editingPathLabel, 0, 0, 1, 2, Qt.AlignTop)
        # add labels
        layout.addWidget(QtWidgets.QLabel(globals.trans.string('PathDataEditor', 0)), 1, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(globals.trans.string('PathDataEditor', 2)), 4, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(globals.trans.string('PathDataEditor', 4)), 5, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(globals.trans.string('PathDataEditor', 6)), 6, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(globals.trans.string('PathDataEditor', 11)), 7, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(createHorzLine(), 2, 0, 1, 2)

        # add the widgets
        layout.addWidget(self.loops, 1, 1)
        layout.addWidget(self.speed, 4, 1)
        layout.addWidget(self.accel, 5, 1)
        layout.addWidget(self.delay, 6, 1)
        layout.addWidget(self.unk1, 7, 1)

        self.path = None
        self.UpdateFlag = False

    def setPath(self, path):
        """
        Change the path being edited by the editor, update all fields
        """
        if self.path == path: return
        self.editingPathLabel.setText(globals.trans.string('PathDataEditor', 8, '[id]', path.pathid))
        self.editingLabel.setText(globals.trans.string('PathDataEditor', 9, '[id]', path.nodeid))
        self.path = path
        self.UpdateFlag = True

        self.speed.setValue(path.nodeinfo['speed'])
        self.accel.setValue(path.nodeinfo['accel'])
        self.delay.setValue(path.nodeinfo['delay'])
        self.loops.setChecked(path.pathinfo['loops'])

        self.UpdateFlag = False

    @QtCore.pyqtSlot(float)
    def HandleSpeedChanged(self, i):
        """
        Handler for the speed changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.path.nodeinfo['speed'] = i

    @QtCore.pyqtSlot(float)
    def HandleAccelChanged(self, i):
        """
        Handler for the accel changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.path.nodeinfo['accel'] = i

    @QtCore.pyqtSlot(int)
    def HandleDelayChanged(self, i):
        """
        Handler for the delay changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.path.nodeinfo['delay'] = i

    @QtCore.pyqtSlot(int)
    def Handleunk1Changed(self, i):
        """
        Handler for the delay changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.path.nodeinfo['unk1'] = i

    @QtCore.pyqtSlot(int)
    def HandleLoopsChanged(self, i):
        if self.UpdateFlag: return
        SetDirty()
        self.path.pathinfo['loops'] = (i == Qt.Checked)
        self.path.pathinfo['peline'].loops = (i == Qt.Checked)
        globals.mainWindow.scene.update()


class LocationEditorWidget(QtWidgets.QWidget):
    """
    Widget for editing location properties
    """

    def __init__(self, defaultmode=False):
        """
        Constructor
        """
        super().__init__()
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))

        # create widgets
        self.locationID = QtWidgets.QSpinBox()
        self.locationID.setToolTip(globals.trans.string('LocationDataEditor', 1))
        self.locationID.setRange(0, 255)
        self.locationID.valueChanged.connect(self.HandleLocationIDChanged)

        self.locationX = QtWidgets.QSpinBox()
        self.locationX.setToolTip(globals.trans.string('LocationDataEditor', 3))
        self.locationX.setRange(16, 65535)
        self.locationX.valueChanged.connect(self.HandleLocationXChanged)

        self.locationY = QtWidgets.QSpinBox()
        self.locationY.setToolTip(globals.trans.string('LocationDataEditor', 5))
        self.locationY.setRange(16, 65535)
        self.locationY.valueChanged.connect(self.HandleLocationYChanged)

        self.locationWidth = QtWidgets.QSpinBox()
        self.locationWidth.setToolTip(globals.trans.string('LocationDataEditor', 7))
        self.locationWidth.setRange(1, 65535)
        self.locationWidth.valueChanged.connect(self.HandleLocationWidthChanged)

        self.locationHeight = QtWidgets.QSpinBox()
        self.locationHeight.setToolTip(globals.trans.string('LocationDataEditor', 9))
        self.locationHeight.setRange(1, 65535)
        self.locationHeight.valueChanged.connect(self.HandleLocationHeightChanged)

        self.snapButton = QtWidgets.QPushButton(globals.trans.string('LocationDataEditor', 10))
        self.snapButton.clicked.connect(self.HandleSnapToGrid)

        # create a layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # 'Editing Location #' label
        self.editingLabel = QtWidgets.QLabel('-')
        layout.addWidget(self.editingLabel, 0, 0, 1, 4, Qt.AlignTop)

        # add labels
        layout.addWidget(QtWidgets.QLabel(globals.trans.string('LocationDataEditor', 0)), 1, 0, 1, 1, Qt.AlignRight)

        layout.addWidget(createHorzLine(), 2, 0, 1, 4)

        layout.addWidget(QtWidgets.QLabel(globals.trans.string('LocationDataEditor', 2)), 3, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(globals.trans.string('LocationDataEditor', 4)), 4, 0, 1, 1, Qt.AlignRight)

        layout.addWidget(QtWidgets.QLabel(globals.trans.string('LocationDataEditor', 6)), 3, 2, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(globals.trans.string('LocationDataEditor', 8)), 4, 2, 1, 1, Qt.AlignRight)

        # add the widgets
        layout.addWidget(self.locationID, 1, 1, 1, 1)
        layout.addWidget(self.snapButton, 1, 3, 1, 1)

        layout.addWidget(self.locationX, 3, 1, 1, 1)
        layout.addWidget(self.locationY, 4, 1, 1, 1)

        layout.addWidget(self.locationWidth, 3, 3, 1, 1)
        layout.addWidget(self.locationHeight, 4, 3, 1, 1)

        self.loc = None
        self.UpdateFlag = False

    def setLocation(self, loc):
        """
        Change the location being edited by the editor, update all fields
        """
        self.loc = loc
        self.UpdateFlag = True

        self.FixTitle()
        self.locationID.setValue(loc.id)
        self.locationX.setValue(loc.objx)
        self.locationY.setValue(loc.objy)
        self.locationWidth.setValue(loc.width)
        self.locationHeight.setValue(loc.height)

        self.UpdateFlag = False

    def FixTitle(self):
        self.editingLabel.setText(globals.trans.string('LocationDataEditor', 11, '[id]', self.loc.id))

    @QtCore.pyqtSlot(int)
    def HandleLocationIDChanged(self, i):
        """
        Handler for the location ID changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.loc.id = i
        self.loc.update()
        self.loc.UpdateTitle()
        self.FixTitle()

    @QtCore.pyqtSlot(int)
    def HandleLocationXChanged(self, i):
        """
        Handler for the location X-pos changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.loc.objx = i
        self.loc.autoPosChange = True
        self.loc.setX(int(i * globals.TileWidth / 16))
        self.loc.autoPosChange = False
        self.loc.UpdateRects()
        self.loc.update()

    @QtCore.pyqtSlot(int)
    def HandleLocationYChanged(self, i):
        """
        Handler for the location Y-pos changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.loc.objy = i
        self.loc.autoPosChange = True
        self.loc.setY(int(i * globals.TileWidth / 16))
        self.loc.autoPosChange = False
        self.loc.UpdateRects()
        self.loc.update()

    @QtCore.pyqtSlot(int)
    def HandleLocationWidthChanged(self, i):
        """
        Handler for the location width changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.loc.width = i
        self.loc.UpdateRects()
        self.loc.update()

    @QtCore.pyqtSlot(int)
    def HandleLocationHeightChanged(self, i):
        """
        Handler for the location height changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.loc.height = i
        self.loc.UpdateRects()
        self.loc.update()

    @QtCore.pyqtSlot()
    def HandleSnapToGrid(self):
        """
        Snaps the current location to an 8x8 grid
        """
        SetDirty()

        loc = self.loc
        left = loc.objx
        top = loc.objy
        right = left + loc.width
        bottom = top + loc.height

        if left % 8 < 4:
            left -= (left % 8)
        else:
            left += 8 - (left % 8)

        if top % 8 < 4:
            top -= (top % 8)
        else:
            top += 8 - (top % 8)

        if right % 8 < 4:
            right -= (right % 8)
        else:
            right += 8 - (right % 8)

        if bottom % 8 < 4:
            bottom -= (bottom % 8)
        else:
            bottom += 8 - (bottom % 8)

        if right <= left: right += 8
        if bottom <= top: bottom += 8

        loc.objx = left
        loc.objy = top
        loc.width = right - left
        loc.height = bottom - top

        loc.setPos(int(left * globals.TileWidth / 16), int(top * globals.TileWidth / 16))
        loc.UpdateRects()
        loc.update()
        self.setLocation(loc)  # updates the fields


class LoadingTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.unk1 = QtWidgets.QSpinBox()
        self.unk1.setRange(0, 0x255)
        self.unk1.setToolTip(globals.trans.string('AreaDlg', 25))
        self.unk1.setValue(globals.Area.unk1)

        self.unk2 = QtWidgets.QSpinBox()
        self.unk2.setRange(0, 255)
        self.unk2.setToolTip(globals.trans.string('AreaDlg', 25))
        self.unk2.setValue(globals.Area.unk2)

        self.timer = QtWidgets.QSpinBox()
        self.timer.setRange(0, 999)
        self.timer.setToolTip(globals.trans.string('AreaDlg', 4))
        self.timer.setValue(globals.Area.timelimit)

        self.timelimit2 = QtWidgets.QSpinBox()
        self.timelimit2.setRange(0, 999)
        self.timelimit2.setToolTip(globals.trans.string('AreaDlg', 38))
        self.timelimit2.setValue(globals.Area.timelimit2 - 100)

        self.timelimit3 = QtWidgets.QSpinBox()
        self.timelimit3.setRange(200, 999)
        self.timelimit3.setToolTip(globals.trans.string('AreaDlg', 38))
        self.timelimit3.setValue(globals.Area.timelimit3 + 200)

        self.unk3 = QtWidgets.QSpinBox()
        self.unk3.setRange(0, 999)
        self.unk3.setToolTip(globals.trans.string('AreaDlg', 26))
        self.unk3.setValue(globals.Area.unk3)

        self.unk4 = QtWidgets.QSpinBox()
        self.unk4.setRange(0, 999)
        self.unk4.setToolTip(globals.trans.string('AreaDlg', 26))
        self.unk4.setValue(globals.Area.unk4)

        self.unk5 = QtWidgets.QSpinBox()
        self.unk5.setRange(0, 999)
        self.unk5.setToolTip(globals.trans.string('AreaDlg', 26))
        self.unk5.setValue(globals.Area.unk5)

        self.unk6 = QtWidgets.QSpinBox()
        self.unk6.setRange(0, 999)
        self.unk6.setToolTip(globals.trans.string('AreaDlg', 26))
        self.unk6.setValue(globals.Area.unk6)

        self.unk7 = QtWidgets.QSpinBox()
        self.unk7.setRange(0, 999)
        self.unk7.setToolTip(globals.trans.string('AreaDlg', 26))
        self.unk7.setValue(globals.Area.unk7)

        settingsLayout = QtWidgets.QFormLayout()
        settingsLayout.addRow(globals.trans.string('AreaDlg', 22), self.unk1)
        settingsLayout.addRow(globals.trans.string('AreaDlg', 23), self.unk2)
        settingsLayout.addRow(globals.trans.string('AreaDlg', 3), self.timer)
        settingsLayout.addRow(globals.trans.string('AreaDlg', 36), self.timelimit2)
        settingsLayout.addRow(globals.trans.string('AreaDlg', 37), self.timelimit3)
        settingsLayout.addRow(globals.trans.string('AreaDlg', 24), self.unk3)
        settingsLayout.addRow(globals.trans.string('AreaDlg', 32), self.unk4)
        settingsLayout.addRow(globals.trans.string('AreaDlg', 33), self.unk5)
        settingsLayout.addRow(globals.trans.string('AreaDlg', 34), self.unk6)
        settingsLayout.addRow(globals.trans.string('AreaDlg', 35), self.unk7)

        Layout = QtWidgets.QVBoxLayout()
        Layout.addLayout(settingsLayout)
        Layout.addStretch(1)
        self.setLayout(Layout)


class TilesetsTab(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.tile0 = QtWidgets.QComboBox()

        name = globals.Area.tileset0
        slot = self.HandleTileset0Choice

        self.currentChoice = None

        data = SimpleTilesetNames()

        # First, find the current index and custom-tileset strings
        if name == '':  # No tileset selected, the current index should be None
            ts_index = globals.trans.string('AreaDlg', 15)  # None
            custom = ''
            custom_fname = globals.trans.string('AreaDlg', 16)  # [CUSTOM]
        else:  # Tileset selected
            ts_index = globals.trans.string('AreaDlg', 18, '[name]', name)  # Custom filename... [name]
            custom = name
            custom_fname = globals.trans.string('AreaDlg', 17, '[name]', name)  # [CUSTOM] [name]

        # Add items to the widget:
        # - None
        self.tile0.addItem(globals.trans.string('AreaDlg', 15), '')  # None
        # - Retail Tilesets
        for tfile, tname in data:
            text = globals.trans.string('AreaDlg', 19, '[name]', tname, '[file]', tfile)  # [name] ([file])
            self.tile0.addItem(text, tfile)
            if name == tfile:
                ts_index = text
                custom = ''
        # - Custom Tileset
        self.tile0.addItem(globals.trans.string('AreaDlg', 18, '[name]', custom), custom_fname)  # Custom filename... [name]

        # Set the current index
        item_idx = self.tile0.findText(ts_index)
        self.currentChoice = item_idx
        self.tile0.setCurrentIndex(item_idx)

        # Handle combobox changes
        self.tile0.activated.connect(slot)

        # don't allow ts0 to be removable
        self.tile0.removeItem(0)

        mainLayout = QtWidgets.QVBoxLayout()
        tile0Box = QtWidgets.QGroupBox(globals.trans.string('AreaDlg', 11))

        t0 = QtWidgets.QVBoxLayout()
        t0.addWidget(self.tile0)

        tile0Box.setLayout(t0)

        mainLayout.addWidget(tile0Box)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)

    @QtCore.pyqtSlot(int)
    def HandleTileset0Choice(self, index):
        w = self.tile0

        if index == (w.count() - 1):
            fname = str(w.itemData(index))
            fname = fname[len(globals.trans.string('AreaDlg', 17, '[name]', '')):]

            dbox = InputBox()
            dbox.setWindowTitle(globals.trans.string('AreaDlg', 20))
            dbox.label.setText(globals.trans.string('AreaDlg', 21))
            dbox.textbox.setMaxLength(31)
            dbox.textbox.setText(fname)
            result = dbox.exec_()

            if result == QtWidgets.QDialog.Accepted:
                fname = str(dbox.textbox.text())
                if fname.endswith('.szs') or fname.endswith('.sarc'): fname = fname[:-3]

                w.setItemText(index, globals.trans.string('AreaDlg', 18, '[name]', fname))
                w.setItemData(index, globals.trans.string('AreaDlg', 17, '[name]', fname))
            else:
                w.setCurrentIndex(self.currentChoice)
                return

        self.currentChoice = index

    def value(self):
        """
        Returns the main tileset choice
        """
        idx = self.tile0.currentIndex()
        name = str(self.tile0.itemData(idx))
        return name


class LevelViewWidget(QtWidgets.QGraphicsView):
    """
    QGraphicsView subclass for the level view
    """
    PositionHover = QtCore.pyqtSignal(int, int)
    FrameSize = QtCore.pyqtSignal(int, int)
    repaint = QtCore.pyqtSignal()
    dragstamp = False

    def __init__(self, scene, parent):
        """
        Constructor
        """
        super().__init__(scene, parent)

        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(119,136,153)))
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        # self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setMouseTracking(True)
        # self.setOptimizationFlags(QtWidgets.QGraphicsView.IndirectPainting)
        self.YScrollBar = QtWidgets.QScrollBar(Qt.Vertical, parent)
        self.XScrollBar = QtWidgets.QScrollBar(Qt.Horizontal, parent)
        self.setVerticalScrollBar(self.YScrollBar)
        self.setHorizontalScrollBar(self.XScrollBar)

        self.currentobj = None

        self.setRenderHints(QtGui.QPainter.Antialiasing | QtGui.QPainter.SmoothPixmapTransform)

    def mousePressEvent(self, event):
        """
        Overrides mouse pressing events if needed
        """
        if event.button() == Qt.RightButton:
            if globals.CurrentPaintType in (0, 1, 2, 3) and globals.CurrentObject != -1:
                # paint an object
                clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)
                clickedx = int(clicked.x() / globals.TileWidth)
                clickedy = int(clicked.y() / globals.TileWidth)

                ln = globals.CurrentLayer
                layer = globals.Area.layers[globals.CurrentLayer]
                if len(layer) == 0:
                    z = (2 - ln) * 8192
                else:
                    z = layer[-1].zValue() + 1

                obj = ObjectItem(globals.CurrentPaintType, globals.CurrentObject, ln, clickedx, clickedy, 1, 1, z, 0)
                layer.append(obj)
                mw = globals.mainWindow
                obj.positionChanged = mw.HandleObjPosChange
                mw.scene.addItem(obj)

                self.dragstamp = False
                self.currentobj = obj
                self.dragstartx = clickedx
                self.dragstarty = clickedy
                SetDirty()

            elif globals.CurrentPaintType == 10 and globals.CurrentObject != -1:
                # See if the object is addable to and add it
                type_ = globals.CurrentObject
                if globals.CurrentObject in globals.ObjectAddedtoEmbedded[globals.CurrentArea][globals.mainWindow.folderPicker.currentIndex()]:
                    (globals.CurrentPaintType,
                     globals.CurrentObject) = globals.ObjectAddedtoEmbedded[globals.CurrentArea][globals.mainWindow.folderPicker.currentIndex()][
                         globals.CurrentObject]
                else:
                    for idx in range(1, 4):
                        usedTiles = getUsedTiles()[idx]
                        if len(usedTiles) >= 256:  # It can't be more than 256, oh well
                            continue

                        numTiles = 0
                        obj = globals.ObjectAllDefinitions[globals.CurrentObject]
                        for row in obj.rows:
                            for tile in row:
                                if len(tile) == 3:
                                    numTiles += 1

                        if numTiles + len(usedTiles) > 256:
                            continue

                        tileoffset = idx * 256

                        freeTiles = []
                        for i in range(256):
                            if i not in usedTiles: freeTiles.append(i)

                        ctile = 0
                        crow = 0
                        i = 0
                        for row in obj.rows:
                            for tile in row:
                                if len(tile) == 3:
                                    obj.rows[crow][ctile][1] = freeTiles[i] | (idx << 8)
                                    i += 1
                                ctile += 1
                            crow += 1
                            ctile = 0

                        if globals.ObjectDefinitions[idx] is None:
                            globals.ObjectDefinitions[idx] = [None] * 256

                        defs = globals.ObjectDefinitions[idx]

                        objNum = 0
                        while defs[objNum] is not None and objNum < 256:
                            objNum += 1

                        globals.ObjectDefinitions[idx][objNum] = obj

                        colldata = globals.ObjectAllCollisions[globals.CurrentObject]
                        img, nml = globals.ObjectAllImages[globals.CurrentObject]

                        # Checks if the slop is reversed and reverses the rows
                        isSlope = obj.rows[0][0][0]
                        if (isSlope & 0x80) and (isSlope & 0x2):
                            x = 0
                            y = (obj.height - 1) * 60
                            i = 0
                            crow = 0
                            for row in obj.rows:
                                for tile in row:
                                    if len(tile) == 3:
                                        tileNum = (tile[1] & 0xFF) + tileoffset
                                        T = TilesetTile(img.copy(x, y, 60, 60), nml.copy(x, y, 60, 60))
                                        realRow = len(obj.rows) - 1 - crow
                                        colls = struct.unpack_from('>8B', colldata, (8 * obj.width * realRow) + i)
                                        T.setCollisions(colls)
                                        globals.Tiles[tileNum] = T
                                        x += 60
                                        i += 8
                                crow += 1
                                y -= 60
                                x = 0
                                i = 0

                        else:
                            x = 0
                            y = 0
                            i = 0
                            for row in obj.rows:
                                for tile in row:
                                    if len(tile) == 3:
                                        tileNum = (tile[1] & 0xFF) + tileoffset
                                        T = TilesetTile(img.copy(x, y, 60, 60), nml.copy(x, y, 60, 60))
                                        T.setCollisions(struct.unpack_from('>8B', colldata, i))
                                        globals.Tiles[tileNum] = T
                                        x += 60
                                        i += 8
                                y += 60
                                x = 0

                        SLib.Tiles = globals.Tiles

                        globals.ObjectAddedtoEmbedded[globals.CurrentArea][globals.mainWindow.folderPicker.currentIndex()][
                            globals.CurrentObject] = (idx, objNum)

                        globals.CurrentPaintType = idx
                        globals.CurrentObject = objNum

                        globals.mainWindow.objPicker.LoadFromTilesets()

                        if not eval('globals.Area.tileset%d' % idx):
                            if idx == 1:
                                globals.Area.tileset1 = 'temp1'

                            elif idx == 2:
                                globals.Area.tileset2 = 'temp2'

                            elif idx == 3:
                                globals.Area.tileset3 = 'temp3'

                        globals.mainWindow.objAllTab.setTabEnabled(2, (globals.Area.tileset1 != ''
                                                               or globals.Area.tileset2 != ''
                                                               or globals.Area.tileset3 != ''))

                        globals.mainWindow.updateNumUsedTilesLabel()

                        break

                    # Checks if the object fit in one of the tilesets
                    if globals.CurrentPaintType == 10:
                        QtWidgets.QMessageBox.critical(None, 'Cannot Paint', 'There isn\'t enough room left for this object!')
                        return 

                # paint an object
                clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)
                clickedx = int(clicked.x() / globals.TileWidth)
                clickedy = int(clicked.y() / globals.TileWidth)

                ln = globals.CurrentLayer
                layer = globals.Area.layers[globals.CurrentLayer]
                if len(layer) == 0:
                    z = (2 - ln) * 8192
                else:
                    z = layer[-1].zValue() + 1

                obj = ObjectItem(globals.CurrentPaintType, globals.CurrentObject, ln, clickedx, clickedy, 1, 1, z, 0)
                layer.append(obj)
                mw = globals.mainWindow
                obj.positionChanged = mw.HandleObjPosChange
                mw.scene.addItem(obj)

                self.dragstamp = False
                self.currentobj = obj
                self.dragstartx = clickedx
                self.dragstarty = clickedy
                SetDirty()

                globals.CurrentPaintType = 10
                globals.CurrentObject = type_

            elif globals.CurrentPaintType == 4 and globals.CurrentSprite != -1:
                # paint a sprite
                clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)

                if globals.CurrentSprite >= 0:  # fixes a bug -Treeki
                    # [18:15:36]  Angel-SL: I found a bug in Reggie
                    # [18:15:42]  Angel-SL: you can paint a 'No sprites found'
                    # [18:15:47]  Angel-SL: results in a sprite -2

                    # paint a sprite
                    clickedx = int(clicked.x() // globals.TileWidth) * 16
                    clickedy = int(clicked.y() // globals.TileWidth) * 16

                    data = globals.mainWindow.defaultDataEditor.data
                    spr = SpriteItem(globals.CurrentSprite, clickedx, clickedy, data)

                    mw = globals.mainWindow
                    spr.positionChanged = mw.HandleSprPosChange
                    mw.scene.addItem(spr)

                    spr.listitem = ListWidgetItem_SortsByOther(spr)
                    mw.spriteList.addItem(spr.listitem)
                    globals.Area.sprites.append(spr)

                    self.dragstamp = False
                    self.currentobj = spr
                    self.dragstartx = clickedx
                    self.dragstarty = clickedy

                    self.scene().update()

                    spr.UpdateListItem()

                SetDirty()

            elif globals.CurrentPaintType == 5:
                # paint an entrance
                clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)
                clickedx = int((clicked.x() - 12) / globals.TileWidth * 16)
                clickedy = int((clicked.y() - 12) / globals.TileWidth * 16)

                getids = [False for x in range(256)]
                for ent in globals.Area.entrances: getids[ent.entid] = True
                minimumID = getids.index(False)

                ent = EntranceItem(clickedx, clickedy, 0, minimumID, 0, 0, 0, 0, 0, 0, 0x80, 0, 0, 0, 0, 0)
                mw = globals.mainWindow
                ent.positionChanged = mw.HandleEntPosChange
                mw.scene.addItem(ent)

                elist = mw.entranceList
                # if it's the first available ID, all the other indexes should match right?
                # so I can just use the ID to insert
                ent.listitem = ListWidgetItem_SortsByOther(ent)
                elist.insertItem(minimumID, ent.listitem)

                globals.PaintingEntrance = ent
                globals.PaintingEntranceListIndex = minimumID

                globals.Area.entrances.insert(minimumID, ent)

                self.dragstamp = False
                self.currentobj = ent
                self.dragstartx = clickedx
                self.dragstarty = clickedy

                ent.UpdateListItem()

                SetDirty()
            elif globals.CurrentPaintType == 6:
                # paint a path node
                clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)
                clickedx = int((clicked.x() - 12) / globals.TileWidth * 16)
                clickedy = int((clicked.y() - 12) / globals.TileWidth * 16)
                mw = globals.mainWindow
                plist = mw.pathList
                selectedpn = None if len(plist.selectedItems()) < 1 else plist.selectedItems()[0]
                # if selectedpn is None:
                #    QtWidgets.QMessageBox.warning(None, 'Error', 'No pathnode selected. Select a pathnode of the path you want to create a new node in.')
                if selectedpn is None:
                    getids = [False for x in range(256)]
                    getids[0] = True
                    for pathdatax in globals.Area.pathdata:
                        # if(len(pathdatax['nodes']) > 0):
                        getids[int(pathdatax['id'])] = True

                    newpathid = getids.index(False)
                    newpathdata = {'id': newpathid,
                                   'unk1': 0,
                                   'nodes': [
                                       {'x': clickedx, 'y': clickedy, 'speed': 0, 'accel': 0, 'delay': 0}],
                                   'loops': False
                                   }
                    globals.Area.pathdata.append(newpathdata)
                    newnode = PathItem(clickedx, clickedy, newpathdata, newpathdata['nodes'][0], 0, 0, 0, 0)
                    newnode.positionChanged = mw.HandlePathPosChange

                    mw.scene.addItem(newnode)

                    peline = PathEditorLineItem(newpathdata['nodes'])
                    newpathdata['peline'] = peline
                    mw.scene.addItem(peline)

                    globals.Area.pathdata.sort(key=lambda path: int(path['id']))

                    newnode.listitem = ListWidgetItem_SortsByOther(newnode)
                    plist.clear()
                    for fpath in globals.Area.pathdata:
                        for fpnode in fpath['nodes']:
                            fpnode['graphicsitem'].listitem = ListWidgetItem_SortsByOther(fpnode['graphicsitem'],
                                                                                          fpnode[
                                                                                              'graphicsitem'].ListString())
                            plist.addItem(fpnode['graphicsitem'].listitem)
                            fpnode['graphicsitem'].updateId()
                    newnode.listitem.setSelected(True)
                    globals.Area.paths.append(newnode)

                    self.dragstamp = False
                    self.currentobj = newnode
                    self.dragstartx = clickedx
                    self.dragstarty = clickedy

                    newnode.UpdateListItem()

                    SetDirty()
                else:
                    pathd = None
                    for pathnode in globals.Area.paths:
                        if pathnode.listitem == selectedpn:
                            pathd = pathnode.pathinfo

                    if not pathd: return  # shouldn't happen

                    pathid = pathd['id']
                    newnodedata = {'x': clickedx, 'y': clickedy, 'speed': 0, 'accel': 0, 'delay': 0}
                    pathd['nodes'].append(newnodedata)
                    nodeid = pathd['nodes'].index(newnodedata)

                    newnode = PathItem(clickedx, clickedy, pathd, newnodedata, 0, 0, 0, 0)

                    newnode.positionChanged = mw.HandlePathPosChange
                    mw.scene.addItem(newnode)

                    newnode.listitem = ListWidgetItem_SortsByOther(newnode)
                    plist.clear()
                    for fpath in globals.Area.pathdata:
                        for fpnode in fpath['nodes']:
                            fpnode['graphicsitem'].listitem = ListWidgetItem_SortsByOther(fpnode['graphicsitem'],
                                                                                          fpnode[
                                                                                              'graphicsitem'].ListString())
                            plist.addItem(fpnode['graphicsitem'].listitem)
                            fpnode['graphicsitem'].updateId()
                    newnode.listitem.setSelected(True)
                    # globals.PaintingEntrance = ent
                    # globals.PaintingEntranceListIndex = minimumID

                    globals.Area.paths.append(newnode)
                    pathd['peline'].nodePosChanged()
                    self.dragstamp = False
                    self.currentobj = newnode
                    self.dragstartx = clickedx
                    self.dragstarty = clickedy

                    newnode.UpdateListItem()

                    SetDirty()

            elif globals.CurrentPaintType == 7:
                # paint a location
                clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)

                clickedx = int(clicked.x() / globals.TileWidth * 16)
                clickedy = int(clicked.y() / globals.TileWidth * 16)

                allID = set()  # faster 'x in y' lookups for sets
                newID = 1
                for i in globals.Area.locations:
                    allID.add(i.id)

                while newID <= 255:
                    if newID not in allID:
                        break
                    newID += 1

                globals.OverrideSnapping = True
                loc = LocationItem(clickedx, clickedy, 4, 4, newID)
                globals.OverrideSnapping = False

                mw = globals.mainWindow
                loc.positionChanged = mw.HandleLocPosChange
                loc.sizeChanged = mw.HandleLocSizeChange
                loc.listitem = ListWidgetItem_SortsByOther(loc)
                mw.locationList.addItem(loc.listitem)
                mw.scene.addItem(loc)

                globals.Area.locations.append(loc)

                self.dragstamp = False
                self.currentobj = loc
                self.dragstartx = clickedx
                self.dragstarty = clickedy

                loc.UpdateListItem()

                SetDirty()

            elif globals.CurrentPaintType == 8:
                # paint a stamp
                clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)

                clickedx = int(clicked.x() / globals.TileWidth * 16)
                clickedy = int(clicked.y() / globals.TileWidth * 16)

                stamp = globals.mainWindow.stampChooser.currentlySelectedStamp()
                if stamp is not None:
                    objs = globals.mainWindow.placeEncodedObjects(stamp.MiyamotoClip, False, clickedx, clickedy)

                    for obj in objs:
                        obj.dragstartx = obj.objx
                        obj.dragstarty = obj.objy
                        obj.update()

                    globals.mainWindow.scene.update()

                    self.dragstamp = True
                    self.dragstartx = clickedx
                    self.dragstarty = clickedy
                    self.currentobj = objs

                    SetDirty()

            elif globals.CurrentPaintType == 9:
                # paint a comment

                clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)
                clickedx = int((clicked.x() - globals.TileWidth / 2) / globals.TileWidth * 16)
                clickedy = int((clicked.y() - globals.TileWidth / 2) / globals.TileWidth * 16)

                com = CommentItem(clickedx, clickedy, '')
                mw = globals.mainWindow
                com.positionChanged = mw.HandleComPosChange
                com.textChanged = mw.HandleComTxtChange
                mw.scene.addItem(com)
                com.setVisible(globals.CommentsShown)

                clist = mw.commentList
                com.listitem = QtWidgets.QListWidgetItem()
                clist.addItem(com.listitem)

                globals.Area.comments.append(com)

                self.dragstamp = False
                self.currentobj = com
                self.dragstartx = clickedx
                self.dragstarty = clickedy

                globals.mainWindow.SaveComments()

                com.UpdateListItem()

                SetDirty()
            event.accept()
        elif (event.button() == Qt.LeftButton) and (QtWidgets.QApplication.keyboardModifiers() == Qt.ShiftModifier):
            mw = globals.mainWindow

            pos = mw.view.mapToScene(event.x(), event.y())
            addsel = mw.scene.items(pos)
            for i in addsel:
                if (int(i.flags()) & i.ItemIsSelectable) != 0:
                    i.setSelected(not i.isSelected())
                    break

        else:
            QtWidgets.QGraphicsView.mousePressEvent(self, event)
        globals.mainWindow.levelOverview.update()

    def resizeEvent(self, event):
        """
        Catches resize events
        """
        self.FrameSize.emit(event.size().width(), event.size().height())
        event.accept()
        QtWidgets.QGraphicsView.resizeEvent(self, event)

    def mouseMoveEvent(self, event):
        """
        Overrides mouse movement events if needed
        """

        pos = globals.mainWindow.view.mapToScene(event.x(), event.y())
        if pos.x() < 0: pos.setX(0)
        if pos.y() < 0: pos.setY(0)
        self.PositionHover.emit(int(pos.x()), int(pos.y()))

        if event.buttons() == Qt.RightButton and self.currentobj is not None and not self.dragstamp:

            # possibly a small optimization
            type_obj = ObjectItem
            type_spr = SpriteItem
            type_ent = EntranceItem
            type_loc = LocationItem
            type_path = PathItem
            type_com = CommentItem

            # iterate through the objects if there's more than one
            if isinstance(self.currentobj, list) or isinstance(self.currentobj, tuple):
                objlist = self.currentobj
            else:
                objlist = (self.currentobj,)

            for obj in objlist:

                if isinstance(obj, type_obj):
                    # resize/move the current object
                    cx = obj.objx
                    cy = obj.objy
                    cwidth = obj.width
                    cheight = obj.height

                    dsx = self.dragstartx
                    dsy = self.dragstarty
                    clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                    if clicked.x() < 0: clicked.setX(0)
                    if clicked.y() < 0: clicked.setY(0)
                    clickx = int(clicked.x() / globals.TileWidth)
                    clicky = int(clicked.y() / globals.TileWidth)

                    # allow negative width/height and treat it properly :D
                    if clickx >= dsx:
                        x = dsx
                        width = clickx - dsx + 1
                    else:
                        x = clickx
                        width = dsx - clickx + 1

                    if clicky >= dsy:
                        y = dsy
                        height = clicky - dsy + 1
                    else:
                        y = clicky
                        height = dsy - clicky + 1

                    # if the position changed, set the new one
                    if cx != x or cy != y:
                        obj.objx = x
                        obj.objy = y
                        obj.setPos(x * globals.TileWidth, y * globals.TileWidth)

                    # if the size changed, recache it and update the area
                    if cwidth != width or cheight != height:
                        obj.width = width
                        obj.height = height
                        obj.updateObjCache()

                        oldrect = obj.BoundingRect
                        oldrect.translate(cx * globals.TileWidth, cy * globals.TileWidth)
                        newrect = QtCore.QRectF(obj.x(), obj.y(), obj.width * globals.TileWidth, obj.height * globals.TileWidth)
                        updaterect = oldrect.united(newrect)

                        obj.UpdateRects()
                        obj.scene().update(updaterect)

                elif isinstance(obj, type_loc):
                    # resize/move the current location
                    cx = obj.objx
                    cy = obj.objy
                    cwidth = obj.width
                    cheight = obj.height

                    dsx = self.dragstartx
                    dsy = self.dragstarty
                    clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                    if clicked.x() < 0: clicked.setX(0)
                    if clicked.y() < 0: clicked.setY(0)
                    clickx = int(clicked.x() / globals.TileWidth * 16)
                    clicky = int(clicked.y() / globals.TileWidth * 16)

                    # allow negative width/height and treat it properly :D
                    if clickx >= dsx:
                        x = dsx
                        width = clickx - dsx + 1
                    else:
                        x = clickx
                        width = dsx - clickx + 1

                    if clicky >= dsy:
                        y = dsy
                        height = clicky - dsy + 1
                    else:
                        y = clicky
                        height = dsy - clicky + 1

                    # if the position changed, set the new one
                    if cx != x or cy != y:
                        obj.objx = x
                        obj.objy = y

                        globals.OverrideSnapping = True
                        obj.setPos(x * globals.TileWidth / 16, y * globals.TileWidth / 16)
                        globals.OverrideSnapping = False

                    # if the size changed, recache it and update the area
                    if cwidth != width or cheight != height:
                        obj.width = width
                        obj.height = height
                        #                    obj.updateObjCache()

                        oldrect = obj.BoundingRect
                        oldrect.translate(cx * globals.TileWidth / 16, cy * globals.TileWidth / 16)
                        newrect = QtCore.QRectF(obj.x(), obj.y(), obj.width * globals.TileWidth / 16,
                                                obj.height * globals.TileWidth / 16)
                        updaterect = oldrect.united(newrect)

                        obj.UpdateRects()
                        obj.scene().update(updaterect)


                elif isinstance(obj, type_spr):
                    # move the created sprite
                    clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                    if clicked.x() < 0: clicked.setX(0)
                    if clicked.y() < 0: clicked.setY(0)
                    clickedx = int((clicked.x() - globals.TileWidth / 2) / globals.TileWidth * 16)
                    clickedy = int((clicked.y() - globals.TileWidth / 2) / globals.TileWidth * 16)

                    if obj.objx != clickedx or obj.objy != clickedy:
                        obj.objx = clickedx
                        obj.objy = clickedy
                        obj.setPos(int((clickedx + obj.ImageObj.xOffset) * globals.TileWidth / 16),
                                   int((clickedy + obj.ImageObj.yOffset) * globals.TileWidth / 16))

                elif isinstance(obj, type_ent) or isinstance(obj, type_path) or isinstance(obj, type_com):
                    # move the created entrance/path/comment
                    clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                    if clicked.x() < 0: clicked.setX(0)
                    if clicked.y() < 0: clicked.setY(0)
                    clickedx = int((clicked.x() - globals.TileWidth / 2) / globals.TileWidth * 16)
                    clickedy = int((clicked.y() - globals.TileWidth / 2) / globals.TileWidth * 16)

                    if obj.objx != clickedx or obj.objy != clickedy:
                        obj.objx = clickedx
                        obj.objy = clickedy
                        obj.setPos(int(clickedx * globals.TileWidth / 16), int(clickedy * globals.TileWidth / 16))
            event.accept()

        elif event.buttons() == Qt.RightButton and self.currentobj is not None and self.dragstamp:
            # The user is dragging a stamp - many objects.

            # possibly a small optimization
            type_obj = ObjectItem
            type_spr = SpriteItem

            # iterate through the objects if there's more than one
            if isinstance(self.currentobj, list) or isinstance(self.currentobj, tuple):
                objlist = self.currentobj
            else:
                objlist = (self.currentobj,)

            for obj in objlist:

                clicked = globals.mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)

                changex = clicked.x() - (self.dragstartx * globals.TileWidth / 16)
                changey = clicked.y() - (self.dragstarty * globals.TileWidth / 16)
                changexobj = int(changex / globals.TileWidth)
                changeyobj = int(changey / globals.TileWidth)
                changexspr = changex * 2 / 3
                changeyspr = changey * 2 / 3

                if isinstance(obj, type_obj):
                    # move the current object
                    newx = int(obj.dragstartx + changexobj)
                    newy = int(obj.dragstarty + changeyobj)

                    if obj.objx != newx or obj.objy != newy:
                        obj.objx = newx
                        obj.objy = newy
                        obj.setPos(newx * globals.TileWidth, newy * globals.TileWidth)

                elif isinstance(obj, type_spr):
                    # move the created sprite

                    newx = int(obj.dragstartx + changexspr)
                    newy = int(obj.dragstarty + changeyspr)

                    if obj.objx != newx or obj.objy != newy:
                        obj.objx = newx
                        obj.objy = newy
                        obj.setPos(int((newx + obj.ImageObj.xOffset) * globals.TileWidth / 16),
                                   int((newy + obj.ImageObj.yOffset) * globals.TileWidth / 16))

            self.scene().update()

        else:
            QtWidgets.QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        """
        Overrides mouse release events if needed
        """
        if event.button() == Qt.RightButton:
            self.currentobj = None
            event.accept()
        else:
            QtWidgets.QGraphicsView.mouseReleaseEvent(self, event)

    def paintEvent(self, e):
        """
        Handles paint events and fires a signal
        """
        self.repaint.emit()
        QtWidgets.QGraphicsView.paintEvent(self, e)

    def drawForeground(self, painter, rect):
        """
        Draws a foreground grid
        """
        if globals.GridType is None: return

        Zoom = globals.mainWindow.ZoomLevel
        drawLine = painter.drawLine
        GridColor = globals.theme.color('grid')

        if globals.GridType == 'grid':  # draw a classic grid
            startx = rect.x()
            startx -= (startx % globals.TileWidth)
            endx = startx + rect.width() + globals.TileWidth

            starty = rect.y()
            starty -= (starty % globals.TileWidth)
            endy = starty + rect.height() + globals.TileWidth

            x = startx - globals.TileWidth
            while x <= endx:
                x += globals.TileWidth
                if x % (globals.TileWidth * 8) == 0:
                    painter.setPen(QtGui.QPen(GridColor, 2 * globals.TileWidth / 24, Qt.DashLine))
                    drawLine(x, starty, x, endy)
                elif x % (globals.TileWidth * 4) == 0:
                    if Zoom < 25: continue
                    painter.setPen(QtGui.QPen(GridColor, 1 * globals.TileWidth / 24, Qt.DashLine))
                    drawLine(x, starty, x, endy)
                else:
                    if Zoom < 50: continue
                    painter.setPen(QtGui.QPen(GridColor, 1 * globals.TileWidth / 24, Qt.DotLine))
                    drawLine(x, starty, x, endy)

            y = starty - globals.TileWidth
            while y <= endy:
                y += globals.TileWidth
                if y % (globals.TileWidth * 8) == 0:
                    painter.setPen(QtGui.QPen(GridColor, 2 * globals.TileWidth / 24, Qt.DashLine))
                    drawLine(startx, y, endx, y)
                elif y % (globals.TileWidth * 4) == 0 and Zoom >= 25:
                    painter.setPen(QtGui.QPen(GridColor, 1 * globals.TileWidth / 24, Qt.DashLine))
                    drawLine(startx, y, endx, y)
                elif Zoom >= 50:
                    painter.setPen(QtGui.QPen(GridColor, 1 * globals.TileWidth / 24, Qt.DotLine))
                    drawLine(startx, y, endx, y)

        else:  # draw a checkerboard
            L = 0.2
            D = 0.1  # Change these values to change the checkerboard opacity

            Light = QtGui.QColor(GridColor)
            Dark = QtGui.QColor(GridColor)
            Light.setAlpha(Light.alpha() * L)
            Dark.setAlpha(Dark.alpha() * D)

            size = globals.TileWidth if Zoom >= 50 else globals.TileWidth * 8

            board = QtGui.QPixmap(8 * size, 8 * size)
            board.fill(QtGui.QColor(0, 0, 0, 0))
            p = QtGui.QPainter(board)
            p.setPen(Qt.NoPen)

            p.setBrush(QtGui.QBrush(Light))
            for x, y in ((0, size), (size, 0)):
                p.drawRect(x + (4 * size), y, size, size)
                p.drawRect(x + (4 * size), y + (2 * size), size, size)
                p.drawRect(x + (6 * size), y, size, size)
                p.drawRect(x + (6 * size), y + (2 * size), size, size)

                p.drawRect(x, y + (4 * size), size, size)
                p.drawRect(x, y + (6 * size), size, size)
                p.drawRect(x + (2 * size), y + (4 * size), size, size)
                p.drawRect(x + (2 * size), y + (6 * size), size, size)
            p.setBrush(QtGui.QBrush(Dark))
            for x, y in ((0, 0), (size, size)):
                p.drawRect(x, y, size, size)
                p.drawRect(x, y + (2 * size), size, size)
                p.drawRect(x + (2 * size), y, size, size)
                p.drawRect(x + (2 * size), y + (2 * size), size, size)

                p.drawRect(x, y + (4 * size), size, size)
                p.drawRect(x, y + (6 * size), size, size)
                p.drawRect(x + (2 * size), y + (4 * size), size, size)
                p.drawRect(x + (2 * size), y + (6 * size), size, size)

                p.drawRect(x + (4 * size), y, size, size)
                p.drawRect(x + (4 * size), y + (2 * size), size, size)
                p.drawRect(x + (6 * size), y, size, size)
                p.drawRect(x + (6 * size), y + (2 * size), size, size)

                p.drawRect(x + (4 * size), y + (4 * size), size, size)
                p.drawRect(x + (4 * size), y + (6 * size), size, size)
                p.drawRect(x + (6 * size), y + (4 * size), size, size)
                p.drawRect(x + (6 * size), y + (6 * size), size, size)

            del p

            painter.drawTiledPixmap(rect, board, QtCore.QPointF(rect.x(), rect.y()))


class InfoPreviewWidget(QtWidgets.QWidget):
    """
    Widget that shows a preview of the level metadata info - available in vertical & horizontal flavors
    """

    def __init__(self, direction):
        """
        Creates and initializes the widget
        """
        super().__init__()
        self.direction = direction

        self.Label1 = QtWidgets.QLabel('')
        if self.direction == Qt.Horizontal: self.Label2 = QtWidgets.QLabel('')
        self.updateLabels()

        self.mainLayout = QtWidgets.QHBoxLayout()
        self.mainLayout.addWidget(self.Label1)
        if self.direction == Qt.Horizontal: self.mainLayout.addWidget(self.Label2)
        self.setLayout(self.mainLayout)

        if self.direction == Qt.Horizontal: self.setMinimumWidth(256)

    def updateLabels(self):
        """
        Updates the widget labels
        """
        if ('Area' not in globals.globals()) or not hasattr(globals.Area, 'filename'):  # can't get level metadata if there's no level
            self.Label1.setText('')
            if self.direction == Qt.Horizontal: self.Label2.setText('')
            return

        a = [  # MUST be a list, not a tuple
            globals.mainWindow.fileTitle,
            globals.Area.Title,
            globals.trans.string('InfoDlg', 8, '[name]', globals.Area.Creator),
            globals.trans.string('InfoDlg', 5) + ' ' + globals.Area.Author,
            globals.trans.string('InfoDlg', 6) + ' ' + globals.Area.Group,
            globals.trans.string('InfoDlg', 7) + ' ' + globals.Area.Webpage,
        ]

        for b, section in enumerate(a):  # cut off excessively long strings
            if self.direction == Qt.Vertical:
                short = clipStr(section, 128)
            else:
                short = clipStr(section, 184)
            if short is not None: a[b] = short + '...'

        if self.direction == Qt.Vertical:
            str1 = a[0] + '<br>' + a[1] + '<br>' + a[2] + '<br>' + a[3] + '<br>' + a[4] + '<br>' + a[5]
            self.Label1.setText(str1)
        else:
            str1 = a[0] + '<br>' + a[1] + '<br>' + a[2]
            str2 = a[3] + '<br>' + a[4] + '<br>' + a[5]
            self.Label1.setText(str1)
            self.Label2.setText(str2)

        self.update()


class ZoomWidget(QtWidgets.QWidget):
    """
    Widget that allows easy zoom level control
    """

    def __init__(self):
        """
        Creates and initializes the widget
        """
        super().__init__()
        maxwidth = 512 - 128
        maxheight = 20

        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.minLabel = QtWidgets.QPushButton()
        self.minusLabel = QtWidgets.QPushButton()
        self.plusLabel = QtWidgets.QPushButton()
        self.maxLabel = QtWidgets.QPushButton()

        self.slider.setMaximumHeight(maxheight)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(globals.mainWindow.ZoomLevels) - 1)
        self.slider.setTickInterval(2)
        self.slider.setTickPosition(self.slider.TicksAbove)
        self.slider.setPageStep(1)
        self.slider.setTracking(True)
        self.slider.setSliderPosition(self.findIndexOfLevel(100))
        self.slider.valueChanged.connect(self.sliderMoved)

        self.minLabel.setIcon(GetIcon('zoommin'))
        self.minusLabel.setIcon(GetIcon('zoomout'))
        self.plusLabel.setIcon(GetIcon('zoomin'))
        self.maxLabel.setIcon(GetIcon('zoommax'))
        self.minLabel.setFlat(True)
        self.minusLabel.setFlat(True)
        self.plusLabel.setFlat(True)
        self.maxLabel.setFlat(True)
        self.minLabel.clicked.connect(globals.mainWindow.HandleZoomMin)
        self.minusLabel.clicked.connect(globals.mainWindow.HandleZoomOut)
        self.plusLabel.clicked.connect(globals.mainWindow.HandleZoomIn)
        self.maxLabel.clicked.connect(globals.mainWindow.HandleZoomMax)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.minLabel, 0, 0)
        self.layout.addWidget(self.minusLabel, 0, 1)
        self.layout.addWidget(self.slider, 0, 2)
        self.layout.addWidget(self.plusLabel, 0, 3)
        self.layout.addWidget(self.maxLabel, 0, 4)
        self.layout.setVerticalSpacing(0)
        self.layout.setHorizontalSpacing(0)
        self.layout.setContentsMargins(0, 0, 4, 0)

        self.setLayout(self.layout)
        self.setMinimumWidth(maxwidth)
        self.setMaximumWidth(maxwidth)
        self.setMaximumHeight(maxheight)

    def sliderMoved(self):
        """
        Handle the slider being moved
        """
        globals.mainWindow.ZoomTo(globals.mainWindow.ZoomLevels[self.slider.value()])

    def setZoomLevel(self, newLevel):
        """
        Moves the slider to the zoom level given
        """
        self.slider.setSliderPosition(self.findIndexOfLevel(newLevel))

    def findIndexOfLevel(self, level):
        for i, mainlevel in enumerate(globals.mainWindow.ZoomLevels):
            if float(mainlevel) == float(level): return i


class ZoomStatusWidget(QtWidgets.QWidget):
    """
    Shows the current zoom level, in percent
    """

    def __init__(self):
        """
        Creates and initializes the widget
        """
        super().__init__()
        self.label = QtWidgets.QPushButton('100%')
        self.label.setFlat(True)
        self.label.clicked.connect(globals.mainWindow.HandleZoomActual)

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.setContentsMargins(4, 0, 8, 0)
        self.setMaximumWidth(56)

        self.setLayout(self.layout)

    def setZoomLevel(self, zoomLevel):
        """
        Updates the widget
        """
        if float(int(zoomLevel)) == float(zoomLevel):
            self.label.setText(str(int(zoomLevel)) + '%')
        else:
            self.label.setText(str(float(zoomLevel)) + '%')


class ListWidgetWithToolTipSignal(QtWidgets.QListWidget):
    """
    A QtWidgets.QListWidget that includes a signal that
    is emitted when a tooltip is about to be shown. Useful
    for making tooltips that update every time you show
    them.
    """
    toolTipAboutToShow = QtCore.pyqtSignal(QtWidgets.QListWidgetItem)

    def viewportEvent(self, e):
        """
        Handles viewport events
        """
        if e.type() == e.ToolTip:
            self.toolTipAboutToShow.emit(self.itemFromIndex(self.indexAt(e.pos())))

        return super().viewportEvent(e)


class ListWidgetItem_SortsByOther(QtWidgets.QListWidgetItem):
    """
    A ListWidgetItem that defers sorting to another object.
    """

    def __init__(self, reference, text=''):
        super().__init__(text)
        self.reference = reference

    def __lt__(self, other):
        return self.reference < other.reference
