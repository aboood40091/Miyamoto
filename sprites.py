#!/usr/bin/python
# -*- coding: latin-1 -*-

# Reggie! - New Super Mario Bros. Wii Level Editor
# Version Next Milestone 2 Alpha 0
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



# sprites.py
# Contains code to render sprite images


################################################################
################################################################

# Imports
import math
import os.path
import random

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

OutlineColour = None
OutlinePen = None
OutlineBrush = None
ImageCache = None
Tiles = None
SpritesFolders = []
gamedef = None
RealViewEnabled = False
# NOTE: standard sprite z-value is 25000



################################################################
################################################################
################################################################
####################### Setup Functions ########################

def Reset(theme):
    """Resets Sprites.py to its original settings"""
    global OutlineColour, OutlinePen, OutlineBrush, ImageCache, SpritesFolders
    OutlineColour = theme.color('smi')
    OutlinePen = QtGui.QPen(OutlineColour, 4)
    OutlineBrush = QtGui.QBrush(OutlineColour)
    ResetInitializers()
    ImageCache = {}
    LoadBasicSuite()
    LoadEnvItems()
    LoadMovableItems()
    SpritesFolders = []
    gamedef = None

def ConfigFrom(path):
    """Reconfigures Sprites.py by overwriting certain functions and variables from filepath"""
    file = open(path)
    data = file.read()
    file.close()
    del file
    exec(data)

    OldInitializers = dict(Initializers) # save a copy for later

    excludes = (
        'data', # Locals used in this function
        'filepath',
        'excludes',
        'loc',
        'module',
        'ImageCache', # Important globals
        'OutlineColour',
        'OutlinePen',
        'OutlineBrush',
        'SpritesFolders',
        'Tiles',
        'Reset', # Important functions that can't be changed
        'ConfigFrom',
        'globalize',
        'GetImg',
        'ResetInitializers',
        )

    loc = dict(locals())
    for module in loc:
        if module in excludes: continue
        globalize(module, loc[module])


    # Other stuff
    global Initializers, ImageCache

    for newKey in Initializers: OldInitializers[newKey] = Initializers[newKey]
    Initializers = OldInitializers

    ImageCache = {}


def globalize(name, value):
    """Creates a global variable called name, and sets it to value"""
    exec('global %s' % name)
    exec('%s = value' % name, locals(), globals())


def GetImg(imgname, image=False):
    """Returns the image path from the PNG filename imgname"""
    imgname = str(imgname)

    # Try to find the best path
    path = 'reggiedata/sprites/' + imgname

    if gamedef != None and imgname in gamedef.files:
        path = gamedef.files[imgname].path
    else:
        for folder in reversed(SpritesFolders): # find the most recent copy
            tryPath = folder + '/' + imgname
            if os.path.isfile(tryPath):
                path = tryPath
                break

    # Return the appropriate object
    if os.path.isfile(path):
        if image: return QtGui.QImage(path)
        else: return QtGui.QPixmap(path)


def ResetInitializers():
    """Resets Initializers to the default"""
    global Initializers
    Initializers = {
        20: InitGoomba,
        21: InitParagoomba,
        23: InitHorzMovingPlatform,
        24: InitBuzzyBeetle,
        25: InitSpiny,
        26: InitUpsideDownSpiny,
        27: InitUnusedVertStoneBlock,
        28: InitUnusedHorzStoneBlock,
        30: InitOldStoneBlock,
        31: InitVertMovingPlatform,
        32: InitStarCoin,
        40: InitQuestionSwitch,
        41: InitPSwitch,
        42: InitExcSwitch,
        43: InitQuestionSwitchBlock,
        44: InitPSwitchBlock,
        45: InitExcSwitchBlock,
        46: InitPodoboo,
        47: InitThwomp,
        48: InitGiantThwomp,
        49: InitUnusedSeesaw,
        50: InitFallingPlatform,
        51: InitTiltingGirder,
        52: InitUnusedRotPlatforms,
        54: InitLakitu,
        55: InitUnusedRisingSeesaw,
        56: InitRisingTiltGirder,
        57: InitKoopaTroopa,
        58: InitKoopaParatroopa,
        59: InitLineTiltGirder,
        60: InitSpikeTop,
        61: InitBigBoo,
        63: InitSpikeBall,
        64: InitOutdoorsFog,
        65: InitPipePiranhaUp,
        66: InitPipePiranhaDown,
        67: InitPipePiranhaRight,
        68: InitPipePiranhaLeft,
        69: InitPipeFiretrapUp,
        70: InitPipeFiretrapDown,
        71: InitPipeFiretrapRight,
        72: InitPipeFiretrapLeft,
        73: InitGroundPiranha,
        74: InitBigGroundPiranha,
        75: InitGroundFiretrap,
        76: InitBigGroundFiretrap,
        77: InitShipKey,
        78: InitCloudTrampoline,
        80: InitFireBro,
        81: InitOldStoneBlock,
        82: InitOldStoneBlock,
        83: InitOldStoneBlock,
        84: InitOldStoneBlock,
        85: InitOldStoneBlock,
        87: InitTrampolineWall,
        86: InitOldStoneBlock,
        92: InitBulletBillLauncher,
        93: InitBanzaiBillLauncher,
        94: InitBoomerangBro,
        95: InitHammerBro,
        96: InitRotationControllerSwaying,
        98: InitGiantSpikeBall,
        100: InitSwooper,
        101: InitBobomb,
        102: InitBroozer,
        103: InitPlatformGenerator,
        104: InitAmp,
        105: InitPokey,
        106: InitLinePlatform,
        108: InitAmp,
        109: InitChainBall,
        110: InitSunlight,
        111: InitBlooper,
        112: InitBlooperBabies,
        113: InitFlagpole,
        114: InitFlameCannon,
        115: InitCheep,
        117: InitPulseFlameCannon,
        118: InitDryBones,
        119: InitGiantDryBones,
        120: InitSledgeBro,
        122: InitOneWayPlatform,
        123: InitUnusedCastlePlatform,
        125: InitFenceKoopaHorz,
        126: InitFenceKoopaVert,
        127: InitFlipFence,
        128: InitFlipFenceLong,
        129: Init4Spinner,
        130: InitWiggler,
        131: InitBoo,
        132: InitUnusedBlockPlatform,
        133: InitStalagmitePlatform,
        134: InitCrow,
        135: InitHangingPlatform,
        137: InitSpikedStake,
        138: InitWater,
        139: InitLava,
        140: InitSpikedStake,
        141: InitSpikedStake,
        142: InitSpikedStake,
        143: InitArrow,
        144: InitRedCoin,
        145: InitFloatingBarrel,
        146: InitChainChomp,
        147: InitCoin,
        148: InitSpring,
        149: InitRotationControllerSpinning,
        151: InitPuffer,
        155: InitStarCoin,
        156: InitRedCoinRing,
        157: InitBigBrick,
        158: InitFireSnake,
        160: InitUnusedBlockPlatform,
        161: InitPipeBubbles,
        166: InitBlockTrain,
        170: InitChestnutGoomba,
        171: InitPowerupBubble,
        172: InitScrewMushroom,
        173: InitGiantFloatingLog,
        174: InitOneWayGate,
        175: InitFlyingQBlock,
        176: InitRouletteBlock,
        177: InitFireChomp,
        178: InitScalePlatform,
        179: InitSpecialExit,
        180: InitCheepChomp,
        182: InitDoor,
        185: InitToadBalloon,
        187: InitPlayerBlock,
        188: InitMidwayPoint,
        189: InitLarryKoopa,
        190: InitTiltingGirderUnused,
        191: InitTileEvent,
        193: InitUrchin,
        194: InitMegaUrchin,
        195: InitHuckitCrab,
        196: InitFishbones,
        197: InitClam,
        198: InitGiantgoomba,
        199: InitMegagoomba,
        200: InitMicrogoomba,
        201: InitIcicle,
        202: InitMGCannon,
        203: InitMGChest,
        205: InitGiantBubble,
        206: InitZoom,
        207: InitBlock,
        208: InitBlock,
        209: InitBlock,
        212: InitRollingHill,
        214: InitFreefallPlatform,
        216: InitPoison,
        219: InitLineBlock,
        221: InitBlock,
        222: InitConveyorSpike,
        223: InitSpringBlock,
        224: InitJumboRay,
        227: InitPipeCannon,
        228: InitExtendShroom,
        229: InitSandPillar,
        230: InitBramball,
        231: InitWiggleShroom,
        232: InitMechaKoopa,
        233: InitBulber,
        237: InitPCoin,
        238: InitFoo,
        240: InitGiantWiggler,
        242: InitFallingLedgeBar,
        252: InitRCEDBlock,
        253: InitSpecialCoin,
        255: InitBlock,
        256: InitBlock,
        259: InitDoor,
        262: InitPoltergeistItem,
        263: InitWaterPiranha,
        264: InitWalkingPiranha,
        265: InitFallingIcicle,
        266: InitRotatingChainLink,
        267: InitTiltGrate,
        268: InitLavaGeyser,
        269: InitParabomb,
        271: InitMouser,
        272: InitIceBro,
        274: InitCastleGear,
        275: InitFiveEnemyRaft,
        276: InitDoor,
        277: InitDoor,
        278: InitDoor,
        280: InitGiantIceBlock,
        286: InitWoodCircle,
        287: InitPathIceBlock,
        288: InitOldBarrel,
        289: InitBox,
        291: InitParabeetle,
        292: InitHeavyParabeetle,
        294: InitIceCube,
        295: InitNutPlatform,
        296: InitMegaBuzzy,
        297: InitDragonCoaster,
        299: InitCannonMulti,
        300: InitRotCannon,
        301: InitRotCannonPipe,
        303: InitMontyMole,
        304: InitRotFlameCannon,
        305: InitLightCircle,
        306: InitRotSpotlight,
        308: InitHammerBro,
        309: InitSynchroFlameJet,
        310: InitArrowSign,
        311: InitMegaIcicle,
        314: InitBubbleGen,
        315: InitBolt,
        316: InitBoltBox,
        318: InitBoxGenerator,
        321: InitArrowBlock,
        323: InitBooCircle,
        325: InitGhostHouseStand,
        326: InitKingBill,
        327: InitLinePlatformBolt,
        330: InitRopeLadder,
        331: InitDishPlatform,
        333: InitPlayerBlockPlatform,
        334: InitCheepGiant,
        336: InitWendyKoopa,
        337: InitIggyKoopa,
        339: InitPipe,
        340: InitLemmyKoopa,
        341: InitBigShell,
        342: InitMuncher,
        343: InitFuzzy,
        344: InitMortonKoopa,
        345: InitChainHolder,
        346: InitHangingChainPlatform,
        347: InitRoyKoopa,
        348: InitLudwigVonKoopa,
        352: InitRockyWrench,
        353: InitPipe,
        354: InitBrownBlock,
        355: InitRollingHillWithPipe,
        356: InitBrownBlock,
        357: InitFruit,
        358: InitLavaParticles,
        359: InitWallLantern,
        360: InitRollingHillWithPipe,
        361: InitCrystalBlock,
        362: InitColouredBox,
        366: InitCubeKinokoRot,
        367: InitCubeKinokoLine,
        368: InitFlashRaft,
        369: InitSlidingPenguin,
        370: InitCloudBlock,
        371: InitSpecialCoin,
        374: InitSnowWind,
        376: InitMovingChainLink,
        377: InitPipe,
        378: InitPipe,
        379: InitPipe,
        380: InitPipe,
        382: InitScrewMushroom,
        385: InitIceBlock,
        386: InitPowBlock,
        387: InitBush,
        388: InitBarrel,
        389: InitStarCoin,
        390: InitSpecialCoin,
        391: InitGlowBlock,
        393: InitPropellerBlock,
        394: InitLemmyBall,
        395: InitSpinyCheep,
        396: InitMoveWhenOn,
        397: InitGhostHouseBox,
        402: InitBlock,
        403: InitBlock,
        413: InitWendyRing,
        414: InitGabon,
        415: InitBetaLarryKoopa,
        416: InitInvisibleOneUp,
        417: InitSpinjumpCoin,
        419: InitBowser,
        420: InitGiantGlowBlock,
        422: InitBlock,
        423: InitBlock,
        424: InitPalmTree,
        425: InitJellybeam,
        427: InitKamek,
        428: InitMGPanel,
        432: InitToad,
        433: InitFloatingQBlock,
        434: InitWarpCannon,
        435: InitGhostFog,
        437: InitPurplePole,
        438: InitCageBlocks,
        439: InitCagePeachFake,
        440: InitHorizontalRope,
        441: InitMushroomPlatform,
        443: InitReplayBlock,
        444: InitSwingingVine,
        445: InitCagePeachReal,
        447: InitUnderwaterLamp,
        448: InitMetalBar,
        450: InitPipe,
        451: InitMouserDespawner,
        452: InitDoor,
        453: InitSeaweed,
        455: InitHammerPlatform,
        456: InitBossBridge,
        457: InitSpinningThinBars,
        464: InitSwingingVine,
        466: InitLavaIronBlock,
        467: InitMovingGemBlock,
        469: InitBoltPlatform,
        470: InitBoltPlatformWire,
        471: InitLiftDokan,
        475: InitIceFlow,
        476: InitFlyingWrench,
        477: InitSuperGuideBlock,
        478: InitBowserSwitchSm,
        479: InitBowserSwitchLg,
        }





# Auxiliary Item Classes

class AuxiliaryItem(QtWidgets.QGraphicsItem):
    """Base class for auxiliary objects that accompany specific sprite types"""
    def __init__(self, parent):
        """Generic constructor for auxiliary items"""
        QtWidgets.QGraphicsItem.__init__(self)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QtWidgets.QGraphicsItem.ItemStacksBehindParent, True)
        self.setParentItem(parent)
        self.hover = False

    def boundingRect(self):
        """Required for Qt"""
        return self.BoundingRect


class AuxiliaryTrackObject(AuxiliaryItem):
    """Track shown behind moving platforms to show where they can move"""
    Horizontal = 1
    Vertical = 2

    def __init__(self, parent, width, height, direction):
        """Constructor"""
        AuxiliaryItem.__init__(self, parent)

        self.BoundingRect = QtCore.QRectF(0,0,width*1.5,height*1.5)
        self.setPos(0,0)
        self.width = width
        self.height = height
        self.direction = direction
        self.hover = False

    def SetSize(self, width, height):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0,0,width*1.5,height*1.5)
        self.width = width
        self.height = height

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)

        if self.direction == 1:
            lineY = self.height * 0.75
            painter.drawLine(20, lineY, (self.width*1.5) - 20, lineY)
            painter.drawEllipse(8, lineY - 4, 8, 8)
            painter.drawEllipse((self.width*1.5) - 16, lineY - 4, 8, 8)
        elif self.direction == 2:
            lineX = self.width * 0.75
            painter.drawLine(lineX, 20, lineX, (self.height*1.5) - 20)
            painter.drawEllipse(lineX - 4, 8, 8, 8)
            painter.drawEllipse(lineX - 4, (self.height*1.5) - 16, 8, 8)


class AuxiliaryCircleOutline(AuxiliaryItem):
    def __init__(self, parent, width):
        """Constructor"""
        AuxiliaryItem.__init__(self, parent)

        self.BoundingRect = QtCore.QRectF(0,0,width*1.5,width*1.5)
        self.setPos((8 - (width / 2)) * 1.5, 0)
        self.width = width
        self.hover = False

    def SetSize(self, width):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0,0,width*1.5,width*1.5)
        self.setPos((8 - (width / 2)) * 1.5, 0)
        self.width = width

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)
        painter.setBrush(OutlineBrush)
        painter.drawEllipse(self.BoundingRect)

class AuxiliaryRotationAreaOutline(AuxiliaryItem):
    def __init__(self, parent, width):
        """Constructor"""
        AuxiliaryItem.__init__(self, parent)

        self.BoundingRect = QtCore.QRectF(0,0,width*1.5,width*1.5)
        self.setPos((8 - (width / 2)) * 1.5, (8 - (width / 2)) * 1.5)
        self.width = width
        self.startAngle = 0
        self.spanAngle = 0
        self.hover = False

    def SetAngle(self, startAngle, spanAngle):
        self.startAngle = startAngle * 16
        self.spanAngle = spanAngle * 16

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)
        painter.setBrush(OutlineBrush)
        painter.drawPie(self.BoundingRect, self.startAngle, self.spanAngle)


class AuxiliaryRectOutline(AuxiliaryItem):
    def __init__(self, parent, width, height, xoff=0, yoff=0):
        """Constructor"""
        AuxiliaryItem.__init__(self, parent)

        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.setPos(xoff, yoff)
        self.hover = False

    def SetSize(self, width, height, xoff=0, yoff=0):
        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.setPos(xoff, yoff)

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)
        painter.setBrush(OutlineBrush)
        painter.drawRect(self.BoundingRect)


class AuxiliaryPainterPath(AuxiliaryItem):
    def __init__(self, parent, path, width, height, xoff=0, yoff=0):
        """Constructor"""
        AuxiliaryItem.__init__(self, parent)

        self.PainterPath = path
        self.setPos(xoff, yoff)
        self.fillFlag = True

        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.hover = False

    def SetPath(self, path):
        self.PainterPath = path

    def SetSize(self, width, height, xoff=0, yoff=0):
        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.setPos(xoff, yoff)

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)
        if self.fillFlag: painter.setBrush(OutlineBrush)
        painter.drawPath(self.PainterPath)


class AuxiliaryImage(AuxiliaryItem):
    def __init__(self, parent, width, height):
        """Constructor"""
        AuxiliaryItem.__init__(self, parent)
        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.width = width
        self.height = height
        self.image = None
        self.hover = True

    def SetSize(self, width, height, xoff=0, yoff=0):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.setPos(xoff, yoff)
        self.width = width
        self.height = height

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        if self.image != None:
            painter.drawPixmap(0, 0, self.image)


class AuxiliaryImage_FollowsRect(AuxiliaryImage):
    def __init__(self, parent, width, height):
        """Constructor"""
        AuxiliaryImage.__init__(self, parent, width, height)
        self.alignment = Qt.AlignTop | Qt.AlignLeft
        self.width = self.width
        self.height = self.height
        self.image = None
        self.realimage = None
        # Doing it this way may provide a slight speed boost?
        self.flagPresent = lambda flags, flag: flags | flag == flags

    def move(self, x, y, w, h):
        """Repositions the auxiliary image"""

        # This will be used later
        oldx, oldy = self.x(), self.y()

        # Decide on the height to use
        # This solves the problem of "what if
        # agument w is smaller than self.width?"
        changedSize = False
        if w < self.width:
            self.width = w
            changedSize = True
        if h < self.height:
            self.height = h
            changedSize = True
        if self.image != None:
            if changedSize:
                self.image = self.realimage.copy(0, 0, w, h)
            else:
                self.image = self.realimage
        

        # Find the absolute X-coord
        if self.flagPresent(self.alignment, Qt.AlignLeft):
            newx = x
        elif self.flagPresent(self.alignment, Qt.AlignRight):
            newx = x + w - self.width
        else:
            newx = x + (w/2) - (self.width/2)

        # Find the absolute Y-coord
        if self.flagPresent(self.alignment, Qt.AlignTop):
            newy = y
        elif self.flagPresent(self.alignment, Qt.AlignBottom):
            newy = y + h - self.height
        else:
            newy = y + (h/2) - (self.height/2)

        # Translate that to relative coords
        parent = self.parentItem()
        newx = newx - parent.x()
        newy = newy - parent.y()

        # Set the pos
        self.setPos(newx, newy)

        # Update the affected area of the scene
        if self.scene() != None:
            self.scene().update(oldx + parent.x(), oldy + parent.y(), self.width, self.height)


# ---- Initializers ----
def InitGoomba(sprite): # 20
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Goomba']
    return (-1,-4,18,20)

def InitParagoomba(sprite): # 21
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Paragoomba']
    return (1,-10,24,26)

def InitMicrogoomba(sprite): # 200
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Microgoomba']
    return (4,8,9,9)

def InitGiantgoomba(sprite): # 198
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Giantgoomba']
    return (-6,-19,32,36)

def InitMegagoomba(sprite): # 199
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Megagoomba']
    return (-11,-37,43,54)

def InitChestnutGoomba(sprite): # 170
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ChestnutGoomba']
    return (-6,-8,30,25)

def InitHorzMovingPlatform(sprite): # 23
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()

    xsize = ((sprite.spritedata[5] & 0xF) + 1) << 4

    sprite.dynamicSize = True
    sprite.dynSizer = SizeHorzMovingPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintWoodenPlatform

    sprite.aux.append(AuxiliaryTrackObject(sprite, xsize, 16, AuxiliaryTrackObject.Horizontal))
    return (0,0,xsize,16)

def InitBuzzyBeetle(sprite): # 24
    sprite.dynamicSize = True
    sprite.dynSizer = SizeBuzzyBeetle
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject

    return (0,0,16,16)

def InitSpiny(sprite): # 25
    sprite.dynamicSize = True
    sprite.dynSizer = SizeSpiny
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject

    return (0,0,16,16)

def InitUpsideDownSpiny(sprite): # 26
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SpinyU']
    return (0,0,16,16)

def InitUnusedVertStoneBlock(sprite): # 27
    if 'DSBlockTop' not in ImageCache:
        LoadDSStoneBlocks()

    height = (sprite.spritedata[4] & 3) >> 4
    ysize = 4 << height

    sprite.dynamicSize = True
    sprite.dynSizer = SizeUnusedVertStoneBlock
    sprite.customPaint = True
    sprite.customPainter = PaintDSStoneBlock

    sprite.aux.append(AuxiliaryTrackObject(sprite, 32, ysize, AuxiliaryTrackObject.Vertical))
    return (0,0,32,ysize)

def InitUnusedHorzStoneBlock(sprite): # 28
    if 'DSBlockTop' not in ImageCache:
        LoadDSStoneBlocks()

    height = (sprite.spritedata[4] & 3) >> 4
    ysize = 4 << height

    sprite.dynamicSize = True
    sprite.dynSizer = SizeUnusedHorzStoneBlock
    sprite.customPaint = True
    sprite.customPainter = PaintDSStoneBlock

    sprite.aux.append(AuxiliaryTrackObject(sprite, 32, ysize, AuxiliaryTrackObject.Horizontal))
    return (0,0,32,ysize)

def InitVertMovingPlatform(sprite): # 31
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()

    xsize = ((sprite.spritedata[5] & 0xF) + 1) << 4

    sprite.dynamicSize = True
    sprite.dynSizer = SizeVertMovingPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintWoodenPlatform

    sprite.aux.append(AuxiliaryTrackObject(sprite, xsize, 16, AuxiliaryTrackObject.Vertical))
    return (0,0,xsize,16)

def InitStarCoin(sprite): # 32, 155, 389
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['StarCoin']
    return (0,3,32,32)

def InitQuestionSwitch(sprite): # 40
    if 'QSwitch' not in ImageCache:
        LoadSwitches()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSwitch
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.switchType = 'Q'
    return (0,0,16,16)

def InitPSwitch(sprite): # 41
    if 'PSwitch' not in ImageCache:
        LoadSwitches()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSwitch
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.switchType = 'P'
    return (0,0,16,16)

def InitExcSwitch(sprite): # 42
    if 'ESwitch' not in ImageCache:
        LoadSwitches()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSwitch
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.switchType = 'E'
    return (0,0,16,16)

def InitQuestionSwitchBlock(sprite): # 43
    if 'QSwitch' not in ImageCache:
        LoadSwitches()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['QSwitchBlock']
    return (0,0,16,16)

def InitPSwitchBlock(sprite): # 44
    if 'PSwitch' not in ImageCache:
        LoadSwitches()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PSwitchBlock']
    return (0,0,16,16)

def InitExcSwitchBlock(sprite): # 45
    if 'ESwitch' not in ImageCache:
        LoadSwitches()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ESwitchBlock']
    return (0,0,16,16)

def InitPodoboo(sprite): # 46
    if 'Podoboo' not in ImageCache:
        LoadCastleStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Podoboo']
    return (0,0,16,16)

def InitThwomp(sprite): # 47
    if 'Thwomp' not in ImageCache:
        LoadCastleStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Thwomp']
    return (-6,-6,44,50)

def InitGiantThwomp(sprite): # 48
    if 'GiantThwomp' not in ImageCache:
        LoadCastleStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GiantThwomp']
    return (-8,-8,80,94)

def InitUnusedSeesaw(sprite): # 49
    if 'UnusedPlatform' not in ImageCache:
        LoadUnusedStuff()

    sprite.aux.append(AuxiliaryRotationAreaOutline(sprite, 48))
    sprite.aux[0].setPos(16*8, -36)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeUnusedSeesaw
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['UnusedPlatform']
    return (0,-8,256,16)

def InitFallingPlatform(sprite): # 50
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()

    xsize = (((sprite.spritedata[5]) & 0xF) + 1) << 4

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFallingPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintWoodenPlatform

    return (0,0,xsize,16)

def InitTiltingGirder(sprite): # 51
    if 'TiltingGirder' not in ImageCache:
        LoadPlatformImages()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['TiltingGirder']
    return (0,-18,224,38)

def InitUnusedRotPlatforms(sprite): # 52
    if 'UnusedPlatform' not in ImageCache:
        LoadUnusedStuff()


    plat = ImageCache['UnusedPlatform'].scaled(144, 24)
    img = QtGui.QPixmap(432, 312)
    img.fill(QtGui.QColor.fromRgb(0,0,0,0))
    img = OverlayPixmaps(img, plat, 144,   0, 1, 0.8) # top
    img = OverlayPixmaps(img, plat, 144, 288, 1, 0.8) # bottom
    img = OverlayPixmaps(img, plat,   0, 144, 1, 0.8) # left
    img = OverlayPixmaps(img, plat, 288, 144, 1, 0.8) # right

    sprite.aux.append(AuxiliaryImage(sprite, 432, 312))
    sprite.aux[0].image = img
    sprite.aux[0].setPos(-144-72, -104-52) # It actually ISN'T centered correctly in-game.

    return (0,0,16,16)

def InitLakitu(sprite): # 54
    if 'Lakitu' not in ImageCache:
        LoadDesertStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Lakitu']
    return (-16,-24,38,56)

def InitUnusedRisingSeesaw(sprite): # 55
    if 'UnusedPlatform' not in ImageCache:
        LoadUnusedStuff()

    img = ImageCache['UnusedPlatform'].scaled(24*7, 24)
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = img
    return (0,0,16*7,16)

