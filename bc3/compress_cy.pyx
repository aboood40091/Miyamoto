#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# BC3 Compressor/Decompressor
# Version 0.1
# Copyright © 2018 MasterVermilli0n / AboodXD

# compress_cy.pyx
# A Cython port of libtxc_dxtn compressor.

################################################################
################################################################

from cpython cimport array
from cython cimport view
from libc.stdlib cimport malloc, free


ctypedef signed char s8
ctypedef unsigned char u8
ctypedef short int16
ctypedef unsigned short u16
ctypedef unsigned int u32


cdef void fancybasecolorsearch(u8 srccolors[4][4][4], u8 *bestcolor[2],
                               int numxpixels, int numypixels):

    # use same luminance-weighted distance metric to determine encoding as for finding the base colors */

    # TODO could also try to find a better encoding for the 3-color-encoding type, this really should be done
    # if it's rgba_dxt1 and we have alpha in the block, currently even values which will be mapped to black
    # due to their alpha value will influence the result

    cdef:
        int i, j, colors, z
        u32 pixerror, pixerrorred, pixerrorgreen, pixerrorblue, pixerrorbest
        int colordist, blockerrlin[2][3]
        u8 nrcolor[2]
        int pixerrorcolorbest[3]
        u8 enc = 0
        u8 cv[4][4]
        u8 testcolor[2][3]

    if (
        ((bestcolor[0][0] & 0xf8) << 8 | (bestcolor[0][1] & 0xfc) << 3 | bestcolor[0][2] >> 3) <
        ((bestcolor[1][0] & 0xf8) << 8 | (bestcolor[1][1] & 0xfc) << 3 | bestcolor[1][2] >> 3)
    ):
        testcolor[0][0] = bestcolor[0][0]
        testcolor[0][1] = bestcolor[0][1]
        testcolor[0][2] = bestcolor[0][2]
        testcolor[1][0] = bestcolor[1][0]
        testcolor[1][1] = bestcolor[1][1]
        testcolor[1][2] = bestcolor[1][2]

    else:
        testcolor[1][0] = bestcolor[0][0]
        testcolor[1][1] = bestcolor[0][1]
        testcolor[1][2] = bestcolor[0][2]
        testcolor[0][0] = bestcolor[1][0]
        testcolor[0][1] = bestcolor[1][1]
        testcolor[0][2] = bestcolor[1][2]

    for i in range(3):
        cv[0][i] = testcolor[0][i]
        cv[1][i] = testcolor[1][i]
        cv[2][i] = (testcolor[0][i] * 2 + testcolor[1][i]) // 3
        cv[3][i] = (testcolor[0][i] + testcolor[1][i] * 2) // 3

    blockerrlin[0][0] = 0
    blockerrlin[0][1] = 0
    blockerrlin[0][2] = 0
    blockerrlin[1][0] = 0
    blockerrlin[1][1] = 0
    blockerrlin[1][2] = 0

    nrcolor[0] = 0
    nrcolor[1] = 0

    for j in range(numypixels):
        for i in range(numxpixels):
            pixerrorbest = 0xffffffff

            for colors in range(4):
                colordist = srccolors[j][i][0] - (cv[colors][0])
                pixerror = colordist * colordist * 4
                pixerrorred = colordist
                colordist = srccolors[j][i][1] - (cv[colors][1])
                pixerror += colordist * colordist * 16
                pixerrorgreen = colordist
                colordist = srccolors[j][i][2] - (cv[colors][2])
                pixerror += colordist * colordist * 1
                pixerrorblue = colordist

                if pixerror < pixerrorbest:
                    enc = colors
                    pixerrorbest = pixerror
                    pixerrorcolorbest[0] = pixerrorred
                    pixerrorcolorbest[1] = pixerrorgreen
                    pixerrorcolorbest[2] = pixerrorblue

            if enc == 0:
                for z in range(3):
                    blockerrlin[0][z] += 3 * pixerrorcolorbest[z]

                nrcolor[0] += 3

            elif enc == 2:
                for z in range(3):
                    blockerrlin[0][z] += 2 * pixerrorcolorbest[z]

                nrcolor[0] += 2

                for z in range(3):
                   blockerrlin[1][z] += 1 * pixerrorcolorbest[z]

                nrcolor[1] += 1

            elif enc == 3:
                for z in range(3):
                   blockerrlin[0][z] += 1 * pixerrorcolorbest[z]

                nrcolor[0] += 1

                for z in range(3):
                   blockerrlin[1][z] += 2 * pixerrorcolorbest[z]

                nrcolor[1] += 2

            elif enc == 1:
                for z in range(3):
                   blockerrlin[1][z] += 3 * pixerrorcolorbest[z]

                nrcolor[1] += 3

    if nrcolor[0] == 0:
        nrcolor[0] = 1

    if nrcolor[1] == 0:
        nrcolor[1] = 1

    cdef int newvalue

    for j in range(2):
        for i in range(3):
            newvalue = testcolor[j][i] + blockerrlin[j][i] // nrcolor[j]
            if newvalue <= 0:
                testcolor[j][i] = 0

            elif newvalue >= 255:
                testcolor[j][i] = 255

            else:
                testcolor[j][i] = newvalue

    cdef:
        u8 coldiffred, coldiffgreen, coldiffblue, coldiffmax, factor, ind0, ind1

    if (
        abs(testcolor[0][0] - testcolor[1][0]) < 8
        and abs(testcolor[0][1] - testcolor[1][1]) < 4
        and abs(testcolor[0][2] - testcolor[1][2]) < 8
    ):
        # both colors are so close they might get encoded as the same 16bit values
        coldiffred = abs(testcolor[0][0] - testcolor[1][0])
        coldiffgreen = 2 * abs(testcolor[0][1] - testcolor[1][1])
        coldiffblue = abs(testcolor[0][2] - testcolor[1][2])
        coldiffmax = coldiffred

        if coldiffmax < coldiffgreen:
            coldiffmax = coldiffgreen

        if coldiffmax < coldiffblue:
            coldiffmax = coldiffblue

        if coldiffmax > 0:
            if coldiffmax > 4:
                factor = 2

            elif coldiffmax > 2:
                factor = 3

            else:
                factor = 4

            # Won't do much if the color value is near 255...
            # argh so many ifs
            if testcolor[1][1] >= testcolor[0][1]:
                ind1 = 1; ind0 = 0

            else:
                ind1 = 0; ind0 = 1

            if (testcolor[ind1][1] + factor * coldiffgreen) <= 255:
                testcolor[ind1][1] += factor * coldiffgreen

            else:
                testcolor[ind1][1] = 255

            if (testcolor[ind1][0] - testcolor[ind0][1]) > 0:
                if (testcolor[ind1][0] + factor * coldiffred) <= 255:
                    testcolor[ind1][0] += factor * coldiffred

                else:
                    testcolor[ind1][0] = 255

            else:
                if (testcolor[ind0][0] + factor * coldiffred) <= 255:
                    testcolor[ind0][0] += factor * coldiffred

                else:
                    testcolor[ind0][0] = 255

            if (testcolor[ind1][2] - testcolor[ind0][2]) > 0:
                if (testcolor[ind1][2] + factor * coldiffblue) <= 255:
                    testcolor[ind1][2] += factor * coldiffblue

                else:
                    testcolor[ind1][2] = 255

            else:
                if (testcolor[ind0][2] + factor * coldiffblue) <= 255:
                    testcolor[ind0][2] += factor * coldiffblue

                else:
                    testcolor[ind0][2] = 255

    if (
        ((testcolor[0][0] & 0xf8) << 8 | (testcolor[0][1] & 0xfc) << 3 | testcolor[0][2] >> 3) <
        ((testcolor[1][0] & 0xf8) << 8 | (testcolor[1][1] & 0xfc) << 3 | testcolor[1][2] >> 3)
    ):
        for i in range(3):
            bestcolor[0][i] = testcolor[0][i]
            bestcolor[1][i] = testcolor[1][i]

    else:
        for i in range(3):
            bestcolor[0][i] = testcolor[1][i]
            bestcolor[1][i] = testcolor[0][i]


