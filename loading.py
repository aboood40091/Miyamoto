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

from gamedefs import *
import globals
from misc import *
from strings import *
from tileset import *
from ui import *


def LoadTheme():
    """
    Loads the theme
    """
    id = setting('Theme')
    if id is None: id = 'Classic'
    print('THEME ID: ' + str(id))

    if id != 'Classic':
        globals.theme = MiyamotoTheme(id)

    else:
        globals.theme = MiyamotoTheme()


def LoadLevelNames():
    """
    Ensures that the level name info is loaded
    """
    # Parse the file
    tree = etree.parse(GetPath('levelnames'))
    root = tree.getroot()

    # Parse the nodes (root acts like a large category)
    globals.LevelNames = LoadLevelNames_Category(root)


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


def LoadTilesetNames(reload_=False):
    """
    Ensures that the tileset name info is loaded
    """
    if (globals.TilesetNames is not None) and (not reload_): return

    # Get paths
    paths = globals.gamedef.recursiveFiles('tilesets')
    new = [globals.trans.files['tilesets']]
    for path in paths: new.append(path)
    paths = new

    # Read each file
    globals.TilesetNames = [[[], False], [[], False], [[], False], [[], False]]
    for path in paths:
        tree = etree.parse(path)
        root = tree.getroot()

        # Go through each slot
        for node in root:
            if node.tag.lower() != 'slot': continue
            try:
                slot = int(node.attrib['num'])
            except ValueError:
                continue
            if slot > 3: continue

            # Parse the category data into a list
            newlist = [LoadTilesetNames_Category(node), ]
            if 'sorted' in node.attrib:
                newlist.append(node.attrib['sorted'].lower() == 'true')
            else:
                newlist.append(globals.TilesetNames[slot][1])  # inherit

            # Apply it as a patch over the current entry
            newlist[0] = CascadeTilesetNames_Category(globals.TilesetNames[slot][0], newlist[0])

            # Sort it
            if not newlist[1]:
                newlist[0] = SortTilesetNames_Category(newlist[0])

            globals.TilesetNames[slot] = newlist


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
            if 'sorted' in child.attrib:
                new.append(str(child.attrib['sorted'].lower()) == 'true')
            else:
                new.append(False)
            cat.append(new)
        elif child.tag.lower() == 'tileset':
            cat.append((str(child.attrib['filename']), str(child.attrib['name'])))
    return list(cat)


def LoadObjDescriptions(reload_=False):
    """
    Ensures that the object description is loaded
    """
    if (globals.ObjDesc is not None) and not reload_: return

    paths, isPatch = globals.gamedef.recursiveFiles('ts1_descriptions', True)
    if isPatch:
        new = []
        new.append(globals.trans.files['ts1_descriptions'])
        for path in paths: new.append(path)
        paths = new

    globals.ObjDesc = {}
    for path in paths:
        f = open(path)
        raw = [x.strip() for x in f.readlines()]
        f.close()

        for line in raw:
            w = line.split('=')
            globals.ObjDesc[int(w[0])] = w[1]


def LoadSpriteData():
    """
    Ensures that the sprite data info is loaded
    """
    globals.Sprites = [None] * 724
    errors = []
    errortext = []

    # It works this way so that it can overwrite settings based on order of precedence
    paths = [(globals.trans.files['spritedata'], None)]
    for pathtuple in globals.gamedef.multipleRecursiveFiles('spritedata', 'spritenames'): paths.append(pathtuple)

    for sdpath, snpath in paths:

        # Add XML sprite data, if there is any
        if sdpath not in (None, ''):
            path = sdpath if isinstance(sdpath, str) else sdpath.path
            tree = etree.parse(path)
            root = tree.getroot()

            for sprite in root:
                if sprite.tag.lower() != 'sprite': continue

                try:
                    spriteid = int(sprite.attrib['id'])
                except ValueError:
                    continue
                spritename = sprite.attrib['name']
                notes = None
                relatedObjFiles = None

                if 'notes' in sprite.attrib:
                    notes = globals.trans.string('SpriteDataEditor', 2, '[notes]', sprite.attrib['notes'])

                if 'files' in sprite.attrib:
                    relatedObjFiles = globals.trans.string('SpriteDataEditor', 8, '[list]',
                                                   sprite.attrib['files'].replace(';', '<br>'))

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

                globals.Sprites[spriteid] = sdef

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
                globals.Sprites[int(spriteid)].name = name

    # Warn the user if errors occurred
    if len(errors) > 0:
        QtWidgets.QMessageBox.warning(None, globals.trans.string('Err_BrokenSpriteData', 0),
                                      globals.trans.string('Err_BrokenSpriteData', 1, '[sprites]', ', '.join(errors)),
                                      QtWidgets.QMessageBox.Ok)
        QtWidgets.QMessageBox.warning(None, globals.trans.string('Err_BrokenSpriteData', 2), repr(errortext))


