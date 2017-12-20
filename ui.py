#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2017 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7, John10v10

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

from xml.etree import ElementTree as etree

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

if not hasattr(QtWidgets.QGraphicsItem, 'ItemSendsGeometryChanges'):
    # enables itemChange being called on QGraphicsItem
    QtWidgets.QGraphicsItem.ItemSendsGeometryChanges = QtWidgets.QGraphicsItem.GraphicsItemFlag(0x800)

import globals
from loading import *
from strings import *


class ChooseLevelNameDialog(QtWidgets.QDialog):
    """
    Dialog which lets you choose a level from a list
    """

    def __init__(self):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle(globals.trans.string('OpenFromNameDlg', 0))
        self.setWindowIcon(GetIcon('open'))

        import loading
        loading.LoadLevelNames()

        self.currentlevel = None

        # create the tree
        tree = QtWidgets.QTreeWidget()
        tree.setColumnCount(1)
        tree.setHeaderHidden(True)
        tree.setIndentation(16)
        tree.currentItemChanged.connect(self.HandleItemChange)
        tree.itemActivated.connect(self.HandleItemActivated)

        # add items (globals.LevelNames is effectively a big category)
        tree.addTopLevelItems(self.ParseCategory(globals.LevelNames))

        # assign it to self.leveltree
        self.leveltree = tree

        # create the buttons
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # create the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.leveltree)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)
        self.layout = layout

        self.setMinimumWidth(320)  # big enough to fit "World 5: Freezeflame Volcano/Freezeflame Glacier"
        self.setMinimumHeight(384)

    def ParseCategory(self, items):
        """
        Parses a XML category
        """
        nodes = []
        for item in items:
            node = QtWidgets.QTreeWidgetItem()
            node.setText(0, item[0])
            # see if it's a category or a level
            if isinstance(item[1], str):
                # it's a level
                node.setData(0, Qt.UserRole, item[1])
                node.setToolTip(0, item[1])
            else:
                # it's a category
                children = self.ParseCategory(item[1])
                for cnode in children:
                    node.addChild(cnode)
                node.setToolTip(0, item[0])
            nodes.append(node)
        return tuple(nodes)

    def HandleItemChange(self, current, previous):
        """
        Catch the selected level and enable/disable OK button as needed
        """
        self.currentlevel = current.data(0, Qt.UserRole)
        if self.currentlevel is None:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            self.currentlevel = str(self.currentlevel)

    def HandleItemActivated(self, item, column):
        """
        Handle a doubleclick on a level
        """
        self.currentlevel = item.data(0, Qt.UserRole)
        if self.currentlevel is not None:
            self.currentlevel = str(self.currentlevel)
            self.accept()


