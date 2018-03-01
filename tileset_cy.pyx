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

ctypedef unsigned char u8
ctypedef unsigned int u32


def imagesIdentical_cy(u8[:] firstBytes, u8[:] secondBytes, u32 width, u32 height):
    """
    Compare these images to see if they're the same or not.
    Based on nsmbulib
    """
    height = (height + 3) // 4
    width = (width + 3) // 4

    cdef u32 x, y, pos
    cdef list firstRgba
    cdef list secondRgba
    cdef u8 idx, channelA, channelB

    for y in range(height):
        for x in range(width):
            pos = (y * width + x) * 4

            firstRgba = [
               (firstBytes[pos + 0] + firstBytes[pos + 4] + firstBytes[pos + 0x8] + firstBytes[pos + 0xC] + 3) // 4,
               (firstBytes[pos + 1] + firstBytes[pos + 5] + firstBytes[pos + 0x9] + firstBytes[pos + 0xD] + 3) // 4,
               (firstBytes[pos + 2] + firstBytes[pos + 6] + firstBytes[pos + 0xA] + firstBytes[pos + 0xE] + 3) // 4,
               (firstBytes[pos + 3] + firstBytes[pos + 7] + firstBytes[pos + 0xB] + firstBytes[pos + 0xF] + 3) // 4,
            ]

            secondRgba = [
               (secondBytes[pos + 0] + secondBytes[pos + 4] + secondBytes[pos + 0x8] + secondBytes[pos + 0xC] + 3) // 4,
               (secondBytes[pos + 1] + secondBytes[pos + 5] + secondBytes[pos + 0x9] + secondBytes[pos + 0xD] + 3) // 4,
               (secondBytes[pos + 2] + secondBytes[pos + 6] + secondBytes[pos + 0xA] + secondBytes[pos + 0xE] + 3) // 4,
               (secondBytes[pos + 3] + secondBytes[pos + 7] + secondBytes[pos + 0xB] + secondBytes[pos + 0xF] + 3) // 4,
            ]

            if firstRgba[3] < 2 and secondRgba[3] < 2:
                # Both pixels are transparent
                continue

            for idx, channelA in enumerate(firstRgba):
                channelB = secondRgba[idx]
                if abs(channelA - channelB) > 2:
                    return False

    return True