cdef void storedxtencodedblock(u8 *blkaddr, u8 srccolors[4][4][4], u8 *bestcolor[2],
                               int numxpixels, int numypixels):

    # use same luminance-weighted distance metric to determine encoding as for finding the base colors

    cdef:
        int i, j, colors
        u32 testerror, testerror2, pixerror, pixerrorbest
        int colordist
        u16 color0, color1, tempcolor
        u32 bits = 0, bits2 = 0
        u8 *colorptr
        u8 enc = 0
        u8 cv[4][4]

    bestcolor[0][0] = bestcolor[0][0] & 0xf8
    bestcolor[0][1] = bestcolor[0][1] & 0xfc
    bestcolor[0][2] = bestcolor[0][2] & 0xf8
    bestcolor[1][0] = bestcolor[1][0] & 0xf8
    bestcolor[1][1] = bestcolor[1][1] & 0xfc
    bestcolor[1][2] = bestcolor[1][2] & 0xf8

    color0 = bestcolor[0][0] << 8 | bestcolor[0][1] << 3 | bestcolor[0][2] >> 3
    color1 = bestcolor[1][0] << 8 | bestcolor[1][1] << 3 | bestcolor[1][2] >> 3

    if color0 < color1:
        tempcolor = color0; color0 = color1; color1 = tempcolor
        colorptr = bestcolor[0]; bestcolor[0] = bestcolor[1]; bestcolor[1] = colorptr

    for i in range(3):
        cv[0][i] = bestcolor[0][i]
        cv[1][i] = bestcolor[1][i]
        cv[2][i] = (bestcolor[0][i] * 2 + bestcolor[1][i]) // 3
        cv[3][i] = (bestcolor[0][i] + bestcolor[1][i] * 2) // 3

    testerror = 0
    for j in range(numypixels):
        for i in range(numxpixels):
            pixerrorbest = 0xffffffff

            for colors in range(4):
                colordist = srccolors[j][i][0] - cv[colors][0]
                pixerror = colordist * colordist * 4
                colordist = srccolors[j][i][1] - cv[colors][1]
                pixerror += colordist * colordist * 16
                colordist = srccolors[j][i][2] - cv[colors][2]
                pixerror += colordist * colordist * 1

                if pixerror < pixerrorbest:
                    pixerrorbest = pixerror
                    enc = colors

            testerror += pixerrorbest
            bits |= enc << (2 * (j * 4 + i))

    for i in range(3):
        cv[2][i] = (bestcolor[0][i] + bestcolor[1][i]) // 2
        # this isn't used. Looks like the black color constant can only be used
        # with RGB_DXT1 if I read the spec correctly (note though that the radeon gpu disagrees,
        # it will decode 3 to black even with DXT3/5), and due to how the color searching works
        # it won't get used even then
        cv[3][i] = 0

    testerror2 = 0
    for j in range(numypixels):
        for i in range(numxpixels):
            pixerrorbest = 0xffffffff

            # we're calculating the same what we have done already for colors 0-1 above...
            for colors in range(3):
                colordist = srccolors[j][i][0] - cv[colors][0]
                pixerror = colordist * colordist * 4
                colordist = srccolors[j][i][1] - cv[colors][1]
                pixerror += colordist * colordist * 16
                colordist = srccolors[j][i][2] - cv[colors][2]
                pixerror += colordist * colordist * 1

                if pixerror < pixerrorbest:
                    pixerrorbest = pixerror

                    # need to exchange colors later
                    if colors > 1:
                        enc = colors

                    else:
                        enc = colors ^ 1

            testerror2 += pixerrorbest
            bits2 |= enc << (2 * (j * 4 + i))

    # finally we're finished, write back colors and bits
    if testerror > testerror2:
        blkaddr[0] = color1 & 0xff; blkaddr += 1
        blkaddr[0] = color1 >> 8; blkaddr += 1
        blkaddr[0] = color0 & 0xff; blkaddr += 1
        blkaddr[0] = color0 >> 8; blkaddr += 1
        blkaddr[0] = bits2 & 0xff; blkaddr += 1
        blkaddr[0] = (bits2 >> 8) & 0xff; blkaddr += 1
        blkaddr[0] = (bits2 >> 16) & 0xff; blkaddr += 1
        blkaddr[0] = bits2 >> 24

    else:
        blkaddr[0] = color0 & 0xff; blkaddr += 1
        blkaddr[0] = color0 >> 8; blkaddr += 1
        blkaddr[0] = color1 & 0xff; blkaddr += 1
        blkaddr[0] = color1 >> 8; blkaddr += 1
        blkaddr[0] = bits & 0xff; blkaddr += 1
        blkaddr[0] = (bits >> 8) & 0xff; blkaddr += 1
        blkaddr[0] = (bits >> 16) & 0xff; blkaddr += 1
        blkaddr[0] = bits >> 24


