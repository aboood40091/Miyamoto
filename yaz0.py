#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2019 Treeki, Tempus, angelsl, JasonP27, Kinnay,
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

# yaz0.py
# Multiple methods for Yaz0 (de)compression


################################################################
################################################################

import os
import platform
import subprocess

import globals

if globals.cython_available:
    try:
        from libyaz0 import compress
        from libyaz0 import decompress

    except:
        pass

    else:
        globals.libyaz0_available = True


def determineCompressionMethod():
    if globals.libyaz0_available:
        return compressLIBYAZ0, decompressLIBYAZ0

    else:
        return compressWSZST, decompressWSZST


def compressWSZST(inb, outf, level=9):
    """
    Compress the file using WSZST
    """
    inf = os.path.join(globals.miyamoto_path, 'tmp.tmp')
    with open(inf, "wb+") as out:
        out.write(inb)

    if os.path.isfile(outf):
        os.remove(outf)

    if platform.system() == 'Windows':
        os.chdir(globals.miyamoto_path + '/Tools')
        subprocess.call('wszst.exe COMPRESS "' + inf + '" --dest "' + outf + '"', creationflags=0x8)

    elif platform.system() == 'Linux':
        os.chdir(globals.miyamoto_path + '/linuxTools')
        os.system('chmod +x ./wszst_linux.elf')
        os.system('./wszst_linux.elf COMPRESS "' + inf + '" --dest "' + outf + '"')

    else:
        os.chdir(globals.miyamoto_path + '/macTools')
        os.system('"' + globals.miyamoto_path + '/macTools/wszst_mac" COMPRESS "' + inf + '" --dest "' + outf + '"')

    os.chdir(globals.miyamoto_path)

    if not os.path.isfile(outf):
        return False

    return True


def decompressWSZST(inb):
    """
    Deompress the data using WSZST
    """
    inf = os.path.join(globals.miyamoto_path, 'tmp.tmp')
    outf = os.path.join(globals.miyamoto_path, 'tmp2.tmp')

    with open(inf, "wb+") as out:
        out.write(inb)

    if os.path.isfile(outf):
        os.remove(outf)

    if platform.system() == 'Windows':
        os.chdir(globals.miyamoto_path + '/Tools')
        subprocess.call('wszst.exe DECOMPRESS "' + inf + '" --dest "' + outf + '"', creationflags=0x8)

    elif platform.system() == 'Linux':
        os.chdir(globals.miyamoto_path + '/linuxTools')
        os.system('chmod +x ./wszst_linux.elf')
        os.system('./wszst_linux.elf DECOMPRESS "' + inf + '" --dest "' + outf + '"')

    else:
        os.chdir(globals.miyamoto_path + '/macTools')
        os.system('"' + globals.miyamoto_path + '/macTools/wszst_mac" DECOMPRESS "' + inf + '" --dest "' + outf + '"')

    os.remove(inf)
    os.chdir(globals.miyamoto_path)

    if not os.path.isfile(outf):
        return b''

    with open(outf, "rb") as inf_:
        data = inf_.read()

    os.remove(outf)

    return data


def compressLIBYAZ0(inb, outf, level=1):
    """
    Compress the file using libyaz0
    """
    try:
        data = compress(inb, 0, level)

        with open(outf, "wb+") as out:
            out.write(data)

    except:
        return False

    else:
        return True


def decompressLIBYAZ0(inb):
    """
    Decompress the file using libyaz0
    """
    try:
        data = decompress(inb)

    except:
        return False

    else:
        return data
