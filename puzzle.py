#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Puzzle NSMBU
# This is Puzzle 0.6, ported to Python 3 & PyQt5, and then ported to support the New Super Mario Bros. U tileset format.
# Puzzle 0.6 by Tempus; all improvements for Python 3, PyQt5 and NSMBU by RoadrunnerWMC and AboodXD

import json
import os
import os.path
import platform
import struct
import sys

from ctypes import create_string_buffer
from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

import globals
import SarcLib
from tileset import HandleTilesetEdited, loadGTX, writeGTX


########################################################
# To Do:
#
#   - Object Editor
#       - Moving objects around
#
#   - Make UI simpler for Pop
#   - Animated Tiles
#   - fix up conflicts with different types of parameters
#   - C speed saving
#   - quick settings for applying to mulitple slopes
#
########################################################


Tileset = None
PuzzleVersion = '2.7'

#############################################################################################
########################## Tileset Class and Tile/Object Subclasses #########################

class TilesetClass:
    '''Contains Tileset data. Inits itself to a blank tileset.
    Methods: addTile, removeTile, addObject, removeObject, clear'''

    class Tile:
        def __init__(self, image, nml, bytelist):
            '''Tile Constructor'''

            self.image = image
            self.normalmap = nml
            self.byte0 = bytelist[0]
            self.byte1 = bytelist[1]
            self.byte2 = bytelist[2]
            self.byte3 = bytelist[3]
            self.byte4 = bytelist[4]
            self.byte5 = bytelist[5]
            self.byte6 = bytelist[6]
            self.byte7 = bytelist[7]


    class Object:

        def __init__(self, height, width, randByte, uslope, lslope, tilelist):
            '''Tile Constructor'''

            self.height = height
            self.width = width

            self.randX = (randByte >> 4) & 1
            self.randY = (randByte >> 5) & 1
            self.randLen = randByte & 0xF

            self.upperslope = uslope
            self.lowerslope = lslope

            self.tiles = tilelist


        def getRandByte(self):
            """
            Builds the Randomization byte.
            """
            if (self.width, self.height) != (1, 1): return 0
            if self.randX + self.randY == 0: return 0
            byte = 0
            if self.randX: byte |= 16
            if self.randY: byte |= 32
            return byte | (self.randLen & 0xF)


    def __init__(self):
        '''Constructor'''

        self.tiles = []
        self.objects = []

        self.slot = 0


    def addTile(self, image, nml, bytelist = (0, 0, 0, 0, 0, 0, 0, 0)):
        '''Adds an tile class to the tile list with the passed image or parameters'''

        self.tiles.append(self.Tile(image, nml, bytelist))


    def addObject(self, height = 1, width = 1, randByte = 0, uslope = [0, 0], lslope = [0, 0], tilelist = [[(0, 0, 0)]]):
        '''Adds a new object'''

        global Tileset

        if tilelist == [[(0, 0, 0)]]:
            tilelist = [[(0, 0, Tileset.slot)]]

        self.objects.append(self.Object(height, width, randByte, uslope, lslope, tilelist))


    def removeObject(self, index):
        '''Removes an Object by Index number. Don't use this much, because we want objects to preserve their ID.'''

        try:
            self.objects.pop(index)

        except IndexError:
            pass


    def clear(self):
        '''Clears the tileset for a new file'''

        self.tiles = []
        self.objects = []


    def getUsedTiles(self):
        usedTiles = []

        for object in self.objects:
            for i in range(len(object.tiles)):
                for tile in object.tiles[i]:
                    if not tile[2] & 3 and Tileset.slot:  # Pa0 tile 0 used in another slot, don't count it
                        continue

                    if object.randLen > 0:
                        for i in range(object.randLen):
                            if tile[1] + i not in usedTiles:
                                usedTiles.append(tile[1] + i)

                    else:
                        if tile[1] not in usedTiles:
                            usedTiles.append(tile[1])

        return usedTiles


#############################################################################################
######################### Palette for painting behaviours to tiles ##########################


