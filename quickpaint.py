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

# Quick Paint Tool created by John10v10

################################################################
################################################################

from random import random as rand

import globals


class QuickPaintOperations:
    """
    All of the actions/functions/operations/whatever programmed for the quick paint tool are stored in here.
    """
    color_shift = 0
    color_shift_mouseGridPosition = None
    object_optimize_database = []
    object_search_database = {}

    @staticmethod
    def _getMaxSize(qp_data):
        """
        Gets the maximum size of all the objects in the quick paint configuration widget.
        """
        res = 1
        for type in qp_data:
            res = max(res, qp_data[type]['ow'], qp_data[type]['oh'])

        return res

    @staticmethod
    def optimizeObjects(FromQPWidget=False):
        """
        This function merges all touching objects of the same type. We don't want huge files for level data.
        Nor do we want an island to be completely made up of 1x1 objects. And we most definately don't want
        objects more than 1x1 to repeat only the first tile in them.
        """
        optimize_memory = []

        if FromQPWidget: lr = range(-1, 0)
        else: lr = range(len(globals.Area.layers))

        for ln in lr:
            objects_inside_optimize_boxes = []

            while len(list(filter(lambda i: i.layer == ln, QuickPaintOperations.object_optimize_database))) > 0:
                from math import sqrt

                obj = min(list(filter(lambda i: i.layer == ln, QuickPaintOperations.object_optimize_database)),
                          key=lambda i: sqrt(i.objx ** 2 + i.objy ** 2))
                w = 1024
                cobj = obj
                calculated_dimensions = []
                atd_archive = []

                for y in range(512):
                    if w != 1024:
                        calculated_dimensions.append((w, y))
                    cobj = QuickPaintOperations.searchObj(obj.layer, obj.objx, obj.objy + y)

                    if cobj is None:
                        break

                    for x in range(w):
                        cobj = QuickPaintOperations.searchObj(obj.layer, obj.objx + x, obj.objy + y)
                        atd_archive.append((
                            x, y, None if not hasattr(cobj, 'modifiedForSize') else cobj.modifiedForSize,
                            None if not hasattr(cobj, 'autoTileType') else cobj.autoTileType))

                        if (not cobj or cobj in objects_inside_optimize_boxes
                            or cobj.tileset != obj.tileset or cobj.type != obj.type):
                            w = x
                            break

                # This somewhat helps remove the bug when painting over slopes.
                calculated_dimensions = list(filter(lambda i: i[0] != 0 and i[1] != 0, calculated_dimensions))
                if True in map(lambda i: i[1] > 1, calculated_dimensions):
                    calculated_dimensions = list(filter(lambda i: i[1] > 1, calculated_dimensions))

                if len(calculated_dimensions) > 0:
                    lets_use_these_dimensions = max(calculated_dimensions, key=lambda i: i[0] * i[1])

                else:
                    lets_use_these_dimensions = [0, 0, []]

                if lets_use_these_dimensions[0] * lets_use_these_dimensions[1] == 0:
                    QuickPaintOperations.object_optimize_database.remove(obj)
                    continue

                calculated_rectangle = (
                    obj.objx, obj.objy, lets_use_these_dimensions[0], lets_use_these_dimensions[1], obj,
                    list(set(atd_archive)))
                optimize_memory.append(calculated_rectangle)

                for y in range(calculated_rectangle[1], calculated_rectangle[1] + calculated_rectangle[3]):
                    for x in range(calculated_rectangle[0], calculated_rectangle[0] + calculated_rectangle[2]):
                        cobj = QuickPaintOperations.searchObj(ln, x, y)

                        if cobj in QuickPaintOperations.object_optimize_database:
                            QuickPaintOperations.object_optimize_database.remove(cobj)
                            objects_inside_optimize_boxes.append(cobj)

            for obj in objects_inside_optimize_boxes:
                if obj not in map(lambda i: i[4], optimize_memory):
                    if FromQPWidget:
                        if obj in globals.mainWindow.quickPaint.scene.display_objects:
                            obj.RemoveFromSearchDatabase()
                            globals.mainWindow.quickPaint.scene.display_objects.remove(obj)

                    else:
                        obj.delete()
                        obj.setSelected(False)
                        globals.mainWindow.scene.removeItem(obj)

            for rect in optimize_memory:
                if rect is not None:
                    obj = rect[4]
                    obj.atd_archive = rect[5]
                    obj.objx = rect[0]
                    obj.objy = rect[1]
                    obj.width = rect[2]
                    obj.height = rect[3]
                    obj.updateObjCache()
                    obj.UpdateRects()
                    obj.UpdateTooltip()

        QuickPaintOperations.object_optimize_database = []

    @staticmethod
    def prePaintObject(ln, layer, x, y, z):
        """
        Schedules an object to be added by adding the coordinates to the list of pre-painted objects.
        """
        if not hasattr(QuickPaintOperations, 'prePaintedObjects'):
            QuickPaintOperations.prePaintedObjects = {}

        if not ('%i_%i' % (x, y) in QuickPaintOperations.prePaintedObjects):
            QuickPaintOperations.prePaintedObjects['%i_%i' % (x, y)] = {'ln': ln, 'layer': layer, 'x': x, 'y': y,
                                                                        'z': z, 'r': int(rand() * 127) + 128,
                                                                        'g': int(rand() * 127) + 128,
                                                                        'b': int(rand() * 127) + 128}
        globals.mainWindow.scene.invalidate()

    @staticmethod
    def PaintFromPrePaintedObjects():
        """
        Creates and adds all the objects scheduled from the list of pre-painted objects to the level.
        """
        QuickPaintOperations.sliceObjRange(QuickPaintOperations.prePaintedObjects)
        if hasattr(QuickPaintOperations, 'prePaintedObjects'):
            for ppobj in QuickPaintOperations.prePaintedObjects:
                # We do this action twice to make sure there is no trailing.
                QuickPaintOperations.AddObj(QuickPaintOperations.prePaintedObjects[ppobj]['ln'],
                                            QuickPaintOperations.prePaintedObjects[ppobj]['layer'],
                                            QuickPaintOperations.prePaintedObjects[ppobj]['x'],
                                            QuickPaintOperations.prePaintedObjects[ppobj]['y'],
                                            QuickPaintOperations.prePaintedObjects[ppobj]['z'])
                QuickPaintOperations.AddObj(QuickPaintOperations.prePaintedObjects[ppobj]['ln'],
                                            QuickPaintOperations.prePaintedObjects[ppobj]['layer'],
                                            QuickPaintOperations.prePaintedObjects[ppobj]['x'],
                                            QuickPaintOperations.prePaintedObjects[ppobj]['y'],
                                            QuickPaintOperations.prePaintedObjects[ppobj]['z'])

        QuickPaintOperations.prePaintedObjects.clear()
        globals.mainWindow.scene.invalidate()

    @staticmethod
    def preEraseObject(ln, layer, x, y):
        """
        Schedules an object to be removed by adding the coordinates to the list of pre-painted objects.
        """
        if not hasattr(QuickPaintOperations, 'prePaintedObjects'):
            QuickPaintOperations.prePaintedObjects = {}

        if not ('%i_%i' % (x, y) in QuickPaintOperations.prePaintedObjects):
            QuickPaintOperations.prePaintedObjects['%i_%i' % (x, y)] = {'ln': ln, 'layer': layer, 'x': x, 'y': y,
                                                                        'z': 0, 'r': int(rand() * 127),
                                                                        'g': int(rand() * 127), 'b': int(rand() * 127)}

    @staticmethod
    def EraseFromPreErasedObjects():
        """
        For every coordinate from the list of pre-painted objects, an object is removed from the level.
        """
        QuickPaintOperations.sliceObjRange(QuickPaintOperations.prePaintedObjects)
        if hasattr(QuickPaintOperations, 'prePaintedObjects'):
            for ppobj in QuickPaintOperations.prePaintedObjects:
                # We do this action twice to make sure there is no trailing.
                QuickPaintOperations.EraseObj(QuickPaintOperations.prePaintedObjects[ppobj]['ln'],
                                              QuickPaintOperations.prePaintedObjects[ppobj]['layer'],
                                              QuickPaintOperations.prePaintedObjects[ppobj]['x'],
                                              QuickPaintOperations.prePaintedObjects[ppobj]['y'])
                QuickPaintOperations.EraseObj(QuickPaintOperations.prePaintedObjects[ppobj]['ln'],
                                              QuickPaintOperations.prePaintedObjects[ppobj]['layer'],
                                              QuickPaintOperations.prePaintedObjects[ppobj]['x'],
                                              QuickPaintOperations.prePaintedObjects[ppobj]['y'])

        QuickPaintOperations.prePaintedObjects.clear()
        globals.mainWindow.scene.invalidate()

    @staticmethod
    def AddObj(ln, layer, x, y, z):
        """
        Adds an object to the level and automatically fixes the tiles of islands it may be touching.
        """
        if globals.mainWindow.quickPaint is not None and globals.mainWindow.quickPaint.scene is not None:
            qpscn = globals.mainWindow.quickPaint.scene
            qp_data = qpscn.object_database

            if qp_data['base']['i'] is not None and qp_data['base']['ts'] is not None and qp_data['base'][
                't'] is not None:
                mw = globals.mainWindow
                objBehindThisOne = QuickPaintOperations.searchObj(ln, x, y)

                while objBehindThisOne is not None:
                    objBehindThisOne.delete()

                    if objBehindThisOne in QuickPaintOperations.object_optimize_database:
                        QuickPaintOperations.object_optimize_database.remove(objBehindThisOne)

                    objBehindThisOne.setSelected(False)
                    mw.scene.removeItem(objBehindThisOne)
                    objBehindThisOne = QuickPaintOperations.searchObj(ln, x, y)

                from items import ObjectItem
                obj = ObjectItem(qp_data['base']['ts'], qp_data['base']['t'], ln, x, y, 1, 1, z, 0)
                del ObjectItem

                layer.append(obj)
                obj.positionChanged = mw.HandleObjPosChange

                if obj not in QuickPaintOperations.object_optimize_database:
                    QuickPaintOperations.object_optimize_database.append(obj)

                mw.scene.addItem(obj)

                connected_objects = []
                # This next function has to repeated multiple times at multiple places in and around this object.
                # Otherwise, you will leave artifacts when painting with bigger objects.
                QuickPaintOperations.autoTileObj(ln, obj)
                for r in range(QuickPaintOperations._getMaxSize(qp_data) + 2):
                    for a in range(-r, r):
                        sobj = QuickPaintOperations.searchObj(ln, obj.objx + a, obj.objy - r)

                        if sobj is not None:
                            QuickPaintOperations.autoTileObj(ln, sobj)

                    for a in range(-r, r):
                        sobj = QuickPaintOperations.searchObj(ln, obj.objx + r, obj.objy + a)

                        if sobj is not None:
                            QuickPaintOperations.autoTileObj(ln, sobj)

                    for a in range(-r, r):
                        sobj = QuickPaintOperations.searchObj(ln, obj.objx - a, obj.objy + r)

                        if sobj is not None:
                            QuickPaintOperations.autoTileObj(ln, sobj)

                    for a in range(-r, r):
                        sobj = QuickPaintOperations.searchObj(ln, obj.objx - r, obj.objy - a)

                        if sobj is not None:
                            QuickPaintOperations.autoTileObj(ln, sobj)

    @staticmethod
    def EraseObj(ln, layer, x, y):
        """
        Removes an object from the level and automatically fixes the tiles of islands it may have been touching.
        """
        if globals.mainWindow.quickPaint is not None and globals.mainWindow.quickPaint.scene is not None:
            qpscn = globals.mainWindow.quickPaint.scene
            qp_data = qpscn.object_database

            if qp_data['base']['i'] is not None and qp_data['base']['ts'] is not None and qp_data['base'][
                't'] is not None:
                mw = globals.mainWindow
                obj = QuickPaintOperations.searchObj(ln, x, y)

                if obj is not None:
                    surrounding_objects = {
                        'TopLeft': QuickPaintOperations.searchObj(ln, obj.objx - 1, obj.objy - 1),
                        'Top': QuickPaintOperations.searchObj(ln, obj.objx, obj.objy - 1),
                        'TopRight': QuickPaintOperations.searchObj(ln, obj.objx + 1, obj.objy - 1),
                        'Left': QuickPaintOperations.searchObj(ln, obj.objx - 1, obj.objy),
                        'Right': QuickPaintOperations.searchObj(ln, obj.objx + 1, obj.objy),
                        'BottomLeft': QuickPaintOperations.searchObj(ln, obj.objx - 1, obj.objy + 1),
                        'Bottom': QuickPaintOperations.searchObj(ln, obj.objx, obj.objy + 1),
                        'BottomRight': QuickPaintOperations.searchObj(ln, obj.objx + 1, obj.objy + 1)
                    }
                    obj.delete()
                    obj.setSelected(False)

                    if obj in QuickPaintOperations.object_optimize_database:
                        QuickPaintOperations.object_optimize_database.remove(obj)

                    mw.scene.removeItem(obj)

                    for r in range(QuickPaintOperations._getMaxSize(qp_data) + 2):
                        for a in range(-r, r):
                            sobj = QuickPaintOperations.searchObj(ln, obj.objx + a, obj.objy - r)

                            if sobj is not None:
                                QuickPaintOperations.autoTileObj(ln, sobj)

                        for a in range(-r, r):
                            sobj = QuickPaintOperations.searchObj(ln, obj.objx + r, obj.objy + a)

                            if sobj is not None:
                                QuickPaintOperations.autoTileObj(ln, sobj)

                        for a in range(-r, r):
                            sobj = QuickPaintOperations.searchObj(ln, obj.objx - a, obj.objy + r)

                            if sobj is not None:
                                QuickPaintOperations.autoTileObj(ln, sobj)

                        for a in range(-r, r):
                            sobj = QuickPaintOperations.searchObj(ln, obj.objx - r, obj.objy - a)

                            if sobj is not None:
                                QuickPaintOperations.autoTileObj(ln, sobj)

    @staticmethod
    def searchObj(layer, x, y):
        """
        Quickly searches for an object at the specified position.
        """
        if not QuickPaintOperations.object_search_database.get((x, y, layer)):
            return None

        if len(QuickPaintOperations.object_search_database[(x, y, layer)]) <= 0:
            return None

        return QuickPaintOperations.object_search_database[(x, y, layer)][0]

    @staticmethod
    def sliceObjRange(posList):
        """
        For every object and objects touching that object, they will slice into 1x1 objects.
        """
        connected_objects = []
        objlist = []
        for pos in map(lambda i: (posList[i]['x'], posList[i]['y'], posList[i]['ln']), posList):
            qpscn = globals.mainWindow.quickPaint.scene
            qp_data = qpscn.object_database
            # pronounced [BOB-JAY] lol
            # Way to go Robert!
            # Actually Bobj stands for base object, because these are the objects we start with as they lie
            # on the positions where the user has painted over on the widget.
            # - John10v10
            bobj = QuickPaintOperations.searchObj(pos[2], pos[0], pos[1])

            if bobj is not None and bobj not in connected_objects:
                connected_objects.append(bobj)
                objlist.append(bobj)

            for r in range(QuickPaintOperations._getMaxSize(qp_data) + 2):
                for a in range(-r, r):
                    bobj = QuickPaintOperations.searchObj(pos[2], pos[0] + a, pos[1] - r)

                    if bobj is not None and bobj not in connected_objects:
                        connected_objects.append(bobj)
                        objlist.append(bobj)

                for a in range(-r, r):
                    bobj = QuickPaintOperations.searchObj(pos[2], pos[0] + r, pos[1] + a)

                    if bobj is not None and bobj not in connected_objects:
                        connected_objects.append(bobj)
                        objlist.append(bobj)

                for a in range(-r, r):
                    bobj = QuickPaintOperations.searchObj(pos[2], pos[0] - a, pos[1] + r)

                    if bobj is not None and bobj not in connected_objects:
                        connected_objects.append(bobj)
                        objlist.append(bobj)

                for a in range(-r, r):
                    bobj = QuickPaintOperations.searchObj(pos[2], pos[0] - r, pos[1] - a)

                    if bobj is not None and bobj not in connected_objects:
                        connected_objects.append(bobj)
                        objlist.append(bobj)

        no_more_found = False
        while not no_more_found:
            preobjlist = []
            for obj in objlist:
                for x in range(obj.objx - 1, obj.objx + obj.width + 1):
                    for y in range(obj.objy - 1, obj.objy + obj.height + 1):
                        sobj = QuickPaintOperations.searchObj(obj.layer, x, y)

                        if sobj is not None and sobj is not obj and sobj not in connected_objects:
                            still_append = True

                            for pos in map(lambda i: (posList[i]['x'], posList[i]['y']), posList):
                                if abs(x - pos[0]) > r or abs(y - pos[1]) > r:
                                    still_append = False

                            if still_append:
                                preobjlist.append(sobj)
                                connected_objects.append(sobj)

            if len(preobjlist) <= 0:
                no_more_found = True

            else:
                objlist = preobjlist

        connected_objects = list(filter(lambda i: i is not None, list(set(connected_objects))))
        for robj in connected_objects:
            QuickPaintOperations.sliceObj(robj)

    @staticmethod
    def sliceObj(obj, px=None, py=None):
        """
        Slices this object into 1x1 objects.
        """
        if not obj or (obj.width == 1 and obj.height == 1):
            if obj not in QuickPaintOperations.object_optimize_database and obj:
                QuickPaintOperations.object_optimize_database.append(obj)

            return obj

        out_obj = None
        mw = globals.mainWindow
        objx = obj.objx
        objy = obj.objy
        w = obj.width
        h = obj.height
        l = obj.layer
        ts = obj.tileset
        t = obj.original_type
        atd_archive = []

        if hasattr(obj, 'atd_archive') and obj.atd_archive:
            atd_archive = obj.atd_archive

        skip = []
        x = 0
        y = 0
        if obj.objdata:
            for row in obj.objdata:
                x = 0

                for tile in row:
                    if tile == -1:
                        skip.append((x, y))

                    x += 1

                y += 1

        if obj in globals.Area.layers[obj.layer]:
            obj.delete()
            obj.setSelected(False)
            mw.scene.removeItem(obj)

        if obj in QuickPaintOperations.object_optimize_database:
            QuickPaintOperations.object_optimize_database.remove(obj)

        for y in range(h):
            for x in range(w):
                if (x, y) in skip: continue

                layer = globals.Area.layers[l]
                ln = globals.CurrentLayer

                if len(layer) == 0:
                    z = (2 - ln) * 8192

                else:
                    z = layer[-1].zValue() + 1

                objBehindThisOne = QuickPaintOperations.sliceObj(QuickPaintOperations.searchObj(ln, x + objx, y + objy),
                                                                 x + objx, y + objy)
                if objBehindThisOne is not None:
                    objBehindThisOne.delete()
                    objBehindThisOne.setSelected(False)

                    if objBehindThisOne in QuickPaintOperations.object_optimize_database:
                        QuickPaintOperations.object_optimize_database.remove(objBehindThisOne)

                    mw.scene.removeItem(objBehindThisOne)

                from items import ObjectItem
                sobj = ObjectItem(ts, t, l, x + objx, y + objy, 1, 1, z, 0)
                del ObjectItem

                atd = list(filter(lambda i: i[0] == x and i[1] == y, atd_archive))

                if atd is not None and len(atd) > 0:
                    sobj.modifiedForSize = atd[0][2]
                    sobj.autoTileType = atd[0][3]

                layer.append(sobj)

                if sobj not in QuickPaintOperations.object_optimize_database:
                    QuickPaintOperations.object_optimize_database.append(sobj)

                sobj.positionChanged = mw.HandleObjPosChange
                mw.scene.addItem(sobj)

                if sobj.objx == px and sobj.objy == py:
                    out_obj = sobj

        return out_obj

    @staticmethod
    def isObjectInQPwidget(obj):
        """
        Checks if object is in the quick paint configuration widget.
        """
        if obj is None: return False

        qpscn = globals.mainWindow.quickPaint.scene
        qp_data = qpscn.object_database

        for t in qp_data:
            if qp_data[t] is not None and qp_data[t]['ts'] == obj.tileset and qp_data[t]['t'] == obj.original_type:
                return True

        return False

    @staticmethod
    def countUpLeft(layer, obj, maxX, maxY):
        """
        Checks if object is inside the top-left corner within a given boundary.
        """
        for x in range(maxX + 1):
            for y in range(maxY + 1):
                if QuickPaintOperations.searchObj(layer, obj.objx - x, obj.objy - y) is None: return True

        return False

    @staticmethod
    def countUpRight(layer, obj, maxX, maxY):
        """
        Checks if object is inside the top-right corner within a given boundary.
        """
        for x in range(maxX + 1):
            for y in range(maxY + 1):
                if QuickPaintOperations.searchObj(layer, obj.objx + x, obj.objy - y) is None: return True

        return False

    @staticmethod
    def countDownLeft(layer, obj, maxX, maxY):
        """
        Checks if object is inside the down-left corner within a given boundary.
        """
        for x in range(maxX + 1):
            for y in range(maxY + 1):
                if QuickPaintOperations.searchObj(layer, obj.objx - x, obj.objy + y) is None: return True

        return False

    @staticmethod
    def countDownRight(layer, obj, maxX, maxY):
        """
        Checks if object is inside the down-right corner within a given boundary.
        """
        for x in range(maxX + 1):
            for y in range(maxY + 1):
                if QuickPaintOperations.searchObj(layer, obj.objx + x, obj.objy + y) is None: return True

        return False

    @staticmethod
    def countUp(layer, obj, maxY):
        """
        Checks if object is not too far underneath the ground within a given boundary.
        """
        for y in range(maxY + 1):
            if QuickPaintOperations.searchObj(layer, obj.objx, obj.objy - y) is None: return True

        return False

    @staticmethod
    def countDown(layer, obj, maxY):
        """
        Checks if object is not too far above the bottom within a given boundary.
        """
        for y in range(maxY + 1):
            if QuickPaintOperations.searchObj(layer, obj.objx, obj.objy + y) is None: return True

        return False

    @staticmethod
    def countLeft(layer, obj, maxX):
        """
        Checks if object is not too far to the right of the left wall within a given boundary.
        """
        for x in range(maxX + 1):
            if QuickPaintOperations.searchObj(layer, obj.objx - x, obj.objy) is None: return True

        return False

    @staticmethod
    def countRight(layer, obj, maxX):
        """
        Checks if object is not too far to the left of the right wall within a given boundary.
        """
        for x in range(maxX + 1):
            if QuickPaintOperations.searchObj(layer, obj.objx + x, obj.objy) is None: return True

        return False

    @staticmethod
    def autoTileObj(layer, obj):
        """
        Automatically picks the tile that best fits its position.
        It's a big process, but I hope it works well enough for Miyamoto users.
        """
        if globals.mainWindow.quickPaint and globals.mainWindow.quickPaint.scene and obj:
            qpscn = globals.mainWindow.quickPaint.scene
            qp_data = qpscn.object_database
            startingTileset = obj.tileset
            startingType = obj.type
            surrounding_objects = {
                'TopLeft': QuickPaintOperations.searchObj(layer, obj.objx - 1, obj.objy - 1),
                'Top': QuickPaintOperations.searchObj(layer, obj.objx, obj.objy - 1),
                'TopRight': QuickPaintOperations.searchObj(layer, obj.objx + 1, obj.objy - 1),
                'Left': QuickPaintOperations.searchObj(layer, obj.objx - 1, obj.objy),
                'Right': QuickPaintOperations.searchObj(layer, obj.objx + 1, obj.objy),
                'BottomLeft': QuickPaintOperations.searchObj(layer, obj.objx - 1, obj.objy + 1),
                'Bottom': QuickPaintOperations.searchObj(layer, obj.objx, obj.objy + 1),
                'BottomRight': QuickPaintOperations.searchObj(layer, obj.objx + 1, obj.objy + 1),
            }

            if QuickPaintOperations.isObjectInQPwidget(obj):
                flag = 0x0
                if QuickPaintOperations.isObjectInQPwidget(surrounding_objects['TopLeft']): flag |= 0x1
                if QuickPaintOperations.isObjectInQPwidget(surrounding_objects['Top']): flag |= 0x2
                if QuickPaintOperations.isObjectInQPwidget(surrounding_objects['TopRight']): flag |= 0x4
                if QuickPaintOperations.isObjectInQPwidget(surrounding_objects['Left']): flag |= 0x8
                if QuickPaintOperations.isObjectInQPwidget(surrounding_objects['Right']): flag |= 0x10
                if QuickPaintOperations.isObjectInQPwidget(surrounding_objects['BottomLeft']): flag |= 0x20
                if QuickPaintOperations.isObjectInQPwidget(surrounding_objects['Bottom']): flag |= 0x40
                if QuickPaintOperations.isObjectInQPwidget(surrounding_objects['BottomRight']): flag |= 0x80

                typeToTile = 'base'
                if flag & 0xdb == 0xB:
                    typeToTile = qpscn.pickObject('bottomRight')
                if flag & 0x7e == 0x16:
                    typeToTile = qpscn.pickObject('bottomLeft')
                if flag & 0xdb == 0xd0:
                    typeToTile = qpscn.pickObject('topLeft')
                if flag & 0x7e == 0x68:
                    typeToTile = qpscn.pickObject('topRight')
                if flag & 0x5a == 0x1a:
                    typeToTile = qpscn.pickObject('bottom')
                if flag & 0x5a == 0x58:
                    typeToTile = qpscn.pickObject('top')
                if flag & 0x5a == 0x52:
                    typeToTile = qpscn.pickObject('left')
                if flag & 0x5a == 0x4a:
                    typeToTile = qpscn.pickObject('right')
                if flag & 0xdb == 0x5b:
                    typeToTile = qpscn.pickObject('topLeftCorner')
                if flag & 0xdb == 0xda:
                    typeToTile = qpscn.pickObject('bottomRightCorner')
                if flag & 0x7e == 0x5e:
                    typeToTile = qpscn.pickObject('topRightCorner')
                if flag & 0x7e == 0x7a:
                    typeToTile = qpscn.pickObject('bottomLeftCorner')

                obj.modifiedForSize = 0x00
                obj.autoTileType = typeToTile
                if typeToTile is not None and qp_data.get(typeToTile) is not None and qp_data[typeToTile][
                    'i'] is not None:
                    obj.tileset = qp_data[typeToTile]['ts']
                    obj.type = qp_data[typeToTile]['t']
                    obj.original_type = qp_data[typeToTile]['t']
                    if qp_data['topLeftCorner']['i'] is not None:
                        for y in range(qp_data['topLeftCorner']['oh']):
                            for x in range(qp_data['topLeftCorner']['ow']):
                                if x > 0 or y > 0:
                                    sobj = QuickPaintOperations.searchObj(layer, obj.objx + x, obj.objy + y)

                                    if (sobj and sobj.width == 1 and sobj.height == 1
                                        and (hasattr(sobj, 'autoTileType') and sobj.autoTileType == 'topLeftCorner')
                                        and not (hasattr(sobj, 'modifiedForSize')
                                                 and sobj.modifiedForSize & 0x100 == 0x100)):
                                        obj.tileset = sobj.tileset
                                        obj.type = sobj.original_type
                                        obj.original_type = sobj.original_type
                                        obj.modifiedForSize |= 0x100

                    if qp_data['topRightCorner']['i'] is not None:
                        for y in range(qp_data['topRightCorner']['oh']):
                            for x in range(qp_data['topRightCorner']['ow']):
                                if x > 0 or y > 0:
                                    sobj = QuickPaintOperations.searchObj(layer, obj.objx - x, obj.objy + y)

                                    if (sobj and sobj.width == 1 and sobj.height == 1
                                        and (hasattr(sobj, 'autoTileType') and sobj.autoTileType == 'topRightCorner')
                                        and not (hasattr(sobj, 'modifiedForSize')
                                                 and sobj.modifiedForSize & 0x200 == 0x200)):
                                        obj.tileset = sobj.tileset
                                        obj.type = sobj.original_type
                                        obj.original_type = sobj.original_type
                                        obj.modifiedForSize |= 0x200

                    if qp_data['bottomLeftCorner']['i'] is not None:
                        for y in range(qp_data['bottomLeftCorner']['oh']):
                            for x in range(qp_data['bottomLeftCorner']['ow']):
                                if x > 0 or y > 0:
                                    sobj = QuickPaintOperations.searchObj(layer, obj.objx + x, obj.objy - y)

                                    if (sobj and sobj.width == 1 and sobj.height == 1
                                        and (hasattr(sobj, 'autoTileType') and sobj.autoTileType == 'bottomLeftCorner')
                                        and not (hasattr(sobj, 'modifiedForSize')
                                                 and sobj.modifiedForSize & 0x400 == 0x400)):
                                        obj.tileset = sobj.tileset
                                        obj.type = sobj.original_type
                                        obj.original_type = sobj.original_type
                                        obj.modifiedForSize |= 0x400

                    if qp_data['bottomRightCorner']['i'] is not None:
                        for y in range(qp_data['bottomRightCorner']['oh']):
                            for x in range(qp_data['bottomRightCorner']['ow']):
                                if x > 0 or y > 0:
                                    sobj = QuickPaintOperations.searchObj(layer, obj.objx - x, obj.objy - y)

                                    if (sobj and sobj.width == 1 and sobj.height == 1
                                        and (hasattr(sobj, 'autoTileType') and sobj.autoTileType == 'bottomRightCorner')
                                        and not (hasattr(sobj, 'modifiedForSize')
                                                 and sobj.modifiedForSize & 0x800 == 0x800)):
                                        obj.tileset = sobj.tileset
                                        obj.type = sobj.original_type
                                        obj.original_type = sobj.original_type
                                        obj.modifiedForSize |= 0x800

                    if qp_data['topLeft']['i'] is not None and QuickPaintOperations.countUpLeft(layer, obj,
                                                                                                qp_data['topLeft'][
                                                                                                    'ow'],
                                                                                                qp_data['topLeft'][
                                                                                                    'oh']):
                        for y in range(qp_data['topLeft']['oh']):
                            for x in range(qp_data['topLeft']['ow']):
                                if x > 0 or y > 0:
                                    sobj = QuickPaintOperations.searchObj(layer, obj.objx - x, obj.objy - y)

                                    if sobj is not None and sobj.width == 1 and sobj.height == 1 and (
                                                hasattr(sobj,
                                                        'autoTileType') and sobj.autoTileType == 'topLeft') and not (
                                                hasattr(sobj,
                                                        'modifiedForSize') and sobj.modifiedForSize & 0x01 == 0x1):
                                        obj.tileset = sobj.tileset
                                        obj.type = sobj.original_type
                                        obj.original_type = sobj.original_type
                                        obj.modifiedForSize |= 0x01

                    if qp_data['topRight']['i'] is not None and QuickPaintOperations.countUpRight(layer, obj,
                                                                                                  qp_data['topRight'][
                                                                                                      'ow'],
                                                                                                  qp_data['topRight'][
                                                                                                      'oh']):
                        for y in range(qp_data['topRight']['oh']):
                            for x in range(qp_data['topRight']['ow']):
                                if x > 0 or y > 0:
                                    sobj = QuickPaintOperations.searchObj(layer, obj.objx + x, obj.objy - y)

                                    if sobj is not None and sobj.width == 1 and sobj.height == 1 and (
                                                hasattr(sobj,
                                                        'autoTileType') and sobj.autoTileType == 'topRight') and not (
                                                hasattr(sobj,
                                                        'modifiedForSize') and sobj.modifiedForSize & 0x02 == 0x2):
                                        obj.tileset = sobj.tileset
                                        obj.type = sobj.original_type
                                        obj.original_type = sobj.original_type
                                        obj.modifiedForSize |= 0x02

                    if qp_data['bottomLeft']['i'] is not None and QuickPaintOperations.countDownLeft(layer, obj,
                                                                                                     qp_data[
                                                                                                         'bottomLeft'][
                                                                                                         'ow'], qp_data[
                                                                                                         'bottomLeft'][
                                                                                                         'oh']):
                        for y in range(qp_data['bottomLeft']['oh']):
                            for x in range(qp_data['bottomLeft']['ow']):
                                if x > 0 or y > 0:
                                    sobj = QuickPaintOperations.searchObj(layer, obj.objx - x, obj.objy + y)

                                    if sobj is not None and sobj.width == 1 and sobj.height == 1 and (
                                                hasattr(sobj,
                                                        'autoTileType') and sobj.autoTileType == 'bottomLeft') and not (
                                                hasattr(sobj,
                                                        'modifiedForSize') and sobj.modifiedForSize & 0x04 == 0x4):
                                        obj.tileset = sobj.tileset
                                        obj.type = sobj.original_type
                                        obj.original_type = sobj.original_type
                                        obj.modifiedForSize |= 0x04

                    if qp_data['bottomRight']['i'] and QuickPaintOperations.countDownRight(layer, obj,
                                                                                           qp_data[
                                                                                               'bottomRight'][
                                                                                               'ow'],
                                                                                           qp_data[
                                                                                               'bottomRight'][
                                                                                               'oh']):
                        for y in range(qp_data['bottomRight']['oh']):
                            for x in range(qp_data['bottomRight']['ow']):
                                if x > 0 or y > 0:
                                    sobj = QuickPaintOperations.searchObj(layer, obj.objx + x, obj.objy + y)

                                    if (sobj is not None and sobj.width == 1 and sobj.height == 1
                                        and (hasattr(sobj, 'autoTileType') and sobj.autoTileType == 'bottomRight')
                                        and not (hasattr(sobj, 'modifiedForSize')
                                                 and sobj.modifiedForSize & 0x08 == 0x8)):
                                        obj.tileset = sobj.tileset
                                        obj.type = sobj.original_type
                                        obj.original_type = sobj.original_type
                                        obj.modifiedForSize |= 0x08

                    if qp_data['top']['i'] is not None and QuickPaintOperations.countUp(layer, obj,
                                                                                        qp_data['top']['oh']):
                        for y in range(qp_data['top']['oh']):
                            if y > 0:
                                sobj = QuickPaintOperations.searchObj(layer, obj.objx, obj.objy - y)

                                if sobj is not None and sobj.width == 1 and sobj.height == 1 and (
                                            hasattr(sobj, 'autoTileType') and sobj.autoTileType == 'top') and not (
                                            hasattr(sobj, 'modifiedForSize') and sobj.modifiedForSize & 0x10 == 0x10):
                                    obj.tileset = sobj.tileset
                                    obj.type = sobj.original_type
                                    obj.original_type = sobj.original_type
                                    obj.modifiedForSize |= 0x10

                    if qp_data['bottom']['i'] is not None and QuickPaintOperations.countDown(layer, obj,
                                                                                             qp_data['bottom']['oh']):
                        for y in range(qp_data['bottom']['oh']):
                            if y > 0:
                                sobj = QuickPaintOperations.searchObj(layer, obj.objx, obj.objy + y)

                                if sobj is not None and sobj.width == 1 and sobj.height == 1 and (
                                            hasattr(sobj, 'autoTileType') and sobj.autoTileType == 'bottom') and not (
                                            hasattr(sobj, 'modifiedForSize') and sobj.modifiedForSize & 0x20 == 0x20):
                                    obj.tileset = sobj.tileset
                                    obj.type = sobj.original_type
                                    obj.original_type = sobj.original_type
                                    obj.modifiedForSize |= 0x20

                    if qp_data['left']['i'] is not None and QuickPaintOperations.countLeft(layer, obj,
                                                                                           qp_data['left']['ow']):
                        for x in range(qp_data['left']['ow']):
                            if x > 0:
                                sobj = QuickPaintOperations.searchObj(layer, obj.objx - x, obj.objy)

                                if sobj is not None and sobj.width == 1 and sobj.height == 1 and (
                                            hasattr(sobj, 'autoTileType') and sobj.autoTileType == 'left') and not (
                                            hasattr(sobj, 'modifiedForSize') and sobj.modifiedForSize & 0x40 == 0x40):
                                    obj.tileset = sobj.tileset
                                    obj.type = sobj.original_type
                                    obj.original_type = sobj.original_type
                                    obj.modifiedForSize |= 0x40

                    if qp_data['right']['i'] is not None and QuickPaintOperations.countRight(layer, obj,
                                                                                             qp_data['right']['ow']):
                        for x in range(qp_data['right']['ow']):
                            if x > 0:
                                sobj = QuickPaintOperations.searchObj(layer, obj.objx + x, obj.objy)

                                if sobj is not None and sobj.width == 1 and sobj.height == 1 and (
                                            hasattr(sobj, 'autoTileType') and sobj.autoTileType == 'right') and not (
                                            hasattr(sobj, 'modifiedForSize') and sobj.modifiedForSize & 0x80 == 0x80):
                                    obj.tileset = sobj.tileset
                                    obj.type = sobj.original_type
                                    obj.original_type = sobj.original_type
                                    obj.modifiedForSize |= 0x80

                    obj.updateObjCache()
                    obj.UpdateTooltip()
