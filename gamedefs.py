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


################################################################
################################################################

############ Imports ############

import importlib
import os
from PyQt5 import QtWidgets
import sys
from xml.etree import ElementTree as etree

import globals
from misc import setting, setSetting
import sprites

#################################


class MiyamotoGameDefinition:
    """
    A class that defines a NSMBU hack: songs, tilesets, sprites, songs, etc.
    """

    # Gamedef File - has 2 values: name (str) and patch (bool)
    class GameDefinitionFile:
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
        Initializes the MiyamotoGameDefinition
        """
        self.InitAsEmpty()

        # Try to init it from name if possible
        NoneTypes = (None, 'None', 0, '', True, False)
        if name in NoneTypes:
            return
        else:
            try:
                self.InitFromName(name)
            except Exception:
                self.InitAsEmpty()  # revert

    def InitAsEmpty(self):
        """
        Sets all properties to their default values
        """
        gdf = self.GameDefinitionFile

        self.custom = False
        self.base = None  # gamedef to use as a base
        self.gamepath = None
        self.name = globals.trans.string('Gamedefs', 13)  # 'New Super Mario Bros. U'
        self.description = globals.trans.string('Gamedefs', 14)  # 'A new adventure, and in HD!' and the date
        self.version = '1.0'

        self.sprites = sprites

        self.files = {
            'bg': gdf(None, False),
            'bgTrans': gdf(None, False),
            'entrancetypes': gdf(None, False),
            'levelnames': gdf(None, False),
            'music': gdf(None, False),
            'spritecategories': gdf(None, False),
            'spritedata': gdf(None, False),
            'spritelistdata': gdf(None, False),
            'spritenames': gdf(None, False),
            'spriteresources': gdf(None, False),
            'tilesets': gdf(None, False),
            'ts1_descriptions': gdf(None, False),
        }
        self.folders = {
            'bg': gdf(None, False),
            'sprites': gdf(None, False),
        }

    def InitFromName(self, name):
        """
        Attempts to open/load a Game Definition from a name string
        """
        self.custom = True
        name = str(name)
        self.gamepath = name

        # Parse the file (errors are handled by __init__())
        path = 'miyamotodata/patches/' + name + '/main.xml'
        tree = etree.parse(path)
        root = tree.getroot()

        # Add the attributes of root: name, description, base
        if 'name' not in root.attrib: raise Exception
        self.name = root.attrib['name']

        self.description = globals.trans.string('Gamedefs', 15)
        if 'description' in root.attrib: self.description = root.attrib['description'].replace('[', '<').replace(']',
                                                                                                                 '>')
        self.version = None
        if 'version' in root.attrib: self.version = root.attrib['version']

        self.base = None
        if 'base' in root.attrib:
            self.base = FindGameDef(root.attrib['base'], name)
        else:
            self.base = MiyamotoGameDefinition()

        # Parse the nodes
        addpath = 'miyamotodata/patches/' + name + '/'
        for node in root:
            n = node.tag.lower()
            if n in ('file', 'folder'):
                path = addpath + node.attrib['path']

                if 'patch' in node.attrib:
                    patch = node.attrib['patch'].lower() == 'true'  # convert to bool
                else:
                    patch = True  # DEFAULT PATCH VALUE
                if 'game' in node.attrib:
                    if node.attrib['game'] != globals.trans.string('Gamedefs', 13):  # 'New Super Mario Bros. U'
                        def_ = FindGameDef(node.attrib['game'], name)
                        path = os.path.join('miyamotodata', 'patches', def_.gamepath, node.attrib['path'])
                    else:
                        path = os.path.join('miyamotodata', node.attrib['path'])

                ListToAddTo = eval('self.%ss' % n)  # self.files or self.folders
                newdef = self.GameDefinitionFile(path, patch)
                ListToAddTo[node.attrib['name']] = newdef

        # Get rid of the XML stuff
        del tree, root

        # Load sprites.py if provided
        if 'sprites' in self.files:
            file = open(self.files['sprites'].path, 'r')
            filedata = file.read()
            file.close();
            del file

            # https://stackoverflow.com/questions/5362771/load-module-from-string-in-python
            # with modifications
            new_module = importlib.types.ModuleType(self.name + '->sprites')
            exec(filedata, new_module.__dict__)
            sys.modules[new_module.__name__] = new_module
            self.sprites = new_module

    def GetGamePath(self):
        """
        Returns the game path
        """
        if not self.custom: return str(setting('GamePath'))
        name = 'GamePath_' + self.name
        setname = setting(name)

        # Use the default if there are no settings for this yet
        if setname is None:
            return str(setting('GamePath'))
        else:
            return str(setname)

    def SetGamePath(self, path):
        """
        Sets the game path
        """
        if not self.custom:
            setSetting('GamePath', path)
        else:
            name = 'GamePath_' + self.name
            setSetting(name, path)

    def GetGamePaths(self):
        """
        Returns game paths of this gamedef and its bases
        """
        mainpath = str(setting('GamePath'))
        if not self.custom: return [mainpath, ]

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
        if stg is None:
            return setting('LastLevel')
        else:
            return stg

    def SetLastLevel(self, path):
        """
        Sets the last loaded level
        """
        if path in (None, 'None', 'none', True, 'True', 'true', False, 'False', 'false', 0, 1, ''): return
        print('Last loaded level set to ' + str(path))
        if not self.custom:
            setSetting('LastLevel', path)
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
            if ListToCheckIn[name].path is None:  # No base, no file

                if isPatch:
                    return [], True
                else:
                    return []

            else:  # No base, file

                alist = []
                alist.append(ListToCheckIn[name].path)
                if isPatch:
                    return alist, ListToCheckIn[name].patch
                else:
                    return alist

        else:

            if isPatch:
                listUpToNow, wasPatch = self.base.recursiveFiles(name, True, folder)
            else:
                listUpToNow = self.base.recursiveFiles(name, False, folder)

            if ListToCheckIn[name].path is None:  # Base, no file

                if isPatch:
                    return listUpToNow, wasPatch
                else:
                    return listUpToNow

            else:  # Base, file

                # If it's a patch, just add it to the end of the list
                if ListToCheckIn[name].patch:
                    listUpToNow.append(ListToCheckIn[name].path)

                # If it's not (it's free-standing), make a new list and start over
                else:
                    newlist = []
                    newlist.append(ListToCheckIn[name].path)
                    if isPatch:
                        return newlist, False
                    else:
                        return newlist

                # Return
                if isPatch:
                    return listUpToNow, wasPatch
                else:
                    return listUpToNow

    def multipleRecursiveFiles(self, *args):
        """
        Returns multiple recursive files in order of least recent to most recent as a list of tuples, one list per gamedef base
        """

        # This should be very simple
        # Each arg should be a file name
        if self.base is None or self.base.base is None:
            main = []  # start a new level
        else:
            main = self.base.multipleRecursiveFiles(*args)

        # Add the values from this level, and then return it
        result = []
        for name in args:
            try:
                file = self.files[name]
                if file.path is None: raise KeyError
                result.append(self.files[name])
            except KeyError:
                result.append(None)
        main.append(tuple(result))
        return main

    def file(self, name):
        """
        Returns a file by recursively checking successive gamedef bases
        """
        if name not in self.files: return

        if self.files[name].path is not None:
            return self.files[name].path
        else:
            if self.base is None: return
            return self.base.file(name)  # it can recursively check its base, too

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


def GetPath(id_):
    """
    Checks the game definition and the translation and returns the appropriate path
    """
    # If there's a custom gamedef, use that
    if globals.gamedef.custom:
        path = globals.gamedef.file(id_)
        if path is not None:
            return path

    return globals.trans.path(id_)


def getMusic():
    """
    Uses the current gamedef + translation to get the music data, and returns it as a list of tuples
    """

    transsong = globals.trans.files['music']
    gamedefsongs, isPatch = globals.gamedef.recursiveFiles('music', True)
    if isPatch:
        paths = [transsong]
        for path in gamedefsongs: paths.append(path)
    else:
        paths = gamedefsongs

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
    """
    Helper function to find a game def with a specific name.
    Skip will be skipped
    """
    toSearch = [None]  # Add the original game first
    for folder in os.listdir(os.path.join('miyamotodata', 'patches')): toSearch.append(folder)

    for folder in toSearch:
        if folder == skip: continue
        def_ = MiyamotoGameDefinition(folder)
        if (not def_.custom) and (folder is not None): continue
        if def_.name == name: return def_


def getAvailableGameDefs():
    GameDefs = []

    # Add them
    folders = os.listdir(os.path.join('miyamotodata', 'patches'))
    for folder in folders:
        if not os.path.isdir(os.path.join('miyamotodata', 'patches', folder)): continue
        inFolder = os.listdir(os.path.join('miyamotodata', 'patches', folder))
        if 'main.xml' not in inFolder: continue
        def_ = MiyamotoGameDefinition(folder)
        if def_.custom: GameDefs.append((def_, folder))

    # Alphabetize them, and then add the default
    GameDefs = sorted(GameDefs, key=lambda def_: def_[0].name)
    new = [None]
    for item in GameDefs: new.append(item[1])
    return new


def loadNewGameDef(def_):
    """
    Loads MiyamotoGameDefinition def_, and displays a progress dialog
    """
    dlg = QtWidgets.QProgressDialog()
    dlg.setAutoClose(True)
    btn = QtWidgets.QPushButton('Cancel')
    btn.setEnabled(False)
    dlg.setCancelButton(btn)
    dlg.show()
    dlg.setValue(0)

    import loading
    loading.LoadGameDef(def_, dlg)
    del loading

    dlg.setValue(100)
    del dlg
