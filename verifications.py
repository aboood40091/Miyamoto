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

############ Imports ############

import os
from PyQt5 import QtWidgets

import globals

#################################


def checkContent(data):
    if not data.startswith(b'SARC'):
        return False

    required = (b'course/', b'course1.bin')
    for r in required:
        if r not in data:
            return False

    return True


def IsNSMBLevel(filename):
    """
    Does some basic checks to confirm a file is a NSMB level
    """
    return True
    if not os.path.isfile(filename): return False

    f = open(filename, 'rb')
    data = f.read()
    f.close()
    del f

    if checkContent(data):
        return True


def SetDirty(noautosave=False):
    if globals.DirtyOverride > 0: return

    if not noautosave: globals.AutoSaveDirty = True
    if globals.Dirty: return

    globals.Dirty = True
    try:
        globals.mainWindow.UpdateTitle()
    except Exception:
        pass


def FilesAreMissing():
    """
    Checks to see if any of the required files for Miyamoto are missing
    """

    if not os.path.isdir('miyamotodata'):
        QtWidgets.QMessageBox.warning(None, globals.trans.string('Err_MissingFiles', 0), globals.trans.string('Err_MissingFiles', 1))
        return True

    required = ['entrances.png', 'entrancetypes.txt', 'icon.png', 'levelnames.xml', 'overrides.png',
                'spritedata.xml', 'tilesets.xml', 'about.png', 'spritecategories.xml']

    missing = []

    for check in required:
        if not os.path.isfile('miyamotodata/' + check):
            missing.append(check)

    if len(missing) > 0:
        QtWidgets.QMessageBox.warning(None, globals.trans.string('Err_MissingFiles', 0),
                                      globals.trans.string('Err_MissingFiles', 2, '[files]', ', '.join(missing)))
        return True

    return False


def isValidGamePath(check='ug'):
    """
    Checks to see if the path for NSMBU contains a valid game
    """
    if check == 'ug': check = globals.gamedef.GetGamePath()

    if check is None or check == '': return False
    if not os.path.isdir(check): return False
    if not (
        os.path.isfile(os.path.join(check, '1-1.szs')) or os.path.isfile(os.path.join(check, '1-1.sarc'))): return False

    return True
