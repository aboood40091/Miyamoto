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

# miyamoto.py
# This is the main executable for Miyamoto!


################################################################
################################################################

# Python version: sanity check
minimum = 3.4
import sys

currentRunningVersion = sys.version_info.major + (.1 * sys.version_info.minor)
if currentRunningVersion < minimum:
    errormsg = 'Please update your copy of Python to ' + str(minimum) + \
               ' or greater. Currently running on: ' + sys.version[:5]
    raise Exception(errormsg)

# Stdlib imports
import base64
import json
import os
import pickle
import platform
import struct
import sys
from xml.etree import ElementTree as etree
import zipfile

# PyQt5: import, and error msg if not installed
from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

if not hasattr(QtWidgets.QGraphicsItem, 'ItemSendsGeometryChanges'):
    # enables itemChange being called on QGraphicsItem
    QtWidgets.QGraphicsItem.ItemSendsGeometryChanges = QtWidgets.QGraphicsItem.GraphicsItemFlag(0x800)

# Local imports
from area import *
from bytes import *
from dialogs import *
from gamedefs import *
import globals
from items import *
from level import *
from libyaz0 import decompress as Yaz0Dec
from loading import *
from misc import *
from quickpaint import *
import SARC as SarcLib
import spritelib as SLib
import sprites
from stamp import *
from strings import *
from tileset import *
from ui import *
from verifications import *
from widgets import *

MiyamotoID = 'Miyamoto! Level Editor by AboodXD, Gota7, John10v10, Based on Reggie! NSMBU by RoadrunnerWMC, MrRean, Grop, and Reggie! by Treeki and Tempus'
MiyamotoVersion = '21.0'
MiyamotoVersionShort = ''
UpdateURL = ''