def InitRisingTiltGirder(sprite): # 56
    if 'RisingTiltGirder' not in ImageCache:
        ImageCache['RisingTiltGirder'] = GetImg('rising_girder.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['RisingTiltGirder']
    return (-32,-10,176,30)

def InitKoopaTroopa(sprite): # 57
    sprite.dynamicSize = True
    sprite.dynSizer = SizeKoopaTroopa
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['KoopaG']
    sprite.FullKoopa = True
    return (-7,-15,24,32)

def InitKoopaParatroopa(sprite): # 58
    sprite.dynamicSize = True
    sprite.dynSizer = SizeKoopaParatroopa
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ParakoopaG']
    return (-7,-12,24,29)

def InitLineTiltGirder(sprite): # 59
    global ImageCache
    if 'LineGirder' not in ImageCache:
        ImageCache['LineGirder'] = GetImg('line_tilt_girder.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['LineGirder']
    return (-8,-10,129,36)

def InitSpikeTop(sprite): # 60
    global ImageCache
    if 'SpikeTopUL' not in ImageCache:
        SpikeTopUp = GetImg('spiketop.png', True)
        SpikeTopDown = GetImg('spiketop_u.png', True)
        ImageCache['SpikeTopUL'] = QtGui.QPixmap.fromImage(SpikeTopUp)
        ImageCache['SpikeTopUR'] = QtGui.QPixmap.fromImage(SpikeTopUp.mirrored(True, False))
        ImageCache['SpikeTopDL'] = QtGui.QPixmap.fromImage(SpikeTopDown)
        ImageCache['SpikeTopDR'] = QtGui.QPixmap.fromImage(SpikeTopDown.mirrored(True, False))

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSpikeTop
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,-4,16,20)

def InitBigBoo(sprite): # 61
    global ImageCache
    if 'BigBoo' not in ImageCache:
        ImageCache['BigBoo'] = GetImg('bigboo.png')

    sprite.aux.append(AuxiliaryImage(sprite, 243, 248))
    sprite.aux[0].image = ImageCache['BigBoo']
    sprite.aux[0].setPos(-48, -48)
    sprite.aux[0].hover = False

    sprite.customPaint = True
    sprite.customPainter = PaintNothing
    return (-38,-80,96,96)

def InitSpikeBall(sprite): # 63
    global ImageCache
    if 'SpikeBall' not in ImageCache:
        LoadCastleStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SpikeBall']
    return (0,0,32,32)

def InitOutdoorsFog(sprite): # 64
    global ImageCache
    if 'OutdoorsFog' not in ImageCache:
        ImageCache['OutdoorsFog'] = GetImg('fog_outdoors.png')

    sprite.zoneRealView = True
    sprite.zoneRealViewer = RealViewOutdoorsFogZone
    sprite.dynamicSize = True
    sprite.dynSizer = SizeOutdoorsFog
    return (0,0,16,16)

def InitPipePiranhaUp(sprite): # 65
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipePlantUp']
    return (2,-32,28,32)

def InitPipePiranhaDown(sprite): # 66
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipePlantDown']
    return (2,32,28,32)

def InitPipePiranhaRight(sprite): # 67
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipePlantRight']
    return (32,2,32,28)

def InitPipePiranhaLeft(sprite): # 68
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipePlantLeft']
    return (-32,2,32,28)

def InitPipeFiretrapUp(sprite): # 69
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipeFiretrapUp']
    return (-4,-29,29,29)

def InitPipeFiretrapDown(sprite): # 70
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipeFiretrapDown']
    return (-4,32,29,29)

def InitPipeFiretrapRight(sprite): # 71
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipeFiretrapRight']
    return (32,6,29,29)

def InitPipeFiretrapLeft(sprite): # 72
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PipeFiretrapLeft']
    return (-29,6,29,29)

def InitGroundPiranha(sprite): # 73
    sprite.dynamicSize = True
    sprite.dynSizer = SizeGroundPiranha
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GroundPiranha']
    return (-20,0,48,26)

def InitBigGroundPiranha(sprite): # 74
    sprite.dynamicSize = True
    sprite.dynSizer = SizeBigGroundPiranha
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BigGroundPiranha']
    return (-65,0,96,52)

def InitGroundFiretrap(sprite): # 75
    sprite.dynamicSize = True
    sprite.dynSizer = SizeGroundFiretrap
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GroundFiretrap']
    return (5,0,24,44)

def InitBigGroundFiretrap(sprite): # 76
    sprite.dynamicSize = True
    sprite.dynSizer = SizeBigGroundFiretrap
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BigGroundFiretrap']
    return (-14,0,47,88)

def InitShipKey(sprite): # 77
    global ImageCache
    if 'ShipKey' not in ImageCache:
        ImageCache['ShipKey'] = GetImg('ship_key.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ShipKey']
    return (-1,-8,19,24)

def InitCloudTrampoline(sprite): # 78
    global ImageCache
    if 'CloudTrBig' not in ImageCache:
        ImageCache['CloudTrBig'] = GetImg('cloud_trampoline_big.png')
        ImageCache['CloudTrSmall'] = GetImg('cloud_trampoline_small.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeCloudTrampoline
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-2,-2,16,16)

def InitFireBro(sprite): # 80
    global ImageCache
    if 'FireBro' not in ImageCache:
        ImageCache['FireBro'] = GetImg('firebro.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FireBro']
    return (-8,-22,26,38)

def InitOldStoneBlock(sprite): # 81, 82, 83, 84, 85, 86
    global ImageCache
    if 'OldStoneTL' not in ImageCache:
        ImageCache['OldStoneTL'] = GetImg('oldstone_tl.png')
        ImageCache['OldStoneT'] = GetImg('oldstone_t.png')
        ImageCache['OldStoneTR'] = GetImg('oldstone_tr.png')
        ImageCache['OldStoneL'] = GetImg('oldstone_l.png')
        ImageCache['OldStoneM'] = GetImg('oldstone_m.png')
        ImageCache['OldStoneR'] = GetImg('oldstone_r.png')
        ImageCache['OldStoneBL'] = GetImg('oldstone_bl.png')
        ImageCache['OldStoneB'] = GetImg('oldstone_b.png')
        ImageCache['OldStoneBR'] = GetImg('oldstone_br.png')
        ImageCache['SpikeU'] = GetImg('spike_up.png')
        ImageCache['SpikeL'] = GetImg('spike_left.png')
        ImageCache['SpikeR'] = GetImg('spike_right.png')
        ImageCache['SpikeD'] = GetImg('spike_down.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeOldStoneBlock
    sprite.customPaint = True
    sprite.customPainter = PaintOldStoneBlock
    sprite.aux.append(AuxiliaryTrackObject(sprite, 16, 16, AuxiliaryTrackObject.Horizontal))
    return (0,0,16,16)

def InitTrampolineWall(sprite): # 87
    if 'UnusedPlatform' not in ImageCache:
        LoadUnusedStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeTrampolineWall
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['UnusedPlatform']
    return (0,0,16,16)

def InitBulletBillLauncher(sprite): # 92
    global ImageCache
    if 'BBLauncherT' not in ImageCache:
        ImageCache['BBLauncherT'] = GetImg('bullet_launcher_top.png')
        ImageCache['BBLauncherM'] = GetImg('bullet_launcher_middle.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBulletBillLauncher
    sprite.customPaint = True
    sprite.customPainter = PaintBulletBillLauncher
    return (0,0,16,16)

def InitBanzaiBillLauncher(sprite): # 93
    global ImageCache
    if 'BanzaiLauncher' not in ImageCache:
        ImageCache['BanzaiLauncher'] = GetImg('banzai_launcher.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BanzaiLauncher']
    return (-32,-68,64,84)

def InitBoomerangBro(sprite): # 94
    global ImageCache
    if 'BoomerangBro' not in ImageCache:
        ImageCache['BoomerangBro'] = GetImg('boomerangbro.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BoomerangBro']
    return (-8,-22,25,38)

def InitHammerBro(sprite): # 95, 308
    global ImageCache
    if 'HammerBro' not in ImageCache:
        ImageCache['HammerBro'] = GetImg('hammerbro.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['HammerBro']
    return (-8,-24,25,40)

def InitRotationControllerSwaying(sprite): # 96
    sprite.setZValue(100000)
    sprite.dynamicSize = True
    sprite.dynSizer = SizeRotationControllerSwaying

    sprite.aux.append(AuxiliaryRotationAreaOutline(sprite, 48))
    return (0,0,16,16)

def InitGiantSpikeBall(sprite): # 98
    if 'SpikeBall' not in ImageCache:
        LoadCastleStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GiantSpikeBall']
    return (-32,-16,64,64)

def InitSwooper(sprite): # 100
    global ImageCache
    if 'Swooper' not in ImageCache:
        ImageCache['Swooper'] = GetImg('swooper.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Swooper']
    return (2,0,11,18)

def InitBobomb(sprite): # 101
    global ImageCache
    if 'Bobomb' not in ImageCache:
        ImageCache['Bobomb'] = GetImg('bobomb.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Bobomb']
    return (-8,-8,21,24)

def InitBroozer(sprite): # 102
    global ImageCache
    if 'Broozer' not in ImageCache:
        ImageCache['Broozer'] = GetImg('broozer.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Broozer']
    return (-9,-17,34,34)

def InitPlatformGenerator(sprite): # 103
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()

    sprite.dynamicSize = True
    sprite.dynSizer = SizePlatformGenerator
    sprite.customPaint = True
    sprite.customPainter = PaintPlatformGenerator
    return (0,0,16,16)

def InitAmp(sprite): # 104, 108
    global ImageCache
    if 'Amp' not in ImageCache:
        ImageCache['Amp'] = GetImg('amp.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Amp']
    return (-8,-8,40,34)

def InitPokey(sprite): # 105
    if 'PokeyTop' not in ImageCache:
        LoadDesertStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizePokey
    sprite.customPaint = True
    sprite.customPainter = PaintPokey
    return (-4,0,24,32)

def InitLinePlatform(sprite): # 106
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeLinePlatform
    sprite.customPaint = True
    sprite.customPainter = PaintWoodenPlatform
    return (0,8,16,16)

def InitChainBall(sprite): # 109
    global ImageCache
    if 'ChainBallU' not in ImageCache:
        ImageCache['ChainBallU'] = GetImg('chainball_up.png')
        ImageCache['ChainBallR'] = GetImg('chainball_right.png')
        ImageCache['ChainBallD'] = GetImg('chainball_down.png')
        ImageCache['ChainBallL'] = GetImg('chainball_left.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeChainBall
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitSunlight(sprite): # 110
    global ImageCache
    if 'Sunlight' not in ImageCache:
        ImageCache['Sunlight'] = GetImg('sunlight.png')

    i = ImageCache['Sunlight']
    sprite.aux.append(AuxiliaryImage_FollowsRect(sprite, i.width(), i.height()))
    sprite.aux[0].realimage = i
    sprite.aux[0].alignment = Qt.AlignTop | Qt.AlignRight
    sprite.scene().views()[0].repaint.connect(lambda: MoveSunlight(sprite))
    sprite.aux[0].hover = False

    return (0,0,16,16)

def MoveSunlight(sprite): # 110
    if RealViewEnabled:
        sprite.aux[0].image = ImageCache['Sunlight']
    else:
        sprite.aux[0].image = None
    zone = sprite.getZone(True)
    if zone is None:
        self.aux[0].image = None
        return
    zoneRect = QtCore.QRectF(zone.objx * 1.5, zone.objy * 1.5, zone.width * 1.5, zone.height * 1.5)
    view = sprite.scene().views()[0]
    viewRect = view.mapToScene(view.viewport().rect()).boundingRect()
    bothRect = zoneRect & viewRect
    
    try:
        sprite.aux[0].move(bothRect.x(), bothRect.y(), bothRect.width(), bothRect.height())
    except RuntimeError: pass

def InitBlooper(sprite): # 111
    global ImageCache
    if 'Blooper' not in ImageCache:
        ImageCache['Blooper'] = GetImg('blooper.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Blooper']
    return (-3,-2,23,30)

def InitBlooperBabies(sprite): # 112
    global ImageCache
    if 'BlooperBabies' not in ImageCache:
        ImageCache['BlooperBabies'] = GetImg('blooper_babies.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BlooperBabies']
    return (-5,-2,27,36)

def InitFlagpole(sprite): # 113
    if 'Flagpole' not in ImageCache:
        LoadFlagpole()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFlagpole
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Flagpole']

    sprite.aux.append(AuxiliaryImage(sprite, 144, 149))
    return (-30,-144,46,160)

def InitFlameCannon(sprite): # 114
    global ImageCache
    if 'FlameCannonR' not in ImageCache:
        LoadFlameCannon()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFlameCannon
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,64,16)

def InitCheep(sprite): # 115
    global ImageCache
    if 'CheepRed' not in ImageCache:
        ImageCache['CheepRed'] = GetImg('cheep_red.png')
        ImageCache['CheepGreen'] = GetImg('cheep_green.png')
        ImageCache['CheepYellow'] = GetImg('cheep_yellow.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeCheep
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-1,-1,19,18)

def InitPulseFlameCannon(sprite): # 117
    global ImageCache
    if 'PulseFlameCannon' not in ImageCache:
        LoadPulseFlameCannon()

    sprite.dynamicSize = True
    sprite.dynSizer = SizePulseFlameCannon
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,112,16)

def InitDryBones(sprite): # 118
    global ImageCache
    if 'DryBones' not in ImageCache:
        ImageCache['DryBones'] = GetImg('drybones.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['DryBones']
    return (-7,-16,23,32)

def InitGiantDryBones(sprite): # 119
    global ImageCache
    if 'GiantDryBones' not in ImageCache:
        ImageCache['GiantDryBones'] = GetImg('giant_drybones.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GiantDryBones']
    return (-13,-24,29,40)

def InitSledgeBro(sprite): # 120
    global ImageCache
    if 'SledgeBro' not in ImageCache:
        ImageCache['SledgeBro'] = GetImg('sledgebro.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SledgeBro']
    return (-8,-28.5,32,45)

def InitOneWayPlatform(sprite): # 122
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeOneWayPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintWoodenPlatform
    return (0,0,16,16)

def InitUnusedCastlePlatform(sprite): # 123
    global ImageCache
    if 'UnusedCastlePlatform' not in ImageCache:
        LoadUnusedStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeUnusedCastlePlatform
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['UnusedCastlePlatform']
    return (0,0,255,255)

def InitFenceKoopaHorz(sprite): # 125
    global ImageCache
    if 'FenceKoopaHG' not in ImageCache:
        ImageCache['FenceKoopaHG'] = GetImg('fencekoopa_horz.png')
    if 'FenceKoopaHR' not in ImageCache:
        ImageCache['FenceKoopaHR'] = GetImg('fencekoopa_horz_red.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFenceKoopaHorz
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-3,-12,22,30)

def InitFenceKoopaVert(sprite): # 126
    global ImageCache
    if 'FenceKoopaVG' not in ImageCache:
        ImageCache['FenceKoopaVG'] = GetImg('fencekoopa_vert.png')
    if 'FenceKoopaVR' not in ImageCache:
        ImageCache['FenceKoopaVR'] = GetImg('fencekoopa_vert_red.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFenceKoopaVert
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-2,-12,22,31)

def InitFlipFence(sprite): # 127
    global ImageCache
    if 'FlipFence' not in ImageCache:
        ImageCache['FlipFence'] = GetImg('flipfence.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FlipFence']
    return (-4,-8,40,48)

def InitFlipFenceLong(sprite): # 128
    global ImageCache
    if 'FlipFenceLong' not in ImageCache:
        ImageCache['FlipFenceLong'] = GetImg('flipfence_long.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FlipFenceLong']
    return (6,0,180,64)

def Init4Spinner(sprite): # 129
    global ImageCache
    if '4Spinner' not in ImageCache:
        ImageCache['4Spinner'] = GetImg('4spinner.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['4Spinner']
    return (-62,-48,142,112)

def InitWiggler(sprite): # 130
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Wiggler']
    return (0,-12,54,28)

def InitBoo(sprite): # 131
    global ImageCache
    if 'Boo1' not in ImageCache:
        ImageCache['Boo1'] = GetImg('boo1.png')

    sprite.aux.append(AuxiliaryImage(sprite, 50, 51))
    sprite.aux[0].image = ImageCache['Boo1']
    sprite.aux[0].setPos(-6, -6)

    sprite.customPaint = True
    sprite.customPainter = PaintNothing
    return (-1,-4,22,22)

def InitUnusedBlockPlatform(sprite): # 132, 160
    global ImageCache
    if 'UnusedBlockPlatform' not in ImageCache:
        LoadUnusedStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeUnusedBlockPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintUnusedBlockPlatform
    return (0,0,48,48)

def InitStalagmitePlatform(sprite): # 133
    global ImageCache
    if 'StalagmitePlatformTop' not in ImageCache:
        ImageCache['StalagmitePlatformTop'] = GetImg('stalagmite_platform_top.png')
        ImageCache['StalagmitePlatformBottom'] = GetImg('stalagmite_platform_bottom.png')

    sprite.aux.append(AuxiliaryImage(sprite, 48, 156))
    sprite.aux[0].image = ImageCache['StalagmitePlatformBottom']
    sprite.aux[0].setPos(24, 60)

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['StalagmitePlatformTop']
    return (0,-8,64,40)

def InitCrow(sprite): # 134
    global ImageCache
    if 'Crow' not in ImageCache:
        ImageCache['Crow'] = GetImg('crow.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Crow']
    return (-3,-2,27,18)

def InitHangingPlatform(sprite): # 135
    global ImageCache
    if 'HangingPlatformTop' not in ImageCache:
        ImageCache['HangingPlatformTop'] = GetImg('hanging_platform_top.png')
        ImageCache['HangingPlatformBottom'] = GetImg('hanging_platform_bottom.png')

    sprite.aux.append(AuxiliaryImage(sprite, 11, 378))
    sprite.aux[0].image = ImageCache['HangingPlatformTop']
    sprite.aux[0].setPos(138,-378)

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['HangingPlatformBottom']
    return (0,0,192,32)

def InitRotBulletLauncher(sprite): # 136
    global ImageCache
    if 'RotLauncherCannon' not in ImageCache:
        ImageCache['RotLauncherCannon'] = GetImg('bullet_cannon_rot_0.png')
        ImageCache['RotLauncherPivot'] = GetImg('bullet_cannon_rot_1.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeRotBulletLauncher
    sprite.customPaint = True
    sprite.customPainter = PaintRotBulletLauncher
    return (-4,0,24,16)

def InitSpikedStake(sprite): # 137, 140, 141, 142
    global ImageCache
    if 'StakeM0up' not in ImageCache:
        for dir in ['up', 'down', 'left', 'right']:
            ImageCache['StakeM0%s' % dir] = GetImg('stake_%s_m_0.png' % dir)
            ImageCache['StakeM1%s' % dir] = GetImg('stake_%s_m_1.png' % dir)
            ImageCache['StakeE0%s' % dir] = GetImg('stake_%s_e_0.png' % dir)
            ImageCache['StakeE1%s' % dir] = GetImg('stake_%s_e_1.png' % dir)

    sprite.aux.append(AuxiliaryTrackObject(sprite, 16, 64, AuxiliaryTrackObject.Vertical))

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSpikedStake
    sprite.customPaint = True
    sprite.customPainter = PaintSpikedStake
    return (0,0,16,16)

def InitWater(sprite): # 138
    global ImageCache
    if 'LiquidWater' not in ImageCache:
        ImageCache['LiquidWater'] = GetImg('liquid_water.png')
        ImageCache['LiquidWaterCrest'] = GetImg('liquid_water_crest.png')
        ImageCache['LiquidWaterRise'] = GetImg('liquid_water_rise.png')
        ImageCache['LiquidWaterRiseCrest'] = GetImg('liquid_water_rise_crest.png')

    sprite.zoneRealView = True
    sprite.zoneRealViewer = RealViewWaterZone
    sprite.dynamicSize = True
    sprite.dynSizer = SizeWater
    return (0,0,16,16)


def InitLava(sprite): # 139
    global ImageCache
    if 'LiquidLava' not in ImageCache:
        ImageCache['LiquidLava'] = GetImg('liquid_lava.png')
        ImageCache['LiquidLavaCrest'] = GetImg('liquid_lava_crest.png')
        ImageCache['LiquidLavaRise'] = GetImg('liquid_lava_rise.png')
        ImageCache['LiquidLavaRiseCrest'] = GetImg('liquid_lava_rise_crest.png')

    sprite.zoneRealView = True
    sprite.zoneRealViewer = RealViewLavaZone
    sprite.dynamicSize = True
    sprite.dynSizer = SizeLava
    return (0,0,16,16)

def InitArrow(sprite): # 143
    global ImageCache
    if 'Arrow0' not in ImageCache:
        for i in range(8):
            ImageCache['Arrow%d' % i] = GetImg('arrow_%d.png' % i)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeArrow
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitRedCoin(sprite): # 144
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['RedCoin']
    return (0,0,16,16)

def InitFloatingBarrel(sprite): # 145
    global ImageCache
    if 'FloatingBarrel' not in ImageCache:
        ImageCache['FloatingBarrel'] = GetImg('barrel_floating.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FloatingBarrel']
    return (-16,-9,48,50)

def InitChainChomp(sprite): # 146
    global ImageCache
    if 'ChainChomp' not in ImageCache:
        ImageCache['ChainChomp'] = GetImg('chain_chomp.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ChainChomp']
    return (-90,-32,109,54)

def InitCoin(sprite): # 147
    global ImageCache
    if 'CoinF' not in ImageCache:
        ImageCache['CoinF'] = OverlayPixmaps(GetImg('iceblock00.png'), ImageCache['Coin'], 0, 0, 0.9, 0.6)
    sprite.dynamicSize = True
    sprite.dynSizer = SizeCoin
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitSpring(sprite): # 148
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Spring']
    return (0,0,16,16)

def InitRotationControllerSpinning(sprite): # 149
    sprite.setZValue(100000)
    return (0,0,16,16)

def InitPuffer(sprite): # 151
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Puffer']
    return (-16,-18,58,54)

def InitRedCoinRing(sprite): # 156
    global ImageCache
    if 'RedCoinRing' not in ImageCache:
        ImageCache['RedCoinRing'] = GetImg('redcoinring.png')

    sprite.aux.append(AuxiliaryImage(sprite, 243, 248))
    sprite.aux[0].image = ImageCache['RedCoinRing']
    sprite.aux[0].setPos(-10, -15)
    sprite.aux[0].hover = False

    sprite.customPaint = True
    sprite.customPainter = PaintNothing
    return (-10,-8,37,48)

def InitBigBrick(sprite): # 157
    global ImageCache
    if 'BigBrick' not in ImageCache:
        ImageCache['BigBrick'] = GetImg('big_brick.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBigBrick
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BigBrick']
    return (0,0,48,48)

def InitFireSnake(sprite): # 158
    global ImageCache
    if 'FireSnake' not in ImageCache:
        LoadFireSnake()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFireSnake
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitPipeBubbles(sprite): # 161

    if 'PipeBubblesU' not in ImageCache:
        LoadPipeBubbles()

    sprite.dynamicSize = True
    sprite.dynSizer = SizePipeBubbles
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,-52,32,53)

def InitBlockTrain(sprite): # 166
    global ImageCache
    if 'BlockTrain' not in ImageCache:
        ImageCache['BlockTrain'] = GetImg('block_train.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBlockTrain
    sprite.customPaint = True
    sprite.customPainter = PaintBlockTrain

    return (0,0,16,16)

def InitPowerupBubble(sprite): # 170
    if 'PowerupBubble' not in ImageCache:
        ImageCache['PowerupBubble'] = GetImg('powerup_bubble.png')
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PowerupBubble']
    return (-8,-8,32,32)

def InitScrewMushroom(sprite): # 172, 382
    global ImageCache
    if 'Bolt' not in ImageCache:
        ImageCache['Bolt'] = GetImg('bolt.png')
    if 'ScrewShroomT' not in ImageCache:
        ImageCache['ScrewShroomT'] = GetImg('screw_shroom_top.png')
        ImageCache['ScrewShroomM'] = GetImg('screw_shroom_middle.png')
        ImageCache['ScrewShroomB'] = GetImg('screw_shroom_bottom.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeScrewMushroom
    sprite.customPaint = True
    sprite.customPainter = PaintScrewMushroom
    return (0,0,16,16)

def InitGiantFloatingLog(sprite): # 173
    global ImageCache
    if 'GiantFloatingLog' not in ImageCache:
        ImageCache['GiantFloatingLog'] = GetImg('giant_floating_log.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GiantFloatingLog']
    return (-152,-32,304,64)

def InitOneWayGate(sprite): # 174
    global ImageCache
    if '1WayGate00' not in ImageCache:
        LoadUnusedStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeOneWayGate
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['1WayGate03']
    return (0,0,16,16)

def InitFlyingQBlock(sprite): # 175
    global ImageCache
    if 'FlyingQBlock' not in ImageCache:
        ImageCache['FlyingQBlock'] = GetImg('flying_qblock.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFlyingQBlock
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject

    return (-12,-16,42,32)

def InitRouletteBlock(sprite): # 176
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['RouletteBlock']
    return (-6,-6,29,29)

def InitFireChomp(sprite): # 177
    global ImageCache
    if 'FireChomp' not in ImageCache:
         ImageCache['FireChomp'] = GetImg('fire_chomp.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FireChomp']
    return (-2,-20,58,40)

def InitScalePlatform(sprite): # 178
    global ImageCache
    if 'WoodenPlatformL' not in ImageCache:
        LoadPlatformImages()
    if 'ScaleRopeH' not in ImageCache:
        ImageCache['ScaleRopeH'] = GetImg('scale_rope_horz.png')
        ImageCache['ScaleRopeV'] = GetImg('scale_rope_vert.png')
        ImageCache['ScalePulley'] = GetImg('scale_pulley.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeScalePlatform
    sprite.customPaint = True
    sprite.customPainter = PaintScalePlatform
    return (0,-10,150,150)

def InitSpecialExit(sprite): # 179
    sprite.aux.append(AuxiliaryRectOutline(sprite, 0, 0))
    sprite.dynamicSize = True
    sprite.dynSizer = SizeSpecialExit
    return (0,0,16,16)

def InitCheepChomp(sprite): # 180
    global ImageCache
    if 'CheepChomp' not in ImageCache:
        ImageCache['CheepChomp'] = GetImg('cheepchomp.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['CheepChomp']
    return (-32,-16,81,71)

def InitToadBalloon(sprite): # 185
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ToadBalloon']
    return (-4,-4,24,24)

def InitPlayerBlock(sprite): # 187
    if 'PlayerBlock' not in ImageCache:
        ImageCache['PlayerBlock'] = GetImg('playerblock.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PlayerBlock']
    return (0,0,16,16)

def InitMidwayPoint(sprite): # 188
    if 'MidwayFlag' not in ImageCache:
        LoadFlagpole()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MidwayFlag']
    return (0,-37,33,54)

def InitLarryKoopa(sprite): # 189
    if 'LarryKoopa' not in ImageCache:
        LoadBosses()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['LarryKoopa']
    return (-17,-33,36,50)

def InitTiltingGirderUnused(sprite): # 190
    if 'TiltingGirder' not in ImageCache:
        LoadPlatformImages()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['TiltingGirder']
    return (0,-18,224,38)

def InitTileEvent(sprite): # 191
    sprite.aux.append(AuxiliaryRectOutline(sprite, 0, 0))
    sprite.dynamicSize = True
    sprite.dynSizer = SizeTileEvent
    return (0,0,16,16)

def InitUrchin(sprite): # 193
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Urchin']
    return (-12,-14,39,38)

def InitMegaUrchin(sprite): # 194
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MegaUrchin']
    return (-40,-46,113,108)

def InitHuckitCrab(sprite): # 195
    sprite.dynamicSize = True
    sprite.dynSizer = SizeHuckitCrab
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,-3,32,19)

def InitFishbones(sprite): # 196
    sprite.dynamicSize = True
    sprite.dynSizer = SizeFishbones
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,-2,28,18)

def InitClam(sprite): # 197
    sprite.dynamicSize = True
    sprite.dynSizer = SizeClam
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-26,-53,70,70)

def InitIcicle(sprite): # 201
    global ImageCache
    if 'IcicleSmall' not in ImageCache:
        LoadIceStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeIcicle
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitMGCannon(sprite): # 202
    if 'MGCannon' not in ImageCache:
        LoadMinigameStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MGCannon']
    return (-12,-42,42,60)

def InitMGChest(sprite): # 203
    if 'MGChest' not in ImageCache:
        LoadMinigameStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MGChest']
    return (-12,-11,40,27)

def InitGiantBubble(sprite): # 205
    global ImageCache
    if 'GiantBubble0' not in ImageCache:
        LoadGiantBubble()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeGiantBubble
    sprite.customPaint = True
    sprite.customPainter = PaintGiantBubble
    return (-61,-68,122,137)

def InitZoom(sprite): # 206
    sprite.aux.append(AuxiliaryRectOutline(sprite, 0, 0))
    sprite.dynamicSize = True
    sprite.dynSizer = SizeZoom
    return (0,0,16,16)

RollingHillSizes = [0, 18*16, 32*16, 50*16, 64*16, 10*16, 14*16, 20*16, 0, 0, 0, 0, 0, 0, 0, 0]
def InitRollingHill(sprite): # 212
    size = (sprite.spritedata[3] >> 4) & 0xF
    realSize = RollingHillSizes[size]

    sprite.dynamicSize = True
    sprite.dynSizer = SizeRollingHill

    sprite.aux.append(AuxiliaryCircleOutline(sprite, realSize))
    return (0,0,16,16)

def InitFreefallPlatform(sprite): # 214
    global ImageCache
    if 'FreefallGH' not in ImageCache:
        ImageCache['FreefallGH'] = GetImg('freefall_gh_platform.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FreefallGH']
    return (0,0,400,79)

def InitPoison(sprite): # 216
    global ImageCache
    if 'LiquidPoison' not in ImageCache:
        ImageCache['LiquidPoison'] = GetImg('liquid_poison.png')
        ImageCache['LiquidPoisonCrest'] = GetImg('liquid_poison_crest.png')
        ImageCache['LiquidPoisonRise'] = GetImg('liquid_poison_rise.png')
        ImageCache['LiquidPoisonRiseCrest'] = GetImg('liquid_poison_rise_crest.png')

    sprite.zoneRealView = True
    sprite.zoneRealViewer = RealViewPoisonZone
    sprite.dynamicSize = True
    sprite.dynSizer = SizePoison
    return (0,0,16,16)

def InitLineBlock(sprite): # 219
    global ImageCache
    if 'LineBlock' not in ImageCache:
        ImageCache['LineBlock'] = GetImg('lineblock.png')

    sprite.aux.append(AuxiliaryImage(sprite, 24, 24))
    sprite.aux[0].setPos(0, 32)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeLineBlock
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitConveyorSpike(sprite): # 222
    global ImageCache
    if 'SpikeU' not in ImageCache:
        ImageCache['SpikeU'] = GetImg('spike_up.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SpikeU']
    return (0,0,16,16)

def InitSpringBlock(sprite): # 223
    sprite.dynamicSize = True
    sprite.dynSizer = SizeSpringBlock
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject

    return (0,0,16,16)

def InitJumboRay(sprite): # 224
    global ImageCache
    if 'JumboRay' not in ImageCache:
        Ray = GetImg('jumbo_ray.png', True)
        ImageCache['JumboRayL'] = QtGui.QPixmap.fromImage(Ray)
        ImageCache['JumboRayR'] = QtGui.QPixmap.fromImage(Ray.mirrored(True, False))

    sprite.dynamicSize = True
    sprite.dynSizer = SizeJumboRay
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,171,79)

def InitPipeCannon(sprite): # 227
    global ImageCache
    if 'PipeCannon' not in ImageCache:
        LoadPipeCannon()

    # sprite.aux[0] is the pipe image
    # sprite.aux[1] is the trajectory indicator
    sprite.aux.append(AuxiliaryImage(sprite, 24, 24))
    sprite.aux[0].hover = False
    sprite.aux.append(AuxiliaryPainterPath(sprite, QtGui.QPainterPath(), 24, 24))
    sprite.aux[1].fillFlag = False
    sprite.aux[1].hover = False
    sprite.aux[0].setZValue(sprite.aux[1].zValue() + 1)
    sprite.dynamicSize = True
    sprite.dynSizer = SizePipeCannon
    sprite.customPaint = True
    sprite.customPainter = PaintNothing
    return (0,0,32,64)

def InitExtendShroom(sprite): # 228
    global ImageCache
    if 'ExtendShroomL' not in ImageCache:
        ImageCache['ExtendShroomB'] = GetImg('extend_shroom_big.png')
        ImageCache['ExtendShroomS'] = GetImg('extend_shroom_small.png')
        ImageCache['ExtendShroomC'] = GetImg('extend_shroom_cont.png')
        ImageCache['ExtendShroomStem'] = GetImg('extend_shroom_stem.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeExtendShroom
    sprite.customPaint = True
    sprite.customPainter = PaintExtendShroom

    return (0,0,16,16)

def InitSandPillar(sprite): # 229
    global ImageCache
    if 'SandPillar' not in ImageCache:
        ImageCache['SandPillar'] = GetImg('sand_pillar.png')

    sprite.alpha = 0.65
    sprite.customPaint = True
    sprite.customPainter = PaintAlphaObject
    sprite.image = ImageCache['SandPillar']
    return (-33,-150,84,167)

def InitBramball(sprite): # 230
    global ImageCache
    if 'Bramball' not in ImageCache:
        ImageCache['Bramball'] = GetImg('bramball.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Bramball']
    return (-32,-48,80,64)

def InitWiggleShroom(sprite): # 231
    global ImageCache
    if 'WiggleShroomL' not in ImageCache:
        ImageCache['WiggleShroomL'] = GetImg('wiggle_shroom_left.png')
        ImageCache['WiggleShroomM'] = GetImg('wiggle_shroom_middle.png')
        ImageCache['WiggleShroomR'] = GetImg('wiggle_shroom_right.png')
        ImageCache['WiggleShroomS'] = GetImg('wiggle_shroom_stem.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeWiggleShroom
    sprite.customPaint = True
    sprite.customPainter = PaintWiggleShroom

    return (0,0,16,16)

def InitMechaKoopa(sprite): # 232
    global ImageCache
    if 'Mechakoopa' not in ImageCache:
        ImageCache['Mechakoopa'] = GetImg('mechakoopa.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Mechakoopa']
    return (-8,-14,30,32)

def InitBulber(sprite): # 233
    global ImageCache
    if 'Bulber' not in ImageCache:
        ImageCache['Bulber'] = GetImg('bulber.png')

    sprite.aux.append(AuxiliaryImage(sprite, 243, 248))
    sprite.aux[0].image = ImageCache['Bulber']
    sprite.aux[0].setPos(-8, 0)

    sprite.customPaint = True
    sprite.customPainter = PaintNothing
    return (2,-4,50,43)

def InitPCoin(sprite): # 237
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PCoin']
    return (0,0,16,16)

def InitFoo(sprite): # 238
    global ImageCache
    if 'Foo' not in ImageCache:
        ImageCache['Foo'] = GetImg('foo.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Foo']
    return (-8,-16,29,32)

def InitGiantWiggler(sprite): # 240
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GiantWiggler']
    return (-24,-64,174,82)

def InitFallingLedgeBar(sprite): # 242
    global ImageCache
    if 'FallingLedgeBar' not in ImageCache:
        ImageCache['FallingLedgeBar'] = GetImg('falling_ledge_bar.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FallingLedgeBar']

    return (0,0,80,16)

def InitRCEDBlock(sprite): # 252
    sprite.dynamicSize = True
    sprite.dynSizer = SizeBlock
    sprite.customPaint = True
    sprite.customPainter = PaintRCEDBlock
    return (0,0,16,16)

def InitSpecialCoin(sprite): # 253, 371, 390
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SpecialCoin']
    return (0,0,16,16)

DoorTypes = {
    182: ('Door', (0,0,32,48)), # Switch Door, same attributes as regular door
    259: ('Door', (0,0,32,48)),
    276: ('GhostDoor', (0,0,32,48)),
    277: ('TowerDoor', (-2,-10.5,53,59)),
    278: ('CastleDoor', (-2,-13,53,62)),
    452: ('BowserDoor', (-53,-134,156,183))
}
def InitDoor(sprite): # 182, 259, 276, 277, 278, 452
    sprite.dynamicSize = True
    sprite.dynSizer = SizeDoor

    sprite.customPaint = True
    if sprite.type == 182: # switch door
        sprite.customPainter = PaintAlphaObject
        sprite.alpha = 0.5
    else:
        sprite.customPainter = PaintGenericObject

    type = DoorTypes[sprite.type]
    sprite.doorType = type[0]
    sprite.doorSize = type[1]
    return type[1]

def InitPoltergeistItem(sprite): # 262
    global ImageCache
    if 'PoltergeistItem' not in ImageCache:
        LoadPolterItems()

    sprite.aux.append(AuxiliaryImage(sprite, 60, 60))
    sprite.aux[0].image = ImageCache['PolterQBlock']
    sprite.aux[0].setPos(-18, -18)
    sprite.aux[0].hover = False

    sprite.dynamicSize = True
    sprite.dynSizer = SizePoltergeistItem
    sprite.customPaint = True
    sprite.customPainter = PaintNothing
    return (0,0,16,16)

def InitWaterPiranha(sprite): # 263
    global ImageCache
    if 'WaterPiranha' not in ImageCache:
        ImageCache['WaterPiranha'] = GetImg('water_piranha.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['WaterPiranha']
    return (-5,-145,26,153)

def InitWalkingPiranha(sprite): # 264
    global ImageCache
    if 'WalkPiranha' not in ImageCache:
        ImageCache['WalkPiranha'] = GetImg('walk_piranha.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['WalkPiranha']
    return (-4,-50,23,66)

def InitFallingIcicle(sprite): # 265
    global ImageCache
    if 'IcicleSmall' not in ImageCache:
        LoadIceStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFallingIcicle
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitRotatingChainLink(sprite): # 266
    global ImageCache
    if 'RotatingChainLink' not in ImageCache:
        ImageCache['RotatingChainLink'] = GetImg('rotating_chainlink.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['RotatingChainLink']
    im = sprite.image
    return (-((2.0/3.0)*(im.width()/2.0-12.0)), -((2.0/3.0)*(im.height()/2.0-12.0)), (2.0/3.0)*im.width(), (2.0/3.0)*im.height())


def InitTiltGrate(sprite): # 267
    global ImageCache
    if 'TiltGrateU' not in ImageCache:
        ImageCache['TiltGrateU'] = GetImg('tilt_grate_up.png')
        ImageCache['TiltGrateD'] = GetImg('tilt_grate_down.png')
        ImageCache['TiltGrateL'] = GetImg('tilt_grate_left.png')
        ImageCache['TiltGrateR'] = GetImg('tilt_grate_right.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeTiltGrate
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitLavaGeyser(sprite): # 268
    global ImageCache
    if 'LavaGeyser0' not in ImageCache:
        ImageCache['LavaGeyser0'] = GetImg('lava_geyser_0.png')
        ImageCache['LavaGeyser1'] = GetImg('lava_geyser_1.png')
        ImageCache['LavaGeyser2'] = GetImg('lava_geyser_2.png')
        ImageCache['LavaGeyser3'] = GetImg('lava_geyser_3.png')
        ImageCache['LavaGeyser4'] = GetImg('lava_geyser_4.png')
        ImageCache['LavaGeyser5'] = GetImg('lava_geyser_5.png')
        ImageCache['LavaGeyser6'] = GetImg('lava_geyser_6.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeLavaGeyser
    sprite.setZValue(1)
    sprite.customPaint = True
    sprite.customPainter = PaintAlphaObject
    return (-37,-186,69,200)

def InitParabomb(sprite): # 269
    global ImageCache
    if 'Parabomb' not in ImageCache:
        ImageCache['Parabomb'] = GetImg('parabomb.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Parabomb']
    return (-2,-16,20,32)

def InitMouser(sprite): # 271
    global ImageCache
    if 'Mouser' not in ImageCache:
        ImageCache['Mouser'] = GetImg('mouser.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeMouser
    sprite.customPaint = True
    sprite.customPainter = PaintMouser
    sprite.image = ImageCache['Mouser']
    return (0,-2,30,19)

def InitIceBro(sprite): # 272
    global ImageCache
    if 'IceBro' not in ImageCache:
        ImageCache['IceBro'] = GetImg('icebro.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['IceBro']
    return (-5,-23,26,39)

def InitCastleGear(sprite):
    global ImageCache
    if 'CastleGearL' not in ImageCache or 'CastleGearS' not in ImageCache:
        LoadCastleGears()
    sprite.dynamicSize = True
    sprite.dynSizer = SizeCastleGear
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    isBig = (sprite.spritedata[4] & 0xF) == 1
    sprite.image = ImageCache['CastleGearL'] if isBig else ImageCache['CastleGearS']
    return (-(((sprite.image.width()/2.0)-12)*(2.0/3.0)), -(((sprite.image.height()/2.0)-12)*(2.0/3.0)), sprite.image.width()*(2.0/3.0), sprite.image.height()*(2.0/3.0))

def InitFiveEnemyRaft(sprite): # 275
    global ImageCache
    if 'FiveEnemyRaft' not in ImageCache:
        ImageCache['FiveEnemyRaft'] = GetImg('5_enemy_max_raft.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FiveEnemyRaft']
    return(0,-8,385,38)

def InitGiantIceBlock(sprite): # 280
    global ImageCache
    if 'IcicleSmall' not in ImageCache:
        LoadIceStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeGiantIceBlock
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,64,64)

def InitWoodCircle(sprite): # 286
    global ImageCache
    if 'WoodCircle0' not in ImageCache:
        ImageCache['WoodCircle0'] = GetImg('wood_circle_0.png')
        ImageCache['WoodCircle1'] = GetImg('wood_circle_1.png')
        ImageCache['WoodCircle2'] = GetImg('wood_circle_2.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeWoodCircle
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitPathIceBlock(sprite): # 287
    global ImageCache
    if 'PathIceBlock' not in ImageCache:
        LoadIceStuff()

    sprite.alpha = 0.8
    sprite.dynamicSize = True
    sprite.dynSizer = SizePathIceBlock
    sprite.customPaint = True
    sprite.customPainter = PaintAlphaObject
    return (0,0,16,16)

def InitOldBarrel(sprite): # 288
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['OldBarrel']
    return (1,-7,30,30)

def InitBox(sprite): # 289
    global ImageCache
    if 'BoxWoodSmall' not in ImageCache:
        ImageCache['BoxWoodSmall'] = GetImg('box_wood_small.png')
        ImageCache['BoxWoodWide'] = GetImg('box_wood_wide.png')
        ImageCache['BoxWoodTall'] = GetImg('box_wood_tall.png')
        ImageCache['BoxWoodBig'] = GetImg('box_wood_big.png')
        ImageCache['BoxMetalSmall'] = GetImg('box_metal_small.png')
        ImageCache['BoxMetalWide'] = GetImg('box_metal_wide.png')
        ImageCache['BoxMetalTall'] = GetImg('box_metal_tall.png')
        ImageCache['BoxMetalBig'] = GetImg('box_metal_big.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBox
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,32,32)

def InitParabeetle(sprite): # 291
    global ImageCache
    if 'Parabeetle0' not in ImageCache:
        ImageCache['Parabeetle0'] = GetImg('parabeetle_right.png')
        ImageCache['Parabeetle1'] = GetImg('parabeetle_left.png')
        ImageCache['Parabeetle2'] = GetImg('parabeetle_moreright.png')
        ImageCache['Parabeetle3'] = GetImg('parabeetle_atyou.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeParabeetle
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,-8,16,28)

def InitHeavyParabeetle(sprite): # 292
    global ImageCache
    if 'HeavyParabeetle0' not in ImageCache:
        ImageCache['HeavyParabeetle0'] = GetImg('heavy_parabeetle_right.png')
        ImageCache['HeavyParabeetle1'] = GetImg('heavy_parabeetle_left.png')
        ImageCache['HeavyParabeetle2'] = GetImg('heavy_parabeetle_moreright.png')
        ImageCache['HeavyParabeetle3'] = GetImg('heavy_parabeetle_atyou.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeHeavyParabeetle
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,-58,16,67)

def InitIceCube(sprite): # 294
    global ImageCache
    if 'IceCube' not in ImageCache:
        ImageCache['IceCube'] = GetImg('ice_cube.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['IceCube']
    return (0,0,16,16)

def InitNutPlatform(sprite): # 295
    global ImageCache
    if 'NutPlatform' not in ImageCache:
        ImageCache['NutPlatform'] = GetImg('nut_platform.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeNutPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-16,0,96,32)

def InitMegaBuzzy(sprite): # 296
    global ImageCache
    if 'MegaBuzzyL' not in ImageCache:
        ImageCache['MegaBuzzyL'] = GetImg('megabuzzy_left.png')
        ImageCache['MegaBuzzyF'] = GetImg('megabuzzy_front.png')
        ImageCache['MegaBuzzyR'] = GetImg('megabuzzy_right.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.dynamicSize = True
    sprite.dynSizer = SizeMegaBuzzy
    return (-41,-80,98,96)

def InitDragonCoaster(sprite): # 297
    global ImageCache
    if 'DragonHead' not in ImageCache:
        ImageCache['DragonHead'] = GetImg('dragon_coaster_head.png')
        ImageCache['DragonBody'] = GetImg('dragon_coaster_body.png')
        ImageCache['DragonTail'] = GetImg('dragon_coaster_tail.png')

    raw_size = sprite.spritedata[5] & 15
    if raw_size == 0:
        xsize = 32
        xoffset = 0
    else:
        xsize = (raw_size * 32) + 32
        xoffset =  (xsize - 32) * -1

    sprite.dynamicSize = True
    sprite.dynSizer = SizeDragonCoaster
    sprite.customPaint = True
    sprite.customPainter = PaintDragonCoaster
    return (xoffset,-2,xsize,20)

def InitCannonMulti(sprite): # 299
    global ImageCache
    if 'CannonMulti0' not in ImageCache:
        LoadCannonMulti()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeCannonMulti
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-8,-11,32,28)

def InitRotCannon(sprite): # 300
    global ImageCache
    if 'RotCannon' not in ImageCache:
        ImageCache['RotCannon'] = GetImg('rot_cannon.png')
        ImageCache['RotCannonU'] = GetImg('rot_cannon_u.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeRotCannon
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitRotCannonPipe(sprite): # 301
    global ImageCache
    if 'RotCannonPipe' not in ImageCache:
        ImageCache['RotCannonPipe'] = GetImg('rot_cannon_pipe.png')
        ImageCache['RotCannonPipeU'] = GetImg('rot_cannon_pipe_u.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeRotCannonPipe
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitMontyMole(sprite): # 303
    global ImageCache
    if 'Mole' not in ImageCache:
        ImageCache['Mole'] = GetImg('monty_mole.png')
        ImageCache['MoleCave'] = GetImg('monty_mole_hole.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeMontyMole
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-6,-4,28,25)

def InitRotFlameCannon(sprite): # 304
    global ImageCache
    if 'RotFlameCannon' not in ImageCache:
        LoadRotFlameCannon()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeRotFlameCannon
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,-2,73,18)

def InitLightCircle(sprite): # 305
    global ImageCache
    if 'LightCircle' not in ImageCache:
        ImageCache['LightCircle'] = GetImg('light_circle.png')

    sprite.aux.append(AuxiliaryImage(sprite, 128, 128))
    sprite.aux[0].image = ImageCache['LightCircle']
    sprite.aux[0].setPos(-48,-48)
    sprite.aux[0].hover = False
    return (0,0,16,16)

def InitRotSpotlight(sprite): # 306
    global ImageCache
    if 'RotSpotlight0' not in ImageCache:
        LoadRotSpotlight()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeRotSpotlight
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-24,-64,62,104)

def InitSynchroFlameJet(sprite): # 309
    global ImageCache
    if 'SynchroFlameJet0' not in ImageCache:
        LoadSynchroFlameJet()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSynchroFlameJet
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,112,16)

def InitArrowSign(sprite): # 310
    global ImageCache
    if 'ArrowSign0' not in ImageCache:
        for i in range(8):
            ImageCache['ArrowSign%d' % i] = GetImg('arrow_sign_%d.png' % i)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeArrowSign
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-8,-16,32,32)

def InitMegaIcicle(sprite): # 311
    global ImageCache
    if 'MegaIcicle' not in ImageCache:
        ImageCache['MegaIcicle'] = GetImg('mega_icicle.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MegaIcicle']
    return (-24,-3,64,85)

def InitBubbleGen(sprite): # 314
    global ImageCache
    if 'BubbleGenEffect' not in ImageCache:
        ImageCache['BubbleGenEffect'] = GetImg('bubble_gen.png')

    sprite.zoneRealView = True
    sprite.zoneRealViewer = RealViewBubbleGen
    sprite.dynamicSize = True
    sprite.dynSizer = SizeBubbleGen
    return (0,0,16,16)

def InitBolt(sprite): # 315
    global ImageCache
    if 'Bolt' not in ImageCache:
        ImageCache['Bolt'] = GetImg('bolt.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Bolt']
    return (2,0,28,16)

def InitBoltBox(sprite): # 316
    global ImageCache
    if 'BoltBox' not in ImageCache:
        ImageCache['BoltBoxTL'] = GetImg('boltbox_tl.png')
        ImageCache['BoltBoxT'] = GetImg('boltbox_t.png')
        ImageCache['BoltBoxTR'] = GetImg('boltbox_tr.png')
        ImageCache['BoltBoxL'] = GetImg('boltbox_l.png')
        ImageCache['BoltBoxM'] = GetImg('boltbox_m.png')
        ImageCache['BoltBoxR'] = GetImg('boltbox_r.png')
        ImageCache['BoltBoxBL'] = GetImg('boltbox_bl.png')
        ImageCache['BoltBoxB'] = GetImg('boltbox_b.png')
        ImageCache['BoltBoxBR'] = GetImg('boltbox_br.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBoltBox
    sprite.customPaint = True
    sprite.customPainter = PaintBoltBox
    return (0,0,16,16)

def InitBoxGenerator(sprite): # 318
    if 'BoxGenerator' not in ImageCache:
        ImageCache['BoxGenerator'] = GetImg('box_generator.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BoxGenerator']
    return (0,-64,64,64)

def InitArrowBlock(sprite): # 321
    global ImageCache
    if 'ArrowBlock0' not in ImageCache:
        ImageCache['ArrowBlock0'] = GetImg('arrow_block_up.png')
        ImageCache['ArrowBlock1'] = GetImg('arrow_block_down.png')
        ImageCache['ArrowBlock2'] = GetImg('arrow_block_left.png')
        ImageCache['ArrowBlock3'] = GetImg('arrow_block_right.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeArrowBlock
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,32,32)

def InitBooCircle(sprite): # 323
    global ImageCache
    if 'Boo2' not in ImageCache:
        ImageCache['Boo1'] = GetImg('boo1.png')
        ImageCache['Boo2'] = GetImg('boo2.png')
        ImageCache['Boo3'] = GetImg('boo3.png')
        ImageCache['Boo4'] = GetImg('boo4.png')

    sprite.BooAuxImage = QtGui.QPixmap(1024, 1024)
    sprite.BooAuxImage.fill(QtGui.QColor.fromRgb(0,0,0,0))
    sprite.aux.append(AuxiliaryImage(sprite, 1024, 1024))
    sprite.aux[0].image = sprite.BooAuxImage
    offsetX = ImageCache['Boo1'].width() /4
    offsetY = ImageCache['Boo1'].height()/4
    sprite.aux[0].setPos(-512+offsetX, -512+offsetY)
    sprite.aux[0].hover = False

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBooCircle
    return (0,0,16,16)

def InitGhostHouseStand(sprite): # 325
    global ImageCache
    if 'GhostHouseStand' not in ImageCache:
        ImageCache['GhostHouseStand'] = GetImg('ghost_house_stand.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GhostHouseStand']
    return (0,-16,16,32)

def InitKingBill(sprite): # 326
    global ImageCache

    PainterPath = QtGui.QPainterPath()
    sprite.aux.append(AuxiliaryPainterPath(sprite, PainterPath, 256, 256))
    sprite.aux[0].SetSize(2048, 2048, -1024, -1024)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeKingBill
    return (0,0,16,16)

def InitLinePlatformBolt(sprite): # 327
    global ImageCache
    if 'LinePlatformBolt' not in ImageCache:
        ImageCache['LinePlatformBolt'] = GetImg('line_platform_with_bolt.png')


    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['LinePlatformBolt']
    return (0,-16,112,32)

def InitRopeLadder(sprite): # 330
    global ImageCache
    if 'RopeLadder0' not in ImageCache:
        LoadEnvStuff()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeRopeLadder
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-3,-2,22,16)

def InitDishPlatform(sprite): # 331
    global ImageCache
    if 'DishPlatform0' not in ImageCache:
        ImageCache['DishPlatform0'] = GetImg('dish_platform_short.png')
        ImageCache['DishPlatform1'] = GetImg('dish_platform_long.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeDishPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-144,-10,304,130)

def InitPlayerBlockPlatform(sprite): # 333
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PlayerBlockPlatform']
    return (0,0,64,16)

def InitCheepGiant(sprite): # 334
    global ImageCache
    if 'CheepGiantRedL' not in ImageCache:
        cheep = GetImg('cheep_giant_red.png', True)
        ImageCache['CheepGiantRedL'] = QtGui.QPixmap.fromImage(cheep)
        ImageCache['CheepGiantRedR'] = QtGui.QPixmap.fromImage(cheep.mirrored(True, False))
        ImageCache['CheepGiantGreen'] = GetImg('cheep_giant_green.png')
        ImageCache['CheepGiantYellow'] = GetImg('cheep_giant_yellow.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeCheepGiant
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-6,-7,28,25)

def InitWendyKoopa(sprite): # 336
    if 'WendyKoopa' not in ImageCache:
        LoadBosses()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['WendyKoopa']
    return (-23,-23,41,40)

def InitIggyKoopa(sprite): # 337
    if 'IggyKoopa' not in ImageCache:
        LoadBosses()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['IggyKoopa']
    return (-17,-46,50,62)

def InitPipe(sprite): # 339, 353, 377, 378, 379, 380, 450
    global ImageCache
    if 'PipeTop0' not in ImageCache:
        i = 0
        for colour in ['green', 'red', 'yellow', 'blue']:
            ImageCache['PipeTop%d' % i] = GetImg('pipe_%s_top.png' % colour)
            ImageCache['PipeMiddle%d' % i] = GetImg('pipe_%s_middle.png' % colour)
            ImageCache['PipeBottom%d' % i] = GetImg('pipe_%s_bottom.png' % colour)
            ImageCache['PipeLeft%d' % i] = GetImg('pipe_%s_left.png' % colour)
            ImageCache['PipeCenter%d' % i] = GetImg('pipe_%s_center.png' % colour)
            ImageCache['PipeRight%d' % i] = GetImg('pipe_%s_right.png' % colour)
            i += 1

    sprite.dynamicSize = True
    sprite.dynSizer = SizePipe
    sprite.customPaint = True
    sprite.customPainter = PaintPipe
    sprite.setZValue(24999)
    return (0,0,16,16)

def InitLemmyKoopa(sprite): # 340
    if 'LemmyKoopa' not in ImageCache:
        LoadBosses()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['LemmyKoopa']
    return (-16,-53,38,70)

def InitBigShell(sprite): # 341
    global ImageCache
    if 'BigShell' not in ImageCache:
        ImageCache['BigShell'] = GetImg('bigshell.png')
        ImageCache['BigShellGrass'] = GetImg('bigshell_grass.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBigShell
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-97,-145,215,168)

def InitMuncher(sprite): # 342
    sprite.dynamicSize = True
    sprite.dynSizer = SizeMuncher
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitFuzzy(sprite): # 343
    global ImageCache
    if 'Fuzzy' not in ImageCache:
        ImageCache['Fuzzy'] = GetImg('fuzzy.png')
        ImageCache['FuzzyGiant'] = GetImg('fuzzy_giant.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFuzzy
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitMortonKoopa(sprite): # 344
    if 'MortonKoopa' not in ImageCache:
        LoadBosses()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MortonKoopa']
    return (-17,-34,51,50)


def InitChainHolder(sprite): # 345
    global ImageCache
    if 'ChainHolder' not in ImageCache:
        ImageCache['ChainHolder'] = GetImg('chain_holder.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ChainHolder']
    return (0,0,16,22)

def InitHangingChainPlatform(sprite): # 346
    global ImageCache
    if 'HangingChainPlatform' not in ImageCache:
        ImageCache['HangingChainPlatformS'] = GetImg('hanging_chain_platform_small.png')
        ImageCache['HangingChainPlatformM'] = GetImg('hanging_chain_platform_medium.png')
        ImageCache['HangingChainPlatformL'] = GetImg('hanging_chain_platform_large.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeHangingChainPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-40,-11,68,27)

def InitRoyKoopa(sprite): # 347
    if 'RoyKoopa' not in ImageCache:
        LoadBosses()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['RoyKoopa']
    return (-27,-24,55,40)

def InitLudwigVonKoopa(sprite): # 348
    if 'LudwigVonKoopa' not in ImageCache:
        LoadBosses()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['LudwigVonKoopa']
    return (-20,-30,42,46)

def InitRockyWrench(sprite): # 352
    global ImageCache
    if 'RockyWrench' not in ImageCache:
        ImageCache['RockyWrench'] = GetImg('rocky_wrench.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['RockyWrench']
    return (4,-41,24,26)

def InitRollingHillWithPipe(sprite): # 355, 360
    sprite.aux.append(AuxiliaryCircleOutline(sprite, 50*16))
    return (0,0,16,16)

def InitBrownBlock(sprite):
    global ImageCache
    if 'BrownBlockTL' not in ImageCache:
        ImageCache['BrownBlockTL'] = GetImg('brown_block_tl.png')
        ImageCache['BrownBlockTM'] = GetImg('brown_block_tm.png')
        ImageCache['BrownBlockTR'] = GetImg('brown_block_tr.png')
        ImageCache['BrownBlockML'] = GetImg('brown_block_ml.png')
        ImageCache['BrownBlockMM'] = GetImg('brown_block_mm.png')
        ImageCache['BrownBlockMR'] = GetImg('brown_block_mr.png')
        ImageCache['BrownBlockBL'] = GetImg('brown_block_bl.png')
        ImageCache['BrownBlockBM'] = GetImg('brown_block_bm.png')
        ImageCache['BrownBlockBR'] = GetImg('brown_block_br.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBrownBlock
    sprite.customPaint = True
    sprite.customPainter = PaintBrownBlock
    if(sprite.type == 354): return (0,0,16,16)
    sprite.aux.append(AuxiliaryTrackObject(sprite, 16, 16, AuxiliaryTrackObject.Horizontal))
    return (0,0,16,16)

def InitFruit(sprite): # 357
    sprite.dynamicSize = True
    sprite.dynSizer = SizeFruit
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitLavaParticles(sprite): # 358
    global ImageCache
    if 'LavaParticlesA' not in ImageCache:
        ImageCache['LavaParticlesA'] = GetImg('lava_particles_a.png')
        ImageCache['LavaParticlesB'] = GetImg('lava_particles_b.png')
        ImageCache['LavaParticlesC'] = GetImg('lava_particles_c.png')

    sprite.zoneRealView = True
    sprite.zoneRealViewer = RealViewLavaParticlesZone
    sprite.dynamicSize = True
    sprite.dynSizer = SizeLavaParticles
    return (0,0,16,16)

def InitWallLantern(sprite): # 359
    global ImageCache
    if 'WallLantern' not in ImageCache:
        ImageCache['WallLantern'] = GetImg('wall_lantern.png')
        ImageCache['WallLanternAux'] = GetImg('wall_lantern_aux.png')

    sprite.aux.append(AuxiliaryImage(sprite, 128, 128))
    sprite.aux[0].image = ImageCache['WallLanternAux']
    sprite.aux[0].setPos(-48,-48)
    sprite.aux[0].hover = False

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['WallLantern']
    return (0,8,16,16)

def InitCrystalBlock(sprite): #361
    global ImageCache
    if 'CrystalBlock0' not in ImageCache:
        for size in range(3):
            ImageCache['CrystalBlock%d' % size] = GetImg('crystal_block_%d.png' % size)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeCrystalBlock
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject

    return (0,0,201,172)

def InitColouredBox(sprite): # 362
    global ImageCache
    if 'CBox0TL' not in ImageCache:
        for colour in [0,1,2,3]:
            for direction in ['TL','T','TR','L','M','R','BL','B','BR']:
                ImageCache['CBox%d%s' % (colour,direction)] = GetImg('cbox_%s_%d.png' % (direction,colour))

    sprite.dynamicSize = True
    sprite.dynSizer = SizeColouredBox
    sprite.customPaint = True
    sprite.customPainter = PaintColouredBox
    return (0,0,16,16)

def InitCubeKinokoRot(sprite): # 366
    global ImageCache
    if 'CubeKinokoG' not in ImageCache:
        ImageCache['CubeKinokoG'] = GetImg('cube_kinoko_g.png')
        ImageCache['CubeKinokoR'] = GetImg('cube_kinoko_r.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeCubeKinokoRot
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitCubeKinokoLine(sprite): # 367
    global ImageCache
    if 'CubeKinokoP' not in ImageCache:
        ImageCache['CubeKinokoP'] = GetImg('cube_kinoko_p.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['CubeKinokoP']
    return (0,0,128,128)

def InitFlashRaft(sprite): # 368
    global ImageCache
    if 'FlashlightRaft' not in ImageCache:
        ImageCache['FlashlightRaft'] = GetImg('flashraft.png')
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FlashlightRaft']
    return (-16,-96,224,114)

def InitSlidingPenguin(sprite): # 369
    global ImageCache
    if 'PenguinL' not in ImageCache:
        penguin = GetImg('sliding_penguin.png', True)
        ImageCache['PenguinL'] = QtGui.QPixmap.fromImage(penguin)
        ImageCache['PenguinR'] = QtGui.QPixmap.fromImage(penguin.mirrored(True, False))

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSlidingPenguin
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-2,-4,36,20)

def InitCloudBlock(sprite): # 370
    global ImageCache
    if 'CloudBlock' not in ImageCache:
        ImageCache['CloudBlock'] = GetImg('cloud_block.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['CloudBlock']
    return (-4,-8,24,24)

def InitSnowWind(sprite): # 374
    global ImageCache
    if 'SnowEffect' not in ImageCache:
        ImageCache['SnowEffect'] = GetImg('snow.png')

    sprite.zoneRealView = True
    sprite.zoneRealViewer = RealViewSnowWindZone
    sprite.dynamicSize = True
    sprite.dynSizer = SizeSnowWind
    return (0,0,16,16)

def InitMovingChainLink(sprite): # 376
    global ImageCache
    if 'MovingChainLink0' not in ImageCache:
        LoadMovingChainLink()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeMovingChainLink
    sprite.customPaint = True
    sprite.customPainter = PaintMovingChainLink
    return (-32,-32,64,64)

def InitIceBlock(sprite): # 385
    global ImageCache
    if 'IceBlock00' not in ImageCache:
        for i in range(4):
            for j in range(4):
                ImageCache['IceBlock%d%d' % (i,j)] = GetImg('iceblock%d%d.png' % (i,j))

    sprite.dynamicSize = True
    sprite.dynSizer = SizeIceBlock
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitPowBlock(sprite): # 386
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['POW']
    return (0,0,16,16)

def InitBush(sprite): # 387
    sprite.setZValue(24999)
    sprite.dynamicSize = True
    sprite.dynSizer = SizeBush
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitBarrel(sprite): # 388
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Barrel']
    return (-4,-8,24,24)

def InitGlowBlock(sprite): # 391
    sprite.aux.append(AuxiliaryImage(sprite, 48, 48))
    sprite.aux[0].image = ImageCache['GlowBlock']
    sprite.aux[0].setPos(-12, -12)

    sprite.customPaint = True
    sprite.customPainter = PaintNothing
    return (0,0,16,16)

def InitPropellerBlock(sprite): # 393
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['PropellerBlock']
    return (-1,-6,18,22)

def InitLemmyBall(sprite): # 394
    global ImageCache
    if 'LemmyBall' not in ImageCache:
        ImageCache['LemmyBall'] = GetImg('lemmyball.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['LemmyBall']
    return (-6,0,29,29)

def InitSpinyCheep(sprite): # 395
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SpinyCheep']
    return (-1,-2,19,19)

def InitMoveWhenOn(sprite): # 396
    if 'MoveWhenOnL' not in ImageCache:
        LoadMoveWhenOn()

    raw_size = sprite.spritedata[5] & 0xF
    if raw_size == 0:
        xoffset = -16
        xsize = 32
    else:
        xoffset = 0
        xsize = raw_size*16

    sprite.dynamicSize = True
    sprite.dynSizer = SizeMoveWhenOn
    sprite.customPaint = True
    sprite.customPainter = PaintMoveWhenOn

    return (xoffset,-2,xsize,20)

def InitGhostHouseBox(sprite): # 397
    global ImageCache
    if 'GHBoxTL' not in ImageCache:
        for direction in ['TL','T','TR','L','M','R','BL','B','BR']:
            ImageCache['GHBox%s' % direction] = GetImg('ghbox_%s.png' % direction)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeGhostHouseBox
    sprite.customPaint = True
    sprite.customPainter = PaintGhostHouseBox
    return (0,0,16,16)

def InitBlock(sprite): # 207, 208, 209, 221, 255, 256, 402, 403, 422, 423
    sprite.dynamicSize = True
    sprite.dynSizer = SizeBlock
    sprite.customPaint = True
    sprite.customPainter = PaintBlock
    return (0,0,16,16)

def InitWendyRing(sprite): # 413
    global ImageCache
    if 'WendyRing' not in ImageCache:
        ImageCache['WendyRing'] = GetImg('wendy_ring.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['WendyRing']
    return (-4,4,24,24)

def InitGabon(sprite): # 414
    global ImageCache
    if 'GabonLeft' not in ImageCache:
        ImageCache['GabonLeft'] = GetImg('gabon_l.png')
        ImageCache['GabonRight'] = GetImg('gabon_r.png')
        ImageCache['GabonDown'] = GetImg('gabon_d.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeGabon
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitInvisibleOneUp(sprite): # 416
    global ImageCache
    if 'InvisibleOneUp' not in ImageCache:
        ImageCache['InvisibleOneUp'] = ImageCache['Blocks'][11].scaled(16, 16)

    sprite.image = ImageCache['InvisibleOneUp']
    sprite.alpha = 0.65

    sprite.customPaint = True
    sprite.customPainter = PaintAlphaObject
    return (3,5,12,11)

def InitBetaLarryKoopa(sprite): # 189
    # For now it will use real Larry's image,
    # but eventually it will need its own
    # because this one looks different.
    if 'LarryKoopa' not in ImageCache:
        LoadBosses()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['LarryKoopa']
    return (-17,-33,36,50)

def InitSpinjumpCoin(sprite): # 417
    global ImageCache

    sprite.customPaint = True
    sprite.customPainter = PaintAlphaObject
    sprite.alpha = 0.55
    sprite.image = ImageCache['Coin']
    return (0,0,16,16)

def InitBowser(sprite): # 419
    global ImageCache
    if 'Bowser' not in ImageCache:
        LoadBosses()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Bowser']
    return (-43,-70,118,86)

def InitGiantGlowBlock(sprite): # 420
    global ImageCache
    if 'GiantGlowBlock' not in ImageCache:
        ImageCache['GiantGlowBlock'] = GetImg('giant_glow_block.png')
        ImageCache['GiantGlowBlockOff'] = GetImg('giant_glow_block_off.png')

    sprite.aux.append(AuxiliaryImage(sprite, 100, 100))
    sprite.aux[0].image = ImageCache['GiantGlowBlock']
    sprite.aux[0].setPos(-25, -30)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeGiantGlowBlock
    sprite.customPaint = True
    sprite.customPainter = PaintNothing
    return (0,0,32,32)

def InitPalmTree(sprite): # 424
    global ImageCache
    if 'PalmTree0' not in ImageCache:
        for i in range(8):
            ImageCache['PalmTree%d' % i] = GetImg('palmtree_%d.png' % i)

    sprite.dynamicSize = True
    sprite.dynSizer = SizePalmTree
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-24.5,0,67,16)

def InitJellybeam(sprite): # 425
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Jellybeam']
    return (-6,0,28,28)

def InitKamek(sprite): # 427
    global ImageCache
    if 'Kamek' not in ImageCache:
        LoadBosses()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Kamek']
    return (-10,-26,38,42)

def InitMGPanel(sprite): # 428
    global ImageCache
    if 'MGPanel' not in ImageCache:
        ImageCache['MGPanel'] = GetImg('minigame_flip_panel.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MGPanel']
    return (-8,-8,48,48)

def InitToad(sprite): # 432
    global ImageCache
    if 'Toad' not in ImageCache:
        ImageCache['Toad'] = GetImg('toad.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Toad']
    return (-1,-16,19,32)

def InitFloatingQBlock(sprite): # 433
    global ImageCache
    if 'FloatingQ' not in ImageCache:
        ImageCache['FloatingQ'] = GetImg('floating_qblock.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FloatingQ']
    return (-6,-6,28,28)


def InitWarpCannon(sprite): # 434
    global ImageCache
    if 'Warp0' not in ImageCache:
        ImageCache['Warp0'] = GetImg('warp_w5.png')
        ImageCache['Warp1'] = GetImg('warp_w6.png')
        ImageCache['Warp2'] = GetImg('warp_w8.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeWarpCannon
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (5,-25,87,106)


def InitGhostFog(sprite): # 435
    global ImageCache
    if 'GhostFog' not in ImageCache:
        ImageCache['GhostFog'] = GetImg('fog_ghost.png')

    sprite.zoneRealView = True
    sprite.zoneRealViewer = RealViewGhostFogZone
    sprite.dynamicSize = True
    sprite.dynSizer = SizeGhostFog
    return (0,0,16,16)


def InitPurplePole(sprite): # 437
    global ImageCache
    if 'VertPole' not in ImageCache:
        ImageCache['VertPoleTop'] = GetImg('purple_pole_top.png')
        ImageCache['VertPole'] = GetImg('purple_pole_middle.png')
        ImageCache['VertPoleBottom'] = GetImg('purple_pole_bottom.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizePurplePole
    sprite.customPaint = True
    sprite.customPainter = PaintPurplePole

    return (0,0,16,16)

def InitCageBlocks(sprite): # 438
    global ImageCache
    if 'CageBlock0' not in ImageCache:
        for type in range(8):
            ImageCache['CageBlock%d' % type] = GetImg('cage_block_%d.png' % type)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeCageBlocks
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (120,120,240,240)

def InitCagePeachFake(sprite): # 439
    global ImageCache
    if 'CagePeachFake' not in ImageCache:
        ImageCache['CagePeachFake'] = GetImg('cage_peach_fake.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['CagePeachFake']
    return (-18,-106,52,122)

def InitHorizontalRope(sprite): # 440
    global ImageCache
    if 'HorzRope' not in ImageCache:
        ImageCache['HorzRope'] = GetImg('horizontal_rope_middle.png')
        ImageCache['HorzRopeEnd'] = GetImg('horizontal_rope_end.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeHorizontalRope
    sprite.customPaint = True
    sprite.customPainter = PaintHorizontalRope

    return (0,0,16,16)

def InitMushroomPlatform(sprite): # 441
    if 'RedShroomL' not in ImageCache:
        LoadMushrooms()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeMushroomPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintMushroomPlatform

    return (0,0,32,32)

def InitReplayBlock(sprite): # 443
    global ImageCache
    if 'ReplayBlock' not in ImageCache:
        ImageCache['ReplayBlock'] = GetImg('replay_block.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ReplayBlock']
    return (-8,-16,32,32)

def InitSwingingVine(sprite): # 444, 464
    global ImageCache
    if 'SwingVine' not in ImageCache:
        ImageCache['SwingVine'] = GetImg('swing_vine.png')
        ImageCache['SwingChain'] = GetImg('swing_chain.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSwingVine
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject

    return (0,0,16,144)

def InitCagePeachReal(sprite): # 445
    global ImageCache
    if 'CagePeachReal' not in ImageCache:
        ImageCache['CagePeachReal'] = GetImg('cage_peach_real.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['CagePeachReal']
    return (-18,-106,52,122)

def InitUnderwaterLamp(sprite): # 447
    global ImageCache

    sprite.aux.append(AuxiliaryImage(sprite, 105, 105))
    sprite.aux[0].image = ImageCache['UnderwaterLamp']
    sprite.aux[0].setPos(-34, -34)

    sprite.customPaint = True
    sprite.customPainter = PaintNothing
    return (-4,-4,24,26)

def InitMetalBar(sprite): # 448
    global ImageCache
    if 'MetalBar' not in ImageCache:
        ImageCache['MetalBar'] = GetImg('metal_bar.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MetalBar']
    return (0,-32,32,80)

def InitMouserDespawner(sprite): # 451
    global ImageCache
    if 'MouserDespawner' not in ImageCache:
        ImageCache['MouserDespawner'] = GetImg('mouser_despawner.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MouserDespawner']
    return (0,0,128,16)


def InitBowserBossDoor(sprite): # 452
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BowserDoor']
    return (-53,-134,156,183)

def InitSeaweed(sprite): # 453
    global ImageCache
    if 'Seaweed0' not in ImageCache:
        for i in range(4):
            ImageCache['Seaweed%d' % i] = GetImg('seaweed_%d.png' % i)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSeaweed
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)

def InitHammerPlatform(sprite): # 455
    global ImageCache
    if 'HammerPlatform' not in ImageCache:
        ImageCache['HammerPlatform'] = GetImg('hammer_platform.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['HammerPlatform']
    sprite.setZValue(24999)
    return (-24,-8,65,179)

def InitBossBridge(sprite): # 456
    global ImageCache
    if 'BossBridgeL' not in ImageCache:
        ImageCache['BossBridgeL'] = GetImg('boss_bridge_left.png')
        ImageCache['BossBridgeM'] = GetImg('boss_bridge_middle.png')
        ImageCache['BossBridgeR'] = GetImg('boss_bridge_right.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBossBridge
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,32,40)

def InitSpinningThinBars(sprite): # 457
    global ImageCache
    if 'SpinningThinBars' not in ImageCache:
        ImageCache['SpinningThinBars'] = GetImg('spinning_thin_bars.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SpinningThinBars']
    sprite.setZValue(24999)
    return (-114,-112,244,240)

def InitLavaIronBlock(sprite): # 466
    global ImageCache
    if 'LavaIronBlock' not in ImageCache:
        ImageCache['LavaIronBlock'] = GetImg('lava_iron_block.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['LavaIronBlock']
    return (-2,-1,145,49)

def InitMovingGemBlock(sprite): # 467
    global ImageCache
    if 'MovingGemBlock' not in ImageCache:
        ImageCache['MovingGemBlock'] = GetImg('moving_gem_block.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['MovingGemBlock']
    return (0,0,48,32)

def InitBoltPlatform(sprite): # 469
    global ImageCache
    if 'BoltPlatformL' not in ImageCache:
        ImageCache['BoltPlatformL'] = GetImg('bolt_platform_left.png')
        ImageCache['BoltPlatformM'] = GetImg('bolt_platform_middle.png')
        ImageCache['BoltPlatformR'] = GetImg('bolt_platform_right.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeBoltPlatform
    sprite.customPaint = True
    sprite.customPainter = PaintBoltPlatform

    return (0,-2.5,16,18)

def InitBoltPlatformWire(sprite): # 470
    global ImageCache
    if 'BoltPlatformWire' not in ImageCache:
        ImageCache['BoltPlatformWire'] = GetImg('bolt_platform_wire.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['BoltPlatformWire']
    return (5,-240,6,256)

def InitLiftDokan(sprite): # 471
    global ImageCache
    if 'LiftDokanT' not in ImageCache:
        ImageCache['LiftDokanT'] = GetImg('lift_dokan_top.png')
        ImageCache['LiftDokanM'] = GetImg('lift_dokan_middle.png')

    sprite.customPaint = True
    sprite.customPainter = PaintLiftDokan

    return (-12,-2,51,386)

def InitIceFlow(sprite): # 475
    global ImageCache
    size = sprite.spritedata[5] & 15
    if 'IceFlow0' not in ImageCache:
        for size in range(16):
            ImageCache['IceFlow%d' % size] = GetImg('ice_flow_%d.png' % size)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeIceFlow
    sprite.alpha = 0.65
    sprite.customPaint = True
    sprite.customPainter = PaintAlphaObject

    return (-1,-32,50,48)

def InitFlyingWrench(sprite): # 476
    if 'Wrench' not in ImageCache:
        LoadDoomshipStuff()

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Wrench']
    return (0,0,16,16)

def InitSuperGuideBlock(sprite): # 477
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SuperGuide']
    return (-4,-4,24,24)

def InitBowserSwitchSm(sprite): # 478
    if 'ESwitch' not in ImageCache:
        LoadSwitches()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSwitch
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.switchType = 'E'
    return (0,0,16,16)

def InitBowserSwitchLg(sprite): # 479
    if 'ESwitchLg' not in ImageCache:
        LoadSwitches()

    sprite.dynamicSize = True
    sprite.dynSizer = SizeSwitch
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.switchType = 'EL'
    return (-16,-32,48,42)








################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################


# ---- Dynamic Sizing ----
def SizeHorzMovingPlatform(sprite): # 23
    # get width and distance
    sprite.xsize = ((sprite.spritedata[5] & 0xF) + 1) << 4
    if sprite.xsize == 16: sprite.xsize = 32

    distance = (sprite.spritedata[4] & 0xF) << 4

    # update the track
    sprite.aux[0].SetSize(sprite.xsize + distance, 16)

    if (sprite.spritedata[3] & 1) == 0:
        # platform goes right
        sprite.aux[0].setPos(0, 0)
    else:
        # platform goes left
        sprite.aux[0].setPos(-distance*1.5, 0)

    # set colour
    sprite.colour = (sprite.spritedata[3] >> 4) & 1

    sprite.aux[0].update()

def SizeBuzzyBeetle(sprite): # 24
    orient = sprite.spritedata[5] & 15

    if orient == 1:
        sprite.image = ImageCache['BuzzyBeetleU']
        sprite.ysize = 16
        sprite.yoffset = 0
    elif orient == 2:
        sprite.image = ImageCache['BuzzyBeetleShell']
        sprite.ysize = 15
        sprite.yoffset = 2
    elif orient == 3:
        sprite.image = ImageCache['BuzzyBeetleShellU']
        sprite.ysize = 15
        sprite.yoffset = 2
    else:
        sprite.image = ImageCache['BuzzyBeetle']
        sprite.ysize = 16
        sprite.yoffset = 0

def SizeSpiny(sprite): # 25
    orient = sprite.spritedata[5] & 15

    if orient == 1:
        sprite.image = ImageCache['SpinyBall']
        sprite.ysize = 18
        sprite.yoffset = -2
    elif orient == 2:
        sprite.image = ImageCache['SpinyShell']
        sprite.ysize = 15
        sprite.yoffset = 1
    elif orient == 3:
        sprite.image = ImageCache['SpinyShellU']
        sprite.ysize = 15
        sprite.yoffset = 2
    else:
        sprite.image = ImageCache['Spiny']
        sprite.ysize = 16
        sprite.yoffset = 0

def SizeUnusedVertStoneBlock(sprite): # 27
    # get height and distance
    width = sprite.spritedata[5] & 7
    if width == 0: width = 1
    byte5 = sprite.spritedata[4]
    sprite.xsize = (16 + (width << 4))
    sprite.ysize = (16 << ((byte5 & 0x30) >> 4)) - 4
    distance = (byte5 & 0xF) << 4

    # update the track
    sprite.aux[0].SetSize(sprite.xsize, distance + sprite.ysize)

    if (sprite.spritedata[3] & 1) == 0:
        # block goes up
        sprite.aux[0].setPos(0, -distance*1.5)
    else:
        # block goes down
        sprite.aux[0].setPos(0, 0)

    sprite.aux[0].update()

def SizeUnusedHorzStoneBlock(sprite): # 28
    # get height and distance
    width = sprite.spritedata[5] & 7
    if width == 0: width = 1
    byte5 = sprite.spritedata[4]
    sprite.xsize = (16 + (width << 4))
    sprite.ysize = (16 << ((byte5 & 0x30) >> 4)) - 5
    distance = (byte5 & 0xF) << 4

    # update the track
    sprite.aux[0].SetSize(distance + sprite.xsize, sprite.ysize)

    if (sprite.spritedata[3] & 1) == 0:
        # block goes right
        sprite.aux[0].setPos(0, 0)
    else:
        # block goes left
        sprite.aux[0].setPos(-distance*1.5, 0)

    sprite.aux[0].update()

def SizeVertMovingPlatform(sprite): # 31
    # get width and distance
    sprite.xsize = ((sprite.spritedata[5] & 0xF) + 1) << 4
    if sprite.xsize == 16: sprite.xsize = 32

    distance = (sprite.spritedata[4] & 0xF) << 4

    # update the track
    sprite.aux[0].SetSize(sprite.xsize, distance + 16)

    if (sprite.spritedata[3] & 1) == 0:
        # platform goes up
        sprite.aux[0].setPos(0, -distance*1.5)
    else:
        # platform goes down
        sprite.aux[0].setPos(0, 0)

    # set colour
    sprite.colour = (sprite.spritedata[3] >> 4) & 1

    sprite.aux[0].update()

def SizeSwitch(sprite): # 40,41,42,478,479
    type = sprite.type
    upsideDown = sprite.spritedata[5] & 1

    if type == 479 and upsideDown == 1:
        sprite.xoffset = -16
        sprite.yoffset = 0
        sprite.xsize = 48
        sprite.ysize = 42
    elif type == 479 and upsideDown == 0:
        sprite.xoffset = -16
        sprite.yoffset = -26
        sprite.xsize = 48
        sprite.ysize = 42
    else:
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 16
        sprite.xsize = 16

    if upsideDown == 0:
        sprite.image = ImageCache[sprite.switchType + 'Switch']
    else:
        sprite.image = ImageCache[sprite.switchType + 'SwitchU']

def SizeGroundPiranha(sprite): # 73
    upsideDown = sprite.spritedata[5] & 1

    if upsideDown == 0:
        sprite.yoffset = 6
        sprite.image = ImageCache['GroundPiranha']
    else:
        sprite.yoffset = 0
        sprite.image = ImageCache['GroundPiranhaU']


def SizeBigGroundPiranha(sprite): # 74
    upsideDown = sprite.spritedata[5] & 1

    if upsideDown == 0:
        sprite.yoffset = -32
        sprite.image = ImageCache['BigGroundPiranha']
    else:
        sprite.yoffset = 0
        sprite.image = ImageCache['BigGroundPiranhaU']


def SizeGroundFiretrap(sprite): # 75
    upsideDown = sprite.spritedata[5] & 1

    if upsideDown == 0:
        sprite.yoffset = -10
        sprite.image = ImageCache['GroundFiretrap']
    else:
        sprite.yoffset = 0
        sprite.image = ImageCache['GroundFiretrapU']


def SizeBigGroundFiretrap(sprite): # 76
    upsideDown = sprite.spritedata[5] & 1

    if upsideDown == 0:
        sprite.yoffset = -68
        sprite.image = ImageCache['BigGroundFiretrap']
    else:
        sprite.yoffset = 0
        sprite.image = ImageCache['BigGroundFiretrapU']

def SizeUnusedSeesaw(sprite): # 48
    w = sprite.spritedata[5] & 15
    if w == 0:
        sprite.xsize = 16*16 # 16 blocks wide
    else:
        sprite.xsize = w*32
    sprite.image = ImageCache['UnusedPlatform'].scaled(sprite.xsize*3/2, sprite.ysize*3/2)
    sprite.xoffset = (8*16)-(sprite.xsize/2)

    swingArc = sprite.spritedata[5] >> 4
    swingArcs = [45,
                 4.5,
                 9,
                 18,
                 65,
                 80]
    if swingArc <= 5:
        realSwingArc = swingArcs[swingArc]
    else:
        realSwingArc = 100 # infinite

    # angle starts at the right position (3 o'clock)
    # negative = clockwise, positive = anti clockwise
    startAngle = 90 - realSwingArc
    spanAngle = realSwingArc * 2

    sprite.aux[0].SetAngle(startAngle, spanAngle)
    sprite.aux[0].setPos((sprite.xsize*0.75)-36, -36)
    sprite.aux[0].update()

def SizeFallingPlatform(sprite): # 50
    # get width
    sprite.xsize = ((sprite.spritedata[5] & 0xF) + 1) << 4

    # override this for the "glitchy" effect caused by length=0
    if sprite.xsize == 16: sprite.xsize = 24

    # set colour
    colour = (sprite.spritedata[3] >> 4)
    if colour == 1:
        sprite.colour = 1
    elif colour == 3:
        sprite.colour = 2
    else:
        sprite.colour = 0

def SizeKoopaTroopa(sprite): # 57
    # get properties
    props = sprite.spritedata[5]
    shell = (props >> 4) & 1
    colour = props & 1

    if shell == 0:
        sprite.xoffset = -7
        sprite.yoffset = -15
        sprite.xsize = 24
        sprite.ysize = 32

        if colour == 0:
            sprite.image = ImageCache['KoopaG']
        else:
            sprite.image = ImageCache['KoopaR']
    else:
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 16
        sprite.ysize = 16

        if colour == 0:
            sprite.image = ImageCache['KoopaShellG']
        else:
            sprite.image = ImageCache['KoopaShellR']

def SizeKoopaParatroopa(sprite): # 58
    # get properties
    colour = sprite.spritedata[5] & 1

    if colour == 0:
        sprite.image = ImageCache['ParakoopaG']
    else:
        sprite.image = ImageCache['ParakoopaR']


def SizeOutdoorsFog(sprite): # 64
    sprite.zoneRealView = sprite.spritedata[5] == 0
    sprite.updateScene()


def SizeOldStoneBlock(sprite): # 30, 81, 82, 83, 84, 85, 86
    size = sprite.spritedata[5]
    height = (size & 0xF0) >> 4
    width = size & 0xF
    if sprite.type == 30:
        height = 1 if height == 0 else height
        width = 1 if width == 0 else width
    sprite.xsize = width * 16 + 16
    sprite.ysize = height * 16 + 16

    type = sprite.type

    if type == 81 or type == 83: # left spikes
        sprite.xoffset = -16
        sprite.xsize += 16
    if type == 84 or type == 86: # top spikes
        sprite.yoffset = -16
        sprite.ysize += 16
    if type == 82 or type == 83: # right spikes
        sprite.xsize += 16
    if type == 85 or type == 86: # bottom spikes
        sprite.ysize += 16




    # now set up the track
    direction = sprite.spritedata[2] & 3
    distance = (sprite.spritedata[4] & 0xF0) >> 4
    if direction > 3: direction = 0

    if direction <= 1: # horizontal
        sprite.aux[0].direction = 1
        sprite.aux[0].SetSize(sprite.xsize + (distance * 16), sprite.ysize)
    else: # vertical
        sprite.aux[0].direction = 2
        sprite.aux[0].SetSize(sprite.xsize, sprite.ysize + (distance * 16))

    if direction == 0 or direction == 3: # right, down
        sprite.aux[0].setPos(0,0)
    elif direction == 1: # left
        sprite.aux[0].setPos(-distance * 24,0)
    elif direction == 2: # up
        sprite.aux[0].setPos(0,-distance * 24)

def SizeTrampolineWall(sprite): # 87
    height = (sprite.spritedata[5] & 15) + 1

    img = ImageCache['UnusedPlatform'].scaled(24, height*24)
    sprite.image = img
    sprite.ysize = height*16

def SizeBulletBillLauncher(sprite): # 92
    height = (sprite.spritedata[5] & 0xF0) >> 4

    sprite.ysize = (height + 2) * 16
    sprite.yoffset = (height + 1) * -16

def SizeRotationControllerSwaying(sprite): # 96
    # get the swing arc: 4 == 90 degrees (45 left from the origin, 45 right)
    swingArc = sprite.spritedata[2] >> 4
    realSwingArc = swingArc * 11.25

    # angle starts at the right position (3 o'clock)
    # negative = clockwise, positive = anti clockwise
    startAngle = 90 - realSwingArc
    spanAngle = realSwingArc * 2

    sprite.aux[0].SetAngle(startAngle, spanAngle)
    sprite.aux[0].update()

def SizeSpikeTop(sprite): # 60
    value = sprite.spritedata[5]
    vertical = (value & 0x20) >> 5
    horizontal = value & 1

    if vertical == 0: # up
        sprite.yoffset = -4
        v = 'U'
    else:
        sprite.yoffset = 0
        v = 'D'

    if horizontal == 0: # right
        sprite.image = ImageCache['SpikeTop%sR' % v]
    else:
        sprite.image = ImageCache['SpikeTop%sL' % v]


def SizeCloudTrampoline(sprite): # 78
    size = (sprite.spritedata[4] & 0x10) >> 4

    if size == 0:
        sprite.image = ImageCache['CloudTrSmall']
        sprite.xsize = 68
        sprite.ysize = 27
    else:
        sprite.image = ImageCache['CloudTrBig']
        sprite.xsize = 132
        sprite.ysize = 32

def SizePlatformGenerator(sprite): # 103
    # get width
    sprite.xsize = (((sprite.spritedata[5] & 0xF0) >> 4) + 1) << 4

    # length=0 becomes length=4
    if sprite.xsize == 16: sprite.xsize = 64

    # override this for the "glitchy" effect caused by length=0
    if sprite.xsize == 32: sprite.xsize = 24

    sprite.colour = 0

def SizePokey(sprite): # 105
    # get the height
    height = sprite.spritedata[5] & 0xF
    sprite.ysize = (height * 16) + 16 + 25
    sprite.yoffset = 0 - sprite.ysize + 16

def SizeLinePlatform(sprite): # 106
    # get width
    sprite.xsize = (sprite.spritedata[5] & 0xF) << 4

    # length=0 becomes length=4
    if sprite.xsize == 0: sprite.xsize = 64

    # override this for the "glitchy" effect caused by length=0
    if sprite.xsize == 16: sprite.xsize = 24

    colour = (sprite.spritedata[4] & 0xF0) >> 4
    if colour > 1: colour = 0
    sprite.colour = colour

def SizeChainBall(sprite): # 109
    direction = sprite.spritedata[5] & 3
    if direction > 3: direction = 0

    if direction % 2 == 0: # horizontal
        sprite.xsize = 96
        sprite.ysize = 38
    else: # vertical
        sprite.xsize = 37
        sprite.ysize = 96

    if direction == 0: # right
        sprite.xoffset = 3
        sprite.yoffset = -8.5
        sprite.image = ImageCache['ChainBallR']
    elif direction == 1: # up
        sprite.xoffset = -8.5
        sprite.yoffset = -81.5
        sprite.image = ImageCache['ChainBallU']
    elif direction == 2: # left
        sprite.xoffset = -83
        sprite.yoffset = -11
        sprite.image = ImageCache['ChainBallL']
    elif direction == 3: # down
        sprite.xoffset = -11
        sprite.yoffset = 3.5
        sprite.image = ImageCache['ChainBallD']


def SizeFlagpole(sprite): # 113
    # get the info
    exit = (sprite.spritedata[2] >> 4) & 1
    snow = sprite.spritedata[5] & 1

    if snow == 0:
        sprite.aux[0].setPos(356,97)
    else:
        sprite.aux[0].setPos(356,91)

    if exit == 0:
        sprite.image = ImageCache['Flagpole']
        if snow == 0:
            sprite.aux[0].image = ImageCache['Castle']
        else:
            sprite.aux[0].image = ImageCache['SnowCastle']
    else:
        sprite.image = ImageCache['FlagpoleSecret']
        if snow == 0:
            sprite.aux[0].image = ImageCache['CastleSecret']
        else:
            sprite.aux[0].image = ImageCache['SnowCastleSecret']

def SizeFlameCannon(sprite): # 114 (0,0,64,16)
    direction = sprite.spritedata[5] & 15
    if direction > 3: direction = 0

    if direction == 0:
        direction = 'R'
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 64
        sprite.ysize = 16
    elif direction == 1:
        direction = 'L'
        sprite.xoffset = -48
        sprite.yoffset = 0
        sprite.xsize = 64
        sprite.ysize = 16
    elif direction == 2:
        direction = 'U'
        sprite.xoffset = 0
        sprite.yoffset = -48
        sprite.xsize = 16
        sprite.ysize = 64
    elif direction == 3:
        direction = 'D'
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 16
        sprite.ysize = 64

    sprite.image = ImageCache['FlameCannon%s' % direction]

def SizeCheep(sprite): # 115
    type = sprite.spritedata[5] & 0xF
    if type == 1:
        sprite.image = ImageCache['CheepGreen']
    elif type == 8:
        sprite.image = ImageCache['CheepYellow']
    else:
        sprite.image = ImageCache['CheepRed']

def SizePulseFlameCannon(sprite): # 117
    direction = sprite.spritedata[5] & 15
    if direction > 3: direction = 0

    if direction == 0:
        direction = 'R'
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 112
        sprite.ysize = 16
    elif direction == 1:
        direction = 'L'
        sprite.xoffset = -96
        sprite.yoffset = 0
        sprite.xsize = 112
        sprite.ysize = 16
    elif direction == 2:
        direction = 'U'
        sprite.xoffset = 0
        sprite.yoffset = -96
        sprite.xsize = 16
        sprite.ysize = 112
    elif direction == 3:
        direction = 'D'
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 16
        sprite.ysize = 112

    sprite.image = ImageCache['PulseFlameCannon%s' % direction]

def SizeOneWayPlatform(sprite): # 122
    width = sprite.spritedata[5] & 0xF
    if width < 2: width = 2
    sprite.xsize = width * 32 + 32

    sprite.xoffset = sprite.xsize * -0.5

    colour = (sprite.spritedata[4] & 0xF0) >> 4
    if colour > 1: colour = 0
    sprite.colour = colour

def SizeRotBulletLauncher(sprite): # 136
    pieces = sprite.spritedata[3] & 15
    sprite.yoffset = -pieces*16
    sprite.ysize = (pieces+1)*16

def SizeUnusedCastlePlatform(sprite): # 123
    rawSize = sprite.spritedata[4] >> 4

    if rawSize != 0:
        widthInBlocks = rawSize*4
    else:
        widthInBlocks = 8

    TopRadiusInBlocks = widthInBlocks/10.0
    heightInBlocks = widthInBlocks + TopRadiusInBlocks

    img = ImageCache['UnusedCastlePlatform'].scaled(widthInBlocks*24, heightInBlocks*24)
    sprite.image = img

    sprite.xsize = widthInBlocks*16
    sprite.ysize = heightInBlocks*16
    sprite.xoffset = -(sprite.xsize/2.0)
    sprite.yoffset = -(TopRadiusInBlocks*16)


def SizeFenceKoopaHorz(sprite): # 125
    color = sprite.spritedata[5] >> 4

    if color == 1:
        sprite.image = ImageCache['FenceKoopaHR']
    else:
        sprite.image = ImageCache['FenceKoopaHG']

def SizeFenceKoopaVert(sprite): # 126
    color = sprite.spritedata[5] >> 4

    if color == 1:
        sprite.image = ImageCache['FenceKoopaVR']
    else:
        sprite.image = ImageCache['FenceKoopaVG']

def SizeUnusedBlockPlatform(sprite): # 132, 160
    if sprite.type == 132:
        sprite.xsize = ((sprite.spritedata[5] & 0xF) + 1) * 16
        sprite.ysize = ((sprite.spritedata[5] >> 4)  + 1) * 16
    else:
        sprite.xsize = ((sprite.spritedata[4] & 0xF) + 1) * 16
        sprite.ysize = ((sprite.spritedata[4] >> 4)  + 1) * 16

def SizeSpikedStake(sprite): # 137, 140, 141, 142
    if sprite.type == 137:
        dir = 'down'
    elif sprite.type == 140:
        dir = 'up'
    elif sprite.type == 141:
        dir = 'right'
    elif sprite.type == 142:
        dir = 'left'

    distance = sprite.spritedata[3] >> 4
    if distance == 0:
        x=16
    elif distance == 1:
        x=7
    elif distance == 2:
        x=14
    elif distance == 3:
        x=10
    else:
        x=16
    distance = x + 1 # In order to hide one side of the track behind the image.

    w = 66
    L = ((37*16)+41)/1.5 # (16 mid sections + an end section), accounting for image/sprite size difference

    if dir == 'up':
        sprite.xsize = w
        sprite.ysize = L
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.aux[0].direction = AuxiliaryTrackObject.Vertical
        sprite.aux[0].setPos(36, 24-(distance*24))
        sprite.aux[0].SetSize(16, distance*16)
    elif dir == 'down':
        sprite.xsize = w
        sprite.ysize = L
        sprite.xoffset = 0
        sprite.yoffset = 16 - L
        sprite.aux[0].direction = AuxiliaryTrackObject.Vertical
        sprite.aux[0].setPos(36, (L*1.5)-24)
        sprite.aux[0].SetSize(16, distance*16)
    elif dir == 'left':
        sprite.xsize = L
        sprite.ysize = w
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.aux[0].direction = AuxiliaryTrackObject.Horizontal
        sprite.aux[0].setPos(24-(distance*24), 36)
        sprite.aux[0].SetSize(distance*16, 16)
    elif dir == 'right':
        sprite.xsize = L
        sprite.ysize = w
        sprite.xoffset = 16 - L
        sprite.yoffset = 0
        sprite.aux[0].direction = AuxiliaryTrackObject.Horizontal
        sprite.aux[0].setPos((L*1.5)-24, 36)
        sprite.aux[0].SetSize(distance*16, 16)


def SizeWater(sprite): # 138
    sprite.zoneRealView = sprite.spritedata[5] == 0
    sprite.updateScene()

def SizeLava(sprite): # 139
    sprite.zoneRealView = sprite.spritedata[5] == 0
    sprite.updateScene()


ArrowOffsets = [(3,0), (5,4), (1,3), (5,-1), (3,0), (-1,-1), (0,3), (-1,4)]
def SizeArrow(sprite): # 143
    direction = sprite.spritedata[5] & 7
    image = ImageCache['Arrow%d' % direction]
    sprite.image = image

    sprite.xsize = image.width() / 1.5
    sprite.ysize = image.height() / 1.5
    offset = ArrowOffsets[direction]
    sprite.xoffset, sprite.yoffset = offset

def SizeCoin(sprite): # 147
    flag = sprite.spritedata[5] & 15

    if flag == 15:
        sprite.image = ImageCache['CoinF']
    else:
        sprite.image = ImageCache['Coin']

def SizeBigBrick(sprite): # 157
    power = sprite.spritedata[5] & 15

    global ImageCache
    if 'ShipKey' not in ImageCache:
        ImageCache['ShipKey'] = GetImg('ship_key.png')
    if '5Coin' not in ImageCache:
        ImageCache['5Coin'] = GetImg('5_coin.png')

    images = [None,                     # empty
              ImageCache['Blocks'][1],  # coin
              ImageCache['Blocks'][2],  # mushroom
              ImageCache['Blocks'][3],  # fire
              ImageCache['Blocks'][4],  # propeller
              ImageCache['Blocks'][5],  # penguin
              ImageCache['Blocks'][6],  # mini
              ImageCache['Blocks'][7],  # star
              None,                     # empty
              OverlayPixmaps(ImageCache['Blocks'][9], ImageCache['Blocks'][3], 24, 0, 1, 1, 0, 0, 0, 24), # yoshi + fire
              ImageCache['5Coin'],      # 5coin
              ImageCache['Blocks'][11], # 1up
              None,                     # empty
              None,                     # empty
              ImageCache['ShipKey'],    # key
              ImageCache['Blocks'][15]] # ice

    # Make sure we have the correct offsets for the non-24x24 powerup overlays
    if power == 9:
        x = 12
        y = 24
    elif power == 14:
        x = 22
        y = 18
    else:
        x = 24
        y = 24

    if images[power] != None:
        sprite.image = OverlayPixmaps(ImageCache['BigBrick'], images[power], x, y, 1, 0.65)
    else:
        sprite.image = ImageCache['BigBrick']

def SizeFireSnake(sprite): # 158
    move = sprite.spritedata[5] & 15

    if move == 1:
        sprite.xsize = 16
        sprite.ysize = 16
        sprite.yoffset = 0
        sprite.image = ImageCache['FireSnakeWait']
    else:
        sprite.xsize = 20
        sprite.ysize = 32
        sprite.yoffset = -16
        sprite.image = ImageCache['FireSnake']

def SizePipeBubbles(sprite): # 161
    direction = sprite.spritedata[5] & 15
    if direction == 0 or direction > 3:
        direction = 'U'
        sprite.xoffset = 0
        sprite.yoffset = -52
        sprite.xsize = 32
        sprite.ysize = 53
    elif direction == 1:
        direction = 'D'
        sprite.xoffset = 0
        sprite.yoffset = 16
        sprite.xsize = 32
        sprite.ysize = 53
    elif direction == 2:
        direction = 'R'
        sprite.xoffset = 16
        sprite.yoffset = -16
        sprite.xsize = 53
        sprite.ysize = 32
    elif direction == 3:
        direction = 'L'
        sprite.xoffset = -52
        sprite.yoffset = -16
        sprite.xsize = 53
        sprite.ysize = 32

    sprite.image = ImageCache['PipeBubbles%s' % direction]

def SizeBlockTrain(sprite): # 166
    length = sprite.spritedata[5] & 15
    sprite.xsize = (length+3) * 16

def SizeScrewMushroom(sprite): # 172, 382
    # I wish I knew what this does
    SomeOffset = sprite.spritedata[3]
    if SomeOffset == 0 or SomeOffset > 8: SomeOffset = 8

    sprite.xsize = 122
    sprite.ysize = 198
    sprite.xoffset = 3
    sprite.yoffset = SomeOffset * -16
    if sprite.type == 172: # with bolt
        sprite.ysize += 16
        sprite.yoffset -= 16

def SizeOneWayGate(sprite): # 174
    flag = (sprite.spritedata[5] >> 4) & 1
    direction = sprite.spritedata[5] & 3
    sprite.image = ImageCache['1WayGate%d%d' % (flag, direction)]
    sprite.xsize = int(sprite.image.width() * (2.0/3))
    sprite.ysize = int(sprite.image.height() * (2.0/3))
    if direction > 3: direction = 3
    if   direction == 0: x, y = 0, -24
    elif direction == 1: x, y = 0, 0
    elif direction == 2: x, y = -24, 0
    elif direction == 3: x, y = 0, 0
    sprite.xoffset, sprite.yoffset = x, y

def SizeFlyingQBlock(sprite): # 175
    color = sprite.spritedata[4] >> 4
    if color == 0 or color > 3:
        block = 9
    elif color == 1:
        block = 59
    elif color == 2:
        block = 109
    elif color == 3:
        block = 159

    sprite.image = OverlayPixmaps(ImageCache['FlyingQBlock'], ImageCache['Overrides'][block], 18, 23)

def SizeScalePlatform(sprite): # 178
    info1 = sprite.spritedata[4]
    info2 = sprite.spritedata[5]
    sprite.platformWidth = (info1 & 0xF0) >> 4
    if sprite.platformWidth > 12: sprite.platformWidth = -1

    sprite.ropeLengthLeft = info1 & 0xF
    sprite.ropeLengthRight = (info2 & 0xF0) >> 4
    sprite.ropeWidth = info2 & 0xF

    ropeWidth = sprite.ropeWidth * 16
    platformWidth = (sprite.platformWidth + 3) * 16
    sprite.xsize = ropeWidth + platformWidth

    maxRopeHeight = max(sprite.ropeLengthLeft, sprite.ropeLengthRight)
    sprite.ysize = maxRopeHeight * 16 + 19
    if maxRopeHeight == 0: sprite.ysize += 8

    sprite.xoffset = -((sprite.platformWidth + 3) * 16 / 2)

def SizeSpecialExit(sprite): # 179
    w = (sprite.spritedata[4] & 15) + 1
    h = (sprite.spritedata[5] >> 4) + 1
    if w == 1 and h == 1: # no point drawing a 1x1 outline behind the sprite
        sprite.aux[0].SetSize(0,0)
        return
    sprite.aux[0].SetSize(w*24, h*24)

def SizeTileEvent(sprite): # 191
    w = sprite.spritedata[5] >> 4
    h = sprite.spritedata[5] & 0xF
    if w == 0: w = 1
    if h == 0: h = 1
    if w == 1 and h == 1: # no point drawing a 1x1 outline behind the sprite
        sprite.aux[0].SetSize(0,0)
        return
    sprite.aux[0].SetSize(w*24, h*24)

def SizeHuckitCrab(sprite): # 195
    info = sprite.spritedata[5]

    if info == 1:
        sprite.image = ImageCache['HuckitCrabR']
        sprite.xoffset = 0
    else:
        if info == 13:
            sprite.image = ImageCache['HuckitCrabR']
            sprite.xoffset = 0
        else:
            sprite.image = ImageCache['HuckitCrabL']
            sprite.xoffset = -16

def SizeFishbones(sprite): # 196
    direction = sprite.spritedata[5] >> 4

    if direction == 1:
        sprite.image = ImageCache['FishbonesR']
    else:
        sprite.image = ImageCache['FishbonesL']

def SizeClam(sprite): # 197
    holds = sprite.spritedata[5] & 0xF
    switchdir = sprite.spritedata[4] & 0xF
    if 'ClamEmpty' not in ImageCache:
        ImageCache['ClamEmpty'] = GetImg('clam.png')
        ImageCache['ClamStar'] = OverlayPixmaps(ImageCache['ClamEmpty'], ImageCache['StarCoin'], 26, 22, 1, 0.6)
        ImageCache['Clam2Coin'] = OverlayPixmaps(ImageCache['ClamEmpty'], ImageCache['Coin'], 28, 42, 1, 0.6)
        ImageCache['Clam2Coin'] = OverlayPixmaps(ImageCache['Clam2Coin'], ImageCache['Coin'], 52, 42, 1, 0.6)
        ImageCache['Clam1Up'] = OverlayPixmaps(ImageCache['ClamEmpty'], ImageCache['Blocks'][11], 40, 42, 1, 0.6)
        if 'PSwitch' not in ImageCache:
            LoadSwitches()
        ImageCache['ClamPSwitch'] = OverlayPixmaps(ImageCache['ClamEmpty'], ImageCache['PSwitch'], 40, 42, 1, 0.6)
        ImageCache['ClamPSwitchU'] = OverlayPixmaps(ImageCache['ClamEmpty'], ImageCache['PSwitchU'], 40, 42, 1, 0.6)

    holdsStr = 'Empty'
    if holds == 1:
        holdsStr = 'Star'
    elif holds == 2:
        holdsStr = '2Coin'
    elif holds == 3:
        holdsStr = '1Up'
    elif holds == 4:
        if switchdir == 1:
            holdsStr = 'PSwitchU'
        else:
            holdsStr = 'PSwitch'

    sprite.image = ImageCache['Clam'+holdsStr]

def SizeIcicle(sprite): # 201
    size = sprite.spritedata[5] & 1

    if size == 0:
        sprite.image = ImageCache['IcicleSmallS']
        sprite.ysize = 16
    else:
        sprite.image = ImageCache['IcicleLargeS']
        sprite.ysize = 32

def SizeGiantBubble(sprite): # 205
    sprite.shape = sprite.spritedata[4] >> 4
    sprite.direction = sprite.spritedata[5] & 15
    arrow = None

    if sprite.shape == 0 or sprite.shape > 3:
        sprite.xsize = 122
        sprite.ysize = 137
    elif sprite.shape == 1:
        sprite.xsize = 76
        sprite.ysize = 170
    elif sprite.shape == 2:
        sprite.xsize = 160
        sprite.ysize = 81

    sprite.xoffset = sprite.xsize / 2 * -1 + 8
    sprite.yoffset = sprite.ysize / 2 * -1 + 8

def SizeZoom(sprite): # 206
    w = sprite.spritedata[5]+1
    h = sprite.spritedata[4]+1
    if w == 1 and h == 1:# no point drawing a 1x1 outline behind the sprite
        sprite.aux[0].SetSize(0,0,0,0)
        return
    sprite.aux[0].SetSize(w*24, h*24, 0, 24-(h*24))

def SizeBlock(sprite): # 207, 208, 209, 221, 255, 256, 402, 403, 422, 423
    # Sprite types:
    # 207 = Question Block
    # 208 = Question Block (unused)
    # 209 = Brick Block
    # 221 = Invisible Block
    # 255 = Rotating Question Block
    # 256 = Rotating Brick Block
    # 402 = Line Question Block
    # 403 = Line Brick Block
    # 422 = Toad Question Block
    # 423 = Toad Brick Block

    type = sprite.type
    contents = sprite.spritedata[5] & 0xF

    # SET TILE TYPE
    if type == 207 or type == 208 or type == 255 or type == 402 or type == 422:
        sprite.tilenum = 49
    elif type == 209 or type == 256 or type == 403 or type == 423:
        sprite.tilenum = 48
    else:
        sprite.tilenum = 1315

    # SET CONTENTS
    # In the blocks.png file:
    # 0 = Empty, 1 = Coin, 2 = Mushroom, 3 = Fire Flower, 4 = Propeller, 5 = Penguin Suit,
    # 6 = Mini Shroom, 7 = Star, 8 = Continuous Star, 9 = Yoshi Egg, 10 = 10 Coins,
    # 11 = 1-up, 12 = Vine, 13 = Spring, 14 = Shroom/Coin, 15 = Ice Flower, 16 = Toad

    if type == 422 or type == 423: # Force Toad
        contents = 16
    elif type == 255 or type == 256: # Contents is a different nybble here
        contents = sprite.spritedata[4] & 0xF

    if contents == 2: # 1 and 2 are always fire flowers
        contents = 3

    if contents == 12 and (type == 208 or type == 255 or type == 256 or type == 402):
        contents = 2 # 12 is a mushroom on some types

    sprite.image = ImageCache['Blocks'][contents]

    # SET UP ROTATION
    if type == 255 or type == 256:
        transform = QtGui.QTransform()
        transform.translate(12, 12)

        angle = (sprite.spritedata[4] & 0xF0) >> 4
        leftTilt = sprite.spritedata[3] & 1

        angle *= (45.0 / 16.0)

        if leftTilt == 0:
            transform.rotate(angle)
        else:
            transform.rotate(360.0 - angle)

        transform.translate(-12, -12)
        sprite.setTransform(transform)


def SizeRollingHill(sprite): # 212
    size = (sprite.spritedata[3] >> 4) & 0xF
    if size != 0: realSize = RollingHillSizes[size]
    else:
        adjust = sprite.spritedata[4] & 0xF
        realSize = 32*(adjust+1)

    sprite.aux[0].SetSize(realSize)
    sprite.aux[0].update()


def SizePoison(sprite): # 216
    sprite.zoneRealView = sprite.spritedata[5] == 0
    sprite.updateScene()


def SizeLineBlock(sprite): # 219
    direction = sprite.spritedata[4] >> 4
    widthA    = sprite.spritedata[5] & 15
    widthB    = sprite.spritedata[5] >> 4
    if direction == 1: widthA, widthB = widthB, widthA # reverse them if going down

    if widthA == 0:
        widthA = 1
        noWidthA = True
        aA = 0.25
    else:
        noWidthA = False
        aA = 1
    if widthB == 0:
        widthB = 1
        noWidthB = True
        aB = 0.25
    else:
        noWidthB = False
        aB = 0.5

    blockimg = ImageCache['LineBlock']

    if widthA > widthB:
        totalBlocks = widthA
    else:
        totalBlocks = widthB

    imgA = QtGui.QPixmap(widthA*24, 24)
    imgB = QtGui.QPixmap(widthB*24, 24)
    imgA.fill(QtGui.QColor.fromRgb(0,0,0,0))
    imgB.fill(QtGui.QColor.fromRgb(0,0,0,0))

    # We could use range(totalBlocks) in the overlay loop, but that gives
    # us a linear-ly sorted list. The game doesn't do it that way so we
    # need to rearrange the list.
    iterList = range(totalBlocks)
    halfList = range(totalBlocks)[(len(iterList)/2):len(iterList)]
    for i in range(len(halfList)):
        iterList[len(iterList)-(i+1)] = halfList[i]

    for i in iterList:
        imgA = OverlayPixmaps(imgA, blockimg, 24*i, 0, 1, aA)
        imgB = OverlayPixmaps(imgB, blockimg, 24*i, 0, 1, aB)


    if widthA >= 1:
        sprite.xsize = widthA*16
    else:
        sprite.xsize = 16
    xposA = (widthA*-8)+8
    if widthA == 0: xposA = 0
    xposB = (widthA-widthB)*12
    if widthA == 0: xposB = 0
    if direction == 1:
        yposB = 96
    else:
        yposB = -96


    sprite.image = imgA
    sprite.xoffset = xposA
    sprite.aux[0].SetSize(imgB.width(), imgB.height())
    sprite.aux[0].image = imgB
    sprite.aux[0].setPos(xposB, yposB)


def SizeSpringBlock(sprite): # 223
    type = sprite.spritedata[5] & 1
    if type == 0:
        sprite.image = ImageCache['SpringBlock1']
    else:
        sprite.image = ImageCache['SpringBlock2']

def SizeJumboRay(sprite): # 224
    flyleft = sprite.spritedata[4] & 15

    if flyleft == 1:
        sprite.xoffset = 0
        sprite.xsize = 171
        sprite.ysize = 79
        sprite.image = ImageCache['JumboRayL']
    else:
        sprite.xoffset = -152
        sprite.xsize = 171
        sprite.ysize = 79
        sprite.image = ImageCache['JumboRayR']

def SizePipeCannon(sprite): # 227
    fireDirection = (sprite.spritedata[5] & 0xF) % 7

    sprite.aux[0].image = ImageCache['PipeCannon%d' % (fireDirection)]

    if fireDirection == 0:
        # 30 deg to the right
        sprite.aux[0].SetSize(84, 101, 0, -5)
        path = QtGui.QPainterPath(QtCore.QPoint(0, 184))
        path.cubicTo(QtCore.QPoint(152, -24), QtCore.QPoint(168, -24), QtCore.QPoint(264, 48))
        path.lineTo(QtCore.QPoint(480, 216))
        sprite.aux[1].SetSize(480, 216, 24, -120)
    elif fireDirection == 1:
        # 30 deg to the left
        sprite.aux[0].SetSize(85, 101, -36, -5)
        path = QtGui.QPainterPath(QtCore.QPoint(480 - 0, 184))
        path.cubicTo(QtCore.QPoint(480 - 152, -24), QtCore.QPoint(480 - 168, -24), QtCore.QPoint(480 - 264, 48))
        path.lineTo(QtCore.QPoint(480 - 480, 216))
        sprite.aux[1].SetSize(480, 216, -480 + 24, -120)
    elif fireDirection == 2:
        # 15 deg to the right
        sprite.aux[0].SetSize(60, 102, 0, -6)
        path = QtGui.QPainterPath(QtCore.QPoint(0, 188))
        path.cubicTo(QtCore.QPoint(36, -36), QtCore.QPoint(60, -36), QtCore.QPoint(96, 84))
        path.lineTo(QtCore.QPoint(144, 252))
        sprite.aux[1].SetSize(144, 252, 30, -156)
    elif fireDirection == 3:
        # 15 deg to the left
        sprite.aux[0].SetSize(61, 102, -12, -6)
        path = QtGui.QPainterPath(QtCore.QPoint(144 - 0, 188))
        path.cubicTo(QtCore.QPoint(144 - 36, -36), QtCore.QPoint(144 - 60, -36), QtCore.QPoint(144 - 96, 84))
        path.lineTo(QtCore.QPoint(144 - 144, 252))
        sprite.aux[1].SetSize(144, 252, -144 + 18, -156)
    elif fireDirection == 4:
        # Straight up
        sprite.aux[0].SetSize(135, 132, -32 - 6 - 4, -16 - 6 - 8 - 4 - 1)
        path = QtGui.QPainterPath(QtCore.QPoint(26, 0))
        path.lineTo(QtCore.QPoint(26, 656))
        sprite.aux[1].SetSize(48, 656, 0, -632)
    elif fireDirection == 5:
        # 45 deg to the right
        sprite.aux[0].SetSize(90, 98, 0, -1)
        path = QtGui.QPainterPath(QtCore.QPoint(0, 320))
        path.lineTo(QtCore.QPoint(264, 64))
        path.cubicTo(QtCore.QPoint(348, -14), QtCore.QPoint(420, -14), QtCore.QPoint(528, 54))
        path.lineTo(QtCore.QPoint(1036, 348))
        sprite.aux[1].SetSize(1036, 348, 24, -252)
    elif fireDirection == 6:
        # 45 deg to the left
        sprite.aux[0].SetSize(91, 98, -42, -1)
        path = QtGui.QPainterPath(QtCore.QPoint(1036 - 0, 320))
        path.lineTo(QtCore.QPoint(1036 - 264, 64))
        path.cubicTo(QtCore.QPoint(1036 - 348, -14), QtCore.QPoint(1036 - 420, -14), QtCore.QPoint(1036 - 528, 54))
        path.lineTo(QtCore.QPoint(1036 - 1036, 348))
        sprite.aux[1].SetSize(1036, 348, -1036 + 24, -252)
    sprite.aux[1].SetPath(path)

def SizeExtendShroom(sprite): # 228
    props = sprite.spritedata[5]

    width = sprite.spritedata[4] & 1
    start = (props & 0x10) >> 4
    stemlength = props & 0xF

    if start == 0: # contracted
        sprite.image = ImageCache['ExtendShroomC']
        xsize = 32
    else:
        if width == 0: # big
            sprite.image = ImageCache['ExtendShroomB']
            xsize = 160
        else: # small
            sprite.image = ImageCache['ExtendShroomS']
            xsize = 96

    sprite.xoffset = 8 - (xsize / 2)
    sprite.xsize = xsize
    sprite.ysize = stemlength * 16 + 48

    sprite.setZValue(24999)

def SizeWiggleShroom(sprite): # 231
    width = (sprite.spritedata[4] & 0xF0) >> 4
    stemlength = sprite.spritedata[3] & 3

    sprite.xoffset = width * -8 - 20
    sprite.xsize = width * 16 + 56
    sprite.ysize = stemlength * 16 + 48 + 16

    sprite.setZValue(24999)

def SizeTiltGrate(sprite): # 256
    direction = sprite.spritedata[5] & 3
    if direction > 3: direction = 3

    if direction < 2:
        sprite.xsize = 69
        sprite.ysize = 166
    else:
        sprite.xsize = 166
        sprite.ysize = 69

    if direction == 0:
        sprite.xoffset = -36
        sprite.yoffset = -115
        sprite.image = ImageCache['TiltGrateU']
    elif direction == 1:
        sprite.xoffset = -36
        sprite.yoffset = 12
        sprite.image = ImageCache['TiltGrateD']
    elif direction == 2:
        sprite.xoffset = -144
        sprite.yoffset = 0
        sprite.image = ImageCache['TiltGrateL']
    elif direction == 3:
        sprite.xoffset = -20
        sprite.yoffset = 0
        sprite.image = ImageCache['TiltGrateR']


def SizeDoor(sprite): # 182, 259, 276, 277, 278, 452
    rotstatus = sprite.spritedata[4]
    if rotstatus & 1 == 0:
        direction = 0
    else:
        direction = (rotstatus & 0x30) >> 4

    if direction > 3: direction = 0
    doorType = sprite.doorType
    doorSize = sprite.doorSize
    if direction == 0:
        sprite.image = ImageCache[doorType+'U']
        sprite.xoffset = doorSize[0]
        sprite.yoffset = doorSize[1]
        sprite.xsize = doorSize[2]
        sprite.ysize = doorSize[3]
    elif direction == 1:
        sprite.image = ImageCache[doorType+'L']
        sprite.xoffset = (doorSize[2] / 2) + doorSize[0] - doorSize[3]
        sprite.yoffset = doorSize[1] + (doorSize[3] - (doorSize[2] / 2))
        sprite.xsize = doorSize[3]
        sprite.ysize = doorSize[2]
    elif direction == 2:
        sprite.image = ImageCache[doorType+'D']
        sprite.xoffset = doorSize[0]
        sprite.yoffset = doorSize[1]+doorSize[3]
        sprite.xsize = doorSize[2]
        sprite.ysize = doorSize[3]
    elif direction == 3:
        sprite.image = ImageCache[doorType+'R']
        sprite.xoffset = doorSize[0] + (doorSize[2] / 2)
        sprite.yoffset = doorSize[1] + (doorSize[3] - (doorSize[2] / 2))
        sprite.xsize = doorSize[3]
        sprite.ysize = doorSize[2]

def SizePoltergeistItem(sprite): # 262
    style = sprite.spritedata[5] & 15

    if style == 0:
        sprite.ysize = 16
        sprite.yoffset = 0
        sprite.aux[0].SetSize(60, 60)
        sprite.aux[0].image = ImageCache['PolterQBlock']
    else:
        sprite.ysize = 32
        sprite.yoffset = -16
        sprite.aux[0].SetSize(60, 84)
        sprite.aux[0].image = ImageCache['PolterStand']

def SizeFallingIcicle(sprite): # 265
    size = sprite.spritedata[5] & 1

    if size == 0:
        sprite.image = ImageCache['IcicleSmall']
        sprite.ysize = 19
    else:
        sprite.image = ImageCache['IcicleLarge']
        sprite.ysize = 36

def SizeLavaGeyser(sprite): # 268
    height = sprite.spritedata[4] >> 4
    startsAs = sprite.spritedata[5] & 15

    if height > 6: height = 0
    if height == 0:
        sprite.xoffset = -30
        sprite.yoffset = -170
        sprite.xsize = 69
        sprite.ysize = 200
    elif height == 1:
        sprite.xoffset = -28
        sprite.yoffset = -155
        sprite.xsize = 68
        sprite.ysize = 177
    elif height == 2:
        sprite.xoffset = -30
        sprite.yoffset = -155
        sprite.xsize = 70
        sprite.ysize = 177
    elif height == 3:
        sprite.xoffset = -43
        sprite.yoffset = -138
        sprite.xsize = 96
        sprite.ysize = 166
    elif height == 4:
        sprite.xoffset = -32
        sprite.yoffset = -105
        sprite.xsize = 76
        sprite.ysize = 134
    elif height == 5:
        sprite.xoffset = -26
        sprite.yoffset = -89
        sprite.xsize = 84
        sprite.ysize = 114
    elif height == 6:
        sprite.xoffset = -32
        sprite.yoffset = -34
        sprite.xsize = 96
        sprite.ysize = 78

    sprite.alpha = 0.75 if startsAs == 1 else 0.5

    sprite.image = ImageCache['LavaGeyser%d' % height]

def SizeMouser(sprite): # 271
    number = sprite.spritedata[5] >> 4
    direction = sprite.spritedata[5] & 0xF

    sprite.xsize = (number+1) * (ImageCache['Mouser'].width() / 1.5)

    if direction == 0: # Facing right
        sprite.xoffset = -(sprite.xsize) + 16
    else:
        sprite.xoffset = 0

def SizeCastleGear(sprite): # 274
    isBig = (sprite.spritedata[4] & 0xF) == 1
    sprite.image = ImageCache['CastleGearL'] if isBig else ImageCache['CastleGearS']
    sprite.xoffset = -(((sprite.image.width()/2.0)-12)*(2.0/3.0))
    sprite.yoffset = -(((sprite.image.height()/2.0)-12)*(2.0/3.0))
    sprite.xsize = sprite.image.width()*(2.0/3.0)
    sprite.ysize = sprite.image.height()*(2.0/3.0)

def SizeGiantIceBlock(sprite): # 280
    item = sprite.spritedata[5] & 3
    if item > 2: item = 0

    if item == 0:
        sprite.image = ImageCache['BigIceBlockEmpty']
    elif item == 1:
        sprite.image = ImageCache['BigIceBlockBobomb']
    elif item == 2:
        sprite.image = ImageCache['BigIceBlockSpikeBall']

def SizeWoodCircle(sprite): # 286
    size = sprite.spritedata[5] & 3
    if size == 3: size = 0

    sprite.image = ImageCache['WoodCircle%d' % size]

    if size == 0 or size > 2:
        sprite.xoffset = -24
        sprite.yoffset = -24
        sprite.xsize = 64
        sprite.ysize = 64
    elif size == 1:
        sprite.xoffset = -40
        sprite.yoffset = -40
        sprite.xsize = 96
        sprite.ysize = 96
    elif size == 2:
        sprite.xoffset = -56
        sprite.yoffset = -56
        sprite.xsize = 128
        sprite.ysize = 128


def SizePathIceBlock(sprite): # 287
    width  = (sprite.spritedata[5] &  15)+1
    height = (sprite.spritedata[5] >> 4) +1

    sprite.image = ImageCache['PathIceBlock'].scaled(width*24, height*24)
    sprite.xsize = width*16
    sprite.ysize = height*16


BoxSizes = [('Small', 32, 32), ('Wide', 64, 32), ('Tall', 32, 64), ('Big', 64, 64)]
def SizeBox(sprite): # 289
    style = sprite.spritedata[4] & 1
    size = (sprite.spritedata[5] >> 4) & 3

    style = 'Wood' if style == 0 else 'Metal'
    size = BoxSizes[size]

    sprite.image = ImageCache['Box%s%s' % (style, size[0])]
    sprite.xsize = size[1]
    sprite.ysize = size[2]

def SizeParabeetle(sprite): # 291
    direction = sprite.spritedata[5] & 3
    sprite.image = ImageCache['Parabeetle%d' % direction]

    if direction == 0 or direction > 3: # right
        sprite.xoffset = -12
        sprite.xsize = 39
    elif direction == 1: # left
        sprite.xoffset = -10
        sprite.xsize = 39
    elif direction == 2: # more right
        sprite.xoffset = -12
        sprite.xsize = 40
    elif direction == 3: # at you
        sprite.xoffset = -26
        sprite.xsize = 67


def SizeHeavyParabeetle(sprite): # 292
    direction = sprite.spritedata[5] & 3
    sprite.image = ImageCache['HeavyParabeetle%d' % direction]

    if direction == 0 or direction > 3: # right
        sprite.xoffset = -38
        sprite.xsize = 93
    elif direction == 1: # left
        sprite.xoffset = -38
        sprite.xsize = 94
    elif direction == 2: # more right
        sprite.xoffset = -38
        sprite.xsize = 93
    elif direction == 3: # at you
        sprite.xoffset = -52
        sprite.xsize = 110

def SizeNutPlatform(sprite): #295 (-16,0,96,32)
    offsetUp = sprite.spritedata[5] >> 4
    offsetRight = sprite.spritedata[5] & 15

    if offsetUp == 0:
        sprite.yoffset = -8
    else:
        sprite.yoffset = 0

    newOffsetRight = offsetRight if offsetRight < 8 else offsetRight - 8
    if newOffsetRight == 0:
        sprite.xoffset = -16
    elif newOffsetRight == 1:
        sprite.xoffset = -8
    elif newOffsetRight == 2:
        sprite.xoffset = 0
    elif newOffsetRight == 3:
        sprite.xoffset = 8
    elif newOffsetRight == 4:
        sprite.xoffset = 16
    elif newOffsetRight == 5:
        sprite.xoffset = 24
    elif newOffsetRight == 6:
        sprite.xoffset = 32
    else:
        sprite.xoffset = 40

    sprite.image = ImageCache['NutPlatform']

def SizeMegaBuzzy(sprite): # 296
    dir = sprite.spritedata[5] & 3

    if dir == 0 or dir > 2:
        sprite.image = ImageCache['MegaBuzzyR']
    elif dir == 1:
        sprite.image = ImageCache['MegaBuzzyL']
    elif dir == 2:
        sprite.image = ImageCache['MegaBuzzyF']

def SizeDragonCoaster(sprite): # 297
    raw_size = sprite.spritedata[5] & 7

    if raw_size == 0 or raw_size == 8:
        sprite.xsize = 32
        sprite.xoffset = 0
    else:
        sprite.xsize =( raw_size*32) + 32
        sprite.xoffset = (sprite.xsize - 32) * -1

def SizeCannonMulti(sprite): # 299  (-8,-11,32,28)
    number = sprite.spritedata[5]
    direction = 'UR'

    if number == 0:
        direction = 'UR'
        sprite.xsize = 32
        sprite.ysize = 28
        sprite.xoffset = -8
        sprite.yoffset = -11
    elif number == 1:
        direction = 'UL'
        sprite.xsize = 32
        sprite.ysize = 28
        sprite.xoffset = -8
        sprite.yoffset = -11
    elif number == 10:
        direction = 'DR'
        sprite.xsize = 32
        sprite.ysize = 28
        sprite.xoffset = -8
        sprite.yoffset = -11
    elif number == 11:
        direction = 'DL'
        sprite.xsize = 32
        sprite.ysize = 28
        sprite.xoffset = -8
        sprite.yoffset = -11
    else:
        sprite.xsize = 16
        sprite.ysize = 16
        sprite.xoffset = 0
        sprite.yoffset = 0
        direction = 'Q'


    sprite.image = ImageCache['CannonMulti%s' % direction]

def SizeRotCannon(sprite): # 300
    direction = (sprite.spritedata[5] & 0x10) >> 4

    sprite.xsize = 40
    sprite.ysize = 45

    if direction == 0 or direction > 1:
        sprite.xoffset = -12
        sprite.yoffset = -29
        sprite.image = ImageCache['RotCannon']
    elif direction == 1:
        sprite.xoffset = -12
        sprite.yoffset = 0
        sprite.image = ImageCache['RotCannonU']


def SizeRotCannonPipe(sprite): # 301
    direction = (sprite.spritedata[5] & 0x10) >> 4

    sprite.xsize = 80
    sprite.ysize = 90

    if direction == 0 or direction > 1:
        sprite.xoffset = -40
        sprite.yoffset = -74
        sprite.image = ImageCache['RotCannonPipe']
    elif direction == 1:
        sprite.xoffset = -40
        sprite.yoffset = 0
        sprite.image = ImageCache['RotCannonPipeU']


def SizeMontyMole(sprite): # 303
    mode = sprite.spritedata[5]
    if mode == 1:
        sprite.image = ImageCache['Mole']
        sprite.xoffset = 3.5
        sprite.yoffset = 0
        sprite.xsize = 20
        sprite.ysize = 23
    else:
        sprite.image = ImageCache['MoleCave']
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 28
        sprite.ysize = 25

def SizeRotFlameCannon(sprite): # 304
    orientation = sprite.spritedata[5] >> 4
    length = sprite.spritedata[5] & 15
    orientation = '' if orientation == 0 else 'Flipped'

    if length > 4: length = 0
    if orientation == '':
        if length == 0:
            sprite.yoffset = -2
            sprite.xsize = 73
        elif length == 1:
            sprite.yoffset = -2
            sprite.xsize = 93
        elif length == 2:
            sprite.yoffset = -2
            sprite.xsize = 108
        elif length == 3:
            sprite.yoffset = -2
            sprite.xsize = 124
        elif length == 4:
            sprite.yoffset = -2
            sprite.xsize = 133
    else:
        if length == 0:
            sprite.yoffset = 0
            sprite.xsize = 73
        elif length == 1:
            sprite.yoffset = 0
            sprite.xsize = 93
        elif length == 2:
            sprite.yoffset = 0
            sprite.xsize = 108
        elif length == 3:
            sprite.yoffset = 0
            sprite.xsize = 124
        elif length == 4:
            sprite.yoffset = 0
            sprite.xsize = 133

    sprite.image = ImageCache['RotFlameCannon%s%d' % (orientation, length)]


def SizeRotSpotlight(sprite): # 306
    angle = sprite.spritedata[3] & 15

    sprite.image = ImageCache['RotSpotlight%d' % angle]

def SizeSynchroFlameJet(sprite): # 309 (0,0,112,16)
    mode = sprite.spritedata[4] & 15
    direction = sprite.spritedata[5] & 15

    mode = 'On' if mode == 0 else 'Off'
    if direction == 0 or direction > 3:
        direction = 'R'
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 112
        sprite.ysize = 16
    elif direction == 1:
        direction = 'L'
        sprite.xoffset = -96
        sprite.yoffset = 0
        sprite.xsize = 112
        sprite.ysize = 16
    elif direction == 2:
        direction = 'U'
        sprite.xoffset = 0
        sprite.yoffset = -96
        sprite.xsize = 16
        sprite.ysize = 112
    elif direction == 3:
        direction = 'D'
        sprite.xoffset = 0
        sprite.yoffset = 0
        sprite.xsize = 16
        sprite.ysize = 112

    sprite.image = ImageCache['SynchroFlameJet%s%s' % (mode, direction)]

def SizeArrowSign(sprite): # 310
    direction = sprite.spritedata[5] & 7
    sprite.image = ImageCache['ArrowSign%d' % direction]

def SizeBubbleGen(sprite): # 314
    sprite.updateScene()

def SizeBoltBox(sprite): # 316
    size = sprite.spritedata[5]
    sprite.xsize = (size & 0xF) * 16 + 32
    sprite.ysize = ((size & 0xF0) >> 4) * 16 + 32

def SizeArrowBlock(sprite): # 321
    direction = sprite.spritedata[5] & 3
    sprite.image = ImageCache['ArrowBlock%d' % direction]

def SizeBooCircle(sprite): # 323
    # Constants (change these to fine-tune the boo positions)
    radiusMultiplier = 24 # pixels between boos per distance value
    radiusConstant = 24 # add to all radius values
    opacity = 0.5

    # Read the data
    outrad   =    sprite.spritedata[2] & 15
    inrad    =    sprite.spritedata[3] >> 4
    ghostnum = 1+(sprite.spritedata[3] & 15)
    differentRads = not inrad == outrad

    # Give up if the data is invalid
    if inrad > outrad:
        null = QtGui.QPixmap(2,2)
        null.fill(QtGui.QColor.fromRgb(0,0,0,0))
        sprite.aux[0].image = null
        return

    # Create a pixmap
    pix = QtGui.QPixmap(1024, 1024)
    pix.fill(QtGui.QColor.fromRgb(0,0,0,0))
    paint = QtGui.QPainter(pix)
    paint.setOpacity(opacity)

    # Iterate through each ghost
    for i in range(ghostnum):
        # Find the angle at which to place the ghost from the center
        MissingGhostWeight = 0.75 - (1.0/ghostnum) # approximate
        angle = math.radians(-360*i/(ghostnum+MissingGhostWeight)) + 89.6

        # Since the origin of the boo img is in the top left, account for that
        offsetX = ImageCache['Boo1'].width()/2
        offsetY = (ImageCache['Boo1'].height()/2) + 16 # the circle is not centered

        # Pick a pixmap
        boo = ImageCache['Boo%d' % (1 if i==0 else ((i-1) % 3) + 2)] # 1  2 3 4  2 3 4  2 3 4 ...

        # Find the abs pos, and paint the ghost at its inner position
        x = math.sin(angle) * ((inrad * radiusMultiplier) + radiusConstant)          - offsetX
        y = (math.cos(angle) * ((inrad * radiusMultiplier) + radiusConstant) * (-1)) - offsetY
        paint.drawPixmap(x+512, y+512, boo)

        # Paint it at its outer position if it has one
        if differentRads:
            x = math.sin(angle) * ((outrad * radiusMultiplier) + radiusConstant)          - offsetX
            y = (math.cos(angle) * ((outrad * radiusMultiplier) + radiusConstant) * (-1)) - offsetY
            paint.drawPixmap(x+512, y+512, boo)

    # Finish it
    paint = None
    sprite.aux[0].image = pix

def SizeKingBill(sprite): # 326
    direction = sprite.spritedata[5] & 15

    PointsRects = [ # These form a LEFT-FACING bullet
        QtCore.QPointF(192,         -180),
        QtCore.QRectF( 0,           -180, 384, 384),
        QtCore.QPointF(192+72,       204),
        QtCore.QPointF(192+72+6,     204-24),
        QtCore.QPointF(192+72+42,    204-24),
        QtCore.QPointF(192+72+48,    204),
        QtCore.QPointF(192+72+96,    204),
        QtCore.QPointF(192+72+96+6,  204-6),
        QtCore.QPointF(192+72+96+6, -180+6),
        QtCore.QPointF(192+72+96,   -180),
        QtCore.QPointF(192+72+48,   -180),
        QtCore.QPointF(192+72+42,   -180+24),
        QtCore.QPointF(192+72+6,    -180+24),
        QtCore.QPointF(192+72,      -180)]

    for thing in PointsRects: # translate each point to flip the image
        if direction == 0:   #faces left
            arc = 'LR'
        elif direction == 1: # faces right
            arc = 'LR'
            if isinstance(thing, QtCore.QPointF):
                thing.setX((thing.x()*-1)+24)
            else:
                thing.setRect((thing.x()*-1)+24, thing.y(), thing.width()*-1, thing.height())
        elif direction == 2: # faces down
            arc = 'UD'
            if isinstance(thing, QtCore.QPointF):
                x = thing.y()-60
                y = (thing.x()*-1)+24
                thing.setX(x)
                thing.setY(y)
            else:
                x = thing.y()-60
                y = (thing.x()*-1)+24
                thing.setRect(x, y, thing.height(), thing.width()*-1)
        else: # faces up
            arc = 'UD'
            if isinstance(thing, QtCore.QPointF):
                x = thing.y()+60
                y = thing.x()
                thing.setX(x)
                thing.setY(y)
            else:
                x = thing.y()+60
                y = thing.x()
                thing.setRect(x, y, thing.height(), thing.width())

    PainterPath = QtGui.QPainterPath()
    PainterPath.moveTo(PointsRects[0])
    if arc == 'LR': PainterPath.arcTo(PointsRects[1],  90,  180)
    else:           PainterPath.arcTo(PointsRects[1], 180, -180)
    for point in PointsRects[2:len(PointsRects)]:
        PainterPath.lineTo(point)
    PainterPath.closeSubpath()

    sprite.aux[0].SetPath(PainterPath)

def SizeRopeLadder(sprite): # 330
    size = sprite.spritedata[5]
    if size > 2: size = 0
    sprite.image = ImageCache['RopeLadder%d' % size]
    if size == 0:
        sprite.ysize = 74
    elif size == 1:
        sprite.ysize = 108
    elif size == 2:
        sprite.ysize = 140

def SizeDishPlatform(sprite): # 331
    size = sprite.spritedata[4] & 15

    if size == 0:
        sprite.xoffset = -144
        sprite.xsize = 304
    else:
        sprite.xoffset = -208
        sprite.xsize = 433

    sprite.image = ImageCache['DishPlatform%d' % size]

def SizeCheepGiant(sprite): # 334 (-6,-7,28,25)
    type = sprite.spritedata[5] & 0xF

    if type == 3:
        sprite.xsize = 28
        sprite.ysize = 25
        sprite.image = ImageCache['CheepGiantRedR']
    elif type == 7:
        sprite.xsize = 28
        sprite.ysize = 26
        sprite.image = ImageCache['CheepGiantGreen']
    elif type == 8:
        sprite.xsize = 27
        sprite.ysize = 28
        sprite.image = ImageCache['CheepGiantYellow']
    else:
        sprite.xsize = 28
        sprite.ysize = 25
        sprite.image = ImageCache['CheepGiantRedL']

def SizePipe(sprite): # 339, 353, 377, 378, 379, 380, 450
    # Sprite types:
    # 339 = Moving Pipe Facing Up
    # 353 = Moving Pipe Facing Down
    # 377 = Pipe Up
    # 378 = Pipe Down
    # 379 = Pipe Right
    # 380 = Pipe Left
    # 450 = Enterable Pipe Up

    type = sprite.type
    props = sprite.spritedata[5]

    if type > 353: # normal pipes
        sprite.moving = False
        sprite.colour = (props & 0x30) >> 4
        length = props & 0xF

        size = length * 16 + 32
        if type == 379 or type == 380: # horizontal
            sprite.xsize = size
            sprite.ysize = 32
            sprite.orientation = 'H'
            if type == 379:   # faces right
                sprite.direction = 'R'
                sprite.xoffset = 0
            else:             # faces left
                sprite.direction = 'L'
                sprite.xoffset = 16 - size
            sprite.yoffset = 0

        else: # vertical
            sprite.xsize = 32
            sprite.ysize = size
            sprite.orientation = 'V'
            if type == 378: # faces down
                sprite.direction = 'D'
                sprite.yoffset = 0
            else:                          # faces up
                sprite.direction = 'U'
                sprite.yoffset = 16 - size
            sprite.xoffset = 0

    else: # moving pipes
        sprite.moving = True

        sprite.colour = sprite.spritedata[3]
        length1 = (props & 0xF0) >> 4
        length2 = (props & 0xF)
        size = max(length1, length2) * 16 + 32

        sprite.xsize = 32
        sprite.ysize = size
        sprite.orientation = 'V'

        if type == 339: # facing up
            sprite.direction = 'U'
            sprite.yoffset = 16 - size
        else:
            sprite.direction = 'D'
            sprite.yoffset = 0

        sprite.length1 = length1 * 16 + 32
        sprite.length2 = length2 * 16 + 32


def SizeBigShell(sprite): # 341
    style = sprite.spritedata[5] & 1
    if style == 0:
        sprite.image = ImageCache['BigShellGrass']
    else:
        sprite.image = ImageCache['BigShell']

def SizeMuncher(sprite): # 342
    frozen = sprite.spritedata[5] & 1
    if frozen == 0:
        sprite.image = ImageCache['Muncher']
    else:
        sprite.image = ImageCache['MuncherF']

def SizeFuzzy(sprite): # 343
    giant = sprite.spritedata[4] & 1

    if giant == 0:
        sprite.xoffset = -7
        sprite.yoffset = -7
        sprite.xsize = 30
        sprite.ysize = 30
        sprite.image = ImageCache['Fuzzy']
    else:
        sprite.xoffset = -18
        sprite.yoffset = -18
        sprite.xsize = 52
        sprite.ysize = 52
        sprite.image = ImageCache['FuzzyGiant']

def SizeHangingChainPlatform(sprite): # 346
    size = sprite.spritedata[4] & 15

    if size in (0, 4, 8, 12):
        size = 'S'
        sprite.xoffset = -26
        sprite.xsize = 68
    elif size in (1, 5, 9, 13):
        size = 'M'
        sprite.xoffset = -42
        sprite.xsize = 98
    else:
        size = 'L'
        sprite.xoffset = -58
        sprite.xsize = 131

    sprite.image = ImageCache['HangingChainPlatform%s' % size]

def SizeBrownBlock(sprite): # 356
    size = sprite.spritedata[5]
    height = (size & 0xF0) >> 4
    width = size & 0xF
    height = 1 if height == 0 else height
    width = 1 if width == 0 else width
    sprite.xsize = width * 16 + 16
    sprite.ysize = height * 16 + 16

    type = sprite.type
    # now set up the track
    if(type == 354): return
    direction = sprite.spritedata[2] & 3
    distance = (sprite.spritedata[4] & 0xF0) >> 4

    if direction <= 1: # horizontal
        sprite.aux[0].direction = 1
        sprite.aux[0].SetSize(sprite.xsize + (distance * 16), sprite.ysize)
    else: # vertical
        sprite.aux[0].direction = 2
        sprite.aux[0].SetSize(sprite.xsize, sprite.ysize + (distance * 16))

    if (direction in (0, 3)) or (direction not in (1, 2)): # right, down
        sprite.aux[0].setPos(0,0)
    elif direction == 1: # left
        sprite.aux[0].setPos(-distance * 24,0)
    elif direction == 2: # up
        sprite.aux[0].setPos(0,-distance * 24)

def SizeFruit(sprite): # 357
    style = sprite.spritedata[5] & 1
    if style == 0:
        sprite.image = ImageCache['Fruit']
    else:
        sprite.image = ImageCache['Cookie']

def SizeLavaParticles(sprite): # 358
    sprite.updateScene()

def SizeCrystalBlock(sprite): # 361
    size = sprite.spritedata[4] & 15
    if size > 2: size = 0

    if size == 0:
        sprite.xsize = 201
        sprite.ysize = 172
    elif size == 1:
        sprite.xsize = 267
        sprite.ysize = 169
    elif size == 2:
        sprite.xsize = 348
        sprite.ysize = 110

    sprite.image = ImageCache['CrystalBlock%d' % size]

def SizeColouredBox(sprite): # 362
    sprite.colour = (sprite.spritedata[3] >> 4) & 3

    size = sprite.spritedata[4]
    width = size >> 4
    height = size & 0xF

    sprite.xsize = ((width + 3) * 16)
    sprite.ysize = ((height + 3) * 16)

def SizeCubeKinokoRot(sprite): # 366
    style = (sprite.spritedata[4] & 1)

    if style == 0:
        sprite.image = ImageCache['CubeKinokoR']
        sprite.xsize = 80
        sprite.ysize = 80
    else:
        sprite.image = ImageCache['CubeKinokoG']
        sprite.xsize = 240
        sprite.ysize = 240

def SizeSlidingPenguin(sprite): # 369
    direction = sprite.spritedata[5] & 1

    if direction == 0:
        sprite.image = ImageCache['PenguinL']
    else:
        sprite.image = ImageCache['PenguinR']

def SizeSnowWind(sprite): # 374
    sprite.updateScene()

def SizeMovingChainLink(sprite): # 376
    sprite.shape = sprite.spritedata[4] >> 4
    sprite.direction = sprite.spritedata[5] & 15
    arrow = None

    if (sprite.shape == 0) or (sprite.shape > 3):
        sprite.xsize = 64
        sprite.ysize = 64
    elif sprite.shape == 1:
        sprite.xsize = 64
        sprite.ysize = 128
    elif sprite.shape == 2:
        sprite.xsize = 64
        sprite.ysize = 224
    elif sprite.shape == 3:
        sprite.xsize = 192
        sprite.ysize = 64

    sprite.xoffset = sprite.xsize / 2 * -1
    sprite.yoffset = sprite.ysize / 2 * -1

def SizeIceBlock(sprite): # 385
    size = sprite.spritedata[5]
    height = (size & 0x30) >> 4
    width = size & 3

    sprite.image = ImageCache['IceBlock%d%d' % (width,height)]
    sprite.xoffset = width * -4
    sprite.yoffset = height * -8
    sprite.xsize = width * 8 + 16
    sprite.ysize = height * 8 + 16

def SizeBush(sprite): # 387
    props = sprite.spritedata[5]
    style = (props >> 4) & 1
    size = props & 3

    sprite.image = ImageCache['Bush%d%d' % (style, size)]

    if (size == 0) or (size > 3):
        sprite.xoffset = -22
        sprite.yoffset = -25
        sprite.xsize = 45
        sprite.ysize = 30
    elif size == 1:
        sprite.xoffset = -29
        sprite.yoffset = -45
        sprite.xsize = 60
        sprite.ysize = 51
    elif size == 2:
        sprite.xoffset = -41
        sprite.yoffset = -61
        sprite.xsize = 83
        sprite.ysize = 69
    elif size == 3:
        sprite.xoffset = -52
        sprite.yoffset = -80
        sprite.xsize = 108
        sprite.ysize = 86

def SizeMoveWhenOn(sprite): # 396
    # get width
    raw_size = sprite.spritedata[5] & 0xF
    if raw_size == 0:
        sprite.xoffset = -16
        sprite.xsize = 32
    else:
        sprite.xoffset = 0
        sprite.xsize = raw_size*16
        sprite.xsize = raw_size*16

    # set direction
    sprite.direction =(sprite.spritedata[3] >> 4)

def SizeGhostHouseBox(sprite): # 397
    height = sprite.spritedata[4] >> 4
    width = sprite.spritedata[5] & 15

    sprite.xsize = ((width + 2) * 16)
    sprite.ysize = ((height + 2) * 16)

def SizeGabon(sprite): # 414
    throwdir = sprite.spritedata[5] & 1
    facing = sprite.spritedata[4] & 1

    if throwdir == 0: # down
        sprite.image = ImageCache['GabonDown']
        sprite.xoffset = -5
        sprite.yoffset = -29
        sprite.xsize = 26
        sprite.ysize = 47
    else: # left/right
        if facing == 0:
            sprite.image = ImageCache['GabonLeft']
            sprite.xoffset = -7
            sprite.yoffset = -31
        else:
            sprite.image = ImageCache['GabonRight']
            sprite.xoffset = -7
            sprite.yoffset = -31
        sprite.xsize = 29
        sprite.ysize = 49

def SizeGiantGlowBlock(sprite): # 420
    type = sprite.spritedata[4] >> 4

    if type == 0:
        sprite.aux[0].image = ImageCache['GiantGlowBlock']
        sprite.aux[0].setPos(-25, -30)
        sprite.aux[0].SetSize(100, 100)
    else:
        sprite.aux[0].image = ImageCache['GiantGlowBlockOff']
        sprite.aux[0].setPos(0, 0)
        sprite.aux[0].SetSize(48, 48)

def SizePalmTree(sprite): # 424
    size = sprite.spritedata[5] & 7
    image = ImageCache['PalmTree%d' % size]
    sprite.image = image
    sprite.ysize = image.height() / 1.5
    sprite.yoffset = 16 - (image.height() / 1.5)

def SizeWarpCannon(sprite): # 434
    dest = sprite.spritedata[5] & 3
    if dest == 3: dest = 0
    sprite.image = ImageCache['Warp%d' % dest]

def SizeGhostFog(sprite): # 435
    sprite.zoneRealView = sprite.spritedata[5] == 0
    sprite.updateScene()

def SizePurplePole(sprite): # 437
    length = sprite.spritedata[5]
    sprite.ysize = (length+3) * 16

def SizeCageBlocks(sprite): # 438
    type = sprite.spritedata[4] & 15

    if (type == 0) or (type > 4):
        sprite.xoffset = -112
        sprite.yoffset = -112
        sprite.xsize = 240
        sprite.ysize = 240
    elif type == 1:
        sprite.xoffset = -112
        sprite.yoffset = -112
        sprite.xsize = 240
        sprite.ysize = 240
    elif type == 2:
        sprite.xoffset = -97
        sprite.yoffset = -81
        sprite.xsize = 210
        sprite.ysize = 177
    elif type == 3:
        sprite.xoffset = -80
        sprite.yoffset = -96
        sprite.xsize = 176
        sprite.ysize = 208
    elif type == 4:
        sprite.xoffset = -112
        sprite.yoffset = -112
        sprite.xsize = 240
        sprite.ysize = 240

    sprite.image = ImageCache['CageBlock%d' % type]

def SizeHorizontalRope(sprite): # 440
    length = sprite.spritedata[5]
    sprite.xsize = (length+3) * 16

def SizeMushroomPlatform(sprite): # 441
    # get size/colour
    sprite.colour = sprite.spritedata[4] & 1
    sprite.shroomsize = (sprite.spritedata[5] >> 4) & 1
    sprite.ysize = 16 * (sprite.shroomsize+1)

    # get width
    width = sprite.spritedata[5] & 0xF
    if sprite.shroomsize == 0:
        sprite.xsize = (width << 4) + 32
        sprite.xoffset = 0 - (int((width + 1) / 2) << 4)
        sprite.yoffset = 0
    else:
        sprite.xsize = (width << 5) + 64
        sprite.xoffset = 16 - (sprite.xsize / 2)
        sprite.yoffset = -16


def SizeSwingVine(sprite): # 444, 464
    style = sprite.spritedata[5] & 1
    if sprite.type == 444: style = 0

    if style == 0:
        sprite.image = ImageCache['SwingVine']
    else:
        sprite.image = ImageCache['SwingChain']


SeaweedSizes = [0, 1, 2, 2, 3]
SeaweedXOffsets = [-26, -22, -31, -42]
def SizeSeaweed(sprite): # 453
    style = sprite.spritedata[5] & 0xF
    if style > 4: style = 4
    size = SeaweedSizes[style]

    image = ImageCache['Seaweed%d' % size]
    sprite.image = image
    sprite.xsize = image.width() / 1.5
    sprite.ysize = image.height() / 1.5
    sprite.xoffset = SeaweedXOffsets[size]
    sprite.yoffset = 17 - sprite.ysize
    sprite.setZValue(24998)

def SizeBossBridge(sprite): # 456
    style = sprite.spritedata[5] & 3
    if (style == 0) or (style > 2):
        sprite.image = ImageCache['BossBridgeM']
    elif style == 1:
        sprite.image = ImageCache['BossBridgeR']
    elif style == 2:
        sprite.image = ImageCache['BossBridgeL']

def SizeBoltPlatform(sprite): # 469
    length = sprite.spritedata[5] & 0xF
    sprite.xsize = (length+2) * 16

def SizeIceFlow(sprite): # 475
    size = sprite.spritedata[5] & 15

    if (size == 0) or (size > 12): # 3x3
        sprite.xoffset = -1
        sprite.yoffset = -32
        sprite.xsize = 50
        sprite.ysize = 48
    elif size == 1: # 4x4
        sprite.xoffset = -2
        sprite.yoffset = -48
        sprite.xsize = 68
        sprite.ysize = 64
    elif size == 2: # 5x5
        sprite.xoffset = -2
        sprite.yoffset = -64
        sprite.xsize = 84
        sprite.ysize = 80
    elif size == 3: # 4x3
        sprite.xoffset = -2
        sprite.yoffset = -32
        sprite.xsize = 67
        sprite.ysize = 48
    elif size == 4: # 5x4
        sprite.xoffset = -2
        sprite.yoffset = -48
        sprite.xsize = 84
        sprite.ysize = 64
    elif size == 5: # 7x6
        sprite.xoffset = -3
        sprite.yoffset = -80
        sprite.xsize = 118
        sprite.ysize = 96
    elif size == 6: # 16x11
        sprite.xoffset = -3
        sprite.yoffset = -160
        sprite.xsize = 264
        sprite.ysize = 176
    elif size == 7: # 11x8
        sprite.xoffset = -3
        sprite.yoffset = -112
        sprite.xsize = 182
        sprite.ysize = 128
    elif size == 8: # 2x4
        sprite.xoffset = -1
        sprite.yoffset = -48
        sprite.xsize = 34
        sprite.ysize = 64
    elif size == 9: # 3x4
        sprite.xoffset = -2
        sprite.yoffset = -48
        sprite.xsize = 51
        sprite.ysize = 64
    elif size == 10: # 6x7
        sprite.xoffset = -2.5
        sprite.yoffset = -96
        sprite.xsize = 101
        sprite.ysize = 112
    elif size == 11: # 2x5
        sprite.xoffset = -1
        sprite.yoffset = -64
        sprite.xsize = 34
        sprite.ysize = 80
    elif size == 12: # 3x5
        sprite.xoffset = -1
        sprite.yoffset = -64
        sprite.xsize = 50
        sprite.ysize = 80

    sprite.image = ImageCache['IceFlow%d' % size]

# ---- Resource Loaders ----
def LoadBasicSuite():
    global ImageCache
    ImageCache['Coin'] = GetImg('coin.png')
    ImageCache['SpecialCoin'] = GetImg('special_coin.png')
    ImageCache['PCoin'] = GetImg('p_coin.png')
    ImageCache['RedCoin'] = GetImg('redcoin.png')
    ImageCache['RedCoinRing'] = GetImg('redcoinring.png')
    ImageCache['Goomba'] = GetImg('goomba.png')
    ImageCache['Paragoomba'] = GetImg('paragoomba.png')
    ImageCache['Fishbones'] = GetImg('fishbones.png')
    ImageCache['SpinyCheep'] = GetImg('cheep_spiny.png')
    ImageCache['Jellybeam'] = GetImg('jellybeam.png')
    ImageCache['Bulber'] = GetImg('bulber.png')
    ImageCache['CheepChomp'] = GetImg('cheep_chomp.png')
    ImageCache['Urchin'] = GetImg('urchin.png')
    ImageCache['MegaUrchin'] = GetImg('mega_urchin.png')
    ImageCache['Puffer'] = GetImg('porcu_puffer.png')
    ImageCache['Microgoomba'] = GetImg('microgoomba.png')
    ImageCache['Giantgoomba'] = GetImg('giantgoomba.png')
    ImageCache['Megagoomba'] = GetImg('megagoomba.png')
    ImageCache['ChestnutGoomba'] = GetImg('chestnut_goomba.png')
    ImageCache['KoopaG'] = GetImg('koopa_green.png')
    ImageCache['KoopaR'] = GetImg('koopa_red.png')
    ImageCache['KoopaShellG'] = GetImg('koopa_green_shell.png')
    ImageCache['KoopaShellR'] = GetImg('koopa_red_shell.png')
    ImageCache['ParakoopaG'] = GetImg('parakoopa_green.png')
    ImageCache['ParakoopaR'] = GetImg('parakoopa_red.png')
    ImageCache['BuzzyBeetle'] = GetImg('buzzy_beetle.png')
    ImageCache['BuzzyBeetleU'] = GetImg('buzzy_beetle_u.png')
    ImageCache['BuzzyBeetleShell'] = GetImg('buzzy_beetle_shell.png')
    ImageCache['BuzzyBeetleShellU'] = GetImg('buzzy_beetle_shell_u.png')
    ImageCache['Spiny'] = GetImg('spiny.png')
    ImageCache['SpinyU'] = GetImg('spiny_u.png')
    ImageCache['SpinyShell'] = GetImg('spiny_shell.png')
    ImageCache['SpinyShellU'] = GetImg('spiny_shell_u.png')
    ImageCache['SpinyBall'] = GetImg('spiny_ball.png')
    ImageCache['Wiggler'] = GetImg('wiggler.png')
    ImageCache['GiantWiggler'] = GetImg('giant_wiggler.png')
    ImageCache['SuperGuide'] = GetImg('superguide_block.png')
    ImageCache['RouletteBlock'] = GetImg('roulette.png')
    ImageCache['GiantGlowBlock'] = GetImg('giant_glow_block.png')
    ImageCache['GiantGlowBlockOff'] = GetImg('giant_glow_block_off.png')
    ImageCache['BigBrickBlock'] = GetImg('big_block.png')
    ImageCache['UnderwaterLamp'] = GetImg('underwater_lamp.png')
    ImageCache['PlayerBlock'] = GetImg('player_block.png')
    ImageCache['PlayerBlockPlatform'] = GetImg('player_block_platform.png')
    ImageCache['BoxGenerator'] = GetImg('box_generator.png')
    ImageCache['StarCoin'] = GetImg('starcoin.png')
    ImageCache['ToadBalloon'] = GetImg('toad_balloon.png')
    ImageCache['RCEDBlock'] = GetImg('rced_block.png')
    ImageCache['PipePlantUp'] = GetImg('piranha_pipe_up.png')
    ImageCache['PipePlantDown'] = GetImg('piranha_pipe_down.png')
    ImageCache['PipePlantLeft'] = GetImg('piranha_pipe_left.png')
    ImageCache['PipePlantRight'] = GetImg('piranha_pipe_right.png')
    ImageCache['PipeFiretrapUp'] = GetImg('firetrap_pipe_up.png')
    ImageCache['PipeFiretrapDown'] = GetImg('firetrap_pipe_down.png')
    ImageCache['PipeFiretrapLeft'] = GetImg('firetrap_pipe_left.png')
    ImageCache['PipeFiretrapRight'] = GetImg('firetrap_pipe_right.png')
    ImageCache['FiveEnemyRaft'] = GetImg('5_enemy_max_raft.png')

    Huckitcrab = GetImg('huckit_crab.png', True)
    ImageCache['HuckitCrabL'] = QtGui.QPixmap.fromImage(Huckitcrab)
    ImageCache['HuckitCrabR'] = QtGui.QPixmap.fromImage(Huckitcrab.mirrored(True, False))

    Fishbones = GetImg('fishbones.png', True)
    ImageCache['FishbonesL'] = QtGui.QPixmap.fromImage(Fishbones)
    ImageCache['FishbonesR'] = QtGui.QPixmap.fromImage(Fishbones.mirrored(True, False))

    Mouser = GetImg('mouser.png', True)
    ImageCache['MouserL'] = QtGui.QPixmap.fromImage(Mouser)
    ImageCache['MouserR'] = QtGui.QPixmap.fromImage(Mouser.mirrored(True, False))

    GP = GetImg('ground_piranha.png', True)
    ImageCache['GroundPiranha'] = QtGui.QPixmap.fromImage(GP)
    ImageCache['GroundPiranhaU'] = QtGui.QPixmap.fromImage(GP.mirrored(False, True))

    BGP = GetImg('big_ground_piranha.png', True)
    ImageCache['BigGroundPiranha'] = QtGui.QPixmap.fromImage(BGP)
    ImageCache['BigGroundPiranhaU'] = QtGui.QPixmap.fromImage(BGP.mirrored(False, True))

    GF = GetImg('ground_firetrap.png', True)
    ImageCache['GroundFiretrap'] = QtGui.QPixmap.fromImage(GF)
    ImageCache['GroundFiretrapU'] = QtGui.QPixmap.fromImage(GF.mirrored(False, True))

    BGF = GetImg('big_ground_firetrap.png', True)
    ImageCache['BigGroundFiretrap'] = QtGui.QPixmap.fromImage(BGF)
    ImageCache['BigGroundFiretrapU'] = QtGui.QPixmap.fromImage(BGF.mirrored(False, True))

    BlockImage = GetImg('blocks.png')
    Blocks = []
    count = BlockImage.width() / 24
    for i in range(int(count)):
        Blocks.append(BlockImage.copy(i*24, 0, 24, 24))
    ImageCache['Blocks'] = Blocks

    Overrides = QtGui.QPixmap('reggiedata/overrides.png')
    Blocks = []
    x = Overrides.width() / 24
    y = Overrides.height() / 24
    for i in range(int(y)):
        for j in range(int(x)):
            Blocks.append(Overrides.copy(j*24, i*24, 24, 24))
    ImageCache['Overrides'] = Blocks

def LoadDesertStuff():
    global ImageCache
    ImageCache['PokeyTop'] = GetImg('pokey_top.png')
    ImageCache['PokeyMiddle'] = GetImg('pokey_middle.png')
    ImageCache['PokeyBottom'] = GetImg('pokey_bottom.png')
    ImageCache['Lakitu'] = GetImg('lakitu.png')

def LoadPlatformImages():
    global ImageCache
    ImageCache['WoodenPlatformL'] = GetImg('wood_platform_left.png')
    ImageCache['WoodenPlatformM'] = GetImg('wood_platform_middle.png')
    ImageCache['WoodenPlatformR'] = GetImg('wood_platform_right.png')
    ImageCache['StonePlatformL'] = GetImg('stone_platform_left.png')
    ImageCache['StonePlatformM'] = GetImg('stone_platform_middle.png')
    ImageCache['StonePlatformR'] = GetImg('stone_platform_right.png')
    ImageCache['BonePlatformL'] = GetImg('bone_platform_left.png')
    ImageCache['BonePlatformM'] = GetImg('bone_platform_middle.png')
    ImageCache['BonePlatformR'] = GetImg('bone_platform_right.png')
    ImageCache['TiltingGirder'] = GetImg('tilting_girder.png')
    ImageCache['FlashlightRaft'] = GetImg('flashraft.png')

def LoadMoveWhenOn():
    global ImageCache
    ImageCache['MoveWhenOnL'] = GetImg('mwo_left.png')
    ImageCache['MoveWhenOnM'] = GetImg('mwo_middle.png')
    ImageCache['MoveWhenOnR'] = GetImg('mwo_right.png')
    ImageCache['MoveWhenOnC'] = GetImg('mwo_circle.png')

    transform90 = QtGui.QTransform()
    transform180 = QtGui.QTransform()
    transform270 = QtGui.QTransform()
    transform90.rotate(90)
    transform180.rotate(180)
    transform270.rotate(270)

    for direction in ['R''L''U''D']:
        image = GetImg('sm_arrow.png', True)
        ImageCache['SmArrow'+'R'] = QtGui.QPixmap.fromImage(image)
        ImageCache['SmArrow'+'D'] = QtGui.QPixmap.fromImage(image.transformed(transform90))
        ImageCache['SmArrow'+'L'] = QtGui.QPixmap.fromImage(image.transformed(transform180))
        ImageCache['SmArrow'+'U'] = QtGui.QPixmap.fromImage(image.transformed(transform270))

def LoadDSStoneBlocks():
    global ImageCache
    ImageCache['DSBlockTopLeft'] = GetImg('dsblock_topleft.png')
    ImageCache['DSBlockTop'] = GetImg('dsblock_top.png')
    ImageCache['DSBlockTopRight'] = GetImg('dsblock_topright.png')
    ImageCache['DSBlockLeft'] = GetImg('dsblock_left.png')
    ImageCache['DSBlockRight'] = GetImg('dsblock_right.png')
    ImageCache['DSBlockBottomLeft'] = GetImg('dsblock_bottomleft.png')
    ImageCache['DSBlockBottom'] = GetImg('dsblock_bottom.png')
    ImageCache['DSBlockBottomRight'] = GetImg('dsblock_bottomright.png')

def LoadSwitches():
    global ImageCache
    q = GetImg('q_switch.png', True)
    p = GetImg('p_switch.png', True)
    e = GetImg('e_switch.png', True)
    elg = GetImg('e_switch_lg.png', True)
    ImageCache['QSwitch'] = QtGui.QPixmap.fromImage(q)
    ImageCache['PSwitch'] = QtGui.QPixmap.fromImage(p)
    ImageCache['ESwitch'] = QtGui.QPixmap.fromImage(e)
    ImageCache['ELSwitch'] = QtGui.QPixmap.fromImage(elg)
    ImageCache['QSwitchU'] = QtGui.QPixmap.fromImage(q.mirrored(True, True))
    ImageCache['PSwitchU'] = QtGui.QPixmap.fromImage(p.mirrored(True, True))
    ImageCache['ESwitchU'] = QtGui.QPixmap.fromImage(e.mirrored(True, True))
    ImageCache['ELSwitchU'] = QtGui.QPixmap.fromImage(elg.mirrored(True, True))
    ImageCache['QSwitchBlock'] = GetImg('q_switch_block.png')
    ImageCache['PSwitchBlock'] = GetImg('p_switch_block.png')
    ImageCache['ESwitchBlock'] = GetImg('e_switch_block.png')

def LoadCastleStuff():
    global ImageCache
    ImageCache['Podoboo'] = GetImg('podoboo.png')
    ImageCache['Thwomp'] = GetImg('thwomp.png')
    ImageCache['GiantThwomp'] = GetImg('giant_thwomp.png')
    ImageCache['SpikeBall'] = GetImg('spike_ball.png')
    ImageCache['GiantSpikeBall'] = GetImg('giant_spike_ball.png')

def LoadEnvItems():
    global ImageCache
    ImageCache['SpringBlock1'] = GetImg('spring_block.png')
    ImageCache['SpringBlock2'] = GetImg('spring_block_alt.png')
    ImageCache['RopeLadder0'] = GetImg('ropeladder_0.png')
    ImageCache['RopeLadder1'] = GetImg('ropeladder_1.png')
    ImageCache['RopeLadder2'] = GetImg('ropeladder_2.png')
    ImageCache['Fruit'] = GetImg('fruit.png')
    ImageCache['Cookie'] = GetImg('cookie.png')
    ImageCache['Muncher'] = GetImg('muncher.png')
    ImageCache['MuncherF'] = GetImg('muncher_frozen.png')
    ImageCache['Bush00'] = GetImg('bush_green_small.png')
    ImageCache['Bush01'] = GetImg('bush_green_med.png')
    ImageCache['Bush02'] = GetImg('bush_green_large.png')
    ImageCache['Bush03'] = GetImg('bush_green_xlarge.png')
    ImageCache['Bush10'] = GetImg('bush_yellow_small.png')
    ImageCache['Bush11'] = GetImg('bush_yellow_med.png')
    ImageCache['Bush12'] = GetImg('bush_yellow_large.png')
    ImageCache['Bush13'] = GetImg('bush_yellow_xlarge.png')

    doors = {'Door': 'door', 'GhostDoor': 'ghost_door', 'TowerDoor': 'tower_door', 'CastleDoor': 'castle_door', 'BowserDoor': 'bowser_door'}
    transform90 = QtGui.QTransform()
    transform180 = QtGui.QTransform()
    transform270 = QtGui.QTransform()
    transform90.rotate(90)
    transform180.rotate(180)
    transform270.rotate(270)

    for door, filename in doors.items():
        image = GetImg('%s.png' % filename, True)
        ImageCache[door+'U'] = QtGui.QPixmap.fromImage(image)
        ImageCache[door+'R'] = QtGui.QPixmap.fromImage(image.transformed(transform90))
        ImageCache[door+'D'] = QtGui.QPixmap.fromImage(image.transformed(transform180))
        ImageCache[door+'L'] = QtGui.QPixmap.fromImage(image.transformed(transform270))

def LoadMovableItems():
    global ImageCache
    ImageCache['Barrel'] = GetImg('barrel.png')
    ImageCache['OldBarrel'] = GetImg('old_barrel.png')
    ImageCache['POW'] = GetImg('pow.png')
    ImageCache['GlowBlock'] = GetImg('glow_block.png')
    ImageCache['PropellerBlock'] = GetImg('propeller_block.png')
    ImageCache['Spring'] = GetImg('spring.png')

def LoadCannonMulti():
    ImageCache['CannonMultiUR'] = GetImg('cannon_multi_0.png')
    ImageCache['CannonMultiUL'] = GetImg('cannon_multi_1.png')
    ImageCache['CannonMultiDR'] = GetImg('cannon_multi_10.png')
    ImageCache['CannonMultiDL'] = GetImg('cannon_multi_11.png')
    ImageCache['CannonMultiQ'] = GetImg('rced_block.png')

def LoadFlameCannon():
    transform90 = QtGui.QTransform()
    transform180 = QtGui.QTransform()
    transform270 = QtGui.QTransform()
    transform90.rotate(90)
    transform180.rotate(180)
    transform270.rotate(270)

    image = GetImg('continuous_flame_cannon.png', True)
    ImageCache['FlameCannonR'] = QtGui.QPixmap.fromImage(image)
    ImageCache['FlameCannonD'] = QtGui.QPixmap.fromImage(image.transformed(transform90))
    ImageCache['FlameCannonL'] = QtGui.QPixmap.fromImage(image.mirrored(True, False))
    ImageCache['FlameCannonU'] = QtGui.QPixmap.fromImage(image.transformed(transform270).mirrored(True, False))

def LoadPulseFlameCannon():
    global ImageCache

    transform90 = QtGui.QTransform()
    transform180 = QtGui.QTransform()
    transform270 = QtGui.QTransform()
    transform90.rotate(90)
    transform180.rotate(180)
    transform270.rotate(270)

    onImage = GetImg('synchro_flame_jet.png', True)
    ImageCache['PulseFlameCannonR'] = QtGui.QPixmap.fromImage(onImage)
    ImageCache['PulseFlameCannonD'] = QtGui.QPixmap.fromImage(onImage.transformed(transform90))
    ImageCache['PulseFlameCannonL'] = QtGui.QPixmap.fromImage(onImage.mirrored(True, False))
    ImageCache['PulseFlameCannonU'] = QtGui.QPixmap.fromImage(onImage.transformed(transform270).mirrored(True, False))


def LoadRotFlameCannon():
    for i in range(5):
        ImageCache['RotFlameCannon%d' % i] = GetImg('rotating_flame_cannon_%d.png' % i)
        originalImg = GetImg('rotating_flame_cannon_%d.png' % i, True)
        ImageCache['RotFlameCannonFlipped%d' % i] = QtGui.QPixmap.fromImage(originalImg.mirrored(False, True))

def LoadSynchroFlameJet():
    global ImageCache

    transform90 = QtGui.QTransform()
    transform180 = QtGui.QTransform()
    transform270 = QtGui.QTransform()
    transform90.rotate(90)
    transform180.rotate(180)
    transform270.rotate(270)

    onImage = GetImg('synchro_flame_jet.png', True)
    offImage = GetImg('synchro_flame_jet_off.png', True)
    ImageCache['SynchroFlameJetOnR'] = QtGui.QPixmap.fromImage(onImage)
    ImageCache['SynchroFlameJetOnD'] = QtGui.QPixmap.fromImage(onImage.transformed(transform90))
    ImageCache['SynchroFlameJetOnL'] = QtGui.QPixmap.fromImage(onImage.mirrored(True, False))
    ImageCache['SynchroFlameJetOnU'] = QtGui.QPixmap.fromImage(onImage.transformed(transform270).mirrored(True, False))
    ImageCache['SynchroFlameJetOffR'] = QtGui.QPixmap.fromImage(offImage)
    ImageCache['SynchroFlameJetOffD'] = QtGui.QPixmap.fromImage(offImage.transformed(transform90))
    ImageCache['SynchroFlameJetOffL'] = QtGui.QPixmap.fromImage(offImage.mirrored(True, False))
    ImageCache['SynchroFlameJetOffU'] = QtGui.QPixmap.fromImage(offImage.transformed(transform270).mirrored(True, False))


def LoadRotSpotlight():
    global ImageCache
    for i in range(16):
        ImageCache['RotSpotlight%d' % i] = GetImg('rotational_spotlight_%d.png' % i)

def LoadMice():
    for i in range(8):
        ImageCache['LittleMouser%d' % i] = GetImg('little_mouser_%d.png' % i)
        originalImg = GetImg('little_mouser_%d.png' % i, True)
        ImageCache['LittleMouserFlipped%d' % i] = QtGui.QPixmap.fromImage(originalImg.mirrored(True, False))

def LoadCrabs():
    global ImageCache
    ImageCache['Huckit'] = GetImg('huckit_crab.png')
    originalImg = GetImg('huckit_crab.png', True)
    ImageCache['HuckitFlipped'] = QtGui.QPixmap.fromImage(originalImg.mirrored(True, False))

def LoadFireSnake():
    global ImageCache
    ImageCache['FireSnakeWait'] = GetImg('fire_snake_0.png')
    ImageCache['FireSnake'] = GetImg('fire_snake_1.png')

def LoadPolterItems():
    global ImageCache
    if 'GhostHouseStand' not in ImageCache:
        ImageCache['GhostHouseStand'] = GetImg('ghost_house_stand.png')

    ImageCache['PolterStand'] = OverlayPixmaps(ImageCache['GhostHouseStand'], GetImg('polter_stand.png'), 18, 18, 1, 1, 18, 18, 18, 18)
    ImageCache['PolterQBlock'] = OverlayPixmaps(ImageCache['Overrides'][9], GetImg('polter_qblock.png'), 18, 18, 1, 1, 18, 18, 18, 18)

def LoadFlyingBlocks():
    global ImageCache
    for color in ['yellow', 'blue', 'gray', 'red']:
        ImageCache['FlyingQBlock%s' % color] = GetImg('flying_qblock_%s.png' % color)

def LoadPipeBubbles():
    global ImageCache
    transform90 = QtGui.QTransform()
    transform180 = QtGui.QTransform()
    transform270 = QtGui.QTransform()
    transform90.rotate(90)
    transform180.rotate(180)
    transform270.rotate(270)

    for direction in ['U''D''R''L']:
        image = GetImg('pipe_bubbles.png', True)
        ImageCache['PipeBubbles'+'U'] = QtGui.QPixmap.fromImage(image)
        ImageCache['PipeBubbles'+'R'] = QtGui.QPixmap.fromImage(image.transformed(transform90))
        ImageCache['PipeBubbles'+'D'] = QtGui.QPixmap.fromImage(image.transformed(transform180))
        ImageCache['PipeBubbles'+'L'] = QtGui.QPixmap.fromImage(image.transformed(transform270))

def LoadPipeCannon():
    for i in range(7):
        ImageCache['PipeCannon%d' % i] = GetImg('pipe_cannon_%d.png' % i)

def LoadGiantBubble():
    for shape in range(4):
        ImageCache['GiantBubble%d' % shape] = GetImg('giant_bubble_%d.png' % shape)

def LoadMovingChainLink():
    for shape in range(4):
        ImageCache['MovingChainLink%d' % shape] = GetImg('moving_chain_link_%d.png' % shape)

def LoadIceStuff():
    global ImageCache
    ImageCache['IcicleSmall'] = GetImg('icicle_small.png')
    ImageCache['IcicleLarge'] = GetImg('icicle_large.png')
    ImageCache['IcicleSmallS'] = GetImg('icicle_small_static.png')
    ImageCache['IcicleLargeS'] = GetImg('icicle_large_static.png')
    ImageCache['BigIceBlockEmpty'] = GetImg('big_ice_block_empty.png')
    ImageCache['BigIceBlockBobomb'] = GetImg('big_ice_block_bobomb.png')
    ImageCache['BigIceBlockSpikeBall'] = GetImg('big_ice_block_spikeball.png')
    ImageCache['PathIceBlock'] = GetImg('unused_path_ice_block.png')

def LoadMushrooms():
    global ImageCache
    ImageCache['RedShroomL'] = GetImg('red_mushroom_left.png')
    ImageCache['RedShroomM'] = GetImg('red_mushroom_middle.png')
    ImageCache['RedShroomR'] = GetImg('red_mushroom_right.png')
    ImageCache['GreenShroomL'] = GetImg('green_mushroom_left.png')
    ImageCache['GreenShroomM'] = GetImg('green_mushroom_middle.png')
    ImageCache['GreenShroomR'] = GetImg('green_mushroom_right.png')
    ImageCache['BlueShroomL'] = GetImg('blue_mushroom_left.png')
    ImageCache['BlueShroomM'] = GetImg('blue_mushroom_middle.png')
    ImageCache['BlueShroomR'] = GetImg('blue_mushroom_right.png')
    ImageCache['OrangeShroomL'] = GetImg('orange_mushroom_left.png')
    ImageCache['OrangeShroomM'] = GetImg('orange_mushroom_middle.png')
    ImageCache['OrangeShroomR'] = GetImg('orange_mushroom_right.png')

def LoadFlagpole():
    global ImageCache
    ImageCache['MidwayFlag'] = GetImg('midway_flag.png')
    ImageCache['Flagpole'] = GetImg('flagpole.png')
    ImageCache['FlagpoleSecret'] = GetImg('flagpole_secret.png')
    ImageCache['Castle'] = GetImg('castle.png')
    ImageCache['CastleSecret'] = GetImg('castle_secret.png')
    ImageCache['SnowCastle'] = GetImg('snow_castle.png')
    ImageCache['SnowCastleSecret'] = GetImg('snow_castle_secret.png')

def LoadDoomshipStuff():
    global ImageCache
    ImageCache['Wrench'] = GetImg('wrench.png')

def LoadUnusedStuff():
    global ImageCache
    ImageCache['UnusedPlatform'] = GetImg('unused_platform.png')
    ImageCache['UnusedBlockPlatform'] = GetImg('unused_block_platform.png')
    ImageCache['UnusedCastlePlatform'] = GetImg('unused_castle_platform.png')

    # This loop generates all 1-way gate images from a single image
    gate = GetImg('1_way_gate.png', True)
    for flip in (0, 1):
        for direction in range(4):
            if flip:
                newgate = QtGui.QPixmap.fromImage(gate.mirrored(True, False))
            else:
                newgate = QtGui.QPixmap.fromImage(gate)

            width = 24
            height = 60 # constants, from the PNG
            xsize = width if direction in (0, 1) else height
            ysize = width if direction in (2, 3) else height
            if direction == 0:
                rotValue = 0
                xpos = 0
                ypos = 0
            elif direction == 1:
                rotValue = 180
                xpos = -width
                ypos = -height
            elif direction == 2:
                rotValue = 270
                xpos = -width
                ypos = 0
            elif direction == 3:
                rotValue = 90
                xpos = 0
                ypos = -height

            dest = QtGui.QPixmap(xsize, ysize)
            dest.fill(QtGui.QColor.fromRgb(0,0,0,0))
            p = QtGui.QPainter(dest)
            p.rotate(rotValue)
            p.drawPixmap(xpos, ypos, newgate)
            del p

            ImageCache['1WayGate%d%d' % (flip, direction)] = dest


def LoadMinigameStuff():
    global ImageCache
    ImageCache['MGCannon'] = GetImg('mg_cannon.png')
    ImageCache['MGChest'] = GetImg('mg_chest.png')
    ImageCache['MGToad'] = GetImg('toad.png')

def LoadCastleGears():
    global ImageCache
    ImageCache['CastleGearL'] = GetImg('castle_gear_large.png')
    ImageCache['CastleGearS'] = GetImg('castle_gear_small.png')

def LoadBosses():
    global ImageCache
    ImageCache['LarryKoopa'] = GetImg('Larry_Koopa.png')
    ImageCache['LemmyKoopa'] = GetImg('Lemmy_Koopa.png')
    ImageCache['WendyKoopa'] = GetImg('Wendy_Koopa.png')
    ImageCache['MortonKoopa'] = GetImg('Morton_Koopa.png')
    ImageCache['RoyKoopa'] = GetImg('Roy_Koopa.png')
    ImageCache['LudwigVonKoopa'] = GetImg('Ludwig_Von_Koopa.png')
    ImageCache['IggyKoopa'] = GetImg('Iggy_Koopa.png')
    ImageCache['Kamek'] = GetImg('Kamek.png')
    ImageCache['Bowser'] = GetImg('Bowser.png')

# ---- Custom Painters ----
def PaintNothing(sprite, painter):
    pass

def PaintGenericObject(sprite, painter):
    painter.drawPixmap(0, 0, sprite.image)

def PaintAlphaObject(sprite, painter):
    painter.save()
    painter.setOpacity(sprite.alpha)
    painter.drawPixmap(0, 0, sprite.image)
    painter.restore()

def PaintBlock(sprite, painter):
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    if Tiles[sprite.tilenum] != None:
        painter.drawPixmap(0, 0, Tiles[sprite.tilenum].main)
    painter.drawPixmap(0, 0, sprite.image)

def PaintRCEDBlock(sprite, painter):
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    if Tiles[sprite.tilenum] != None:
        painter.drawPixmap(0, 0, Tiles[sprite.tilenum].main)
    painter.drawPixmap(0, 0, sprite.image)
    painter.drawPixmap(0, 0, ImageCache['RCEDBlock'])

def PaintWoodenPlatform(sprite, painter):
    if sprite.colour == 0:
        colour = 'Wooden'
    elif sprite.colour == 1:
        colour = 'Stone'
    elif sprite.colour == 2:
        colour = 'Bone'

    if sprite.xsize > 32:
        painter.drawTiledPixmap(27, 0, ((sprite.xsize * 1.5) - 51), 24, ImageCache[colour + 'PlatformM'])

    if sprite.xsize == 24:
        # replicate glitch effect forced by sprite 50
        painter.drawPixmap(0, 0, ImageCache[colour + 'PlatformR'])
        painter.drawPixmap(8, 0, ImageCache[colour + 'PlatformL'])
    else:
        # normal rendering
        painter.drawPixmap((sprite.xsize - 16) * 1.5, 0, ImageCache[colour + 'PlatformR'])
        painter.drawPixmap(0, 0, ImageCache[colour + 'PlatformL'])

def PaintDragonCoaster(sprite, painter):

    raw_size = sprite.spritedata[5] & 15

    if raw_size == 0 or raw_size == 8:
        # just the head
        painter.drawPixmap(0, 0, ImageCache['DragonHead'])
    elif raw_size == 1:
        # head and tail only
        painter.drawPixmap(48, 0, ImageCache['DragonHead'])
        painter.drawPixmap(0, 0, ImageCache['DragonTail'])
    else:
        painter.drawPixmap((sprite.xsize*1.5)-48, 0, ImageCache['DragonHead'])
        if raw_size > 1:
            painter.drawTiledPixmap(48, 0, (sprite.xsize*1.5)-96, 24, ImageCache['DragonBody'])
        painter.drawPixmap(0, 0, ImageCache['DragonTail'])

def PaintMouser(sprite, painter):
    direction = sprite.spritedata[5] & 0xF

    mouser = ImageCache['Mouser']
    if direction == 1:
        mouser = QtGui.QImage(mouser)
        mouser = QtGui.QPixmap.fromImage(mouser.mirrored(True, False))

    painter.drawTiledPixmap(0, 0, sprite.xsize * 1.5, 24, mouser)

def PaintMoveWhenOn(sprite, painter):
    if sprite.direction == 0:
        direction = 'R'
    elif sprite.direction == 1:
        direction = 'L'
    elif sprite.direction == 2:
        direction = 'U'
    elif sprite.direction == 3:
        direction = 'D'

    raw_size = sprite.spritedata[5] & 0xF

    if raw_size == 0:
        # hack for the glitchy version
        painter.drawPixmap(0, 2, ImageCache['MoveWhenOnR'])
        painter.drawPixmap(24, 2, ImageCache['MoveWhenOnL'])
    elif raw_size == 1:
        painter.drawPixmap(0, 2, ImageCache['MoveWhenOnM'])
    else:
        painter.drawPixmap(0, 2, ImageCache['MoveWhenOnL'])
        if raw_size > 2:
            painter.drawTiledPixmap(24, 2, (raw_size-2)*24, 24, ImageCache['MoveWhenOnM'])
        painter.drawPixmap((sprite.xsize*1.5)-24, 2, ImageCache['MoveWhenOnR'])

    center = (sprite.xsize / 2) * 1.5
    painter.drawPixmap(center - 14, 0, ImageCache['MoveWhenOnC'])
    painter.drawPixmap(center - 12, 1, ImageCache['SmArrow%s' % sprite.direction])

def PaintPlatformGenerator(sprite, painter):
    PaintWoodenPlatform(sprite, painter)
    # todo: add arrows

def PaintDSStoneBlock(sprite, painter):
    middle_width = (sprite.xsize - 32) * 1.5
    middle_height = (sprite.ysize * 1.5) - 16
    bottom_y = (sprite.ysize * 1.5) - 8
    right_x = (sprite.xsize - 16) * 1.5

    painter.drawPixmap(0, 0, ImageCache['DSBlockTopLeft'])
    painter.drawTiledPixmap(24, 0, middle_width, 8, ImageCache['DSBlockTop'])
    painter.drawPixmap(right_x, 0, ImageCache['DSBlockTopRight'])

    painter.drawTiledPixmap(0, 8, 24, middle_height, ImageCache['DSBlockLeft'])
    painter.drawTiledPixmap(right_x, 8, 24, middle_height, ImageCache['DSBlockRight'])

    painter.drawPixmap(0, bottom_y, ImageCache['DSBlockBottomLeft'])
    painter.drawTiledPixmap(24, bottom_y, middle_width, 8, ImageCache['DSBlockBottom'])
    painter.drawPixmap(right_x, bottom_y, ImageCache['DSBlockBottomRight'])

def PaintOldStoneBlock(sprite, painter):
    blockX = 0
    blockY = 0
    type = sprite.type
    width = sprite.xsize*1.5
    height = sprite.ysize*1.5

    if type == 81 or type == 83: # left spikes
        painter.drawTiledPixmap(0, 0, 24, height, ImageCache['SpikeL'])
        blockX = 24
        width -= 24
    if type == 84 or type == 86: # top spikes
        painter.drawTiledPixmap(0, 0, width, 24, ImageCache['SpikeU'])
        blockY = 24
        height -= 24
    if type == 82 or type == 83: # right spikes
        painter.drawTiledPixmap(blockX+width-24, 0, 24, height, ImageCache['SpikeR'])
        width -= 24
    if type == 85 or type == 86: # bottom spikes
        painter.drawTiledPixmap(0, blockY+height-24, width, 24, ImageCache['SpikeD'])
        height -= 24

    column2x = blockX + 24
    column3x = blockX + width - 24
    row2y = blockY + 24
    row3y = blockY + height - 24

    painter.drawPixmap(blockX, blockY, ImageCache['OldStoneTL'])
    painter.drawTiledPixmap(column2x, blockY, width-48, 24, ImageCache['OldStoneT'])
    painter.drawPixmap(column3x, blockY, ImageCache['OldStoneTR'])

    painter.drawTiledPixmap(blockX, row2y, 24, height-48, ImageCache['OldStoneL'])
    painter.drawTiledPixmap(column2x, row2y, width-48, height-48, ImageCache['OldStoneM'])
    painter.drawTiledPixmap(column3x, row2y, 24, height-48, ImageCache['OldStoneR'])

    painter.drawPixmap(blockX, row3y, ImageCache['OldStoneBL'])
    painter.drawTiledPixmap(column2x, row3y, width-48, 24, ImageCache['OldStoneB'])
    painter.drawPixmap(column3x, row3y, ImageCache['OldStoneBR'])

def PaintMushroomPlatform(sprite, painter):
    tilesize = 24 + (sprite.shroomsize * 24)
    if sprite.shroomsize == 0:
        if sprite.colour == 0:
            colour = 'Orange'
        else:
            colour = 'Blue'
    else:
        if sprite.colour == 0:
            colour = 'Red'
        else:
            colour = 'Green'

    painter.drawPixmap(0, 0, ImageCache[colour + 'ShroomL'])
    painter.drawTiledPixmap(tilesize, 0, (sprite.xsize*1.5) - (tilesize * 2), tilesize, ImageCache[colour + 'ShroomM'])
    painter.drawPixmap((sprite.xsize*1.5) - tilesize, 0, ImageCache[colour + 'ShroomR'])

def PaintPurplePole(sprite, painter):
    painter.drawPixmap(0, 0, ImageCache['VertPoleTop'])
    painter.drawTiledPixmap(0, 24, 24, sprite.ysize*1.5 - 48, ImageCache['VertPole'])
    painter.drawPixmap(0, sprite.ysize*1.5 - 24, ImageCache['VertPoleBottom'])

def PaintBlockTrain(sprite, painter):
    endpiece = ImageCache['BlockTrain']
    painter.drawPixmap(0, 0, endpiece)
    painter.drawTiledPixmap(24, 0, sprite.xsize*1.5 - 48, 24, ImageCache['BlockTrain'])
    painter.drawPixmap(sprite.xsize*1.5 - 24, 0, endpiece)

def PaintHorizontalRope(sprite, painter):
    endpiece = ImageCache['HorzRopeEnd']
    painter.drawPixmap(0, 0, endpiece)
    painter.drawTiledPixmap(24, 0, sprite.xsize*1.5 - 48, 24, ImageCache['HorzRope'])
    painter.drawPixmap(sprite.xsize*1.5 - 24, 0, endpiece)

def PaintPokey(sprite, painter):
    painter.drawPixmap(0, 0, ImageCache['PokeyTop'])
    painter.drawTiledPixmap(0, 37, 36, sprite.ysize*1.5 - 61, ImageCache['PokeyMiddle'])
    painter.drawPixmap(0, sprite.ysize*1.5 - 24, ImageCache['PokeyBottom'])

def PaintGiantBubble(sprite, painter):
    if sprite.direction == 0:
        arrow = 'ud'
    else:
        arrow = 'lr'
    xsize = sprite.xsize
    ysize = sprite.ysize

    painter.drawPixmap(0, 0, ImageCache['GiantBubble%d' % sprite.shape])

def PaintMovingChainLink(sprite, painter):
    if sprite.direction == 0:
        arrow = 'ud'
    else:
        arrow = 'lr'
    xsize = sprite.xsize
    ysize = sprite.ysize

    painter.drawPixmap(0, 0, ImageCache['MovingChainLink%d' % sprite.shape])

def PaintColouredBox(sprite, painter):
    prefix = 'CBox%d' % sprite.colour
    xsize = sprite.xsize*1.5
    ysize = sprite.ysize*1.5

    painter.drawPixmap(0, 0, ImageCache[prefix+'TL'])
    painter.drawPixmap(xsize-25, 0, ImageCache[prefix+'TR'])
    painter.drawPixmap(0, ysize-25, ImageCache[prefix+'BL'])
    painter.drawPixmap(xsize-25, ysize-25, ImageCache[prefix+'BR'])

    painter.drawTiledPixmap(25, 0, xsize-50, 25, ImageCache[prefix+'T'])
    painter.drawTiledPixmap(25, ysize-25, xsize-50, 25, ImageCache[prefix+'B'])
    painter.drawTiledPixmap(0, 25, 25, ysize-50, ImageCache[prefix+'L'])
    painter.drawTiledPixmap(xsize-25, 25, 25, ysize-50, ImageCache[prefix+'R'])

    painter.drawTiledPixmap(25, 25, xsize-50, ysize-50, ImageCache[prefix+'M'])

def PaintGhostHouseBox(sprite, painter):
    prefix = 'GHBox'
    xsize = sprite.xsize*1.5
    ysize = sprite.ysize*1.5

    painter.drawPixmap(0, 0, ImageCache[prefix+'TL'])
    painter.drawPixmap(xsize-24, 0, ImageCache[prefix+'TR'])
    painter.drawPixmap(0, ysize-24, ImageCache[prefix+'BL'])
    painter.drawPixmap(xsize-24, ysize-24, ImageCache[prefix+'BR'])

    painter.drawTiledPixmap(24, 0, xsize-48, 24, ImageCache[prefix+'T'])
    painter.drawTiledPixmap(24, ysize-24, xsize-48, 24, ImageCache[prefix+'B'])
    painter.drawTiledPixmap(0, 24, 24, ysize-48, ImageCache[prefix+'L'])
    painter.drawTiledPixmap(xsize-24, 24, 24, ysize-48, ImageCache[prefix+'R'])

    painter.drawTiledPixmap(24, 24, xsize-48, ysize-48, ImageCache[prefix+'M'])

def PaintBoltBox(sprite, painter):
    xsize = sprite.xsize*1.5
    ysize = sprite.ysize*1.5

    painter.drawPixmap(0, 0, ImageCache['BoltBoxTL'])
    painter.drawTiledPixmap(24, 0, xsize-48, 24, ImageCache['BoltBoxT'])
    painter.drawPixmap(xsize-24, 0, ImageCache['BoltBoxTR'])

    painter.drawTiledPixmap(0, 24, 24, ysize-48, ImageCache['BoltBoxL'])
    painter.drawTiledPixmap(24, 24, xsize-48, ysize-48, ImageCache['BoltBoxM'])
    painter.drawTiledPixmap(xsize-24, 24, 24, ysize-48, ImageCache['BoltBoxR'])

    painter.drawPixmap(0, ysize-24, ImageCache['BoltBoxBL'])
    painter.drawTiledPixmap(24, ysize-24, xsize-48, 24, ImageCache['BoltBoxB'])
    painter.drawPixmap(xsize-24, ysize-24, ImageCache['BoltBoxBR'])

def PaintLiftDokan(sprite, painter):
    painter.drawPixmap(0, 0, ImageCache['LiftDokanT'])
    painter.drawTiledPixmap(12, 143, 52, 579, ImageCache['LiftDokanM'])

def PaintScrewMushroom(sprite, painter):
    y = 0
    if sprite.type == 172: # with bolt
        painter.drawPixmap(70, 0, ImageCache['Bolt'])
        y += 24
    painter.drawPixmap(0, y, ImageCache['ScrewShroomT'])
    painter.drawTiledPixmap(76, y+93, 31, 172, ImageCache['ScrewShroomM'])
    painter.drawPixmap(76, y+253, ImageCache['ScrewShroomB'])

def PaintScalePlatform(sprite, painter):
    # this is FUN!! (not)
    ropeLeft = sprite.ropeLengthLeft * 24 + 4
    if sprite.ropeLengthLeft == 0: ropeLeft += 12

    ropeRight = sprite.ropeLengthRight * 24 + 4
    if sprite.ropeLengthRight == 0: ropeRight += 12

    ropeWidth = sprite.ropeWidth * 24 + 8
    platformWidth = (sprite.platformWidth + 3) * 24

    ropeX = platformWidth / 2 - 4

    painter.drawTiledPixmap(ropeX + 8, 0, ropeWidth - 16, 8, ImageCache['ScaleRopeH'])

    ropeVertImage = ImageCache['ScaleRopeV']
    painter.drawTiledPixmap(ropeX, 8, 8, ropeLeft - 8, ropeVertImage)
    painter.drawTiledPixmap(ropeX + ropeWidth - 8, 8, 8, ropeRight - 8, ropeVertImage)

    pulleyImage = ImageCache['ScalePulley']
    painter.drawPixmap(ropeX, 0, pulleyImage)
    painter.drawPixmap(ropeX + ropeWidth - 20, 0, pulleyImage)

    platforms = [(0, ropeLeft), (ropeX+ropeWidth-(platformWidth/2)-4, ropeRight)]
    for x,y in platforms:
        painter.drawPixmap(x, y, ImageCache['WoodenPlatformL'])
        painter.drawTiledPixmap(x + 27, y, (platformWidth - 51), 24, ImageCache['WoodenPlatformM'])
        painter.drawPixmap(x + platformWidth - 24, y, ImageCache['WoodenPlatformR'])

def PaintBulletBillLauncher(sprite, painter):
    painter.drawPixmap(0, 0, ImageCache['BBLauncherT'])
    painter.drawTiledPixmap(0, 48, 24, sprite.ysize*1.5 - 48, ImageCache['BBLauncherM'])

def PaintWiggleShroom(sprite, painter):
    xsize = sprite.xsize * 1.5
    painter.drawPixmap(0, 0, ImageCache['WiggleShroomL'])
    painter.drawTiledPixmap(18, 0, xsize-36, 24, ImageCache['WiggleShroomM'])
    painter.drawPixmap(xsize-18, 0, ImageCache['WiggleShroomR'])
    painter.drawTiledPixmap(xsize / 2 - 12, 24, 24, sprite.ysize * 1.5 - 24, ImageCache['WiggleShroomS'])

def PaintExtendShroom(sprite, painter):
    painter.drawPixmap(0, 0, sprite.image)
    painter.drawTiledPixmap((sprite.xsize * 1.5) / 2 - 14, 48, 28, sprite.ysize * 1.5 - 48, ImageCache['ExtendShroomStem'])

def PaintBoltPlatform(sprite, painter):
    painter.drawPixmap(0, 0, ImageCache['BoltPlatformL'])
    painter.drawTiledPixmap(24, 3, sprite.xsize*1.5 - 48, 24, ImageCache['BoltPlatformM'])
    painter.drawPixmap(sprite.xsize*1.5 - 24, 0, ImageCache['BoltPlatformR'])

def PaintBrownBlock(sprite, painter):
    blockX = 0
    blockY = 0
    type = sprite.type
    width = sprite.xsize*1.5
    height = sprite.ysize*1.5

    column2x = blockX + 24
    column3x = blockX + width - 24
    row2y = blockY + 24
    row3y = blockY + height - 24

    painter.drawPixmap(blockX, blockY, ImageCache['BrownBlockTL'])
    painter.drawTiledPixmap(column2x, blockY, width-48, 24, ImageCache['BrownBlockTM'])
    painter.drawPixmap(column3x, blockY, ImageCache['BrownBlockTR'])

    painter.drawTiledPixmap(blockX, row2y, 24, height-48, ImageCache['BrownBlockML'])
    painter.drawTiledPixmap(column2x, row2y, width-48, height-48, ImageCache['BrownBlockMM'])
    painter.drawTiledPixmap(column3x, row2y, 24, height-48, ImageCache['BrownBlockMR'])

    painter.drawPixmap(blockX, row3y, ImageCache['BrownBlockBL'])
    painter.drawTiledPixmap(column2x, row3y, width-48, 24, ImageCache['BrownBlockBM'])
    painter.drawPixmap(column3x, row3y, ImageCache['BrownBlockBR'])

def PaintUnusedBlockPlatform(sprite, painter):
    pixmap = ImageCache['UnusedBlockPlatform'].scaled(sprite.xsize*3/2, sprite.ysize*3/2)
    painter.drawPixmap(0, 0, pixmap)

def PaintSpikedStake(sprite, painter):
    if sprite.type == 137:
        dir = 'down'
    elif sprite.type == 140:
        dir = 'up'
    elif sprite.type == 141:
        dir = 'right'
    elif sprite.type == 142:
        dir = 'left'

    color = sprite.spritedata[3] & 15
    if color == 2 or color == 3 or color == 7:
        mid = ImageCache['StakeM1'+dir]
        end = ImageCache['StakeE1'+dir]
    else:
        mid = ImageCache['StakeM0'+dir]
        end = ImageCache['StakeE0'+dir]

    tiles = 16
    tilesize = 37
    endsize = 41
    width = 100

    if dir == 'up':
        painter.drawPixmap(0, 0, end)
        painter.drawTiledPixmap(0, endsize, width, tilesize*tiles, mid)
    elif dir == 'down':
        painter.drawTiledPixmap(0, 0, width, tilesize*tiles, mid)
        painter.drawPixmap(0, (sprite.ysize*1.5)-endsize, end)
    elif dir == 'left':
        painter.drawPixmap(0, 0, end)
        painter.drawTiledPixmap(endsize, 0, tilesize*tiles, width, mid)
    elif dir == 'right':
        painter.drawTiledPixmap(0, 0, tilesize*tiles, width, mid)
        painter.drawPixmap((sprite.xsize*1.5)-endsize, 0, end)

def PaintRotBulletLauncher(sprite, painter): # 136
    pieces = (sprite.spritedata[3] & 15) + 1
    pivot1_4 = sprite.spritedata[4] & 15
    pivot5_8 = sprite.spritedata[4] >> 4
    startleft1_4 = sprite.spritedata[5] & 15
    startleft5_8 = sprite.spritedata[5] >> 4

    pivots = [pivot1_4,pivot5_8]
    startleft = [startleft1_4,startleft5_8]

    ysize = sprite.ysize * 1.5

    for piece in range(pieces):
        bitpos = 2**(piece%4)
        if pivots[piece/4] & bitpos:
            painter.drawPixmap(5,ysize-piece*24-24,ImageCache['RotLauncherPivot'])
        else:
            xo = 6
            image = ImageCache['RotLauncherCannon']
            if startleft[piece/4] & bitpos:
                transform = QtGui.QTransform()
                transform.rotate(180)
                image = QtGui.QPixmap(image.transformed(transform))
                xo = 0
            painter.drawPixmap(xo,ysize-(piece+1)*24,image)

def PaintPipe(sprite, painter):
    colour = sprite.colour
    xsize = sprite.xsize*1.5
    ysize = sprite.ysize*1.5

    if not sprite.moving:
        # Static pipes
        if sprite.orientation == 'V': # vertical
            if sprite.direction == 'U':
                painter.drawPixmap(0, 0, ImageCache['PipeTop%d' % colour])
                painter.drawTiledPixmap(0, 24, 48, ysize-24, ImageCache['PipeMiddle%d' % colour])
            else:
                painter.drawTiledPixmap(0, 0, 48, ysize-24, ImageCache['PipeMiddle%d' % colour])
                painter.drawPixmap(0, ysize-24, ImageCache['PipeBottom%d' % colour])
        else: # horizontal
            if sprite.direction == 'L':
                painter.drawPixmap(0, 0, ImageCache['PipeLeft%d' % colour])
                painter.drawTiledPixmap(24, 0, xsize-24, 48, ImageCache['PipeCenter%d' % colour])
            else:
                painter.drawTiledPixmap(0, 0, xsize-24, 48, ImageCache['PipeCenter%d' % colour])
                painter.drawPixmap(xsize-24, 0, ImageCache['PipeRight%d' % colour])
    else:
        # Moving pipes
        length1 = sprite.length1*1.5
        length2 = sprite.length2*1.5
        low = min(length1, length2)
        high = max(length1, length2)

        if sprite.direction == 'U':
            y1 = ysize - low
            y2 = ysize - high

            # draw semi transparent pipe
            painter.save()
            painter.setOpacity(0.5)
            painter.drawPixmap(0, y2, ImageCache['PipeTop%d' % colour])
            painter.drawTiledPixmap(0, y2+24, 48, high-24, ImageCache['PipeMiddle%d' % colour])
            painter.restore()

            # draw opaque pipe
            painter.drawPixmap(0, y1, ImageCache['PipeTop%d' % colour])
            painter.drawTiledPixmap(0, y1+24, 48, low-24, ImageCache['PipeMiddle%d' % colour])

        else:
            # draw semi transparent pipe
            painter.save()
            painter.setOpacity(0.5)
            painter.drawTiledPixmap(0, 0, 48, high-24, ImageCache['PipeMiddle%d' % colour])
            painter.drawPixmap(0, high-24, ImageCache['PipeBottom%d' % colour])
            painter.restore()

            # draw opaque pipe
            painter.drawTiledPixmap(0, 0, 48, low-24, ImageCache['PipeMiddle%d' % colour])
            painter.drawPixmap(0, low-24, ImageCache['PipeBottom%d' % colour])


# ---- Real View Painters ----
def RealViewOutdoorsFogZone(sprite, painter, zoneRect, viewRect): # 64

    # (0, 0) is the top-left corner of the zone

    # Get the width and height of the zone
    zx = zoneRect.topLeft().x()
    zy = zoneRect.topLeft().y()
    zw = zoneRect.width()
    zh = zoneRect.height()

    # Get the y pos of the sprite
    sy = sprite.objy

    # Get pixmaps
    mid = ImageCache['OutdoorsFog']

    paintLiquid(painter, None, mid, None, None, zx, zy, zw, zh, sy, False, 0)

    
def RealViewSunlight(sprite, painter, zoneRect, viewRect): # 110

    # (0, 0) is the top-left corner of the zone
    ImageW = ImageCache['Sunlight'].width()
    ImageH = ImageCache['Sunlight'].height()

    x = viewRect.topRight().x() - zoneRect.topLeft().x() - ImageW
    y = viewRect.topRight().y() - zoneRect.topRight().y()

    if x < 4: x = 4
    if y < 4: y = 4
    if x > zoneRect.topRight().x() - zoneRect.topLeft().x() - ImageW - 4:
        x = zoneRect.topRight().x() - zoneRect.topLeft().x() - ImageW - 4
    if y > zoneRect.bottomLeft().y() - zoneRect.topLeft().y() - ImageH - 4:
        y = zoneRect.bottomLeft().y() - zoneRect.topLeft().y() - ImageH - 4

    painter.drawPixmap(x, y, ImageCache['Sunlight'])


def RealViewWaterZone(sprite, painter, zoneRect, viewRect): # 138

    # (0, 0) is the top-left corner of the zone

    drawCrest = sprite.spritedata[4] & 15 == 0
    RH = (sprite.spritedata[3] & 0xF) << 4
    RH |= sprite.spritedata[4] >> 4
    risingHeight = RH

    # Get the width and height of the zone
    zx = zoneRect.topLeft().x()
    zy = zoneRect.topLeft().y()
    zw = zoneRect.width()
    zh = zoneRect.height()

    # Get the y pos of the sprite
    sy = sprite.objy

    # Get pixmaps
    mid = ImageCache['LiquidWater']
    crest = ImageCache['LiquidWaterCrest']
    rise = ImageCache['LiquidWaterRiseCrest']
    riseCrestless = ImageCache['LiquidWaterRise']

    paintLiquid(painter, crest, mid, rise, riseCrestless, zx, zy, zw, zh, sy, drawCrest, risingHeight)


def RealViewLavaZone(sprite, painter, zoneRect, viewRect): # 139

    # (0, 0) is the top-left corner of the zone

    drawCrest = sprite.spritedata[4] & 15 == 0
    RH = (sprite.spritedata[3] & 0xF) << 4
    RH |= sprite.spritedata[4] >> 4
    fall = (sprite.spritedata[2] >> 4) > 7
    if fall: RH -= 2*RH # make it negative
    risingHeight = RH

    # Get the width and height of the zone
    zx = zoneRect.topLeft().x()
    zy = zoneRect.topLeft().y()
    zw = zoneRect.width()
    zh = zoneRect.height()

    # Get the y pos of the sprite
    sy = sprite.objy

    # Get pixmaps
    mid = ImageCache['LiquidLava']
    crest = ImageCache['LiquidLavaCrest']
    rise = ImageCache['LiquidLavaRiseCrest']
    riseCrestless = ImageCache['LiquidLavaRise']

    paintLiquid(painter, crest, mid, rise, riseCrestless, zx, zy, zw, zh, sy, drawCrest, risingHeight)


def RealViewPoisonZone(sprite, painter, zoneRect, viewRect): # 216

    # (0, 0) is the top-left corner of the zone

    drawCrest = sprite.spritedata[4] & 15 == 0
    RH = (sprite.spritedata[3] & 0xF) << 4
    RH |= sprite.spritedata[4] >> 4
    fall = (sprite.spritedata[2] >> 4) > 7
    if fall: RH -= 2*RH # make it negative
    risingHeight = RH

    # Get the width and height of the zone
    zx = zoneRect.topLeft().x()
    zy = zoneRect.topLeft().y()
    zw = zoneRect.width()
    zh = zoneRect.height()

    # Get the y pos of the sprite
    sy = sprite.objy

    # Get pixmaps
    mid = ImageCache['LiquidPoison']
    crest = ImageCache['LiquidPoisonCrest']
    rise = ImageCache['LiquidPoisonRiseCrest']
    riseCrestless = ImageCache['LiquidPoisonRise']

    paintLiquid(painter, crest, mid, rise, riseCrestless, zx, zy, zw, zh, sy, drawCrest, risingHeight)


def RealViewBubbleGen(sprite, painter, zoneRect, viewRect): # 314
    # Constants (change these if you want)
    bubbleFrequency = .01
    bubbleEccentricityX = 16
    bubbleEccentricityY = 48

    size = sprite.spritedata[5] & 0xF
    if size > 3: return

    Image = ImageCache['BubbleGenEffect']

    if size == 0: pct = 50.0
    elif size == 1: pct = 60.0
    elif size == 2: pct = 80.0
    else: pct = 70.0
    Image = Image.scaledToWidth(int(Image.width() * pct / 100))

    distanceFromTop = (sprite.objy * 1.5) - zoneRect.topLeft().y()
    random.seed(distanceFromTop + sprite.objx) # looks ridiculous without this

    coords = []
    numOfBubbles = int(distanceFromTop * bubbleFrequency)
    for num in range(numOfBubbles):
        xmod = (random.random() * 2 * bubbleEccentricityX) - bubbleEccentricityX
        ymod = (random.random() * 2 * bubbleEccentricityY) - bubbleEccentricityY
        x = ((sprite.objx * 1.5) - zoneRect.topLeft().x()) + xmod + 12 - (Image.width() / 2.0)
        y = ((num * 1.0 / numOfBubbles) * distanceFromTop) + ymod
        if not (0 < y < sprite.objy * 1.5): continue
        coords.append([x, y])

    for x, y in coords:
        painter.drawPixmap(x, y, Image)


def RealViewLavaParticlesZone(sprite, painter, zoneRect, viewRect): # 358

    # (0, 0) is the top-left corner of the zone

    type = sprite.spritedata[5] & 15

    # Get the width and height of the zone
    zx = zoneRect.topLeft().x()
    zy = zoneRect.topLeft().y()
    zw = zoneRect.width()
    zh = zoneRect.height()

    # Get pixmaps
    midA = ImageCache['LavaParticlesA']
    midB = ImageCache['LavaParticlesB']
    midC = ImageCache['LavaParticlesC']

    # Pick one
    mid = midA
    if type == 1: mid = midB
    elif type == 2: mid = midC

    paintLiquid(painter, None, mid, None, None, zx, zy, zw, zh, 0, False, 0)


def RealViewSnowWindZone(sprite, painter, zoneRect, viewRect): # 374

    # (0, 0) is the top-left corner of the zone

    # For now, we only paint snow
    if sprite.spritedata[5] & 1: return

    # Get the width and height of the zone
    zx = zoneRect.topLeft().x()
    zy = zoneRect.topLeft().y()
    zw = zoneRect.width()
    zh = zoneRect.height()

    # Get the pixmap
    mid = ImageCache['SnowEffect']

    paintLiquid(painter, None, mid, None, None, zx, zy, zw, zh, 0, False, 0)


def RealViewGhostFogZone(sprite, painter, zoneRect, viewRect): # 435

    # (0, 0) is the top-left corner of the zone

    # Get the width and height of the zone
    zx = zoneRect.topLeft().x()
    zy = zoneRect.topLeft().y()
    zw = zoneRect.width()
    zh = zoneRect.height()

    # Get the y pos of the sprite
    sy = sprite.objy

    # Get pixmaps
    mid = ImageCache['GhostFog']

    paintLiquid(painter, None, mid, None, None, zx, zy, zw, zh, sy, False, 0)


def paintLiquid(painter, crest, mid, rise, riseCrestless, zx, zy, zw, zh, top, drawCrest, risingHeight):
    """Helper function to paint generic liquids"""

    drawRise = risingHeight != 0

    # Get positions
    offsetFromTop = (top * 1.5) - zy
    if offsetFromTop <= 4:
        offsetFromTop = 4
        drawCrest = False # off the top of the zone; no crest
    if top > (zy + zh) / 1.5:
        # the sprite is below the zone; don't draw anything
        return

    # If all that fits in the zone is some of the crest, determine how much
    if drawCrest:
        crestSizeRemoval = (zy + offsetFromTop + crest.height()) - (zy + zh) + 4
        if crestSizeRemoval < 0: crestSizeRemoval = 0
        crestHeight = crest.height() - crestSizeRemoval

    # Determine where to put the rise image
    offsetRise = offsetFromTop - (risingHeight * 24)
    riseToDraw = rise
    if offsetRise < 4: # close enough to the top zone border
        offsetRise = 4
        riseToDraw = riseCrestless
    if not drawCrest:
        riseToDraw = riseCrestless

    if drawCrest:
        painter.drawTiledPixmap(4, offsetFromTop, zw-8, crestHeight, crest)
        painter.drawTiledPixmap(4, offsetFromTop + crestHeight, zw-8, zh-crestHeight-offsetFromTop-4, mid)
    else:
        painter.drawTiledPixmap(4, offsetFromTop, zw-8, zh-offsetFromTop-4, mid)
    if drawRise:
        painter.drawTiledPixmap(4, offsetRise, zw-8, riseToDraw.height(), riseToDraw)


# ---- Overlay Pixmaps Function ----

def OverlayPixmaps(bottom, top, xOffset = 0, yOffset = 0, opacityB = 1, opacityT = 1, extTop = 0, extBottom = 0, extLeft = 0, extRight = 0):
    """Overlays one QPixmap on top of another. Returns a QPixmap, or None if errors occur."""
    # There are a lot of arguments, so here's an explanation:
    # bottom, top: The QPixmaps to be used
    # xOffset, yOffset: The amount the top pixmap should be offset BEFORE bottom pixmap extention.
    # opacityB, opacityT: The opacity (float 0-1) of each layer
    # extTop, extBottom, extLeft, extRight: The amount (in pixels) for each side of the bottom pixmap to be
    #    extended prior to adding the top pixmap.

    # Check for obvious argument problems
    if opacityB > 1 or opacityT > 1 or opacityB < 0 or opacityT < 0:
        return None

    # Put the entire thing into a try... except clause in order to catch any errors
    try:
        # Create a pixmap with the correct dimensions as specified by the ext args and the original image
        w = QtGui.QPixmap(bottom.width()+extLeft+extRight, bottom.height()+extTop+extBottom)
        w.fill(QtGui.QColor.fromRgb(0,0,0,0))

        # Create the painter
        p = QtGui.QPainter(w)

        # Paint the bottom pixmap onto w using opacityB and the extention arguments
        p.setOpacity(opacityB)
        p.drawPixmap(extLeft, extTop, bottom)

        # Paint the top pixmap onto w using opacityT and the offset arguments
        p.setOpacity(opacityT)
        p.drawPixmap(xOffset-extLeft, yOffset-extTop, top)

        # Destroy the painter (leaving this line out causes errors later)
        del p
    except:
        # An error occured somewhere
        return None

    # Return the result
    return w
