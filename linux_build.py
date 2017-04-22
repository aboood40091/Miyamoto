#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! Level Editor - New Super Mario Bros. U Level Editor
# Copyright (C) 2009-2017 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop, AboodXD, Gota7

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

# linux_build.py
# Builds Miyamoto! to a Linux binary
# Use the values below to configure the release:

PackageName = 'miyamoto_v10.0'
Version = '1.0.0' # This must be a valid float in string format


################################################################
################################################################

# Imports
import os, os.path, shutil, sys
from cx_Freeze import setup, Executable

# Pick a build directory
dir_ = 'distrib/' + PackageName

# Print some stuff
print('[[ Freezing Miyamoto! NSMBU ]]')
print('>> Destination directory: %s' % dir_)

# Add the "build" parameter to the system argument list
if 'build' not in sys.argv:
    sys.argv.append('build')

# Clear the directory
if os.path.isdir(dir_): shutil.rmtree(dir_)
os.makedirs(dir_)

# exclude QtWebKit to save space, plus Python stuff we don't use
excludes = ['doctest', 'pdb', 'unittest', 'difflib', 'inspect',
    'os2emxpath', 'posixpath', 'optpath', 'locale', 'calendar',
    'select', 'multiprocessing', 'ssl',
    'PyQt5.QtWebKit', 'PyQt5.QtNetwork']

# Set it up
base = None
setup(
    name = 'Miyamoto! NSMBU',
    version = Version,
    description = 'Miyamoto! NSMBU',
    options={
        'build_exe': {
            'excludes': excludes,
            'packages': ['sip', 'encodings', 'encodings.hex_codec', 'encodings.utf_8'],
            'compressed': 1,
            'build_exe': dir_,
            'icon': 'miyamotodata/win_icon.ico',
            },
        },
    executables = [
        Executable(
            'miyamoto_linux.py',
            base = base,
            ),
        ],
    )
print('>> Built frozen executable!')



# Now that it's built, configure everything


print('>> Attempting to copy required files...')
if os.path.isdir(dir_ + '/miyamotodata'): shutil.rmtree(dir_ + '/miyamotodata') 
if os.path.isdir(dir_ + '/miyamotoextras'): shutil.rmtree(dir_ + '/miyamotoextras')
if os.path.isdir(dir_ + '/linuxTools'): shutil.rmtree(dir_ + '/linuxTools') 
shutil.copytree('miyamotodata', dir_ + '/miyamotodata') 
shutil.copytree('miyamotoextras', dir_ + '/miyamotoextras')
shutil.copytree('linuxTools', dir_ + '/linuxTools')
shutil.copy('license.txt', dir_)
shutil.copy('README.md', dir_)
print('>> Files copied!')

print('>> Miyamoto has been frozen to %s !' % dir_)
