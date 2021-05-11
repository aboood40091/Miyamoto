#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! DX Level Editor - New Super Mario Bros. U Deluxe Level Editor
# Copyright (C) 2009-2021 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7, John10v10,
# mrbengtsson

# This file is part of Miyamoto! DX.

# Miyamoto! DX is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Miyamoto! DX is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Miyamoto! DX.  If not, see <http://www.gnu.org/licenses/>.

# build.py
# Builds Miyamoto! DX to a binary
# Use the values below to configure the release:

from globals import MiyamotoVersionFloat

Version = str(MiyamotoVersionFloat)
PackageName = 'miyamotodx_v%s' % Version


################################################################
################################################################

# Imports
import os, os.path, platform, shutil, sys
from cx_Freeze import setup, Executable

# Pick a build directory
dir_ = 'distrib/' + PackageName

# Print some stuff
print('[[ Freezing Miyamoto! DX ]]')
print('>> Destination directory: %s' % dir_)

# Add the "build" parameter to the system argument list
if 'build' not in sys.argv:
    sys.argv.append('build')

# Clear the directory
if os.path.isdir(dir_): shutil.rmtree(dir_)
os.makedirs(dir_)

# exclude QtWebChannel, QtWebSockets and QtNetwork to save space, plus Python stuff we don't use
excludes = ['doctest', 'pdb', 'unittest', 'difflib', 'inspect',
    'os2emxpath', 'posixpath', 'optpath', 'locale', 'calendar',
    'multiprocessing', 'ssl',
    'PyQt5.QtWebChannel', 'PyQt5.QtWebSockets', 'PyQt5.QtNetwork']

# Set it up
base = 'Win32GUI' if sys.platform == 'win32' else None
setup(
    name = 'Miyamoto! DX',
    version = Version,
    description = 'Miyamoto! DX',
    options={
        'build_exe': {
            'excludes': excludes,
            'packages': ['sip', 'encodings', 'encodings.hex_codec', 'encodings.utf_8'],
            'build_exe': dir_,
            'optimize': 2,
            'silent': True,
            },
        },
    executables = [
        Executable(
            'miyamoto.py',
            icon = 'miyamotodata/win_icon.ico',
            base = base,
            ),
        ],
    )
print('>> Built frozen executable!')



# Now that it's built, configure everything


if platform.system() == 'Windows':
    # Remove a useless file we don't need
    try: os.unlink(dir_ + '/w9xpopen.exe')
    except: pass
else: pass

print('>> Attempting to copy required files...')
if os.path.isdir(dir_ + '/miyamotodata'): shutil.rmtree(dir_ + '/miyamotodata') 
shutil.copytree('miyamotodata', dir_ + '/miyamotodata') 
if platform.system() == 'Windows':
    if os.path.isdir(dir_ + '/Tools'): shutil.rmtree(dir_ + '/Tools') 
    shutil.copytree('Tools', dir_ + '/Tools')
elif platform.system() == 'Linux':
    if os.path.isdir(dir_ + '/linuxTools'): shutil.rmtree(dir_ + '/linuxTools') 
    shutil.copytree('linuxTools', dir_ + '/linuxTools')
else:
    if os.path.isdir(dir_ + '/macTools'): shutil.rmtree(dir_ + '/macTools') 
    shutil.copytree('macTools', dir_ + '/macTools')
shutil.copy('license.txt', dir_)
shutil.copy('README.md', dir_)
print('>> Files copied!')

print('>> Miyamoto! DX has been frozen to %s !' % dir_)