class MiyamotoTheme:
    """
    Class that represents a Miyamoto theme
    """

    def __init__(self, folder=None):
        """
        Initializes the theme
        """
        self.initAsClassic()
        if folder is not None: self.initFromFolder(folder)

    def initAsClassic(self):
        """
        Initializes the theme as the hardcoded Classic theme
        """
        self.fileName = 'Classic'
        self.formatver = 1.0
        self.version = 1.0
        self.themeName = globals.trans.string('Themes', 0)
        self.creator = globals.trans.string('Themes', 1)
        self.description = globals.trans.string('Themes', 2)
        self.iconCacheSm = {}
        self.iconCacheLg = {}
        self.style = None

        # Add the colours                                             # Descriptions:
        self.colors = {
            'bg': QtGui.QColor(119, 136, 153),  # Main scene background fill
            'comment_fill': QtGui.QColor(220, 212, 135, 120),  # Unselected comment fill
            'comment_fill_s': QtGui.QColor(254, 240, 240, 240),  # Selected comment fill
            'comment_lines': QtGui.QColor(192, 192, 192, 120),  # Unselected comment lines
            'comment_lines_s': QtGui.QColor(220, 212, 135, 240),  # Selected comment lines
            'entrance_fill': QtGui.QColor(190, 0, 0, 120),  # Unselected entrance fill
            'entrance_fill_s': QtGui.QColor(190, 0, 0, 240),  # Selected entrance fill
            'entrance_lines': QtGui.QColor(0, 0, 0),  # Unselected entrance lines
            'entrance_lines_s': QtGui.QColor(255, 255, 255),  # Selected entrance lines
            'grid': QtGui.QColor(255, 255, 255, 100),  # Grid
            'location_fill': QtGui.QColor(114, 42, 188, 70),  # Unselected location fill
            'location_fill_s': QtGui.QColor(170, 128, 215, 100),  # Selected location fill
            'location_lines': QtGui.QColor(0, 0, 0),  # Unselected location lines
            'location_lines_s': QtGui.QColor(255, 255, 255),  # Selected location lines
            'location_text': QtGui.QColor(255, 255, 255),  # Location text
            'object_fill_s': QtGui.QColor(255, 255, 255, 64),  # Select object fill
            'object_lines_s': QtGui.QColor(255, 255, 255),  # Selected object lines
            'overview_entrance': QtGui.QColor(255, 0, 0),  # Overview entrance fill
            'overview_location_fill': QtGui.QColor(114, 42, 188, 50),  # Overview location fill
            'overview_location_lines': QtGui.QColor(0, 0, 0),  # Overview location lines
            'overview_object': QtGui.QColor(255, 255, 255),  # Overview object fill
            'overview_sprite': QtGui.QColor(0, 92, 196),  # Overview sprite fill
            'overview_viewbox': QtGui.QColor(0, 0, 255),  # Overview background fill
            'overview_zone_fill': QtGui.QColor(47, 79, 79, 120),  # Overview zone fill
            'overview_zone_lines': QtGui.QColor(0, 255, 255),  # Overview zone lines
            'path_connector': QtGui.QColor(6, 249, 20),  # Path node connecting lines
            'nabbit_path_connector': QtGui.QColor(161, 69, 255),  # Nabbit path node connecting lines
            'path_fill': QtGui.QColor(6, 249, 20, 120),  # Unselected path node fill
            'path_fill_s': QtGui.QColor(6, 249, 20, 240),  # Selected path node fill
            'nabbit_path_fill': QtGui.QColor(161, 69, 255, 120),  # Unselected nabbit path node fill
            'nabbit_path_fill_s': QtGui.QColor(161, 69, 255, 240),  # Selected nabbit path node fill
            'path_lines': QtGui.QColor(0, 0, 0),  # Unselected path node lines
            'path_lines_s': QtGui.QColor(255, 255, 255),  # Selected path node lines
            'nabbit_path_lines': QtGui.QColor(0, 0, 0),  # Unselected nabbit path node lines
            'nabbit_path_lines_s': QtGui.QColor(255, 255, 255),  # Selected nabbit path node lines
            'smi': QtGui.QColor(255, 255, 255, 80),  # Sprite movement indicator
            'sprite_fill_s': QtGui.QColor(255, 255, 255, 64),  # Selected sprite w/ image fill
            'sprite_lines_s': QtGui.QColor(255, 255, 255),  # Selected sprite w/ image lines
            'spritebox_fill': QtGui.QColor(0, 92, 196, 120),  # Unselected sprite w/o image fill
            'spritebox_fill_s': QtGui.QColor(0, 92, 196, 240),  # Selected sprite w/o image fill
            'spritebox_lines': QtGui.QColor(0, 0, 0),  # Unselected sprite w/o image fill
            'spritebox_lines_s': QtGui.QColor(255, 255, 255),  # Selected sprite w/o image fill
            'zone_entrance_helper': QtGui.QColor(190, 0, 0, 120),  # Zone entrance-placement left border indicator
            'zone_lines': QtGui.QColor(145, 200, 255, 176),  # Zone lines
            'zone_corner': QtGui.QColor(255, 255, 255),  # Zone grabbers/corners
            'zone_dark_fill': QtGui.QColor(0, 0, 0, 48),  # Zone fill when dark
            'zone_text': QtGui.QColor(44, 64, 84),  # Zone text
        }

    def initFromFolder(self, folder):
        """
        Initializes the theme from the folder
        """
        folder = os.path.join('miyamotodata', 'themes', folder)

        fileList = os.listdir(folder)

        # Create a XML ElementTree
        maintree = etree.parse(os.path.join(folder, 'main.xml'))
        root = maintree.getroot()

        # Parse the attributes of the <theme> tag
        if not self.parseMainXMLHead(root):
            # The attributes are messed up
            return

        # Parse the other nodes
        for node in root:
            if node.tag.lower() == 'colors':
                if 'file' not in node.attrib: continue

                # Load the colors XML
                self.loadColorsXml(os.path.join(folder, node.attrib['file']))

            elif node.tag.lower() == 'icons':
                if not all(thing in node.attrib for thing in ['size', 'folder']): continue

                foldername = node.attrib['folder']
                big = node.attrib['size'].lower()[:2] == 'lg'
                cache = self.iconCacheLg if big else self.iconCacheSm

                # Load the icons
                for iconfilename in fileList:
                    iconname = iconfilename
                    if not iconname.startswith(foldername + '/'): continue
                    iconname = iconname[len(foldername) + 1:]
                    if len(iconname) <= len('icon-.png'): continue
                    if not iconname.startswith('icon-') or not iconname.endswith('.png'): continue
                    iconname = iconname[len('icon-'): -len('.png')]

                    with open(os.path.join(folder, iconfilename), "rb") as inf:
                        icodata = inf.read()
                    pix = QtGui.QPixmap()
                    if not pix.loadFromData(icodata): continue
                    ico = QtGui.QIcon(pix)

                    cache[iconname] = ico

                ##        # Add some overview colors if they weren't specified
                ##        fallbacks = {
                ##            'overview_entrance': 'entrance_fill',
                ##            'overview_location_fill': 'location_fill',
                ##            'overview_location_lines': 'location_lines',
                ##            'overview_sprite': 'sprite_fill',
                ##            'overview_zone_lines': 'zone_lines',
                ##            }
                ##        for index in fallbacks:
                ##            if (index not in colors) and (fallbacks[index] in colors): colors[index] = colors[fallbacks[index]]
                ##
                ##        # Use the new colors dict to overwrite values in self.colors
                ##        for index in colors:
                ##            self.colors[index] = colors[index]

    def parseMainXMLHead(self, root):
        """
        Parses the main attributes of main.xml
        """
        MaxSupportedXMLVersion = 1.0

        # Check for required attributes
        if root.tag.lower() != 'theme': return False
        if 'format' in root.attrib:
            formatver = root.attrib['format']
            try:
                self.formatver = float(formatver)
            except ValueError:
                return False
        else:
            return False

        if self.formatver > MaxSupportedXMLVersion: return False
        if 'name' in root.attrib:
            self.themeName = root.attrib['name']
        else:
            return False

        # Check for optional attributes
        self.creator = globals.trans.string('Themes', 3)
        self.description = globals.trans.string('Themes', 4)
        self.style = None
        self.version = 1.0
        if 'creator' in root.attrib: self.creator = root.attrib['creator']
        if 'description' in root.attrib: self.description = root.attrib['description']
        if 'style' in root.attrib: self.style = root.attrib['style']
        if 'version' in root.attrib:
            try:
                self.version = float(root.attrib['version'])
            except ValueError:
                pass

        return True

    def loadColorsXml(self, file):
        """
        Loads a colors.xml file
        """
        try:
            tree = etree.parse(file)
        except Exception:
            return

        root = tree.getroot()
        if root.tag.lower() != 'colors': return False

        colorDict = {}
        for colorNode in root:
            if colorNode.tag.lower() != 'color': continue
            if not all(thing in colorNode.attrib for thing in ['id', 'value']): continue

            colorval = colorNode.attrib['value']
            if colorval.startswith('#'): colorval = colorval[1:]
            a = 255
            try:
                if len(colorval) == 3:
                    # RGB
                    r = int(colorval[0], 16)
                    g = int(colorval[1], 16)
                    b = int(colorval[2], 16)
                elif len(colorval) == 4:
                    # RGBA
                    r = int(colorval[0], 16)
                    g = int(colorval[1], 16)
                    b = int(colorval[2], 16)
                    a = int(colorval[3], 16)
                elif len(colorval) == 6:
                    # RRGGBB
                    r = int(colorval[0:2], 16)
                    g = int(colorval[2:4], 16)
                    b = int(colorval[4:6], 16)
                elif len(colorval) == 8:
                    # RRGGBBAA
                    r = int(colorval[0:2], 16)
                    g = int(colorval[2:4], 16)
                    b = int(colorval[4:6], 16)
                    a = int(colorval[6:8], 16)
            except ValueError:
                continue
            colorobj = QtGui.QColor(r, g, b, a)
            colorDict[colorNode.attrib['id']] = colorobj

        # Merge dictionaries
        self.colors.update(colorDict)

    def color(self, name):
        """
        Returns a color
        """
        try:
            return self.colors[name]

        except KeyError:
            return None

    def GetIcon(self, name, big=False):
        """
        Returns an icon
        """

        cache = self.iconCacheLg if big else self.iconCacheSm

        if name not in cache:
            path = 'miyamotodata/ico/lg/icon-' if big else 'miyamotodata/ico/sm/icon-'
            path += name
            cache[name] = QtGui.QIcon(path)

        return cache[name]

    def ui(self):
        """
        Returns the UI style
        """
        return self.uiStyle