class paletteWidget(QtWidgets.QWidget):

    def __init__(self, window):
        super(paletteWidget, self).__init__(window)


        # Core Types Radio Buttons and Tooltips
        self.coreType = QtWidgets.QGroupBox()
        self.coreType.setTitle('Core Type:')
        self.coreWidgets = []
        coreLayout = QtWidgets.QGridLayout()

        path = globals.miyamoto_path + '/miyamotodata/Icons/'

        self.coreTypes = [  ['Default', QtGui.QIcon(path + 'Core/Default.png'), 'The standard type for tiles.\n\nAny regular terrain or backgrounds\nshould be of this generic type.'],
                            ['Rails', QtGui.QIcon(path + 'Core/Rails.png'), 'Used for all types of rails.\n\nRails are replaced in-game with\n3D models, so modifying these\ntiles with different graphics\nwill have no effect.'],
                            ['Dash Coin', QtGui.QIcon(path + 'Core/DashCoin.png'), 'Creates a dash coin.\n\nDash coins, also known as\n"coin outlines," turn into\na coin a second or so after they\nare touched by the player.'],
                            ['Coin', QtGui.QIcon(path + 'Core/Coin.png'), 'Creates a coin.\n\nCoins have no solid collision,\nand when touched will disappear\nand increment the coin counter.\nUnused Blue Coins go in this\ncategory, too.'],
                            ['Blue Coin', QtGui.QIcon(path + 'Core/BlueCoin.png'), 'This is used for the blue coin in Pa0_jyotyu\nthat has a black checkerboard outline.'],
                            ['Used Item Block, Stone Block, Wood Block, Red Block', QtGui.QIcon(path + 'Core/UsedWoodStoneRed.png'), 'Defines a used item block, a stone\nblock, a wooden block or a red block.'],
                            ['Brick Block', QtGui.QIcon(path + 'Core/Brick.png'), 'Defines a brick block.'],
                            ['? Block', QtGui.QIcon(path + 'Core/Qblock.png'), 'Defines a ? block.'],
                            ['Quicksand', QtGui.QIcon(path + 'Core/Quicksand.png'), 'Creates a quicksand area. Use with the "Quicksand" terrain type.'],
                            ['Partial Block', QtGui.QIcon(path + 'Core/Partial.png'), 'DOESN\'T WORK!\n\nUsed for blocks with partial collisions.\n\nVery useful for Mini-Mario secret\nareas, but also for providing a more\naccurate collision map for your tiles.\nUse with the "Solid" setting.'],
                            ['Invisible Block with Item', QtGui.QIcon(path + 'Core/Invisible.png'), 'Used for invisible item blocks.'],
                            ['Slope', QtGui.QIcon(path + 'Core/Slope.png'), 'Defines a sloped tile.\n\nSloped tiles have sloped collisions,\nwhich Mario can slide on.'],
                            ['Reverse Slope', QtGui.QIcon(path + 'Core/RSlope.png'), 'Defines an upside-down slope.\n\nSloped tiles have sloped collisions,\nwhich Mario can hit.'],
                            ['Default 2', QtGui.QIcon(path + 'Core/Default.png'), 'This is an unused type which seems to be the same as Default.'],
                            ['Climbable Wall with Ledge', QtGui.QIcon(path + 'Core/ClimbLedge.png'), 'Creates terrain that can be\nclimbed on, with a ledge at\nthe top.\n\nClimable terrain cannot be walked on.\n\nWhen Mario is on top of a climable\ntile and the player presses up, Mario\nwill enter a climbing state.'],
                            ['Spike', QtGui.QIcon(path + 'Core/Spike.png'), 'Dangerous spikey spikes.\n\nSpike tiles will damage Mario one hit\nwhen they are touched.'],
                            ['Pipe or Pipe Joint', QtGui.QIcon(path + 'Core/Pipe.png'), 'Denotes a pipe tile, or a pipe joint.\n\nPipe tiles are specified according to\nthe part of the pipe. It\'s important\nto specify the right parts or\nentrances may not function correctly.'],
                            ['Conveyor Belt', QtGui.QIcon(path + 'Core/Conveyor.png'), 'Defines moving tiles.\n\nMoving tiles will move Mario in one\ndirection or another.'],
                            ['Donut Block', QtGui.QIcon(path + 'Core/Donut.png'), 'Creates a falling donut block.\n\nThese blocks fall after they have been\nstood on for a few seconds, and then\nrespawn later. They are replaced by\nthe game with 3D models, so you can\'t\neasily make your own.'],
                            ['Cave Entrance', QtGui.QIcon(path + 'Core/Cave.png'), 'Creates a cave entrance.\n\nCave entrances are used to mark secret\nareas hidden behind Layer 0 tiles.'],
                            ['Hanging Ledge/Climbable Wall', QtGui.QIcon(path + 'Core/ClimbLedge.png'), 'Creates a hanging ledge, or terrain that can be\nclimbed on.\n\nYou cannot climb down from the ledge\nif climable terrian is under it,\nand you cannot climb up from the climable terrian\nif the ledge is above it.'],
                            ['Rope', QtGui.QIcon(path + 'Core/Rope.png'), 'Unused type that produces a rope you can hang to. If solidity is set to "None," it will have no effect. "Solid on Top" and "Solid on Bottom" produce no useful behavior.'],
                            ['Climbable Pole', QtGui.QIcon(path + 'Core/Pole.png'), 'Creates a pole that can be climbed. Use with "No Solidity."'],
                        ]

        for i, item in enumerate(self.coreTypes):
            self.coreWidgets.append(QtWidgets.QRadioButton())
            if i in [0, 13]:
                self.coreWidgets[i].setText(item[0])

            else:
                self.coreWidgets[i].setIcon(item[1])

            self.coreWidgets[i].setIconSize(QtCore.QSize(24, 24))
            self.coreWidgets[i].setToolTip('<b>' + item[0] + ':</b><br><br>' + item[2].replace('\n', '<br>'))
            self.coreWidgets[i].clicked.connect(self.swapParams)
            coreLayout.addWidget(self.coreWidgets[i], i // 4, i % 4)

        self.coreWidgets[0].setChecked(True) # make "Default" selected at first
        self.coreType.setLayout(coreLayout)


        # Parameters
        self.parametersGroup = QtWidgets.QGroupBox()
        self.parametersGroup.setTitle('Parameters:')
        parametersLayout = QtWidgets.QVBoxLayout()

        self.parameters1 = QtWidgets.QComboBox()
        self.parameters2 = QtWidgets.QComboBox()
        self.parameters1.setIconSize(QtCore.QSize(24, 24))
        self.parameters2.setIconSize(QtCore.QSize(24, 24))
        self.parameters1.setMinimumHeight(32)
        self.parameters2.setMinimumHeight(32)
        self.parameters1.hide()
        self.parameters2.hide()

        parametersLayout.addWidget(self.parameters1)
        parametersLayout.addWidget(self.parameters2)

        self.parametersGroup.setLayout(parametersLayout)


        GenericParams = [['Normal', QtGui.QIcon(path + 'Core/Default.png')],
                         ['Beanstalk Stop', QtGui.QIcon(path + '/Generic/Beanstopper.png')]]

        RailParams = [['Upslope', QtGui.QIcon(path + 'Rails/Upslope.png')],
                      ['Downslope', QtGui.QIcon(path + 'Rails/Downslope.png')],
                      ['Top-Left Corner', QtGui.QIcon(path + 'Rails/Top-Left Corner.png')],
                      ['Bottom-Right Corner', QtGui.QIcon(path + 'Rails/Bottom-Right Corner.png')],
                      ['Horizontal', QtGui.QIcon(path + 'Rails/Horizontal.png')],
                      ['Vertical', QtGui.QIcon(path + 'Rails/Vertical.png')],
                      ['Blank', QtGui.QIcon()],
                      ['Gentle Upslope 2', QtGui.QIcon(path + 'Rails/Gentle Upslope 2.png')],
                      ['Gentle Upslope 1', QtGui.QIcon(path + 'Rails/Gentle Upslope 1.png')],
                      ['Gentle Downslope 2', QtGui.QIcon(path + 'Rails/Gentle Downslope 2.png')],
                      ['Gentle Downslope 1', QtGui.QIcon(path + 'Rails/Gentle Downslope 1.png')],
                      ['Steep Upslope 2', QtGui.QIcon(path + 'Rails/Steep Upslope 2.png')],
                      ['Steep Upslope 1', QtGui.QIcon(path + 'Rails/Steep Upslope 1.png')],
                      ['Steep Downslope 2', QtGui.QIcon(path + 'Rails/Steep Downslope 2.png')],
                      ['Steep Downslope 1', QtGui.QIcon(path + 'Rails/Steep Downslope 1.png')],
                      ['1x1 Circle', QtGui.QIcon(path + 'Rails/1x1 Circle.png')],
                      ['2x2 Circle Upper Right', QtGui.QIcon(path + 'Rails/2x2 Circle Upper Right.png')],
                      ['2x2 Circle Upper Left', QtGui.QIcon(path + 'Rails/2x2 Circle Upper Left.png')],
                      ['2x2 Circle Lower Right', QtGui.QIcon(path + 'Rails/2x2 Circle Lower Right.png')],
                      ['2x2 Circle Lower Left', QtGui.QIcon(path + 'Rails/2x2 Circle Lower Left.png')],

                      ['4x4 Circle Top Left Corner', QtGui.QIcon(path + 'Rails/4x4 Circle Top Left Corner.png')],
                      ['4x4 Circle Top Left', QtGui.QIcon(path + 'Rails/4x4 Circle Top Left.png')],
                      ['4x4 Circle Top Right', QtGui.QIcon(path + 'Rails/4x4 Circle Top Right.png')],
                      ['4x4 Circle Top Right Corner', QtGui.QIcon(path + 'Rails/4x4 Circle Top Right Corner.png')],

                      ['4x4 Circle Upper Left Side', QtGui.QIcon(path + 'Rails/4x4 Circle Upper Left Side.png')],
                      ['4x4 Circle Upper Right Side', QtGui.QIcon(path + 'Rails/4x4 Circle Upper Right Side.png')],

                      ['4x4 Circle Lower Left Side', QtGui.QIcon(path + 'Rails/4x4 Circle Lower Left Side.png')],
                      ['4x4 Circle Lower Right Side', QtGui.QIcon(path + 'Rails/4x4 Circle Lower Right Side.png')],

                      ['4x4 Circle Bottom Left Corner', QtGui.QIcon(path + 'Rails/4x4 Circle Bottom Left Corner.png')],
                      ['4x4 Circle Bottom Left', QtGui.QIcon(path + 'Rails/4x4 Circle Bottom Left.png')],
                      ['4x4 Circle Bottom Right', QtGui.QIcon(path + 'Rails/4x4 Circle Bottom Right.png')],
                      ['4x4 Circle Bottom Right Corner', QtGui.QIcon(path + 'Rails/4x4 Circle Bottom Right Corner.png')],

                      ['End Stop', QtGui.QIcon()]]

        CoinParams = [['Generic Coin', QtGui.QIcon(path + 'Coin/Coin.png')],
                      ['Nothing', QtGui.QIcon(path + 'Core/Default.png')],
                      ['Blue Coin', QtGui.QIcon(path + 'Coin/BlueCoin.png')]]

        UsedStoneWoodenRedParams = [['Used Item Block', QtGui.QIcon(path + 'UsedStoneWoodenRed/Used.png')],
                                    ['Stone Block', QtGui.QIcon(path + 'UsedStoneWoodenRed/Stone.png')],
                                    ['Wooden Block', QtGui.QIcon(path + 'UsedStoneWoodenRed/Wooden.png')],
                                    ['Red Block', QtGui.QIcon(path + 'UsedStoneWoodenRed/Red.png')]]

        PartialParams = [['Upper Left', QtGui.QIcon(path + 'Partial/UpLeft.png')], 
                         ['Upper Right', QtGui.QIcon(path + 'Partial/UpRight.png')], 
                         ['Top Half', QtGui.QIcon(path + 'Partial/TopHalf.png')], 
                         ['Lower Left', QtGui.QIcon(path + 'Partial/LowLeft.png')], 
                         ['Left Half', QtGui.QIcon(path + 'Partial/LeftHalf.png')], 
                         ['Diagonal Downwards', QtGui.QIcon(path + 'Partial/DiagDn.png')], 
                         ['Upper Left 3/4', QtGui.QIcon(path + 'Partial/UpLeft3-4.png')], 
                         ['Lower Right', QtGui.QIcon(path + 'Partial/LowRight.png')], 
                         ['Diagonal Downwards', QtGui.QIcon(path + 'Partial/DiagDn.png')], 
                         ['Right Half', QtGui.QIcon(path + 'Partial/RightHalf.png')], 
                         ['Upper Right 3/4', QtGui.QIcon(path + 'Partial/UpRig3-4.png')], 
                         ['Lower Half', QtGui.QIcon(path + 'Partial/LowHalf.png')], 
                         ['Lower Left 3/4', QtGui.QIcon(path + 'Partial/LowLeft3-4.png')], 
                         ['Lower Right 3/4', QtGui.QIcon(path + 'Partial/LowRight3-4.png')], 
                         ['Full Brick', QtGui.QIcon(path + 'Partial/Full.png')]]

        SlopeParams = [['Steep Upslope', QtGui.QIcon(path + 'Slope/steepslopeleft.png')],
                       ['Steep Downslope', QtGui.QIcon(path + 'Slope/steepsloperight.png')],
                       ['Upslope 1', QtGui.QIcon(path + 'Slope/slopeleft.png')],
                       ['Upslope 2', QtGui.QIcon(path + 'Slope/slope3left.png')],
                       ['Downslope 1', QtGui.QIcon(path + 'Slope/slope3right.png')],
                       ['Downslope 2', QtGui.QIcon(path + 'Slope/sloperight.png')],
                       ['Very Steep Upslope 1', QtGui.QIcon(path + 'Slope/vsteepup1.png')],
                       ['Very Steep Upslope 2', QtGui.QIcon(path + 'Slope/vsteepup2.png')],
                       ['Very Steep Downslope 1', QtGui.QIcon(path + 'Slope/vsteepdown2.png')],
                       ['Very Steep Downslope 2', QtGui.QIcon(path + 'Slope/vsteepdown1.png')],
                       ['Slope Edge (solid)', QtGui.QIcon(path + 'Slope/edge.png')],
                       ['Gentle Upslope 1', QtGui.QIcon(path + 'Slope/gentleupslope1.png')],
                       ['Gentle Upslope 2', QtGui.QIcon(path + 'Slope/gentleupslope2.png')],
                       ['Gentle Upslope 3', QtGui.QIcon(path + 'Slope/gentleupslope3.png')],
                       ['Gentle Upslope 4', QtGui.QIcon(path + 'Slope/gentleupslope4.png')],
                       ['Gentle Downslope 1', QtGui.QIcon(path + 'Slope/gentledownslope1.png')],
                       ['Gentle Downslope 2', QtGui.QIcon(path + 'Slope/gentledownslope2.png')],
                       ['Gentle Downslope 3', QtGui.QIcon(path + 'Slope/gentledownslope3.png')],
                       ['Gentle Downslope 4', QtGui.QIcon(path + 'Slope/gentledownslope4.png')]]

        ReverseSlopeParams = [['Steep Downslope', QtGui.QIcon(path + 'Slope/Rsteepslopeleft.png')],
                              ['Steep Upslope', QtGui.QIcon(path + 'Slope/Rsteepsloperight.png')],
                              ['Downslope 1', QtGui.QIcon(path + 'Slope/Rslopeleft.png')],
                              ['Downslope 2', QtGui.QIcon(path + 'Slope/Rslope3left.png')],
                              ['Upslope 1', QtGui.QIcon(path + 'Slope/Rslope3right.png')],
                              ['Upslope 2', QtGui.QIcon(path + 'Slope/Rsloperight.png')],
                              ['Very Steep Downslope 1', QtGui.QIcon(path + 'Slope/Rvsteepdown1.png')],
                              ['Very Steep Downslope 2', QtGui.QIcon(path + 'Slope/Rvsteepdown2.png')],
                              ['Very Steep Upslope 1', QtGui.QIcon(path + 'Slope/Rvsteepup2.png')],
                              ['Very Steep Upslope 2', QtGui.QIcon(path + 'Slope/Rvsteepup1.png')],
                              ['Slope Edge (solid)', QtGui.QIcon(path + 'Slope/edge.png')],
                              ['Gentle Downslope 1', QtGui.QIcon(path + 'Slope/Rgentledownslope1.png')],
                              ['Gentle Downslope 2', QtGui.QIcon(path + 'Slope/Rgentledownslope2.png')],
                              ['Gentle Downslope 3', QtGui.QIcon(path + 'Slope/Rgentledownslope3.png')],
                              ['Gentle Downslope 4', QtGui.QIcon(path + 'Slope/Rgentledownslope4.png')],
                              ['Gentle Upslope 1', QtGui.QIcon(path + 'Slope/Rgentleupslope1.png')],
                              ['Gentle Upslope 2', QtGui.QIcon(path + 'Slope/Rgentleupslope2.png')],
                              ['Gentle Upslope 3', QtGui.QIcon(path + 'Slope/Rgentleupslope3.png')],
                              ['Gentle Upslope 4', QtGui.QIcon(path + 'Slope/Rgentleupslope4.png')]]

        SpikeParams = [['No Spikes', QtGui.QIcon(path + 'Unknown.png')],
                       ['No Spikes', QtGui.QIcon(path + 'Unknown.png')],
                       ['Glitchy', QtGui.QIcon(path + 'Unknown.png')],
                       ['Left-Facing Spikes', QtGui.QIcon(path + 'Spikes/SpikeLeft.png')],
                       ['Right-Facing Spikes', QtGui.QIcon(path + 'Spikes/SpikeRight.png')],
                       ['Up-Facing Spikes', QtGui.QIcon(path + 'Spikes/Spike.png')],
                       ['Down-Facing Spikes', QtGui.QIcon(path + 'Spikes/SpikeDown.png')]]

        PipeParams = [['Vert. Top Entrance Left', QtGui.QIcon(path + 'Pipes/UpLeft.png')],
                      ['Vert. Top Entrance Right', QtGui.QIcon(path + 'Pipes/UpRight.png')],
                      ['Vert. Bottom Entrance Left', QtGui.QIcon(path + 'Pipes/DownLeft.png')],
                      ['Vert. Bottom Entrance Right', QtGui.QIcon(path + 'Pipes/DownRight.png')],
                      ['Horiz. Left Entrance Top', QtGui.QIcon(path + 'Pipes/LeftTop.png')],
                      ['Horiz. Left Entrance Bottom', QtGui.QIcon(path + 'Pipes/LeftBottom.png')],
                      ['Horiz. Right Entrance Top', QtGui.QIcon(path + 'Pipes/RightTop.png')],
                      ['Horiz. Right Entrance Bottom', QtGui.QIcon(path + 'Pipes/RightBottom.png')],
                      ['Vert. Mini Pipe Top', QtGui.QIcon(path + 'Pipes/MiniUp.png')],
                      ['Vert. Mini Pipe Bottom', QtGui.QIcon(path + 'Pipes/MiniDown.png')],
                      ['Horiz. Mini Pipe Left', QtGui.QIcon(path + 'Pipes/MiniLeft.png')],
                      ['Horiz. Mini Pipe Right', QtGui.QIcon(path + 'Pipes/MiniRight.png')],
                      ['Vert. Center Left', QtGui.QIcon(path + 'Pipes/VertCenterLeft.png')],
                      ['Vert. Center Right', QtGui.QIcon(path + 'Pipes/VertCenterRight.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['Horiz. Center Top', QtGui.QIcon(path + 'Pipes/HorizCenterTop.png')],
                      ['Horiz. Center Bottom', QtGui.QIcon(path + 'Pipes/HorizCenterBottom.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['Vert. Mini Pipe Center', QtGui.QIcon(path + 'Pipes/MiniVertCenter.png')],
                      ['Horiz. Mini Pipe Center', QtGui.QIcon(path + 'Pipes/MiniHorizCenter.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['UNUSED', QtGui.QIcon(path + 'Unknown.png')],
                      ['Pipe Joint', QtGui.QIcon(path + 'Pipes/Joint.png')]]

        ConveyorParams = [['Left', QtGui.QIcon(path + 'Conveyor/Left.png')],
                          ['Left Fast', QtGui.QIcon(path + 'Conveyor/LeftFast.png')],
                          ['Right', QtGui.QIcon(path + 'Conveyor/Right.png')],
                          ['Right Fast', QtGui.QIcon(path + 'Conveyor/RightFast.png')]]

        CaveParams = [['Left', QtGui.QIcon(path + 'Cave/Left.png')],
                      ['Right', QtGui.QIcon(path + 'Cave/Right.png')]]

        ClimbLedgeParams = [['Hanging Ledge', QtGui.QIcon(path + 'Core/Ledge.png')],
                            ['Climbable Wall', QtGui.QIcon(path + 'Core/Climb.png')]]


        self.ParameterList = [GenericParams, # 0x00
                              RailParams, # 0x01
                              None, # 0x02
                              CoinParams, # 0x03
                              None, # 0x04
                              UsedStoneWoodenRedParams, # 0x05
                              None, # 0x06
                              None, # 0x07
                              None, # 0x08
                              PartialParams, # 0x09
                              None, # 0x0A
                              SlopeParams, # 0x0B
                              ReverseSlopeParams, # 0x0C
                              None, # 0x0D
                              None, # 0x0E
                              SpikeParams, # 0x0F
                              PipeParams, # 0x10
                              ConveyorParams, # 0x11
                              None, # 0x12
                              CaveParams, # 0x13
                              ClimbLedgeParams, # 0x14
                              None, # 0x15
                              None, # 0x16
                              ]


        SpikeParams2 = [['Spikes', QtGui.QIcon(path + 'Spikes/Spikes.png')],
                        ['Muncher (no visible difference)', QtGui.QIcon(path + 'Spikes/Muncher.png')]]

        PipeParams2 = [['Green', QtGui.QIcon(path + 'PipeColors/Green.png')],
                       ['Red', QtGui.QIcon(path + 'PipeColors/Red.png')],
                       ['Yellow', QtGui.QIcon(path + 'PipeColors/Yellow.png')]]

        self.ParameterList2 = [
                            None, # 0x0
                            None, # 0x1
                            None, # 0x2
                            None, # 0x3
                            None, # 0x4
                            None, # 0x5
                            None, # 0x6
                            None, # 0x7
                            None, # 0x8
                            None, # 0x9
                            None, # 0xA
                            None, # 0xB
                            None, # 0xC
                            None, # 0xD
                            None, # 0xE
                            SpikeParams2, # 0xF
                            PipeParams2, # 0x10
                            None, # 0x11
                            None, # 0x12
                            None, # 0x13
                            None, # 0x14
                            None, # 0x15
                            None, # 0x16
                            ]


        # Collision Type
        self.collsType = QtWidgets.QComboBox()
        self.collsGroup = QtWidgets.QGroupBox('Collision Type')
        L = QtWidgets.QVBoxLayout(self.collsGroup)
        L.addWidget(self.collsType)

        self.collsTypes = [['No Solidity', QtGui.QIcon(path + 'Collisions/NoSolidity.png')],
                           ['Solid', QtGui.QIcon(path + 'Collisions/Solid.png')],
                           ['Solid-on-Top', QtGui.QIcon(path + 'Collisions/SolidOnTop.png')],
                           ['Solid-on-Bottom', QtGui.QIcon(path + 'Collisions/SolidOnBottom.png')],
                           ['Sloped Solid-on-Top (1)', QtGui.QIcon(path + 'Collisions/SlopedSolidOnTop.png')],
                           ['Sloped Solid-on-Top (2)', QtGui.QIcon(path + 'Collisions/SlopedSolidOnTop.png')],
                           ]

        for item in self.collsTypes:
            self.collsType.addItem(item[1], item[0])
        self.collsType.setIconSize(QtCore.QSize(24, 24))
        self.collsType.setToolTip('Set the collision style of the terrain.\n\n'

                                    '<b>No Solidity:</b>\nThe tile cannot be stood on or hit.\n\n'
                                    '<b>Solid:</b>\nThe tile can be stood on and hit from all sides.\n\n'
                                    '<b>Solid-on-Top:</b>\nThe tile can only be stood on.\n\n'
                                    '<b>Solid-on-Bottom:</b>\nThe tile can only be hit from below.\n\n'
                                    '<b>Sloped Solid-on-Top (1):</b>\nDoes not seem to work in-game.\n\n'
                                    '<b>Sloped Solid-on-Top (2):</b>\nDoes not seem to work in-game.'.replace('\n', '<br>')
                                   )


        # Terrain Type
        self.terrainType = QtWidgets.QComboBox()
        self.terrainGroup = QtWidgets.QGroupBox('Terrain Type')
        L = QtWidgets.QVBoxLayout(self.terrainGroup)
        L.addWidget(self.terrainType)

        # Quicksand is unused.
        self.terrainTypes = [['Default', QtGui.QIcon(path + 'Core/Default.png')],
                        ['Ice', QtGui.QIcon(path + 'Terrain/Ice.png')],
                        ['Snow', QtGui.QIcon(path + 'Terrain/Snow.png')],
                        ['Quicksand', QtGui.QIcon(path + 'Terrain/Quicksand.png')],
                        ['Sand', QtGui.QIcon(path + 'Terrain/Sand.png')],
                        ['Grass', QtGui.QIcon(path + 'Terrain/Grass.png')],
                        ]

        for item in range(len(self.terrainTypes)):
            self.terrainType.addItem(self.terrainTypes[item][1], self.terrainTypes[item][0])
        self.terrainType.setIconSize(QtCore.QSize(24, 24))
        self.terrainType.setToolTip('Set the various types of terrain.\n\n'

                                    '<b>Default:</b>\nTerrain with no paticular properties.\n\n'
                                    '<b>Ice:</b>\nWill be slippery.\n\n'
                                    '<b>Snow:</b>\nWill emit puffs of snow and snow noises.\n\n'
                                    '<b>Quicksand:</b>\nWill emit puffs of sand. Use with the "Quicksand" core type.\n\n'
                                    '<b>Grass:</b>\nWill emit grass-like footstep noises.\n\n'
                                    '<b>Beach Sand:</b>\nWill create sand tufts around\nMario\'s feet.'.replace('\n', '<br>')
                                   )



        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.coreType)
        layout.addWidget(self.parametersGroup)
        layout.addWidget(self.collsGroup)
        layout.addWidget(self.terrainGroup)
        self.setLayout(layout)

        self.swapParams()


    def swapParams(self):
        for item in range(len(self.ParameterList)):
            if self.coreWidgets[item].isChecked():
                self.parameters1.clear()
                if self.ParameterList[item] is not None:
                    for option in self.ParameterList[item]:
                        self.parameters1.addItem(option[1], option[0])
                    self.parameters1.show()
                else:
                    self.parameters1.hide()
                self.parameters2.clear()
                if self.ParameterList2[item] is not None:
                    for option in self.ParameterList2[item]:
                        self.parameters2.addItem(option[1], option[0])
                    self.parameters2.show()
                else:
                    self.parameters2.hide()



#############################################################################################
######################### InfoBox Custom Widget to display info to ##########################


class InfoBox(QtWidgets.QWidget):
    def __init__(self, window):
        super(InfoBox, self).__init__(window)

        # InfoBox
        superLayout = QtWidgets.QGridLayout()
        infoLayout = QtWidgets.QFormLayout()

        self.imageBox = QtWidgets.QGroupBox()
        imageLayout = QtWidgets.QHBoxLayout()

        pix = QtGui.QPixmap(24, 24)
        pix.fill(Qt.transparent)

        self.coreImage = QtWidgets.QLabel()
        self.coreImage.setPixmap(pix)
        self.terrainImage = QtWidgets.QLabel()
        self.terrainImage.setPixmap(pix)
        self.parameterImage = QtWidgets.QLabel()
        self.parameterImage.setPixmap(pix)


        self.collisionOverlay = QtWidgets.QCheckBox('Overlay Collision')
        self.collisionOverlay.clicked.connect(window.tileDisplay.update)


        self.coreInfo = QtWidgets.QLabel()
        self.propertyInfo = QtWidgets.QLabel('             \n\n\n\n\n')
        self.terrainInfo = QtWidgets.QLabel()
        self.paramInfo = QtWidgets.QLabel()

        Font = self.font()
        Font.setPointSize(9)

        self.coreInfo.setFont(Font)
        self.propertyInfo.setFont(Font)
        self.terrainInfo.setFont(Font)
        self.paramInfo.setFont(Font)


        self.LabelB = QtWidgets.QLabel('Properties:')
        self.LabelB.setFont(Font)

        self.hexdata = QtWidgets.QLabel('Hex Data: 0x00 0x00 0x00 0x00\n                0x00 0x00 0x00 0x00')
        self.hexdata.setFont(Font)


        coreLayout = QtWidgets.QVBoxLayout()
        terrLayout = QtWidgets.QVBoxLayout()
        paramLayout = QtWidgets.QVBoxLayout()

        coreLayout.setGeometry(QtCore.QRect(0,0,40,40))
        terrLayout.setGeometry(QtCore.QRect(0,0,40,40))
        paramLayout.setGeometry(QtCore.QRect(0,0,40,40))


        label = QtWidgets.QLabel('Core')
        label.setFont(Font)
        coreLayout.addWidget(label, 0, Qt.AlignCenter)

        label = QtWidgets.QLabel('Terrain')
        label.setFont(Font)
        terrLayout.addWidget(label, 0, Qt.AlignCenter)

        label = QtWidgets.QLabel('Parameters')
        label.setFont(Font)
        paramLayout.addWidget(label, 0, Qt.AlignCenter)

        coreLayout.addWidget(self.coreImage, 0, Qt.AlignCenter)
        terrLayout.addWidget(self.terrainImage, 0, Qt.AlignCenter)
        paramLayout.addWidget(self.parameterImage, 0, Qt.AlignCenter)

        coreLayout.addWidget(self.coreInfo, 0, Qt.AlignCenter)
        terrLayout.addWidget(self.terrainInfo, 0, Qt.AlignCenter)
        paramLayout.addWidget(self.paramInfo, 0, Qt.AlignCenter)

        imageLayout.setContentsMargins(0,4,4,4)
        imageLayout.addLayout(coreLayout)
        imageLayout.addLayout(terrLayout)
        imageLayout.addLayout(paramLayout)

        self.imageBox.setLayout(imageLayout)


        superLayout.addWidget(self.imageBox, 0, 0)
        superLayout.addWidget(self.collisionOverlay, 1, 0)
        infoLayout.addRow(self.LabelB, self.propertyInfo)
        infoLayout.addRow(self.hexdata)
        superLayout.addLayout(infoLayout, 0, 1, 2, 1)
        self.setLayout(superLayout)




#############################################################################################
##################### Object List Widget and Model Setup with Painter #######################


class objectList(QtWidgets.QListView):

    def __init__(self, parent=None):
        super(objectList, self).__init__(parent)


        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setIconSize(QtCore.QSize(96,96))
        self.setGridSize(QtCore.QSize(114,114))
        self.setMovement(QtWidgets.QListView.Static)
        self.setBackgroundRole(QtGui.QPalette.BrightText)
        self.setWrapping(False)
        self.setMinimumHeight(140)
        self.setMaximumHeight(140)



def SetupObjectModel(self, objects, tiles):
    global Tileset
    self.clear()

    count = 0
    for object in objects:
        tex = QtGui.QPixmap(object.width * 24, object.height * 24)
        tex.fill(Qt.transparent)
        painter = QtGui.QPainter(tex)

        Xoffset = 0
        Yoffset = 0

        for i in range(len(object.tiles)):
            for tile in object.tiles[i]:
                if (Tileset.slot == 0) or ((tile[2] & 3) != 0):
                    painter.drawPixmap(Xoffset, Yoffset, tiles[tile[1]].image.scaledToWidth(24, Qt.SmoothTransformation))
                Xoffset += 24
            Xoffset = 0
            Yoffset += 24

        painter.end()

        self.appendRow(QtGui.QStandardItem(QtGui.QIcon(tex), 'Object {0}'.format(count)))

        count += 1


#############################################################################################
######################## List Widget with custom painter/MouseEvent #########################


class displayWidget(QtWidgets.QListView):

    mouseMoved = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(displayWidget, self).__init__(parent)

        self.setMinimumWidth(426)
        self.setMaximumWidth(426)
        self.setMinimumHeight(404)
        self.setDragEnabled(True)
        self.setViewMode(QtWidgets.QListView.IconMode)
        self.setIconSize(QtCore.QSize(24,24))
        self.setGridSize(QtCore.QSize(25,25))
        self.setMovement(QtWidgets.QListView.Static)
        self.setAcceptDrops(False)
        self.setDropIndicatorShown(True)
        self.setResizeMode(QtWidgets.QListView.Adjust)
        self.setUniformItemSizes(True)
        self.setBackgroundRole(QtGui.QPalette.BrightText)
        self.setMouseTracking(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        self.setItemDelegate(self.TileItemDelegate())


    def mouseMoveEvent(self, event):
        QtWidgets.QWidget.mouseMoveEvent(self, event)

        self.mouseMoved.emit(event.x(), event.y())



    class TileItemDelegate(QtWidgets.QAbstractItemDelegate):
        """Handles tiles and their rendering"""

        def __init__(self):
            """Initialises the delegate"""
            QtWidgets.QAbstractItemDelegate.__init__(self)

        def paint(self, painter, option, index):
            """Paints an object"""

            global Tileset
            p = index.model().data(index, Qt.DecorationRole)
            painter.drawPixmap(option.rect.x(), option.rect.y(), p.pixmap(24,24))

            x = option.rect.x()
            y = option.rect.y()


            # Collision Overlays
            info = window.infoDisplay
            if index.row() >= len(Tileset.tiles): return
            curTile = Tileset.tiles[index.row()]

            if info.collisionOverlay.isChecked():
                path = os.path.dirname(os.path.abspath(sys.argv[0])) + '/Icons/'

                colour = QtGui.QColor(0, 0, 0, 120)

                # Sets the colour based on terrain type
                if curTile.byte5 == 1:      # Ice
                    colour = QtGui.QColor(0, 0, 255, 120)
                elif curTile.byte5 == 2:    # Snow
                    colour = QtGui.QColor(120, 120, 255, 120)
                elif curTile.byte5 == 4:    # Sand
                    colour = QtGui.QColor(128,64,0, 120)
                elif curTile.byte5 == 5:    # Grass
                    colour = QtGui.QColor(0, 255, 0, 120)

                # Sets Brush style for fills
                if curTile.byte0 in [14, 20, 21]:  # Climbing Grid
                    style = Qt.DiagCrossPattern
                elif curTile.byte0 in [5, 6, 7]:  # Breakable
                    style = Qt.Dense5Pattern
                else:
                    style = Qt.SolidPattern


                brush = QtGui.QBrush(colour, style)
                painter.setBrush(brush)
                painter.setRenderHint(QtGui.QPainter.Antialiasing)


                # Paints shape based on other junk
                if curTile.byte0 == 0xB:  # Slope
                    if curTile.byte2 == 0:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y)]))
                    elif curTile.byte2 == 1:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 2:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y + 12)]))
                    elif curTile.byte2 == 3:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x, y + 12),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 24)]))
                    elif curTile.byte2 == 4:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x + 24, y + 24)]))
                    elif curTile.byte2 == 5:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 12),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 6:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 12, y)]))
                    elif curTile.byte2 == 7:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 12, y + 24),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y)]))
                    elif curTile.byte2 == 8:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 12, y),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 9:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 12, y + 24),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 10:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y)]))
                    elif curTile.byte2 == 11:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x + 24, y + 18),
                                                            QtCore.QPoint(x + 24, y + 24)]))
                    elif curTile.byte2 == 12:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x, y + 18),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 13:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y + 6),
                                                            QtCore.QPoint(x, y + 12),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 14:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x, y + 6),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 15:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y + 6),
                                                            QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 16:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x, y + 6),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 17:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y + 18),
                                                            QtCore.QPoint(x, y + 12),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 18:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x, y + 18),
                                                            QtCore.QPoint(x, y + 24)]))

                elif curTile.byte0 == 0xC:  # Reverse Slope
                    if curTile.byte2 == 0:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y)]))
                    elif curTile.byte2 == 1:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y)]))
                    elif curTile.byte2 == 2:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y + 12)]))
                    elif curTile.byte2 == 3:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x, y + 12),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y)]))
                    elif curTile.byte2 == 4:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 12)]))
                    elif curTile.byte2 == 5:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 12),
                                                            QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y)]))
                    elif curTile.byte2 == 6:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 12, y + 24),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x, y)]))
                    elif curTile.byte2 == 7:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 12, y)]))
                    elif curTile.byte2 == 8:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 12, y + 24),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 9:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 12, y),
                                                            QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 10:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y)]))
                    elif curTile.byte2 == 11:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 6)]))
                    elif curTile.byte2 == 12:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x, y + 6)]))
                    elif curTile.byte2 == 13:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 18),
                                                            QtCore.QPoint(x, y + 12)]))
                    elif curTile.byte2 == 14:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x, y + 18)]))
                    elif curTile.byte2 == 15:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 18),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 16:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x, y + 18)]))
                    elif curTile.byte2 == 17:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 6),
                                                            QtCore.QPoint(x, y + 12)]))
                    elif curTile.byte2 == 18:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x, y + 6)]))

                elif curTile.byte0 == 9:  # Partial
                    if curTile.byte2 == 0:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 12, y),
                                                            QtCore.QPoint(x + 12, y + 12),
                                                            QtCore.QPoint(x, y + 12)]))
                    elif curTile.byte2 == 1:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 12, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x + 12, y + 12)]))
                    elif curTile.byte2 == 2:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x, y + 12)]))
                    elif curTile.byte2 == 3:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 12),
                                                            QtCore.QPoint(x + 12, y + 12),
                                                            QtCore.QPoint(x + 12, y + 24),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 4:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 12, y),
                                                            QtCore.QPoint(x + 12, y + 24),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 5:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x + 12, y + 24),
                                                            QtCore.QPoint(x + 12, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x, y + 12)]))
                    elif curTile.byte2 == 6:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x + 12, y + 12),
                                                            QtCore.QPoint(x + 12, y + 24),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 7:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 12, y + 12),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 12, y + 24)]))
                    elif curTile.byte2 == 8:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x, y + 12),
                                                            QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x + 12, y + 24),
                                                            QtCore.QPoint(x + 12, y)]))
                    elif curTile.byte2 == 9:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 12, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 12, y + 24)]))
                    elif curTile.byte2 == 10:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 12, y + 24),
                                                            QtCore.QPoint(x + 12, y + 12),
                                                            QtCore.QPoint(x, y + 12)]))
                    elif curTile.byte2 == 11:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 12),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 12:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 12, y),
                                                            QtCore.QPoint(x + 12, y + 12),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 13:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 12, y),
                                                            QtCore.QPoint(x + 12, y + 12),
                                                            QtCore.QPoint(x, y + 12),
                                                            QtCore.QPoint(x, y + 24)]))
                    elif curTile.byte2 == 14:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x, y + 24)]))

                elif curTile.byte0 == 0 and curTile.byte4 == 3:  # Solid-on-bottom
                    painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 24),
                                                        QtCore.QPoint(x + 24, y + 24),
                                                        QtCore.QPoint(x + 24, y + 18),
                                                        QtCore.QPoint(x, y + 18)]))

                    painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 15, y),
                                                        QtCore.QPoint(x + 15, y + 12),
                                                        QtCore.QPoint(x + 18, y + 12),
                                                        QtCore.QPoint(x + 12, y + 17),
                                                        QtCore.QPoint(x + 6, y + 12),
                                                        QtCore.QPoint(x + 9, y + 12),
                                                        QtCore.QPoint(x + 9, y)]))

                elif curTile.byte0 == 0 and curTile.byte4 == 2:  # Solid-on-top
                    painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                        QtCore.QPoint(x + 24, y),
                                                        QtCore.QPoint(x + 24, y + 6),
                                                        QtCore.QPoint(x, y + 6)]))

                    painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 15, y + 24),
                                                        QtCore.QPoint(x + 15, y + 12),
                                                        QtCore.QPoint(x + 18, y + 12),
                                                        QtCore.QPoint(x + 12, y + 7),
                                                        QtCore.QPoint(x + 6, y + 12),
                                                        QtCore.QPoint(x + 9, y + 12),
                                                        QtCore.QPoint(x + 9, y + 24)]))

                elif curTile.byte0 == 0xF:  # Spikes
                    if curTile.byte2 == 3:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x, y + 6)]))
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 24, y + 12),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x, y + 18)]))
                    elif curTile.byte2 == 4:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x, y + 12),
                                                            QtCore.QPoint(x + 24, y + 6)]))
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 12),
                                                            QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x + 24, y + 18)]))
                    elif curTile.byte2 == 5:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y + 24),
                                                            QtCore.QPoint(x + 12, y + 24),
                                                            QtCore.QPoint(x + 6, y)]))
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 12, y + 24),
                                                            QtCore.QPoint(x + 24, y + 24),
                                                            QtCore.QPoint(x + 18, y)]))
                    elif curTile.byte2 == 6:
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x, y),
                                                            QtCore.QPoint(x + 12, y),
                                                            QtCore.QPoint(x + 6, y + 24)]))
                        painter.drawPolygon(QtGui.QPolygon([QtCore.QPoint(x + 12, y),
                                                            QtCore.QPoint(x + 24, y),
                                                            QtCore.QPoint(x + 18, y + 24)]))

                elif curTile.byte4 == 1:  # Solid
                    painter.drawRect(option.rect)

                else:  # No fill
                    pass


            # Highlight stuff.
            colour = QtGui.QColor(option.palette.highlight())
            colour.setAlpha(80)

            if option.state & QtWidgets.QStyle.State_Selected:
                painter.fillRect(option.rect, colour)


        def sizeHint(self, option, index):
            """Returns the size for the object"""
            return QtCore.QSize(24, 24)



