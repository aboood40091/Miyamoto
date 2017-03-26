#!/usr/bin/python
# -*- coding: latin-1 -*-

# Miyamoto! Next - New Super Mario Bros. U Level Editor
# Version v0.6
# Copyright (C) 2009-2016 Treeki, Tempus, angelsl, JasonP27, Kinnay,
# MalStar1000, RoadrunnerWMC, MrRean, Grop

# This file is part of Miyamoto! Next.

# Miyamoto! is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# Miyamoto! is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Miyamoto!. If not, see <http://www.gnu.org/licenses/>.

# lz77.py
# Decompresses lz77 compressed files.

################################################################
################################################################
import struct

class LZS11(object):
	def __init__(self):
		self.magic = 0x11
		self.decomp_size = 0
		self.curr_size = 0
		self.compressed = True
		self.outdata = []

	def Decompress11LZS(self , filein):
		offset = 0
		# check that file is < 2GB
		assert len(filein) < ( 0x4000 * 0x4000 * 2 )
		self.magic = struct.unpack('<B', filein[0:1])[0]
		assert self.magic == 0x11
		self.decomp_size = struct.unpack('<I', filein[offset:offset+4])[0] >> 8
		offset += 4
		assert self.decomp_size <= 0x200000
		if ( self.decomp_size == 0 ):
			self.decomp_size = struct.unpack('<I', filein[offset:offset+4])[0]
			offset += 4
		assert self.decomp_size <= 0x200000 << 8
		self.outdata = [0 for x in range(self.decomp_size)]

		while self.curr_size < self.decomp_size and offset < len(filein):
			flags = struct.unpack('<B', filein[offset:offset+1])[0]
			offset += 1

			for i in range(8):
				x = 7 - i
				if self.curr_size >= self.decomp_size:
					break
				if (flags & (1 << x)) > 0:
					first = struct.unpack('<B', filein[offset:offset+1])[0]
					offset += 1
					second = struct.unpack('<B', filein[offset:offset+1])[0]
					offset += 1

					if first < 0x20:
						third = struct.unpack('<B', filein[offset:offset+1])[0]
						offset += 1

						if first >= 0x10:
							fourth = struct.unpack('<B', filein[offset:offset+1])[0]
							offset += 1

							pos = (((third & 0xF) << 8) | fourth) + 1
							copylen = ((second << 4) | ((first & 0xF) << 12) | (third >> 4)) + 273
						else:
							pos = (((second & 0xF) << 8) | third) + 1
							copylen = (((first & 0xF) << 4) | (second >> 4)) + 17
					else:
						pos = (((first & 0xF) << 8) | second) + 1
						copylen = (first >> 4) + 1

					for y in range(copylen):
						self.outdata[self.curr_size + y] = self.outdata[self.curr_size - pos + y]

					self.curr_size += copylen
				else:

					self.outdata[self.curr_size] = struct.unpack('<B', filein[offset:offset+1])[0]
					offset += 1
					self.curr_size += 1

				if offset >= len(filein) or self.curr_size >= self.decomp_size:
					break
		return self.outdata