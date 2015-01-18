#!/usr/bin/python
# -*- coding: latin-1 -*-

# Reggie Next - New Super Mario Bros. Wii / New Super Mario Bros 2 Level Editor
# Milestone 2 Alpha 4
# Copyright (C) 2009-2014 Treeki, Tempus, angelsl, JasonP27, Kamek64,
# MalStar1000, RoadrunnerWMC

# This file is part of Reggie Next.

# Reggie Next is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Reggie Next is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Reggie Next.  If not, see <http://www.gnu.org/licenses/>.


# sprites_nsmb2.py
# Contains code to render sprite images from New Super Mario Bros. 2


################################################################
################################################################

# Imports

from PyQt5 import QtCore, QtGui
Qt = QtCore.Qt


import spritelib as SLib
ImageCache = SLib.ImageCache
import sprites_common


################################################################
################################################################


def LoadBasics():
    """
    Loads basic images used in NSMB2
    """
    # Load some coins, because coins are in almost every Mario level ever
    ImageCache['Coin'] = SLib.GetImg('coin.png')
    ImageCache['StarCoin'] = SLib.GetImg('starcoin.png')

    # Load blocks
    BlockImage = SLib.GetImg('blocks.png')
    Blocks = []
    count = BlockImage.width() // 24
    for i in range(count):
        Blocks.append(BlockImage.copy(i * 24, 0, 24, 24))
    ImageCache['Blocks'] = Blocks

    # Load the overrides
    Overrides = QtGui.QPixmap('reggiedata/overrides.png')
    Blocks = []
    x = Overrides.width() // 24
    y = Overrides.height() // 24
    for i in range(y):
        for j in range(x):
            Blocks.append(Overrides.copy(j * 24, i * 24, 24, 24))
    ImageCache['Overrides'] = Blocks

    # Load vines, because these are used by entrances
    SLib.loadIfNotInImageCache('VineTop', 'vine_top.png')
    SLib.loadIfNotInImageCache('VineMid', 'vine_mid.png')
    SLib.loadIfNotInImageCache('VineBtm', 'vine_btm.png')


class SpriteImage_BobOmb(SLib.SpriteImage_Static): # 29
    def __init__(self, parent):
        super().__init__(
            parent,
            1.25,
            ImageCache['BobOmb'],
            (-2, -9),
            )

    @staticmethod
    def loadImages():
        loadIfNotInImageCache('BobOmb', 'bob-omb.png')


class SpriteImage_Coin(SLib.SpriteImage_Static): # 55
    def __init__(self, parent):
        super().__init__(
            parent,
            1.25,
            ImageCache['Coin'],
            )


class SpriteImage_FireballPipeJunction(SLib.SpriteImage_Static): # 81
    def __init__(self, parent):
        super().__init__(
            parent,
            1.25,
            ImageCache['FireballPipeJunction'],
            )

    @staticmethod
    def loadImages():
        loadIfNotInImageCache('FireballPipeJunction', 'block_fireball_pipe.png')


class SpriteImage_StarCoin(SLib.SpriteImage_Static): # 219
    def __init__(self, parent):
        super().__init__(
            parent,
            1.25,
            ImageCache['StarCoin'],
            )


################################################################
################################################################


ImageClasses = {
    29: SpriteImage_BobOmb,
    55: SpriteImage_Coin,
    81: SpriteImage_FireballPipeJunction,
    219: SpriteImage_StarCoin,
    }