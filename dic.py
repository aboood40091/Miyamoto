#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Miyamoto! DX Level Editor - New Super Mario Bros. U Deluxe Level Editor
# Copyright (C) 2009-2020 Treeki, Tempus, angelsl, JasonP27, Kinnay,
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


# dic.py: script for generating a radix tree used in multiple Nintendo formats
# Python <=3.6 port by AboodXD

# Original implementation:
# https://github.com/zeldamods/evfl/blob/master/evfl/dic.py


################################################################
################################################################

from collections import namedtuple, OrderedDict


def _bit_mismatch(int1, int2):
    """
    Returns the index of the first different bit or -1 if the values are the same.
    """
    for i in range(max(int1.bit_length(), int2.bit_length())):
        if _bit(int1, i) != _bit(int2, i):
            return i

    return -1


def _first_1bit(n):
    for i in range(n.bit_length()):
        if _bit(n, i):
            return i

    assert False


def _bit(n, b):
    b &= 0xffffffff
    if b >= n.bit_length():
        return 0

    if b > 0x7fffffff:
        # slow path, workaround for Python issue 29816
        return int(bin(n)[-b-1])

    else:
        return (n >> b) & 1


IndexTableEntry = namedtuple('IndexTableEntry', ['name', 'reference_bit', 'left_idx', 'right_idx'])
IndexTableEntry.__str__ = lambda self: '[%d] %s' % (self.reference_bit, self.name)


def debug_print_graph(table):
    print('digraph {')

    for d in table:
        print('"%s" -> "%s" [color=red];' % (str(d), str(table[d.left_idx])))
        print('"%s" -> "%s" [color=green];' % (str(d), str(table[d.right_idx])))

    print('}')


class _Node:
    __slots__ = ['child', 'data', 'bit_idx', 'parent']
    def __init__(self, data, bit_idx, parent):
        self.child = [self, self]
        self.data = data
        self.bit_idx = bit_idx
        # Trade space complexity for convenience.
        self.parent = parent

    def __str__(self):
        if self.data == 0:
            return '<ROOT>'

        return '[%d] %s' % (self.bit_idx, self.get_name())

    def get_name(self):
        return self.data.to_bytes((self.data.bit_length() + 7) // 8, byteorder='big').decode()

    def get_reference_bit(self):
        byte_idx = self.bit_idx // 8
        return ((byte_idx << 3) | (self.bit_idx - 8*byte_idx)) & 0xffffffff


class Tree(_Node):
    """
    Implementation of a binary radix search tree used by Nintendo's DIC data structure.

    It is not intended to be used for lookups (as such, it does _not_ store any data)
    but only to build a DIC and in particular to generate the index table.
    """

    __slots__ = ['_entries']
    def __init__(self):
        super().__init__(0, -1, self)
        self._entries = OrderedDict()
        self._insert_entry(0, self)

    def get_reference_bit(self):
        return 0xffffffff

    def search(self, data, prev):
        if self.child[0] is self:
            return self

        node = self.child[0]
        prev_node = node
        while True:
            prev_node = node
            node = node.child[_bit(data, node.bit_idx)]
            if node.bit_idx <= prev_node.bit_idx:
                break

        return prev_node if prev else node

    def _insert_entry(self, data, node):
        self._entries[data] = (len(self._entries), node)

    def insert(self, name):
        data = int.from_bytes(name.encode(), byteorder='big')

        current = self.search(data, prev=True)
        bit_idx = _bit_mismatch(current.data, data)
        while bit_idx < current.parent.bit_idx:
            current = current.parent

        if bit_idx < current.bit_idx:
            # Insert before the current node as our bit index is lower,
            # which means the new node is closer to the root than the current one.
            new = _Node(data, bit_idx, current.parent)
            new.child[_bit(data, bit_idx)^1] = current
            current.parent.child[_bit(data, current.parent.bit_idx)] = new
            current.parent = new
            self._insert_entry(data, new)

        elif bit_idx > current.bit_idx:
            # Insert as a child of the current node as our bit index is higher,
            # which means the new node is deeper in the tree.
            new = _Node(data, bit_idx, current)
            if _bit(current.data, bit_idx) == _bit(data, bit_idx)^1:
                new.child[_bit(data, bit_idx)^1] = current

            else:
                new.child[_bit(data, bit_idx)^1] = self

            current.child[_bit(data, current.bit_idx)] = new
            self._insert_entry(data, new)

        else:
            # Both nodes have the same depth: insert the new node as a child of the current node.
            # Preserve tree invariants (bit indices must increase during traversal)
            # by using a higher bit index.
            # Nintendo's algorithm seems to use the index of the first set bit.
            new_bit_idx = _first_1bit(data)

            # If the current node pointed to another node, use the bit that differentiates
            # the new node from the other one.
            if current.child[_bit(data, bit_idx)] != self:
                new_bit_idx = _bit_mismatch(current.child[_bit(data, bit_idx)].data, data)

            new = _Node(data, new_bit_idx, current)
            new.child[_bit(data, new_bit_idx)^1] = current.child[_bit(data, bit_idx)]
            current.child[_bit(data, bit_idx)] = new
            self._insert_entry(data, new)

    def get_index_table(self):
        return [IndexTableEntry(node.get_name(), node.get_reference_bit(),
                                self._entries[node.child[0].data][0], self._entries[node.child[1].data][0])
                for _, node in self._entries.values()]