def toQColor(*args):
    """
    Usage: toQColor(r, g, b[, a]) OR toQColor((r, g, b[, a]))
    """
    if len(args) == 1: args = args[0]
    r = args[0]
    g = args[1]
    b = args[2]
    a = args[3] if len(args) == 4 else 255
    return QtGui.QColor(r, g, b, a)


def createHorzLine():
    f = QtWidgets.QFrame()
    f.setFrameStyle(QtWidgets.QFrame.HLine | QtWidgets.QFrame.Sunken)
    return f


def createVertLine():
    f = QtWidgets.QFrame()
    f.setFrameStyle(QtWidgets.QFrame.VLine | QtWidgets.QFrame.Sunken)
    return f


def LoadNumberFont():
    """
    Creates a valid font we can use to display the item numbers
    """
    if globals.NumberFont is not None: return

    # this is a really crappy method, but I can't think of any other way
    # normal Qt defines Q_WS_WIN and Q_WS_MAC but we don't have that here
    s = QtCore.QSysInfo()
    if hasattr(s, 'WindowsVersion'):
        globals.NumberFont = QtGui.QFont('Tahoma', (7 / 24) * globals.TileWidth)
    elif hasattr(s, 'MacintoshVersion'):
        globals.NumberFont = QtGui.QFont('Lucida Grande', (9 / 24) * globals.TileWidth)
    else:
        globals.NumberFont = QtGui.QFont('Sans', (8 / 24) * globals.TileWidth)


def GetIcon(name, big=False):
    """
    Helper function to grab a specific icon
    """
    return globals.theme.GetIcon(name, big)