#############################################################################################
############################ Tile widget for drag n'drop Objects ############################


class tileOverlord(QtWidgets.QWidget):

    def __init__(self):
        super(tileOverlord, self).__init__()

        # Setup Widgets
        self.tiles = tileWidget()

        self.addObject = QtWidgets.QPushButton('Add')
        self.removeObject = QtWidgets.QPushButton('Remove')

        self.addRow = QtWidgets.QPushButton('+')
        self.removeRow = QtWidgets.QPushButton('-')

        self.addColumn = QtWidgets.QPushButton('+')
        self.removeColumn = QtWidgets.QPushButton('-')

        self.tilingMethod = QtWidgets.QComboBox()
        self.tilesetType = QtWidgets.QLabel('Pa%d' % Tileset.slot)

        self.tilingMethod.addItems(['Repeat',
                                    'Stretch Center',
                                    'Stretch X',
                                    'Stretch Y',
                                    'Repeat Bottom',
                                    'Repeat Top',
                                    'Repeat Left',
                                    'Repeat Right',
                                    'Upward slope',
                                    'Downward slope',
                                    'Downward reverse slope',
                                    'Upward reverse slope'])

        self.randX = QtWidgets.QCheckBox('Randomize Horizontally')
        self.randY = QtWidgets.QCheckBox('Randomize Vertically')
        self.randX.setToolTip('<b>Randomize Horizontally:</b><br><br>'
            'Check this if you want to use randomized replacements for '
            'this tile, in the <u>horizontal</u> direction. Examples: '
            'floor tiles and ceiling tiles.')
        self.randY.setToolTip('<b>Randomize Vertically:</b><br><br>'
            'Check this if you want to use randomized replacements for '
            'this tile, in the <u>vertical</u> direction. Example: '
            'edge tiles.')

        self.randLenLbl = QtWidgets.QLabel('Total Randomizable Tiles:')
        self.randLen = QtWidgets.QSpinBox()
        self.randLen.setRange(1, 15)
        self.randLen.setEnabled(False)
        self.randLen.setToolTip('<b>Total Randomizable Tiles:</b><br><br>'
            'This specifies the total number of tiles the game may '
            'use for randomized replacements of this tile. This '
            'will be the tile itself, and <i>(n - 1)</i> tiles after it, '
            'where <i>n</i> is the number in this box. Tiles "after" this one '
            'are tiles to the right of it in the tileset image, wrapping '
            'to the next line if the right edge of the image is reached.')


        # Connections
        self.addObject.released.connect(self.addObj)
        self.removeObject.released.connect(self.removeObj)
        self.addRow.released.connect(self.addRowHandler)
        self.removeRow.released.connect(self.removeRowHandler)
        self.addColumn.released.connect(self.addColumnHandler)
        self.removeColumn.released.connect(self.removeColumnHandler)

        self.tilingMethod.activated.connect(self.setTiling)

        self.randX.toggled.connect(self.changeRandX)
        self.randY.toggled.connect(self.changeRandY)
        self.randLen.valueChanged.connect(self.changeRandLen)


        # Layout
        self.randStuff = QtWidgets.QWidget()
        randLyt = QtWidgets.QGridLayout(self.randStuff)
        randLyt.addWidget(self.randX, 0, 0)
        randLyt.addWidget(self.randY, 1, 0)
        randLyt.addWidget(self.randLenLbl, 0, 1)
        randLyt.addWidget(self.randLen, 1, 1)

        layout = QtWidgets.QGridLayout()

        layout.addWidget(self.tilesetType, 0, 0, 1, 3)
        layout.addWidget(self.tilingMethod, 0, 3, 1, 3)

        layout.addWidget(self.addObject, 0, 6, 1, 1)
        layout.addWidget(self.removeObject, 0, 7, 1, 1)

        layout.setRowMinimumHeight(1, 40)

        layout.addWidget(self.randStuff, 1, 0, 1, 8)

        layout.setRowStretch(2, 1)
        layout.setRowStretch(3, 5)
        layout.setRowStretch(6, 5)
        layout.addWidget(self.tiles, 3, 1, 4, 6)

        layout.addWidget(self.addColumn, 4, 7, 1, 1)
        layout.addWidget(self.removeColumn, 5, 7, 1, 1)
        layout.addWidget(self.addRow, 7, 3, 1, 1)
        layout.addWidget(self.removeRow, 7, 4, 1, 1)

        self.setLayout(layout)




    def addObj(self):
        global Tileset

        Tileset.addObject()

        pix = QtGui.QPixmap(24, 24)
        pix.fill(Qt.transparent)
        if Tileset.slot == 0:
            painter = QtGui.QPainter(pix)
            painter.drawPixmap(0, 0, Tileset.tiles[0].image.scaledToWidth(24, Qt.SmoothTransformation))
            painter.end()

        count = len(Tileset.objects)
        window.objmodel.appendRow(QtGui.QStandardItem(QtGui.QIcon(pix), 'Object {0}'.format(count-1)))
        index = window.objectList.currentIndex()
        window.objectList.setCurrentIndex(index)
        self.setObject(index)

        window.objectList.update()
        self.update()


    def removeObj(self):
        global Tileset

        index = window.objectList.currentIndex()

        Tileset.removeObject(index.row())
        window.objmodel.removeRow(index.row())
        self.tiles.clear()

        SetupObjectModel(window.objmodel, Tileset.objects, Tileset.tiles)

        window.objectList.update()
        self.update()


    def setObject(self, index):
        global Tileset
        object = Tileset.objects[index.row()]

        width = len(object.tiles[0])-1
        height = len(object.tiles)-1
        Xuniform = True
        Yuniform = True
        Xstretch = False
        Ystretch = False

        self.randStuff.setVisible((width, height) == (0, 0))
        self.randX.setChecked(object.randX == 1)
        self.randY.setChecked(object.randY == 1)
        self.randLen.setValue(object.randLen)
        self.randLen.setEnabled(object.randX + object.randY > 0)


        for tile in object.tiles[0]:
            if tile[0] != object.tiles[0][0][0]:
                Xuniform = False

        for tile in object.tiles:
            if tile[0][0] != object.tiles[0][0][0]:
                Yuniform = False

        if object.tiles[0][0][0] == object.tiles[0][width][0] and Xuniform == False:
            Xstretch = True

        if object.tiles[0][0][0] == object.tiles[height][0][0] and Xuniform == False:
            Ystretch = True



        if object.upperslope[0] != 0:
            if object.upperslope[0] == 0x90:
                self.tilingMethod.setCurrentIndex(8)
            elif object.upperslope[0] == 0x91:
                self.tilingMethod.setCurrentIndex(9)
            elif object.upperslope[0] == 0x92:
                self.tilingMethod.setCurrentIndex(10)
            elif object.upperslope[0] == 0x93:
                self.tilingMethod.setCurrentIndex(11)

        else:
            if Xuniform and Yuniform:
                self.tilingMethod.setCurrentIndex(0)
            elif Xstretch and Ystretch:
                self.tilingMethod.setCurrentIndex(1)
            elif Xstretch:
                self.tilingMethod.setCurrentIndex(2)
            elif Ystretch:
                self.tilingMethod.setCurrentIndex(3)
            elif Xuniform and Yuniform == False and object.tiles[0][0][0] == 0:
                self.tilingMethod.setCurrentIndex(4)
            elif Xuniform and Yuniform == False and object.tiles[height][0][0] == 0:
                self.tilingMethod.setCurrentIndex(5)
            elif Xuniform == False and Yuniform and object.tiles[0][0][0] == 0:
                self.tilingMethod.setCurrentIndex(6)
            elif Xuniform == False and Yuniform and object.tiles[0][width][0] == 0:
                self.tilingMethod.setCurrentIndex(7)


        self.tiles.setObject(object)

