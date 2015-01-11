#!/usr/bin/python
# -*- coding: latin-1 -*-

# Reggie! - New Super Mario Bros. Wii Level Editor
# Version Next Milestone 2 Alpha 4
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



# reggie.py
# This is the main executable for Reggie!


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
import importlib
from math import floor as math_floor
import os.path
import pickle
import struct
import subprocess
import threading
import time
import urllib.request
from xml.etree import ElementTree as etree
import zipfile

# PyQt5: import, and error msg if not installed
try:
    from PyQt5 import QtCore, QtGui, QtWidgets
except (ImportError, NameError):
    errormsg = 'PyQt5 is not installed for this Python installation. Go online and download it.'
    raise Exception(errormsg) from None
Qt = QtCore.Qt

# PyQtRibbon: import, and error msg if not installed
try:
    from PyQtRibbon.FileMenu import QFileMenu, QFileMenuPanel
    from PyQtRibbon.RecentFilesManager import QRecentFilesManager
    from PyQtRibbon.Ribbon import QRibbon, QRibbonTab, QRibbonSection
except (ImportError, NameError):
    errormsg = 'You haven\'t installed PyQtRibbon, or your installation of it is broken. Please download or fix it.'
    raise Exception(errormsg)

# Local imports
import archive
import LHTool
import lz77
import SARC as SarcLib
import spritelib as SLib
import sprites
import TPLLib

ReggieID = 'Reggie! Level Editor Next by Treeki, Tempus, RoadrunnerWMC'
ReggieVersion = 'Next Milestone 2 Alpha 4'
UpdateURL = 'http://rvlution.net/reggie/updates.xml'


if not hasattr(QtWidgets.QGraphicsItem, 'ItemSendsGeometryChanges'):
    # enables itemChange being called on QGraphicsItem
    QtWidgets.QGraphicsItem.ItemSendsGeometryChanges = QtWidgets.QGraphicsItem.GraphicsItemFlag(0x800)


# Globals
app = None
mainWindow = None
settings = None


# Game enums
NewSuperMarioBros = 0
NewSuperMarioBrosWii = 1
NewSuperMarioBros2 = 2
NewSuperMarioBrosU = 3
NewSuperLuigiU = 4
FileExtentions = {
    NewSuperMarioBros: (),
    NewSuperMarioBrosWii: ('.arc', '.arc.LH'),
    NewSuperMarioBros2: ('.sarc',),
    NewSuperMarioBrosU: ('.sarc',),
    NewSuperLuigiU: ('.sarc',),
    }
FirstLevels = {
    NewSuperMarioBros: '',
    NewSuperMarioBrosWii: '01-01',
    NewSuperMarioBros2: '1-1',
    NewSuperMarioBrosU: '',
    NewSuperLuigiU: '',
    }

def checkSplashEnabled():
    """
    Checks to see if the splash screen is enabled
    """
    global prefs
    if setting('SplashEnabled') is None and not TPLLib.using_cython:
        return True
    elif setting('SplashEnabled'):
        return True
    else:
        return False

def loadSplash():
    """
    If called, this will show the splash screen until removeSplash is called
    """
    splashpixmap = QtGui.QPixmap('reggiedata/splash.png')
    app.splashscrn = QtWidgets.QSplashScreen(splashpixmap)
    app.splashscrn.show()
    app.processEvents()

def updateSplash(message, progress):
    """
    This will update the splashscreen with the given message and progressval
    """
    font = QtGui.QFont()
    font.setPointSize(10)

    message = trans.string('Splash', 0, '[current]', message, '[stage]', progress)
    splashtextpixmap = QtGui.QPixmap('reggiedata/splash.png')
    splashtextpixmappainter = QtGui.QPainter(splashtextpixmap)
    splashtextpixmappainter.setFont(font)
    splashtextpixmappainter.drawText(220, 195, message)
    app.splashscrn.setPixmap(splashtextpixmap)
    splashtextpixmappainter = None
    app.processEvents()

def removeSplash():
    """
    This will delete the splash screen, if it exists
    """
    if app.splashscrn is not None:
        app.splashscrn.close()
        app.splashscrn = None
        splashpixmap = None
        splashtextpixmap = None

def GetUseRibbon():
    """
    This tells us if we're using the Ribbon
    """
    global UseRibbon
    if str(setting('Menu')) == 'Ribbon': UseRibbon = True
    else: UseRibbon = False

defaultStyle = None
defaultPalette = None
def GetDefaultStyle():
    """
    Stores a copy of the default app style upon launch, which can then be accessed later
    """
    global defaultStyle, defaultPalette, app
    if (defaultStyle, defaultPalette) != (None, None): return
    defaultStyle = app.style()
    defaultPalette = QtGui.QPalette(app.palette())

def setting(name, default=None):
    """
    Thin wrapper around QSettings, fixes the type=bool bug
    """
    result = settings.value(name, default)
    if result == 'false': return False
    elif result == 'true': return True
    elif result == 'none': return None
    else: return result

def setSetting(name, value):
    """
    Thin wrapper around QSettings
    """
    return settings.setValue(name, value)

def module_path():
    """
    This will get us the program's directory, even if we are frozen using cx_Freeze
    """
    if hasattr(sys, 'frozen'):
        return os.path.dirname(sys.executable)
    if __name__ == '__main__':
        return os.path.dirname(os.path.abspath(sys.argv[0]))
    return None

compressed = False
def checkContent(data):
    if not data.startswith(b'SARC'):
        return False

    required = (b'course/', b'course1.bin')
    for r in required:
        if r not in data:
            return False

    return True

def IsNSMBLevel(filename):
    global compressed
    """
    Does some basic checks to confirm a file is a NSMB level
    """
    if not os.path.isfile(filename): return False

    f = open(filename, 'rb')
    data = f.read()
    f.close()
    del f

    if LHTool.isLHCompressed(data):
        decomp = LHTool.decompressLH(data)
        if checkContent(decomp):
            compressed = True
            return True
    else:
        if checkContent(data):
            compressed = False
            return True


def FilesAreMissing():
    """
    Checks to see if any of the required files for Reggie are missing
    """

    if not os.path.isdir('reggiedata'):
        QtWidgets.QMessageBox.warning(None, trans.string('Err_MissingFiles', 0), trans.string('Err_MissingFiles', 1))
        return True

    required = ['entrances.png', 'entrancetypes.txt', 'icon.png', 'levelnames.xml', 'overrides.png',
                'spritedata.xml', 'tilesets.xml', 'bga/000A.png', 'bga.txt', 'bgb/000A.png', 'bgb.txt',
                'about.png', 'spritecategories.xml']

    missing = []

    for check in required:
        if not os.path.isfile('reggiedata/' + check):
            missing.append(check)

    if len(missing) > 0:
        QtWidgets.QMessageBox.warning(None, trans.string('Err_MissingFiles', 0), trans.string('Err_MissingFiles', 2, '[files]', ', '.join(missing)))
        return True

    return False


def GetIcon(name, big=False):
    """
    Helper function to grab a specific icon
    """
    return theme.GetIcon(name, big)


def SetGamePath(newpath):
    """
    Sets the NSMBWii game path
    """
    global gamedef

    # you know what's fun?
    # isValidGamePath crashes in os.path.join if QString is used..
    # so we must change it to a Python string manually
    gamedef.SetGamePath(str(newpath))



def isValidGamePath(check='ug'):
    """
    Checks to see if the path for NSMB2 contains a valid game
    """
    if check == 'ug': check = gamedef.GetGamePath()

    if check is None or check == '': return False
    if not os.path.isdir(check): return False
    if not os.path.isdir(os.path.join(check, 'Unit')): return False
    if not os.path.isfile(os.path.join(check, '1-1.sarc')): return False

    return True



LevelNames = None
def LoadLevelNames():
    """
    Ensures that the level name info is loaded
    """
    global LevelNames

    # Parse the file
    tree = etree.parse(GetPath('levelnames'))
    root = tree.getroot()

    # Parse the nodes (root acts like a large category)
    LevelNames = LoadLevelNames_Category(root)

def LoadLevelNames_Category(node):
    """
    Loads a LevelNames XML category
    """
    cat = []
    for child in node:
        if child.tag.lower() == 'category':
            cat.append((str(child.attrib['name']), LoadLevelNames_Category(child)))
        elif child.tag.lower() == 'level':
            cat.append((str(child.attrib['name']), str(child.attrib['file'])))
    return tuple(cat)


TilesetNames = None
def LoadTilesetNames(reload_=False):
    """
    Ensures that the tileset name info is loaded
    """
    global TilesetNames
    if (TilesetNames is not None) and (not reload_): return

    # Get paths
    paths = gamedef.recursiveFiles('tilesets')
    new = []
    new.append(trans.files['tilesets'])
    for path in paths: new.append(path)
    paths = new

    # Read each file
    TilesetNames = [[[], False], [[], False], [[], False], [[], False]]
    for path in paths:
        tree = etree.parse(path)
        root = tree.getroot()

        # Go through each slot
        for node in root:
            if node.tag.lower() != 'slot': continue
            try: slot = int(node.attrib['num'])
            except ValueError: continue
            if slot > 3: continue

            # Parse the category data into a list
            newlist = [LoadTilesetNames_Category(node),]
            if 'sorted' in node.attrib: newlist.append(node.attrib['sorted'].lower() == 'true')
            else: newlist.append(TilesetNames[slot][1]) # inherit

            # Apply it as a patch over the current entry
            newlist[0] = CascadeTilesetNames_Category(TilesetNames[slot][0], newlist[0])

            # Sort it
            if not newlist[1]:
                newlist[0] = SortTilesetNames_Category(newlist[0])

            TilesetNames[slot] = newlist

def LoadTilesetNames_Category(node):
    """
    Loads a TilesetNames XML category
    """
    cat = []
    for child in node:
        if child.tag.lower() == 'category':
            new = [
                str(child.attrib['name']),
                LoadTilesetNames_Category(child),
                ]
            if 'sorted' in child.attrib: new.append(str(child.attrib['sorted'].lower()) == 'true')
            else: new.append(False)
            cat.append(new)
        elif child.tag.lower() == 'tileset':
            cat.append((str(child.attrib['filename']), str(child.attrib['name'])))
    return list(cat)

def CascadeTilesetNames_Category(lower, upper):
    """
    Applies upper as a patch of lower
    """
    lower = list(lower)
    for item in upper:

        if isinstance(item[1], tuple) or isinstance(item[1], list):
            # It's a category

            found = False
            for i, lowitem in enumerate(lower):
                lowitem = lower[i]
                if lowitem[0] == item[0]: # names are ==
                    lower[i] = list(lower[i])
                    lower[i][1] = CascadeTilesetNames_Category(lowitem[1], item[1])
                    found = True
                    break

            if not found:
                i = 0
                while (i < len(lower)) and (isinstance(lower[i][1], tuple) or isinstance(lower[i][1], list)): i += 1
                lower.insert(i+1, item)

        else: # It's a tileset entry
            found = False
            for i, lowitem in enumerate(lower):
                lowitem = lower[i]
                if lowitem[0] == item[0]: # filenames are ==
                    lower[i] = list(lower[i])
                    lower[i][1] = item[1]
                    found = True
                    break

            if not found: lower.append(item)
    return lower

def SortTilesetNames_Category(cat):
    """
    Sorts a tileset names category
    """
    cat = list(cat)

    # First, remove all category nodes
    cats = []
    for node in cat:
        if isinstance(node[1], tuple) or isinstance(node[1], list):
            cats.append(node)
    for node in cats: cat.remove(node)

    # Sort the tileset names
    cat.sort(key=lambda entry: entry[1])

    # Sort the data within each category
    for i, cat_ in enumerate(cats):
        cats[i] = list(cat_)
        if not cats[i][2]: cats[i][1] = SortTilesetNames_Category(cats[i][1])

    # Put them back together
    new = []
    for category in cats: new.append(tuple(category))
    for tileset in cat: new.append(tuple(tileset))
    return tuple(new)

ObjDesc = None
def LoadObjDescriptions(reload_=False):
    """
    Ensures that the object description is loaded
    """
    global ObjDesc
    if (ObjDesc is not None) and not reload_: return

    paths, isPatch = gamedef.recursiveFiles('ts1_descriptions', True)
    if isPatch:
        new = []
        new.append(trans.files['ts1_descriptions'])
        for path in paths: new.append(path)
        paths = new

    ObjDesc = {}
    for path in paths:
        f = open(path)
        raw = [x.strip() for x in f.readlines()]
        f.close()

        for line in raw:
            w = line.split('=')
            ObjDesc[int(w[0])] = w[1]


BgANames = None
def LoadBgANames(reload_=False):
    """
    Ensures that the background name info is loaded
    """
    global BgANames
    if (BgANames is not None) and not reload_: return

    paths, isPatch = gamedef.recursiveFiles('bga', True)
    if isPatch:
        new = []
        new.append(trans.files['bga'])
        for path in paths: new.append(path)
        paths = new

    BgANames = []
    for path in paths:
        f = open(path)
        raw = [x.strip() for x in f.readlines()]
        f.close()

        for line in raw:
            w = line.split('=')

            found = False
            for check in BgANames:
                if check[0] == w[0]:
                    check[1] = w[1]
                    found = True

            if not found: BgANames.append([w[0], w[1]])

        BgANames = sorted(BgANames, key=lambda entry: int(entry[0], 16))


BgBNames = None
def LoadBgBNames(reload_=False):
    """
    Ensures that the background name info is loaded
    """
    global BgBNames
    if (BgBNames is not None) and not reload_: return

    paths, isPatch = gamedef.recursiveFiles('bgb', True)
    if isPatch:
        new = []
        new.append(trans.files['bgb'])
        for path in paths: new.append(path)
        paths = new

    BgBNames = []
    for path in paths:
        f = open(path)
        raw = [x.strip() for x in f.readlines()]
        f.close()

        for line in raw:
            w = line.split('=')

            found = False
            for check in BgBNames:
                if check[0] == w[0]:
                    check[1] = w[1]
                    found = True

            if not found: BgBNames.append([w[0], w[1]])

        BgBNames = sorted(BgBNames, key=lambda entry: int(entry[0], 16))


def LoadConstantLists():
    """
    Loads some lists of constants
    """
    global BgScrollRates
    global BgScrollRateStrings
    global ZoneThemeValues
    global ZoneTerrainThemeValues
    global Sprites
    global SpriteCategories

    BgScrollRates = [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0, 0.0, 1.2, 1.5, 2.0, 4.0]
    BgScrollRateStrings = []
    s = trans.stringList('BGDlg', 1)
    for i in s:
        BgScrollRateStrings.append(i)

    ZoneThemeValues = trans.stringList('ZonesDlg', 1)

    ZoneTerrainThemeValues = trans.stringList('ZonesDlg', 2)

    Sprites = None
    SpriteListData = None


class SpriteDefinition():
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
            QtCore.QAbstractListModel.__init__(self)
            self.entries = entries
            self.existingLookup = existingLookup
            self.max = max

        def rowCount(self, parent=None):
            """
            Required by Qt
            """
            #return self.max
            return len(self.entries)

        def data(self, index, role=Qt.DisplayRole):
            """
            Get what we have for a specific row
            """
            if not index.isValid(): return None
            n = index.row()
            if n < 0: return None
            #if n >= self.max: return None
            if n >= len(self.entries): return None

            if role == Qt.DisplayRole:
                #entries = self.entries
                #if n in entries:
                #    return '%d: %s' % (n, entries[n])
                #else:
                #    return '%d: <unknown/unused>' % n
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
                comment = trans.string('SpriteDataEditor', 1, '[name]', attribs['title'], '[note]', attribs['comment'])
            else:
                comment = None

            if field.tag == 'checkbox':
                # parameters: title, nybble, mask, comment
                snybble = attribs['nybble']
                if '-' not in snybble:
                    nybble = int(snybble) - 1
                else:
                    getit = snybble.split('-')
                    nybble = (int(getit[0]) - 1, int(getit[1]))

                fields.append((0, attribs['title'], nybble, int(attribs['mask']) if 'mask' in attribs else 1, comment))
            elif field.tag == 'list':
                # parameters: title, nybble, model, comment
                snybble = attribs['nybble']
                if '-' not in snybble:
                    nybble = int(snybble) - 1
                    max = 16
                else:
                    getit = snybble.split('-')
                    nybble = (int(getit[0]) - 1, int(getit[1]))
                    max = (16 << ((nybble[1] - nybble[0] - 1) * 4))

                entries = []
                existing = [None for i in range(max)]
                for e in field:
                    if e.tag != 'entry': continue

                    i = int(e.attrib['value'])
                    entries.append((i, e.text))
                    existing[i] = True

                fields.append((1, attribs['title'], nybble, SpriteDefinition.ListPropertyModel(entries, existing, max), comment))
            elif field.tag == 'value':
                # parameters: title, nybble, max, comment
                snybble = attribs['nybble']

                # if it's 5-12 skip it
                # fixes tobias's crashy 'unknown values'
                if snybble == '5-12': continue

                if '-' not in snybble:
                    nybble = int(snybble) - 1
                    max = 16
                else:
                    getit = snybble.split('-')
                    nybble = (int(getit[0]) - 1, int(getit[1]))
                    max = (16 << ((nybble[1] - nybble[0] - 1) * 4))

                fields.append((2, attribs['title'], nybble, max, comment))
            elif field.tag == 'bitfield':
                # parameters: title, startbit, bitnum, comment
                startbit = int(attribs['startbit'])
                bitnum = int(attribs['bitnum'])

                fields.append((3, attribs['title'], startbit, bitnum, comment))


def LoadSpriteData():
    """
    Ensures that the sprite data info is loaded
    """
    global Sprites

    Sprites = [None] * 326
    errors = []
    errortext = []

    # It works this way so that it can overwrite settings based on order of precedence
    paths = []
    paths.append((trans.files['spritedata'], None))
    for pathtuple in gamedef.multipleRecursiveFiles('spritedata', 'spritenames'): paths.append(pathtuple)


    for sdpath, snpath in paths:

        # Add XML sprite data, if there is any
        if sdpath not in (None, ''):
            path = sdpath if isinstance(sdpath, str) else sdpath.path
            tree = etree.parse(path)
            root = tree.getroot()

            for sprite in root:
                if sprite.tag.lower() != 'sprite': continue

                try: spriteid = int(sprite.attrib['id'])
                except ValueError: continue
                spritename = sprite.attrib['name']
                notes = None
                relatedObjFiles = None

                if 'notes' in sprite.attrib:
                    notes = trans.string('SpriteDataEditor', 2, '[notes]', sprite.attrib['notes'])

                if 'files' in sprite.attrib:
                    relatedObjFiles = trans.string('SpriteDataEditor', 8, '[list]', sprite.attrib['files'].replace(';', '<br>'))

                sdef = SpriteDefinition()
                sdef.id = spriteid
                sdef.name = spritename
                sdef.notes = notes
                sdef.relatedObjFiles = relatedObjFiles

                try:
                    sdef.loadFrom(sprite)
                except Exception as e:
                    errors.append(str(spriteid))
                    errortext.append(str(e))

                Sprites[spriteid] = sdef

        # Add TXT sprite names, if there are any
        # This code is only ever run when a custom
        # gamedef is loaded, because spritenames.txt
        # is a file only ever used by custom gamedefs.
        if (snpath is not None) and (snpath.path is not None):
            snfile = open(snpath.path)
            data = snfile.read()
            snfile.close()
            del snfile

            # Split the data
            data = data.split('\n')
            for i, line in enumerate(data): data[i] = line.split(':')

            # Apply it
            for spriteid, name in data:
                Sprites[int(spriteid)].name = name

    # Warn the user if errors occurred
    if len(errors) > 0:
        QtWidgets.QMessageBox.warning(None, trans.string('Err_BrokenSpriteData', 0), trans.string('Err_BrokenSpriteData', 1, '[sprites]', ', '.join(errors)), QtWidgets.QMessageBox.Ok)
        QtWidgets.QMessageBox.warning(None, trans.string('Err_BrokenSpriteData', 2), repr(errortext))

SpriteCategories = None
def LoadSpriteCategories(reload_=False):
    """
    Ensures that the sprite category info is loaded
    """
    global Sprites, SpriteCategories
    if (SpriteCategories is not None) and not reload_: return

    paths, isPatch = gamedef.recursiveFiles('spritecategories', True)
    if isPatch:
        new = []
        new.append(trans.files['spritecategories'])
        for path in paths: new.append(path)
        paths = new

    SpriteCategories = []
    for path in paths:
        tree = etree.parse(path)
        root = tree.getroot()

        CurrentView = None
        for view in root:
            if view.tag.lower() != 'view': continue

            viewname = view.attrib['name']

            # See if it's in there already
            CurrentView = []
            for potentialview in SpriteCategories:
                if potentialview[0] == viewname: CurrentView = potentialview[1]
            if CurrentView == []: SpriteCategories.append((viewname, CurrentView, []))

            CurrentCategory = None
            for category in view:
                if category.tag.lower() != 'category': continue

                catname = category.attrib['name']

                # See if it's in there already
                CurrentCategory = []
                for potentialcat in CurrentView:
                    if potentialcat[0] == catname: CurrentCategory = potentialcat[1]
                if CurrentCategory == []: CurrentView.append((catname, CurrentCategory))

                for attach in category:
                    if attach.tag.lower() != 'attach': continue

                    sprite = attach.attrib['sprite']
                    if '-' not in sprite:
                        if int(sprite) not in CurrentCategory:
                            CurrentCategory.append(int(sprite))
                    else:
                        x = sprite.split('-')
                        for i in range(int(x[0]), int(x[1])+1):
                            if i not in CurrentCategory:
                                CurrentCategory.append(i)

    # Add a Search category
    SpriteCategories.append((trans.string('Sprites', 19), [(trans.string('Sprites', 16), list(range(0, 326)))], []))
    SpriteCategories[-1][1][0][1].append(9999) # 'no results' special case


SpriteListData = None
def LoadSpriteListData(reload_=False):
    """
    Ensures that the sprite list modifier data is loaded
    """
    global SpriteListData
    if (SpriteListData is not None) and not reload_: return

    paths = gamedef.recursiveFiles('spritelistdata')
    new = []
    new.append('reggiedata/spritelistdata.txt')
    for path in paths: new.append(path)
    paths = new

    SpriteListData = []
    for i in range(24): SpriteListData.append([])
    for path in paths:
        f = open(path)
        data = f.read()
        f.close()

        split = data.replace('\n', '').split(';')
        for lineidx in range(24):
            line = split[lineidx]
            splitline = line.split(',')
            splitlinelist = []

            # Add them
            for item in splitline:
                try: newitem = int(item)
                except ValueError: continue
                if newitem in SpriteListData[lineidx]: continue
                SpriteListData[lineidx].append(newitem)
            SpriteListData[lineidx].sort()


EntranceTypeNames = None
def LoadEntranceNames(reload_=False):
    """
    Ensures that the entrance names are loaded
    """
    global EntranceTypeNames
    if (EntranceTypeNames is not None) and not reload_: return

    paths, isPatch = gamedef.recursiveFiles('entrancetypes', True)
    if isPatch:
        new = []
        new.append(trans.files['entrancetypes'])
        for path in paths: new.append(path)
        paths = new

    NameList = {}
    for path in paths:
        getit = open(path, 'r')
        newNames = {}
        for line in getit.readlines(): newNames[int(line.split(':')[0])] = line.split(':')[1].replace('\n', '')
        for idx in newNames: NameList[idx] = newNames[idx]

    EntranceTypeNames = []
    idx = 0
    while idx in NameList:
        EntranceTypeNames.append(trans.string('EntranceDataEditor', 28, '[id]', idx, '[name]', NameList[idx]))
        idx += 1


class ChooseLevelNameDialog(QtWidgets.QDialog):
    """
    Dialog which lets you choose a level from a list
    """
    def __init__(self):
        """
        Creates and initializes the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('OpenFromNameDlg', 0))
        self.setWindowIcon(GetIcon('open'))
        LoadLevelNames()
        self.currentlevel = None

        # create the tree
        tree = QtWidgets.QTreeWidget()
        tree.setColumnCount(1)
        tree.setHeaderHidden(True)
        tree.setIndentation(16)
        tree.currentItemChanged.connect(self.HandleItemChange)
        tree.itemActivated.connect(self.HandleItemActivated)

        # add items (LevelNames is effectively a big category)
        tree.addTopLevelItems(self.ParseCategory(LevelNames))

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

        self.setMinimumWidth(320) # big enough to fit "World 5: Freezeflame Volcano/Freezeflame Glacier"
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
                node.setToolTip(0, item[1] + '.sarc')
            else:
                # it's a category
                children = self.ParseCategory(item[1])
                for cnode in children:
                    node.addChild(cnode)
                node.setToolTip(0, item[0])
            nodes.append(node)
        return tuple(nodes)

    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem)
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


    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
    def HandleItemActivated(self, item, column):
        """
        Handle a doubleclick on a level
        """
        self.currentlevel = item.data(0, Qt.UserRole)
        if self.currentlevel is not None:
            self.currentlevel = str(self.currentlevel)
            self.accept()


Tiles = None # 0x200 tiles per tileset, plus 64 for each type of override
TilesetFilesLoaded = [None, None, None, None]
TilesetAnimTimer = None
TilesetCache = {} # Tileset cache, to avoid reloading when possible
Overrides = None # 320 tiles, this is put into Tiles usually
TileBehaviours = None
ObjectDefinitions = None # 4 tilesets
TilesetsAnimating = False

class ObjectDef():
    """
    Class for the object definitions
    """

    def __init__(self):
        """
        Constructor
        """
        self.width = 0
        self.height = 0
        self.rows = []

    def load(self, source, offset, tileoffset):
        """
        Load an object definition
        """
        i = offset
        row = []

        while True:
            cbyte = source[i]

            if cbyte == 0xFE:
                self.rows.append(row)
                i += 1
                row = []
            elif cbyte == 0xFF:
                return
            elif (cbyte & 0x80) != 0:
                row.append((cbyte,))
                i += 1
            else:
                extra = source[i+2]
                tilesetoffset = ((extra & 7) >> 1) * 0x200
                tile = (cbyte, source[i+1] + tilesetoffset, extra >> 2)
                row.append(tile)
                i += 3


class TilesetTile():
    """
    Class that represents a single tile in a tileset
    """
    def __init__(self, main):
        """
        Initializes the TilesetTile
        """
        self.main = main
        self.isAnimated = False
        self.animFrame = 0
        self.animTiles = []
        self.collData = ()
        self.collOverlay = None
        self.depthMap = None

    def addAnimationData(self, data):
        """
        Applies Newer-style animation data to the tile
        """
        animTiles = []
        numberOfFrames = len(data) // 2048
        for frame in range(numberOfFrames):
            framedata = data[frame*2048: (frame*2048)+2048]
            decoder = TPLLib.decoder(TPLLib.RGB4A3)
            decoder = decoder(framedata, 32, 32)
            newdata = decoder.run()
            img = QtGui.QImage(newdata, 32, 32, 128, QtGui.QImage.Format_ARGB32)
            pix = QtGui.QPixmap.fromImage(img.copy(0, 0, 31, 31).scaledToHeight(24, Qt.SmoothTransformation))
            animTiles.append(pix)
        self.animTiles = animTiles
        self.isAnimated = True

        # This NSMBLib method crashes.
        ##padded = str(data)
        ##padded += ' ' * (0x80000 - len(data))
        ### It'll crash on this next line
        ##rgbdata = NSMBLib.decodeTileAnims(padded)
        ##tilesImg = QtGui.QImage(rgbdata, 32, (len(rgbdata)/4)/32, 32*4, QtGui.QImage.Format_ARGB32_Premultiplied)
        ##tilesPix = QtGui.QPixmap.fromImage(tilesImg)

        ##self.isAnimated = True
        ##self.animTiles = []
        ##self.animTiles.append(tilesPix.copy(0, 0, 31, 31).scaled(24, 24))

    def nextFrame(self):
        """
        Increments to the next frame
        """
        if not self.isAnimated: return
        self.animFrame += 1
        if self.animFrame == len(self.animTiles):
            self.animFrame = 0

    def resetAnimation(self):
        """
        Resets the animation frame
        """
        self.animFrame = 0

    def getCurrentTile(self):
        """
        Returns the current tile based on the current animation frame
        """
        result = None
        if (not TilesetsAnimating) or (not self.isAnimated): result = self.main
        else: result = self.animTiles[self.animFrame]
        result = QtGui.QPixmap(result)

        p = QtGui.QPainter(result)
        if CollisionsShown and (self.collOverlay is not None):
            p.drawPixmap(0, 0, self.collOverlay)
        if DepthShown and (self.depthMap is not None):
            p.drawPixmap(0, 0, self.depthMap)
        del p

        return result

    def setCollisions(self, colldata):
        """
        Sets the collision data for this tile
        """
        self.collData = tuple(colldata)
        self.updateCollisionOverlay()

    def setQuestionCollisions(self):
        """
        Sets the collision data to that of a question block
        """
        self.setCollisions((0,0,0,5,0,0,0,0))

    def setBrickCollisions(self):
        """
        Sets the collision data to that of a brick block
        """
        self.setCollisions((0,0,0,0x10,0,0,0,0))

    def updateCollisionOverlay(self):
        """
        Updates the collisions overlay for this pixmap
        """
        # This is completely stolen from Puzzle. Only minor
        # changes have been made. Thanks, Treeki!
        CD = self.collData
        if CD[2] & 16:      # Red
            color = QtGui.QColor(255, 0, 0, 120)
        elif CD[5] == 1:    # Ice
            color = QtGui.QColor(0, 0, 255, 120)
        elif CD[5] == 2:    # Snow
            color = QtGui.QColor(0, 0, 255, 120)
        elif CD[5] == 3:    # Quicksand
            color = QtGui.QColor(128,64,0, 120)
        elif CD[5] == 4:    # Conveyor
            color = QtGui.QColor(128,128,128, 120)
        elif CD[5] == 5:    # Conveyor
            color = QtGui.QColor(128,128,128, 120)
        elif CD[5] == 6:    # Rope
            color = QtGui.QColor(128,0,255, 120)
        elif CD[5] == 7:    # Half Spike
            color = QtGui.QColor(128,0,255, 120)
        elif CD[5] == 8:    # Ledge
            color = QtGui.QColor(128,0,255, 120)
        elif CD[5] == 9:    # Ladder
            color = QtGui.QColor(128,0,255, 120)
        elif CD[5] == 10:   # Staircase
            color = QtGui.QColor(255, 0, 0, 120)
        elif CD[5] == 11:   # Carpet
            color = QtGui.QColor(255, 0, 0, 120)
        elif CD[5] == 12:   # Dust
            color = QtGui.QColor(128,64,0, 120)
        elif CD[5] == 13:   # Grass
            color = QtGui.QColor(0, 255, 0, 120)
        elif CD[5] == 14:   # Unknown
            color = QtGui.QColor(255, 0, 0, 120)
        elif CD[5] == 15:   # Beach Sand
            color = QtGui.QColor(128, 64, 0, 120)
        else:               # Brown?
            color = QtGui.QColor(64, 30, 0, 120)


        # Sets Brush style for fills
        if CD[2] & 4:        # Climbing Grid
            style = Qt.DiagCrossPattern
        elif (CD[3] & 16) or (CD[3] & 4) or (CD[3] & 8): # Breakable
            style = Qt.Dense5Pattern
        else:
            style = Qt.SolidPattern

        brush = QtGui.QBrush(color, style)
        pen = QtGui.QPen(QtGui.QColor(0,0,0,128))
        collPix = QtGui.QPixmap(24, 24)
        collPix.fill(QtGui.QColor(0,0,0,0))
        painter = QtGui.QPainter(collPix)
        painter.setBrush(brush)
        painter.setPen(pen)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Paints shape based on other stuff
        if CD[3] & 32: # Slope
            if CD[7] == 0:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 0)]))
            elif CD[7] == 1:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 2:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 12)]))
            elif CD[7] == 3:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(0, 12),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 24)]))
            elif CD[7] == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(24, 24)]))
            elif CD[7] == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 12),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 10:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 0)]))
            elif CD[7] == 11:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(24, 18),
                                                    QtCore.QPoint(24, 24)]))
            elif CD[7] == 12:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(0, 18),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 13:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 6),
                                                    QtCore.QPoint(0, 12),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 14:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(0, 6),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 15:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 6),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 16:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(0, 6),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 17:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 18),
                                                    QtCore.QPoint(0, 12),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 18:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(0, 18),
                                                    QtCore.QPoint(0, 24)]))

        elif CD[3] & 64: # Reverse Slope
            if CD[7] == 0:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 0)]))
            elif CD[7] == 1:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0)]))
            elif CD[7] == 2:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 12)]))
            elif CD[7] == 3:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(0, 12),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 0)]))
            elif CD[7] == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 12)]))
            elif CD[7] == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 12),
                                                    QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0)]))
            elif CD[7] == 10:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 0)]))
            elif CD[7] == 11:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 6)]))
            elif CD[7] == 12:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(0, 6)]))
            elif CD[7] == 13:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 18),
                                                    QtCore.QPoint(0, 12)]))
            elif CD[7] == 14:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(0, 18)]))
            elif CD[7] == 15:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 18),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 16:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(0, 18)]))
            elif CD[7] == 17:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 6),
                                                    QtCore.QPoint(0, 12)]))
            elif CD[7] == 18:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(0, 6)]))

        elif CD[2] & 8: # Partial
            if CD[7] == 1:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(12, 0),
                                                    QtCore.QPoint(12, 12),
                                                    QtCore.QPoint(0, 12)]))
            elif CD[7] == 2:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(12, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(12, 12)]))
            elif CD[7] == 3:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(0, 12)]))
            elif CD[7] == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 12),
                                                    QtCore.QPoint(12, 12),
                                                    QtCore.QPoint(12, 24),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(12, 0),
                                                    QtCore.QPoint(12, 24),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 6:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(12, 24),
                                                    QtCore.QPoint(12, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(0, 12)]))
            elif CD[7] == 7:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(12, 12),
                                                    QtCore.QPoint(12, 24),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 8:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(12, 12),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(12, 24)]))
            elif CD[7] == 9:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(0, 12),
                                                    QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(12, 24),
                                                    QtCore.QPoint(12, 0)]))
            elif CD[7] == 10:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(12, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(12, 24)]))
            elif CD[7] == 11:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(12, 24),
                                                    QtCore.QPoint(12, 12),
                                                    QtCore.QPoint(0, 12)]))
            elif CD[7] == 12:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 12),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 13:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(12, 0),
                                                    QtCore.QPoint(12, 12),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 14:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(12, 0),
                                                    QtCore.QPoint(12, 12),
                                                    QtCore.QPoint(0, 12),
                                                    QtCore.QPoint(0, 24)]))
            elif CD[7] == 15:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(0, 24)]))

        elif CD[2] & 0x20: # Solid-on-bottom
            painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 24),
                                                QtCore.QPoint(24, 24),
                                                QtCore.QPoint(24, 18),
                                                QtCore.QPoint(0, 18)]))

            painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(15, 0),
                                                QtCore.QPoint(15, 12),
                                                QtCore.QPoint(18, 12),
                                                QtCore.QPoint(12, 17),
                                                QtCore.QPoint(6, 12),
                                                QtCore.QPoint(9, 12),
                                                QtCore.QPoint(9, 0)]))

        elif CD[2] & 0x80: # Solid-on-top
            painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                QtCore.QPoint(24, 0),
                                                QtCore.QPoint(24, 6),
                                                QtCore.QPoint(0, 6)]))

            painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(15, 24),
                                                QtCore.QPoint(15, 12),
                                                QtCore.QPoint(18, 12),
                                                QtCore.QPoint(12, 7),
                                                QtCore.QPoint(6, 12),
                                                QtCore.QPoint(9, 12),
                                                QtCore.QPoint(9, 24)]))

        elif CD[2] & 16: # Spikes
            if CD[7] == 0:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(0, 6)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(24, 12),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(0, 18)]))
            if CD[7] == 1:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(0, 12),
                                                    QtCore.QPoint(24, 6)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 12),
                                                    QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(24, 18)]))
            if CD[7] == 2:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 24),
                                                    QtCore.QPoint(12, 24),
                                                    QtCore.QPoint(6, 0)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(12, 24),
                                                    QtCore.QPoint(24, 24),
                                                    QtCore.QPoint(18, 0)]))
            if CD[7] == 3:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(12, 0),
                                                    QtCore.QPoint(6, 24)]))
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(12, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(18, 24)]))
            if CD[7] == 4:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(18, 24),
                                                    QtCore.QPoint(6, 24)]))
            if CD[7] == 5:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(6, 0),
                                                    QtCore.QPoint(18, 0),
                                                    QtCore.QPoint(12, 24)]))
            if CD[7] == 6:
                painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(0, 0),
                                                    QtCore.QPoint(24, 0),
                                                    QtCore.QPoint(12, 24)]))

##        elif CD[3] & 4: # QBlock
##            if CD[7] == 0:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'QBlock/FireF.png'))
##            if CD[7] == 1:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'QBlock/Star.png'))
##            if CD[7] == 2:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'QBlock/Coin.png'))
##            if CD[7] == 3:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'QBlock/Vine.png'))
##            if CD[7] == 4:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'QBlock/1up.png'))
##            if CD[7] == 5:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'QBlock/Mini.png'))
##            if CD[7] == 6:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'QBlock/Prop.png'))
##            if CD[7] == 7:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'QBlock/Peng.png'))
##            if CD[7] == 8:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'QBlock/IceF.png'))
##
##        elif CD[3] & 2: # Coin
##            if CD[7] == 0:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'Coin/Coin.png'))
##            if CD[7] == 4:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'Coin/POW.png'))
##
##        elif CD[3] & 8: # Exploder
##            if CD[7] == 1:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'Explode/Stone.png'))
##            if CD[7] == 2:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'Explode/Wood.png'))
##            if CD[7] == 3:
##                painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'Explode/Red.png'))
##
##        elif CD[1] & 2: # Falling
##            painter.drawPixmap(option.rect, QtGui.QPixmap(path + 'Prop/Fall.png'))

#                elif CD[5] == 4 or 5: # Conveyor
#                    d

        elif (CD[3] & 1) or (CD[3] in (5, 0x10)) or (CD[3] & 4) or (CD[3] & 8): # Solid, question or brick
            painter.drawRect(0, 0, 24, 24)

        else: # No fill
            pass

        self.collOverlay = collPix


    def addOverlay(self, overlayTile):
        """
        Adds a 3D overlay tile
        """
        if overlayTile is not None:
            overlayPix = overlayTile.main

            # Create a depth map
            self.depthMap = QtGui.QPixmap(24, 24)
            self.depthMap.fill(theme.color('depth_highlight'))
            p2 = QtGui.QPainter(self.depthMap)
            p2.setCompositionMode(p2.CompositionMode_DestinationIn)
            p2.drawPixmap(0, 0, overlayPix)
            p2.end; del p2

            # Known bug: if the depth_highlight color is
            # fully opaque, things can get messed up.

            # Overlay the overlay tile onto self.main
            p1 = QtGui.QPainter(self.main)
            p1.drawPixmap(0, 0, overlayPix)
            p1.end; del p1


def RenderObject(tileset, objnum, width, height, fullslope=False):
    """
    Render a tileset object into an array
    """
    # allocate an array
    dest = []
    for i in range(height): dest.append([0]*width)

    # ignore non-existent objects
    try:
        tileset_defs = ObjectDefinitions[tileset]
    except IndexError:
        tileset_defs = None
    if tileset_defs is None: return dest
    try:
        obj = tileset_defs[objnum]
    except IndexError:
        obj = None
    if obj is None: return dest
    if len(obj.rows) == 0: return dest

    # diagonal objects are rendered differently
    if (obj.rows[0][0][0] & 0x80) != 0:
        RenderDiagonalObject(dest, obj, width, height, fullslope)
    else:
        # standard object
        repeatFound = False
        beforeRepeat = []
        inRepeat = []
        afterRepeat = []

        for row in obj.rows:
            if len(row) == 0: continue
            # row[0][0] is 0, 1, 2, 4
            if (row[0][0] & 2) != 0 or (row[0][0] & 4) != 0:
                repeatFound = True
                inRepeat.append(row)
            else:
                if repeatFound:
                    afterRepeat.append(row)
                else:
                    beforeRepeat.append(row)

        bc = len(beforeRepeat); ic = len(inRepeat); ac = len(afterRepeat)
        if ic == 0:
            for y in range(height):
                RenderStandardRow(dest[y], beforeRepeat[y % bc], y, width)
        else:
            afterthreshold = height - ac - 1
            for y in range(height):
                if y < bc:
                    RenderStandardRow(dest[y], beforeRepeat[y], y, width)
                elif y > afterthreshold:
                    RenderStandardRow(dest[y], afterRepeat[y - height + ac], y, width)
                else:
                    RenderStandardRow(dest[y], inRepeat[(y - bc) % ic], y, width)

    return dest


def RenderStandardRow(dest, row, y, width):
    """
    Render a row from an object
    """
    repeatFound = False
    beforeRepeat = []
    inRepeat = []
    afterRepeat = []

    for tile in row:
        # NSMB2 introduces two (?) new ways to define horizontal tiling, IN ADDITION TO the original one
        tiling = False
        tiling = tiling or ((tile[2] & 1) != 0 and (tile[0] & 1) != 0) # NSMBW-style (still applies to NSMB2)
        tiling = tiling or ((row[0][0] & 4) != 0 and (tile[0] & 4) == 0) # NSMB2-style (J_Kihon BG rocks)
        tiling = tiling or ((tile[0] & 1) != 0) # NSMB2-style (horizontal pipes)

        if tiling:
            repeatFound = True
            inRepeat.append(tile)
        else:
            if repeatFound:
                afterRepeat.append(tile)
            else:
                beforeRepeat.append(tile)

    bc = len(beforeRepeat); ic = len(inRepeat); ac = len(afterRepeat)
    if ic == 0:
        for x in range(width):
            dest[x] = beforeRepeat[x % bc][1]
    else:
        afterthreshold = width - ac - 1
        for x in range(width):
            if x < bc:
                dest[x] = beforeRepeat[x][1]
            elif x > afterthreshold:
                dest[x] = afterRepeat[x - width + ac][1]
            else:
                dest[x] = inRepeat[(x - bc) % ic][1]


def RenderDiagonalObject(dest, obj, width, height, fullslope):
    """
    Render a diagonal object
    """
    # set all to empty tiles
    for row in dest:
        for x in range(width):
            row[x] = -1

    # get sections
    mainBlock,subBlock = GetSlopeSections(obj)
    cbyte = obj.rows[0][0][0]

    # get direction
    goLeft = ((cbyte & 1) != 0)
    goDown = ((cbyte & 2) != 0)

    # base the amount to draw by seeing how much we can fit in each direction
    if fullslope:
        drawAmount = max(height // len(mainBlock), width // len(mainBlock[0]))
    else:
        drawAmount = min(height // len(mainBlock), width // len(mainBlock[0]))

    # if it's not goingLeft and not goingDown:
    if not goLeft and not goDown:
        # slope going from SW => NE
        # start off at the bottom left
        x = 0
        y = height - len(mainBlock) - (0 if subBlock is None else len(subBlock))
        xi = len(mainBlock[0])
        yi = -len(mainBlock)

    # ... and if it's goingLeft and not goingDown:
    elif goLeft and not goDown:
        # slope going from SE => NW
        # start off at the top left
        x = 0
        y = 0
        xi = len(mainBlock[0])
        yi = len(mainBlock)

    # ... and if it's not goingLeft but it's goingDown:
    elif not goLeft and goDown:
        # slope going from NW => SE
        # start off at the top left
        x = 0
        y = (0 if subBlock is None else len(subBlock))
        xi = len(mainBlock[0])
        yi = len(mainBlock)

    # ... and finally, if it's goingLeft and goingDown:
    else:
        # slope going from SW => NE
        # start off at the bottom left
        x = 0
        y = height - len(mainBlock)
        xi = len(mainBlock[0])
        yi = -len(mainBlock)


    # finally draw it
    for i in range(drawAmount):
        PutObjectArray(dest, x, y, mainBlock, width, height)
        if subBlock is not None:
            xb = x
            if goLeft: xb = x + len(mainBlock[0]) - len(subBlock[0])
            if goDown:
                PutObjectArray(dest, xb, y - len(subBlock), subBlock, width, height)
            else:
                PutObjectArray(dest, xb, y + len(mainBlock), subBlock, width, height)
        x += xi
        y += yi


def PutObjectArray(dest, xo, yo, block, width, height):
    """
    Places a tile array into an object
    """
    #for y in range(yo,min(yo+len(block),height)):
    for y in range(yo,yo+len(block)):
        if y < 0: continue
        if y >= height: continue
        drow = dest[y]
        srow = block[y-yo]
        #for x in range(xo,min(xo+len(srow),width)):
        for x in range(xo,xo+len(srow)):
            if x < 0: continue
            if x >= width: continue
            drow[x] = srow[x-xo][1]


def GetSlopeSections(obj):
    """
    Sorts the slope data into sections
    """
    sections = []
    currentSection = None

    for row in obj.rows:
        if len(row) > 0 and (row[0][0] & 0x80) != 0: # begin new section
            if currentSection is not None:
                sections.append(CreateSection(currentSection))
            currentSection = []
        currentSection.append(row)

    if currentSection is not None: # end last section
        sections.append(CreateSection(currentSection))

    if len(sections) == 1:
        return (sections[0],None)
    else:
        return (sections[0],sections[1])


def CreateSection(rows):
    """
    Create a slope section
    """
    # calculate width
    width = 0
    for row in rows:
        thiswidth = CountTiles(row)
        if width < thiswidth: width = thiswidth

    # create the section
    section = []
    for row in rows:
        drow = [0] * width
        x = 0
        for tile in row:
            if (tile[0] & 0x80) == 0:
                drow[x] = tile
                x += 1
        section.append(drow)

    return section


def CountTiles(row):
    """
    Counts the amount of real tiles in an object row
    """
    res = 0
    for tile in row:
        if (tile[0] & 0x80) == 0:
            res += 1
    return res


def CreateTilesets():
    """
    Blank out the tileset arrays
    """
    global Tiles, TilesetFilesLoaded, TilesetAnimTimer, TileBehaviours, ObjectDefinitions

    Tiles = [None]*0x200*4
    Tiles += Overrides
    TilesetFilesLoaded = [None, None, None, None]
    #TileBehaviours = [0]*1024
    TilesetAnimTimer = QtCore.QTimer()
    TilesetAnimTimer.timeout.connect(IncrementTilesetFrame)
    TilesetAnimTimer.start(180)
    ObjectDefinitions = [None]*4
    SLib.Tiles = Tiles


def LoadTileset(idx, name, reload=False):
    try:
        return _LoadTileset(idx, name, reload)
    except Exception:
        QtWidgets.QMessageBox.warning(None, trans.string('Err_CorruptedTileset', 0), trans.string('Err_CorruptedTileset', 1, '[file]', name))
        return False


def _LoadTileset(idx, name, reload=False):
    """
    Load in a tileset into a specific slot
    """

    # find the tileset path
    global arcname
    TilesetPaths = reversed(gamedef.GetGamePaths())

    found = False
    for path in TilesetPaths:
        if path is None: break

        arcname = path + '/Unit/' + name + '.sarc'
        compressed = False
        if os.path.isfile(arcname):
            found = True
            break
        arcname += '.lh'
        compressed = True
        if os.path.isfile(arcname):
            found = True
            break

    # warning if not found
    if not found:
        QtWidgets.QMessageBox.warning(None, trans.string('Err_MissingTileset', 0), trans.string('Err_MissingTileset', 1, '[file]', name))
        return False

    # if this file's already loaded, return
    if TilesetFilesLoaded[idx] == arcname and not reload: return

    # get the data
    with open(arcname, 'rb') as fileobj:
        arcdata = fileobj.read()
    if compressed:
        arcdata = LHTool.decompressLH(arcdata)
    arc = SarcLib.SARC_Archive()
    arc.load(arcdata)

    tileoffset = idx * 0x200

    global Tiles, TilesetCache
    if name not in TilesetCache:
        # Load the tiles

        # decompress the textures
        try:
            comptiledata = arc['BG_tex/%s.ctpk' % name].data
            colldata = arc['BG_chk/d_bgchk_%s.bin' % name].data
        except KeyError:
            QtWidgets.QMessageBox.warning(None, trans.string('Err_CorruptedTilesetData', 0), trans.string('Err_CorruptedTilesetData', 1, '[file]', name))
            return False

        # load in the textures
        img = LoadTexture(comptiledata)

        # Divide it into individual tiles and
        # add collisions at the same time
        def getTileFromImage(tilemap, xtilenum, ytilenum):
            return dest.copy((xtilenum * 24) + 2, (ytilenum * 24) + 2, 20, 20).scaledToWidth(24, Qt.SmoothTransformation)
        dest = QtGui.QPixmap.fromImage(img)
        sourcex = 0
        sourcey = 0
        for i in range(tileoffset, tileoffset + 441):
            T = TilesetTile(getTileFromImage(dest, sourcex, sourcey))
            Tiles[i] = T
            sourcex += 1
            if sourcex >= 21:
                sourcex = 0
                sourcey += 1

        # Add overlays
        overlayfile = arc['BG_unt/%s_add.bin' % name].data
        overlayArray = struct.unpack('<441H', overlayfile[:882])
        i = idx * 0x200
        arrayi = 0
        for y in range(21):
            for x in range(21):
                if Tiles[i] is not None:
                    Tiles[i].addOverlay(Tiles[overlayArray[arrayi]])
                i += 1; arrayi += 1

        # Load the tileset animations, if there are any
        #isAnimated, prefix = CheckTilesetAnimated(arc)
        isAnimated = False
        if isAnimated:
            row = 0
            col = 0
            for i in range(tileoffset,tileoffset+441):
                filenames = []
                filenames.append('%s_%d%s%s.bin' % (prefix, idx, hex(row)[2].lower(), hex(col)[2].lower()))
                filenames.append('%s_%d%s%s.bin' % (prefix, idx, hex(row)[2].upper(), hex(col)[2].upper()))
                if filenames[0] == filenames[1]:
                    item = filenames[0]
                    filenames = []
                    filenames.append(item)
                for fn in filenames:
                    fn = 'BG_tex/' + fn
                    found = False
                    try:
                        arc[fn]
                        found = True
                    except KeyError:
                        pass
                    if found:
                        Tiles[i].addAnimationData(arc[fn])
                col += 1
                if col == 16:
                    col = 0
                    row += 1

    else:
        # We already have tiles in the tileset cache; copy them over to Tiles
        for i in range(0x200):
            Tiles[i + tileoffset] = TilesetCache[name][i]


    # load the object definitions
    defs = [None] * 256

    indexfile = arc['BG_unt/%s_hd.bin' % name].data
    deffile = arc['BG_unt/%s.bin' % name].data
    objcount = len(indexfile) // 6
    indexstruct = struct.Struct('<HBBH')

    for i in range(objcount):
        data = indexstruct.unpack_from(indexfile, i * 6)
        obj = ObjectDef()
        obj.width = data[1]
        obj.height = data[2]
        obj.load(deffile, data[0], tileoffset)
        defs[i] = obj

    ObjectDefinitions[idx] = defs

    ProcessOverrides(idx, name)

    # Keep track of this filepath
    TilesetFilesLoaded[idx] = arcname

    # Add Tiles to spritelib
    SLib.Tiles = Tiles

    # Add Tiles to the cache
    TilesetCache[name] = []
    for i in range(0x200):
        TilesetCache[name].append(Tiles[i + tileoffset])


def LoadTexture(tiledata):
    with open('texturipper/texture.ctpk', 'wb') as binfile:
        binfile.write(tiledata)

    if AutoOpenScriptEnabled: return QtGui.QImage(512, 512, QtGui.QImage.Format_ARGB32)

    with subprocess.Popen('texturipper/texturipper_1.2.exe texture.ctpk', cwd='texturipper') as proc:
        pass

    pngname = None
    for filename in os.listdir('texturipper'):
        if filename.endswith('.png'):
            pngname = filename
    if not pngname: raise Exception

    with open(os.path.join('texturipper', pngname), 'rb') as pngfile:
        img = QtGui.QImage(os.path.join('texturipper', pngname))

    for filename in os.listdir('texturipper'):
        if filename == 'texturipper_1.2.exe': continue
        os.remove(os.path.join('texturipper', filename))

    return img


def IncrementTilesetFrame():
    """
    Moves each tileset to the next frame
    """
    if not TilesetsAnimating: return
    for tile in Tiles:
        if tile is not None: tile.nextFrame()
    mainWindow.scene.update()
    mainWindow.objPicker.update()


def CheckTilesetAnimated(tileset):
    """Checks if a tileset contains Newer-style animations, and if so, returns
    (True, prefix) where prefix is the animation prefix. If not, (False, None).
    tileset should be a Wii.py U8 object."""
    # Find the animation files, if any
    excludes = (
        'block_anime.bin',
        'hatena_anime.bin',
        'tuka_coin_anime.bin',
        )
    texFiles = tileset['BG_tex']
    animFiles = []
    for f in texFiles:
        # Determine if it's likely an animation file
        if f.lower() in excludes: continue
        if f[-4:].lower() != '.bin': continue
        namelen = len(f)
        if namelen == 9:
            if f[1] != '_': continue
            if f[2] not in '0123': continue
            if f[3].lower() not in '0123456789abcdef': continue
            if f[4].lower() not in '0123456789abcdef': continue
        elif namelen == 10:
            if f[2] != '_': continue
            if f[3] not in '0123': continue
            if f[4].lower() not in '0123456789abcdef': continue
            if f[5].lower() not in '0123456789abcdef': continue
        animFiles.append(f)

    # Quit if there's no animation
    if len(animFiles) == 0: return False, None
    else:
        # This makes so many assumptions
        fn = animFiles[0]
        prefix = fn[0] if len(fn) == 9 else fn[:2]
        return True, prefix



def UnloadTileset(idx):
    """
    Unload the tileset from a specific slot
    """
    for i in range(idx * 0x200, idx * 0x200 + 0x200):
        Tiles[i] = None

    ObjectDefinitions[idx] = None
    TilesetFilesLoaded[idx] = None


def ProcessOverrides(idx, name):
    """
    Load overridden tiles if there are any
    """

    try:
        tsindexes = ['J_Kihon', 'J_Chika', 'J_Setsugen', 'J_Yougan', 'J_Gold', 'J_Suichu']
        if name in tsindexes:
            offset = (0x200 * 4) + (tsindexes.index(name) * 64)
            # Setsugen/Snow is unused for some reason? but we still override it

            defs = ObjectDefinitions[idx]
            t = Tiles

            # Invisible blocks
            # these are all the same so let's just load them from the first row
            replace = 0x200 * 4
            for i in [3, 4, 5, 6, 7, 8, 9, 10]:
                t[i].main = t[replace].main
                replace += 1

            # Question and brick blocks
            # these don't have their own tiles so we have to do them by objects
            replace = offset + 9
            for i in range(30, 41):
                defs[i].rows[0][0] = (0, replace, 0)
                replace += 1
            for i in range(16, 30):
                defs[i].rows[0][0] = (0, replace, 0)
                replace += 1

            # now the extra stuff (invisible collisions etc)
            replace = 0x200 * 4 + 64 * 4
            for i in [0, 1, 11, 14, 2, 13, 12]:
                t[i].main = t[replace].main
                replace += 1
            replace = 0x200 * 4 + 64 * 5
            for i in [190, 191, 192]:
                t[i].main = t[replace].main
                replace += 1
            # t[1].main = t[1280].main # solid
            # t[2].main = t[1311].main # vine stopper
            # t[11].main = t[1310].main # jumpthrough platform
            # t[12].main = t[1309].main # 16x8 roof platform

            # t[16].main = t[1291].main # 1x1 slope going up
            # t[17].main = t[1292].main # 1x1 slope going down
            # t[18].main = t[1281].main # 2x1 slope going up (part 1)
            # t[19].main = t[1282].main # 2x1 slope going up (part 2)
            # t[20].main = t[1283].main # 2x1 slope going down (part 1)
            # t[21].main = t[1284].main # 2x1 slope going down (part 2)
            # t[22].main = t[1301].main # 4x1 slope going up (part 1)
            # t[23].main = t[1302].main # 4x1 slope going up (part 2)
            # t[24].main = t[1303].main # 4x1 slope going up (part 3)
            # t[25].main = t[1304].main # 4x1 slope going up (part 4)
            # t[26].main = t[1305].main # 4x1 slope going down (part 1)
            # t[27].main = t[1306].main # 4x1 slope going down (part 2)
            # t[28].main = t[1307].main # 4x1 slope going down (part 3)
            # t[29].main = t[1308].main # 4x1 slope going down (part 4)
            # t[30].main = t[1062].main # coin

            # t[32].main = t[1289].main # 1x1 roof going down
            # t[33].main = t[1290].main # 1x1 roof going up
            # t[34].main = t[1285].main # 2x1 roof going down (part 1)
            # t[35].main = t[1286].main # 2x1 roof going down (part 2)
            # t[36].main = t[1287].main # 2x1 roof going up (part 1)
            # t[37].main = t[1288].main # 2x1 roof going up (part 2)
            # t[38].main = t[1293].main # 4x1 roof going down (part 1)
            # t[39].main = t[1294].main # 4x1 roof going down (part 2)
            # t[40].main = t[1295].main # 4x1 roof going down (part 3)
            # t[41].main = t[1296].main # 4x1 roof going down (part 4)
            # t[42].main = t[1297].main # 4x1 roof going up (part 1)
            # t[43].main = t[1298].main # 4x1 roof going up (part 2)
            # t[44].main = t[1299].main # 4x1 roof going up (part 3)
            # t[45].main = t[1300].main # 4x1 roof going up (part 4)
            # t[46].main = t[1312].main # P-switch coins

            # t[53].main = t[1314].main # donut lift
            # t[61].main = t[1063].main # multiplayer coin
            # t[63].main = t[1313].main # instant death tile

        elif name == 'Pa1_nohara' or name == 'Pa1_nohara2' or name == 'Pa1_daishizen':
            # flowers
            t = Tiles
            t[416].main = t[1092].main # grass
            t[417].main = t[1093].main
            t[418].main = t[1094].main
            t[419].main = t[1095].main
            t[420].main = t[1096].main

            if name == 'Pa1_nohara' or name == 'Pa1_nohara2':
                t[432].main = t[1068].main # flowers
                t[433].main = t[1069].main # flowers
                t[434].main = t[1070].main # flowers

                t[448].main = t[1158].main # flowers on grass
                t[449].main = t[1159].main
                t[450].main = t[1160].main
            elif name == 'Pa1_daishizen':
                # forest flowers
                t[432].main = t[1071].main # flowers
                t[433].main = t[1072].main # flowers
                t[434].main = t[1073].main # flowers

                t[448].main = t[1222].main # flowers on grass
                t[449].main = t[1223].main
                t[450].main = t[1224].main

        elif name == 'Pa3_rail' or name == 'Pa3_rail_white' or name == 'Pa3_daishizen':
            # These are the line guides
            # Pa3_daishizen has less though

            t = Tiles

            t[768].main = t[1088].main # horizontal line
            t[769].main = t[1089].main # vertical line
            t[770].main = t[1090].main # bottomright corner
            t[771].main = t[1091].main # topleft corner

            t[784].main = t[1152].main # left red blob (part 1)
            t[785].main = t[1153].main # top red blob (part 1)
            t[786].main = t[1154].main # top red blob (part 2)
            t[787].main = t[1155].main # right red blob (part 1)
            t[788].main = t[1156].main # topleft red blob
            t[789].main = t[1157].main # topright red blob

            t[800].main = t[1216].main # left red blob (part 2)
            t[801].main = t[1217].main # bottom red blob (part 1)
            t[802].main = t[1218].main # bottom red blob (part 2)
            t[803].main = t[1219].main # right red blob (part 2)
            t[804].main = t[1220].main # bottomleft red blob
            t[805].main = t[1221].main # bottomright red blob

            # Those are all for Pa3_daishizen
            if name == 'Pa3_daishizen': return

            t[816].main = t[1056].main # 1x2 diagonal going up (top edge)
            t[817].main = t[1057].main # 1x2 diagonal going down (top edge)

            t[832].main = t[1120].main # 1x2 diagonal going up (part 1)
            t[833].main = t[1121].main # 1x2 diagonal going down (part 1)
            t[834].main = t[1186].main # 1x1 diagonal going up
            t[835].main = t[1187].main # 1x1 diagonal going down
            t[836].main = t[1058].main # 2x1 diagonal going up (part 1)
            t[837].main = t[1059].main # 2x1 diagonal going up (part 2)
            t[838].main = t[1060].main # 2x1 diagonal going down (part 1)
            t[839].main = t[1061].main # 2x1 diagonal going down (part 2)

            t[848].main = t[1184].main # 1x2 diagonal going up (part 2)
            t[849].main = t[1185].main # 1x2 diagonal going down (part 2)
            t[850].main = t[1250].main # 1x1 diagonal going up
            t[851].main = t[1251].main # 1x1 diagonal going down
            t[852].main = t[1122].main # 2x1 diagonal going up (part 1)
            t[853].main = t[1123].main # 2x1 diagonal going up (part 2)
            t[854].main = t[1124].main # 2x1 diagonal going down (part 1)
            t[855].main = t[1125].main # 2x1 diagonal going down (part 2)

            t[866].main = t[1065].main # big circle piece 1st row
            t[867].main = t[1066].main # big circle piece 1st row
            t[870].main = t[1189].main # medium circle piece 1st row
            t[871].main = t[1190].main # medium circle piece 1st row

            t[881].main = t[1128].main # big circle piece 2nd row
            t[882].main = t[1129].main # big circle piece 2nd row
            t[883].main = t[1130].main # big circle piece 2nd row
            t[884].main = t[1131].main # big circle piece 2nd row
            t[885].main = t[1252].main # medium circle piece 2nd row
            t[886].main = t[1253].main # medium circle piece 2nd row
            t[887].main = t[1254].main # medium circle piece 2nd row
            t[888].main = t[1188].main # small circle

            t[896].main = t[1191].main # big circle piece 3rd row
            t[897].main = t[1192].main # big circle piece 3rd row
            t[900].main = t[1195].main # big circle piece 3rd row
            t[901].main = t[1316].main # medium circle piece 3rd row
            t[902].main = t[1317].main # medium circle piece 3rd row
            t[903].main = t[1318].main # medium circle piece 3rd row

            t[912].main = t[1255].main # big circle piece 4th row
            t[913].main = t[1256].main # big circle piece 4th row
            t[916].main = t[1259].main # big circle piece 4th row

            t[929].main = t[1320].main # big circle piece 5th row
            t[930].main = t[1321].main # big circle piece 5th row
            t[931].main = t[1322].main # big circle piece 5th row
            t[932].main = t[1323].main # big circle piece 5th row

        elif name == 'Pa3_MG_house_ami_rail':
            t = Tiles

            t[832].main = t[1088].main # horizontal line
            t[833].main = t[1090].main # bottomright corner
            t[834].main = t[1088].main # horizontal line

            t[848].main = t[1089].main # vertical line
            t[849].main = t[1089].main # vertical line
            t[850].main = t[1091].main # topleft corner

            t[835].main = t[1152].main # left red blob (part 1)
            t[836].main = t[1153].main # top red blob (part 1)
            t[837].main = t[1154].main # top red blob (part 2)
            t[838].main = t[1155].main # right red blob (part 1)

            t[851].main = t[1216].main # left red blob (part 2)
            t[852].main = t[1217].main # bottom red blob (part 1)
            t[853].main = t[1218].main # bottom red blob (part 2)
            t[854].main = t[1219].main # right red blob (part 2)

            t[866].main = t[1065].main # big circle piece 1st row
            t[867].main = t[1066].main # big circle piece 1st row
            t[870].main = t[1189].main # medium circle piece 1st row
            t[871].main = t[1190].main # medium circle piece 1st row

            t[881].main = t[1128].main # big circle piece 2nd row
            t[882].main = t[1129].main # big circle piece 2nd row
            t[883].main = t[1130].main # big circle piece 2nd row
            t[884].main = t[1131].main # big circle piece 2nd row
            t[885].main = t[1252].main # medium circle piece 2nd row
            t[886].main = t[1253].main # medium circle piece 2nd row
            t[887].main = t[1254].main # medium circle piece 2nd row

            t[896].main = t[1191].main # big circle piece 3rd row
            t[897].main = t[1192].main # big circle piece 3rd row
            t[900].main = t[1195].main # big circle piece 3rd row
            t[901].main = t[1316].main # medium circle piece 3rd row
            t[902].main = t[1317].main # medium circle piece 3rd row
            t[903].main = t[1318].main # medium circle piece 3rd row

            t[912].main = t[1255].main # big circle piece 4th row
            t[913].main = t[1256].main # big circle piece 4th row
            t[916].main = t[1259].main # big circle piece 4th row

            t[929].main = t[1320].main # big circle piece 5th row
            t[930].main = t[1321].main # big circle piece 5th row
            t[931].main = t[1322].main # big circle piece 5th row
            t[932].main = t[1323].main # big circle piece 5th row
    except Exception:
        # Fail silently
        pass


def LoadOverrides():
    """
    Load overrides
    """
    global Overrides

    OverrideBitmap = QtGui.QPixmap('reggiedata/overrides.png')
    Overrides = [None]*384
    idx = 0
    xcount = OverrideBitmap.width() // 24
    ycount = OverrideBitmap.height() // 24
    sourcex = 0
    sourcey = 0

    for y in range(ycount):
        for x in range(xcount):
            bmp = OverrideBitmap.copy(sourcex, sourcey, 24, 24)
            Overrides[idx] = TilesetTile(bmp)

            # Set collisions if it's a brick or question
            if y <= 4:
                if 8 < x < 20: Overrides[idx].setQuestionCollisions()
                elif 20 <= x < 32: Overrides[idx].setBrickCollisions()

            idx += 1
            sourcex += 24
        sourcex = 0
        sourcey += 24
        if idx % 64 != 0:
            idx -= (idx % 64)
            idx += 64


def SetAppStyle():
    """
    Set the application window color
    """
    global app
    global theme

    # Change the color if applicable
    #if theme.color('ui') is not None: app.setPalette(QtGui.QPalette(theme.color('ui')))

    # Change the style
    styleKey = setting('uiStyle')
    style = QtWidgets.QStyleFactory.create(styleKey)
    app.setStyle(style)


Area = None
Dirty = False
DirtyOverride = 0
AutoSaveDirty = False
OverrideSnapping = False
CurrentPaintType = -1
CurrentObject = -1
CurrentSprite = -1
CurrentLayer = 1
Layer0Shown = True
Layer1Shown = True
Layer2Shown = True
SpritesShown = True
SpriteImagesShown = True
RealViewEnabled = False
LocationsShown = True
CommentsShown = True
ObjectsFrozen = False
SpritesFrozen = False
EntrancesFrozen = False
LocationsFrozen = False
PathsFrozen = False
ProgressPathsFrozen = False
CommentsFrozen = False
PaintingEntrance = None
PaintingEntranceListIndex = None
NumberFont = None
GridType = None
RestoredFromAutoSave = False
AutoSavePath = ''
AutoSaveData = b''
AutoOpenScriptEnabled = False
CurrentLevelNameForAutoOpenScript = None

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
    global NumberFont
    if NumberFont is not None: return

    # this is a really crappy method, but I can't think of any other way
    # normal Qt defines Q_WS_WIN and Q_WS_MAC but we don't have that here
    s = QtCore.QSysInfo()
    if hasattr(s, 'WindowsVersion'):
        NumberFont = QtGui.QFont('Tahoma', 7)
    elif hasattr(s, 'MacintoshVersion'):
        NumberFont = QtGui.QFont('Lucida Grande', 9)
    else:
        NumberFont = QtGui.QFont('Sans', 8)

def SetDirty(noautosave=False):
    global Dirty, DirtyOverride, AutoSaveDirty
    if DirtyOverride > 0: return

    if not noautosave: AutoSaveDirty = True
    if Dirty: return

    Dirty = True
    try:
        mainWindow.UpdateTitle()
    except Exception:
        pass


def MapPositionToZoneID(zones, x, y, useid=False):
    """
    Returns the zone ID containing or nearest the specified position
    """
    id = 0
    minimumdist = -1
    rval = -1

    for zone in zones:
        r = zone.ZoneRect
        if   r.contains(x,y) and     useid: return zone.id
        elif r.contains(x,y) and not useid: return id

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



class Metadata():
    """
    Class for the new level metadata system
    """
    # This new system is much more useful and flexible than the old
    # system, but is incompatible with older versions of Reggie.
    # They will fail to understand the data, and skip it like it
    # doesn't exist. The new system is written with forward-compatibility
    # in mind. Thus, when newer versions of Reggie are created
    # with new metadata values, they will be easily able to add to
    # the existing ones. In addition, the metadata system is lossless,
    # so unrecognized values will be preserved when you open and save.

    # Type values:
    # 0 = binary
    # 1 = string
    # 2+ = undefined as of now - future Reggies can use them
    # Theoretical limit to type values is 4,294,967,296

    def __init__(self, data=None):
        """
        Creates a metadata object with the data given
        """
        self.DataDict = {}
        if data is None: return

        if data[0:4] != b'MD2_':
            # This is old-style metadata - convert it
            try:
                strdata = ''
                for d in data: strdata += chr(d)
                level_info = pickle.loads(strdata)
                for k, v in level_info.iteritems():
                    self.setStrData(k, v)
            except Exception: pass
            if ('Website' not in self.DataDict) and ('Webpage' in self.DataDict):
                self.DataDict['Website'] = self.DataDict['Webpage']
            return

        # Iterate through the data
        idx = 4
        while idx < len(data) - 4:

            # Read the next (first) four bytes - the key length
            rawKeyLen = data[idx:idx+4]
            idx += 4

            keyLen = (rawKeyLen[0] << 24) | (rawKeyLen[1] << 16) | (rawKeyLen[2] << 8) | rawKeyLen[3]

            # Read the next (key length) bytes - the key (as a str)
            rawKey = data[idx:idx+keyLen]
            idx += keyLen

            key = ''
            for b in rawKey: key += chr(b)

            # Read the next four bytes - the number of type entries
            rawTypeEntries = data[idx:idx+4]
            idx += 4

            typeEntries = (rawTypeEntries[0] << 24) | (rawTypeEntries[1] << 16) | (rawTypeEntries[2] << 8) | rawTypeEntries[3]

            # Iterate through each type entry
            typeData = {}
            for entry in range(typeEntries):

                # Read the next four bytes - the type
                rawType = data[idx:idx+4]
                idx += 4

                type = (rawType[0] << 24) | (rawType[1] << 16) | (rawType[2] << 8) | rawType[3]

                # Read the next four bytes - the data length
                rawDataLen = data[idx:idx+4]
                idx += 4

                dataLen = (rawDataLen[0] << 24) | (rawDataLen[1] << 16) | (rawDataLen[2] << 8) | rawDataLen[3]

                # Read the next (data length) bytes - the data (as bytes)
                entryData = data[idx:idx+dataLen]
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

        return data


class AbstractLevel():
    """
    Class for an abstract level from any game. Defines the API.
    """
    def __init__(self):
        """
        Initializes the level with default settings
        """
        self.filepath = None
        self.name = 'untitled'

        self.areas = []

    def load(self, data, areaNum, progress=None):
        """
        Loads a level from bytes data. You MUST reimplement this in subclasses!
        """
        pass

    def save(self):
        """
        Returns the level as a bytes object. You MUST reimplement this in subclasses!
        """
        return b''

    def addArea(self):
        """
        Adds an area to the level, and returns it.
        """
        new = AbstractArea()
        self.areas.append(new)

        return new

    def deleteArea(self, number):
        """
        Removes the area specified. Number is a 1-based value, not 0-based;
        so you would pass a 1 if you wanted to delete the first area.
        """
        del self.areas[number - 1]
        return True


class Level_NSMB2(AbstractLevel):
    """
    Class for a level from New Super Mario Bros. 2
    """
    def __init__(self):
        """
        Initializes the level with default settings
        """
        super().__init__()
        self.areas.append(Area_NSMB2())

    def load(self, data, areaNum, progress=None):
        """
        Loads a NSMB2 level from bytes data.
        """
        super().load(data, areaNum, progress)

        global Area

        arc = SarcLib.SARC_Archive()
        arc.load(data)

        try:
            courseFolder = arc['course']
        except:
            return False

        # Sort the area data
        areaData = {}
        for file in courseFolder.contents:
            name, val = file.name, file.data

            if val is None: continue

            if not name.startswith('course'): continue
            if not name.endswith('.bin'): continue
            if '_bgdatL' in name:
                # It's a layer file
                if len(name) != 19: continue
                try:
                    thisArea = int(name[6])
                    laynum = int(name[14])
                except ValueError: continue
                if not (0 < thisArea < 5): continue

                if thisArea not in areaData: areaData[thisArea] = [None] * 4
                areaData[thisArea][laynum + 1] = val
            else:
                # It's the course file
                if len(name) != 11: continue
                try:
                    thisArea = int(name[6])
                except ValueError: continue
                if not (0 < thisArea < 5): continue

                if thisArea not in areaData: areaData[thisArea] = [None] * 4
                areaData[thisArea][0] = val

        # Create area objects
        self.areas = []
        thisArea = 1
        while thisArea in areaData:
            course = areaData[thisArea][0]
            L0 = areaData[thisArea][1]
            L1 = areaData[thisArea][2]
            L2 = areaData[thisArea][3]

            if thisArea == areaNum:
                newarea = Area_NSMB2()
                Area = newarea
                SLib.Area = Area
            else:
                newarea = AbstractArea()

            newarea.areanum = thisArea
            newarea.load(course, L0, L1, L2, progress)
            self.areas.append(newarea)

            thisArea += 1

        return True

    def save(self):
        """
        Save the level back to a file
        """

        # Make a new archive
        newArchive = SarcLib.SARC_Archive()

        # Create a folder within the archive
        courseFolder = SarcLib.Folder('course')
        newArchive.addFolder(courseFolder)

        # Go through the areas, save them and add them back to the archive
        for areanum, area in enumerate(self.areas):
            course, L0, L1, L2 = area.save()

            if course is not None:
                courseFolder.addFile(SarcLib.File('course%d.bin' % (areanum + 1), course))
            if L0 is not None:
                courseFolder.addFile(SarcLib.File('course%d_bgdatL0.bin' % (areanum + 1), L0))
            if L1 is not None:
                courseFolder.addFile(SarcLib.File('course%d_bgdatL1.bin' % (areanum + 1), L1))
            if L2 is not None:
                courseFolder.addFile(SarcLib.File('course%d_bgdatL2.bin' % (areanum + 1), L2))

        # return the U8 archive data
        return newArchive.save()


    def addArea(self):
        """
        Adds an area to the level, and returns it.
        """
        new = Area_NSMB2()
        self.areas.append(new)

        return new


class AbstractArea():
    """
    An extremely basic abstract area. Implements the basic function API.
    """
    def __init__(self):
        self.areanum = 1
        self.course = None
        self.L0 = None
        self.L1 = None
        self.L2 = None

    def load(self, course, L0, L1, L2, progress=None):
        self.course = course
        self.L0 = L0
        self.L1 = L1
        self.L2 = L2

    def save(self):
        return (self.course, self.L0, self.L1, self.L2)


class AbstractParsedArea(AbstractArea):
    """
    An area that is parsed to load sprites, entrances, etc. Still abstracted among games.
    Don't instantiate this! It could blow up becuase many of the functions are only defined
    within subclasses. If you want an area object, use a game-specific subclass.
    """
    def __init__(self):
        """
        Creates a completely new area
        """

        # Default area number
        self.areanum = 1

        # Settings
        self.defEvents = 0
        self.wrapFlag = 0
        self.timeLimit = 300
        self.unk1 = 0
        self.startEntrance = 0
        self.unk2 = 0
        self.unk3 = 0

        # Lists of things
        self.entrances = []
        self.sprites = []
        self.zones = []
        self.locations = []
        self.pathdata = []
        self.paths = []
        self.progpathdata = []
        self.progpaths = []
        self.comments = []
        self.layers = [[], [], []]

        # Metadata
        self.LoadReggieInfo(None)

        # Load tilesets
        CreateTilesets()
        LoadTileset(0, self.tileset0)
        LoadTileset(1, self.tileset1)


    def load(self, course, L0, L1, L2, progress=None):
        """
        Loads an area from the archive files
        """

        # Load in the course file and blocks
        self.LoadBlocks(course)

        # Load stuff from individual blocks
        self.LoadTilesetNames() # block 1
        self.LoadOptions() # block 2
        self.LoadEntrances() # block 7
        self.LoadSprites() # block 8
        self.LoadZones() # block 10 (also blocks 3, 5, and 6)
        self.LoadLocations() # block 11
        self.LoadPaths() # block 12 and 13
        self.LoadProgPaths() # block 16 and 17

        # Load the editor metadata
        if self.block1pos[0] != 0x70:
            rdsize = self.block1pos[0] - 0x70
            rddata = course[0x70:self.block1pos[0]]
            self.LoadReggieInfo(rddata)
        else:
            self.LoadReggieInfo(None)
        del self.block1pos

        # Now, load the comments
        self.LoadComments()

        # Load the tilesets
        if progress is not None: progress.setLabelText(trans.string('Splash', 3))
        if app.splashscrn is not None: updateSplash(trans.string('Splash', 3), 0)

        CreateTilesets()
        if progress is not None: progress.setValue(1)
        if app.splashscrn is not None: updateSplash(trans.string('Splash', 3), 1)
        if self.tileset0 != '': LoadTileset(0, self.tileset0)
        if progress is not None: progress.setValue(2)
        if app.splashscrn is not None: updateSplash(trans.string('Splash', 3), 2)
        if self.tileset1 != '': LoadTileset(1, self.tileset1)
        if progress is not None: progress.setValue(3)
        if app.splashscrn is not None: updateSplash(trans.string('Splash', 3), 3)
        if self.tileset2 != '': LoadTileset(2, self.tileset2)
        if progress is not None: progress.setValue(4)
        if app.splashscrn is not None: updateSplash(trans.string('Splash', 3), 4)
        if self.tileset3 != '': LoadTileset(3, self.tileset3)

        # Load the object layers
        if progress is not None:
            progress.setLabelText(trans.string('Splash', 1))
            progress.setValue(5)
        if app.splashscrn is not None:
            updateSplash(trans.string('Splash', 1), 5)

        self.layers = [[], [], []]

        if L0 is not None:
            self.LoadLayer(0, L0)
        if L1 is not None:
            self.LoadLayer(1, L1)
        if L2 is not None:
            self.LoadLayer(2, L2)

        # Delete self.blocks
        #del self.blocks

        return True

    def save(self):
        """
        Save the area back to a file
        """
        # Prepare this first because otherwise the game refuses to load some sprites
        self.SortSpritesByZone()

        # We don't parse blocks 4, 11, 12, 13, 14.
        # We can create the rest manually.
        #self.blocks = [None] * 17
        self.blocks[3] = b'\0\0\0\0\0\0\0\0'
        # Other known values for block 4 in NSMBW: 0000 0002 0042 0000,
        #                     0000 0002 0002 0000, 0000 0003 0003 0000
        self.blocks[5] = b'\0\0\xFF\xFF\xFF\xFF\0\0\0\0\0\0\0\0\0\0\0\0\0\0' # always this
        self.blocks[11] = b'' # never used
        self.blocks[12] = b'' # never used
        #self.blocks[13] = b'' # paths
        #self.blocks[14] = b'' # path nodes
        #self.blocks[15] = b'' # progress paths
        #self.blocks[16] = b'' # progress path nodes

        # Save each block
        self.SaveTilesetNames() # block 1
        #self.SaveOptions() # block 2
        #self.SaveEntrances() # block 7
        self.SaveSprites() # block 8
        self.SaveLoadedSprites() # block 9
        #self.SaveZones() # block 10 (and 3, 5 and 6)
        self.SaveLocations() # block 11
        #self.SavePaths() # blocks 14 and 15
        self.SaveProgPaths() # blocks 16 and 17

        # Save the metadata
        rdata = bytearray(self.Metadata.save())
        if len(rdata) % 4 != 0:
           for i in range(4 - (len(rdata) % 4)):
               rdata.append(0)
        rdata = bytes(rdata)

        # Save the main course file
        # We'll be passing over the blocks array two times.
        # Using bytearray here because it offers mutable bytes
        # and works directly with struct.pack_into(), so it's a
        # win-win situation
        FileLength = (len(self.blocks) * 8) + len(rdata)
        for block in self.blocks:
            FileLength += len(block)

        course = bytearray()
        for i in range(FileLength): course.append(0)
        saveblock = struct.Struct('<II')

        HeaderOffset = 0
        FileOffset = (len(self.blocks) * 8) + len(rdata)
        struct.pack_into('{0}s'.format(len(rdata)), course, 0x70, rdata)
        for block in self.blocks:
            blocksize = len(block)
            saveblock.pack_into(course, HeaderOffset, FileOffset, blocksize)
            if blocksize > 0:
                course[FileOffset:FileOffset + blocksize] = block
            HeaderOffset += 8
            FileOffset += blocksize

        # Return stuff
        return (
            bytes(course),
            self.SaveLayer(0),
            self.SaveLayer(1),
            self.SaveLayer(2),
            )


    def RemoveFromLayer(self, obj):
        """
        Removes a specific object from the level and updates Z-indices accordingly
        """
        layer = self.layers[obj.layer]
        idx = layer.index(obj)
        del layer[idx]
        for i in range(idx,len(layer)):
            upd = layer[i]
            upd.setZValue(upd.zValue() - 1)

    def SortSpritesByZone(self):
        """
        Sorts the sprite list by zone ID so it will work in-game
        """

        split = {}
        zones = []

        f_MapPositionToZoneID = MapPositionToZoneID
        zonelist = self.zones

        for sprite in self.sprites:
            zone = f_MapPositionToZoneID(zonelist, sprite.objx, sprite.objy)
            sprite.zoneID = zone
            if not zone in split:
                split[zone] = []
                zones.append(zone)
            split[zone].append(sprite)

        newlist = []
        zones.sort()
        for z in zones:
            newlist += split[z]

        self.sprites = newlist


    def LoadReggieInfo(self, data):
        if (data is None) or (len(data) == 0):
            self.Metadata = Metadata()
            return

        try: self.Metadata = Metadata(data)
        except Exception: self.Metadata = Metadata() # fallback


class Area_NSMB2(AbstractParsedArea):
    """
    Class for a parsed NSMB2 level area
    """
    def __init__(self):
        """
        Creates a completely new NSMB2 area
        """
        # Default tileset names for NSMB2
        self.tileset0 = 'J_Kihon'
        self.tileset1 = 'M_Nohara_Onpu'
        self.tileset2 = ''
        self.tileset3 = ''

        super().__init__()

    def LoadBlocks(self, course):
        """
        Loads self.blocks from the course file
        """
        self.blocks = [None] * 17
        getblock = struct.Struct('<II')
        for i in range(17):
            data = getblock.unpack_from(course, i * 8)
            if data[1] == 0:
                self.blocks[i] = b''
            else:
                self.blocks[i] = course[data[0]:data[0] + data[1]]

        self.block1pos = getblock.unpack_from(course, 0)


    def LoadTilesetNames(self):
        """
        Loads block 1, the tileset names
        """
        data = struct.unpack_from('32s32s32s32s', self.blocks[0])
        self.tileset0 = data[0].strip(b'\0').decode('latin-1')
        self.tileset1 = data[1].strip(b'\0').decode('latin-1')
        self.tileset2 = data[2].strip(b'\0').decode('latin-1')
        self.tileset3 = data[3].strip(b'\0').decode('latin-1')


    def LoadOptions(self):
        """
        Loads block 2, the general options
        """
        optdata = self.blocks[1]
        optstruct = struct.Struct('<IxxxxHhLBBBx')
        offset = 0
        data = optstruct.unpack_from(optdata,offset)
        self.defEvents, self.wrapFlag, self.timeLimit, self.unk1, self.startEntrance, self.unk2, self.unk3 = data


    def LoadEntrances(self):
        """
        Loads block 7, the entrances
        """
        entdata = self.blocks[6]
        entcount = len(entdata) // 24
        entstruct = struct.Struct('<HHxxxxBBBBxBBBHxB')
        offset = 0
        entrances = []
        for i in range(entcount):
            data = entstruct.unpack_from(entdata,offset)
            #def __init__(self, x, y, id, destarea, destentrance, type, zone, layer, path, settings, cpd):
            entrances.append(EntranceItem(data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10]))
            offset += 24
        self.entrances = entrances


    def LoadSprites(self):
        """
        Loads block 8, the sprites
        """
        spritedata = self.blocks[7]
        sprcount = len(spritedata) // 24
        sprstruct = struct.Struct('<HHH10sxx2sxxxx')
        offset = 0
        sprites = []

        unpack = sprstruct.unpack_from
        append = sprites.append
        obj = SpriteItem
        for i in range(sprcount):
            data = unpack(spritedata, offset)
            append(obj(data[0], data[1], data[2], data[3] + data[4]))
            offset += 24
        self.sprites = sprites


    def LoadZones(self):
        """
        Loads blocks 3, 5, 6 and 10 - the bounding, background and zone data
        """

        # Block 3 - bounding data
        bdngdata = self.blocks[2]
        count = len(bdngdata) // 28
        bdngstruct = struct.Struct('<llllHHxxxxxxxx')
        offset = 0
        bounding = []
        for i in range(count):
            datab = bdngstruct.unpack_from(bdngdata,offset)
            bounding.append([datab[0], datab[1], datab[2], datab[3], datab[4], datab[5]])
            offset += 28
        self.bounding = bounding

        # Block 5 - Bg data
        bgData = self.blocks[4]
        bgCount = len(bgData) // 28
        offset = 0
        bg = {}
        for i in range(bgCount):
            newBg = Background_NSMB2()
            bgId = newBg.loadFrom(bgData[offset:offset + 28])
            bg[bgId] = newBg
            offset += 28
        self.bg = bg

        # Block 10 - zone data
        zonedata = self.blocks[9]
        zonestruct = struct.Struct('<hhhhHxxBBxxxxxxBBBxBxxx')
        count = len(zonedata) // 28
        offset = 0
        zones = []
        for i in range(count):
            dataz = zonestruct.unpack_from(zonedata, offset)

            # Find the proper bounding
            boundObj = None
            id = dataz[6]
            for checkb in self.bounding:
                if checkb[4] == id: boundObj = checkb

            # Find the proper bg
            bgObj = None
            if dataz[10] in bg:
                bgObj = bg[dataz[10]]

            zones.append(ZoneItem(dataz[0], dataz[1], dataz[2], dataz[3], dataz[4], dataz[5], dataz[6], dataz[7], dataz[8], dataz[9], dataz[10], boundObj, bgObj, i))
            offset += 28
        self.zones = zones


    def LoadLocations(self):
        """
        Loads block 11, the locations
        """
        locdata = self.blocks[10]
        locstruct = struct.Struct('<HHHHBxxx')
        count = len(locdata) // 12
        offset = 0
        locations = []
        for i in range(count):
            data = locstruct.unpack_from(locdata, offset)
            locations.append(LocationItem(data[0], data[1], data[2], data[3], data[4]))
            offset += 12
        self.locations = locations


    def LoadLayer(self, idx, layerdata):
        """
        Loads a specific object layer from a bytes object
        """
        if idx == 0: return
        objcount = len(layerdata) // 16
        objstruct = struct.Struct('<HhhHH')
        offset = 0
        z = (2 - idx) * 8192

        layer = self.layers[idx]
        append = layer.append
        unpack = objstruct.unpack_from
        for i in range(objcount):
            data = unpack(layerdata, offset)
            x, y = data[1], data[2]
            append(ObjectItem(data[0] >> 12, data[0] & 4095, idx, x, y, data[3], data[4], z))
            z += 1
            offset += 16


    def LoadPaths(self):
        """
        Loads block 12, the paths
        """
        # Path struct: <BxHHH
        pathdata = self.blocks[13]
        pathcount = len(pathdata) // 12
        pathstruct = struct.Struct('<BxHHH')
        offset = 0
        unpack = pathstruct.unpack_from
        pathinfo = []
        paths = []
        for i in range(pathcount):
            data = unpack(pathdata, offset)
            nodes = self.LoadPathNodes(data[1], data[2])
            add2p = {'id': int(data[0]),
                     'nodes': [],
                     'loops': data[3] == 2,
                     }
            for node in nodes:
                add2p['nodes'].append(node)
            pathinfo.append(add2p)


            offset += 12

        for i in range(pathcount):
            xpi = pathinfo[i]
            for j, xpj in enumerate(xpi['nodes']):
                paths.append(PathItem(xpj['x'], xpj['y'], xpi, xpj))


        self.pathdata = pathinfo
        self.paths = paths


    def LoadPathNodes(self, startindex, count):
        """
        Loads block 13, the path nodes
        """
        # PathNode struct: <HHffhxx
        ret = []
        nodedata = self.blocks[14]
        nodestruct = struct.Struct('<HHffhxx')
        offset = startindex * 20
        unpack = nodestruct.unpack_from
        for i in range(count):
            data = unpack(nodedata, offset)
            ret.append({'x': int(data[0]),
                        'y': int(data[1]),
                        'speed': float(data[2]),
                        'accel': float(data[3]),
                        'delay': int(data[4]),
                        #'id' : i
            })
            offset += 20
        return ret

    def LoadProgPaths(self):
        """
        Loads block 16, the progress paths
        """
        # Progress path struct: <HHHxxx?xx
        progpathdata = self.blocks[15]
        progpathcount = len(progpathdata) // 12
        progpathstruct = struct.Struct('<HHHxxx?xx')
        offset = 0
        unpack = progpathstruct.unpack_from
        progpathinfo = []
        progpaths = []
        for i in range(progpathcount):
            data = unpack(progpathdata, offset)
            nodes = self.LoadProgPathNodes(data[1], data[2])
            add2p = {'id': data[0],
                     'nodes': [],
                     'altpath': data[3],
                     }
            for node in nodes:
                add2p['nodes'].append(node)
            progpathinfo.append(add2p)

            offset += 12

        for i in range(progpathcount):
            xpi = progpathinfo[i]
            for j, xpj in enumerate(xpi['nodes']):
                progpaths.append(ProgressPathItem(xpj['x'], xpj['y'], xpi, xpj))


        self.progpathdata = progpathinfo
        self.progpaths = progpaths


    def LoadProgPathNodes(self, startindex, count):
        """
        Loads block 17, the progress path nodes
        """

        ret = []
        nodedata = self.blocks[16]
        nodestruct = struct.Struct('<hh16x')
        offset = startindex * 20
        unpack = nodestruct.unpack_from
        for i in range(count):
            data = unpack(nodedata, offset)
            ret.append({'x': int(data[0]),
                        'y': int(data[1]),
            })
            offset += 20
        return ret


    def LoadComments(self):
        """
        Loads the comments from self.Metadata
        """
        self.comments = []
        b = self.Metadata.binData('InLevelComments_A%d' % self.areanum)
        if b is None: return
        idx = 0
        while idx < len(b):
            xpos  = b[idx]   << 24
            xpos |= b[idx+1] << 16
            xpos |= b[idx+2] << 8
            xpos |= b[idx+3]
            idx += 4
            ypos  = b[idx]   << 24
            ypos |= b[idx+1] << 16
            ypos |= b[idx+2] << 8
            ypos |= b[idx+3]
            idx += 4
            tlen  = b[idx]   << 24
            tlen |= b[idx+1] << 16
            tlen |= b[idx+2] << 8
            tlen |= b[idx+3]
            idx += 4
            s = ''
            for char in range(tlen):
                s += chr(b[idx])
                idx += 1

            com = CommentItem(xpos, ypos, s)
            com.listitem = QtWidgets.QListWidgetItem()

            self.comments.append(com)

            com.UpdateListItem()


    def SaveTilesetNames(self):
        """
        Saves the tileset names back to block 1
        """
        self.blocks[0] = ''.join([self.tileset0.ljust(32, '\0'), self.tileset1.ljust(32, '\0'), self.tileset2.ljust(32, '\0'), self.tileset3.ljust(32, '\0')]).encode('latin-1')


    def SaveOptions(self):
        """
        Saves block 2, the general options
        """
        optstruct = struct.Struct('<IxxxxHhLBBBx')
        buffer = bytearray(20)
        optstruct.pack_into(buffer, 0, self.defEvents, self.wrapFlag, self.timeLimit, self.unk1, self.startEntrance, self.unk2, self.unk3)
        self.blocks[1] = bytes(buffer)


    def SaveLayer(self, idx):
        """
        Saves an object layer to a bytes object
        """
        if idx == 0: return None

        layer = self.layers[idx]
        if not layer: return None

        offset = 0
        objstruct = struct.Struct('<HhhHH')
        buffer = bytearray((len(layer) * 16) + 2)
        f_int = int
        for obj in layer:
            objstruct.pack_into(buffer, offset, f_int((obj.tileset << 12) | obj.type), f_int(obj.objx), f_int(obj.objy), f_int(obj.width), f_int(obj.height))
            offset += 16
        buffer[offset] = 0xFF
        buffer[offset + 1] = 0xFF
        return bytes(buffer)


    def SaveEntrances(self):
        """
        Saves the entrances back to block 7
        """
        offset = 0
        entstruct = struct.Struct('<HHxxxxBBBBxBBBHxB')
        buffer = bytearray(len(self.entrances) * 20)
        zonelist = self.zones
        for entrance in self.entrances:
            zoneID = MapPositionToZoneID(zonelist, entrance.objx, entrance.objy)
            entstruct.pack_into(buffer, offset, int(entrance.objx), int(entrance.objy), int(entrance.entid), int(entrance.destarea), int(entrance.destentrance), int(entrance.enttype), zoneID, int(entrance.entlayer), int(entrance.entpath), int(entrance.entsettings), int(entrance.cpdirection))
            offset += 20
        self.blocks[6] = bytes(buffer)


    def SavePaths(self):
        """
        Saves the paths back to block 13
        """
        pathstruct = struct.Struct('<BxHHH')
        nodecount = 0
        for path in self.pathdata:
            nodecount += len(path['nodes'])
        nodebuffer = bytearray(nodecount * 20)
        nodeoffset = 0
        nodeindex = 0
        offset = 0
        buffer = bytearray(len(self.pathdata) * 12)
        
        for path in self.pathdata:
            if(len(path['nodes']) < 1): continue
            self.WritePathNodes(nodebuffer, nodeoffset, path['nodes'])

            pathstruct.pack_into(buffer, offset, int(path['id']), int(nodeindex), int(len(path['nodes'])), 2 if path['loops'] else 0)
            offset += 12
            nodeoffset += len(path['nodes']) * 20
            nodeindex += len(path['nodes'])

        self.blocks[13] = bytes(buffer)
        self.blocks[14] = bytes(nodebuffer)


    def WritePathNodes(self, buffer, offst, nodes):
        """
        Writes the pathnode data to the block 14 bytearray
        """
        offset = int(offst)
        
        nodestruct = struct.Struct('<HHffhxxxxxx')
        for node in nodes:
            nodestruct.pack_into(buffer, offset, int(node['x']), int(node['y']), float(node['speed']), float(node['accel']), int(node['delay']))
            offset += 20


    def SaveProgPaths(self):
        """
        Saves the progress paths back to block 16
        """
        pathstruct = struct.Struct('<HHHxxx?xx')
        nodecount = 0
        for path in self.progpathdata:
            nodecount += len(path['nodes'])
        nodebuffer = bytearray(nodecount * 20)
        nodeoffset = 0
        nodeindex = 0
        offset = 0
        buffer = bytearray(len(self.progpathdata) * 12)
        
        for path in self.progpathdata:
            if(len(path['nodes']) < 1): continue
            self.WriteProgPathNodes(nodebuffer, nodeoffset, path['nodes'])

            pathstruct.pack_into(buffer, offset, int(path['id']), int(nodeindex), int(len(path['nodes'])), path['altpath'])
            offset += 12
            nodeoffset += len(path['nodes']) * 20
            nodeindex += len(path['nodes'])

        self.blocks[15] = bytes(buffer)
        self.blocks[16] = bytes(nodebuffer)


    def WriteProgPathNodes(self, buffer, offst, nodes):
        """
        Writes the progpathnode data to the block 17 bytearray
        """
        offset = int(offst)
        
        nodestruct = struct.Struct('<hh16x')
        for node in nodes:
            nodestruct.pack_into(buffer, offset, int(node['x']), int(node['y']))
            offset += 20


    def SaveSprites(self):
        """
        Saves the sprites back to block 8
        """
        offset = 0
        sprstruct = struct.Struct('<HHH10sH2sxxxx')
        buffer = bytearray((len(self.sprites) * 24) + 4)
        f_int = int
        for sprite in self.sprites:
            try:
                sprstruct.pack_into(buffer, offset, f_int(sprite.type), f_int(sprite.objx), f_int(sprite.objy), sprite.spritedata[:10], sprite.zoneID, sprite.spritedata[10:])
            except struct.error:
                # Hopefully this will solve the mysterious bug, and will
                # soon no longer be necessary.
                raise ValueError('SaveSprites struct.error. Current sprite data dump:\n' + \
                    str(offset) + '\n' + \
                    str(sprite.type) + '\n' + \
                    str(sprite.objx) + '\n' + \
                    str(sprite.objy) + '\n' + \
                    str(sprite.spritedata[:6]) + '\n' + \
                    str(sprite.zoneID) + '\n' + \
                    str(bytes([sprite.spritedata[7],])) + '\n',
                    )
            offset += 24
        buffer[offset] = 0xFF
        buffer[offset + 1] = 0xFF
        buffer[offset + 2] = 0xFF
        buffer[offset + 3] = 0xFF
        self.blocks[7] = bytes(buffer)


    def SaveLoadedSprites(self):
        """
        Saves the list of loaded sprites back to block 9
        """
        ls = []
        for sprite in self.sprites:
            if sprite.type not in ls: ls.append(sprite.type)
        ls.sort()

        offset = 0
        sprstruct = struct.Struct('<Hxx')
        buffer = bytearray(len(ls) * 4)
        for s in ls:
            sprstruct.pack_into(buffer, offset, int(s))
            offset += 4
        self.blocks[8] = bytes(buffer)


    def SaveZones(self):
        """
        Saves blocks 10, 3, 5 and 6, the zone data, boundings, bgA and bgB data respectively
        """
        bdngstruct = struct.Struct('<llllxBxBxxxx')
        bgAstruct = struct.Struct('<xBhhhhHHHxxxBxxxx')
        bgBstruct = struct.Struct('<xBhhhhHHHxxxBxxxx')
        zonestruct = struct.Struct('<HHHHHHBBBBxBBBBxBB')
        offset = 0
        i = 0
        zcount = len(Area.zones)
        buffer2 = bytearray(24 * zcount)
        buffer4 = bytearray(24 * zcount)
        buffer5 = bytearray(24 * zcount)
        buffer9 = bytearray(24 * zcount)
        for z in Area.zones:
            bdngstruct.pack_into(buffer2, offset, z.yupperbound, z.ylowerbound, z.yupperbound2, z.ylowerbound2, i, 0xF)
            bgAstruct.pack_into(buffer4, offset, i, z.XscrollA, z.YscrollA, z.YpositionA, z.XpositionA, z.bg1A, z.bg2A, z.bg3A, z.ZoomA)
            bgBstruct.pack_into(buffer5, offset, i, z.XscrollB, z.YscrollB, z.YpositionB, z.XpositionB, z.bg1B, z.bg2B, z.bg3B, z.ZoomB)
            zonestruct.pack_into(buffer9, offset, z.objx, z.objy, z.width, z.height, z.modeldark, z.terraindark, i, i, z.cammode, z.camzoom, z.visibility, i, i, z.camtrack, z.music, z.sfxmod)
            offset += 24
            i += 1

        self.blocks[2] = bytes(buffer2)
        self.blocks[4] = bytes(buffer4)
        self.blocks[5] = bytes(buffer5)
        self.blocks[9] = bytes(buffer9)


    def SaveLocations(self):
        """
        Saves block 11, the location data
        """
        locstruct = struct.Struct('<HHHHBxxx')
        offset = 0
        zcount = len(Area.locations)
        buffer = bytearray(12 * zcount)

        for z in Area.locations:
            locstruct.pack_into(buffer, offset, int(z.objx), int(z.objy), int(z.width), int(z.height), int(z.id))
            offset += 12

        self.blocks[10] = bytes(buffer)


class ListWidgetItem_SortsByOther(QtWidgets.QListWidgetItem):
    """
    A ListWidgetItem that defers sorting to another object.
    """
    def __init__(self, reference, text=''):
        super().__init__(text)
        self.reference = reference
    def __lt__(self, other):
        return self.reference < other.reference


class LevelEditorItem(QtWidgets.QGraphicsItem):
    """
    Class for any type of item that can show up in the level editor control
    """
    positionChanged = None # Callback: positionChanged(LevelEditorItem obj, int oldx, int oldy, int x, int y)
    autoPosChange = False
    dragoffsetx = 0
    dragoffsety = 0

    def __init__(self):
        """
        Generic constructor for level editor items
        """
        QtWidgets.QGraphicsItem.__init__(self)
        self.setFlag(self.ItemSendsGeometryChanges, True)

    def __lt__(self, other):
        return (self.objx * 100000 + self.objy) < (other.objx * 100000 + other.objy)

    def itemChange(self, change, value):
        """
        Makes sure positions don't go out of bounds and updates them as necessary
        """

        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            # snap to 24x24
            newpos = value

            # snap even further if Alt isn't held
            # but -only- if OverrideSnapping is off
            if (not OverrideSnapping) and (not self.autoPosChange):
                if self.scene() is None: objectsSelected = False
                else: objectsSelected = any([isinstance(thing, ObjectItem) for thing in mainWindow.CurrentSelection])
                if QtWidgets.QApplication.keyboardModifiers() == Qt.AltModifier:
                    # Alt is held; don't snap
                    newpos.setX(int(int((newpos.x() + 0.75) / 1.5) * 1.5))
                    newpos.setY(int(int((newpos.y() + 0.75) / 1.5) * 1.5))
                elif not objectsSelected and self.isSelected() and len(mainWindow.CurrentSelection) > 1:
                    # Snap to 8x8, but with the dragoffsets
                    dragoffsetx, dragoffsety = int(self.dragoffsetx), int(self.dragoffsety)
                    if dragoffsetx < -12: dragoffsetx += 12
                    if dragoffsety < -12: dragoffsety += 12
                    if dragoffsetx == 0: dragoffsetx = -12
                    if dragoffsety == 0: dragoffsety = -12
                    referenceX = int((newpos.x() + 6 + 12 + dragoffsetx) / 12) * 12
                    referenceY = int((newpos.y() + 6 + 12 + dragoffsety) / 12) * 12
                    newpos.setX(referenceX - (12 + dragoffsetx))
                    newpos.setY(referenceY - (12 + dragoffsety))
                elif objectsSelected and self.isSelected():
                    # Objects are selected, too; move in sync by snapping to whole blocks
                    dragoffsetx, dragoffsety = int(self.dragoffsetx), int(self.dragoffsety)
                    if dragoffsetx == 0: dragoffsetx = -24
                    if dragoffsety == 0: dragoffsety = -24
                    referenceX = int((newpos.x() + 12 + 24 + dragoffsetx) / 24) * 24
                    referenceY = int((newpos.y() + 12 + 24 + dragoffsety) / 24) * 24
                    newpos.setX(referenceX - (24 + dragoffsetx))
                    newpos.setY(referenceY - (24 + dragoffsety))
                else:
                    # Snap to 8x8
                    newpos.setX(int(int((newpos.x() + 6) / 12) * 12))
                    newpos.setY(int(int((newpos.y() + 6) / 12) * 12))

            x = newpos.x()
            y = newpos.y()

            # don't let it get out of the boundaries
            if x < 0: newpos.setX(0)
            if x > 24552: newpos.setX(24552)
            if y < 0: newpos.setY(0)
            if y > 12264: newpos.setY(12264)

            # update the data
            x = int(newpos.x() / 1.5)
            y = int(newpos.y() / 1.5)
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
        mainWindow.scene.render(
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

    def __init__(self, tileset, type, layer, x, y, width, height, z):
        """
        Creates an object with specific data
        """
        LevelEditorItem.__init__(self)

        self.tileset = tileset
        self.type = type
        self.objx = x
        self.objy = y
        self.layer = layer
        self.width = width
        self.height = height
        self.objdata = None

        self.setFlag(self.ItemIsMovable, not ObjectsFrozen)
        self.setFlag(self.ItemIsSelectable, not ObjectsFrozen)
        self.UpdateRects()

        self.dragging = False
        self.dragstartx = -1
        self.dragstarty = -1
        self.objsDragging = {}

        global DirtyOverride
        DirtyOverride += 1
        self.setPos(x*24,y*24)
        DirtyOverride -= 1

        self.setZValue(z)
        self.UpdateTooltip()

        if layer == 0:
            self.setVisible(Layer0Shown)
        elif layer == 1:
            self.setVisible(Layer1Shown)
        elif layer == 2:
            self.setVisible(Layer2Shown)

        self.updateObjCache()
        self.UpdateTooltip()


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
        self.setToolTip(trans.string('Objects', 0, '[tileset]', self.tileset+1, '[obj]', self.type, '[width]', self.width, '[height]', self.height, '[layer]', self.layer))


    def updateObjCache(self):
        """
        Updates the rendered object data
        """
        self.objdata = RenderObject(self.tileset, self.type, self.width, self.height)


    def UpdateRects(self):
        """
        Recreates the bounding and selection rects
        """
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0, 0, 24 * self.width, 24 * self.height)
        self.SelectionRect = QtCore.QRectF(0, 0, (24 * self.width) - 1, (24 * self.height) - 1)
        self.GrabberRect = QtCore.QRectF((24 * self.width) - 5, (24 * self.height) - 5, 5, 5)
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
            newpos.setX(int((newpos.x() + 12) / 24) * 24)
            newpos.setY(int((newpos.y() + 12) / 24) * 24)
            x = newpos.x()
            y = newpos.y()

            # don't let it get out of the boundaries
            if x < 0: newpos.setX(0)
            if x > 24576: newpos.setX(24576)
            if y < 0: newpos.setY(0)
            if y > 12288: newpos.setY(12288)

            # update the data
            x = int(newpos.x() / 24)
            y = int(newpos.y() / 24)
            if x != self.objx or y != self.objy:
                self.LevelRect.moveTo(x,y)

                oldx = self.objx
                oldy = self.objy
                self.objx = x
                self.objy = y
                if self.positionChanged is not None:
                    self.positionChanged(self, oldx, oldy, x, y)

                SetDirty()

                #updRect = QtCore.QRectF(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())
                #scene.invalidate(updRect)

                scene.invalidate(self.x(), self.y(), self.width*24, self.height*24, QtWidgets.QGraphicsScene.BackgroundLayer)
                #scene.invalidate(newpos.x(), newpos.y(), self.width*24, self.height*24, QtWidgets.QGraphicsScene.BackgroundLayer)

            return newpos

        return QtWidgets.QGraphicsItem.itemChange(self, change, value)


    def paint(self, painter, option, widget):
        """
        Paints the object
        """
        global theme

        if self.isSelected():
            painter.setPen(QtGui.QPen(theme.color('object_lines_s'), 1, Qt.DotLine))
            painter.drawRect(self.SelectionRect)
            painter.fillRect(self.SelectionRect, theme.color('object_fill_s'))

            painter.fillRect(self.GrabberRect, theme.color('object_lines_s'))


    def mousePressEvent(self, event):
        """
        Overrides mouse pressing events if needed for resizing
        """
        if event.button() == Qt.LeftButton:
            if QtWidgets.QApplication.keyboardModifiers() == Qt.ControlModifier:
                layer = Area.layers[self.layer]
                if len(layer) == 0:
                    newZ = (2 - self.layer) * 8192
                else:
                    newZ = layer[-1].zValue() + 1

                currentZ = self.zValue()
                self.setZValue(newZ) # swap the Z values so it doesn't look like the cloned item is the old one
                newitem = ObjectItem(self.tileset, self.type, self.layer, self.objx, self.objy, self.width, self.height, currentZ)
                layer.append(newitem)
                mainWindow.scene.addItem(newitem)
                mainWindow.scene.clearSelection()
                self.setSelected(True)

                SetDirty()

        if self.isSelected() and self.GrabberRect.contains(event.pos()):
            # start dragging
            self.dragging = True
            self.dragstartx = int((event.pos().x() - 10) / 24)
            self.dragstarty = int((event.pos().y() - 10) / 24)
            self.objsDragging = {}
            for selitem in mainWindow.scene.selectedItems():
                if not isinstance(selitem, ObjectItem): continue
                self.objsDragging[selitem] = [selitem.width, selitem.height]
            event.accept()
        else:
            LevelEditorItem.mousePressEvent(self, event)
            self.dragging = False
            self.objsDragging = {}
        self.UpdateTooltip()


    def mouseMoveEvent(self, event):
        """
        Overrides mouse movement events if needed for resizing
        """
        if event.buttons() != Qt.NoButton and self.dragging:
            # resize it
            dsx = self.dragstartx
            dsy = self.dragstarty

            clickedx = int((event.pos().x() - 10) / 24)
            clickedy = int((event.pos().y() - 10) / 24)

            cx = self.objx
            cy = self.objy

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
                    if newWidth < 1: newWidth = 1
                    if newHeight < 1: newHeight = 1
                    obj.width = newWidth
                    obj.height = newHeight

                    obj.updateObjCache()

                    oldrect = obj.BoundingRect
                    oldrect.translate(cx * 24, cy * 24)
                    newrect = QtCore.QRectF(obj.x(), obj.y(), obj.width * 24, obj.height * 24)
                    updaterect = oldrect.united(newrect)

                    obj.UpdateRects()
                    obj.scene().update(updaterect)
                SetDirty()

            event.accept()
        else:
            LevelEditorItem.mouseMoveEvent(self, event)
        self.UpdateTooltip()


    def delete(self):
        """
        Delete the object from the level
        """
        Area.RemoveFromLayer(self)
        self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())


class AbstractBackground():
    """
    A class that represents an abstract background for a zone (both bgA and bgB)
    """
    def __init__(self, xScroll=1, yScroll=1, xPos=1, yPos=1):
        self.xScroll = xScroll
        self.yScroll = yScroll
        self.xPos = xPos
        self.yPos = yPos

    def save(idnum=0):
        return b''


class Background_NSMBW(AbstractBackground):
    """
    A class that represents a background from New Super Mario Bros. Wii
    """
    pass # not yet implemented


class Background_NSMB2(AbstractBackground):
    """
    A class that represents a background from New Super Mario Bros. 2
    """
    def __init__(self, xScroll=1, yScroll=1, xPos=1, yPos=1, name=''):
        super().__init__(xScroll, yScroll, xPos, yPos)
        self.name = name

    def loadFrom(self, data):
        if len(data) != 28:
            raise ValueError('Wrong data length: must be 28 bytes exactly')

        bgstruct = struct.Struct('<Hbbbbxx15sbxxxx')
        bgvalues = bgstruct.unpack(data)
        id = bgvalues[0]
        self.xScroll = bgvalues[1]
        self.yScroll = bgvalues[2]
        self.xPos = bgvalues[3]
        self.yPos = bgvalues[4]
        self.name = bgvalues[5].split(b'\0')[0].decode('utf-8')
        self.unk1 = bgvalues[6]

        return id
    
    def save(idnum=0):
        bgstruct = struct.struct('<Hbbbbxx15sbxxxx')
        return # not yet implemented properly; ignore the stuff below
        settings = struct.pack('<Hbbbbxx', idnum, self.xScroll, self.yScroll, self.xPos, self.yPos)
        name = self.name.encode('utf-8') + b'\0' * (20 - len(self.name))
        return settings + name


class ZoneItem(LevelEditorItem):
    """
    Level editor item that represents a zone
    """

    def __init__(self, a, b, c, d, e, f, g, h, i, j, k, bounding, bg, id=None):
        """
        Creates a zone with specific data
        """
        LevelEditorItem.__init__(self)

        self.font = NumberFont
        self.TitlePos = QtCore.QPointF(10, 18)

        self.objx = a
        self.objy = b
        self.width = c
        self.height = d

        self.unk1 = e
        self.id = f
        self.block3id = g
        self.camtrack = h
        self.unk2 = i
        self.music = j
        self.background = bg
        self.UpdateRects()

        # These options aren't present in NSMB2, as far as I can tell
        self.modeldark = 0
        self.terraindark = 0
        self.cammode = 0
        self.camzoom = 0
        self.visibility = 0
        self.block5id = 0
        self.block6id = 0
        self.sfxmod = 0

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

        self.dragging = False
        self.dragstartx = -1
        self.dragstarty = -1

        global DirtyOverride
        DirtyOverride += 1
        self.setPos(int(a*1.5),int(b*1.5))
        DirtyOverride -= 1
        self.setZValue(50000)


    def UpdateTitle(self):
        """
        Updates the zone's title
        """
        self.title = trans.string('Zones', 0, '[num]', self.id + 1)


    def UpdateRects(self):
        """
        Updates the zone's bounding rectangle
        """
        if hasattr(mainWindow, 'ZoomLevel'):
            grabberWidth = 500 / mainWindow.ZoomLevel
            if grabberWidth < 5: grabberWidth = 5
        else: grabberWidth = 5

        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0, 0, self.width * 1.5, self.height * 1.5)
        self.ZoneRect = QtCore.QRectF(self.objx, self.objy, self.width, self.height)
        self.DrawRect = QtCore.QRectF(3, 3, int(self.width * 1.5) - 6, int(self.height * 1.5) - 6)
        self.GrabberRectTL = QtCore.QRectF(0, 0, grabberWidth, grabberWidth)
        self.GrabberRectTR = QtCore.QRectF(int(self.width * 1.5) - grabberWidth, 0, grabberWidth, grabberWidth)
        self.GrabberRectBL = QtCore.QRectF(0, int(self.height * 1.5) - grabberWidth, grabberWidth, grabberWidth)
        self.GrabberRectBR = QtCore.QRectF(int(self.width * 1.5) - grabberWidth, int(self.height * 1.5)-grabberWidth, grabberWidth, grabberWidth)


    def paint(self, painter, option, widget):
        """
        Paints the zone on screen
        """
        global theme

        #painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Paint an indicator line to show the leftmost edge of
        # where entrances can be safely placed
        if 24 * 13 < self.DrawRect.width():
            painter.setPen(QtGui.QPen(theme.color('zone_entrance_helper'), 2))
            lineStart = QtCore.QPointF(self.DrawRect.x() + (24 * 13), self.DrawRect.y())
            lineEnd = QtCore.QPointF(self.DrawRect.x() + (24 * 13), self.DrawRect.y() + self.DrawRect.height())
            #painter.drawLine(lineStart, lineEnd)

        # Now paint the borders
        painter.setPen(QtGui.QPen(theme.color('zone_lines'), 3))
        if (self.visibility >= 32) and RealViewEnabled:
            painter.setBrush(QtGui.QBrush(theme.color('zone_dark_fill')))
        painter.drawRect(self.DrawRect)

        # And text
        painter.setPen(QtGui.QPen(theme.color('zone_text'), 3))
        painter.setFont(self.font)
        painter.drawText(self.TitlePos, self.title)

        # And corners ("grabbers")
        GrabberColor = theme.color('zone_corner')
        painter.fillRect(self.GrabberRectTL, GrabberColor)
        painter.fillRect(self.GrabberRectTR, GrabberColor)
        painter.fillRect(self.GrabberRectBL, GrabberColor)
        painter.fillRect(self.GrabberRectBR, GrabberColor)


    def mousePressEvent(self, event):
        """
        Overrides mouse pressing events if needed for resizing
        """

        if self.GrabberRectTL.contains(event.pos()):
            # start dragging
            self.dragging = True
            self.dragstartx = int(event.pos().x() / 1.5)
            self.dragstarty = int(event.pos().y() / 1.5)
            self.dragcorner = 1
            event.accept()
        elif self.GrabberRectTR.contains(event.pos()):
            self.dragging = True
            self.dragstartx = int(event.pos().x() / 1.5)
            self.dragstarty = int(event.pos().y() / 1.5)
            self.dragcorner = 2
            event.accept()
        elif self.GrabberRectBL.contains(event.pos()):
            self.dragging = True
            self.dragstartx = int(event.pos().x() / 1.5)
            self.dragstarty = int(event.pos().y() / 1.5)
            self.dragcorner = 3
            event.accept()
        elif self.GrabberRectBR.contains(event.pos()):
            self.dragging = True
            self.dragstartx = int(event.pos().x() / 1.5)
            self.dragstarty = int(event.pos().y() / 1.5)
            self.dragcorner = 4
            event.accept()
        else:
            LevelEditorItem.mousePressEvent(self, event)
            self.dragging = False


    def mouseMoveEvent(self, event):
        """
        Overrides mouse movement events if needed for resizing
        """

        if event.buttons() != Qt.NoButton and self.dragging:
            # resize it
            dsx = self.dragstartx
            dsy = self.dragstarty
            clickedx = int(event.pos().x() / 1.5)
            clickedy = int(event.pos().y() / 1.5)
            corner = self.dragcorner

            cx = self.objx
            cy = self.objy

            checkwidth = self.width - 128
            checkheight = self.height - 128
            if corner == 1:
                if clickedx >= checkwidth: clickedx = checkwidth - 1
                if clickedy >= checkheight: clickedy = checkheight - 1
            elif corner == 2:
                if clickedx < 0: clickedx = 0
                if clickedy >= checkheight: clickedy = checkheight - 1
            elif corner == 3:
                if clickedx >= checkwidth: clickedx = checkwidth - 1
                if clickedy < 0: clickedy = 0
            elif corner == 4:
                if clickedx < 0: clickedx = 0
                if clickedy < 0: clickedy = 0

            if clickedx != dsx or clickedy != dsy:
                #if (cx + clickedx - dsx) < 16: clickedx += (16 - (cx + clickedx - dsx))
                #if (cy + clickedy - dsy) < 16: clickedy += (16 - (cy + clickedy - dsy))

                self.dragstartx = clickedx
                self.dragstarty = clickedy
                xdelta = clickedx - dsx
                ydelta = clickedy - dsy

                if corner == 1:
                    self.objx += xdelta
                    self.objy += ydelta
                    self.dragstartx -= xdelta
                    self.dragstarty -= ydelta
                    self.width -= xdelta
                    self.height -= ydelta
                elif corner == 2:
                    self.objy += ydelta
                    self.dragstarty -= ydelta
                    self.width += xdelta
                    self.height -= ydelta
                elif corner == 3:
                    self.objx += xdelta
                    self.dragstartx -= xdelta
                    self.width -= xdelta
                    self.height += ydelta
                elif corner == 4:
                    self.width += xdelta
                    self.height += ydelta

                if self.width < 16:
                    self.objx -= (16 - self.width)
                    self.width = 16
                if self.height < 16:
                    self.objy -= (16 - self.height)
                    self.height = 16

                if self.objx < 16:
                    self.width -= (16 - self.objx)
                    self.objx = 16
                if self.objy < 16:
                    self.height -= (16 - self.objy)
                    self.objy = 16

                oldrect = self.BoundingRect
                oldrect.translate(cx * 1.5, cy * 1.5)
                newrect = QtCore.QRectF(self.x(), self.y(), self.width * 1.5, self.height * 1.5)
                updaterect = oldrect.united(newrect)
                updaterect.setTop(updaterect.top() - 3)
                updaterect.setLeft(updaterect.left() - 3)
                updaterect.setRight(updaterect.right() + 3)
                updaterect.setBottom(updaterect.bottom() + 3)

                self.UpdateRects()
                self.setPos(int(self.objx * 1.5), int(self.objy * 1.5))
                self.scene().update(updaterect)

                mainWindow.levelOverview.update()

                # Call the zoneRepositioned function of all
                # the sprite auxs for this zone
                for a in self.aux:
                    a.zoneRepositioned()

                SetDirty()

            event.accept()
        else:
            LevelEditorItem.mouseMoveEvent(self, event)

    def itemChange(self, change, value):
        """
        Avoids snapping for zones
        """
        return QtWidgets.QGraphicsItem.itemChange(self, change, value)


class LocationItem(LevelEditorItem):
    """
    Level editor item that represents a sprite location
    """
    sizeChanged = None # Callback: sizeChanged(SpriteItem obj, int width, int height)

    def __init__(self, x, y, width, height, id):
        """
        Creates a location with specific data
        """
        LevelEditorItem.__init__(self)

        self.font = NumberFont
        self.TitlePos = QtCore.QPointF(4,12)
        self.objx = x
        self.objy = y
        self.width = width
        self.height = height
        self.id = id
        self.listitem = None
        self.UpdateTitle()
        self.UpdateRects()

        self.setFlag(self.ItemIsMovable, not LocationsFrozen)
        self.setFlag(self.ItemIsSelectable, not LocationsFrozen)

        global DirtyOverride
        DirtyOverride += 1
        self.setPos(int(x*1.5),int(y*1.5))
        DirtyOverride -= 1

        self.dragging = False
        self.setZValue(24000)


    def ListString(self):
        """
        Returns a string that can be used to describe the location in a list
        """
        return trans.string('Locations', 2, '[id]', self.id, '[width]', int(self.width), '[height]', int(self.height), '[x]', int(self.objx), '[y]', int(self.objy))


    def UpdateTitle(self):
        """
        Updates the location's title
        """
        self.title = trans.string('Locations', 0, '[id]', self.id)
        self.UpdateListItem()


    def __lt__(self, other):
        return self.id < other.id


    def UpdateRects(self):
        """
        Updates the location's bounding rectangle
        """
        self.prepareGeometryChange()
        if self.width == 0: self.width == 1
        if self.height == 0: self.height == 1
        self.BoundingRect = QtCore.QRectF(0, 0, self.width * 1.5, self.height * 1.5)
        self.SelectionRect = QtCore.QRectF(self.objx * 1.5, self.objy * 1.5, self.width * 1.5, self.height * 1.5)
        self.ZoneRect = QtCore.QRectF(self.objx, self.objy, self.width, self.height)
        self.DrawRect = QtCore.QRectF(1, 1, (self.width * 1.5) - 2, (self.height * 1.5) - 2)
        self.GrabberRect = QtCore.QRectF((1.5 * self.width) - 6, (1.5 * self.height) - 6, 5, 5)
        self.UpdateListItem()


    def paint(self, painter, option, widget):
        """
        Paints the location on screen
        """
        global theme

        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Draw the purple rectangle
        if not self.isSelected():
            painter.setBrush(QtGui.QBrush(theme.color('location_fill')))
            painter.setPen(QtGui.QPen(theme.color('location_lines')))
        else:
            painter.setBrush(QtGui.QBrush(theme.color('location_fill_s')))
            painter.setPen(QtGui.QPen(theme.color('location_lines_s'), 1, Qt.DotLine))
        painter.drawRect(self.DrawRect)

        # Draw the ID
        painter.setPen(QtGui.QPen(theme.color('location_text')))
        painter.setFont(self.font)
        painter.drawText(self.TitlePos, self.title)

        # Draw the resizer rectangle, if selected
        if self.isSelected(): painter.fillRect(self.GrabberRect, theme.color('location_lines_s'))


    def mousePressEvent(self, event):
        """
        Overrides mouse pressing events if needed for resizing
        """
        if self.isSelected() and self.GrabberRect.contains(event.pos()):
            # start dragging
            self.dragging = True
            self.dragstartx = int(event.pos().x() / 1.5)
            self.dragstarty = int(event.pos().y() / 1.5)
            event.accept()
        else:
            LevelEditorItem.mousePressEvent(self, event)
            self.dragging = False


    def mouseMoveEvent(self, event):
        """
        Overrides mouse movement events if needed for resizing
        """
        if event.buttons() != Qt.NoButton and self.dragging:
            # resize it
            dsx = self.dragstartx
            dsy = self.dragstarty
            clickedx = event.pos().x() / 1.5
            clickedy = event.pos().y() / 1.5

            cx = self.objx
            cy = self.objy

            if clickedx < 0: clickedx = 0
            if clickedy < 0: clickedy = 0

            if clickedx != dsx or clickedy != dsy:
                self.dragstartx = clickedx
                self.dragstarty = clickedy

                self.width += clickedx - dsx
                self.height += clickedy - dsy

                oldrect = self.BoundingRect
                oldrect.translate(cx * 1.5, cy * 1.5)
                newrect = QtCore.QRectF(self.x(), self.y(), self.width * 1.5, self.height * 1.5)
                updaterect = oldrect.united(newrect)

                self.UpdateRects()
                self.scene().update(updaterect)
                SetDirty()

                if self.sizeChanged is not None:
                    self.sizeChanged(self, self.width, self.height)

                if RealViewEnabled:
                    for sprite in Area.sprites:
                        if self.id in sprite.ImageObj.locationIDs and sprite.ImageObj.updateSceneAfterLocationMoved:
                            self.scene().update()

            event.accept()
        else:
            LevelEditorItem.mouseMoveEvent(self, event)


    def delete(self):
        """
        Delete the location from the level
        """
        loclist = mainWindow.locationList
        mainWindow.UpdateFlag = True
        loclist.takeItem(loclist.row(self.listitem))
        mainWindow.UpdateFlag = False
        loclist.selectionModel().clearSelection()
        Area.locations.remove(self)
        self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())




class SpriteItem(LevelEditorItem):
    """
    Level editor item that represents a sprite
    """
    BoundingRect = QtCore.QRectF(0, 0, 24, 24)
    SelectionRect = QtCore.QRectF(0, 0, 23, 23)

    def __init__(self, type, x, y, data):
        """
        Creates a sprite with specific data
        """
        LevelEditorItem.__init__(self)
        self.setZValue(26000)

        self.font = NumberFont
        self.type = type
        self.objx = x
        self.objy = y
        self.spritedata = data
        self.listitem = None
        self.LevelRect = QtCore.QRectF(self.objx / 16, self.objy / 16, 1.5, 1.5)
        self.ChangingPos = False

        SLib.SpriteImage.loadImages()
        self.ImageObj = SLib.SpriteImage(self)

        try:
            sname = Sprites[type].name
            self.name = sname
        except:
            self.name = 'UNKNOWN'

        self.InitializeSprite()

        self.setFlag(self.ItemIsMovable, not SpritesFrozen)
        self.setFlag(self.ItemIsSelectable, not SpritesFrozen)

        global DirtyOverride
        DirtyOverride += 1
        self.setPos(
            int((self.objx + self.ImageObj.xOffset) * 1.5),
            int((self.objy + self.ImageObj.yOffset) * 1.5),
            )
        DirtyOverride -= 1

    def SetType(self, type):
        """
        Sets the type of the sprite
        """
        self.name = Sprites[type].name
        self.setToolTip(trans.string('Sprites', 0, '[type]', type, '[name]', self.name))
        self.type = type

        self.InitializeSprite()

        self.UpdateListItem()

    def ListString(self):
        """
        Returns a string that can be used to describe the sprite in a list
        """
        baseString = trans.string('Sprites', 1, '[name]', self.name, '[x]', self.objx, '[y]', self.objy)

        global SpriteListData
        SpritesThatActivateAnEvent = set(SpriteListData[0])
        SpritesThatActivateAnEventNyb0 = set(SpriteListData[1])
        SpritesTriggeredByAnEventNyb1 = set(SpriteListData[2])
        SpritesTriggeredByAnEventNyb0 = set(SpriteListData[3])
        StarCoinNumbers = set(SpriteListData[4])
        SpritesWithSetIDs = set(SpriteListData[5])
        SpritesWithMovementIDsNyb2 = set(SpriteListData[6])
        SpritesWithMovementIDsNyb3 = set(SpriteListData[7])
        SpritesWithMovementIDsNyb5 = set(SpriteListData[8])
        SpritesWithRotationIDs = set(SpriteListData[9])
        SpritesWithLocationIDsNyb5 = set(SpriteListData[10])
        SpritesWithLocationIDsNyb5and0xF = set(SpriteListData[11])
        SpritesWithLocationIDsNyb4 = set(SpriteListData[12])
        AndController = set(SpriteListData[13])
        OrController = set(SpriteListData[14])
        MultiChainer = set(SpriteListData[15])
        Random = set(SpriteListData[16])
        Clam = set(SpriteListData[17])
        Coin = set(SpriteListData[18])
        MushroomScrewPlatforms = set(SpriteListData[19])
        SpritesWithMovementIDsNyb5Type2 = set(SpriteListData[20])
        BowserFireballArea = set(SpriteListData[21])
        CheepCheepArea = set(SpriteListData[22])
        PoltergeistItem = set(SpriteListData[23])

        # Triggered by an Event
        if self.type in SpritesTriggeredByAnEventNyb1 and self.spritedata[1] != '\0':
            baseString += trans.string('Sprites', 2, '[event]', self.spritedata[1])
        elif self.type in SpritesTriggeredByAnEventNyb0 and self.spritedata[0] != '\0':
            baseString += trans.string('Sprites', 2, '[event]', self.spritedata[0])
        elif self.type in AndController:
            baseString += trans.string('Sprites', 3, '[event1]', self.spritedata[0], '[event2]', self.spritedata[2], '[event3]', self.spritedata[3], '[event4]', self.spritedata[4])
        elif self.type in OrController:
            baseString += trans.string('Sprites', 4, '[event1]', self.spritedata[0], '[event2]', self.spritedata[2], '[event3]', self.spritedata[3], '[event4]', self.spritedata[4])

        # Activates an Event
        if (self.type in SpritesThatActivateAnEvent)and (self.spritedata[1] != '\0'):
            baseString += trans.string('Sprites', 5, '[event]', self.spritedata[1])
        elif (self.type in SpritesThatActivateAnEventNyb0) and (self.spritedata[0] != '\0'):
            baseString += trans.string('Sprites', 5, '[event]', self.spritedata[0])
        elif (self.type in MultiChainer):
            baseString += trans.string('Sprites', 6, '[event1]', self.spritedata[0], '[event2]', self.spritedata[1])
        elif (self.type in Random):
            baseString += trans.string('Sprites', 7, '[event1]', self.spritedata[0], '[event2]', self.spritedata[2], '[event3]', self.spritedata[3], '[event4]', self.spritedata[4])

        # Star Coin
        if (self.type in StarCoinNumbers):
            number = (self.spritedata[4] & 15) + 1
            baseString += trans.string('Sprites', 8, '[num]', number)
        elif (self.type in Clam) and (self.spritedata[5] & 15) == 1:
            baseString += trans.string('Sprites', 9)

        # Set ID
        if self.type in SpritesWithSetIDs:
            baseString += trans.string('Sprites', 10, '[id]', self.spritedata[5] & 15)
        elif self.type in Coin and self.spritedata[2] != '\0':
            baseString += trans.string('Sprites', 11, '[id]', self.spritedata[2])

        # Movement ID (Nybble 2)
        if self.type in SpritesWithMovementIDsNyb2 and self.spritedata[2] != '\0':
            baseString += trans.string('Sprites', 12, '[id]', self.spritedata[2])
        elif self.type in MushroomScrewPlatforms and self.spritedata[2] >> 4 != '\0':
            baseString += trans.string('Sprites', 12, '[id]', self.spritedata[2] >> 4)

        # Movement ID (Nybble 3)
        if self.type in SpritesWithMovementIDsNyb3 and self.spritedata[3] >> 4 != '\0':
            baseString += trans.string('Sprites', 12, '[id]', (self.spritedata[3] >> 4))

        # Movement ID (Nybble 5)
        if self.type in SpritesWithMovementIDsNyb5 and self.spritedata[5] >> 4:
            baseString += trans.string('Sprites', 12, '[id]', (self.spritedata[5] >> 4))
        elif self.type in SpritesWithMovementIDsNyb5Type2 and self.spritedata[5] != '\0':
            baseString += trans.string('Sprites', 12, '[id]', self.spritedata[5])

        # Rotation ID
        if self.type in SpritesWithRotationIDs and self.spritedata[5] != '\0':
            baseString += trans.string('Sprites', 13, '[id]', self.spritedata[5])

        # Location ID (Nybble 5)
        if self.type in SpritesWithLocationIDsNyb5 and self.spritedata[5] != '\0':
            baseString += trans.string('Sprites', 14, '[id]', self.spritedata[5])
        elif self.type in SpritesWithLocationIDsNyb5and0xF and self.spritedata[5] & 15 != '\0':
            baseString += trans.string('Sprites', 14, '[id]', self.spritedata[5] & 15)
        elif self.type in SpritesWithLocationIDsNyb4 and self.spritedata[4] != '\0':
            baseString += trans.string('Sprites', 14, '[id]', self.spritedata[4])
        elif self.type in BowserFireballArea and self.spritedata[3] != '\0':
            baseString += trans.string('Sprites', 14, '[id]', self.spritedata[3])
        elif self.type in CheepCheepArea: # nybble 8-9
            if (((self.spritedata[3] & 0xF) << 4) | ((self.spritedata[4] & 0xF0) >> 4)) != '\0':
                baseString += trans.string('Sprites', 14, '[id]', (((self.spritedata[3] & 0xF) << 4) | ((self.spritedata[4] & 0xF0) >> 4)))
        elif self.type in PoltergeistItem and (((self.spritedata[4] & 0xF) << 4) | ((self.spritedata[5] & 0xF0) >> 4)) != '\0': # nybble 10-11
            baseString += trans.string('Sprites', 14, '[id]', (((self.spritedata[4] & 0xF) << 4) | ((self.spritedata[5] & 0xF0) >> 4)))

        # Add ')' to the end
        baseString += trans.string('Sprites', 15)

        return baseString

    def __lt__(self, other):
        # Sort by objx, then objy, then sprite type
        return (self.objx * 100000 + self.objy) * 1000 + self.type < (other.objx * 100000 + other.objy) * 1000 + other.type

    def InitializeSprite(self):
        """
        Initializes sprite and creates any auxiliary objects needed
        """
        global prefs

        type = self.type

        if type > len(Sprites): return

        self.name = Sprites[type].name
        self.setToolTip(trans.string('Sprites', 0, '[type]', self.type, '[name]', self.name))

        imgs = gamedef.getImageClasses()
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

        if (self.type in gamedef.getImageClasses()) and (self.type not in SLib.SpriteImagesLoaded):
            gamedef.getImageClasses()[self.type].loadImages()
            SLib.SpriteImagesLoaded.add(self.type)
        self.ImageObj = obj(self)

        self.UpdateDynamicSizing()
        self.UpdateRects()
        self.ChangingPos = True
        self.setPos(
            int((self.objx + self.ImageObj.xOffset) * 1.5),
            int((self.objy + self.ImageObj.yOffset) * 1.5),
            )
        self.ChangingPos = False
        if self.scene() is not None: self.scene().update()

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
        self.UpdateRects()

        self.ChangingPos = True
        self.setPos(
            int((self.objx + self.ImageObj.xOffset) * 1.5),
            int((self.objy + self.ImageObj.yOffset) * 1.5),
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
        type = self.type

        self.prepareGeometryChange()

        # Get rects
        imgRect = QtCore.QRectF(
            0, 0,
            self.ImageObj.width * 1.5,
            self.ImageObj.height * 1.5,
            )
        spriteboxRect = QtCore.QRectF(
            0, 0,
            self.ImageObj.spritebox.BoundingRect.width(),
            self.ImageObj.spritebox.BoundingRect.height(),
            )
        imgOffsetRect = imgRect.translated(
            (self.objx + self.ImageObj.xOffset) * 1.5,
            (self.objy + self.ImageObj.yOffset) * 1.5,
            )
        spriteboxOffsetRect = spriteboxRect.translated(
            (self.objx * 1.5) + self.ImageObj.spritebox.BoundingRect.topLeft().x(),
            (self.objy * 1.5) + self.ImageObj.spritebox.BoundingRect.topLeft().y(),
            )

        if SpriteImagesShown:
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
                unitedOffsetRect.topLeft().x() / 24,
                unitedOffsetRect.topLeft().y() / 24,
                unitedOffsetRect.width() / 24,
                unitedOffsetRect.height() / 24,
                )

            # BoundingRect: The sprite can only paint within
            # this area.
            self.BoundingRect = unitedRect.translated(
                self.ImageObj.spritebox.BoundingRect.topLeft().x(),
                self.ImageObj.spritebox.BoundingRect.topLeft().y(),
                )

        else:
            self.SelectionRect = QtCore.QRectF(0, 0, 24, 24)

            self.LevelRect = QtCore.QRectF(
                spriteboxOffsetRect.topLeft().x() / 24,
                spriteboxOffsetRect.topLeft().y() / 24,
                spriteboxOffsetRect.width() / 24,
                spriteboxOffsetRect.height() / 24,
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

        if change == QtWidgets.QGraphicsItem.ItemPositionChange:
            if self.scene() is None: return value
            if self.ChangingPos: return value

            if SpriteImagesShown:
                xOffset, xOffsetAdjusted = self.ImageObj.xOffset, self.ImageObj.xOffset * 1.5
                yOffset, yOffsetAdjusted = self.ImageObj.yOffset, self.ImageObj.yOffset * 1.5
            else:
                xOffset, xOffsetAdjusted = 0, 0
                yOffset, yOffsetAdjusted = 0, 0

            # snap to 24x24
            newpos = value

            # snap even further if Shift isn't held
            # but -only- if OverrideSnapping is off
            if not OverrideSnapping:
                objectsSelected = any([isinstance(thing, ObjectItem) for thing in mainWindow.CurrentSelection])
                if QtWidgets.QApplication.keyboardModifiers() == Qt.AltModifier:
                    # Alt is held; don't snap
                    newpos.setX((int((newpos.x() + 0.75) / 1.5) * 1.5))
                    newpos.setY((int((newpos.y() + 0.75) / 1.5) * 1.5))
                elif not objectsSelected and self.isSelected() and len(mainWindow.CurrentSelection) > 1:
                    # Snap to 8x8, but with the dragoffsets
                    dragoffsetx, dragoffsety = int(self.dragoffsetx), int(self.dragoffsety)
                    if dragoffsetx < -12: dragoffsetx += 12
                    if dragoffsety < -12: dragoffsety += 12
                    if dragoffsetx == 0: dragoffsetx = -12
                    if dragoffsety == 0: dragoffsety = -12
                    referenceX = int((newpos.x() + 6 + 12 + dragoffsetx - xOffsetAdjusted) / 12) * 12
                    referenceY = int((newpos.y() + 6 + 12 + dragoffsety - yOffsetAdjusted) / 12) * 12
                    newpos.setX(referenceX - (12 + dragoffsetx) + xOffsetAdjusted)
                    newpos.setY(referenceY - (12 + dragoffsety) + yOffsetAdjusted)
                elif objectsSelected and self.isSelected():
                    # Objects are selected, too; move in sync by snapping to whole blocks
                    dragoffsetx, dragoffsety = int(self.dragoffsetx), int(self.dragoffsety)
                    if dragoffsetx == 0: dragoffsetx = -24
                    if dragoffsety == 0: dragoffsety = -24
                    referenceX = int((newpos.x() + 12 + 24 + dragoffsetx - xOffsetAdjusted) / 24) * 24
                    referenceY = int((newpos.y() + 12 + 24 + dragoffsety - yOffsetAdjusted) / 24) * 24
                    newpos.setX(referenceX - (24 + dragoffsetx) + xOffsetAdjusted)
                    newpos.setY(referenceY - (24 + dragoffsety) + yOffsetAdjusted)
                else:
                    # Snap to 8x8
                    newpos.setX(int(int((newpos.x() + 6 - xOffsetAdjusted) / 12) * 12 + xOffsetAdjusted))
                    newpos.setY(int(int((newpos.y() + 6 - yOffsetAdjusted) / 12) * 12 + yOffsetAdjusted))

            x = newpos.x()
            y = newpos.y()

            # don't let it get out of the boundaries
            if x < 0: newpos.setX(0)
            if x > 24552: newpos.setX(24552)
            if y < 0: newpos.setY(0)
            if y > 12264: newpos.setY(12264)

            # update the data
            x = int(newpos.x() / 1.5 - xOffset)
            y = int(newpos.y() / 1.5 - yOffset)

            if x != self.objx or y != self.objy:
                #oldrect = self.BoundingRect
                #oldrect.translate(self.objx*1.5, self.objy*1.5)
                updRect = QtCore.QRectF(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())
                #self.scene().update(updRect.united(oldrect))
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

    def mousePressEvent(self, event):
        """
        Overrides mouse pressing events if needed for cloning
        """
        if event.button() == Qt.LeftButton:
            if QtWidgets.QApplication.keyboardModifiers() == Qt.ControlModifier:
                newitem = SpriteItem(self.type, self.objx, self.objy, self.spritedata)
                newitem.listitem = ListWidgetItem_SortsByOther(newitem, newitem.ListString())
                mainWindow.spriteList.addItem(newitem.listitem)
                Area.sprites.append(newitem)
                mainWindow.scene.addItem(newitem)
                mainWindow.scene.clearSelection()
                self.setSelected(True)
                newitem.UpdateListItem()
                SetDirty()
                return

        LevelEditorItem.mousePressEvent(self, event)

    def nearestZone(self, obj=False):
        """
        Calls a modified MapPositionToZoneID (if obj = True, it returns the actual ZoneItem object)
        """
        if not hasattr(Area, 'zones'): return None
        id = MapPositionToZoneID(Area.zones, self.objx, self.objy, True)
        if obj:
            for z in Area.zones:
                if z.id == id: return z
        else: return id

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
            aux.setVisible(SpriteImagesShown)

        # Default spritebox
        drawSpritebox = True
        spriteboxRect = QtCore.QRectF(1, 1, 22, 22)

        if SpriteImagesShown or overrideGlobals:
            self.ImageObj.paint(painter)

            drawSpritebox = self.ImageObj.spritebox.shown

            # Draw the selected-sprite-image overlay box
            if self.isSelected() and (not drawSpritebox or self.ImageObj.size != (16, 16)):
                painter.setPen(QtGui.QPen(theme.color('sprite_lines_s'), 1, Qt.DotLine))
                painter.drawRect(self.SelectionRect)
                painter.fillRect(self.SelectionRect, theme.color('sprite_fill_s'))

            # Determine the spritebox position
            if drawSpritebox:
                spriteboxRect = self.ImageObj.spritebox.RoundedRect

        # Draw the spritebox if applicable
        if drawSpritebox:
            if self.isSelected():
                painter.setBrush(QtGui.QBrush(theme.color('spritebox_fill_s')))
                painter.setPen(QtGui.QPen(theme.color('spritebox_lines_s'), 1))
            else:
                painter.setBrush(QtGui.QBrush(theme.color('spritebox_fill')))
                painter.setPen(QtGui.QPen(theme.color('spritebox_lines'), 1))
            painter.drawRoundedRect(spriteboxRect, 4, 4)

            painter.setFont(self.font)
            painter.drawText(spriteboxRect, Qt.AlignCenter, str(self.type))


    def scene(self):
        """
        Solves a small bug
        """
        return mainWindow.scene

    def delete(self):
        """
        Delete the sprite from the level
        """
        sprlist = mainWindow.spriteList
        mainWindow.UpdateFlag = True
        sprlist.takeItem(sprlist.row(self.listitem))
        mainWindow.UpdateFlag = False
        sprlist.selectionModel().clearSelection()
        Area.sprites.remove(self)
        #self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())
        self.scene().update() # The zone painters need for the whole thing to update


class EntranceItem(LevelEditorItem):
    """
    Level editor item that represents an entrance
    """
    BoundingRect = QtCore.QRectF(0, 0, 24, 24)
    RoundedRect = QtCore.QRectF(1, 1, 22, 22)
    EntranceImages = None

    class AuxEntranceItem(QtWidgets.QGraphicsItem):
        """
        Auxiliary item for drawing entrance things
        """
        BoundingRect = QtCore.QRectF(0, 0, 24, 24)
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
                self.setPos(0, -276)
                self.BoundingRect = QtCore.QRectF(0, 0, 98, 300)
            elif self.parent.enttype == 21:
                # Vine
                self.setPos(-12, -240)
                self.BoundingRect = QtCore.QRectF(0, 0, 48, 696)
            elif self.parent.enttype == 24:
                # Jumping facing left
                self.setPos(-74, -276)
                self.BoundingRect = QtCore.QRectF(0, 0, 98, 300)
            else:
                self.setPos(0, 0)
                self.BoundingRect = QtCore.QRectF(0, 0, 24, 24)

        def paint(self, painter, option, widget):
            """
            Paints the entrance aux
            """

            painter.setClipRect(option.exposedRect)
            painter.setRenderHint(QtGui.QPainter.Antialiasing)

            if self.parent.enttype == 20:
                # Jumping facing right

                path = QtGui.QPainterPath(QtCore.QPoint(12, 276))
                path.cubicTo(QtCore.QPoint(40, -24), QtCore.QPoint(50, -24), QtCore.QPoint(60, 36))
                path.lineTo(QtCore.QPoint(96, 300))

                painter.setPen(SLib.OutlinePen)
                painter.drawPath(path)

            elif self.parent.enttype == 21:
                # Vine

                # Draw the top half
                painter.setOpacity(1)
                painter.drawPixmap(0, 0, SLib.ImageCache['VineTop'])
                painter.drawTiledPixmap(12, 48, 24, 168, SLib.ImageCache['VineMid'])
                # Draw the bottom half
                # This is semi-transparent because you can't interact with it.
                painter.setOpacity(0.5)
                painter.drawTiledPixmap(12, 216, 24, 456, SLib.ImageCache['VineMid'])
                painter.drawPixmap(12, 672, SLib.ImageCache['VineBtm'])

            elif self.parent.enttype == 24:
                # Jumping facing left

                path = QtGui.QPainterPath(QtCore.QPoint(86, 276))
                path.cubicTo(QtCore.QPoint(58, -24), QtCore.QPoint(48, -24), QtCore.QPoint(38, 36))
                path.lineTo(QtCore.QPoint(2, 300))

                painter.setPen(SLib.OutlinePen)
                painter.drawPath(path)

        def boundingRect(self):
            """
            Required by Qt
            """
            return self.BoundingRect

    def __init__(self, x, y, id, destarea, destentrance, type, zone, layer, path, settings, cpd):
        """
        Creates an entrance with specific data
        """
        if EntranceItem.EntranceImages is None:
            ei = []
            src = QtGui.QPixmap('reggiedata/entrances.png')
            for i in range(18):
                ei.append(src.copy(i * 24, 0, 24, 24))
            EntranceItem.EntranceImages = ei

        LevelEditorItem.__init__(self)

        self.font = NumberFont
        self.objx = x
        self.objy = y
        self.entid = id
        self.destarea = destarea
        self.destentrance = destentrance
        self.enttype = type
        self.entzone = zone
        self.entsettings = settings
        self.entlayer = layer
        self.entpath = path
        self.listitem = None
        self.LevelRect = QtCore.QRectF(self.objx / 16, self.objy / 16, 1.5, 1.5)
        self.cpdirection = cpd

        self.setFlag(self.ItemIsMovable, not EntrancesFrozen)
        self.setFlag(self.ItemIsSelectable, not EntrancesFrozen)

        global DirtyOverride
        DirtyOverride += 1
        self.setPos(int(x * 1.5), int(y * 1.5))
        DirtyOverride -= 1

        self.aux = self.AuxEntranceItem(self)

        self.setZValue(27000)
        self.UpdateTooltip()
        self.TypeChange()

    def UpdateTooltip(self):
        """
        Updates the entrance object's tooltip
        """
        if self.enttype >= len(EntranceTypeNames):
            name = trans.string('Entrances', 1)
        else:
            name = EntranceTypeNames[self.enttype]

        if (self.entsettings & 0x80) != 0:
            destination = trans.string('Entrances', 2)
        else:
            if self.destarea == 0:
                destination = trans.string('Entrances', 3, '[id]', self.destentrance)
            else:
                destination = trans.string('Entrances', 4, '[id]', self.destentrance, '[area]', self.destarea)

        self.name = name
        self.destination = destination
        self.setToolTip(trans.string('Entrances', 0, '[ent]', self.entid, '[type]', name, '[dest]', destination))

    def ListString(self):
        """
        Returns a string that can be used to describe the entrance in a list
        """
        if self.enttype >= len(EntranceTypeNames):
            name = trans.string('Entrances', 1)
        else:
            name = EntranceTypeNames[self.enttype]

        if (self.entsettings & 0x80) != 0:
            return trans.string('Entrances', 5, '[id]', self.entid, '[name]', name, '[x]', self.objx, '[y]', self.objy)
        else:
            return trans.string('Entrances', 6, '[id]', self.entid, '[name]', name, '[x]', self.objx, '[y]', self.objy)

    def __lt__(self, other):
        return self.entid < other.entid

    def TypeChange(self):
        """
        Handles the entrance's type changing
        """

        # Determine the size and position of the entrance
        x, y, w, h = 0, 0, 1, 1
        if self.enttype in (0, 1):
            # Standing entrance
            x, w = -1, 3
        elif self.enttype in (3, 4):
            # Vertical pipe
            w = 2
        elif self.enttype in (5, 6):
            # Horizontal pipe
            h = 2

        # Now make the rects
        self.RoundedRect = QtCore.QRectF((x * 24) + 1, (y * 24) + 1, (w * 24) - 2, (h * 24) - 2)
        self.BoundingRect = QtCore.QRectF(x * 24, y * 24, w * 24, h * 24)

        # Update the aux thing
        self.aux.TypeChange()

    def paint(self, painter, option, widget):
        """
        Paints the entrance
        """
        global theme

        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        if self.isSelected():
            painter.setBrush(QtGui.QBrush(theme.color('entrance_fill_s')))
            painter.setPen(QtGui.QPen(theme.color('entrance_lines_s')))
        else:
            painter.setBrush(QtGui.QBrush(theme.color('entrance_fill')))
            painter.setPen(QtGui.QPen(theme.color('entrance_lines')))

        self.TypeChange()
        painter.drawRoundedRect(self.RoundedRect, 4, 4)

        icontype = 0
        enttype = self.enttype
        if enttype == 0 or enttype == 1: icontype = 1 # normal
        if enttype == 2: icontype = 2 # door exit
        if enttype == 3: icontype = 4 # pipe up
        if enttype == 4: icontype = 5 # pipe down
        if enttype == 5: icontype = 6 # pipe left
        if enttype == 6: icontype = 7 # pipe right
        if enttype == 8: icontype = 12 # ground pound
        if enttype == 9: icontype = 13 # sliding
        #0F/15 is unknown?
        if enttype == 16: icontype = 8 # mini pipe up
        if enttype == 17: icontype = 9 # mini pipe down
        if enttype == 18: icontype = 10 # mini pipe left
        if enttype == 19: icontype = 11 # mini pipe right
        if enttype == 20: icontype = 15 # jump out facing right
        if enttype == 21: icontype = 17 # vine entrance
        if enttype == 23: icontype = 14 # boss battle entrance
        if enttype == 24: icontype = 16 # jump out facing left
        if enttype == 27: icontype = 3 # door entrance

        painter.drawPixmap(0, 0, EntranceItem.EntranceImages[icontype])

        painter.setFont(self.font)
        painter.drawText(3, 12, str(self.entid))

    def delete(self):
        """
        Delete the entrance from the level
        """
        elist = mainWindow.entranceList
        mainWindow.UpdateFlag = True
        elist.takeItem(elist.row(self.listitem))
        mainWindow.UpdateFlag = False
        elist.selectionModel().clearSelection()
        Area.entrances.remove(self)
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
    BoundingRect = QtCore.QRectF(0, 0, 24, 24)
    SelectionRect = QtCore.QRectF(0, 0, 23, 23)
    RoundedRect = QtCore.QRectF(1, 1, 22, 22)


    def __init__(self, objx, objy, pathinfo, nodeinfo):
        """
        Creates a path node with specific data
        """

        global mainWindow
        LevelEditorItem.__init__(self)

        self.font = NumberFont
        self.objx = objx
        self.objy = objy
        self.pathid = pathinfo['id']
        self.nodeid = pathinfo['nodes'].index(nodeinfo)
        self.pathinfo = pathinfo
        self.nodeinfo = nodeinfo
        self.listitem = None
        self.LevelRect = (QtCore.QRectF(self.objx/16, self.objy/16, 24/16, 24/16))
        self.setFlag(self.ItemIsMovable, not PathsFrozen)
        self.setFlag(self.ItemIsSelectable, not PathsFrozen)

        global DirtyOverride
        DirtyOverride += 1
        self.setPos(int(objx*1.5),int(objy*1.5))
        DirtyOverride -= 1

        self.setZValue(25002)
        self.UpdateTooltip()

        # now that we're inited, set
        self.nodeinfo['graphicsitem'] = self

    def UpdateTooltip(self):
        """
        Updates the path object's tooltip
        """
        self.setToolTip(trans.string('Paths', 0, '[path]', self.pathid, '[node]', self.nodeid))

    def ListString(self):
        """
        Returns a string that can be used to describe the path in a list
        """
        return trans.string('Paths', 1, '[path]', self.pathid, '[node]', self.nodeid)

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

        # if node doesn't exist, let Reggie implode!

    def paint(self, painter, option, widget):
        """
        Paints the path
        """
        global theme

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setClipRect(option.exposedRect)

        if self.isSelected():
            painter.setBrush(QtGui.QBrush(theme.color('path_fill_s')))
            painter.setPen(QtGui.QPen(theme.color('path_lines_s')))
        else:
            painter.setBrush(QtGui.QBrush(theme.color('path_fill')))
            painter.setPen(QtGui.QPen(theme.color('path_lines')))
        painter.drawRoundedRect(self.RoundedRect, 4, 4)

        icontype = 0

        painter.setFont(self.font)
        painter.drawText(4,11,str(self.pathid))
        painter.drawText(4,9 + QtGui.QFontMetrics(self.font).height(),str(self.nodeid))
        painter.drawPoint(self.objx, self.objy)

    def delete(self):
        """
        Delete the path from the level
        """
        global mainWindow
        plist = mainWindow.pathList
        mainWindow.UpdateFlag = True
        plist.takeItem(plist.row(self.listitem))
        mainWindow.UpdateFlag = False
        plist.selectionModel().clearSelection()
        Area.paths.remove(self)
        self.pathinfo['nodes'].remove(self.nodeinfo)

        if(len(self.pathinfo['nodes']) < 1):
            Area.pathdata.remove(self.pathinfo)
            self.scene().removeItem(self.pathinfo['peline'])

        # update other nodes' IDs
        for pathnode in self.pathinfo['nodes']:
            pathnode['graphicsitem'].updateId()

        self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())



class PathEditorLineItem(LevelEditorItem):
    """
    Level editor item to draw a line between two path nodes
    """
    BoundingRect = QtCore.QRectF(0, 0, 1, 1) # compute later

    def __init__(self, nodelist):
        """
        Creates a path line with specific data
        """

        global mainWindow
        LevelEditorItem.__init__(self)

        self.font = NumberFont
        self.objx = 0
        self.objy = 0
        self.nodelist = nodelist
        self.loops = False
        self.setFlag(self.ItemIsMovable, False)
        self.setFlag(self.ItemIsSelectable, False)
        self.computeBoundRectAndPos()
        self.setZValue(25002)
        self.UpdateTooltip()

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
            xcoords.append(int(node['x']))
            ycoords.append(int(node['y']))
        self.objx = (min(xcoords) - 4)
        self.objy = (min(ycoords) - 4)

        mywidth = (8 + (max(xcoords) - self.objx)) * 1.5
        myheight = (8 + (max(ycoords) - self.objy)) * 1.5
        global DirtyOverride
        DirtyOverride += 1
        self.setPos(self.objx * 1.5, self.objy * 1.5)
        DirtyOverride -= 1
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(-4, -4, mywidth, myheight)



    def paint(self, painter, option, widget):
        """
        Paints the path lines
        """
        global theme

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setClipRect(option.exposedRect)

        color = theme.color('path_connector')
        painter.setBrush(QtGui.QBrush(color))
        painter.setPen(QtGui.QPen(color, 3, join = Qt.RoundJoin, cap = Qt.RoundCap))
        ppath = QtGui.QPainterPath()

        lines = []

        firstn = True

        snl = self.nodelist
        for j, node in enumerate(snl):
            if ((j+1) < len(snl)):
                a = QtCore.QPointF(float(snl[j]['x']*1.5) - self.x(),float(snl[j]['y']*1.5) - self.y())
                b = QtCore.QPointF(float(snl[j+1]['x']*1.5) - self.x(),float(snl[j+1]['y']*1.5) - self.y())
                lines.append(QtCore.QLineF(a, b))
            elif self.loops and (j+1) == len(snl):
                a = QtCore.QPointF(float(snl[j]['x']*1.5) - self.x(),float(snl[j]['y']*1.5) - self.y())
                b = QtCore.QPointF(float(snl[0]['x']*1.5) - self.x(),float(snl[0]['y']*1.5) - self.y())
                lines.append(QtCore.QLineF(a, b))

        painter.drawLines(lines)


    def delete(self):
        """
        Delete the line from the level
        """
        self.scene().update()



class ProgressPathItem(LevelEditorItem):
    """
    Level editor item that represents a progress path node
    """
    BoundingRect = QtCore.QRectF(0, 0, 24, 24)
    SelectionRect = QtCore.QRectF(0, 0, 23, 23)
    RoundedRect = QtCore.QRectF(1, 1, 22, 22)


    def __init__(self, objx, objy, progpathinfo, nodeinfo):
        """
        Creates a progress path node with specific data
        """

        global mainWindow
        LevelEditorItem.__init__(self)

        self.font = NumberFont
        self.objx = objx
        self.objy = objy
        self.progpathid = progpathinfo['id']
        self.nodeid = progpathinfo['nodes'].index(nodeinfo)
        self.progpathinfo = progpathinfo
        self.nodeinfo = nodeinfo
        self.listitem = None
        self.LevelRect = (QtCore.QRectF(self.objx/16, self.objy/16, 24/16, 24/16))
        self.setFlag(self.ItemIsMovable, not ProgressPathsFrozen)
        self.setFlag(self.ItemIsSelectable, not ProgressPathsFrozen)

        global DirtyOverride
        DirtyOverride += 1
        self.setPos(int(objx*1.5),int(objy*1.5))
        DirtyOverride -= 1

        self.setZValue(25002)
        self.UpdateTooltip()

        # now that we're inited, set
        self.nodeinfo['graphicsitem'] = self

    def UpdateTooltip(self):
        """
        Updates the progress path object's tooltip
        """
        self.setToolTip(trans.string('ProgPaths', (3 if self.progpathinfo['altpath'] else 2), '[path]', self.progpathid, '[node]', self.nodeid))

    def ListString(self):
        """
        Returns a string that can be used to describe the progress path in a list
        """
        return trans.string('ProgPaths', (5 if self.progpathinfo['altpath'] else 4), '[path]', self.progpathid, '[node]', self.nodeid)

    def __lt__(self, other):
        myWeight = self.progpathid * 100000 + (1 if self.progpathinfo['altpath'] else 0) * 10000 + self.nodeid
        otherWeight = other.progpathid * 100000 + (1 if other.progpathinfo['altpath'] else 0) * 10000 + other.nodeid
        return myWeight < otherWeight

    def updatePos(self):
        """
        Our x/y was changed, update pathinfo
        """
        self.progpathinfo['nodes'][self.nodeid]['x'] = self.objx
        self.progpathinfo['nodes'][self.nodeid]['y'] = self.objy

    def updateId(self):
        """
        Path was changed, find our new nodeid
        """
        # called when 1. add node 2. delete node 3. change node order
        # hacky code but it works. considering how pathnodes are stored.
        self.nodeid = self.progpathinfo['nodes'].index(self.nodeinfo)
        self.UpdateTooltip()
        self.scene().update()
        self.UpdateListItem()

        # if node doesn't exist, let Reggie implode!

    def paint(self, painter, option, widget):
        """
        Paints the progress path
        """
        global theme

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setClipRect(option.exposedRect)

        if self.isSelected():
            painter.setBrush(QtGui.QBrush(theme.color('progpath_fill_s')))
            painter.setPen(QtGui.QPen(theme.color('progpath_lines_s')))
        else:
            painter.setBrush(QtGui.QBrush(theme.color('progpath_fill')))
            painter.setPen(QtGui.QPen(theme.color('progpath_lines')))
        painter.drawRoundedRect(self.RoundedRect, 4, 4)

        painter.setFont(self.font)
        painter.drawText(4, 11, trans.string('ProgPaths', (1 if self.progpathinfo['altpath'] else 0), '[id]', self.progpathid))
        painter.drawText(4, 9 + QtGui.QFontMetrics(self.font).height(), str(self.nodeid))
        painter.drawPoint(self.objx, self.objy)

    def delete(self):
        """
        Delete the progress path from the level
        """
        global mainWindow
        plist = mainWindow.progPathList
        mainWindow.UpdateFlag = True
        plist.takeItem(plist.row(self.listitem))
        mainWindow.UpdateFlag = False
        plist.selectionModel().clearSelection()
        Area.progpaths.remove(self)
        self.progpathinfo['nodes'].remove(self.nodeinfo)

        if(len(self.progpathinfo['nodes']) < 1):
            Area.progpathdata.remove(self.progpathinfo)
            self.scene().removeItem(self.progpathinfo['peline'])

        # update other nodes' IDs
        for progpathnode in self.progpathinfo['nodes']:
            progpathnode['graphicsitem'].updateId()

        self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())



class ProgressPathEditorLineItem(LevelEditorItem):
    """
    Level editor item to draw a line between two progress path nodes
    """
    BoundingRect = QtCore.QRectF(0, 0, 1, 1) # compute later

    def __init__(self, nodelist):
        """
        Creates a progress path line with specific data
        """

        global mainWindow
        LevelEditorItem.__init__(self)

        self.font = NumberFont
        self.objx = 0
        self.objy = 0
        self.nodelist = nodelist
        self.loops = False
        self.setFlag(self.ItemIsMovable, False)
        self.setFlag(self.ItemIsSelectable, False)
        self.computeBoundRectAndPos()
        self.setZValue(25002)
        self.UpdateTooltip()

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
            xcoords.append(int(node['x']))
            ycoords.append(int(node['y']))
        self.objx = (min(xcoords) - 4)
        self.objy = (min(ycoords) - 4)

        mywidth = (8 + (max(xcoords) - self.objx)) * 1.5
        myheight = (8 + (max(ycoords) - self.objy)) * 1.5
        global DirtyOverride
        DirtyOverride += 1
        self.setPos(self.objx * 1.5, self.objy * 1.5)
        DirtyOverride -= 1
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(-4, -4, mywidth, myheight)



    def paint(self, painter, option, widget):
        """
        Paints the progress path line
        """
        global theme

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setClipRect(option.exposedRect)
        color = theme.color('progpath_connector')
        painter.setBrush(QtGui.QBrush(color))
        painter.setPen(QtGui.QPen(color, 3, join = Qt.RoundJoin, cap = Qt.RoundCap))
        ppath = QtGui.QPainterPath()

        lines = []

        firstn = True

        snl = self.nodelist
        for j, node in enumerate(snl):
            if ((j+1) < len(snl)):
                a = QtCore.QPointF(float(snl[j]['x']*1.5) - self.x(),float(snl[j]['y']*1.5) - self.y())
                b = QtCore.QPointF(float(snl[j+1]['x']*1.5) - self.x(),float(snl[j+1]['y']*1.5) - self.y())
                lines.append(QtCore.QLineF(a, b))
            elif self.loops and (j+1) == len(snl):
                a = QtCore.QPointF(float(snl[j]['x']*1.5) - self.x(),float(snl[j]['y']*1.5) - self.y())
                b = QtCore.QPointF(float(snl[0]['x']*1.5) - self.x(),float(snl[0]['y']*1.5) - self.y())
                lines.append(QtCore.QLineF(a, b))

        painter.drawLines(lines)


    def delete(self):
        """
        Delete the progress path line from the level
        """
        self.scene().update()



class CommentItem(LevelEditorItem):
    """
    Level editor item that represents a in-level comment
    """
    BoundingRect = QtCore.QRectF(-8, -8, 48, 48)
    SelectionRect = QtCore.QRectF(-4, -4, 4, 4)
    Circle = QtCore.QRectF(0, 0, 32, 32)

    def __init__(self, x, y, text=''):
        """
        Creates a in-level comment
        """
        LevelEditorItem.__init__(self)
        zval = 50000
        self.zval = zval

        self.text = text

        self.objx = x
        self.objy = y
        self.listitem = None
        self.LevelRect = (QtCore.QRectF(self.objx / 16, self.objy / 16, 2.25, 2.25))

        self.setFlag(self.ItemIsMovable, not CommentsFrozen)
        self.setFlag(self.ItemIsSelectable, not CommentsFrozen)

        global DirtyOverride
        DirtyOverride += 1
        self.setPos(int(x * 1.5), int(y * 1.5))
        DirtyOverride -= 1

        self.setZValue(zval + 1)
        self.UpdateTooltip()

        self.TextEdit = QtWidgets.QPlainTextEdit()
        self.TextEditProxy = mainWindow.scene.addWidget(self.TextEdit)
        self.TextEditProxy.setZValue(self.zval)
        self.TextEditProxy.setCursor(Qt.IBeamCursor)
        self.TextEditProxy.boundingRect = lambda self: QtCore.QRectF(0, 0, 4000, 4000)
        self.TextEdit.setVisible(False)
        self.TextEdit.setMaximumWidth(192)
        self.TextEdit.setMaximumHeight(128)
        self.TextEdit.setPlainText(self.text)
        self.TextEdit.textChanged.connect(self.handleTextChanged)
        self.reposTextEdit()


    def UpdateTooltip(self):
        """
        For compatibility, just in case
        """
        self.setToolTip(trans.string('Comments', 1, '[x]', self.objx, '[y]', self.objy))


    def ListString(self):
        """
        Returns a string that can be used to describe the comment in a list
        """
        t = self.OneLineText()
        return trans.string('Comments', 0, '[x]', self.objx, '[y]', self.objy, '[text]', t)


    def OneLineText(self):
        """
        Returns the text of this comment in a format that can be written on one line
        """
        t = str(self.text)
        if t.replace(' ', '').replace('\n', '') == '': t = trans.string('Comments', 3)
        while '\n\n' in t: t = t.replace('\n\n', '\n')
        t = t.replace('\n', trans.string('Comments', 2))

        f = None
        if self.listitem is not None: f = self.listitem.font()
        t2 = clipStr(t, 128, f)
        if t2 is not None: t = t2 + '...'

        return t


    def paint(self, painter, option, widget):
        """
        Paints the comment
        """
        global theme

        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        if self.isSelected():
            painter.setBrush(QtGui.QBrush(theme.color('comment_fill_s')))
            p = QtGui.QPen(theme.color('comment_lines_s'))
            p.setWidth(3)
            painter.setPen(p)
        else:
            painter.setBrush(QtGui.QBrush(theme.color('comment_fill')))
            p = QtGui.QPen(theme.color('comment_lines'))
            p.setWidth(3)
            painter.setPen(p)

        painter.drawEllipse(self.Circle)
        if not self.isSelected(): painter.setOpacity(.5)
        painter.drawPixmap(4, 4, GetIcon('comments', 24).pixmap(24, 24))
        painter.setOpacity(1)


        # Set the text edit visibility
        try: shouldBeVisible = (len(mainWindow.scene.selectedItems()) == 1) and self.isSelected()
        except RuntimeError: shouldBeVisible = False
        try: self.TextEdit.setVisible(shouldBeVisible)
        except RuntimeError:
            # Sometimes Qt deletes my text edit.
            # Therefore, I need to make a new one.
            self.TextEdit = QtWidgets.QPlainTextEdit()
            self.TextEditProxy = mainWindow.scene.addWidget(self.TextEdit)
            self.TextEditProxy.setZValue(self.zval)
            self.TextEditProxy.setCursor(Qt.IBeamCursor)
            self.TextEditProxy.BoundingRect = QtCore.QRectF(0, 0, 400, 400)
            self.TextEditProxy.boundingRect = lambda self: self.BoundingRect
            self.TextEdit.setMaximumWidth(192)
            self.TextEdit.setMaximumHeight(128)
            self.TextEdit.setPlainText(self.text)
            self.TextEdit.textChanged.connect(self.handleTextChanged)
            self.reposTextEdit()
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
        self.TextEditProxy.setPos((self.objx * 3/2) + 24, (self.objy * 3/2) + 16)

    def handlePosChange(self, oldx, oldy):
        """
        Handles the position changing
        """
        self.reposTextEdit()

        # Manual scene update :(
        w = 192 + 24
        h = 128 + 24
        oldx *= 1.5
        oldy *= 1.5
        oldRect = QtCore.QRectF(oldx, oldy, w, h)
        self.scene().update(oldRect)


    def delete(self):
        """
        Delete the comment from the level
        """
        clist = mainWindow.commentList
        mainWindow.UpdateFlag = True
        clist.takeItem(clist.row(self.listitem))
        mainWindow.UpdateFlag = False
        clist.selectionModel().clearSelection()
        p = self.TextEditProxy
        p.setSelected(False)
        mainWindow.scene.removeItem(p)
        Area.comments.remove(self)
        self.scene().update(self.x(), self.y(), self.BoundingRect.width(), self.BoundingRect.height())
        mainWindow.SaveComments()




class LevelOverviewWidget(QtWidgets.QWidget):
    """
    Widget that shows an overview of the level and can be clicked to move the view
    """
    moveIt = QtCore.pyqtSignal(int, int)

    def __init__(self):
        """
        Constructor for the level overview widget
        """
        global theme

        QtWidgets.QWidget.__init__(self)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding))

        self.bgbrush = QtGui.QBrush(theme.color('bg'))
        self.objbrush = QtGui.QBrush(theme.color('overview_object'))
        self.viewbrush = QtGui.QBrush(theme.color('overview_zone_fill'))
        self.view = QtCore.QRectF(0,0,0,0)
        self.spritebrush = QtGui.QBrush(theme.color('overview_sprite'))
        self.entrancebrush = QtGui.QBrush(theme.color('overview_entrance'))
        self.locationbrush = QtGui.QBrush(theme.color('overview_location_fill'))

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
        self.posmult = 24.0 / self.scale

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
        global theme

        if not hasattr(Area, 'layers'):
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
        painter.setPen(QtGui.QPen(theme.color('overview_zone_lines'), 1))

        for zone in Area.zones:
            x = zone.objx / 16
            y = zone.objy / 16
            width = zone.width / 16
            height = zone.height / 16
            fr(x, y, width, height, b)
            dr(x, y, width, height)
            if x+width > maxX:
                maxX = x+width
            if y+height > maxY:
                maxY = y+height

        b = self.objbrush

        for layer in Area.layers:
            for obj in layer:
                fr(obj.LevelRect, b)
                if obj.objx > maxX:
                    maxX = obj.objx
                if obj.objy > maxY:
                    maxY = obj.objy


        b = self.spritebrush

        for sprite in Area.sprites:
            fr(sprite.LevelRect, b)
            if sprite.objx/16 > maxX:
                maxX = sprite.objx/16
            if sprite.objy/16 > maxY:
                maxY = sprite.objy/16


        b = self.entrancebrush

        for ent in Area.entrances:
            fr(ent.LevelRect, b)
            if ent.objx/16 > maxX:
                maxX = ent.objx/16
            if ent.objy/16 > maxY:
                maxY = ent.objy/16


        b = self.locationbrush
        painter.setPen(QtGui.QPen(theme.color('overview_location_lines'), 1))

        for location in Area.locations:
            x = location.objx / 16
            y = location.objy / 16
            width = location.width / 16
            height = location.height / 16
            fr(x, y, width, height, b)
            dr(x, y, width, height)
            if x+width > maxX:
                maxX = x+width
            if y+height > maxY:
                maxY = y+height

        self.maxX = maxX
        self.maxY = maxY

        b = self.locationbrush
        painter.setPen(QtGui.QPen(theme.color('overview_viewbox'), 1))
        painter.drawRect(self.Xposlocator/24/self.mainWindowScale, self.Yposlocator/24/self.mainWindowScale, self.Wlocator/24/self.mainWindowScale, self.Hlocator/24/self.mainWindowScale)


    def Rescale(self):
        self.Xscale = (float(self.width())/float(self.maxX+45))
        self.Yscale = (float(self.height())/float(self.maxY+25))

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

        QtWidgets.QListView.__init__(self)
        self.setFlow(QtWidgets.QListView.LeftToRight)
        self.setLayoutMode(QtWidgets.QListView.SinglePass)
        self.setMovement(QtWidgets.QListView.Static)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setWrapping(True)

        self.m0 = ObjectPickerWidget.ObjectListModel()
        self.m1 = ObjectPickerWidget.ObjectListModel()
        self.m2 = ObjectPickerWidget.ObjectListModel()
        self.m3 = ObjectPickerWidget.ObjectListModel()
        self.setModel(self.m0)

        self.setItemDelegate(ObjectPickerWidget.ObjectItemDelegate())

        self.clicked.connect(self.HandleObjReplace)

    def LoadFromTilesets(self):
        """
        Renders all the object previews
        """
        self.m0.LoadFromTileset(0)
        self.m1.LoadFromTileset(1)
        self.m2.LoadFromTileset(2)
        self.m3.LoadFromTileset(3)

    def ShowTileset(self, id):
        """
        Shows a specific tileset in the picker
        """
        sel = self.currentIndex().row()
        if id == 0: self.setModel(self.m0)
        if id == 1: self.setModel(self.m1)
        if id == 2: self.setModel(self.m2)
        if id == 3: self.setModel(self.m3)
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

    ObjChanged = QtCore.pyqtSignal(int)
    ObjReplace = QtCore.pyqtSignal(int)


    class ObjectItemDelegate(QtWidgets.QAbstractItemDelegate):
        """
        Handles tileset objects and their rendering
        """

        def __init__(self):
            """
            Initializes the delegate
            """
            QtWidgets.QAbstractItemDelegate.__init__(self)

        def paint(self, painter, option, index):
            """
            Paints an object
            """
            if option.state & QtWidgets.QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())

            p = index.model().data(index, Qt.DecorationRole)
            painter.drawPixmap(option.rect.x()+2, option.rect.y()+2, p)
            #painter.drawText(option.rect, str(index.row()))

        def sizeHint(self, option, index):
            """
            Returns the size for the object
            """
            p = index.model().data(index, Qt.UserRole)
            return p
            #return QtCore.QSize(76,76)


    class ObjectListModel(QtCore.QAbstractListModel):
        """
        Model containing all the objects in a tileset
        """

        def __init__(self):
            """
            Initializes the model
            """
            self.items = []
            self.ritems = []
            self.itemsize = []
            QtCore.QAbstractListModel.__init__(self)

            #for i in range(256):
            #    self.items.append(None)
            #    self.ritems.append(None)

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

            if role == Qt.DecorationRole:
                return self.ritems[n]

            if role == Qt.BackgroundRole:
                return QtGui.qApp.palette().base()

            if role == Qt.UserRole:
                return self.itemsize[n]

            if role == Qt.ToolTipRole:
                return self.tooltips[n]

            return None

        def LoadFromTileset(self, idx):
            """
            Renders all the object previews for the model
            """
            if ObjectDefinitions[idx] is None: return

            self.beginResetModel()

            self.items = []
            self.ritems = []
            self.itemsize = []
            self.tooltips = []
            defs = ObjectDefinitions[idx]

            for i in range(256):
                if defs[i] is None: break
                obj = RenderObject(idx, i, defs[i].width, defs[i].height, True)
                self.items.append(obj)

                pm = QtGui.QPixmap(defs[i].width * 24, defs[i].height * 24)
                pm.fill(Qt.transparent)
                p = QtGui.QPainter()
                p.begin(pm)
                y = 0
                isAnim = False

                for row in obj:
                    x = 0
                    for tile in row:
                        if tile != -1:
                            if isinstance(Tiles[tile].main, QtGui.QImage):
                                p.drawImage(x, y, Tiles[tile].main)
                            else:
                                p.drawPixmap(x, y, Tiles[tile].main)
                            if isinstance(Tiles[tile], TilesetTile) and Tiles[tile].isAnimated: isAnim = True
                        x += 24
                    y += 24
                p.end()

                self.ritems.append(pm)
                self.itemsize.append(QtCore.QSize(defs[i].width * 24 + 4, defs[i].height * 24 + 4))
                if (idx == 0) and (i in ObjDesc) and isAnim:
                    self.tooltips.append(trans.string('Objects', 4, '[id]', i, '[desc]', ObjDesc[i]))
                elif (idx == 0) and (i in ObjDesc):
                    self.tooltips.append(trans.string('Objects', 3, '[id]', i, '[desc]', ObjDesc[i]))
                elif isAnim:
                    self.tooltips.append(trans.string('Objects', 2, '[id]', i))
                else:
                    self.tooltips.append(trans.string('Objects', 1, '[id]', i))

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
        QtWidgets.QListView.__init__(self)

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
            QtWidgets.QStyledItemDelegate.__init__(self)

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


class StampListModel(QtCore.QAbstractListModel):
    """
    Model containing all the stamps
    """

    def __init__(self):
        """
        Initializes the model
        """
        QtCore.QAbstractListModel.__init__(self)

        self.items = [] # list of Stamp objects

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

        if role == Qt.DecorationRole:
            return self.items[n].Icon

        elif role == Qt.BackgroundRole:
            return QtGui.qApp.palette().base()

        elif role == Qt.UserRole:
            return self.items[n].Name

        elif role == Qt.StatusTipRole:
            return self.items[n].Name

        else: return None

    def setData(self, index, value, role=Qt.DisplayRole):
        """
        Set data for a specific row
        """
        if not index.isValid(): return None
        n = index.row()
        if n < 0: return None
        if n >= len(self.items): return None

        if role == Qt.UserRole:
            self.items[n].Name = value

    def addStamp(self, stamp):
        """
        Adds a stamp
        """

        # Start resetting
        self.beginResetModel()

        # Add the stamp to self.items
        self.items.append(stamp)

        # Finish resetting
        self.endResetModel()

    def removeStamp(self, stamp):
        """
        Removes a stamp
        """

        # Start resetting
        self.beginResetModel()

        # Remove the stamp from self.items
        idx = self.items.index(stamp)
        self.items.remove(stamp)

        # Finish resetting
        self.endResetModel()


class Stamp():
    """
    Class that represents a stamp in the list
    """
    def __init__(self, ReggieClip=None, Name=''):
        """
        Initializes the stamp
        """

        self.ReggieClip = ReggieClip
        self.Name = Name
        self.Icon = self.render()

    def renderPreview(self):
        """
        Renders the stamp preview
        """

        minX, minY, maxX, maxY = 24576, 12288, 0, 0

        layers, sprites = mainWindow.getEncodedObjects(self.ReggieClip)

        # Go through the sprites and find the maxs and mins
        for spr in sprites:

            br = spr.getFullRect()

            x1 = br.topLeft().x()
            y1 = br.topLeft().y()
            x2 = x1 + br.width()
            y2 = y1 + br.height()

            if x1 < minX: minX = x1
            if x2 > maxX: maxX = x2
            if y1 < minY: minY = y1
            if y2 > maxY: maxY = y2

        # Go through the objects and find the maxs and mins
        for layer in layers:
            for obj in layer:
                x1 = (obj.objx * 24)
                x2 = x1 + (obj.width * 24)
                y1 = (obj.objy * 24)
                y2 = y1 + (obj.height * 24)

                if x1 < minX: minX = x1
                if x2 > maxX: maxX = x2
                if y1 < minY: minY = y1
                if y2 > maxY: maxY = y2

        # Calculate offset amounts (snap to 24x24 increments)
        offsetX = int(minX // 24) * 24
        offsetY = int(minY // 24) * 24
        drawOffsetX = offsetX - minX
        drawOffsetY = offsetY - minY

        # Go through the things again and shift them by the offset amount
        for spr in sprites:
            spr.objx -= offsetX / 1.5
            spr.objy -= offsetY / 1.5
        for layer in layers:
            for obj in layer:
                obj.objx -= offsetX // 24
                obj.objy -= offsetY // 24

        # Calculate the required pixmap size
        pixmapSize = (maxX - minX, maxY - minY)

        # Create the pixmap, and a painter
        pix = QtGui.QPixmap(pixmapSize[0], pixmapSize[1])
        pix.fill(Qt.transparent)
        painter = QtGui.QPainter(pix)
        painter.setRenderHint(painter.Antialiasing)

        # Paint all objects
        objw, objh = int(pixmapSize[0] // 24) + 1, int(pixmapSize[1] // 24) + 1
        for layer in reversed(layers):
            tmap = []
            for i in range(objh):
                tmap.append([-1] * objw)
            for obj in layer:
                startx = int(obj.objx)
                starty = int(obj.objy)

                desty = starty
                for row in obj.objdata:
                    destrow = tmap[desty]
                    destx = startx
                    for tile in row:
                        if tile > 0:
                            destrow[destx] = tile
                        destx += 1
                    desty += 1

                painter.save()
                desty = 0
                for row in tmap:
                    destx = 0
                    for tile in row:
                        if tile > 0:
                            if Tiles[tile] is None: continue
                            r = Tiles[tile].main
                            painter.drawPixmap(destx + drawOffsetX, desty + drawOffsetY, r)
                        destx += 24
                    desty += 24
                painter.restore()

        # Paint all sprites
        for spr in sprites:
            offx = ((spr.objx + spr.ImageObj.xOffset) * 1.5) + drawOffsetX
            offy = ((spr.objy + spr.ImageObj.yOffset) * 1.5) + drawOffsetY

            painter.save()
            painter.translate(offx, offy)

            spr.paint(painter, None, None, True)

            painter.restore()

            # Paint any auxiliary things
            for aux in spr.ImageObj.aux:
                painter.save()
                painter.translate(
                    offx + aux.x(),
                    offy + aux.y(),
                    )

                aux.paint(painter, None, None)

                painter.restore()

        # End painting
        painter.end()
        del painter

        # Scale it
        maxW, maxH = 96, 96
        w, h = pix.width(), pix.height()
        if w > h and w > maxW:
            pix = pix.scaledToWidth(maxW)
        elif h > w and h > maxH:
            pix = pix.scaledToHeight(maxH)

        # Return it
        return pix

    def render(self):
        """
        Renders the stamp icon, preview AND text
        """

        # Get the preview icon
        prevIcon = self.renderPreview()

        # Calculate the total size of the icon
        textSize = self.calculateTextSize(self.Name)
        totalWidth = max(prevIcon.width(), textSize.width())
        totalHeight = prevIcon.height() + 2 + textSize.height()

        # Make a pixmap and painter
        pix = QtGui.QPixmap(totalWidth, totalHeight)
        pix.fill(Qt.transparent)
        painter = QtGui.QPainter(pix)

        # Draw the preview
        iconWidth = prevIcon.width()
        iconXOffset = (totalWidth - prevIcon.width()) / 2
        painter.drawPixmap(iconXOffset, 0, prevIcon)

        # Draw the text
        textRect = QtCore.QRectF(0, prevIcon.height() + 2, totalWidth, textSize.height())
        painter.setFont(QtGui.QFont())
        painter.drawText(textRect, Qt.AlignTop | Qt.TextWordWrap, self.Name)

        # Return the pixmap
        return pix

    @staticmethod
    def calculateTextSize(text):
        """
        Calculates the size of text. Crops to 96 pixels wide.
        """
        fontMetrics = QtGui.QFontMetrics(QtGui.QFont())
        fontRect = fontMetrics.boundingRect(QtCore.QRect(0, 0, 96, 48), Qt.TextWordWrap, text)
        w, h = fontRect.width(), fontRect.height()
        return QtCore.QSizeF(min(w, 96), h)

    def update(self):
        """
        Updates the stamp icon
        """
        self.Icon = self.render()


class SpritePickerWidget(QtWidgets.QTreeWidget):
    """
    Widget that shows a list of available sprites
    """
    def __init__(self):
        """
        Initializes the widget
        """
        QtWidgets.QTreeWidget.__init__(self)
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

        for viewname, view, nodelist in SpriteCategories:
            for n in nodelist: nodelist.remove(n)
            for catname, category in view:
                cnode = QtWidgets.QTreeWidgetItem()
                cnode.setText(0, catname)
                cnode.setData(0, Qt.UserRole, -1)

                isSearch = (catname == trans.string('Sprites', 16))
                if isSearch:
                    self.SearchResultsCategory = cnode
                    SearchableItems = []

                for id in category:
                    snode = QtWidgets.QTreeWidgetItem()
                    if id == 9999:
                        snode.setText(0, trans.string('Sprites', 17))
                        snode.setData(0, Qt.UserRole, -2)
                        self.NoSpritesFound = snode
                    else:
                        snode.setText(0, trans.string('Sprites', 18, '[id]', id, '[name]', Sprites[id].name))
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


    def SwitchView(self, view):
        """
        Changes the selected sprite view
        """
        for i in range(1, self.topLevelItemCount()):
            self.topLevelItem(i).setHidden(True)

        for node in view[2]:
            node.setHidden(False)


    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, QtWidgets.QTreeWidgetItem)
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


    @QtCore.pyqtSlot(QtWidgets.QTreeWidgetItem, int)
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
        QtWidgets.QWidget.__init__(self)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))

        # create the raw editor
        font = QtGui.QFont()
        font.setPointSize(8)
        editbox = QtWidgets.QLabel(trans.string('SpriteDataEditor', 3))
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
        self.noteButton.setText(trans.string('SpriteDataEditor', 4))
        self.noteButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.noteButton.setAutoRaise(True)
        self.noteButton.clicked.connect(self.ShowNoteTooltip)

        self.relatedObjFilesButton = QtWidgets.QToolButton()
        self.relatedObjFilesButton.setIcon(GetIcon('data'))
        self.relatedObjFilesButton.setText(trans.string('SpriteDataEditor', 7))
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
        self.data = b'\0\0\0\0\0\0\0\0\0\0\0\0'
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

        def __init__(self):
            """
            Generic constructor
            """
            super().__init__()

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
                return (data[nybble//2] >> (0 if (nybble & 1) == 1 else 4)) & 15


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
            layout.addWidget(QtWidgets.QLabel(title+':'), row, 0, Qt.AlignRight)
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
            layout.addWidget(QtWidgets.QLabel(title+':'), row, 0, Qt.AlignRight)
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
            sprite = Sprites[type]
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
            self.spriteLabel.setText(trans.string('SpriteDataEditor', 5, '[id]', type))
            self.noteButton.setVisible(False)

            # use the raw editor if nothing is there
            self.raweditor.setVisible(True)
            if len(self.fields) > 0: self.fields = []

        else:
            self.spriteLabel.setText(trans.string('SpriteDataEditor', 6, '[id]', type, '[name]', sprite.name))

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
        self.raweditor.setText('%02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x' % (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]))
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

        self.raweditor.setText('%02x%02x %02x%02x %02x%02x %02x%02x %02x%02x %02x%02x' % (data[0], data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[8], data[9], data[10], data[11]))
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
                    data.append(int(raw[r:r+2], 16))
                data = bytes(data)
                valid = True
            except Exception: pass

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
        QtWidgets.QWidget.__init__(self)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))

        self.CanUseFlag8 = {3, 4, 5, 6, 16, 17, 18, 19}
        self.CanUseFlag4 = {3, 4, 5, 6}

        # create widgets
        self.entranceID = QtWidgets.QSpinBox()
        self.entranceID.setRange(0, 255)
        self.entranceID.setToolTip(trans.string('EntranceDataEditor', 1))
        self.entranceID.valueChanged.connect(self.HandleEntranceIDChanged)

        self.entranceType = QtWidgets.QComboBox()
        LoadEntranceNames()
        self.entranceType.addItems(EntranceTypeNames)
        self.entranceType.setToolTip(trans.string('EntranceDataEditor', 3))
        self.entranceType.activated.connect(self.HandleEntranceTypeChanged)

        self.destArea = QtWidgets.QSpinBox()
        self.destArea.setRange(0, 4)
        self.destArea.setToolTip(trans.string('EntranceDataEditor', 7))
        self.destArea.valueChanged.connect(self.HandleDestAreaChanged)

        self.destEntrance = QtWidgets.QSpinBox()
        self.destEntrance.setRange(0, 255)
        self.destEntrance.setToolTip(trans.string('EntranceDataEditor', 5))
        self.destEntrance.valueChanged.connect(self.HandleDestEntranceChanged)

        self.allowEntryCheckbox = QtWidgets.QCheckBox(trans.string('EntranceDataEditor', 8))
        self.allowEntryCheckbox.setToolTip(trans.string('EntranceDataEditor', 9))
        self.allowEntryCheckbox.clicked.connect(self.HandleAllowEntryClicked)

        self.unknownFlagCheckbox = QtWidgets.QCheckBox(trans.string('EntranceDataEditor', 10))
        self.unknownFlagCheckbox.setToolTip(trans.string('EntranceDataEditor', 11))
        self.unknownFlagCheckbox.clicked.connect(self.HandleUnknownFlagClicked)

        self.connectedPipeCheckbox = QtWidgets.QCheckBox(trans.string('EntranceDataEditor', 12))
        self.connectedPipeCheckbox.setToolTip(trans.string('EntranceDataEditor', 13))
        self.connectedPipeCheckbox.clicked.connect(self.HandleConnectedPipeClicked)

        self.connectedPipeReverseCheckbox = QtWidgets.QCheckBox(trans.string('EntranceDataEditor', 14))
        self.connectedPipeReverseCheckbox.setToolTip(trans.string('EntranceDataEditor', 15))
        self.connectedPipeReverseCheckbox.clicked.connect(self.HandleConnectedPipeReverseClicked)

        self.pathID = QtWidgets.QSpinBox()
        self.pathID.setRange(0, 255)
        self.pathID.setToolTip(trans.string('EntranceDataEditor', 17))
        self.pathID.valueChanged.connect(self.HandlePathIDChanged)

        self.forwardPipeCheckbox = QtWidgets.QCheckBox(trans.string('EntranceDataEditor', 18))
        self.forwardPipeCheckbox.setToolTip(trans.string('EntranceDataEditor', 19))
        self.forwardPipeCheckbox.clicked.connect(self.HandleForwardPipeClicked)

        self.activeLayer = QtWidgets.QComboBox()
        self.activeLayer.addItems(trans.stringList('EntranceDataEditor', 21))
        self.activeLayer.setToolTip(trans.string('EntranceDataEditor', 22))
        self.activeLayer.activated.connect(self.HandleActiveLayerChanged)

        self.cpDirection = QtWidgets.QComboBox()
        self.cpDirection.addItems(trans.stringList('EntranceDataEditor', 27))
        self.cpDirection.setToolTip(trans.string('EntranceDataEditor', 26))
        self.cpDirection.activated.connect(self.HandleCpDirectionChanged)


        # create a layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # 'Editing Entrance #' label
        self.editingLabel = QtWidgets.QLabel('-')
        layout.addWidget(self.editingLabel, 0, 0, 1, 4, Qt.AlignTop)

        # add labels
        layout.addWidget(QtWidgets.QLabel(trans.string('EntranceDataEditor', 0)), 3, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(trans.string('EntranceDataEditor', 2)), 1, 0, 1, 1, Qt.AlignRight)

        layout.addWidget(createHorzLine(), 2, 0, 1, 4)

        layout.addWidget(QtWidgets.QLabel(trans.string('EntranceDataEditor', 4)), 3, 2, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(trans.string('EntranceDataEditor', 6)), 4, 2, 1, 1, Qt.AlignRight)

        layout.addWidget(QtWidgets.QLabel(trans.string('EntranceDataEditor', 20)), 4, 0, 1, 1, Qt.AlignRight)

        self.pathIDLabel = QtWidgets.QLabel(trans.string('EntranceDataEditor', 16))
        self.cpDirectionLabel = QtWidgets.QLabel(trans.string('EntranceDataEditor', 25))

        # add the widgets
        layout.addWidget(self.entranceID, 3, 1, 1, 1)
        layout.addWidget(self.entranceType, 1, 1, 1, 3)

        layout.addWidget(self.destEntrance, 3, 3, 1, 1)
        layout.addWidget(self.destArea, 4, 3, 1, 1)
        layout.addWidget(createHorzLine(), 5, 0, 1, 4)
        layout.addWidget(self.allowEntryCheckbox, 6, 0, 1, 2)#, Qt.AlignRight)
        layout.addWidget(self.unknownFlagCheckbox, 6, 2, 1, 2)#, Qt.AlignRight)
        layout.addWidget(self.forwardPipeCheckbox, 7, 0, 1, 2)#, Qt.AlignRight)
        layout.addWidget(self.connectedPipeCheckbox, 7, 2, 1, 2)#, Qt.AlignRight)

        self.cpHorzLine = createHorzLine()
        layout.addWidget(self.cpHorzLine, 8, 0, 1, 4)
        layout.addWidget(self.connectedPipeReverseCheckbox, 9, 0, 1, 2)#, Qt.AlignRight)
        layout.addWidget(self.pathID, 9, 3, 1, 1)
        layout.addWidget(self.pathIDLabel, 9, 2, 1, 1, Qt.AlignRight)

        layout.addWidget(self.activeLayer, 4, 1, 1, 1)
        layout.addWidget(self.cpDirectionLabel, 10, 0, 1, 2, Qt.AlignRight)
        layout.addWidget(self.cpDirection, 10, 2, 1, 2)

        self.ent = None
        self.UpdateFlag = False

    @QtCore.pyqtSlot()
    def setEntrance(self, ent):
        """
        Change the entrance being edited by the editor, update all fields
        """
        if self.ent == ent: return

        self.editingLabel.setText(trans.string('EntranceDataEditor', 23, '[id]', ent.entid))
        self.ent = ent
        self.UpdateFlag = True

        self.entranceID.setValue(ent.entid)
        self.entranceType.setCurrentIndex(ent.enttype)
        self.destArea.setValue(ent.destarea)
        self.destEntrance.setValue(ent.destentrance)

        self.allowEntryCheckbox.setChecked(((ent.entsettings & 0x80) == 0))
        self.unknownFlagCheckbox.setChecked(((ent.entsettings & 2) != 0))

        self.connectedPipeCheckbox.setVisible(ent.enttype in self.CanUseFlag8)
        self.connectedPipeCheckbox.setChecked(((ent.entsettings & 8) != 0))

        self.connectedPipeReverseCheckbox.setVisible(ent.enttype in self.CanUseFlag8 and ((ent.entsettings & 8) != 0))
        self.connectedPipeReverseCheckbox.setChecked(((ent.entsettings & 1) != 0))

        self.forwardPipeCheckbox.setVisible(ent.enttype in self.CanUseFlag4)
        self.forwardPipeCheckbox.setChecked(((ent.entsettings & 4) != 0))

        self.pathID.setVisible(ent.enttype in self.CanUseFlag8 and ((ent.entsettings & 8) != 0))
        self.pathID.setValue(ent.entpath)
        self.pathIDLabel.setVisible(ent.enttype in self.CanUseFlag8 and ((ent.entsettings & 8) != 0))

        self.cpDirection.setVisible(ent.enttype in self.CanUseFlag8 and ((ent.entsettings & 8) != 0))
        self.cpDirection.setCurrentIndex(ent.cpdirection)
        self.cpDirectionLabel.setVisible(ent.enttype in self.CanUseFlag8 and ((ent.entsettings & 8) != 0))
        self.cpHorzLine.setVisible(ent.enttype in self.CanUseFlag8 and ((ent.entsettings & 8) != 0))

        self.activeLayer.setCurrentIndex(ent.entlayer)

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
        self.editingLabel.setText(trans.string('EntranceDataEditor', 23, '[id]', i))


    @QtCore.pyqtSlot(int)
    def HandleEntranceTypeChanged(self, i):
        """
        Handler for the entrance type changing
        """
        self.connectedPipeCheckbox.setVisible(i in self.CanUseFlag8)
        self.connectedPipeReverseCheckbox.setVisible(i in self.CanUseFlag8 and ((self.ent.entsettings & 8) != 0))
        self.pathIDLabel.setVisible(i and ((self.ent.entsettings & 8) != 0))
        self.pathID.setVisible(i and ((self.ent.entsettings & 8) != 0))
        self.cpDirection.setVisible(self.ent.enttype in self.CanUseFlag8 and ((self.ent.entsettings & 8) != 0))
        self.cpDirectionLabel.setVisible(self.ent.enttype in self.CanUseFlag8 and ((self.ent.entsettings & 8) != 0))
        self.cpHorzLine.setVisible(self.ent.enttype in self.CanUseFlag8 and ((self.ent.entsettings & 8) != 0))
        self.forwardPipeCheckbox.setVisible(i in self.CanUseFlag4)
        if self.UpdateFlag: return
        SetDirty()
        self.ent.enttype = i
        self.ent.TypeChange()
        self.ent.update()
        self.ent.UpdateTooltip()
        mainWindow.scene.update()
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


    @QtCore.pyqtSlot(bool)
    def HandleConnectedPipeClicked(self, checked):
        """
        Handle for the connected pipe checkbox being clicked
        """
        self.connectedPipeReverseCheckbox.setVisible(checked)
        self.pathID.setVisible(checked)
        self.pathIDLabel.setVisible(checked)
        self.cpDirection.setVisible(checked)
        self.cpDirectionLabel.setVisible(checked)
        self.cpHorzLine.setVisible(checked)
        if self.UpdateFlag: return
        SetDirty()
        if checked:
            self.ent.entsettings |= 8
        else:
            self.ent.entsettings &= ~8

    @QtCore.pyqtSlot(bool)
    def HandleConnectedPipeReverseClicked(self, checked):
        """
        Handle for the connected pipe reverse checkbox being clicked
        """
        if self.UpdateFlag: return
        SetDirty()
        if checked:
            self.ent.entsettings |= 1
        else:
            self.ent.entsettings &= ~1

    @QtCore.pyqtSlot(int)
    def HandlePathIDChanged(self, i):
        """
        Handler for the path ID changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.ent.entpath = i

    @QtCore.pyqtSlot(bool)
    def HandleForwardPipeClicked(self, checked):
        """
        Handle for the forward pipe checkbox being clicked
        """
        if self.UpdateFlag: return
        SetDirty()
        if checked:
            self.ent.entsettings |= 4
        else:
            self.ent.entsettings &= ~4

    @QtCore.pyqtSlot(int)
    def HandleActiveLayerChanged(self, i):
        """
        Handle for the active layer changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.ent.entlayer = i

    @QtCore.pyqtSlot(int)
    def HandleCpDirectionChanged(self, i):
        """
        Handle for CP Direction changing
        """
        if self.UpdateFlag: return
        SetDirty()
        self.ent.cpdirection = i



class PathNodeEditorWidget(QtWidgets.QWidget):
    """
    Widget for editing path node properties
    """

    def __init__(self, defaultmode=False):
        """
        Constructor
        """
        QtWidgets.QWidget.__init__(self)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))

        # create widgets
        #[20:52:41]  [Angel-SL] 1. (readonly) pathid 2. (readonly) nodeid 3. x 4. y 5. speed (float spinner) 6. accel (float spinner)
        #not doing [20:52:58]  [Angel-SL] and 2 buttons - 7. 'Move Up' 8. 'Move Down'
        self.speed = QtWidgets.QDoubleSpinBox()
        self.speed.setRange(min(sys.float_info), max(sys.float_info))
        self.speed.setToolTip(trans.string('PathDataEditor', 3))
        self.speed.setDecimals(int(sys.float_info.__getattribute__('dig')))
        self.speed.valueChanged.connect(self.HandleSpeedChanged)
        self.speed.setMaximumWidth(256)

        self.accel = QtWidgets.QDoubleSpinBox()
        self.accel.setRange(min(sys.float_info), max(sys.float_info))
        self.accel.setToolTip(trans.string('PathDataEditor', 5))
        self.accel.setDecimals(int(sys.float_info.__getattribute__('dig')))
        self.accel.valueChanged.connect(self.HandleAccelChanged)
        self.accel.setMaximumWidth(256)

        self.delay = QtWidgets.QSpinBox()
        self.delay.setRange(0, 65535)
        self.delay.setToolTip(trans.string('PathDataEditor', 7))
        self.delay.valueChanged.connect(self.HandleDelayChanged)
        self.delay.setMaximumWidth(256)

        self.loops = QtWidgets.QCheckBox()
        self.loops.setToolTip(trans.string('PathDataEditor', 1))
        self.loops.stateChanged.connect(self.HandleLoopsChanged)

        # create a layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # 'Editing Path #' label
        self.editingLabel = QtWidgets.QLabel('-')
        self.editingPathLabel = QtWidgets.QLabel('-')
        layout.addWidget(self.editingLabel, 3, 0, 1, 2, Qt.AlignTop)
        layout.addWidget(self.editingPathLabel, 0, 0, 1, 2, Qt.AlignTop)
        # add labels
        layout.addWidget(QtWidgets.QLabel(trans.string('PathDataEditor', 0)), 1, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(trans.string('PathDataEditor', 2)), 4, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(trans.string('PathDataEditor', 4)), 5, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(trans.string('PathDataEditor', 6)), 6, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(createHorzLine(), 2, 0, 1, 2)

        # add the widgets
        layout.addWidget(self.loops, 1, 1)
        layout.addWidget(self.speed, 4, 1)
        layout.addWidget(self.accel, 5, 1)
        layout.addWidget(self.delay, 6, 1)


        self.path = None
        self.UpdateFlag = False


    def setPath(self, path):
        """
        Change the path being edited by the editor, update all fields
        """
        if self.path == path: return
        self.editingPathLabel.setText(trans.string('PathDataEditor', 8, '[id]', path.pathid))
        self.editingLabel.setText(trans.string('PathDataEditor', 9, '[id]', path.nodeid))
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
    def HandleLoopsChanged(self, i):
        if self.UpdateFlag: return
        SetDirty()
        self.path.pathinfo['loops'] = (i == Qt.Checked)
        self.path.pathinfo['peline'].loops = (i == Qt.Checked)
        mainWindow.scene.update()



class ProgressPathNodeEditorWidget(QtWidgets.QWidget):
    """
    Widget for editing progress path node properties
    """

    def __init__(self, defaultmode=False):
        """
        Constructor
        """
        QtWidgets.QWidget.__init__(self)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))

        # create widgets
        self.progpathid = QtWidgets.QSpinBox()
        self.progpathid.setRange(1, 255) # ID 0 is not allowed in NSMB2
        self.progpathid.setToolTip(trans.string('ProgPathDataEditor', 3))
        self.progpathid.valueChanged.connect(self.HandleIDChanged)
        self.progpathid.setMaximumWidth(256)

        self.altpath = QtWidgets.QCheckBox()
        self.altpath.setToolTip(trans.string('ProgPathDataEditor', 5))
        self.altpath.stateChanged.connect(self.HandleAltPathChanged)

        # create a layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # 'Editing Progress Path #' label
        self.editingProgPathLabel = QtWidgets.QLabel('-')
        self.editingNodeLabel = QtWidgets.QLabel('-')
        layout.addWidget(self.editingProgPathLabel, 0, 0, 1, 2, Qt.AlignTop)
        layout.addWidget(self.editingNodeLabel, 4, 0, 1, 2, Qt.AlignTop)

        # add labels
        layout.addWidget(QtWidgets.QLabel(trans.string('ProgPathDataEditor', 2)), 1, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(trans.string('ProgPathDataEditor', 4)), 2, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(createHorzLine(), 3, 0, 1, 2)

        # add the widgets
        layout.addWidget(self.progpathid, 1, 1)
        layout.addWidget(self.altpath, 2, 1)


        self.progpath = None
        self.UpdateFlag = False


    def setProgPath(self, progpath):
        """
        Change the progress path being edited by the editor, update all fields
        """
        if self.progpath == progpath: return
        self.editingProgPathLabel.setText(trans.string('ProgPathDataEditor', 1, '[id]', progpath.progpathid))
        self.editingNodeLabel.setText(trans.string('ProgPathDataEditor', 6, '[id]', progpath.nodeid))
        self.progpath = progpath
        self.UpdateFlag = True

        self.progpathid.setValue(progpath.progpathinfo['id'])
        self.altpath.setChecked(progpath.progpathinfo['altpath'])

        self.UpdateFlag = False


    @QtCore.pyqtSlot(int)
    def HandleIDChanged(self, i):
        """
        Handler for the ID changing
        """
        if self.UpdateFlag: return
        SetDirty()

        # This affects ALL nodes in the progpath, so update them accordingly
        for nodedata in self.progpath.progpathinfo['nodes']:
            node = nodedata['graphicsitem']
            node.progpathinfo['id'] = i
            node.progpathid = i
            node.update()
            node.UpdateTooltip()
            node.UpdateListItem()


    @QtCore.pyqtSlot(int)
    def HandleAltPathChanged(self, i):
        if self.UpdateFlag: return
        SetDirty()
        self.progpath.progpathinfo['altpath'] = (i == Qt.Checked)

        # This affects ALL nodes in the progpath, so update them accordingly
        for nodedata in self.progpath.progpathinfo['nodes']:
            node = nodedata['graphicsitem']
            node.update()
            node.UpdateTooltip()
            node.UpdateListItem()


class IslandGeneratorWidget(QtWidgets.QWidget):
    """
    Widget for editing entrance properties
    """
    def __init__(self, defaultmode=False):
        """
        Constructor
        """
        QtWidgets.QWidget.__init__(self)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))

        # create widgets
        self.wpos = QtWidgets.QSpinBox()
        self.wpos.setRange(1, 65535)
        self.wpos.setToolTip('Width (tiles)')
        self.wpos.setValue(7)

        self.hpos = QtWidgets.QSpinBox()
        self.hpos.setRange(1, 65535)
        self.hpos.setToolTip('Height (tiles)')
        self.hpos.setValue(7)

        self.tileset = QtWidgets.QSpinBox()
        self.tileset.setRange(1, 4)
        self.tileset.setToolTip('Tileset ID')
        self.tileset.setValue(2)

        self.tstl = QtWidgets.QSpinBox()
        self.tstl.setRange(0, 65536)
        self.tstl.setToolTip('Top-left Object ID')
        self.tstl.setValue(5)

        self.tstg = QtWidgets.QSpinBox()
        self.tstg.setRange(0, 65536)
        self.tstg.setToolTip('Top Ground Object ID')
        self.tstg.setValue(0)

        self.tstr = QtWidgets.QSpinBox()
        self.tstr.setRange(0, 65536)
        self.tstr.setToolTip('Top-right Object ID')
        self.tstr.setValue(6)


        self.tsml = QtWidgets.QSpinBox()
        self.tsml.setRange(0, 65536)
        self.tsml.setToolTip('Middle-left Object ID')
        self.tsml.setValue(3)

        self.tsmf = QtWidgets.QSpinBox()
        self.tsmf.setRange(0, 65536)
        self.tsmf.setToolTip('Middle Filler Object ID')
        self.tsmf.setValue(1)

        self.tsmr = QtWidgets.QSpinBox()
        self.tsmr.setRange(0, 65536)
        self.tsmr.setToolTip('Middle-right Object ID')
        self.tsmr.setValue(4)


        self.tsbl = QtWidgets.QSpinBox()
        self.tsbl.setRange(0, 65536)
        self.tsbl.setToolTip('Bottom-left Object ID')
        self.tsbl.setValue(7)

        self.tsbm = QtWidgets.QSpinBox()
        self.tsbm.setRange(0, 65536)
        self.tsbm.setToolTip('Bottom Roof Object ID')
        self.tsbm.setValue(2)

        self.tsbr = QtWidgets.QSpinBox()
        self.tsbr.setRange(0, 65536)
        self.tsbr.setToolTip('Bottom-right Object ID')
        self.tsbr.setValue(8)


        self.midix = QtWidgets.QSpinBox()
        self.midix.setRange(0, 65536)
        self.midix.setValue(0)
        self.midix.setToolTip('Top Ground, Middle Filler and Bottom Roof \'interval\'. Set 0 to disable. The amount of tiles before a new object is created.<br><br>e.g. if you wanted a 2000t long island, the middle can be seperated into 100 20t long objects instead of 1 2000t long object.')

        self.midiy = QtWidgets.QSpinBox()
        self.midiy.setRange(0, 65536)
        self.midiy.setValue(0)
        self.midiy.setToolTip('Middle Left, Middle Filler and Middle Right \'interval\'. Set 0 to disable. The amount of tiles before a new object is created.<br><br>e.g. if you wanted a 2000t tall island, the middle can be seperated into 100 20t tall objects instead of 1 2000t tall object.')


        self.layer = QtWidgets.QSpinBox()
        self.layer.setRange(0, 2)
        self.layer.setToolTip('Layer to paint the island onto')
        self.layer.setValue(1)

        self.copyButton = QtWidgets.QPushButton('Copy to Clipboard')
        self.copyButton.setToolTip('Copies the island you specified here to the clipboard. Paste it anywhere in Reggie. (Ctrl+V)')
        self.copyButton.clicked.connect(self.HandleCopy)

        self.placeButton = QtWidgets.QPushButton('Place')
        self.placeButton.setToolTip('Places the island specified here into Reggie.')
        self.placeButton.clicked.connect(self.HandlePlace)


        # create a layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        self.editingLabel = QtWidgets.QLabel('<b>Island Generator</b>')
        layout.addWidget(self.editingLabel, 0, 0, 1, 4, Qt.AlignTop)
        # add labels

        layout.addWidget(QtWidgets.QLabel('Width:'), 1, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel('Height:'), 2, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel('Layer:'), 3, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel('Tileset ID:'), 4, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel('X Interval:'), 5, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel('Y Interval:'), 6, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(createHorzLine(), 7, 0, 1, -1)

        # add the widgets
        layout.addWidget(self.wpos, 1, 1, 1, -1)
        layout.addWidget(self.hpos, 2, 1, 1, -1)
        layout.addWidget(self.layer, 3, 1, 1, -1)
        layout.addWidget(self.tileset, 4, 1, 1, -1)
        layout.addWidget(self.midix, 5, 1, 1, -1)
        layout.addWidget(self.midiy, 6, 1, 1, -1)

        layout.addWidget(self.tstl, 8, 1, 1, 1)
        layout.addWidget(self.tstg, 8, 2, 1, 1)
        layout.addWidget(self.tstr, 8, 3, 1, 1)

        layout.addWidget(self.tsml, 9, 1, 1, 1)
        layout.addWidget(self.tsmf, 9, 2, 1, 1)
        layout.addWidget(self.tsmr, 9, 3, 1, 1)

        layout.addWidget(self.tsbl, 10, 1, 1, 1)
        layout.addWidget(self.tsbm, 10, 2, 1, 1)
        layout.addWidget(self.tsbr, 10, 3, 1, 1)

        layout.addWidget(self.copyButton, 11, 0, 1, 2)
        layout.addWidget(self.placeButton, 11, 3, 1, 2)
        self.UpdateFlag = False

    def GetClipboardString(self):
        midixwas0 = False
        midiywas0 = False
        if self.midix.value() == 0:
            self.midix.setValue(self.wpos.value())
            midixwas0 = True
        if self.midiy.value() == 0:
            self.midiy.setValue(self.hpos.value())
            midiywas0 = True
        ret = ''
        convclip = ['ReggieClip']

        # Paint the top tiles

        # Top-left tip
        convclip.append('0:%d:%d:%d:0:0:1:1' % (self.tileset.value()-1, self.tstl.value(), self.layer.value()))
        # Top Ground
        remnx = self.wpos.value() - 2
        remx = 1
        while True:
            if remnx >= self.midix.value():
                convclip.append('0:%d:%d:%d:%d:0:%d:%d' % (self.tileset.value()-1, self.tstg.value(), self.layer.value(), remx, self.midix.value(), 1))
                remnx -= self.midix.value()
                remx += self.midix.value()
            else:
                convclip.append('0:%d:%d:%d:%d:0:%d:%d' % (self.tileset.value()-1, self.tstg.value(), self.layer.value(), remx, remnx, 1))
                break

        # Top-right tip
        convclip.append('0:%d:%d:%d:%d:0:1:1' % (self.tileset.value()-1, self.tstr.value(), self.layer.value(), self.wpos.value() - 1))

        # Paint the middle tiles

        remny = self.hpos.value() -2
        remy = 1

        # Middle-left edge
        while True:
            if remny >= self.midiy.value():
                convclip.append('0:%d:%d:%d:0:%d:%d:%d' % (self.tileset.value()-1, self.tsml.value(), self.layer.value(), remy ,1, self.midiy.value()))
                remny -= self.midiy.value()
                remy += self.midiy.value()
            else:
                convclip.append('0:%d:%d:%d:0:%d:%d:%d' % (self.tileset.value()-1, self.tsml.value(), self.layer.value(), remy, 1, remny))
                break



        # Middle Filler! Hard
        fullwidt = int(math_floor((self.wpos.value()-2) / self.midix.value()))

        widtremainder = int(math_floor((self.wpos.value()-2) % self.midix.value()))

        fullvert = int(math_floor((self.hpos.value()-2) / self.midiy.value()))
        vertremainder = int(math_floor((self.hpos.value()-2) % self.midiy.value()))



        for x in range(fullwidt):
            for y in range(fullvert):
                convclip.append('0:%d:%d:%d:%d:%d:%d:%d' % (self.tileset.value()-1, self.tsmf.value(), self.layer.value(), (x*self.midix.value()) +1, (y*self.midiy.value()) +1 ,self.midix.value(), self.midiy.value()))


        # Now paint the remainders
        if vertremainder:
            remnx = self.wpos.value() - 2 - widtremainder
            remx = 1
            while True:
                if remnx >= self.midix.value():
                    convclip.append('0:%d:%d:%d:%d:%d:%d:%d' % (self.tileset.value()-1, self.tsmf.value(), self.layer.value(), remx, self.hpos.value() - 1 - vertremainder , self.midix.value(), vertremainder))
                    remnx -= self.midix.value()
                    remx += self.midix.value()

                else:
                    convclip.append('0:%d:%d:%d:%d:%d:%d:%d' % (self.tileset.value()-1, self.tsmf.value(), self.layer.value(), remx, self.hpos.value() - 1 - vertremainder, remnx, vertremainder))
                    break

        if widtremainder > 0:
            remny = self.hpos.value() - 2 - vertremainder
            remy = 1
            while True:
                if remny >= self.midiy.value():
                    convclip.append('0:%d:%d:%d:%d:%d:%d:%d' % (self.tileset.value()-1, self.tsmf.value(), self.layer.value(), self.wpos.value() - 1 - widtremainder, remy , widtremainder, self.midiy.value()))
                    remny -= self.midiy.value()
                    remy += self.midiy.value()

                else:
                    convclip.append('0:%d:%d:%d:%d:%d:%d:%d' % (self.tileset.value()-1, self.tsmf.value(), self.layer.value(), self.wpos.value() - 1 - widtremainder, remy , widtremainder, remny))
                    break

        if vertremainder and widtremainder:
            convclip.append('0:%d:%d:%d:%d:%d:%d:%d' % (self.tileset.value()-1, self.tsmf.value(), self.layer.value(), self.wpos.value() - 1 - widtremainder, self.hpos.value() - 1 - vertremainder , widtremainder, vertremainder))


        # Middle-right edge

        remny = self.hpos.value() -2
        remy = 1
        while True:
            if remny >= self.midiy.value():
                convclip.append('0:%d:%d:%d:%d:%d:%d:%d' % (self.tileset.value()-1, self.tsmr.value(), self.layer.value(), self.wpos.value() -1, remy ,1, self.midiy.value()))
                remny -= self.midiy.value()
                remy += self.midiy.value()
            else:
                convclip.append('0:%d:%d:%d:%d:%d:%d:%d' % (self.tileset.value()-1, self.tsmr.value(), self.layer.value(), self.wpos.value() -1, remy, 1, remny))
                break


        # Paint the bottom tiles

        # bottom-left tip
        convclip.append('0:%d:%d:%d:0:%d:1:1' % (self.tileset.value()-1, self.tsbl.value(), self.layer.value(), self.hpos.value() -1))
        # Bottom Roof
        remnx = self.wpos.value() - 2
        remx = 1
        while True:
            if remnx >= self.midix.value():
                convclip.append('0:%d:%d:%d:%d:%d:%d:%d' % (self.tileset.value()-1, self.tsbm.value(), self.layer.value(), remx, self.hpos.value() -1, self.midix.value(), 1))
                remnx -= self.midix.value()
                remx += self.midix.value()
            else:
                convclip.append('0:%d:%d:%d:%d:%d:%d:%d' % (self.tileset.value()-1, self.tsbm.value(), self.layer.value(), remx, self.hpos.value() -1, remnx, 1))
                break

        # Bottom-right tip
        convclip.append('0:%d:%d:%d:%d:%d:1:1' % (self.tileset.value()-1, self.tsbr.value(), self.layer.value(), self.wpos.value() - 1, self.hpos.value() -1))
        convclip.append('%')
        if midixwas0:
            self.midix.setValue(0)
        if midiywas0:
            self.midiy.setValue(0)
        return '|'.join(convclip)

    @QtCore.pyqtSlot()
    def HandleCopy(self):
        """
        Makes a copy of the island
        """
        retcb = self.GetClipboardString()
        mainWindow.actions['paste'].setEnabled(True)
        mainWindow.clipboard = retcb
        mainWindow.systemClipboard.setText(mainWindow.clipboard)


    @QtCore.pyqtSlot()
    def HandlePlace(self):
        """
        Places the island directly into the editor
        """
        retcb = self.GetClipboardString()
        mainWindow.placeEncodedObjects(retcb)



class LocationEditorWidget(QtWidgets.QWidget):
    """
    Widget for editing location properties
    """

    def __init__(self, defaultmode=False):
        """
        Constructor
        """
        QtWidgets.QWidget.__init__(self)
        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed))

        # create widgets
        self.locationID = QtWidgets.QSpinBox()
        self.locationID.setToolTip(trans.string('LocationDataEditor', 1))
        self.locationID.setRange(0, 255)
        self.locationID.valueChanged.connect(self.HandleLocationIDChanged)

        self.locationX = QtWidgets.QSpinBox()
        self.locationX.setToolTip(trans.string('LocationDataEditor', 3))
        self.locationX.setRange(16, 65535)
        self.locationX.valueChanged.connect(self.HandleLocationXChanged)

        self.locationY = QtWidgets.QSpinBox()
        self.locationY.setToolTip(trans.string('LocationDataEditor', 5))
        self.locationY.setRange(16, 65535)
        self.locationY.valueChanged.connect(self.HandleLocationYChanged)

        self.locationWidth = QtWidgets.QSpinBox()
        self.locationWidth.setToolTip(trans.string('LocationDataEditor', 7))
        self.locationWidth.setRange(1, 65535)
        self.locationWidth.valueChanged.connect(self.HandleLocationWidthChanged)

        self.locationHeight = QtWidgets.QSpinBox()
        self.locationHeight.setToolTip(trans.string('LocationDataEditor', 9))
        self.locationHeight.setRange(1, 65535)
        self.locationHeight.valueChanged.connect(self.HandleLocationHeightChanged)

        self.snapButton = QtWidgets.QPushButton(trans.string('LocationDataEditor', 10))
        self.snapButton.clicked.connect(self.HandleSnapToGrid)

        # create a layout
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)

        # 'Editing Location #' label
        self.editingLabel = QtWidgets.QLabel('-')
        layout.addWidget(self.editingLabel, 0, 0, 1, 4, Qt.AlignTop)

        # add labels
        layout.addWidget(QtWidgets.QLabel(trans.string('LocationDataEditor', 0)), 1, 0, 1, 1, Qt.AlignRight)

        layout.addWidget(createHorzLine(), 2, 0, 1, 4)

        layout.addWidget(QtWidgets.QLabel(trans.string('LocationDataEditor', 2)), 3, 0, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(trans.string('LocationDataEditor', 4)), 4, 0, 1, 1, Qt.AlignRight)

        layout.addWidget(QtWidgets.QLabel(trans.string('LocationDataEditor', 6)), 3, 2, 1, 1, Qt.AlignRight)
        layout.addWidget(QtWidgets.QLabel(trans.string('LocationDataEditor', 8)), 4, 2, 1, 1, Qt.AlignRight)

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
        self.editingLabel.setText(trans.string('LocationDataEditor', 11, '[id]', self.loc.id))


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
        self.loc.setX(int(i*1.5))
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
        self.loc.setY(int(i*1.5))
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
        right = left+loc.width
        bottom = top+loc.height

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

        loc.setPos(int(left * 1.5), int(top * 1.5))
        loc.UpdateRects()
        loc.update()
        self.setLocation(loc) # updates the fields



def LoadTheme():
    """
    Loads the theme
    """
    global theme

    id = setting('Theme')
    print('THEME ID: ' + str(id))
    if id is None: id = 'Classic'
    if id != 'Classic':

        path = str('reggiedata\\themes\\'+id).replace('\\', '/')
        with open(path, 'rb') as f:
            theme = ReggieTheme(f)
        
    else: theme = ReggieTheme()


class ReggieTheme():
    """
    Class that represents a Reggie theme
    """
    def __init__(self, file=None):
        """
        Initializes the theme
        """
        self.initAsClassic()
        if file is not None: self.initFromFile(file)


    def initAsClassic(self):
        """
        Initializes the theme as the hardcoded Classic theme
        """
        self.fileName = 'Classic'
        self.formatver = 1.0
        self.version = 1.0
        self.themeName = trans.string('Themes', 0)
        self.creator = trans.string('Themes', 1)
        self.description = trans.string('Themes', 2)
        self.iconCacheSm = {}
        self.iconCacheLg = {}
        self.style = None

        # Add the colors                                               # Descriptions:
        self.colors = {
            'bg':                       QtGui.QColor(119,136,153),     # Main scene background fill
            'comment_fill':             QtGui.QColor(220,212,135,120), # Unselected comment fill
            'comment_fill_s':           QtGui.QColor(254,240,240,240), # Selected comment fill
            'comment_lines':            QtGui.QColor(192,192,192,120), # Unselected comment lines
            'comment_lines_s':          QtGui.QColor(220,212,135,240), # Selected comment lines
            'depth_highlight':          QtGui.QColor(243,243,21,191),  # Tileset 3D effect highlight (NSMB2)
            'entrance_fill':            QtGui.QColor(190,0,0,120),     # Unselected entrance fill
            'entrance_fill_s':          QtGui.QColor(190,0,0,240),     # Selected entrance fill
            'entrance_lines':           QtGui.QColor(0,0,0),           # Unselected entrance lines
            'entrance_lines_s':         QtGui.QColor(255,255,255),     # Selected entrance lines
            'grid':                     QtGui.QColor(255,255,255,100), # Grid
            'location_fill':            QtGui.QColor(114,42,188,70),   # Unselected location fill
            'location_fill_s':          QtGui.QColor(170,128,215,100), # Selected location fill
            'location_lines':           QtGui.QColor(0,0,0),           # Unselected location lines
            'location_lines_s':         QtGui.QColor(255,255,255),     # Selected location lines
            'location_text':            QtGui.QColor(255,255,255),     # Location text
            'object_fill_s':            QtGui.QColor(255,255,255,64),  # Select object fill
            'object_lines_s':           QtGui.QColor(255,255,255),     # Selected object lines
            'overview_entrance':        QtGui.QColor(255,0,0),         # Overview entrance fill
            'overview_location_fill':   QtGui.QColor(114,42,188,50),   # Overview location fill
            'overview_location_lines':  QtGui.QColor(0,0,0),           # Overview location lines
            'overview_object':          QtGui.QColor(255,255,255),     # Overview object fill
            'overview_sprite':          QtGui.QColor(0,92,196),        # Overview sprite fill
            'overview_viewbox':         QtGui.QColor(0,0,255),         # Overview background fill
            'overview_zone_fill':       QtGui.QColor(47,79,79,120),    # Overview zone fill
            'overview_zone_lines':      QtGui.QColor(0,255,255),       # Overview zone lines
            'path_connector':           QtGui.QColor(6,249,20),        # Path node connecting lines
            'path_fill':                QtGui.QColor(6,249,20,120),    # Unselected path node fill
            'path_fill_s':              QtGui.QColor(6,249,20,240),    # Selected path node fill
            'path_lines':               QtGui.QColor(0,0,0),           # Unselected path node lines
            'path_lines_s':             QtGui.QColor(255,255,255),     # Selected path node lines
            'progpath_connector':      QtGui.QColor(255,96,0),        # Progress path node connecting lines
            'progpath_fill':           QtGui.QColor(255,96,0,120),    # Unselected progress path node fill
            'progpath_fill_s':         QtGui.QColor(255,96,0,240),    # Selected progress path node fill
            'progpath_lines':          QtGui.QColor(0,0,0),           # Unselected progress path node lines
            'progpath_lines_s':        QtGui.QColor(255,255,255),     # Selected progress path node lines
            'smi':                      QtGui.QColor(255,255,255,80),  # Sprite movement indicator
            'sprite_fill_s':            QtGui.QColor(255,255,255,64),  # Selected sprite w/ image fill
            'sprite_lines_s':           QtGui.QColor(255,255,255),     # Selected sprite w/ image lines
            'spritebox_fill':           QtGui.QColor(0,92,196,120),    # Unselected sprite w/o image fill
            'spritebox_fill_s':         QtGui.QColor(0,92,196,240),    # Selected sprite w/o image fill
            'spritebox_lines':          QtGui.QColor(0,0,0),           # Unselected sprite w/o image fill
            'spritebox_lines_s':        QtGui.QColor(255,255,255),     # Selected sprite w/o image fill
            'zone_entrance_helper':     QtGui.QColor(190,0,0,120),     # Zone entrance-placement left border indicator
            'zone_lines':               QtGui.QColor(145,200,255,176), # Zone lines
            'zone_corner':              QtGui.QColor(255,255,255),     # Zone grabbers/corners
            'zone_dark_fill':           QtGui.QColor(0,0,0,48),        # Zone fill when dark
            'zone_text':                QtGui.QColor(44,64,84),        # Zone text
            }

    def initFromFile(self, file):
        """
        Initializes the theme from the file
        """
        try:
            zipf = zipfile.ZipFile(file, 'r')
            zipfList = zipf.namelist()
        except Exception:
            # Can't load the data for some reason
            return
        try:
            mainxmlfile = zipf.open('main.xml')
        except KeyError:
            # There's no main.xml in the file
            return

        # Create a XML ElementTree
        try: maintree = etree.parse(mainxmlfile)
        except Exception: return
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
                try:
                    self.loadColorsXml(zipf.open(node.attrib['file']))
                except Exception: continue
                
            elif node.tag.lower() == 'stylesheet':
                if 'file' not in node.attrib: continue

                # Load the stylesheet
                try:
                    self.loadStylesheet(zipf.open(node.attrib['file']))
                except Exception: continue
                
            elif node.tag.lower() == 'icons':
                if not all(thing in node.attrib for thing in ['size', 'folder']): continue

                foldername = node.attrib['folder']
                big = node.attrib['size'].lower()[:2] == 'lg'
                cache = self.iconCacheLg if big else self.iconCacheSm

                # Load the icons
                for iconfilename in zipfList:
                    iconname = iconfilename
                    if not iconname.startswith(foldername + '/'): continue
                    iconname = iconname[len(foldername)+1:]
                    if len(iconname) <= len('icon-.png'): continue
                    if not iconname.startswith('icon-') or not iconname.endswith('.png'): continue
                    iconname = iconname[len('icon-'): -len('.png')]

                    icodata = zipf.open(iconfilename).read()
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
            try: self.formatver = float(formatver)
            except ValueError: return False
        else: return False

        if self.formatver > MaxSupportedXMLVersion: return False
        if 'name' in root.attrib: self.themeName = root.attrib['name']
        else: return False

        # Check for optional attributes
        self.creator = trans.string('Themes', 3)
        self.description = trans.string('Themes', 4)
        self.style = None
        self.version = 1.0
        if 'creator'     in root.attrib: self.creator = root.attrib['creator']
        if 'description' in root.attrib: self.description = root.attrib['description']
        if 'style'       in root.attrib: self.style = root.attrib['style']
        if 'version'     in root.attrib:
            try: self.version = float(root.attrib['style'])
            except ValueError: pass

        return True

    def loadColorsXml(self, file):
        """
        Loads a colors.xml file
        """
        try: tree = etree.parse(file)
        except Exception: return
        
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
            except ValueError: continue
            colorobj = QtGui.QColor(r, g, b, a)
            colorDict[colorNode.attrib['id']] = colorobj

        # Merge dictionaries
        self.colors.update(colorDict)


    def loadStylesheet(self, file):
        """
        Loads a stylesheet
        """
        print(file)

    def color(self, name):
        """
        Returns a color
        """
        return self.colors[name]

    def GetIcon(self, name, big=False):
        """
        Returns an icon
        """

        cache = self.iconCacheLg if big else self.iconCacheSm

        if name not in cache:
            path = 'reggiedata/ico/lg/icon-' if big else 'reggiedata/ico/sm/icon-'
            path += name
            cache[name] = QtGui.QIcon(path)

        return cache[name]

    def ui(self):
        """
        Returns the UI style
        """
        return self.uiStyle


# Related function
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





# Game Definitions

def LoadGameDef(name=None, dlg=None):
    """
    Loads a game definition
    """
    global gamedef
    if dlg: dlg.setMaximum(7)

    # Put the whole thing into a try-except clause
    # to catch whatever errors may happen
    try:

        # Load the gamedef
        if dlg: dlg.setLabelText(trans.string('Gamedefs', 1)) # Loading game patch...
        gamedef = ReggieGameDefinition(name)
        if gamedef.custom and (not settings.contains('GamePath_' + gamedef.name)):
            # First-time usage of this gamedef. Have the
            # user pick a stage folder so we can load stages
            # and tilesets from there
            QtWidgets.QMessageBox.information(None, trans.string('Gamedefs', 2), trans.string('Gamedefs', 3, '[game]', gamedef.name), QtWidgets.QMessageBox.Ok)
            result = mainWindow.HandleChangeGamePath(True)
            if result is not True: QtWidgets.QMessageBox.information(None, trans.string('Gamedefs', 4), trans.string('Gamedefs', 5, '[game]', gamedef.name), QtWidgets.QMessageBox.Ok)
            else: QtWidgets.QMessageBox.information(None, trans.string('Gamedefs', 6), trans.string('Gamedefs', 7, '[game]', gamedef.name), QtWidgets.QMessageBox.Ok)
        if dlg: dlg.setValue(1)

        # Load spritedata.xml and spritecategories.xml
        if dlg: dlg.setLabelText(trans.string('Gamedefs', 8)) # Loading sprite data...
        LoadSpriteData()
        LoadSpriteListData(True)
        LoadSpriteCategories(True)
        if mainWindow:
            mainWindow.spriteViewPicker.clear()
            for cat in SpriteCategories:
                mainWindow.spriteViewPicker.addItem(cat[0])
            mainWindow.sprPicker.LoadItems() # Reloads the sprite picker list items
            mainWindow.spriteViewPicker.setCurrentIndex(0) # Sets the sprite picker to category 0 (enemies)
            mainWindow.spriteDataEditor.setSprite(mainWindow.spriteDataEditor.spritetype, True) # Reloads the sprite data editor fields
            mainWindow.spriteDataEditor.update()
        if dlg: dlg.setValue(2)

        # Load BgA/BgB names
        if dlg: dlg.setLabelText(trans.string('Gamedefs', 9)) # Loading background names...
        LoadBgANames(True)
        LoadBgBNames(True)
        if dlg: dlg.setValue(3)

        # Reload tilesets
        if dlg: dlg.setLabelText(trans.string('Gamedefs', 10)) # Reloading tilesets...
        LoadObjDescriptions(True) # reloads ts1_descriptions
        if mainWindow is not None: mainWindow.ReloadTilesets(True)
        LoadTilesetNames(True) # reloads tileset names
        if dlg: dlg.setValue(4)

        # Load sprites.py
        if dlg: dlg.setLabelText(trans.string('Gamedefs', 11)) # Loading sprite image data...
        if Area is not None:
            SLib.SpritesFolders = gamedef.recursiveFiles('sprites', False, True)

            SLib.ImageCache.clear()
            SLib.SpriteImagesLoaded.clear()
            SLib.LoadBasicSuite()

            spriteClasses = gamedef.getImageClasses()

            for s in Area.sprites:
                if s.type in SLib.SpriteImagesLoaded: continue
                if s.type not in spriteClasses: continue

                spriteClasses[s.type].loadImages()

                SLib.SpriteImagesLoaded.add(s.type)

            for s in Area.sprites:
                if s.type in spriteClasses:
                    s.setImageObj(spriteClasses[s.type])
                else:
                    s.setImageObj(SLib.SpriteImage)

        if dlg: dlg.setValue(5)

        # Reload the sprite-picker text
        if dlg: dlg.setLabelText(trans.string('Gamedefs', 12)) # Applying sprite image data...
        if Area is not None:
            for spr in Area.sprites:
                spr.UpdateListItem() # Reloads the sprite-picker text
        if dlg: dlg.setValue(6)

        # Load entrance names
        if dlg: dlg.setLabelText(trans.string('Gamedefs', 16)) # Loading entrance names...
        LoadEntranceNames(True)
        if dlg: dlg.setValue(7)

    except Exception as e: raise
    #    # Something went wrong.
    #    if dlg: dlg.setValue(7) # autocloses it
    #    QtWidgets.QMessageBox.information(None, trans.string('Gamedefs', 17), trans.string('Gamedefs', 18, '[error]', str(e)))
    #    if name is not None: LoadGameDef(None)
    #    return False


    # Success!
    if dlg: setSetting('LastGameDef', name)
    return True


class ReggieGameDefinition():
    """
    A class that defines a NSMBW hack: songs, tilesets, sprites, songs, etc.
    """

    # Gamedef File - has 2 values: name (str) and patch (bool)
    class GameDefinitionFile():
        """
        A class that defines a filepath, and some options
        """
        def __init__(self, path, patch):
            """
            Initializes the GameDefinitionFile
            """
            self.path = path
            self.patch = patch

    def __init__(self, name=None):
        """
        Initializes the ReggieGameDefinition
        """
        self.InitAsEmpty()

        # Try to init it from name if possible
        NoneTypes = (None, 'None', 0, '', True, False)
        if name in NoneTypes: return
        else:
            try: self.InitFromName(name)
            except Exception: self.InitAsEmpty() # revert


    def InitAsEmpty(self):
        """
        Sets all properties to their default values
        """
        gdf = self.GameDefinitionFile

        self.custom = False
        self.base = None # gamedef to use as a base
        self.gamepath = None
        self.name = trans.string('Gamedefs', 13) # 'New Super Mario Bros. Wii'
        self.description = trans.string('Gamedefs', 14) # 'A new Mario adventure!<br>' and the date
        self.version = '2'

        self.sprites = sprites

        self.files = {
            'bga': gdf(None, False),
            'bgb': gdf(None, False),
            'entrancetypes': gdf(None, False),
            'levelnames': gdf(None, False),
            'music': gdf(None, False),
            'spritecategories': gdf(None, False),
            'spritedata': gdf(None, False),
            'spritelistdata': gdf(None, False),
            'spritenames': gdf(None, False),
            'tilesets': gdf(None, False),
            'ts1_descriptions': gdf(None, False),
            }
        self.folders = {
            'bga': gdf(None, False),
            'bgb': gdf(None, False),
            'sprites': gdf(None, False),
            }

    def InitFromName(self, name):
        """
        Attempts to open/load a Game Definition from a name string
        """
        raise NotImplementedError
        self.custom = True
        name = str(name)
        self.gamepath = name
        MaxVer = 1.0

        # Parse the file (errors are handled by __init__())
        path = 'reggiedata/games/' + name + '/main.xml'
        tree = etree.parse(path)
        root = tree.getroot()

        # Add the attributes of root: name, description, base
        if 'name' not in root.attrib: raise Exception
        self.name = root.attrib['name']

        self.description = trans.string('Gamedefs', 15)
        if 'description' in root.attrib: self.description = root.attrib['description'].replace('[', '<').replace(']', '>')
        self.version = None
        if 'version' in root.attrib: self.version = root.attrib['version']

        self.base = None
        if 'base' in root.attrib: self.base = FindGameDef(root.attrib['base'], name)
        else: self.base = ReggieGameDefinition()

        # Parse the nodes
        addpath = 'reggiedata/games/' + name + '/'
        for node in root:
            n = node.tag.lower()
            if n in ('file', 'folder'):
                path = addpath + node.attrib['path']

                if 'patch' in node.attrib:
                    patch = node.attrib['patch'].lower() == 'true' # convert to bool
                else: patch = True # DEFAULT PATCH VALUE
                if 'game' in node.attrib:
                    if node.attrib['game'] != trans.string('Gamedefs', 13): # 'New Super Mario Bros. Wii'
                        def_ = FindGameDef(node.attrib['game'], name)
                        path = 'reggiedata/games/' + def_.gamepath + '/' + node.attrib['path']
                    else:
                        path = 'reggiedata/' + node.attrib['path']

                ListToAddTo = eval('self.%ss' % n) # self.files or self.folders
                newdef = self.GameDefinitionFile(path, patch)
                ListToAddTo[node.attrib['name']] = newdef

        # Get rid of the XML stuff
        del tree, root

        # Load sprites.py if provided
        if 'sprites' in self.files:
            file = open(self.files['sprites'].path, 'r')
            filedata = file.read()
            file.close(); del file

            # https://stackoverflow.com/questions/5362771/load-module-from-string-in-python
            # with modifications
            new_module = importlib.types.ModuleType(self.name + '->sprites')
            exec(filedata, new_module.__dict__)
            sys.modules[new_module.__name__] = new_module
            self.sprites = new_module


    def bgFile(self, name, layer):
        """
        Returns the folder to a bg image. Layer must be 'a' or 'b'
        """
        # Name will be of the format '0000.png'
        fallback = 'reggiedata/bg' + layer
        filename = 'bg%s/%s' % (layer, name)


        # See if it was defined specifically
        if filename in self.files:
            path = self.files[filename].path
            if os.path.isfile(path): return path

        # See if it's in one of self.folders
        if self.folders['bg%s' % layer].path is not None:
            trypath = self.folders['bg%s' % layer].path + '/' + name
            if os.path.isfile(trypath): return trypath

        # If there's a base, return self.base.bgFile
        if self.base is not None: return self.base.bgFile(name, layer)

        # If not, return fallback
        else: return fallback + '/' + name


    def GetGamePath(self):
        """
        Returns the game path
        """
        if not self.custom: return str(setting('GamePath_NSMB2'))
        name = 'GamePath_' + self.name
        setname = setting(name)

        # Use the default if there are no settings for this yet
        if setname is None: return str(setting('GamePath_NSMB2'))
        else: return str(setname)

    def SetGamePath(self, path):
        """
        Sets the game path
        """
        if not self.custom: setSetting('GamePath_NSMB2', path)
        else:
            name = 'GamePath_' + self.name
            setSetting(name, path)

    def GetGamePaths(self):
        """
        Returns game paths of this gamedef and its bases
        """
        mainpath = str(setting('GamePath_NSMB2'))
        if not self.custom: return [mainpath,]

        name = 'GamePath_' + self.name
        stg = setting(name)
        if self.base is None:
            return [mainpath, stg]
        else:
            paths = self.base.GetGamePaths()
            paths.append(stg)
            return paths


    def GetLastLevel(self):
        """
        Returns the last loaded level
        """
        if not self.custom: return setting('LastLevel')
        name = 'LastLevel_' + self.name
        stg = setting(name)

        # Use the default if there are no settings for this yet
        if stg is None: return setting('LastLevel')
        else: return stg

    def SetLastLevel(self, path):
        """
        Sets the last loaded level
        """
        if path in (None, 'None', 'none', True, 'True', 'true', False, 'False', 'false', 0, 1, ''): return
        print('Last loaded level set to ' + str(path))
        if not self.custom: setSetting('LastLevel', path)
        else:
            name = 'LastLevel_' + self.name
            setSetting(name, path)


    def recursiveFiles(self, name, isPatch=False, folder=False):
        """
        Checks each base of this gamedef and returns a list of successive file paths
        """
        ListToCheckIn = self.files if not folder else self.folders

        # This can be handled 4 ways: if we do or don't have a base, and if we do or don't have a copy of the file.
        if self.base is None:
            if ListToCheckIn[name].path is None: # No base, no file

                if isPatch: return [], True
                else: return []

            else: # No base, file

                alist = []
                alist.append(ListToCheckIn[name].path)
                if isPatch: return alist, ListToCheckIn[name].patch
                else: return alist

        else:

            if isPatch: listUpToNow, wasPatch = self.base.recursiveFiles(name, True, folder)
            else: listUpToNow = self.base.recursiveFiles(name, False, folder)

            if ListToCheckIn[name].path is None: # Base, no file

                if isPatch: return listUpToNow, wasPatch
                else: return listUpToNow

            else: # Base, file

                # If it's a patch, just add it to the end of the list
                if ListToCheckIn[name].patch: listUpToNow.append(ListToCheckIn[name].path)

                # If it's not (it's free-standing), make a new list and start over
                else:
                    newlist = []
                    newlist.append(ListToCheckIn[name].path)
                    if isPatch: return newlist, False
                    else: return newlist

                # Return
                if isPatch: return listUpToNow, wasPatch
                else: return listUpToNow

    def multipleRecursiveFiles(self, *args):
        """
        Returns multiple recursive files in order of least recent to most recent as a list of tuples, one list per gamedef base
        """

        # This should be very simple
        # Each arg should be a file name
        if self.base is None: main = [] # start a new level
        else: main = self.base.multipleRecursiveFiles(*args)

        # Add the values from this level, and then return it
        result = []
        for name in args:
            try:
                file = self.files[name]
                if file.path is None: raise KeyError
                result.append(self.files[name])
            except KeyError: result.append(None)
        main.append(tuple(result))
        return main

    def file(self, name):
        """
        Returns a file by recursively checking successive gamedef bases
        """
        if name not in self.files: return

        if self.files[name].path is not None: return self.files[name].path
        else:
            if self.base is None: return
            return self.base.file(name) # it can recursively check its base, too

    def getImageClasses(self):
        """
        Gets all image classes
        """
        if not self.custom:
            return self.sprites.ImageClasses

        if self.base is not None:
            images = dict(self.base.getImageClasses())
        else:
            images = {}

        if hasattr(self.sprites, 'ImageClasses'):
            images.update(self.sprites.ImageClasses)
        return images



# Related functions
def GetPath(id_):
    """
    Checks the game definition and the translation and returns the appropriate path
    """
    global gamedef
    global trans

    # If there's a custom gamedef, use that
    if gamedef.custom and gamedef.file(id_) is not None: return gamedef.file(id_)
    else: return trans.path(id_)


def getMusic():
    """
    Uses the current gamedef + translation to get the music data, and returns it as a list of tuples
    """

    transsong = trans.files['music']
    gamedefsongs, isPatch = gamedef.recursiveFiles('music', True)
    if isPatch:
        paths = [transsong]
        for path in gamedefsongs: paths.append(path)
    else: paths = gamedefsongs

    songs = []
    for path in paths:
        musicfile = open(path)
        data = musicfile.read()
        musicfile.close()
        del musicfile

        # Split the data
        data = data.split('\n')
        while '' in data: data.remove('')
        for i, line in enumerate(data): data[i] = line.split(':')

        # Apply it
        for songid, name in data:
            found = False
            for song in songs:
                if song[0] == songid:
                    song[1] = name
                    found = True
            if not found:
                songs.append([songid, name])

    return sorted(songs, key=lambda song: int(song[0]))

def FindGameDef(name, skip=None):
    "Helper function to find a game def with a specific name. Skip will be skipped"""
    toSearch = [None] # Add the original game first
    for folder in os.listdir('reggiedata/games'): toSearch.append(folder)

    for folder in toSearch:
        if folder == skip: continue
        def_ = ReggieGameDefinition(folder)
        if (not def_.custom) and (folder is not None): continue
        if def_.name == name: return def_






# Translations

def LoadTranslation():
    """
    Loads the translation
    """
    global trans

    name = setting('Translation')
    eng = (None, 'None', 'English', '', 0)
    if name in eng: trans = ReggieTranslation(None)
    else: trans = ReggieTranslation(name)

    if generateStringsXML: trans.generateXML()


class ReggieTranslation():
    """
    A translation of all visible Reggie strings
    """
    def __init__(self, name):
        """
        Creates a Reggie translation
        """
        self.InitAsEnglish()

        # Try to load it from an XML
        try:
            self.InitFromXML(name)
        except Exception:
            self.InitAsEnglish()


    def InitAsEnglish(self):
        """
        Initializes the ReggieTranslation as the English translation
        """
        self.name = 'English'
        self.version = 1.0
        self.translator = 'Treeki, Tempus'

        self.files = {
            'bga': 'reggiedata/bga.txt',
            'bgb': 'reggiedata/bgb.txt',
            'entrancetypes': 'reggiedata/entrancetypes.txt',
            'levelnames': 'reggiedata/levelnames.xml',
            'music': 'reggiedata/music.txt',
            'spritecategories': 'reggiedata/spritecategories.xml',
            'spritedata': 'reggiedata/spritedata.xml',
            'tilesets': 'reggiedata/tilesets.xml',
            'ts1_descriptions': 'reggiedata/ts1_descriptions.txt',
            }

        self.strings = {
            'AboutDlg': {
                0: 'About Reggie!',
                },
            'AreaChoiceDlg': {
                0: 'Choose an Area',
                1: 'Area [num]',
                2: 'You have reached the maximum amount of areas in this level.[br]Due to the game\'s limitations, Reggie! only allows you to add up to 4 areas to a level.',
                },
            'AreaCombobox': {
                0: 'Area [num]',
                },
            'AreaDlg': {
                0: 'Area Options',
                1: 'Tilesets',
                2: 'Settings',
                3: 'Timer:',
                4: '[b]Timer:[/b][br]Sets the time limit, in "Mario seconds," for the level.[br][b]Midway Timer Info:[/b] The midway timer is calculated by subtracting 200 from this value. Because the game will use the timer setting from whatever area the midpoint is located in, it\'s possible to pick your own time limit if you put the midpoint in any area other than Area 1. Just set the time limit value for that area to the midpoint time you want + 200.',
                5: 'Entrance ID:',
                6: '[b]Entrance ID:[/b][br]Sets the entrance ID to load into when loading from the World Map',
                7: 'Wrap across Edges',
                8: '[b]Wrap across Edges:[/b][br]Makes the stage edges wrap[br]Warning: This option may cause the game to crash or behave weirdly. Wrapping only works correctly where the area is set up in the right way; see Coin Battle 1 for an example.',
                9: None, # REMOVED: 'Event [id]'
                10: None, # REMOVED: 'Default Events'
                11: 'Standard Suite',
                12: 'Stage Suite',
                13: 'Background Suite',
                14: 'Interactive Suite',
                15: 'None',
                16: '[CUSTOM]',
                17: '[CUSTOM] [name]',
                18: 'Custom filename... [name]',
                19: '[name] ([file])',
                20: 'Enter a Filename',
                21: 'Enter the name of a custom tileset file to use. It must be placed in the game\'s Stage\\Texture or Unit folder in order for Reggie to recognize it. Do not add the \'.arc\' or \'.sarc\' extension at the end of the filename.',
                22: 'Unknown Value 1:',
                23: 'Unknown Value 2:',
                24: 'Unknown Value 3:', # Currently unused
                25: '[b]Unknown Value 1:[/b] We haven\'t managed to figure out what this does, or if it does anything.',
                26: '[b]Unknown Value 2:[/b] We haven\'t managed to figure out what this does, or if it does anything.',
                27: '[b]Unknown Value 3:[/b] We haven\'t managed to figure out what this does, or if it does anything.', # Currently unused
                28: 'Name',
                29: 'File',
                30: '(None)',
                31: 'Tileset (Pa[slot]):',
                },
            'AutoSaveDlg': {
                0: 'Auto-saved backup found',
                1: 'Reggie! has found some level data which wasn\'t saved - possibly due to a crash within the editor or by your computer. Do you want to restore this level?[br][br]If you pick No, the autosaved level data will be deleted and will no longer be accessible.[br][br]Original file path: [path]',
                2: 'The level has unsaved changes in it.',
                3: 'Do you want to save them?',
                },
            'BGDlg': {
                0: 'Backgrounds',
                1: (
                    'None',
                    '0.125x',
                    '0.25x',
                    '0.375x',
                    '0.5x',
                    '0.625x',
                    '0.75x',
                    '0.875x',
                    '1x',
                    'None',
                    '1.25x',
                    '1.5x',
                    '2x',
                    '4x',
                    ),
                2: 'Zone [num]',
                3: 'Scenery',
                4: 'Backdrop',
                5: 'Position:',
                6: 'X:',
                7: '[b]Position (X):[/b][br]Sets the horizontal offset of your background',
                8: 'Y:',
                9: '[b]Position (Y):[/b][br]Sets the vertical offset of your background',
                10: 'Scroll Rate:',
                11: '[b]Scroll Rate (X):[/b][br]Changes the rate that the background moves in[br]relation to Mario when he moves horizontally.[br]Values higher than 1x may be glitchy!',
                12: '[b]Scroll Rate (Y):[/b][br]Changes the rate that the background moves in[br]relation to Mario when he moves vertically.[br]Values higher than 1x may be glitchy!',
                13: 'Zoom:',
                14: '[b]Zoom:[/b][br]Sets the zoom level of the background image',
                15: (
                    '100%',
                    '125%',
                    '150%',
                    '200%',
                    ),
                16: 'Preview',
                17: '[name] ([hex])',
                18: '(Custom)',
                19: 'Background Types:',
                20: 'Alignment Mode: This combination of backgrounds will result in "[mode]"',
                21: (
                    'Normal',
                    'Unknown 1',
                    'Unknown 2',
                    'Unknown 3',
                    'Unknown 4',
                    'Align to Screen',
                    'Unknown 5',
                    'Unknown 6',
                    ),
                },
            'ChangeGamePath': {
                0: 'Choose the Course folder from [game]',
                1: 'Error',
                2: 'This folder doesn\'t have all of the files from the extracted NSMBWii Stage folder.',
                3: 'This folder doesn\'t seem to have the required files. In order to use Reggie, you need the Stage folder from the game, including the Texture folder and the level files contained within it.',
                },
            'Comments': {
                0: '[x], [y]: [text]',
                1: '[b]Comment[/b][br]at [x], [y]',
                2: ' - ',
                3: '(empty)',
                4: '...',
                },
            'DeleteArea': {
                0: 'Are you [b]sure[/b] you want to delete this area?[br][br]The level will automatically save afterwards - there is no way[br]you can undo the deletion or get it back afterwards!',
                },
            'Diag': {
                0: 'Level Diagnostics Tool',
                1: 'This level references tilesets not used in NSMBWii.',
                2: 'Some objects in the level are not found in the tileset files.',
                3: 'There are sprites in this area which are known to cause NSMBWii to crash.',
                4: 'There are sprites in this area which have settings which are known to cause NSMBWii to crash.',
                5: 'There are too many sprites in this area.',
                6: 'There are entrances with duplicate IDs.',
                7: 'There is no start entrance in this area.',
                8: 'The start entrance is too close to the left edge of the zone.',
                9: 'An entrance is outside of a zone.',
                10: 'There are more than 8 zones in this area.',
                11: 'There are no zones in this area.',
                12: 'Some zones are positioned too close together.',
                13: 'A zone is positioned too close to the edges of this area.',
                14: 'Some zones do not have bias enabled.',
                15: 'Some zones are too large.',
                16: 'This level references backgrounds not used in NSMBWii.',
                17: 'Problems found within this area:',
                18: 'This level is:',
                19: 'Good',
                20: 'No problems were found in this area, and it should load[br]correctly in the game. If you\'re experiencing problems,[br]try running the diagnostic again in other areas.',
                21: 'Probably Good',
                22: 'There are some things in this area which may[br]cause the level to crash if you\'re not careful.[br]If you\'re experiencing problems, check[br]everything on this list, and try running this test[br]in other areas.',
                23: 'Broken',
                24: 'Problems have been found in this area which may cause[br]it to crash in-game. These problems are listed below.',
                25: 'Fix Selected Items...',
                26: 'You can select multiple items at once',
                27: 'Are you sure?',
                28: 'Are you sure you want fix these items? This [b]cannot[/b] be undone!',
                29: 'Fixing issues...',
                },
            'EntranceDataEditor': {
                0: 'ID:',
                1: '[b]ID:[/b][br]Must be different from all other IDs',
                2: 'Type:',
                3: '[b]Type:[/b][br]Sets how the entrance behaves',
                4: 'Dest. ID:',
                5: '[b]Dest. ID:[/b][br]If this entrance leads nowhere or the destination is in this area, set this to 0.',
                6: 'Dest. Area:',
                7: '[b]Dest. Area:[/b][br]If this entrance leads nowhere, set this to 0.',
                8: 'Enterable',
                9: '[b]Enterable:[/b][br]If this box is checked on a pipe or door entrance, Mario will be able to enter the pipe/door. If it\'s not checked, he won\'t be able to enter it. Behaviour on other types of entrances is unknown/undefined.',
                10: 'Unknown Flag',
                11: '[b]Unknown Flag:[/b][br]This box is checked on a few entrances in the game, but we haven\'t managed to figure out what it does (or if it does anything).',
                12: 'Connected Pipe',
                13: '[b]Connected Pipe:[/b][br]This box allows you to enable an unused/broken feature in the game. It allows the pipe to function like the pipes in SMB3 where Mario simply goes through the pipe. However, it doesn\'t work correctly.',
                14: 'Connected Pipe Reverse',
                15: '[b]Connected Pipe:[/b][br]This box allows you to enable an unused/broken feature in the game. It allows the pipe to function like the pipes in SMB3 where Mario simply goes through the pipe. However, it doesn\'t work correctly.',
                16: 'Path ID:',
                17: '[b]Path ID:[/b][br]Use this option to set the path number that the connected pipe will follow.',
                18: 'Links to Forward Pipe',
                19: '[b]Links to Forward Pipe:[/b][br]If this option is set on a pipe, the destination entrance/area values will be ignored - Mario will pass through the pipe and then reappear several tiles ahead, coming out of a forward-facing pipe.',
                20: 'Layer:',
                21: ('Layer 1', 'Layer 2', 'Layer 0'),
                22: '[b]Layer:[/b][br]Allows you to change the collision layer which this entrance is active on. This option is very glitchy and not used in the default levels - for almost all normal cases, you will want to use layer 1.',
                23: '[b]Entrance [id]:[/b]',
                24: 'Modify Selected Entrance Properties',
                25: 'CP Exit Direction:',
                26: '[b]CP Exit Direction:[/b][br]Set the direction the player will exit out of a connected pipe.',
                27: (
                    'Up',
                    'Down',
                    'Left',
                    'Right',
                    ),
                28: '([id]) [name]',
                },
            'Entrances': {
                0: '[b]Entrance [ent]:[/b][br]Type: [type][br][i][dest][/i]',
                1: 'Unknown',
                2: '(cannot be entered)',
                3: '(arrives at entrance [id] in this area)',
                4: '(arrives at entrance [id] in area [area])',
                5: '[id]: [name] (cannot be entered) at [x], [y]',
                6: '[id]: [name] (enterable) at [x], [y]'
                },
            'Err_BrokenSpriteData': {
                0: 'Warning',
                1: 'The sprite data file didn\'t load correctly. The following sprites have incorrect and/or broken data in them, and may not be editable correctly in the editor: [sprites]',
                2: 'Errors',
                },
            'Err_CantFindLevel': {
                0: 'Could not find file:[br][name]',
                },
            'Err_CorruptedTileset': {
                0: 'Error',
                1: 'An error occurred while trying to load [file].arc. Check your Unit folder to make sure it is complete and not corrupted. The editor may run in a broken state or crash after this.',
                },
            'Err_CorruptedTilesetData': {
                0: 'Error',
                1: 'Cannot find the required texture within the tileset file [file].arc, so it will not be loaded. Keep in mind that the tileset file cannot be renamed without changing the names of the texture/object files within the archive as well!',
                },
            'Err_InvalidLevel': {
                0: 'This file doesn\'t seem to be a valid level.',
                },
            'Err_MissingFiles': {
                0: 'Error',
                1: 'Sorry, you seem to be missing the required data files for Reggie! to work. Please redownload your copy of the editor.',
                2: 'Sorry, you seem to be missing some of the required data files for Reggie! to work. Please redownload your copy of the editor. These are the files you are missing: [files]',
                },
            'Err_MissingLevel': {
                0: 'Error',
                1: 'Cannot find the required level file [file].arc. Check your Stage folder and make sure it exists.',
                },
            'Err_MissingTileset': {
                0: 'Error',
                1: 'Cannot find the required tileset file [file].arc. Check your Stage folder and make sure it exists.',
                },
            'Err_Save': {
                0: 'Error',
                1: 'Error while Reggie was trying to save the level:[br](#[err1]) [err2][br][br](Your work has not been saved! Try saving it under a different filename or in a different folder.)',
                },
            'FileDlgs': {
                0: 'Choose a level archive',
                1: 'NSMB2 Level Archives',
                2: 'All Files',
                3: 'Choose a new filename',
                4: 'Portable Network Graphics',
                5: 'Compressed Level Archives',
                6: 'Choose a stamp archive',
                7: 'Stamps File',
                },
            'Gamedefs': {
                0: 'This game has custom sprite images',
                1: 'Loading patch...',
                2: 'New Game Patch',
                3: 'It appears that this is your first time using the game patch for [game]. Please select its Stage folder so custom tilesets and levels can be loaded.',
                4: 'Aborted Game Path Selection',
                5: 'Since you did not select the stage folder for [game], stages and tilesets will not load correctly. You can try again by choosing Change Game Path while the [game] patch is loaded.',
                6: 'New Game Patch',
                7: 'You can change the game path for [game] at any time by choosing Change Game Path while the [game] patch is loaded.',
                8: 'Loading sprite data...',
                9: 'Loading background names...',
                10: 'Reloading tilesets...',
                11: 'Loading sprite image data...',
                12: 'Applying sprite image data...',
                13: 'New Super Mario Bros. 2',
                14: '(insert catchphrase here)[br]Published by Nintendo in August 2012.',
                15: '[i]No description[/i]',
                16: 'Loading entrance names...',
                17: 'Error',
                18: 'An error occurred while attempting to load this game patch. It will now be unloaded. Here\'s the specific error:[br][error]',
                },
            'InfoDlg': {
                0: 'Level Information',
                1: 'Add/Change Password',
                2: 'This level\'s information is locked.[br]Please enter the password below in order to modify it.',
                3: 'Password:',
                4: 'Title:',
                5: 'Author:',
                6: 'Group:',
                7: 'Website:',
                8: 'Created with [name]',
                9: 'Change Password',
                10: 'New Password:',
                11: 'Verify Password:',
                12: 'Level Information',
                13: 'Password may be composed of any ASCII character,[br]and up to 64 characters long.[br]',
                14: 'Sorry![br][br]You can only view or edit Level Information in Area 1.',
                },
            'LocationDataEditor': {
                0: 'ID:',
                1: '[b]ID:[/b][br]Must be different from all other IDs',
                2: 'X Pos:',
                3: '[b]X Pos:[/b][br]Specifies the X position of the location',
                4: 'Y Pos:',
                5: '[b]Y Pos:[/b][br]Specifies the Y position of the location',
                6: 'Width:',
                7: '[b]Width:[/b][br]Specifies the width of the location',
                8: 'Height:',
                9: '[b]Height:[/b][br]Specifies the height of the location',
                10: 'Snap to Grid',
                11: '[b]Location [id]:[/b]',
                12: 'Modify Selected Location Properties',
                },
            'Locations': {
                0: '[id]',
                1: '', # REMOVED: 'Paint New Location'
                2: '[id]: [width]x[height] at [x], [y]',
                },
            'MainWindow': {
                0: '[unsaved]',
                1: 'You\'re trying to paste over 300 items at once.[br]This may take a while (depending on your computer speed), are you sure you want to continue?',
                },
            'Menubar': {
                0: '&File',
                1: '&Edit',
                2: '&View',
                3: '&Settings',
                4: '&Help',
                5: 'Editor Toolbar',
                },
            'MenuItems': {
                0: 'New Level',
                1: 'Create a new, blank level',
                2: 'Open Level by Name...',
                3: 'Open a level based on its in-game world/number',
                4: 'Open Level by File...',
                5: 'Open a level based on its filename',
                6: 'Recent Files',
                7: 'Open a level from a list of recently opened levels',
                8: 'Save Level',
                9: 'Save the level back to the archive file',
                10: 'Save Level As...',
                11: 'Save a level with a new filename',
                12: 'Level Information...',
                13: 'Add title and author information to the level\'s metadata',
                14: 'Level Screenshot...',
                15: 'Take a full size screenshot of your level for you to share',
                16: 'Change Game Path...',
                17: 'Set a different folder to load the game files from',
                18: 'Reggie! Preferences...',
                19: 'Change important Reggie! settings',
                20: 'Exit Reggie!',
                21: 'Exit the editor',
                22: 'Select All',
                23: 'Select all items in this area',
                24: 'Deselect',
                25: 'Deselect all currently selected items',
                26: 'Cut',
                27: 'Cut out the current selection to the clipboard',
                28: 'Copy',
                29: 'Copy the current selection to the clipboard',
                30: 'Paste',
                31: 'Paste items from the clipboard',
                32: 'Shift Items...',
                33: 'Move all selected items by an offset',
                34: 'Merge Locations',
                35: 'Merge selected locations into a single large location',
                36: 'Level Diagnostics Tool...',
                37: 'Find and fix problems with the level',
                38: 'Freeze\\nObjects',
                39: 'Make objects non-selectable',
                40: 'Freeze\\nSprites',
                41: 'Make sprites non-selectable',
                42: 'Freeze Entrances',
                43: 'Make entrances non-selectable',
                44: 'Freeze\\nLocations',
                45: 'Make locations non-selectable',
                46: 'Freeze Paths',
                47: 'Make paths non-selectable',
                48: 'Layer 0',
                49: 'Toggle viewing of object layer 0',
                50: 'Layer 1',
                51: 'Toggle viewing of object layer 1',
                52: 'Layer 2',
                53: 'Toggle viewing of object layer 2',
                54: 'Show Sprites',
                55: 'Toggle viewing of sprites',
                56: 'Show Sprite Images',
                57: 'Toggle viewing of sprite images',
                58: 'Show Locations',
                59: 'Toggle viewing of locations',
                60: 'Switch\\nGrid',
                61: 'Cycle through available grid views',
                62: 'Zoom to Maximum',
                63: 'Zoom in all the way',
                64: 'Zoom In',
                65: 'Zoom into the main level view',
                66: 'Zoom 100%',
                67: 'Show the level at the default zoom',
                68: 'Zoom Out',
                69: 'Zoom out of the main level view',
                70: 'Zoom to Minimum',
                71: 'Zoom out all the way',
                72: 'Area\\nSettings...',
                73: 'Control tileset swapping, stage timer, entrance on load, and stage wrap',
                74: 'Zone\\nSettings...',
                75: 'Zone creation, deletion, and preference editing',
                76: 'Backgrounds...',
                77: 'Apply backgrounds to individual zones in the current area',
                78: 'Add New Area',
                79: 'Add a new area (sublevel) to this level',
                80: 'Import Area from Level...',
                81: 'Import an area (sublevel) from another level file',
                82: 'Delete Current Area...',
                83: 'Delete the area (sublevel) currently open from the level',
                84: 'Reload Tilesets',
                85: 'Reload the tileset data files, including any changes made since the level was loaded',
                86: 'About Reggie!',
                87: 'Info about the program, and the team behind it',
                88: 'Help Contents...',
                89: 'Help documentation for the needy newbie',
                90: 'Reggie! Tips...',
                91: 'Tips and controls for beginners and power users',
                92: 'About PyQt...',
                93: 'About the Qt library Reggie! is based on',
                94: 'Level Overview',
                95: 'Show or hide the Level Overview window',
                96: 'Palette',
                97: 'Show or hide the Palette window',
                98: 'Change Game',
                99: 'Change the currently loaded Reggie! game patch',
                100: 'Island Generator',
                101: 'Show or hide the Island Generator window',
                102: None, # REMOVED: 'Stamp Pad'
                103: None, # REMOVED: 'Show or hide the Stamp Pad window'
                104: 'Swap Objects\' Tileset',
                105: 'Swaps the tileset of objects using a certain tileset',
                106: 'Swap Objects\' Type',
                107: 'Swaps the type of objects of a certain type',
                108: 'Tileset Animations',
                109: 'Play tileset animations if they exist (may cause a slowdown)',
                110: 'Tileset Collisions',
                111: 'View tileset collisions for existing objects',
                112: 'Open Level...',
                113: None, # This keeps the even-odd pattern going, since 112 uses description 3
                114: 'Freeze Comments',
                115: 'Make comments non-selectable',
                116: 'Show Comments',
                117: 'Toggle viewing of comments',
                118: 'Real View',
                119: 'Show special effects present in the level',
                120: 'Check for Updates...',
                121: 'Check if any updates for Reggie! Next are available to download',
                122: 'Highlight 3D Effects',
                123: 'Toggle viewing of 3D depth effect highlighting (NSMB2 only)',
                124: 'Freeze\\nProgress Paths',
                125: 'Make progress paths non-selectable',
                },
            'Objects': {
                0: '[b]Tileset [tileset], object [obj]:[/b][br][width]x[height] on layer [layer]',
                1: 'Object [id]',
                2: 'Object [id][br][i]This object is animated[/i]',
                3: '[b]Object [id]:[/b][br][desc]',
                4: '[b]Object [id]:[/b][br][desc][br][i]This object is animated[/i]',
                },
            'OpenFromNameDlg': {
                0: 'Choose Level',
                },
            'Palette': {
                0: 'Paint on Layer:',
                1: '[b]Layer 0:[/b][br]This layer is mostly used for hidden caves, but can also be used to overlay tiles to create effects. The flashlight effect will occur if Mario walks behind a tile on layer 0 and the zone has it enabled.[br]This layer is not supported in New Super Mario Bros. 2.[br][b]Note:[/b] To switch objects on other layers to this layer, select them and then click this button while holding down the [i]Alt[/i] key.',
                2: '[b]Layer 1:[/b][br]All or most of your normal level objects should be placed on this layer. This is the only layer where tile interactions (solids, slopes, etc) will work.[br][b]Note:[/b] To switch objects on other layers to this layer, select them and then click this button while holding down the [i]Alt[/i] key.',
                3: '[b]Layer 2:[/b][br]Background/wall tiles (such as those in the hidden caves) should be placed on this layer. Tiles on layer 2 have no effect on collisions.[br][b]Note:[/b] To switch objects on other layers to this layer, select them and then click this button while holding down the [i]Alt[/i] key.',
                4: 'View:',
                5: 'Search:',
                6: 'Set Default Properties',
                7: 'Default Properties',
                8: 'Entrances currently in this area:[br](Double-click one to jump to it instantly)',
                9: 'Path nodes currently in this area:[br](Double-click one to jump to it instantly)[br]To delete a path, remove all its nodes one by one.[br]To add new paths, hit the button below and right click.',
                10: 'Deselect (then right click for new path)',
                11: 'Sprites currently in this area:[br](Double-click one to jump to it instantly)',
                12: 'Locations currently in this area:[br](Double-click one to jump to it instantly)',
                13: 'Objects',
                14: 'Sprites',
                15: 'Entrances',
                16: 'Locations',
                17: 'Paths',
                18: 'Events',
                19: 'Stamps',
                20: 'Event states upon level launch:[br](Click on one to add a note)',
                21: 'Note:',
                22: 'State',
                23: 'Notes',
                24: 'Event [id]',
                25: 'Add',
                26: 'Current',
                27: 'Available stamps:',
                28: 'Add',
                29: 'Remove',
                30: 'Tools',
                31: 'Open Set...',
                32: 'Save Set As...',
                33: 'Comments',
                34: 'Comments currently in this area:[br](Double-click one to jump to it instantly)',
                35: 'Name:',
                36: 'Progress Paths',
                37: 'Progress Path nodes currently in this area:[br](Double-click one to jump to it instantly)[br]To delete a progress path, remove all its nodes one by one.[br]To add new progress paths, hit the button below and right click.',
                38: 'Deselect (then right click for new progress path)',
                },
            'PathDataEditor': {
                0: 'Loops:',
                1: '[b]Loops:[/b][br]Anything following this path will wait for any delay set at the last node and then proceed back in a straight line to the first node, and continue.',
                2: 'Speed:',
                3: '[b]Speed:[/b][br]Unknown unit. Mess around and report your findings!',
                4: 'Accel:',
                5: '[b]Accel:[/b][br]Unknown unit. Mess around and report your findings!',
                6: 'Delay:',
                7: '[b]Delay:[/b][br]Amount of time to stop here (at this node) before continuing to next node. Unit is 1/60 of a second (60 for 1 second)',
                8: '[b]Path [id][/b]',
                9: '[b]Node [id][/b]',
                10: 'Modify Selected Path Node Properties',
                },
            'Paths': {
                0: '[b]Path [path][/b][br]Node [node]',
                1: 'Path [path], Node [node]',
                },
            'PrefsDlg': {
                0: 'Reggie! Preferences',
                1: 'General',
                2: 'Toolbar',
                3: 'Themes',
                4: '[b]Reggie! Preferences[/b][br]Customize Reggie! by changing these settings.[br]Use the tabs below to view even more settings.[br]Reggie! must be restarted before certain changes can take effect.',
                5: '[b]Toolbar Preferences[/b][br]Choose menu items you would like to appear on the toolbar.[br]Reggie! must be restarted before the toolbar can be updated.[br]',
                6: '[b]Reggie! Themes[/b][br]Pick a theme below to change application colors and icons.[br]You can download more themes at [a href="rvlution.net"]rvlution.net[/a].[br]Reggie! must be restarted before the theme can be changed.',
                7: 'Show the splash screen:',
                8: 'If TPLLib cannot use a fast backend (recommended)',
                9: 'Always',
                10: 'Never',
                11: 'Menu format:',
                12: 'Use the ribbon',
                13: 'Use the menubar',
                14: 'Language:',
                15: 'Recent Files data:',
                16: 'Clear All',
                17: 'Clear All Recent Files Data',
                18: 'Are you sure you want to delete all recent files data? This [b]cannot[/b] be undone!',
                19: 'Current Area',
                20: 'Reset',
                21: 'Available Themes',
                22: 'Preview',
                23: 'Use Nonstandard Window Style',
                24: '[b]Use Nonstandard Window Style[/b][br]If this is checkable, the selected theme specifies a[br]window style other than the default. In most cases, you[br]should leave this checked. Uncheck this if you dislike[br]the style this theme uses.',
                25: 'Options',
                26: '[b][name][/b][br]By [creator][br][description]',
                27: 'Tilesets:',
                28: 'Use Default Tileset Picker (recommended)',
                29: 'Use Old Tileset Picker',
                30: 'You may need to restart Reggie! for changes to take effect.',
                },
            'ProgPaths': {
                0: '[id]',
                1: '[id]A',
                2: '[b]Progress Path [path][/b][br]Node [node]',
                3: '[b]Progress Path [path]A[/b][br]Node [node]',
                4: 'Progress Path [path], Node [node]',
                5: 'Progress Path [path]A, Node [node]',
                },
            'ProgPathDataEditor': {
                0: 'Modify Selected Progress Path Node Properties',
                1: '[b]Progress Path [id][/b]',
                2: 'ID:',
                3: '[b]ID:[/b][br]This is the Progress Path ID. The game puts together all progress paths from all areas and sorts them by this ID. The first progress path should have an ID of 0. Duplicate IDs are allowed if one progress path has the Alternate Path checkbox checked.',
                4: 'Alternate Path:',
                5: '[b]Alternate Path:[/b][br]If there are two different zones for the player to choose from, and they both end up in the same place but the player has to choose one or the other, put a Progress Path in each one, give them the same ID and check this checkbox on one of them.',
                6: '[b]Node [id][/b]',
                },
            'Ribbon': {
                0: '&Home',
                1: '&Actions',
                2: '&View',
                3: '&Game',
                4: None, # REMOVED: 'H&elp'
                5: 'Clipboard',
                6: 'Freeze',
                7: 'Level Information',
                8: 'Area',
                9: 'Selection',
                10: 'Items',
                11: 'Level Settings',
                12: 'Areas',
                13: 'Tilesets',
                14: 'Layers',
                15: 'Visibility',
                16: 'Zoom',
                17: 'Docks',
                18: 'Reggie!',
                19: 'Libraries',
                20: '([shortcut]) [description]',
                21: ', ',
                22: '(None) [description]',
                23: '&File',
                },
            'ScrShtDlg': {
                0: 'Choose a Screenshot source',
                1: 'Current Screen',
                2: 'All Zones',
                3: 'Zone [zone]',
                },
            'ShftItmDlg': {
                0: 'Shift Items',
                1: 'Move objects by:',
                2: 'Enter an offset in pixels - each block is 16 pixels wide/high. Note that normal objects can only be placed on 16x16 boundaries, so if the offset you enter isn\'t a multiple of 16, they won\'t be moved correctly.',
                3: 'X:',
                4: 'Y:',
                5: 'Warning',
                6: 'You are trying to move object(s) by an offset which isn\'t a multiple of 16. It will work, but the objects will not be able to move exactly the same amount as the sprites. Are you sure you want to do this?',
                },
            'Splash': {
                0: '[current] (Stage [stage])',
                1: 'Loading layers...',
                2: 'Loading level data...',
                3: 'Loading tilesets...',
                4: 'Loading objects...',
                5: 'Preparing editor...',
                },
            'SpriteDataEditor': {
                0: 'Modify Selected Sprite Properties',
                1: '[b][name][/b]: [note]',
                2: '[b]Sprite Notes:[/b] [notes]',
                3: 'Modify Raw Data:',
                4: 'Notes',
                5: '[b]Unidentified/Unknown Sprite ([id])[/b]',
                6: '[b]Sprite [id]:[br][name][/b]',
                7: 'Object Files',
                8: '[b]This sprite uses:[/b][br][list]',
                },
            'Sprites': {
                0: '[b]Sprite [type]:[/b][br][name]',
                1: '[name] (at [x], [y]',
                2: ', triggered by event [event]',
                3: ', triggered by events [event1]+[event2]+[event3]+[event4]',
                4: ', triggered by event [event1], [event2], [event3], or [event4]',
                5: ', activates event [event]',
                6: ', activates events [event1] - [event2]',
                7: ', activates event [event1], [event2], [event3], or [event4]',
                8: ', Star Coin [num]',
                9: ', Star Coin 1',
                10: ', Coin/Set ID [id]',
                11: ', Movement/Coin ID [id]',
                12: ', Movement ID [id]',
                13: ', Rotation ID [id]',
                14: ', Location ID [id]',
                15: ')',
                16: 'Search Results',
                17: 'No sprites found',
                18: '[id]: [name]',
                19: 'Search',
                },
            'Statusbar': {
                0: '- 1 object selected',
                1: '- 1 sprite selected',
                2: '- 1 entrance selected',
                3: '- 1 location selected',
                4: '- 1 path node selected',
                5: '- [x] objects selected',
                6: '- [x] sprites selected',
                7: '- [x] entrances selected',
                8: '- [x] locations selected',
                9: '- [x] path nodes selected',
                10: '- [x] items selected (',
                11: ', ',
                12: '1 object',
                13: '[x] objects',
                14: '1 sprite',
                15: '[x] sprites',
                16: '1 entrance',
                17: '[x] entrances',
                18: '1 location',
                19: '[x] locations',
                20: '1 path node',
                21: '[x] path nodes',
                22: ')',
                23: '- Object under mouse: size [width]x[height] at ([xpos], [ypos]) on layer [layer]; type [type] from tileset [tileset]',
                24: '- Sprite under mouse: [name] at [xpos], [ypos]',
                25: '- Entrance under mouse: [name] at [xpos], [ypos] [dest]',
                26: '- Location under mouse: Location ID [id] at [xpos], [ypos]; width [width], height [height]',
                27: '- Path node under mouse: Path [path], Node [node] at [xpos], [ypos]',
                28: '([objx], [objy]) - ([sprx], [spry])',
                29: '- 1 comment selected',
                30: '- [x] comments selected',
                31: '1 comment',
                32: '[x] comments',
                33: '- Comment under mouse: [xpos], [ypos]; "[text]"',
                34: '- 1 progress path node selected',
                35: '- [x] progress path nodes selected',
                36: '1 progress path node',
                37: '[x] progress path nodes',
                38: '- Progress Path node under mouse: Progress Path [path], Node [node] at [xpos], [ypos]',
                39: '- Progress Path node under mouse: Progress Path [path]A, Node [node] at [xpos], [ypos]',
                },
            'Themes': {
                0: 'Classic',
                1: 'Treeki, Tempus',
                2: 'The default Reggie! theme.',
                3: '[i](unknown)[/i]',
                4: '[i]No description[/i]',
                },
            'Updates': {
                0: 'Check for Updates',
                1: 'Error while checking for updates.',
                2: 'No updates are available.',
                3: 'An update is available: [name][br][info]',
                4: 'Download Now',
                5: 'Please wait, the update is downloading...',
                6: 'Restart to finalize update!',
                },
            'WindowTitle': {
                0: 'Untitled',
                },
            'ZonesDlg': {
                0: 'Zones',
                1: (
                    'Overworld',
                    'Underground',
                    'Underwater',
                    'Lava/Volcano (reddish)',
                    'Desert',
                    'Beach*',
                    'Forest*',
                    'Snow Overworld*',
                    'Sky/Bonus*',
                    'Mountains*',
                    'Tower',
                    'Castle',
                    'Ghost House',
                    'River Cave',
                    'Ghost House Exit',
                    'Underwater Cave',
                    'Desert Cave',
                    'Icy Cave*',
                    'Lava/Volcano',
                    'Final Battle',
                    'World 8 Castle',
                    'World 8 Doomship*',
                    'Lit Tower',
                    ),
                2: (
                    'Normal/Overworld',
                    'Underground',
                    'Underwater',
                    'Lava/Volcano',
                    ),
                3: 'Zone [num]',
                4: 'New',
                5: 'Delete',
                6: 'Warning',
                7: 'You are trying to add more than 8 zones to a level - keep in mind that without the proper fix to the game, this will cause your level to [b]crash[/b] or have other strange issues![br][br]Are you sure you want to do this?',
                8: 'Dimensions',
                9: 'X position:',
                10: '[b]X position:[/b][br]Sets the X Position of the upper left corner',
                11: 'Y position:',
                12: '[b]Y position:[/b][br]Sets the Y Position of the upper left corner',
                13: 'X size:',
                14: '[b]X size:[/b][br]Sets the width of the zone',
                15: 'Y size:',
                16: '[b]Y size:[/b][br]Sets the height of the zone',
                17: 'Preset:',
                18: '[b]Preset:[/b][br]Snaps the zone to common sizes.[br]The number before each entry specifies which zoom level works best with each size.',
                19: 'Rendering and Camera',
                20: 'Zone Theme:',
                21: '[b]Zone Theme:[/b][br]Changes the way models and parts of the background are rendered (for blurring, darkness, lava effects, and so on). Themes with * next to them are used in the game, but look the same as the overworld theme.',
                22: 'Terrain Lighting:',
                23: '[b]Terrain Lighting:[/b][br]Changes the way the terrain is rendered. It also affects the parts of the background which the normal theme doesn\'t change.',
                24: 'Normal',
                25: '[b]Visibility - Normal:[/b][br]Sets the visibility mode to normal.',
                26: 'Layer 0 Spotlight',
                27: '[b]Visibility - Layer 0 Spotlight:[/b][br]Sets the visibility mode to spotlight. In Spotlight mode,[br]moving behind layer 0 objects enables a spotlight that[br]follows Mario around.',
                28: 'Full Darkness',
                29: '[b]Visibility - Full Darkness:[/b][br]Sets the visibility mode to full darkness. In full dark mode,[br]the screen is completely black and visibility is only provided[br]by the available spotlight effect. Stars and some sprites[br]can enhance the default visibility.',
                30: 'X Tracking:',
                31: '[b]X Tracking:[/b][br]Allows the camera to track Mario across the X dimension.[br]Turning off this option centers the screen horizontally in the view, producing a stationary camera mode.',
                32: 'Y Tracking:',
                33: '[b]Y Tracking:[/b][br]Allows the camera to track Mario across the Y dimension.[br]Turning off this option centers the screen vertically in the view, producing very vertically limited stages.',
                34: 'Zoom Level:',
                35: '[b]Zoom Level:[/b][br]Changes the camera zoom functionality[br] - Negative values: Zoom In[br] - Positive values: Zoom Out[br][br]Zoom Level 4 is rather glitchy',
                36: 'Bias:',
                37: '[b]Bias:[/b][br]Sets the screen bias to the left edge on load, preventing initial scrollback.[br]Useful for pathed levels.[br]Note: Not all zoom/mode combinations support bias',
                38: (
                    'Left to Right',
                    'Right to Left',
                    'Top to Bottom',
                    'Bottom to Top',
                    ),
                39: 'Camera Tracking:',
                40: '[b]Camera Tracking:[/b][br]This setting makes changes to camera tracking during multiplayer mode.[br]If the camera doesn\'t move, choose Left to Right.[br]If you\'re unsure, choose Left to Right.',
                41: (
                    'Hidden',
                    'On Top',
                    ),
                42: '[b]Visibility:[/b][br]Hidden - Mario is hidden when moving behind objects on Layer 0[br]On Top - Mario is displayed above Layer 0 at all times.[br][br]Note: Entities behind layer 0 other than Mario are never visible',
                43: (
                    'Small',
                    'Large',
                    'Full Screen',
                    ),
                44: '[b]Visibility:[/b][br]Small - A small, centered spotlight affords visibility through layer 0.[br]Large - A large, centered spotlight affords visibility through layer 0[br]Full Screen - the entire screen is revealed whenever Mario walks behind layer 0',
                45: ('Large Foglight',
                     'Lightbeam',
                     'Large Focus Light',
                     'Small Foglight',
                     'Small Focus Light',
                     'Absolute Black',
                     ),
                46: '[b]Visibility:[/b][br]Large Foglight - A large, organic lightsource surrounds Mario[br]Lightbeam - Mario is able to aim a conical lightbeam through use of the Wiimote[br]Large Focus Light - A large spotlight which changes size based upon player movement[br]Small Foglight - A small, organic lightsource surrounds Mario[br]Small Focuslight - A small spotlight which changes size based on player movement[br]Absolute Black - Visibility is provided only by fireballs, stars, and certain sprites',
                47: 'Bounds',
                48: 'Upper Bounds:',
                49: '[b]Upper Bounds:[/b][br] - Positive Values: Easier to scroll upwards (110 is centered)[br] - Negative Values: Harder to scroll upwards (30 is the top edge of the screen)[br][br]Values higher than 240 can cause instant death upon screen scrolling',
                50: 'Lower Bounds:',
                51: '[b]Lower Bounds:[/b][br] - Positive Values: Harder to scroll downwards (65 is the bottom edge of the screen)[br] - Negative Values: Easier to scroll downwards (95 is centered)[br][br]Values higher than 100 will prevent the scene from scrolling until Mario is offscreen',
                52: 'Audio',
                53: 'Background Music:',
                54: '[b]Background Music:[/b][br]Changes the background music',
                55: 'Sound Modulation:',
                56: '[b]Sound Modulation:[/b][br]Changes the sound effect modulation',
                57: (
                    'Normal',
                    'Wall Echo',
                    'Room Echo',
                    'Double Echo',
                    'Cave Echo',
                    'Underwater Echo',
                    'Triple Echo',
                    'High Pitch Echo',
                    'Tinny Echo',
                    'Flat',
                    'Dull',
                    'Hollow Echo',
                    'Rich',
                    'Triple Underwater',
                    'Ring Echo',
                    ),
                58: 'Boss Flag:',
                59: '[b]Boss Flag:[/b][br]Set for bosses to allow proper music switching by sprites',
                60: '(None)',
                61: 'Error',
                62: 'Zoom level -2 does not support bias modes.',
                63: 'Zoom level -1 does not support bias modes.',
                64: 'Zoom level -1 is not supported with these Tracking modes. Set to Zoom level 0.',
                65: 'Zoom mode 4 can be glitchy with these settings.',
                66: 'No tracking mode is consistently glitchy and does not support bias.',
                67: 'No tracking mode is consistently glitchy.',
                68: 'Background Music ID:',
                69: '[b]Background Music ID:[/b][br]This advanced option allows custom music tracks to be loaded if the proper ASM hacks are in place.',
                70: 'Upper Bounds 2:',
                71: '[b]Upper Bounds 2:[/b][br]Unknown differences from the main upper bounds.',
                72: 'Lower Bounds 2:',
                73: '[b]Lower Bounds 2:[/b][br]Unknown differences from the main lower bounds.',
                74: 'Unknown Flag',
                75: '[b]Unknown Flag:[/b][br]Unknown purpose. Seems to be always checked.',
                },
            'Zones': {
                0: 'Zone [num]',
                },
            }


    def InitFromXML(self, name):
        """
        Parses the translation XML
        """
        if name in ('', None, 'None'): return
        name = str(name)
        MaxVer = 1.0

        # Parse the file (errors are handled by __init__())
        path = 'reggiedata/translations/' + name + '/main.xml'
        tree = etree.parse(path)
        root = tree.getroot()

        # Add attributes
        # Name
        if 'name' not in root.attrib: raise Exception
        self.name = root.attrib['name']
        # Version
        if 'version' not in root.attrib: raise Exception
        self.version = float(root.attrib['version'])
        if self.version > MaxVer: raise Exception
        # Translator
        if 'translator' not in root.attrib: raise Exception
        self.translator = root.attrib['translator']

        # Parse the nodes
        files = {}
        strings = False
        addpath = 'reggiedata/translations/' + name + '/'
        for node in root:
            if node.tag.lower() == 'file':
                # It's a file node
                name = node.attrib['name']
                path = addpath + node.attrib['path']
                files[name] = path
            elif node.tag.lower() == 'strings':
                # It's a strings node
                strings = addpath + node.attrib['path']

        # Get rid of the XML stuff
        del tree, root

        # Overwrite self.files with files
        for index in files: self.files[index] = files[index]



        # Check for a strings node
        if not strings: raise Exception

        # Parse the strings
        tree = etree.parse(strings)
        root = tree.getroot()

        # Parse the nodes
        strings = {}
        for section in root:
            # Get a section
            if section.tag.lower() != 'section': continue
            id = section.attrib['id']
            sectionStrings = {}

            # Get the strings/stringlists in this section
            for string in section:
                if not hasattr(string, 'attrib'): continue
                strValue = None
                if string.tag.lower() == 'string':
                    # String node; this is easy
                    strValue = string[0]
                elif string.tag.lower() == 'stringlist':
                    # Not as easy, but not hard
                    strValue = []
                    for entry in string:
                        if entry.tag.lower() == 'entry':
                            strValue.append(entry[0])
                    strValue = tuple(strValue)

                # Add this string to sectionStrings
                idB = int(string.attrib['id'])
                if strValue is not None: sectionStrings[idB] = strValue

            # Add it to strings
            strings[id] = sectionStrings

        # Overwrite self.strings with strings
        for index in strings:
            if index not in self.strings: self.strings[index] = {}
            for index2 in strings[index]:
                self.strings[index][index2] = strings[index][index2]


    def string(*args):
        """
        Usage: string(section, numcode, replacementDummy, replacement, replacementDummy2, replacement2, etc.)
        """
        self = args[0]

        # If there are errors when the string is found, return an error report instead
        try: return self.string_(args[1:])
        except Exception as e:
            text = '\nReggieTranslation.string() ERROR: ' + str(args[1]) + '; ' + str(args[2]) + '; ' + repr(e) + '\n'
            # do 3 things with the text - print it, save it to ReggieErrors.txt, return it
            print(text)
            if not os.path.isfile('ReggieErrors.txt'):
                f = open('ReggieErrors.txt', 'w')
            else:
                f = open('ReggieErrors.txt', 'a')
            f.write(text)
            f.close(); del f
            return text

    def string_(*args):
        """
        Gets a string from the translation and returns it
        """
        # Get self and remove it from args
        self = args[0]
        args = args[1]

        # Get the string
        astring = self.strings[args[0]][args[1]]

        # Perform any replacements
        i = 2
        while i < len(args):

            # Get the old string
            old = str(args[i])

            # Get the new string
            new = str(args[i+1])

            # Replace
            astring = astring.replace(old, new)
            i += 2

        # Do some automatic replacements
        replace = {
            '[br]': '<br>',
            '[b]': '<b>',
            '[/b]': '</b>',
            '[i]': '<i>',
            '[/i]': '</i>',
            '[a': '<a',
            '"]': '">', # workaround
            '[/a]': '</a>',
            '\\n': '\n',
            '//n': '\n',
            }
        for old in replace:
            astring = astring.replace(old, replace[old])

        # Return it
        return astring

    def stringList(self, section, numcode):
        """
        Returns a list of strings
        """
        try: return self.strings[section][numcode]
        except Exception: return ('ReggieTranslation.stringList() ERROR:', section, numcode)

    def path(self, key):
        """
        Returns the path to the file indicated by key
        """
        try: return self.files[key]
        except Exception:
            # (print, save, return) an error message
            text = 'ReggieTranslation.path() ERROR: ' + key
            print(text)
            F = open('ReggieErrors.txt', 'w')
            F.write(text)
            F.close()
            raise SystemExit

    def generateXML(self):
        """
        Generates a strings.xml and places it in the folder of reggie.py
        """

        # Sort self.strings
        sortedstrings = sorted(
            (
                [
                    key,
                    sorted(
                        self.strings[key].items(),
                        key=lambda entry: entry[0]),
                    ]
                for key in self.strings
                ),
            key=lambda entry: entry[0])

        # Create an XML
        root = etree.Element('strings')
        for sectionname, section in sortedstrings:
            sectionElem = etree.Element('section', {'id': sectionname})
            root.append(sectionElem)
            for stringid, string in section:
                if isinstance(string, tuple) or isinstance(string, list):
                    stringlistElem = etree.Element('stringlist', {'id': str(stringid)})
                    sectionElem.append(stringlistElem)
                    for entryname in string:
                        entryElem = etree.Element('entry')
                        entryElem.text = entryname
                        stringlistElem.append(entryElem)
                else:
                    stringElem = etree.Element('string', {'id': str(stringid)})
                    stringElem.text = string
                    sectionElem.append(stringElem)

        tree = etree.ElementTree(root)
        tree.write('strings.xml', encoding='utf-8')


class LevelScene(QtWidgets.QGraphicsScene):
    """
    GraphicsView subclass for the level scene
    """
    def __init__(self, *args):
        global theme

        self.bgbrush = QtGui.QBrush(theme.color('bg'))
        QtWidgets.QGraphicsScene.__init__(self, *args)

    def drawBackground(self, painter, rect):
        """
        Draws all visible tiles
        """
        painter.fillRect(rect, self.bgbrush)
        if not hasattr(Area, 'layers'): return

        drawrect = QtCore.QRectF(rect.x() / 24, rect.y() / 24, rect.width() / 24 + 1, rect.height() / 24 + 1)
        isect = drawrect.intersects

        layer0 = []; l0add = layer0.append
        layer1 = []; l1add = layer1.append
        layer2 = []; l2add = layer2.append

        type_obj = ObjectItem
        ii = isinstance

        x1 = 1024
        y1 = 512
        x2 = 0
        y2 = 0

        # iterate through each object
        funcs = [layer0.append, layer1.append, layer2.append]
        show = [Layer0Shown, Layer1Shown, Layer2Shown]
        for layer, add, process in zip(Area.layers, funcs, show):
            if not process: continue
            for item in layer:
                if not isect(item.LevelRect): continue
                add(item)
                xs = item.objx
                xe = xs+item.width
                ys = item.objy
                ye = ys+item.height
                if xs < x1: x1 = xs
                if xe > x2: x2 = xe
                if ys < y1: y1 = ys
                if ye > y2: y2 = ye

        width = x2 - x1
        height = y2 - y1
        tiles = Tiles

        # create and draw the tilemaps
        for layer in [layer2, layer1, layer0]:
            if len(layer) > 0:
                tmap = []
                i = 0
                while i < height:
                    tmap.append([None] * width)
                    i += 1

                for item in layer:
                    startx = item.objx - x1
                    desty = item.objy - y1

                    exists = True
                    if ObjectDefinitions[item.tileset] is None:
                        exists = False
                    elif ObjectDefinitions[item.tileset][item.type] is None:
                        exists = False

                    for row in item.objdata:
                        destrow = tmap[desty]
                        destx = startx
                        for tile in row:
                            if not exists:
                                destrow[destx] = -1
                            elif tile > 0:
                                destrow[destx] = tile
                            destx += 1
                        desty += 1

                painter.save()
                painter.translate(x1 * 24, y1 * 24)
                drawPixmap = painter.drawPixmap
                desty = 0
                for row in tmap:
                    destx = 0
                    for tile in row:
                        pix = None

                        if tile == -1:
                            # Draw unknown tiles
                            pix = Overrides[108].getCurrentTile()
                        elif tile is not None:
                            pix = tiles[tile].getCurrentTile()

                        if pix is not None:
                            painter.drawPixmap(destx, desty, pix)

                        destx += 24
                    desty += 24
                painter.restore()



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
        QtWidgets.QGraphicsView.__init__(self, scene, parent)

        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        #self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(119,136,153)))
        self.setDragMode(QtWidgets.QGraphicsView.RubberBandDrag)
        #self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
        self.setMouseTracking(True)
        #self.setOptimizationFlags(QtWidgets.QGraphicsView.IndirectPainting)
        self.YScrollBar = QtWidgets.QScrollBar(Qt.Vertical, parent)
        self.XScrollBar = QtWidgets.QScrollBar(Qt.Horizontal, parent)
        self.setVerticalScrollBar(self.YScrollBar)
        self.setHorizontalScrollBar(self.XScrollBar)

        self.currentobj = None

    def mousePressEvent(self, event):
        """
        Overrides mouse pressing events if needed
        """
        if event.button() == Qt.RightButton:
            if CurrentPaintType in (0, 1, 2, 3) and CurrentObject != -1:
                # paint an object
                clicked = mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)
                clickedx = int(clicked.x() / 24)
                clickedy = int(clicked.y() / 24)

                ln = CurrentLayer
                layer = Area.layers[CurrentLayer]
                if len(layer) == 0:
                    z = (2 - ln) * 8192
                else:
                    z = layer[-1].zValue() + 1

                obj = ObjectItem(CurrentPaintType, CurrentObject, ln, clickedx, clickedy, 1, 1, z)
                layer.append(obj)
                mw = mainWindow
                obj.positionChanged = mw.HandleObjPosChange
                mw.scene.addItem(obj)

                self.dragstamp = False
                self.currentobj = obj
                self.dragstartx = clickedx
                self.dragstarty = clickedy
                SetDirty()

            elif CurrentPaintType == 4 and CurrentSprite != -1:
                # paint a sprite
                clicked = mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)

                if CurrentSprite >= 0: # fixes a bug -Treeki
                    #[18:15:36]  Angel-SL: I found a bug in Reggie
                    #[18:15:42]  Angel-SL: you can paint a 'No sprites found'
                    #[18:15:47]  Angel-SL: results in a sprite -2

                    # paint a sprite
                    clickedx = int((clicked.x() - 12) / 12) * 8
                    clickedy = int((clicked.y() - 12) / 12) * 8

                    data = mainWindow.defaultDataEditor.data
                    spr = SpriteItem(CurrentSprite, clickedx, clickedy, data)

                    mw = mainWindow
                    spr.positionChanged = mw.HandleSprPosChange
                    mw.scene.addItem(spr)

                    spr.listitem = ListWidgetItem_SortsByOther(spr)
                    mw.spriteList.addItem(spr.listitem)
                    Area.sprites.append(spr)

                    self.dragstamp = False
                    self.currentobj = spr
                    self.dragstartx = clickedx
                    self.dragstarty = clickedy

                    self.scene().update()

                    spr.UpdateListItem()

                SetDirty()

            elif CurrentPaintType == 5:
                # paint an entrance
                clicked = mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)
                clickedx = int((clicked.x() - 12) / 1.5)
                clickedy = int((clicked.y() - 12) / 1.5)

                getids = [False for x in range(256)]
                for ent in Area.entrances: getids[ent.entid] = True
                minimumID = getids.index(False)

                ent = EntranceItem(clickedx, clickedy, minimumID, 0, 0, 0, 0, 0, 0, 0x80, 0)
                mw = mainWindow
                ent.positionChanged = mw.HandleEntPosChange
                mw.scene.addItem(ent)

                elist = mw.entranceList
                # if it's the first available ID, all the other indexes should match right?
                # so I can just use the ID to insert
                ent.listitem = ListWidgetItem_SortsByOther(ent)
                elist.insertItem(minimumID, ent.listitem)

                global PaintingEntrance, PaintingEntranceListIndex
                PaintingEntrance = ent
                PaintingEntranceListIndex = minimumID

                Area.entrances.insert(minimumID, ent)

                self.dragstamp = False
                self.currentobj = ent
                self.dragstartx = clickedx
                self.dragstarty = clickedy

                ent.UpdateListItem()

                SetDirty()
            elif CurrentPaintType == 6:
                # paint a path node
                clicked = mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)
                clickedx = int((clicked.x() - 12) / 1.5)
                clickedy = int((clicked.y() - 12) / 1.5)
                mw = mainWindow
                plist = mw.pathList
                selectedpn = None if len(plist.selectedItems()) < 1 else plist.selectedItems()[0]
                #if selectedpn is None:
                #    QtWidgets.QMessageBox.warning(None, 'Error', 'No pathnode selected. Select a pathnode of the path you want to create a new node in.')
                if selectedpn is None:
                    getids = [False for x in range(256)]
                    getids[0] = True
                    for pathdatax in Area.pathdata:
                        #if(len(pathdatax['nodes']) > 0):
                        getids[int(pathdatax['id'])] = True

                    newpathid = getids.index(False)
                    newpathdata = {'id': newpathid,
                                   'nodes': [{'x': clickedx, 'y': clickedy, 'speed': 0.5, 'accel': 0.00498, 'delay': 0}],
                                   'loops': False
                    }
                    Area.pathdata.append(newpathdata)
                    newnode = PathItem(clickedx, clickedy, newpathdata, newpathdata['nodes'][0])
                    newnode.positionChanged = mw.HandlePathPosChange

                    mw.scene.addItem(newnode)

                    peline = PathEditorLineItem(newpathdata['nodes'])
                    newpathdata['peline'] = peline
                    mw.scene.addItem(peline)

                    Area.pathdata.sort(key=lambda path: int(path['id']))

                    newnode.listitem = ListWidgetItem_SortsByOther(newnode)
                    plist.clear()
                    for fpath in Area.pathdata:
                        for fpnode in fpath['nodes']:
                            fpnode['graphicsitem'].listitem = ListWidgetItem_SortsByOther(fpnode['graphicsitem'], fpnode['graphicsitem'].ListString())
                            plist.addItem(fpnode['graphicsitem'].listitem)
                            fpnode['graphicsitem'].updateId()
                    newnode.listitem.setSelected(True)
                    Area.paths.append(newnode)

                    self.dragstamp = False
                    self.currentobj = newnode
                    self.dragstartx = clickedx
                    self.dragstarty = clickedy

                    newnode.UpdateListItem()

                    SetDirty()
                else:
                    pathd = None
                    for pathnode in Area.paths:
                        if pathnode.listitem == selectedpn:
                            pathd = pathnode.pathinfo

                    if not pathd: return # shouldn't happen

                    pathid = pathd['id']
                    newnodedata = {'x': clickedx, 'y': clickedy, 'speed': 0.5, 'accel': 0.00498, 'delay': 0}
                    pathd['nodes'].append(newnodedata)
                    nodeid = pathd['nodes'].index(newnodedata)


                    newnode = PathItem(clickedx, clickedy, pathd, newnodedata)

                    newnode.positionChanged = mw.HandlePathPosChange
                    mw.scene.addItem(newnode)

                    newnode.listitem = ListWidgetItem_SortsByOther(newnode)
                    plist.clear()
                    for fpath in Area.pathdata:
                        for fpnode in fpath['nodes']:
                            fpnode['graphicsitem'].listitem = ListWidgetItem_SortsByOther(fpnode['graphicsitem'], fpnode['graphicsitem'].ListString())
                            plist.addItem(fpnode['graphicsitem'].listitem)
                            fpnode['graphicsitem'].updateId()
                    newnode.listitem.setSelected(True)
                    #global PaintingEntrance, PaintingEntranceListIndex
                    #PaintingEntrance = ent
                    #PaintingEntranceListIndex = minimumID

                    Area.paths.append(newnode)
                    pathd['peline'].nodePosChanged()
                    self.dragstamp = False
                    self.currentobj = newnode
                    self.dragstartx = clickedx
                    self.dragstarty = clickedy

                    newnode.UpdateListItem()

                    SetDirty()

            elif CurrentPaintType == 7:
                # paint a location
                clicked = mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)

                clickedx = int(clicked.x() / 1.5)
                clickedy = int(clicked.y() / 1.5)

                allID = set() # faster 'x in y' lookups for sets
                newID = 1
                for i in Area.locations:
                    allID.add(i.id)

                while newID <= 255:
                    if newID not in allID:
                        break
                    newID += 1

                global OverrideSnapping
                OverrideSnapping = True
                loc = LocationItem(clickedx, clickedy, 4, 4, newID)
                OverrideSnapping = False

                mw = mainWindow
                loc.positionChanged = mw.HandleLocPosChange
                loc.sizeChanged = mw.HandleLocSizeChange
                loc.listitem = ListWidgetItem_SortsByOther(loc)
                mw.locationList.addItem(loc.listitem)
                mw.scene.addItem(loc)

                Area.locations.append(loc)

                self.dragstamp = False
                self.currentobj = loc
                self.dragstartx = clickedx
                self.dragstarty = clickedy

                loc.UpdateListItem()

                SetDirty()

            elif CurrentPaintType == 8:
                # paint a stamp
                clicked = mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)

                clickedx = int(clicked.x() / 1.5)
                clickedy = int(clicked.y() / 1.5)

                stamp = mainWindow.stampChooser.currentlySelectedStamp()
                if stamp is not None:
                    objs = mainWindow.placeEncodedObjects(stamp.ReggieClip, False, clickedx, clickedy)

                    for obj in objs:
                        obj.dragstartx = obj.objx
                        obj.dragstarty = obj.objy
                        obj.update()

                    mainWindow.scene.update()

                    self.dragstamp = True
                    self.dragstartx = clickedx
                    self.dragstarty = clickedy
                    self.currentobj = objs

                    SetDirty()

            elif CurrentPaintType == 9:
                # paint a comment

                clicked = mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)
                clickedx = int((clicked.x() - 12) / 1.5)
                clickedy = int((clicked.y() - 12) / 1.5)

                com = CommentItem(clickedx, clickedy, '')
                mw = mainWindow
                com.positionChanged = mw.HandleComPosChange
                com.textChanged = mw.HandleComTxtChange
                mw.scene.addItem(com)
                com.setVisible(CommentsShown)

                clist = mw.commentList
                com.listitem = QtWidgets.QListWidgetItem()
                clist.addItem(com.listitem)

                Area.comments.append(com)

                self.dragstamp = False
                self.currentobj = com
                self.dragstartx = clickedx
                self.dragstarty = clickedy

                mainWindow.SaveComments()

                com.UpdateListItem()

                SetDirty()

            elif CurrentPaintType == 10:
                # paint a progress path node
                clicked = mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)
                clickedx = int((clicked.x() - 12) / 1.5)
                clickedy = int((clicked.y() - 12) / 1.5)
                mw = mainWindow
                plist = mw.progPathList
                selectedpn = None if len(plist.selectedItems()) < 1 else plist.selectedItems()[0]
                #if selectedpn is None:
                #    QtWidgets.QMessageBox.warning(None, 'Error', 'No pathnode selected. Select a pathnode of the path you want to create a new node in.')
                if selectedpn is None:
                    getids = [False for x in range(256)]
                    getids[0] = True
                    for pathdatax in Area.progpathdata:
                        #if(len(pathdatax['nodes']) > 0):
                        getids[int(pathdatax['id'])] = True

                    newpathid = getids.index(False)
                    newpathdata = {'id': newpathid,
                                   'nodes': [{'x': clickedx, 'y': clickedy}],
                                   'altpath': False,
                    }
                    Area.progpathdata.append(newpathdata)
                    newnode = ProgressPathItem(clickedx, clickedy, newpathdata, newpathdata['nodes'][0])
                    newnode.positionChanged = mw.HandleProgressPathPosChange

                    mw.scene.addItem(newnode)

                    peline = ProgressPathEditorLineItem(newpathdata['nodes'])
                    newpathdata['peline'] = peline
                    mw.scene.addItem(peline)

                    Area.progpathdata.sort(key=lambda path: int(path['id']))

                    newnode.listitem = ListWidgetItem_SortsByOther(newnode)
                    plist.clear()
                    for fpath in Area.progpathdata:
                        for fpnode in fpath['nodes']:
                            fpnode['graphicsitem'].listitem = ListWidgetItem_SortsByOther(fpnode['graphicsitem'], fpnode['graphicsitem'].ListString())
                            plist.addItem(fpnode['graphicsitem'].listitem)
                            fpnode['graphicsitem'].updateId()
                    newnode.listitem.setSelected(True)
                    Area.progpaths.append(newnode)

                    self.dragstamp = False
                    self.currentobj = newnode
                    self.dragstartx = clickedx
                    self.dragstarty = clickedy

                    newnode.UpdateListItem()

                    SetDirty()
                else:
                    pathd = None
                    for pathnode in Area.progpaths:
                        if pathnode.listitem == selectedpn:
                            pathd = pathnode.progpathinfo

                    if not pathd:
                        print(':(')
                        return # shouldn't happen

                    pathid = pathd['id']
                    newnodedata = {'x': clickedx, 'y': clickedy, 'altpath': False}
                    pathd['nodes'].append(newnodedata)
                    nodeid = pathd['nodes'].index(newnodedata)


                    newnode = ProgressPathItem(clickedx, clickedy, pathd, newnodedata)

                    newnode.positionChanged = mw.HandleProgressPathPosChange
                    mw.scene.addItem(newnode)

                    newnode.listitem = ListWidgetItem_SortsByOther(newnode)
                    plist.clear()
                    for fpath in Area.progpathdata:
                        for fpnode in fpath['nodes']:
                            fpnode['graphicsitem'].listitem = ListWidgetItem_SortsByOther(fpnode['graphicsitem'], fpnode['graphicsitem'].ListString())
                            plist.addItem(fpnode['graphicsitem'].listitem)
                            fpnode['graphicsitem'].updateId()
                    newnode.listitem.setSelected(True)
                    #global PaintingEntrance, PaintingEntranceListIndex
                    #PaintingEntrance = ent
                    #PaintingEntranceListIndex = minimumID

                    Area.progpaths.append(newnode)
                    pathd['peline'].nodePosChanged()
                    self.dragstamp = False
                    self.currentobj = newnode
                    self.dragstartx = clickedx
                    self.dragstarty = clickedy

                    newnode.UpdateListItem()

                    SetDirty()

            event.accept()
        elif (event.button() == Qt.LeftButton) and (QtWidgets.QApplication.keyboardModifiers() == Qt.ShiftModifier):
            mw = mainWindow

            pos = mw.view.mapToScene(event.x(), event.y())
            addsel = mw.scene.items(pos)
            for i in addsel:
                if (int(i.flags()) & i.ItemIsSelectable) != 0:
                    i.setSelected(not i.isSelected())
                    break

        else:
            QtWidgets.QGraphicsView.mousePressEvent(self, event)
        mainWindow.levelOverview.update()


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

        pos = mainWindow.view.mapToScene(event.x(), event.y())
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
            type_progpath = ProgressPathItem
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
                    clicked = mainWindow.view.mapToScene(event.x(), event.y())
                    if clicked.x() < 0: clicked.setX(0)
                    if clicked.y() < 0: clicked.setY(0)
                    clickx = int(clicked.x() / 24)
                    clicky = int(clicked.y() / 24)

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
                        obj.setPos(x * 24, y * 24)

                    # if the size changed, recache it and update the area
                    if cwidth != width or cheight != height:
                        obj.width = width
                        obj.height = height
                        obj.updateObjCache()

                        oldrect = obj.BoundingRect
                        oldrect.translate(cx * 24, cy * 24)
                        newrect = QtCore.QRectF(obj.x(), obj.y(), obj.width * 24, obj.height * 24)
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
                    clicked = mainWindow.view.mapToScene(event.x(), event.y())
                    if clicked.x() < 0: clicked.setX(0)
                    if clicked.y() < 0: clicked.setY(0)
                    clickx = int(clicked.x() / 1.5)
                    clicky = int(clicked.y() / 1.5)

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

                        global OverrideSnapping
                        OverrideSnapping = True
                        obj.setPos(x * 1.5, y * 1.5)
                        OverrideSnapping = False

                    # if the size changed, recache it and update the area
                    if cwidth != width or cheight != height:
                        obj.width = width
                        obj.height = height
    #                    obj.updateObjCache()

                        oldrect = obj.BoundingRect
                        oldrect.translate(cx * 1.5, cy * 1.5)
                        newrect = QtCore.QRectF(obj.x(), obj.y(), obj.width * 1.5, obj.height * 1.5)
                        updaterect = oldrect.united(newrect)

                        obj.UpdateRects()
                        obj.scene().update(updaterect)


                elif isinstance(obj, type_spr):
                    # move the created sprite
                    clicked = mainWindow.view.mapToScene(event.x(), event.y())
                    if clicked.x() < 0: clicked.setX(0)
                    if clicked.y() < 0: clicked.setY(0)
                    clickedx = int((clicked.x() - 12) / 1.5)
                    clickedy = int((clicked.y() - 12) / 1.5)

                    if obj.objx != clickedx or obj.objy != clickedy:
                        obj.objx = clickedx
                        obj.objy = clickedy
                        obj.setPos(int((clickedx+obj.ImageObj.xOffset) * 1.5), int((clickedy+obj.ImageObj.yOffset) * 1.5))

                elif isinstance(obj, type_ent) or isinstance(obj, type_path) or isinstance(obj, type_progpath) or isinstance(obj, type_com):
                    # move the created entrance/path/comment
                    clicked = mainWindow.view.mapToScene(event.x(), event.y())
                    if clicked.x() < 0: clicked.setX(0)
                    if clicked.y() < 0: clicked.setY(0)
                    clickedx = int((clicked.x() - 12) / 1.5)
                    clickedy = int((clicked.y() - 12) / 1.5)

                    if obj.objx != clickedx or obj.objy != clickedy:
                        obj.objx = clickedx
                        obj.objy = clickedy
                        obj.setPos(int(clickedx * 1.5), int(clickedy * 1.5))
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

                clicked = mainWindow.view.mapToScene(event.x(), event.y())
                if clicked.x() < 0: clicked.setX(0)
                if clicked.y() < 0: clicked.setY(0)
                    
                changex = clicked.x() - (self.dragstartx * 1.5)
                changey = clicked.y() - (self.dragstarty * 1.5)
                changexobj = int(changex / 24)
                changeyobj = int(changey / 24)
                changexspr = changex * 2/3
                changeyspr = changey * 2/3

                if isinstance(obj, type_obj):
                    # move the current object
                    newx = int(obj.dragstartx + changexobj)
                    newy = int(obj.dragstarty + changeyobj)

                    if obj.objx != newx or obj.objy != newy:
                        
                        obj.objx = newx
                        obj.objy = newy
                        obj.setPos(newx * 24, newy * 24)

                elif isinstance(obj, type_spr):
                    # move the created sprite
                    
                    newx = int(obj.dragstartx + changexspr)
                    newy = int(obj.dragstarty + changeyspr)

                    if obj.objx != newx or obj.objy != newy:
                        obj.objx = newx
                        obj.objy = newy
                        obj.setPos(int((newx + obj.ImageObj.xOffset) * 1.5), int((newy + obj.ImageObj.yOffset) * 1.5))

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
        if GridType is None: return
        global theme

        Zoom = mainWindow.ZoomLevel
        drawLine = painter.drawLine
        GridColor = theme.color('grid')

        if GridType == 'grid': # draw a classic grid
            startx = rect.x()
            startx -= (startx % 24)
            endx = startx + rect.width() + 24

            starty = rect.y()
            starty -= (starty % 24)
            endy = starty + rect.height() + 24

            x = startx - 24
            while x <= endx:
                x += 24
                if x % 192 == 0:
                    painter.setPen(QtGui.QPen(GridColor, 2, Qt.DashLine))
                    drawLine(x, starty, x, endy)
                elif x % 96 == 0:
                    if Zoom < 25: continue
                    painter.setPen(QtGui.QPen(GridColor, 1, Qt.DashLine))
                    drawLine(x, starty, x, endy)
                else:
                    if Zoom < 50: continue
                    painter.setPen(QtGui.QPen(GridColor, 1, Qt.DotLine))
                    drawLine(x, starty, x, endy)

            y = starty - 24
            while y <= endy:
                y += 24
                if y % 192 == 0:
                    painter.setPen(QtGui.QPen(GridColor, 2, Qt.DashLine))
                    drawLine(startx, y, endx, y)
                elif y % 96 == 0 and Zoom >= 25:
                    painter.setPen(QtGui.QPen(GridColor, 1, Qt.DashLine))
                    drawLine(startx, y, endx, y)
                elif Zoom >= 50:
                    painter.setPen(QtGui.QPen(GridColor, 1, Qt.DotLine))
                    drawLine(startx, y, endx, y)

        else: # draw a checkerboard
            L = 0.2
            D = 0.1     # Change these values to change the checkerboard opacity

            Light = QtGui.QColor(GridColor)
            Dark = QtGui.QColor(GridColor)
            Light.setAlpha(Light.alpha()*L)
            Dark.setAlpha(Dark.alpha()*D)

            size = 24 if Zoom >= 50 else 96

            board = QtGui.QPixmap(8*size, 8*size)
            board.fill(QtGui.QColor(0,0,0,0))
            p = QtGui.QPainter(board)
            p.setPen(Qt.NoPen)

            p.setBrush(QtGui.QBrush(Light))
            for x, y in ((0, size), (size, 0)):
                p.drawRect(x+(4*size), y,          size, size)
                p.drawRect(x+(4*size), y+(2*size), size, size)
                p.drawRect(x+(6*size), y,          size, size)
                p.drawRect(x+(6*size), y+(2*size), size, size)

                p.drawRect(x,          y+(4*size), size, size)
                p.drawRect(x,          y+(6*size), size, size)
                p.drawRect(x+(2*size), y+(4*size), size, size)
                p.drawRect(x+(2*size), y+(6*size), size, size)
            p.setBrush(QtGui.QBrush(Dark))
            for x, y in ((0, 0), (size, size)):
                p.drawRect(x,          y,          size, size)
                p.drawRect(x,          y+(2*size), size, size)
                p.drawRect(x+(2*size), y,          size, size)
                p.drawRect(x+(2*size), y+(2*size), size, size)

                p.drawRect(x,          y+(4*size), size, size)
                p.drawRect(x,          y+(6*size), size, size)
                p.drawRect(x+(2*size), y+(4*size), size, size)
                p.drawRect(x+(2*size), y+(6*size), size, size)

                p.drawRect(x+(4*size), y,          size, size)
                p.drawRect(x+(4*size), y+(2*size), size, size)
                p.drawRect(x+(6*size), y,          size, size)
                p.drawRect(x+(6*size), y+(2*size), size, size)

                p.drawRect(x+(4*size), y+(4*size), size, size)
                p.drawRect(x+(4*size), y+(6*size), size, size)
                p.drawRect(x+(6*size), y+(4*size), size, size)
                p.drawRect(x+(6*size), y+(6*size), size, size)


            del p

            painter.drawTiledPixmap(rect, board, QtCore.QPointF(rect.x(), rect.y()))




####################################################################
####################################################################
####################################################################

class HexSpinBox(QtWidgets.QSpinBox):
    class HexValidator(QtGui.QValidator):
        def __init__(self, min, max):
            QtGui.QValidator.__init__(self)
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
        QtWidgets.QSpinBox.__init__(self, *args)
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

class InputBox(QtWidgets.QDialog):
    Type_TextBox = 1
    Type_SpinBox = 2
    Type_HexSpinBox = 3

    def __init__(self, type=Type_TextBox):
        QtWidgets.QDialog.__init__(self)

        self.label = QtWidgets.QLabel('-')
        self.label.setWordWrap(True)

        if type == InputBox.Type_TextBox:
            self.textbox = QtWidgets.QLineEdit()
            widget = self.textbox
        elif type == InputBox.Type_SpinBox:
            self.spinbox = QtWidgets.QSpinBox()
            widget = self.spinbox
        elif type == InputBox.Type_HexSpinBox:
            self.spinbox = HexSpinBox()
            widget = self.spinbox

        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(widget)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)


class AboutDialog(QtWidgets.QDialog):
    """
    Shows the About info for Reggie
    """
    def __init__(self):
        """
        Creates and initializes the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('AboutDlg', 0))
        self.setWindowIcon(GetIcon('reggie'))

        # Set the palette to the default
        # defaultPalette is a global
        self.setPalette(QtGui.QPalette(defaultPalette))

        # Open the readme file
        f = open('readme.md', 'r')
        readme = f.read()
        f.close()
        del f

        # Logo
        logo = QtGui.QPixmap('reggiedata/about.png')
        logoLabel = QtWidgets.QLabel()
        logoLabel.setPixmap(logo)
        logoLabel.setContentsMargins(16, 4, 32, 4)

        # Description
        description =  '<html><head><style type=\'text/CSS\'>'
        description += 'body {font-family: Calibri}'
        description += '.main {font-size: 12px}'
        description += '</style></head><body>'
        description += '<center><h1><i>Reggie!</i> Level Editor</h1><div class=\'main\'>'
        description += '<i>Reggie! Level Editor</i> is an open-source global project started by Treeki in 2010 that aims to bring you the fun of designing original New Super Mario Bros. Wii&trade;-compatible levels.<br>'
        description += 'Interested? Check out <a href=\'http://rvlution.net/reggie\'>rvlution.net/reggie</a> for updates and related downloads, or <a href=\'http://rvlution.net/forums\'>rvlution.net/forums</a> to get in touch with the developers.<br>'
        description += '</div></center></body></html>'

        # Description label
        descLabel = QtWidgets.QLabel()
        descLabel.setText(description)
        descLabel.setMinimumWidth(512)
        descLabel.setWordWrap(True)

        # Readme.md viewer
        readmeView = QtWidgets.QPlainTextEdit()
        readmeView.setPlainText(readme)
        readmeView.setReadOnly(True)

        # Buttonbox
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)

        # Main layout
        L = QtWidgets.QGridLayout()
        L.addWidget(logoLabel, 0, 0, 2, 1)
        L.addWidget(descLabel, 0, 1)
        L.addWidget(readmeView, 1, 1)
        L.addWidget(buttonBox, 2, 0, 1, 2)
        L.setRowStretch(1, 1)
        L.setColumnStretch(1, 1)
        self.setLayout(L)


class ObjectShiftDialog(QtWidgets.QDialog):
    """
    Lets you pick an amount to shift selected items by
    """
    def __init__(self):
        """
        Creates and initializes the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('ShftItmDlg', 0))
        self.setWindowIcon(GetIcon('move'))

        self.XOffset = QtWidgets.QSpinBox()
        self.XOffset.setRange(-16384, 16383)

        self.YOffset = QtWidgets.QSpinBox()
        self.YOffset.setRange(-8192, 8191)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        moveLayout = QtWidgets.QFormLayout()
        offsetlabel = QtWidgets.QLabel(trans.string('ShftItmDlg', 2))
        offsetlabel.setWordWrap(True)
        moveLayout.addWidget(offsetlabel)
        moveLayout.addRow(trans.string('ShftItmDlg', 3), self.XOffset)
        moveLayout.addRow(trans.string('ShftItmDlg', 4), self.YOffset)

        moveGroupBox = QtWidgets.QGroupBox(trans.string('ShftItmDlg', 1))
        moveGroupBox.setLayout(moveLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(moveGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)



class ObjectTilesetSwapDialog(QtWidgets.QDialog):
    """
    Lets you pick tilesets to swap objects to
    """
    def __init__(self):
        """
        Creates and initializes the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle('Swap Objects\' Tilesets')
        self.setWindowIcon(GetIcon('swap'))

        # Create widgets
        self.FromTS = QtWidgets.QSpinBox()
        self.FromTS.setRange(1, 4)

        self.ToTS = QtWidgets.QSpinBox()
        self.ToTS.setRange(1, 4)


        # Swap layouts
        swapLayout = QtWidgets.QFormLayout()

        swapLayout.addRow('From tileset:', self.FromTS)
        swapLayout.addRow('To tileset:', self.ToTS)

        self.DoExchange = QtWidgets.QCheckBox('Exchange (perform 2-way conversion)')


        # Buttonbox
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)


        # Main layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(swapLayout)
        mainLayout.addWidget(self.DoExchange)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)



class ObjectTypeSwapDialog(QtWidgets.QDialog):
    """
    Lets you pick object types to swap objects to
    """
    def __init__(self):
        """
        Creates and initializes the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle('Swap Objects\' Types')
        self.setWindowIcon(GetIcon('swap'))


        # Create widgets
        self.FromType = QtWidgets.QSpinBox()
        self.FromType.setRange(0, 255)

        self.ToType = QtWidgets.QSpinBox()
        self.ToType.setRange(0, 255)

        self.FromTileset = QtWidgets.QSpinBox()
        self.FromTileset.setRange(1, 4)

        self.ToTileset = QtWidgets.QSpinBox()
        self.ToTileset.setRange(1, 4)

        self.DoExchange = QtWidgets.QCheckBox('Exchange (perform 2-way conversion)')


        # Swap layout
        swapLayout = QtWidgets.QGridLayout()

        swapLayout.addWidget(QtWidgets.QLabel('From tile type:'), 0, 0)
        swapLayout.addWidget(self.FromType, 0, 1)

        swapLayout.addWidget(QtWidgets.QLabel('From tileset:'), 1, 0)
        swapLayout.addWidget(self.FromTileset, 1, 1)

        swapLayout.addWidget(QtWidgets.QLabel('To tile type:'), 0, 2)
        swapLayout.addWidget(self.ToType, 0, 3)

        swapLayout.addWidget(QtWidgets.QLabel('To tileset:'), 1, 2)
        swapLayout.addWidget(self.ToTileset, 1, 3)


        # Buttonbox
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)


        # Main layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(swapLayout)
        mainLayout.addWidget(self.DoExchange)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)



class MetaInfoDialog(QtWidgets.QDialog):
    """
    Allows the user to enter in various meta-info to be kept in the level for display
    """
    def __init__(self):
        """
        Creates and initializes the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('InfoDlg', 0))
        self.setWindowIcon(GetIcon('info'))

        title = Area.Metadata.strData('Title')
        author = Area.Metadata.strData('Author')
        group = Area.Metadata.strData('Group')
        website = Area.Metadata.strData('Website')
        creator = Area.Metadata.strData('Creator')
        password = Area.Metadata.strData('Password')
        if title is None: title = '-'
        if author is None: author = '-'
        if group is None: group = '-'
        if website is None: website = '-'
        if creator is None: creator = '(unknown)'
        if password is None: password = ''

        self.levelName = QtWidgets.QLineEdit()
        self.levelName.setMaxLength(128)
        self.levelName.setReadOnly(True)
        self.levelName.setMinimumWidth(320)
        self.levelName.setText(title)

        self.Author = QtWidgets.QLineEdit()
        self.Author.setMaxLength(128)
        self.Author.setReadOnly(True)
        self.Author.setMinimumWidth(320)
        self.Author.setText(author)

        self.Group = QtWidgets.QLineEdit()
        self.Group.setMaxLength(128)
        self.Group.setReadOnly(True)
        self.Group.setMinimumWidth(320)
        self.Group.setText(group)

        self.Website = QtWidgets.QLineEdit()
        self.Website.setMaxLength(128)
        self.Website.setReadOnly(True)
        self.Website.setMinimumWidth(320)
        self.Website.setText(website)

        self.Password = QtWidgets.QLineEdit()
        self.Password.setMaxLength(128)
        self.Password.textChanged.connect(self.PasswordEntry)
        self.Password.setMinimumWidth(320)

        self.changepw = QtWidgets.QPushButton(trans.string('InfoDlg', 1))


        if password != '':
            self.levelName.setReadOnly(False)
            self.Author.setReadOnly(False)
            self.Group.setReadOnly(False)
            self.Website.setReadOnly(False)
            self.changepw.setDisabled(False)


        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.addButton(self.changepw, buttonBox.ActionRole)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.changepw.clicked.connect(self.ChangeButton)
        self.changepw.setDisabled(True)

        self.lockedLabel = QtWidgets.QLabel(trans.string('InfoDlg', 2))

        infoLayout = QtWidgets.QFormLayout()
        infoLayout.addWidget(self.lockedLabel)
        infoLayout.addRow(trans.string('InfoDlg', 3), self.Password)
        infoLayout.addRow(trans.string('InfoDlg', 4), self.levelName)
        infoLayout.addRow(trans.string('InfoDlg', 5), self.Author)
        infoLayout.addRow(trans.string('InfoDlg', 6), self.Group)
        infoLayout.addRow(trans.string('InfoDlg', 7), self.Website)

        self.PasswordLabel = infoLayout.labelForField(self.Password)

        levelIsLocked = password != ''
        self.lockedLabel.setVisible(levelIsLocked)
        self.PasswordLabel.setVisible(levelIsLocked)
        self.Password.setVisible(levelIsLocked)

        infoGroupBox = QtWidgets.QGroupBox(trans.string('InfoDlg', 8, '[name]', creator))
        infoGroupBox.setLayout(infoLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(infoGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.PasswordEntry('')

    @QtCore.pyqtSlot(str)
    def PasswordEntry(self, text):
        pswd = Area.Metadata.strData('Password')
        if pswd is None: pswd = ''
        if text == pswd:
            self.levelName.setReadOnly(False)
            self.Author.setReadOnly(False)
            self.Group.setReadOnly(False)
            self.Website.setReadOnly(False)
            self.changepw.setDisabled(False)
        else:
            self.levelName.setReadOnly(True)
            self.Author.setReadOnly(True)
            self.Group.setReadOnly(True)
            self.Website.setReadOnly(True)
            self.changepw.setDisabled(True)


#   To all would be crackers who are smart enough to reach here:
#
#   Make your own damn levels.
#
#
#
#       - The management
#


    def ChangeButton(self):
        """
        Allows the changing of a given password
        """

        class ChangePWDialog(QtWidgets.QDialog):
            """
            Dialog
            """
            def __init__(self):
                QtWidgets.QDialog.__init__(self)
                self.setWindowTitle(trans.string('InfoDlg', 9))
                self.setWindowIcon(GetIcon('info'))

                self.New = QtWidgets.QLineEdit()
                self.New.setMaxLength(64)
                self.New.textChanged.connect(self.PasswordMatch)
                self.New.setMinimumWidth(320)

                self.Verify = QtWidgets.QLineEdit()
                self.Verify.setMaxLength(64)
                self.Verify.textChanged.connect(self.PasswordMatch)
                self.Verify.setMinimumWidth(320)

                self.Ok = QtWidgets.QPushButton('OK')
                self.Cancel = QtWidgets.QDialogButtonBox.Cancel

                buttonBox = QtWidgets.QDialogButtonBox()
                buttonBox.addButton(self.Ok, buttonBox.AcceptRole)
                buttonBox.addButton(self.Cancel)

                buttonBox.accepted.connect(self.accept)
                buttonBox.rejected.connect(self.reject)
                self.Ok.setDisabled(True)

                infoLayout = QtWidgets.QFormLayout()
                infoLayout.addRow(trans.string('InfoDlg', 10), self.New)
                infoLayout.addRow(trans.string('InfoDlg', 11), self.Verify)

                infoGroupBox = QtWidgets.QGroupBox(trans.string('InfoDlg', 12))

                infoLabel = QtWidgets.QVBoxLayout()
                infoLabel.addWidget(QtWidgets.QLabel(trans.string('InfoDlg', 13)), 0, Qt.AlignCenter)
                infoLabel.addLayout(infoLayout)
                infoGroupBox.setLayout(infoLabel)

                mainLayout = QtWidgets.QVBoxLayout()
                mainLayout.addWidget(infoGroupBox)
                mainLayout.addWidget(buttonBox)
                self.setLayout(mainLayout)

            @QtCore.pyqtSlot(str)
            def PasswordMatch(self, text):
                self.Ok.setDisabled(self.New.text() != self.Verify.text() and self.New.text() != '')

        dlg = ChangePWDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.lockedLabel.setVisible(True)
            self.Password.setVisible(True)
            self.PasswordLabel.setVisible(True)
            pswd = str(dlg.Verify.text())
            Area.Metadata.setStrData('Password', pswd)
            self.Password.setText(pswd)
            SetDirty()

            self.levelName.setReadOnly(False)
            self.Author.setReadOnly(False)
            self.Group.setReadOnly(False)
            self.Website.setReadOnly(False)
            self.changepw.setDisabled(False)



# Sets up the Area Options Menu
class AreaOptionsDialog(QtWidgets.QDialog):
    """
    Dialog which lets you choose among various area options from tabs
    """
    def __init__(self, NewTilesetsTab = True):
        """
        Creates and initializes the tab dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('AreaDlg', 0))
        self.setWindowIcon(GetIcon('area'))

        self.tabWidget = QtWidgets.QTabWidget()
        self.LoadingTab = LoadingTab()
        self.TilesetsTab = TilesetsTab() if NewTilesetsTab else OldTilesetsTab()
        self.tabWidget.addTab(self.TilesetsTab, trans.string('AreaDlg', 1))
        self.tabWidget.addTab(self.LoadingTab, trans.string('AreaDlg', 2))

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)


class LoadingTab(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.timer = QtWidgets.QSpinBox()
        self.timer.setRange(0, 999)
        self.timer.setToolTip(trans.string('AreaDlg', 4))
        self.timer.setValue(Area.timeLimit + 200)

        self.entrance = QtWidgets.QSpinBox()
        self.entrance.setRange(0, 255)
        self.entrance.setToolTip(trans.string('AreaDlg', 6))
        self.entrance.setValue(Area.startEntrance)

        self.wrap = QtWidgets.QCheckBox(trans.string('AreaDlg', 7))
        self.wrap.setToolTip(trans.string('AreaDlg', 8))
        self.wrap.setChecked((Area.wrapFlag & 1) != 0)

        ##self.unk1 = QtWidgets.QSpinBox()
        ##self.unk1.setRange(0, 0x255)
        ##self.unk1.setToolTip(trans.string('AreaDlg', 25))
        ##self.unk1.setValue(Area.unk1)

        self.unk2 = QtWidgets.QSpinBox()
        self.unk2.setRange(0, 255)
        self.unk2.setToolTip(trans.string('AreaDlg', 25))
        self.unk2.setValue(Area.unk2)

        self.unk3 = QtWidgets.QSpinBox()
        self.unk3.setRange(0, 255)
        self.unk3.setToolTip(trans.string('AreaDlg', 26))
        self.unk3.setValue(Area.unk3)

        settingsLayout = QtWidgets.QFormLayout()
        settingsLayout.addRow(trans.string('AreaDlg', 3), self.timer)
        settingsLayout.addRow(trans.string('AreaDlg', 5), self.entrance)
        ##settingsLayout.addRow(trans.string('AreaDlg', 22), self.unk1)
        settingsLayout.addRow(trans.string('AreaDlg', 22), self.unk2)
        settingsLayout.addRow(trans.string('AreaDlg', 23), self.unk3)
        settingsLayout.addRow(self.wrap)
        # The max value of unk1 is too big for QtWidgets.QSpinBox() to handle...

        Layout = QtWidgets.QVBoxLayout()
        Layout.addLayout(settingsLayout)
        Layout.addStretch(1)
        self.setLayout(Layout)


class TilesetsTab(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        self.setMinimumWidth(384)

        # Set up each tileset
        self.widgets = []
        self.trees = []
        self.lineEdits = []
        self.itemDict = [{}, {}, {}, {}]
        self.noneItems = []

        for slot in range(4):
            # Create the main widget
            widget = QtWidgets.QWidget()
            self.widgets.append(widget)

            # Create the tree widget
            tree = QtWidgets.QTreeWidget()
            tree.setColumnCount(2)
            tree.setHeaderLabels([trans.string('AreaDlg', 28), trans.string('AreaDlg', 29)]) # ['Name', 'File']
            tree.setIndentation(16)
            if slot == 0: handler = self.handleTreeSel0
            elif slot == 1: handler = self.handleTreeSel1
            elif slot == 2: handler = self.handleTreeSel2
            else: handler = self.handleTreeSel3
            tree.itemSelectionChanged.connect(handler)
            self.trees.append(tree)

            # Add "None" entry
            item = QtWidgets.QTreeWidgetItem()
            item.setText(0, trans.string('AreaDlg', 15)) # 'None'
            tree.addTopLevelItem(item)
            self.noneItems.append(item)

            # Keep an unsorted list for the textbox autocomplete
            tilesetList = []

            # Add entries for each tileset
            def ParseCategory(items):
                """
                Parses a list of strings and returns a tuple of QTreeWidgetItem's
                """
                nodes = []
                for item in items:
                    node = QtWidgets.QTreeWidgetItem()

                    # Check if it's a tileset or a category
                    if isinstance(item[1], str):
                        # It's a tileset
                        node.setText(0, item[1])
                        node.setText(1, item[0])
                        node.setToolTip(0, item[1])
                        node.setToolTip(1, item[0])
                        self.itemDict[slot][item[0]] = node
                        tilesetList.append(item[0])
                    else:
                        # It's a category
                        node.setText(0, item[0])
                        node.setToolTip(0, item[0])
                        node.setFlags(Qt.ItemIsEnabled)
                        children = ParseCategory(item[1])
                        for cnode in children:
                            node.addChild(cnode)
                    nodes.append(node)
                return tuple(nodes)
            categories = ParseCategory(TilesetNames[slot][0])
            tree.addTopLevelItems(categories)

            # Create the line edit
            line = QtWidgets.QLineEdit()
            line.textChanged.connect(eval('self.handleTextEdit%d' % slot))
            line.setCompleter(QtWidgets.QCompleter(tilesetList))
            line.setPlaceholderText(trans.string('AreaDlg', 30)) # '(None)'
            self.lineEdits.append(line)
            line.setText(eval('Area.tileset%d' % slot))
            self.handleTextEdit(slot)
            # Above line: For some reason, PyQt doesn't automatically call
            # the handler if (Area.tileset%d % slot) == ''

            # Create the layout and add it to the widget
            L = QtWidgets.QGridLayout()
            L.addWidget(tree, 0, 0, 1, 2)
            L.addWidget(QtWidgets.QLabel(trans.string('AreaDlg', 31, '[slot]', slot)), 1, 0) # 'Tilesets (Pa[slot])'
            L.addWidget(line, 1, 1)
            L.setRowStretch(0, 1)
            widget.setLayout(L)

        # Set up the tab widget
        T = QtWidgets.QTabWidget()
        T.setTabPosition(T.West)
        T.setUsesScrollButtons(False)
        T.addTab(self.widgets[0], trans.string('AreaDlg', 11)) # 'Standard Suite'
        T.addTab(self.widgets[1], trans.string('AreaDlg', 12)) # 'Stage Suite'
        T.addTab(self.widgets[2], trans.string('AreaDlg', 13)) # 'Background Suite'
        T.addTab(self.widgets[3], trans.string('AreaDlg', 14)) # 'Interactive Suite'
        L = QtWidgets.QVBoxLayout()
        L.addWidget(T)
        self.setLayout(L)
        return

    # Tree handlers
    def handleTreeSel0(self):
        self.handleTreeSel(0)
    def handleTreeSel1(self):
        self.handleTreeSel(1)
    def handleTreeSel2(self):
        self.handleTreeSel(2)
    def handleTreeSel3(self):
        self.handleTreeSel(3)
    def handleTreeSel(self, slot):
        """
        Handles changes to the selections in all tree widgets
        """
        selItems = self.trees[slot].selectedItems()
        if len(selItems) != 1: return
        item = selItems[0]

        value = str(item.text(1))
        self.lineEdits[slot].setText(value)

    # Line-edit handlers
    def handleTextEdit0(self):
        self.handleTextEdit(0)
    def handleTextEdit1(self):
        self.handleTextEdit(1)
    def handleTextEdit2(self):
        self.handleTextEdit(2)
    def handleTextEdit3(self):
        self.handleTextEdit(3)
    def handleTextEdit(self, slot):
        """
        Handles changes made to the line-edit widgets
        """
        self.trees[slot].clearSelection()
        txt = str(self.lineEdits[slot].text())

        if (txt in self.itemDict[slot]) or (txt == ''):
            # Collapse all
            for i in range(self.trees[slot].topLevelItemCount()):
                self.trees[slot].collapseItem(self.trees[slot].topLevelItem(i))

            # If there's no text, just select None
            if txt == '':
                self.noneItems[slot].setSelected(True)
                return

            # Find the item matching the description, and select it
            item = self.itemDict[slot][txt]
            item.setSelected(True)

            # Expand all of its parents
            parent = item.parent()
            while parent is not None:
                parent.setExpanded(True)
                parent = parent.parent()

    def values(self):
        """
        Returns all 4 tileset choices
        """
        result = []
        for i in range(4):
            result.append(str(self.lineEdits[i].text()))
        return tuple(result)


class OldTilesetsTab(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)

        self.tile0 = QtWidgets.QComboBox()
        self.tile1 = QtWidgets.QComboBox()
        self.tile2 = QtWidgets.QComboBox()
        self.tile3 = QtWidgets.QComboBox()

        self.widgets = [self.tile0, self.tile1, self.tile2, self.tile3]
        names = [Area.tileset0, Area.tileset1, Area.tileset2, Area.tileset3]
        slots = [self.HandleTileset0Choice, self.HandleTileset1Choice, self.HandleTileset2Choice, self.HandleTileset3Choice]

        self.currentChoices = [None, None, None, None]

        TilesetNamesIterable = SimpleTilesetNames()

        for idx, widget, name, data, slot in zip(range(4), self.widgets, names, TilesetNamesIterable, slots):
            # This loop runs once for each tileset.
            # First, find the current index and custom-tileset strings
            if name == '': # No tileset selected, the current index should be None
                ts_index = trans.string('AreaDlg', 15) # None
                custom = ''
                custom_fname = trans.string('AreaDlg', 16) # [CUSTOM]
            else: # Tileset selected
                ts_index = trans.string('AreaDlg', 18, '[name]', name) # Custom filename... [name]
                custom = name
                custom_fname = trans.string('AreaDlg', 17, '[name]', name) # [CUSTOM] [name]

            # Add items to the widget:
            # - None
            widget.addItem(trans.string('AreaDlg', 15), '') # None
            # - Retail Tilesets
            for tfile, tname in data:
                text = trans.string('AreaDlg', 19, '[name]', tname, '[file]', tfile) # [name] ([file])
                widget.addItem(text, tfile)
                if name == tfile:
                    ts_index = text
                    custom = ''
            # - Custom Tileset
            widget.addItem(trans.string('AreaDlg', 18, '[name]', custom), custom_fname) # Custom filename... [name]

            # Set the current index
            item_idx = widget.findText(ts_index)
            self.currentChoices[idx] = item_idx
            widget.setCurrentIndex(item_idx)

            # Handle combobox changes
            widget.activated.connect(slot)

        # don't allow ts0 to be removable
        self.tile0.removeItem(0)

        mainLayout = QtWidgets.QVBoxLayout()
        tile0Box = QtWidgets.QGroupBox(trans.string('AreaDlg', 11))
        tile1Box = QtWidgets.QGroupBox(trans.string('AreaDlg', 12))
        tile2Box = QtWidgets.QGroupBox(trans.string('AreaDlg', 13))
        tile3Box = QtWidgets.QGroupBox(trans.string('AreaDlg', 14))

        t0 = QtWidgets.QVBoxLayout()
        t0.addWidget(self.tile0)
        t1 = QtWidgets.QVBoxLayout()
        t1.addWidget(self.tile1)
        t2 = QtWidgets.QVBoxLayout()
        t2.addWidget(self.tile2)
        t3 = QtWidgets.QVBoxLayout()
        t3.addWidget(self.tile3)

        tile0Box.setLayout(t0)
        tile1Box.setLayout(t1)
        tile2Box.setLayout(t2)
        tile3Box.setLayout(t3)

        mainLayout.addWidget(tile0Box)
        mainLayout.addWidget(tile1Box)
        mainLayout.addWidget(tile2Box)
        mainLayout.addWidget(tile3Box)
        mainLayout.addStretch(1)
        self.setLayout(mainLayout)

    @QtCore.pyqtSlot(int)
    def HandleTileset0Choice(self, index):
        self.HandleTilesetChoice(0, index)

    @QtCore.pyqtSlot(int)
    def HandleTileset1Choice(self, index):
        self.HandleTilesetChoice(1, index)

    @QtCore.pyqtSlot(int)
    def HandleTileset2Choice(self, index):
        self.HandleTilesetChoice(2, index)

    @QtCore.pyqtSlot(int)
    def HandleTileset3Choice(self, index):
        self.HandleTilesetChoice(3, index)

    def HandleTilesetChoice(self, tileset, index):
        w = self.widgets[tileset]

        if index == (w.count() - 1):
            fname = str(w.itemData(index))
            fname = fname[len(trans.string('AreaDlg', 17, '[name]', '')):]

            dbox = InputBox()
            dbox.setWindowTitle(trans.string('AreaDlg', 20))
            dbox.label.setText(trans.string('AreaDlg', 21))
            dbox.textbox.setMaxLength(31)
            dbox.textbox.setText(fname)
            result = dbox.exec_()

            if result == QtWidgets.QDialog.Accepted:
                fname = str(dbox.textbox.text())
                if fname.endswith('.sarc'): fname = fname[:-4]

                w.setItemText(index, trans.string('AreaDlg', 18, '[name]', fname))
                w.setItemData(index, trans.string('AreaDlg', 17, '[name]', fname))
            else:
                w.setCurrentIndex(self.currentChoices[tileset])
                return

        self.currentChoices[tileset] = index

    def values(self):
        """
        Returns all 4 tileset choices
        """
        result = []
        for i in range(4):
            widget = eval('self.tile%d' % i)
            idx = widget.currentIndex()
            name = str(widget.itemData(idx))
            result.append(name)
        return tuple(result)

def SimpleTilesetNames():
    """
    simple
    """
    # Category parser
    def ParseCategory(items):
        """
        Parses a list of strings and returns a tuple of strings
        """
        result = []
        for item in items:
            if isinstance(item[1], str):
                # It's a tileset
                name = item[1]
                file = item[0]
                result.append((file, name))
            else:
                # It's a category
                childStrings = ParseCategory(item[1])
                for child in childStrings:
                    result.append(child)
        return result

    pa0 = sorted(ParseCategory(TilesetNames[0][0]), key=lambda entry: entry[1])
    pa1 = sorted(ParseCategory(TilesetNames[1][0]), key=lambda entry: entry[1])
    pa2 = sorted(ParseCategory(TilesetNames[2][0]), key=lambda entry: entry[1])
    pa3 = sorted(ParseCategory(TilesetNames[3][0]), key=lambda entry: entry[1])
    return (pa0, pa1, pa2, pa3)



#Sets up the Zones Menu
class ZonesDialog(QtWidgets.QDialog):
    """
    Dialog which lets you choose among various from tabs
    """
    def __init__(self):
        """
        Creates and initializes the tab dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('ZonesDlg', 0))
        self.setWindowIcon(GetIcon('zones'))

        self.tabWidget = QtWidgets.QTabWidget()

        i = 0
        self.zoneTabs = []
        for z in Area.zones:
            i = i+1
            ZoneTabName = trans.string('ZonesDlg', 3, '[num]', i)
            tab = ZoneTab(z)
            self.zoneTabs.append(tab)
            self.tabWidget.addTab(tab, ZoneTabName)


        if self.tabWidget.count() > 5:
            for tab in range(0, self.tabWidget.count()):
                self.tabWidget.setTabText(tab, str(tab + 1))


        self.NewButton = QtWidgets.QPushButton(trans.string('ZonesDlg', 4))
        self.DeleteButton = QtWidgets.QPushButton(trans.string('ZonesDlg', 5))

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.addButton(self.NewButton, buttonBox.ActionRole);
        buttonBox.addButton(self.DeleteButton, buttonBox.ActionRole);

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        #self.NewButton.setEnabled(len(self.zoneTabs) < 8)
        self.NewButton.clicked.connect(self.NewZone)
        self.DeleteButton.clicked.connect(self.DeleteZone)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

    @QtCore.pyqtSlot()
    def NewZone(self):
        if len(self.zoneTabs) >= 8:
            result = QtWidgets.QMessageBox.warning(self, trans.string('ZonesDlg', 6), trans.string('ZonesDlg', 7), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if result == QtWidgets.QMessageBox.No:
                return

        a = []
        b = []

        a.append([0, 0, 0, 0, 0, 0])
        b.append([0, 0, 0, 0, 0, 10, 10, 10, 0])
        id = len(self.zoneTabs)
        z = ZoneItem(256, 256, 448, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, a, b, b, id)
        ZoneTabName = trans.string('ZonesDlg', 3, '[num]', id+1)
        tab = ZoneTab(z)
        self.zoneTabs.append(tab)
        self.tabWidget.addTab(tab, ZoneTabName)
        if self.tabWidget.count() > 5:
            for tab in range(0, self.tabWidget.count()):
                self.tabWidget.setTabText(tab, str(tab + 1))

        #self.NewButton.setEnabled(len(self.zoneTabs) < 8)


    @QtCore.pyqtSlot()
    def DeleteZone(self):
        curindex = self.tabWidget.currentIndex()
        tabamount = self.tabWidget.count()
        if tabamount == 0: return
        self.tabWidget.removeTab(curindex)

        for tab in range(curindex, tabamount):
            if self.tabWidget.count() < 6:
                self.tabWidget.setTabText(tab, trans.string('ZonesDlg', 3, '[num]', tab+1))
            if self.tabWidget.count() > 5:
                self.tabWidget.setTabText(tab, str(tab + 1))

        self.zoneTabs.pop(curindex)
        if self.tabWidget.count() < 6:
            for tab in range(0, self.tabWidget.count()):
                self.tabWidget.setTabText(tab, trans.string('ZonesDlg', 3, '[num]', tab+1))

        #self.NewButton.setEnabled(len(self.zoneTabs) < 8)



class ZoneTab(QtWidgets.QWidget):
    def __init__(self, z):
        QtWidgets.QWidget.__init__(self)

        self.zoneObj = z
        self.AutoChangingSize = False

        self.createDimensions(z)
        self.createVisibility(z)
        self.createBounds(z)
        self.createAudio(z)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.Dimensions)
        mainLayout.addWidget(self.Visibility)
        mainLayout.addWidget(self.Bounds)
        mainLayout.addWidget(self.Audio)
        self.setLayout(mainLayout)



    def createDimensions(self, z):
        self.Dimensions = QtWidgets.QGroupBox(trans.string('ZonesDlg', 8))

        self.Zone_xpos = QtWidgets.QSpinBox()
        self.Zone_xpos.setRange(16, 65535)
        self.Zone_xpos.setToolTip(trans.string('ZonesDlg', 10))
        self.Zone_xpos.setValue(z.objx)

        self.Zone_ypos = QtWidgets.QSpinBox()
        self.Zone_ypos.setRange(16, 65535)
        self.Zone_ypos.setToolTip(trans.string('ZonesDlg', 12))
        self.Zone_ypos.setValue(z.objy)

        self.Zone_width = QtWidgets.QSpinBox()
        self.Zone_width.setRange(300, 65535)
        self.Zone_width.setToolTip(trans.string('ZonesDlg', 14))
        self.Zone_width.setValue(z.width)
        self.Zone_width.valueChanged.connect(self.PresetDeselected)

        self.Zone_height = QtWidgets.QSpinBox()
        self.Zone_height.setRange(200, 65535)
        self.Zone_height.setToolTip(trans.string('ZonesDlg', 16))
        self.Zone_height.setValue(z.height)
        self.Zone_height.valueChanged.connect(self.PresetDeselected)

        # Common retail zone presets
        # 416 x 224; Zoom Level 0 (used with minigames)
        # 448 x 224; Zoom Level 0 (used with boss battles)
        # 512 x 272; Zoom Level 0 (used in many, many places)
        # 560 x 304; Zoom Level 2
        # 608 x 320; Zoom Level 2 (actually 609x320; rounded it down myself)
        # 784 x 320; Zoom Level 2 (not added to list because it's just an expansion of 608x320)
        # 704 x 384; Zoom Level 3 (used multiple times; therefore it's important)
        # 944 x 448; Zoom Level 4 (used in 9-3 zone 3)
        self.Zone_presets_values = ('0: 416x224', '0: 448x224', '0: 512x272', '2: 560x304', '2: 608x320', '3: 704x384', '4: 944x448')

        self.Zone_presets = QtWidgets.QComboBox()
        self.Zone_presets.addItems(self.Zone_presets_values)
        self.Zone_presets.setToolTip(trans.string('ZonesDlg', 18))
        self.Zone_presets.currentIndexChanged.connect(self.PresetSelected)
        self.PresetDeselected() # can serve as an initializer for self.Zone_presets


        ZonePositionLayout = QtWidgets.QFormLayout()
        ZonePositionLayout.addRow(trans.string('ZonesDlg', 9), self.Zone_xpos)
        ZonePositionLayout.addRow(trans.string('ZonesDlg', 11), self.Zone_ypos)

        ZoneSizeLayout = QtWidgets.QFormLayout()
        ZoneSizeLayout.addRow(trans.string('ZonesDlg', 13), self.Zone_width)
        ZoneSizeLayout.addRow(trans.string('ZonesDlg', 15), self.Zone_height)
        ZoneSizeLayout.addRow(trans.string('ZonesDlg', 17), self.Zone_presets)


        innerLayout = QtWidgets.QHBoxLayout()

        innerLayout.addLayout(ZonePositionLayout)
        innerLayout.addLayout(ZoneSizeLayout)
        self.Dimensions.setLayout(innerLayout)



    def createVisibility(self, z):
        self.Visibility = QtWidgets.QGroupBox(trans.string('ZonesDlg', 19))

        self.Zone_modeldark = QtWidgets.QComboBox()
        self.Zone_modeldark.addItems(ZoneThemeValues)
        self.Zone_modeldark.setToolTip(trans.string('ZonesDlg', 21))
        if z.modeldark < 0: z.modeldark = 0
        if z.modeldark >= len(ZoneThemeValues): z.modeldark = len(ZoneThemeValues)
        self.Zone_modeldark.setCurrentIndex(z.modeldark)

        self.Zone_terraindark = QtWidgets.QComboBox()
        self.Zone_terraindark.addItems(ZoneTerrainThemeValues)
        self.Zone_terraindark.setToolTip(trans.string('ZonesDlg', 23))
        if z.terraindark < 0: z.terraindark = 0
        if z.terraindark >= len(ZoneTerrainThemeValues): z.terraindark = len(ZoneTerrainThemeValues)
        self.Zone_terraindark.setCurrentIndex(z.terraindark)


        self.Zone_vnormal = QtWidgets.QRadioButton(trans.string('ZonesDlg', 24))
        self.Zone_vnormal.setToolTip(trans.string('ZonesDlg', 25))

        self.Zone_vspotlight = QtWidgets.QRadioButton(trans.string('ZonesDlg', 26))
        self.Zone_vspotlight.setToolTip(trans.string('ZonesDlg', 27))

        self.Zone_vfulldark = QtWidgets.QRadioButton(trans.string('ZonesDlg', 28))
        self.Zone_vfulldark.setToolTip(trans.string('ZonesDlg', 29))

        self.Zone_visibility = QtWidgets.QComboBox()

        self.zv = z.visibility
        VRadioDiv = self.zv // 16

        if VRadioDiv == 0:
            self.Zone_vnormal.setChecked(True)
        elif VRadioDiv == 1:
            self.Zone_vspotlight.setChecked(True)
        elif VRadioDiv == 2:
            self.Zone_vfulldark.setChecked(True)
        elif VRadioDiv == 3:
            self.Zone_vfulldark.setChecked(True)


        self.ChangeList()
        self.Zone_vnormal.clicked.connect(self.ChangeList)
        self.Zone_vspotlight.clicked.connect(self.ChangeList)
        self.Zone_vfulldark.clicked.connect(self.ChangeList)


        self.Zone_xtrack = QtWidgets.QCheckBox()
        self.Zone_xtrack.setToolTip(trans.string('ZonesDlg', 31))
        if z.cammode in [0, 3, 6]:
            self.Zone_xtrack.setChecked(True)
        self.Zone_ytrack = QtWidgets.QCheckBox()
        self.Zone_ytrack.setToolTip(trans.string('ZonesDlg', 33))
        if z.cammode in [0, 1, 3, 4]:
            self.Zone_ytrack.setChecked(True)


        self.Zone_camerazoom = QtWidgets.QComboBox()
        self.Zone_camerazoom.setToolTip(trans.string('ZonesDlg', 35))
        newItems1 = ['-2', '-1', '0', '1', '2', '3', '4']
        self.Zone_camerazoom.addItems(newItems1)
        if z.camzoom == 8:
            self.Zone_camerazoom.setCurrentIndex(0)
        elif (z.camzoom == 9 and z.cammode in [3, 4]) or (z.camzoom in [19, 20] and z.cammode == 9):
            self.Zone_camerazoom.setCurrentIndex(1)
        elif (z.camzoom in [0, 1, 2] and z.cammode in [0, 1, 6]) or (z.camzoom in [10, 11] and z.cammode in [3, 4]) or (z.camzoom == 13 and z.cammode == 9):
            self.Zone_camerazoom.setCurrentIndex(2)
        elif z.camzoom in [5, 6, 7, 9, 10] and z.cammode in [0, 1, 6] or (z.camzoom == 12 and z.cammode == 9):
            self.Zone_camerazoom.setCurrentIndex(3)
        elif (z.camzoom in [4, 11] and z.cammode in [0, 1, 6]) or (z.camzoom in [1, 5] and z.cammode in [3, 4])  or (z.camzoom == 14 and z.cammode == 9):
            self.Zone_camerazoom.setCurrentIndex(4)
        elif (z.camzoom == 3 and z.cammode in [0, 1, 6]) or (z.camzoom == 2 and z.cammode in [3, 4]) or (z.camzoom == 15 and z.cammode == 9):
            self.Zone_camerazoom.setCurrentIndex(5)
        elif (z.camzoom == 16 and z.cammode in [0, 1, 6]) or (z.camzoom in [3, 7] and z.cammode in [3, 4]) or (z.camzoom == 16 and z.cammode == 9):
            self.Zone_camerazoom.setCurrentIndex(6)
        else:
            self.Zone_camerazoom.setCurrentIndex(2)

        self.Zone_camerabias = QtWidgets.QCheckBox()
        self.Zone_camerabias.setToolTip(trans.string('ZonesDlg', 37))
        if z.camzoom in [1, 2, 3, 4, 5, 6, 9, 10]:
            self.Zone_camerabias.setChecked(True)

        directionmodeValues = trans.stringList('ZonesDlg', 38)
        self.Zone_directionmode = QtWidgets.QComboBox()
        self.Zone_directionmode.addItems(directionmodeValues)
        self.Zone_directionmode.setToolTip(trans.string('ZonesDlg', 40))
        if z.camtrack < 0: z.camtrack = 0
        if z.camtrack >= 6: z.camtrack = 6
        idx = z.camtrack/2
        if z.camtrack == 1: idx = 1
        self.Zone_directionmode.setCurrentIndex(idx)

        # Layouts
        ZoneZoomLayout = QtWidgets.QFormLayout()
        ZoneZoomLayout.addRow(trans.string('ZonesDlg', 34), self.Zone_camerazoom)
        ZoneZoomLayout.addRow(trans.string('ZonesDlg', 20), self.Zone_modeldark)
        ZoneZoomLayout.addRow(trans.string('ZonesDlg', 22), self.Zone_terraindark)

        ZoneCameraLayout = QtWidgets.QFormLayout()
        ZoneCameraLayout.addRow(trans.string('ZonesDlg', 30), self.Zone_xtrack)
        ZoneCameraLayout.addRow(trans.string('ZonesDlg', 32), self.Zone_ytrack)
        ZoneCameraLayout.addRow(trans.string('ZonesDlg', 36), self.Zone_camerabias)

        ZoneVisibilityLayout = QtWidgets.QHBoxLayout()
        ZoneVisibilityLayout.addWidget(self.Zone_vnormal)
        ZoneVisibilityLayout.addWidget(self.Zone_vspotlight)
        ZoneVisibilityLayout.addWidget(self.Zone_vfulldark)

        ZoneDirectionLayout = QtWidgets.QFormLayout()
        ZoneDirectionLayout.addRow(trans.string('ZonesDlg', 39), self.Zone_directionmode)

        TopLayout = QtWidgets.QHBoxLayout()
        TopLayout.addLayout(ZoneCameraLayout)
        TopLayout.addLayout(ZoneZoomLayout)

        InnerLayout = QtWidgets.QVBoxLayout()
        InnerLayout.addLayout(TopLayout)
        InnerLayout.addLayout(ZoneVisibilityLayout)
        InnerLayout.addWidget(self.Zone_visibility)
        InnerLayout.addLayout(ZoneDirectionLayout)
        self.Visibility.setLayout(InnerLayout)

    @QtCore.pyqtSlot(bool)
    def ChangeList(self):
        VRadioMod = self.zv % 16

        if self.Zone_vnormal.isChecked():
            self.Zone_visibility.clear()
            addList = trans.stringList('ZonesDlg', 41)
            self.Zone_visibility.addItems(addList)
            self.Zone_visibility.setToolTip(trans.string('ZonesDlg', 42))
            self.Zone_visibility.setCurrentIndex(VRadioMod)
        elif self.Zone_vspotlight.isChecked():
            self.Zone_visibility.clear()
            addList = trans.stringList('ZonesDlg', 43)
            self.Zone_visibility.addItems(addList)
            self.Zone_visibility.setToolTip(trans.string('ZonesDlg', 44))
            self.Zone_visibility.setCurrentIndex(VRadioMod)
        elif self.Zone_vfulldark.isChecked():
            self.Zone_visibility.clear()
            addList = trans.stringList('ZonesDlg', 45)
            self.Zone_visibility.addItems(addList)
            self.Zone_visibility.setToolTip(trans.string('ZonesDlg', 46))
            self.Zone_visibility.setCurrentIndex(VRadioMod)


    def createBounds(self, z):
        self.Bounds = QtWidgets.QGroupBox(trans.string('ZonesDlg', 47))

        #Block3 = Area.bounding[z.block3id]

        self.Zone_yboundup = QtWidgets.QSpinBox()
        self.Zone_yboundup.setRange(-32766, 32767)
        self.Zone_yboundup.setToolTip(trans.string('ZonesDlg', 49))
        self.Zone_yboundup.setSpecialValueText('32')
        self.Zone_yboundup.setValue(z.yupperbound)

        self.Zone_ybounddown = QtWidgets.QSpinBox()
        self.Zone_ybounddown.setRange(-32766, 32767)
        self.Zone_ybounddown.setToolTip(trans.string('ZonesDlg', 51))
        self.Zone_ybounddown.setValue(z.ylowerbound)

        self.Zone_yboundup2 = QtWidgets.QSpinBox()
        self.Zone_yboundup2.setRange(-32766, 32767)
        self.Zone_yboundup2.setToolTip(trans.string('ZonesDlg', 71))
        self.Zone_yboundup2.setValue(z.yupperbound2)

        self.Zone_ybounddown2 = QtWidgets.QSpinBox()
        self.Zone_ybounddown2.setRange(-32766, 32767)
        self.Zone_ybounddown2.setToolTip(trans.string('ZonesDlg', 73))
        self.Zone_ybounddown2.setValue(z.ylowerbound2)

        self.Zone_boundflg = QtWidgets.QCheckBox()
        self.Zone_boundflg.setToolTip(trans.string('ZonesDlg', 75))
        self.Zone_boundflg.setChecked(z.unknownbnf == 0xF)


        LA = QtWidgets.QFormLayout()
        LA.addRow(trans.string('ZonesDlg', 48), self.Zone_yboundup)
        LA.addRow(trans.string('ZonesDlg', 50), self.Zone_ybounddown)
        LA.addRow(trans.string('ZonesDlg', 74), self.Zone_boundflg)
        LB = QtWidgets.QFormLayout()
        LB.addRow(trans.string('ZonesDlg', 70), self.Zone_yboundup2)
        LB.addRow(trans.string('ZonesDlg', 72), self.Zone_ybounddown2)
        LC = QtWidgets.QGridLayout()
        LC.addLayout(LA, 0, 0)
        LC.addLayout(LB, 0, 1)

        self.Bounds.setLayout(LC)


    def createAudio(self, z):
        self.Audio = QtWidgets.QGroupBox(trans.string('ZonesDlg', 52))
        self.AutoEditMusic = False

        self.Zone_music = QtWidgets.QComboBox()
        self.Zone_music.setToolTip(trans.string('ZonesDlg', 54))
        newItems = getMusic()
        for a, b in newItems:
            self.Zone_music.addItem(b, a) # text, songid
        self.Zone_music.setCurrentIndex(self.Zone_music.findData(z.music))
        self.Zone_music.currentIndexChanged.connect(self.handleMusicListSelect)

        self.Zone_musicid = QtWidgets.QSpinBox()
        self.Zone_musicid.setToolTip(trans.string('ZonesDlg', 69))
        self.Zone_musicid.setMaximum(255)
        self.Zone_musicid.setValue(z.music)
        self.Zone_musicid.valueChanged.connect(self.handleMusicIDChange)

        self.Zone_sfx = QtWidgets.QComboBox()
        self.Zone_sfx.setToolTip(trans.string('ZonesDlg', 56))
        newItems3 = trans.stringList('ZonesDlg', 57)
        self.Zone_sfx.addItems(newItems3)
        self.Zone_sfx.setCurrentIndex(z.sfxmod / 16)

        self.Zone_boss = QtWidgets.QCheckBox()
        self.Zone_boss.setToolTip(trans.string('ZonesDlg', 59))
        self.Zone_boss.setChecked(z.sfxmod % 16)


        ZoneAudioLayout = QtWidgets.QFormLayout()
        ZoneAudioLayout.addRow(trans.string('ZonesDlg', 53), self.Zone_music)
        ZoneAudioLayout.addRow(trans.string('ZonesDlg', 68), self.Zone_musicid)
        ZoneAudioLayout.addRow(trans.string('ZonesDlg', 55), self.Zone_sfx)
        ZoneAudioLayout.addRow(trans.string('ZonesDlg', 58), self.Zone_boss)

        self.Audio.setLayout(ZoneAudioLayout)


    def handleMusicListSelect(self):
        """
        Handles the user selecting an entry from the music list
        """
        if self.AutoEditMusic: return
        id = self.Zone_music.itemData(self.Zone_music.currentIndex())
        id = int(str(id)) # id starts out as a QString

        self.AutoEditMusic = True
        self.Zone_musicid.setValue(id)
        self.AutoEditMusic = False

    def handleMusicIDChange(self):
        """
        Handles the user selecting a custom music ID
        """
        if self.AutoEditMusic: return
        id = self.Zone_musicid.value()

        # BUG: The music entries are out of order

        self.AutoEditMusic = True
        self.Zone_music.setCurrentIndex(self.Zone_music.findData(id))
        self.AutoEditMusic = False

    def PresetSelected(self, info=None):
        """
        Handles a zone size preset being selected
        """
        if self.AutoChangingSize: return

        if self.Zone_presets.currentText() == trans.string('ZonesDlg', 60): return
        w, h = self.Zone_presets.currentText()[3:].split('x')

        self.AutoChangingSize = True
        self.Zone_width.setValue(int(w))
        self.Zone_height.setValue(int(h))
        self.AutoChangingSize = False

        if self.Zone_presets.itemText(0) == trans.string('ZonesDlg', 60): self.Zone_presets.removeItem(0)

    def PresetDeselected(self, info=None):
        """
        Handles the zone height or width boxes being changed
        """
        if self.AutoChangingSize: return

        self.AutoChangingSize = True
        w = self.Zone_width.value()
        h = self.Zone_height.value()
        check = str(w) + 'x' + str(h)

        found = None
        for preset in self.Zone_presets_values:
            if check == preset[3:]: found = preset


        if found is not None:
            self.Zone_presets.setCurrentIndex(self.Zone_presets.findText(found))
            if self.Zone_presets.itemText(0) == trans.string('ZonesDlg', 60): self.Zone_presets.removeItem(0)
        else:
            if self.Zone_presets.itemText(0) != trans.string('ZonesDlg', 60): self.Zone_presets.insertItem(0, trans.string('ZonesDlg', 60))
            self.Zone_presets.setCurrentIndex(0)
        self.AutoChangingSize = False



#Sets up the Background Dialog
class BGDialog(QtWidgets.QDialog):
    """
    Dialog which lets you choose among various from tabs
    """
    def __init__(self):
        """
        Creates and initializes the tab dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('BGDlg', 0))
        self.setWindowIcon(GetIcon('backgrounds'))

        self.tabWidget = QtWidgets.QTabWidget()

        i = 0
        self.BGTabs = []
        for z in Area.zones:
            i = i+1
            BGTabName = trans.string('BGDlg', 2, '[num]', i)
            tab = BGTab(z)
            self.BGTabs.append(tab)
            self.tabWidget.addTab(tab, BGTabName)


        if self.tabWidget.count() > 5:
            for tab in range(0, self.tabWidget.count()):
                self.tabWidget.setTabText(tab, str(tab + 1))


        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)


class BGTab(QtWidgets.QWidget):
    def __init__(self, z):
        QtWidgets.QWidget.__init__(self)

        self.createBGSettings(z)
        self.createBGViewers(z)

        mainLayout = QtWidgets.QGridLayout()
        mainLayout.addWidget(self.BGASettings, 0, 0)
        mainLayout.addWidget(self.BGBSettings, 1, 0)
        mainLayout.addWidget(self.BGAViewer, 0, 1)
        mainLayout.addWidget(self.BGBViewer, 1, 1)
        self.setLayout(mainLayout)

        self.updatePreviews()


    def createBGSettings(self, z):
        """
        Creates the BG Settings for BGA and BGB
        """
        for slot in ('A', 'B'):
            g = QtWidgets.QGroupBox(trans.string('BGDlg', 3 if slot == 'A' else 4)) # 'Scenery' or 'Backdrop'
            exec('self.BG%sSettings = g' % slot)


            # BG Comboboxes
            exec("""
            self.hex1%s = HexSpinBox()
            self.hex2%s = HexSpinBox()
            self.hex3%s = HexSpinBox()
            self.name1%s = QtWidgets.QComboBox()
            self.name2%s = QtWidgets.QComboBox()
            self.name3%s = QtWidgets.QComboBox()
            for box in (self.hex1%s, self.hex2%s, self.hex3%s):
                box.setRange(0, 0xFFFF)
            self.hex1%s.setValue(z.bg1%s)
            self.hex2%s.setValue(z.bg2%s)
            self.hex3%s.setValue(z.bg3%s)
            self.hex1%s.valueChanged.connect(self.handleHexBox)
            self.hex2%s.valueChanged.connect(self.handleHexBox)
            self.hex3%s.valueChanged.connect(self.handleHexBox)
            self.name1%s.activated.connect(self.handleNameBox)
            self.name2%s.activated.connect(self.handleNameBox)
            self.name3%s.activated.connect(self.handleNameBox)
            for bfile_raw, bname in Bg%sNames:
                bfile = int(bfile_raw, 16)
                self.name1%s.addItem(trans.string('BGDlg', 17, '[name]', bname, '[hex]', '%04X' % bfile), bfile)
                self.name2%s.addItem(trans.string('BGDlg', 17, '[name]', bname, '[hex]', '%04X' % bfile), bfile)
                self.name3%s.addItem(trans.string('BGDlg', 17, '[name]', bname, '[hex]', '%04X' % bfile), bfile)
                if z.bg1%s == bfile: self.name1%s.setCurrentIndex(self.name1%s.count() - 1)
                if z.bg2%s == bfile: self.name2%s.setCurrentIndex(self.name2%s.count() - 1)
                if z.bg3%s == bfile: self.name3%s.setCurrentIndex(self.name3%s.count() - 1)
            """.replace('%s', slot).replace('            ', ''))


            # Position
            exec("""
            self.xpos%s = QtWidgets.QSpinBox()
            self.xpos%s.setToolTip(trans.string('BGDlg', 7))
            self.xpos%s.setRange(-256, 255)
            self.xpos%s.setValue(z.Xposition%s)

            self.ypos%s = QtWidgets.QSpinBox()
            self.ypos%s.setToolTip(trans.string('BGDlg', 9))
            self.ypos%s.setRange(-255, 256)
            self.ypos%s.setValue(-z.Yposition%s)
            """.replace('%s', slot).replace('            ', ''))


            # Scrolling
            exec("""
            self.xscroll%s = QtWidgets.QComboBox()
            self.xscroll%s.addItems(BgScrollRateStrings)
            self.xscroll%s.setToolTip(trans.string('BGDlg', 11))
            if z.Xscroll%s < 0: z.Xscroll%s = 0
            if z.Xscroll%s >= len(BgScrollRates): z.Xscroll%s = len(BgScrollRates)
            self.xscroll%s.setCurrentIndex(z.Xscroll%s)

            self.yscroll%s = QtWidgets.QComboBox()
            self.yscroll%s.addItems(BgScrollRateStrings)
            self.yscroll%s.setToolTip(trans.string('BGDlg', 12))
            if z.Yscroll%s < 0: z.Yscroll%s = 0
            if z.Yscroll%s >= len(BgScrollRates): z.Yscroll%s = len(BgScrollRates)
            self.yscroll%s.setCurrentIndex(z.Yscroll%s)
            """.replace('%s', slot).replace('            ', ''))


            # Zoom
            exec("""
            self.zoom%s = QtWidgets.QComboBox()
            addstr = trans.stringList('BGDlg', 15)
            self.zoom%s.addItems(addstr)
            self.zoom%s.setToolTip(trans.string('BGDlg', 14))
            self.zoom%s.setCurrentIndex(z.Zoom%s)
            """.replace('%s', slot).replace('            ', ''))


            # Labels
            bgLabel = QtWidgets.QLabel(trans.string('BGDlg', 19))
            positionLabel = QtWidgets.QLabel(trans.string('BGDlg', 5))
            scrollLabel = QtWidgets.QLabel(trans.string('BGDlg', 10))
            alignLabel = QtWidgets.QLabel(trans.string('BGDlg', 16))


            # Layouts
            exec("""
            Lpos = QtWidgets.QFormLayout()
            Lpos.addRow(trans.string('BGDlg', 6), self.xpos%s)
            Lpos.addRow(trans.string('BGDlg', 8), self.ypos%s)

            Lscroll = QtWidgets.QFormLayout()
            Lscroll.addRow(trans.string('BGDlg', 6), self.xscroll%s)
            Lscroll.addRow(trans.string('BGDlg', 8), self.yscroll%s)

            Lzoom = QtWidgets.QFormLayout()
            Lzoom.addRow(trans.string('BGDlg', 13), self.zoom%s)
            """.replace('%s', slot).replace('            ', ''))


            exec("""
            mainLayout = QtWidgets.QGridLayout()
            mainLayout.addWidget(bgLabel, 0, 0, 1, 2)
            mainLayout.addWidget(self.hex1%s, 1, 0)
            mainLayout.addWidget(self.hex2%s, 2, 0)
            mainLayout.addWidget(self.hex3%s, 3, 0)
            mainLayout.addWidget(self.name1%s, 1, 1)
            mainLayout.addWidget(self.name2%s, 2, 1)
            mainLayout.addWidget(self.name3%s, 3, 1)
            mainLayout.addWidget(positionLabel, 4, 0)
            mainLayout.addLayout(Lpos, 5, 0)
            mainLayout.addWidget(scrollLabel, 4, 1)
            mainLayout.addLayout(Lscroll, 5, 1)
            mainLayout.addLayout(Lzoom, 6, 0, 1, 2)
            mainLayout.setRowStretch(7, 1)
            self.BG%sSettings.setLayout(mainLayout)
            """.replace('%s', slot).replace('            ', ''))



    def createBGViewers(self, z):
        for slot in ('A', 'B'):
            g = QtWidgets.QGroupBox(trans.string('BGDlg', 16)) # Preview
            exec('self.BG%sViewer = g' % slot)

            exec("""
            self.preview1%s = QtWidgets.QLabel()
            self.preview2%s = QtWidgets.QLabel()
            self.preview3%s = QtWidgets.QLabel()
            self.align%s = QtWidgets.QLabel()

            mainLayout = QtWidgets.QGridLayout()
            mainLayout.addWidget(self.preview1%s, 0, 0)
            mainLayout.addWidget(self.preview2%s, 0, 1)
            mainLayout.addWidget(self.preview3%s, 0, 2)
            mainLayout.addWidget(self.align%s, 1, 0, 1, 3)
            mainLayout.setRowStretch(2, 1)
            self.BG%sViewer.setLayout(mainLayout)
            """.replace('%s', slot).replace('            ', ''))


    @QtCore.pyqtSlot()
    def handleHexBox(self):
        """
        Handles any hex box changing
        """
        for slot in ('A', 'B'):
            for boxnum in (1, 2, 3):
                hexbox = eval('self.hex%d%s' % (boxnum, slot))
                namebox = eval('self.name%d%s' % (boxnum, slot))
                val = hexbox.value()
                idx = namebox.findData(val)
                if idx != -1:
                    # it's a retail BG value
                    namebox.setCurrentIndex(idx)
                    lastEntry = namebox.itemText(namebox.count() - 1)
                    if lastEntry == trans.string('BGDlg', 18): namebox.removeItem(namebox.count() - 1)
                else:
                    # it's a custom BG value
                    lastEntry = namebox.itemText(namebox.count() - 1)
                    if lastEntry != trans.string('BGDlg', 18): namebox.addItem(trans.string('BGDlg', 18))
                    namebox.setCurrentIndex(namebox.count() - 1)
        self.updatePreviews()


    @QtCore.pyqtSlot()
    def handleNameBox(self):
        """
        Handles any name box changing
        """
        for slot in ('A', 'B'):
            for boxnum in (1, 2, 3):
                hexbox = eval('self.hex%d%s' % (boxnum, slot))
                namebox = eval('self.name%d%s' % (boxnum, slot))
                val = namebox.itemData(namebox.currentIndex())
                if val is None: continue # the user chose '(Custom)'
                hexbox.setValue(val)
        self.updatePreviews()


    def updatePreviews(self):
        """
        Updates all 6 preview labels
        """
        scale = 0.75
        for slot in ('A', 'B'):
            for boxnum in (1, 2, 3):
                val = eval('self.hex%d%s' % (boxnum, slot)).value()
                val = '%04X' % val

                filename = gamedef.bgFile(val + '.png', slot.lower())
                if not os.path.isfile(filename):
                    filename = 'reggiedata/bg%s/no_preview.png' % slot.lower()
                pix = QtGui.QPixmap(filename)
                pix = pix.scaled(pix.width() * scale, pix.height() * scale)
                eval('self.preview%d%s' % (boxnum, slot)).setPixmap(pix)

            # Alignment mode
            box1 = eval('self.hex1%s' % slot).value()
            box2 = eval('self.hex2%s' % slot).value()
            box3 = eval('self.hex3%s' % slot).value()
            alignText = trans.stringList('BGDlg', 21)[calculateBgAlignmentMode(box1, box2, box3)]
            alignText = trans.string('BGDlg', 20, '[mode]', alignText)
            eval('self.align%s' % slot).setText(alignText)


def calculateBgAlignmentMode(idA, idB, idC):
    """
    Calculates alignment modes using the exact same logic as NSMBW
    """
    # This really is RE'd ASM translated to Python, mostly

    if idA <= 0x000A: idA = 0
    if idB <= 0x000A: idB = 0
    if idC <= 0x000A: idC = 0

    if ((idA == 0) and (idB == 0)) or (idC == 0):
        # Either both the first two are empty or the last one is empty
        return 0
    elif (idA == idC) and (idB == idC):
        # They are all the same
        return 5
    elif (idA == idC) and (idB != idC) and (idB != 0):
        # The first and last ones are the same, but
        # the middle one is different (not empty, though)
        return 1
    elif (idC == idB) and (idA != idC) and (idA != 0):
        # The second and last ones are the same, but
        # the first one is different (not empty, though)
        return 2
    elif (idB == 0) and (idA != idC) and (idA != 0):
        # The middle one is empty. The first and last
        # ones are different, and the first one is not
        # empty
        return 3
    elif (idA == 0) and (idB != idC) and (idB != 0):
        # The first one is empty. The second and last
        # ones are different, and the second one is not
        # empty
        return 4
    elif (idA == idB) and (idA != 0) and (idB != 0):
        # The first two match, and are not empty
        return 6
    elif (idA != 0) and (idA != 0) and (idB != 0):
        # Every single one is not empty
        return 7
    else:
        # Doesn't fit into any of the above categories
        return 0



#Sets up the Screen Cap Choice Dialog
class ScreenCapChoiceDialog(QtWidgets.QDialog):
    """
    Dialog which lets you choose which zone to take a pic of
    """
    def __init__(self):
        """
        Creates and initializes the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('ScrShtDlg', 0))
        self.setWindowIcon(GetIcon('screenshot'))

        i=0
        self.zoneCombo = QtWidgets.QComboBox()
        self.zoneCombo.addItem(trans.string('ScrShtDlg', 1))
        self.zoneCombo.addItem(trans.string('ScrShtDlg', 2))
        for z in Area.zones:
            i = i+1
            self.zoneCombo.addItem(trans.string('ScrShtDlg', 3, '[zone]', i))


        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.zoneCombo)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)


class AutoSavedInfoDialog(QtWidgets.QDialog):
    """
    Dialog which lets you know that an auto saved level exists
    """

    def __init__(self, filename):
        """
        Creates and initializes the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('AutoSaveDlg', 0))
        self.setWindowIcon(GetIcon('save'))

        mainlayout = QtWidgets.QVBoxLayout(self)

        hlayout = QtWidgets.QHBoxLayout()

        icon = QtWidgets.QLabel()
        hlayout.addWidget(icon)

        label = QtWidgets.QLabel(trans.string('AutoSaveDlg', 1, '[path]', filename))
        label.setWordWrap(True)
        hlayout.addWidget(label)
        hlayout.setStretch(1, 1)

        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.No | QtWidgets.QDialogButtonBox.Yes)
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)

        mainlayout.addLayout(hlayout)
        mainlayout.addWidget(buttonbox)


class AreaChoiceDialog(QtWidgets.QDialog):
    """
    Dialog which lets you choose an area
    """

    def __init__(self, areacount):
        """
        Creates and initializes the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('AreaChoiceDlg', 0))
        self.setWindowIcon(GetIcon('areas'))

        self.areaCombo = QtWidgets.QComboBox()
        for i in range(areacount):
            self.areaCombo.addItem(trans.string('AreaChoiceDlg', 1, '[num]', i+1))

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.areaCombo)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)


class DiagnosticToolDialog(QtWidgets.QDialog):
    """
    Dialog which checks for errors within the level
    """
    def __init__(self):
        """
        Creates and initializes the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('Diag', 0))
        self.setWindowIcon(GetIcon('diagnostics'))

        # CheckFunctions: (icon, description, function, iscritical)
        self.CheckFunctions = (('objects', trans.string('Diag', 1), self.UnusedTilesets, False),
                               ('objects', trans.string('Diag', 2), self.ObjsInTileset, True),
                               ('sprites', trans.string('Diag', 3), self.CrashSprites, False),
                               ('sprites', trans.string('Diag', 4), self.CrashSpriteSettings, True),
                               ('sprites', trans.string('Diag', 5), self.TooManySprites, False),
                               ('entrances', trans.string('Diag', 6), self.DuplicateEntranceIDs, True),
                               ('entrances', trans.string('Diag', 7), self.NoStartEntrance, True),
                               ('entrances', trans.string('Diag', 8), self.EntranceTooCloseToZoneEdge, False),
                               ('entrances', trans.string('Diag', 9), self.EntranceOutsideOfZone, False),
                               ('zones', trans.string('Diag', 10), self.TooManyZones, True),
                               ('zones', trans.string('Diag', 11), self.NoZones, True),
                               ('zones', trans.string('Diag', 12), self.ZonesTooClose, True),
                               ('zones', trans.string('Diag', 13), self.ZonesTooCloseToAreaEdges, True),
                               ('zones', trans.string('Diag', 14), self.BiasNotEnabled, False),
                               ('zones', trans.string('Diag', 15), self.ZonesTooBig, True),
                               #('background', trans.string('Diag', 16), self.UnusedBackgrounds, False),
                               )

        box = QtWidgets.QGroupBox(trans.string('Diag', 17))
        self.errorLayout = QtWidgets.QVBoxLayout()
        result, numErrors = self.populateLists()
        box.setLayout(self.errorLayout)

        self.updateHeader(result)
        hW = QtWidgets.QWidget()
        hW.setLayout(self.header)

        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.addWidget(hW)
        self.mainLayout.addWidget(box)
        self.mainLayout.addWidget(self.buttonBox)
        self.setLayout(self.mainLayout)

    def updateHeader(self, testresult, secondTime = False):
        """
        Creates the header
        """
        self.header = QtWidgets.QGridLayout()
        self.header.addWidget(QtWidgets.QLabel(trans.string('Diag', 18)), 0, 0, 1, 3)

        pointsize = 14 # change this if you don't like it
        if testresult is None: # good
            L = QtWidgets.QLabel()
            L.setPixmap(GetIcon('check', True).pixmap(64, 64))
            self.header.addWidget(L, 1, 0)

            px = QtGui.QPixmap(64, pointsize)
            px.fill(QtGui.QColor(0,0,0,0))
            p = QtGui.QPainter(px)
            f = p.font()
            f.setPointSize(pointsize)
            p.setFont(f)
            p.setPen(QtGui.QColor(0,200,0))
            p.drawText(0, pointsize, trans.string('Diag', 19))
            del p
            L = QtWidgets.QLabel()
            L.setPixmap(px)
            self.header.addWidget(L, 1, 1)

            self.header.addWidget(QtWidgets.QLabel(trans.string('Diag', 20)), 1, 2)
        elif not testresult: # warnings
            L = QtWidgets.QLabel()
            L.setPixmap(GetIcon('warning', True).pixmap(64, 64))
            self.header.addWidget(L, 1, 0)

            px = QtGui.QPixmap(128, pointsize*3/2)
            px.fill(QtGui.QColor(0,0,0,0))
            p = QtGui.QPainter(px)
            f = p.font()
            f.setPointSize(pointsize)
            p.setFont(f)
            p.setPen(QtGui.QColor(210,210,0))
            p.drawText(0, pointsize, trans.string('Diag', 21))
            del p
            L = QtWidgets.QLabel()
            L.setPixmap(px)
            self.header.addWidget(L, 1, 1)

            self.header.addWidget(QtWidgets.QLabel(trans.string('Diag', 22)), 1, 2)
        else: # bad
            L = QtWidgets.QLabel()
            L.setPixmap(GetIcon('delete', True).pixmap(64, 64))
            self.header.addWidget(L, 1, 0)

            px = QtGui.QPixmap(72, pointsize)
            px.fill(QtGui.QColor(0,0,0,0))
            p = QtGui.QPainter(px)
            f = p.font()
            f.setPointSize(pointsize)
            p.setFont(f)
            p.setPen(QtGui.QColor(255,0,0))
            p.drawText(0, pointsize, trans.string('Diag', 23))
            del p
            L = QtWidgets.QLabel()
            L.setPixmap(px)
            self.header.addWidget(L, 1, 1)

            self.header.addWidget(QtWidgets.QLabel(trans.string('Diag', 24)), 1, 2)

        if secondTime:
            w = QtWidgets.QWidget()
            w.setLayout(self.header)
            self.mainLayout.takeAt(0).widget().hide()
            self.mainLayout.insertWidget(0, w)


    def populateLists(self):
        """
        Runs the check functions and adds items to the list if needed
        """
        self.buttonHandlers = []

        self.errorList = QtWidgets.QListWidget()
        self.errorList.setSelectionMode(self.errorList.MultiSelection)

        foundAnything = False
        foundCritical = False
        for ico, desc, fxn, isCritical in self.CheckFunctions:
            if fxn('c'):

                foundAnything = True
                if isCritical: foundCritical = True

                item = QtWidgets.QListWidgetItem()
                item.setText(desc)
                if isCritical: item.setForeground(QtGui.QColor(255, 0, 0))
                else:          item.setForeground(QtGui.QColor(172, 172, 0))
                item.setIcon(GetIcon(ico))
                item.fix = fxn

                self.errorList.addItem(item)

        self.fixBtn = QtWidgets.QPushButton(trans.string('Diag', 25))
        self.fixBtn.setToolTip(trans.string('Diag', 26))
        self.fixBtn.clicked.connect(self.FixSelected)
        if not foundAnything: self.fixBtn.setEnabled(False)

        self.errorLayout.addWidget(self.errorList)
        self.errorLayout.addWidget(self.fixBtn)

        if foundCritical: return True, len(self.buttonHandlers)
        elif foundAnything: return False, len(self.buttonHandlers)
        return None, len(self.buttonHandlers)


    def FixSelected(self):
        """
        Fixes the selected items
        """

        # Ask the user to make sure
        btn = QtWidgets.QMessageBox.warning(None, trans.string('Diag', 27), trans.string('Diag', 28), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if btn != QtWidgets.QMessageBox.Yes: return

        # Show the 'Fixing...' box while fixing
        pleasewait = QtWidgets.QProgressDialog()
        pleasewait.setLabelText(trans.string('Diag', 29)) # Fixing...
        pleasewait.setMinimum(0)
        pleasewait.setMaximum(100)
        pleasewait.setAutoClose(True)
        pleasewait.open()
        pleasewait.show()
        pleasewait.setValue(0)

        # Fix them
        for index, item in enumerate(self.errorList.selectedIndexes()[:]):
            listItem = self.errorList.itemFromIndex(item)
            try: listItem.fix()
            except Exception: pass # fail silently
            self.errorList.takeItem(item.row())

            total = len(self.errorList.selectedIndexes()[:])
            if total != 0: pleasewait.setValue(int(float(index)/total*100))

        # Remove the 'Fixing...' box
        pleasewait.setValue(100)
        del pleasewait

        # Gray out the Fix button if there are no more problems
        if self.errorList.count() == 0: self.fixBtn.setEnabled(False)


    def UnusedTilesets(self, mode='f'):
        """
        Checks for any tilesets in this area not found in NSMBWii
        """
        global Area
        global TilesetNames

        # Find all retail tileset names
        possible = ['', ' ', None] # empty tilesets are represented by ''
        for palette in SimpleTilesetNames():
            for tileset in palette:
                possible.append(tileset[0])

        # Check if any tilesets aren't retail
        TS0 = True
        TS1 = True
        TS2 = True
        TS3 = True
        if Area.tileset0 not in possible: TS0 = False
        if Area.tileset1 not in possible: TS1 = False
        if Area.tileset2 not in possible: TS2 = False
        if Area.tileset3 not in possible: TS3 = False

        # Do the appropriate thing based on mode
        if mode == 'c':
            return not (TS0 and TS1 and TS2 and TS3)
        else:
            # Remove all non-retail tilesets
            for IsRetail, name, slot in ((TS0, 'Area.tileset0', 0), (TS1, 'Area.tileset1', 1), (TS2, 'Area.tileset2', 2), (TS3, 'Area.tileset3', 3)):
                if IsRetail: continue

                UnloadTileset(slot)
                exec(name + ' = \'\' if slot != 0 else \'J_Kihon\'')

            self.ObjsInTileset('f') # remove all orphaned objects w/o a loaded tileset

            # Update the palette
            mainWindow.objPicker.LoadFromTilesets()
            self.objAllTab.setCurrentIndex(0)
            self.objAllTab.setTabEnabled(0, (Area.tileset0 != ''))
            self.objAllTab.setTabEnabled(1, (Area.tileset1 != ''))
            self.objAllTab.setTabEnabled(2, (Area.tileset2 != ''))
            self.objAllTab.setTabEnabled(3, (Area.tileset3 != ''))

            # Update the layers
            for layer in Area.layers:
                for obj in layer:
                    obj.updateObjCache()

            # Update the scene
            self.scene.update()


    def ObjsInTileset(self, mode='f'):
        """
        Checks for any objects which cannot be found in the tilesets
        """
        global Area
        global ObjectDefinitions

        deletions = []
        for Layer in Area.layers:
            for obj in Layer:

                if ObjectDefinitions[obj.tileset] is None:
                    deletions.append(obj)
                elif ObjectDefinitions[obj.tileset][obj.type] is None:
                    deletions.append(obj)

        if mode == 'c': return len(deletions) != 0
        elif len(deletions) != 0:
            for obj in deletions:
                obj.delete()
                obj.setSelected(False)
                mainWindow.scene.removeItem(obj)

            mainWindow.levelOverview.update()


    def CrashSprites(self, mode='f'):
        """
        Checks if there are any sprites which are known to be crashy and cause problems often
        """
        global Area
        problems = (0,1,2,3,4,5,6,7,8,9, # glitch sprites
                    121, # en reverse
                    475) # will crash if you use a looped path

        founds = []
        for sprite in Area.sprites:
            if sprite.type in problems: founds.append(sprite)

        if mode == 'c': return len(founds) != 0
        else:
            for sprite in founds:
                sprite.delete()
                sprite.setSelected(False)
                mainWindow.scene.removeItem(sprite)
                mainWindow.levelOverview.update()


    def CrashSpriteSettings(self, mode='f'):
        """
        Checks for sprite settings which are known to cause major glitches and crashes
        """
        global Area

        checkfor = []
        problem = False
        for sprite in Area.sprites:
            # ask somebody about 153 for clarification, the add it to the fixers
            if sprite.type == 166 and (ord(sprite.spritedata[2]) & 0xF0) >> 4 == 4: problem = True
            #           also double-check nyb10, then add it to the fixers
            if sprite.type == 171 and ord(sprite.spritedata[4]) & 0xF != 1: problem = True
            if sprite.type == 203 and ord(sprite.spritedata[4]) & 0xF == 1:
                if [454, 432] not in checkfor: checkfor.append([454, 432])
            if sprite.type == 247 and ord(sprite.spritedata[5]) & 0xF == 1: problem = True
            if sprite.type == 323:
                if ord(sprite.spritedata[4]) & 0xF == 4: problem = True
                if ord(sprite.spritedata[2]) & 0xF < (ord(sprite.spritedata[3]) & 0xF0) >> 4: problem = True
            if sprite.type == 449 and (ord(sprite.spritedata[5]) & 0xF0) >> 4 == 1: problem = True
            if sprite.type == 479 and ord(sprite.spritedata[4]) & 0xF == 1: problem = True
            if sprite.type == 481:
                if ord(sprite.spritedata[5]) & 0xF > 2: problem = True
                if [419] not in checkfor: checkfor.append([419])

        # check for sprites which are depended on by other sprites
        new = list(checkfor)
        for item in checkfor:
            for sprite in Area.sprites:
                if sprite.type in item:
                    try: new.remove(item)
                    except Exception: pass # probably already removed it
        checkfor = new
        if len(checkfor) > 0: problem = True

        if mode == 'c': return problem
        elif problem:
            addsprites = []
            for sprite in Area.sprites:
                # :(
                if sprite.type == 166 and (ord(sprite.spritedata[2]) & 0xF0) >> 4 == 4: sprite.spritedata = sprite.spritedata[0:2]+' '+sprite.spritedata[3:]
                if sprite.type == 171 and ord(sprite.spritedata[4]) & 0xF != 1: sprite.spritedata = sprite.spritedata[0:4]+chr(1)+sprite.spritedata[5:]
                if sprite.type == 203 and ord(sprite.spritedata[4]) & 0xF == 1:
                    if [454, 432] in checkfor:
                        addsprites.append((454, sprite.objx-128, sprite.objy-128))
                if sprite.type == 247 and ord(sprite.spritedata[5]) & 0xF == 1: sprite.spritedata = sprite.spritedata[0:5]+chr(0)+sprite.spritedata[6:]
                if sprite.type == 323:
                    if ord(sprite.spritedata[4]) & 0xF == 4: sprite.spritedata = sprite.spritedata[0:4]+chr(1)+sprite.spritedata[5:]
                    if ord(sprite.spritedata[2]) & 0xF < (ord(sprite.spritedata[3]) & 0xF0) >> 4:
                        sprite.spritedata = sprite.spritedata[0:2] + chr((ord(sprite.spritedata[3]) & 0xF0) >> 4)+sprite.spritedata[3:]
                if sprite.type == 449 and (ord(sprite.spritedata[5]) & 0xF0) >> 4 == 1: sprite.spritedata = sprite.spritedata[0:5]+chr(0)+sprite.spritedata[6:]
                if sprite.type == 479 and ord(sprite.spritedata[4]) & 0xF == 1:
                    if (ord(sprite.spritedata[4]) & 0xF0) >> 4 == 1: sprite.spritedata = sprite.spritedata[0:4]+chr(0x10)+sprite.spritedata[5:]
                    else: sprite.spritedata = sprite.spritedata[0:4]+chr(0)+sprite.spritedata[5:]
                if sprite.type == 481:
                    if ord(sprite.spritedata[5]) & 0xF > 2: sprite.spritedata = sprite.spritdata[0:5]+chr(2)+sprite.spritedata[6:]
                    addsprites.append((419, sprite.objx-128, sprite.objy-128))

            for id, x, y in addsprites:
                new = SpriteItem(id, x, y, '\0\0\0\0\0\0\0\0\0\0')
                new.positionChanged = mainWindow.HandleSprPosChange
                mainWindow.scene.addItem(new)

                new.listitem = ListWidgetItem_SortsByOther(new)
                mainWindow.spriteList.addItem(new.listitem)
                Area.sprites.append(new)
                mainWindow.scene.update()

                new.UpdateListItem()


    def TooManySprites(self, mode='f'):
        """
        Determines if the # of sprites in the current area is > max
        """
        global Area
        max = 1000

        problem = len(Area.sprites) > max
        if mode == 'c': return problem
        elif problem:
            for spr in Area.sprites[max:]:
                spr.delete()
                spr.setSelected(False)
                mainWindow.scene.removeItem(spr)

            Area.sprites = Area.sprites[0:max]
            mainWindow.scene.update()
            mainWindow.levelOverview.update()


    def DuplicateEntranceIDs(self, mode='f'):
        """
        Checks for the prescence of multiple entrances with the same ID
        """
        global Area

        IDs = []
        for ent in Area.entrances:
            if ent.entid in IDs:
                if mode == 'c': return False
                else:
                    # find the lowest available ID
                    getids = [False for x in range(256)]
                    for check in Area.entrances: getids[check.entid] = True
                    minimumID = getids.index(False)

                    ent.entid = minimumID
                    ent.UpdateTooltip()
                    ent.UpdateListItem()
            IDs.append(ent.entid)

        return False


    def NoStartEntrance(self, mode='f'):
        """
        Determines if there is a start entrance or not
        """
        global Area

        start = None
        for ent in Area.entrances:
            if ent.entid == Area.startEntrance: start = ent
        else: problem = False
        problem = start is None


        if mode == 'c': return problem
        elif problem:
            # make an entrance at 1024, 512 with an ID of Area.startEntrance
            ent = EntranceItem(1024, 512, Area.startEntrance, 0, 0, 0, 0, 0, 0, 0x80, 0)
            ent.positionChanged = mainWindow.HandleEntPosChange
            mainWindow.scene.addItem(ent)

            elist = mainWindow.entranceList
            ent.listitem = ListWidgetItem_SortsByOther(ent)
            elist.insertItem(Area.startEntrance, ent.listitem)

            global PaintingEntrance, PaintingEntranceListIndex
            PaintingEntrance = ent
            PaintingEntranceListIndex = Area.startEntrance
            Area.entrances.insert(Area.startEntrance, ent)

            ent.UpdateListItem()

            SetDirty()


    def EntranceTooCloseToZoneEdge(self, mode='f'):
        """
        Checks if the main entrance is too close to the left zone edge
        """
        global Area
        offset = 24 * 8 # 8 blocks away from the left zone edge
        if len(Area.zones) == 0: return False

        # if the ent isn't even in the zone, return
        if self.EntranceOutsideOfZone('c'): return False

        start = None
        for ent in Area.entrances:
            if ent.entid == Area.startEntrance: start = ent
        if start is None: return False

        firstzoneid = MapPositionToZoneID(Area.zones, start.objx, start.objy, True)
        firstzone = None
        for z in Area.zones:
            if z.id == firstzoneid: firstzone = z
        if firstzone is None: return False

        problem = start.objx < firstzone.objx + offset
        if mode == 'c': return problem
        elif problem: start.setPos((firstzone.objx + offset)*1.5, start.objy*1.5)


    def EntranceOutsideOfZone(self, mode='f'):
        """
        Checks if any entrances are not inside of a zone
        """
        global Area
        left_offset = 24 * 8 # 8 blocks away from the left zone edge
        if len(Area.zones) == 0: return False

        for ent in Area.entrances:
            x = ent.objx
            y = ent.objy
            zoneID = MapPositionToZoneID(Area.zones, x, y, True)
            zone = None
            for z in Area.zones:
                if z.id == zoneID: zone = z
            if zone is None: return False

            if   x < zone.objx: problem = True
            elif x > zone.objx + zone.width: problem = True
            elif y < zone.objy - 64: problem = True
            elif y > zone.objy + zone.height: problem = True
            else: problem = False

            if problem and mode == 'c': return True
            elif problem:
                if   x < zone.objx:               newx = zone.objx + left_offset
                elif x > zone.objx + zone.width:  newx = zone.objx + zone.width - 16
                else:                             newx = ent.objx
                if   y < (zone.objy - 64):        newy = zone.objy - 64 # entrances can be placed a few blocks above the top zone border
                elif y > zone.objy + zone.height: newy = zone.objy + zone.height - 32
                else:                             newy = ent.objy
                ent.objx = newx
                ent.objy = newy
                ent.setPos(int(newx*1.5), int(newy*1.5))
                mainWindow.scene.update()

        return False


    def TooManyZones(self, mode='f'):
        """
        Checks if there are too many zones in this area
        """
        global Area

        problem = len(Area.zones) > 8

        if mode == 'c': return problem
        elif problem:
            Area.zones = Area.zones[0:8]

            mainWindow.scene.update()
            mainWindow.levelOverview.update()


    def NoZones(self, mode='f'):
        """
        Checks if there are no zones in this area
        """
        global Area

        problem = len(Area.zones) == 0
        if mode == 'c': return problem
        elif problem:
            # make a default zone
            a = []
            b = []
            a.append([0, 0, 0, 0, 0, 0])
            b.append([0, 0, 0, 0, 0, 10, 10, 10, 0])
            z = ZoneItem(16, 16, 448, 224, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, a, b, b, len(Area.zones))

            z.UpdateTitle()
            Area.zones.append(z)
            mainWindow.scene.addItem(z)
            mainWindow.scene.update()
            mainWindow.levelOverview.update()


    def ZonesTooClose(self, mode='f'):
        """
        Checks for any zones which are too close together or are overlapping
        """
        global Area
        padding = 4 # minimum blocks between zones

        for check in reversed(Area.zones): # reversed because generally zone 0 is most important, 1 is less, 2 is lesser, etc.
            crect = check.ZoneRect
            for against in Area.zones:
                if check is against: continue
                arect = against.ZoneRect.adjusted(-16*padding,-16*padding,16*padding,16*padding)

                if crect.intersects(arect):
                    if mode=='c': return True
                    else:
                        # AAAAAAAAAAA
                        center = crect.center()

                        if arect.contains(crect) or crect.contains(arect):
                            # one inside the other
                            axes = [None, 'both']
                        elif abs(center.x()-arect.center().x()) > abs(center.y()-arect.center().y()):
                            # horizontally positioned
                            if arect.center().x() > center.x():
                                # shrink the right
                                axes = [None, 'w']
                            else:
                                # shrink the left
                                axes = ['x', 'w']
                        else:
                            # vertically positioned
                            if arect.center().y() < center.y():
                                # shrink the top
                                axes = ['y', 'h']
                            else:
                                # shrink the bottom
                                axes = [None, 'h']

                        # the simplest method :D
                        checkzone = check.ZoneRect
                        oldCoords = checkzone.getCoords()
                        while checkzone.intersects(arect):
                            if axes[0] is None: pass
                            elif axes[0] == 'x': check.objx += 1
                            else: check.objy += 1

                            if axes[1] == 'both':
                                check.objx += 1
                                check.objy += 1
                            elif axes[1] == 'w': check.width -= 1
                            else: check.height -= 1
                            if check.width < 300: check.width = 300
                            if check.height < 200: check.height = 200

                            check.UpdateRects()
                            check.setPos(int(check.objx * 1.5), int(check.objy * 1.5))
                            mainWindow.scene.update()
                            checkzone = check.ZoneRect

                            if oldCoords == checkzone.getCoords(): break
                            oldCoords = checkzone.getCoords()

                        mainWindow.scene.update()

        return False


    def ZonesTooCloseToAreaEdges(self, mode='f'):
        """
        Checks for any zones which are too close to the area edges, and moves them
        """
        global Area
        areaw = 16384
        areah = 8192

        for z in Area.zones:
            if (z.objx < 16) or (z.objy < 16) or (z.objx + z.width > areaw - 16) or (z.objy + z.height > areah - 16):
                if mode=='c': return False
                else:
                    if z.objx < 16: z.objx = 16
                    if z.objy < 16: z.objy = 16
                    if z.objx + z.width > areaw - 16: z.width = areaw - z.objx - 16
                    if z.objy + z.height > areah - 16: z.height = areah - z.objy - 16
                    z.UpdateRects()
                    mainWindow.scene.update()

        return False


    def BiasNotEnabled(self, mode='f'):
        """
        Checks for any zones which do not have bias enabled
        """
        global Area
        fix = {'0 0':  (0, 1),
               '0 7':  (0, 6),
               '0 11': (0, 4),
               '3 2':  (0, 3),
               '3 7':  (3, 3),      # This doesn't always appear
               '6 0':  (6, 2),      # to work due to inconsistencies
               '6 7':  (6, 6),      # in the editor, but I'm pretty
               '6 11': (6, 4),      # sure it's written correctly.
               '1 0':  (1, 1),
               '1 7':  (1, 10),
               '1 11': (1, 4),
               '4 2':  (1, 3),
               '4 7':  (4, 3)}

        for z in Area.zones:
            check = str(z.cammode) + ' ' + str(z.camzoom)
            if check in fix:
                if mode=='c': return False
                else:
                    z.cammode = fix[check][0]
                    z.camzoom = fix[check][1]

        return False


    def ZonesTooBig(self, mode='f'):
        """
        Checks for any zones which may be too large
        """
        global Area
        maxarea = 16384 # blocks (approximated value)

        for z in Area.zones:
            if int((z.width/32)*(z.height/32)) > maxarea*8:
                if mode == 'c': return False
                else: # shrink it by whichever dimension is larger
                    if z.width > z.height: z.width = int(256*maxarea/z.height)
                    else: z.height = int(256*maxarea/z.width)
                    z.UpdateRects()
                    mainWindow.scene.update()

        return False


    def ZonesTooSmall(self, mode='f'):
        """
        Checks for any zones which may be too small for their zoom level
        """
        global Area
        MinimumSize = (484, 272)
##                        (484, 272), # -1
##                        (484, 272), # 0
##                        (484, 272), # 1
##                        (540, 304), # 2
##                        (596, 336), # 3
##                        (796, 448)) # 4
##        ZoomLevels = (3,
##                      3,
##                      6,
##                      6,
##                      5,
##                      None,
##                      4,
##                      4,
##                      0,
##                      1,
##                      None,
##                      5)

        fixes = []
        for z in Area.zones:
            if z.width < MinimumSize[0]:
                fixes.append(z)
            elif z.height < MinimumSize[1]:
                fixes.append(z)

        if mode == 'c':
            return False if len(fixes) == 0 else True

        for z in fixes:
            if z.width < MinimumSize[0]: z.width = MinimumSize[0]
            if z.height < MinimumSize[1]: z.height = MinimumSize[1]
            z.prepareGeometryChange()
            z.UpdateRects()

        mainWindow.scene.update()
        mainWindow.levelOverview.update()


    def UnusedBackgrounds(self, mode='f'):
        """
        Checks if there are custom background IDs in this area
        """
        global Area
        global BgANames
        global BgBNames

        for z in Area.zones:
            for name in ('1A', '2A', '3A', '1B', '2B', '3B'):
                bg = eval('z.bg%s' % name)
                id = '%04X' % bg
                if name[1] == 'A': check = BgANames
                else: check = BgBNames

                found = False
                for entry in check:
                    if id in entry: found = True

                if not found:
                    if mode == 'c': return True
                    else:
                        if   name == '1A': z.bg1A = 1
                        elif name == '2A': z.bg2A = 1
                        elif name == '3A': z.bg3A = 1
                        elif name == '1B': z.bg1B = 1
                        elif name == '2B': z.bg2B = 1
                        elif name == '3B': z.bg3B = 1
        return False



class ReggieRibbon(QRibbon):
    """
    Class that represents Reggie's ribbon
    """
    def __init__(self):
        """
        Creates and initializes the Reggie Ribbon
        """
        QRibbon.__init__(self)

        # Set up the file menu
        self.fileMenu = ReggieRibbonFileMenu()
        self.setFileMenu(self.fileMenu)
        self.setFileTitle(trans.string('Ribbon', 23))

        # Add tabs
        self.btns = {}
        self.addHomeTab()
        self.addActionsTab()
        self.addViewTab()

        # Add the Help Menu
        m = mainWindow.SetupHelpMenu()
        self.setHelpMenu(m)
        self.setHelpIcon(GetIcon('help'))

        # Stylize on Windows
        self.stylizeOnWindows(mainWindow)

        global theme


    def addHomeTab(self):
        """
        Adds the Home Tab
        """
        tab = self.addTab(trans.string('Ribbon', 0)) # "Home"
        self.homeTab = tab

        gi, ts, mw, qk = GetIcon, trans.string, mainWindow, QtGui.QKeySequence

        # Clipboard Section
        cSection = tab.addSection(ts('Ribbon', 5)) # "Clipboard"
        a = cSection.addFullButton(gi('paste', True), ts('MenuItems', 30), mw.Paste, qk.Paste, ts('MenuItems', 31))
        b = cSection.addSmallButton(gi('cut'),   ts('MenuItems', 26), mw.Cut,   qk.Cut,   ts('MenuItems', 27))
        c = cSection.addSmallButton(gi('copy'),  ts('MenuItems', 28), mw.Copy,  qk.Copy,  ts('MenuItems', 29))
        self.btns['paste'], self.btns['cut'], self.btns['copy'] = a, b, c
        self.btns['cut'].setEnabled(False)
        self.btns['copy'].setEnabled(False)

        # Freeze Section
        fSection = tab.addSection(ts('Ribbon', 6)) # "Freeze"
        a = fSection.addSmallToggleButton(gi('objectsfreeze'),   None, mw.HandleObjectsFreeze,   'Ctrl+Shift+1', ts('MenuItems', 39))
        b = fSection.addSmallToggleButton(gi('spritesfreeze'),   None, mw.HandleSpritesFreeze,   'Ctrl+Shift+2', ts('MenuItems', 41))
        c = fSection.addSmallToggleButton(gi('entrancesfreeze'), None, mw.HandleEntrancesFreeze, 'Ctrl+Shift+3', ts('MenuItems', 43))
        d = fSection.addSmallToggleButton(gi('locationsfreeze'), None, mw.HandleLocationsFreeze, 'Ctrl+Shift+4', ts('MenuItems', 45))
        e = fSection.addSmallToggleButton(gi('pathsfreeze'),     None, mw.HandlePathsFreeze,     'Ctrl+Shift+5', ts('MenuItems', 47))
        f = fSection.addSmallToggleButton(gi('commentsfreeze'),  None, mw.HandleCommentsFreeze,  'Ctrl+Shift+9', ts('MenuItems', 115))
        self.btns['objfrz'], self.btns['sprfrz'], self.btns['entfrz'], self.btns['locfrz'], self.btns['pthfrz'], self.btns['comfrz'] = a, b, c, d, e, f

        # Area Section
        aSection = tab.addSection(ts('Ribbon', 8)) # "Area"
        #a = aSection.addCustomWidget(self.AreaMenuButton())
        b = aSection.addFullButton(gi('area', True), ts('MenuItems', 72), mw.HandleAreaOptions, 'Ctrl+Alt+A', ts('MenuItems', 73))
        #self.btns['areasel'], self.btns['areaset'] = a, b
            ##        LGroup.addButton(mainWindow.HandleAreaOptions, 'Ctrl+Alt+A', trans.string('MenuItems', 73), True, 'area', trans.string('MenuItems', 72))

        # Set the toggle buttons to their default positions
        self.btns['objfrz'].setChecked(ObjectsFrozen)
        self.btns['sprfrz'].setChecked(SpritesFrozen)
        self.btns['entfrz'].setChecked(EntrancesFrozen)
        self.btns['locfrz'].setChecked(LocationsFrozen)
        self.btns['pthfrz'].setChecked(PathsFrozen)
        self.btns['comfrz'].setChecked(CommentsFrozen)

        return # Everything after this is old

##        cGroup = RibbonGroup(trans.string('Ribbon', 5)) # Clipboard
##        tab.cutBtn   = cGroup.addButton(mainWindow.Cut, QtGui.QKeySequence.Cut, trans.string('MenuItems', 27), False, 'cut', trans.string('MenuItems', 26))
##        tab.copyBtn  = cGroup.addButton(mainWindow.Copy, QtGui.QKeySequence.Copy, trans.string('MenuItems', 29), False, 'copy', trans.string('MenuItems', 28))
##        tab.pasteBtn = cGroup.addButton(mainWindow.Paste, QtGui.QKeySequence.Paste, trans.string('MenuItems', 31), True, 'paste', trans.string('MenuItems', 30))
##        tab.cutBtn.setEnabled(False)
##        tab.copyBtn.setEnabled(False) # nothing should be selected yet
##
##        fGroup = RibbonGroup(trans.string('Ribbon', 6)) # Freeze
##
##
##        iGroup = RibbonGroup(trans.string('Ribbon', 7)) # Level Information
##        iGroup.addButton(mainWindow.HandleInfo, 'Ctrl+Alt+I', trans.string('MenuItems', 13), True, 'info', trans.string('MenuItems', 12))
##        tab.infoWidget = InfoPreviewWidget(Qt.Horizontal)
##        iGroup.addWidget(tab.infoWidget)
##
##        aGroup = RibbonGroup(trans.string('Ribbon', 8)) # Area
##        tab.areaComboBox = QtWidgets.QComboBox()
##        tab.areaComboBox.activated.connect(mainWindow.HandleSwitchArea)
##        aGroup.addWidget(tab.areaComboBox)
##
##        tab.addGroup(cGroup)
##        tab.addGroup(fGroup)
##        tab.addGroup(iGroup)
##        tab.addGroup(aGroup)
##        tab.finish()
##
##        return tab


    def addActionsTab(self):
        """
        Adds the Actions Tab
        """
        tab = self.addTab(trans.string('Ribbon', 1)) # "Actions"
        self.actionsTab = tab

        gi, ts, mw, qk = GetIcon, trans.string, mainWindow, QtGui.QKeySequence

        return # Everything after this is old

##        sGroup = RibbonGroup(trans.string('Ribbon', 9)) # Selection
##        sGroup.addButton(mainWindow.SelectAll, QtGui.QKeySequence.SelectAll, trans.string('MenuItems', 23), False, 'select', trans.string('MenuItems', 22))
##        tab.deselBtn = sGroup.addButton(mainWindow.Deselect, 'Ctrl+D', trans.string('MenuItems', 25), False, 'deselect', trans.string('MenuItems', 24))
##        tab.deselBtn.setEnabled(False) # nothing should be selected upon startup
##
##        iGroup = RibbonGroup(trans.string('Ribbon', 10)) # Items
##        tab.shiftBtn = iGroup.addButton(mainWindow.ShiftItems, 'Ctrl+Shift+S', trans.string('MenuItems', 33), False, 'move', trans.string('MenuItems', 32))
##        tab.mergeBtn = iGroup.addButton(mainWindow.MergeLocations, 'Ctrl+Shift+E', trans.string('MenuItems', 35), False, 'merge', trans.string('MenuItems', 34))
##        iGroup.addButton(mainWindow.SwapObjectsTilesets, 'Ctrl+Shift+L', trans.string('MenuItems', 105), False, 'swap', trans.string('MenuItems', 104))
##        iGroup.addButton(mainWindow.SwapObjectsTypes, 'Ctrl+Shift+Y', trans.string('MenuItems', 107), False, 'swap', trans.string('MenuItems', 106))
##
##        tab.shiftBtn.setEnabled(False)
##        tab.mergeBtn.setEnabled(False)
##
##        LGroup = RibbonGroup(trans.string('Ribbon', 11)) # Level Settings
##        LGroup.addButton(mainWindow.HandleAreaOptions, 'Ctrl+Alt+A', trans.string('MenuItems', 73), True, 'area', trans.string('MenuItems', 72))
##        LGroup.addButton(mainWindow.HandleZones, 'Ctrl+Alt+Z', trans.string('MenuItems', 75), True, 'zones', trans.string('MenuItems', 74))
##        LGroup.addButton(mainWindow.HandleBG, 'Ctrl+Alt+B', trans.string('MenuItems', 77), True, 'background', trans.string('MenuItems', 76))
##        LGroup.addButton(mainWindow.HandleDiagnostics, 'Ctrl+Shift+D', trans.string('MenuItems', 37), True, 'diagnostics', trans.string('MenuItems', 36))
##        LGroup.addButton(mainWindow.HandleChangeGamePath, 'Ctrl+Alt+G', trans.string('MenuItems', 17), False, 'folderpath', trans.string('MenuItems', 16))
##        LGroup.addButton(mainWindow.HandleScreenshot, 'Ctrl+Alt+S', trans.string('MenuItems', 15), False, 'screenshot', trans.string('MenuItems', 14))
##
##        aGroup = RibbonGroup(trans.string('Ribbon', 12)) # Areas
##        tab.addAreaBtn    = aGroup.addButton(mainWindow.HandleAddNewArea, 'Ctrl+Alt+N', trans.string('MenuItems', 79), True, 'add', trans.string('MenuItems', 78))
##        tab.importAreaBtn = aGroup.addButton(mainWindow.HandleImportArea, 'Ctrl+Alt+O', trans.string('MenuItems', 81), False, 'import', trans.string('MenuItems', 80))
##        tab.deleteAreaBtn = aGroup.addButton(mainWindow.HandleDeleteArea, 'Ctrl+Alt+D', trans.string('MenuItems', 83), False, 'delete', trans.string('MenuItems', 82))
##
##        tGroup = RibbonGroup(trans.string('Ribbon', 13)) # Tilesets
##        tGroup.addButton(mainWindow.ReloadTilesets, 'Ctrl+Shift+R', trans.string('MenuItems', 85), True, 'reload', trans.string('MenuItems', 84))
##
##        tab.addGroup(sGroup)
##        tab.addGroup(iGroup)
##        tab.addGroup(LGroup)
##        tab.addGroup(aGroup)
##        tab.addGroup(tGroup)
##        tab.finish()
##
##        return tab

    def addViewTab(self):
        """
        Adds the View Tab
        """
        tab = self.addTab(trans.string('Ribbon', 2)) # "View"
        self.viewTab = tab

        gi, ts, mw, qk = GetIcon, trans.string, mainWindow, QtGui.QKeySequence

        # Layers
        LSection = tab.addSection(ts('Ribbon', 14)) # "Layers"
        a = LSection.addFullToggleButton(gi('layer0', True), ts('MenuItems', 48), mw.HandleUpdateLayer0, 'Ctrl+1', ts('MenuItems', 49))
        b = LSection.addFullToggleButton(gi('layer1', True), ts('MenuItems', 50), mw.HandleUpdateLayer1, 'Ctrl+2', ts('MenuItems', 51))
        c = LSection.addFullToggleButton(gi('layer2', True), ts('MenuItems', 52), mw.HandleUpdateLayer2, 'Ctrl+3', ts('MenuItems', 53))
        self.btns['lay0'], self.btns['lay1'], self.btns['lay2'] = a, b, c

        # Tilesets
        tSection = tab.addSection(ts('Ribbon', 13)) # "Tilesets"
        a = tSection.addSmallToggleButton(gi('animation'),  ts('MenuItems', 108), mw.HandleTilesetAnimToggle, 'Ctrl+7', ts('MenuItems', 109))
        b = tSection.addSmallToggleButton(gi('collisions'), ts('MenuItems', 110), mw.HandleCollisionsToggle,  'Ctrl+8', ts('MenuItems', 111))
        self.btns['anim'], self.btns['colls'] = a, b

        # Visibility
        vSection = tab.addSection(ts('Ribbon', 15)) # "Visibility"
        a = vSection.addSmallToggleButton(gi('sprites'),    ts('MenuItems', 54),  mw.HandleSpritesVisibility,   'Ctrl+4', ts('MenuItems', 55))
        b = vSection.addSmallToggleButton(gi('sprites'),    ts('MenuItems', 56),  mw.HandleSpriteImages,        'Ctrl+6', ts('MenuItems', 57))
        c = vSection.addSmallToggleButton(gi('locations'),  ts('MenuItems', 58),  mw.HandleLocationsVisibility, 'Ctrl+5', ts('MenuItems', 59))
        d = vSection.addSmallToggleButton(gi('comments'),   ts('MenuItems', 116), mw.HandleCommentsVisibility,  'Ctrl+0', ts('MenuItems', 117))
        e = vSection.addSmallToggleButton(gi('realview'),   ts('MenuItems', 118), mw.HandleRealViewToggle,  'Ctrl+9', ts('MenuItems', 119))
        f = vSection.addFullButton(       gi('grid', True), ts('MenuItems', 60),  mw.HandleSwitchGrid,          'Ctrl+G', ts('MenuItems', 61))
        self.btns['showsprites'], self.btns['showspriteimgs'], self.btns['showlocs'], self.btns['showcoms'], self.btns['realview'], self.btns['grid'] = a, b, c, d, e, f

        # Set the toggle buttons to their default start values
        self.btns['lay0'].setChecked(Layer0Shown)
        self.btns['lay1'].setChecked(Layer1Shown)
        self.btns['lay2'].setChecked(Layer2Shown)
        self.btns['showsprites'].setChecked(SpritesShown)
        self.btns['showspriteimgs'].setChecked(SpriteImagesShown)
        self.btns['showlocs'].setChecked(LocationsShown)
        self.btns['showcoms'].setChecked(CommentsShown)
        self.btns['realview'].setChecked(RealViewEnabled)

        return # Everything after this is old

##        TGroup = RibbonGroup(trans.string('Ribbon', 13)) # Tilesets
##        tab.L0Btn = TGroup.addButton(mainWindow.HandleUpdateLayer0, 'Ctrl+1', trans.string('MenuItems', 49), True, 'layer0', trans.string('MenuItems', 48), True, True)
##        tab.L1Btn = TGroup.addButton(mainWindow.HandleUpdateLayer1, 'Ctrl+2', trans.string('MenuItems', 51), True, 'layer1', trans.string('MenuItems', 50), True, True)
##        tab.L2Btn = TGroup.addButton(mainWindow.HandleUpdateLayer2, 'Ctrl+3', trans.string('MenuItems', 53), True, 'layer2', trans.string('MenuItems', 52), True, True)
##        tab.TileAnimBtn = TGroup.addButton(mainWindow.HandleTilesetAnimToggle, 'Ctrl+7', trans.string('MenuItems', 109) , True, 'animation', trans.string('MenuItems', 108), True, False)
##
##        iGroup = RibbonGroup(trans.string('Ribbon', 15)) # Visibility
##        tab.ShowSpritesBtn = iGroup.addButton(mainWindow.HandleSpritesVisibility, 'Ctrl+4', trans.string('MenuItems', 55), False, 'sprites', trans.string('MenuItems', 54), True, SpritesShown)
##        tab.ShowSpriteImgsBtn = iGroup.addButton(mainWindow.HandleSpriteImages, 'Ctrl+6', trans.string('MenuItems', 57), False, 'sprites', trans.string('MenuItems', 56), True, not SpriteImagesShown)
##        tab.ShowLocsBtn = iGroup.addButton(mainWindow.HandleLocationsVisibility, 'Ctrl+5', trans.string('MenuItems', 59), True, 'locations', trans.string('MenuItems', 58), True, not LocationsShown)
##        iGroup.addButton(mainWindow.HandleSwitchGrid, 'Ctrl+G', trans.string('MenuItems', 61), True, 'grid', trans.string('MenuItems', 60))
##
##        zGroup = RibbonGroup(trans.string('Ribbon', 16)) # Zoom
##        tab.zoomInBtn =     zGroup.addButton(mainWindow.HandleZoomIn, QtGui.QKeySequence.ZoomIn, trans.string('MenuItems', 65), False, 'zoomin', trans.string('MenuItems', 64))
##        tab.zoomMaxBtn =    zGroup.addButton(mainWindow.HandleZoomMax, 'Ctrl+PgDown', trans.string('MenuItems', 63), False, 'zoommax', trans.string('MenuItems', 62))
##        tab.zoomActualBtn = zGroup.addButton(mainWindow.HandleZoomActual, 'Ctrl+0', trans.string('MenuItems', 67), True, 'zoomactual', trans.string('MenuItems', 66))
##        tab.zoomOutBtn =    zGroup.addButton(mainWindow.HandleZoomOut, QtGui.QKeySequence.ZoomOut, trans.string('MenuItems', 69), False, 'zoomout', trans.string('MenuItems', 68))
##        tab.zoomMinBtn =    zGroup.addButton(mainWindow.HandleZoomMin, 'Ctrl+PgUp', trans.string('MenuItems', 71), False, 'zoommin', trans.string('MenuItems', 70))
##
##        tab.addGroup(TGroup)
##        tab.addGroup(iGroup)
##        tab.addGroup(zGroup)
##        # tab.finish() is called later, after adding palette and overview buttons
##
##        return tab


    def addOverview(self, dock, act):
        """
        Adds the Show/Hide Overview action to the ribbon
        """
        return
        self.oDock = dock
        self.dockGroup = RibbonGroup(trans.string('Ribbon', 17))
        self.overBtn = self.dockGroup.addButton(self.HandleOverviewClick, act.shortcut(), trans.string('MenuItems', 95), True, 'overview', trans.string('MenuItems', 94), True, True)

    def addPalette(self, dock, act):
        """
        Adds the Show/Hide Palette action to the ribbon
        """
        return
        self.pDock = dock
        self.palBtn = self.dockGroup.addButton(self.HandlePaletteClick, act.shortcut(), trans.string('MenuItems', 97), True, 'palette', trans.string('MenuItems', 96), True, True)

    def addIslandGen(self, dock, act):
        """
        Adds the Show/Hide Island Generator action to the ribbon
        """
        return
        self.iDock = dock
        self.genBtn = self.dockGroup.addButton(self.HandleIslandGenClick, act.shortcut(), trans.string('MenuItems', 101), True, 'islandgen', trans.string('MenuItems', 100), True, True)
        self.viewTab.addGroup(self.dockGroup)
        self.viewTab.finish()

    @QtCore.pyqtSlot(bool)
    def HandleOverviewClick(self, checked = None):
        """
        Updates the overview btn
        """
        return
        visible = checked if checked is not None else not self.oDock.isVisible()
        self.oDock.setVisible(visible)
        if checked is None: self.overBtn.setChecked(visible)

    @QtCore.pyqtSlot(bool)
    def HandlePaletteClick(self, checked = None):
        """
        Updates the palette btn
        """
        return
        visible = checked if checked is not None else not self.pDock.isVisible()
        self.pDock.setVisible(visible)
        if checked is None: self.palBtn.setChecked(visible)

    @QtCore.pyqtSlot(bool)
    def HandleIslandGenClick(self, checked = None):
        """
        Updates the island generator btn
        """
        return
        visible = checked if checked is not None else not self.iDock.isVisible()
        self.iDock.setVisible(visible)
        if checked is None: self.genBtn.setChecked(visible)

    def updateAreaComboBox(self, areas, area):
        """
        Updates the Area Combo Box
        """
        return
        self.homeTab.areaComboBox.clear()
        for i in range(1, len(Level.areas) + 1):
            self.homeTab.areaComboBox.addItem(trans.string('AreaCombobox', 0, '[num]', i))
        self.homeTab.areaComboBox.setCurrentIndex(area-1)

    def setBtnEnabled(self, btn, enabled):
        """
        Enables or disables a button
        """
        try: self.btns[btn].setEnabled(enabled)
        except Exception: print('Ribbon enabling error: ' + btn + ', ' + str(enabled))


class ReggieRibbonFileMenu(QFileMenu):
    """
    Widget that represents the file menu for the ribbon
    """
    def __init__(self):
        """
        Creates and initializes the menu
        """
        QFileMenu.__init__(self)
        self.setRecentFilesText('Recent levels')
        self.btns = {}

        # Add a recent files manager
        self.recentFilesMgr = QRecentFilesManager(setting('RecentFiles'))
        self.setRecentFilesManager(self.recentFilesMgr)
        self.recentFileClicked.connect(self.handleRecentFileClicked)

        # Get ready to add buttons
        gi, ts, mw, qk = GetIcon, trans.string, mainWindow, QtGui.QKeySequence

        # Create right-side panels
        openPanel = QFileMenuPanel('Open an existing level')
        a = openPanel.addButton(gi('open',         True), ts('MenuItems', 2),  mw.HandleOpenFromName, qk.Open,        ts('MenuItems', 3))
        b = openPanel.addButton(gi('openfromfile', True), ts('MenuItems', 4),  mw.HandleOpenFromFile, 'Ctrl+Shift+O', ts('MenuItems', 5))
        self.btns['openname2'], self.btns['openfile'] = a, b

        # Add left-side buttons
        a = self.addButton(                gi('new', True),    ts('MenuItems', 0),   mw.HandleNewLevel,     qk.New,             ts('MenuItems', 1))
        b = self.addArrowButton(openPanel, gi('open', True),   ts('MenuItems', 112), mw.HandleOpenFromName, None,               ts('MenuItems', 3))
        c = self.addButton(                gi('save', True),   ts('MenuItems', 8),   mw.HandleSave,         qk.Save,            ts('MenuItems', 9))
        d = self.addButton(                gi('saveas', True), ts('MenuItems', 10),  mw.HandleSaveAs,       qk.SaveAs,          ts('MenuItems', 11))
        self.btns['new'], self.btns['openname1'], self.btns['save'], self.btns['saveas'] = a, b, c, d
        self.addSeparator()
        a = self.addButton(gi('info', True),     trans.string('MenuItems', 12), mw.HandleInfo,        'Ctrl+Alt+I', trans.string('MenuItems', 13))
        b = self.addButton(gi('settings', True), trans.string('MenuItems', 18), mw.HandlePreferences, 'Ctrl+Alt+P', trans.string('MenuItems', 19))
        self.addSeparator()
        c = self.addButton(gi('delete', True), trans.string('MenuItems', 20), mw.HandleExit, qk.Quit, trans.string('MenuItems', 21))
        self.btns['lvlinfo'], self.btns['prefs'], self.btns['exit'] = a, b, c

##        # create a left-column layout
##        leftLayout = QtWidgets.QVBoxLayout()
##        leftLayout.addWidget(a)
##        leftLayout.addWidget(b)
##        leftLayout.addWidget(c)
##        leftLayout.addWidget(d)
##        leftLayout.addWidget(e)
##
##        # create the Info Preview Widget
##        self.InfoWidget = InfoPreviewWidget(Qt.Vertical)
##        L = QtWidgets.QVBoxLayout()
##        L.addWidget(self.InfoWidget)
##        InfoBox = QtWidgets.QGroupBox(trans.string('InfoDlg', 0)) # 'Level Information'
##        InfoBox.setLayout(L)
##
##        # create the Recent Files group
##        recentGroup = QtWidgets.QGroupBox(trans.string('MenuItems', 6)) # 'Recent Files'
##        RL = QtWidgets.QVBoxLayout()
##        RL.addWidget(mainWindow.RecentMenu)
##        RL.addStretch(1)
##        recentGroup.setLayout(RL)
##
##        # create a bottom buttons layout
##        prefsButton = QtWidgets.QPushButton(GetIcon('settings'), trans.string('MenuItems', 18)) # Reggie! Preferences
##        prefsButton.clicked.connect(mainWindow.HandlePreferences)
##        prefsButton.setToolTip(trans.string('MenuItems', 19))
##        s = QtGui.QShortcut(QtGui.QKeySequence('Ctrl+Alt+P'), mainWindow)
##        s.activated.connect(mainWindow.HandlePreferences)
##        self.setButtonColor(prefsButton)
##        exitButton = QtWidgets.QPushButton(GetIcon('delete'), trans.string('MenuItems', 20)) # Exit Reggie!
##        exitButton.clicked.connect(mainWindow.HandleExit)
##        exitButton.setToolTip(trans.string('MenuItems', 21))
##        s = QtGui.QShortcut(QtGui.QKeySequence.Quit, mainWindow)
##        s.activated.connect(mainWindow.HandleExit)
##        self.setButtonColor(exitButton)
##        bottomButtonsLayout = QtWidgets.QHBoxLayout()
##        bottomButtonsLayout.addStretch(1)
##        bottomButtonsLayout.addWidget(prefsButton)
##        bottomButtonsLayout.addWidget(exitButton)
##
##        # create a top layout
##        self.topLayout = QtWidgets.QGridLayout()
##        self.topLayout.addLayout(leftLayout, 0, 0)
##        self.topLayout.addWidget(InfoBox, 1, 0)
##        self.topLayout.addWidget(recentGroup, 0, 1, 3, 1)
##        self.topLayout.addLayout(bottomButtonsLayout,  3, 0, 1, 2)
##        self.topLayout.setRowStretch(2, 1)
##
##        # create a bottom (watermark) layout
##        bottomLayout = QtWidgets.QGridLayout()
##        v = self.getWatermark()
##        if v is not None:
##            w = QtWidgets.QLabel()
##            w.setPixmap(v)
##            bottomLayout.addWidget(w, 0, 0, 1, 1, Qt.AlignBottom | Qt.AlignRight)
##
##        # create a main layout
##        self.mainLayout = QtWidgets.QGridLayout()
##        self.mainLayout.addLayout(bottomLayout, 0, 0)
##        self.mainLayout.addLayout(self.topLayout, 0, 0)
##        self.setLayout(self.mainLayout)

    def handleRecentFileClicked(self, path):
        """
        Handles recent files being clicked
        """
        mainWindow.LoadLevel(None, str(path), True, 1)



class InfoPreviewWidget(QtWidgets.QWidget):
    """
    Widget that shows a preview of the level metadata info - available in vertical & horizontal flavors
    """
    def __init__(self, direction):
        """
        Creates and initializes the widget
        """
        QtWidgets.QWidget.__init__(self)
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
        if ('Area' not in globals()) or not hasattr(Area, 'filename'): # can't get level metadata if there's no level
            self.Label1.setText('')
            if self.direction == Qt.Horizontal: self.Label2.setText('')
            return

        a = [ # MUST be a list, not a tuple
            mainWindow.fileTitle,
            Area.Title,
            trans.string('InfoDlg', 8, '[name]', Area.Creator),
            trans.string('InfoDlg', 5) + ' ' + Area.Author,
            trans.string('InfoDlg', 6) + ' ' + Area.Group,
            trans.string('InfoDlg', 7) + ' ' + Area.Webpage,
            ]

        for b, section in enumerate(a): # cut off excessively long strings
            if self.direction == Qt.Vertical: short = clipStr(section, 128)
            else: short = clipStr(section, 184)
            if short is not None: a[b] = short + '...'

        if self.direction == Qt.Vertical:
            str1 = a[0]+'<br>'+a[1]+'<br>'+a[2]+'<br>'+a[3]+'<br>'+a[4]+'<br>'+a[5]
            self.Label1.setText(str1)
        else:
            str1 = a[0]+'<br>'+a[1]+'<br>'+a[2]
            str2 = a[3]+'<br>'+a[4]+'<br>'+a[5]
            self.Label1.setText(str1)
            self.Label2.setText(str2)

        self.update()


class GameDefViewer(QtWidgets.QWidget):
    """
    Widget which displays basic info about the current game definition
    """
    def __init__(self):
        """
        Initializes the widget
        """
        QtWidgets.QWidget.__init__(self)
        self.imgLabel = QtWidgets.QLabel()
        self.imgLabel.setToolTip(trans.string('Gamedefs', 0))
        self.imgLabel.setPixmap(GetIcon('sprites', False).pixmap(16, 16))
        self.versionLabel = QtWidgets.QLabel()
        self.titleLabel = QtWidgets.QLabel()
        self.descLabel = QtWidgets.QLabel()
        self.descLabel.setWordWrap(True)
        self.descLabel.setMinimumHeight(40)

        # Make layouts
        left = QtWidgets.QVBoxLayout()
        left.addWidget(self.imgLabel)
        left.addWidget(self.versionLabel)
        left.addStretch(1)
        right = QtWidgets.QVBoxLayout()
        right.addWidget(self.titleLabel)
        right.addWidget(self.descLabel)
        right.addStretch(1)
        main = QtWidgets.QHBoxLayout()
        main.addLayout(left)
        main.addWidget(createVertLine())
        main.addLayout(right)
        main.setStretch(2, 1)
        self.setLayout(main)
        self.setMaximumWidth(256 + 64)

        self.updateLabels()

    def updateLabels(self):
        """
        Updates all labels
        """
        empty = QtGui.QPixmap(16, 16)
        empty.fill(QtGui.QColor(0,0,0,0))
        img = GetIcon('sprites', False).pixmap(16, 16) if ((gamedef.recursiveFiles('sprites', False, True) != []) or (not gamedef.custom)) else empty
        ver = '' if gamedef.version is None else '<i><p style="font-size:10px;">v' + str(gamedef.version) + '</p></i>'
        title = '<b>' + str(gamedef.name) + '</b>'
        desc = str(gamedef.description)

        self.imgLabel.setPixmap(img)
        self.versionLabel.setText(ver)
        self.titleLabel.setText(title)
        self.descLabel.setText(desc)


class GameDefSelector(QtWidgets.QWidget):
    """
    Widget which lets you pick a new game definition
    """
    gameChanged = QtCore.pyqtSignal()
    def __init__(self):
        """
        Initializes the widget
        """
        QtWidgets.QWidget.__init__(self)

        # Populate a list of gamedefs
        self.GameDefs = getAvailableGameDefs()

        # Add them to the main layout
        self.group = QtWidgets.QButtonGroup()
        self.group.setExclusive(True)
        L = QtWidgets.QGridLayout()
        row = 0
        col = 0
        current = setting('LastGameDef')
        id = 0
        for folder in self.GameDefs:
            def_ = ReggieGameDefinition(folder)
            btn = QtWidgets.QRadioButton()
            if folder == current: btn.setChecked(True)
            btn.toggled.connect(self.HandleRadioButtonClick)
            self.group.addButton(btn, id)
            btn.setToolTip(def_.description)
            id += 1
            L.addWidget(btn, row, col)

            name = QtWidgets.QLabel(def_.name)
            name.setToolTip(def_.description)
            L.addWidget(name, row, col + 1)

            row += 1
            if row > 2:
                row = 0
                col += 2

        self.setLayout(L)


    def HandleRadioButtonClick(self, checked):
        """
        Handles radio button clicks
        """
        if not checked: return # this is called twice; one button is checked, another is unchecked

        loadNewGameDef(self.GameDefs[self.group.checkedId()])
        self.gameChanged.emit()


class GameDefMenu(QtWidgets.QMenu):
    """
    A menu which lets the user pick gamedefs
    """
    gameChanged = QtCore.pyqtSignal()
    def __init__(self):
        """
        Creates and initializes the menu
        """
        QtWidgets.QMenu.__init__(self)

        # Add the gamedef viewer widget
        self.currentView = GameDefViewer()
        self.currentView.setMinimumHeight(100)
        self.gameChanged.connect(self.currentView.updateLabels)

        v = QtWidgets.QWidgetAction(self)
        v.setDefaultWidget(self.currentView)
        self.addAction(v)
        self.addSeparator()

        # Add entries for each gamedef
        self.GameDefs = getAvailableGameDefs()

        self.actGroup = QtWidgets.QActionGroup(self)
        loadedDef = setting('LastGameDef')
        for folder in self.GameDefs:
            def_ = ReggieGameDefinition(folder)
            act = QtWidgets.QAction(self)
            act.setText(def_.name)
            act.setToolTip(def_.description)
            act.setData(folder)
            act.setActionGroup(self.actGroup)
            act.setCheckable(True)
            if folder == loadedDef:
                act.setChecked(True)
                first = False
            act.toggled.connect(self.handleGameDefClicked)
            self.addAction(act)

    def handleGameDefClicked(self, checked):
        """
        Handles the user clicking a gamedef
        """
        if not checked: return

        name = self.actGroup.checkedAction().data()
        loadNewGameDef(name)
        self.gameChanged.emit()



def getAvailableGameDefs():
    GameDefs = []

    # Add them
    folders = os.listdir('reggiedata/games')
    for folder in folders:
        if not os.path.isdir('reggiedata/games/' + folder): continue
        inFolder = os.listdir('reggiedata/games/' + folder)
        if 'main.xml' not in inFolder: continue
        def_ = ReggieGameDefinition(folder)
        if def_.custom: GameDefs.append((def_, folder))

    # Alphabetize them, and then add the default
    GameDefs = sorted(GameDefs, key=lambda def_: def_[0].name)
    new = [None]
    for item in GameDefs: new.append(item[1])
    return new

def loadNewGameDef(def_):
    """
    Loads ReggieGameDefinition def_, and displays a progress dialog
    """
    dlg = QtWidgets.QProgressDialog()
    dlg.setAutoClose(True)
    btn = QtWidgets.QPushButton('Cancel')
    btn.setEnabled(False)
    dlg.setCancelButton(btn)
    dlg.show()
    dlg.setValue(0)

    LoadGameDef(def_, dlg)

    dlg.setValue(100)
    del dlg



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


class RecentFilesMenu(QtWidgets.QMenu):
    """
    A menu which displays recently opened files
    """
    def __init__(self):
        """
        Creates and initializes the menu
        """
        QtWidgets.QMenu.__init__(self)
        self.setMinimumWidth(192)

        # Here's how this works:
        # - Upon startup, RecentFiles is obtained from QSettings and put into self.FileList
        # - All modifications to the menu thereafter are then applied to self.FileList
        # - The actions displayed in the menu are determined by whatever's in self.FileList
        # - Whenever self.FileList is changed, self.writeSettings is called which writes
        #      it all back to the QSettings

        # Populate FileList upon startup
        if settings.contains('RecentFiles'):
            self.FileList = str(setting('RecentFiles')).split('|')
        else:
            self.FileList = ['']

        # This fixes bugs
        self.FileList = [path for path in self.FileList if path.lower() not in ('', 'none', 'false', 'true')]

        self.updateActionList()


    def writeSettings(self):
        """
        Writes FileList back to the Registry
        """
        setSetting('RecentFiles', str('|'.join(self.FileList)))

    def updateActionList(self):
        """
        Updates the actions visible in the menu
        """

        self.clear() # removes any actions already in the menu
        ico = GetIcon('new')
        currentShortcut = 0

        for i, filename in enumerate(self.FileList):
            filename = filename.split('\\')[-1]
            short = clipStr(filename, 72)
            if short is not None: filename = short + '...'

            act = QtWidgets.QAction(ico, filename, self)
            if i <=9: act.setShortcut(QtGui.QKeySequence('Ctrl+Alt+'+str(i)))
            act.setToolTip(str(self.FileList[i]))

            # This is a TERRIBLE way to do this, but I can't think of anything simpler. :(
            if i == 0:  handler = self.HandleOpenRecentFile0
            if i == 1:  handler = self.HandleOpenRecentFile1
            if i == 2:  handler = self.HandleOpenRecentFile2
            if i == 3:  handler = self.HandleOpenRecentFile3
            if i == 4:  handler = self.HandleOpenRecentFile4
            if i == 5:  handler = self.HandleOpenRecentFile5
            if i == 6:  handler = self.HandleOpenRecentFile6
            if i == 7:  handler = self.HandleOpenRecentFile7
            if i == 8:  handler = self.HandleOpenRecentFile8
            if i == 9:  handler = self.HandleOpenRecentFile9
            if i == 10: handler = self.HandleOpenRecentFile10
            if i == 11: handler = self.HandleOpenRecentFile11
            if i == 12: handler = self.HandleOpenRecentFile12
            if i == 13: handler = self.HandleOpenRecentFile13
            if i == 14: handler = self.HandleOpenRecentFile14
            act.triggered.connect(handler)

            self.addAction(act)

    def AddToList(self, path):
        """
        Adds an entry to the list
        """
        MaxLength = 16

        if path in ('None', 'True', 'False', None, True, False): return # fixes bugs
        path = str(path).replace('/', '\\')

        new = [path]
        for filename in self.FileList:
            if filename != path:
                new.append(filename)
        if len(new) > MaxLength: new = new[0:MaxLength]

        self.FileList = new
        self.writeSettings()
        self.updateActionList()

    def RemoveFromList(self, index):
        """
        Removes an entry from the list
        """
        del self.FileList[index]
        self.writeSettings()
        self.updateActionList()

    def clearAll(self):
        """
        Clears all recent files from the list and the registry
        """
        self.FileList = []
        self.writeSettings()
        self.updateActionList()

    def HandleOpenRecentFile0(self):
        self.HandleOpenRecentFile(0)
    def HandleOpenRecentFile1(self):
        self.HandleOpenRecentFile(1)
    def HandleOpenRecentFile2(self):
        self.HandleOpenRecentFile(2)
    def HandleOpenRecentFile3(self):
        self.HandleOpenRecentFile(3)
    def HandleOpenRecentFile4(self):
        self.HandleOpenRecentFile(4)
    def HandleOpenRecentFile5(self):
        self.HandleOpenRecentFile(5)
    def HandleOpenRecentFile6(self):
        self.HandleOpenRecentFile(6)
    def HandleOpenRecentFile7(self):
        self.HandleOpenRecentFile(7)
    def HandleOpenRecentFile8(self):
        self.HandleOpenRecentFile(8)
    def HandleOpenRecentFile9(self):
        self.HandleOpenRecentFile(9)
    def HandleOpenRecentFile10(self):
        self.HandleOpenRecentFile(10)
    def HandleOpenRecentFile11(self):
        self.HandleOpenRecentFile(11)
    def HandleOpenRecentFile12(self):
        self.HandleOpenRecentFile(12)
    def HandleOpenRecentFile13(self):
        self.HandleOpenRecentFile(13)
    def HandleOpenRecentFile14(self):
        self.HandleOpenRecentFile(14)
    def HandleOpenRecentFile(self, number):
        """
        Open a recently opened level picked from the main menu
        """
        if mainWindow.CheckDirty(): return

        if not mainWindow.LoadLevel(None, self.FileList[number], True, 1): self.RemoveFromList(number)


class ZoomWidget(QtWidgets.QWidget):
    """
    Widget that allows easy zoom level control
    """
    def __init__(self):
        """
        Creates and initializes the widget
        """
        QtWidgets.QWidget.__init__(self)
        maxwidth = 512-128
        maxheight = 20

        self.slider = QtWidgets.QSlider(Qt.Horizontal)
        self.minLabel = QtWidgets.QPushButton()
        self.minusLabel = QtWidgets.QPushButton()
        self.plusLabel = QtWidgets.QPushButton()
        self.maxLabel = QtWidgets.QPushButton()

        self.slider.setMaximumHeight(maxheight)
        self.slider.setMinimum(0)
        self.slider.setMaximum(len(mainWindow.ZoomLevels)-1)
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
        self.minLabel.clicked.connect(mainWindow.HandleZoomMin)
        self.minusLabel.clicked.connect(mainWindow.HandleZoomOut)
        self.plusLabel.clicked.connect(mainWindow.HandleZoomIn)
        self.maxLabel.clicked.connect(mainWindow.HandleZoomMax)

        self.layout = QtWidgets.QGridLayout()
        self.layout.addWidget(self.minLabel,   0, 0)
        self.layout.addWidget(self.minusLabel, 0, 1)
        self.layout.addWidget(self.slider,     0, 2)
        self.layout.addWidget(self.plusLabel,  0, 3)
        self.layout.addWidget(self.maxLabel,   0, 4)
        self.layout.setVerticalSpacing(0)
        self.layout.setHorizontalSpacing(0)
        self.layout.setContentsMargins(0,0,4,0)

        self.setLayout(self.layout)
        self.setMinimumWidth(maxwidth)
        self.setMaximumWidth(maxwidth)
        self.setMaximumHeight(maxheight)

    def sliderMoved(self):
        """
        Handle the slider being moved
        """
        mainWindow.ZoomTo(mainWindow.ZoomLevels[self.slider.value()])

    def setZoomLevel(self, newLevel):
        """
        Moves the slider to the zoom level given
        """
        self.slider.setSliderPosition(self.findIndexOfLevel(newLevel))

    def findIndexOfLevel(self, level):
        for i, mainlevel in enumerate(mainWindow.ZoomLevels):
            if float(mainlevel) == float(level): return i


class ZoomStatusWidget(QtWidgets.QWidget):
    """
    Shows the current zoom level, in percent
    """
    def __init__(self):
        """
        Creates and initializes the widget
        """
        QtWidgets.QWidget.__init__(self)
        self.label = QtWidgets.QPushButton('100%')
        self.label.setFlat(True)
        self.label.clicked.connect(mainWindow.HandleZoomActual)

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.setContentsMargins(4,0,8,0)
        self.setMaximumWidth(56)

        self.setLayout(self.layout)

    def setZoomLevel(self, zoomLevel):
        """
        Updates the widget
        """
        if float(int(zoomLevel)) == float(zoomLevel):
            self.label.setText(str(int(zoomLevel))+'%')
        else:
            self.label.setText(str(float(zoomLevel))+'%')



def LoadActionsLists():
    # Define the menu items, their default settings and their mainWindow.actions keys
    # These are used both in the Preferences Dialog and when init'ing the toolbar.
    global FileActions
    global EditActions
    global ViewActions
    global SettingsActions
    global HelpActions

    FileActions = (
        (trans.string('MenuItems', 0),  True,  'newlevel'),
        (trans.string('MenuItems', 2),  True,  'openfromname'),
        (trans.string('MenuItems', 4),  False, 'openfromfile'),
        (trans.string('MenuItems', 6),  False, 'openrecent'),
        (trans.string('MenuItems', 8),  True,  'save'),
        (trans.string('MenuItems', 10), False, 'saveas'),
        (trans.string('MenuItems', 12), False, 'metainfo'),
        (trans.string('MenuItems', 14), True,  'screenshot'),
        (trans.string('MenuItems', 16), False, 'changegamepath'),
        (trans.string('MenuItems', 18), False, 'preferences'),
        (trans.string('MenuItems', 20), False, 'exit'),
        )
    EditActions = (
        (trans.string('MenuItems', 22), False, 'selectall'),
        (trans.string('MenuItems', 24), False, 'deselect'),
        (trans.string('MenuItems', 26), True,  'cut'),
        (trans.string('MenuItems', 28), True,  'copy'),
        (trans.string('MenuItems', 30), True,  'paste'),
        (trans.string('MenuItems', 32), False, 'shiftitems'),
        (trans.string('MenuItems', 34), False, 'mergelocations'),
        (trans.string('MenuItems', 36), False, 'diagnostic'),
        (trans.string('MenuItems', 38), False, 'freezeobjects'),
        (trans.string('MenuItems', 40), False, 'freezesprites'),
        (trans.string('MenuItems', 42), False, 'freezeentrances'),
        (trans.string('MenuItems', 44), False, 'freezelocations'),
        (trans.string('MenuItems', 46), False, 'freezepaths'),
        (trans.string('MenuItems', 124), False, 'freezeprogresspaths'),
        )
    ViewActions = (
        (trans.string('MenuItems', 48), True,  'showlay0'),
        (trans.string('MenuItems', 50), True,  'showlay1'),
        (trans.string('MenuItems', 52), True,  'showlay2'),
        (trans.string('MenuItems', 54), True,  'showsprites'),
        (trans.string('MenuItems', 56), False, 'showspriteimages'),
        (trans.string('MenuItems', 58), True,  'showlocations'),
        (trans.string('MenuItems', 60), True,  'grid'),
        (trans.string('MenuItems', 62), True,  'zoommax'),
        (trans.string('MenuItems', 64), True,  'zoomin'),
        (trans.string('MenuItems', 66), True,  'zoomactual'),
        (trans.string('MenuItems', 68), True,  'zoomout'),
        (trans.string('MenuItems', 70), True,  'zoommin'),
        )
    SettingsActions = (
        (trans.string('MenuItems', 72), True, 'areaoptions'),
        (trans.string('MenuItems', 74), True, 'zones'),
        (trans.string('MenuItems', 76), True, 'backgrounds'),
        (trans.string('MenuItems', 78), False, 'addarea'),
        (trans.string('MenuItems', 80), False, 'importarea'),
        (trans.string('MenuItems', 82), False, 'deletearea'),
        (trans.string('MenuItems', 84), False, 'reloadgfx'),
        )
    HelpActions = (
        (trans.string('MenuItems', 86), False, 'infobox'),
        (trans.string('MenuItems', 88), False, 'helpbox'),
        (trans.string('MenuItems', 90), False, 'tipbox'),
        (trans.string('MenuItems', 92), False, 'aboutqt'),
        )


class PreferencesDialog(QtWidgets.QDialog):
    """
    Dialog which lets you customize Reggie
    """
    def __init__(self):
        """
        Creates and initializes the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('PrefsDlg', 0))
        self.setWindowIcon(GetIcon('settings'))

        # Create the tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.currentChanged.connect(self.tabChanged)

        # Create other widgets
        self.infoLabel = QtWidgets.QLabel()
        self.generalTab = self.getGeneralTab()
        self.toolbarTab = self.getToolbarTab()
        self.themesTab = self.getThemesTab()
        self.tabWidget.addTab(self.generalTab, trans.string('PrefsDlg', 1))
        self.tabWidget.addTab(self.toolbarTab, trans.string('PrefsDlg', 2))
        self.tabWidget.addTab(self.themesTab, trans.string('PrefsDlg', 3))

        # Create the buttonbox
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        # Create a main layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.infoLabel)
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        # Update it
        self.tabChanged()
        self.menuSettingChanged()

    def tabChanged(self):
        """
        Handles the current tab being changed
        """
        self.infoLabel.setText(self.tabWidget.currentWidget().info)

    def menuSettingChanged(self):
        """
        Handles the menu-style option being changed
        """
        self.tabWidget.setTabEnabled(1, self.generalTab.MenuM.isChecked())


    def getGeneralTab(self):
        """
        Returns the General Tab
        """

        class GeneralTab(QtWidgets.QWidget):
            """
            General Tab
            """
            info = trans.string('PrefsDlg', 4)

            def __init__(self, menuHandler):
                """
                Initializes the General Tab
                """
                QtWidgets.QWidget.__init__(self)

                # Add the Splash Screen settings
                self.SplashR = QtWidgets.QRadioButton(trans.string('PrefsDlg', 8))
                self.SplashA = QtWidgets.QRadioButton(trans.string('PrefsDlg', 9))
                self.SplashN = QtWidgets.QRadioButton(trans.string('PrefsDlg', 10))
                self.SplashG = QtWidgets.QButtonGroup() # huge glitches if it's not assigned to self.something
                self.SplashG.setExclusive(True)
                self.SplashG.addButton(self.SplashR)
                self.SplashG.addButton(self.SplashA)
                self.SplashG.addButton(self.SplashN)
                SplashL = QtWidgets.QVBoxLayout()
                SplashL.addWidget(self.SplashR)
                SplashL.addWidget(self.SplashA)
                SplashL.addWidget(self.SplashN)

                # Add the Menu Format settings
                self.MenuR = QtWidgets.QRadioButton(trans.string('PrefsDlg', 12))
                self.MenuM = QtWidgets.QRadioButton(trans.string('PrefsDlg', 13))
                self.MenuG = QtWidgets.QButtonGroup() # huge glitches if it's not assigned to self.something
                self.MenuG.setExclusive(True)
                self.MenuG.addButton(self.MenuR)
                self.MenuG.addButton(self.MenuM)
                MenuL = QtWidgets.QVBoxLayout()
                MenuL.addWidget(self.MenuR)
                MenuL.addWidget(self.MenuM)
                self.MenuG.buttonClicked.connect(menuHandler)

                # Add the Tileset Selection settings
                self.TileD = QtWidgets.QRadioButton(trans.string('PrefsDlg', 28))
                self.TileO = QtWidgets.QRadioButton(trans.string('PrefsDlg', 29))
                self.TileG = QtWidgets.QButtonGroup() # huge glitches if it's not assigned to self.something
                self.TileG.setExclusive(True)
                self.TileG.addButton(self.TileD)
                self.TileG.addButton(self.TileO)
                TileL = QtWidgets.QVBoxLayout()
                TileL.addWidget(self.TileD)
                TileL.addWidget(self.TileO)

                # Add the Translation Language setting
                self.Trans = QtWidgets.QComboBox()
                self.Trans.setMaximumWidth(256)

                # Add the Clear Recent Files button
                ClearRecentBtn = QtWidgets.QPushButton(trans.string('PrefsDlg', 16))
                ClearRecentBtn.setMaximumWidth(ClearRecentBtn.minimumSizeHint().width())
                ClearRecentBtn.clicked.connect(self.ClearRecent)

                # Create the main layout
                L = QtWidgets.QFormLayout()
                L.addRow(trans.string('PrefsDlg', 7), SplashL)
                L.addRow(trans.string('PrefsDlg', 11), MenuL)
                L.addRow(trans.string('PrefsDlg', 27), TileL)
                L.addRow(trans.string('PrefsDlg', 14), self.Trans)
                L.addRow(trans.string('PrefsDlg', 15), ClearRecentBtn)
                self.setLayout(L)

                # Set the buttons
                self.Reset()


            def Reset(self):
                """
                Read the preferences and check the respective boxes
                """
                if str(setting('ShowSplash')): self.SplashA.setChecked(True)
                elif str(setting('ShowSplash')): self.SplashN.setChecked(True)
                else: self.SplashR.setChecked(True)

                if str(setting('Menu')) == 'Ribbon': self.MenuR.setChecked(True)
                else: self.MenuM.setChecked(True)

                if str(setting('TilesetTab')) != 'Old': self.TileD.setChecked(True)
                else: self.TileO.setChecked(True)

                self.Trans.addItem('English')
                self.Trans.setItemData(0, None, Qt.UserRole)
                self.Trans.setCurrentIndex(0)
                i = 1
                for trans in os.listdir('reggiedata/translations'):
                    if trans.lower() == 'english': continue

                    fp = 'reggiedata/translations/' + trans + '/main.xml'
                    if not os.path.isfile(fp): continue

                    transobj = ReggieTranslation(trans)
                    name = transobj.name
                    self.Trans.addItem(name)
                    self.Trans.setItemData(i, trans, Qt.UserRole)
                    if trans == str(setting('Translation')):
                        self.Trans.setCurrentIndex(i)
                    i += 1

            def ClearRecent(self):
                """
                Handle the Clear Recent Files button being clicked
                """
                ans = QtWidgets.QMessageBox.question(None, trans.string('PrefsDlg', 17), trans.string('PrefsDlg', 18), QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                if ans != QtWidgets.QMessageBox.Yes: return
                self.RecentMenu.clearAll()


        return GeneralTab(self.menuSettingChanged)


    def getToolbarTab(self):
        """
        Returns the Toolbar Tab
        """

        class ToolbarTab(QtWidgets.QWidget):
            """
            Toolbar Tab
            """
            info = trans.string('PrefsDlg', 5)

            def __init__(self):
                """
                Initializes the Toolbar Tab
                """
                global FileActions
                global EditActions
                global ViewActions
                global SettingsActions
                global HelpActions

                QtWidgets.QWidget.__init__(self)

                # Determine which keys are activated
                if setting('ToolbarActs') in (None, 'None', 'none', '', 0):
                    # Get the default settings
                    toggled = {}
                    for List in (FileActions, EditActions, ViewActions, SettingsActions, HelpActions):
                        for name, activated, key in List:
                            toggled[key] = activated
                else: # Get the registry settings
                    toggled = setting('ToolbarActs')
                    newToggled = {} # here, I'm replacing QStrings w/ python strings
                    for key in toggled:
                        newToggled[str(key)] = toggled[key]
                    toggled = newToggled

                # Create some data
                self.FileBoxes = []
                self.EditBoxes = []
                self.ViewBoxes = []
                self.SettingsBoxes = []
                self.HelpBoxes = []
                FL = QtWidgets.QVBoxLayout()
                EL = QtWidgets.QVBoxLayout()
                VL = QtWidgets.QVBoxLayout()
                SL = QtWidgets.QVBoxLayout()
                HL = QtWidgets.QVBoxLayout()
                FB = QtWidgets.QGroupBox(trans.string('Menubar', 0))
                EB = QtWidgets.QGroupBox(trans.string('Menubar', 1))
                VB = QtWidgets.QGroupBox(trans.string('Menubar', 2))
                SB = QtWidgets.QGroupBox(trans.string('Menubar', 3))
                HB = QtWidgets.QGroupBox(trans.string('Menubar', 4))

                # Arrange this data so it can be iterated over
                menuItems = (
                    (FileActions, self.FileBoxes, FL, FB),
                    (EditActions, self.EditBoxes, EL, EB),
                    (ViewActions, self.ViewBoxes, VL, VB),
                    (SettingsActions, self.SettingsBoxes, SL, SB),
                    (HelpActions, self.HelpBoxes, HL, HB),
                )

                # Set up the menus by iterating over the above data
                for defaults, boxes, layout, group in menuItems:
                    for L, C, I in defaults:
                        box = QtWidgets.QCheckBox(L)
                        boxes.append(box)
                        layout.addWidget(box)
                        try: box.setChecked(toggled[I])
                        except KeyError: pass
                        box.InternalName = I # to save settings later
                    group.setLayout(layout)


                # Create the always-enabled Current Area checkbox
                CurrentArea = QtWidgets.QCheckBox(trans.string('PrefsDlg', 19))
                CurrentArea.setChecked(True)
                CurrentArea.setEnabled(False)

                # Create the Reset button
                reset = QtWidgets.QPushButton(trans.string('PrefsDlg', 20))
                reset.clicked.connect(self.reset)

                # Create the main layout
                L = QtWidgets.QGridLayout()
                L.addWidget(reset,       0, 0, 1, 1)
                L.addWidget(FB,          1, 0, 3, 1)
                L.addWidget(EB,          1, 1, 3, 1)
                L.addWidget(VB,          1, 2, 3, 1)
                L.addWidget(SB,          1, 3, 1, 1)
                L.addWidget(HB,          2, 3, 1, 1)
                L.addWidget(CurrentArea, 3, 3, 1, 1)
                self.setLayout(L)

            def reset(self):
                """
                This is called when the Reset button is clicked
                """
                items = (
                    (self.FileBoxes, FileActions),
                    (self.EditBoxes, EditActions),
                    (self.ViewBoxes, ViewActions),
                    (self.SettingsBoxes, SettingsActions),
                    (self.HelpBoxes, HelpActions)
                )

                for boxes, defaults in items:
                    for box, default in zip(boxes, defaults):
                        box.setChecked(default[1])

        return ToolbarTab()


    def getThemesTab(self):
        """
        Returns the Themes Tab
        """

        class ThemesTab(QtWidgets.QWidget):
            """
            Themes Tab
            """
            info = trans.string('PrefsDlg', 6)

            def __init__(self):
                """
                Initializes the Themes Tab
                """
                QtWidgets.QWidget.__init__(self)

                # Get the current and available themes
                self.themeID = theme.themeName
                self.themes = self.getAvailableThemes()

                # Create the radiobuttons
                self.btns = []
                self.btnvals = {}
                for name, themeObj in self.themes:
                    displayname = name
                    if displayname.lower().endswith('.rt'): displayname = displayname[:-3]
                    
                    btn = QtWidgets.QRadioButton(displayname)
                    if name == str(setting('Theme')): btn.setChecked(True)
                    btn.clicked.connect(self.UpdatePreview)
                    
                    self.btns.append(btn)
                    self.btnvals[btn] = (name, themeObj)

                # Create the buttons group
                btnG = QtWidgets.QButtonGroup()
                btnG.setExclusive(True)
                for btn in self.btns:
                    btnG.addButton(btn)

                # Create the buttons groupbox
                L = QtWidgets.QGridLayout()
                for idx, button in enumerate(self.btns):
                    L.addWidget(btn, idx%12, int(idx/12))
                btnGB = QtWidgets.QGroupBox(trans.string('PrefsDlg', 21))
                btnGB.setLayout(L)

                # Create the preview labels and groupbox
                self.preview = QtWidgets.QLabel()
                self.description = QtWidgets.QLabel()
                L = QtWidgets.QVBoxLayout()
                L.addWidget(self.preview)
                L.addWidget(self.description)
                L.addStretch(1)
                previewGB = QtWidgets.QGroupBox(trans.string('PrefsDlg', 22))
                previewGB.setLayout(L)

                # Create the options box options
                keys = QtWidgets.QStyleFactory().keys()
                self.NonWinStyle = QtWidgets.QComboBox()
                self.NonWinStyle.setToolTip(trans.string('PrefsDlg', 24))
                self.NonWinStyle.addItems(keys)
                uistyle = setting('uiStyle')
                if uistyle is not None:
                    self.NonWinStyle.setCurrentIndex(keys.index(setting('uiStyle')))

                # Create the options groupbox
                L = QtWidgets.QVBoxLayout()
                L.addWidget(self.NonWinStyle)
                optionsGB = QtWidgets.QGroupBox(trans.string('PrefsDlg', 25))
                optionsGB.setLayout(L)

                # Create a main layout
                L = QtWidgets.QGridLayout()
                L.addWidget(btnGB, 0, 0, 2, 1)
                L.addWidget(optionsGB, 0, 1)
                L.addWidget(previewGB, 1, 1)
                L.setRowStretch(1, 1)
                self.setLayout(L)

                # Update the preview things
                self.UpdatePreview()


            def getAvailableThemes(self):
                """Searches the Themes folder and returns a list of theme filepaths.
                Automatically adds 'Classic' to the list."""
                themes = os.listdir('reggiedata/themes')
                themeList = [('Classic', ReggieTheme())]
                for themeName in themes:
                    try:
                        if themeName.split('.')[-1].lower() == 'rt':
                            data = open('reggiedata/themes/' + themeName, 'rb').read()
                            theme = ReggieTheme(data)
                            themeList.append((themeName, theme))
                    except Exception: pass

                return tuple(themeList)

            def UpdatePreview(self):
                """
                Updates the preview
                """
                for btn in self.btns:
                    if btn.isChecked():
                        t = self.btnvals[btn][1]
                        self.preview.setPixmap(self.drawPreview(t))
                        text = trans.string('PrefsDlg', 26, '[name]', t.themeName, '[creator]', t.creator, '[description]', t.description)
                        self.description.setText(text)

            def drawPreview(self, theme):
                """
                Returns a preview pixmap for the given theme
                """

                # Set up some things
                px = QtGui.QPixmap(350, 185)
                px.fill(theme.color('bg'))
                return px
                

                paint = QtGui.QPainter(px)

                UIColor = theme.color('ui')
                if UIColor is None: UIColor = toQColor(240,240,240) # close enough

                ice = QtGui.QPixmap('reggiedata/sprites/ice_flow_7.png')

                global NumberFont
                font = QtGui.QFont(NumberFont) # need to make a new instance to avoid changing global settings
                font.setPointSize(6)
                paint.setFont(font)

                # Draw the spriteboxes
                paint.setPen(QtGui.QPen(theme.color('spritebox_lines'), 1))
                paint.setBrush(QtGui.QBrush(theme.color('spritebox_fill')))

                paint.drawRoundedRect(176, 64, 16, 16, 5, 5)
                paint.drawText(QtCore.QPointF(180, 75), '38')

                paint.drawRoundedRect(16, 96, 16, 16, 5, 5)
                paint.drawText(QtCore.QPointF(20, 107), '53')

                # Draw the entrance
                paint.setPen(QtGui.QPen(theme.color('entrance_lines'), 1))
                paint.setBrush(QtGui.QBrush(theme.color('entrance_fill')))

                paint.drawRoundedRect(208, 128, 16, 16, 5, 5)
                paint.drawText(QtCore.QPointF(212, 138), '0')

                # Draw the location
                paint.setPen(QtGui.QPen(theme.color('location_lines'), 1))
                paint.setBrush(QtGui.QBrush(theme.color('location_fill')))

                paint.drawRect(16, 144, 96, 32)
                paint.setPen(QtGui.QPen(theme.color('location_text'), 1))
                paint.drawText(QtCore.QPointF(20, 154), '1')

                # Draw the iceblock (can't easily draw a tileset obj)
                paint.drawPixmap(160, 144, ice.scaled(ice.width()*2/3, ice.height()*2/3))

                # Draw the zone
                paint.setPen(QtGui.QPen(theme.color('zone_lines'), 3))
                paint.setBrush(QtGui.QBrush(toQColor(0,0,0,0)))
                paint.drawRect(136, 52, 256, 120)
                paint.setPen(QtGui.QPen(theme.color('zone_corner'), 3))
                paint.setBrush(QtGui.QBrush(theme.color('zone_corner'), 3))
                paint.drawRect(135, 51, 2, 2)
                paint.drawRect(135, 171, 2, 2)
                paint.setPen(QtGui.QPen(theme.color('zone_text'), 1))
                font = QtGui.QFont(NumberFont)
                font.setPointSize(5)
                paint.setFont(font)
                paint.drawText(QtCore.QPointF(140, 62), 'Zone 1')

                # Draw the grid
                paint.setPen(QtGui.QPen(theme.color('grid'), 1, Qt.DotLine))
                gridcoords = []
                i=0
                while i < 350:
                    gridcoords.append(i)
                    i=i+16
                for i in gridcoords:
                    paint.setPen(QtGui.QPen(theme.color('grid'), 0.75, Qt.DotLine))
                    paint.drawLine(i, 0, i, 185)
                    paint.drawLine(0, i, 350, i)
                    if (i/16)%4 == 0:
                        paint.setPen(QtGui.QPen(theme.color('grid'), 1.5, Qt.DotLine))
                        paint.drawLine(i, 0, i, 185)
                        paint.drawLine(0, i, 350, i)
                    if (i/16)%8 == 0:
                        paint.setPen(QtGui.QPen(theme.color('grid'), 2.25, Qt.DotLine))
                        paint.drawLine(i, 0, i, 185)
                        paint.drawLine(0, i, 350, i)

                # Draw the UI
                paint.setBrush(QtGui.QBrush(UIColor))
                paint.setPen(toQColor(0,0,0,0))
                paint.drawRect(0, 0, 350, 24)
                paint.drawRect(300, 24, 50, 165)

                # Delete the painter and return the pixmap
                del paint
                return px


        return ThemesTab()


class UpdateDialog(QtWidgets.QDialog):
    """
    Dialog to display any available updates
    """
    def __init__(self):
        """
        Init the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle(trans.string('Updates', 0))
        self.setWindowIcon(GetIcon('download'))
        self.setMinimumWidth(256)

        # Create widgets
        self.msgLabel = QtWidgets.QLabel()
        self.dldBtn = QtWidgets.QPushButton(trans.string('Updates', 4))
        self.dldBtn.clicked.connect(self.handleDldBtn)
        self.dldBtn.hide()
        self.progLabel = QtWidgets.QLabel()

        # Create the buttonbox
        buttonBox = QtWidgets.QDialogButtonBox()
        buttonBox.addButton(QtWidgets.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        self.PerformCheck()

        # Create a main layout
        L = QtWidgets.QVBoxLayout()
        L.addWidget(self.msgLabel)
        L.addWidget(self.dldBtn)
        L.addWidget(self.progLabel)
        L.addWidget(buttonBox)
        self.setLayout(L)

    def PerformCheck(self):
        """
        Performs the update check
        """
        # Attempt to download data
        errors = False
        try: data = self.getTxt()
        except Exception: errors = True

        if not errors:
            try: releaseType = open('release.txt', 'r').read()
            except Exception: releaseType = 'unknown'
            releaseType = releaseType.replace('\n', '').replace('\r', '')

            available = ReggieVersion in data and len(data[ReggieVersion].values()) > 0

        # All right; now handle the results
        if errors:
            # Errors occurred
            self.UpdateUi('error')
        elif available:
            # Update is available
            name = list(data[ReggieVersion].keys())[0]
            infourl = data[ReggieVersion][name]['InfoUrl']
            url = data[ReggieVersion][name][releaseType]['url']
            self.UpdateUi(True, name, infourl, url)
        else:
            # No update is available
            self.UpdateUi(False)

    def getTxt(self):
        """
        Returns the parsed data in the online text file
        """
        rawdata = urllib.request.urlopen(UpdateURL)
        rawdata = rawdata.read(20000).decode('latin-1')

        tree = etree.ElementTree(etree.fromstring(rawdata))
        root = tree.getroot()

        rootData = {}
        for versionNode in root:
            if versionNode.tag.lower() != 'version': continue
            versionData = {}

            for updateNode in versionNode:
                if updateNode.tag.lower() != 'update': continue
                updateData = {}

                for releaseNode in updateNode:
                    if releaseNode.tag.lower() != 'release': continue
                    releaseData = {}
                    releaseData['url'] = releaseNode.attrib['url']

                    updateData[releaseNode.attrib['id']] = releaseData

                versionData[updateNode.attrib['name']] = updateData
                updateData['InfoUrl'] = updateNode.attrib['url']

            rootData[versionNode.attrib['id']] = versionData

        return rootData


    def UpdateUi(self, available, name='', infourl='', url=''):
        """
        Updates the UI based on updateinfo
        """
        if available == 'error':
            # Error while checking for update
            self.msgLabel.setText(trans.string('Updates', 1))
        elif not available:
            # No updates
            self.msgLabel.setText(trans.string('Updates', 2))
        else:
            # Updates!
            self.msgLabel.setText(trans.string('Updates', 3, '[name]', name, '[info]', infourl))

            self.dldBtn.show()
            self.dldBtn.url = url # hacky method


    def handleDldBtn(self):
        """
        Handles the user clicking the Download Now button
        """
        self.dldBtn.hide()
        self.progLabel.show()
        self.progLabel.setText(trans.string('Updates', 5))

        downloader = self.downloader(self.dldBtn.url)
        downloader.done.connect(self.handleDldDone)

        thread = threading.Thread(None, downloader.run)
        thread.start()

    def handleDldDone(self):
        """
        The download finished
        """
        self.progLabel.setText(trans.string('Updates', 6))

    class downloader(QtCore.QObject):
        """
        An object that downloads the update. Contains signals.
        """
        done = QtCore.pyqtSignal()
        def __init__(self, url):
            """
            Initializes it
            """
            QtCore.QObject.__init__(self)
            self.url = url
        def run(self):
            """
            Runs the download
            """
            local_filename, headers = urllib.request.urlretrieve(self.url)

            if local_filename.startswith('\\'):
                local_filename = local_filename[1:]
            dest = os.path.dirname(sys.argv[0])

            zipfile.ZipFile(local_filename).extractall(dest)

            time.sleep(8)

            self.done.emit()



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



####################################################################
####################################################################
####################################################################



class ReggieWindow(QtWidgets.QMainWindow):
    """
    Reggie main level editor window
    """

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
        global Initializing
        Initializing = True

        # Reggie Version number goes below here. 64 char max (32 if non-ascii).
        self.ReggieInfo = ReggieID

        self.ZoomLevels = [7.5, 10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0, 60.0, 65.0, 70.0, 75.0, 85.0, 90.0, 95.0, 100.0, 125.0, 150.0, 175.0, 200.0, 250.0, 300.0, 350.0, 400.0]

        self.AutosaveTimer = QtCore.QTimer()
        self.AutosaveTimer.timeout.connect(self.Autosave)
        self.AutosaveTimer.start(20000)

        # required variables
        self.UpdateFlag = False
        self.SelectionUpdateFlag = False
        self.selObj = None
        self.CurrentSelection = []

        self.CurrentGame = setting('CurrentGame')
        if self.CurrentGame is None: self.CurrentGame = NewSuperMarioBros2

        # set up the window
        QtWidgets.QMainWindow.__init__(self, None)
        self.setWindowTitle('Reggie! Level Editor Next')
        self.setWindowIcon(QtGui.QIcon('reggiedata/icon.png'))
        self.setIconSize(QtCore.QSize(16, 16))

        # create the level view
        self.scene = LevelScene(0, 0, 1024*24, 512*24, self)
        self.scene.setItemIndexMethod(QtWidgets.QGraphicsScene.NoIndex)
        self.scene.selectionChanged.connect(self.ChangeSelectionHandler)

        self.view = LevelViewWidget(self.scene, self)
        self.view.centerOn(0,0) # this scrolls to the top left
        self.view.PositionHover.connect(self.PositionHovered)
        self.view.XScrollBar.valueChanged.connect(self.XScrollChange)
        self.view.YScrollBar.valueChanged.connect(self.YScrollChange)
        self.view.FrameSize.connect(self.HandleWindowSizeChange)

        # make a 'ribbon' placeholder
        self.ribbon = None

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
        Finishes initialization. (fixes bugs with some widgets calling mainWindow.something before it's fully init'ed)
        """
        # set up actions and menus
        self.SetupActionsAndMenus()

        # set up the status bar
        self.posLabel = QtWidgets.QLabel()
        self.selectionLabel = QtWidgets.QLabel()
        self.hoverLabel = QtWidgets.QLabel()
        self.statusBar().addWidget(self.posLabel)
        self.statusBar().addWidget(self.selectionLabel)
        self.statusBar().addWidget(self.hoverLabel)
        self.ZoomWidget = ZoomWidget()
        self.ZoomStatusWidget = ZoomStatusWidget()
        self.statusBar().addPermanentWidget(self.ZoomWidget)
        self.statusBar().addPermanentWidget(self.ZoomStatusWidget)

        # create the various panels
        self.SetupDocksAndPanels()

        # now get stuff ready
        loaded = False
        curgame = self.CurrentGame

        if not AutoOpenScriptEnabled:
            if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]) and IsNSMBLevel(sys.argv[1]):
                loaded = self.LoadLevel(curgame, sys.argv[1], True, 1)
            elif settings.contains('LastLevel'):
                lastlevel = str(gamedef.GetLastLevel())
                loaded = self.LoadLevel(curgame, lastlevel, True, 1)

            if not loaded:
                self.LoadLevel(curgame, FirstLevels[curgame], False, 1)
        else:
            # Auto-level-opening script for rapid testing and analysis
            pass

            # To search for sprites, put this in the __init__ function of SpriteItem:
            # for byte in range(8):
            #     nyb1 = data[byte] >> 4
            #     nyb2 = data[byte] & 0xF
            #     if nyb1 not in SpriteDatas[type][byte * 2]:
            #         SpriteDatas[type][byte * 2][nyb1] = []
            #     if CurrentLevelNameForAutoOpenScript not in SpriteDatas[type][byte * 2][nyb1]:
            #         SpriteDatas[type][byte * 2][nyb1].append(CurrentLevelNameForAutoOpenScript)
            #     if nyb2 not in SpriteDatas[type][byte * 2 + 1]:
            #         SpriteDatas[type][byte * 2 + 1][nyb2] = []
            #     if CurrentLevelNameForAutoOpenScript not in SpriteDatas[type][byte * 2 + 1][nyb2]:
            #         SpriteDatas[type][byte * 2 + 1][nyb2].append(CurrentLevelNameForAutoOpenScript)
            # SpriteDatas[type][16].append(CurrentLevelNameForAutoOpenScript)
            # ... and this before the auto-opening loop:
            # global SpriteDatas
            # SpriteDatas = []
            # for i in range(326):
            #     newlist = []
            #     for nyb in range(16):
            #         newlist.append({})
            #     newlist.append([]) # list of all levels in which it's used
            #     SpriteDatas.append(newlist)
            # ... and this after the auto-opening loop:
            # prints = ''
            # for sprnum in range(326):
            #     data = SpriteDatas[sprnum]
            #     printedFirstThing = False
            #     if not data[9]:
            #         prints += 'Sprite %d is unused.\n' % sprnum
            #     else:
            #         prints += 'Sprite %d:\n' % sprnum
            #         prints += '    Used in ' + ', '.join(sorted(set(data[16]))) + '\n'
            #         for byte in range(8):
            #             nyb1 = data[byte * 2]
            #             nyb2 = data[byte * 2 + 1]
            #             if len(nyb1) > 1 or (len(nyb1) == 1 and 0 not in nyb1):
            #                 prints += '    Nybble %d:\n' % (byte * 2 + 1)
            #                 for nybval, usedin in sorted(nyb1.items(), key=lambda thing: thing[0]):
            #                     if usedin:
            #                         prints += '        Value %s used in ' % hex(nybval)[2:]
            #                         prints += ', '.join(sorted(usedin))
            #                         prints += '\n'
            #             if len(nyb2) > 1 or (len(nyb2) == 1 and 0 not in nyb2):
            #                 prints += '    Nybble %d:\n' % (byte * 2 + 2)
            #                 for nybval, usedin in sorted(nyb2.items(), key=lambda thing: thing[0]):
            #                     if usedin:
            #                         prints += '        Value %s used in ' % hex(nybval)[2:]
            #                         prints += ', '.join(sorted(usedin))
            #                         prints += '\n'
            # print(prints)

            # To search for Pa0 objects, put this in the __init__ method for ObjectItem:
            # unknownvalues = (0, 1, 2, 3, 4, 6, 7, 10, 12, 19, 24, 25, 28, 31, 36, 38)
            # if tileset == 0 and type in unknownvalues:
            #     print('Unknown thing in %s: Type %d (at (%d, %d))' % (CurrentLevelNameForAutoOpenScript, type, x, y))

            # Leave this here
            global CurrentLevelNameForAutoOpenScript
            for levelname in os.listdir(setting('GamePath_NSMB2')):
                if not levelname.endswith(FileExtentions[curgame]): continue
                print('Loading %s...' % levelname)
                for areanum in range(4):
                    try:
                        CurrentLevelNameForAutoOpenScript = levelname[:-5] + ' A' + str(areanum + 1)
                        self.LoadLevel(curgame, os.path.join(setting('GamePath_NSMB2'), levelname), True, areanum + 1)
                    except: pass


        QtCore.QTimer.singleShot(100, self.levelOverview.update)

        toggleHandlers = {
            self.HandleSpritesVisibility: SpritesShown,
            self.HandleSpriteImages: SpriteImagesShown,
            self.HandleLocationsVisibility: LocationsShown,
            self.HandleCommentsVisibility: CommentsShown,
            }
        for handler in toggleHandlers:
            handler(toggleHandlers[handler]) # call each toggle-button handler to set each feature correctly upon startup

        # let's restore the state and geometry
        # geometry: determines the main window position
        # state: determines positions of docks
        if settings.contains('MainWindowGeometry'):
            self.restoreGeometry(setting('MainWindowGeometry'))
        if settings.contains('MainWindowState'):
            self.restoreState(setting('MainWindowState'), 0)

        # Load the most recently used gamedef
        LoadGameDef(setting('LastGameDef'), False)

        # Aaaaaand... initializing is done!
        Initializing = False


    def SetupActionsAndMenus(self):
        """
        Sets up Reggie's actions, menus and toolbars
        """
        self.RecentMenu = RecentFilesMenu()
        self.GameDefMenu = GameDefMenu()

        self.ribbon = None
        if UseRibbon:
            self.createRibbon()
        else:
            self.createMenubar()

    def createRibbon(self):
        """
        Create a ribbon rather than a menubar/toolbar
        """
        self.ribbon = ReggieRibbon()
        self.setMenuWidget(self.ribbon)
        self.RecentFilesMgr = self.ribbon.fileMenu.recentFilesMgr
        self.RecentFilesMgr.pathAdded.connect(self.handleRecentFilesPathAdded)

    actions = {}
    def createMenubar(self):
        """
        Create actions, a menubar and a toolbar
        """

        # File
        self.CreateAction('newlevel', self.HandleNewLevel, GetIcon('new'), trans.string('MenuItems', 0), trans.string('MenuItems', 1), QtGui.QKeySequence.New)
        self.CreateAction('openfromname', self.HandleOpenFromName, GetIcon('open'), trans.string('MenuItems', 2), trans.string('MenuItems', 3), QtGui.QKeySequence.Open)
        self.CreateAction('openfromfile', self.HandleOpenFromFile, GetIcon('openfromfile'), trans.string('MenuItems', 4), trans.string('MenuItems', 5), QtGui.QKeySequence('Ctrl+Shift+O'))
        self.CreateAction('openrecent', None, GetIcon('recent'), trans.string('MenuItems', 6), trans.string('MenuItems', 7), None)
        self.CreateAction('save', self.HandleSave, GetIcon('save'), trans.string('MenuItems', 8), trans.string('MenuItems', 9), QtGui.QKeySequence.Save)
        self.CreateAction('saveas', self.HandleSaveAs, GetIcon('saveas'), trans.string('MenuItems', 10), trans.string('MenuItems', 11), QtGui.QKeySequence.SaveAs)
        self.CreateAction('metainfo', self.HandleInfo, GetIcon('info'), trans.string('MenuItems', 12), trans.string('MenuItems', 13), QtGui.QKeySequence('Ctrl+Alt+I'))
        self.CreateAction('changegamedef', None, GetIcon('game'), trans.string('MenuItems', 98), trans.string('MenuItems', 99), None)
        self.CreateAction('screenshot', self.HandleScreenshot, GetIcon('screenshot'), trans.string('MenuItems', 14), trans.string('MenuItems', 15), QtGui.QKeySequence('Ctrl+Alt+S'))
        self.CreateAction('changegamepath', self.HandleChangeGamePath, GetIcon('folderpath'), trans.string('MenuItems', 16), trans.string('MenuItems', 17), QtGui.QKeySequence('Ctrl+Alt+G'))
        self.CreateAction('preferences', self.HandlePreferences, GetIcon('settings'), trans.string('MenuItems', 18), trans.string('MenuItems', 19), QtGui.QKeySequence('Ctrl+Alt+P'))
        self.CreateAction('exit', self.HandleExit, GetIcon('delete'), trans.string('MenuItems', 20), trans.string('MenuItems', 21), QtGui.QKeySequence('Ctrl+Q'))

        # Edit
        self.CreateAction('selectall', self.SelectAll, GetIcon('select'), trans.string('MenuItems', 22), trans.string('MenuItems', 23), QtGui.QKeySequence.SelectAll)
        self.CreateAction('deselect', self.Deselect, GetIcon('deselect'), trans.string('MenuItems', 24), trans.string('MenuItems', 25), QtGui.QKeySequence('Ctrl+D'))
        self.CreateAction('cut', self.Cut, GetIcon('cut'), trans.string('MenuItems', 26), trans.string('MenuItems', 27), QtGui.QKeySequence.Cut)
        self.CreateAction('copy', self.Copy, GetIcon('copy'), trans.string('MenuItems', 28), trans.string('MenuItems', 29), QtGui.QKeySequence.Copy)
        self.CreateAction('paste', self.Paste, GetIcon('paste'), trans.string('MenuItems', 30), trans.string('MenuItems', 31), QtGui.QKeySequence.Paste)
        self.CreateAction('shiftitems', self.ShiftItems, GetIcon('move'), trans.string('MenuItems', 32), trans.string('MenuItems', 33), QtGui.QKeySequence('Ctrl+Shift+S'))
        self.CreateAction('mergelocations', self.MergeLocations, GetIcon('merge'), trans.string('MenuItems', 34), trans.string('MenuItems', 35), QtGui.QKeySequence('Ctrl+Shift+E'))
        self.CreateAction('swapobjectstilesets', self.SwapObjectsTilesets, GetIcon('swap'), trans.string('MenuItems', 104), trans.string('MenuItems', 105), QtGui.QKeySequence('Ctrl+Shift+L'))
        self.CreateAction('swapobjectstypes', self.SwapObjectsTypes, GetIcon('swap'), trans.string('MenuItems', 106), trans.string('MenuItems', 107), QtGui.QKeySequence('Ctrl+Shift+Y'))
        self.CreateAction('diagnostic', self.HandleDiagnostics, GetIcon('diagnostics'), trans.string('MenuItems', 36), trans.string('MenuItems', 37), QtGui.QKeySequence('Ctrl+Shift+D'))
        self.CreateAction('freezeobjects', self.HandleObjectsFreeze, GetIcon('objectsfreeze'), trans.string('MenuItems', 38), trans.string('MenuItems', 39), QtGui.QKeySequence('Ctrl+Shift+1'), True)
        self.CreateAction('freezesprites', self.HandleSpritesFreeze, GetIcon('spritesfreeze'), trans.string('MenuItems', 40), trans.string('MenuItems', 41), QtGui.QKeySequence('Ctrl+Shift+2'), True)
        self.CreateAction('freezeentrances', self.HandleEntrancesFreeze, GetIcon('entrancesfreeze'), trans.string('MenuItems', 42), trans.string('MenuItems', 43), QtGui.QKeySequence('Ctrl+Shift+3'), True)
        self.CreateAction('freezelocations', self.HandleLocationsFreeze, GetIcon('locationsfreeze'), trans.string('MenuItems', 44), trans.string('MenuItems', 45), QtGui.QKeySequence('Ctrl+Shift+4'), True)
        self.CreateAction('freezepaths', self.HandlePathsFreeze, GetIcon('pathsfreeze'), trans.string('MenuItems', 46), trans.string('MenuItems', 47), QtGui.QKeySequence('Ctrl+Shift+5'), True)
        self.CreateAction('freezeprogresspaths', self.HandleProgressPathsFreeze, GetIcon('progresspathsfreeze'), trans.string('MenuItems', 124), trans.string('MenuItems', 125), QtGui.QKeySequence('Ctrl+Shift+6'), True)
        self.CreateAction('freezecomments', self.HandleCommentsFreeze, GetIcon('commentsfreeze'), trans.string('MenuItems', 114), trans.string('MenuItems', 115), QtGui.QKeySequence('Ctrl+Shift+9'), True)

        # View
        self.CreateAction('showlay0', self.HandleUpdateLayer0, GetIcon('layer0'), trans.string('MenuItems', 48), trans.string('MenuItems', 49), QtGui.QKeySequence('Ctrl+1'), True)
        self.CreateAction('showlay1', self.HandleUpdateLayer1, GetIcon('layer1'), trans.string('MenuItems', 50), trans.string('MenuItems', 51), QtGui.QKeySequence('Ctrl+2'), True)
        self.CreateAction('showlay2', self.HandleUpdateLayer2, GetIcon('layer2'), trans.string('MenuItems', 52), trans.string('MenuItems', 53), QtGui.QKeySequence('Ctrl+3'), True)
        self.CreateAction('tileanim', self.HandleTilesetAnimToggle, GetIcon('animation'), trans.string('MenuItems', 108), trans.string('MenuItems', 109), QtGui.QKeySequence('Ctrl+7'), True)
        self.CreateAction('collisions', self.HandleCollisionsToggle, GetIcon('collisions'), trans.string('MenuItems', 110), trans.string('MenuItems', 111), QtGui.QKeySequence('Ctrl+8'), True)
        self.CreateAction('depth', self.HandleDepthToggle, GetIcon('depth'), trans.string('MenuItems', 122), trans.string('MenuItems', 123), QtGui.QKeySequence('Ctrl+H'), True)
        self.CreateAction('realview', self.HandleRealViewToggle, GetIcon('realview'), trans.string('MenuItems', 118), trans.string('MenuItems', 119), QtGui.QKeySequence('Ctrl+9'), True)
        self.CreateAction('showsprites', self.HandleSpritesVisibility, GetIcon('sprites'), trans.string('MenuItems', 54), trans.string('MenuItems', 55), QtGui.QKeySequence('Ctrl+4'), True)
        self.CreateAction('showspriteimages', self.HandleSpriteImages, GetIcon('sprites'), trans.string('MenuItems', 56), trans.string('MenuItems', 57), QtGui.QKeySequence('Ctrl+6'), True)
        self.CreateAction('showlocations', self.HandleLocationsVisibility, GetIcon('locations'), trans.string('MenuItems', 58), trans.string('MenuItems', 59), QtGui.QKeySequence('Ctrl+5'), True)
        self.CreateAction('showcomments', self.HandleCommentsVisibility, GetIcon('comments'), trans.string('MenuItems', 116), trans.string('MenuItems', 117), QtGui.QKeySequence('Ctrl+0'), True)
        self.CreateAction('grid', self.HandleSwitchGrid, GetIcon('grid'), trans.string('MenuItems', 60), trans.string('MenuItems', 61), QtGui.QKeySequence('Ctrl+G'), False)
        self.CreateAction('zoommax', self.HandleZoomMax, GetIcon('zoommax'), trans.string('MenuItems', 62), trans.string('MenuItems', 63), QtGui.QKeySequence('Ctrl+PgDown'), False)
        self.CreateAction('zoomin', self.HandleZoomIn, GetIcon('zoomin'), trans.string('MenuItems', 64), trans.string('MenuItems', 65), QtGui.QKeySequence.ZoomIn, False)
        self.CreateAction('zoomactual', self.HandleZoomActual, GetIcon('zoomactual'), trans.string('MenuItems', 66), trans.string('MenuItems', 67), QtGui.QKeySequence('Ctrl+0'), False)
        self.CreateAction('zoomout', self.HandleZoomOut, GetIcon('zoomout'), trans.string('MenuItems', 68), trans.string('MenuItems', 69), QtGui.QKeySequence.ZoomOut, False)
        self.CreateAction('zoommin', self.HandleZoomMin, GetIcon('zoommin'), trans.string('MenuItems', 70), trans.string('MenuItems', 71), QtGui.QKeySequence('Ctrl+PgUp'), False)
        # Show Overview and Show Palette are added later

        # Settings
        self.CreateAction('areaoptions', self.HandleAreaOptions, GetIcon('area'), trans.string('MenuItems', 72), trans.string('MenuItems', 73), QtGui.QKeySequence('Ctrl+Alt+A'))
        self.CreateAction('zones', self.HandleZones, GetIcon('zones'), trans.string('MenuItems', 74), trans.string('MenuItems', 75), QtGui.QKeySequence('Ctrl+Alt+Z'))
        self.CreateAction('backgrounds', self.HandleBG, GetIcon('background'), trans.string('MenuItems', 76), trans.string('MenuItems', 77), QtGui.QKeySequence('Ctrl+Alt+B'))
        self.CreateAction('addarea', self.HandleAddNewArea, GetIcon('add'), trans.string('MenuItems', 78), trans.string('MenuItems', 79), QtGui.QKeySequence('Ctrl+Alt+N'))
        self.CreateAction('importarea', self.HandleImportArea, GetIcon('import'), trans.string('MenuItems', 80), trans.string('MenuItems', 81), QtGui.QKeySequence('Ctrl+Alt+O'))
        self.CreateAction('deletearea', self.HandleDeleteArea, GetIcon('delete'), trans.string('MenuItems', 82), trans.string('MenuItems', 83), QtGui.QKeySequence('Ctrl+Alt+D'))
        self.CreateAction('reloadgfx', self.ReloadTilesets, GetIcon('reload'), trans.string('MenuItems', 84), trans.string('MenuItems', 85), QtGui.QKeySequence('Ctrl+Shift+R'))

        # Help actions are created later

        # Recent Files Menu
        self.RecentFilesMgr = QRecentFilesManager()


        # Configure them
        self.actions['openrecent'].setMenu(self.RecentMenu)
        self.actions['changegamedef'].setMenu(self.GameDefMenu)

        self.actions['collisions'].setChecked(CollisionsShown)
        self.actions['depth'].setChecked(DepthShown)
        self.actions['realview'].setChecked(RealViewEnabled)

        self.actions['showsprites'].setChecked(SpritesShown)
        self.actions['showspriteimages'].setChecked(SpriteImagesShown)
        self.actions['showlocations'].setChecked(LocationsShown)
        self.actions['showcomments'].setChecked(CommentsShown)

        self.actions['freezeobjects'].setChecked(ObjectsFrozen)
        self.actions['freezesprites'].setChecked(SpritesFrozen)
        self.actions['freezeentrances'].setChecked(EntrancesFrozen)
        self.actions['freezelocations'].setChecked(LocationsFrozen)
        self.actions['freezepaths'].setChecked(PathsFrozen)
        self.actions['freezeprogresspaths'].setChecked(ProgressPathsFrozen)
        self.actions['freezecomments'].setChecked(CommentsFrozen)

        self.actions['cut'].setEnabled(False)
        self.actions['copy'].setEnabled(False)
        self.actions['paste'].setEnabled(False)
        self.actions['shiftitems'].setEnabled(False)
        self.actions['mergelocations'].setEnabled(False)
        self.actions['deselect'].setEnabled(False)
        self.actions['showlay0'].setEnabled(False)


        ####
        menubar = QtWidgets.QMenuBar()
        self.setMenuBar(menubar)


        fmenu = menubar.addMenu(trans.string('Menubar', 0))
        fmenu.addAction(self.actions['newlevel'])
        fmenu.addAction(self.actions['openfromname'])
        fmenu.addAction(self.actions['openfromfile'])
        fmenu.addAction(self.actions['openrecent'])
        fmenu.addSeparator()
        fmenu.addAction(self.actions['save'])
        fmenu.addAction(self.actions['saveas'])
        fmenu.addAction(self.actions['metainfo'])
        fmenu.addSeparator()
        fmenu.addAction(self.actions['changegamedef'])
        fmenu.addAction(self.actions['screenshot'])
        fmenu.addAction(self.actions['changegamepath'])
        fmenu.addAction(self.actions['preferences'])
        fmenu.addSeparator()
        fmenu.addAction(self.actions['exit'])

        emenu = menubar.addMenu(trans.string('Menubar', 1))
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
        emenu.addAction(self.actions['diagnostic'])
        emenu.addSeparator()
        emenu.addAction(self.actions['freezeobjects'])
        emenu.addAction(self.actions['freezesprites'])
        emenu.addAction(self.actions['freezeentrances'])
        emenu.addAction(self.actions['freezelocations'])
        emenu.addAction(self.actions['freezepaths'])
        emenu.addAction(self.actions['freezeprogresspaths'])
        emenu.addAction(self.actions['freezecomments'])

        vmenu = menubar.addMenu(trans.string('Menubar', 2))
        vmenu.addAction(self.actions['showlay0'])
        vmenu.addAction(self.actions['showlay1'])
        vmenu.addAction(self.actions['showlay2'])
        vmenu.addAction(self.actions['tileanim'])
        vmenu.addAction(self.actions['collisions'])
        vmenu.addAction(self.actions['depth'])
        vmenu.addAction(self.actions['realview'])
        vmenu.addSeparator()
        vmenu.addAction(self.actions['showsprites'])
        vmenu.addAction(self.actions['showspriteimages'])
        vmenu.addAction(self.actions['showlocations'])
        vmenu.addAction(self.actions['showcomments'])
        vmenu.addSeparator()
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

        lmenu = menubar.addMenu(trans.string('Menubar', 3))
        lmenu.addAction(self.actions['areaoptions'])
        lmenu.addAction(self.actions['zones'])
        lmenu.addAction(self.actions['backgrounds'])
        lmenu.addSeparator()
        lmenu.addAction(self.actions['addarea'])
        lmenu.addAction(self.actions['importarea'])
        lmenu.addAction(self.actions['deletearea'])
        lmenu.addSeparator()
        lmenu.addAction(self.actions['reloadgfx'])

        hmenu = menubar.addMenu(trans.string('Menubar', 4))
        self.SetupHelpMenu(hmenu)

        # create a toolbar
        self.toolbar = self.addToolBar(trans.string('Menubar', 5))
        self.toolbar.setObjectName('MainToolbar')

        # Add buttons to the toolbar
        self.addToolbarButtons()

        # Add the area combo box
        self.areaComboBox = QtWidgets.QComboBox()
        self.areaComboBox.activated.connect(self.HandleSwitchArea)
        self.toolbar.addWidget(self.areaComboBox)

    def SetupHelpMenu(self, menu=None):
        """
        Creates the help menu. This is separate because both the ribbon and the menubar use this
        """
        self.CreateAction('infobox', self.AboutBox, GetIcon('reggie'), trans.string('MenuItems', 86), trans.string('MenuItems', 87), QtGui.QKeySequence('Ctrl+Shift+I'))
        self.CreateAction('helpbox', self.HelpBox, GetIcon('contents'), trans.string('MenuItems', 88), trans.string('MenuItems', 89), QtGui.QKeySequence('Ctrl+Shift+H'))
        self.CreateAction('tipbox', self.TipBox, GetIcon('tips'), trans.string('MenuItems', 90), trans.string('MenuItems', 91), QtGui.QKeySequence('Ctrl+Shift+T'))
        self.CreateAction('update', self.UpdateCheck, GetIcon('download'), trans.string('MenuItems', 120), trans.string('MenuItems', 121), QtGui.QKeySequence('Ctrl+Shift+U'))
        self.CreateAction('aboutqt', QtWidgets.qApp.aboutQt, GetIcon('qt'), trans.string('MenuItems', 92), trans.string('MenuItems', 93), QtGui.QKeySequence('Ctrl+Shift+Q'))

        if menu is None:
            menu = QtWidgets.QMenu(trans.string('Menubar', 4))
        menu.addAction(self.actions['infobox'])
        menu.addAction(self.actions['helpbox'])
        menu.addAction(self.actions['tipbox'])
        menu.addSeparator()
        menu.addAction(self.actions['update'])
        menu.addSeparator()
        menu.addAction(self.actions['aboutqt'])
        return menu

    def addToolbarButtons(self):
        """
        Reads from the Preferences file and adds the appropriate options to the toolbar
        """
        global FileActions
        global EditActions
        global ViewActions
        global SettingsActions
        global HelpActions

        # First, define groups. Each group is isolated by separators.
        Groups = (
            (
                'newlevel',
                'openfromname',
                'openfromfile',
                'openrecent',
                'save',
                'saveas',
                'metainfo',
                'screenshot',
                'changegamepath',
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
                'freezeprogresspaths',
            ), (
                'diagnostic',
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
                'reloadgfx',
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
            for List in (FileActions, EditActions, ViewActions, SettingsActions, HelpActions):
                for name, activated, key in List:
                    toggled[key] = activated
        else: # Get the registry settings
            toggled = setting('ToolbarActs')
            newToggled = {} # here, I'm replacing QStrings w/ python strings
            for key in toggled:
                newToggled[str(key)] = toggled[key]
            toggled = newToggled

        # Add each to the toolbar if toggled[key]
        for group in Groups:
            addedButtons = False
            for key in group:
                if key in toggled and toggled[key]:
                    act = self.actions[key]
                    self.toolbar.addAction(act)
                    addedButtons = True
            if addedButtons:
                self.toolbar.addSeparator()


    def handleRecentFilesPathAdded(self, path):
        """
        Handles a file being added to self.RecentFilesMgr
        """
        setSetting('RecentFiles', self.RecentFilesMgr.data())


    def SetupDocksAndPanels(self):
        """
        Sets up the dock widgets and panels
        """
        # level overview
        dock = QtWidgets.QDockWidget(trans.string('MenuItems', 94), self)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetClosable)
        #dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('leveloverview') # needed for the state to save/restore correctly

        self.levelOverview = LevelOverviewWidget()
        self.levelOverview.moveIt.connect(self.HandleOverviewClick)
        self.levelOverviewDock = dock
        dock.setWidget(self.levelOverview)

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setVisible(True)
        act = dock.toggleViewAction()
        act.setShortcut(QtGui.QKeySequence('Ctrl+M'))
        act.setIcon(GetIcon('overview'))
        act.setStatusTip(trans.string('MenuItems', 95))
        if UseRibbon: self.ribbon.addOverview(dock, act)
        else: self.vmenu.addAction(act)

        # create the sprite editor panel
        dock = QtWidgets.QDockWidget(trans.string('SpriteDataEditor', 0), self)
        dock.setVisible(False)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('spriteeditor') #needed for the state to save/restore correctly

        self.spriteDataEditor = SpriteEditorWidget()
        self.spriteDataEditor.DataUpdate.connect(self.SpriteDataUpdated)
        dock.setWidget(self.spriteDataEditor)
        self.spriteEditorDock = dock

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setFloating(True)

        # create the entrance editor panel
        dock = QtWidgets.QDockWidget(trans.string('EntranceDataEditor', 24), self)
        dock.setVisible(False)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('entranceeditor') #needed for the state to save/restore correctly

        self.entranceEditor = EntranceEditorWidget()
        dock.setWidget(self.entranceEditor)
        self.entranceEditorDock = dock

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setFloating(True)

        # create the path node editor panel
        dock = QtWidgets.QDockWidget(trans.string('PathDataEditor', 10), self)
        dock.setVisible(False)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('pathnodeeditor') #needed for the state to save/restore correctly

        self.pathEditor = PathNodeEditorWidget()
        dock.setWidget(self.pathEditor)
        self.pathEditorDock = dock

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setFloating(True)

        # create the progress path node editor panel
        dock = QtWidgets.QDockWidget(trans.string('ProgPathDataEditor', 0), self)
        dock.setVisible(False)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('progresspathnodeeditor') #needed for the state to save/restore correctly

        self.progPathEditor = ProgressPathNodeEditorWidget()
        dock.setWidget(self.progPathEditor)
        self.progPathEditorDock = dock

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setFloating(True)

        # create the location editor panel
        dock = QtWidgets.QDockWidget(trans.string('LocationDataEditor', 12), self)
        dock.setVisible(False)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('locationeditor') #needed for the state to save/restore correctly

        self.locationEditor = LocationEditorWidget()
        dock.setWidget(self.locationEditor)
        self.locationEditorDock = dock

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setFloating(True)

        # create the island generator panel
        dock = QtWidgets.QDockWidget(trans.string('MenuItems', 100), self)
        dock.setVisible(False)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetClosable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('islandgenerator') #needed for the state to save/restore correctly

        self.islandGen = IslandGeneratorWidget()
        dock.setWidget(self.islandGen)
        self.islandGenDock = dock

        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        dock.setFloating(True)
        act = dock.toggleViewAction()
        act.setShortcut(QtGui.QKeySequence('Ctrl+I'))
        act.setIcon(GetIcon('islandgen'))
        act.setToolTip(trans.string('MenuItems', 101))
        if UseRibbon: self.ribbon.addIslandGen(dock, act)
        else: self.vmenu.addAction(act)

        # create the palette
        dock = QtWidgets.QDockWidget(trans.string('MenuItems', 96), self)
        dock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetClosable)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setObjectName('palette') #needed for the state to save/restore correctly

        self.creationDock = dock
        act = dock.toggleViewAction()
        act.setShortcut(QtGui.QKeySequence('Ctrl+P'))
        act.setIcon(GetIcon('palette'))
        act.setStatusTip(trans.string('MenuItems', 97))
        if UseRibbon: self.ribbon.addPalette(dock, act)
        else: self.vmenu.addAction(act)

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
        tabs.setTabToolTip(0, trans.string('Palette', 13))

        self.objTS0Tab = QtWidgets.QWidget()
        self.objTS1Tab = QtWidgets.QWidget()
        self.objTS2Tab = QtWidgets.QWidget()
        self.objTS3Tab = QtWidgets.QWidget()
        self.objAllTab.addTab(self.objTS0Tab, tsicon, '1')
        self.objAllTab.addTab(self.objTS1Tab, tsicon, '2')
        self.objAllTab.addTab(self.objTS2Tab, tsicon, '3')
        self.objAllTab.addTab(self.objTS3Tab, tsicon, '4')

        oel = QtWidgets.QVBoxLayout(self.objTS0Tab)
        self.createObjectLayout = oel

        ll = QtWidgets.QHBoxLayout()
        self.objUseLayer0 = QtWidgets.QRadioButton('0')
        self.objUseLayer0.setToolTip(trans.string('Palette', 1))
        self.objUseLayer0.setEnabled(False)
        self.objUseLayer1 = QtWidgets.QRadioButton('1')
        self.objUseLayer1.setToolTip(trans.string('Palette', 2))
        self.objUseLayer2 = QtWidgets.QRadioButton('2')
        self.objUseLayer2.setToolTip(trans.string('Palette', 3))
        ll.addWidget(QtWidgets.QLabel(trans.string('Palette', 0)))
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

        self.objPicker = ObjectPickerWidget()
        self.objPicker.ObjChanged.connect(self.ObjectChoiceChanged)
        self.objPicker.ObjReplace.connect(self.ObjectReplace)
        oel.addWidget(self.objPicker, 1)

        # sprite tab
        self.sprAllTab = QtWidgets.QTabWidget()
        self.sprAllTab.currentChanged.connect(self.SprTabChanged)
        tabs.addTab(self.sprAllTab, GetIcon('sprites'), '')
        tabs.setTabToolTip(1, trans.string('Palette', 14))

        # sprite tab: add
        self.sprPickerTab = QtWidgets.QWidget()
        self.sprAllTab.addTab(self.sprPickerTab, GetIcon('spritesadd'), trans.string('Palette', 25))

        spl = QtWidgets.QVBoxLayout(self.sprPickerTab)
        self.sprPickerLayout = spl

        svpl = QtWidgets.QHBoxLayout()
        svpl.addWidget(QtWidgets.QLabel(trans.string('Palette', 4)))

        sspl = QtWidgets.QHBoxLayout()
        sspl.addWidget(QtWidgets.QLabel(trans.string('Palette', 5)))

        LoadSpriteCategories()
        viewpicker = QtWidgets.QComboBox()
        for view in SpriteCategories:
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
        self.sprPicker.SwitchView(SpriteCategories[0])
        spl.addWidget(self.sprPicker, 1)

        self.defaultPropButton = QtWidgets.QPushButton(trans.string('Palette', 6))
        self.defaultPropButton.setEnabled(False)
        self.defaultPropButton.clicked.connect(self.ShowDefaultProps)

        sdpl = QtWidgets.QHBoxLayout()
        sdpl.addStretch(1)
        sdpl.addWidget(self.defaultPropButton)
        sdpl.addStretch(1)
        spl.addLayout(sdpl)

        # default sprite data editor
        ddock = QtWidgets.QDockWidget(trans.string('Palette', 7), self)
        ddock.setFeatures(QtWidgets.QDockWidget.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetClosable)
        ddock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        ddock.setObjectName('defaultprops') #needed for the state to save/restore correctly

        self.defaultDataEditor = SpriteEditorWidget(True)
        self.defaultDataEditor.setVisible(False)
        ddock.setWidget(self.defaultDataEditor)

        self.addDockWidget(Qt.RightDockWidgetArea, ddock)
        ddock.setVisible(False)
        ddock.setFloating(True)
        self.defaultPropDock = ddock

        # sprite tab: current
        self.sprEditorTab = QtWidgets.QWidget()
        self.sprAllTab.addTab(self.sprEditorTab, GetIcon('spritelist'), trans.string('Palette', 26))

        spel = QtWidgets.QVBoxLayout(self.sprEditorTab)
        self.sprEditorLayout = spel

        slabel = QtWidgets.QLabel(trans.string('Palette', 11))
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
        tabs.setTabToolTip(2, trans.string('Palette', 15))

        eel = QtWidgets.QVBoxLayout(self.entEditorTab)
        self.entEditorLayout = eel

        elabel = QtWidgets.QLabel(trans.string('Palette', 8))
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
        tabs.setTabToolTip(3, trans.string('Palette', 16))

        locL = QtWidgets.QVBoxLayout(self.locEditorTab)
        self.locEditorLayout = locL

        Llabel = QtWidgets.QLabel(trans.string('Palette', 12))
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
        tabs.setTabToolTip(4, trans.string('Palette', 17))

        pathel = QtWidgets.QVBoxLayout(self.pathEditorTab)
        self.pathEditorLayout = pathel

        pathlabel = QtWidgets.QLabel(trans.string('Palette', 9))
        pathlabel.setWordWrap(True)
        deselectbtn = QtWidgets.QPushButton(trans.string('Palette', 10))
        deselectbtn.clicked.connect(self.DeselectPathSelection)
        self.pathList = ListWidgetWithToolTipSignal()
        self.pathList.itemActivated.connect(self.HandlePathSelectByList)
        self.pathList.toolTipAboutToShow.connect(self.HandlePathToolTipAboutToShow)
        self.pathList.setSortingEnabled(True)

        pathel.addWidget(pathlabel)
        pathel.addWidget(deselectbtn)
        pathel.addWidget(self.pathList)

        # progress paths tab
        self.progPathEditorTab = QtWidgets.QWidget()
        tabs.addTab(self.progPathEditorTab, GetIcon('progresspaths'), '')
        tabs.setTabToolTip(5, trans.string('Palette', 36))

        progpathel = QtWidgets.QVBoxLayout(self.progPathEditorTab)
        self.progPathEditorLayout = progpathel

        progpathlabel = QtWidgets.QLabel(trans.string('Palette', 37))
        progpathlabel.setWordWrap(True)
        deselectbtn = QtWidgets.QPushButton(trans.string('Palette', 38))
        deselectbtn.clicked.connect(self.DeselectProgressPathSelection)
        self.progPathList = ListWidgetWithToolTipSignal()
        self.progPathList.itemActivated.connect(self.HandleProgressPathSelectByList)
        self.progPathList.toolTipAboutToShow.connect(self.HandleProgressPathToolTipAboutToShow)
        self.progPathList.setSortingEnabled(True)

        progpathel.addWidget(progpathlabel)
        progpathel.addWidget(deselectbtn)
        progpathel.addWidget(self.progPathList)

        # events tab
        self.eventEditorTab = QtWidgets.QWidget()
        tabs.addTab(self.eventEditorTab, GetIcon('events'), '')
        tabs.setTabToolTip(6, trans.string('Palette', 18))
        tabs.setTabEnabled(6, False)

        eventel = QtWidgets.QGridLayout(self.eventEditorTab)
        self.eventEditorLayout = eventel

        eventlabel = QtWidgets.QLabel(trans.string('Palette', 20))
        eventNotesLabel = QtWidgets.QLabel(trans.string('Palette', 21))
        self.eventNotesEditor = QtWidgets.QLineEdit()
        self.eventNotesEditor.textEdited.connect(self.handleEventNotesEdit)

        self.eventChooser = QtWidgets.QTreeWidget()
        self.eventChooser.setColumnCount(2)
        self.eventChooser.setHeaderLabels((trans.string('Palette', 22), trans.string('Palette', 23)))
        self.eventChooser.itemClicked.connect(self.handleEventTabItemClick)
        self.eventChooserItems = []
        flags = Qt.ItemIsSelectable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled
        for id in range(32):
            itm = QtWidgets.QTreeWidgetItem()
            itm.setFlags(flags)
            itm.setCheckState(0, Qt.Unchecked)
            itm.setText(0, trans.string('Palette', 24, '[id]', str(id+1)))
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
        tabs.setTabToolTip(7, trans.string('Palette', 19))

        stampLabel = QtWidgets.QLabel(trans.string('Palette', 27))

        stampAddBtn = QtWidgets.QPushButton(trans.string('Palette', 28))
        stampAddBtn.clicked.connect(self.handleStampsAdd)
        stampAddBtn.setEnabled(False)
        self.stampAddBtn = stampAddBtn # so we can enable/disable it later
        stampRemoveBtn = QtWidgets.QPushButton(trans.string('Palette', 29))
        stampRemoveBtn.clicked.connect(self.handleStampsRemove)
        stampRemoveBtn.setEnabled(False)
        self.stampRemoveBtn = stampRemoveBtn # so we can enable/disable it later

        menu = QtWidgets.QMenu()
        menu.addAction(trans.string('Palette', 31), self.handleStampsOpen, 0) # Open Set...
        menu.addAction(trans.string('Palette', 32), self.handleStampsSave, 0) # Save Set As...
        stampToolsBtn = QtWidgets.QToolButton()
        stampToolsBtn.setText(trans.string('Palette', 30))
        stampToolsBtn.setMenu(menu)
        stampToolsBtn.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        stampToolsBtn.setSizePolicy(stampAddBtn.sizePolicy())
        stampToolsBtn.setMinimumHeight(stampAddBtn.height() / 20)

        stampNameLabel = QtWidgets.QLabel(trans.string('Palette', 35))
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
        tabs.setTabToolTip(8, trans.string('Palette', 33))

        cel = QtWidgets.QVBoxLayout()
        self.commentsTab.setLayout(cel)
        self.entEditorLayout = cel

        clabel = QtWidgets.QLabel(trans.string('Palette', 34))
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
            self.pathList.setItemSelected(selecteditem, False)

    def DeselectProgressPathSelection(self, checked):
        """
        Deselects selected progress path nodes in the list
        """
        for selecteditem in self.progPathList.selectedItems():
            self.progPathList.setItemSelected(selecteditem, False)

    @QtCore.pyqtSlot()
    def Autosave(self):
        """
        Auto saves the level
        """
        global AutoSaveDirty
        if not AutoSaveDirty: return

        data = Level.save()
        setSetting('AutoSaveFilePath', self.fileSavePath)
        setSetting('AutoSaveFileData', QtCore.QByteArray(data))
        AutoSaveDirty = False


    @QtCore.pyqtSlot()
    def TrackClipboardUpdates(self):
        """
        Catches systemwide clipboard updates
        """
        if Initializing: return
        clip = self.systemClipboard.text()
        if clip is not None and clip != '':
            clip = str(clip).strip()

            if clip.startswith('ReggieClip|') and clip.endswith('|%'):
                self.clipboard = clip.replace(' ', '').replace('\n', '').replace('\r', '').replace('\t', '')

                if UseRibbon: self.ribbon.setBtnEnabled('Paste', True)
                else: self.actions['paste'].setEnabled(True)
            else:
                self.clipboard = None
                if UseRibbon: self.ribbon.setBtnEnabled('Paste', False)
                else: self.actions['paste'].setEnabled(False)


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
        self.setWindowTitle('Reggie! Level Editor Next - %s%s' % (self.fileTitle, (' ' + trans.string('MainWindow', 0)) if Dirty else ''))

    def CheckDirty(self):
        """
        Checks if the level is unsaved and asks for a confirmation if so - if it returns True, Cancel was picked
        """
        if not Dirty: return False

        msg = QtWidgets.QMessageBox()
        msg.setText(trans.string('AutoSaveDlg', 2))
        msg.setInformativeText(trans.string('AutoSaveDlg', 3))
        msg.setStandardButtons(QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel)
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
        defEvents = Area.defEvents
        checked = Qt.Checked
        unchecked = Qt.Unchecked

        data = Area.Metadata.binData('EventNotes_A%d' % Area.areanum)
        eventTexts = {}
        if data is not None:
            # Iterate through the data
            idx = 0
            while idx < len(data):
                eventId = data[idx]
                idx += 1
                rawStrLen = data[idx:idx+4]
                idx += 4
                strLen = (rawStrLen[0] << 24) | (rawStrLen[1] << 16) | (rawStrLen[2] << 8) | rawStrLen[3]
                rawStr = data[idx:idx+strLen]
                idx += strLen
                newStr = ''
                for char in rawStr: newStr += chr(char)
                eventTexts[eventId] = newStr

        for id in range(32):
            item = self.eventChooserItems[id]
            value = 1 << id
            item.setCheckState(0, checked if (defEvents & value) != 0 else unchecked)
            if id in eventTexts: item.setText(1, eventTexts[id])
            else: item.setText(1, '')
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
            Area.defEvents |= 1 << selIdx
        else:
            # Turn a bit off (invert, turn on, invert)
            Area.defEvents = ~Area.defEvents
            Area.defEvents |= 1 << selIdx
            Area.defEvents = ~Area.defEvents

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

        Area.Metadata.setBinData('EventNotes_A%d' % Area.areanum, data)
        SetDirty()

    def handleStampsAdd(self):
        """
        Handles the "Add Stamp" btn being clicked
        """
        # Create a ReggieClip
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
        RegClp = self.encodeObjects(clipboard_o, clipboard_s)

        # Create a Stamp
        self.stampChooser.addStamp(Stamp(RegClp, 'New Stamp'))


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
        filetypes += trans.string('FileDlgs', 7) + ' (*.stamps);;' # *.stamps
        filetypes += trans.string('FileDlgs', 2) + ' (*)' # *
        fn = QtWidgets.QFileDialog.getOpenFileName(self, trans.string('FileDlgs', 6), '', filetypes)[0]
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
                    i += 9999 # avoid infinite loops
                    continue

                stamps.append(Stamp(rc, name))

        for stamp in stamps: self.stampChooser.addStamp(stamp)
            

    def handleStampsSave(self):
        """
        Handles the "Save Set As..." btn being clicked
        """
        filetypes = ''
        filetypes += trans.string('FileDlgs', 7) + ' (*.stamps);;' # *.stamps
        filetypes += trans.string('FileDlgs', 2) + ' (*)' # *
        fn = QtWidgets.QFileDialog.getSaveFileName(self, trans.string('FileDlgs', 3), '', filetypes)[0]
        if fn == '': return

        newdata = ''
        newdata += 'stamps\n'
        newdata += '------\n'

        for stampobj in self.stampChooser.model.items:
            name = stampobj.Name
            rc = stampobj.ReggieClip
            newdata += '\n'
            newdata += stampobj.Name + '\n'
            newdata += stampobj.ReggieClip + '\n'

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
        if Area.areanum == 1:
            dlg = MetaInfoDialog()
            if dlg.exec_() == QtWidgets.QDialog.Accepted:
                Area.Metadata.setStrData('Title', dlg.levelName.text())
                Area.Metadata.setStrData('Author', dlg.Author.text())
                Area.Metadata.setStrData('Group', dlg.Group.text())
                Area.Metadata.setStrData('Website', dlg.Website.text())

                SetDirty()
                return
        else:
            dlg = QtWidgets.QMessageBox()
            dlg.setText(trans.string('InfoDlg', 14))
            dlg.exec_()


    @QtCore.pyqtSlot()
    def HelpBox(self):
        """
        Shows the help box
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(os.path.join(module_path(), 'reggiedata', 'help', 'index.html')))


    @QtCore.pyqtSlot()
    def TipBox(self):
        """
        Reggie! Tips and Commands
        """
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(os.path.join(module_path(), 'reggiedata', 'help', 'tips.html')))


    @QtCore.pyqtSlot()
    def UpdateCheck(self):
        """
        Checks for updates and displays an appropriate dialog
        """
        UpdateDialog().exec_()


    @QtCore.pyqtSlot()
    def SelectAll(self):
        """
        Select all objects in the current area
        """
        paintRect = QtGui.QPainterPath()
        paintRect.addRect(float(0), float(0), float(1024*24), float(512*24))
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
                if UseRibbon: self.ribbon.setBtnEnabled('Cut', False)
                else: self.actions['cut'].setEnabled(False)
                if UseRibbon: self.ribbon.setBtnEnabled('Paste', True)
                else: self.actions['paste'].setEnabled(True)
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
                if UseRibbon: self.ribbon.setBtnEnabled('Paste', True)
                else: self.actions['paste'].setEnabled(True)
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
        convclip = ['ReggieClip']

        # get objects
        clipboard_o.sort(key=lambda x: x.zValue())

        for item in clipboard_o:
            convclip.append('0:%d:%d:%d:%d:%d:%d:%d' % (item.tileset, item.type, item.layer, item.objx, item.objy, item.width, item.height))

        # get sprites
        for item in clipboard_s:
            data = item.spritedata
            convclip.append('1:%d:%d:%d:%d:%d:%d:%d:%d:%d:%d' % (item.type, item.objx, item.objy, data[0], data[1], data[2], data[3], data[4], data[5], data[7]))

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

        global OverrideSnapping
        OverrideSnapping = True

        if not (encoded.startswith('ReggieClip|') and encoded.endswith('|%')): return

        clip = encoded.split('|')[1:-1]

        if len(clip) > 300:
            result = QtWidgets.QMessageBox.warning(self, 'Reggie!', trans.string('MainWindow', 1), QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
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

            Area.sprites.append(spr)
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
            AreaLayer = Area.layers[0]
            if len(AreaLayer) > 0:
                z = AreaLayer[-1].zValue() + 1
            else:
                z = 16384
            for obj in layer0:
                AreaLayer.append(obj)
                obj.setZValue(z)
                z += 1

        if len(layer1) > 0:
            AreaLayer = Area.layers[1]
            if len(AreaLayer) > 0:
                z = AreaLayer[-1].zValue() + 1
            else:
                z = 8192
            for obj in layer1:
                AreaLayer.append(obj)
                obj.setZValue(z)
                z += 1

        if len(layer2) > 0:
            AreaLayer = Area.layers[2]
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
        viewportx = (self.view.XScrollBar.value() / zoomscaler) / 24
        viewporty = (self.view.YScrollBar.value() / zoomscaler) / 24
        viewportwidth = (self.view.width() / zoomscaler) / 24
        viewportheight = (self.view.height() / zoomscaler) / 24

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
                    (item.objx + xpixeloffset + item.ImageObj.xOffset) * 1.5,
                    (item.objy + ypixeloffset + item.ImageObj.yOffset) * 1.5,
                    )
            elif isinstance(item, ObjectItem):
                item.setPos((item.objx + xoffset) * 24, (item.objy + yoffset) * 24)
            if select: item.setSelected(True)

        OverrideSnapping = False

        self.levelOverview.update()
        SetDirty()
        self.SelectionUpdateFlag = False
        self.ChangeSelectionHandler()

        return added

    def getEncodedObjects(self, encoded):
        """
        Create the objects from a ReggieClip
        """

        layers = ([], [], [])
        sprites = []

        try:
            if not (encoded.startswith('ReggieClip|') and encoded.endswith('|%')): return

            clip = encoded[11:-2].split('|')

            if len(clip) > 300:
                result = QtWidgets.QMessageBox.warning(self, 'Reggie!', trans.string('MainWindow', 1), QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
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
                    if len(split) != 11: continue

                    objx = int(split[2])
                    objy = int(split[3])
                    data = bytes(map(int, [split[4], split[5], split[6], split[7], split[8], split[9], '0', split[10]]))

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
                    result = QtWidgets.QMessageBox.information(None, trans.string('ShftItmDlg', 5),  trans.string('ShftItmDlg', 6), QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                    if result == QtWidgets.QMessageBox.No:
                        return

            xpoffset = xoffset * 1.5
            ypoffset = yoffset * 1.5

            global OverrideSnapping
            OverrideSnapping = True

            for obj in items:
                obj.setPos(obj.x() + xpoffset, obj.y() + ypoffset)

            OverrideSnapping = False

            SetDirty()


    @QtCore.pyqtSlot()
    def SwapObjectsTilesets(self):
        """
        Swaps objects' tilesets
        """
        global Area

        dlg = ObjectTilesetSwapDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            for layer in Area.layers:
                for nsmbobj in layer:
                    if nsmbobj.tileset == (dlg.FromTS.value()-1):
                        nsmbobj.SetType(dlg.ToTS.value() -1, nsmbobj.type)
                    elif nsmbobj.tileset == (dlg.ToTS.value()-1) and dlg.DoExchange.checkState() == Qt.Checked:
                        nsmbobj.SetType(dlg.FromTS.value() -1, nsmbobj.type)


            SetDirty()

    @QtCore.pyqtSlot()
    def SwapObjectsTypes(self):
        """
        Swaps objects' types
        """
        global Area

        dlg = ObjectTypeSwapDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            for layer in Area.layers:
                for nsmbobj in layer:
                    if nsmbobj.type == (dlg.FromType.value()) and nsmbobj.tileset == (dlg.FromTileset.value() - 1):
                        nsmbobj.SetType(dlg.ToTileset.value() - 1, dlg.ToType.value())
                    elif nsmbobj.type == (dlg.ToType.value()) and nsmbobj.tileset == (dlg.ToTileset.value() - 1) and dlg.DoExchange.checkState() == Qt.Checked:
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
            allID = set() # faster 'x in y' lookups for sets
            newID = 1
            for i in Area.locations:
                allID.add(i.id)

            while newID <= 255:
                if newID not in allID:
                    break
                newID += 1

            loc = LocationItem(newx, newy, neww - newx, newh - newy, newID)

            mw = mainWindow
            loc.positionChanged = mw.HandleObjPosChange
            mw.scene.addItem(loc)

            Area.locations.append(loc)
            loc.setSelected(True)


    @QtCore.pyqtSlot()
    def HandleAddNewArea(self):
        """
        Adds a new area to the level
        """
        if len(Level.areas) >= 4:
            QtWidgets.QMessageBox.warning(self, 'Reggie!', trans.string('AreaChoiceDlg', 2))
            return

        if self.CheckDirty():
            return

        try:
            newA = Level.addArea()
        except: return

        with open('reggiedata/blankcourse.bin', 'rb') as blank:
            course = blank.read()
        newA.load(course)

        newID = len(Level.areas)

        if not self.HandleSave(): return
        self.LoadLevel(None, self.fileSavePath, True, newID)


    @QtCore.pyqtSlot()
    def HandleImportArea(self):
        """
        Imports an area from another level
        """
        if len(Level.areas) >= 4:
            QtWidgets.QMessageBox.warning(self, 'Reggie!', trans.string('AreaChoiceDlg', 2))
            return

        if self.CheckDirty():
            return

        filetypes = ''
        filetypes += trans.string('FileDlgs', 1) + ' (*.sarc);;' # *.sarc
        filetypes += trans.string('FileDlgs', 5) + ' (*.sarc.lh);;' # *.sarc.LH
        filetypes += trans.string('FileDlgs', 2) + ' (*)' # *
        fn = QtWidgets.QFileDialog.getOpenFileName(self, trans.string('FileDlgs', 0), '', filetypes)[0]
        if fn == '': return

        with open(str(fn), 'rb') as fileobj:
            arcdata = fileobj.read()
        if LHTool.isLHCompressed(arcdata):
            arcdata = LHTool.decompressLH(arcdata)

        arc = SarcLib.SARC_Archive()
        arc.load(arcdata)

        # get the area count
        areacount = 0

        for item, val in arc.files:
            if val is not None:
                # it's a file
                fname = item[item.rfind('/')+1:]
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

        for item, val in arc.files:
            if val is not None:
                fname = item.split('/')[-1]
                if fname == reqcourse:
                    course = val
                elif fname == reqL0:
                    L0 = val
                elif fname == reqL1:
                    L1 = val
                elif fname == reqL2:
                    L2 = val

        # add them to our level
        newID = len(Level.areas) + 1

        newA = Level.addArea()
        newA.load(course, L0, L1, L2)

        if not self.HandleSave(): return
        self.LoadLevel(None, self.fileSavePath, True, newID)


    @QtCore.pyqtSlot()
    def HandleDeleteArea(self):
        """
        Deletes the current area
        """
        result = QtWidgets.QMessageBox.warning(self, 'Reggie!', trans.string('DeleteArea', 0), QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if result == QtWidgets.QMessageBox.No: return

        if not self.HandleSave(): return

        Level.deleteArea(Area.areanum)

        # no error checking. if it saved last time, it will probably work now

        with open(self.fileSavePath, 'wb') as f:
            f.write(Level.save())
        self.LoadLevel(None, self.fileSavePath, True, 1)


    @QtCore.pyqtSlot()
    def HandleChangeGamePath(self, auto=False):
        """
        Change the game path used by the current game definition
        """
        if self.CheckDirty(): return

        path = None
        while not isValidGamePath(path):
            path = QtWidgets.QFileDialog.getExistingDirectory(None, trans.string('ChangeGamePath', 0, '[game]', gamedef.name))
            if path == '':
                return False

            path = str(path)

            if (not isValidGamePath(path)) and (not gamedef.custom): # custom gamedefs can use incomplete folders
                QtWidgets.QMessageBox.information(None, trans.string('ChangeGamePath', 1),  trans.string('ChangeGamePath', 2))
            else:
                SetGamePath(path)
                break

        if not auto: self.LoadLevel(None, FirstLevels[CurrentGame], False, 1)
        return True


    @QtCore.pyqtSlot()
    def HandlePreferences(self):
        """
        Edit Reggie preferences
        """

        # Show the dialog
        dlg = PreferencesDialog()
        if dlg.exec_() == QtWidgets.QDialog.Rejected:
            return


        # Get the splash screen setting
        if dlg.generalTab.SplashA.isChecked():
            setSetting('ShowSplash', True)
        elif dlg.generalTab.SplashN.isChecked():
            setSetting('ShowSplash', False)
        else:
            setSetting('ShowSplash', 'TPLLib')

        # Get the Menubar/Ribbon setting
        if dlg.generalTab.MenuR.isChecked():
            setSetting('Menu', 'Ribbon')
        else:
            setSetting('Menu', 'Menubar')

        # Get the Tileset Tab setting
        if dlg.generalTab.TileD.isChecked():
            setSetting('TilesetTab', 'Default')
        else:
            setSetting('TilesetTab', 'Old')

        # Get the translation
        name = str(dlg.generalTab.Trans.itemData(dlg.generalTab.Trans.currentIndex(), Qt.UserRole))
        setSetting('Translation', name)

        # Get the Toolbar tab settings
        boxes = (dlg.toolbarTab.FileBoxes, dlg.toolbarTab.EditBoxes, dlg.toolbarTab.ViewBoxes, dlg.toolbarTab.SettingsBoxes, dlg.toolbarTab.HelpBoxes)
        ToolbarSettings = {}
        for boxList in boxes:
            for box in boxList:
                ToolbarSettings[box.InternalName] = box.isChecked()
        setSetting('ToolbarActs', ToolbarSettings)

        # Get the theme settings
        for btn in dlg.themesTab.btns:
            if btn.isChecked():
                setSetting('Theme', dlg.themesTab.btnvals[btn][0])
                break
        setSetting('uiStyle', dlg.themesTab.NonWinStyle.currentText())

        # Warn the user that they may need to restart
        QtWidgets.QMessageBox.warning(None, trans.string('PrefsDlg', 0), trans.string('PrefsDlg', 30))


    @QtCore.pyqtSlot()
    def HandleNewLevel(self):
        """
        Create a new level
        """
        if self.CheckDirty(): return
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
            self.LoadLevel(None, dlg.currentlevel, False, 1)


    @QtCore.pyqtSlot()
    def HandleOpenFromFile(self):
        """
        Open a level using the filename
        """
        if self.CheckDirty(): return

        filetypes = ''
        filetypes += trans.string('FileDlgs', 1) + ' (*.sarc);;' # *.sarc
        filetypes += trans.string('FileDlgs', 5) + ' (*.sarc.lh);;' # *.sarc.LH
        filetypes += trans.string('FileDlgs', 2) + ' (*)' # *
        fn = QtWidgets.QFileDialog.getOpenFileName(self, trans.string('FileDlgs', 0), '', filetypes)[0]
        if fn == '': return
        self.LoadLevel(None, str(fn), True, 1)


    @QtCore.pyqtSlot()
    def HandleSave(self):
        """
        Save a level back to the archive
        """
        if not mainWindow.fileSavePath:
            self.HandleSaveAs()
            return

        global Dirty, AutoSaveDirty
        data = Level.save()
        try:
            with open(self.fileSavePath, 'wb') as f:
                f.write(data)
        except IOError as e:
            QtWidgets.QMessageBox.warning(None, trans.string('Err_Save', 0), trans.string('Err_Save', 1, '[err1]', e.args[0], '[err2]', e.args[1]))
            return False

        Dirty = False
        AutoSaveDirty = False
        self.UpdateTitle()

        setSetting('AutoSaveFilePath', self.fileSavePath)
        setSetting('AutoSaveFileData', 'x')
        return True


    @QtCore.pyqtSlot()
    def HandleSaveAs(self):
        """
        Save a level back to the archive, with a new filename
        """
        fn = QtWidgets.QFileDialog.getSaveFileName(self, trans.string('FileDlgs', 3), '', trans.string('FileDlgs', 1) + ' (*.sarc);;' + trans.string('FileDlgs', 2) + ' (*)')[0]
        if fn == '': return
        fn = str(fn)

        global Dirty, AutoSaveDirty
        Dirty = False
        AutoSaveDirty = False
        Dirty = False

        self.fileSavePath = fn
        self.fileTitle = os.path.basename(fn)

        data = Level.save()
        with open(fn, 'wb') as f:
            f.write(data)

        setSetting('AutoSaveFilePath', fn)
        setSetting('AutoSaveFileData', 'x')

        self.UpdateTitle()

        self.RecentFilesMgr.addPath(self.fileSavePath)

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
            self.areaComboBox.setCurrentIndex(Area.areanum)
            return

        if Area.areanum != idx + 1:
            self.LoadLevel(None, self.fileSavePath, True, idx + 1)


    @QtCore.pyqtSlot(bool)
    def HandleUpdateLayer0(self, checked):
        """
        Handle toggling of layer 0 being shown
        """
        global Layer0Shown

        Layer0Shown = checked

        if Area is not None:
            for obj in Area.layers[0]:
                obj.setVisible(Layer0Shown)

        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleUpdateLayer1(self, checked):
        """
        Handle toggling of layer 1 being shown
        """
        global Layer1Shown

        Layer1Shown = checked

        if Area is not None:
            for obj in Area.layers[1]:
                obj.setVisible(Layer1Shown)

        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleUpdateLayer2(self, checked):
        """
        Handle toggling of layer 2 being shown
        """
        global Layer2Shown

        Layer2Shown = checked

        if Area is not None:
            for obj in Area.layers[2]:
                obj.setVisible(Layer2Shown)

        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleTilesetAnimToggle(self, checked):
        """
        Handle toggling of tileset animations
        """
        global TilesetsAnimating

        TilesetsAnimating = checked
        for tile in Tiles:
            if tile is not None: tile.resetAnimation()

        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleCollisionsToggle(self, checked):
        """
        Handle toggling of tileset collisions viewing
        """
        global CollisionsShown

        CollisionsShown = checked

        setSetting('ShowCollisions', CollisionsShown)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleDepthToggle(self, checked):
        """
        Handle toggling of tileset depth highlighting viewing
        """
        global DepthShown

        DepthShown = checked

        setSetting('ShowDepth', DepthShown)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleRealViewToggle(self, checked):
        """
        Handle toggling of Real View
        """
        global RealViewEnabled

        RealViewEnabled = checked
        SLib.RealViewEnabled = RealViewEnabled

        setSetting('RealViewEnabled', RealViewEnabled)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleSpritesVisibility(self, checked):
        """
        Handle toggling of sprite visibility
        """
        global SpritesShown

        SpritesShown = checked

        if Area is not None:
            for spr in Area.sprites:
                spr.setVisible(SpritesShown)

        setSetting('ShowSprites', SpritesShown)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleSpriteImages(self, checked):
        """
        Handle toggling of sprite images
        """
        global SpriteImagesShown

        SpriteImagesShown = checked

        setSetting('ShowSpriteImages', SpriteImagesShown)

        if Area is not None:
            for spr in Area.sprites:
                spr.UpdateRects()
                if SpriteImagesShown:
                    spr.setPos(
                        (spr.objx + spr.ImageObj.xOffset) * 1.5,
                        (spr.objy + spr.ImageObj.yOffset) * 1.5,
                        )
                else:
                    spr.setPos(
                        spr.objx * 1.5,
                        spr.objy * 1.5,
                        )

        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleLocationsVisibility(self, checked):
        """
        Handle toggling of location visibility
        """
        global LocationsShown

        LocationsShown = checked

        if Area is not None:
            for loc in Area.locations:
                loc.setVisible(LocationsShown)

        setSetting('ShowLocations', LocationsShown)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleCommentsVisibility(self, checked):
        """
        Handle toggling of comment visibility
        """
        global CommentsShown

        CommentsShown = checked

        if Area is not None:
            for com in Area.comments:
                com.setVisible(CommentsShown)

        setSetting('ShowComments', CommentsShown)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleObjectsFreeze(self, checked):
        """
        Handle toggling of objects being frozen
        """
        global ObjectsFrozen

        ObjectsFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if Area is not None:
            for layer in Area.layers:
                for obj in layer:
                    obj.setFlag(flag1, not ObjectsFrozen)
                    obj.setFlag(flag2, not ObjectsFrozen)

        setSetting('FreezeObjects', ObjectsFrozen)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleSpritesFreeze(self, checked):
        """
        Handle toggling of sprites being frozen
        """
        global SpritesFrozen

        SpritesFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if Area is not None:
            for spr in Area.sprites:
                spr.setFlag(flag1, not SpritesFrozen)
                spr.setFlag(flag2, not SpritesFrozen)

        setSetting('FreezeSprites', SpritesFrozen)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleEntrancesFreeze(self, checked):
        """
        Handle toggling of entrances being frozen
        """
        global EntrancesFrozen

        EntrancesFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if Area is not None:
            for ent in Area.entrances:
                ent.setFlag(flag1, not EntrancesFrozen)
                ent.setFlag(flag2, not EntrancesFrozen)

        setSetting('FreezeEntrances', EntrancesFrozen)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleLocationsFreeze(self, checked):
        """
        Handle toggling of locations being frozen
        """
        global LocationsFrozen

        LocationsFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if Area is not None:
            for loc in Area.locations:
                loc.setFlag(flag1, not LocationsFrozen)
                loc.setFlag(flag2, not LocationsFrozen)

        setSetting('FreezeLocations', LocationsFrozen)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandlePathsFreeze(self, checked):
        """
        Handle toggling of paths being frozen
        """
        global PathsFrozen

        PathsFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if Area is not None:
            for node in Area.paths:
                node.setFlag(flag1, not PathsFrozen)
                node.setFlag(flag2, not PathsFrozen)

        setSetting('FreezePaths', PathsFrozen)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleProgressPathsFreeze(self, checked):
        """
        Handle toggling of progress paths being frozen
        """
        global ProgressPathsFrozen

        ProgressPathsFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if Area is not None:
            for node in Area.progpaths:
                node.setFlag(flag1, not ProgressPathsFrozen)
                node.setFlag(flag2, not ProgressPathsFrozen)

        setSetting('FreezeProgressPaths', ProgressPathsFrozen)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleCommentsFreeze(self, checked):
        """
        Handle toggling of comments being frozen
        """
        global CommentsFrozen

        CommentsFrozen = checked
        flag1 = QtWidgets.QGraphicsItem.ItemIsSelectable
        flag2 = QtWidgets.QGraphicsItem.ItemIsMovable

        if Area is not None:
            for com in Area.comments:
                com.setFlag(flag1, not CommentsFrozen)
                com.setFlag(flag2, not CommentsFrozen)

        setSetting('FreezeComments', CommentsFrozen)
        self.scene.update()


    @QtCore.pyqtSlot(bool)
    def HandleSwitchGrid(self):
        """
        Handle switching of the grid view
        """
        global GridType

        if GridType is None: GridType = 'grid'
        elif GridType == 'grid': GridType = 'checker'
        else: GridType = None

        setSetting('GridType', GridType)
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
        self.ZoomTo(self.ZoomLevels[len(self.ZoomLevels)-1])


    def ZoomTo(self, z):
        """
        Zoom to a specific level
        """
        tr = QtGui.QTransform()
        tr.scale(z / 100.0, z / 100.0)
        self.ZoomLevel = z
        self.view.setTransform(tr)
        self.levelOverview.mainWindowScale = z/100.0

        zi = self.ZoomLevels.index(z)
        if UseRibbon:
            # zoomMax and zoomMin are handled by the ribbon itself
            self.ribbon.setBtnEnabled('zoommax', zi < len(self.ZoomLevels) - 1)
            self.ribbon.setBtnEnabled('zoomin', zi < len(self.ZoomLevels) - 1)
            self.ribbon.setBtnEnabled('zoom100', z != 100.0)
            self.ribbon.setBtnEnabled('zoomout', zi > 0)
            self.ribbon.setBtnEnabled('zoommin', zi > 0)
        else:
            self.actions['zoommax'].setEnabled(zi < len(self.ZoomLevels) - 1)
            self.actions['zoomin'] .setEnabled(zi < len(self.ZoomLevels) - 1)
            self.actions['zoomactual'].setEnabled(z != 100.0)
            self.actions['zoomout'].setEnabled(zi > 0)
            self.actions['zoommin'].setEnabled(zi > 0)

        self.ZoomWidget.setZoomLevel(z)
        self.ZoomStatusWidget.setZoomLevel(z)

        # Update the zone grabber rects, to resize for the new zoom level
        for z in Area.zones:
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
        for com in Area.comments:
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
        Area.Metadata.setBinData('InLevelComments_A%d' % Area.areanum, b)


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
            self.progPathEditorDock.setVisible(False)
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

            gamedef.SetLastLevel(str(mainWindow.fileSavePath))

            setSetting('AutoSaveFilePath', 'none')
            setSetting('AutoSaveFileData', 'x')

            event.accept()


    def LoadLevel(self, game, name, isFullPath, areaNum):
        """
        Load a level from any game into the editor
        """
        global levName; levName=name.replace('\\', '/').split('/')[-1]

        if game is None:
            game = self.CurrentGame

        # Get the file path, if possible
        if name is not None:
            checknames = []
            if isFullPath:
                checknames = [name,]
            else:
                for ext in FileExtentions[game]:
                    checknames.append(os.path.join(gamedef.GetGamePath(), name + ext))

            found = False
            for checkname in checknames:
                if os.path.isfile(checkname):
                    found = True
                    break
            if not found:
                QtWidgets.QMessageBox.warning(self, 'Reggie!', trans.string('Err_CantFindLevel', 0, '[name]', checkname), QtWidgets.QMessageBox.Ok)
                return False
            if not IsNSMBLevel(checkname):
                QtWidgets.QMessageBox.warning(self, 'Reggie!', trans.string('Err_InvalidLevel', 0), QtWidgets.QMessageBox.Ok)
                return False

        name = checkname

        # Get the data
        global RestoredFromAutoSave
        if not RestoredFromAutoSave:

            # Check if there is a file by this name
            if not os.path.isfile(name):
                QtWidgets.QMessageBox.warning(None, trans.string('Err_MissingLevel', 0), trans.string('Err_MissingLevel', 1, '[file]', name))
                return False

            # Set the filepath variables
            self.fileSavePath = name
            self.fileTitle = os.path.basename(self.fileSavePath)

            # Open the file
            with open(self.fileSavePath, 'rb') as fileobj:
                levelData = fileobj.read()

            # Decompress, if needed
            if LHTool.isLHCompressed(levelData):
                levelData = LHTool.decompressLH(levelData)

        else:
            # Auto-saved level. Check if there's a path associated with it:

            if AutoSavePath == 'None':
                self.fileSavePath = None
                self.fileTitle = trans.string('WindowTitle', 0)
            else:
                self.fileSavePath = AutoSavePath
                self.fileTitle = os.path.basename(name)

            # Get the level data
            levelData = AutoSaveData
            SetDirty(noautosave=True)

            # Turn off the autosave flag
            RestoredFromAutoSave = False

        # Turn the dirty flag off, and keep it that way
        global Dirty, DirtyOverride
        Dirty = False
        DirtyOverride += 1

        # Track progress.. but only if we don't have TPLLib
        # Cython version because otherwise it's far too fast.
        if TPLLib.using_cython:
            progress = None
        elif app.splashscrn is not None:
            progress = None
        else:
            progress = QtWidgets.QProgressDialog(self)

            progress.setCancelButton(None)
            progress.setMinimumDuration(0)
            progress.setRange(0, 7)
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowTitle('Reggie!')

        # Here's how progress is tracked. (After the major refactor, it may be a bit messed up now.)
        # - 0: Loading level data
        # [Area.__init__ is entered here]
        # - 1: Loading tilesets [1/2/3/4 allocated for each tileset]
        # - 5: Loading layers
        # [Control is returned to LoadLevel_NSMB2]
        # - 6: Loading objects
        # - 7: Preparing editor

        # First, clear out the existing level.
        self.scene.clearSelection()
        self.CurrentSelection = []
        self.scene.clear()

        # Clear out all level-thing lists
        for thingList in (self.spriteList, self.entranceList, self.locationList, self.pathList, self.progPathList, self.commentList):
            thingList.clear()
            thingList.selectionModel().setCurrentIndex(QtCore.QModelIndex(), QtCore.QItemSelectionModel.Clear)

        # Reset these here, because if they are set after
        # creating the objects, they use the old values.
        global CurrentLayer, Layer0Shown, Layer1Shown, Layer2Shown
        CurrentLayer = 1
        Layer0Shown = True
        Layer1Shown = True
        Layer2Shown = True

        # Prevent things from snapping when they're created
        global OverrideSnapping
        OverrideSnapping = True

        # Update progress
        if progress is not None:
            progress.setLabelText(trans.string('Splash', 2))
            progress.setValue(0)
        if app.splashscrn is not None:
            updateSplash(trans.string('Splash', 2), 0)

        # Load the actual level for this specific game
        if game is NewSuperMarioBros:
            # This game is not supported... YET
            raise NotImplementedError
        elif game is NewSuperMarioBrosWii:
            self.LoadLevel_NSMBW(levelData, areaNum, progress)
        elif game is NewSuperMarioBros2:
            self.LoadLevel_NSMB2(levelData, areaNum, progress)
        elif game is NewSuperMarioBrosU:
            # This game is not supported... YET
            raise NotImplementedError
        elif game is NewSuperLuigiU:
            # This game is not supported... YET
            raise NotImplementedError

        # Set the level overview settings
        mainWindow.levelOverview.maxX = 100
        mainWindow.levelOverview.maxY = 40

        # Fill up the area list
        if UseRibbon:
            self.ribbon.updateAreaComboBox(len(Level.areas), area)
        else:
            self.areaComboBox.clear()
            for i in range(1, len(Level.areas) + 1):
                self.areaComboBox.addItem(trans.string('AreaCombobox', 0, '[num]', i))
            self.areaComboBox.setCurrentIndex(areaNum - 1)

        self.levelOverview.update()

        # Scroll to the initial entrance
        startEntID = Area.startEntrance
        startEnt = None
        for ent in Area.entrances:
            if ent.entid == startEntID: startEnt = ent

        self.view.centerOn(0, 0)
        if startEnt is not None: self.view.centerOn(startEnt.objx * 1.5, startEnt.objy * 1.5)
        self.ZoomTo(100.0)

        # Reset some editor things
        if UseRibbon:
            self.ribbon.setBtnEnabled('addarea', len(Level.areas) < 4)
            self.ribbon.setBtnEnabled('imarea', len(Level.areas) < 4)
            self.ribbon.setBtnEnabled('delarea', len(Level.areas) > 1)
        else:
            self.actions['showlay0'].setChecked(True)
            self.actions['showlay1'].setChecked(True)
            self.actions['showlay2'].setChecked(True)
            self.actions['addarea'].setEnabled(len(Level.areas) < 4)
            self.actions['importarea'].setEnabled(len(Level.areas) < 4)
            self.actions['deletearea'].setEnabled(len(Level.areas) > 1)

        # Turn snapping back on
        OverrideSnapping = False

        # Turn the dirty flag off
        DirtyOverride -= 1
        self.UpdateTitle()

        # Update UI things
        self.scene.update()

        self.levelOverview.Reset()
        self.levelOverview.update()
        QtCore.QTimer.singleShot(20, self.levelOverview.update)

        # Remove the splashscreen
        removeSplash()

        # Add the path to Recent Files
        self.RecentFilesMgr.addPath(mainWindow.fileSavePath)

        # Set the Current Game setting
        self.CurrentGame = game
        setSetting('CurrentGame', self.CurrentGame)

        # If we got this far, everything worked! Return True.
        return True


    def LoadLevel_NSMBW(self, levelData, areaNum, progress):
        """
        Performs all level-loading tasks specific to New Super Mario Bros. Wii levels.
        Do not call this directly - use LoadLevel(NewSuperMarioBrosWii, ...) instead!
        """
        raise NotImplementedError

    def LoadLevel_NSMB2(self, levelData, areaNum, progress):
        """
        Performs all level-loading tasks specific to New Super Mario Bros. 2 levels.
        Do not call this directly - use LoadLevel(NewSuperMarioBros2, ...) instead!
        """

        # Create the new level object
        global Level
        Level = Level_NSMB2()

        # Load it
        if not Level.load(levelData, areaNum, progress):
            raise Exception

        # Prepare the object picker
        if progress is not None:
            progress.setLabelText(trans.string('Splash', 4))
            progress.setValue(6)
        if app.splashscrn is not None:
            updateSplash(trans.string('Splash', 4), 6)

        self.objUseLayer1.setChecked(True)

        self.objPicker.LoadFromTilesets()

        self.objAllTab.setCurrentIndex(0)
        self.objAllTab.setTabEnabled(0, (Area.tileset0 != ''))
        self.objAllTab.setTabEnabled(1, (Area.tileset1 != ''))
        self.objAllTab.setTabEnabled(2, (Area.tileset2 != ''))
        self.objAllTab.setTabEnabled(3, (Area.tileset3 != ''))

        # Add all things to scene
        if progress is not None:
            progress.setLabelText(trans.string('Splash', 5))
            progress.setValue(7)
        if app.splashscrn is not None:
            updateSplash(trans.string('Splash', 5), 7)

        # Load events
        self.LoadEventTabFromLevel()

        # Add all things to the scene
        pcEvent = self.HandleObjPosChange
        for layer in reversed(Area.layers):
            for obj in layer:
                obj.positionChanged = pcEvent
                self.scene.addItem(obj)

        pcEvent = self.HandleSprPosChange
        for spr in Area.sprites:
            spr.positionChanged = pcEvent
            spr.listitem = ListWidgetItem_SortsByOther(spr)
            self.spriteList.addItem(spr.listitem)
            self.scene.addItem(spr)
            spr.UpdateListItem()

        pcEvent = self.HandleEntPosChange
        for ent in Area.entrances:
            ent.positionChanged = pcEvent
            ent.listitem = ListWidgetItem_SortsByOther(ent)
            ent.listitem.entid = ent.entid
            self.entranceList.addItem(ent.listitem)
            self.scene.addItem(ent)
            ent.UpdateListItem()

        for zone in Area.zones:
            self.scene.addItem(zone)

        pcEvent = self.HandleLocPosChange
        scEvent = self.HandleLocSizeChange
        for location in Area.locations:
            location.positionChanged = pcEvent
            location.sizeChanged = scEvent
            location.listitem = ListWidgetItem_SortsByOther(location)
            self.locationList.addItem(location.listitem)
            self.scene.addItem(location)
            location.UpdateListItem()

        for path in Area.paths:
            path.positionChanged = self.HandlePathPosChange
            path.listitem = ListWidgetItem_SortsByOther(path)
            self.pathList.addItem(path.listitem)
            self.scene.addItem(path)
            path.UpdateListItem()

        for path in Area.pathdata:
            peline = PathEditorLineItem(path['nodes'])
            path['peline'] = peline
            self.scene.addItem(peline)
            peline.loops = path['loops']

        for path in Area.paths:
            path.UpdateListItem()

        for progPath in Area.progpaths:
            progPath.positionChanged = self.HandleProgressPathPosChange
            progPath.listitem = ListWidgetItem_SortsByOther(progPath)
            self.progPathList.addItem(progPath.listitem)
            self.scene.addItem(progPath)
            progPath.UpdateListItem()

        for progPath in Area.progpathdata:
            peline = ProgressPathEditorLineItem(progPath['nodes'])
            progPath['peline'] = peline
            self.scene.addItem(peline)

        for progPath in Area.progpaths:
            progPath.UpdateListItem()

        for com in Area.comments:
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
        global TilesetCache
        if not soft: TilesetCache = {} # blank out the tileset cache; we're reloading them

        tilesets = [Area.tileset0, Area.tileset1, Area.tileset2, Area.tileset3]
        for idx, name in enumerate(tilesets):
            if (name is not None) and (name != ''):
                LoadTileset(idx, name, not soft)

        self.objPicker.LoadFromTilesets()

        for layer in Area.layers:
            for obj in layer:
                obj.updateObjCache()

        self.scene.update()


        global Sprites
        Sprites = None
        LoadSpriteData()


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
        showProgPathPanel = False
        updateModeInfo = False

        # clear our variables
        self.selObj = None
        self.selObjs = None

        self.spriteList.setCurrentItem(None)
        self.entranceList.setCurrentItem(None)
        self.locationList.setCurrentItem(None)
        self.pathList.setCurrentItem(None)
        self.progPathList.setCurrentItem(None)
        self.commentList.setCurrentItem(None)
        
        # possibly a small optimization
        func_ii = isinstance
        type_obj = ObjectItem
        type_spr = SpriteItem
        type_ent = EntranceItem
        type_loc = LocationItem
        type_path = PathItem
        type_progpath = ProgressPathItem
        type_com = CommentItem

        if len(selitems) == 0:
            # nothing is selected
            if UseRibbon:
                self.ribbon.setBtnEnabled('cut', False)
                self.ribbon.setBtnEnabled('copy', False)
                self.ribbon.setBtnEnabled('shiftitems', False)
                self.ribbon.setBtnEnabled('mergelocs', False)
            else:
                self.actions['cut'].setEnabled(False)
                self.actions['copy'].setEnabled(False)
                self.actions['shiftitems'].setEnabled(False)
                self.actions['mergelocations'].setEnabled(False)

        elif len(selitems) == 1:
            # only one item, check the type
            if UseRibbon:
                self.ribbon.setBtnEnabled('cut', True)
                self.ribbon.setBtnEnabled('copy', True)
                self.ribbon.setBtnEnabled('shiftitems', True)
                self.ribbon.setBtnEnabled('mergelocs', False)
            else:
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
            elif func_ii(item, type_progpath):
                self.creationTabs.setCurrentIndex(5)
                self.UpdateFlag = True
                self.progPathList.setCurrentItem(item.listitem)
                self.UpdateFlag = False
                showProgPathPanel = True
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
            if UseRibbon:
                self.ribbon.setBtnEnabled('cut', True)
                self.ribbon.setBtnEnabled('copy', True)
                self.ribbon.setBtnEnabled('shiftitems', True)
            else:
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
        progpath = 0
        com = 0
        for item in selitems:
            if func_ii(item, type_spr): spr += 1
            elif func_ii(item, type_ent): ent += 1
            elif func_ii(item, type_obj): obj += 1
            elif func_ii(item, type_loc): loc += 1
            elif func_ii(item, type_path): path += 1
            elif func_ii(item, type_progpath): progpath += 1
            elif func_ii(item, type_com): com += 1

        if loc > 2:
            if UseRibbon: self.ribbon.setBtnEnabled('MergeLocations', True)
            else: self.actions['mergelocations'].setEnabled(True)

        # write the statusbar label text
        text = ''
        if len(selitems) > 0:
            singleitem = len(selitems) == 1
            if singleitem:
                if obj: text = trans.string('Statusbar', 0)  # 1 object selected
                elif spr: text = trans.string('Statusbar', 1)  # 1 sprite selected
                elif ent: text = trans.string('Statusbar', 2)  # 1 entrance selected
                elif loc: text = trans.string('Statusbar', 3)  # 1 location selected
                elif path: text = trans.string('Statusbar', 4)  # 1 path node selected
                elif progpath: text = trans.string('Statusbar', 34)  # 1 progress path node selected
                else: text = trans.string('Statusbar', 29) # 1 comment selected
            else: # multiple things selected; see if they're all the same type
                if not any((spr, ent, loc, path, progpath, com)):
                    text = trans.string('Statusbar', 5, '[x]', obj) # x objects selected
                elif not any((obj, ent, loc, path, progpath, com)):
                    text = trans.string('Statusbar', 6, '[x]', spr) # x sprites selected
                elif not any((obj, spr, loc, path, progpath, com)):
                    text = trans.string('Statusbar', 7, '[x]', ent) # x entrances selected
                elif not any((obj, spr, ent, path, progpath, com)):
                    text = trans.string('Statusbar', 8, '[x]', loc) # x locations selected
                elif not any((obj, spr, ent, loc, progpath, com)):
                    text = trans.string('Statusbar', 9, '[x]', path) # x path nodes selected
                elif not any((obj, spr, ent, loc, path, com)):
                    text = trans.string('Statusbar', 35, '[x]', progpath) # x progress path nodes selected
                elif not any((obj, spr, ent, loc, path, progpath)):
                    text = trans.string('Statusbar', 30, '[x]', com) # x comments selected
                else: # different types
                    text = trans.string('Statusbar', 10, '[x]', len(selitems)) # x items selected
                    types = (
                        (obj, 12, 13), # variable, translation string ID if var == 1, translation string ID if var > 1
                        (spr, 14, 15),
                        (ent, 16, 17),
                        (loc, 18, 19),
                        (path, 20, 21),
                        (progpath, 36, 37),
                        (com, 31, 32),
                        )
                    first = True
                    for var, singleCode, multiCode in types:
                        if var > 0:
                            if not first: text += trans.string('Statusbar', 11)
                            first = False
                            text += trans.string('Statusbar', (singleCode if var == 1 else multiCode), '[x]', var)
                            # above: '[x]', var) can't hurt if var == 1

                    text += trans.string('Statusbar', 22) # ')'
        self.selectionLabel.setText(text)

        self.CurrentSelection = selitems

        for thing in selitems:
            # This helps sync non-objects with objects while dragging
            if not isinstance(thing, ObjectItem):
                thing.dragoffsetx = (((thing.objx // 16) * 16) - thing.objx) * 1.5
                thing.dragoffsety = (((thing.objy // 16) * 16) - thing.objy) * 1.5

        self.spriteEditorDock.setVisible(showSpritePanel)
        self.entranceEditorDock.setVisible(showEntrancePanel)

        self.locationEditorDock.setVisible(showLocationPanel)
        self.pathEditorDock.setVisible(showPathPanel)
        self.progPathEditorDock.setVisible(showProgPathPanel)

        if len(self.CurrentSelection) > 0:
            if UseRibbon: self.ribbon.setBtnEnabled('desel', True)
            else: self.actions['deselect'].setEnabled(True)
        else:
            if UseRibbon: self.ribbon.setBtnEnabled('desel', False)
            else: self.actions['deselect'].setEnabled(False)

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
        if idx == 0: # objects
            CPT = self.objAllTab.currentIndex()
        elif idx == 1: # sprites
            CPT = 4
            if self.sprAllTab.currentIndex() == 1: CPT = -1
        elif idx == 2: CPT = 5 # entrances
        elif idx == 3: CPT = 7 # locations
        elif idx == 4: CPT = 6 # paths
        elif idx == 5: CPT = 10 # progress paths
        elif idx == 6: CPT = -1 # events
        elif idx == 7: CPT = 8 # stamp pad
        elif idx == 8: CPT = 9 # comment

        global CurrentPaintType
        CurrentPaintType = CPT

    @QtCore.pyqtSlot(int)
    def ObjTabChanged(self, nt):
        """
        Handles the selected slot tab in the object palette changing
        """
        if hasattr(self, 'objPicker'):
            if nt >= 0 and nt <= 3:
                self.objPicker.ShowTileset(nt)
                eval('self.objTS%dTab' % nt).setLayout(self.createObjectLayout)
            self.defaultPropDock.setVisible(False)
        global CurrentPaintType
        CurrentPaintType = nt


    @QtCore.pyqtSlot(int)
    def SprTabChanged(self, nt):
        """
        Handles the selected tab in the sprite palette changing
        """
        if nt == 0: cpt = 4
        else: cpt = -1
        global CurrentPaintType
        CurrentPaintType = cpt


    @QtCore.pyqtSlot(int)
    def LayerChoiceChanged(self, nl):
        """
        Handles the selected layer changing
        """
        global CurrentLayer
        CurrentLayer = nl

        # should we replace?
        if QtWidgets.QApplication.keyboardModifiers() == Qt.AltModifier:
            items = self.scene.selectedItems()
            type_obj = ObjectItem
            tileset = CurrentPaintType
            area = Area
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
                    newVisibility = Layer0Shown
                elif nl == 1:
                    newVisibility = Layer1Shown
                else:
                    newVisibility = Layer2Shown

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


    @QtCore.pyqtSlot(int)
    def ObjectChoiceChanged(self, type):
        """
        Handles a new object being chosen
        """
        global CurrentObject
        CurrentObject = type


    @QtCore.pyqtSlot(int)
    def ObjectReplace(self, type):
        """
        Handles a new object being chosen to replace the selected objects
        """
        items = self.scene.selectedItems()
        type_obj = ObjectItem
        tileset = CurrentPaintType
        changed = False

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
        global CurrentSprite
        CurrentSprite = type
        if type != 1000 and type >= 0:
            self.defaultDataEditor.setSprite(type)
            self.defaultDataEditor.data = b'\0\0\0\0\0\0\0\0\0\0\0\0'
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
                x.spritedata = self.defaultDataEditor.data # change this first or else images get messed up
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
        cat = SpriteCategories[type]
        self.sprPicker.SwitchView(cat)

        isSearch = (type == len(SpriteCategories) - 1)
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

    def HandleProgressPathPosChange(self, obj, oldx, oldy, x, y):
        """
        Handle the progress path being dragged
        """
        if oldx == x and oldy == y: return
        obj.updatePos()
        obj.progpathinfo['peline'].nodePosChanged()
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
        #item = self.entranceList.item(row)
        ent = None
        for check in Area.entrances:
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
        for check in Area.entrances:
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
        #item = self.locationList.item(row)
        loc = None
        for check in Area.locations:
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
        for check in Area.locations:
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
        #item = self.spriteList.item(row)
        spr = None
        for check in Area.sprites:
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
        for check in Area.sprites:
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
        #if self.UpdateFlag: return

        #can't really think of any other way to do this
        #item = self.pathlist.item(row)
        path = None
        for check in Area.paths:
           if check.listitem == item:
                path = check
                break
        if path is None: return

        path.ensureVisible(QtCore.QRectF(), 192, 192)
        self.scene.clearSelection()
        path.setSelected(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandleProgressPathSelectByList(self, item):
        """
        Handle a progress path node being selected
        """
        #if self.UpdateFlag: return

        #can't really think of any other way to do this
        #item = self.progPathlist.item(row)
        progpath = None
        for check in Area.progpaths:
           if check.listitem == item:
                progpath = check
                break
        if progpath is None: return

        progpath.ensureVisible(QtCore.QRectF(), 192, 192)
        self.scene.clearSelection()
        progpath.setSelected(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandlePathToolTipAboutToShow(self, item):
        """
        Handle a path node being hovered in the list
        """
        path = None
        for check in Area.paths:
           if check.listitem == item:
                path = check
                break
        if path is None: return

        path.UpdateListItem(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandleProgressPathToolTipAboutToShow(self, item):
        """
        Handle a progress path node being hovered in the list
        """
        progpath = None
        for check in Area.progpaths:
           if check.listitem == item:
                progpath = check
                break
        if progpath is None: return

        progpath.UpdateListItem(True)

    @QtCore.pyqtSlot(QtWidgets.QListWidgetItem)
    def HandleCommentSelectByList(self, item):
        """
        Handle a comment being selected
        """
        comment = None
        for check in Area.comments:
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
        for check in Area.comments:
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
        elif self.progPathEditorDock.isVisible():
            self.progPathEditor.setProgPath(self.selObj)
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
        type_ppeline = ProgressPathEditorLineItem
        for item in hovereditems:
            hover = item.hover if hasattr(item, 'hover') else True
            if (not isinstance(item, type_zone)) and (not isinstance(item, type_peline)) and(not isinstance(item, type_ppeline)) and hover:
                hovered = item
                break

        if hovered is not None:
            if isinstance(hovered, ObjectItem): # Object
                info = trans.string('Statusbar', 23, '[width]', hovered.width, '[height]', hovered.height, '[xpos]', hovered.objx, '[ypos]', hovered.objy, '[layer]', hovered.layer, '[type]', hovered.type, '[tileset]', hovered.tileset+1)
            elif isinstance(hovered, SpriteItem): # Sprite
                info = trans.string('Statusbar', 24, '[name]', hovered.name, '[xpos]', hovered.objx, '[ypos]', hovered.objy)
            elif isinstance(hovered, SLib.AuxiliaryItem): # Sprite (auxiliary thing) (treat it like the actual sprite)
                info = trans.string('Statusbar', 24, '[name]', hovered.parentItem().name, '[xpos]', hovered.parentItem().objx, '[ypos]', hovered.parentItem().objy)
            elif isinstance(hovered, EntranceItem): # Entrance
                info = trans.string('Statusbar', 25, '[name]', hovered.name, '[xpos]', hovered.objx, '[ypos]', hovered.objy, '[dest]', hovered.destination)
            elif isinstance(hovered, LocationItem): # Location
                info = trans.string('Statusbar', 26, '[id]', int(hovered.id), '[xpos]', int(hovered.objx), '[ypos]', int(hovered.objy), '[width]', int(hovered.width), '[height]', int(hovered.height))
            elif isinstance(hovered, PathItem): # Path
                info = trans.string('Statusbar', 27, '[path]', hovered.pathid, '[node]', hovered.nodeid, '[xpos]', hovered.objx, '[ypos]', hovered.objy)
            elif isinstance(hovered, ProgressPathItem): # Progress Path
                if not hovered.progpathinfo['altpath']:
                    info = trans.string('Statusbar', 38, '[path]', hovered.progpathid, '[node]', hovered.nodeid, '[xpos]', hovered.objx, '[ypos]', hovered.objy)
                else:
                    info = trans.string('Statusbar', 39, '[path]', hovered.progpathid, '[node]', hovered.nodeid, '[xpos]', hovered.objx, '[ypos]', hovered.objy)
            elif isinstance(hovered, CommentItem): # Comment
                info = trans.string('Statusbar', 33, '[xpos]', hovered.objx, '[ypos]', hovered.objy, '[text]', hovered.OneLineText())

        self.posLabel.setText(trans.string('Statusbar', 28, '[objx]', int(x/24), '[objy]', int(y/24), '[sprx]', int(x/1.5), '[spry]', int(y/1.5)))
        self.hoverLabel.setText(info)


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
        dlg = AreaOptionsDialog(setting('TilesetTab') != 'Old')
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            SetDirty()
            Area.timeLimit = dlg.LoadingTab.timer.value() - 200
            Area.startEntrance = dlg.LoadingTab.entrance.value()
            #Area.unk1 = dlg.LoadingTab.unk1.value()
            Area.unk2 = dlg.LoadingTab.unk2.value()
            Area.unk3 = dlg.LoadingTab.unk3.value()

            if dlg.LoadingTab.wrap.isChecked():
                Area.wrapFlag |= 1
            else:
                Area.wrapFlag &= ~1

            tileset0tmp = Area.tileset0
            tileset1tmp = Area.tileset1
            tileset2tmp = Area.tileset2
            tileset3tmp = Area.tileset3

            oldnames = [Area.tileset0, Area.tileset1, Area.tileset2, Area.tileset3]
            assignments = ['Area.tileset0', 'Area.tileset1', 'Area.tileset2', 'Area.tileset3']
            newnames = dlg.TilesetsTab.values()

            toUnload = []

            for idx, oldname, assignment, fname in zip(range(4), oldnames, assignments, newnames):

                if fname in ('', None):
                    toUnload.append(idx)
                    continue
                elif fname.startswith(trans.string('AreaDlg', 16)):
                    fname = fname[len(trans.string('AreaDlg', 17, '[name]', '')):]
                    if fname == '': continue

                exec (assignment + ' = fname')
                LoadTileset(idx, fname)

            for idx in toUnload:
                exec ('Area.tileset%d = \'\'' % idx)
                UnloadTileset(idx)

            mainWindow.objPicker.LoadFromTilesets()
            self.objAllTab.setCurrentIndex(0)
            self.objAllTab.setTabEnabled(0, (Area.tileset0 != ''))
            self.objAllTab.setTabEnabled(1, (Area.tileset1 != ''))
            self.objAllTab.setTabEnabled(2, (Area.tileset2 != ''))
            self.objAllTab.setTabEnabled(3, (Area.tileset3 != ''))

            for layer in Area.layers:
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

            Area.zones = []

            for tab in dlg.zoneTabs:
                z = tab.zoneObj
                z.id = i
                z.UpdateTitle()
                Area.zones.append(z)
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
                z.setPos(z.objx*1.5, z.objy*1.5)

                z.modeldark = tab.Zone_modeldark.currentIndex()
                z.terraindark = tab.Zone_terraindark.currentIndex()

                if tab.Zone_xtrack.isChecked():
                    if tab.Zone_ytrack.isChecked():
                        if tab.Zone_camerabias.isChecked():
                            #Xtrack, YTrack, Bias
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.cammode = 0
                                z.camzoom = 8
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 62))
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.cammode = 3
                                z.camzoom = 9
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 63))
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
                            #Xtrack, YTrack, No Bias
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
                            #Xtrack, No YTrack, Bias
                            z.cammode = 6
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.camzoom = 8
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 62))
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.camzoom = 1
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 63))
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
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 65))
                        else:
                            #Xtrack, No YTrack, No Bias
                            z.cammode = 6
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.camzoom = 8
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.camzoom = 0
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 64))
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
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 65))
                else:
                    if tab.Zone_ytrack.isChecked():
                        if tab.Zone_camerabias.isChecked():
                            #No Xtrack, YTrack, Bias
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.cammode = 1
                                z.camzoom = 8
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 62))
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.cammode = 4
                                z.camzoom = 9
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 63))
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
                            #No Xtrack, YTrack, No Bias
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
                            #No Xtrack, No YTrack, Bias (glitchy)
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.cammode = 9
                                z.camzoom = 8
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 66))
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.cammode = 9
                                z.camzoom = 20
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 66))
                            elif tab.Zone_camerazoom.currentIndex() == 2:
                                z.cammode = 9
                                z.camzoom = 13
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 66))
                            elif tab.Zone_camerazoom.currentIndex() == 3:
                                z.cammode = 9
                                z.camzoom = 12
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 66))
                            elif tab.Zone_camerazoom.currentIndex() == 4:
                                z.cammode = 9
                                z.camzoom = 14
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 66))
                            elif tab.Zone_camerazoom.currentIndex() == 5:
                                z.cammode = 9
                                z.camzoom = 15
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 66))
                            elif tab.Zone_camerazoom.currentIndex() == 6:
                                z.cammode = 9
                                z.camzoom = 16
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 66))
                        else:
                            #No Xtrack, No YTrack, No Bias (glitchy)
                            if tab.Zone_camerazoom.currentIndex() == 0:
                                z.cammode = 9
                                z.camzoom = 8
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 67))
                            elif tab.Zone_camerazoom.currentIndex() == 1:
                                z.cammode = 9
                                z.camzoom = 19
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 67))
                            elif tab.Zone_camerazoom.currentIndex() == 2:
                                z.cammode = 9
                                z.camzoom = 13
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 67))
                            elif tab.Zone_camerazoom.currentIndex() == 3:
                                z.cammode = 9
                                z.camzoom = 12
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 67))
                            elif tab.Zone_camerazoom.currentIndex() == 4:
                                z.cammode = 9
                                z.camzoom = 14
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 67))
                            elif tab.Zone_camerazoom.currentIndex() == 5:
                                z.cammode = 9
                                z.camzoom = 15
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 67))
                            elif tab.Zone_camerazoom.currentIndex() == 6:
                                z.cammode = 9
                                z.camzoom = 16
                                QtWidgets.QMessageBox.warning(None, trans.string('ZonesDlg', 61), trans.string('ZonesDlg', 67))


                if tab.Zone_vnormal.isChecked():
                    z.visibility = 0
                    z.visibility = z.visibility + tab.Zone_visibility.currentIndex()
                if tab.Zone_vspotlight.isChecked():
                    z.visibility = 16
                    z.visibility = z.visibility + tab.Zone_visibility.currentIndex()
                if tab.Zone_vfulldark.isChecked():
                    z.visibility = 32
                    z.visibility = z.visibility + tab.Zone_visibility.currentIndex()

                val = tab.Zone_directionmode.currentIndex()*2
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
            i = 0
            for z in Area.zones:
                tab = dlg.BGTabs[i]

                z.XpositionA = tab.xposA.value()
                z.YpositionA = -tab.yposA.value()
                z.XscrollA = tab.xscrollA.currentIndex()
                z.YscrollA = tab.yscrollA.currentIndex()

                z.ZoomA = tab.zoomA.currentIndex()

                z.bg1A = tab.hex1A.value()
                z.bg2A = tab.hex2A.value()
                z.bg3A = tab.hex3A.value()


                z.XpositionB = tab.xposB.value()
                z.YpositionB = -tab.yposB.value()
                z.XscrollB = tab.xscrollB.currentIndex()
                z.YscrollB = tab.yscrollB.currentIndex()

                z.ZoomB = tab.zoomB.currentIndex()

                z.bg1B = tab.hex1B.value()
                z.bg2B = tab.hex2B.value()
                z.bg3B = tab.hex3B.value()

                i = i + 1

    @QtCore.pyqtSlot()
    def HandleScreenshot(self):
        """
        Takes a screenshot of the entire level and saves it
        """

        dlg = ScreenCapChoiceDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            fn = QtWidgets.QFileDialog.getSaveFileName(mainWindow, trans.string('FileDlgs', 3), '/untitled.png', trans.string('FileDlgs', 4) + ' (*.png)')[0]
            if fn == '': return
            fn = str(fn)

            if dlg.zoneCombo.currentIndex() == 0:
                ScreenshotImage = QtGui.QImage(mainWindow.view.width(), mainWindow.view.height(), QtGui.QImage.Format_ARGB32)
                ScreenshotImage.fill(Qt.transparent)

                RenderPainter = QtGui.QPainter(ScreenshotImage)
                mainWindow.view.render(RenderPainter, QtCore.QRectF(0,0,mainWindow.view.width(),  mainWindow.view.height()), QtCore.QRect(QtCore.QPoint(0,0), QtCore.QSize(mainWindow.view.width(),  mainWindow.view.height())))
                RenderPainter.end()
            elif dlg.zoneCombo.currentIndex() == 1:
                maxX = maxY = 0
                minX = minY = 0x0ddba11
                for z in Area.zones:
                    if maxX < ((z.objx*1.5) + (z.width*1.5)):
                        maxX = ((z.objx*1.5) + (z.width*1.5))
                    if maxY < ((z.objy*1.5) + (z.height*1.5)):
                        maxY = ((z.objy*1.5) + (z.height*1.5))
                    if minX > z.objx*1.5:
                        minX = z.objx*1.5
                    if minY > z.objy*1.5:
                        minY = z.objy*1.5
                maxX = (1024*24 if 1024*24 < maxX+40 else maxX+40)
                maxY = (512*24 if 512*24 < maxY+40 else maxY+40)
                minX = (0 if 40 > minX else minX-40)
                minY = (40 if 40 > minY else minY-40)

                ScreenshotImage = QtGui.QImage(int(maxX - minX), int(maxY - minY), QtGui.QImage.Format_ARGB32)
                ScreenshotImage.fill(Qt.transparent)

                RenderPainter = QtGui.QPainter(ScreenshotImage)
                mainWindow.scene.render(RenderPainter, QtCore.QRectF(0,0,int(maxX - minX) ,int(maxY - minY)), QtCore.QRectF(int(minX), int(minY), int(maxX - minX), int(maxY - minY)))
                RenderPainter.end()


            else:
                i = dlg.zoneCombo.currentIndex() - 2
                ScreenshotImage = QtGui.QImage(Area.zones[i].width*1.5, Area.zones[i].height*1.5, QtGui.QImage.Format_ARGB32)
                ScreenshotImage.fill(Qt.transparent)

                RenderPainter = QtGui.QPainter(ScreenshotImage)
                mainWindow.scene.render(RenderPainter, QtCore.QRectF(0,0,Area.zones[i].width*1.5, Area.zones[i].height*1.5), QtCore.QRectF(int(Area.zones[i].objx)*1.5, int(Area.zones[i].objy)*1.5, Area.zones[i].width*1.5, Area.zones[i].height*1.5))
                RenderPainter.end()

            ScreenshotImage.save(fn, 'PNG', 50)

    def HandleDiagnostics(self):
        """
        Checks the level for any obvious problems and provides options to autofix them
        """
        dlg = DiagnosticToolDialog()
        dlg.exec_()


def main():
    """
    Main startup function for Reggie
    """

    global app, mainWindow, settings, ReggieVersion

    # create an application
    app = QtWidgets.QApplication(sys.argv)

    # load the settings
    settings = QtCore.QSettings('Reggie', ReggieVersion)

    # load the translation (needs to happen first)
    LoadTranslation()

    # load the style
    GetDefaultStyle()

    # go to the script path
    path = module_path()
    if path is not None:
        os.chdir(module_path())

    # check if required files are missing
    if FilesAreMissing():
        sys.exit(1)

    # load required stuff
    global UseRibbon
    global Sprites
    global SpriteListData
    Sprites = None
    SpriteListData = None
    LoadGameDef()
    LoadTheme()
    LoadActionsLists()
    GetUseRibbon()
    LoadConstantLists()
    SetAppStyle()
    LoadTilesetNames()
    LoadObjDescriptions()
    LoadBgANames()
    LoadBgBNames()
    LoadSpriteData()
    LoadSpriteListData()
    LoadEntranceNames()
    LoadNumberFont()
    LoadOverrides()
    SLib.OutlineColor = theme.color('smi')
    SLib.main()

    # load the splashscreen
    app.splashscrn = None
    if checkSplashEnabled():
        loadSplash()

    global EnableAlpha, GridType, CollisionsShown, DepthShown, RealViewEnabled
    global ObjectsFrozen, SpritesFrozen, EntrancesFrozen, LocationsFrozen, PathsFrozen, ProgressPathsFrozen, CommentsFrozen
    global SpritesShown, SpriteImagesShown, LocationsShown, CommentsShown

    gt = setting('GridType')
    if gt == 'checker': GridType = 'checker'
    elif gt == 'grid': GridType = 'grid'
    else: GridType = None
    CollisionsShown = setting('ShowCollisions', False)
    DepthShown = setting('ShowDepth', False)
    RealViewEnabled = setting('RealViewEnabled', False)
    ObjectsFrozen = setting('FreezeObjects', False)
    SpritesFrozen = setting('FreezeSprites', False)
    EntrancesFrozen = setting('FreezeEntrances', False)
    LocationsFrozen = setting('FreezeLocations', False)
    PathsFrozen = setting('FreezePaths', False)
    ProgressPathsFrozen = setting('FreezeProgressPaths', False)
    CommentsFrozen = setting('FreezeComments', False)
    SpritesShown = setting('ShowSprites', True)
    SpriteImagesShown = setting('ShowSpriteImages', True)
    LocationsShown = setting('ShowLocations', True)
    CommentsShown = setting('ShowComments', True)
    SLib.RealViewEnabled = RealViewEnabled

    # choose a folder for the game
    # let the user pick a folder without restarting the editor if they fail
    while not isValidGamePath():
        path = QtWidgets.QFileDialog.getExistingDirectory(None, trans.string('ChangeGamePath', 0, '[game]', gamedef.name))
        if path == '':
            sys.exit(0)

        SetGamePath(path)
        if not isValidGamePath():
            QtWidgets.QMessageBox.information(None, trans.string('ChangeGamePath', 1),  trans.string('ChangeGamePath', 3))
        else:
            setSetting('GamePath_NSMB2', path)
            break

    # check to see if we have anything saved
    autofile = setting('AutoSaveFilePath')
    if autofile is not None:
        autofiledata = setting('AutoSaveFileData', 'x')
        result = AutoSavedInfoDialog(autofile).exec_()
        if result == QtWidgets.QDialog.Accepted:
            global RestoredFromAutoSave, AutoSavePath, AutoSaveData
            RestoredFromAutoSave = True
            AutoSavePath = autofile
            AutoSaveData = bytes(autofiledata, 'latin-1')
        else:
            setSetting('AutoSaveFilePath', 'none')
            setSetting('AutoSaveFileData', 'x')

    # create and show the main window
    mainWindow = ReggieWindow()
    mainWindow.__init2__() # fixes bugs
    mainWindow.show()
    exitcodesys = app.exec_()
    app.deleteLater()
    sys.exit(exitcodesys)

generateStringsXML = False
if '-generatestringsxml' in sys.argv:
    generateStringsXML = True

if __name__ == '__main__': main()
