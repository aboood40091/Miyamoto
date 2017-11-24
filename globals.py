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

import os, sys

# Globals
generateStringsXML = False
app = None
mainWindow = None
trans = None
settings = None
gamedef = None
theme = None
compressed = False
LevelNames = None
TilesetNames = None
ObjDesc = None
SpriteCategories = None
SpriteListData = None
EntranceTypeNames = None
Tiles = None  # 0x200 tiles per tileset, plus 64 for each type of override
TilesetAnimTimer = None
Overrides = None  # 320 tiles, this is put into Tiles usually
TileBehaviours = None
ObjectDefinitions = None  # 4 tilesets
ObjectAllDefinitions = None
ObjectAllCollisions = None
ObjectAllImages = None
ObjectAddedtoEmbedded = None
TilesetsAnimating = False
Area = None
Dirty = False
DirtyOverride = 0
AutoSaveDirty = False
OverrideSnapping = False
CurrentPaintType = -1
CurrentObject = -1
CurrentSprite = -1
CurrentLayer = 1
CurrentArea = 1
Layer0Shown = True
Layer1Shown = True
Layer2Shown = True
SpritesShown = True
SpriteImagesShown = True
RealViewEnabled = False
LocationsShown = True
CommentsShown = True
PathsShown = True
ObjectsFrozen = False
SpritesFrozen = False
EntrancesFrozen = False
LocationsFrozen = False
PathsFrozen = False
CommentsFrozen = False
OverwriteSprite = False
PaintingEntrance = None
PaintingEntranceListIndex = None
NumberFont = None
GridType = None
RestoredFromAutoSave = False
AutoSavePath = ''
AutoSaveData = b''
AutoOpenScriptEnabled = False
CurrentLevelNameForAutoOpenScript = 'AAAAAAAAAAAAAAAAAAAAAAAAAA'
TileWidth = 60
szsData = {}
levelNameCache = ''
miyamoto_path = os.path.dirname(os.path.realpath(sys.argv[0])).replace("\\", "/")

# Sort BG Names
names_bg = []
names_bgTrans = []

with open(miyamoto_path + '/miyamotodata/bg.txt', 'r') as txt:
    for line in txt.readlines():
        names_bg.append(line.rstrip())
names_bg = tuple(names_bg)

with open(miyamoto_path + '/miyamotodata/bgTrans.txt', 'r') as txt:
    for line in txt.readlines():
        names_bgTrans.append(line.rstrip())
names_bgTrans = tuple(names_bgTrans)

# Game enums
NewSuperMarioBrosU = 0
NewSuperLuigiU = 1
FileExtentions = {
    NewSuperMarioBrosU: ('.szs', '.sarc'),
    NewSuperLuigiU: ('.szs', '.sarc'),
}
FirstLevels = {
    NewSuperMarioBrosU: '1-1',
    NewSuperLuigiU: '1-1',
}