#        print 'Object {0}, Width: {1} / Height: {2}, Slope {3}/{4}'.format(index.row(), object.width, object.height, object.upperslope, object.lowerslope)
#        for row in object.tiles:
#            print 'Row: {0}'.format(row)
#        print ''

    @QtCore.pyqtSlot(int)
    def setTiling(self, listindex):
        global Tileset

        index = window.objectList.currentIndex()
        object = Tileset.objects[index.row()]


        if listindex == 0:  # Repeat
            ctile = 0
            crow = 0

            for row in object.tiles:
                for tile in row:
                    object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    ctile += 1
                crow += 1
                ctile = 0

        if listindex == 1:  # Stretch Center

            if object.width < 3 and object.height < 3:
                reply = QtWidgets.QMessageBox.information(self, "Warning", "An object must be at least 3 tiles\nwide and 3 tiles tall to apply stretch center.")
                self.setObject(index)
                return

            ctile = 0
            crow = 0

            for row in object.tiles:
                for tile in row:
                    if crow == 0 and ctile == 0:
                        object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    elif crow == 0 and ctile == object.width-1:
                        object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    elif crow == object.height-1 and ctile == object.width-1:
                        object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    elif crow == object.height-1 and ctile == 0:
                        object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    elif crow == 0 or crow == object.height-1:
                        object.tiles[crow][ctile] = (1, tile[1], tile[2])
                    elif ctile == 0 or ctile == object.width-1:
                        object.tiles[crow][ctile] = (2, tile[1], tile[2])
                    else:
                        object.tiles[crow][ctile] = (3, tile[1], tile[2])
                    ctile += 1
                crow += 1
                ctile = 0

            object.upperslope = [0, 0]
            object.lowerslope = [0, 0]

        if listindex == 2:  # Stretch X

            if object.width < 3:
                reply = QtWidgets.QMessageBox.information(self, "Warning", "An object must be at least 3 tiles\nwide to apply stretch X.")
                self.setObject(index)
                return

            ctile = 0
            crow = 0

            for row in object.tiles:
                for tile in row:
                    if ctile == 0:
                        object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    elif ctile == object.width-1:
                        object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    else:
                        object.tiles[crow][ctile] = (1, tile[1], tile[2])
                    ctile += 1
                crow += 1
                ctile = 0

            object.upperslope = [0, 0]
            object.lowerslope = [0, 0]

        if listindex == 3:  # Stretch Y

            if object.height < 3:
                reply = QtWidgets.QMessageBox.information(self, "Warning", "An object must be at least 3 tiles\ntall to apply stretch Y.")
                self.setObject(index)
                return

            ctile = 0
            crow = 0

            for row in object.tiles:
                for tile in row:
                    if crow == 0:
                        object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    elif crow == object.height-1:
                        object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    else:
                        object.tiles[crow][ctile] = (2, tile[1], tile[2])
                    ctile += 1
                crow += 1
                ctile = 0

            object.upperslope = [0, 0]
            object.lowerslope = [0, 0]

        if listindex == 4:  # Repeat Bottom

            if object.height < 2:
                reply = QtWidgets.QMessageBox.information(self, "Warning", "An object must be at least 2 tiles\ntall to apply repeat bottom.")
                self.setObject(index)
                return

            ctile = 0
            crow = 0

            for row in object.tiles:
                for tile in row:
                    if crow == object.height-1:
                        object.tiles[crow][ctile] = (2, tile[1], tile[2])
                    else:
                        object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    ctile += 1
                crow += 1
                ctile = 0

            object.upperslope = [0, 0]
            object.lowerslope = [0, 0]

        if listindex == 5:  # Repeat Top

            if object.height < 2:
                reply = QtWidgets.QMessageBox.information(self, "Warning", "An object must be at least 2 tiles\ntall to apply repeat top.")
                self.setObject(index)
                return

            ctile = 0
            crow = 0

            for row in object.tiles:
                for tile in row:
                    if crow == 0:
                        object.tiles[crow][ctile] = (2, tile[1], tile[2])
                    else:
                        object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    ctile += 1
                crow += 1
                ctile = 0

            object.upperslope = [0, 0]
            object.lowerslope = [0, 0]

        if listindex == 6:  # Repeat Left

            if object.width < 2:
                reply = QtWidgets.QMessageBox.information(self, "Warning", "An object must be at least 2 tiles\nwide to apply repeat left.")
                self.setObject(index)
                return

            ctile = 0
            crow = 0

            for row in object.tiles:
                for tile in row:
                    if ctile == 0:
                        object.tiles[crow][ctile] = (1, tile[1], tile[2])
                    else:
                        object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    ctile += 1
                crow += 1
                ctile = 0

            object.upperslope = [0, 0]
            object.lowerslope = [0, 0]

        if listindex == 7:  # Repeat Right

            if object.width < 2:
                reply = QtWidgets.QMessageBox.information(self, "Warning", "An object must be at least 2 tiles\nwide to apply repeat right.")
                self.setObject(index)
                return

            ctile = 0
            crow = 0

            for row in object.tiles:
                for tile in row:
                    if ctile == object.width-1:
                        object.tiles[crow][ctile] = (1, tile[1], tile[2])
                    else:
                        object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    ctile += 1
                crow += 1
                ctile = 0

            object.upperslope = [0, 0]
            object.lowerslope = [0, 0]


        if listindex == 8:  # Upward Slope
            ctile = 0
            crow = 0
            for row in object.tiles:
                for tile in row:
                    object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    ctile += 1
                crow += 1
                ctile = 0

            object.upperslope = [0x90, 1]
            object.lowerslope = [0x84, object.height - 1]
            self.tiles.slope = 1

            self.tiles.update()

        if listindex == 9:  # Downward Slope
            ctile = 0
            crow = 0
            for row in object.tiles:
                for tile in row:
                    object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    ctile += 1
                crow += 1
                ctile = 0

            object.upperslope = [0x91, 1]
            object.lowerslope = [0x84, object.height - 1]
            self.tiles.slope = 1

            self.tiles.update()

        if listindex == 10:  # Upward Reverse Slope
            ctile = 0
            crow = 0
            for row in object.tiles:
                for tile in row:
                    object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    ctile += 1
                crow += 1
                ctile = 0

            object.upperslope = [0x92, object.height - 1]
            object.lowerslope = [0x84, 1]
            self.tiles.slope = 0-(object.height-1)

            self.tiles.update()

        if listindex == 11:  # Downward Reverse Slope
            ctile = 0
            crow = 0
            for row in object.tiles:
                for tile in row:
                    object.tiles[crow][ctile] = (0, tile[1], tile[2])
                    ctile += 1
                crow += 1
                ctile = 0

            object.upperslope = [0x93, object.height - 1]
            object.lowerslope = [0x84, 1]
            self.tiles.slope = 0-(object.height-1)

            self.tiles.update()


    def addRowHandler(self):
        self.tiles.addRow()
        self.randStuff.setVisible(self.tiles.size == [1, 1])
    def removeRowHandler(self):
        self.tiles.removeRow()
        self.randStuff.setVisible(self.tiles.size == [1, 1])
    def addColumnHandler(self):
        self.tiles.addColumn()
        self.randStuff.setVisible(self.tiles.size == [1, 1])
    def removeColumnHandler(self):
        self.tiles.removeColumn()
        self.randStuff.setVisible(self.tiles.size == [1, 1])

    def changeRandX(self, toggled):
        index = window.objectList.currentIndex()
        object = Tileset.objects[index.row()]
        object.randX = 1 if toggled else 0
        self.randLen.setEnabled(object.randX + object.randY > 0)
    def changeRandY(self, toggled):
        index = window.objectList.currentIndex()
        object = Tileset.objects[index.row()]
        object.randY = 1 if toggled else 0
        self.randLen.setEnabled(object.randX + object.randY > 0)
    def changeRandLen(self, val):
        index = window.objectList.currentIndex()
        object = Tileset.objects[index.row()]
        object.randLen = val


