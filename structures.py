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


from enum import Enum
import globals


class Structures(Enum):
    CourseBlock  = 'II'
    Background   = 'Hhhh16sHxx'
    Sprite       = 'HHHHIIBB2sBxxx'
    Options      = 'IIHHxBBBBxxBHH'
    Entrance     = 'HHhhBBBBBBxBHBBBBBx'
    Boundings    = 'llllHHhhxxxx'
    Zone         = 'HHHHHHBBBBBBBBBBBBBBxx'
    Location     = 'HHHHBxxx'
    LayerObject  = 'HhhHHB'
    Path         = 'BbHHHxxxx'
    PathNode     = 'HHffhHBBBx'
    LoadedSprite = 'Hxx'


def GetFormat(structId):
    assert isinstance(structId, Structures)

    endianness = '<' if globals.IsNSMBUDX else '>'
    formatStr = structId.value

    return endianness + formatStr
