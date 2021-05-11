#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2021 Treeki, Tempus, angelsl, JasonP27, Kinnay,
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


################################################################
################################################################

############ Imports ############

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

if not hasattr(QtWidgets.QGraphicsItem, 'ItemSendsGeometryChanges'):
    # enables itemChange being called on QGraphicsItem
    QtWidgets.QGraphicsItem.ItemSendsGeometryChanges = QtWidgets.QGraphicsItem.GraphicsItemFlag(0x800)

import globals

#################################


class LevelScene(QtWidgets.QGraphicsScene):
    """
    GraphicsScene subclass for the level scene
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.setBackgroundBrush(QtGui.QBrush(globals.theme.color('bg')))

    def drawForeground(self, painter, rect):
        """
        Draw a foreground grid (only called when taking a screenshot)
        """
        drawForegroundGrid(painter, rect)

    def drawBackground(self, painter, rect):
        """
        Draws all visible tiles
        """
        super().drawBackground(painter, rect)
        if not hasattr(globals.Area, 'layers'):
            return

        drawrect = QtCore.QRectF(rect.x() / globals.TileWidth, rect.y() / globals.TileWidth, rect.width() / globals.TileWidth + 1,
                                 rect.height() / globals.TileWidth + 1)
        isect = drawrect.intersects

        layer0 = []
        layer1 = []
        layer2 = []

        x1 = 1024
        y1 = 512
        x2 = 0
        y2 = 0

        # iterate through each object
        funcs = [layer0.append, layer1.append, layer2.append]
        show = [globals.Layer0Shown, globals.Layer1Shown, globals.Layer2Shown]
        for layer, add, process in zip(globals.Area.layers, funcs, show):
            if not process: continue
            for item in layer:
                if not isect(item.LevelRect): continue
                add(item)
                xs = item.objx
                xe = xs + item.width
                ys = item.objy
                ye = ys + item.height
                if xs < x1: x1 = xs
                if xe > x2: x2 = xe
                if ys < y1: y1 = ys
                if ye > y2: y2 = ye

        width = x2 - x1
        height = y2 - y1

        objectDefinitions = globals.ObjectDefinitions
        tiles = globals.Tiles

        offset = 0x800
        items = {1: 26, 2: 27, 3: 16, 4: 17, 5: 18, 6: 19,
                 7: 20, 8: 21, 9: 22, 10: 25, 11: 23, 12: 24,
                 14: 32, 15: 33, 16: 34, 17: 35, 18: 42, 19: 36,
                 20: 37, 21: 38, 22: 41, 23: 39, 24: 40}

        # create and draw the tilemaps
        for idx, layer in (2, layer2), (1, layer1), (0, layer0):
            if not layer:
                continue

            tmap = [[None] * width for _ in range(height)]

            for item in layer:
                startx = item.objx - x1
                desty = item.objy - y1

                exists = True
                try:
                    if objectDefinitions[item.tileset] is None:
                        exists = False
                    elif objectDefinitions[item.tileset][item.type] is None:
                        exists = False
                except IndexError:
                    exists = False

                for row in item.objdata:
                    destrow = tmap[desty]
                    destx = startx
                    for tile in row:
                        # If this object has data, make sure to override it properly
                        if tile > 0:
                            if item.data in items:
                                destrow[destx] = offset + items[item.data]
                            else:
                                destrow[destx] = tile
                        elif not exists:
                            destrow[destx] = -1
                        destx += 1
                    desty += 1

            painter.save()
            painter.translate(x1 * globals.TileWidth, y1 * globals.TileWidth)
            drawPixmap = painter.drawPixmap
            desty = 0
            for row in tmap:
                destx = 0
                for tile in row:
                    pix = None

                    if tile == -1:
                        # Draw unknown tiles
                        pix = tiles[0x800].getCurrentTile()
                    elif tile is not None:
                        pix = tiles[tile].getCurrentTile(idx == 1)

                    if pix is not None:
                        drawPixmap(destx, desty, pix)

                    destx += globals.TileWidth
                desty += globals.TileWidth
            painter.restore()


class HexSpinBox(QtWidgets.QSpinBox):
    class HexValidator(QtGui.QValidator):
        def __init__(self, min, max):
            super().__init__()
            self.valid = set('0123456789abcdef')
            self.min = min
            self.max = max

        def validate(self, input, pos):
            try:
                input = str(input).lower()
            except Exception:
                return (self.Invalid, input, pos)
            valid = self.valid

            for char in input:
                if char not in valid:
                    return (self.Invalid, input, pos)

            try:
                value = int(input, 16)
            except ValueError:
                # If value == '' it raises ValueError
                return (self.Invalid, input, pos)

            if value < self.min or value > self.max:
                return (self.Intermediate, input, pos)

            return (self.Acceptable, input, pos)

    def __init__(self, format='%04X', *args):
        self.format = format
        super().__init__(*args)
        self.validator = self.HexValidator(self.minimum(), self.maximum())

    def setMinimum(self, value):
        self.validator.min = value
        QtWidgets.QSpinBox.setMinimum(self, value)

    def setMaximum(self, value):
        self.validator.max = value
        QtWidgets.QSpinBox.setMaximum(self, value)

    def setRange(self, min, max):
        self.validator.min = min
        self.validator.max = max
        QtWidgets.QSpinBox.setMinimum(self, min)
        QtWidgets.QSpinBox.setMaximum(self, max)

    def validate(self, text, pos):
        return self.validator.validate(text, pos)

    def textFromValue(self, value):
        return self.format % value

    def valueFromText(self, value):
        return int(str(value), 16)


class SpriteDefinition:
    """
    Stores and manages the data info for a specific sprite
    """

    class ListPropertyModel(QtCore.QAbstractListModel):
        """
        Contains all the possible values for a list property on a sprite
        """

        def __init__(self, entries, existingLookup, max):
            """
            Constructor
            """
            super().__init__()
            self.entries = entries
            self.existingLookup = existingLookup
            self.max = max

        def rowCount(self, parent=None):
            """
            Required by Qt
            """
            return len(self.entries)

        def data(self, index, role=Qt.DisplayRole):
            """
            Get what we have for a specific row
            """
            if not index.isValid():
                return None

            n = index.row()
            if n < 0 or n >= len(self.entries):
                return None

            if role == Qt.DisplayRole:
                return '%d: %s' % self.entries[n]

            return None

    def loadFrom(self, elem):
        """
        Loads in all the field data from an XML node
        """
        self.fields = []
        fields = self.fields

        for field in elem:
            if field.tag not in ['checkbox', 'list', 'value', 'bitfield']: continue

            attribs = field.attrib

            if 'comment' in attribs:
                comment = globals.trans.string('SpriteDataEditor', 1, '[name]', attribs['title'], '[note]', attribs['comment'])
            else:
                comment = None

            if field.tag == 'checkbox':
                # parameters: title, bit, mask, comment
                if 'nybble' in attribs:
                    sbit = attribs['nybble']
                    sft = 2

                else:
                    sbit = attribs['bit']
                    sft = 0

                if not '-' in sbit:
                    if not sft:
                        # just 1 bit
                        bit = int(sbit)

                    else:
                        # just 4 bits
                        bit = (((int(sbit) - 1) << 2) + 1, (int(sbit) << 2) + 1)

                else:
                    # different number of bits
                    getit = sbit.split('-')
                    bit = (((int(getit[0]) - 1) << sft) + 1, (int(getit[1]) << sft) + 1)

                if 'mask' in attribs:
                    mask = int(attribs['mask'])

                else:
                    mask = 1

                fields.append((0, attribs['title'], bit, mask, comment))

            elif field.tag == 'list':
                # parameters: title, bit, model, comment
                if 'nybble' in attribs:
                    sbit = attribs['nybble']
                    sft = 2

                else:
                    sbit = attribs['bit']
                    sft = 0

                if not '-' in sbit:
                    if not sft:
                        # just 1 bit
                        bit = int(sbit)
                        max = 2

                    else:
                        # just 4 bits
                        bit = (((int(sbit) - 1) << 2) + 1, (int(sbit) << 2) + 1)
                        max = 16

                else:
                    # different number of bits
                    getit = sbit.split('-')
                    bit = (((int(getit[0]) - 1) << sft) + 1, (int(getit[1]) << sft) + 1)
                    max = 1 << (bit[1] - bit[0])

                entries = []
                existing = [None for i in range(max)]
                for e in field:
                    if e.tag != 'entry': continue

                    i = int(e.attrib['value'])
                    entries.append((i, e.text))
                    existing[i] = True

                fields.append(
                    (1, attribs['title'], bit, SpriteDefinition.ListPropertyModel(entries, existing, max), comment))

            elif field.tag == 'value':
                # parameters: title, bit, max, comment
                if 'nybble' in attribs:
                    sbit = attribs['nybble']
                    sft = 2

                else:
                    sbit = attribs['bit']
                    sft = 0

                if not '-' in sbit:
                    if not sft:
                        # just 1 bit
                        bit = int(sbit)
                        max = 2

                    else:
                        # just 4 bits
                        bit = (((int(sbit) - 1) << 2) + 1, (int(sbit) << 2) + 1)
                        max = 16

                else:
                    # different number of bits
                    getit = sbit.split('-')
                    bit = (((int(getit[0]) - 1) << sft) + 1, (int(getit[1]) << sft) + 1)
                    max = 1 << (bit[1] - bit[0])

                fields.append((2, attribs['title'], bit, max, comment))

            elif field.tag == 'bitfield':
                # parameters: title, startbit, bitnum, comment
                startbit = int(attribs['startbit'])
                bitnum = int(attribs['bitnum'])

                fields.append((3, attribs['title'], startbit, bitnum, comment))


class Metadata:
    """
    Class for the new level metadata system
    """

    # This new system is much more useful and flexible than the old
    # system, but is incompatible with older versions of Miyamoto.
    # They will fail to understand the data, and skip it like it
    # doesn't exist. The new system is written with forward-compatibility
    # in mind. Thus, when newer versions of Miyamoto are created
    # with new metadata values, they will be easily able to add to
    # the existing ones. In addition, the metadata system is lossless,
    # so unrecognized values will be preserved when you open and save.

    # Type values:
    # 0 = binary
    # 1 = string
    # 2+ = undefined as of now - future Miyamotos can use them
    # Theoretical limit to type values is 4,294,967,296

    def __init__(self, data=None):
        """
        Creates a metadata object with the data given
        """
        self.DataDict = {}
        if not data or data[0:4] != b'MD2_': return

        # Iterate through the data
        idx = 4
        while idx < len(data) - 4:

            # Read the next (first) four bytes - the key length
            rawKeyLen = data[idx:idx + 4]
            idx += 4

            keyLen = (rawKeyLen[0] << 24) | (rawKeyLen[1] << 16) | (rawKeyLen[2] << 8) | rawKeyLen[3]

            # Read the next (key length) bytes - the key (as a str)
            rawKey = data[idx:idx + keyLen]
            idx += keyLen

            key = ''
            for b in rawKey: key += chr(b)

            # Read the next four bytes - the number of type entries
            rawTypeEntries = data[idx:idx + 4]
            idx += 4

            typeEntries = (rawTypeEntries[0] << 24) | (rawTypeEntries[1] << 16) | (rawTypeEntries[2] << 8) | \
                          rawTypeEntries[3]

            # Iterate through each type entry
            for entry in range(typeEntries):
                # Read the next four bytes - the type
                rawType = data[idx:idx + 4]
                idx += 4

                type = (rawType[0] << 24) | (rawType[1] << 16) | (rawType[2] << 8) | rawType[3]

                # Read the next four bytes - the data length
                rawDataLen = data[idx:idx + 4]
                idx += 4

                dataLen = (rawDataLen[0] << 24) | (rawDataLen[1] << 16) | (rawDataLen[2] << 8) | rawDataLen[3]

                # Read the next (data length) bytes - the data (as bytes)
                entryData = data[idx:idx + dataLen]
                idx += dataLen

                # Add it to typeData
                self.setOtherData(key, type, entryData)

    def binData(self, key):
        """
        Returns the binary data associated with key
        """
        return self.otherData(key, 0)

    def strData(self, key):
        """
        Returns the string data associated with key
        """
        data = self.otherData(key, 1)
        if data is None: return
        s = ''
        for d in data: s += chr(d)
        return s

    def otherData(self, key, type):
        """
        Returns unknown data, with the given type value, associated with key (as binary data)
        """
        if key not in self.DataDict: return
        if type not in self.DataDict[key]: return
        return self.DataDict[key][type]

    def setBinData(self, key, value):
        """
        Sets binary data, overwriting any existing binary data with that key
        """
        self.setOtherData(key, 0, value)

    def setStrData(self, key, value):
        """
        Sets string data, overwriting any existing string data with that key
        """
        data = []
        for char in value: data.append(ord(char))
        self.setOtherData(key, 1, data)

    def setOtherData(self, key, type, value):
        """
        Sets other (binary) data, overwriting any existing data with that key and type
        """
        if key not in self.DataDict: self.DataDict[key] = {}
        self.DataDict[key][type] = value

    def save(self):
        """
        Returns a bytes object that can later be loaded from
        """

        # Sort self.DataDict
        dataDictSorted = []
        for dataKey in self.DataDict: dataDictSorted.append((dataKey, self.DataDict[dataKey]))
        dataDictSorted.sort(key=lambda entry: entry[0])

        data = []

        # Add 'MD2_'
        data.append(ord('M'))
        data.append(ord('D'))
        data.append(ord('2'))
        data.append(ord('_'))

        # Iterate through self.DataDict
        for dataKey, types in dataDictSorted:

            # Add the key length (4 bytes)
            keyLen = len(dataKey)
            data.append(keyLen >> 24)
            data.append((keyLen >> 16) & 0xFF)
            data.append((keyLen >> 8) & 0xFF)
            data.append(keyLen & 0xFF)

            # Add the key (key length bytes)
            for char in dataKey: data.append(ord(char))

            # Sort the types
            typesSorted = []
            for type in types: typesSorted.append((type, types[type]))
            typesSorted.sort(key=lambda entry: entry[0])

            # Add the number of types (4 bytes)
            typeNum = len(typesSorted)
            data.append(typeNum >> 24)
            data.append((typeNum >> 16) & 0xFF)
            data.append((typeNum >> 8) & 0xFF)
            data.append(typeNum & 0xFF)

            # Iterate through typesSorted
            for type, typeData in typesSorted:

                # Add the type (4 bytes)
                data.append(type >> 24)
                data.append((type >> 16) & 0xFF)
                data.append((type >> 8) & 0xFF)
                data.append(type & 0xFF)

                # Add the data length (4 bytes)
                dataLen = len(typeData)
                data.append(dataLen >> 24)
                data.append((dataLen >> 16) & 0xFF)
                data.append((dataLen >> 8) & 0xFF)
                data.append(dataLen & 0xFF)

                # Add the data (data length bytes)
                for d in typeData: data.append(d)

        if bytes(data) == b'MD2_':
            return[]

        return data


class BGName:
    def __init__(self, name, trans):
        self.name = name
        self.trans = trans

    def __eq__(self, other):
        return other in (self.name, self.trans)

    @staticmethod
    def index(name):
        try:
            return globals.names_bg.index(name)

        except ValueError:
            return len(globals.names_bg) - 1

    @staticmethod
    def getNameForTrans(trans):
        return globals.names_bg[BGName.index(trans)].name

    @staticmethod
    def getTransAll():
        return [bg.trans for bg in globals.names_bg]

    class Custom:
        def __init__(self):
            self.name = ''
            self.trans = 'Custom filename...'

        def __eq__(self, other):
            return False


def clipStr(text, idealWidth, font=None):
    """
    Returns a shortened string, or None if it need not be shortened
    """
    if font is None: font = QtGui.QFont()
    width = QtGui.QFontMetrics(font).width(text)
    if width <= idealWidth: return None

    while width > idealWidth:
        text = text[:-1]
        width = QtGui.QFontMetrics(font).width(text)

    return text


def setting(name, default=None):
    """
    Thin wrapper around QSettings, fixes the type=bool bug
    """
    types_str = {str: 'str', int: 'int', float: 'float', dict: 'dict', bool: 'bool', QtCore.QByteArray: 'QByteArray', type(None): 'NoneType'}
    types = {'str': str, 'int': int, 'float': float, 'dict': dict, 'bool': bool, 'QByteArray': QtCore.QByteArray}

    type_ = globals.settings.value('typeof(%s)' % name, types_str[type(default)], str)
    if type_ == 'NoneType':
        return None

    return globals.settings.value(name, default, types[type_])


def setSetting(name, value):
    """
    Thin wrapper around QSettings
    """
    types_str = {str: 'str', int: 'int', float: 'float', dict: 'dict', bool: 'bool', QtCore.QByteArray: 'QByteArray', type(None): 'NoneType'}
    assert isinstance(name, str) and type(value) in types_str

    globals.settings.setValue(name, value)
    globals.settings.setValue('typeof(%s)' % name, types_str[type(value)])


def SetGamePath(newpath):
    """
    Sets the NSMBU game path
    """
    # you know what's fun?
    # isValidGamePath crashes in os.path.join if QString is used..
    # so we must change it to a Python string manually
    globals.gamedef.SetGamePath(str(newpath))


def drawForegroundGrid(painter, rect):
    """
    Draws a foreground grid
    """
    if globals.GridType is None:
        return

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