class tileWidget(QtWidgets.QWidget):

    def __init__(self):
        super(tileWidget, self).__init__()

        self.tiles = []

        self.size = [1, 1]
        self.setMinimumSize(24, 24)

        self.slope = 0

        self.highlightedRect = QtCore.QRect()

        self.setAcceptDrops(True)
        self.object = 0


    def clear(self):
        self.tiles = []
        self.size = [1, 1] # [width, height]

        self.slope = 0
        self.highlightedRect = QtCore.QRect()

        self.update()


    def addColumn(self):
        global Tileset

        if self.size[0] >= 24:
            return

        self.size[0] += 1
        self.setMinimumSize(self.size[0]*24, self.size[1]*24)

        pix = QtGui.QPixmap(24,24)
        pix.fill(QtGui.QColor(0,0,0,0))

        for y in range(self.size[1]):
            self.tiles.insert(((y+1) * self.size[0]) -1, [self.size[0]-1, y, pix])


        curObj = Tileset.objects[self.object]
        curObj.width += 1

        for row in curObj.tiles:
            row.append((0, 0, 0))

        self.update()
        self.updateList()


    def removeColumn(self):
        global Tileset

        if self.size[0] == 1:
            return

        for y in range(self.size[1]):
            self.tiles.pop(((y+1) * self.size[0])-(y+1))

        self.size[0] = self.size[0] - 1
        self.setMinimumSize(self.size[0]*24, self.size[1]*24)


        curObj = Tileset.objects[self.object]
        curObj.width -= 1

        for row in curObj.tiles:
            row.pop()

        self.update()
        self.updateList()


    def addRow(self):
        global Tileset

        if self.size[1] >= 24:
            return

        self.size[1] += 1
        self.setMinimumSize(self.size[0]*24, self.size[1]*24)

        pix = QtGui.QPixmap(24,24)
        pix.fill(QtGui.QColor(0,0,0,0))

        for x in range(self.size[0]):
            self.tiles.append([x, self.size[1]-1, pix])

        curObj = Tileset.objects[self.object]
        curObj.height += 1

        curObj.tiles.append([])
        for i in range(0, curObj.width):
            curObj.tiles[len(curObj.tiles)-1].append((0, 0, 0))

        self.update()
        self.updateList()


    def removeRow(self):
        global Tileset

        if self.size[1] == 1:
            return

        for x in range(self.size[0]):
            self.tiles.pop()

        self.size[1] -= 1
        self.setMinimumSize(self.size[0]*24, self.size[1]*24)

        curObj = Tileset.objects[self.object]
        curObj.tiles = list(curObj.tiles)
        curObj.height -= 1

        curObj.tiles.pop()

        self.update()
        self.updateList()


    def setObject(self, object):
        self.clear()

        global Tileset

        self.size = [object.width, object.height]

        if not object.upperslope[1] == 0:
            if object.upperslope[0] & 2:
                self.slope = 0 - object.lowerslope[1]
            else:
                self.slope = object.upperslope[1]

        x = 0
        y = 0
        for row in object.tiles:
            for tile in row:
                if (Tileset.slot == 0) or ((tile[2] & 3) != 0):
                    self.tiles.append([x, y, Tileset.tiles[tile[1]].image.scaledToWidth(24, Qt.SmoothTransformation)])
                else:
                    pix = QtGui.QPixmap(24,24)
                    pix.fill(QtGui.QColor(0,0,0,0))
                    self.tiles.append([x, y, pix])
                x += 1
            y += 1
            x = 0


        self.object = window.objectList.currentIndex().row()
        self.update()
        self.updateList()


    def contextMenuEvent(self, event):

        TileMenu = QtWidgets.QMenu(self)
        self.contX = event.x()
        self.contY = event.y()

        TileMenu.addAction('Set tile...', self.setTile)
        TileMenu.addAction('Add Item...', self.setItem)

        TileMenu.exec_(event.globalPos())


    def mousePressEvent(self, event):
        global Tileset

        if event.button() == 2:
            return

        if window.tileDisplay.selectedIndexes() == []:
            return

        currentSelected = window.tileDisplay.selectedIndexes()

        ix = 0
        iy = 0
        for modelItem in currentSelected:
            # Update yourself!
            centerPoint = self.contentsRect().center()

            tile = modelItem.row()
            upperLeftX = centerPoint.x() - self.size[0]*12
            upperLeftY = centerPoint.y() - self.size[1]*12

            lowerRightX = centerPoint.x() + self.size[0]*12
            lowerRightY = centerPoint.y() + self.size[1]*12


            x = int((event.x() - upperLeftX)/24 + ix)
            y = int((event.y() - upperLeftY)/24 + iy)

            if event.x() < upperLeftX or event.y() < upperLeftY or event.x() > lowerRightX or event.y() > lowerRightY:
                return

            try:
                self.tiles[(y * self.size[0]) + x][2] = Tileset.tiles[tile].image.scaledToWidth(24, Qt.SmoothTransformation)
                Tileset.objects[self.object].tiles[y][x] = (Tileset.objects[self.object].tiles[y][x][0], tile, Tileset.slot)
            except IndexError:
                pass

            ix += 1
            if self.size[0]-1 < ix:
                ix = 0
                iy += 1
            if iy > self.size[1]-1:
                break


        self.update()

        self.updateList()


    def updateList(self):
        # Update the list >.>
        object = window.objmodel.itemFromIndex(window.objectList.currentIndex())
        if not object: return


        tex = QtGui.QPixmap(self.size[0] * 24, self.size[1] * 24)
        tex.fill(Qt.transparent)
        painter = QtGui.QPainter(tex)

        Xoffset = 0
        Yoffset = 0

        for tile in self.tiles:
            painter.drawPixmap(tile[0]*24, tile[1]*24, tile[2])

        painter.end()

        object.setIcon(QtGui.QIcon(tex))

        window.objectList.update()



    def setTile(self):
        global Tileset

        dlg = self.setTileDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            # Do stuff
            centerPoint = self.contentsRect().center()

            upperLeftX = centerPoint.x() - self.size[0]*12
            upperLeftY = centerPoint.y() - self.size[1]*12

            tile = dlg.tile.value()
            tileset = dlg.tileset.currentIndex()

            x = int((self.contX - upperLeftX) / 24)
            y = int((self.contY - upperLeftY) / 24)

            if tileset != Tileset.slot:
                tex = QtGui.QPixmap(self.size[0] * 24, self.size[1] * 24)
                tex.fill(Qt.transparent)

                self.tiles[(y * self.size[0]) + x][2] = tex

            Tileset.objects[self.object].tiles[y][x] = (Tileset.objects[self.object].tiles[y][x][0], tile, tileset)

            self.update()
            self.updateList()


    class setTileDialog(QtWidgets.QDialog):

        def __init__(self):
            QtWidgets.QDialog.__init__(self)

            self.setWindowTitle('Set tiles')

            self.tileset = QtWidgets.QComboBox()
            self.tileset.addItems(['Pa0', 'Pa1', 'Pa2', 'Pa3'])

            self.tile = QtWidgets.QSpinBox()
            self.tile.setRange(0, 255)

            self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
            self.buttons.accepted.connect(self.accept)
            self.buttons.rejected.connect(self.reject)

            self.layout = QtWidgets.QGridLayout()
            self.layout.addWidget(QtWidgets.QLabel('Tileset:'), 0,0,1,1, Qt.AlignLeft)
            self.layout.addWidget(QtWidgets.QLabel('Tile:'), 0,3,1,1, Qt.AlignLeft)
            self.layout.addWidget(self.tileset, 1, 0, 1, 2)
            self.layout.addWidget(self.tile, 1, 3, 1, 3)
            self.layout.addWidget(self.buttons, 2, 3)
            self.setLayout(self.layout)


    def setItem(self):
        global Tileset

        dlg = self.setItemDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            # Do stuff
            centerPoint = self.contentsRect().center()

            upperLeftX = centerPoint.x() - self.size[0]*12
            upperLeftY = centerPoint.y() - self.size[1]*12

            item = dlg.item.currentIndex()

            x = int((self.contX - upperLeftX) / 24)
            y = int((self.contY - upperLeftY) / 24)

            obj = Tileset.objects[self.object].tiles[y][x]

            obj = (obj[0], obj[1], obj[2] | (item << 2))

            self.update()
            self.updateList()


    class setItemDialog(QtWidgets.QDialog):

        def __init__(self):
            QtWidgets.QDialog.__init__(self)

            self.setWindowTitle('Set item')

            self.item = QtWidgets.QComboBox()
            self.item.addItems(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14'])

            self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
            self.buttons.accepted.connect(self.accept)
            self.buttons.rejected.connect(self.reject)

            self.layout = QtWidgets.QHBoxLayout()
            self.vlayout = QtWidgets.QVBoxLayout()
            self.layout.addWidget(QtWidgets.QLabel('Item:'))
            self.layout.addWidget(self.item)
            self.vlayout.addLayout(self.layout)
            self.vlayout.addWidget(self.buttons)
            self.setLayout(self.vlayout)



    def paintEvent(self, event):
        painter = QtGui.QPainter()
        painter.begin(self)

        centerPoint = self.contentsRect().center()
        upperLeftX = centerPoint.x() - self.size[0]*12
        lowerRightX = centerPoint.x() + self.size[0]*12

        upperLeftY = centerPoint.y() - self.size[1]*12
        lowerRightY = centerPoint.y() + self.size[1]*12


        painter.fillRect(upperLeftX, upperLeftY, self.size[0] * 24, self.size[1]*24, QtGui.QColor(205, 205, 255))

        for x, y, pix in self.tiles:
            painter.drawPixmap(upperLeftX + (x * 24), upperLeftY + (y * 24), pix)

        if not self.slope == 0:
            pen = QtGui.QPen()
#            pen.setStyle(Qt.QDashLine)
            pen.setWidth(1)
            pen.setColor(Qt.blue)
            painter.setPen(QtGui.QPen(pen))
            painter.drawLine(upperLeftX, upperLeftY + (abs(self.slope) * 24), lowerRightX, upperLeftY + (abs(self.slope) * 24))

            if self.slope > 0:
                main = 'Main'
                sub = 'Sub'
            elif self.slope < 0:
                main = 'Sub'
                sub = 'Main'

            font = painter.font()
            font.setPixelSize(8)
            font.setFamily('Monaco')
            painter.setFont(font)

            painter.drawText(upperLeftX+1, upperLeftY+10, main)
            painter.drawText(upperLeftX+1, upperLeftY + (abs(self.slope) * 24) + 9, sub)

        painter.end()



#############################################################################################
############################ Subclassed one dimension Item Model ############################


class PiecesModel(QtCore.QAbstractListModel):
    def __init__(self, parent=None):
        super(PiecesModel, self).__init__(parent)

        self.pixmaps = []

    def supportedDragActions(self):
        super().supportedDragActions()
        return Qt.CopyAction | Qt.MoveAction | Qt.LinkAction

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None

        if role == Qt.DecorationRole:
            return QtGui.QIcon(self.pixmaps[index.row()])

        if role == Qt.UserRole:
            return self.pixmaps[index.row()]

        return None

    def addPieces(self, pixmap):
        row = len(self.pixmaps)

        self.beginInsertRows(QtCore.QModelIndex(), row, row)
        self.pixmaps.insert(row, pixmap)
        self.endInsertRows()

    def flags(self,index):
        if index.isValid():
            return (Qt.ItemIsEnabled | Qt.ItemIsSelectable |
                    Qt.ItemIsDragEnabled)

    def clear(self):
        row = len(self.pixmaps)

        del self.pixmaps[:]


    def mimeTypes(self):
        return ['image/x-tile-piece']


    def mimeData(self, indexes):
        mimeData = QtCore.QMimeData()
        encodedData = QtCore.QByteArray()

        stream = QtCore.QDataStream(encodedData, QtCore.QIODevice.WriteOnly)

        for index in indexes:
            if index.isValid():
                pixmap = QtGui.QPixmap(self.data(index, Qt.UserRole))
                stream << pixmap

        mimeData.setData('image/x-tile-piece', encodedData)
        return mimeData


    def rowCount(self, parent):
        if parent.isValid():
            return 0
        else:
            return len(self.pixmaps)

    def supportedDragActions(self):
        return Qt.CopyAction | Qt.MoveAction



#############################################################################################
############ Main Window Class. Takes care of menu functions and widget creation ############


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, name, data, slot, con, flags, parent=None):
        super().__init__(parent, flags)

        global window
        window = self

        self.saved = False
        self.con = con

        self.slot = int(slot)
        if self.slot == 0:
            self.anime = ['belt_conveyor_anime', 'block_anime', 'block_anime_L', 'hatena_anime', 'hatena_anime_L', 'tuka_coin_anime']

        self.tileImage = QtGui.QPixmap()
        self.normalmap = False

        global Tileset, PuzzleVersion
        Tileset = TilesetClass()

        self.name = name

        self.forceClose = False

        self.setupMenus()
        self.setupWidgets()

        self.setuptile()

        if data == 'None':
            self.newTileset()

        else:
            with open(data, 'rb') as fn:
                self.data = fn.read()

            if not self.openTileset():
                self.forceClose = True

        self.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed,
                QtWidgets.QSizePolicy.Fixed))
        self.setWindowTitle(name + ' - Puzzle NSMBU v%s' % PuzzleVersion)


    def closeEvent(self, event):
        if platform.system() == 'Windows':
            tile_path = globals.miyamoto_path + '/Tools'

        elif platform.system() == 'Linux':
            tile_path = globals.miyamoto_path + '/linuxTools'

        else:
            tile_path = globals.miyamoto_path + '/macTools'

        if os.path.isfile(tile_path + '/tmp.tmp'):
            os.remove(tile_path + '/tmp.tmp')

        """
        # Object-duplicates-related
        if self.saved:
            toDelete = []
            for folderIndex in globals.ObjectAddedtoEmbedded[globals.CurrentArea]:
                for objNum in globals.ObjectAddedtoEmbedded[globals.CurrentArea][folderIndex]:
                    idx, _ = globals.ObjectAddedtoEmbedded[globals.CurrentArea][folderIndex][objNum]
                    if idx == self.slot:
                        toDelete.append([folderIndex, objNum])

            for (folderIndex, objNum) in toDelete:
                del globals.ObjectAddedtoEmbedded[globals.CurrentArea][folderIndex][objNum]
        """

        if not self.saved and self.con:
            exec("globals.Area.tileset%d = ''" % self.slot)

        super().closeEvent(event)


    def setuptile(self):
        self.tileWidget.tiles.clear()
        self.model.clear()

        if self.normalmap:
            for tile in Tileset.tiles:
                self.model.addPieces(tile.normalmap.scaledToWidth(24, Qt.SmoothTransformation))
        else:
            for tile in Tileset.tiles:
                self.model.addPieces(tile.image.scaledToWidth(24, Qt.SmoothTransformation))


    def newTileset(self):
        '''Creates a new, blank tileset'''

        global Tileset
        Tileset.clear()
        Tileset = TilesetClass()

        EmptyPix = QtGui.QPixmap(60, 60)
        EmptyPix.fill(Qt.black)

        normalmap = QtGui.QPixmap(60, 60)
        normalmap.fill(QtGui.QColor(0x80, 0x80, 0xff))

        for i in range(256):
            Tileset.addTile(EmptyPix, normalmap)

        Tileset.slot = self.slot
        self.tileWidget.tilesetType.setText('Pa{0}'.format(Tileset.slot))

        self.setuptile()

        cobj = 0
        crow = 0
        ctile = 0
        for object in Tileset.objects:
            for row in object.tiles:
                for tile in row:
                    if tile[2] & 3 or not Tileset.slot:
                        Tileset.objects[cobj].tiles[crow][ctile] = (tile[0], tile[1], (tile[2] & 0xFC) | Tileset.slot)
                    ctile += 1
                crow += 1
                ctile = 0
            cobj += 1
            crow = 0
            ctile = 0


    @staticmethod
    def getData(arc):
        Image = None
        NmlMap = None
        behaviourdata = None
        objstrings = None
        metadata = None

        for folder in arc.contents:
            if folder.name == 'BG_tex':
                for file in folder.contents:
                    if file.name.endswith('_nml.gtx') and len(file.data) in (1421344, 4196384):
                        NmlMap = file.data
                    elif file.name.endswith('.gtx') and len(file.data) in (1421344, 4196384):
                        Image = file.data
                            
            elif folder.name == 'BG_chk':
                for file in folder.contents:
                    if file.name.startswith('d_bgchk_') and file.name.endswith('.bin'):
                        behaviourdata = file.data
            elif folder.name == 'BG_unt':
                for file in folder.contents:
                    if file.name.endswith('_hd.bin'):
                        metadata = file.data
                    elif file.name.endswith('.bin'):
                        objstrings = file.data

        return Image, NmlMap, behaviourdata, objstrings, metadata


    def openTileset(self):
        '''Opens a Nintendo tileset sarc and parses the heck out of it.'''

        data = self.data

        if not data.startswith(b'SARC'):
            QtWidgets.QMessageBox.warning(None, 'Error',  'Error - this is not a SARC file.\n\nNot a valid tileset, sadly.')
            return

        arc = SarcLib.SARC_Archive(data)
        self.arc = arc

        Image, NmlMap, behaviourdata, objstrings, metadata = self.getData(arc)

        if not Image:
            QtWidgets.QMessageBox.warning(None, 'Error',  'Error - Couldn\'t load the image data')
            return

        elif not NmlMap:
            QtWidgets.QMessageBox.warning(None, 'Error',  'Error - Couldn\'t load the normal map data')
            return

        elif not (behaviourdata and objstrings and metadata):
            QtWidgets.QMessageBox.warning(None, 'Error',  'Error - the necessary files were not found.\n\nNot a valid tileset, sadly.')
            return

        global Tileset
        Tileset.clear()

        # Loads the Image Data.
        dest = loadGTX(Image)
        destnml = loadGTX(NmlMap)

        self.tileImage = QtGui.QPixmap.fromImage(dest)
        self.nmlImage = QtGui.QPixmap.fromImage(destnml)

        # Loads Tile Behaviours
        behaviours = []
        for entry in range(256):
            thisline = list(struct.unpack('>8B', behaviourdata[entry*8:entry*8+8]))
            behaviours.append(tuple(thisline))


        # Makes us some nice Tile Classes!
        Xoffset = 2
        Yoffset = 2
        for i in range(256):
            Tileset.addTile(
                self.tileImage.copy(Xoffset,Yoffset,60,60),
                self.nmlImage.copy(Xoffset,Yoffset,60,60),
                behaviours[i])
            Xoffset += 64
            if Xoffset >= 2048:
                Xoffset = 2
                Yoffset += 64


        # Load Objects

        meta = []
        for i in range(len(metadata) // 6):
            meta.append(struct.unpack_from('>HBBH', metadata, i * 6))

        tilelist = [[]]
        upperslope = [0, 0]
        lowerslope = [0, 0]
        byte = 0

        for entry in meta:
            offset = entry[0]
            byte = struct.unpack_from('>B', objstrings, offset)[0]
            row = 0

            while byte != 0xFF:

                if byte == 0xFE:
                    tilelist.append([])

                    if (upperslope[0] != 0) and (lowerslope[0] == 0):
                        upperslope[1] = upperslope[1] + 1

                    if lowerslope[0] != 0:
                        lowerslope[1] = lowerslope[1] + 1

                    offset += 1
                    byte = struct.unpack_from('>B', objstrings, offset)[0]

                elif (byte & 0x80):

                    if upperslope[0] == 0:
                        upperslope[0] = byte
                    else:
                        lowerslope[0] = byte

                    offset += 1
                    byte = struct.unpack_from('>B', objstrings, offset)[0]

                else:
                    tilelist[-1].append(struct.unpack_from('>3B', objstrings, offset))

                    offset += 3
                    byte = struct.unpack_from('>B', objstrings, offset)[0]

            tilelist.pop()

            if (upperslope[0] & 0x80) and (upperslope[0] & 0x2):
                for i in range(lowerslope[1]):
                    pop = tilelist.pop()
                    tilelist.insert(0, pop)

            Tileset.addObject(entry[2], entry[1], entry[3], upperslope, lowerslope, tilelist)

            tilelist = [[]]
            upperslope = [0, 0]
            lowerslope = [0, 0]

        Tileset.slot = self.slot
        self.tileWidget.tilesetType.setText('Pa%d' % Tileset.slot)

        cobj = 0
        crow = 0
        ctile = 0
        for object in Tileset.objects:
            for row in object.tiles:
                for tile in row:
                    if tile[2] & 3 or not Tileset.slot:
                        Tileset.objects[cobj].tiles[crow][ctile] = (tile[0], tile[1], (tile[2] & 0xFC) | Tileset.slot)
                    ctile += 1
                crow += 1
                ctile = 0
            cobj += 1
            crow = 0
            ctile = 0

        self.setuptile()
        SetupObjectModel(self.objmodel, Tileset.objects, Tileset.tiles)

        return True


    def openTilesetfromFile(self):
        '''Opens a NSMBU tileset sarc from a file and parses the heck out of it.'''

        path = QtWidgets.QFileDialog.getOpenFileName(self, "Open NSMBU Tileset", '',
                    "All files (*)")[0]

        if not path: return

        name = '.'.join(os.path.basename(path).split('.')[:-1])

        with open(path, 'rb') as file:
            data = file.read()

        if not data.startswith(b'SARC'):
            QtWidgets.QMessageBox.warning(None, 'Error',  'Error - this is not a SARC file.\n\nNot a valid tileset, sadly.')
            return

        arc = SarcLib.SARC_Archive(data)
        self.arc = arc

        Image, NmlMap, behaviourdata, objstrings, metadata = self.getData(arc)

        if not Image:
            QtWidgets.QMessageBox.warning(None, 'Error',  'Error - Couldn\'t load the image data')
            return

        elif not NmlMap:
            QtWidgets.QMessageBox.warning(None, 'Error',  'Error - Couldn\'t load the normal map data')
            return

        elif not (behaviourdata and objstrings and metadata):
            QtWidgets.QMessageBox.warning(None, 'Error',  'Error - the necessary files were not found.\n\nNot a valid tileset, sadly.')
            return

        global Tileset
        Tileset.clear()

        # Loads the Image Data.
        dest = loadGTX(Image)
        destnml = loadGTX(NmlMap)

        self.tileImage = QtGui.QPixmap.fromImage(dest)
        self.nmlImage = QtGui.QPixmap.fromImage(destnml)

        # Loads Tile Behaviours
        behaviours = []
        for entry in range(256):
            thisline = list(struct.unpack('>8B', behaviourdata[entry*8:entry*8+8]))
            behaviours.append(tuple(thisline))


        # Makes us some nice Tile Classes!
        Xoffset = 2
        Yoffset = 2
        for i in range(256):
            Tileset.addTile(
                self.tileImage.copy(Xoffset,Yoffset,60,60),
                self.nmlImage.copy(Xoffset,Yoffset,60,60),
                behaviours[i])
            Xoffset += 64
            if Xoffset >= 2048:
                Xoffset = 2
                Yoffset += 64


        # Load Objects

        meta = []
        for i in range(len(metadata) // 6):
            meta.append(struct.unpack_from('>HBBH', metadata, i * 6))

        tilelist = [[]]
        upperslope = [0, 0]
        lowerslope = [0, 0]
        byte = 0

        for entry in meta:
            offset = entry[0]
            byte = struct.unpack_from('>B', objstrings, offset)[0]
            row = 0

            while byte != 0xFF:

                if byte == 0xFE:
                    tilelist.append([])

                    if (upperslope[0] != 0) and (lowerslope[0] == 0):
                        upperslope[1] = upperslope[1] + 1

                    if lowerslope[0] != 0:
                        lowerslope[1] = lowerslope[1] + 1

                    offset += 1
                    byte = struct.unpack_from('>B', objstrings, offset)[0]

                elif (byte & 0x80):

                    if upperslope[0] == 0:
                        upperslope[0] = byte
                    else:
                        lowerslope[0] = byte

                    offset += 1
                    byte = struct.unpack_from('>B', objstrings, offset)[0]

                else:
                    tilelist[-1].append(struct.unpack_from('>3B', objstrings, offset))

                    offset += 3
                    byte = struct.unpack_from('>B', objstrings, offset)[0]

            tilelist.pop()

            if (upperslope[0] & 0x80) and (upperslope[0] & 0x2):
                for i in range(lowerslope[1]):
                    pop = tilelist.pop()
                    tilelist.insert(0, pop)

            Tileset.addObject(entry[2], entry[1], entry[3], upperslope, lowerslope, tilelist)

            tilelist = [[]]
            upperslope = [0, 0]
            lowerslope = [0, 0]

        Tileset.slot = self.slot
        self.tileWidget.tilesetType.setText('Pa%d' % Tileset.slot)

        cobj = 0
        crow = 0
        ctile = 0
        for object in Tileset.objects:
            for row in object.tiles:
                for tile in row:
                    if tile[2] & 3 or not Tileset.slot:
                        Tileset.objects[cobj].tiles[crow][ctile] = (tile[0], tile[1], (tile[2] & 0xFC) | Tileset.slot)
                    ctile += 1
                crow += 1
                ctile = 0
            cobj += 1
            crow = 0
            ctile = 0

        self.setuptile()
        SetupObjectModel(self.objmodel, Tileset.objects, Tileset.tiles)


    def openImage(self, nml=False):
        '''Opens an Image from png, and creates a new tileset from it.'''

        path = QtWidgets.QFileDialog.getOpenFileName(self, "Open Image", '',
                    "Image Files (*.png)")[0]

        if not path: return
        newImage = QtGui.QPixmap()
        self.tileImage = newImage

        if not newImage.load(path):
            QtWidgets.QMessageBox.warning(self, "Open Image",
                    "The image file could not be loaded.",
                    QtWidgets.QMessageBox.Cancel)
            return

        if ((newImage.width() == 960) & (newImage.height() == 960)):
            x = 0
            y = 0
            for i in range(256):
                if nml:
                    Tileset.tiles[i].normalmap = self.tileImage.copy(x*60,y*60,60,60)
                else:
                    Tileset.tiles[i].image = self.tileImage.copy(x*60,y*60,60,60)
                x += 1
                if (x * 60) >= 960:
                    y += 1
                    x = 0

        else:
            QtWidgets.QMessageBox.warning(self, "Open Image",
                    "The image was not the proper dimensions."
                    "Please resize the image to 960x960 pixels.",
                    QtWidgets.QMessageBox.Cancel)
            return


        self.setuptile()


    def saveImage(self, nml=False):

        fn = QtWidgets.QFileDialog.getSaveFileName(self, 'Choose a new filename', '', '.png (*.png)')[0]
        if fn == '': return

        tex = QtGui.QPixmap(960, 960)
        tex.fill(Qt.transparent)
        painter = QtGui.QPainter(tex)

        Xoffset = 0
        Yoffset = 0

        for tile in Tileset.tiles:
            tileimg = tile.image
            if nml:
                tileimg = tile.normalmap
            painter.drawPixmap(Xoffset, Yoffset, tileimg)
            Xoffset += 60
            if Xoffset >= 960:
                Xoffset = 0
                Yoffset += 60

        painter.end()

        tex.save(fn)


    def openNml(self):
        self.openImage(True)


    def saveNml(self):
        self.saveImage(True)


    def saveTileset(self):
        outdata = self.saving(os.path.basename(self.name))
        globals.szsData[eval('globals.Area.tileset%d' % self.slot)] = outdata

        if self.slot == 0:
            import loading
            loading.LoadTileset(0, globals.Area.tileset0)
            del loading

            import verifications
            verifications.SetDirty()
            del verifications

            HandleTilesetEdited(True)
            globals.mainWindow.objAllTab.setTabEnabled(0, True)
            globals.mainWindow.objAllTab.setCurrentIndex(0)

        else:
            globals.mainWindow.ReloadTilesets()

            import verifications
            verifications.SetDirty()
            del verifications

            HandleTilesetEdited(True)

            if globals.ObjectDefinitions[self.slot] == [None] * 256:
                import tileset
                tileset.UnloadTileset(self.slot)
                del tileset

                exec("globals.Area.tileset%d = ''" % self.slot)

            else:
                globals.mainWindow.objAllTab.setCurrentIndex(2)

        for layer in globals.Area.layers:
            for obj in layer:
                obj.updateObjCache()

        globals.mainWindow.scene.update()

        self.saved = True
        self.close()


    def saveTilesetAs(self):

        fn = QtWidgets.QFileDialog.getSaveFileName(self, 'Choose a new filename', '', 'All files (*)')[0]
        if fn == '': return

        outdata = self.saving(os.path.basename(str(fn)))
        
        with open(fn, 'wb') as f:
            f.write(outdata)


    def saving(self, name):

        # Prepare tiles, objects, object metadata, and textures and stuff into buffers.
        textureType = self.slot in range(1, 4)
        textureBuffer = self.PackTexture(textureType)
        textureBufferNml = self.PackTexture(textureType, True)
        tileBuffer = self.PackTiles()
        objectBuffers = self.PackObjects()
        objectBuffer = objectBuffers[0]
        objectMetaBuffer = objectBuffers[1]


        # Make an arc and pack up the files!
        arc = SarcLib.SARC_Archive()

        tex = SarcLib.Folder('BG_tex'); arc.addFolder(tex)
        tex.addFile(SarcLib.File('%s.gtx' % name, textureBuffer))
        tex.addFile(SarcLib.File('%s_nml.gtx' % name, textureBufferNml))

        if self.slot == 0:
            for folder in self.arc.contents:
                if folder.name == 'BG_tex':
                    for file in folder.contents:
                        for name2 in self.anime:
                            if file.name == '%s.gtx' % name2:
                                tex.addFile(SarcLib.File('%s.gtx' % name2, file.data))

        chk = SarcLib.Folder('BG_chk'); arc.addFolder(chk)
        chk.addFile(SarcLib.File('d_bgchk_%s.bin' % name, tileBuffer))

        unt = SarcLib.Folder('BG_unt'); arc.addFolder(unt)
        unt.addFile(SarcLib.File('%s.bin' % name, objectBuffer))
        unt.addFile(SarcLib.File('%s_hd.bin' % name, objectMetaBuffer))

        return arc.save()[0]


    def PackTexture(self, isDxt5, normalmap=False):

        tex = QtGui.QImage(2048, 512, QtGui.QImage.Format_RGBA8888)
        tex.fill(Qt.transparent)
        painter = QtGui.QPainter(tex)

        Xoffset = 0
        Yoffset = 0

        for tile in Tileset.tiles:
            minitex = QtGui.QImage(64, 64, QtGui.QImage.Format_RGBA8888)
            minitex.fill(Qt.transparent)
            minipainter = QtGui.QPainter(minitex)

            minipainter.drawPixmap(2, 2, tile.normalmap if normalmap else tile.image)
            minipainter.end()

            # Read colours and DESTROY THEM (or copy them to the edges, w/e)
            for i in range(2, 62):

                # Top Clamp
                colour = minitex.pixel(i, 2)
                for p in range(0,2):
                    minitex.setPixel(i, p, colour)

                # Left Clamp
                colour = minitex.pixel(2, i)
                for p in range(0,2):
                    minitex.setPixel(p, i, colour)

                # Right Clamp
                colour = minitex.pixel(i, 61)
                for p in range(62,64):
                    minitex.setPixel(i, p, colour)

                # Bottom Clamp
                colour = minitex.pixel(61, i)
                for p in range(62,64):
                    minitex.setPixel(p, i, colour)

            # UpperLeft Corner Clamp
            colour = minitex.pixel(2, 2)
            for x in range(0,2):
                for y in range(0,2):
                    minitex.setPixel(x, y, colour)

            # UpperRight Corner Clamp
            colour = minitex.pixel(61, 2)
            for x in range(62,64):
                for y in range(0,2):
                    minitex.setPixel(x, y, colour)

            # LowerLeft Corner Clamp
            colour = minitex.pixel(2, 61)
            for x in range(0,2):
                for y in range(62,64):
                    minitex.setPixel(x, y, colour)

            # LowerRight Corner Clamp
            colour = minitex.pixel(61, 61)
            for x in range(62,64):
                for y in range(62,64):
                    minitex.setPixel(x, y, colour)


            painter.drawImage(Xoffset, Yoffset, minitex)

            Xoffset += 64

            if Xoffset >= 2048:
                Xoffset = 0
                Yoffset += 64

        painter.end()

        return writeGTX(tex, Tileset.slot)


    def PackTiles(self):
        offset = 0
        tilespack = struct.Struct('>8B')
        Tilebuffer = create_string_buffer(2048)
        for tile in Tileset.tiles:
            tilespack.pack_into(Tilebuffer, offset, tile.byte0, tile.byte1, tile.byte2, tile.byte3, tile.byte4, tile.byte5, tile.byte6, tile.byte7)
            offset += 8

        return Tilebuffer.raw


    def PackObjects(self):
        objectStrings = []

        o = 0
        for object in Tileset.objects:


            # Slopes
            if object.upperslope[0] != 0:

                # Reverse Slopes
                if object.upperslope[0] & 0x2:
                    a = struct.pack('>B', object.upperslope[0])

                    if not object.lowerslope[1]:
                        for row in range(0, object.upperslope[1]):
                            for tile in object.tiles[row]:
                                a += struct.pack('>BBB', tile[0], tile[1], tile[2])
                            a += b'\xfe'

                    else:
                        if object.height == 1:
                            iterationsA = 0
                            iterationsB = 1
                        else:
                            iterationsA = object.upperslope[1]
                            iterationsB = object.lowerslope[1] + object.upperslope[1]

                        for row in range(iterationsA, iterationsB):
                            for tile in object.tiles[row]:
                                a += struct.pack('>BBB', tile[0], tile[1], tile[2])
                            a += b'\xfe'

                        if object.height > 1:
                            a += struct.pack('>B', object.lowerslope[0])

                            for row in range(0, object.upperslope[1]):
                                for tile in object.tiles[row]:
                                    a += struct.pack('>BBB', tile[0], tile[1], tile[2])
                                a += b'\xfe'

                    a += b'\xff'
                    objectStrings.append(a)


                # Regular Slopes
                else:
                    a = struct.pack('>B', object.upperslope[0])

                    for row in range(0, object.upperslope[1]):
                        for tile in object.tiles[row]:
                            a += struct.pack('>BBB', tile[0], tile[1], tile[2])
                        a += b'\xfe'

                    if object.height > 1 and object.lowerslope[1]:
                        a += struct.pack('>B', object.lowerslope[0])

                        for row in range(object.upperslope[1], object.height):
                            for tile in object.tiles[row]:
                                a += struct.pack('>BBB', tile[0], tile[1], tile[2])
                            a += b'\xfe'

                    a += b'\xff'
                    objectStrings.append(a)


            # Not slopes!
            else:
                a = b''

                for tilerow in object.tiles:
                    for tile in tilerow:
                        a += struct.pack('>BBB', tile[0], tile[1], tile[2])

                    a += b'\xfe'

                a += b'\xff'

                objectStrings.append(a)

            o += 1

        Objbuffer = b''
        Metabuffer = b''
        i = 0
        for a in objectStrings:
            Metabuffer += struct.pack('>HBBH', len(Objbuffer), Tileset.objects[i].width, Tileset.objects[i].height, Tileset.objects[i].getRandByte())
            Objbuffer += a

            i += 1

        return (Objbuffer, Metabuffer)



    def setupMenus(self):
        fileMenu = self.menuBar().addMenu("&File")

        pixmap = QtGui.QPixmap(60,60)
        pixmap.fill(Qt.black)
        icon = QtGui.QIcon(pixmap)

        fileMenu.addAction("Import Tileset from file...", self.openTilesetfromFile, QtGui.QKeySequence.Open)
        fileMenu.addAction("Export Tileset...", self.saveTilesetAs, QtGui.QKeySequence.SaveAs)
        fileMenu.addAction("Import Image...", self.openImage, QtGui.QKeySequence('Ctrl+I'))
        fileMenu.addAction("Export Image...", self.saveImage, QtGui.QKeySequence('Ctrl+E'))
        fileMenu.addAction("Import Normal Map...", self.openNml, QtGui.QKeySequence('Ctrl+Shift+I'))
        fileMenu.addAction("Export Normal Map...", self.saveNml, QtGui.QKeySequence('Ctrl+Shift+E'))
        fileMenu.addAction("Save and Quit", self.saveTileset, QtGui.QKeySequence.Save)
        fileMenu.addAction("Quit", self.close, QtGui.QKeySequence('Ctrl-Q'))

        taskMenu = self.menuBar().addMenu("&Tasks")

        taskMenu.addAction("Toggle Normal Map", self.toggleNormal, QtGui.QKeySequence('Ctrl+Shift+N'))
        taskMenu.addAction("Show Tiles info...", self.showInfo, QtGui.QKeySequence('Ctrl+P'))
        taskMenu.addAction("Import object from file...", self.importObjFromFile, '')
        taskMenu.addAction("Export object...", self.saveObject, '')
        taskMenu.addAction("Export all objects...", self.saveAllObjects, '')
        taskMenu.addAction("Clear Collision Data", self.clearCollisions, QtGui.QKeySequence('Ctrl+Shift+Backspace'))
        taskMenu.addAction("Clear Object Data", self.clearObjects, QtGui.QKeySequence('Ctrl+Alt+Backspace'))



    def toggleNormal(self):
        # Replace regular image with normalmap images in model
        self.normalmap = not self.normalmap

        self.setuptile()

    def showInfo(self):
        usedTiles = len(Tileset.getUsedTiles())
        freeTiles = 256 - usedTiles
        QtWidgets.QMessageBox.information(self, "Tiles info",
                "Used Tiles: " + str(usedTiles) + (" tile.\n" if freeTiles == 1 else " tiles.\n")
                + "Free Tiles: " + str(freeTiles) + (" tile." if freeTiles == 1 else " tiles."),
                QtWidgets.QMessageBox.Ok)

    def importObjFromFile(self):
        usedTiles = Tileset.getUsedTiles()
        if len(usedTiles) >= 256:  # It can't be more than 256, oh well
            QtWidgets.QMessageBox.warning(self, "Open Object",
                    "There isn't enough room in the Tileset.",
                    QtWidgets.QMessageBox.Cancel)
            return

        file = QtWidgets.QFileDialog.getOpenFileName(self, "Open Object", '',
                    "Object files (*.json)")[0]

        if not file: return

        with open(file) as inf:
            jsonData = json.load(inf)

        dir = os.path.dirname(file)

        tilelist = [[]]
        upperslope = [0, 0]
        lowerslope = [0, 0]

        metaData = open(dir + "/" + jsonData["meta"], "rb").read()
        objstrings = open(dir + "/" + jsonData["objlyt"], "rb").read()
        colls = open(dir + "/" + jsonData["colls"], "rb").read()

        randLen = 0

        if "randLen" in jsonData:
            randLen = (metaData[5] & 0xF)
            numTiles = randLen

        else:
            tilesUsed = []

            pos = 0
            while objstrings[pos] != 0xFF:
                if objstrings[pos] & 0x80:
                    pos += 1
                    continue

                tile = objstrings[pos:pos+3]
                if tile != b'\0\0\0':
                    if tile[1] not in tilesUsed:
                        tilesUsed.append(tile[1])

                pos += 3

            numTiles = len(tilesUsed)

        if numTiles + len(usedTiles) > 256:
            QtWidgets.QMessageBox.warning(self, "Open Object",
                    "There isn't enough room for the object.",
                    QtWidgets.QMessageBox.Cancel)
            return

        freeTiles = [i for i in range(256) if i not in usedTiles]

        if randLen:
            found = False
            for i in freeTiles:
                for z in range(randLen):
                    if i + z not in freeTiles:
                        break

                    if z == randLen - 1:
                        tileNum = i
                        found = True
                        break

                if found:
                    break

            if not found:
                QtWidgets.QMessageBox.warning(self, "Open Object",
                        "There isn't enough room for the object.",
                        QtWidgets.QMessageBox.Cancel)
                return

        tilesUsed = {}

        offset = 0
        byte = struct.unpack_from('>B', objstrings, offset)[0]
        i = 0
        row = 0

        while byte != 0xFF:

            if byte == 0xFE:
                tilelist.append([])

                if (upperslope[0] != 0) and (lowerslope[0] == 0):
                    upperslope[1] = upperslope[1] + 1

                if lowerslope[0] != 0:
                    lowerslope[1] = lowerslope[1] + 1

                offset += 1
                byte = struct.unpack_from('>B', objstrings, offset)[0]

            elif (byte & 0x80):

                if upperslope[0] == 0:
                    upperslope[0] = byte
                else:
                    lowerslope[0] = byte

                offset += 1
                byte = struct.unpack_from('>B', objstrings, offset)[0]

            else:
                tileBytes = objstrings[offset:offset + 3]
                if tileBytes == b'\0\0\0':
                    tile = [0, 0, 0]

                else:
                    tile = []
                    tile.append(byte)

                    if randLen:
                        tile.append(tileNum + i)
                        if i < randLen: i += 1

                    else:
                        if tileBytes[1] not in tilesUsed:
                            tilesUsed[tileBytes[1]] = i
                            tile.append(freeTiles[i])
                            i += 1
                        else:
                            tile.append(freeTiles[tilesUsed[tileBytes[1]]])

                    byte2 = (struct.unpack_from('>B', objstrings, offset + 2)[0]) & 0xFC
                    byte2 |= Tileset.slot
                    tile.append(byte2)

                tilelist[-1].append(tile)

                offset += 3
                byte = struct.unpack_from('>B', objstrings, offset)[0]

        tilelist.pop()

        if (upperslope[0] & 0x80) and (upperslope[0] & 0x2):
            for i in range(lowerslope[1]):
                pop = tilelist.pop()
                tilelist.insert(0, pop)

        if randLen:
            Tileset.addObject(metaData[3], metaData[2], metaData[5], upperslope, lowerslope, tilelist)

        else:
            Tileset.addObject(metaData[3], metaData[2], 0, upperslope, lowerslope, tilelist)

        count = len(Tileset.objects)

        object = Tileset.objects[count-1]

        tileImage = QtGui.QPixmap(dir + "/" + jsonData["img"])
        nmlImage = QtGui.QPixmap(dir + "/" + jsonData["nml"])

        if randLen:
            tex = tileImage.copy(0,0,60,60)

            colls_off = 0
            for z in range(randLen):
                Tileset.tiles[tileNum + z].image = tileImage.copy(z*60,0,60,60)
                Tileset.tiles[tileNum + z].normalmap = nmlImage.copy(z*60,0,60,60)
                Tileset.tiles[tileNum + z].byte0 = colls[colls_off]
                colls_off += 1
                Tileset.tiles[tileNum + z].byte1 = colls[colls_off]
                colls_off += 1
                Tileset.tiles[tileNum + z].byte2 = colls[colls_off]
                colls_off += 1
                Tileset.tiles[tileNum + z].byte3 = colls[colls_off]
                colls_off += 1
                Tileset.tiles[tileNum + z].byte4 = colls[colls_off]
                colls_off += 1
                Tileset.tiles[tileNum + z].byte5 = colls[colls_off]
                colls_off += 1
                Tileset.tiles[tileNum + z].byte6 = colls[colls_off]
                colls_off += 1
                Tileset.tiles[tileNum + z].byte7 = colls[colls_off]
                colls_off += 1

        else:
            tex = QtGui.QPixmap(object.width * 60, object.height * 60)
            tex.fill(Qt.transparent)
            painter = QtGui.QPainter(tex)

            Xoffset = 0
            Yoffset = 0

            colls_off = 0

            tilesReplaced = []

            for row in object.tiles:
                for tile in row:
                    if tile[2] & 3 or not Tileset.slot:
                        if tile[1] not in tilesReplaced:
                            tilesReplaced.append(tile[1])

                            Tileset.tiles[tile[1]].image = tileImage.copy(Xoffset,Yoffset,60,60)
                            Tileset.tiles[tile[1]].normalmap = nmlImage.copy(Xoffset,Yoffset,60,60)
                            Tileset.tiles[tile[1]].byte0 = colls[colls_off]
                            Tileset.tiles[tile[1]].byte1 = colls[colls_off + 1]
                            Tileset.tiles[tile[1]].byte2 = colls[colls_off + 2]
                            Tileset.tiles[tile[1]].byte3 = colls[colls_off + 3]
                            Tileset.tiles[tile[1]].byte4 = colls[colls_off + 4]
                            Tileset.tiles[tile[1]].byte5 = colls[colls_off + 5]
                            Tileset.tiles[tile[1]].byte6 = colls[colls_off + 6]
                            Tileset.tiles[tile[1]].byte7 = colls[colls_off + 7]


                        painter.drawPixmap(Xoffset, Yoffset, Tileset.tiles[tile[1]].image)

                    Xoffset += 60
                    colls_off += 8

                Xoffset = 0
                Yoffset += 60

            painter.end()

        self.objmodel.appendRow(QtGui.QStandardItem(QtGui.QIcon(tex), 'Object {0}'.format(count-1)))
        index = self.objectList.currentIndex()
        self.objectList.setCurrentIndex(index)
        self.tileWidget.setObject(index)

        self.setuptile()

        self.objectList.update()
        self.tileWidget.update()

    @staticmethod
    def exportObject(name, baseName, n):
        object = Tileset.objects[n]
        object.jsonData = {}

        if object.randLen and (object.width, object.height) == (1, 1):
            tex = QtGui.QPixmap(object.randLen * 60, object.height * 60)

        else:
            tex = QtGui.QPixmap(object.width * 60, object.height * 60)

        tex.fill(Qt.transparent)
        painter = QtGui.QPainter(tex)

        Xoffset = 0
        Yoffset = 0

        Tilebuffer = b''

        for i in range(len(object.tiles)):
            for tile in object.tiles[i]:
                if object.randLen and (object.width, object.height) == (1, 1):
                    for z in range(object.randLen):
                        if (Tileset.slot == 0) or ((tile[2] & 3) != 0):
                            painter.drawPixmap(Xoffset, Yoffset, Tileset.tiles[tile[1] + z].image)
                        Tilebuffer += (Tileset.tiles[tile[1] + z].byte0).to_bytes(1, 'big')
                        Tilebuffer += (Tileset.tiles[tile[1] + z].byte1).to_bytes(1, 'big')
                        Tilebuffer += (Tileset.tiles[tile[1] + z].byte2).to_bytes(1, 'big')
                        Tilebuffer += (Tileset.tiles[tile[1] + z].byte3).to_bytes(1, 'big')
                        Tilebuffer += (Tileset.tiles[tile[1] + z].byte4).to_bytes(1, 'big')
                        Tilebuffer += (Tileset.tiles[tile[1] + z].byte5).to_bytes(1, 'big')
                        Tilebuffer += (Tileset.tiles[tile[1] + z].byte6).to_bytes(1, 'big')
                        Tilebuffer += (Tileset.tiles[tile[1] + z].byte7).to_bytes(1, 'big')
                        Xoffset += 60
                    break

                else:
                    if (Tileset.slot == 0) or ((tile[2] & 3) != 0):
                        painter.drawPixmap(Xoffset, Yoffset, Tileset.tiles[tile[1]].image)
                    Tilebuffer += (Tileset.tiles[tile[1]].byte0).to_bytes(1, 'big')
                    Tilebuffer += (Tileset.tiles[tile[1]].byte1).to_bytes(1, 'big')
                    Tilebuffer += (Tileset.tiles[tile[1]].byte2).to_bytes(1, 'big')
                    Tilebuffer += (Tileset.tiles[tile[1]].byte3).to_bytes(1, 'big')
                    Tilebuffer += (Tileset.tiles[tile[1]].byte4).to_bytes(1, 'big')
                    Tilebuffer += (Tileset.tiles[tile[1]].byte5).to_bytes(1, 'big')
                    Tilebuffer += (Tileset.tiles[tile[1]].byte6).to_bytes(1, 'big')
                    Tilebuffer += (Tileset.tiles[tile[1]].byte7).to_bytes(1, 'big')
                    Xoffset += 60
            Xoffset = 0
            Yoffset += 60

        painter.end()

        # Slopes
        if object.upperslope[0] != 0:

            # Reverse Slopes
            if object.upperslope[0] & 0x2:
                a = struct.pack('>B', object.upperslope[0])

                if not object.lowerslope[1]:
                    for row in range(0, object.upperslope[1]):
                        for tile in object.tiles[row]:
                            a += struct.pack('>BBB', tile[0], tile[1], tile[2])
                        a += b'\xfe'

                else:
                    if object.height == 1:
                        iterationsA = 0
                        iterationsB = 1
                    else:
                        iterationsA = object.upperslope[1]
                        iterationsB = object.lowerslope[1] + object.upperslope[1]

                    for row in range(iterationsA, iterationsB):
                        for tile in object.tiles[row]:
                            a += struct.pack('>BBB', tile[0], tile[1], tile[2])
                        a += b'\xfe'

                    if object.height > 1:
                        a += struct.pack('>B', object.lowerslope[0])

                        for row in range(0, object.upperslope[1]):
                            for tile in object.tiles[row]:
                                a += struct.pack('>BBB', tile[0], tile[1], tile[2])
                            a += b'\xfe'

                a += b'\xff'


            # Regular Slopes
            else:
                a = struct.pack('>B', object.upperslope[0])

                for row in range(0, object.upperslope[1]):
                    for tile in object.tiles[row]:
                        a += struct.pack('>BBB', tile[0], tile[1], tile[2])
                    a += b'\xfe'

                if object.height > 1 and object.lowerslope[1]:
                    a += struct.pack('>B', object.lowerslope[0])

                    for row in range(object.upperslope[1], object.height):
                        for tile in object.tiles[row]:
                            a += struct.pack('>BBB', tile[0], tile[1], tile[2])
                        a += b'\xfe'

                a += b'\xff'


        # Not slopes!
        else:
            a = b''

            for tilerow in object.tiles:
                for tile in tilerow:
                    a += struct.pack('>BBB', tile[0], tile[1], tile[2])

                a += b'\xfe'

            a += b'\xff'

        Objbuffer = a
        Metabuffer = struct.pack('>HBBH', (0 if n == 0 else len(Objbuffer)), object.width, object.height, object.getRandByte())

        tex.save(name + ".png", "PNG")

        object.jsonData['img'] = baseName + ".png"

        with open(name + ".colls", "wb+") as colls:
            colls.write(Tilebuffer)

        object.jsonData['colls'] = baseName + ".colls"

        with open(name + ".objlyt", "wb+") as objlyt:
            objlyt.write(Objbuffer)

        object.jsonData['objlyt'] = baseName + ".objlyt"

        with open(name + ".meta", "wb+") as meta:
            meta.write(Metabuffer)

        object.jsonData['meta'] = baseName + ".meta"

        if object.randLen and (object.width, object.height) == (1, 1):
            object.jsonData['randLen'] = object.randLen

        if object.randLen and (object.width, object.height) == (1, 1):
            tex = QtGui.QPixmap(object.randLen * 60, object.height * 60)
        else:
            tex = QtGui.QPixmap(object.width * 60, object.height * 60)
        tex.fill(Qt.transparent)
        painter = QtGui.QPainter(tex)

        Xoffset = 0
        Yoffset = 0

        for i in range(len(object.tiles)):
            for tile in object.tiles[i]:
                if object.randLen and (object.width, object.height) == (1, 1):
                    for z in range(object.randLen):
                        if (Tileset.slot == 0) or ((tile[2] & 3) != 0):
                            painter.drawPixmap(Xoffset, Yoffset, Tileset.tiles[tile[1] + z].normalmap)
                        Xoffset += 60
                    break

                else:
                    if (Tileset.slot == 0) or ((tile[2] & 3) != 0):
                        painter.drawPixmap(Xoffset, Yoffset, Tileset.tiles[tile[1]].normalmap)
                    Xoffset += 60
            Xoffset = 0
            Yoffset += 60

        painter.end()

        tex.save(name + "_nml.png", "PNG")

        object.jsonData['nml'] = baseName + "_nml.png"

        with open(name + ".json", 'w+') as outfile:
            json.dump(object.jsonData, outfile)

    def saveAllObjects(self):
        save_path = QtWidgets.QFileDialog.getExistingDirectory(None, "Choose where to save the Object folder")
        if not save_path:
            return

        for n in range(len(Tileset.objects)):
            baseName = "object_%d" % n
            name = os.path.join(save_path, baseName)

            self.exportObject(name, baseName, n)

    def saveObject(self):
        if len(Tileset.objects) == 0: return
        dlg = getObjNum()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            n = dlg.objNum.value()

            file = QtWidgets.QFileDialog.getSaveFileName(None, "Save Objects", "", "Object files (*.json)")[0]
            if not file:
                return

            name = os.path.splitext(file)[0]
            baseName = os.path.basename(name)

            self.exportObject(name, baseName, n)

    def clearObjects(self):
        '''Clears the object data'''

        Tileset.objects = []

        SetupObjectModel(self.objmodel, Tileset.objects, Tileset.tiles)

        self.objectList.update()
        self.tileWidget.update()

    def clearCollisions(self):
        '''Clears the collisions data'''

        for tile in Tileset.tiles:
            tile.byte0 = 0
            tile.byte1 = 0
            tile.byte2 = 0
            tile.byte3 = 0
            tile.byte4 = 0
            tile.byte5 = 0
            tile.byte6 = 0
            tile.byte7 = 0

        self.updateInfo(0, 0)
        self.tileDisplay.update()

    def setupWidgets(self):
        frame = QtWidgets.QFrame()
        frameLayout = QtWidgets.QGridLayout(frame)

        # Displays the tiles
        self.tileDisplay = displayWidget()

        # Info Box for tile information
        self.infoDisplay = InfoBox(self)

        # Sets up the model for the tile pieces
        self.model = PiecesModel(self)
        self.tileDisplay.setModel(self.model)

        # Object List
        self.objectList = objectList()
        self.objmodel = QtGui.QStandardItemModel()
        SetupObjectModel(self.objmodel, Tileset.objects, Tileset.tiles)
        self.objectList.setModel(self.objmodel)

        # Creates the Tab Widget for behaviours and objects
        self.tabWidget = QtWidgets.QTabWidget()
        self.tileWidget = tileOverlord()
        self.paletteWidget = paletteWidget(self)

        # Second Tab
        self.container = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.objectList)
        layout.addWidget(self.tileWidget)
        self.container.setLayout(layout)

        # Sets the Tabs
        self.tabWidget.addTab(self.paletteWidget, 'Behaviours')
        self.tabWidget.addTab(self.container, 'Objects')

        # Connections do things!
        self.tileDisplay.clicked.connect(self.paintFormat)
        self.tileDisplay.mouseMoved.connect(self.updateInfo)
        self.objectList.clicked.connect(self.tileWidget.setObject)

        # Layout
        frameLayout.addWidget(self.infoDisplay, 0, 0, 1, 1)
        frameLayout.addWidget(self.tileDisplay, 1, 0)
        frameLayout.addWidget(self.tabWidget, 0, 1, 2, 1)
        self.setCentralWidget(frame)


    def updateInfo(self, x, y):

        index = [self.tileDisplay.indexAt(QtCore.QPoint(x, y))]
        curTile = Tileset.tiles[index[0].row()]
        info = self.infoDisplay
        palette = self.paletteWidget

        propertyList = []
        propertyText = ''


        if curTile.byte4 == 1:
            propertyList.append('Solid')
        elif curTile.byte4 == 2:
            propertyList.append('Solid-on-Top')
        elif curTile.byte4 == 3:
            propertyList.append('Solid-on-Bottom')
        elif curTile.byte4 == 0x21:
            propertyList.append('Sloped Solid-on-Top (1)')
        elif curTile.byte4 == 0x22:
            propertyList.append('Sloped Solid-on-Top (2)')


        if len(propertyList) == 0:
            propertyText = 'None'
        elif len(propertyList) == 1:
            propertyText = propertyList[0]
        else:
            propertyText = propertyList.pop(0)
            for string in propertyList:
                propertyText = propertyText + ', ' + string

        if palette.ParameterList[curTile.byte0] is not None:
            if curTile.byte2 < len(palette.ParameterList[curTile.byte0]):
                parameter = palette.ParameterList[curTile.byte0][curTile.byte2]
            else:
                print('Error 1: %d, %d, %d' % (index[0].row(), curTile.byte0, curTile.byte2))
                parameter = ['', QtGui.QIcon()]
        else:
            parameter = ['', QtGui.QIcon()]


        info.coreImage.setPixmap(palette.coreTypes[curTile.byte0][1].pixmap(24,24))
        info.terrainImage.setPixmap(palette.terrainTypes[curTile.byte5][1].pixmap(24,24))
        info.parameterImage.setPixmap(parameter[1].pixmap(24,24))

        info.coreInfo.setText(palette.coreTypes[curTile.byte0][0])
        info.propertyInfo.setText(propertyText)
        info.terrainInfo.setText(palette.terrainTypes[curTile.byte5][0])
        info.paramInfo.setText(parameter[0])

        info.hexdata.setText('Hex Data: {0} {1} {2} {3}\n                {4} {5} {6} {7}'.format(
                                hex(curTile.byte0), hex(curTile.byte1), hex(curTile.byte2), hex(curTile.byte3),
                                hex(curTile.byte4), hex(curTile.byte5), hex(curTile.byte6), hex(curTile.byte7)))



    def paintFormat(self, index):
        if self.tabWidget.currentIndex() == 1:
            return

        curTile = Tileset.tiles[index.row()]
        palette = self.paletteWidget

        # Find the checked Core widget
        for i, w in enumerate(palette.coreWidgets):
            if w.isChecked():
                curTile.byte0 = i
                break

        curTile.byte1 = 0

        if palette.ParameterList[i] is not None:
            curTile.byte2 = palette.parameters1.currentIndex()

        if palette.ParameterList2[i] is not None:
            curTile.byte3 = palette.parameters2.currentIndex()

        curTile.byte4 = palette.collsType.currentIndex()

        if curTile.byte4 in [4, 5]:
            curTile.byte4 += 0x1D

        curTile.byte5 = palette.terrainType.currentIndex()
        curTile.byte6 = 0
        curTile.byte7 = 0

        self.updateInfo(0, 0)
        self.tileDisplay.update()



#############################################################################################
######################## Widget for selecting the object to export ##########################

class getObjNum(QtWidgets.QDialog):
    """
    Dialog which lets you choose an object to export
    """
    def __init__(self):
        """
        Creates and initializes the dialog
        """
        QtWidgets.QDialog.__init__(self)
        self.setWindowTitle('Choose Object')

        self.objNum = QtWidgets.QSpinBox()
        count = len(Tileset.objects) - 1
        self.objNum.setRange(0, count)
        self.objNum.setValue(0)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.objNum)
        mainLayout.addWidget(buttonBox)

        self.setLayout(mainLayout)
