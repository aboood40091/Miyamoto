#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright © 2018 AboodXD
# Licensed under GNU GPLv3

################################################################
################################################################

from cpython cimport array
from cython cimport view
from libc.stdlib cimport malloc, free


ctypedef unsigned char u8
ctypedef unsigned short u16
ctypedef unsigned int u32


cdef void getComponentsFromPixel(str format_, pixel, u8 *comp):
    if format_ == 'l8':
        comp[2] = pixel & 0xFF

    elif format_ == 'la8':
        comp[2] = pixel & 0xFF
        comp[3] = (pixel & 0xFF00) >> 8

    elif format_ == 'la4':
        comp[2] = (pixel & 0xF) * 17
        comp[3] = ((pixel & 0xF0) >> 4) * 17

    elif format_ == 'rgb565':
        comp[2] = int((pixel & 0x1F) / 0x1F * 0xFF)
        comp[3] = int(((pixel & 0x7E0) >> 5) / 0x3F * 0xFF)
        comp[4] = int(((pixel & 0xF800) >> 11) / 0x1F * 0xFF)

    elif format_ == 'bgr565':
        comp[2] = int(((pixel & 0xF800) >> 11) / 0x1F * 0xFF)
        comp[3] = int(((pixel & 0x7E0) >> 5) / 0x3F * 0xFF)
        comp[4] = int((pixel & 0x1F) / 0x1F * 0xFF)

    elif format_ == 'rgb5a1':
        comp[2] = int((pixel & 0x1F) / 0x1F * 0xFF)
        comp[3] = int(((pixel & 0x3E0) >> 5) / 0x1F * 0xFF)
        comp[4] = int(((pixel & 0x7c00) >> 10) / 0x1F * 0xFF)
        comp[5] = ((pixel & 0x8000) >> 15) * 0xFF

    elif format_ == 'bgr5a1':
        comp[2] = int(((pixel & 0x7c00) >> 10) / 0x1F * 0xFF)
        comp[3] = int(((pixel & 0x3E0) >> 5) / 0x1F * 0xFF)
        comp[4] = int((pixel & 0x1F) / 0x1F * 0xFF)
        comp[5] = ((pixel & 0x8000) >> 15) * 0xFF

    elif format_ == 'a1bgr5':
        comp[2] = ((pixel & 0x8000) >> 15) * 0xFF
        comp[3] = int(((pixel & 0x7c00) >> 10) / 0x1F * 0xFF)
        comp[4] = int(((pixel & 0x3E0) >> 5) / 0x1F * 0xFF)
        comp[5] = int((pixel & 0x1F) / 0x1F * 0xFF)

    elif format_ == 'rgba4':
        comp[2] = (pixel & 0xF) * 17
        comp[3] = ((pixel & 0xF0) >> 4) * 17
        comp[4] = ((pixel & 0xF00) >> 8) * 17
        comp[5] = ((pixel & 0xF000) >> 12) * 17

    elif format_ == 'abgr4':
        comp[2] = ((pixel & 0xF000) >> 12) * 17
        comp[3] = ((pixel & 0xF00) >> 8) * 17
        comp[4] = ((pixel & 0xF0) >> 4) * 17
        comp[5] = (pixel & 0xF) * 17

    elif format_ == 'rgb8':
        comp[2] = pixel & 0xFF
        comp[3] = (pixel & 0xFF00) >> 8
        comp[4] = (pixel & 0xFF0000) >> 16

    elif format_ == 'bgr10a2':
        comp[2] = int((pixel & 0x3FF) / 0x3FF * 0xFF)
        comp[3] = int(((pixel & 0xFFC00) >> 10) / 0x3FF * 0xFF)
        comp[4] = int(((pixel & 0x3FF00000) >> 20) / 0x3FF * 0xFF)
        comp[5] = int(((pixel & 0xC0000000) >> 30) / 0x3 * 0xFF)

    elif format_ == 'rgba8':
        comp[2] = pixel & 0xFF
        comp[3] = (pixel & 0xFF00) >> 8
        comp[4] = (pixel & 0xFF0000) >> 16
        comp[5] = (pixel & 0xFF000000) >> 24

    elif format_ == 'bgra8':
        comp[2] = (pixel & 0xFF0000) >> 16
        comp[3] = (pixel & 0xFF00) >> 8
        comp[4] = pixel & 0xFF
        comp[5] = (pixel & 0xFF000000) >> 24

cpdef bytes torgba8(u32 width, u32 height, bytearray data_, str format_, u32 bpp, list compSel_):
    cdef:
        array.array dataArr = array.array('B', data_)
        u8 *data = dataArr.data.as_uchars

        u32[4] compSel
        u32 i, elem

    for i, elem in enumerate(compSel_):
        compSel[i] = elem

    assert len(data_) >= width * height * bpp

    cdef:
        u32 size = width * height * 4
        u8 *new_data = <u8 *>malloc(size)

        u32 x, y, pos, pos_, pixel
        u8* comp = <u8 *>malloc(6)  # "u8[6] comp" causes issues

    comp[0] = 0
    comp[1] = 0xFF
    comp[2] = 0
    comp[3] = 0
    comp[4] = 0
    comp[5] = 0xFF

    if bpp not in [1, 2, 4]:
        try:
            return bytes(<u8[:size]>new_data)

        finally:
            free(new_data)
            free(comp)

    for y in range(height):
        for x in range(width):
            pos = (y * width + x) * bpp
            pos_ = (y * width + x) * 4

            pixel = 0
            for i in range(bpp):
                pixel |= data[pos + i] << (8 * i)

            getComponentsFromPixel(format_, pixel, comp)

            new_data[pos_ + 3] = <u8>comp[compSel[3]]
            new_data[pos_ + 2] = <u8>comp[compSel[2]]
            new_data[pos_ + 1] = <u8>comp[compSel[1]]
            new_data[pos_ + 0] = <u8>comp[compSel[0]]

    try:
        return bytes(<u8[:size]>new_data)

    finally:
        free(new_data)
        free(comp)


cpdef bytes rgb8torgbx8(bytearray data):
    cdef:
        u32 numPixels = len(data) // 3

        u8 *new_data = <u8 *>malloc(numPixels * 4)
        u32 i

    try:
        for i in range(numPixels):
            new_data[4 * i + 0] = data[3 * i + 0]
            new_data[4 * i + 1] = data[3 * i + 1]
            new_data[4 * i + 2] = data[3 * i + 2]
            new_data[4 * i + 3] = 0xFF

        return bytes(<u8[:numPixels * 4]>new_data)

    finally:
        free(new_data)