cdef void encodedxtcolorblockfaster(u8 *blkaddr, u8 srccolors[4][4][4],
                                    int numxpixels, int numypixels):

    # simplistic approach. We need two base colors, simply use the "highest" and the "lowest" color
    # present in the picture as base colors

    # define lowest and highest color as shortest and longest vector to 0/0/0, though the
    # vectors are weighted similar to their importance in rgb-luminance conversion
    # doesn't work too well though...
    # This seems to be a rather difficult problem

    cdef:
        u8 *bestcolor[2]
        u8 basecolors[2][3]
        u8 i, j
        u32 lowcv, highcv, testcv

    lowcv = highcv = (srccolors[0][0][0] * srccolors[0][0][0] * 4
                      + srccolors[0][0][1] * srccolors[0][0][1] * 16
                      + srccolors[0][0][2] * srccolors[0][0][2] * 1)

    bestcolor[0] = bestcolor[1] = srccolors[0][0]
    for j in range(numypixels):
        for i in range(numxpixels):
            # don't use this as a base color if the pixel will get black/transparent anyway
            testcv = (srccolors[j][i][0] * srccolors[j][i][0] * 4
                      + srccolors[j][i][1] * srccolors[j][i][1] * 16
                      + srccolors[j][i][2] * srccolors[j][i][2] * 1)

            if testcv > highcv:
                highcv = testcv
                bestcolor[1] = srccolors[j][i]

            elif testcv < lowcv:
                lowcv = testcv
                bestcolor[0] = srccolors[j][i]

    # make sure the original color values won't get touched...
    for j in range(2):
        for i in range(3):
         basecolors[j][i] = bestcolor[j][i]

    bestcolor[0] = basecolors[0]
    bestcolor[1] = basecolors[1]

    # try to find better base colors
    fancybasecolorsearch(srccolors, bestcolor, numxpixels, numypixels)

    # find the best encoding for these colors, and store the result
    storedxtencodedblock(blkaddr, srccolors, bestcolor, numxpixels, numypixels)