class MiyamotoWindow(QtWidgets.QMainWindow):
    """
    Miyamoto main level editor window
    """
    ZoomLevel = 100

    def CreateAction(self, shortname, function, icon, text, statustext, shortcut, toggle=False):
        """
        Helper function to create an action
        """

        if icon is not None:
            act = QtWidgets.QAction(icon, text, self)
        else:
            act = QtWidgets.QAction(text, self)

        if shortcut is not None: act.setShortcut(shortcut)
        if statustext is not None: act.setStatusTip(statustext)
        if toggle:
            act.setCheckable(True)
        if function is not None: act.triggered.connect(function)

        self.actions[shortname] = act

    def __init__(self):
        """
        Editor window constructor
        """
        globals.Initializing = True

        globals.ObjectAddedtoEmbedded = {1: {}}

        # Miyamoto Version number goes below here. 64 char max (32 if non-ascii).
        self.MiyamotoInfo = MiyamotoID

        self.ZoomLevels = [7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0,
                           85.0, 90.0, 95.0, 100.0, 125.0, 150.0, 175.0, 200.0, 250.0, 300.0, 350.0, 400.0]

        # required variables
        self.UpdateFlag = False
        self.SelectionUpdateFlag = False
        self.selObj = None
        self.CurrentSelection = []

        self.CurrentGame = setting('CurrentGame')
        if self.CurrentGame is None: self.CurrentGame = globals.NewSuperMarioBrosU

        # set up the window
        super().__init__(None)
        self.setWindowTitle('Miyamoto! v%s' % MiyamotoVersion)
        self.setWindowIcon(QtGui.QIcon('miyamotodata/icon.png'))
        self.setIconSize(QtCore.QSize(16, 16))
        self.setUnifiedTitleAndToolBarOnMac(True)

        # create the level view
        self.scene = LevelScene(0, 0, 1024 * globals.TileWidth, 512 * globals.TileWidth, self)
        self.scene.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)
        self.scene.selectionChanged.connect(self.ChangeSelectionHandler)

        self.view = LevelViewWidget(self.scene, self)
        self.view.centerOn(0, 0)  # this scrolls to the top left
        self.view.PositionHover.connect(self.PositionHovered)
        self.view.XScrollBar.valueChanged.connect(self.XScrollChange)
        self.view.YScrollBar.valueChanged.connect(self.YScrollChange)
        self.view.FrameSize.connect(self.HandleWindowSizeChange)

        # done creating the window!
        self.setCentralWidget(self.view)

        # set up the clipboard stuff
        self.clipboard = None
        self.systemClipboard = QtWidgets.QApplication.clipboard()
        self.systemClipboard.dataChanged.connect(self.TrackClipboardUpdates)

        # we might have something there already, activate Paste if so
        self.TrackClipboardUpdates()

    def __init2__(self):
        """
        Finishes initialization. (fixes bugs with some widgets calling globals.mainWindow.something before it's fully init'ed)
        """

        try:
            self.AutosaveTimer = QtCore.QTimer()
            self.AutosaveTimer.timeout.connect(self.Autosave)
            self.AutosaveTimer.start(20000)
        except TypeError:
            pass

        # set up actions and menus
        self.SetupActionsAndMenus()

        # set up the status bar
        self.posLabel = QtWidgets.QLabel()
        self.numUsedTilesLabel = QtWidgets.QLabel()
        self.selectionLabel = QtWidgets.QLabel()
        self.hoverLabel = QtWidgets.QLabel()
        self.statusBar().addWidget(self.posLabel)
        self.statusBar().addWidget(self.numUsedTilesLabel)
        self.statusBar().addWidget(self.selectionLabel)
        self.statusBar().addWidget(self.hoverLabel)
        self.ZoomWidget = ZoomWidget()
        self.ZoomStatusWidget = ZoomStatusWidget()
        self.statusBar().addPermanentWidget(self.ZoomWidget)
        self.statusBar().addPermanentWidget(self.ZoomStatusWidget)

        # create the various panels
        self.SetupDocksAndPanels()

        # now get stuff ready
        curgame = self.CurrentGame

        # load first level
        if '-level' in sys.argv:
            index = sys.argv.index('-level')
            try:
                fn = sys.argv[index + 1]
                self.LoadLevel(curgame, fn, True, 1)
            except:
                self.LoadLevel(curgame, globals.FirstLevels[curgame], False, 1)
        else:
            filetypes = ''
            filetypes += globals.trans.string('FileDlgs', 1) + ' (*.szs);;'
            filetypes += 'Uncompressed Level Archives (*.sarc);;'
            filetypes += globals.trans.string('FileDlgs', 2) + ' (*)'
            fn = QtWidgets.QFileDialog.getOpenFileName(self, globals.trans.string('FileDlgs', 0), '', filetypes)[0]
            if fn:
                self.LoadLevel(curgame, fn, True, 1)
            else:
                self.LoadLevel(curgame, globals.FirstLevels[curgame], False, 1)

        QtCore.QTimer.singleShot(100, self.levelOverview.update)

        toggleHandlers = {
            self.HandleSpritesVisibility: globals.SpritesShown,
            self.HandleSpriteImages: globals.SpriteImagesShown,
            self.HandleLocationsVisibility: globals.LocationsShown,
            self.HandleCommentsVisibility: globals.CommentsShown,
        }
        for handler in toggleHandlers:
            handler(
                toggleHandlers[handler])  # call each toggle-button handler to set each feature correctly upon startup

        # let's restore the state and geometry
        # geometry: determines the main window position
        # state: determines positions of docks
        if globals.settings.contains('MainWindowGeometry'):
            self.restoreGeometry(setting('MainWindowGeometry'))
        if globals.settings.contains('MainWindowState'):
            self.restoreState(setting('MainWindowState'), 0)

        # Load the most recently used gamedef
        LoadGameDef(setting('LastGameDef'), False)

        # Aaaaaand... initializing is done!
        globals.Initializing = False

    def SetupActionsAndMenus(self):
        """
        Sets up Miyamoto's actions, menus and toolbars
        """
        self.RecentMenu = RecentFilesMenu()

        self.createMenubar()

    actions = {}

    def createMenubar(self):
        """
        Create actions, a menubar and a toolbar
        """

        # File
        self.CreateAction('newlevel', self.HandleNewLevel, GetIcon('new'), globals.trans.string('MenuItems', 0),
                          globals.trans.string('MenuItems', 1), QtGui.QKeySequence.New)
        self.CreateAction('openfromname', self.HandleOpenFromName, GetIcon('open'), globals.trans.string('MenuItems', 2),
                          globals.trans.string('MenuItems', 3), QtGui.QKeySequence.Open)
        self.CreateAction('openfromfile', self.HandleOpenFromFile, GetIcon('openfromfile'),
                          globals.trans.string('MenuItems', 4), globals.trans.string('MenuItems', 5),
                          QtGui.QKeySequence('Ctrl+Shift+O'))
        self.CreateAction('openrecent', None, GetIcon('recent'), globals.trans.string('MenuItems', 6),
                          globals.trans.string('MenuItems', 7), None)
        self.CreateAction('save', self.HandleSave, GetIcon('save'), globals.trans.string('MenuItems', 8),
                          globals.trans.string('MenuItems', 9), QtGui.QKeySequence.Save)
        self.CreateAction('saveas', self.HandleSaveAs, GetIcon('saveas'), globals.trans.string('MenuItems', 10),
                          globals.trans.string('MenuItems', 11), QtGui.QKeySequence.SaveAs)
        self.CreateAction('screenshot', self.HandleScreenshot, GetIcon('screenshot'), globals.trans.string('MenuItems', 14),
                          globals.trans.string('MenuItems', 15), QtGui.QKeySequence('Ctrl+Alt+S'))
        self.CreateAction('changegamepath', self.HandleChangeGamePath, GetIcon('folderpath'),
                          globals.trans.string('MenuItems', 16), globals.trans.string('MenuItems', 17),
                          QtGui.QKeySequence('Ctrl+Alt+G'))
        self.CreateAction('changeobjpath', self.HandleChangeObjPath, GetIcon('folderpath'),
                          globals.trans.string('MenuItems', 132), globals.trans.string('MenuItems', 133),
                          None)
        # self.CreateAction('changesavepath', self.HandleChangeSavePath, GetIcon('folderpath'), globals.trans.string('MenuItems', 134), globals.trans.string('MenuItems', 135), QtGui.QKeySequence('Ctrl+Alt+L'))
        self.CreateAction('preferences', self.HandlePreferences, GetIcon('settings'), globals.trans.string('MenuItems', 18),
                          globals.trans.string('MenuItems', 19), QtGui.QKeySequence('Ctrl+Alt+P'))
        self.CreateAction('exit', self.HandleExit, GetIcon('delete'), globals.trans.string('MenuItems', 20),
                          globals.trans.string('MenuItems', 21), QtGui.QKeySequence('Ctrl+Q'))

        # Edit
        self.CreateAction('selectall', self.SelectAll, GetIcon('select'), globals.trans.string('MenuItems', 22),
                          globals.trans.string('MenuItems', 23), QtGui.QKeySequence.SelectAll)
        self.CreateAction('deselect', self.Deselect, GetIcon('deselect'), globals.trans.string('MenuItems', 24),
                          globals.trans.string('MenuItems', 25), QtGui.QKeySequence('Ctrl+D'))
        self.CreateAction('cut', self.Cut, GetIcon('cut'), globals.trans.string('MenuItems', 26), globals.trans.string('MenuItems', 27),
                          QtGui.QKeySequence.Cut)
        self.CreateAction('copy', self.Copy, GetIcon('copy'), globals.trans.string('MenuItems', 28),
                          globals.trans.string('MenuItems', 29), QtGui.QKeySequence.Copy)
        self.CreateAction('paste', self.Paste, GetIcon('paste'), globals.trans.string('MenuItems', 30),
                          globals.trans.string('MenuItems', 31), QtGui.QKeySequence.Paste)
        self.CreateAction('shiftitems', self.ShiftItems, GetIcon('move'), globals.trans.string('MenuItems', 32),
                          globals.trans.string('MenuItems', 33), QtGui.QKeySequence('Ctrl+Shift+S'))
        self.CreateAction('mergelocations', self.MergeLocations, GetIcon('merge'), globals.trans.string('MenuItems', 34),
                          globals.trans.string('MenuItems', 35), QtGui.QKeySequence('Ctrl+Shift+E'))
        self.CreateAction('swapobjectstilesets', self.SwapObjectsTilesets, GetIcon('swap'),
                          globals.trans.string('MenuItems', 104), globals.trans.string('MenuItems', 105),
                          QtGui.QKeySequence('Ctrl+Shift+L'))
        self.CreateAction('swapobjectstypes', self.SwapObjectsTypes, GetIcon('swap'), globals.trans.string('MenuItems', 106),
                          globals.trans.string('MenuItems', 107), QtGui.QKeySequence('Ctrl+Shift+Y'))
        self.CreateAction('freezeobjects', self.HandleObjectsFreeze, GetIcon('objectsfreeze'),
                          globals.trans.string('MenuItems', 38), globals.trans.string('MenuItems', 39),
                          QtGui.QKeySequence('Ctrl+Shift+1'), True)
        self.CreateAction('freezesprites', self.HandleSpritesFreeze, GetIcon('spritesfreeze'),
                          globals.trans.string('MenuItems', 40), globals.trans.string('MenuItems', 41),
                          QtGui.QKeySequence('Ctrl+Shift+2'), True)
        self.CreateAction('freezeentrances', self.HandleEntrancesFreeze, GetIcon('entrancesfreeze'),
                          globals.trans.string('MenuItems', 42), globals.trans.string('MenuItems', 43),
                          QtGui.QKeySequence('Ctrl+Shift+3'), True)
        self.CreateAction('freezelocations', self.HandleLocationsFreeze, GetIcon('locationsfreeze'),
                          globals.trans.string('MenuItems', 44), globals.trans.string('MenuItems', 45),
                          QtGui.QKeySequence('Ctrl+Shift+4'), True)
        self.CreateAction('freezepaths', self.HandlePathsFreeze, GetIcon('pathsfreeze'), globals.trans.string('MenuItems', 46),
                          globals.trans.string('MenuItems', 47), QtGui.QKeySequence('Ctrl+Shift+5'), True)
        self.CreateAction('freezecomments', self.HandleCommentsFreeze, GetIcon('commentsfreeze'),
                          globals.trans.string('MenuItems', 114), globals.trans.string('MenuItems', 115),
                          QtGui.QKeySequence('Ctrl+Shift+9'), True)

        # View
        self.CreateAction('showlay0', self.HandleUpdateLayer0, GetIcon('layer0'), globals.trans.string('MenuItems', 48),
                          globals.trans.string('MenuItems', 49), QtGui.QKeySequence('Ctrl+1'), True)
        self.CreateAction('showlay1', self.HandleUpdateLayer1, GetIcon('layer1'), globals.trans.string('MenuItems', 50),
                          globals.trans.string('MenuItems', 51), QtGui.QKeySequence('Ctrl+2'), True)
        self.CreateAction('showlay2', self.HandleUpdateLayer2, GetIcon('layer2'), globals.trans.string('MenuItems', 52),
                          globals.trans.string('MenuItems', 53), QtGui.QKeySequence('Ctrl+3'), True)
        self.CreateAction('tileanim', self.HandleTilesetAnimToggle, GetIcon('animation'),
                          globals.trans.string('MenuItems', 108), globals.trans.string('MenuItems', 109),
                          QtGui.QKeySequence('Ctrl+7'), True)
        self.CreateAction('collisions', self.HandleCollisionsToggle, GetIcon('collisions'),
                          globals.trans.string('MenuItems', 110), globals.trans.string('MenuItems', 111),
                          QtGui.QKeySequence('Ctrl+8'), True)
        self.CreateAction('realview', self.HandleRealViewToggle, GetIcon('realview'),
                          globals.trans.string('MenuItems', 118), globals.trans.string('MenuItems', 119),
                          QtGui.QKeySequence('Ctrl+9'), True)
        self.CreateAction('showsprites', self.HandleSpritesVisibility, GetIcon('sprites'),
                          globals.trans.string('MenuItems', 54), globals.trans.string('MenuItems', 55), QtGui.QKeySequence('Ctrl+4'),
                          True)
        self.CreateAction('showspriteimages', self.HandleSpriteImages, GetIcon('sprites'),
                          globals.trans.string('MenuItems', 56), globals.trans.string('MenuItems', 57), QtGui.QKeySequence('Ctrl+6'),
                          True)
        self.CreateAction('showlocations', self.HandleLocationsVisibility, GetIcon('locations'),
                          globals.trans.string('MenuItems', 58), globals.trans.string('MenuItems', 59), QtGui.QKeySequence('Ctrl+5'),
                          True)
        self.CreateAction('showcomments', self.HandleCommentsVisibility, GetIcon('comments'),
                          globals.trans.string('MenuItems', 116), globals.trans.string('MenuItems', 117), QtGui.QKeySequence('Ctrl+0'),
                          True)
        self.CreateAction('fullscreen', self.HandleFullscreen, GetIcon('fullscreen'), globals.trans.string('MenuItems', 126),
                          globals.trans.string('MenuItems', 127), QtGui.QKeySequence('Ctrl+U'), True)
        self.CreateAction('grid', self.HandleSwitchGrid, GetIcon('grid'), globals.trans.string('MenuItems', 60),
                          globals.trans.string('MenuItems', 61), QtGui.QKeySequence('Ctrl+G'), False)
        self.CreateAction('zoommax', self.HandleZoomMax, GetIcon('zoommax'), globals.trans.string('MenuItems', 62),
                          globals.trans.string('MenuItems', 63), QtGui.QKeySequence('Ctrl+PgDown'), False)
        self.CreateAction('zoomin', self.HandleZoomIn, GetIcon('zoomin'), globals.trans.string('MenuItems', 64),
                          globals.trans.string('MenuItems', 65), QtGui.QKeySequence.ZoomIn, False)
        self.CreateAction('zoomactual', self.HandleZoomActual, GetIcon('zoomactual'), globals.trans.string('MenuItems', 66),
                          globals.trans.string('MenuItems', 67), QtGui.QKeySequence('Ctrl+0'), False)
        self.CreateAction('zoomout', self.HandleZoomOut, GetIcon('zoomout'), globals.trans.string('MenuItems', 68),
                          globals.trans.string('MenuItems', 69), QtGui.QKeySequence.ZoomOut, False)
        self.CreateAction('zoommin', self.HandleZoomMin, GetIcon('zoommin'), globals.trans.string('MenuItems', 70),
                          globals.trans.string('MenuItems', 71), QtGui.QKeySequence('Ctrl+PgUp'), False)
        # Show Overview and Show Palette are added later

        # Settings
        self.CreateAction('areaoptions', self.HandleAreaOptions, GetIcon('area'), globals.trans.string('MenuItems', 72),
                          globals.trans.string('MenuItems', 73), QtGui.QKeySequence('Ctrl+Alt+A'))
        self.CreateAction('zones', self.HandleZones, GetIcon('zones'), globals.trans.string('MenuItems', 74),
                          globals.trans.string('MenuItems', 75), QtGui.QKeySequence('Ctrl+Alt+Z'))
        self.CreateAction('backgrounds', self.HandleBG, GetIcon('background'), globals.trans.string('MenuItems', 76),
                          globals.trans.string('MenuItems', 77), QtGui.QKeySequence('Ctrl+Alt+B'))
        self.CreateAction('addarea', self.HandleAddNewArea, GetIcon('add'), globals.trans.string('MenuItems', 78),
                          globals.trans.string('MenuItems', 79), QtGui.QKeySequence('Ctrl+Alt+N'))
        self.CreateAction('importarea', self.HandleImportArea, GetIcon('import'), globals.trans.string('MenuItems', 80),
                          globals.trans.string('MenuItems', 81), QtGui.QKeySequence('Ctrl+Alt+O'))
        self.CreateAction('deletearea', self.HandleDeleteArea, GetIcon('delete'), globals.trans.string('MenuItems', 82),
                          globals.trans.string('MenuItems', 83), QtGui.QKeySequence('Ctrl+Alt+D'))
        self.CreateAction('reloaddata', self.ReloadSpriteData, GetIcon('reload'), globals.trans.string('MenuItems', 128),
                          globals.trans.string('MenuItems', 129), QtGui.QKeySequence('Ctrl+Shift+R'))
        self.CreateAction('overwritesprite', self.HandleOverwriteSprite, GetIcon('folderpath'),
                          globals.trans.string('MenuItems', 134), globals.trans.string('MenuItems', 135), None, True)

        # Tilesets
        self.CreateAction('editslot1', self.EditSlot1, GetIcon('animation'), globals.trans.string('MenuItems', 130),
                          globals.trans.string('MenuItems', 131), None)

        # Help actions are created later


        # Configure them
        self.actions['openrecent'].setMenu(self.RecentMenu)

        self.actions['collisions'].setChecked(globals.CollisionsShown)
        self.actions['realview'].setChecked(globals.RealViewEnabled)

        self.actions['showsprites'].setChecked(globals.SpritesShown)
        self.actions['showspriteimages'].setChecked(globals.SpriteImagesShown)
        self.actions['showlocations'].setChecked(globals.LocationsShown)
        self.actions['showcomments'].setChecked(globals.CommentsShown)

        self.actions['freezeobjects'].setChecked(globals.ObjectsFrozen)
        self.actions['freezesprites'].setChecked(globals.SpritesFrozen)
        self.actions['freezeentrances'].setChecked(globals.EntrancesFrozen)
        self.actions['freezelocations'].setChecked(globals.LocationsFrozen)
        self.actions['freezepaths'].setChecked(globals.PathsFrozen)
        self.actions['freezecomments'].setChecked(globals.CommentsFrozen)

        self.actions['overwritesprite'].setChecked(globals.OverwriteSprite)

        self.actions['cut'].setEnabled(False)
        self.actions['copy'].setEnabled(False)
        self.actions['paste'].setEnabled(False)
        self.actions['shiftitems'].setEnabled(False)
        self.actions['mergelocations'].setEnabled(False)
        self.actions['deselect'].setEnabled(False)

        ####
        menubar = QtWidgets.QMenuBar()
        self.setMenuBar(menubar)

        fmenu = menubar.addMenu(globals.trans.string('Menubar', 0))
        fmenu.addAction(self.actions['newlevel'])
        fmenu.addAction(self.actions['openfromname'])
        fmenu.addAction(self.actions['openfromfile'])
        fmenu.addAction(self.actions['openrecent'])
        fmenu.addSeparator()
        fmenu.addAction(self.actions['save'])
        fmenu.addAction(self.actions['saveas'])
        fmenu.addSeparator()
        fmenu.addAction(self.actions['screenshot'])
        fmenu.addAction(self.actions['changegamepath'])
        fmenu.addAction(self.actions['changeobjpath'])
        # fmenu.addAction(self.actions['changesavepath'])
        fmenu.addAction(self.actions['preferences'])
        fmenu.addSeparator()
        fmenu.addAction(self.actions['exit'])

        emenu = menubar.addMenu(globals.trans.string('Menubar', 1))
        emenu.addAction(self.actions['selectall'])
        emenu.addAction(self.actions['deselect'])
        emenu.addSeparator()
        emenu.addAction(self.actions['cut'])
        emenu.addAction(self.actions['copy'])
        emenu.addAction(self.actions['paste'])
        emenu.addSeparator()
        emenu.addAction(self.actions['shiftitems'])
        emenu.addAction(self.actions['mergelocations'])
        emenu.addAction(self.actions['swapobjectstilesets'])
        emenu.addAction(self.actions['swapobjectstypes'])
        emenu.addSeparator()
        emenu.addAction(self.actions['freezeobjects'])
        emenu.addAction(self.actions['freezesprites'])
        emenu.addAction(self.actions['freezeentrances'])
        emenu.addAction(self.actions['freezelocations'])
        emenu.addAction(self.actions['freezepaths'])
        emenu.addAction(self.actions['freezecomments'])

        vmenu = menubar.addMenu(globals.trans.string('Menubar', 2))
        vmenu.addAction(self.actions['showlay0'])
        vmenu.addAction(self.actions['showlay1'])
        vmenu.addAction(self.actions['showlay2'])
        vmenu.addAction(self.actions['tileanim'])
        vmenu.addAction(self.actions['collisions'])
        vmenu.addAction(self.actions['realview'])
        vmenu.addSeparator()
        vmenu.addAction(self.actions['showsprites'])
        vmenu.addAction(self.actions['showspriteimages'])
        vmenu.addAction(self.actions['showlocations'])
        vmenu.addAction(self.actions['showcomments'])
        vmenu.addSeparator()
        vmenu.addAction(self.actions['fullscreen'])
        vmenu.addAction(self.actions['grid'])
        vmenu.addSeparator()
        vmenu.addAction(self.actions['zoommax'])
        vmenu.addAction(self.actions['zoomin'])
        vmenu.addAction(self.actions['zoomactual'])
        vmenu.addAction(self.actions['zoomout'])
        vmenu.addAction(self.actions['zoommin'])
        vmenu.addSeparator()
        # self.levelOverviewDock.toggleViewAction() is added here later
        # so we assign it to self.vmenu
        self.vmenu = vmenu

        lmenu = menubar.addMenu(globals.trans.string('Menubar', 3))
        lmenu.addAction(self.actions['areaoptions'])
        lmenu.addAction(self.actions['zones'])
        lmenu.addAction(self.actions['backgrounds'])
        lmenu.addSeparator()
        lmenu.addAction(self.actions['addarea'])
        lmenu.addAction(self.actions['importarea'])
        lmenu.addAction(self.actions['deletearea'])
        lmenu.addSeparator()
        lmenu.addAction(self.actions['reloaddata'])
        lmenu.addSeparator()
        lmenu.addAction(self.actions['overwritesprite'])

        tmenu = menubar.addMenu(globals.trans.string('Menubar', 4))
        tmenu.addAction(self.actions['editslot1'])

        hmenu = menubar.addMenu(globals.trans.string('Menubar', 5))
        self.SetupHelpMenu(hmenu)

        # create a toolbar
        self.toolbar = self.addToolBar(globals.trans.string('Menubar', 6))
        self.toolbar.setObjectName('MainToolbar')

        # Add buttons to the toolbar
        self.addToolbarButtons()

        # Add the area combo box
        self.areaComboBox = QtWidgets.QComboBox()
        self.areaComboBox.activated.connect(self.HandleSwitchArea)
        self.toolbar.addWidget(self.areaComboBox)

    def SetupHelpMenu(self, menu=None):
        """
        Creates the help menu. This is separate because both the menubar uses this
        """
        self.CreateAction('infobox', self.AboutBox, GetIcon('miyamoto'), globals.trans.string('MenuItems', 86),
                          globals.trans.string('MenuItems', 87), QtGui.QKeySequence('Ctrl+Shift+I'))
        self.CreateAction('helpbox', self.HelpBox, GetIcon('contents'), globals.trans.string('MenuItems', 88),
                          globals.trans.string('MenuItems', 89), QtGui.QKeySequence('Ctrl+Shift+H'))
        self.CreateAction('tipbox', self.TipBox, GetIcon('tips'), globals.trans.string('MenuItems', 90),
                          globals.trans.string('MenuItems', 91), QtGui.QKeySequence('Ctrl+Shift+T'))
        self.CreateAction('aboutqt', QtWidgets.qApp.aboutQt, GetIcon('qt'), globals.trans.string('MenuItems', 92),
                          globals.trans.string('MenuItems', 93), QtGui.QKeySequence('Ctrl+Shift+Q'))

        if menu is None:
            menu = QtWidgets.QMenu(globals.trans.string('Menubar', 5))
        menu.addAction(self.actions['infobox'])
        menu.addAction(self.actions['helpbox'])
        menu.addAction(self.actions['tipbox'])
        menu.addSeparator()
        menu.addAction(self.actions['aboutqt'])
        return menu

    def addToolbarButtons(self):
        """
        Reads from the Preferences file and adds the appropriate options to the toolbar
        """
        # First, define groups. Each group is isolated by separators.
        Groups = (
            (
                'newlevel',
                'openfromname',
                'openfromfile',
                'openrecent',
                'save',
                'saveas',
                'screenshot',
                'changegamepath',
                'changeobjpath',
                # 'changesavepath',
                'preferences',
                'exit',
            ), (
                'selectall',
                'deselect',
            ), (
                'cut',
                'copy',
                'paste',
            ), (
                'shiftitems',
                'mergelocations',
            ), (
                'freezeobjects',
                'freezesprites',
                'freezeentrances',
                'freezelocations',
                'freezepaths',
            ), (
                'zoommax',
                'zoomin',
                'zoomactual',
                'zoomout',
                'zoommin',
            ), (
                'grid',
            ), (
                'showlay0',
                'showlay1',
                'showlay2',
            ), (
                'showsprites',
                'showspriteimages',
                'showlocations',
            ), (
                'areaoptions',
                'zones',
                'backgrounds',
            ), (
                'addarea',
                'importarea',
                'deletearea',
            ), (
                'reloaddata',
            ), (
                'editslot1',
            ), (
                'infobox',
                'helpbox',
                'tipbox',
                'aboutqt',
            ),
        )

        # Determine which keys are activated
        if setting('ToolbarActs') in (None, 'None', 'none', '', 0):
            # Get the default settings
            toggled = {}
            for List in (globals.FileActions, globals.EditActions, globals.ViewActions, globals.SettingsActions, globals.TileActions, globals.HelpActions):
                for name, activated, key in List:
                    toggled[key] = activated
        else:  # Get the registry settings
            toggled = setting('ToolbarActs')
            newToggled = {}  # here, I'm replacing QStrings w/ python strings
            for key in toggled:
                newToggled[str(key)] = toggled[key]
            toggled = newToggled

        # Add each to the toolbar if toggled[key]
        for group in Groups:
            addedButtons = False
            for key in group:
                if key in toggled and toggled[key] and key != 'save':
                    act = self.actions[key]
                    self.toolbar.addAction(act)
                    addedButtons = True
            if addedButtons:
                self.toolbar.addSeparator()

    def SetupDocksAndPanels(self):
        """
        Sets up the dock widgets and panels
        """
        # level overview
        dock = QtWidgets.QDockWidget(globals.trans.string('MenuItems', 94), self)
        dock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetClosable)
        # dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('leveloverview')  # needed for the state to save/restore correctly

        self.levelOverview = LevelOverviewWidget()
        self.levelOverview.moveIt.connect(self.HandleOverviewClick)
        self.levelOverviewDock = dock
        dock.setWidget(self.levelOverview)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setVisible(True)
        act = dock.toggleViewAction()
        act.setShortcut(QtGui.QKeySequence('Ctrl+M'))
        act.setIcon(GetIcon('overview'))
        act.setStatusTip(globals.trans.string('MenuItems', 95))
        self.vmenu.addAction(act)
		
        # quick paint configuration
        dock = QtWidgets.QDockWidget(globals.trans.string('MenuItems', 136), self)
        dock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetClosable)
        # dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('quickpaint')  # needed for the state to save/restore correctly #

        self.quickPaint = QuickPaintConfigWidget()
        #self.quickPaint.moveIt.connect(self.HandleOverviewClick)
        self.quickPaintDock = dock
        dock.setWidget(self.quickPaint)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setVisible(True)
        act = dock.toggleViewAction()
        act.setShortcut(QtGui.QKeySequence('Alt+Q'))
        act.setIcon(GetIcon('quickpaint'))
        act.setStatusTip(globals.trans.string('MenuItems', 137))
        self.vmenu.addAction(act)

        # create the sprite editor panel
        dock = QtWidgets.QDockWidget(globals.trans.string('SpriteDataEditor', 0), self)
        dock.setVisible(False)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('spriteeditor')  # needed for the state to save/restore correctly

        self.spriteDataEditor = SpriteEditorWidget()
        self.spriteDataEditor.DataUpdate.connect(self.SpriteDataUpdated)
        dock.setWidget(self.spriteDataEditor)
        self.spriteEditorDock = dock

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setFloating(True)

        # create the entrance editor panel
        dock = QtWidgets.QDockWidget(globals.trans.string('EntranceDataEditor', 24), self)
        dock.setVisible(False)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('entranceeditor')  # needed for the state to save/restore correctly

        self.entranceEditor = EntranceEditorWidget()
        dock.setWidget(self.entranceEditor)
        self.entranceEditorDock = dock

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setFloating(True)

        # create the path node editor panel
        dock = QtWidgets.QDockWidget(globals.trans.string('PathDataEditor', 10), self)
        dock.setVisible(False)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('pathnodeeditor')  # needed for the state to save/restore correctly

        self.pathEditor = PathNodeEditorWidget()
        dock.setWidget(self.pathEditor)
        self.pathEditorDock = dock

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setFloating(True)

        # create the location editor panel
        dock = QtWidgets.QDockWidget(globals.trans.string('LocationDataEditor', 12), self)
        dock.setVisible(False)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('locationeditor')  # needed for the state to save/restore correctly

        self.locationEditor = LocationEditorWidget()
        dock.setWidget(self.locationEditor)
        self.locationEditorDock = dock

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setFloating(True)

        # create the palette
        dock = QtWidgets.QDockWidget(globals.trans.string('MenuItems', 96), self)
        dock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetClosable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('palette')  # needed for the state to save/restore correctly

        self.creationDock = dock
        act = dock.toggleViewAction()
        act.setShortcut(QtGui.QKeySequence('Ctrl+P'))
        act.setIcon(GetIcon('palette'))
        act.setStatusTip(globals.trans.string('MenuItems', 97))
        self.vmenu.addAction(act)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setVisible(True)

        # add tabs to it
        tabs = QtWidgets.QTabWidget()
        tabs.setIconSize(QtCore.QSize(16, 16))
        tabs.currentChanged.connect(self.CreationTabChanged)
        dock.setWidget(tabs)
        self.creationTabs = tabs

        # object choosing tabs
        tsicon = GetIcon('objects')

        self.objAllTab = QtWidgets.QTabWidget()
        self.objAllTab.currentChanged.connect(self.ObjTabChanged)
        tabs.addTab(self.objAllTab, tsicon, '')
        tabs.setTabToolTip(0, globals.trans.string('Palette', 13))

        self.objTS0Tab = QtWidgets.QWidget()
        self.objTSAllTab = QtWidgets.QWidget()
        self.objTS123Tab = QtWidgets.QWidget()
        self.objAllTab.addTab(self.objTS0Tab, tsicon, 'Main')
        self.objAllTab.addTab(self.objTSAllTab, tsicon, 'All')
        self.objAllTab.addTab(self.objTS123Tab, tsicon, 'Embedded')

        oel = QtWidgets.QVBoxLayout(self.objTS0Tab)
        self.createObjectLayout = oel

        ll = QtWidgets.QHBoxLayout()
        self.objUseLayer0 = QtWidgets.QRadioButton('0')
        self.objUseLayer0.setToolTip(globals.trans.string('Palette', 1))
        self.objUseLayer1 = QtWidgets.QRadioButton('1')
        self.objUseLayer1.setToolTip(globals.trans.string('Palette', 2))
        self.objUseLayer2 = QtWidgets.QRadioButton('2')
        self.objUseLayer2.setToolTip(globals.trans.string('Palette', 3))
        ll.addWidget(QtWidgets.QLabel(globals.trans.string('Palette', 0)))
        ll.addWidget(self.objUseLayer0)
        ll.addWidget(self.objUseLayer1)
        ll.addWidget(self.objUseLayer2)
        ll.addStretch(1)
        oel.addLayout(ll)

        lbg = QtWidgets.QButtonGroup(self)
        lbg.addButton(self.objUseLayer0, 0)
        lbg.addButton(self.objUseLayer1, 1)
        lbg.addButton(self.objUseLayer2, 2)
        lbg.buttonClicked[int].connect(self.LayerChoiceChanged)
        self.LayerButtonGroup = lbg

        self.folderPicker = QtWidgets.QComboBox()

        top_folder = setting('ObjPath')

        if not (top_folder and os.path.isdir(top_folder)):
            self.objAllTab.setTabEnabled(1, False)

        else:
            i = 0
            for folder in os.listdir(top_folder):
                if os.path.isdir(top_folder + "/" + folder):
                    globals.ObjectAddedtoEmbedded[globals.CurrentArea][i] = {}
                    self.folderPicker.addItem(folder)
                    i += 1

        self.folderPicker.setVisible(False)
        oel.addWidget(self.folderPicker, 1)

        self.importObj = QtWidgets.QPushButton()
        self.importObj.setText("Import")
        self.importObj.clicked.connect(self.ImportObjFromFile)
        self.importObj.setVisible(False)
        oel.addWidget(self.importObj, 1)

        self.exportAll = QtWidgets.QPushButton()
        self.exportAll.setText("Export All")
        self.exportAll.clicked.connect(self.HandleExportAllObj)
        self.exportAll.setVisible(False)
        oel.addWidget(self.exportAll, 1)

        self.deleteAll = QtWidgets.QPushButton()
        self.deleteAll.setText("Delete All")
        self.deleteAll.clicked.connect(self.HandleDeleteAllObj)
        self.deleteAll.setVisible(False)
        oel.addWidget(self.deleteAll, 1)

        self.objPicker = ObjectPickerWidget()
        self.objPicker.ObjChanged.connect(self.ObjectChoiceChanged)
        self.objPicker.ObjReplace.connect(self.ObjectReplace)
        oel.addWidget(self.objPicker, 1)

        if top_folder and os.path.isdir(top_folder):
            def UpdateObjFolder():
                self.objPicker.mall.LoadFromFolder()

            UpdateObjFolder()

            self.folderPicker.currentIndexChanged.connect(UpdateObjFolder)

        # sprite tab
        self.sprAllTab = QtWidgets.QTabWidget()
        self.sprAllTab.currentChanged.connect(self.SprTabChanged)
        tabs.addTab(self.sprAllTab, GetIcon('sprites'), '')
        tabs.setTabToolTip(1, globals.trans.string('Palette', 14))

        # sprite tab: add
        self.sprPickerTab = QtWidgets.QWidget()
        self.sprAllTab.addTab(self.sprPickerTab, GetIcon('spritesadd'), globals.trans.string('Palette', 25))

        spl = QtWidgets.QVBoxLayout(self.sprPickerTab)
        self.sprPickerLayout = spl

        svpl = QtWidgets.QHBoxLayout()
        svpl.addWidget(QtWidgets.QLabel(globals.trans.string('Palette', 4)))

        sspl = QtWidgets.QHBoxLayout()
        sspl.addWidget(QtWidgets.QLabel(globals.trans.string('Palette', 5)))

        LoadSpriteCategories()
        viewpicker = QtWidgets.QComboBox()
        for view in globals.SpriteCategories:
            viewpicker.addItem(view[0])
        viewpicker.currentIndexChanged.connect(self.SelectNewSpriteView)

        self.spriteViewPicker = viewpicker
        svpl.addWidget(viewpicker, 1)

        self.spriteSearchTerm = QtWidgets.QLineEdit()
        self.spriteSearchTerm.textChanged.connect(self.NewSearchTerm)
        sspl.addWidget(self.spriteSearchTerm, 1)

        spl.addLayout(svpl)
        spl.addLayout(sspl)

        self.spriteSearchLayout = sspl
        sspl.itemAt(0).widget().setVisible(False)
        sspl.itemAt(1).widget().setVisible(False)

        self.sprPicker = SpritePickerWidget()
        self.sprPicker.SpriteChanged.connect(self.SpriteChoiceChanged)
        self.sprPicker.SpriteReplace.connect(self.SpriteReplace)
        self.sprPicker.SwitchView(globals.SpriteCategories[0])
        spl.addWidget(self.sprPicker, 1)

        self.defaultPropButton = QtWidgets.QPushButton(globals.trans.string('Palette', 6))
        self.defaultPropButton.setEnabled(False)
        self.defaultPropButton.clicked.connect(self.ShowDefaultProps)

        sdpl = QtWidgets.QHBoxLayout()
        sdpl.addStretch(1)
        sdpl.addWidget(self.defaultPropButton)
        sdpl.addStretch(1)
        spl.addLayout(sdpl)

        # default sprite data editor
        ddock = QtWidgets.QDockWidget(globals.trans.string('Palette', 7), self)
        ddock.setFeatures(
            QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetClosable)
        ddock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        ddock.setObjectName('defaultprops')  # needed for the state to save/restore correctly

        self.defaultDataEditor = SpriteEditorWidget(True)
        self.defaultDataEditor.setVisible(False)
        ddock.setWidget(self.defaultDataEditor)

        self.addDockWidget(Qt.RightDockWidgetArea, ddock)
        ddock.setVisible(False)
        ddock.setFloating(True)
        self.defaultPropDock = ddock

        # sprite tab: current
        self.sprEditorTab = QtWidgets.QWidget()
        self.sprAllTab.addTab(self.sprEditorTab, GetIcon('spritelist'), globals.trans.string('Palette', 26))

        spel = QtWidgets.QVBoxLayout(self.sprEditorTab)
        self.sprEditorLayout = spel

        slabel = QtWidgets.QLabel(globals.trans.string('Palette', 11))
        slabel.setWordWrap(True)
        self.spriteList = ListWidgetWithToolTipSignal()
        self.spriteList.itemActivated.connect(self.HandleSpriteSelectByList)
        self.spriteList.toolTipAboutToShow.connect(self.HandleSpriteToolTipAboutToShow)
        self.spriteList.setSortingEnabled(True)

        spel.addWidget(slabel)
        spel.addWidget(self.spriteList)

        # entrance tab
        self.entEditorTab = QtWidgets.QWidget()
        tabs.addTab(self.entEditorTab, GetIcon('entrances'), '')
        tabs.setTabToolTip(2, globals.trans.string('Palette', 15))

        eel = QtWidgets.QVBoxLayout(self.entEditorTab)
        self.entEditorLayout = eel

        elabel = QtWidgets.QLabel(globals.trans.string('Palette', 8))
        elabel.setWordWrap(True)
        self.entranceList = ListWidgetWithToolTipSignal()
        self.entranceList.itemActivated.connect(self.HandleEntranceSelectByList)
        self.entranceList.toolTipAboutToShow.connect(self.HandleEntranceToolTipAboutToShow)
        self.entranceList.setSortingEnabled(True)

        eel.addWidget(elabel)
        eel.addWidget(self.entranceList)

        # locations tab
        self.locEditorTab = QtWidgets.QWidget()
        tabs.addTab(self.locEditorTab, GetIcon('locations'), '')
        tabs.setTabToolTip(3, globals.trans.string('Palette', 16))

        locL = QtWidgets.QVBoxLayout(self.locEditorTab)
        self.locEditorLayout = locL

        Llabel = QtWidgets.QLabel(globals.trans.string('Palette', 12))
        Llabel.setWordWrap(True)
        self.locationList = ListWidgetWithToolTipSignal()
        self.locationList.itemActivated.connect(self.HandleLocationSelectByList)
        self.locationList.toolTipAboutToShow.connect(self.HandleLocationToolTipAboutToShow)
        self.locationList.setSortingEnabled(True)

        locL.addWidget(Llabel)
        locL.addWidget(self.locationList)

        # paths tab
        self.pathEditorTab = QtWidgets.QWidget()
        tabs.addTab(self.pathEditorTab, GetIcon('paths'), '')
        tabs.setTabToolTip(4, globals.trans.string('Palette', 17))

        pathel = QtWidgets.QVBoxLayout(self.pathEditorTab)
        self.pathEditorLayout = pathel

        pathlabel = QtWidgets.QLabel(globals.trans.string('Palette', 9))
        pathlabel.setWordWrap(True)
        deselectbtn = QtWidgets.QPushButton(globals.trans.string('Palette', 10))
        deselectbtn.clicked.connect(self.DeselectPathSelection)
        self.pathList = ListWidgetWithToolTipSignal()
        self.pathList.itemActivated.connect(self.HandlePathSelectByList)
        self.pathList.toolTipAboutToShow.connect(self.HandlePathToolTipAboutToShow)
        self.pathList.setSortingEnabled(True)

        pathel.addWidget(pathlabel)
        pathel.addWidget(deselectbtn)
        pathel.addWidget(self.pathList)

        # events tab
        self.eventEditorTab = QtWidgets.QWidget()
        tabs.addTab(self.eventEditorTab, GetIcon('events'), '')
        tabs.setTabToolTip(6, globals.trans.string('Palette', 18))
        tabs.setTabEnabled(6, False)

        eventel = QtWidgets.QGridLayout(self.eventEditorTab)
        self.eventEditorLayout = eventel

        eventlabel = QtWidgets.QLabel(globals.trans.string('Palette', 20))
        eventNotesLabel = QtWidgets.QLabel(globals.trans.string('Palette', 21))
        self.eventNotesEditor = QtWidgets.QLineEdit()
        self.eventNotesEditor.textEdited.connect(self.handleEventNotesEdit)

        self.eventChooser = QtWidgets.QTreeWidget()
        self.eventChooser.setColumnCount(2)
        self.eventChooser.setHeaderLabels((globals.trans.string('Palette', 22), globals.trans.string('Palette', 23)))
        self.eventChooser.itemClicked.connect(self.handleEventTabItemClick)
        self.eventChooserItems = []
        flags = Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        for id in range(32):
            itm = QtWidgets.QTreeWidgetItem()
            itm.setFlags(flags)
            itm.setCheckState(0, Qt.Unchecked)
            itm.setText(0, globals.trans.string('Palette', 24, '[id]', str(id + 1)))
            itm.setText(1, '')
            self.eventChooser.addTopLevelItem(itm)
            self.eventChooserItems.append(itm)
            if id == 0: itm.setSelected(True)

        eventel.addWidget(eventlabel, 0, 0, 1, 2)
        eventel.addWidget(eventNotesLabel, 1, 0)
        eventel.addWidget(self.eventNotesEditor, 1, 1)
        eventel.addWidget(self.eventChooser, 2, 0, 1, 2)

        # stamps tab
        self.stampTab = QtWidgets.QWidget()
        tabs.addTab(self.stampTab, GetIcon('stamp'), '')
        tabs.setTabToolTip(7, globals.trans.string('Palette', 19))

        stampLabel = QtWidgets.QLabel(globals.trans.string('Palette', 27))

        stampAddBtn = QtWidgets.QPushButton(globals.trans.string('Palette', 28))
        stampAddBtn.clicked.connect(self.handleStampsAdd)
        stampAddBtn.setEnabled(False)
        self.stampAddBtn = stampAddBtn  # so we can enable/disable it later
        stampRemoveBtn = QtWidgets.QPushButton(globals.trans.string('Palette', 29))
        stampRemoveBtn.clicked.connect(self.handleStampsRemove)
        stampRemoveBtn.setEnabled(False)
        self.stampRemoveBtn = stampRemoveBtn  # so we can enable/disable it later

        menu = QtWidgets.QMenu()
        menu.addAction(globals.trans.string('Palette', 31), self.handleStampsOpen, 0)  # Open Set...
        menu.addAction(globals.trans.string('Palette', 32), self.handleStampsSave, 0)  # Save Set As...
        stampToolsBtn = QtWidgets.QToolButton()
        stampToolsBtn.setText(globals.trans.string('Palette', 30))
        stampToolsBtn.setMenu(menu)
        stampToolsBtn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        stampToolsBtn.setSizePolicy(stampAddBtn.sizePolicy())
        stampToolsBtn.setMinimumHeight(stampAddBtn.height() / 20)

        stampNameLabel = QtWidgets.QLabel(globals.trans.string('Palette', 35))
        self.stampNameEdit = QtWidgets.QLineEdit()
        self.stampNameEdit.setEnabled(False)
        self.stampNameEdit.textChanged.connect(self.handleStampNameEdited)

        nameLayout = QtWidgets.QHBoxLayout()
        nameLayout.addWidget(stampNameLabel)
        nameLayout.addWidget(self.stampNameEdit)

        self.stampChooser = StampChooserWidget()
        self.stampChooser.selectionChangedSignal.connect(self.handleStampSelectionChanged)

        stampL = QtWidgets.QGridLayout()
        stampL.addWidget(stampLabel, 0, 0, 1, 3)
        stampL.addWidget(stampAddBtn, 1, 0)
        stampL.addWidget(stampRemoveBtn, 1, 1)
        stampL.addWidget(stampToolsBtn, 1, 2)
        stampL.addLayout(nameLayout, 2, 0, 1, 3)
        stampL.addWidget(self.stampChooser, 3, 0, 1, 3)
        self.stampTab.setLayout(stampL)

        # comments tab
        self.commentsTab = QtWidgets.QWidget()
        tabs.addTab(self.commentsTab, GetIcon('comments'), '')
        tabs.setTabToolTip(8, globals.trans.string('Palette', 33))

        cel = QtWidgets.QVBoxLayout()
        self.commentsTab.setLayout(cel)
        self.entEditorLayout = cel

        clabel = QtWidgets.QLabel(globals.trans.string('Palette', 34))
        clabel.setWordWrap(True)

        self.commentList = ListWidgetWithToolTipSignal()
        self.commentList.itemActivated.connect(self.HandleCommentSelectByList)
        self.commentList.toolTipAboutToShow.connect(self.HandleCommentToolTipAboutToShow)
        self.commentList.setSortingEnabled(True)

        cel.addWidget(clabel)
        cel.addWidget(self.commentList)

        # Set the current tab to the Object tab
        self.CreationTabChanged(0)

    def DeselectPathSelection(self, checked):
        """
        Deselects selected path nodes in the list
        """
        for selecteditem in self.pathList.selectedItems():
            selecteditem.setSelected(False)

    @QtCore.pyqtSlot()
    def Autosave(self):
        """
        Auto saves the level
        """
        return
        if not globals.AutoSaveDirty: return

        name = self.getInnerSarcName()
        if "-" not in name:
            print('HEY THERE IS NO -, THIS WILL NOT WORK!')
        if name == '':
            return

        data = globals.Level.save(name)
        globals.levelNameCache = name
        setSetting('AutoSaveFilePath', self.fileSavePath)
        setSetting('AutoSaveFileData', QtCore.QByteArray(data))
        globals.AutoSaveDirty = False

    @QtCore.pyqtSlot()
    def TrackClipboardUpdates(self):
        """
        Catches systemwide clipboard updates
        """
        if globals.Initializing: return
        clip = self.systemClipboard.text()
        if clip is not None and clip != '':
            clip = str(clip).strip()

            if clip.startswith('MiyamotoClip|') and clip.endswith('|%'):
                self.clipboard = clip.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '')

                self.actions['paste'].setEnabled(True)
            else:
                self.clipboard = None
                self.actions['paste'].setEnabled(False)

    @QtCore.pyqtSlot(int)
    def XScrollChange(self, pos):
        """
        Moves the Overview current position box based on X scroll bar value
        """
        self.levelOverview.Xposlocator = pos
        self.levelOverview.update()

    @QtCore.pyqtSlot(int)
    def YScrollChange(self, pos):
        """
        Moves the Overview current position box based on Y scroll bar value
        """
        self.levelOverview.Yposlocator = pos
        self.levelOverview.update()

    @QtCore.pyqtSlot(int, int)
    def HandleWindowSizeChange(self, w, h):
        self.levelOverview.Hlocator = h
        self.levelOverview.Wlocator = w
        self.levelOverview.update()

    def UpdateTitle(self):
        """
        Sets the window title accordingly
        """
        self.setWindowTitle('You Make Good Level Now! - %s%s' % (
        self.fileTitle, (' ' + globals.trans.string('MainWindow', 0)) if globals.Dirty else ''))

    def CheckDirty(self):
        """
        Checks if the level is unsaved and asks for a confirmation if so - if it returns True, Cancel was picked
        """
        if not globals.Dirty: return False

        msg = QtWidgets.QMessageBox()
        msg.setText(globals.trans.string('AutoSaveDlg', 2))
        msg.setInformativeText(globals.trans.string('AutoSaveDlg', 3))
        msg.setStandardButtons(
            QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
        msg.setDefaultButton(QtWidgets.QMessageBox.Save)
        ret = msg.exec_()

        if ret == QtWidgets.QMessageBox.Save:
            if not self.HandleSave():
                # save failed
                return True
            return False
        elif ret == QtWidgets.QMessageBox.Discard:
            return False
        elif ret == QtWidgets.QMessageBox.Cancel:
            return True

    def LoadEventTabFromLevel(self):
        """
        Configures the Events tab from the data in Area.defEvents
        """
        defEvents = globals.Area.defEvents
        checked = Qt.Checked
        unchecked = Qt.Unchecked

        data = globals.Area.Metadata.binData('EventNotes_A%d' % globals.Area.areanum)
        eventTexts = {}
        if data is not None:
            # Iterate through the data
            idx = 0
            while idx < len(data):
                eventId = data[idx]
                idx += 1
                rawStrLen = data[idx:idx + 4]
                idx += 4
                strLen = (rawStrLen[0] << 24) | (rawStrLen[1] << 16) | (rawStrLen[2] << 8) | rawStrLen[3]
                rawStr = data[idx:idx + strLen]
                idx += strLen
                newStr = ''
                for char in rawStr: newStr += chr(char)
                eventTexts[eventId] = newStr

        for id in range(32):
            item = self.eventChooserItems[id]
            value = 1 << id
            item.setCheckState(0, checked if (defEvents & value) != 0 else unchecked)
            if id in eventTexts:
                item.setText(1, eventTexts[id])
            else:
                item.setText(1, '')
            item.setSelected(False)

        self.eventChooserItems[0].setSelected(True)
        txt0 = ''
        if 0 in eventTexts: txt0 = eventTexts[0]
        self.eventNotesEditor.setText(txt0)

    def handleEventTabItemClick(self, item):
        """
        Handles an item being clicked in the Events tab
        """
        noteText = item.text(1)
        self.eventNotesEditor.setText(noteText)
        selIdx = self.eventChooserItems.index(item)
        if item.checkState(0):
            # Turn a bit on
            globals.Area.defEvents |= 1 << selIdx
        else:
            # Turn a bit off (invert, turn on, invert)
            globals.Area.defEvents = ~globals.Area.defEvents
            globals.Area.defEvents |= 1 << selIdx
            globals.Area.defEvents = ~globals.Area.defEvents

    def handleEventNotesEdit(self):
        """
        Handles the text within self.eventNotesEditor changing
        """
        newText = self.eventNotesEditor.text()

        # Set the text to the event chooser
        currentItem = self.eventChooser.selectedItems()[0]
        currentItem.setText(1, newText)
        selIdx = self.eventChooserItems.index(currentItem)

        # Save all the events to the metadata
        data = []
        for id in range(32):
            idtext = str(self.eventChooserItems[id].text(1))
            if idtext == '': continue

            # Add the ID
            data.append(id)

            # Add the string length
            strlen = len(idtext)
            data.append(strlen >> 24)
            data.append((strlen >> 16) & 0xFF)
            data.append((strlen >> 8) & 0xFF)
            data.append(strlen & 0xFF)

            # Add the string
            for char in idtext: data.append(ord(char))

        globals.Area.Metadata.setBinData('EventNotes_A%d' % globals.Area.areanum, data)
        SetDirty()

    def handleStampsAdd(self):
        """
        Handles the "Add Stamp" btn being clicked
        """
        # Create a MiyamotoClip
        selitems = self.scene.selectedItems()
        if len(selitems) == 0: return
        clipboard_o = []
        clipboard_s = []
        ii = isinstance
        type_obj = ObjectItem
        type_spr = SpriteItem
        for obj in selitems:
            if ii(obj, type_obj):
                clipboard_o.append(obj)
            elif ii(obj, type_spr):
                clipboard_s.append(obj)
        MiyClp = self.encodeObjects(clipboard_o, clipboard_s)

        # Create a Stamp
        self.stampChooser.addStamp(Stamp(MiyClp, 'New Stamp'))

    def handleStampsRemove(self):
        """
        Handles the "Remove Stamp" btn being clicked
        """
        self.stampChooser.removeStamp(self.stampChooser.currentlySelectedStamp())

    def handleStampsOpen(self):
        """
        Handles the "Open Set..." btn being clicked
        """
        filetypes = ''
        filetypes += globals.trans.string('FileDlgs', 7) + ' (*.stamps);;'  # *.stamps
        filetypes += globals.trans.string('FileDlgs', 2) + ' (*)'  # *
        fn = QtWidgets.QFileDialog.getOpenFileName(self, globals.trans.string('FileDlgs', 6), '', filetypes)[0]
        if fn == '': return

        stamps = []

        with open(fn, 'r', encoding='utf-8') as file:
            filedata = file.read()

            if not filedata.startswith('stamps\n------\n'): return

            filesplit = filedata.split('\n')[3:]
            i = 0
            while i < len(filesplit):
                try:
                    # Get data
                    name = filesplit[i]
                    rc = filesplit[i + 1]

                    # Increment the line counter by 3, tp
                    # account for the blank line
                    i += 3

                except IndexError:
                    # Meh. Malformed stamps file.
                    i += 9999  # avoid infinite loops
                    continue

                stamps.append(Stamp(rc, name))

        for stamp in stamps: self.stampChooser.addStamp(stamp)

    def handleStampsSave(self):
        """
        Handles the "Save Set As..." btn being clicked
        """
        filetypes = ''
        filetypes += globals.trans.string('FileDlgs', 7) + ' (*.stamps);;'  # *.stamps
        filetypes += globals.trans.string('FileDlgs', 2) + ' (*)'  # *
        fn = QtWidgets.QFileDialog.getSaveFileName(self, globals.trans.string('FileDlgs', 3), '', filetypes)[0]
        if fn == '': return

        newdata = ''
        newdata += 'stamps\n'
        newdata += '------\n'

        for stampobj in self.stampChooser.model.items:
            name = stampobj.Name
            rc = stampobj.MiyamotoClip
            newdata += '\n'
            newdata += stampobj.Name + '\n'
            newdata += stampobj.MiyamotoClip + '\n'

        with open(fn, 'w', encoding='utf-8') as f:
            f.write(newdata)

    def handleStampSelectionChanged(self):
        """
        Called when the stamp selection is changed
        """
        newStamp = self.stampChooser.currentlySelectedStamp()
        stampSelected = newStamp is not None
        self.stampRemoveBtn.setEnabled(stampSelected)
        self.stampNameEdit.setEnabled(stampSelected)

        newName = '' if not stampSelected else newStamp.Name
        self.stampNameEdit.setText(newName)

    def handleStampNameEdited(self):
        """
        Called when the user edits the name of the current stamp
        """
        stamp = self.stampChooser.currentlySelectedStamp()
        text = self.stampNameEdit.text()
        stamp.Name = text
        stamp.update()

        # Try to get it to update!!! But fail. D:
        for i in range(3):
            self.stampChooser.updateGeometries()
            self.stampChooser.update(self.stampChooser.currentIndex())
            self.stampChooser.update()
            self.stampChooser.repaint()

    @QtCore.pyqtSlot()
    def AboutBox(self):
        """
        Shows the about box
        """
        AboutDialog().exec_()

    @QtCore.pyqtSlot()
    def HandleInfo(self):
        """
        Records the Level Meta Information
        """
        if globals.Area.areanum == 1:
            dlg = MetaInfoDialog()
            if dlg.exec_() == QtWidgets.QDialog.Accepted:
                globals.Area.Metadata.setStrData('Title', dlg.levelName.text())
                globals.Area.Metadata.setStrData('Author', dlg.Author.text())
                globals.Area.Metadata.setStrData('Group', dlg.Group.text())
                globals.Area.Metadata.setStrData('Website', dlg.Website.text())

                SetDirty()
                return
        else:
            dlg = QtWidgets.QMessageBox()
            dlg.setText(globals.trans.string('InfoDlg', 14))
            dlg.exec_()

    @QtCore.pyqtSlot()
    def HelpBox(self):
        """
        Shows the help box
        """
        QtGui.QDesktopServices.openUrl(
            QtCore.QUrl.fromLocalFile(os.path.join(globals.miyamoto_path, 'miyamotodata', 'help', 'index.html')))

    @QtCore.pyqtSlot()
    def TipBox(self):
        """
        Miyamoto! Tips and Commands
        """
        QtGui.QDesktopServices.openUrl(
            QtCore.QUrl.fromLocalFile(os.path.join(globals.miyamoto_path, 'miyamotodata', 'help', 'tips.html')))

    @QtCore.pyqtSlot()
    def SelectAll(self):
        """
        Select all objects in the current area
        """
        paintRect = QtGui.QPainterPath()
        paintRect.addRect(float(0), float(0), float(1024 * globals.TileWidth), float(512 * globals.TileWidth))
        self.scene.setSelectionArea(paintRect)

    @QtCore.pyqtSlot()
    def Deselect(self):
        """
        Deselect all currently selected items
        """
        items = self.scene.selectedItems()
        for obj in items:
            obj.setSelected(False)

    @QtCore.pyqtSlot()
    def Cut(self):
        """
        Cuts the selected items
        """
        self.SelectionUpdateFlag = True
        selitems = self.scene.selectedItems()
        self.scene.clearSelection()

        if len(selitems) > 0:
            clipboard_o = []
            clipboard_s = []
            ii = isinstance
            type_obj = ObjectItem
            type_spr = SpriteItem

            for obj in selitems:
                if ii(obj, type_obj):
                    obj.delete()
                    obj.setSelected(False)
                    self.scene.removeItem(obj)
                    clipboard_o.append(obj)
                elif ii(obj, type_spr):
                    obj.delete()
                    obj.setSelected(False)
                    self.scene.removeItem(obj)
                    clipboard_s.append(obj)

            if len(clipboard_o) > 0 or len(clipboard_s) > 0:
                SetDirty()
                self.actions['cut'].setEnabled(False)
                self.actions['paste'].setEnabled(True)
                self.clipboard = self.encodeObjects(clipboard_o, clipboard_s)
                self.systemClipboard.setText(self.clipboard)

        self.levelOverview.update()
        self.SelectionUpdateFlag = False
        self.ChangeSelectionHandler()

    @QtCore.pyqtSlot()
    def Copy(self):
        """
        Copies the selected items
        """
        selitems = self.scene.selectedItems()
        if len(selitems) > 0:
            clipboard_o = []
            clipboard_s = []
            ii = isinstance
            type_obj = ObjectItem
            type_spr = SpriteItem

            for obj in selitems:
                if ii(obj, type_obj):
                    clipboard_o.append(obj)
                elif ii(obj, type_spr):
                    clipboard_s.append(obj)

            if len(clipboard_o) > 0 or len(clipboard_s) > 0:
                self.actions['paste'].setEnabled(True)
                self.clipboard = self.encodeObjects(clipboard_o, clipboard_s)
                self.systemClipboard.setText(self.clipboard)

    @QtCore.pyqtSlot()
    def Paste(self):
        """
        Paste the selected items
        """
        if self.clipboard is not None:
            self.placeEncodedObjects(self.clipboard)

    def encodeObjects(self, clipboard_o, clipboard_s):
        """
        Encode a set of objects and sprites into a string
        """
        convclip = ['MiyamotoClip']

        # get objects
        clipboard_o.sort(key=lambda x: x.zValue())

        for item in clipboard_o:
            convclip.append('0:%d:%d:%d:%d:%d:%d:%d' % (
            item.tileset, item.type, item.layer, item.objx, item.objy, item.width, item.height))

        # get sprites
        for item in clipboard_s:
            data = item.spritedata
            convclip.append('1:%d:%d:%d:%d:%d:%d:%d:%d:%d:%d:%d:%d:%d:%d:%d' % (
            item.type, item.objx, item.objy, data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7],
            data[8], data[9], data[10], data[11]))

        convclip.append('%')
        return '|'.join(convclip)

    def placeEncodedObjects(self, encoded, select=True, xOverride=None, yOverride=None):
        """
        Decode and place a set of objects
        """
        self.SelectionUpdateFlag = True
        self.scene.clearSelection()
        added = []

        x1 = 1024
        x2 = 0
        y1 = 512
        y2 = 0

        globals.OverrideSnapping = True

        if not (encoded.startswith('MiyamotoClip|') and encoded.endswith('|%')): return

        clip = encoded.split('|')[1:-1]

        if len(clip) > 300:
            result = QtWidgets.QMessageBox.warning(self, 'Miyamoto!', globals.trans.string('MainWindow', 1),
                                                   QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
            if result == QtWidgets.QMessageBox.No: return

        layers, sprites = self.getEncodedObjects(encoded)

        # Go through the sprites
        for spr in sprites:
            x = spr.objx / 16
            y = spr.objy / 16
            if x < x1: x1 = x
            if x > x2: x2 = x
            if y < y1: y1 = y
            if y > y2: y2 = y

            globals.Area.sprites.append(spr)
            added.append(spr)
            self.scene.addItem(spr)

        # Go through the objects
        for layer in layers:
            for obj in layer:
                xs = obj.objx
                xe = obj.objx + obj.width - 1
                ys = obj.objy
                ye = obj.objy + obj.height - 1
                if xs < x1: x1 = xs
                if xe > x2: x2 = xe
                if ys < y1: y1 = ys
                if ye > y2: y2 = ye

                added.append(obj)
                self.scene.addItem(obj)

        layer0, layer1, layer2 = layers

        if len(layer0) > 0:
            AreaLayer = globals.Area.layers[0]
            if len(AreaLayer) > 0:
                z = AreaLayer[-1].zValue() + 1
            else:
                z = 16384
            for obj in layer0:
                AreaLayer.append(obj)
                obj.setZValue(z)
                z += 1

        if len(layer1) > 0:
            AreaLayer = globals.Area.layers[1]
            if len(AreaLayer) > 0:
                z = AreaLayer[-1].zValue() + 1
            else:
                z = 8192
            for obj in layer1:
                AreaLayer.append(obj)
                obj.setZValue(z)
                z += 1

        if len(layer2) > 0:
            AreaLayer = globals.Area.layers[2]
            if len(AreaLayer) > 0:
                z = AreaLayer[-1].zValue() + 1
            else:
                z = 0
            for obj in layer2:
                AreaLayer.append(obj)
                obj.setZValue(z)
                z += 1

        # now center everything
        zoomscaler = (self.ZoomLevel / 100.0)
        width = x2 - x1 + 1
        height = y2 - y1 + 1
        viewportx = (self.view.XScrollBar.value() / zoomscaler) / globals.TileWidth
        viewporty = (self.view.YScrollBar.value() / zoomscaler) / globals.TileWidth
        viewportwidth = (self.view.width() / zoomscaler) / globals.TileWidth
        viewportheight = (self.view.height() / zoomscaler) / globals.TileWidth

        # tiles
        if xOverride is None:
            xoffset = int(0 - x1 + viewportx + ((viewportwidth / 2) - (width / 2)))
            xpixeloffset = xoffset * 16
        else:
            xoffset = int(0 - x1 + (xOverride / 16) - (width / 2))
            xpixeloffset = xoffset * 16
        if yOverride is None:
            yoffset = int(0 - y1 + viewporty + ((viewportheight / 2) - (height / 2)))
            ypixeloffset = yoffset * 16
        else:
            yoffset = int(0 - y1 + (yOverride / 16) - (height / 2))
            ypixeloffset = yoffset * 16

        for item in added:
            if isinstance(item, SpriteItem):
                item.setPos(
                    (item.objx + xpixeloffset + item.ImageObj.xOffset) * globals.TileWidth / 16,
                    (item.objy + ypixeloffset + item.ImageObj.yOffset) * globals.TileWidth / 16,
                )
            elif isinstance(item, ObjectItem):
                item.setPos((item.objx + xoffset) * globals.TileWidth, (item.objy + yoffset) * globals.TileWidth)
            if select: item.setSelected(True)

        globals.OverrideSnapping = False

        self.levelOverview.update()
        SetDirty()
        self.SelectionUpdateFlag = False
        self.ChangeSelectionHandler()

        return added

    def getEncodedObjects(self, encoded):
        """
        Create the objects from a MiyamotoClip
        """

        layers = ([], [], [])
        sprites = []

        try:
            if not (encoded.startswith('MiyamotoClip|') and encoded.endswith('|%')): return

            clip = encoded[11:-2].split('|')

            if len(clip) > 300:
                result = QtWidgets.QMessageBox.warning(self, 'Miyamoto!', globals.trans.string('MainWindow', 1),
                                                       QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                if result == QtWidgets.QMessageBox.No:
                    return

            for item in clip:
                # Check to see whether it's an object or sprite
                # and add it to the correct stack
                split = item.split(':')
                if split[0] == '0':
                    # object
                    if len(split) != 8: continue

                    tileset = int(split[1])
                    type = int(split[2])
                    layer = int(split[3])
                    objx = int(split[4])
                    objy = int(split[5])
                    width = int(split[6])
                    height = int(split[7])

                    # basic sanity checks
                    if tileset < 0 or tileset > 3: continue
                    if type < 0 or type > 255: continue
                    if layer < 0 or layer > 2: continue
                    if objx < 0 or objx > 1023: continue
                    if objy < 0 or objy > 511: continue
                    if width < 1 or width > 1023: continue
                    if height < 1 or height > 511: continue

                    newitem = ObjectItem(tileset, type, layer, objx, objy, width, height, 1)

                    layers[layer].append(newitem)

                elif split[0] == '1':
                    # sprite
                    if len(split) != 16: continue

                    objx = int(split[2])
                    objy = int(split[3])
                    data = bytes(map(int,
                                     [split[4], split[5], split[6], split[7], split[8], split[9],
                                      split[10], split[11], split[12], split[13], split[14], split[15]]))

                    x = objx / 16
                    y = objy / 16

                    newitem = SpriteItem(int(split[1]), objx, objy, data)
                    sprites.append(newitem)

        except ValueError:
            # an int() probably failed somewhere
            pass

        return layers, sprites

    @QtCore.pyqtSlot()
    def ShiftItems(self):
        """
        Shifts the selected object(s)
        """
        items = self.scene.selectedItems()
        if len(items) == 0: return

        dlg = ObjectShiftDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            xoffset = dlg.XOffset.value()
            yoffset = dlg.YOffset.value()
            if xoffset == 0 and yoffset == 0: return

            type_obj = ObjectItem
            type_spr = SpriteItem
            type_ent = EntranceItem
            type_loc = LocationItem

            if ((xoffset % 16) != 0) or ((yoffset % 16) != 0):
                # warn if any objects exist
                objectsExist = False
                spritesExist = False
                for obj in items:
                    if isinstance(obj, type_obj):
                        objectsExist = True
                    elif isinstance(obj, type_spr) or isinstance(obj, type_ent):
                        spritesExist = True

                if objectsExist and spritesExist:
                    # no point in warning them if there are only objects
                    # since then, it will just silently reduce the offset and it won't be noticed
                    result = QtWidgets.QMessageBox.information(None, globals.trans.string('ShftItmDlg', 5),
                                                               globals.trans.string('ShftItmDlg', 6), QtWidgets.QMessageBox.Yes,
                                                               QtWidgets.QMessageBox.No)
                    if result == QtWidgets.QMessageBox.No:
                        return

            xpoffset = xoffset * globals.TileWidth / 16
            ypoffset = yoffset * globals.TileWidth / 16

            globals.OverrideSnapping = True

            for obj in items:
                obj.setPos(obj.x() + xpoffset, obj.y() + ypoffset)

            globals.OverrideSnapping = False

            SetDirty()

    @QtCore.pyqtSlot()
    def SwapObjectsTilesets(self):
        """
        Swaps objects' tilesets
        """
        dlg = ObjectTilesetSwapDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            for layer in globals.Area.layers:
                for nsmbobj in layer:
                    if nsmbobj.tileset == (dlg.FromTS.value() - 1):
                        nsmbobj.SetType(dlg.ToTS.value() - 1, nsmbobj.type)
                    elif nsmbobj.tileset == (dlg.ToTS.value() - 1) and dlg.DoExchange.checkState() == Qt.Checked:
                        nsmbobj.SetType(dlg.FromTS.value() - 1, nsmbobj.type)

            SetDirty()

    @QtCore.pyqtSlot()
    def SwapObjectsTypes(self):
        """
        Swaps objects' types
        """
        dlg = ObjectTypeSwapDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            for layer in globals.Area.layers:
                for nsmbobj in layer:
                    if nsmbobj.type == (dlg.FromType.value()) and nsmbobj.tileset == (dlg.FromTileset.value() - 1):
                        nsmbobj.SetType(dlg.ToTileset.value() - 1, dlg.ToType.value())
                    elif nsmbobj.type == (dlg.ToType.value()) and nsmbobj.tileset == (
                        dlg.ToTileset.value() - 1) and dlg.DoExchange.checkState() == Qt.Checked:
                        nsmbobj.SetType(dlg.FromTileset.value() - 1, dlg.FromType.value())

            SetDirty()

    @QtCore.pyqtSlot()
    def MergeLocations(self):
        """
        Merges selected sprite locations
        """
        items = self.scene.selectedItems()
        if len(items) == 0: return

        newx = 999999
        newy = 999999
        neww = 0
        newh = 0

        type_loc = LocationItem
        for obj in items:
            if isinstance(obj, type_loc):
                if obj.objx < newx:
                    newx = obj.objx
                if obj.objy < newy:
                    newy = obj.objy
                if obj.width + obj.objx > neww:
                    neww = obj.width + obj.objx
                if obj.height + obj.objy > newh:
                    newh = obj.height + obj.objy
                obj.delete()
                obj.setSelected(False)
                self.scene.removeItem(obj)
                self.levelOverview.update()
                SetDirty()

        if newx != 999999 and newy != 999999:
            allID = set()  # faster 'x in y' lookups for sets
            newID = 1
            for i in globals.Area.locations:
                allID.add(i.id)

            while newID <= 255:
                if newID not in allID:
                    break
                newID += 1

            loc = LocationItem(newx, newy, neww - newx, newh - newy, newID)

            mw = globals.mainWindow
            loc.positionChanged = mw.HandleObjPosChange
            mw.scene.addItem(loc)

            globals.Area.locations.append(loc)
            loc.setSelected(True)

    @QtCore.pyqtSlot()
    def HandleAddNewArea(self):
        """
        Adds a new area to the level
        """
        if len(globals.Level.areas) >= 4:
            QtWidgets.QMessageBox.warning(self, 'Miyamoto!', globals.trans.string('AreaChoiceDlg', 2))
            return

        if self.CheckDirty():
            return

        newID = len(globals.Level.areas) + 1

        with open('miyamotodata/blankcourse.bin', 'rb') as blank:
            course = blank.read()
        L0 = None
        L1 = None
        L2 = None

        if not self.HandleSaveNewArea(course, L0, L1, L2): return
        self.LoadLevel(None, self.fileSavePath, True, newID)

    @QtCore.pyqtSlot()
    def HandleImportArea(self):
        """
        Imports an area from another level
        """
        if len(globals.Level.areas) >= 4:
            QtWidgets.QMessageBox.warning(self, 'Miyamoto!', globals.trans.string('AreaChoiceDlg', 2))
            return

        if globals.Dirty:
            con_msg = "You need to save this level before importing/deleting Areas.\nDo you want to save now?"
            reply = QtWidgets.QMessageBox.question(self, 'Message',
                                                   con_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

            if reply == QtWidgets.QMessageBox.Yes:
                if not self.HandleSave(): return
            else:
                return

        filetypes = ''
        filetypes += globals.trans.string('FileDlgs', 1) + ' (*.szs);;'
        filetypes += 'Uncompressed Level Archives (*.sarc);;'
        filetypes += globals.trans.string('FileDlgs', 2) + ' (*)'
        fn = QtWidgets.QFileDialog.getOpenFileName(self, globals.trans.string('FileDlgs', 0), '', filetypes)[0]
        if fn == '': return
        fn = str(fn)

        with open(fn, 'rb') as fileobj:
            data = fileobj.read()

        # Decompress, if needed (Yaz0)
        if data.startswith(b'Yaz0'):
            print('Beginning Yaz0 decompression...')
            data = Yaz0Dec(data)
            print('Decompression finished.')
        elif data.startswith(b'SARC'):
            print('Yaz0 decompression skipped.')
        else:
            return False  # keep it from crashing by loading things it shouldn't

        arc = SarcLib.SARC_Archive()
        arc.load(data)

        def exists(fn):
            nonlocal arc
            try:
                arc[fn]
            except:
                return False
            return True

        if exists('levelname'):
            fn1 = bytes_to_string(arc['levelname'].data)
            if exists(fn1):
                arcdata = arc[fn1].data
            else:
                possibilities = []
                possibilities.append(os.path.basename(fn))
                possibilities.append(os.path.basename(fn).split(' ')[-1])  # for names like "NSMBU 1-1.szs"
                possibilities.append(os.path.basename(fn).split(' ')[0])  # for names like "1-1 test.szs"
                possibilities.append(os.path.basename(fn).split('.')[0])
                possibilities.append(os.path.basename(fn).split('_')[0])
                for fn in possibilities:
                    if exists(fn):
                        arcdata = arc[fn].data
                        break
                else:
                    warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'OH NO',
                                                       'Couldn\'t find the inner level file. Aborting.')
                    warningBox.exec_()
                    return False

        else:
            possibilities = []
            possibilities.append(os.path.basename(fn))
            possibilities.append(os.path.basename(fn).split(' ')[-1])  # for names like "NSMBU 1-1.szs"
            possibilities.append(os.path.basename(fn).split(' ')[0])  # for names like "1-1 test.szs"
            possibilities.append(os.path.basename(fn).split('.')[0])
            possibilities.append(os.path.basename(fn).split('_')[0])
            for fn in possibilities:
                if exists(fn):
                    arcdata = arc[fn].data
                    break
            else:
                warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'OH NO',
                                                   'Couldn\'t find the inner level file. Aborting.')
                warningBox.exec_()
                return False

        arc = SarcLib.SARC_Archive()
        arc.load(arcdata)

        # get the area count
        areacount = 0

        try:
            courseFolder = arc['course']
        except:
            return False

        for file in courseFolder.contents:
            fname, val = file.name, file.data
            if val is not None:
                # it's a file
                if fname.startswith('course'):
                    maxarea = int(fname[6])
                    if maxarea > areacount: areacount = maxarea

        # choose one
        dlg = AreaChoiceDialog(areacount)
        if dlg.exec_() == QtWidgets.QDialog.Rejected:
            return

        area = dlg.areaCombo.currentIndex() + 1

        # get the required files
        reqcourse = 'course%d.bin' % area
        reqL0 = 'course%d_bgdatL0.bin' % area
        reqL1 = 'course%d_bgdatL1.bin' % area
        reqL2 = 'course%d_bgdatL2.bin' % area

        course = None
        L0 = None
        L1 = None
        L2 = None

        for file in courseFolder.contents:
            fname, val = file.name, file.data
            if val is not None:
                if fname == reqcourse:
                    course = val
                elif fname == reqL0:
                    L0 = val
                elif fname == reqL1:
                    L1 = val
                elif fname == reqL2:
                    L2 = val

        # add them to our level
        newID = len(globals.Level.areas) + 1

        if not self.HandleSaveNewArea(course, L0, L1, L2): return
        self.LoadLevel(None, self.fileSavePath, True, newID)

    @QtCore.pyqtSlot()
    def HandleDeleteArea(self):
        """
        Deletes the current area
        """
        result = QtWidgets.QMessageBox.warning(self, 'Miyamoto!', globals.trans.string('DeleteArea', 0),
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.No: return

        if globals.Dirty:
            con_msg = "You need to save this level before importing/deleting Areas.\nDo you want to save now?"
            reply = QtWidgets.QMessageBox.question(self, 'Message',
                                                   con_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

            if reply == QtWidgets.QMessageBox.Yes:
                if not self.HandleSave(): return
            else:
                return

        name = self.getInnerSarcName()
        if "-" not in name:
            print('HEY THERE IS NO -, THIS WILL NOT WORK!')
        if name == '':
            return

        globals.Level.deleteArea(globals.Area.areanum)

        # no error checking. if it saved last time, it will probably work now

        if self.fileSavePath.endswith('.szs'):
            course_name = os.path.splitext(self.fileSavePath)[0]
            with open(course_name + '.tmp', 'wb') as f:
                f.write(globals.Level.saveNewArea(name, None, None, None, None))

            if os.path.isfile(self.fileSavePath):
                os.remove(self.fileSavePath)
            if platform.system() == 'Windows':
                os.chdir(globals.miyamoto_path + '/Tools')
                os.system('wszst.exe COMPRESS "' + course_name + '.tmp" --dest "' + self.fileSavePath + '"')
                os.chdir(globals.miyamoto_path)
            elif platform.system() == 'Linux':
                os.chdir(globals.miyamoto_path + '/linuxTools')
                os.system('chmod +x ./wszst_linux.elf')
                os.system('./wszst_linux.elf COMPRESS "' + course_name + '.tmp" --dest "' + self.fileSavePath + '"')
                os.chdir(globals.miyamoto_path)
            elif platform.system() == 'Darwin':
                os.system(
                    'open -a "' + globals.miyamoto_path + '/macTools/wszst_mac" --args COMPRESS "' + course_name + '.tmp" --dest "' + self.fileSavePath + '"')
            else:
                warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'OH NO',
                                                   'Not a supported platform, sadly...')
                warningBox.exec_()
                return
            os.remove(course_name + '.tmp')
        else:
            with open(self.fileSavePath, 'wb') as f:
                f.write(globals.Level.saveNewArea(name, None, None, None, None))
        globals.levelNameCache = name

        if globals.CurrentArea in globals.ObjectAddedtoEmbedded:  # Should always be true
            del globals.ObjectAddedtoEmbedded[globals.CurrentArea]

        self.LoadLevel(None, self.fileSavePath, True, 1)

    @QtCore.pyqtSlot()
    def HandleChangeGamePath(self, auto=False):
        """
        Change the game path used by the current game definition
        """
        if self.CheckDirty(): return

        path = None
        # while not isValidGamePath(path):
        globals.CurrentGame = globals.NewSuperMarioBrosU
        path = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                          globals.trans.string('ChangeGamePath', 0, '[game]', globals.gamedef.name))
        if path == '':
            return False

        path = str(path)

        if (not isValidGamePath(path)) and (not globals.gamedef.custom):  # custom gamedefs can use incomplete folders
            QtWidgets.QMessageBox.information(None, globals.trans.string('ChangeGamePath', 1),
                                              globals.trans.string('ChangeGamePath', 2))
        else:
            SetGamePath(path)
            # break

        if not auto:
            globals.ObjectAddedtoEmbedded = {}

            self.LoadLevel(None, globals.FirstLevels[globals.CurrentGame], False, 1)

        return True

    @QtCore.pyqtSlot()
    def HandleChangeObjPath(self):
        """
        Change the Objects path used by "All" tab
        """
        path = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                          'Choose the folder containing Object folders')

        if not path: return

        setSetting('ObjPath', path)

        self.objAllTab.setTabEnabled(1, True)

        self.folderPicker.clear()

        i = 0
        for folder in os.listdir(path):
            if os.path.isdir(path + "/" + folder):
                globals.ObjectAddedtoEmbedded[globals.CurrentArea][i] = {}
                self.folderPicker.addItem(folder)
                i += 1

        def UpdateObjFolder():
            self.objPicker.mall.LoadFromFolder()

        UpdateObjFolder()

        self.folderPicker.currentIndexChanged.connect(UpdateObjFolder)

    @QtCore.pyqtSlot()
    def HandleChangeSavePath(self, auto=False):
        """
        Change the save path used by the current game definition
        """
        if self.CheckDirty(): return

        path = None
        # while not isValidGamePath(path):
        globals.CurrentGame = globals.NewSuperMarioBrosU
        path = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                          globals.trans.string('ChangeGamePath', 0, '[game]', globals.gamedef.name))
        if path == '':
            return False

        path = str(path)

        if (not isValidGamePath(path)) and (not globals.gamedef.custom):  # custom gamedefs can use incomplete folders
            QtWidgets.QMessageBox.information(None, globals.trans.string('ChangeGamePath', 1),
                                              globals.trans.string('ChangeGamePath', 2))
        else:
            SetSavePath(path)
            # break

        return True

    @QtCore.pyqtSlot()
    def HandlePreferences(self):
        """
        Edit Miyamoto preferences
        """

        # Show the dialog
        dlg = PreferencesDialog()
        if dlg.exec_() == QtWidgets.QDialog.Rejected:
            return

        # Get the Menubar setting
        setSetting('Menu', 'Menubar')

        # Get the translation
        name = str(dlg.generalTab.Trans.itemData(dlg.generalTab.Trans.currentIndex(), Qt.UserRole))
        setSetting('Translation', name)

        # Get the Toolbar tab settings
        boxes = (
        dlg.toolbarTab.FileBoxes, dlg.toolbarTab.EditBoxes, dlg.toolbarTab.ViewBoxes, dlg.toolbarTab.SettingsBoxes,
        dlg.toolbarTab.HelpBoxes)
        ToolbarSettings = {}
        for boxList in boxes:
            for box in boxList:
                ToolbarSettings[box.InternalName] = box.isChecked()
        setSetting('ToolbarActs', ToolbarSettings)

        # Get the theme settings
        setSetting('Theme', dlg.themesTab.themeBox.currentText())

        # Warn the user that they may need to restart
        QtWidgets.QMessageBox.warning(None, globals.trans.string('PrefsDlg', 0), globals.trans.string('PrefsDlg', 30))

    @QtCore.pyqtSlot()
    def HandleNewLevel(self):
        """
        Create a new level
        """
        if self.CheckDirty(): return

        globals.ObjectAddedtoEmbedded = {}

        self.LoadLevel(None, None, False, 1)

    @QtCore.pyqtSlot()
    def HandleOpenFromName(self):
        """
        Open a level using the level picker
        """
        if self.CheckDirty(): return

        LoadLevelNames()
        dlg = ChooseLevelNameDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            globals.ObjectAddedtoEmbedded = {}

            self.LoadLevel(None, dlg.currentlevel, False, 1)

    @QtCore.pyqtSlot()
    def HandleOpenFromFile(self):
        """
        Open a level using the filename
        """
        if self.CheckDirty(): return

        filetypes = ''
        filetypes += globals.trans.string('FileDlgs', 1) + ' (*.szs);;'
        filetypes += 'Uncompressed Level Archives (*.sarc);;'
        filetypes += globals.trans.string('FileDlgs', 2) + ' (*)'
        fn = QtWidgets.QFileDialog.getOpenFileName(self, globals.trans.string('FileDlgs', 0), '', filetypes)[0]
        if fn == '': return

        globals.ObjectAddedtoEmbedded = {}

        self.LoadLevel(None, str(fn), True, 1)

    @QtCore.pyqtSlot()
    def HandleSave(self):
        """
        Save a level back to the archive
        """
        if not globals.mainWindow.fileSavePath:
            if not self.HandleSaveAs():
                return False
            else:
                return True

        name = self.getInnerSarcName()
        if "-" not in name:
            print('HEY THERE IS NO -, THIS WILL NOT WORK!')
        if name == '':
            return False

        data = globals.Level.save(name)
        globals.levelNameCache = name
        try:
            if globals.mainWindow.fileSavePath.endswith('.szs'):
                course_name = os.path.splitext(globals.mainWindow.fileSavePath)[0]
                with open(course_name + '.tmp', 'wb') as f:
                    f.write(data)

                if os.path.isfile(globals.mainWindow.fileSavePath):
                    os.remove(globals.mainWindow.fileSavePath)
                if platform.system() == 'Windows':
                    os.chdir(globals.miyamoto_path + '/Tools')
                    os.system('wszst.exe COMPRESS "' + course_name + '.tmp" --dest "' + globals.mainWindow.fileSavePath + '"')
                    os.chdir(globals.miyamoto_path)
                elif platform.system() == 'Linux':
                    os.chdir(globals.miyamoto_path + '/linuxTools')
                    os.system('chmod +x ./wszst_linux.elf')
                    os.system(
                        './wszst_linux.elf COMPRESS "' + course_name + '.tmp" --dest "' + globals.mainWindow.fileSavePath + '"')
                    os.chdir(globals.miyamoto_path)
                elif platform.system() == 'Darwin':
                    os.system(
                        'open -a "' + globals.miyamoto_path + '/macTools/wszst_mac" --args COMPRESS "' + course_name + '.tmp" --dest "' + globals.mainWindow.fileSavePath + '"')
                else:
                    warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'OH NO',
                                                       'Not a supported platform, sadly...')
                    warningBox.exec_()
                    return
                os.remove(course_name + '.tmp')
            else:
                with open(globals.mainWindow.fileSavePath, 'wb') as f:
                    f.write(data)
        except IOError as e:
            QtWidgets.QMessageBox.warning(None, globals.trans.string('Err_Save', 0),
                                          globals.trans.string('Err_Save', 1, '[err1]', e.args[0], '[err2]', e.args[1]))
            return False

        globals.Dirty = False
        globals.AutoSaveDirty = False
        self.UpdateTitle()

        # setSetting('AutoSaveFilePath', self.fileSavePath)
        # setSetting('AutoSaveFileData', 'x')
        return True

    @QtCore.pyqtSlot()
    def HandleSaveNewArea(self, course, L0, L1, L2):
        """
        Save a level back to the archive
        """
        if not globals.mainWindow.fileSavePath:
            if not self.HandleSaveAs():
                return False
            else:
                return True

        name = self.getInnerSarcName()
        if "-" not in name:
            print('HEY THERE IS NO -, THIS WILL NOT WORK!')
        if name == '':
            return False

        data = globals.Level.saveNewArea(name, course, L0, L1, L2)
        globals.levelNameCache = name
        try:
            if globals.mainWindow.fileSavePath.endswith('.szs'):
                course_name = os.path.splitext(globals.mainWindow.fileSavePath)[0]
                with open(course_name + '.tmp', 'wb') as f:
                    f.write(data)

                if os.path.isfile(globals.mainWindow.fileSavePath):
                    os.remove(globals.mainWindow.fileSavePath)
                if platform.system() == 'Windows':
                    os.chdir(globals.miyamoto_path + '/Tools')
                    os.system('wszst.exe COMPRESS "' + course_name + '.tmp" --dest "' + globals.mainWindow.fileSavePath + '"')
                    os.chdir(globals.miyamoto_path)
                elif platform.system() == 'Linux':
                    os.chdir(globals.miyamoto_path + '/linuxTools')
                    os.system('chmod +x ./wszst_linux.elf')
                    os.system(
                        './wszst_linux.elf COMPRESS "' + course_name + '.tmp" --dest "' + globals.mainWindow.fileSavePath + '"')
                    os.chdir(globals.miyamoto_path)
                elif platform.system() == 'Darwin':
                    os.system(
                        'open -a "' + globals.miyamoto_path + '/macTools/wszst_mac" --args COMPRESS "' + course_name + '.tmp" --dest "' + globals.mainWindow.fileSavePath + '"')
                else:
                    warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'OH NO',
                                                       'Not a supported platform, sadly...')
                    warningBox.exec_()
                    return
                os.remove(course_name + '.tmp')
            else:
                with open(globals.mainWindow.fileSavePath, 'wb') as f:
                    f.write(data)
        except IOError as e:
            QtWidgets.QMessageBox.warning(None, globals.trans.string('Err_Save', 0),
                                          globals.trans.string('Err_Save', 1, '[err1]', e.args[0], '[err2]', e.args[1]))
            return False

        globals.Dirty = False
        globals.AutoSaveDirty = False
        self.UpdateTitle()

        # setSetting('AutoSaveFilePath', self.fileSavePath)
        # setSetting('AutoSaveFileData', 'x')
        return True

    @QtCore.pyqtSlot()
    def HandleSaveAs(self):
        """
        Save a level back to the archive, with a new filename
        """
        filetypes = ''
        filetypes += globals.trans.string('FileDlgs', 1) + ' (*.szs);;'
        filetypes += 'Uncompressed Level Archives (*.sarc);;'
        filetypes += globals.trans.string('FileDlgs', 2) + ' (*)'
        fn = QtWidgets.QFileDialog.getSaveFileName(self, globals.trans.string('FileDlgs', 0), '', filetypes)[0]
        if fn == '': return False
        fn = str(fn)

        globals.Dirty = False
        globals.AutoSaveDirty = False

        self.fileSavePath = fn
        self.fileTitle = os.path.basename(fn)

        # we take the name of the level and make sure it's formatted right. if not, crashy
        # this is one of the few ways, if there's no - it will certainly crash
        failure = False
        name = self.getInnerSarcName()
        # oh noes there's no - !!!
        if "-" not in name:
            warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'Name warning',
                                               'The input name does not include a -, which is what retail levels use. \nThis may crash, because it does not fit the proper format.')
            warningBox.exec_()
        elif name == "":
            return False

        data = globals.Level.save(name)
        globals.levelNameCache = name
        if self.fileSavePath.endswith('.szs'):
            course_name = os.path.splitext(self.fileSavePath)[0]
            with open(course_name + '.tmp', 'wb') as f:
                f.write(data)

            if os.path.isfile(self.fileSavePath):
                os.remove(self.fileSavePath)
            if platform.system() == 'Windows':
                os.chdir(globals.miyamoto_path + '/Tools')
                os.system('wszst.exe COMPRESS "' + course_name + '.tmp" --dest "' + self.fileSavePath + '"')
                os.chdir(globals.miyamoto_path)
            elif platform.system() == 'Linux':
                os.chdir(globals.miyamoto_path + '/linuxTools')
                os.system('chmod +x ./wszst_linux.elf')
                os.system('./wszst_linux.elf COMPRESS "' + course_name + '.tmp" --dest "' + self.fileSavePath + '"')
                os.chdir(globals.miyamoto_path)
            elif platform.system() == 'Darwin':
                os.system(
                    'open -a "' + globals.miyamoto_path + '/macTools/wszst_mac" --args COMPRESS "' + course_name + '.tmp" --dest "' + self.fileSavePath + '"')
            else:
                warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'OH NO',
                                                   'Not a supported platform, sadly...')
                warningBox.exec_()
                return
            os.remove(course_name + '.tmp')
        else:
            with open(self.fileSavePath, 'wb') as f:
                f.write(data)
        self.UpdateTitle()

        self.RecentMenu.AddToList(self.fileSavePath)

        return True

    def getInnerSarcName(self):
        name = QtWidgets.QInputDialog.getText(self, "Choose Internal Name",
                                              "Choose an internal filename for this level (do not add a .sarc/.szs extension) (example: 1-1):",
                                              QtWidgets.QLineEdit.Normal)[0]

        if "/" in name or "\\" in name:
            warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'Name warning', r'The input name included "/" or "\", aborting...')
            warningBox.exec_()
            return ''

        return name

    @QtCore.pyqtSlot()
    def HandleExit(self):
        """
        Exit the editor. Why would you want to do this anyway?
        """
        self.close()

    @QtCore.pyqtSlot(int)
    def HandleSwitchArea(self, idx):
        """
        Handle activated signals for areaComboBox
        """
        if self.CheckDirty():
            self.areaComboBox.setCurrentIndex(globals.Area.areanum)
            return

        if globals.Area.areanum != idx + 1:
            self.LoadLevel(None, self.fileSavePath, True, idx + 1)

    @QtCore.pyqtSlot(bool)
    def HandleUpdateLayer0(self, checked):
        """
        Handle toggling of layer 0 being shown
        """
        globals.Layer0Shown = checked

        if globals.Area is not None:
            for obj in globals.Area.layers[0]:
                obj.setVisible(globals.Layer0Shown)

        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleUpdateLayer1(self, checked):
        """
        Handle toggling of layer 1 being shown
        """
        globals.Layer1Shown = checked

        if globals.Area is not None:
            for obj in globals.Area.layers[1]:
                obj.setVisible(globals.Layer1Shown)

        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleUpdateLayer2(self, checked):
        """
        Handle toggling of layer 2 being shown
        """
        globals.Layer2Shown = checked

        if globals.Area is not None:
            for obj in globals.Area.layers[2]:
                obj.setVisible(globals.Layer2Shown)

        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleTilesetAnimToggle(self, checked):
        """
        Handle toggling of tileset animations
        """
        globals.TilesetsAnimating = checked
        for tile in globals.Tiles:
            if tile is not None: tile.resetAnimation()

        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleCollisionsToggle(self, checked):
        """
        Handle toggling of tileset collisions viewing
        """
        globals.CollisionsShown = checked

        setSetting('ShowCollisions', globals.CollisionsShown)
        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleRealViewToggle(self, checked):
        """
        Handle toggling of Real View
        """
        globals.RealViewEnabled = checked
        SLib.RealViewEnabled = globals.RealViewEnabled

        setSetting('RealViewEnabled', globals.RealViewEnabled)
        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleSpritesVisibility(self, checked):
        """
        Handle toggling of sprite visibility
        """
        globals.SpritesShown = checked

        if globals.Area is not None:
            for spr in globals.Area.sprites:
                spr.setVisible(globals.SpritesShown)

        setSetting('ShowSprites', globals.SpritesShown)
        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleSpriteImages(self, checked):
        """
        Handle toggling of sprite images
        """
        globals.SpriteImagesShown = checked

        setSetting('ShowSpriteImages', globals.SpriteImagesShown)

        if globals.Area is not None:
            for spr in globals.Area.sprites:
                spr.UpdateRects()
                if globals.SpriteImagesShown:
                    spr.setPos(
                        (spr.objx + spr.ImageObj.xOffset) * (globals.TileWidth / 16),
                        (spr.objy + spr.ImageObj.yOffset) * (globals.TileWidth / 16),
                    )
                else:
                    spr.setPos(
                        spr.objx * (globals.TileWidth / 16),
                        spr.objy * (globals.TileWidth / 16),
                    )

        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleLocationsVisibility(self, checked):
        """
        Handle toggling of location visibility
        """
        globals.LocationsShown = checked

        if globals.Area is not None:
            for loc in globals.Area.locations:
                loc.setVisible(globals.LocationsShown)

        setSetting('ShowLocations', globals.LocationsShown)
        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleCommentsVisibility(self, checked):
        """
        Handle toggling of comment visibility
        """
        globals.CommentsShown = checked

        if globals.Area is not None:
            for com in globals.Area.comments:
                com.setVisible(globals.CommentsShown)

        setSetting('ShowComments', globals.CommentsShown)
        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleObjectsFreeze(self, checked):
        """
        Handle toggling of objects being frozen
        """
        globals.ObjectsFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if globals.Area is not None:
            for layer in globals.Area.layers:
                for obj in layer:
                    obj.setFlag(flag1, not globals.ObjectsFrozen)
                    obj.setFlag(flag2, not globals.ObjectsFrozen)

        setSetting('FreezeObjects', globals.ObjectsFrozen)
        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleSpritesFreeze(self, checked):
        """
        Handle toggling of sprites being frozen
        """
        globals.SpritesFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if globals.Area is not None:
            for spr in globals.Area.sprites:
                spr.setFlag(flag1, not globals.SpritesFrozen)
                spr.setFlag(flag2, not globals.SpritesFrozen)

        setSetting('FreezeSprites', globals.SpritesFrozen)
        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleEntrancesFreeze(self, checked):
        """
        Handle toggling of entrances being frozen
        """
        globals.EntrancesFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if globals.Area is not None:
            for ent in globals.Area.entrances:
                ent.setFlag(flag1, not globals.EntrancesFrozen)
                ent.setFlag(flag2, not globals.EntrancesFrozen)

        setSetting('FreezeEntrances', globals.EntrancesFrozen)
        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleLocationsFreeze(self, checked):
        """
        Handle toggling of locations being frozen
        """
        globals.LocationsFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if globals.Area is not None:
            for loc in globals.Area.locations:
                loc.setFlag(flag1, not globals.LocationsFrozen)
                loc.setFlag(flag2, not globals.LocationsFrozen)

        setSetting('FreezeLocations', globals.LocationsFrozen)
        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandlePathsFreeze(self, checked):
        """
        Handle toggling of paths being frozen
        """
        globals.PathsFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if globals.Area is not None:
            for node in globals.Area.paths:
                node.setFlag(flag1, not globals.PathsFrozen)
                node.setFlag(flag2, not globals.PathsFrozen)

        setSetting('FreezePaths', globals.PathsFrozen)
        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleCommentsFreeze(self, checked):
        """
        Handle toggling of comments being frozen
        """
        globals.CommentsFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if globals.Area is not None:
            for com in globals.Area.comments:
                com.setFlag(flag1, not globals.CommentsFrozen)
                com.setFlag(flag2, not globals.CommentsFrozen)

        setSetting('FreezeComments', globals.CommentsFrozen)
        self.scene.update()

    @QtCore.pyqtSlot(bool)
    def HandleOverwriteSprite(self, checked):
        """
        Handle setting overwriting sprites
        """
        globals.OverwriteSprite = not checked

        setSetting('OverwriteSprite', globals.OverwriteSprite)

    @QtCore.pyqtSlot(bool)
    def HandleFullscreen(self, checked):
        """
        Handle fullscreen mode
        """
        if checked:
            self.showFullScreen()
        else:
            self.showMaximized()

    @QtCore.pyqtSlot()
    def HandleSwitchGrid(self):
        """
        Handle switching of the grid view
        """
        if globals.GridType is None:
            globals.GridType = 'grid'
        elif globals.GridType == 'grid':
            globals.GridType = 'checker'
        else:
            globals.GridType = None

        setSetting('GridType', globals.GridType)
        self.scene.update()

    @QtCore.pyqtSlot()
    def HandleZoomIn(self):
        """
        Handle zooming in
        """
        z = self.ZoomLevel
        zi = self.ZoomLevels.index(z)
        zi += 1
        if zi < len(self.ZoomLevels):
            self.ZoomTo(self.ZoomLevels[zi])

    @QtCore.pyqtSlot()
    def HandleZoomOut(self):
        """
        Handle zooming out
        """
        z = self.ZoomLevel
        zi = self.ZoomLevels.index(z)
        zi -= 1
        if zi >= 0:
            self.ZoomTo(self.ZoomLevels[zi])

    @QtCore.pyqtSlot()
    def HandleZoomActual(self):
        """
        Handle zooming to the actual size
        """
        self.ZoomTo(100.0)

    @QtCore.pyqtSlot()
    def HandleZoomMin(self):
        """
        Handle zooming to the minimum size
        """
        self.ZoomTo(self.ZoomLevels[0])

    @QtCore.pyqtSlot()
    def HandleZoomMax(self):
        """
        Handle zooming to the maximum size
        """
        self.ZoomTo(self.ZoomLevels[len(self.ZoomLevels) - 1])

    def ZoomTo(self, z):
        """
        Zoom to a specific level
        """
        zEffective = z / globals.TileWidth * 24  # "100%" zoom level produces 24x24 level view
        tr = QtGui.QTransform()
        tr.scale(zEffective / 100.0, zEffective / 100.0)
        self.ZoomLevel = z
        self.view.setTransform(tr)
        self.levelOverview.mainWindowScale = zEffective / 100.0

        zi = self.ZoomLevels.index(z)
        self.actions['zoommax'].setEnabled(zi < len(self.ZoomLevels) - 1)
        self.actions['zoomin'].setEnabled(zi < len(self.ZoomLevels) - 1)
        self.actions['zoomactual'].setEnabled(z != 100.0)
        self.actions['zoomout'].setEnabled(zi > 0)
        self.actions['zoommin'].setEnabled(zi > 0)

        self.ZoomWidget.setZoomLevel(z)
        self.ZoomStatusWidget.setZoomLevel(z)

        # Update the zone grabber rects, to resize for the new zoom level
        for z in globals.Area.zones:
            z.UpdateRects()

        self.scene.update()

    @QtCore.pyqtSlot(int, int)
    def HandleOverviewClick(self, x, y):
        """
        Handle position changes from the level overview
        """
        self.view.centerOn(x, y)
        self.levelOverview.update()

    def SaveComments(self):
        """
        Saves the comments data back to self.Metadata
        """
        b = []
        for com in globals.Area.comments:
            xpos, ypos, tlen = com.objx, com.objy, len(com.text)
            b.append(xpos >> 24)
            b.append((xpos >> 16) & 0xFF)
            b.append((xpos >> 8) & 0xFF)
            b.append(xpos & 0xFF)
            b.append(ypos >> 24)
            b.append((ypos >> 16) & 0xFF)
            b.append((ypos >> 8) & 0xFF)
            b.append(ypos & 0xFF)
            b.append(tlen >> 24)
            b.append((tlen >> 16) & 0xFF)
            b.append((tlen >> 8) & 0xFF)
            b.append(tlen & 0xFF)
            for char in com.text: b.append(ord(char))
        globals.Area.Metadata.setBinData('InLevelComments_A%d' % globals.Area.areanum, b)

    def closeEvent(self, event):
        """
        Handler for the main window close event
        """

        if self.CheckDirty():
            event.ignore()
        else:
            # save our state
            self.spriteEditorDock.setVisible(False)
            self.entranceEditorDock.setVisible(False)
            self.pathEditorDock.setVisible(False)
            self.locationEditorDock.setVisible(False)
            self.defaultPropDock.setVisible(False)

            # state: determines positions of docks
            # geometry: determines the main window position
            setSetting('MainWindowState', self.saveState(0))
            setSetting('MainWindowGeometry', self.saveGeometry())

            if hasattr(self, 'HelpBoxInstance'):
                self.HelpBoxInstance.close()

            if hasattr(self, 'TipsBoxInstance'):
                self.TipsBoxInstance.close()

            globals.gamedef.SetLastLevel(str(globals.mainWindow.fileSavePath))

            setSetting('AutoSaveFilePath', 'none')
            setSetting('AutoSaveFileData', 'x')

            event.accept()

    def LoadLevel(self, game, name, isFullPath, areaNum):
        """
        Load a level from any game into the editor
        """
        hmm = False
        if name != None:
            globals.levName = os.path.basename(name)

            game = globals.NewSuperMarioBrosU

            # Get the file path, if possible
            if name is not None:
                checknames = []
                if isFullPath:
                    checknames = [name, ]
                else:
                    for ext in globals.FileExtentions[game]:
                        checknames.append(os.path.join(globals.gamedef.GetGamePath(), name + ext))

                for checkname in checknames:
                    if os.path.isfile(checkname):
                        break
                else:
                    QtWidgets.QMessageBox.warning(self, 'Miyamoto!',
                                                  globals.trans.string('Err_CantFindLevel', 0, '[name]', checkname),
                                                  QtWidgets.QMessageBox.Ok)
                    return False
                if not IsNSMBLevel(checkname):
                    QtWidgets.QMessageBox.warning(self, 'Miyamoto!', globals.trans.string('Err_InvalidLevel', 0),
                                                  QtWidgets.QMessageBox.Ok)
                    return False

            name = checkname

            # Get the data
            if not globals.RestoredFromAutoSave:

                # Check if there is a file by this name
                if not os.path.isfile(name):
                    QtWidgets.QMessageBox.warning(None, globals.trans.string('Err_MissingLevel', 0),
                                                  globals.trans.string('Err_MissingLevel', 1, '[file]', name))
                    return False

                # Set the filepath variables
                self.fileSavePath = name
                self.fileTitle = os.path.basename(self.fileSavePath)

                # Open the file
                with open(self.fileSavePath, 'rb') as fileobj:
                    levelData = fileobj.read()

                # Decompress, if needed (Yaz0)
                if levelData.startswith(b'Yaz0'):
                    print('Beginning Yaz0 decompression...')
                    levelData = Yaz0Dec(levelData)
                    print('Decompression finished.')
                elif levelData.startswith(b'SARC'):
                    print('Yaz0 decompression skipped.')
                else:
                    return False  # keep it from crashing by loading things it shouldn't

                arc = SarcLib.SARC_Archive()
                arc.load(levelData)

                def exists(fn):
                    nonlocal arc
                    try:
                        arc[fn]
                    except:
                        return False
                    return True

                if exists('levelname'):
                    fn = bytes_to_string(arc['levelname'].data)
                    if exists(fn):
                        globals.levelNameCache = fn
                        levelFileData = arc[fn].data
                    else:
                        possibilities = []
                        possibilities.append(os.path.basename(self.fileSavePath))
                        possibilities.append(
                            os.path.basename(self.fileSavePath).split(' ')[-1])  # for names like "NSMBU 1-1.szs"
                        possibilities.append(
                            os.path.basename(self.fileSavePath).split(' ')[0])  # for names like "1-1 test.szs"
                        possibilities.append(os.path.basename(self.fileSavePath).split('.')[0])
                        possibilities.append(os.path.basename(self.fileSavePath).split('_')[0])
                        possibilities.append(globals.levelNameCache)
                        for fn in possibilities:
                            if exists(fn):
                                globals.levelNameCache = fn
                                levelFileData = arc[fn].data
                                hmm = True
                                break
                        else:
                            warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'OH NO',
                                                               'Couldn\'t find the inner level file. Aborting.')
                            warningBox.exec_()
                            return False

                else:
                    possibilities = []
                    possibilities.append(os.path.basename(self.fileSavePath))
                    possibilities.append(
                        os.path.basename(self.fileSavePath).split(' ')[-1])  # for names like "NSMBU 1-1.szs"
                    possibilities.append(
                        os.path.basename(self.fileSavePath).split(' ')[0])  # for names like "1-1 test.szs"
                    possibilities.append(os.path.basename(self.fileSavePath).split('.')[0])
                    possibilities.append(os.path.basename(self.fileSavePath).split('_')[0])
                    possibilities.append(globals.levelNameCache)
                    for fn in possibilities:
                        if exists(fn):
                            globals.levelNameCache = fn
                            levelFileData = arc[fn].data
                            break
                    else:
                        warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'OH NO',
                                                           'Couldn\'t find the inner level file. Aborting.')
                        warningBox.exec_()
                        return False

                # Sort the szs data
                globals.szsData = {}
                for file in arc.contents:
                    globals.szsData[file.name] = file.data

                levelData = levelFileData

            else:
                # Auto-saved level. Check if there's a path associated with it:

                if globals.AutoSavePath == 'None':
                    self.fileSavePath = None
                    self.fileTitle = globals.trans.string('WindowTitle', 0)
                else:
                    self.fileSavePath = globals.AutoSavePath
                    self.fileTitle = os.path.basename(name)

                # Get the level data
                levelData = globals.AutoSaveData
                SetDirty(noautosave=True)

                # Turn off the autosave flag
                globals.RestoredFromAutoSave = False
        else:
            hmm = True
            # Set the filepath variables
            self.fileSavePath = False
            self.fileTitle = 'untitled'

            with open(globals.miyamoto_path + "/miyamotoextras/Pa0_jyotyu.szs", "rb") as inf:
                inb = inf.read()

            data = Yaz0Dec(inb)
            globals.szsData = {'Pa0_jyotyu': data}

        # Turn the dirty flag off, and keep it that way
        globals.Dirty = False
        globals.DirtyOverride += 1

        # Here's how progress is tracked. (After the major refactor, it may be a bit messed up now.)
        # - 0: Loading level data
        # [Area.__init__ is entered here]
        # - 1: Loading tilesets [1/2/3/4 allocated for each tileset]
        # - 5: Loading layers
        # [Control is returned to LoadLevel_NSMBU]
        # - 6: Loading objects
        # - 7: Preparing editor

        # First, clear out the existing level.
        self.scene.clearSelection()
        self.CurrentSelection = []
        self.scene.clear()

        # Clear out all level-thing lists
        for thingList in (self.spriteList, self.entranceList, self.locationList, self.pathList, self.commentList):
            thingList.clear()
            thingList.selectionModel().setCurrentIndex(QtCore.QModelIndex(), QtCore.QItemSelectionModel.Clear)

        # Reset these here, because if they are set after
        # creating the objects, they use the old values.
        globals.CurrentLayer = 1
        globals.Layer0Shown = True
        globals.Layer1Shown = True
        globals.Layer2Shown = True
        globals.CurrentArea = areaNum

        if globals.CurrentArea not in globals.ObjectAddedtoEmbedded:
            globals.ObjectAddedtoEmbedded[globals.CurrentArea] = {}

            top_folder = setting('ObjPath')

            if not (top_folder and os.path.isdir(top_folder)):
                self.objAllTab.setTabEnabled(1, False)

            else:
                self.folderPicker.clear()

                i = 0
                for folder in os.listdir(top_folder):
                        if os.path.isdir(top_folder + "/" + folder):
                            globals.ObjectAddedtoEmbedded[globals.CurrentArea][i] = {}
                            self.folderPicker.addItem(folder)
                            i += 1 

        globals.OverrideSnapping = False

        # Load the actual level
        if name == None:
            self.newLevel()
        else:
            self.LoadLevel_NSMBU(levelData, areaNum)

        # Set the level overview settings
        globals.mainWindow.levelOverview.maxX = 100
        globals.mainWindow.levelOverview.maxY = 40

        # Fill up the area list
        self.areaComboBox.clear()
        for i in range(1, len(globals.Level.areas) + 1):
            self.areaComboBox.addItem(globals.trans.string('AreaCombobox', 0, '[num]', i))
        self.areaComboBox.setCurrentIndex(areaNum - 1)

        self.levelOverview.update()

        # Scroll to the initial entrance
        startEntID = globals.Area.startEntrance
        startEnt = None
        for ent in globals.Area.entrances:
            if ent.entid == startEntID: startEnt = ent

        self.view.centerOn(0, 0)
        if startEnt is not None: self.view.centerOn(startEnt.objx * (globals.TileWidth / 16), startEnt.objy * (globals.TileWidth / 16))
        self.ZoomTo(100.0)

        # Reset some editor things
        self.actions['showlay0'].setChecked(True)
        self.actions['showlay1'].setChecked(True)
        self.actions['showlay2'].setChecked(True)
        self.actions['addarea'].setEnabled(len(globals.Level.areas) < 4)
        self.actions['importarea'].setEnabled(len(globals.Level.areas) < 4)
        self.actions['deletearea'].setEnabled(len(globals.Level.areas) > 1)

        # Turn snapping back on
        globals.OverrideSnapping = False

        # Turn the dirty flag off
        globals.DirtyOverride -= 1
        self.UpdateTitle()

        # Update UI things
        self.scene.update()

        self.levelOverview.Reset()
        self.levelOverview.update()
        QtCore.QTimer.singleShot(20, self.levelOverview.update)
        self.updateNumUsedTilesLabel()

        # Set the Current Game setting
        self.CurrentGame = game
        setSetting('CurrentGame', self.CurrentGame)

        if hmm:
            SetDirty()

        else:
            # Add the path to Recent Files
            self.RecentMenu.AddToList(globals.mainWindow.fileSavePath)

        # If we got this far, everything worked! Return True.
        return True

    def newLevel(self):
        # Create the new level object
        globals.Level = Level_NSMBU()

        # Load it
        globals.Level.new()

        self.objUseLayer1.setChecked(True)

        CreateTilesets()

        self.ReloadTilesets()

        self.objPicker.LoadFromTilesets()

        self.objAllTab.setCurrentIndex(0)
        self.objAllTab.setTabEnabled(0, True)

    def LoadLevel_NSMBU(self, levelData, areaNum):
        """
        Performs all level-loading tasks specific to New Super Mario Bros. U levels.
        Do not call this directly - use LoadLevel(NewSuperMarioBrosU, ...) instead!
        """

        # Create the new level object
        globals.Level = Level_NSMBU()

        # Load it
        if not globals.Level.load(levelData, areaNum):
            raise Exception

        self.objUseLayer1.setChecked(True)

        self.objPicker.LoadFromTilesets()

        self.objAllTab.setCurrentIndex(0)
        self.objAllTab.setTabEnabled(0, (globals.Area.tileset0 != ''))

        # Load events
        self.LoadEventTabFromLevel()

        # Add all things to the scene
        pcEvent = self.HandleObjPosChange
        for layer in reversed(globals.Area.layers):
            for obj in layer:
                obj.positionChanged = pcEvent
                self.scene.addItem(obj)

        pcEvent = self.HandleSprPosChange
        for spr in globals.Area.sprites:
            spr.positionChanged = pcEvent
            spr.listitem = ListWidgetItem_SortsByOther(spr)
            self.spriteList.addItem(spr.listitem)
            self.scene.addItem(spr)
            spr.UpdateListItem()
            spr.UpdateRects()
            if globals.SpriteImagesShown:
                spr.setPos(
                    (spr.objx + spr.ImageObj.xOffset) * (globals.TileWidth / 16),
                    (spr.objy + spr.ImageObj.yOffset) * (globals.TileWidth / 16),
                )
            else:
                spr.setPos(
                    spr.objx * (globals.TileWidth / 16),
                    spr.objy * (globals.TileWidth / 16),
                )

        pcEvent = self.HandleEntPosChange
        for ent in globals.Area.entrances:
            ent.positionChanged = pcEvent
            ent.listitem = ListWidgetItem_SortsByOther(ent)
            ent.listitem.entid = ent.entid
            self.entranceList.addItem(ent.listitem)
            self.scene.addItem(ent)
            ent.UpdateListItem()

        for zone in globals.Area.zones:
            self.scene.addItem(zone)

        pcEvent = self.HandleLocPosChange
        scEvent = self.HandleLocSizeChange
        for location in globals.Area.locations:
            location.positionChanged = pcEvent
            location.sizeChanged = scEvent
            location.listitem = ListWidgetItem_SortsByOther(location)
            self.locationList.addItem(location.listitem)
            self.scene.addItem(location)
            location.UpdateListItem()

        for path in globals.Area.paths:
            path.positionChanged = self.HandlePathPosChange
            path.listitem = ListWidgetItem_SortsByOther(path)
            self.pathList.addItem(path.listitem)
            self.scene.addItem(path)
            path.UpdateListItem()

        for path in globals.Area.pathdata:
            peline = PathEditorLineItem(path['nodes'])
            path['peline'] = peline
            self.scene.addItem(peline)
            peline.loops = path['loops']

        for path in globals.Area.paths:
            path.UpdateListItem()

        for com in globals.Area.comments:
            com.positionChanged = self.HandleComPosChange
            com.textChanged = self.HandleComTxtChange
            com.listitem = QtWidgets.QListWidgetItem()
            self.commentList.addItem(com.listitem)
            self.scene.addItem(com)
            com.UpdateListItem()

    @QtCore.pyqtSlot()
    def ReloadTilesets(self, soft=False):
        """
        Reloads all the tilesets. If soft is True, they will not be reloaded if the filepaths have not changed.
        """
        tilesets = [globals.Area.tileset0, globals.Area.tileset1, globals.Area.tileset2, globals.Area.tileset3]
        for idx, name in enumerate(tilesets):
            if (name is not None) and (name != ''):
                LoadTileset(idx, name, not soft)

        self.objPicker.LoadFromTilesets()

        for layer in globals.Area.layers:
            for obj in layer:
                obj.updateObjCache()

        self.scene.update()

    @QtCore.pyqtSlot()
    def ReloadSpriteData(self):
        globals.Sprites = None
        LoadSpriteData()
        for sprite in globals.Area.sprites:
            sprite.InitializeSprite()
        self.scene.update()

    @QtCore.pyqtSlot()
    def ChangeSelectionHandler(self):
        """
        Update the visible panels whenever the selection changes
        """
        if self.SelectionUpdateFlag: return

        try:
            selitems = self.scene.selectedItems()
        except RuntimeError:
            # must catch this error: if you close the app while something is selected,
            # you get a RuntimeError about the 'underlying C++ object being deleted'
            return

        # do this to avoid flicker
        showSpritePanel = False
        showEntrancePanel = False
        showLocationPanel = False
        showPathPanel = False
        updateModeInfo = False

        # clear our variables
        self.selObj = None
        self.selObjs = None

        self.spriteList.setCurrentItem(None)
        self.entranceList.setCurrentItem(None)
        self.locationList.setCurrentItem(None)
        self.pathList.setCurrentItem(None)
        self.commentList.setCurrentItem(None)

        # possibly a small optimization
        func_ii = isinstance
        type_obj = ObjectItem
        type_spr = SpriteItem
        type_ent = EntranceItem
        type_loc = LocationItem
        type_path = PathItem
        type_com = CommentItem

        if len(selitems) == 0:
            # nothing is selected
            self.actions['cut'].setEnabled(False)
            self.actions['copy'].setEnabled(False)
            self.actions['shiftitems'].setEnabled(False)
            self.actions['mergelocations'].setEnabled(False)

        elif len(selitems) == 1:
            # only one item, check the type
            self.actions['cut'].setEnabled(True)
            self.actions['copy'].setEnabled(True)
            self.actions['shiftitems'].setEnabled(True)
            self.actions['mergelocations'].setEnabled(False)

            item = selitems[0]
            self.selObj = item
            if func_ii(item, type_spr):
                showSpritePanel = True
                updateModeInfo = True
            elif func_ii(item, type_ent):
                self.creationTabs.setCurrentIndex(2)
                self.UpdateFlag = True
                self.entranceList.setCurrentItem(item.listitem)
                self.UpdateFlag = False
                showEntrancePanel = True
                updateModeInfo = True
            elif func_ii(item, type_loc):
                self.creationTabs.setCurrentIndex(3)
                self.UpdateFlag = True
                self.locationList.setCurrentItem(item.listitem)
                self.UpdateFlag = False
                showLocationPanel = True
                updateModeInfo = True
            elif func_ii(item, type_path):
                self.creationTabs.setCurrentIndex(4)
                self.UpdateFlag = True
                self.pathList.setCurrentItem(item.listitem)
                self.UpdateFlag = False
                showPathPanel = True
                updateModeInfo = True
            elif func_ii(item, type_com):
                self.creationTabs.setCurrentIndex(8)
                self.UpdateFlag = True
                self.commentList.setCurrentItem(item.listitem)
                self.UpdateFlag = False
                updateModeInfo = True

        else:
            updateModeInfo = True

            # more than one item
            self.actions['cut'].setEnabled(True)
            self.actions['copy'].setEnabled(True)
            self.actions['shiftitems'].setEnabled(True)

        # turn on the Stamp Add btn if applicable
        self.stampAddBtn.setEnabled(len(selitems) > 0)

        # count the # of each type, for the statusbar label
        spr = 0
        ent = 0
        obj = 0
        loc = 0
        path = 0
        com = 0
        for item in selitems:
            if func_ii(item, type_spr):
                spr += 1
            elif func_ii(item, type_ent):
                ent += 1
            elif func_ii(item, type_obj):
                obj += 1
            elif func_ii(item, type_loc):
                loc += 1
            elif func_ii(item, type_path):
                path += 1
            elif func_ii(item, type_com):
                com += 1

        if loc > 2:
            self.actions['mergelocations'].setEnabled(True)

        # write the statusbar label text
        text = ''
        if len(selitems) > 0:
            singleitem = len(selitems) == 1
            if singleitem:
                if obj:
                    text = globals.trans.string('Statusbar', 0)  # 1 object selected
                elif spr:
                    text = globals.trans.string('Statusbar', 1)  # 1 sprite selected
                elif ent:
                    text = globals.trans.string('Statusbar', 2)  # 1 entrance selected
                elif loc:
                    text = globals.trans.string('Statusbar', 3)  # 1 location selected
                elif path:
                    text = globals.trans.string('Statusbar', 4)  # 1 path node selected
                else:
                    text = globals.trans.string('Statusbar', 29)  # 1 comment selected
            else:  # multiple things selected; see if they're all the same type
                if not any((spr, ent, loc, path, com)):
                    text = globals.trans.string('Statusbar', 5, '[x]', obj)  # x objects selected
                elif not any((obj, ent, loc, path, com)):
                    text = globals.trans.string('Statusbar', 6, '[x]', spr)  # x sprites selected
                elif not any((obj, spr, loc, path, com)):
                    text = globals.trans.string('Statusbar', 7, '[x]', ent)  # x entrances selected
                elif not any((obj, spr, ent, path, com)):
                    text = globals.trans.string('Statusbar', 8, '[x]', loc)  # x locations selected
                elif not any((obj, spr, ent, loc, com)):
                    text = globals.trans.string('Statusbar', 9, '[x]', path)  # x path nodes selected
                elif not any((obj, spr, ent, loc, path)):
                    text = globals.trans.string('Statusbar', 30, '[x]', com)  # x comments selected
                else:  # different types
                    text = globals.trans.string('Statusbar', 10, '[x]', len(selitems))  # x items selected
                    types = (
                        (obj, 12, 13),  # variable, translation string ID if var == 1, translation string ID if var > 1
                        (spr, 14, 15),
                        (ent, 16, 17),
                        (loc, 18, 19),
                        (path, 20, 21),
                        (com, 31, 32),
                    )
                    first = True
                    for var, singleCode, multiCode in types:
                        if var > 0:
                            if not first: text += globals.trans.string('Statusbar', 11)
                            first = False
                            text += globals.trans.string('Statusbar', (singleCode if var == 1 else multiCode), '[x]', var)
                            # above: '[x]', var) can't hurt if var == 1

                    text += globals.trans.string('Statusbar', 22)  # ')'
        self.selectionLabel.setText(text)

        self.CurrentSelection = selitems

        for thing in selitems:
            # This helps sync non-objects with objects while dragging
            if not isinstance(thing, ObjectItem):
                thing.dragoffsetx = (((thing.objx // 16) * 16) - thing.objx) * globals.TileWidth / 16
                thing.dragoffsety = (((thing.objy // 16) * 16) - thing.objy) * globals.TileWidth / 16

        self.spriteEditorDock.setVisible(showSpritePanel)
        self.entranceEditorDock.setVisible(showEntrancePanel)
        self.locationEditorDock.setVisible(showLocationPanel)
        self.pathEditorDock.setVisible(showPathPanel)

        if len(self.CurrentSelection) > 0:
            self.actions['deselect'].setEnabled(True)
        else:
            self.actions['deselect'].setEnabled(False)

        if updateModeInfo: self.UpdateModeInfo()

    def HandleObjPosChange(self, obj, oldx, oldy, x, y):
        """
        Handle the object being dragged
        """
        if obj == self.selObj:
            if oldx == x and oldy == y: return
            SetDirty()
        self.levelOverview.update()

    @QtCore.pyqtSlot(int)
    def CreationTabChanged(self, nt):
        """
        Handles the selected palette tab changing
        """
        idx = self.creationTabs.currentIndex()
        CPT = -1
        if idx == 0:  # objects
            CPT = self.objAllTab.currentIndex()
            if CPT == 1:
                CPT = 10 # "All" objects
        elif idx == 1:  # sprites
            if self.sprAllTab.currentIndex() != 1: CPT = 4
        elif idx == 2:
            CPT = 5  # entrances
        elif idx == 3:
            CPT = 7  # locations
        elif idx == 4:
            CPT = 6  # paths
        elif idx == 6:
            CPT = 8  # stamp pad
        elif idx == 7:
            CPT = 9  # comment

        globals.CurrentPaintType = CPT

    @QtCore.pyqtSlot(int)
    def ObjTabChanged(self, nt):
        """
        Handles the selected slot tab in the object palette changing
        """
        if hasattr(self, 'objPicker'):
            if nt >= 0 and nt <= 3:
                self.objPicker.ShowTileset(nt)
                if nt == 0:
                    self.objTS0Tab.setLayout(self.createObjectLayout)
                    self.folderPicker.setVisible(False)
                    self.importObj.setVisible(False)
                    self.exportAll.setVisible(False)
                    self.deleteAll.setVisible(False)
                elif nt == 1:
                    self.objTSAllTab.setLayout(self.createObjectLayout)
                    self.folderPicker.setVisible(True)
                    self.importObj.setVisible(False)
                    self.exportAll.setVisible(False)
                    self.deleteAll.setVisible(False)
                    nt = 10
                else:
                    self.objTS123Tab.setLayout(self.createObjectLayout)
                    self.folderPicker.setVisible(False)
                    self.importObj.setVisible(True)
                    self.exportAll.setVisible(True)
                    self.deleteAll.setVisible(True)
            self.defaultPropDock.setVisible(False)
        globals.CurrentPaintType = nt

    @QtCore.pyqtSlot(int)
    def SprTabChanged(self, nt):
        """
        Handles the selected tab in the sprite palette changing
        """
        if nt == 0:
            cpt = 4
        else:
            cpt = -1
        globals.CurrentPaintType = cpt

    @QtCore.pyqtSlot(int)
    def LayerChoiceChanged(self, nl):
        """
        Handles the selected layer changing
        """
        globals.CurrentLayer = nl

        # should we replace?
        if QtWidgets.QApplication.keyboardModifiers() == Qt.AltModifier:
            items = self.scene.selectedItems()
            type_obj = ObjectItem
            tileset = globals.CurrentPaintType
            area = globals.Area
            change = []

            if nl == 0:
                newLayer = area.layers[0]
            elif nl == 1:
                newLayer = area.layers[1]
            else:
                newLayer = area.layers[2]

            for x in items:
                if isinstance(x, type_obj) and x.layer != nl:
                    change.append(x)

            if len(change) > 0:
                change.sort(key=lambda x: x.zValue())

                if len(newLayer) == 0:
                    z = (2 - nl) * 8192
                else:
                    z = newLayer[-1].zValue() + 1

                if nl == 0:
                    newVisibility = globals.Layer0Shown
                elif nl == 1:
                    newVisibility = globals.Layer1Shown
                else:
                    newVisibility = globals.Layer2Shown

                for item in change:
                    area.RemoveFromLayer(item)
                    item.layer = nl
                    newLayer.append(item)
                    item.setZValue(z)
                    item.setVisible(newVisibility)
                    item.update()
                    item.UpdateTooltip()
                    z += 1

            self.scene.update()
            SetDirty()

    def ImportObjFromFile(self):
        """
        Handles importing an object
        """
        # Get the json file
        file = QtWidgets.QFileDialog.getOpenFileName(self, "Open Object", '',
                    "Object files (*.json)")[0]

        if not file: return

        with open(file) as inf:
            jsonData = json.load(inf)

        dir = os.path.dirname(file)

        # Read the other files
        with open(dir + "/" + jsonData["meta"], "rb") as inf:
            indexfile = inf.read()

        with open(dir + "/" + jsonData["objlyt"], "rb") as inf:
            deffile = inf.read()

        with open(dir + "/" + jsonData["colls"], "rb") as inf:
            colls = inf.read()

        # Get the object's definition
        indexstruct = struct.Struct('>HBBH')

        data = indexstruct.unpack_from(indexfile, 0)
        obj = ObjectDef()
        obj.width = data[1]
        obj.height = data[2]

        if "randLen" in jsonData:
            obj.randByte = data[3]

        else:
            obj.randByte = 0

        obj.load(deffile, 0)

        # Get the image and normal map
        img = QtGui.QPixmap(dir + "/" + jsonData["img"])
        nml = QtGui.QPixmap(dir + "/" + jsonData["nml"])

        # Add the object to one of the tilesets
        paintType, objNum = addObjToTileset(obj, colls, img, nml)

        # Checks if the object fit in one of the tilesets
        if paintType == 11:
            # Throw a message that the object didn't fit
            QtWidgets.QMessageBox.critical(None, 'Cannot Import', "There isn't enough room left for this object!")

    def HandleExportAllObj(self):
        """
        Handles exporting all the objects
        """
        save_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Choose where to save the Object folder")
        if not save_path: return

        for idx in [1, 2, 3]:
            if globals.ObjectDefinitions[idx] is None:
                continue

            tileoffset = idx * 256

            name = eval('globals.Area.tileset%d' % idx)

            for objNum in range(256):
                if globals.ObjectDefinitions[idx][objNum] is None:
                    break

                obj = globals.ObjectDefinitions[idx][objNum]

                jsonData = {}

                randLen = obj.randByte & 0xF

                if randLen and (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
                    tex = QtGui.QPixmap(randLen * 60, obj.height * 60)
                    nml = QtGui.QPixmap(randLen * 60, obj.height * 60)

                else:
                    tex = QtGui.QPixmap(obj.width * 60, obj.height * 60)
                    nml = QtGui.QPixmap(obj.width * 60, obj.height * 60)

                tex.fill(Qt.transparent)
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
                                if randLen and (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
                                    for z in range(randLen):
                                        painter.drawPixmap(x, y, globals.Tiles[tileNum + z].main)
                                        nmlPainter.drawPixmap(x, y, globals.Tiles[tileNum + z].nml)
                                        colls += bytes(globals.Tiles[tileNum + z].collData)
                                        x += 60
                                    break

                                else:
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
                                if randLen and (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
                                    for z in range(randLen):
                                        painter.drawPixmap(x, y, globals.Tiles[tileNum + z].main)
                                        nmlPainter.drawPixmap(x, y, globals.Tiles[tileNum + z].nml)
                                        colldata += bytes(globals.Tiles[tileNum + z].collData)
                                        x += 60
                                    break

                                else:
                                    painter.drawPixmap(x, y, globals.Tiles[tileNum].main)
                                    nmlPainter.drawPixmap(x, y, globals.Tiles[tileNum].nml)
                                    colldata += bytes(globals.Tiles[tileNum].collData)
                                    x += 60
                        y += 60
                        x = 0

                painter.end()
                nmlPainter.end()

                if not os.path.exists(save_path + "/" + name + "_objects"):
                    os.makedirs(save_path + "/" + name + "_objects")

                tex.save(save_path + "/" + name + "_objects" + "/" + name + "_object_" + str(objNum) + ".png", "PNG")
                jsonData['img'] = name + "_object_" + str(objNum) + ".png"

                nml.save(save_path + "/" + name + "_objects" + "/" + name + "_object_" + str(objNum) + "_nml.png", "PNG")
                jsonData['nml'] = name + "_object_" + str(objNum) + "_nml.png"

                with open(save_path + "/" + name + "_objects" + "/" + name + "_object_" + str(objNum) + ".colls", "wb+") as colls:
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

                with open(save_path + "/" + name + "_objects" + "/" + name + "_object_" + str(objNum) + ".objlyt", "wb+") as objlyt:
                    objlyt.write(deffile)

                jsonData['objlyt'] = name + "_object_" + str(objNum) + ".objlyt"

                indexfile = struct.pack('>HBBxB', 0, obj.width, obj.height, 0)

                with open(save_path + "/" + name + "_objects" + "/" + name + "_object_" + str(objNum) + ".meta", "wb+") as meta:
                    meta.write(indexfile)

                jsonData['meta'] = name + "_object_" + str(objNum) + ".meta"

                if randLen and (obj.width, obj.height) == (1, 1) and len(obj.rows) == 1:
                    jsonData['randLen'] = randLen

                with open(save_path + "/" + name + "_objects" + "/" + name + "_object_" + str(objNum) + ".json", 'w+') as outfile:
                    json.dump(jsonData, outfile)

    def HandleDeleteAllObj(self):
        """
        Handles deleting all objects
        """
        dlgTxt = "Do you really want to delete all the objects?\nThis can't be undone!"
        reply = QtWidgets.QMessageBox.question(self, 'Warning',
                                               dlgTxt, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            instancesFound = False
            noneRemoved = True

            for idx in [1, 2, 3]:
                if globals.ObjectDefinitions[idx] is None:
                    continue

                objNum = 0
                while True:
                    if globals.ObjectDefinitions[idx][objNum] is None:
                        break

                    instanceFound = False
                    for layer in globals.Area.layers:
                        for obj in layer:
                            if obj.tileset == idx and obj.type == objNum:
                                if not instanceFound:
                                    instanceFound = True

                                if not instancesFound:
                                    instancesFound = True

                    if instanceFound:
                        objNum += 1
                        continue

                    # Replace the object's tiles with transparent tiles
                    obj = globals.ObjectDefinitions[idx][objNum]
                    usedTiles = []
                    for row in obj.rows:
                        for tile in row:
                            if len(tile) == 3:
                                randLen = obj.randByte & 0xF
                                tileNum = tile[1] & 0xFF
                                if randLen > 0:
                                    for i in range(randLen):
                                        if tileNum + i not in usedTiles:
                                            usedTiles.append(tileNum + i)
                                else:
                                    if tileNum not in usedTiles:
                                        usedTiles.append(tileNum)

                    T = TilesetTile()
                    T.setCollisions([0] * 8)

                    tileoffset = idx * 256

                    for i in usedTiles:
                        globals.Tiles[i + tileoffset] = T

                    # Completely remove the object's definitions
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
                                    obj.SetType(idx, obj.type - 1)

                    if noneRemoved:
                        noneRemoved = False

            if not noneRemoved:
                self.objPicker.LoadFromTilesets()

                if not (globals.Area.tileset1 or globals.Area.tileset2 or globals.Area.tileset3):
                    globals.CurrentObject = -1

                globals.mainWindow.scene.update()
                SetDirty()

                globals.mainWindow.updateNumUsedTilesLabel()

            if instancesFound:
                dlgTxt = "Some objects couldn't be deleted because there are instances of them in the level scene."

                QtWidgets.QMessageBox.critical(self, 'Cannot Delete', dlgTxt)

    @QtCore.pyqtSlot(int)
    def ObjectChoiceChanged(self, type):
        """
        Handles a new object being chosen
        """
        if globals.CurrentPaintType not in [0, 10]:
            type += 1
            if type > globals.numObj[1]:
                globals.CurrentPaintType = 3
                globals.CurrentObject = type - globals.numObj[1]
            elif type > globals.numObj[0]:
                globals.CurrentPaintType = 2
                globals.CurrentObject = type - globals.numObj[0]
            else:
                globals.CurrentPaintType = 1
                globals.CurrentObject = type
            globals.CurrentObject -= 1

        else:
            globals.CurrentObject = type

    @QtCore.pyqtSlot(int)
    def ObjectReplace(self, type):
        """
        Handles a new object being chosen to replace the selected objects
        """
        if globals.CurrentPaintType == 10: return

        items = self.scene.selectedItems()
        type_obj = ObjectItem
        tileset = globals.CurrentPaintType
        changed = False

        if globals.CurrentPaintType != 0:
            type += 1

            if type > globals.numObj[1]:
                type -= globals.numObj[1]

            elif type > globals.numObj[0]:
                type -= globals.numObj[0]

            type -= 1

        for x in items:
            if isinstance(x, type_obj) and (x.tileset != tileset or x.type != type):
                x.SetType(tileset, type)
                x.update()
                changed = True

        if changed:
            SetDirty()

    @QtCore.pyqtSlot(int)
    def SpriteChoiceChanged(self, type):
        """
        Handles a new sprite being chosen
        """
        globals.CurrentSprite = type
        if type != 1000 and type >= 0:
            self.defaultDataEditor.setSprite(type)
            self.defaultDataEditor.data = to_bytes(0, 12)
            self.defaultDataEditor.update()
            self.defaultPropButton.setEnabled(True)
        else:
            self.defaultPropButton.setEnabled(False)
            self.defaultPropDock.setVisible(False)
            self.defaultDataEditor.update()

    @QtCore.pyqtSlot(int)
    def SpriteReplace(self, type):
        """
        Handles a new sprite type being chosen to replace the selected sprites
        """
        items = self.scene.selectedItems()
        type_spr = SpriteItem
        changed = False

        for x in items:
            if isinstance(x, type_spr):
                x.spritedata = self.defaultDataEditor.data  # change this first or else images get messed up
                x.SetType(type)
                x.update()
                changed = True

        if changed:
            SetDirty()

        self.ChangeSelectionHandler()

    @QtCore.pyqtSlot(int)
    def SelectNewSpriteView(self, type):
        """
        Handles a new sprite view being chosen
        """
        cat = globals.SpriteCategories[type]
        self.sprPicker.SwitchView(cat)

        isSearch = (type == len(globals.SpriteCategories) - 1)
        layout = self.spriteSearchLayout
        layout.itemAt(0).widget().setVisible(isSearch)
        layout.itemAt(1).widget().setVisible(isSearch)

    @QtCore.pyqtSlot(str)
    def NewSearchTerm(self, text):
        """
        Handles a new sprite search term being entered
        """
        self.sprPicker.SetSearchString(text)

    @QtCore.pyqtSlot()
    def ShowDefaultProps(self):
        """
        Handles the Show Default Properties button being clicked
        """
        self.defaultPropDock.setVisible(True)

    def HandleSprPosChange(self, obj, oldx, oldy, x, y):
        """
        Handle the sprite being dragged
        """
        if obj == self.selObj:
            if oldx == x and oldy == y: return
            obj.UpdateListItem()
            SetDirty()

    @QtCore.pyqtSlot('PyQt_PyObject')
    def SpriteDataUpdated(self, data):
        """
        Handle the current sprite's data being updated
        """
        if self.spriteEditorDock.isVisible():
            obj = self.selObj
            obj.spritedata = data
            obj.UpdateListItem()
            SetDirty()

            obj.UpdateDynamicSizing()

    def HandleEntPosChange(self, obj, oldx, oldy, x, y):
        """
        Handle the entrance being dragged
        """
        if oldx == x and oldy == y: return
        obj.UpdateListItem()
        if obj == self.selObj:
            SetDirty()

    def HandlePathPosChange(self, obj, oldx, oldy, x, y):
        """
        Handle the path being dragged
        """
        if oldx == x and oldy == y: return
        obj.updatePos()
        obj.pathinfo['peline'].nodePosChanged()
        obj.UpdateListItem()
        if obj == self.selObj:
            SetDirty()

    def HandleComPosChange(self, obj, oldx, oldy, x, y):
        """
        Handle the comment being dragged
        """
        if oldx == x and oldy == y: return
        obj.UpdateTooltip()
        obj.handlePosChange(oldx, oldy)
        obj.UpdateListItem()
        if obj == self.selObj:
            self.SaveComments()
            SetDirty()

    def HandleComTxtChange(self, obj):
        """
        Handle the comment's text being changed
        """
        obj.UpdateListItem()
        obj.UpdateTooltip()
        self.SaveComments()
        SetDirty()

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandleEntranceSelectByList(self, item):
        """
        Handle an entrance being selected from the list
        """
        if self.UpdateFlag: return

        # can't really think of any other way to do this
        # item = self.entranceList.item(row)
        ent = None
        for check in globals.Area.entrances:
            if check.listitem == item:
                ent = check
                break
        if ent is None: return

        ent.ensureVisible(QtCore.QRectF(), 192, 192)
        self.scene.clearSelection()
        ent.setSelected(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandleEntranceToolTipAboutToShow(self, item):
        """
        Handle an entrance being hovered in the list
        """
        ent = None
        for check in globals.Area.entrances:
            if check.listitem == item:
                ent = check
                break
        if ent is None: return

        ent.UpdateListItem(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandleLocationSelectByList(self, item):
        """
        Handle a location being selected from the list
        """
        if self.UpdateFlag: return

        # can't really think of any other way to do this
        # item = self.locationList.item(row)
        loc = None
        for check in globals.Area.locations:
            if check.listitem == item:
                loc = check
                break
        if loc is None: return

        loc.ensureVisible(QtCore.QRectF(), 192, 192)
        self.scene.clearSelection()
        loc.setSelected(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandleLocationToolTipAboutToShow(self, item):
        """
        Handle a location being hovered in the list
        """
        loc = None
        for check in globals.Area.locations:
            if check.listitem == item:
                loc = check
                break
        if loc is None: return

        loc.UpdateListItem(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandleSpriteSelectByList(self, item):
        """
        Handle a sprite being selected from the list
        """
        if self.UpdateFlag: return

        # can't really think of any other way to do this
        # item = self.spriteList.item(row)
        spr = None
        for check in globals.Area.sprites:
            if check.listitem == item:
                spr = check
                break
        if spr is None: return

        spr.ensureVisible(QtCore.QRectF(), 192, 192)
        self.scene.clearSelection()
        spr.setSelected(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandleSpriteToolTipAboutToShow(self, item):
        """
        Handle a sprite being hovered in the list
        """
        spr = None
        for check in globals.Area.sprites:
            if check.listitem == item:
                spr = check
                break
        if spr is None: return

        spr.UpdateListItem(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandlePathSelectByList(self, item):
        """
        Handle a path node being selected
        """
        # if self.UpdateFlag: return

        # can't really think of any other way to do this
        # item = self.pathlist.item(row)
        path = None
        for check in globals.Area.paths:
            if check.listitem == item:
                path = check
                break
        if path is None: return

        path.ensureVisible(QtCore.QRectF(), 192, 192)
        self.scene.clearSelection()
        path.setSelected(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandlePathToolTipAboutToShow(self, item):
        """
        Handle a path node being hovered in the list
        """
        path = None
        for check in globals.Area.paths:
            if check.listitem == item:
                path = check
                break
        if path is None: return

        path.UpdateListItem(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandleCommentSelectByList(self, item):
        """
        Handle a comment being selected
        """
        comment = None
        for check in globals.Area.comments:
            if check.listitem == item:
                comment = check
                break
        if comment is None: return

        comment.ensureVisible(QtCore.QRectF(), 192, 192)
        self.scene.clearSelection()
        comment.setSelected(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandleCommentToolTipAboutToShow(self, item):
        """
        Handle a comment being hovered in the list
        """
        comment = None
        for check in globals.Area.comments:
            if check.listitem == item:
                comment = check
                break
        if comment is None: return

        comment.UpdateListItem(True)

    def HandleLocPosChange(self, loc, oldx, oldy, x, y):
        """
        Handle the location being dragged
        """
        if loc == self.selObj:
            if oldx == x and oldy == y: return
            self.locationEditor.setLocation(loc)
            SetDirty()
        loc.UpdateListItem()
        self.levelOverview.update()

    def HandleLocSizeChange(self, loc, width, height):
        """
        Handle the location being resized
        """
        if loc == self.selObj:
            self.locationEditor.setLocation(loc)
            SetDirty()
        loc.UpdateListItem()
        self.levelOverview.update()

    def UpdateModeInfo(self):
        """
        Change the info in the currently visible panel
        """
        self.UpdateFlag = True

        if self.spriteEditorDock.isVisible():
            obj = self.selObj
            self.spriteDataEditor.setSprite(obj.type)
            self.spriteDataEditor.data = obj.spritedata
            self.spriteDataEditor.update()
        elif self.entranceEditorDock.isVisible():
            self.entranceEditor.setEntrance(self.selObj)
        elif self.pathEditorDock.isVisible():
            self.pathEditor.setPath(self.selObj)
        elif self.locationEditorDock.isVisible():
            self.locationEditor.setLocation(self.selObj)

        self.UpdateFlag = False

    @QtCore.pyqtSlot(int, int)
    def PositionHovered(self, x, y):
        """
        Handle a position being hovered in the view
        """
        info = ''
        hovereditems = self.scene.items(QtCore.QPointF(x, y))
        hovered = None
        type_zone = ZoneItem
        type_peline = PathEditorLineItem
        for item in hovereditems:
            hover = item.hover if hasattr(item, 'hover') else True
            if (not isinstance(item, type_zone)) and (not isinstance(item, type_peline)) and hover:
                hovered = item
                break

        if hovered is not None:
            if isinstance(hovered, ObjectItem):  # Object
                info = globals.trans.string('Statusbar', 23, '[width]', hovered.width, '[height]', hovered.height, '[xpos]',
                                    hovered.objx, '[ypos]', hovered.objy, '[layer]', hovered.layer, '[type]',
                                    hovered.type, '[tileset]', hovered.tileset + 1) + (
                       '' if hovered.data == 0 else '; contents value of %d' % hovered.data)
            elif isinstance(hovered, SpriteItem):  # Sprite
                info = globals.trans.string('Statusbar', 24, '[name]', hovered.name, '[xpos]', hovered.objx, '[ypos]',
                                    hovered.objy)
            elif isinstance(hovered, SLib.AuxiliaryItem):  # Sprite (auxiliary thing) (treat it like the actual sprite)
                info = globals.trans.string('Statusbar', 24, '[name]', hovered.parentItem().name, '[xpos]',
                                    hovered.parentItem().objx, '[ypos]', hovered.parentItem().objy)
            elif isinstance(hovered, EntranceItem):  # Entrance
                info = globals.trans.string('Statusbar', 25, '[name]', hovered.name, '[xpos]', hovered.objx, '[ypos]',
                                    hovered.objy, '[dest]', hovered.destination)
            elif isinstance(hovered, LocationItem):  # Location
                info = globals.trans.string('Statusbar', 26, '[id]', int(hovered.id), '[xpos]', int(hovered.objx), '[ypos]',
                                    int(hovered.objy), '[width]', int(hovered.width), '[height]', int(hovered.height))
            elif isinstance(hovered, PathItem):  # Path
                info = globals.trans.string('Statusbar', 27, '[path]', hovered.pathid, '[node]', hovered.nodeid, '[xpos]',
                                    hovered.objx, '[ypos]', hovered.objy)
            elif isinstance(hovered, CommentItem):  # Comment
                info = globals.trans.string('Statusbar', 33, '[xpos]', hovered.objx, '[ypos]', hovered.objy, '[text]',
                                    hovered.OneLineText())

        self.posLabel.setText(
            globals.trans.string('Statusbar', 28, '[objx]', int(x / globals.TileWidth), '[objy]', int(y / globals.TileWidth), '[sprx]',
                         int(x / globals.TileWidth * 16), '[spry]', int(y / globals.TileWidth * 16)))
        self.hoverLabel.setText(info)

    def updateNumUsedTilesLabel(self):
        """
        Updates the label for number of used tiles
        Based on a similar function from Satoru
        """
        usedTiles = getUsedTiles()

        numUsedTiles = 0

        for idx in range(1, 4):
            numUsedTiles += len(usedTiles[idx])

        text = str(numUsedTiles) + '/768 tiles (' + str(numUsedTiles / 768 * 100)[:5] + '%)'

        if numUsedTiles > 768:
            text = '<span style="color:red;font-weight:bold;">' + text + '</span>'

        self.numUsedTilesLabel.setText(text)

    def keyPressEvent(self, event):
        """
        Handles key press events for the main window if needed
        """
        if event.key() == Qt.Key_Delete or event.key() == Qt.Key_Backspace:
            sel = self.scene.selectedItems()
            self.SelectionUpdateFlag = True
            if len(sel) > 0:
                for obj in sel:
                    obj.delete()
                    obj.setSelected(False)
                    self.scene.removeItem(obj)
                    self.levelOverview.update()
                SetDirty()
                event.accept()
                self.SelectionUpdateFlag = False
                self.ChangeSelectionHandler()
                return
        self.levelOverview.update()

        QtWidgets.QMainWindow.keyPressEvent(self, event)

    @QtCore.pyqtSlot()
    def HandleAreaOptions(self):
        """
        Pops up the options for Area Dialogue
        """
        dlg = AreaOptionsDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            SetDirty()
            globals.Area.timelimit = dlg.LoadingTab.timer.value()
            globals.Area.unk1 = dlg.LoadingTab.unk1.value()
            globals.Area.unk2 = dlg.LoadingTab.unk2.value()
            globals.Area.unk3 = dlg.LoadingTab.unk3.value()
            globals.Area.unk4 = dlg.LoadingTab.unk4.value()
            globals.Area.unk5 = dlg.LoadingTab.unk5.value()
            globals.Area.unk6 = dlg.LoadingTab.unk6.value()
            globals.Area.unk7 = dlg.LoadingTab.unk7.value()
            globals.Area.timelimit2 = dlg.LoadingTab.timelimit2.value() + 100
            globals.Area.timelimit3 = dlg.LoadingTab.timelimit3.value() - 200

            fname = dlg.TilesetsTab.value()

            toUnload = False

            if fname in ('', None):
                toUnload = True
            else:
                if fname.startswith(globals.trans.string('AreaDlg', 16)):
                    fname = fname[len(globals.trans.string('AreaDlg', 17, '[name]', '')):]

                if fname not in ('', None):
                    if fname not in globals.szsData:
                        toUnload = True
                    else:
                        globals.Area.tileset0 = fname
                        LoadTileset(0, fname)

            if toUnload:
                globals.Area.tileset0 = ''
                UnloadTileset(0)

            self.objPicker.LoadFromTilesets()
            self.objAllTab.setCurrentIndex(0)
            self.objAllTab.setTabEnabled(0, (globals.Area.tileset0 != ''))

            for layer in globals.Area.layers:
                for obj in layer:
                    obj.updateObjCache()

            self.scene.update()

    @QtCore.pyqtSlot()
    def HandleZones(self):
        """
        Pops up the options for Zone dialog
        """
        dlg = ZonesDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            SetDirty()
            i = 0

            # resync the zones
            items = self.scene.items()
            func_ii = isinstance
            type_zone = ZoneItem

            for item in items:
                if func_ii(item, type_zone):
                    self.scene.removeItem(item)

            globals.Area.zones = []

            for tab in dlg.zoneTabs:
                z = tab.zoneObj
                z.id = i
                z.UpdateTitle()
                globals.Area.zones.append(z)
                self.scene.addItem(z)

                if tab.Zone_xpos.value() < 16:
                    z.objx = 16
                elif tab.Zone_xpos.value() > 24560:
                    z.objx = 24560
                else:
                    z.objx = tab.Zone_xpos.value()

                if tab.Zone_ypos.value() < 16:
                    z.objy = 16
                elif tab.Zone_ypos.value() > 12272:
                    z.objy = 12272
                else:
                    z.objy = tab.Zone_ypos.value()

                if (tab.Zone_width.value() + tab.Zone_xpos.value()) > 24560:
                    z.width = 24560 - tab.Zone_xpos.value()
                else:
                    z.width = tab.Zone_width.value()

                if (tab.Zone_height.value() + tab.Zone_ypos.value()) > 12272:
                    z.height = 12272 - tab.Zone_ypos.value()
                else:
                    z.height = tab.Zone_height.value()

                z.prepareGeometryChange()
                z.UpdateRects()
                z.setPos(z.objx * (globals.TileWidth / 16), z.objy * (globals.TileWidth / 16))

                if tab.Zone_xtrack.isChecked():
                    if tab.Zone_ytrack.isChecked():
                        if tab.Zone_camerabias.isChecked():
                            # Xtrack, YTrack, Bias
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.cammode = 0
                                z.camzoom = 8
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 62))
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.cammode = 3
                                z.camzoom = 9
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 63))
                            elif tab.Zone_camerazoom.currentIndex() == 2:
                                z.cammode = 0
                                z.camzoom = 1
                            elif tab.Zone_camerazoom.currentIndex() == 3:
                                z.cammode = 0
                                z.camzoom = 6
                            elif tab.Zone_camerazoom.currentIndex() == 4:
                                z.cammode = 0
                                z.camzoom = 4
                            elif tab.Zone_camerazoom.currentIndex() == 5:
                                z.cammode = 0
                                z.camzoom = 3
                            elif tab.Zone_camerazoom.currentIndex() == 6:
                                z.cammode = 3
                                z.camzoom = 3
                        else:
                            # Xtrack, YTrack, No Bias
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.cammode = 0
                                z.camzoom = 8
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.cammode = 3
                                z.camzoom = 9
                            elif tab.Zone_camerazoom.currentIndex() == 2:
                                z.cammode = 0
                                z.camzoom = 0
                            elif tab.Zone_camerazoom.currentIndex() == 3:
                                z.cammode = 0
                                z.camzoom = 7
                            elif tab.Zone_camerazoom.currentIndex() == 4:
                                z.cammode = 0
                                z.camzoom = 11
                            elif tab.Zone_camerazoom.currentIndex() == 5:
                                z.cammode = 3
                                z.camzoom = 2
                            elif tab.Zone_camerazoom.currentIndex() == 6:
                                z.cammode = 3
                                z.camzoom = 7
                    else:
                        if tab.Zone_camerabias.isChecked():
                            # Xtrack, No YTrack, Bias
                            z.cammode = 6
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.camzoom = 8
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 62))
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.camzoom = 1
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 63))
                            elif tab.Zone_camerazoom.currentIndex() == 2:
                                z.camzoom = 2
                            elif tab.Zone_camerazoom.currentIndex() == 3:
                                z.camzoom = 6
                            elif tab.Zone_camerazoom.currentIndex() == 4:
                                z.camzoom = 4
                            elif tab.Zone_camerazoom.currentIndex() == 5:
                                z.camzoom = 3
                            elif tab.Zone_camerazoom.currentIndex() == 6:
                                z.camzoom = 16
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 65))
                        else:
                            # Xtrack, No YTrack, No Bias
                            z.cammode = 6
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.camzoom = 8
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.camzoom = 0
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 64))
                            elif tab.Zone_camerazoom.currentIndex() == 2:
                                z.camzoom = 0
                            elif tab.Zone_camerazoom.currentIndex() == 3:
                                z.camzoom = 7
                            elif tab.Zone_camerazoom.currentIndex() == 4:
                                z.camzoom = 11
                            elif tab.Zone_camerazoom.currentIndex() == 5:
                                z.camzoom = 3
                            elif tab.Zone_camerazoom.currentIndex() == 6:
                                z.camzoom = 16
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 65))
                else:
                    if tab.Zone_ytrack.isChecked():
                        if tab.Zone_camerabias.isChecked():
                            # No Xtrack, YTrack, Bias
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.cammode = 1
                                z.camzoom = 8
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 62))
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.cammode = 4
                                z.camzoom = 9
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 63))
                            elif tab.Zone_camerazoom.currentIndex() == 2:
                                z.cammode = 1
                                z.camzoom = 1
                            elif tab.Zone_camerazoom.currentIndex() == 3:
                                z.cammode = 1
                                z.camzoom = 10
                            elif tab.Zone_camerazoom.currentIndex() == 4:
                                z.cammode = 1
                                z.camzoom = 4
                            elif tab.Zone_camerazoom.currentIndex() == 5:
                                z.cammode = 1
                                z.camzoom = 3
                            elif tab.Zone_camerazoom.currentIndex() == 6:
                                z.cammode = 4
                                z.camzoom = 3
                        else:
                            # No Xtrack, YTrack, No Bias
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.cammode = 4
                                z.camzoom = 8
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.cammode = 4
                                z.camzoom = 9
                            elif tab.Zone_camerazoom.currentIndex() == 2:
                                z.cammode = 1
                                z.camzoom = 0
                            elif tab.Zone_camerazoom.currentIndex() == 3:
                                z.cammode = 1
                                z.camzoom = 7
                            elif tab.Zone_camerazoom.currentIndex() == 4:
                                z.cammode = 1
                                z.camzoom = 11
                            elif tab.Zone_camerazoom.currentIndex() == 5:
                                z.cammode = 4
                                z.camzoom = 2
                            elif tab.Zone_camerazoom.currentIndex() == 6:
                                z.cammode = 4
                                z.camzoom = 7
                    else:
                        if tab.Zone_camerabias.isChecked():
                            # No Xtrack, No YTrack, Bias (glitchy)
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.cammode = 9
                                z.camzoom = 8
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 66))
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.cammode = 9
                                z.camzoom = 20
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 66))
                            elif tab.Zone_camerazoom.currentIndex() == 2:
                                z.cammode = 9
                                z.camzoom = 13
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 66))
                            elif tab.Zone_camerazoom.currentIndex() == 3:
                                z.cammode = 9
                                z.camzoom = 12
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 66))
                            elif tab.Zone_camerazoom.currentIndex() == 4:
                                z.cammode = 9
                                z.camzoom = 14
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 66))
                            elif tab.Zone_camerazoom.currentIndex() == 5:
                                z.cammode = 9
                                z.camzoom = 15
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 66))
                            elif tab.Zone_camerazoom.currentIndex() == 6:
                                z.cammode = 9
                                z.camzoom = 16
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 66))
                        else:
                            # No Xtrack, No YTrack, No Bias (glitchy)
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.cammode = 9
                                z.camzoom = 8
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 67))
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.cammode = 9
                                z.camzoom = 19
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 67))
                            elif tab.Zone_camerazoom.currentIndex() == 2:
                                z.cammode = 9
                                z.camzoom = 13
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 67))
                            elif tab.Zone_camerazoom.currentIndex() == 3:
                                z.cammode = 9
                                z.camzoom = 12
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 67))
                            elif tab.Zone_camerazoom.currentIndex() == 4:
                                z.cammode = 9
                                z.camzoom = 14
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 67))
                            elif tab.Zone_camerazoom.currentIndex() == 5:
                                z.cammode = 9
                                z.camzoom = 15
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 67))
                            elif tab.Zone_camerazoom.currentIndex() == 6:
                                z.cammode = 9
                                z.camzoom = 16
                                QtWidgets.QMessageBox.warning(None, globals.trans.string('ZonesDlg', 61),
                                                              globals.trans.string('ZonesDlg', 67))

                if tab.Zone_vnormal.isChecked():
                    z.visibility = 0
                    z.visibility = z.visibility + tab.Zone_visibility.currentIndex()
                if tab.Zone_vspotlight.isChecked():
                    z.visibility = 16
                    z.visibility = z.visibility + tab.Zone_visibility.currentIndex()
                if tab.Zone_vfulldark.isChecked():
                    z.visibility = 32
                    z.visibility = z.visibility + tab.Zone_visibility.currentIndex()

                val = tab.Zone_directionmode.currentIndex() * 2
                if val == 2: val = 1
                z.camtrack = val

                z.yupperbound = tab.Zone_yboundup.value()
                z.ylowerbound = tab.Zone_ybounddown.value()
                z.yupperbound2 = tab.Zone_yboundup2.value()
                z.ylowerbound2 = tab.Zone_ybounddown2.value()
                z.unknownbnf = 0xF if tab.Zone_boundflg.isChecked() else 0

                z.music = tab.Zone_musicid.value()
                z.sfxmod = (tab.Zone_sfx.currentIndex() * 16)
                if tab.Zone_boss.isChecked():
                    z.sfxmod = z.sfxmod + 1

                if tab.Zone_type.currentIndex() == 0:
                    z.type = 0
                elif tab.Zone_type.currentIndex() == 1:
                    z.type = 1
                elif tab.Zone_type.currentIndex() == 2:
                    z.type = 5
                elif tab.Zone_type.currentIndex() == 3:
                    z.type = 12
                elif tab.Zone_type.currentIndex() == 4:
                    z.type = 160

                i = i + 1
        self.levelOverview.update()

    # Handles setting the backgrounds
    @QtCore.pyqtSlot()
    def HandleBG(self):
        """
        Pops up the Background settings Dialog
        """
        dlg = BGDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            SetDirty()

            for z in globals.Area.zones:
                name = globals.names_bg[globals.names_bgTrans.index(str(dlg.BGTabs[z.id].bg_name.currentText()))]
                unk1 = dlg.BGTabs[z.id].unk1.value()
                unk2 = dlg.BGTabs[z.id].unk2.value()
                z.background = (z.id, unk1, to_bytes(name, 16), unk2)
                print('Zone ' + str(z.id + 1) + ' BG: ' + name)

    @QtCore.pyqtSlot()
    def HandleScreenshot(self):
        """
        Takes a screenshot of the entire level and saves it
        """

        dlg = ScreenCapChoiceDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            fn = QtWidgets.QFileDialog.getSaveFileName(globals.mainWindow, globals.trans.string('FileDlgs', 3), '/untitled.png',
                                                       globals.trans.string('FileDlgs', 4) + ' (*.png)')[0]
            if fn == '': return
            fn = str(fn)

            if dlg.zoneCombo.currentIndex() == 0:
                ScreenshotImage = QtGui.QImage(globals.mainWindow.view.width(), globals.mainWindow.view.height(),
                                               QtGui.QImage.Format_ARGB32)
                ScreenshotImage.fill(Qt.transparent)

                RenderPainter = QtGui.QPainter(ScreenshotImage)
                globals.mainWindow.view.render(RenderPainter,
                                       QtCore.QRectF(0, 0, globals.mainWindow.view.width(), globals.mainWindow.view.height()),
                                       QtCore.QRect(QtCore.QPoint(0, 0),
                                                    QtCore.QSize(globals.mainWindow.view.width(), globals.mainWindow.view.height())))
                RenderPainter.end()
            elif dlg.zoneCombo.currentIndex() == 1:
                maxX = maxY = 0
                minX = minY = 0x0ddba11
                for z in globals.Area.zones:
                    if maxX < ((z.objx * (globals.TileWidth / 16)) + (z.width * (globals.TileWidth / 16))):
                        maxX = ((z.objx * (globals.TileWidth / 16)) + (z.width * (globals.TileWidth / 16)))
                    if maxY < ((z.objy * (globals.TileWidth / 16)) + (z.height * (globals.TileWidth / 16))):
                        maxY = ((z.objy * (globals.TileWidth / 16)) + (z.height * (globals.TileWidth / 16)))
                    if minX > z.objx * (globals.TileWidth / 16):
                        minX = z.objx * (globals.TileWidth / 16)
                    if minY > z.objy * (globals.TileWidth / 16):
                        minY = z.objy * (globals.TileWidth / 16)
                maxX = (1024 * globals.TileWidth if 1024 * globals.TileWidth < maxX + 40 else maxX + 40)
                maxY = (512 * globals.TileWidth if 512 * globals.TileWidth < maxY + 40 else maxY + 40)
                minX = (0 if 40 > minX else minX - 40)
                minY = (40 if 40 > minY else minY - 40)

                ScreenshotImage = QtGui.QImage(int(maxX - minX), int(maxY - minY), QtGui.QImage.Format_ARGB32)
                ScreenshotImage.fill(Qt.transparent)

                RenderPainter = QtGui.QPainter(ScreenshotImage)
                globals.mainWindow.scene.render(RenderPainter, QtCore.QRectF(0, 0, int(maxX - minX), int(maxY - minY)),
                                        QtCore.QRectF(int(minX), int(minY), int(maxX - minX), int(maxY - minY)))
                RenderPainter.end()


            else:
                i = dlg.zoneCombo.currentIndex() - 2
                ScreenshotImage = QtGui.QImage(globals.Area.zones[i].width * globals.TileWidth / 16,
                                               globals.Area.zones[i].height * globals.TileWidth / 16, QtGui.QImage.Format_ARGB32)
                ScreenshotImage.fill(Qt.transparent)

                RenderPainter = QtGui.QPainter(ScreenshotImage)
                globals.mainWindow.scene.render(RenderPainter, QtCore.QRectF(0, 0, globals.Area.zones[i].width * globals.TileWidth / 16,
                                                                     globals.Area.zones[i].height * globals.TileWidth / 16),
                                        QtCore.QRectF(int(globals.Area.zones[i].objx) * globals.TileWidth / 16,
                                                      int(globals.Area.zones[i].objy) * globals.TileWidth / 16,
                                                      globals.Area.zones[i].width * globals.TileWidth / 16,
                                                      globals.Area.zones[i].height * globals.TileWidth / 16))
                RenderPainter.end()

            ScreenshotImage.save(fn, 'PNG', 50)

    @QtCore.pyqtSlot()
    def EditSlot1(self):
        """
        Edits Slot 1 tileset
        """
        if platform.system() == 'Windows':
            tile_path = globals.miyamoto_path + '/Tools'
        elif platform.system() == 'Linux':
            tile_path = globals.miyamoto_path + '/linuxTools'
        elif platform.system() == 'Darwin':
            tile_path = globals.miyamoto_path + '/macTools'

        if (globals.Area.tileset0 not in ('', None)) and (globals.Area.tileset0 in globals.szsData):
            sarcdata = globals.szsData[globals.Area.tileset0]

            with open(tile_path + '/tmp.tmp', 'wb') as fn:
                fn.write(sarcdata)

        else:
            con_msg = "This Tileset doesn't exist, do you want to import it?"
            reply = QtWidgets.QMessageBox.question(self, 'Message',
                                                   con_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

            if reply == QtWidgets.QMessageBox.Yes:
                fn = QtWidgets.QFileDialog.getOpenFileName(self, globals.trans.string('FileDlgs', 0), '',
                                                           globals.trans.string('FileDlgs', 2) + ' (*)')[0]
                if fn == '': return
                fn = str(fn)

                globals.Area.tileset0 = os.path.basename(fn)
                if globals.Area.tileset0 in ('', None): return
                with open(fn, 'rb') as fileobj:
                    globals.szsData[globals.Area.tileset0] = fileobj.read()

                LoadTileset(0, globals.Area.tileset0)
                SetDirty()
                self.objPicker.LoadFromTilesets()
                self.objAllTab.setCurrentIndex(0)
                self.objAllTab.setTabEnabled(0, (globals.Area.tileset0 != ''))

                for layer in globals.Area.layers:
                    for obj in layer:
                        obj.updateObjCache()

                self.scene.update()

                return

            else:
                return

        if platform.system() == 'Windows':
            os.chdir(globals.miyamoto_path + '/Tools')
            os.system('puzzle.exe ' + globals.Area.tileset0 + ' tmp.tmp "' + globals.miyamoto_path + '" 0')
            os.chdir(globals.miyamoto_path)
        elif platform.system() == 'Linux':
            os.chdir(globals.miyamoto_path + '/linuxTools')
            os.system('chmod +x ./puzzle.elf')
            os.system('./puzzle.elf ' + globals.Area.tileset0 + ' tmp.tmp "' + globals.miyamoto_path + '" 0')
            os.chdir(globals.miyamoto_path)
        elif platform.system() == 'Darwin':
            os.chdir(globals.miyamoto_path + '/macTools')
            os.system('python3 puzzle.py ' + globals.Area.tileset0 + ' tmp.tmp "' + globals.miyamoto_path + '" 0')
            os.chdir(globals.miyamoto_path)
        else:
            warningBox = QtWidgets.QMessageBox(QtWidgets.QMessageBox.NoIcon, 'OH NO',
                                               'Not a supported platform, sadly...')
            warningBox.exec_()
            return

        if os.path.isfile(tile_path + '/tmp.tmp'):
            with open(tile_path + '/tmp.tmp', 'rb') as fn:
                globals.szsData[globals.Area.tileset0] = fn.read()
            os.remove(tile_path + '/tmp.tmp')
            LoadTileset(0, globals.Area.tileset0)
            SetDirty()
            self.objPicker.LoadFromTilesets()
            self.objAllTab.setCurrentIndex(0)
            self.objAllTab.setTabEnabled(0, (globals.Area.tileset0 != ''))

            for layer in globals.Area.layers:
                for obj in layer:
                    obj.updateObjCache()

            self.scene.update()


def main():
    """
    Main startup function for Miyamoto
    """

    global MiyamotoVersion

    # create an application
    globals.app = QtWidgets.QApplication(sys.argv)

    # load the settings
    globals.settings = QtCore.QSettings('Miyamoto', MiyamotoVersion)

    # load the translation (needs to happen first)
    LoadTranslation()

    # go to the script path
    path = globals.miyamoto_path
    if path is not None:
        os.chdir(globals.miyamoto_path)

    # set the default theme, plus some other stuff too
    globals.theme = MiyamotoTheme()

    # check if required files are missing
    if FilesAreMissing():
        sys.exit(1)

    # load required stuff
    globals.Sprites = None
    globals.SpriteListData = None
    LoadGameDef()
    LoadTheme()
    LoadActionsLists()
    LoadTilesetNames()
    LoadObjDescriptions()
    LoadSpriteData()
    LoadSpriteListData()
    LoadEntranceNames()
    LoadNumberFont()
    LoadOverrides()
    SLib.OutlineColor = globals.theme.color('smi')
    SLib.main()

    # Set the default window icon (used for random popups and stuff)
    globals.app.setWindowIcon(GetIcon('miyamoto'))
    globals.app.setApplicationDisplayName('Miyamoto! v%s' % MiyamotoVersion)

    gt = setting('GridType')
    if gt == 'checker':
        globals.GridType = 'checker'
    elif gt == 'grid':
        globals.GridType = 'grid'
    else:
        globals.GridType = None
    globals.CollisionsShown = setting('ShowCollisions', False)
    globals.ObjectsFrozen = setting('FreezeObjects', False)
    globals.SpritesFrozen = setting('FreezeSprites', False)
    globals.EntrancesFrozen = setting('FreezeEntrances', False)
    globals.LocationsFrozen = setting('FreezeLocations', False)
    globals.PathsFrozen = setting('FreezePaths', False)
    globals.CommentsFrozen = setting('FreezeComments', False)
    globals.OverwriteSprite = setting('OverwriteSprite', False)
    globals.SpritesShown = setting('ShowSprites', True)
    globals.SpriteImagesShown = setting('ShowSpriteImages', True)
    globals.LocationsShown = setting('ShowLocations', True)
    globals.CommentsShown = setting('ShowComments', True)
    SLib.RealViewEnabled = globals.RealViewEnabled

    # choose a folder for the game
    # let the user pick a folder without restarting the editor if they fail
    while not isValidGamePath():
        path = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                          globals.trans.string('ChangeGamePath', 0, '[game]', globals.gamedef.name))
        if path == '':
            sys.exit(0)

        SetGamePath(path)
        if not isValidGamePath():
            QtWidgets.QMessageBox.information(None, globals.trans.string('ChangeGamePath', 1),
                                              globals.trans.string('ChangeGamePath', 3))
        else:
            setSetting('GamePath_NSMBU', path)
            break

    # create and show the main window
    globals.mainWindow = MiyamotoWindow()
    globals.mainWindow.__init2__()  # fixes bugs
    globals.mainWindow.show()
    exitcodesys = globals.app.exec_()
    globals.app.deleteLater()
    sys.exit(exitcodesys)


if '-generatestringsxml' in sys.argv:
    globals.generateStringsXML = True

if __name__ == '__main__': main()
