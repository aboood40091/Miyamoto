#!/usr/bin/python3
# -*- coding: latin-1 -*-

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

# prepare_source_dist.py
# Prepares the source distribution of Miyamoto!

# Use the values below to configure the release:
PackageName = 'miyamoto_nsmbu_041_alpha_src'


################################################################
################################################################

# Imports
import os.path, os, shutil

dir_ = 'distrib/' + PackageName

print('[[ Preparing Source Distribution for Miyamoto! ]]')
print('>> Destination directory: %s' % dir_)

if os.path.isdir(dir_): shutil.rmtree(dir_)
os.makedirs(dir_)

folders = (
    ('miyamotodata', dir_ + '/miyamotodata'),
    ('miyamotoextras', dir_ + '/miyamotoextras'),
    )
files = (
    
    # alphabetical
    ('common.py', dir_),
    ('lz77.py', dir_),
    ('prepare_source_dist.py', dir_),
    ('pyqtribbon.py', dir_),
    ('miyamoto.py', dir_),
    ('sprites.py', dir_),
    ('windows_build.py', dir_),

    ('license.txt', dir_),
    ('readme.txt', dir_),
    )
errors = []
for folder, folderdir in folders:
    try: shutil.copytree(folder, folderdir)
    except: errors.append(folder)
for file, filedir in files:
    try: shutil.copy(file, filedir)
    except: errors.append(file)

if len(errors) > 0:
    print('>> The following files and/or folders failed to copy:')
    for e in errors: print('    ' + e)
print('>> All done!')