def LoadSpriteCategories(reload_=False):
    """
    Ensures that the sprite category info is loaded
    """
    if (globals.SpriteCategories is not None) and not reload_: return

    paths, isPatch = globals.gamedef.recursiveFiles('spritecategories', True)
    if isPatch:
        new = []
        new.append(globals.trans.files['spritecategories'])
        for path in paths: new.append(path)
        paths = new

    globals.SpriteCategories = []
    for path in paths:
        tree = etree.parse(path)
        root = tree.getroot()

        CurrentView = None
        for view in root:
            if view.tag.lower() != 'view': continue

            viewname = view.attrib['name']

            # See if it's in there already
            CurrentView = []
            for potentialview in globals.SpriteCategories:
                if potentialview[0] == viewname: CurrentView = potentialview[1]
            if CurrentView == []: globals.SpriteCategories.append((viewname, CurrentView, []))

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
                        for i in range(int(x[0]), int(x[1]) + 1):
                            if i not in CurrentCategory:
                                CurrentCategory.append(i)

    # Add a Search category
    globals.SpriteCategories.append((globals.trans.string('Sprites', 19), [(globals.trans.string('Sprites', 16), list(range(0, 724)))], []))
    globals.SpriteCategories[-1][1][0][1].append(9999)  # 'no results' special case


def LoadSpriteListData(reload_=False):
    """
    Ensures that the sprite list modifier data is loaded
    """
    if (globals.SpriteListData is not None) and not reload_: return

    paths = globals.gamedef.recursiveFiles('spritelistdata')
    new = []
    new.append('miyamotodata/spritelistdata.txt')
    for path in paths: new.append(path)
    paths = new

    globals.SpriteListData = []
    for i in range(24): globals.SpriteListData.append([])
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
                try:
                    newitem = int(item)
                except ValueError:
                    continue
                if newitem in globals.SpriteListData[lineidx]: continue
                globals.SpriteListData[lineidx].append(newitem)
            globals.SpriteListData[lineidx].sort()


def LoadEntranceNames(reload_=False):
    """
    Ensures that the entrance names are loaded
    """
    if (globals.EntranceTypeNames is not None) and not reload_: return

    paths, isPatch = globals.gamedef.recursiveFiles('entrancetypes', True)
    if isPatch:
        new = [globals.trans.files['entrancetypes']]
        for path in paths: new.append(path)
        paths = new

    NameList = {}
    for path in paths:
        getit = open(path, 'r')
        newNames = {}
        for line in getit.readlines(): newNames[int(line.split(':')[0])] = line.split(':')[1].replace('\n', '')
        for idx in newNames: NameList[idx] = newNames[idx]

    globals.EntranceTypeNames = []
    idx = 0
    while idx in NameList:
        globals.EntranceTypeNames.append(globals.trans.string('EntranceDataEditor', 28, '[id]', idx, '[name]', NameList[idx]))
        idx += 1


def LoadTileset(idx, name, reload=False):
    try:
        import tileset
        ans = tileset._LoadTileset(idx, name, reload)
        del tileset

        return ans

    except:
        return False


def LoadOverrides():
    """
    Load overrides
    """
    OverrideBitmap = QtGui.QPixmap('miyamotodata/overrides.png')
    globals.Overrides = [None] * 256
    idx = 0
    xcount = OverrideBitmap.width() // globals.TileWidth
    ycount = OverrideBitmap.height() // globals.TileWidth
    sourcex = 0
    sourcey = 0

    for y in range(ycount):
        for x in range(xcount):
            bmp = OverrideBitmap.copy(sourcex, sourcey, globals.TileWidth, globals.TileWidth)
            globals.Overrides[idx] = TilesetTile(bmp)

            # Set collisions if it's a brick or question
            if y in [1, 2]:
                if x < 11 or x == 14: globals.Overrides[idx].setQuestionCollisions()
                elif x < 12: globals.Overrides[idx].setBrickCollisions()

            idx += 1
            sourcex += globals.TileWidth
        sourcex = 0
        sourcey += globals.TileWidth
        if idx % 16 != 0:
            idx -= (idx % 16)
            idx += 16

    # ? Block for Sprite 59
    bmp = OverrideBitmap.copy(44 * globals.TileWidth, 2 * globals.TileWidth, globals.TileWidth, globals.TileWidth)
    globals.Overrides[160] = TilesetTile(bmp)


