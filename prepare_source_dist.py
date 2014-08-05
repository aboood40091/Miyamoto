#!/usr/bin/python
# -*- coding: latin-1 -*-

# Reggie! - New Super Mario Bros. Wii Level Editor
# Version Next Milestone 2 Alpha 4
# Copyright (C) 2009-2014 Treeki, Tempus, angelsl, JasonP27, Kamek64,
# MalStar1000, RoadrunnerWMC

# This file is part of Reggie!.

# Reggie! is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Reggie! is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Reggie!.  If not, see <http://www.gnu.org/licenses/>.



# prepare_source_dist.py
# Prepares the source distribution of Reggie!

# Use the values below to configure the release:
PackageName = 'reggie_next_m2a4_src'


################################################################
################################################################

# Imports
import os.path, os, shutil

dir_ = 'distrib/' + PackageName

print('[[ Preparing Source Distribution for Reggie! ]]')
print('>> Destination directory: %s' % dir_)

if os.path.isdir(dir_): shutil.rmtree(dir_)
os.makedirs(dir_)

folders = (
    ('reggiedata', dir_ + '/reggiedata'),
    ('reggieextras', dir_ + '/reggieextras'),
    )
files = (
    
    # alphabetical
    ('archive.py', dir_),
    ('common.py', dir_),
    ('LHdec.py', dir_),
    ('LHDecompressor.exe', dir_),
    ('lz77.py', dir_),
    ('prepare_source_dist.py', dir_),
    ('pyqtribbon.py', dir_),
    ('reggie.py', dir_),
    ('sprites.py', dir_),
    ('windows_build.py', dir_),

    ('license.txt', dir_),
    ('readme.txt', dir_),
    
    ('nsmblib-0.5a.tar.gz', dir_),
    ('nsmblib-0.5a.zip', dir_),
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