cdef void writedxt5encodedalphablock(u8 *blkaddr, u8 alphabase1, u8 alphabase2, u8 alphaenc[16]):
    blkaddr[0] = alphabase1; blkaddr += 1
    blkaddr[0] = alphabase2; blkaddr += 1
    blkaddr[0] = alphaenc[0] | (alphaenc[1] << 3) | ((alphaenc[2] & 3) << 6); blkaddr += 1
    blkaddr[0] = (alphaenc[2] >> 2) | (alphaenc[3] << 1) | (alphaenc[4] << 4) | ((alphaenc[5] & 1) << 7); blkaddr += 1
    blkaddr[0] = (alphaenc[5] >> 1) | (alphaenc[6] << 2) | (alphaenc[7] << 5); blkaddr += 1
    blkaddr[0] = alphaenc[8] | (alphaenc[9] << 3) | ((alphaenc[10] & 3) << 6); blkaddr += 1
    blkaddr[0] = (alphaenc[10] >> 2) | (alphaenc[11] << 1) | (alphaenc[12] << 4) | ((alphaenc[13] & 1) << 7); blkaddr += 1
    blkaddr[0] = (alphaenc[13] >> 1) | (alphaenc[14] << 2) | (alphaenc[15] << 5); blkaddr += 1


cdef void encodedxt5alpha(u8 *blkaddr, u8 srccolors[4][4][4],
                            int numxpixels, int numypixels):

    cdef:
        u8 alphabase[2], alphause[2]
        int16 alphatest[2]
        u32 alphablockerror1, alphablockerror2, alphablockerror3
        u8 i, j, aindex, acutValues[7]
        u8 alphaenc1[16], alphaenc2[16], alphaenc3[16]
        u8 alphaabsmin = 0
        u8 alphaabsmax = 0
        int16 alphadist

    # find lowest and highest alpha value in block, alphabase[0] lowest, alphabase[1] highest
    alphabase[0] = 0xff; alphabase[1] = 0x0
    for j in range(numypixels):
        for i in range(numxpixels):
            if srccolors[j][i][3] == 0:
                alphaabsmin = 1
            elif srccolors[j][i][3] == 255:
                alphaabsmax = 1
            else:
                if srccolors[j][i][3] > alphabase[1]:
                    alphabase[1] = srccolors[j][i][3]
                if srccolors[j][i][3] < alphabase[0]:
                    alphabase[0] = srccolors[j][i][3]

    if (alphabase[0] > alphabase[1]) and not (alphaabsmin and alphaabsmax):  # one color, either max or min
        # shortcut here since it is a very common case (and also avoids later problems)
        # or (alphabase[0] == alphabase[1] and not alphaabsmin and not alphaabsmax)
        # could also thest for alpha0 == alpha1 (and not min/max), but probably not common, so don't bother

        blkaddr[0] = srccolors[0][0][3]; blkaddr += 1
        blkaddr += 1
        blkaddr[0] = 0; blkaddr += 1
        blkaddr[0] = 0; blkaddr += 1
        blkaddr[0] = 0; blkaddr += 1
        blkaddr[0] = 0; blkaddr += 1
        blkaddr[0] = 0; blkaddr += 1
        blkaddr[0] = 0; blkaddr += 1

        return

    # find best encoding for alpha0 > alpha1
    #  it's possible this encoding is better even if both alphaabsmin and alphaabsmax are true
    alphablockerror1 = 0x0
    alphablockerror2 = 0xffffffff
    alphablockerror3 = 0xffffffff

    if alphaabsmin:
        alphause[0] = 0

    else:
        alphause[0] = alphabase[0]

    if alphaabsmax:
        alphause[1] = 255

    else:
        alphause[1] = alphabase[1]

    # calculate the 7 cut values, just the middle between 2 of the computed alpha values
    for aindex in range(7):
        # don't forget here is always rounded down
        acutValues[aindex] = (alphause[0] * (2 * aindex + 1) + alphause[1] * (14 - (2 * aindex + 1))) // 14

    for j in range(numypixels):
        for i in range(numxpixels):
            # maybe it's overkill to have the most complicated calculation just for the error
            # calculation which we only need to figure out if encoding1 or encoding2 is better...
            if srccolors[j][i][3] > acutValues[0]:
                alphaenc1[4 * j + i] = 0
                alphadist = srccolors[j][i][3] - alphause[1]

            elif srccolors[j][i][3] > acutValues[1]:
                alphaenc1[4 * j + i] = 2
                alphadist = srccolors[j][i][3] - (alphause[1] * 6 + alphause[0] * 1) // 7

            elif srccolors[j][i][3] > acutValues[2]:
                alphaenc1[4 * j + i] = 3
                alphadist = srccolors[j][i][3] - (alphause[1] * 5 + alphause[0] * 2) // 7

            elif srccolors[j][i][3] > acutValues[3]:
                alphaenc1[4 * j + i] = 4
                alphadist = srccolors[j][i][3] - (alphause[1] * 4 + alphause[0] * 3) // 7

            elif srccolors[j][i][3] > acutValues[4]:
                alphaenc1[4 * j + i] = 5
                alphadist = srccolors[j][i][3] - (alphause[1] * 3 + alphause[0] * 4) // 7

            elif srccolors[j][i][3] > acutValues[5]:
                alphaenc1[4 * j + i] = 6
                alphadist = srccolors[j][i][3] - (alphause[1] * 2 + alphause[0] * 5) // 7

            elif srccolors[j][i][3] > acutValues[6]:
                alphaenc1[4 * j + i] = 7
                alphadist = srccolors[j][i][3] - (alphause[1] * 1 + alphause[0] * 6) // 7

            else:
                alphaenc1[4 * j + i] = 1
                alphadist = srccolors[j][i][3] - alphause[0]

            alphablockerror1 += alphadist * alphadist

    cdef:
        int16 blockerrlin1
        int16 blockerrlin2
        u8 nralphainrangelow
        u8 nralphainrangehigh

    # it's not very likely this encoding is better if both alphaabsmin and alphaabsmax
    # are false but try it anyway
    if alphablockerror1 >= 32:

        # don't bother if encoding is already very good, this condition should also imply
        # we have valid alphabase colors which we absolutely need (alphabase[0] <= alphabase[1])
        alphablockerror2 = 0

        for aindex in range(5):
            # don't forget here is always rounded down
            acutValues[aindex] = (alphabase[0] * (10 - (2 * aindex + 1)) + alphabase[1] * (2 * aindex + 1)) // 10

        for j in range(numypixels):
            for i in range(numxpixels):
                # maybe it's overkill to have the most complicated calculation just for the error
                # calculation which we only need to figure out if encoding1 or encoding2 is better...
                if srccolors[j][i][3] == 0:
                    alphaenc2[4 * j + i] = 6
                    alphadist = 0

                elif srccolors[j][i][3] == 255:
                    alphaenc2[4 * j + i] = 7
                    alphadist = 0

                elif srccolors[j][i][3] <= acutValues[0]:
                    alphaenc2[4 * j + i] = 0
                    alphadist = srccolors[j][i][3] - alphabase[0]

                elif srccolors[j][i][3] <= acutValues[1]:
                    alphaenc2[4 * j + i] = 2
                    alphadist = srccolors[j][i][3] - (alphabase[0] * 4 + alphabase[1] * 1) // 5

                elif srccolors[j][i][3] <= acutValues[2]:
                    alphaenc2[4 * j + i] = 3
                    alphadist = srccolors[j][i][3] - (alphabase[0] * 3 + alphabase[1] * 2) // 5

                elif srccolors[j][i][3] <= acutValues[3]:
                    alphaenc2[4 * j + i] = 4
                    alphadist = srccolors[j][i][3] - (alphabase[0] * 2 + alphabase[1] * 3) // 5

                elif srccolors[j][i][3] <= acutValues[4]:
                    alphaenc2[4 * j + i] = 5
                    alphadist = srccolors[j][i][3] - (alphabase[0] * 1 + alphabase[1] * 4) // 5

                else:
                    alphaenc2[4 * j + i] = 1
                    alphadist = srccolors[j][i][3] - alphabase[1]

                alphablockerror2 += alphadist * alphadist

        # skip this if the error is already very small
        # this encoding is MUCH better on average than #2 though, but expensive!
        if (alphablockerror2 > 96) and (alphablockerror1 > 96):
            blockerrlin1 = 0
            blockerrlin2 = 0
            nralphainrangelow = 0
            nralphainrangehigh = 0
            alphatest[0] = 0xff
            alphatest[1] = 0x0

            # if we have large range it's likely there are values close to 0/255, try to map them to 0/255
            for j in range(numypixels):
                for i in range(numxpixels):
                    if (srccolors[j][i][3] > alphatest[1]) and (srccolors[j][i][3] < (255 -(alphabase[1] - alphabase[0]) // 28)):
                        alphatest[1] = srccolors[j][i][3]
                    if (srccolors[j][i][3] < alphatest[0]) and (srccolors[j][i][3] > (alphabase[1] - alphabase[0]) // 28):
                        alphatest[0] = srccolors[j][i][3]

            # shouldn't happen too often, don't really care about those degenerated cases
            if alphatest[1] <= alphatest[0]:
                alphatest[0] = 1
                alphatest[1] = 254

            for aindex in range(5):
                # don't forget here is always rounded down
                acutValues[aindex] = (alphatest[0] * (10 - (2*aindex + 1)) + alphatest[1] * (2*aindex + 1)) // 10

            # find the "average" difference between the alpha values and the next encoded value.
            # This is then used to calculate new base values.
            # Should there be some weighting, i.e. those values closer to alphatest[x] have more weight,
            # since they will see more improvement, and also because the values in the middle are somewhat
            # likely to get no improvement at all (because the base values might move in different directions)?
            # OTOH it would mean the values in the middle are even less likely to get an improvement

            for j in range(numypixels):
                for i in range(numxpixels):
                    if srccolors[j][i][3] <= alphatest[0] // 2:
                        pass

                    elif srccolors[j][i][3] > ((255 + alphatest[1]) // 2):
                        pass

                    elif srccolors[j][i][3] <= acutValues[0]:
                        blockerrlin1 += (srccolors[j][i][3] - alphatest[0])
                        nralphainrangelow += 1

                    elif srccolors[j][i][3] <= acutValues[1]:
                        blockerrlin1 += (srccolors[j][i][3] - (alphatest[0] * 4 + alphatest[1] * 1) // 5)
                        blockerrlin2 += (srccolors[j][i][3] - (alphatest[0] * 4 + alphatest[1] * 1) // 5)
                        nralphainrangelow += 1
                        nralphainrangehigh += 1

                    elif srccolors[j][i][3] <= acutValues[2]:
                        blockerrlin1 += (srccolors[j][i][3] - (alphatest[0] * 3 + alphatest[1] * 2) // 5)
                        blockerrlin2 += (srccolors[j][i][3] - (alphatest[0] * 3 + alphatest[1] * 2) // 5)
                        nralphainrangelow += 1
                        nralphainrangehigh += 1

                    elif srccolors[j][i][3] <= acutValues[3]:
                        blockerrlin1 += (srccolors[j][i][3] - (alphatest[0] * 2 + alphatest[1] * 3) // 5)
                        blockerrlin2 += (srccolors[j][i][3] - (alphatest[0] * 2 + alphatest[1] * 3) // 5)
                        nralphainrangelow += 1
                        nralphainrangehigh += 1

                    elif srccolors[j][i][3] <= acutValues[4]:
                        blockerrlin1 += (srccolors[j][i][3] - (alphatest[0] * 1 + alphatest[1] * 4) // 5)
                        blockerrlin2 += (srccolors[j][i][3] - (alphatest[0] * 1 + alphatest[1] * 4) // 5)
                        nralphainrangelow += 1
                        nralphainrangehigh += 1

                    else:
                        blockerrlin2 += (srccolors[j][i][3] - alphatest[1])
                        nralphainrangehigh += 1

            # shouldn't happen often, needed to avoid div by zero
            if nralphainrangelow == 0:
                nralphainrangelow = 1

            if nralphainrangehigh == 0:
                nralphainrangehigh = 1

            alphatest[0] = alphatest[0] + (blockerrlin1 // nralphainrangelow)

            # again shouldn't really happen often...
            if alphatest[0] < 0:
                alphatest[0] = 0

            alphatest[1] = alphatest[1] + (blockerrlin2 // nralphainrangehigh)
            if alphatest[1] > 255:
                alphatest[1] = 255

            alphablockerror3 = 0

            for aindex in range(5):
                # don't forget here is always rounded down
                acutValues[aindex] = (alphatest[0] * (10 - (2 * aindex + 1)) + alphatest[1] * (2 * aindex + 1)) // 10

            for j in range(numypixels):
                for i in range(numxpixels):
                    # maybe it's overkill to have the most complicated calculation just for the error
                    # calculation which we only need to figure out if encoding1 or encoding2 is better...
                    if srccolors[j][i][3] <= alphatest[0] // 2:
                        alphaenc3[4 * j + i] = 6
                        alphadist = srccolors[j][i][3]

                    elif srccolors[j][i][3] > ((255 + alphatest[1]) // 2):
                        alphaenc3[4 * j + i] = 7
                        alphadist = 255 - srccolors[j][i][3]

                    elif srccolors[j][i][3] <= acutValues[0]:
                        alphaenc3[4 * j + i] = 0
                        alphadist = srccolors[j][i][3] - alphatest[0]

                    elif srccolors[j][i][3] <= acutValues[1]:
                        alphaenc3[4 * j + i] = 2
                        alphadist = srccolors[j][i][3] - (alphatest[0] * 4 + alphatest[1] * 1) // 5

                    elif srccolors[j][i][3] <= acutValues[2]:
                          alphaenc3[4 * j + i] = 3
                          alphadist = srccolors[j][i][3] - (alphatest[0] * 3 + alphatest[1] * 2) // 5

                    elif srccolors[j][i][3] <= acutValues[3]:
                          alphaenc3[4 * j + i] = 4
                          alphadist = srccolors[j][i][3] - (alphatest[0] * 2 + alphatest[1] * 3) // 5

                    elif srccolors[j][i][3] <= acutValues[4]:
                          alphaenc3[4 * j + i] = 5
                          alphadist = srccolors[j][i][3] - (alphatest[0] * 1 + alphatest[1] * 4) // 5

                    else:
                        alphaenc3[4 * j + i] = 1
                        alphadist = srccolors[j][i][3] - alphatest[1]

                    alphablockerror3 += alphadist * alphadist

    # write the alpha values and encoding back.
    if (alphablockerror1 <= alphablockerror2) and (alphablockerror1 <= alphablockerror3):
        writedxt5encodedalphablock(blkaddr, alphause[1], alphause[0], alphaenc1)

    elif alphablockerror2 <= alphablockerror3:
        writedxt5encodedalphablock(blkaddr, alphabase[0], alphabase[1], alphaenc2)

    else:
        writedxt5encodedalphablock(blkaddr, <u8>alphatest[0], <u8>alphatest[1], alphaenc3)


cdef void extractsrccolors(u8 srcpixels[4][4][4], u8 *srcaddr, int srcRowStride,
                           int numxpixels, int numypixels):

    cdef:
        u8 i, j, c
        u8 *curaddr

    for j in range(numypixels):
        curaddr = srcaddr + j * srcRowStride * 4
        for i in range(numxpixels):
            for c in range(4):
                srcpixels[j][i][c] = curaddr[0]; curaddr += 1


cpdef bytearray compress(bytes src, int width, int height):
    cdef:
        array.array dataArr = array.array('B', src)
        u8 *srcPixData = dataArr.data.as_uchars
        u8 *srcaddr = srcPixData
        u8 *srcend = srcPixData + len(src)

        u32 dest_len = ((width + 3) // 4) * ((height + 3) // 4) * 16
        u8 *dest = <u8 *>malloc(dest_len)
        u8 *blkaddr = dest

        int dstRowStride = ((width + 3) // 4) * 16

        u8 srcpixels[4][4][4]
        int numxpixels, numypixels
        int i, j
        int dstRowDiff

    if dstRowStride >= (width * 4):
        dstRowDiff = dstRowStride - (((width + 3) & ~3) * 4)

    else:
        dstRowDiff = 0

    try:
        for j in range(0, height, 4):
            if height > j + 3:
                numypixels = 4

            else:
                numypixels = height - j

            srcaddr = srcPixData + j * width * 4
            if srcaddr >= srcend:
                break

            for i in range(0, width, 4):
                if width > i + 3:
                    numxpixels = 4

                else:
                    numxpixels = width - i

                extractsrccolors(srcpixels, srcaddr, width, numxpixels, numypixels)
                encodedxt5alpha(blkaddr, srcpixels, numxpixels, numypixels)
                encodedxtcolorblockfaster(blkaddr + 8, srcpixels, numxpixels, numypixels)
                srcaddr += 4 * numxpixels
                blkaddr += 16

            blkaddr += dstRowDiff

        return bytearray(<u8[:dest_len]>dest)

    finally:
        free(dest)