def LoadTranslation():
    """
    Loads the translation
    """
    name = setting('Translation')
    eng = (None, 'None', 'English', '', 0)
    if name in eng:
        globals.trans = MiyamotoTranslation(None)
    else:
        globals.trans = MiyamotoTranslation(name)

    if globals.generateStringsXML: trans.generateXML()


def LoadGameDef(name=None, dlg=None):
    """
    Loads a game definition
    """
    # Put the whole thing into a try-except clause
    # to catch whatever errors may happen
    try:

        # Load the gamedef
        globals.gamedef = MiyamotoGameDefinition(name)
        if globals.gamedef.custom and (not settings.contains('GamePath_' + globals.gamedef.name)):
            # First-time usage of this gamedef. Have the
            # user pick a stage folder so we can load stages
            # and tilesets from there
            QtWidgets.QMessageBox.information(None, globals.trans.string('Gamedefs', 2),
                                              globals.trans.string('Gamedefs', 3, '[game]', globals.gamedef.name),
                                              QtWidgets.QMessageBox.Ok)
            result = globals.mainWindow.HandleChangeGamePath(True)
            if result is not True:
                QtWidgets.QMessageBox.information(None, globals.trans.string('Gamedefs', 4),
                                                  globals.trans.string('Gamedefs', 5, '[game]', globals.gamedef.name),
                                                  QtWidgets.QMessageBox.Ok)
            else:
                QtWidgets.QMessageBox.information(None, globals.trans.string('Gamedefs', 6),
                                                  globals.trans.string('Gamedefs', 7, '[game]', globals.gamedef.name),
                                                  QtWidgets.QMessageBox.Ok)

        # Load spritedata.xml and spritecategories.xml
        LoadSpriteData()
        LoadSpriteListData(True)
        LoadSpriteCategories(True)
        if globals.mainWindow:
            globals.mainWindow.spriteViewPicker.clear()
            for cat in globals.SpriteCategories:
                globals.mainWindow.spriteViewPicker.addItem(cat[0])
            globals.mainWindow.sprPicker.LoadItems()  # Reloads the sprite picker list items
            globals.mainWindow.spriteViewPicker.setCurrentIndex(0)  # Sets the sprite picker to category 0 (enemies)
            globals.mainWindow.spriteDataEditor.setSprite(globals.mainWindow.spriteDataEditor.spritetype,
                                                  True)  # Reloads the sprite data editor fields
            globals.mainWindow.spriteDataEditor.update()

        # Reload tilesets
        LoadObjDescriptions(True)  # reloads ts1_descriptions
        LoadTilesetNames(True)  # reloads tileset names

        # Load sprites.py
        if globals.Area is not None:
            SLib.SpritesFolders = globals.gamedef.recursiveFiles('sprites', False, True)

            SLib.ImageCache.clear()
            SLib.SpriteImagesLoaded.clear()
            SLib.loadVines()

            spriteClasses = globals.gamedef.getImageClasses()

            for s in globals.Area.sprites:
                if s.type in SLib.SpriteImagesLoaded: continue
                if s.type not in spriteClasses: continue

                spriteClasses[s.type].loadImages()

                SLib.SpriteImagesLoaded.add(s.type)

            for s in globals.Area.sprites:
                if s.type in spriteClasses:
                    s.setImageObj(spriteClasses[s.type])
                else:
                    s.setImageObj(SLib.SpriteImage)

        # Reload the sprite-picker text
        if globals.Area is not None:
            for spr in globals.Area.sprites:
                spr.UpdateListItem()  # Reloads the sprite-picker text

        # Load entrance names
        LoadEntranceNames(True)

    except Exception as e:
        raise
    #    # Something went wrong.
    #    QtWidgets.QMessageBox.information(None, globals.trans.string('Gamedefs', 17), globals.trans.string('Gamedefs', 18, '[error]', str(e)))
    #    if name is not None: LoadGameDef(None)
    #    return False


    # Success!
    return True


def LoadActionsLists():
    # Define the menu items, their default settings and their globals.mainWindow.actions keys
    # These are used both in the Preferences Dialog and when init'ing the toolbar.
    globals.FileActions = (
        (globals.trans.string('MenuItems', 0), True, 'newlevel'),
        (globals.trans.string('MenuItems', 2), True, 'openfromname'),
        (globals.trans.string('MenuItems', 4), False, 'openfromfile'),
        (globals.trans.string('MenuItems', 8), True, 'save'),
        (globals.trans.string('MenuItems', 10), False, 'saveas'),
        (globals.trans.string('MenuItems', 12), False, 'metainfo'),
        (globals.trans.string('MenuItems', 14), True, 'screenshot'),
        (globals.trans.string('MenuItems', 16), False, 'changegamepath'),
        (globals.trans.string('MenuItems', 132), False, 'changeobjpath'),
        # (globals.trans.string('MenuItems', 16), False, 'changesavepath'),
        (globals.trans.string('MenuItems', 18), False, 'preferences'),
        (globals.trans.string('MenuItems', 20), False, 'exit'),
    )
    globals.EditActions = (
        (globals.trans.string('MenuItems', 22), False, 'selectall'),
        (globals.trans.string('MenuItems', 24), False, 'deselect'),
        (globals.trans.string('MenuItems', 26), True, 'cut'),
        (globals.trans.string('MenuItems', 28), True, 'copy'),
        (globals.trans.string('MenuItems', 30), True, 'paste'),
        (globals.trans.string('MenuItems', 32), False, 'shiftitems'),
        (globals.trans.string('MenuItems', 34), False, 'mergelocations'),
        (globals.trans.string('MenuItems', 38), False, 'freezeobjects'),
        (globals.trans.string('MenuItems', 40), False, 'freezesprites'),
        (globals.trans.string('MenuItems', 42), False, 'freezeentrances'),
        (globals.trans.string('MenuItems', 44), False, 'freezelocations'),
        (globals.trans.string('MenuItems', 46), False, 'freezepaths'),
    )
    globals.ViewActions = (
        (globals.trans.string('MenuItems', 48), True, 'showlay0'),
        (globals.trans.string('MenuItems', 50), True, 'showlay1'),
        (globals.trans.string('MenuItems', 52), True, 'showlay2'),
        (globals.trans.string('MenuItems', 54), True, 'showsprites'),
        (globals.trans.string('MenuItems', 56), False, 'showspriteimages'),
        (globals.trans.string('MenuItems', 58), True, 'showlocations'),
        (globals.trans.string('MenuItems', 138), True, 'showpaths'),
        (globals.trans.string('MenuItems', 60), True, 'grid'),
        (globals.trans.string('MenuItems', 62), True, 'zoommax'),
        (globals.trans.string('MenuItems', 64), True, 'zoomin'),
        (globals.trans.string('MenuItems', 66), True, 'zoomactual'),
        (globals.trans.string('MenuItems', 68), True, 'zoomout'),
        (globals.trans.string('MenuItems', 70), True, 'zoommin'),
    )
    globals.SettingsActions = (
        (globals.trans.string('MenuItems', 72), True, 'areaoptions'),
        (globals.trans.string('MenuItems', 74), True, 'zones'),
        (globals.trans.string('MenuItems', 76), True, 'backgrounds'),
        (globals.trans.string('MenuItems', 78), False, 'addarea'),
        (globals.trans.string('MenuItems', 80), False, 'importarea'),
        (globals.trans.string('MenuItems', 82), False, 'deletearea'),
        (globals.trans.string('MenuItems', 128), False, 'reloaddata'),
    )
    globals.TileActions = (
        (globals.trans.string('MenuItems', 130), False, 'editslot1'),
    )
    globals.HelpActions = (
        (globals.trans.string('MenuItems', 86), False, 'infobox'),
        (globals.trans.string('MenuItems', 88), False, 'helpbox'),
        (globals.trans.string('MenuItems', 90), False, 'tipbox'),
        (globals.trans.string('MenuItems', 92), False, 'aboutqt'),
    )
