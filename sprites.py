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

Outlinecolor = None
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
    global Outlinecolor, OutlinePen, OutlineBrush, ImageCache, SpritesFolders
    Outlinecolor = theme.color('smi')
    OutlinePen = QtGui.QPen(Outlinecolor, 4)
    OutlineBrush = QtGui.QBrush(Outlinecolor)
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
        'Outlinecolor',
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
        20: SpriteImage_Goomba,
        21: SpriteImage_Paragoomba,
        23: SpriteImage_HorzMovingPlatform,
        24: SpriteImage_BuzzyBeetle,
        25: SpriteImage_Spiny,
        26: SpriteImage_UpsideDownSpiny,
        27: SpriteImage_DSStoneBlock_Vert,
        28: SpriteImage_DSStoneBlock_Horz,
        30: SpriteImage_OldStoneBlock_NoSpikes,
        31: SpriteImage_VertMovingPlatform,
        32: SpriteImage_StarCoinRegular,
        40: SpriteImage_QuestionSwitch,
        41: SpriteImage_PSwitch,
        42: SpriteImage_ExcSwitch,
        43: SpriteImage_QuestionSwitchBlock,
        44: SpriteImage_PSwitchBlock,
        45: SpriteImage_ExcSwitchBlock,
        46: SpriteImage_Podoboo,
        47: SpriteImage_Thwomp,
        48: SpriteImage_GiantThwomp,
        49: SpriteImage_UnusedSeesaw,
        50: SpriteImage_FallingPlatform,
        51: SpriteImage_TiltingGirder,
        52: SpriteImage_UnusedRotPlatforms,
        54: SpriteImage_Lakitu,
        55: SpriteImage_UnusedRisingSeesaw,
        56: SpriteImage_RisingTiltGirder,
        57: SpriteImage_KoopaTroopa,
        58: SpriteImage_KoopaParatroopa,
        59: SpriteImage_LineTiltGirder,
        60: SpriteImage_SpikeTop,
        61: SpriteImage_BigBoo,
        63: SpriteImage_SpikeBall,
        64: SpriteImage_OutdoorsFog,
        65: SpriteImage_PipePiranhaUp,
        66: SpriteImage_PipePiranhaDown,
        67: SpriteImage_PipePiranhaRight,
        68: SpriteImage_PipePiranhaLeft,
        69: SpriteImage_PipeFiretrapUp,
        70: SpriteImage_PipeFiretrapDown,
        71: SpriteImage_PipeFiretrapRight,
        72: SpriteImage_PipeFiretrapLeft,
        73: SpriteImage_GroundPiranha,
        74: SpriteImage_BigGroundPiranha,
        75: SpriteImage_GroundFiretrap,
        76: SpriteImage_BigGroundFiretrap,
        77: SpriteImage_ShipKey,
        78: SpriteImage_CloudTrampoline,
        80: SpriteImage_FireBro,
        81: SpriteImage_OldStoneBlock_SpikesLeft,
        82: SpriteImage_OldStoneBlock_SpikesRight,
        83: SpriteImage_OldStoneBlock_SpikesLeftRight,
        84: SpriteImage_OldStoneBlock_SpikesTop,
        85: SpriteImage_OldStoneBlock_SpikesBottom,
        86: SpriteImage_OldStoneBlock_SpikesTopBottom,
        87: SpriteImage_TrampolineWall,
        92: SpriteImage_BulletBillLauncher,
        93: SpriteImage_BanzaiBillLauncher,
        94: SpriteImage_BoomerangBro,
        95: SpriteImage_HammerBroNormal,
        96: SpriteImage_RotationControllerSwaying,
        97: SpriteImage_RotationControlledSolidBetaPlatform,
        98: SpriteImage_GiantSpikeBall,
        100: SpriteImage_Swooper,
        101: SpriteImage_Bobomb,
        102: SpriteImage_Broozer,
        103: SpriteImage_PlatformGenerator,
        104: SpriteImage_AmpNormal,
        105: SpriteImage_Pokey,
        106: SpriteImage_LinePlatform,
        107: SpriteImage_RotationControlledPassBetaPlatform,
        108: SpriteImage_AmpLine,
        109: SpriteImage_ChainBall,
        110: SpriteImage_Sunlight,
        111: SpriteImage_Blooper,
        112: SpriteImage_BlooperBabies,
        113: SpriteImage_Flagpole,
        114: SpriteImage_FlameCannon,
        115: SpriteImage_Cheep,
        117: SpriteImage_PulseFlameCannon,
        118: SpriteImage_DryBones,
        119: SpriteImage_GiantDryBones,
        120: SpriteImage_SledgeBro,
        122: SpriteImage_OneWayPlatform,
        123: SpriteImage_UnusedCastlePlatform,
        125: SpriteImage_FenceKoopaHorz,
        126: SpriteImage_FenceKoopaVert,
        127: SpriteImage_FlipFence,
        128: SpriteImage_FlipFenceLong,
        129: SpriteImage_4Spinner,
        130: SpriteImage_Wiggler,
        131: SpriteImage_Boo,
        132: SpriteImage_UnusedBlockPlatform,
        133: SpriteImage_StalagmitePlatform,
        134: SpriteImage_Crow,
        135: SpriteImage_HangingPlatform,
        137: SpriteImage_SpikedStakeDown,
        138: SpriteImage_Water,
        139: SpriteImage_Lava,
        140: SpriteImage_SpikedStakeUp,
        141: SpriteImage_SpikedStakeRight,
        142: SpriteImage_SpikedStakeLeft,
        143: SpriteImage_Arrow,
        144: SpriteImage_RedCoin,
        145: SpriteImage_FloatingBarrel,
        146: SpriteImage_ChainChomp,
        147: SpriteImage_Coin,
        148: SpriteImage_Spring,
        149: SpriteImage_RotationControllerSpinning,
        151: SpriteImage_Puffer,
        155: SpriteImage_StarCoinLineControlled,
        156: SpriteImage_RedCoinRing,
        157: SpriteImage_BigBrick,
        158: SpriteImage_FireSnake,
        160: SpriteImage_UnusedBlockPlatform,
        161: SpriteImage_PipeBubbles,
        166: SpriteImage_BlockTrain,
        170: SpriteImage_ChestnutGoomba,
        171: SpriteImage_PowerupBubble,
        172: SpriteImage_ScrewMushroomWithBolt,
        173: SpriteImage_GiantFloatingLog,
        174: SpriteImage_OneWayGate,
        175: SpriteImage_FlyingQBlock,
        176: SpriteImage_RouletteBlock,
        177: SpriteImage_FireChomp,
        178: SpriteImage_ScalePlatform,
        179: SpriteImage_SpecialExit,
        180: SpriteImage_CheepChomp,
        182: SpriteImage_EventDoor,
        185: SpriteImage_ToadBalloon,
        187: SpriteImage_PlayerBlock,
        188: SpriteImage_MidwayPoint,
        189: SpriteImage_LarryKoopa,
        190: SpriteImage_TiltingGirderUnused,
        191: SpriteImage_TileEvent,
        193: SpriteImage_Urchin,
        194: SpriteImage_MegaUrchin,
        195: SpriteImage_HuckitCrab,
        196: SpriteImage_Fishbones,
        197: SpriteImage_Clam,
        198: SpriteImage_Giantgoomba,
        199: SpriteImage_Megagoomba,
        200: SpriteImage_Microgoomba,
        201: SpriteImage_Icicle,
        202: SpriteImage_MGCannon,
        203: SpriteImage_MGChest,
        205: SpriteImage_GiantBubble,
        206: SpriteImage_Zoom,
        207: SpriteImage_QBlock,
        208: SpriteImage_QBlockUnused,
        209: SpriteImage_BrickBlock,
        212: SpriteImage_RollingHill,
        214: SpriteImage_FreefallPlatform,
        216: SpriteImage_Poison,
        219: SpriteImage_LineBlock,
        221: SpriteImage_InvisibleBlock,
        222: SpriteImage_ConveyorSpike,
        223: SpriteImage_SpringBlock,
        224: SpriteImage_JumboRay,
        227: SpriteImage_PipeCannon,
        228: SpriteImage_ExtendShroom,
        229: SpriteImage_SandPillar,
        230: SpriteImage_Bramball,
        231: SpriteImage_WiggleShroom,
        232: SpriteImage_MechaKoopa,
        233: SpriteImage_Bulber,
        237: SpriteImage_PCoin,
        238: SpriteImage_Foo,
        240: SpriteImage_GiantWiggler,
        242: SpriteImage_FallingLedgeBar,
        #252: SpriteImage_RotControlledBlock,
        253: SpriteImage_RotControlledCoin,
        255: SpriteImage_RotatingQBlock,
        256: SpriteImage_RotatingBrickBlock,
        259: SpriteImage_RegularDoor,
        262: SpriteImage_PoltergeistItem,
        263: SpriteImage_WaterPiranha,
        264: SpriteImage_WalkingPiranha,
        265: SpriteImage_FallingIcicle,
        266: SpriteImage_RotatingChainLink,
        267: SpriteImage_TiltGrate,
        268: SpriteImage_LavaGeyser,
        269: SpriteImage_Parabomb,
        271: SpriteImage_Mouser,
        272: SpriteImage_IceBro,
        274: SpriteImage_CastleGear,
        275: SpriteImage_FiveEnemyRaft,
        276: SpriteImage_GhostDoor,
        277: SpriteImage_TowerDoor,
        278: SpriteImage_CastleDoor,
        280: SpriteImage_GiantIceBlock,
        286: SpriteImage_WoodCircle,
        287: SpriteImage_PathIceBlock,
        288: SpriteImage_OldBarrel,
        289: SpriteImage_Box,
        291: SpriteImage_Parabeetle,
        292: SpriteImage_HeavyParabeetle,
        294: SpriteImage_IceCube,
        295: SpriteImage_NutPlatform,
        296: SpriteImage_MegaBuzzy,
        297: SpriteImage_DragonCoaster,
        299: SpriteImage_CannonMulti,
        300: SpriteImage_RotCannon,
        301: SpriteImage_RotCannonPipe,
        303: SpriteImage_MontyMole,
        304: SpriteImage_RotFlameCannon,
        305: SpriteImage_LightCircle,
        306: SpriteImage_RotSpotlight,
        308: SpriteImage_HammerBroPlatform,
        309: SpriteImage_SynchroFlameJet,
        310: SpriteImage_ArrowSign,
        311: SpriteImage_MegaIcicle,
        314: SpriteImage_BubbleGen,
        315: SpriteImage_Bolt,
        316: SpriteImage_BoltBox,
        318: SpriteImage_BoxGenerator,
        321: SpriteImage_ArrowBlock,
        323: SpriteImage_BooCircle,
        325: SpriteImage_GhostHouseStand,
        326: SpriteImage_KingBill,
        327: SpriteImage_LinePlatformBolt,
        330: SpriteImage_RopeLadder,
        331: SpriteImage_DishPlatform,
        333: SpriteImage_PlayerBlockPlatform,
        334: SpriteImage_CheepGiant,
        336: SpriteImage_WendyKoopa,
        337: SpriteImage_IggyKoopa,
        339: SpriteImage_Pipe_MovingUp,
        340: SpriteImage_LemmyKoopa,
        341: SpriteImage_BigShell,
        342: SpriteImage_Muncher,
        343: SpriteImage_Fuzzy,
        344: SpriteImage_MortonKoopa,
        345: SpriteImage_ChainHolder,
        346: SpriteImage_HangingChainPlatform,
        347: SpriteImage_RoyKoopa,
        348: SpriteImage_LudwigVonKoopa,
        352: SpriteImage_RockyWrench,
        353: SpriteImage_Pipe_MovingDown,
        354: SpriteImage_BrownBlock,
        355: SpriteImage_RollingHillWith1Pipe,
        356: SpriteImage_BrownBlock,
        357: SpriteImage_Fruit,
        358: SpriteImage_LavaParticles,
        359: SpriteImage_WallLantern,
        360: SpriteImage_RollingHillWith8Pipes,
        361: SpriteImage_CrystalBlock,
        362: SpriteImage_ColoredBox,
        366: SpriteImage_CubeKinokoRot,
        367: SpriteImage_CubeKinokoLine,
        368: SpriteImage_FlashRaft,
        369: SpriteImage_SlidingPenguin,
        370: SpriteImage_CloudBlock,
        371: SpriteImage_RollingHillCoin,
        374: SpriteImage_SnowWind,
        376: SpriteImage_MovingChainLink,
        377: SpriteImage_Pipe_Up,
        378: SpriteImage_Pipe_Down,
        379: SpriteImage_Pipe_Right,
        380: SpriteImage_Pipe_Left,
        382: SpriteImage_ScrewMushroomNoBolt,
        385: SpriteImage_IceBlock,
        386: SpriteImage_PowBlock,
        387: SpriteImage_Bush,
        388: SpriteImage_Barrel,
        389: SpriteImage_StarCoinBoltControlled,
        390: SpriteImage_BoltControlledCoin,
        391: SpriteImage_GlowBlock,
        393: SpriteImage_PropellerBlock,
        394: SpriteImage_LemmyBall,
        395: SpriteImage_SpinyCheep,
        396: SpriteImage_MoveWhenOn,
        397: SpriteImage_GhostHouseBox,
        402: SpriteImage_LineQBlock,
        403: SpriteImage_LineBrickBlock,
        413: SpriteImage_WendyRing,
        414: SpriteImage_Gabon,
        415: SpriteImage_BetaLarryKoopa,
        416: SpriteImage_InvisibleOneUp,
        417: SpriteImage_SpinjumpCoin,
        419: SpriteImage_Bowser,
        420: SpriteImage_GiantGlowBlock,
        421: SpriteImage_UnusedGhostDoor,
        422: SpriteImage_ToadQBlock,
        423: SpriteImage_ToadBrickBlock,
        424: SpriteImage_PalmTree,
        425: SpriteImage_Jellybeam,
        427: SpriteImage_Kamek,
        428: SpriteImage_MGPanel,
        432: SpriteImage_Toad,
        433: SpriteImage_FloatingQBlock,
        434: SpriteImage_WarpCannon,
        435: SpriteImage_GhostFog,
        437: SpriteImage_PurplePole,
        438: SpriteImage_CageBlocks,
        439: SpriteImage_CagePeachFake,
        440: SpriteImage_HorizontalRope,
        441: SpriteImage_MushroomPlatform,
        443: SpriteImage_ReplayBlock,
        444: SpriteImage_SwingingVine,
        445: SpriteImage_CagePeachReal,
        447: SpriteImage_UnderwaterLamp,
        448: SpriteImage_MetalBar,
        450: SpriteImage_Pipe_EnterableUp,
        451: SpriteImage_MouserDespawner,
        452: SpriteImage_BowserDoor,
        453: SpriteImage_Seaweed,
        455: SpriteImage_HammerPlatform,
        456: SpriteImage_BossBridge,
        457: SpriteImage_SpinningThinBars,
        464: SpriteImage_SwingingVine,
        466: SpriteImage_LavaIronBlock,
        467: SpriteImage_MovingGemBlock,
        469: SpriteImage_BoltPlatform,
        470: SpriteImage_BoltPlatformWire,
        471: SpriteImage_PotPlatform,
        475: SpriteImage_IceFloe,
        476: SpriteImage_FlyingWrench,
        477: SpriteImage_SuperGuideBlock,
        478: SpriteImage_BowserSwitchSm,
        479: SpriteImage_BowserSwitchLg,
        }



def loadIfNotInImageCache(name, filename):
    """
    If name is not in ImageCache, loads the image
    referenced by 'filename' and puts it there
    """
    if name not in ImageCache:
        ImageCache[name] = GetImg(filename)




# Auxiliary Item Classes

class AuxiliaryItem(QtWidgets.QGraphicsItem):
    """Base class for auxiliary objects that accompany specific sprite types"""
    def __init__(self, parent):
        """Generic constructor for auxiliary items"""
        super().__init__(parent)
        self.parent = parent
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
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0, 0, width * 1.5, height * 1.5)
        self.setPos(0,0)
        self.width = width
        self.height = height
        self.direction = direction
        self.hover = False

    def setSize(self, width, height):
        self.prepareGeometryChange()
        self.BoundingRect = QtCore.QRectF(0, 0, width * 1.5, height * 1.5)
        self.width = width
        self.height = height

    def paint(self, painter, option, widget):
        painter.setClipRect(option.exposedRect)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(OutlinePen)

        if self.direction == self.Horizontal:
            lineY = self.height * 0.75
            painter.drawLine(20, lineY, (self.width * 1.5) - 20, lineY)
            painter.drawEllipse(8, lineY - 4, 8, 8)
            painter.drawEllipse((self.width * 1.5) - 16, lineY - 4, 8, 8)
        else:
            lineX = self.width * 0.75
            painter.drawLine(lineX, 20, lineX, (self.height * 1.5) - 20)
            painter.drawEllipse(lineX - 4, 8, 8, 8)
            painter.drawEllipse(lineX - 4, (self.height * 1.5) - 16, 8, 8)


class AuxiliaryCircleOutline(AuxiliaryItem):
    def __init__(self, parent, width):
        """Constructor"""
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0,0,width * 1.5,width * 1.5)
        self.setPos((8 - (width / 2)) * 1.5, 0)
        self.width = width
        self.hover = False

    def setSize(self, width):
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
        super().__init__(parent)

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
        super().__init__(parent)

        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.setPos(xoff, yoff)
        self.hover = False

    def setSize(self, width, height, xoff=0, yoff=0):
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
        super().__init__(parent)

        self.PainterPath = path
        self.setPos(xoff, yoff)
        self.fillFlag = True

        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.hover = False

    def SetPath(self, path):
        self.PainterPath = path

    def setSize(self, width, height, xoff=0, yoff=0):
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
        super().__init__(parent)
        self.BoundingRect = QtCore.QRectF(0,0,width,height)
        self.width = width
        self.height = height
        self.image = None
        self.hover = True

    def setSize(self, width, height, xoff=0, yoff=0):
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
        super().__init__(parent, width, height)
        self.alignment = Qt.AlignTop | Qt.AlignLeft
        self.realwidth = self.width
        self.realheight = self.height
        self.realimage = None
        # Doing it this way may provide a slight speed boost?
        self.flagPresent = lambda flags, flag: flags | flag == flags

    def setSize(self, width, height):
        super().setSize(width, height)
        self.realwidth = width
        self.realheight = height

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.realimage == None:
            try: self.realimage = self.image
            except: pass

    def move(self, x, y, w, h):
        """Repositions the auxiliary image"""

        # This will be used later
        oldx, oldy = self.x(), self.y()

        # Decide on the height to use
        # This solves the problem of "what if
        # agument w is smaller than self.width?"
        self.width = self.realwidth
        self.height = self.realheight
        changedSize = False
        if w < self.width:
            self.width = w
            changedSize = True
        if h < self.height:
            self.height = h
            changedSize = True
        if self.realimage != None:
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
        parent = self.parent
        newx = newx - parent.x()
        newy = newy - parent.y()

        # Set the pos
        self.setPos(newx, newy)

        # Update the affected area of the scene
        if self.scene() != None:
            self.scene().update(oldx + parent.x(), oldy + parent.y(), self.width, self.height)


# ---- SpriteImage Low-level Classes ----

class SpriteImage():
    """
    Class that contains information about a sprite image
    """
    def __init__(self, parent):
        self.parent = parent
        self.alpha = 1.0
        self.image = None
        self.showSpritebox = True
        self.xOffset = 0
        self.yOffset = 0
        self.width = 16
        self.height = 16
        self.aux = []
        self.updateSceneAfterPaint = False
    def updateSize(self):
        pass
    def paint(self, painter):
        pass
    def realViewZone(self, painter, zoneRect, viewRect):
        pass

    def getOffset(self):
        return [self.xOffset, self.yOffset]
    def setOffset(self, new):
        self.xOffset, self.yOffset = new[0], new[1]
    def delOffset(self):
        self.xOffset, self.yOffset = [0, 0]
    def getSize(self):
        return [self.width, self.height]
    def setSize(self, new):
        self.width, self.height = new[0], new[1]
    def delSize(self):
        self.width, self.height = [16, 16]
    def getDimensions(self):
        return [self.xOffset, self.yOffset, self.width, self.height]
    def setDimensions(self, new):
        self.xOffset, self.yOffset, self.width, self.height = new[0], new[1], new[2], new[3]
    def delDimensions(self):
        self.xOffset, self.yOffset, self.width, self.height = [0, 0, 16, 16]

    offset = property(getOffset, setOffset, delOffset,
        'Convenience property that provides access to self.xOffset and self.yOffset in one list')
    size = property(getSize, setSize, delSize,
        'Convenience property that provides access to self.width and self.height in one list')
    dimensions = property(getDimensions, setDimensions, delDimensions,
        'Convenience property that provides access to self.xOffset, self.yOffset, self.width and self.height in one list')

class SpriteImage_Static(SpriteImage):
    """
    A simple class for drawing a static sprite image
    """
    def __init__(self, parent, image=None, offset=None):
        super().__init__(parent)
        self.image = image
        self.showSpritebox = False
        if self.image is not None:
            self.width = (self.image.width() / 1.5) + 1
            self.height = (self.image.height() / 1.5) + 2
        if offset is not None:
            self.xOffset = offset[0]
            self.yOffset = offset[1]
    def updateSize(self):
        super().updateSize()

        if self.image is not None:
            self.size = (
                (self.image.width() / 1.5) + 1,
                (self.image.height() / 1.5) + 2,
                )
        else:
            del self.size

    def paint(self, painter):
        super().paint(painter)

        if self.image is None: return
        painter.save()
        painter.setOpacity(self.alpha)
        painter.drawPixmap(0, 0, self.image)
        painter.restore()

class SpriteImage_SimpleDynamic(SpriteImage_Static):
    """
    A class that acts like a SpriteImage_Static but lets you change
    the image with the size() method
    """
    def __init__(self, parent, image=None, offset=None):
        super().__init__(parent, image, offset)
    # no other changes needed yet


# ---- SpriteImage Medium-Level Classes ----

class SpriteImage_WoodenPlatform(SpriteImage):
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'WoodenPlatformL' not in ImageCache:
            LoadPlatformImages()

    def paint(self, painter):
        super().paint(painter)

        if self.color == 0:
            color = 'Wooden'
        elif self.color == 1:
            color = 'Stone'
        elif self.color == 2:
            color = 'Bone'

        if self.width > 32:
            painter.drawTiledPixmap(27, 0, ((self.width * 1.5) - 51), 24, ImageCache[color + 'PlatformM'])

        if self.width == 24:
            # replicate glitch effect foRotControlled by sprite 50
            painter.drawPixmap(0, 0, ImageCache[color + 'PlatformR'])
            painter.drawPixmap(8, 0, ImageCache[color + 'PlatformL'])
        else:
            # normal rendering
            painter.drawPixmap((self.width - 16) * 1.5, 0, ImageCache[color + 'PlatformR'])
            painter.drawPixmap(0, 0, ImageCache[color + 'PlatformL'])

class SpriteImage_DSStoneBlock(SpriteImage):
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'DSBlockTop' not in ImageCache:
            LoadDSStoneBlocks()

    def updateSize(self):
        super().updateSize()

        # get size
        width = self.parent.spritedata[5] & 7
        if width == 0: width = 1
        byte5 = self.parent.spritedata[4]
        self.width = (16 + (width << 4))
        self.height = (16 << ((byte5 & 0x30) >> 4)) - 4

    def paint(self, painter):
        super().paint(painter)

        middle_width = (self.width - 32) * 1.5
        middle_height = (self.height * 1.5) - 16
        bottom_y = (self.height * 1.5) - 8
        right_x = (self.width - 16) * 1.5

        painter.drawPixmap(0, 0, ImageCache['DSBlockTopLeft'])
        painter.drawTiledPixmap(24, 0, middle_width, 8, ImageCache['DSBlockTop'])
        painter.drawPixmap(right_x, 0, ImageCache['DSBlockTopRight'])

        painter.drawTiledPixmap(0, 8, 24, middle_height, ImageCache['DSBlockLeft'])
        painter.drawTiledPixmap(right_x, 8, 24, middle_height, ImageCache['DSBlockRight'])

        painter.drawPixmap(0, bottom_y, ImageCache['DSBlockBottomLeft'])
        painter.drawTiledPixmap(24, bottom_y, middle_width, 8, ImageCache['DSBlockBottom'])
        painter.drawPixmap(right_x, bottom_y, ImageCache['DSBlockBottomRight'])


class SpriteImage_StarCoin(SpriteImage_Static):
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['StarCoin'],
            (0, 3),
            )


class SpriteImage_Switch(SpriteImage_SimpleDynamic):
    def __init__(self, parent):
        super().__init__(parent)

        if 'QSwitch' not in ImageCache:
            LoadSwitches()

        self.switchType = ''

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1

        if not upsideDown:
            self.image = ImageCache[self.switchType + 'Switch']
        else:
            self.image = ImageCache[self.switchType + 'SwitchU']

        super().updateSize()


class SpriteImage_OldStoneBlock(SpriteImage):
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

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

        self.aux.append(AuxiliaryTrackObject(parent, 16, 16, AuxiliaryTrackObject.Horizontal))
        self.spikesL = False
        self.spikesR = False
        self.spikesT = False
        self.spikesB = False

    def updateSize(self):
        super().updateSize()

        size = self.parent.spritedata[5]
        height = (size & 0xF0) >> 4
        width = size & 0xF
        if self.parent.type == 30:
            height = 1 if height == 0 else height
            width = 1 if width == 0 else width
        self.width = width * 16 + 16
        self.height = height * 16 + 16

        type = self.parent.type

        if self.spikesL: # left spikes
            self.xOffset = -16
            self.width += 16
        if self.spikesT: # top spikes
            self.yOffset = -16
            self.height += 16
        if self.spikesR: # right spikes
            self.width += 16
        if self.spikesB: # bottom spikes
            self.height += 16

        # now set up the track
        direction = self.parent.spritedata[2] & 3
        distance = (self.parent.spritedata[4] & 0xF0) >> 4
        if direction > 3: direction = 0

        if direction <= 1: # horizontal
            self.aux[0].direction = 1
            self.aux[0].setSize(self.width + (distance * 16), self.height)
        else: # vertical
            self.aux[0].direction = 2
            self.aux[0].setSize(self.width, self.height + (distance * 16))

        if direction == 0 or direction == 3: # right, down
            self.aux[0].setPos(0,0)
        elif direction == 1: # left
            self.aux[0].setPos(-distance * 24,0)
        elif direction == 2: # up
            self.aux[0].setPos(0,-distance * 24)

    def paint(self, painter):
        super().paint(painter)

        blockX = 0
        blockY = 0
        type = self.parent.type
        width = self.width*1.5
        height = self.height*1.5

        if self.spikesL: # left spikes
            painter.drawTiledPixmap(0, 0, 24, height, ImageCache['SpikeL'])
            blockX = 24
            width -= 24
        if self.spikesT: # top spikes
            painter.drawTiledPixmap(0, 0, width, 24, ImageCache['SpikeU'])
            blockY = 24
            height -= 24
        if self.spikesR: # right spikes
            painter.drawTiledPixmap(blockX+width-24, 0, 24, height, ImageCache['SpikeR'])
            width -= 24
        if self.spikesB: # bottom spikes
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


class SpriteImage_HammerBro(SpriteImage_Static): # 95, 308
    def __init__(self, parent):
        loadIfNotInImageCache('HammerBro', 'hammerbro.png')
        super().__init__(
            parent,
            ImageCache['HammerBro'],
            (-8, -24),
            )


class SpriteImage_Amp(SpriteImage_Static): # 104, 108
    def __init__(self, parent):
        loadIfNotInImageCache('Amp', 'amp.png')
        super().__init__(
            parent,
            ImageCache['Amp'],
            (-8, -8),
            )


class SpriteImage_UnusedBlockPlatform(SpriteImage): # 97, 107, 132, 160
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'UnusedPlatform' not in ImageCache:
            LoadUnusedStuff()

        self.size = (48, 48)
        self.isDark = False
        self.drawPlatformImage = True

    def paint(self, painter):
        super().paint(painter)
        if not self.drawPlatformImage: return

        pixmap = ImageCache['UnusedPlatformDark'] if self.isDark else ImageCache['UnusedPlatform']
        pixmap = pixmap.scaled(
            self.width * 1.5, self.height * 1.5,
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation,
            )
        painter.drawPixmap(0, 0, pixmap)


class SpriteImage_SpikedStake(SpriteImage): # 137, 140, 141, 142
    def __init__(self, parent):
        super().__init__(parent)

        if 'StakeM0up' not in ImageCache:
            for dir in ['up', 'down', 'left', 'right']:
                ImageCache['StakeM0%s' % dir] = GetImg('stake_%s_m_0.png' % dir)
                ImageCache['StakeM1%s' % dir] = GetImg('stake_%s_m_1.png' % dir)
                ImageCache['StakeE0%s' % dir] = GetImg('stake_%s_e_0.png' % dir)
                ImageCache['StakeE1%s' % dir] = GetImg('stake_%s_e_1.png' % dir)

        self.SpikeLength = ((37 * 16) + 41) / 1.5
        # (16 mid sections + an end section), accounting for image/sprite size difference
        self.dir = 'down'

    def updateSize(self):
        super().updateSize()

        distance = self.parent.spritedata[3] >> 4
        if distance == 0:
            x = 16
        elif distance == 1:
            x = 7
        elif distance == 2:
            x = 14
        elif distance == 3:
            x = 10
        else:
            x = 16
        distance = x + 1 # In order to hide one side of the track behind the image.

        w = 66
        L = ((37 * 16) + 41) / 1.5 # (16 mid sections + an end section), accounting for image/sprite size difference

        if self.dir == 'up':
            self.aux[0].setPos(36, 24 - (distance * 24))
            self.aux[0].setSize(16, distance*16)
        elif self.dir == 'down':
            self.aux[0].setPos(36, (L * 1.5) - 24)
            self.aux[0].setSize(16, distance*16)
        elif self.dir == 'left':
            self.aux[0].setPos(24 - (distance * 24), 36)
            self.aux[0].setSize(distance * 16, 16)
        elif self.dir == 'right':
            self.aux[0].setPos((L * 1.5) - 24, 36)
            self.aux[0].setSize(distance * 16, 16)

    def paint(self, painter):
        super().paint(painter)

        color = self.parent.spritedata[3] & 15
        if color == 2 or color == 3 or color == 7:
            mid = ImageCache['StakeM1' + self.dir]
            end = ImageCache['StakeE1' + self.dir]
        else:
            mid = ImageCache['StakeM0' + self.dir]
            end = ImageCache['StakeE0' + self.dir]

        tiles = 16
        tilesize = 37
        endsize = 41
        width = 100

        if dir == 'up':
            painter.drawPixmap(0, 0, end)
            painter.drawTiledPixmap(0, endsize, width, tilesize * tiles, mid)
        elif dir == 'down':
            painter.drawTiledPixmap(0, 0, width, tilesize * tiles, mid)
            painter.drawPixmap(0, (self.height * 1.5) - endsize, end)
        elif dir == 'left':
            painter.drawPixmap(0, 0, end)
            painter.drawTiledPixmap(endsize, 0, tilesize * tiles, width, mid)
        elif dir == 'right':
            painter.drawTiledPixmap(0, 0, tilesize * tiles, width, mid)
            painter.drawPixmap((self.width * 1.5) - endsize, 0, end)


class SpriteImage_ScrewMushroom(SpriteImage): # 172, 382
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'Bolt' not in ImageCache:
            ImageCache['Bolt'] = GetImg('bolt.png')
        if 'ScrewShroomT' not in ImageCache:
            ImageCache['ScrewShroomT'] = GetImg('screw_shroom_top.png')
            ImageCache['ScrewShroomM'] = GetImg('screw_shroom_middle.png')
            ImageCache['ScrewShroomB'] = GetImg('screw_shroom_bottom.png')

        self.hasBolt = False

    def updateSize(self):
        super().updateSize()

        # I wish I knew what this does
        SomeOffset = self.parent.spritedata[3]
        if SomeOffset == 0 or SomeOffset > 8: SomeOffset = 8

        self.width = 122
        self.height = 198
        self.xOffset = 3
        self.yOffset = SomeOffset * -16
        if self.hasBolt:
            self.height += 16
            self.yOffset -= 16

    def paint(self, painter):
        super().paint(painter)

        y = 0
        if self.hasBolt:
            painter.drawPixmap(70, 0, ImageCache['Bolt'])
            y += 24
        painter.drawPixmap(0, y, ImageCache['ScrewShroomT'])
        painter.drawTiledPixmap(76, y + 93, 31, 172, ImageCache['ScrewShroomM'])
        painter.drawPixmap(76, y + 253, ImageCache['ScrewShroomB'])


class SpriteImage_Block(SpriteImage): # 207, 208, 209, 221, 255, 256, 402, 403, 422, 423
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        self.tilenum = 1315
        self.contentsNybble = 5
        self.contentsOverride = None
        self.twelveIsMushroom = False
        self.rotates = False

    def updateSize(self):
        super().updateSize()

        # SET CONTENTS
        # In the blocks.png file:
        # 0 = Empty, 1 = Coin, 2 = Mushroom, 3 = Fire Flower, 4 = Propeller, 5 = Penguin Suit,
        # 6 = Mini Shroom, 7 = Star, 8 = Continuous Star, 9 = Yoshi Egg, 10 = 10 Coins,
        # 11 = 1-up, 12 = Vine, 13 = Spring, 14 = Shroom/Coin, 15 = Ice Flower, 16 = Toad

        if self.contentsOverride is not None:
            contents = self.contentsOverride
        else:
            contents = self.parent.spritedata[self.contentsNybble] & 0xF

        if contents == 2: # 1 and 2 are always fire flowers
            contents = 3

        if contents == 12 and self.twelveIsMushroom:
            contents = 2 # 12 is a mushroom on some types

        self.image = ImageCache['Blocks'][contents]

        # SET UP ROTATION
        if self.rotates:
            transform = QtGui.QTransform()
            transform.translate(12, 12)

            angle = (self.parent.spritedata[4] & 0xF0) >> 4
            leftTilt = self.parent.spritedata[3] & 1

            angle *= (45.0 / 16.0)

            if leftTilt == 0:
                transform.rotate(angle)
            else:
                transform.rotate(360.0 - angle)

            transform.translate(-12, -12)
            self.parent.setTransform(transform)

    def paint(self, painter):
        super().paint(painter)

        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        if Tiles[self.tilenum] != None:
            painter.drawPixmap(0, 0, Tiles[self.tilenum].main)
        painter.drawPixmap(0, 0, self.image)


class SpriteImage_SpecialCoin(SpriteImage_Static): # 253, 371, 390
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SpecialCoin'],
            )


class SpriteImage_Door(SpriteImage): # 182, 259, 276, 277, 278, 421, 452
    def __init__(self, parent):
        super().__init__(parent)
        self.doorName = 'Door'
        self.doorDimensions = (0, 0, 32, 48)

    def updateSize(self):
        super().updateSize()

        rotstatus = self.parent.spritedata[4]
        if rotstatus & 1 == 0:
            direction = 0
        else:
            direction = (rotstatus & 0x30) >> 4

        if direction > 3: direction = 0
        doorType = self.parent.doorType
        doorSize = self.parent.doorSize
        if direction == 0:
            self.image = ImageCache[self.doorName + 'U']
            self.xOffset = doorSize[0]
            self.yOffset = doorSize[1]
            self.width = doorSize[2]
            self.height = doorSize[3]
        elif direction == 1:
            self.image = ImageCache[self.doorName + 'L']
            self.xOffset = (doorSize[2] / 2) + doorSize[0] - doorSize[3]
            self.yOffset = doorSize[1] + (doorSize[3] - (doorSize[2] / 2))
            self.width = doorSize[3]
            self.height = doorSize[2]
        elif direction == 2:
            self.image = ImageCache[self.doorName + 'D']
            self.xOffset = doorSize[0]
            self.yOffset = doorSize[1]+doorSize[3]
            self.width = doorSize[2]
            self.height = doorSize[3]
        elif direction == 3:
            self.image = ImageCache[self.doorName + 'R']
            self.xOffset = doorSize[0] + (doorSize[2] / 2)
            self.yOffset = doorSize[1] + (doorSize[3] - (doorSize[2] / 2))
            self.width = doorSize[3]
            self.height = doorSize[2]


class SpriteImage_Pipe(SpriteImage): # 339, 353, 377, 378, 379, 380, 450
    def __init__(self, parent):
        super().__init__(parent)

        if 'PipeTop0' not in ImageCache:
            for i, color in enumerate(['green', 'red', 'yellow', 'blue']):
                ImageCache['PipeTop%d' % i] = GetImg('pipe_%s_top.png' % color)
                ImageCache['PipeMiddle%d' % i] = GetImg('pipe_%s_middle.png' % color)
                ImageCache['PipeBottom%d' % i] = GetImg('pipe_%s_bottom.png' % color)
                ImageCache['PipeLeft%d' % i] = GetImg('pipe_%s_left.png' % color)
                ImageCache['PipeCenter%d' % i] = GetImg('pipe_%s_center.png' % color)
                ImageCache['PipeRight%d' % i] = GetImg('pipe_%s_right.png' % color)

        self.parent.setZValue(24999)

        self.moving = False
        self.direction = 'U'

    def updateSize(self):
        super().updateSize()
        # sprite types:
        # 339 = Moving Pipe Facing Up
        # 353 = Moving Pipe Facing Down
        # 377 = Pipe Up
        # 378 = Pipe Down
        # 379 = Pipe Right
        # 380 = Pipe Left
        # 450 = Enterable Pipe Up

        props = self.parent.spritedata[5]

        if not self.moving: # normal pipes
            self.color = (props & 0x30) >> 4
            length = props & 0xF

            size = length * 16 + 32
            if self.direction in 'LR': # horizontal
                self.width = size
                self.height = 32
                if self.direction == 'R': # faces right
                    self.xOffset = 0
                else: # faces left
                    self.xOffset = 16 - size
                self.yOffset = 0

            else: # vertical
                self.width = 32
                self.height = size
                if self.direction == 'D': # faces down
                    self.yOffset = 0
                else: # faces up
                    self.yOffset = 16 - size
                self.xOffset = 0

        else: # moving pipes
            self.color = self.parent.spritedata[3]
            length1 = (props & 0xF0) >> 4
            length2 = (props & 0xF)
            size = max(length1, length2) * 16 + 32

            self.width = 32
            self.height = size

            if self.direction == 'U': # facing up
                self.yOffset = 16 - size
            else: # facing down
                self.yOffset = 0

            self.length1 = length1 * 16 + 32
            self.length2 = length2 * 16 + 32

    def paint(self, painter):
        super().paint(painter)

        color = self.color
        xsize = self.width * 1.5
        ysize = self.height * 1.5

        if not self.parent.moving:
            # Static pipes
            if self.direction in 'UD': # vertical
                if self.direction == 'U':
                    painter.drawPixmap(0, 0, ImageCache['PipeTop%d' % color])
                    painter.drawTiledPixmap(0, 24, 48, ysize-24, ImageCache['PipeMiddle%d' % color])
                else:
                    painter.drawTiledPixmap(0, 0, 48, ysize-24, ImageCache['PipeMiddle%d' % color])
                    painter.drawPixmap(0, ysize-24, ImageCache['PipeBottom%d' % color])
            else: # horizontal
                if self.direction == 'L':
                    painter.drawPixmap(0, 0, ImageCache['PipeLeft%d' % color])
                    painter.drawTiledPixmap(24, 0, xsize-24, 48, ImageCache['PipeCenter%d' % color])
                else:
                    painter.drawTiledPixmap(0, 0, xsize-24, 48, ImageCache['PipeCenter%d' % color])
                    painter.drawPixmap(xsize-24, 0, ImageCache['PipeRight%d' % color])
        else:
            # Moving pipes
            length1 = self.length1*1.5
            length2 = self.length2*1.5
            low = min(length1, length2)
            high = max(length1, length2)

            if self.parent.direction == 'U':
                y1 = ysize - low
                y2 = ysize - high

                # draw semi-transparent pipe
                painter.save()
                painter.setOpacity(0.5)
                painter.drawPixmap(0, y2, ImageCache['PipeTop%d' % color])
                painter.drawTiledPixmap(0, y2 + 24, 48, high - 24, ImageCache['PipeMiddle%d' % color])
                painter.restore()

                # draw opaque pipe
                painter.drawPixmap(0, y1, ImageCache['PipeTop%d' % color])
                painter.drawTiledPixmap(0, y1 + 24, 48, low - 24, ImageCache['PipeMiddle%d' % color])

            else:
                # draw semi-transparent pipe
                painter.save()
                painter.setOpacity(0.5)
                painter.drawTiledPixmap(0, 0, 48, high - 24, ImageCache['PipeMiddle%d' % color])
                painter.drawPixmap(0, high-24, ImageCache['PipeBottom%d' % color])
                painter.restore()

                # draw opaque pipe
                painter.drawTiledPixmap(0, 0, 48, low - 24, ImageCache['PipeMiddle%d' % color])
                painter.drawPixmap(0, low-24, ImageCache['PipeBottom%d' % color])


class SpriteImage_RollingHillWithPipe(SpriteImage): # 355, 360
    def __init__(self, parent):
        super().__init__(parent)
        self.aux.append(AuxiliaryCircleOutline(parent, 800))



# ---- SpriteImage High-Level Classes ----

class SpriteImage_Goomba(SpriteImage_Static): # 20
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Goomba'],
            (-1, -4),
            )


class SpriteImage_Paragoomba(SpriteImage_Static): # 21
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Paragoomba'],
            (1, -10),
            )


class SpriteImage_HorzMovingPlatform(SpriteImage_WoodenPlatform): # 23
    def __init__(self, parent):
        super().__init__(parent)

        self.width = ((self.parent.spritedata[5] & 0xF) + 1) << 4
        self.aux.append(AuxiliaryTrackObject(parent, self.width, 16, AuxiliaryTrackObject.Horizontal))

    def updateSize(self):
        super().updateSize()

        # get width and distance
        self.width = ((self.parent.spritedata[5] & 0xF) + 1) << 4
        if self.width == 16: self.width = 32

        distance = (self.parent.spritedata[4] & 0xF) << 4

        # update the track
        self.aux[0].setSize(self.width + distance, 16)

        if (self.parent.spritedata[3] & 1) == 0:
            # platform goes right
            self.aux[0].setPos(0, 0)
        else:
            # platform goes left
            self.aux[0].setPos(-distance*1.5, 0)

        # set color
        self.color = (self.parent.spritedata[3] >> 4) & 1

        self.aux[0].update()


class SpriteImage_BuzzyBeetle(SpriteImage_SimpleDynamic): # 24
    def updateSize(self):

        orient = self.parent.spritedata[5] & 15
        if orient == 1:
            self.image = ImageCache['BuzzyBeetleU']
            self.yOffset = 0
        elif orient == 2:
            self.image = ImageCache['BuzzyBeetleShell']
            self.yOffset = 2
        elif orient == 3:
            self.image = ImageCache['BuzzyBeetleShellU']
            self.yOffset = 2
        else:
            self.image = ImageCache['BuzzyBeetle']
            self.yOffset = 0

        super().updateSize()


class SpriteImage_Spiny(SpriteImage_SimpleDynamic): # 25
    def updateSize(self):

        orient = self.parent.spritedata[5] & 15
        if orient == 1:
            self.image = ImageCache['SpinyBall']
            self.yOffset = -2
        elif orient == 2:
            self.image = ImageCache['SpinyShell']
            self.yOffset = 1
        elif orient == 3:
            self.image = ImageCache['SpinyShellU']
            self.yOffset = 2
        else:
            self.image = ImageCache['Spiny']
            self.yOffset = 0

        super().updateSize()


class SpriteImage_UpsideDownSpiny(SpriteImage_Static): # 26
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SpinyU'],
            )


class SpriteImage_DSStoneBlock_Vert(SpriteImage_DSStoneBlock): # 27
    def __init__(self, parent):
        super().__init__(parent)

        self.aux.append(AuxiliaryTrackObject(parent, 32, 16, AuxiliaryTrackObject.Vertical))
        self.size = (32, 16)

    def updateSize(self):
        super().updateSize()

        # get height and distance
        byte5 = self.parent.spritedata[4]
        distance = (byte5 & 0xF) << 4

        # update the track
        self.aux[0].setSize(self.width, distance + self.height)

        if (self.parent.spritedata[3] & 1) == 0:
            # block goes up
            self.aux[0].setPos(0, -distance * 1.5)
        else:
            # block goes down
            self.aux[0].setPos(0, 0)

        self.aux[0].update()


class SpriteImage_DSStoneBlock_Horz(SpriteImage_DSStoneBlock): # 28
    def __init__(self, parent):
        super().__init__(parent)

        self.aux.append(AuxiliaryTrackObject(parent, 32, 16, AuxiliaryTrackObject.Horizontal))
        self.size = (32, 16)

    def updateSize(self):
        super().updateSize()

        # get height and distance
        byte5 = self.parent.spritedata[4]
        distance = (byte5 & 0xF) << 4

        # update the track
        self.aux[0].setSize(distance + self.width, self.height)

        if (self.parent.spritedata[3] & 1) == 0:
            # block goes right
            self.aux[0].setPos(0, 0)
        else:
            # block goes left
            self.aux[0].setPos(-distance * 1.5, 0)

        self.aux[0].update()


class SpriteImage_OldStoneBlock_NoSpikes(SpriteImage_OldStoneBlock): # 30
    pass


class SpriteImage_VertMovingPlatform(SpriteImage_WoodenPlatform): # 31
    def __init__(self, parent):
        super().__init__(parent)

        self.width = ((self.parent.spritedata[5] & 0xF) + 1) << 4
        self.aux.append(AuxiliaryTrackObject(parent, self.width, 16, AuxiliaryTrackObject.Vertical))


    def updateSize(self):
        super().updateSize()

        # get width and distance
        self.width = ((self.parent.spritedata[5] & 0xF) + 1) << 4
        if self.width == 16: self.width = 32

        distance = (self.parent.spritedata[4] & 0xF) << 4

        # update the track
        self.aux[0].setSize(self.width, distance + 16)

        if (self.parent.spritedata[3] & 1) == 0:
            # platform goes up
            self.aux[0].setPos(0, -distance * 1.5)
        else:
            # platform goes down
            self.aux[0].setPos(0, 0)

        # set color
        self.color = (self.parent.spritedata[3] >> 4) & 1

        self.aux[0].update()


class SpriteImage_StarCoinRegular(SpriteImage_StarCoin): # 32
    pass


class SpriteImage_QuestionSwitch(SpriteImage_Switch): # 40
    def __init__(self, parent):
        super().__init__(parent)
        self.switchType = 'Q'


class SpriteImage_PSwitch(SpriteImage_Switch): # 41
    def __init__(self, parent):
        super().__init__(parent)
        self.switchType = 'P'


class SpriteImage_ExcSwitch(SpriteImage_Switch): # 42
    def __init__(self, parent):
        super().__init__(parent)
        self.switchType = 'E'


class SpriteImage_QuestionSwitchBlock(SpriteImage_Static): # 43
    def __init__(self, parent):
        if 'QSwitch' not in ImageCache:
            LoadSwitches()
        super().__init__(
            parent,
            ImageCache['QSwitchBlock'],
            )


class SpriteImage_PSwitchBlock(SpriteImage_Static): # 44
    def __init__(self, parent):
        if 'PSwitch' not in ImageCache:
            LoadSwitches()
        super().__init__(
            parent,
            ImageCache['PSwitchBlock'],
            )


class SpriteImage_ExcSwitchBlock(SpriteImage_Static): # 45
    def __init__(self, parent):
        if 'ESwitch' not in ImageCache:
            LoadSwitches()
        super().__init__(
            parent,
            ImageCache['ESwitchBlock'],
            )


class SpriteImage_Podoboo(SpriteImage_Static): # 46
    def __init__(self, parent):
        if 'Podoboo' not in ImageCache:
            LoadCastleStuff()
        super().__init__(
            parent,
            ImageCache['Podoboo'],
            )


class SpriteImage_Thwomp(SpriteImage_Static): # 47
    def __init__(self, parent):
        if 'Thwomp' not in ImageCache:
            LoadCastleStuff()
        super().__init__(
            parent,
            ImageCache['Thwomp'],
            (-6, -6),
            )


class SpriteImage_GiantThwomp(SpriteImage_Static): # 48
    def __init__(self, parent):
        if 'GiantThwomp' not in ImageCache:
            LoadCastleStuff()
        super().__init__(
            parent,
            ImageCache['GiantThwomp'],
            (-8, -8),
            )


class SpriteImage_UnusedSeesaw(SpriteImage): # 49
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'UnusedPlatformDark' not in ImageCache:
            LoadUnusedStuff()

        self.aux.append(AuxiliaryRotationAreaOutline(parent, 48))
        self.aux[0].setPos(128, -36)

        self.image = ImageCache['UnusedPlatformDark']
        self.dimensions = (0, -8, 256, 16)

    def updateSize(self):
        w = self.parent.spritedata[5] & 15
        if w == 0:
            self.width = 16 * 16 # 16 blocks wide
        else:
            self.width = w * 32
        self.image = ImageCache['UnusedPlatformDark'].scaled(
            self.width * 1.5, self.height * 1.5,
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation,
            )
        self.xOffset = (8 * 16) - (self.width / 2)
        print(self.image)

        swingArc = self.parent.spritedata[5] >> 4
        swingArcs = (
            45,
            4.5,
            9,
            18,
            65,
            80,
            )
        if swingArc <= 5:
            realSwingArc = swingArcs[swingArc]
        else:
            realSwingArc = 100 # infinite

        # angle starts at the right position (3 o'clock)
        # negative = clockwise, positive = counter-clockwise
        startAngle = 90 - realSwingArc
        spanAngle = realSwingArc * 2

        self.aux[0].SetAngle(startAngle, spanAngle)
        self.aux[0].setPos((self.width / 1.5) - 36, -36)
        self.aux[0].update()

        super().updateSize()

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, self.image)


class SpriteImage_FallingPlatform(SpriteImage_WoodenPlatform): # 50
    def __init__(self, parent):
        super().__init__(parent)

    def updateSize(self):
        super().updateSize()

        # get width
        self.width = ((self.parent.spritedata[5] & 0xF) + 1) << 4

        # override this for the "glitchy" effect caused by length=0
        if self.width == 16: self.width = 24

        # set color
        color = (self.parent.spritedata[3] >> 4)
        if color == 1:
            self.color = 1
        elif color == 3:
            self.color = 2
        else:
            self.color = 0


class SpriteImage_TiltingGirder(SpriteImage_Static): # 51
    def __init__(self, parent):
        if 'TiltingGirder' not in ImageCache:
            LoadPlatformImages()
        super().__init__(
            parent,
            ImageCache['TiltingGirder'],
            (0, -18),
            )


class SpriteImage_UnusedRotPlatforms(SpriteImage): # 52
    def __init__(self, parent):
        super().__init__(parent)

        if 'UnusedRotPlatforms' not in ImageCache:
            LoadUnusedStuff()

        self.aux.append(AuxiliaryImage(parent, 432, 312))
        self.aux[0].image = ImageCache['UnusedRotPlatforms']
        self.aux[0].setPos(-144 - 72, -104 - 52) # It actually isn't centered correctly in-game


class SpriteImage_Lakitu(SpriteImage_Static): # 54
    def __init__(self, parent):
        if 'Lakitu' not in ImageCache:
            LoadDesertStuff()
        super().__init__(
            parent,
            ImageCache['Lakitu'],
            (-16, -24),
            )


class SpriteImage_UnusedRisingSeesaw(SpriteImage_Static): # 55
    def __init__(self, parent):
        if 'UnusedPlatformDark' not in ImageCache:
            LoadUnusedStuff()
        super().__init__(
            parent,
            ImageCache['UnusedPlatformDark'].scaled(
                377, 24,
                Qt.IgnoreAspectRatio, Qt.SmoothTransformation,
                ),
            )


class SpriteImage_RisingTiltGirder(SpriteImage_Static): # 56
    def __init__(self, parent):
        loadIfNotInImageCache('RisingTiltGirder', 'rising_girder.png')
        super().__init__(
            parent,
            ImageCache['RisingTiltGirder'],
            (-32, -10),
            )


class SpriteImage_KoopaTroopa(SpriteImage_SimpleDynamic): # 57
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['KoopaG'],
            (-7, -15),
            )

    def updateSize(self):
        # get properties
        props = self.parent.spritedata[5]
        shell = (props >> 4) & 1
        color = props & 1

        if shell == 0:
            self.offset = (-7, -15)

            if color == 0:
                self.image = ImageCache['KoopaG']
            else:
                self.image = ImageCache['KoopaR']
        else:
            del self.offset

            if color == 0:
                self.image = ImageCache['KoopaShellG']
            else:
                self.image = ImageCache['KoopaShellR']

        super().updateSize()


class SpriteImage_KoopaParatroopa(SpriteImage_SimpleDynamic): # 58
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ParakoopaG'],
            (-7, -12),
            )

    def updateSize(self):

        # get properties
        color = self.parent.spritedata[5] & 1

        if color == 0:
            self.image = ImageCache['ParakoopaG']
        else:
            self.image = ImageCache['ParakoopaR']

        super().updateSize()


class SpriteImage_LineTiltGirder(SpriteImage_Static): # 59
    def __init__(self, parent):
        loadIfNotInImageCache('LineGirder', 'line_tilt_girder.png')
        super().__init__(
            parent,
            ImageCache['LineGirder'],
            (-8, -10),
            )


class SpriteImage_SpikeTop(SpriteImage_SimpleDynamic): # 60
    def __init__(self, parent):
        if 'SpikeTopUL' not in ImageCache:
            SpikeTop = GetImg('spiketop.png', True)

            Transform = QtGui.QTransform()
            ImageCache['SpikeTop00'] = QtGui.QPixmap.fromImage(SpikeTop.mirrored(True, False))
            Transform.rotate(90)
            ImageCache['SpikeTop10'] = ImageCache['SpikeTop00'].transformed(Transform)
            Transform.rotate(90)
            ImageCache['SpikeTop20'] = ImageCache['SpikeTop00'].transformed(Transform)
            Transform.rotate(90)
            ImageCache['SpikeTop30'] = ImageCache['SpikeTop00'].transformed(Transform)

            Transform = QtGui.QTransform()
            ImageCache['SpikeTop01'] = QtGui.QPixmap.fromImage(SpikeTop)
            Transform.rotate(90)
            ImageCache['SpikeTop11'] = ImageCache['SpikeTop01'].transformed(Transform)
            Transform.rotate(90)
            ImageCache['SpikeTop21'] = ImageCache['SpikeTop01'].transformed(Transform)
            Transform.rotate(90)
            ImageCache['SpikeTop31'] = ImageCache['SpikeTop01'].transformed(Transform)

        super().__init__(
            parent,
            ImageCache['SpikeTop00'],
            (0, -4),
            )

    def updateSize(self):

        orientation = (self.parent.spritedata[5] >> 4) % 4
        direction = self.parent.spritedata[5] & 1

        self.image = ImageCache['SpikeTop%d%d' % (orientation, direction)]

        self.offset = (
            (0, -4),
            (0, 0),
            (0, 0),
            (-4, 0),
            )[orientation]

        super().updateSize()


class SpriteImage_BigBoo(SpriteImage): # 61
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        loadIfNotInImageCache('BigBoo', 'bigboo.png')

        self.aux.append(AuxiliaryImage(parent, 243, 248))
        self.aux[0].image = ImageCache['BigBoo']
        self.aux[0].setPos(-48, -48)
        self.aux[0].hover = False

        self.dimensions = (-38, -80, 98, 102)


class SpriteImage_SpikeBall(SpriteImage_Static): # 63
    def __init__(self, parent):
        if 'SpikeBall' not in ImageCache:
            LoadCastleStuff()
        super().__init__(
            parent,
            ImageCache['SpikeBall'],
            )


class SpriteImage_OutdoorsFog(SpriteImage): # 64
    def __init__(self, parent):
        super().__init__(parent)
        self.updateSceneAfterPaint = True

        loadIfNotInImageCache('OutdoorsFog', 'fog_outdoors.png')

    def updateSize(self):
        super().updateSize()
        self.parent.updateScene()

    def realViewZone(self, painter, zoneRect, viewRect):

        if self.parent.spritedata[5]: return

        # (0, 0) is the top-left corner of the zone

        # Get the width and height of the zone
        zx = zoneRect.topLeft().x()
        zy = zoneRect.topLeft().y()
        zw = zoneRect.width()
        zh = zoneRect.height()

        # Get the y pos of the self.parent
        sy = self.parent.objy

        # Get pixmaps
        mid = ImageCache['OutdoorsFog']

        paintLiquid(painter, None, mid, None, None, zx, zy, zw, zh, sy, False, 0)


class SpriteImage_PipePiranhaUp(SpriteImage_Static): # 65
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipePlantUp'],
            (2, -32),
            )


class SpriteImage_PipePiranhaDown(SpriteImage_Static): # 66
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipePlantDown'],
            (2, 32),
            )


class SpriteImage_PipePiranhaRight(SpriteImage_Static): # 67
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipePlantRight'],
            (32, 2),
            )


class SpriteImage_PipePiranhaLeft(SpriteImage_Static): # 68
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipePlantLeft'],
            (-32, 2),
            )


class SpriteImage_PipeFiretrapUp(SpriteImage_Static): # 69
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipeFiretrapUp'],
            (-4, -29),
            )


class SpriteImage_PipeFiretrapDown(SpriteImage_Static): # 70
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipeFiretrapDown'],
            (-4, 32),
            )


class SpriteImage_PipeFiretrapRight(SpriteImage_Static): # 71
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipeFiretrapRight'],
            (32, 6),
            )


class SpriteImage_PipeFiretrapLeft(SpriteImage_Static): # 72
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PipeFiretrapLeft'],
            (-29, 6),
            )


class SpriteImage_GroundPiranha(SpriteImage_SimpleDynamic): # 73
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['GroundPiranha'],
            (-20, 0),
            )

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1
        if not upsideDown:
            self.yOffset = 6
            self.image = ImageCache['GroundPiranha']
        else:
            self.yOffset = 0
            self.image = ImageCache['GroundPiranhaU']

        super().updateSize()


class SpriteImage_BigGroundPiranha(SpriteImage_SimpleDynamic): # 74
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['BigGroundPiranha'],
            (-65, 0),
            )

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1
        if not upsideDown:
            self.yOffset = -32
            self.image = ImageCache['BigGroundPiranha']
        else:
            self.yOffset = 0
            self.image = ImageCache['BigGroundPiranhaU']

        super().updateSize()


class SpriteImage_GroundFiretrap(SpriteImage_SimpleDynamic): # 75
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['GroundFiretrap'],
            (5, 0),
            )

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1
        if not upsideDown:
            self.yOffset = -10
            self.image = ImageCache['GroundFiretrap']
        else:
            self.yOffset = 0
            self.image = ImageCache['GroundFiretrapU']

        super().updateSize()


class SpriteImage_BigGroundFiretrap(SpriteImage_SimpleDynamic): # 76
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['BigGroundFiretrap'],
            (-14, 0),
            )

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1
        if not upsideDown:
            self.yOffset = -68
            self.image = ImageCache['BigGroundFiretrap']
        else:
            self.yOffset = 0
            self.image = ImageCache['BigGroundFiretrapU']

        super().updateSize()


class SpriteImage_ShipKey(SpriteImage_Static): # 77
    def __init__(self, parent):
        loadIfNotInImageCache('ShipKey', 'ship_key.png')
        super().__init__(
            parent,
            ImageCache['ShipKey'],
            (-1, -8),
            )


class SpriteImage_CloudTrampoline(SpriteImage_SimpleDynamic): # 78
    def __init__(self, parent):
        loadIfNotInImageCache('CloudTrBig', 'cloud_trampoline_big.png')
        loadIfNotInImageCache('CloudTrSmall', 'cloud_trampoline_small.png')
        super().__init__(
            parent,
            ImageCache['CloudTrSmall'],
            (-2, -2),
            )

    def updateSize(self):

        size = (self.parent.spritedata[4] & 0x10) >> 4
        if size == 0:
            self.image = ImageCache['CloudTrSmall']
            self.size = (68, 27)
        else:
            self.image = ImageCache['CloudTrBig']
            self.size = (132, 32)

        super().updateSize()


class SpriteImage_FireBro(SpriteImage_Static): # 80
    def __init__(self, parent):
        loadIfNotInImageCache('FireBro', 'firebro.png')
        super().__init__(
            parent,
            ImageCache['FireBro'],
            (-8, -22),
            )


class SpriteImage_OldStoneBlock_SpikesLeft(SpriteImage_OldStoneBlock): # 81
    def __init__(self, parent):
        super().__init__(parent)
        self.spikesL = True


class SpriteImage_OldStoneBlock_SpikesRight(SpriteImage_OldStoneBlock): # 82
    def __init__(self, parent):
        super().__init__(parent)
        self.spikesR = True


class SpriteImage_OldStoneBlock_SpikesLeftRight(SpriteImage_OldStoneBlock): # 83
    def __init__(self, parent):
        super().__init__(parent)
        self.spikesL = True
        self.spikesR = True


class SpriteImage_OldStoneBlock_SpikesTop(SpriteImage_OldStoneBlock): # 84
    def __init__(self, parent):
        super().__init__(parent)
        self.spikesT = True


class SpriteImage_OldStoneBlock_SpikesBottom(SpriteImage_OldStoneBlock): # 85
    def __init__(self, parent):
        super().__init__(parent)
        self.spikesB = True


class SpriteImage_OldStoneBlock_SpikesTopBottom(SpriteImage_OldStoneBlock): # 86
    def __init__(self, parent):
        super().__init__(parent)
        self.spikesT = True
        self.spikesB = True


class SpriteImage_TrampolineWall(SpriteImage_SimpleDynamic): # 87
    def __init__(self, parent):
        if 'UnusedPlatformDark' not in ImageCache:
            LoadUnusedStuff()
        super().__init__(parent)

    def updateSize(self):
        height = (self.parent.spritedata[5] & 15) + 1

        self.image = ImageCache['UnusedPlatformDark'].scaled(
            24, height * 24,
            Qt.IgnoreAspectRatio, Qt.SmoothTransformation,
            )
        self.height = height * 16

        super().updateSize()


class SpriteImage_BulletBillLauncher(SpriteImage): # 92
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        loadIfNotInImageCache('BBLauncherT', 'bullet_launcher_top.png')
        loadIfNotInImageCache('BBLauncherM', 'bullet_launcher_middle.png')

    def updateSize(self):
        super().updateSize()
        height = (self.parent.spritedata[5] & 0xF0) >> 4

        self.height = (height + 2) * 16
        self.yOffset = (height + 1) * -16

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['BBLauncherT'])
        painter.drawTiledPixmap(0, 48, 24, self.height*1.5 - 48, ImageCache['BBLauncherM'])


class SpriteImage_BanzaiBillLauncher(SpriteImage_Static): # 93
    def __init__(self, parent):
        loadIfNotInImageCache('BanzaiLauncher', 'banzai_launcher.png')
        super().__init__(
            parent,
            ImageCache['BanzaiLauncher'],
            (-32, -68),
            )


class SpriteImage_BoomerangBro(SpriteImage_Static): # 94
    def __init__(self, parent):
        loadIfNotInImageCache('BoomerangBro', 'boomerangbro.png')
        super().__init__(
            parent,
            ImageCache['BoomerangBro'],
            (-8, -22),
            )


class SpriteImage_HammerBroNormal(SpriteImage_HammerBro): # 95
    pass


class SpriteImage_RotationControllerSwaying(SpriteImage): # 96
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.setZValue(100000)
        self.aux.append(AuxiliaryRotationAreaOutline(parent, 48))

    def updateSize(self):
        super().updateSize()
        # get the swing arc: 4 == 90 degrees (45 left from the origin, 45 right)
        swingArc = self.parent.spritedata[2] >> 4
        realSwingArc = swingArc * 11.25

        # angle starts at the right position (3 o'clock)
        # negative = clockwise, positive = counter-clockwise
        startAngle = 90 - realSwingArc
        spanAngle = realSwingArc * 2

        self.aux[0].SetAngle(startAngle, spanAngle)
        self.aux[0].update()


class SpriteImage_RotationControlledSolidBetaPlatform(SpriteImage_UnusedBlockPlatform): # 97
    def __init__(self, parent):
        super().__init__(parent)
        self.isDark = True

    def updateSize(self):
        size = self.parent.spritedata[4]
        width = size >> 4
        height = size & 0xF

        if width == 0 or height == 0:
            self.showSpritebox = True
            self.drawPlatformImage = False
            del self.size
        else:
            self.showSpritebox = False
            self.drawPlatformImage = True
            self.size = (width * 16, height * 16)

        super().updateSize()


class SpriteImage_GiantSpikeBall(SpriteImage_Static): # 98
    def __init__(self, parent):
        if 'GiantSpikeBall' not in ImageCache:
            LoadCastleStuff()
        super().__init__(
            parent,
            ImageCache['GiantSpikeBall'],
            (-32, -16),
            )


class SpriteImage_Swooper(SpriteImage_Static): # 100
    def __init__(self, parent):
        loadIfNotInImageCache('Swooper', 'swooper.png')
        super().__init__(
            parent,
            ImageCache['Swooper'],
            (2, 0),
            )


class SpriteImage_Bobomb(SpriteImage_Static): # 101
    def __init__(self, parent):
        loadIfNotInImageCache('Bobomb', 'bobomb.png')
        super().__init__(
            parent,
            ImageCache['Bobomb'],
            (-8, -8),
            )


class SpriteImage_Broozer(SpriteImage_Static): # 102
    def __init__(self, parent):
        loadIfNotInImageCache('Broozer', 'broozer.png')
        super().__init__(
            parent,
            ImageCache['Broozer'],
            (-9, -17),
            )


class SpriteImage_PlatformGenerator(SpriteImage_WoodenPlatform): # 103
    # TODO: Add arrows
    def updateSize(self):
        super().updateSize()
        # get width
        self.width = (((self.parent.spritedata[5] & 0xF0) >> 4) + 1) << 4

        # length=0 becomes length=4
        if self.width == 16: self.width = 64

        # override this for the "glitchy" effect caused by length=0
        if self.width == 32: self.width = 24

        self.color = 0


class SpriteImage_AmpNormal(SpriteImage_Static): # 104
    pass


class SpriteImage_Pokey(SpriteImage): # 105
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'PokeyTop' not in ImageCache:
            LoadDesertStuff()

        self.dimensions = (-4, 0, 24, 32)

    def updateSize(self):
        super().updateSize()

        # get the height
        height = self.parent.spritedata[5] & 0xF
        self.height = (height * 16) + 16 + 25
        self.yOffset = 0 - self.height + 16

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['PokeyTop'])
        painter.drawTiledPixmap(0, 37, 36, self.height*1.5 - 61, ImageCache['PokeyMiddle'])
        painter.drawPixmap(0, self.height*1.5 - 24, ImageCache['PokeyBottom'])


class SpriteImage_LinePlatform(SpriteImage_WoodenPlatform): # 106
    def __init__(self, parent):
        super().__init__(parent)
        self.yOffset = 8

    def updateSize(self):
        super().updateSize()

        # get width
        self.width = (self.parent.spritedata[5] & 0xF) << 4

        # length=0 becomes length=4
        if self.width == 0: self.width = 64

        # override this for the "glitchy" effect caused by length=0
        if self.width == 16: self.width = 24

        color = (self.parent.spritedata[4] & 0xF0) >> 4
        if color > 1: color = 0
        self.color = color


class SpriteImage_RotationControlledPassBetaPlatform(SpriteImage_UnusedBlockPlatform): # 107
    def __init__(self, parent):
        super().__init__(parent)
        self.isDark = True
        self.width = 16

    def updateSize(self):
        size = self.parent.spritedata[4]
        height = (size & 0xF) + 1

        self.yOffset = -(height - 1) * 8
        self.height = height * 16

        super().updateSize()


class SpriteImage_AmpLine(SpriteImage_Static): # 108
    pass


class SpriteImage_ChainBall(SpriteImage_SimpleDynamic): # 109
    def __init__(self, parent):
        super().__init__(parent)

        if 'ChainBallU' not in ImageCache:
            ImageCache['ChainBallU'] = GetImg('chainball_up.png')
            ImageCache['ChainBallR'] = GetImg('chainball_right.png')
            ImageCache['ChainBallD'] = GetImg('chainball_down.png')
            ImageCache['ChainBallL'] = GetImg('chainball_left.png')

    def updateSize(self):
        direction = self.parent.spritedata[5] & 3
        if direction > 3: direction = 0

        if direction % 2 == 0: # horizontal
            self.size = (96, 38)
        else: # vertical
            self.size = (37, 96)

        if direction == 0: # right
            self.image = ImageCache['ChainBallR']
            self.offset = (3, -8.5)
        elif direction == 1: # up
            self.image = ImageCache['ChainBallU']
            self.offset = (-8.5, -81.5)
        elif direction == 2: # left
            self.image = ImageCache['ChainBallL']
            self.offset = (-83, -11)
        elif direction == 3: # down
            self.image = ImageCache['ChainBallD']
            self.offset = (-11, 3.5)

        super().updateSize()


class SpriteImage_Sunlight(SpriteImage): # 110
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('Sunlight', 'sunlight.png')

        i = ImageCache['Sunlight']
        self.aux.append(AuxiliaryImage_FollowsRect(parent, i.width(), i.height()))
        self.aux[0].realimage = i
        self.aux[0].alignment = Qt.AlignTop | Qt.AlignRight
        self.parent.scene().views()[0].repaint.connect(lambda: self.moveSunlight())
        self.aux[0].hover = False


    def moveSunlight(self):
        if RealViewEnabled:
            self.aux[0].realimage = ImageCache['Sunlight']
        else:
            self.aux[0].realimage = None
            return
        zone = self.parent.getZone(True)
        if zone is None:
            self.aux[0].realimage = None
            return
        zoneRect = QtCore.QRectF(zone.objx * 1.5, zone.objy * 1.5, zone.width * 1.5, zone.height * 1.5)
        view = self.parent.scene().views()[0]
        viewRect = view.mapToScene(view.viewport().rect()).boundingRect()
        bothRect = zoneRect & viewRect

        self.aux[0].move(bothRect.x(), bothRect.y(), bothRect.width(), bothRect.height())


class SpriteImage_Blooper(SpriteImage_Static): # 111
    def __init__(self, parent):
        loadIfNotInImageCache('Blooper', 'blooper.png')
        super().__init__(
            parent,
            ImageCache['Blooper'],
            (-3, -2),
            )


class SpriteImage_BlooperBabies(SpriteImage_Static): # 112
    def __init__(self, parent):
        loadIfNotInImageCache('BlooperBabies', 'blooper_babies.png')
        super().__init__(
            parent,
            ImageCache['BlooperBabies'],
            (-5, -2),
            )


class SpriteImage_Flagpole(SpriteImage): # 113
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'Flagpole' not in ImageCache:
            LoadFlagpole()

        self.image = ImageCache['Flagpole']

        self.aux.append(AuxiliaryImage(parent, 144, 149))
        self.dimensions = (-30, -144, 46, 160)

    def updateSize(self):

        # get the info
        exit = (self.parent.spritedata[2] >> 4) & 1
        snow = self.parent.spritedata[5] & 1

        if snow == 0:
            self.aux[0].setPos(356, 97)
        else:
            self.aux[0].setPos(356, 91)

        if exit == 0:
            self.image = ImageCache['Flagpole']
            if snow == 0:
                self.aux[0].image = ImageCache['Castle']
            else:
                self.aux[0].image = ImageCache['SnowCastle']
        else:
            self.image = ImageCache['FlagpoleSecret']
            if snow == 0:
                self.aux[0].image = ImageCache['CastleSecret']
            else:
                self.aux[0].image = ImageCache['SnowCastleSecret']

        super().updateSize()


class SpriteImage_FlameCannon(SpriteImage_SimpleDynamic): # 114
    def __init__(self, parent):
        super().__init__(parent)

        if 'FlameCannonR' not in ImageCache:
            LoadFlameCannon()

        self.height = 64

    def updateSize(self):
        direction = self.parent.spritedata[5] & 15
        if direction > 3: direction = 0

        if direction == 0: # right
            del self.offset
        elif direction == 1: # left
            self.offset = (-48, 0)
        elif direction == 2: # up
            self.offset = (0, -48)
        elif direction == 3: # down
            del self.offset

        directionstr = 'RLUD'[direction]
        self.image = ImageCache['FlameCannon%s' % directionstr]

        super().updateSize()


class SpriteImage_Cheep(SpriteImage_SimpleDynamic): # 115
    def __init__(self, parent):
        super().__init__(parent)

        if 'CheepRed' not in ImageCache:
            ImageCache['CheepRed'] = GetImg('cheep_red.png')
            ImageCache['CheepGreen'] = GetImg('cheep_green.png')
            ImageCache['CheepYellow'] = GetImg('cheep_yellow.png')

        self.dimensions = (-1,-1,19,18)

    def updateSize(self):

        type = self.parent.spritedata[5] & 0xF
        if type == 1:
            self.image = ImageCache['CheepGreen']
        elif type == 8:
            self.image = ImageCache['CheepYellow']
        else:
            self.image = ImageCache['CheepRed']

        super().updateSize()


class SpriteImage_PulseFlameCannon(SpriteImage_SimpleDynamic): # 117
    def __init__(self, parent):
        super().__init__(parent)

        if 'PulseFlameCannon' not in ImageCache:
            LoadPulseFlameCannon()

        self.height = 112

    def updateSize(self):

        direction = self.parent.spritedata[5] & 15
        if direction > 3: direction = 0

        if direction == 0:
            del self.offset
        elif direction == 1:
            self.offset = (-96, 0)
        elif direction == 2:
            self.offset = (0, -96)
        elif direction == 3:
            del self.offset

        directionstr = 'RLUD'[direction]
        self.image = ImageCache['PulseFlameCannon%s' % directionstr]

        super().updateSize()


class SpriteImage_DryBones(SpriteImage_Static): # 118
    def __init__(self, parent):
        loadIfNotInImageCache('DryBones', 'drybones.png')
        super().__init__(
            parent,
            ImageCache['DryBones']
            (-7, -16),
            )


class SpriteImage_GiantDryBones(SpriteImage_Static): # 119
    def __init__(self, parent):
        loadIfNotInImageCache('GiantDryBones', 'giant_drybones.png')
        super().__init__(
            parent,
            ImageCache['GiantDryBones'],
            (-13, -24),
            )


class SpriteImage_SledgeBro(SpriteImage_Static): # 120
    def __init__(self, parent):
        loadIfNotInImageCache('SledgeBro', 'sledgebro.png')
        super().__init__(
            parent,
            ImageCache['SledgeBro'],
            (-8, -28.5),
            )


class SpriteImage_OneWayPlatform(SpriteImage_WoodenPlatform): # 122
    def updateSize(self):
        super().updateSize()
        width = self.parent.spritedata[5] & 0xF
        if width < 2: width = 2
        self.width = width * 32 + 32

        self.xOffset = self.width * -0.5

        color = (self.parent.spritedata[4] & 0xF0) >> 4
        if color > 1: color = 0
        self.color = color


class SpriteImage_UnusedCastlePlatform(SpriteImage_SimpleDynamic): # 123
    def __init__(self, parent):
        super().__init__(parent)

        if 'UnusedCastlePlatform' not in ImageCache:
            LoadUnusedStuff()

        self.image = ImageCache['UnusedCastlePlatform']
        self.size = (255, 255)

    def updateSize(self):
        super().updateSize()
        rawSize = self.parent.spritedata[4] >> 4

        if rawSize != 0:
            widthInBlocks = rawSize * 4
        else:
            widthInBlocks = 8

        topRadiusInBlocks = widthInBlocks / 10
        heightInBlocks = widthInBlocks + topRadiusInBlocks

        self.image = ImageCache['UnusedCastlePlatform'].scaled(widthInBlocks * 24, heightInBlocks * 24)

        self.dimensions = (
            self.width / 2,
            topRadiusInBlocks * 16,
            widthInBlocks * 16,
            heightInBlocks * 16,
            )


class SpriteImage_FenceKoopaHorz(SpriteImage_SimpleDynamic): # 125
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('FenceKoopaHG', 'fencekoopa_horz')
        loadIfNotInImageCache('FenceKoopaHR', 'fencekoopa_horz_red')

        self.offset = (-3, -12)

    def updateSize(self):

        color = self.parent.spritedata[5] >> 4
        if color == 1:
            self.image = ImageCache['FenceKoopaHR']
        else:
            self.image = ImageCache['FenceKoopaHG']

        super().updateSize()


class SpriteImage_FenceKoopaVert(SpriteImage): # 126
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('FenceKoopaVG', 'fencekoopa_vert')
        loadIfNotInImageCache('FenceKoopaVR', 'fencekoopa_vert_red')

        self.offset = (-2, -12)

    def updateSize(self):

        color = self.parent.spritedata[5] >> 4
        if color == 1:
            self.image = ImageCache['FenceKoopaVR']
        else:
            self.image = ImageCache['FenceKoopaVG']

        super().updateSize()


class SpriteImage_FlipFence(SpriteImage_Static): # 127
    def __init__(self, parent):
        loadIfNotInImageCache('FlipFence', 'flipfence.png')
        super().__init__(
            parent,
            ImageCache['FlipFence'],
            (-4, -8),
            )


class SpriteImage_FlipFenceLong(SpriteImage_Static): # 128
    def __init__(self, parent):
        loadIfNotInImageCache('FlipFenceLong', 'flipfence_long.png')
        super().__init__(
            parent,
            ImageCache['FlipFenceLong'],
            (6, 0),
            )


class SpriteImage_4Spinner(SpriteImage_Static): # 129
    def __init__(self, parent):
        loadIfNotInImageCache('4Spinner', '4spinner.png')
        super().__init__(
            parent,
            ImageCache['4Spinner'],
            (-62, -48),
            )


class SpriteImage_Wiggler(SpriteImage_Static): # 130
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Wiggler'],
            (0, -12),
            )


class SpriteImage_Boo(SpriteImage): # 131
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        loadIfNotInImageCache('Boo1', 'boo1.png')

        self.aux.append(AuxiliaryImage(parent, 50, 51))
        self.aux[0].image = ImageCache['Boo1']
        self.aux[0].setPos(-6, -6)

        self.dimensions = (-1, -4, 22, 22)


class SpriteImage_UnusedBlockPlatform1(SpriteImage_UnusedBlockPlatform): # 132
    def updateSize(self):
        super().updateSize()
        self.width = ((self.parent.spritedata[5] & 0xF) + 1) * 16
        self.height = ((self.parent.spritedata[5] >> 4)  + 1) * 16


class SpriteImage_StalagmitePlatform(SpriteImage_Static): # 133
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('StalagmitePlatformTop', 'stalagmite_platform_top.png')
        loadIfNotInImageCache('StalagmitePlatformBottom', 'stalagmite_platform_bottom.png')

        self.aux.append(AuxiliaryImage(parent, 48, 156))
        self.aux[0].image = ImageCache['StalagmitePlatformBottom']
        self.aux[0].setPos(24, 60)

        self.image = ImageCache['StalagmitePlatformTop']
        self.dimensions = (0,-8,64,40)


class SpriteImage_Crow(SpriteImage_Static): # 134
    def __init__(self, parent):
        loadIfNotInImageCache('Crow', 'crow.png')
        super().__init__(
            parent,
            ImageCache['Crow'],
            (-3, -2),
            )


class SpriteImage_HangingPlatform(SpriteImage_Static): # 135
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('HangingPlatformTop', 'hanging_platform_top.png')
        loadIfNotInImageCache('HangingPlatformBottom', 'hanging_platform_bottom.png')

        self.aux.append(AuxiliaryImage(parent, 11, 378))
        self.aux[0].image = ImageCache['HangingPlatformTop']
        self.aux[0].setPos(138, -378)

        self.image = ImageCache['HangingPlatformBottom']
        self.size = (192, 32)


class SpriteImage_RotBulletLauncher(SpriteImage): # 136
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        loadIfNotInImageCache('RotLauncherCannon', 'bullet_cannon_rot_0.png')
        loadIfNotInImageCache('RotLauncherPivot', 'bullet_cannon_rot_1.png')

        self.dimensions = (-4, 0, 24, 16)

    def updateSize(self):
        super().updateSize()
        pieces = self.parent.spritedata[3] & 15
        self.yOffset = -pieces * 16
        self.height = (pieces + 1) * 16

    def paint(self, painter):
        super().paint(painter)

        pieces = (self.parent.spritedata[3] & 15) + 1
        pivot1_4 = self.parent.spritedata[4] & 15
        pivot5_8 = self.parent.spritedata[4] >> 4
        startleft1_4 = self.parent.spritedata[5] & 15
        startleft5_8 = self.parent.spritedata[5] >> 4

        pivots = [pivot1_4, pivot5_8]
        startleft = [startleft1_4, startleft5_8]

        ysize = self.height * 1.5

        for piece in range(pieces):
            bitpos = 2 ** (piece % 4)
            if pivots[int(piece / 4)] & bitpos:
                painter.drawPixmap(5, ysize - (piece * 24) - 24, ImageCache['RotLauncherPivot'])
            else:
                xo = 6
                image = ImageCache['RotLauncherCannon']
                if startleft[int(piece / 4)] & bitpos:
                    transform = QtGui.QTransform()
                    transform.rotate(180)
                    image = QtGui.QPixmap(image.transformed(transform))
                    xo = 0
                painter.drawPixmap(xo, ysize - (piece + 1) * 24, image)


class SpriteImage_SpikedStakeDown(SpriteImage_SpikedStake): # 137
    def __init__(self, parent):
        super().__init__(parent)
        self.dir = 'down'
        self.aux.append(AuxiliaryTrackObject(parent, 16, 64, AuxiliaryTrackObject.Vertical))

        self.dimensions = (0, 16 - self.SpikeLength, 66, self.SpikeLength)


class SpriteImage_Water(SpriteImage): # 138
    def __init__(self, parent):
        super().__init__(parent)
        self.updateSceneAfterPaint = True

        if 'LiquidWater' not in ImageCache:
            ImageCache['LiquidWater'] = GetImg('liquid_water.png')
            ImageCache['LiquidWaterCrest'] = GetImg('liquid_water_crest.png')
            ImageCache['LiquidWaterRise'] = GetImg('liquid_water_rise.png')
            ImageCache['LiquidWaterRiseCrest'] = GetImg('liquid_water_rise_crest.png')

    def updateSize(self):
        super().updateSize()
        self.parent.updateScene()

    def realViewZone(self, painter, zoneRect, viewRect):

        if self.parent.spritedata[5]: return

        # (0, 0) is the top-left corner of the zone

        drawCrest = self.parent.spritedata[4] & 15 == 0
        RH = (self.parent.spritedata[3] & 0xF) << 4
        RH |= self.parent.spritedata[4] >> 4
        risingHeight = RH

        # Get the width and height of the zone
        zx = zoneRect.topLeft().x()
        zy = zoneRect.topLeft().y()
        zw = zoneRect.width()
        zh = zoneRect.height()

        # Get the y pos of the self.parent
        sy = self.parent.objy

        # Get pixmaps
        mid = ImageCache['LiquidWater']
        crest = ImageCache['LiquidWaterCrest']
        rise = ImageCache['LiquidWaterRiseCrest']
        riseCrestless = ImageCache['LiquidWaterRise']

        paintLiquid(painter, crest, mid, rise, riseCrestless, zx, zy, zw, zh, sy, drawCrest, risingHeight)



class SpriteImage_Lava(SpriteImage): # 139
    def __init__(self, parent):
        super().__init__(parent)
        self.updateSceneAfterPaint = True

        if 'LiquidLava' not in ImageCache:
            ImageCache['LiquidLava'] = GetImg('liquid_lava.png')
            ImageCache['LiquidLavaCrest'] = GetImg('liquid_lava_crest.png')
            ImageCache['LiquidLavaRise'] = GetImg('liquid_lava_rise.png')
            ImageCache['LiquidLavaRiseCrest'] = GetImg('liquid_lava_rise_crest.png')

    def updateSize(self):
        super().updateSize()
        self.parent.updateScene()

    def realViewZone(self, painter, zoneRect, viewRect):

        if self.parent.spritedata[5]: return

        # (0, 0) is the top-left corner of the zone

        drawCrest = self.parent.spritedata[4] & 15 == 0
        RH = (self.parent.spritedata[3] & 0xF) << 4
        RH |= self.parent.spritedata[4] >> 4
        fall = (self.parent.spritedata[2] >> 4) > 7
        if fall: RH = -RH
        risingHeight = RH

        # Get the width and height of the zone
        zx = zoneRect.topLeft().x()
        zy = zoneRect.topLeft().y()
        zw = zoneRect.width()
        zh = zoneRect.height()

        # Get the y pos of the self.parent
        sy = self.parent.objy

        # Get pixmaps
        mid = ImageCache['LiquidLava']
        crest = ImageCache['LiquidLavaCrest']
        rise = ImageCache['LiquidLavaRiseCrest']
        riseCrestless = ImageCache['LiquidLavaRise']

        paintLiquid(painter, crest, mid, rise, riseCrestless, zx, zy, zw, zh, sy, drawCrest, risingHeight)


class SpriteImage_SpikedStakeUp(SpriteImage_SpikedStake): # 140
    def __init__(self, parent):
        super().__init__(parent)
        self.dir = 'up'
        self.aux.append(AuxiliaryTrackObject(parent, 16, 64, AuxiliaryTrackObject.Vertical))

        self.dimensions = (0, 0, 66, self.SpikeLength)


class SpriteImage_SpikedStakeRight(SpriteImage_SpikedStake): # 141
    def __init__(self, parent):
        super().__init__(parent)
        self.dir = 'right'
        self.aux.append(AuxiliaryTrackObject(parent, 64, 16, AuxiliaryTrackObject.Horizontal))

        self.dimensions = (16 - self.SpikeLength, 0, self.SpikeLength, 66)


class SpriteImage_SpikedStakeLeft(SpriteImage_SpikedStake): # 142
    def __init__(self, parent):
        super().__init__(parent)
        self.dir = 'left'
        self.aux.append(AuxiliaryTrackObject(parent, 64, 16, AuxiliaryTrackObject.Horizontal))

        self.dimensions = (0, 0, self.SpikeLength, 66)


class SpriteImage_Arrow(SpriteImage_SimpleDynamic): # 143
    def __init__(self, parent):
        super().__init__(parent)

        if 'Arrow0' not in ImageCache:
            for i in range(8):
                ImageCache['Arrow%d' % i] = GetImg('arrow_%d.png' % i)

    def updateSize(self):
        ArrowOffsets = [(3,0), (5,4), (1,3), (5,-1), (3,0), (-1,-1), (0,3), (-1,4)]

        direction = self.parent.spritedata[5] & 7
        self.image = ImageCache['Arrow%d' % direction]

        self.width = self.image.width() / 1.5
        self.height = self.image.height() / 1.5
        self.offset = ArrowOffsets[direction]

        super().updateSize()


class SpriteImage_RedCoin(SpriteImage_Static): # 144
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['RedCoin'],
            )


class SpriteImage_FloatingBarrel(SpriteImage_Static): # 145
    def __init__(self, parent):
        loadIfNotInImageCache('FloatingBarrel', 'barrel_floating.png')
        super().__init__(
            parent,
            ImageCache['FloatingBarrel'],
            (-16, -9),
            )


class SpriteImage_ChainChomp(SpriteImage_Static): # 146
    def __init__(self, parent):
        loadIfNotInImageCache('ChainChomp', 'chain_chomp.png')
        super().__init__(
            parent,
            ImageCache['ChainChomp'],
            (-90, -32),
            )


class SpriteImage_Coin(SpriteImage_SimpleDynamic): # 147
    def __init__(self, parent):
        super().__init__(parent)

        if 'CoinF' not in ImageCache:
            pix = QtGui.QPixmap(16, 16)
            pix.fill(Qt.transparent)
            paint = QtGui.QPainter(pix)
            paint.setOpacity(0.9)
            paint.drawPixmap(0, 0, GetImg('iceblock00.png'))
            paint.setOpacity(0.6)
            paint.drawPixmap(0, 0, ImageCache['Coin'])
            del paint
            ImageCache['CoinF'] = pix

    def updateSize(self):
        flag = self.parent.spritedata[5] & 0xF

        if flag == 0xF:
            self.image = ImageCache['CoinF']
        else:
            self.image = ImageCache['Coin']

        super().updateSize()


class SpriteImage_Spring(SpriteImage_Static): # 148
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Spring'],
            )


class SpriteImage_RotationControllerSpinning(SpriteImage): # 149
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.setZValue(100000)


class SpriteImage_Puffer(SpriteImage_Static): # 151
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Puffer'],
            (-16, -18),
            )


class SpriteImage_StarCoinLineControlled(SpriteImage_StarCoin): # 155
    pass


class SpriteImage_RedCoinRing(SpriteImage): # 156
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        loadIfNotInImageCache('RedCoinRing', 'redcoinring.png')

        self.aux.append(AuxiliaryImage(parent, 243, 248))
        self.aux[0].image = ImageCache['RedCoinRing']
        self.aux[0].setPos(-10, -15)
        self.aux[0].hover = False

        self.dimensions = (-10, -8, 37, 48)


class SpriteImage_BigBrick(SpriteImage_SimpleDynamic): # 157
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('BigBrick', 'big_brick.png')
        loadIfNotInImageCache('ShipKey', 'ship_key.png')
        loadIfNotInImageCache('5Coin', '5_coin.png')
        if 'YoshiFire' not in ImageCache:
            pix = QtGui.QPixmap(48, 24)
            pix.fill(Qt.transparent)
            paint = QtGui.QPainter(pix)
            paint.drawPixmap(ImageCache['Blocks'][9], 0, 0)
            paint.drawPixmap(ImageCache['Blocks'][3], 24, 0)
            del paint
            ImageCache['YoshiFire'] = pix

        self.image = ImageCache['BigBrick']
        self.size = (48, 48)

    def paint(self, painter):
        super().paint(painter)

        power = self.parent.spritedata[5] & 15

        images = [
            None,                     # empty
            ImageCache['Blocks'][1],  # coin
            ImageCache['Blocks'][2],  # mushroom
            ImageCache['Blocks'][3],  # fire
            ImageCache['Blocks'][4],  # propeller
            ImageCache['Blocks'][5],  # penguin
            ImageCache['Blocks'][6],  # mini
            ImageCache['Blocks'][7],  # star
            None,                     # empty
            ImageCache['YoshiFire'],  # yoshi + fire
            ImageCache['5Coin'],      # 5coin
            ImageCache['Blocks'][11], # 1up
            None,                     # empty
            None,                     # empty
            ImageCache['ShipKey'],    # key
            ImageCache['Blocks'][15], # ice
            ]

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

        painter.drawPixmap(0, 0, ImageCache['BigBrick'])
        if images[power] != None:
            painter.drawPixmap(x, y, images[power])


class SpriteImage_FireSnake(SpriteImage_SimpleDynamic): # 158
    def __init__(self, parent):
        super().__init__(parent)

        if 'FireSnake' not in ImageCache:
            LoadFireSnake()

    def updateSize(self):

        move = self.parent.spritedata[5] & 15
        if move == 1:
            del self.size
            self.yOffset = 0
            self.image = ImageCache['FireSnakeWait']
        else:
            self.size = (20, 32)
            self.yOffset = -16
            self.image = ImageCache['FireSnake']

        super().updateSize()


class SpriteImage_UnusedBlockPlatform2(SpriteImage_UnusedBlockPlatform): # 160
    def updateSize(self):
        super().updateSize()
        self.width = ((self.parent.spritedata[5] & 0xF) + 1) * 16
        self.height = ((self.parent.spritedata[5] >> 4)  + 1) * 16


class SpriteImage_PipeBubbles(SpriteImage_SimpleDynamic): # 161
    def __init__(self, parent):
        super().__init__(parent)

        if 'PipeBubblesU' not in ImageCache:
            LoadPipeBubbles()

        self.dimensions = (0, -52, 32, 53)

    def updateSize(self):

        direction = self.parent.spritedata[5] & 15
        if direction == 0 or direction > 3:
            self.dimensions = (0, -52, 32, 53)
            direction = 'U'
        elif direction == 1:
            self.dimensions = (0, 16, 32, 53)
            direction = 'D'
        elif direction == 2:
            self.dimensions = (16, -16, 53, 32)
            direction = 'R'
        elif direction == 3:
            self.dimensions = (-52, -16, 53, 32)
            direction = 'L'

        self.image = ImageCache['PipeBubbles%s' % direction]

        super().updateSize()


class SpriteImage_BlockTrain(SpriteImage): # 166
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        loadIfNotInImageCache('BlockTrain', 'block_train.png')

    def updateSize(self):
        super().updateSize()
        length = self.parent.spritedata[5] & 15
        self.width = (length + 3) * 16

    def paint(self, painter):
        super().paint(painter)

        endpiece = ImageCache['BlockTrain']
        painter.drawPixmap(0, 0, endpiece)
        painter.drawTiledPixmap(24, 0, (self.width * 1.5) - 48, 24, ImageCache['BlockTrain'])
        painter.drawPixmap((self.width * 1.5) - 24, 0, endpiece)


class SpriteImage_ChestnutGoomba(SpriteImage_Static): # 170
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ChestnutGoomba'],
            (-6, -8),
            )


class SpriteImage_PowerupBubble(SpriteImage): # 171
    def __init__(self, parent):
        loadIfNotInImageCache('PowerupBubble', 'powerup_bubble.png')
        super().__init__(
            parent,
            ImageCache['PowerupBubble'],
            (-8, -8),
            )


class SpriteImage_ScrewMushroomWithBolt(SpriteImage_ScrewMushroom): # 172
    def __init__(self, parent):
        super().__init__(parent)
        self.hasBolt = True


class SpriteImage_GiantFloatingLog(SpriteImage_Static): # 173
    def __init__(self, parent):
        loadIfNotInImageCache('GiantFloatingLog', 'giant_floating_log.png')
        super().__init__(
            parent,
            ImageCache['GiantFloatingLog'],
            (-152, -32),
            )


class SpriteImage_OneWayGate(SpriteImage): # 174
    def __init__(self, parent):
        super().__init__(parent)

        if '1WayGate00' not in ImageCache:
            LoadUnusedStuff()

        self.image = ImageCache['1WayGate03']

    def updateSize(self):

        flag = (self.parent.spritedata[5] >> 4) & 1
        direction = self.parent.spritedata[5] & 3
        self.image = ImageCache['1WayGate%d%d' % (flag, direction)]

        if direction > 3: direction = 3
        self.offset = (
            (0, -24),
            (0, 0),
            (-24, 0),
            (0, 0),
            )[direction]

        super().updateSize()


class SpriteImage_FlyingQBlock(SpriteImage): # 175
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('FlyingQBlock', 'flying_qblock.png')

        self.dimensions = (-12, -16, 42, 32)

    def paint(self, painter):
        super().paint(painter)

        color = self.parent.spritedata[4] >> 4
        if color == 0 or color > 3:
            block = 9
        elif color == 1:
            block = 59
        elif color == 2:
            block = 109
        elif color == 3:
            block = 159

        painter.drawPixmap(ImageCache['FlyingQBlock'], 0, 0)
        painter.drawPixmap(ImageCache['Overrides'][block], 18, 23)


class SpriteImage_RouletteBlock(SpriteImage_Static): # 176
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['RouletteBlock'],
            (-6, -6),
            )


class SpriteImage_FireChomp(SpriteImage): # 177
    def __init__(self, parent):
        loadIfNotInImageCache('FireChomp', 'fire_chomp.png')
        super().__init__(
            parent,
            ImageCache['FireChomp'],
            (-2, -20),
            )


class SpriteImage_ScalePlatform(SpriteImage): # 178
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'WoodenPlatformL' not in ImageCache:
            LoadPlatformImages()
        if 'ScaleRopeH' not in ImageCache:
            ImageCache['ScaleRopeH'] = GetImg('scale_rope_horz.png')
            ImageCache['ScaleRopeV'] = GetImg('scale_rope_vert.png')
            ImageCache['ScalePulley'] = GetImg('scale_pulley.png')

        self.dimensions = (0, -10, 150, 150)

    def updateSize(self):
        super().updateSize()

        info1 = self.parent.spritedata[4]
        info2 = self.parent.spritedata[5]
        self.parent.platformWidth = (info1 & 0xF0) >> 4
        if self.parent.platformWidth > 12: self.parent.platformWidth = -1

        self.parent.ropeLengthLeft = info1 & 0xF
        self.parent.ropeLengthRight = (info2 & 0xF0) >> 4
        self.parent.ropeWidth = info2 & 0xF

        ropeWidth = self.parent.ropeWidth * 16
        platformWidth = (self.parent.platformWidth + 3) * 16
        self.width = ropeWidth + platformWidth

        maxRopeHeight = max(self.parent.ropeLengthLeft, self.parent.ropeLengthRight)
        self.height = maxRopeHeight * 16 + 19
        if maxRopeHeight == 0: self.height += 8

        self.xOffset = -(self.parent.platformWidth + 3) * 8

    def paint(self, painter):
        super().paint(painter)

        # this is FUN!! (not)
        ropeLeft = self.parent.ropeLengthLeft * 24 + 4
        if self.parent.ropeLengthLeft == 0: ropeLeft += 12

        ropeRight = self.parent.ropeLengthRight * 24 + 4
        if self.parent.ropeLengthRight == 0: ropeRight += 12

        ropeWidth = self.parent.ropeWidth * 24 + 8
        platformWidth = (self.parent.platformWidth + 3) * 24

        ropeX = platformWidth / 2 - 4

        painter.drawTiledPixmap(ropeX + 8, 0, ropeWidth - 16, 8, ImageCache['ScaleRopeH'])

        ropeVertImage = ImageCache['ScaleRopeV']
        painter.drawTiledPixmap(ropeX, 8, 8, ropeLeft - 8, ropeVertImage)
        painter.drawTiledPixmap(ropeX + ropeWidth - 8, 8, 8, ropeRight - 8, ropeVertImage)

        pulleyImage = ImageCache['ScalePulley']
        painter.drawPixmap(ropeX, 0, pulleyImage)
        painter.drawPixmap(ropeX + ropeWidth - 20, 0, pulleyImage)

        platforms = [(0, ropeLeft), (ropeX + ropeWidth - int(platformWidth / 2) - 4, ropeRight)]
        for x, y in platforms:
            painter.drawPixmap(x, y, ImageCache['WoodenPlatformL'])
            painter.drawTiledPixmap(x + 27, y, (platformWidth - 51), 24, ImageCache['WoodenPlatformM'])
            painter.drawPixmap(x + platformWidth - 24, y, ImageCache['WoodenPlatformR'])


class SpriteImage_SpecialExit(SpriteImage): # 179
    def __init__(self, parent):
        super().__init__(parent)
        self.aux.append(AuxiliaryRectOutline(parent, 0, 0))

    def updateSize(self):
        super().updateSize()

        w = (self.parent.spritedata[4] & 15) + 1
        h = (self.parent.spritedata[5] >> 4) + 1
        if w == 1 and h == 1: # no point drawing a 1x1 outline behind the self.parent
            self.aux[0].setSize(0,0)
            return
        self.aux[0].setSize(w * 24, h * 24)


class SpriteImage_CheepChomp(SpriteImage_Static): # 180
    def __init__(self, parent):
        loadIfNotInImageCache('CheepChomp', 'cheepchomp.png')
        super().__init__(
            parent,
            ImageCache['CheepChomp'],
            (-32, -16),
            )


class SpriteImage_EventDoor(SpriteImage_Door): # 182
    def __init__(self, parent):
        super().__init__(parent)
        self.alpha = 0.5


class SpriteImage_ToadBalloon(SpriteImage_Static): # 185
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ToadBalloon'],
            (-4, -4),
            )


class SpriteImage_PlayerBlock(SpriteImage_Static): # 187
    def __init__(self, parent):
        loadIfNotInImageCache('PlayerBlock', 'playerblock.png')
        super().__init__(
            parent,
            ImageCache['PlayerBlock'],
            )


class SpriteImage_MidwayPoint(SpriteImage_Static): # 188
    def __init__(self, parent):
        if 'MidwayFlag' not in ImageCache:
            LoadFlagpole()
        super().__init__(
            parent,
            ImageCache['MidwayFlag'],
            (0, -37),
            )


class SpriteImage_LarryKoopa(SpriteImage_Static): # 189
    def __init__(self, parent):
        if 'LarryKoopa' not in ImageCache:
            LoadBosses()
        super().__init__(
            parent,
            ImageCache['LarryKoopa'],
            (-17, -33),
            )


class SpriteImage_TiltingGirderUnused(SpriteImage_Static): # 190
    def __init__(self, parent):
        if 'TiltingGirder' not in ImageCache:
            LoadPlatformImages()
        super().__init__(
            parent,
            ImageCache['TiltingGirder'],
            (0, -18),
            )


class SpriteImage_TileEvent(SpriteImage): # 191
    def __init__(self, parent):
        super().__init__(parent)
        self.aux.append(AuxiliaryRectOutline(parent, 0, 0))

    def updateSize(self):
        super().updateSize()

        w = self.parent.spritedata[5] >> 4
        h = self.parent.spritedata[5] & 0xF
        if w == 0: w = 1
        if h == 0: h = 1
        if w == 1 and h == 1: # no point drawing a 1x1 outline behind the self.parent
            self.aux[0].setSize(0,0)
            return
        self.aux[0].setSize(w * 24, h * 24)


class SpriteImage_Urchin(SpriteImage_Static): # 193
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Urchin'],
            (-12, -14),
            )


class SpriteImage_MegaUrchin(SpriteImage_Static): # 194
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['MegaUrchin'],
            (-40, -46),
            )


class SpriteImage_HuckitCrab(SpriteImage_SimpleDynamic): # 195
    def __init__(self, parent):
        super().__init__(parent)
        self.dimensions = (0, -3, 32, 19)

    def updateSize(self):
        info = self.parent.spritedata[5]

        if info == 1:
            self.image = ImageCache['HuckitCrabR']
            self.xOffset = 0
        else:
            if info == 13:
                self.image = ImageCache['HuckitCrabR']
                self.xOffset = 0
            else:
                self.image = ImageCache['HuckitCrabL']
                self.xOffset = -16

        super().updateSize()


class SpriteImage_Fishbones(SpriteImage_SimpleDynamic): # 196
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = (0, -2)

    def updateSize(self):

        direction = self.parent.spritedata[5] >> 4
        if direction == 1:
            self.image = ImageCache['FishbonesR']
        else:
            self.image = ImageCache['FishbonesL']

        super().updateSize()


class SpriteImage_Clam(SpriteImage_SimpleDynamic): # 197
    def __init__(self, parent):
        super().__init__(parent)

        self.dimensions = (-26, -53, 70, 70)

        if 'PSwitch' not in ImageCache:
            LoadSwitches()
        if 'ClamEmpty' not in ImageCache:
            LoadClam()

    def updateSize(self):

        holds = self.parent.spritedata[5] & 0xF
        switchdir = self.parent.spritedata[4] & 0xF

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

        self.image = ImageCache['Clam' + holdsStr]

        super().updateSize()


class SpriteImage_Giantgoomba(SpriteImage_Static): # 198
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Giantgoomba'],
            (-6, -19),
            )


class SpriteImage_Megagoomba(SpriteImage_Static): # 199
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Megagoomba'],
            (-11, -37),
            )


class SpriteImage_Microgoomba(SpriteImage_Static): # 200
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Microgoomba'],
            (4, 8),
            )


class SpriteImage_Icicle(SpriteImage_SimpleDynamic): # 201
    def __init__(self, parent):
        super().__init__(parent)
        if 'IcicleSmall' not in ImageCache:
            LoadIceStuff()

    def updateSize(self):

        size = self.parent.spritedata[5] & 1
        if size == 0:
            self.image = ImageCache['IcicleSmallS']
        else:
            self.image = ImageCache['IcicleLargeS']

        super().updateSize()


class SpriteImage_MGCannon(SpriteImage_Static): # 202
    def __init__(self, parent):
        if 'MGCannon' not in ImageCache:
            LoadMinigameStuff()
        super().__init__(
            parent,
            ImageCache['MGCannon'],
            (-12, -42),
            )


class SpriteImage_MGChest(SpriteImage_Static): # 203
    def __init__(self, parent):
        if 'MGChest' not in ImageCache:
            LoadMinigameStuff()
        super().__init__(
            parent,
            ImageCache['MGChest'],
            (-12, -11),
            )


class SpriteImage_GiantBubble(SpriteImage): # 205
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'GiantBubble0' not in ImageCache:
            LoadGiantBubble()

        self.dimensions = (-61,- 68, 122, 137)

    def updateSize(self):
        super().updateSize()

        self.shape = self.parent.spritedata[4] >> 4
        self.direction = self.parent.spritedata[5] & 15
        arrow = None

        if self.shape == 0 or self.shape > 3:
            self.size = (122, 137)
        elif self.shape == 1:
            self.size = (76, 170)
        elif self.shape == 2:
            self.size = (160, 81)

        self.xoffset = -(self.xsize / 2) + 8
        self.yoffset = -(self.ysize / 2) + 8

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['GiantBubble%d' % self.parent.shape])


class SpriteImage_Zoom(SpriteImage): # 206
    def __init__(self, parent):
        super().__init__(parent)
        self.aux.append(AuxiliaryRectOutline(parent, 0, 0))

    def updateSize(self):
        super().updateSize()

        w = self.parent.spritedata[5]+1
        h = self.parent.spritedata[4]+1
        if w == 1 and h == 1: # no point drawing a 1x1 outline behind the self.parent
            self.aux[0].setSize(0,0,0,0)
            return
        self.aux[0].setSize(w*24, h*24, 0, 24-(h*24))


class SpriteImage_QBlock(SpriteImage_Block): # 207
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 49


class SpriteImage_QBlockUnused(SpriteImage_Block): # 208
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 49
        self.twelveIsMushroom = True


class SpriteImage_BrickBlock(SpriteImage_Block): # 209
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 48


class SpriteImage_RollingHill(SpriteImage): # 212
    RollingHillSizes = [0, 18*16, 32*16, 50*16, 64*16, 10*16, 14*16, 20*16, 0, 0, 0, 0, 0, 0, 0, 0]
    def __init__(self, parent):
        super().__init__(parent)

        size = (self.parent.spritedata[3] >> 4) & 0xF
        realSize = self.RollingHillSizes[size]

        self.aux.append(AuxiliaryCircleOutline(parent, realSize))

    def updateSize(self):
        super().updateSize()

        size = (self.parent.spritedata[3] >> 4) & 0xF
        if size != 0: realSize = self.RollingHillSizes[size]
        else:
            adjust = self.parent.spritedata[4] & 0xF
            realSize = 32 * (adjust + 1)

        self.aux[0].setSize(realSize)
        self.aux[0].update()


class SpriteImage_FreefallPlatform(SpriteImage_Static): # 214
    def __init__(self, parent):
        loadIfNotInImageCache('FreefallGH', 'freefall_gh_platform.png')
        super().__init__(
            parent,
            ImageCache['FreefallGH'],
            )


class SpriteImage_Poison(SpriteImage): # 216
    def __init__(self, parent):
        super().__init__(parent)
        self.updateSceneAfterPaint = True

        if 'LiquidPoison' not in ImageCache:
            ImageCache['LiquidPoison'] = GetImg('liquid_poison.png')
            ImageCache['LiquidPoisonCrest'] = GetImg('liquid_poison_crest.png')
            ImageCache['LiquidPoisonRise'] = GetImg('liquid_poison_rise.png')
            ImageCache['LiquidPoisonRiseCrest'] = GetImg('liquid_poison_rise_crest.png')

    def updateSize(self):
        super().updateSize()
        self.parent.updateScene()

    def realViewZone(self, painter, zoneRect, viewRect):

        if self.parent.spritedata[5]: return

        # (0, 0) is the top-left corner of the zone

        drawCrest = self.parent.spritedata[4] & 15 == 0
        RH = (self.parent.spritedata[3] & 0xF) << 4
        RH |= self.parent.spritedata[4] >> 4
        fall = (self.parent.spritedata[2] >> 4) > 7
        if fall: RH = -RH # make it negative
        risingHeight = RH

        # Get the width and height of the zone
        zx = zoneRect.topLeft().x()
        zy = zoneRect.topLeft().y()
        zw = zoneRect.width()
        zh = zoneRect.height()

        # Get the y pos of the self.parent
        sy = self.parent.objy

        # Get pixmaps
        mid = ImageCache['LiquidPoison']
        crest = ImageCache['LiquidPoisonCrest']
        rise = ImageCache['LiquidPoisonRiseCrest']
        riseCrestless = ImageCache['LiquidPoisonRise']

        paintLiquid(painter, crest, mid, rise, riseCrestless, zx, zy, zw, zh, sy, drawCrest, risingHeight)


class SpriteImage_LineBlock(SpriteImage): # 219
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        loadIfNotInImageCache('LineBlock', 'lineblock.png')
        self.aux.append(AuxiliaryImage(parent, 24, 24))
        self.aux[0].setPos(0, 32)

    def updateSize(self):

        direction = self.parent.spritedata[4] >> 4
        widthA = self.parent.spritedata[5] & 15
        widthB = self.parent.spritedata[5] >> 4
        if direction & 1:
            # reverse them if going down
            widthA, widthB = widthB, widthA

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

        imgA = QtGui.QPixmap(widthA * 24, 24)
        imgB = QtGui.QPixmap(widthB * 24, 24)
        imgA.fill(Qt.transparent)
        imgB.fill(Qt.transparent)
        painterA = QtGui.QPainter(imgA)
        painterB = QtGui.QPainter(imgB)
        painterA.setOpacity(aA)
        painterB.setOpacity(aB)

        # We could use range(totalBlocks) in the overlay loop, but that gives
        # us a linear-ly sorted list. The game doesn't do it that way so we
        # need to rearrange the list.
        iterList = range(totalBlocks)
        halfList = range(totalBlocks)[(len(iterList)/2):len(iterList)]
        for i in range(len(halfList)):
            iterList[len(iterList)-(i+1)] = halfList[i]

        for i in iterList:
            painterA.drawPixmap(blockimg, 24 * i, 0)
            painterB.drawPixmap(blockimg, 24 * i, 0)


        if widthA >= 1:
            self.width = widthA*16
        else:
            self.width = 16
        xposA = (widthA*-8)+8
        if widthA == 0: xposA = 0
        xposB = (widthA-widthB)*12
        if widthA == 0: xposB = 0
        if direction == 1:
            yposB = 96
        else:
            yposB = -96

        self.image = imgA
        self.xOffset = xposA
        self.aux[0].setSize(imgB.width(), imgB.height())
        self.aux[0].image = imgB
        self.aux[0].setPos(xposB, yposB)

        super().updateSize()


class SpriteImage_InvisibleBlock(SpriteImage_Block): # 221
    pass


class SpriteImage_ConveyorSpike(SpriteImage_Static): # 222
    def __init__(self, parent):
        loadIfNotInImageCache('SpikeU', 'spike_up.png')
        super().__init__(
            parent,
            ImageCache['SpikeU'],
            )


class SpriteImage_SpringBlock(SpriteImage_SimpleDynamic): # 223
    def updateSize(self):

        type = self.parent.spritedata[5] & 1
        if type == 0:
            self.image = ImageCache['SpringBlock1']
        else:
            self.image = ImageCache['SpringBlock2']

        super().updateSize()


class SpriteImage_JumboRay(SpriteImage): # 224
    def __init__(self, parent):
        super().__init__(parent)

        if 'JumboRay' not in ImageCache:
            Ray = GetImg('jumbo_ray.png', True)
            ImageCache['JumboRayL'] = QtGui.QPixmap.fromImage(Ray)
            ImageCache['JumboRayR'] = QtGui.QPixmap.fromImage(Ray.mirrored(True, False))

        self.size = (171, 79)

    def updateSize(self):

        flyleft = self.parent.spritedata[4] & 15
        if flyleft:
            self.xOffset = 0
            self.image = ImageCache['JumboRayL']
        else:
            self.xOffset = -152
            self.image = ImageCache['JumboRayR']

        super().updateSize()


class SpriteImage_PipeCannon(SpriteImage): # 227
    def __init__(self, parent):
        super().__init__(parent)

        if 'PipeCannon' not in ImageCache:
            LoadPipeCannon()

        # self.aux[0] is the pipe image
        self.aux.append(AuxiliaryImage(parent, 24, 24))
        self.aux[0].hover = False

        # self.aux[1] is the trajectory indicator
        self.aux.append(AuxiliaryPainterPath(parent, QtGui.QPainterPath(), 24, 24))
        self.aux[1].fillFlag = False
        self.aux[1].hover = False
        self.aux[0].setZValue(self.aux[1].zValue() + 1)

        self.size = (32, 64)

    def updateSize(self):
        super().updateSize()

        fireDirection = (self.parent.spritedata[5] & 0xF) % 7

        self.aux[0].image = ImageCache['PipeCannon%d' % (fireDirection)]

        if fireDirection == 0:
            # 30 deg to the right
            self.aux[0].setSize(84, 101, 0, -5)
            path = QtGui.QPainterPath(QtCore.QPoint(0, 184))
            path.cubicTo(QtCore.QPoint(152, -24), QtCore.QPoint(168, -24), QtCore.QPoint(264, 48))
            path.lineTo(QtCore.QPoint(480, 216))
            self.aux[1].setSize(480, 216, 24, -120)
        elif fireDirection == 1:
            # 30 deg to the left
            self.aux[0].setSize(85, 101, -36, -5)
            path = QtGui.QPainterPath(QtCore.QPoint(480 - 0, 184))
            path.cubicTo(QtCore.QPoint(480 - 152, -24), QtCore.QPoint(480 - 168, -24), QtCore.QPoint(480 - 264, 48))
            path.lineTo(QtCore.QPoint(480 - 480, 216))
            self.aux[1].setSize(480, 216, -480 + 24, -120)
        elif fireDirection == 2:
            # 15 deg to the right
            self.aux[0].setSize(60, 102, 0, -6)
            path = QtGui.QPainterPath(QtCore.QPoint(0, 188))
            path.cubicTo(QtCore.QPoint(36, -36), QtCore.QPoint(60, -36), QtCore.QPoint(96, 84))
            path.lineTo(QtCore.QPoint(144, 252))
            self.aux[1].setSize(144, 252, 30, -156)
        elif fireDirection == 3:
            # 15 deg to the left
            self.aux[0].setSize(61, 102, -12, -6)
            path = QtGui.QPainterPath(QtCore.QPoint(144 - 0, 188))
            path.cubicTo(QtCore.QPoint(144 - 36, -36), QtCore.QPoint(144 - 60, -36), QtCore.QPoint(144 - 96, 84))
            path.lineTo(QtCore.QPoint(144 - 144, 252))
            self.aux[1].setSize(144, 252, -144 + 18, -156)
        elif fireDirection == 4:
            # Straight up
            self.aux[0].setSize(135, 132, -32 - 6 - 4, -16 - 6 - 8 - 4 - 1)
            path = QtGui.QPainterPath(QtCore.QPoint(26, 0))
            path.lineTo(QtCore.QPoint(26, 656))
            self.aux[1].setSize(48, 656, 0, -632)
        elif fireDirection == 5:
            # 45 deg to the right
            self.aux[0].setSize(90, 98, 0, -1)
            path = QtGui.QPainterPath(QtCore.QPoint(0, 320))
            path.lineTo(QtCore.QPoint(264, 64))
            path.cubicTo(QtCore.QPoint(348, -14), QtCore.QPoint(420, -14), QtCore.QPoint(528, 54))
            path.lineTo(QtCore.QPoint(1036, 348))
            self.aux[1].setSize(1036, 348, 24, -252)
        elif fireDirection == 6:
            # 45 deg to the left
            self.aux[0].setSize(91, 98, -42, -1)
            path = QtGui.QPainterPath(QtCore.QPoint(1036 - 0, 320))
            path.lineTo(QtCore.QPoint(1036 - 264, 64))
            path.cubicTo(QtCore.QPoint(1036 - 348, -14), QtCore.QPoint(1036 - 420, -14), QtCore.QPoint(1036 - 528, 54))
            path.lineTo(QtCore.QPoint(1036 - 1036, 348))
            self.aux[1].setSize(1036, 348, -1036 + 24, -252)
        self.aux[1].SetPath(path)


class SpriteImage_ExtendShroom(SpriteImage): # 228
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False
        self.parent.setZValue(24999)

        if 'ExtendShroomL' not in ImageCache:
            ImageCache['ExtendShroomB'] = GetImg('extend_shroom_big.png')
            ImageCache['ExtendShroomS'] = GetImg('extend_shroom_small.png')
            ImageCache['ExtendShroomC'] = GetImg('extend_shroom_cont.png')
            ImageCache['ExtendShroomStem'] = GetImg('extend_shroom_stem.png')

    def updateSize(self):

        props = self.parent.spritedata[5]
        width = self.parent.spritedata[4] & 1
        start = (props & 0x10) >> 4
        stemlength = props & 0xF

        if start == 0: # contracted
            self.image = ImageCache['ExtendShroomC']
            self.width = 32
        else:
            if width == 0: # big
                self.image = ImageCache['ExtendShroomB']
                self.width = 160
            else: # small
                self.image = ImageCache['ExtendShroomS']
                self.width = 96

        self.xOffset = 8 - (self.width / 2)
        self.height = (stemlength * 16) + 48

        super().updateSize()

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, self.image)
        painter.drawTiledPixmap(
            (self.width * 1.5) / 2 - 14,
            48,
            28,
            (self.height * 1.5) - 48,
            ImageCache['ExtendShroomStem'],
            )


class SpriteImage_SandPillar(SpriteImage_Static): # 229
    def __init__(self, parent):
        loadIfNotInImageCache('SandPillar', 'sand_pillar.png')
        self.alpha = 0.65
        super().__init__(
            parent,
            ImageCache['SandPillar'],
            (-33, -150),
            )


class SpriteImage_Bramball(SpriteImage_Static): # 230
    def __init__(self, parent):
        loadIfNotInImageCache('Bramball', 'bramball.png')
        super().__init__(
            parent,
            ImageCache['Bramball'],
            (-32, -48),
            )


class SpriteImage_WiggleShroom(SpriteImage): # 231
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'WiggleShroomL' not in ImageCache:
            ImageCache['WiggleShroomL'] = GetImg('wiggle_shroom_left.png')
            ImageCache['WiggleShroomM'] = GetImg('wiggle_shroom_middle.png')
            ImageCache['WiggleShroomR'] = GetImg('wiggle_shroom_right.png')
            ImageCache['WiggleShroomS'] = GetImg('wiggle_shroom_stem.png')

    def updateSize(self):
        super().updateSize()

        width = (self.parent.spritedata[4] & 0xF0) >> 4
        stemlength = self.parent.spritedata[3] & 3

        self.xOffset = -(width * 8) - 20
        self.width = (width * 16) + 56
        self.height = (stemlength * 16) + 64

        self.parent.setZValue(24999)

    def paint(self, painter):
        super().paint(painter)

        xsize = self.width * 1.5
        painter.drawPixmap(0, 0, ImageCache['WiggleShroomL'])
        painter.drawTiledPixmap(18, 0, xsize - 36, 24, ImageCache['WiggleShroomM'])
        painter.drawPixmap(xsize - 18, 0, ImageCache['WiggleShroomR'])
        painter.drawTiledPixmap((xsize / 2) - 12, 24, 24, (self.height * 1.5) - 24, ImageCache['WiggleShroomS'])


class SpriteImage_MechaKoopa(SpriteImage_Static): # 232
    def __init__(self, parent):
        loadIfNotInImageCache('MechaKoopa', 'mechakoopa.png')
        super().__init__(
            parent,
            ImageCache['MechaKoopa'],
            (-8, -14),
            )


class SpriteImage_Bulber(SpriteImage_Static): # 233
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('Bulber', 'bulber.png')

        self.aux.append(AuxiliaryImage(parent, 243, 248))
        self.aux[0].image = ImageCache['Bulber']
        self.aux[0].setPos(-8, 0)

        self.dimensions = (2, -4, 50, 43)


class SpriteImage_PCoin(SpriteImage_Static): # 237
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PCoin'],
            )


class SpriteImage_Foo(SpriteImage_Static): # 238
    def __init__(self, parent):
        loadIfNotInImageCache('Foo', 'foo.png')
        super().__init__(
            parent,
            ImageCache['Foo'],
            (-8, -16),
            )


class SpriteImage_GiantWiggler(SpriteImage_Static): # 240
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['GiantWiggler'],
            (-24, -64),
            )


class SpriteImage_FallingLedgeBar(SpriteImage_Static): # 242
    def __init__(self, parent):
        loadIfNotInImageCache('FallingLedgeBar', 'falling_ledge_bar.png')
        super().__init__(
            parent,
            ImageCache['FallingLedgeBar'],
            )


class SpriteImage_RotControlledCoin(SpriteImage_SpecialCoin): # 253
    pass


class SpriteImage_RotatingQBlock(SpriteImage_Block): # 255
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 49
        self.contentsNybble = 4
        self.twelveIsMushroom = True
        self.rotates = True


class SpriteImage_RotatingBrickBlock(SpriteImage_Block): # 256
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 48
        self.contentsNybble = 4
        self.twelveIsMushroom = True
        self.rotates = True


class SpriteImage_RegularDoor(SpriteImage_Door): # 259
    pass


class SpriteImage_PoltergeistItem(SpriteImage): # 262
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'PoltergeistItem' not in ImageCache:
            LoadPolterItems()

        self.aux.append(AuxiliaryImage(parent, 60, 60))
        self.aux[0].image = ImageCache['PolterQBlock']
        self.aux[0].setPos(-18, -18)
        self.aux[0].hover = False

    def updateSize(self):

        style = self.parent.spritedata[5] & 15
        if style == 0:
            self.yOffset = 0
            self.aux[0].setSize(60, 60)
            self.aux[0].image = ImageCache['PolterQBlock']
        else:
            self.yOffset = -16
            self.aux[0].setSize(60, 84)
            self.aux[0].image = ImageCache['PolterStand']

        super().updateSize()


class SpriteImage_WaterPiranha(SpriteImage_Static): # 263
    def __init__(self, parent):
        super().__init__(parent)
        loadIfNotInImageCache('WaterPiranha', 'water_piranha.png')

        self.image = ImageCache['WaterPiranha']
        self.offset = (-5, -145)


class SpriteImage_WalkingPiranha(SpriteImage_Static): # 264
    def __init__(self, parent):
        super().__init__(parent)
        loadIfNotInImageCache('WalkPiranha', 'walk_piranha.png')

        self.image = ImageCache['WalkPiranha']
        self.offsets = (-4, -50)


class SpriteImage_FallingIcicle(SpriteImage_SimpleDynamic): # 265
    def __init__(self, parent):
        super().__init__(parent)
        if 'IcicleSmall' not in ImageCache:
            LoadIceStuff()

    def updateSize(self):
        super().updateSize()

        size = self.parent.spritedata[5] & 1
        if size == 0:
            self.image = ImageCache['IcicleSmall']
            self.height = 19
        else:
            self.image = ImageCache['IcicleLarge']
            self.height = 36


class SpriteImage_RotatingChainLink(SpriteImage_Static): # 266
    def __init__(self, parent):
        loadIfNotInImageCache('RotatingChainLink', 'rotating_chainlink.png')
        w, h = ImageCache['RotatingChainLink'].width(), ImageCache['RotatingChainLink'].height()
        super().__init__(
            parent,
            ImageCache['RotatingChainLink'],
            (
                -((im.width() / 2) - 12) / 1.5,
                -((im.height() / 2) - 12) / 1.5,
                )
            )


class SpriteImage_TiltGrate(SpriteImage): # 267
    def __init__(self, parent):
        super().__init__(parent)
        if 'TiltGrateU' not in ImageCache:
            ImageCache['TiltGrateU'] = GetImg('tilt_grate_up.png')
            ImageCache['TiltGrateD'] = GetImg('tilt_grate_down.png')
            ImageCache['TiltGrateL'] = GetImg('tilt_grate_left.png')
            ImageCache['TiltGrateR'] = GetImg('tilt_grate_right.png')

    def updateSize(self):
        direction = self.parent.spritedata[5] & 3
        if direction > 3: direction = 3

        if direction < 2:
            self.size = (69, 166)
        else:
            self.size = (166, 69)

        if direction == 0:
            self.offset = (-36, -115)
            self.image = ImageCache['TiltGrateU']
        elif direction == 1:
            self.offset = (-36, 12)
            self.image = ImageCache['TiltGrateD']
        elif direction == 2:
            self.offset = (-144, 0)
            self.image = ImageCache['TiltGrateL']
        elif direction == 3:
            self.offset = (-20, 0)
            self.image = ImageCache['TiltGrateR']

        super().updateSize()


class SpriteImage_LavaGeyser(SpriteImage): # 268
    def __init__(self, parent):
        super().__init__(parent)

        if 'LavaGeyser0' not in ImageCache:
            for i in range(7):
                ImageCache['LavaGeyser%d' % i] = GetImg('lava_geyser_%d.png' % i)

        self.parent.setZValue(1)
        self.dimensions = (-37, -186, 69, 200)

    def updateSize(self):

        height = self.parent.spritedata[4] >> 4
        startsAs = self.parent.spritedata[5] & 15

        if height > 6: height = 0
        self.offset = (
            (-30, -170),
            (-28, -155),
            (-30, -155),
            (-43, -138),
            (-32, -105),
            (-26, -89),
            (-32, -34),
            )[height]

        self.parent.alpha = 0.75 if startsAs == 1 else 0.5

        self.image = ImageCache['LavaGeyser%d' % height]

        super().updateSize()


class SpriteImage_Parabomb(SpriteImage_Static): # 269
    def __init__(self, parent):
        loadIfNotInImageCache('Parabomb', 'parabomb.png')
        super().__init__(
            parent,
            ImageCache['Parabomb'],
            (-2, -16),
            )


class SpriteImage_Mouser(SpriteImage): # 271
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        loadIfNotInImageCache('Mouser', 'mouser.png')

        self.image = ImageCache['Mouser']
        self.dimensions = (0, -2, 30, 19)

    def updateSize(self):
        super().updateSize()

        number = self.parent.spritedata[5] >> 4
        direction = self.parent.spritedata[5] & 0xF

        self.width = (number + 1) * (ImageCache['Mouser'].width() / 1.5)

        if direction == 0: # Facing right
            self.xOffset = -self.width + 16
        else:
            self.xOffset = 0

    def paint(self, painter):
        super().paint(painter)

        direction = self.parent.spritedata[5] & 0xF

        mouser = ImageCache['Mouser']
        if direction == 1:
            mouser = QtGui.QImage(mouser)
            mouser = QtGui.QPixmap.fromImage(mouser.mirrored(True, False))

        painter.drawTiledPixmap(0, 0, self.width * 1.5, 24, mouser)


class SpriteImage_IceBro(SpriteImage_Static): # 272
    def __init__(self, parent):
        loadIfNotInImageCache('IceBro', 'icebro.png')
        super().__init__(
            parent,
            ImageCache['IceBro'],
            (-5, -23),
            )


class SpriteImage_CastleGear(SpriteImage_SimpleDynamic): # 274
    def __init__(self, parent):
        super().__init__(parent)
        if 'CastleGearL' not in ImageCache or 'CastleGearS' not in ImageCache:
            LoadCastleGears()

    def updateSize(self):
        
        isBig = (self.parent.spritedata[4] & 0xF) == 1
        self.image = ImageCache['CastleGearL'] if isBig else ImageCache['CastleGearS']
        self.offset = (
            -(((self.image.width()  / 2) - 12) * (2 / 3)),
            -(((self.image.height() / 2) - 12) * (2 / 3)),
            )

        super().updateSize()


class SpriteImage_FiveEnemyRaft(SpriteImage_Static): # 275
    def __init__(self, parent):
        loadIfNotInImageCache('FiveEnemyRaft', '5_enemy_max_raft.png')
        super().__init__(
            parent,
            ImageCache['FiveEnemyRaft'],
            (0, -8),
            )


class SpriteImage_GhostDoor(SpriteImage_Door): # 276
    def __init__(self, parent):
        super().__init__(parent)
        self.doorName = 'GhostDoor'
        self.doorDimensions = (0, 0, 32, 48)


class SpriteImage_TowerDoor(SpriteImage_Door): # 277
    def __init__(self, parent):
        super().__init__(parent)
        self.doorName = 'TowerDoor'
        self.doorDimensions = (-2, -10.5, 53, 59)


class SpriteImage_CastleDoor(SpriteImage): # 278
    def __init__(self, parent):
        super().__init__(parent)
        self.doorName = 'CastleDoor'
        self.doorDimensions = (-2, -13, 53, 62)


class SpriteImage_GiantIceBlock(SpriteImage): # 280
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'IcicleSmall' not in ImageCache:
            LoadIceStuff()

        self.size = (64, 64)

    def updateSize(self):

        item = self.parent.spritedata[5] & 3
        if item > 2: item = 0

        if item == 0:
            self.image = ImageCache['BigIceBlockEmpty']
        elif item == 1:
            self.image = ImageCache['BigIceBlockBobomb']
        elif item == 2:
            self.image = ImageCache['BigIceBlockSpikeBall']

        super().updateSize()


class SpriteImage_WoodCircle(SpriteImage_SimpleDynamic): # 286
    def __init__(self, parent):
        super().__init__(parent)

        if 'WoodCircle0' not in ImageCache:
            ImageCache['WoodCircle0'] = GetImg('wood_circle_0.png')
            ImageCache['WoodCircle1'] = GetImg('wood_circle_1.png')
            ImageCache['WoodCircle2'] = GetImg('wood_circle_2.png')

    def updateSize(self):
        super().updateSize()
        size = self.parent.spritedata[5] & 3

        self.image = ImageCache['WoodCircle%d' % size]

        if size > 2: size = 0
        self.dimensions = (
            (-24, -24, 64, 64),
            (-40, -40, 96, 96),
            (-56, -56, 128, 128),
            )[size]


class SpriteImage_PathIceBlock(SpriteImage): # 287
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'PathIceBlock' not in ImageCache:
            LoadIceStuff()

        self.alpha = 0.8

    def updateSize(self):

        width  = (self.parent.spritedata[5] &  15)+1
        height = (self.parent.spritedata[5] >> 4) +1

        self.image = ImageCache['PathIceBlock'].scaled(width * 24, height * 24)

        super().updateSize()


class SpriteImage_OldBarrel(SpriteImage_Static): # 288
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['OldBarrel'],
            (1, -7),
            )


class SpriteImage_Box(SpriteImage): # 289
    def __init__(self, parent):
        super().__init__(parent)
        if 'BoxWoodSmall' not in ImageCache:
            for style, stylestr in ((0, 'Wood'), (1, 'Metal')):
                for size, sizestr in zip(range(4), ('small', 'wide', 'tall', 'big')):
                    ImageCache['Box%d%d' % (style, size)] = GetImg('box_%s_%s' % (stylestr, sizestr))

    def updateSize(self):
        BoxSizes = [(32, 32), (64, 32), (32, 64), (64, 64)]

        style = self.parent.spritedata[4] & 1
        size = (self.parent.spritedata[5] >> 4) & 3

        if style > 1: style = 1
        if size > 3: size = 0

        self.image = ImageCache['Box%d%d' % (style, size)]
        self.size = BoxSizes[size]

        super().updateSize()


class SpriteImage_Parabeetle(SpriteImage_SimpleDynamic): # 291
    def __init__(self, parent):
        super().__init__(parent)
        if 'Parabeetle0' not in ImageCache:
            ImageCache['Parabeetle0'] = GetImg('parabeetle_right.png')
            ImageCache['Parabeetle1'] = GetImg('parabeetle_left.png')
            ImageCache['Parabeetle2'] = GetImg('parabeetle_moreright.png')
            ImageCache['Parabeetle3'] = GetImg('parabeetle_atyou.png')

    def updateSize(self):

        direction = self.parent.spritedata[5] & 3
        self.image = ImageCache['Parabeetle%d' % direction]

        if direction == 0 or direction > 3: # right
            self.xOffset = -12
        elif direction == 1: # left
            self.xOffset = -10
        elif direction == 2: # more right
            self.xOffset = -12
        elif direction == 3: # at you
            self.xOffset = -26

        super().updateSize()


class SpriteImage_HeavyParabeetle(SpriteImage_SimpleDynamic): # 292
    def __init__(self, parent):
        super().__init__(parent)
        if 'HeavyParabeetle0' not in ImageCache:
            ImageCache['HeavyParabeetle0'] = GetImg('heavy_parabeetle_right.png')
            ImageCache['HeavyParabeetle1'] = GetImg('heavy_parabeetle_left.png')
            ImageCache['HeavyParabeetle2'] = GetImg('heavy_parabeetle_moreright.png')
            ImageCache['HeavyParabeetle3'] = GetImg('heavy_parabeetle_atyou.png')

    def updateSize(self):

        direction = self.parent.spritedata[5] & 3
        self.image = ImageCache['HeavyParabeetle%d' % direction]

        if direction == 0 or direction > 3: # right
            self.xOffset = -38
        elif direction == 1: # left
            self.xOffset = -38
        elif direction == 2: # more right
            self.xOffset = -38
        elif direction == 3: # at you
            self.xOffset = -52

        super().updateSize()


class SpriteImage_IceCube(SpriteImage_Static): # 294
    def __init__(self, parent):
        loadIfNotInImageCache('IceCube', 'ice_cube.png')
        super().__init__(
            parent,
            ImageCache['IceCube'],
            )


class SpriteImage_NutPlatform(SpriteImage): # 295
    def __init__(self, parent):
        super().__init__(parent)
        loadIfNotInImageCache('NutPlatform', 'nut_platform.png')

    def updateSize(self):
        offsetUp = self.parent.spritedata[5] >> 4
        offsetRight = self.parent.spritedata[5] & 15

        if offsetUp == 0:
            self.yOffset = -8
        else:
            self.yOffset = 0

        newOffsetRight = offsetRight % 8
        self.xOffset = (
            -16,
            -8,
            0,
            8,
            16,
            24,
            32,
            40,
            )[newOffsetRight]

        self.image = ImageCache['NutPlatform']

        super().updateSize()


class SpriteImage_MegaBuzzy(SpriteImage): # 296
    def __init__(self, parent):
        super().__init__(parent)

        if 'MegaBuzzyL' not in ImageCache:
            ImageCache['MegaBuzzyL'] = GetImg('megabuzzy_left.png')
            ImageCache['MegaBuzzyF'] = GetImg('megabuzzy_front.png')
            ImageCache['MegaBuzzyR'] = GetImg('megabuzzy_right.png')

        self.dimensions = (-41, -80, 98, 96)

    def updateSize(self):

        dir = self.parent.spritedata[5] & 3
        if dir == 0 or dir > 2:
            self.image = ImageCache['MegaBuzzyR']
        elif dir == 1:
            self.image = ImageCache['MegaBuzzyL']
        elif dir == 2:
            self.image = ImageCache['MegaBuzzyF']

        super().updateSize()


class SpriteImage_DragonCoaster(SpriteImage): # 297
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'DragonHead' not in ImageCache:
            ImageCache['DragonHead'] = GetImg('dragon_coaster_head.png')
            ImageCache['DragonBody'] = GetImg('dragon_coaster_body.png')
            ImageCache['DragonTail'] = GetImg('dragon_coaster_tail.png')

        self.dimensions = (0, -2, 32, 20)

    def updateSize(self):
        super().updateSize()

        raw_size = self.parent.spritedata[5] & 7

        if raw_size == 0 or raw_size == 8:
            self.width = 32
            self.xOffset = 0
        else:
            self.width = (raw_size * 32) + 32
            self.xOffset = -(self.width - 32)

    def paint(self, painter):
        super().paint(painter)

        raw_size = self.parent.spritedata[5] & 15

        if raw_size == 0 or raw_size == 8:
            # just the head
            painter.drawPixmap(0, 0, ImageCache['DragonHead'])
        elif raw_size == 1:
            # head and tail only
            painter.drawPixmap(48, 0, ImageCache['DragonHead'])
            painter.drawPixmap(0, 0, ImageCache['DragonTail'])
        else:
            painter.drawPixmap((self.width*1.5)-48, 0, ImageCache['DragonHead'])
            if raw_size > 1:
                painter.drawTiledPixmap(48, 0, (self.width*1.5)-96, 24, ImageCache['DragonBody'])
            painter.drawPixmap(0, 0, ImageCache['DragonTail'])


class SpriteImage_CannonMulti(SpriteImage): # 299
    def __init__(self, parent):
        super().__init__(parent)

        if 'CannonMulti0' not in ImageCache:
            LoadCannonMulti()

    def updateSize(self):

        number = self.parent.spritedata[5]
        direction = 'UR'

        self.offset = (-8, -11)
        if number == 0:
            direction = 'UR'
        elif number == 1:
            direction = 'UL'
        elif number == 10:
            direction = 'DR'
        elif number == 11:
            direction = 'DL'
        else:
            direction = 'Q'
            del self.offset

        self.image = ImageCache['CannonMulti%s' % direction]

        super().updateSize()


class SpriteImage_RotCannon(SpriteImage_SimpleDynamic): # 300
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('RotCannon', 'rot_cannon.png')
        loadIfNotInImageCache('RotCannonU', 'rot_cannon_u.png')
        self.size = (40, 45)

    def updateSize(self):

        direction = (self.parent.spritedata[5] & 0x10) >> 4
        if direction != 1:
            self.image = ImageCache['RotCannon']
            self.offset = (-12, -29)
        else:
            self.image = ImageCache['RotCannonU']
            self.offset = (-12, 0)

        super().updateSize()


class SpriteImage_RotCannonPipe(SpriteImage_SimpleDynamic): # 301
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('RotCannonPipe', 'rot_cannon_pipe.png')
        loadIfNotInImageCache('RotCannonPipeU', 'rot_cannon_pipe_u.png')
        self.size = (80, 90)

    def updateSize(self):

        direction = (self.parent.spritedata[5] & 0x10) >> 4
        if direction != 1:
            self.image = ImageCache['RotCannonPipe']
            self.size = (-40, -74)
        else:
            self.image = ImageCache['RotCannonPipeU']
            self.size = (-40, 0)

        super().updateSize()


class SpriteImage_MontyMole(SpriteImage): # 303
    def __init__(self, parent):
        super().__init__(parent)
        loadIfNotInImageCache('Mole', 'monty_mole.png')
        loadIfNotInImageCache('MoleCave', 'monty_mole_hole.png')

    def updateSize(self):

        mode = self.parent.spritedata[5]
        if mode == 1:
            self.image = ImageCache['Mole']
            self.offset = (3.5, 0)
        else:
            self.image = ImageCache['MoleCave']
            del self.offset

        super().updateSize()


class SpriteImage_RotFlameCannon(SpriteImage_SimpleDynamic): # 304
    def __init__(self, parent):
        super().__init__(parent)
        if 'RotFlameCannon' not in ImageCache:
            LoadRotFlameCannon()

    def updateSize(self):

        orientation = self.parent.spritedata[5] >> 4
        length = self.parent.spritedata[5] & 15
        orientation = '' if orientation == 0 else 'Flipped'

        if length > 4: length = 0
        if not orientation:
            self.yOffset = -2
        else:
            self.yOffset = 0

        self.image = ImageCache['RotFlameCannon%s%d' % (orientation, length)]

        super().updateSize()


class SpriteImage_LightCircle(SpriteImage): # 305
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        loadIfNotInImageCache('LightCircle', 'light_circle.png')

        self.aux.append(AuxiliaryImage(parent, 128, 128))
        self.aux[0].image = ImageCache['LightCircle']
        self.aux[0].setPos(-48, -48)
        self.aux[0].hover = False


class SpriteImage_RotSpotlight(SpriteImage_SimpleDynamic): # 306
    def __init__(self, parent):
        super().__init__(parent)

        if 'RotSpotlight0' not in ImageCache:
            LoadRotSpotlight()

        self.dimensions = (-24, -64, 62, 104)

    def updateSize(self):

        angle = self.parent.spritedata[3] & 15
        self.image = ImageCache['RotSpotlight%d' % angle]

        super().updateSize()


class SpriteImage_HammerBroPlatform(SpriteImage_HammerBro): # 308
    pass


class SpriteImage_SynchroFlameJet(SpriteImage_SimpleDynamic): # 309
    def __init__(self, parent):
        super().__init__(parent)

        if 'SynchroFlameJet0' not in ImageCache:
            LoadSynchroFlameJet()

        self.width = 112

    def updateSize(self):

        mode = (self.parent.spritedata[4] & 15) % 1
        direction = (self.parent.spritedata[5] & 15) % 3

        mode = 'Off' if mode else 'On'
        self.offset = (
            (0, 0),
            (-96, 0),
            (0, -96),
            (0, 0),
            )[direction]
        directionstr = 'RLUD'[direction]

        self.image = ImageCache['SynchroFlameJet%s%s' % (mode, directionstr)]

        super().updateSize()


class SpriteImage_ArrowSign(SpriteImage_SimpleDynamic): # 310
    def __init__(self, parent):
        super().__init__(parent)

        if 'ArrowSign0' not in ImageCache:
            for i in range(8):
                ImageCache['ArrowSign%d' % i] = GetImg('arrow_sign_%d.png' % i)

        self.dimensions = (-8, -16, 32, 32)

    def updateSize(self):

        direction = self.parent.spritedata[5] & 0xF
        self.image = ImageCache['ArrowSign%d' % direction]

        super().updateSize()


class SpriteImage_MegaIcicle(SpriteImage_Static): # 311
    def __init__(self, parent):
        loadIfNotInImageCache('MegaIcicle', 'mega_icicle.png')
        super().__init__(
            parent,
            ImageCache['MegaIcicle'],
            (-24, -3),
            )


class SpriteImage_BubbleGen(SpriteImage): # 314
    def __init__(self, parent):
        super().__init__(parent)
        self.updateSceneAfterPaint = True
        loadIfNotInImageCache('BubbleGen', 'bubble_gen.png')

    def updateSize(self):
        super().updateSize()
        self.parent.updateScene()

    def realViewZone(self, painter, zoneRect, viewRect):
        # Constants (change these if you want)
        bubbleFrequency = .01
        bubbleEccentricityX = 16
        bubbleEccentricityY = 48

        size = self.parent.spritedata[5] & 0xF
        if size > 3: return

        Image = ImageCache['BubbleGenEffect']

        if size == 0: pct = 50.0
        elif size == 1: pct = 60.0
        elif size == 2: pct = 80.0
        else: pct = 70.0
        Image = Image.scaledToWidth(int(Image.width() * pct / 100))

        distanceFromTop = (self.parent.objy * 1.5) - zoneRect.topLeft().y()
        random.seed(distanceFromTop + self.parent.objx) # looks ridiculous without this

        coords = []
        numOfBubbles = int(distanceFromTop * bubbleFrequency)
        for num in range(numOfBubbles):
            xmod = (random.random() * 2 * bubbleEccentricityX) - bubbleEccentricityX
            ymod = (random.random() * 2 * bubbleEccentricityY) - bubbleEccentricityY
            x = ((self.parent.objx * 1.5) - zoneRect.topLeft().x()) + xmod + 12 - (Image.width() / 2.0)
            y = ((num * 1.0 / numOfBubbles) * distanceFromTop) + ymod
            if not (0 < y < self.parent.objy * 1.5): continue
            coords.append([x, y])

        for x, y in coords:
            painter.drawPixmap(x, y, Image)


class SpriteImage_Bolt(SpriteImage_Static): # 315
    def __init__(self, parent):
        loadIfNotInImageCache('Bolt', 'bolt.png')
        super().__init__(
            parent,
            ImageCache['Bolt'],
            (2, 0),
            )


class SpriteImage_BoltBox(SpriteImage): # 316
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

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

    def updateSize(self):
        super().updateSize()

        size = self.parent.spritedata[5]
        self.width = (size & 0xF) * 16 + 32
        self.height = ((size & 0xF0) >> 4) * 16 + 32

    def paint(self, painter):
        super().paint(painter)

        xsize = self.width * 1.5
        ysize = self.height * 1.5

        painter.drawPixmap(0, 0, ImageCache['BoltBoxTL'])
        painter.drawTiledPixmap(24, 0, xsize - 48, 24, ImageCache['BoltBoxT'])
        painter.drawPixmap(xsize - 24, 0, ImageCache['BoltBoxTR'])

        painter.drawTiledPixmap(0, 24, 24, ysize-48, ImageCache['BoltBoxL'])
        painter.drawTiledPixmap(24, 24, xsize - 48, ysize - 48, ImageCache['BoltBoxM'])
        painter.drawTiledPixmap(xsize - 24, 24, 24, ysize - 48, ImageCache['BoltBoxR'])

        painter.drawPixmap(0, ysize - 24, ImageCache['BoltBoxBL'])
        painter.drawTiledPixmap(24, ysize - 24, xsize - 48, 24, ImageCache['BoltBoxB'])
        painter.drawPixmap(xsize - 24, ysize - 24, ImageCache['BoltBoxBR'])


class SpriteImage_BoxGenerator(SpriteImage_Static): # 318
    def __init__(self, parent):
        loadIfNotInImageCache('BoxGen', 'box_generator.png')
        super().__init__(
            parent,
            ImageCache['BoxGenerator'],
            (0, -64),
            )


class SpriteImage_ArrowBlock(SpriteImage_SimpleDynamic): # 321
    def __init__(self, parent):
        super().__init__(parent)

        if 'ArrowBlock0' not in ImageCache:
            ImageCache['ArrowBlock0'] = GetImg('arrow_block_up.png')
            ImageCache['ArrowBlock1'] = GetImg('arrow_block_down.png')
            ImageCache['ArrowBlock2'] = GetImg('arrow_block_left.png')
            ImageCache['ArrowBlock3'] = GetImg('arrow_block_right.png')

    def updateSize(self):

        direction = (self.parent.spritedata[5] & 3) % 4
        self.image = ImageCache['ArrowBlock%d' % direction]

        super().updateSize()


class SpriteImage_BooCircle(SpriteImage): # 323
    def __init__(self, parent):
        super().__init__(parent)

        if 'Boo2' not in ImageCache:
            ImageCache['Boo1'] = GetImg('boo1.png')
            ImageCache['Boo2'] = GetImg('boo2.png')
            ImageCache['Boo3'] = GetImg('boo3.png')
            ImageCache['Boo4'] = GetImg('boo4.png')

        self.BooAuxImage = QtGui.QPixmap(1024, 1024)
        self.BooAuxImage.fill(Qt.transparent)
        self.aux.append(AuxiliaryImage(parent, 1024, 1024))
        self.aux[0].image = self.BooAuxImage
        offsetX = ImageCache['Boo1'].width() / 4
        offsetY = ImageCache['Boo1'].height() / 4
        self.aux[0].setPos(-512 + offsetX, -512 + offsetY)
        self.aux[0].hover = False

    def updateSize(self):
        # Constants (change these to fine-tune the boo positions)
        radiusMultiplier = 24 # pixels between boos per distance value
        radiusConstant = 24 # add to all radius values
        opacity = 0.5

        # Read the data
        outrad = self.parent.spritedata[2] & 15
        inrad = self.parent.spritedata[3] >> 4
        ghostnum = 1 + (self.parent.spritedata[3] & 15)
        differentRads = not (inrad == outrad)

        # Give up if the data is invalid
        if inrad > outrad:
            null = QtGui.QPixmap(2,2)
            null.fill(Qt.transparent)
            self.aux[0].image = null
            return

        # Create a pixmap
        pix = QtGui.QPixmap(1024, 1024)
        pix.fill(Qt.transparent)
        paint = QtGui.QPainter(pix)
        paint.setOpacity(opacity)

        # Paint each boo
        for i in range(ghostnum):
            # Find the angle at which to place the ghost from the center
            MissingGhostWeight = 0.75 - (1 / ghostnum) # approximate
            angle = math.radians(-360 * i / (ghostnum + MissingGhostWeight)) + 89.6

            # Since the origin of the boo img is in the top left, account for that
            offsetX = ImageCache['Boo1'].width() / 2
            offsetY = (ImageCache['Boo1'].height() / 2) + 16 # the circle is not centered

            # Pick a pixmap
            boo = ImageCache['Boo%d' % (1 if i == 0 else ((i - 1) % 3) + 2)] # 1  2 3 4  2 3 4  2 3 4 ...

            # Find the abs pos, and paint the ghost at its inner position
            x = math.sin(angle) * ((inrad * radiusMultiplier) + radiusConstant) - offsetX
            y = -(math.cos(angle) * ((inrad * radiusMultiplier) + radiusConstant)) - offsetY
            paint.drawPixmap(x + 512, y + 512, boo)

            # Paint it at its outer position if it has one
            if differentRads:
                x = math.sin(angle) * ((outrad * radiusMultiplier) + radiusConstant) - offsetX
                y = -(math.cos(angle) * ((outrad * radiusMultiplier) + radiusConstant)) - offsetY
                paint.drawPixmap(x + 512, y + 512, boo)

        # Finish it
        paint = None
        self.aux[0].image = pix


class SpriteImage_GhostHouseStand(SpriteImage_Static): # 325
    def __init__(self, parent):
        loadIfNotInImageCache('GhostHouseStand', 'ghost_house_stand.png')
        super().__init__(
            parent,
            ImageCache['GhostHouseStand'],
            (0, -16),
            )


class SpriteImage_KingBill(SpriteImage): # 326
    def __init__(self, parent):
        super().__init__(parent)

        PainterPath = QtGui.QPainterPath()
        self.aux.append(AuxiliaryPainterPath(parent, PainterPath, 256, 256))
        self.aux[0].setSize(2048, 2048, -1024, -1024)

    def updateSize(self):
        super().updateSize()
        direction = self.parent.spritedata[5] & 15

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
            if direction == 0:   # faces left
                arc = 'LR'
            elif direction == 1: # faces right
                arc = 'LR'
                if isinstance(thing, QtCore.QPointF):
                    thing.setX(24 - thing.x())
                else:
                    thing.setRect(24 - thing.x(), thing.y(), -thing.width(), thing.height())
            elif direction == 2: # faces down
                arc = 'UD'
                if isinstance(thing, QtCore.QPointF):
                    x = thing.y() - 60
                    y = 24 - thing.x()
                    thing.setX(x)
                    thing.setY(y)
                else:
                    x = thing.y() - 60
                    y = 24 - thing.x()
                    thing.setRect(x, y, thing.height(), -thing.width())
            else: # faces up
                arc = 'UD'
                if isinstance(thing, QtCore.QPointF):
                    x = thing.y() + 60
                    y = thing.x()
                    thing.setX(x)
                    thing.setY(y)
                else:
                    x = thing.y() + 60
                    y = thing.x()
                    thing.setRect(x, y, thing.height(), thing.width())

        PainterPath = QtGui.QPainterPath()
        PainterPath.moveTo(PointsRects[0])
        if arc == 'LR': PainterPath.arcTo(PointsRects[1],  90,  180)
        else:           PainterPath.arcTo(PointsRects[1], 180, -180)
        for point in PointsRects[2:len(PointsRects)]:
            PainterPath.lineTo(point)
        PainterPath.closeSubpath()

        self.aux[0].SetPath(PainterPath)


class SpriteImage_LinePlatformBolt(SpriteImage_Static): # 327
    def __init__(self, parent):
        loadIfNotInImageCache('LinePlatformBolt', 'line_platform_with_bolt.png')
        super().__init__(
            parent,
            ImageCache['LinePlatformBolt'],
            (0, -16),
            )


class SpriteImage_RopeLadder(SpriteImage_SimpleDynamic): # 330
    def __init__(self, parent):
        super().__init__(parent)
        if 'RopeLadder0' not in ImageCache:
            LoadEnvStuff()

    def updateSize(self):

        size = self.parent.spritedata[5]
        if size > 2: size = 0

        self.image = ImageCache['RopeLadder%d' % size]

        super().updateSize()


class SpriteImage_DishPlatform(SpriteImage_SimpleDynamic): # 331
    def __init__(self, parent):
        super().__init__(parent)
        loadIfNotInImageCache('DishPlatform0', 'dish_platform_short.png')
        loadIfNotInImageCache('DishPlatform1', 'dish_platform_long.png')

    def updateSize(self):

        size = self.parent.spritedata[4] & 15
        if size == 0:
            self.xOffset = -144
            self.width = 304
        else:
            self.xOffset = -208
            self.width = 433

        self.image = ImageCache['DishPlatform%d' % size]

        super().updateSize()


class SpriteImage_PlayerBlockPlatform(SpriteImage_Static): # 333
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PlayerBlockPlatform'],
            )


class SpriteImage_CheepGiant(SpriteImage_SimpleDynamic): # 334
    def __init__(self, parent):
        super().__init__(parent)

        if 'CheepGiantRedL' not in ImageCache:
            cheep = GetImg('cheep_giant_red.png', True)
            ImageCache['CheepGiantRedL'] = QtGui.QPixmap.fromImage(cheep)
            ImageCache['CheepGiantRedR'] = QtGui.QPixmap.fromImage(cheep.mirrored(True, False))
            ImageCache['CheepGiantGreen'] = GetImg('cheep_giant_green.png')
            ImageCache['CheepGiantYellow'] = GetImg('cheep_giant_yellow.png')

    def updateSize(self):

        type = self.parent.spritedata[5] & 0xF
        if type == 3:
            self.image = ImageCache['CheepGiantRedR']
        elif type == 7:
            self.image = ImageCache['CheepGiantGreen']
        elif type == 8:
            self.image = ImageCache['CheepGiantYellow']
        else:
            self.image = ImageCache['CheepGiantRedL']

        super().updateSize()


class SpriteImage_WendyKoopa(SpriteImage_Static): # 336
    def __init__(self, parent):
        if 'WendyKoopa' not in ImageCache:
            LoadBosses()
        super().__init__(
            parent,
            ImageCache['WendyKoopa']
            (-23, -23),
            )


class SpriteImage_IggyKoopa(SpriteImage_Static): # 337
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['IggyKoopa'],
            (-17, -46),
            )


class SpriteImage_Pipe_MovingUp(SpriteImage): # 339
    def __init__(self, parent):
        super().__init__(parent)
        self.moving = True
        self.direction = 'U'


class SpriteImage_LemmyKoopa(SpriteImage_Static): # 340
    def __init__(self, parent):
        if 'LemmyKoopa' not in ImageCache:
            LoadBosses()
        super().__init__(
            parent,
            ImageCache['LemmyKoopa'],
            (-16, -53),
            )


class SpriteImage_BigShell(SpriteImage_SimpleDynamic): # 341
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('BigShell', 'bigshell.png')
        loadIfNotInImageCache('BigShellGrass', 'bigshell_grass.png')

    def updateSize(self):
        
        style = self.parent.spritedata[5] & 1
        if style == 0:
            self.image = ImageCache['BigShellGrass']
        else:
            self.image = ImageCache['BigShell']

        super().updateSize()


class SpriteImage_Muncher(SpriteImage_SimpleDynamic): # 342
    def updateSize(self):

        frozen = self.parent.spritedata[5] & 1
        if frozen == 1:
            self.image = ImageCache['MuncherF']
        else:
            self.image = ImageCache['Muncher']

        super().updateSize()


class SpriteImage_Fuzzy(SpriteImage): # 343
    def __init__(self, parent):
        super().__init__(parent)
        loadIfNotInImageCache('Fuzzy', 'fuzzy.png')
        loadIfNotInImageCache('FuzzyGiant', 'fuzzy_giant.png')

    def updateSize(self):

        giant = self.parent.spritedata[4] & 1

        self.image = ImageCache['FuzzyGiant'] if giant else ImageCache['Fuzzy']
        self.offset = (-18, -18) if giant else (-7, -7)

        super().updateSize()


class SpriteImage_MortonKoopa(SpriteImage_Static): # 344
    def __init__(self, parent):
        if 'MortonKoopa' not in ImageCache:
            LoadBosses()
        super().__init__(
            parent,
            ImageCache['MortonKoopa'],
            (-17, -34),
            )


class SpriteImage_ChainHolder(SpriteImage_Static): # 345
    def __init__(self, parent):
        loadIfNotInImageCache('ChainHolder', 'chain_holder.png')
        super().__init__(
            parent,
            ImageCache['ChainHolder']
            )


class SpriteImage_HangingChainPlatform(SpriteImage): # 346
    def __init__(self, parent):
        super().__init__(parent)

        if 'HangingChainPlatform' not in ImageCache:
            ImageCache['HangingChainPlatformS'] = GetImg('hanging_chain_platform_small.png')
            ImageCache['HangingChainPlatformM'] = GetImg('hanging_chain_platform_medium.png')
            ImageCache['HangingChainPlatformL'] = GetImg('hanging_chain_platform_large.png')

    def updateSize(self):

        size = ((self.parent.spritedata[4] & 15) % 4) % 3
        size, self.xOffset = (
            ('S', -26),
            ('M', -42),
            ('L', -58),
            )[size]

        self.image = ImageCache['HangingChainPlatform%s' % size]

        super().updateSize()


class SpriteImage_RoyKoopa(SpriteImage_Static): # 347
    def __init__(self, parent):
        if 'RoyKoopa' not in ImageCache:
            LoadBosses()
        super().__init__(
            parent,
            ImageCache['RoyKoopa'],
            (-27, -24)
            )


class SpriteImage_LudwigVonKoopa(SpriteImage_Static): # 348
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['LudwigVonKoopa'],
            (-20, -30),
            )


class SpriteImage_RockyWrench(SpriteImage_Static): # 352
    def __init__(self, parent):
        loadIfNotInImageCache('RockyWrench', 'rocky_wrench.png')
        super().__init__(
            parent,
            ImageCache['RockyWrench'],
            (4, -41),
            )


class SpriteImage_Pipe_MovingDown(SpriteImage): # 353
    def __init__(self, parent):
        super().__init__(parent)
        self.moving = True
        self.direction = 'D'


class SpriteImage_RollingHillWith1Pipe(SpriteImage_RollingHillWithPipe): # 355
    pass


class SpriteImage_BrownBlock(SpriteImage): # 356
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'BrownBlockTL' not in ImageCache:
            for vert in 'TMB':
                for horz in 'LMR':
                    ImageCache['BrownBlock' + vert + horz] = \
                        GetImg('brown_block_%s%s.png' % (vert.lower(), horz.lower()))

        self.aux.append(AuxiliaryTrackObject(parent, 16, 16, AuxiliaryTrackObject.Horizontal))

    def updateSize(self):
        super().updateSize()

        size = self.parent.spritedata[5]
        height = (size & 0xF0) >> 4
        width = size & 0xF
        height = 1 if height == 0 else height
        width = 1 if width == 0 else width
        self.width = width * 16 + 16
        self.height = height * 16 + 16

        # now set up the track
        direction = self.parent.spritedata[2] & 3
        distance = (self.parent.spritedata[4] & 0xF0) >> 4

        if direction <= 1: # horizontal
            self.aux[0].direction = 1
            self.aux[0].setSize(self.width + (distance * 16), self.height)
        else: # vertical
            self.aux[0].direction = 2
            self.aux[0].setSize(self.width, self.height + (distance * 16))

        if (direction in (0, 3)) or (direction not in (1, 2)): # right, down
            self.aux[0].setPos(0,0)
        elif direction == 1: # left
            self.aux[0].setPos(-distance * 24,0)
        elif direction == 2: # up
            self.aux[0].setPos(0,-distance * 24)

    def paint(self, painter):
        super().paint(painter)

        blockX = 0
        blockY = 0

        width = self.width * 1.5
        height = self.height * 1.5

        column2x = blockX + 24
        column3x = blockX + width - 24
        row2y = blockY + 24
        row3y = blockY + height - 24

        painter.drawPixmap(blockX, blockY, ImageCache['BrownBlockTL'])
        painter.drawTiledPixmap(column2x, blockY, width - 48, 24, ImageCache['BrownBlockTM'])
        painter.drawPixmap(column3x, blockY, ImageCache['BrownBlockTR'])

        painter.drawTiledPixmap(blockX, row2y, 24, height - 48, ImageCache['BrownBlockML'])
        painter.drawTiledPixmap(column2x, row2y, width - 48, height - 48, ImageCache['BrownBlockMM'])
        painter.drawTiledPixmap(column3x, row2y, 24, height - 48, ImageCache['BrownBlockMR'])

        painter.drawPixmap(blockX, row3y, ImageCache['BrownBlockBL'])
        painter.drawTiledPixmap(column2x, row3y, width - 48, 24, ImageCache['BrownBlockBM'])
        painter.drawPixmap(column3x, row3y, ImageCache['BrownBlockBR'])


class SpriteImage_Fruit(SpriteImage_SimpleDynamic): # 357
    def updateSize(self):

        style = self.parent.spritedata[5] & 1
        if style == 0:
            self.image = ImageCache['Fruit']
        else:
            self.image = ImageCache['Cookie']

        super().updateSize()


class SpriteImage_LavaParticles(SpriteImage): # 358
    def __init__(self, parent):
        super().__init__(parent)
        self.updateSceneAfterPaint = True

        if 'LavaParticlesA' not in ImageCache:
            ImageCache['LavaParticlesA'] = GetImg('lava_particles_a.png')
            ImageCache['LavaParticlesB'] = GetImg('lava_particles_b.png')
            ImageCache['LavaParticlesC'] = GetImg('lava_particles_c.png')

    def updateSize(self):
        super().updateSize()
        self.parent.updateScene()

    def realViewZone(self, painter, zoneRect, viewRect):

        # (0, 0) is the top-left corner of the zone

        type = self.parent.spritedata[5] & 15

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


class SpriteImage_WallLantern(SpriteImage): # 359
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        loadIfNotInImageCache('WallLantern', 'wall_lantern.png')
        loadIfNotInImageCache('WallLanternAux', 'wall_lantern_aux.png')

        self.aux.append(AuxiliaryImage(parent, 128, 128))
        self.aux[0].image = ImageCache['WallLanternAux']
        self.aux[0].setPos(-48, -48)
        self.aux[0].hover = False

        self.image = ImageCache['WallLantern']
        self.yOffset = 8


class SpriteImage_RollingHillWith8Pipes(SpriteImage_RollingHillWithPipe): # 360
    pass


class SpriteImage_CrystalBlock(SpriteImage_SimpleDynamic): # 361
    def __init__(self, parent):
        super().__init__(parent)

        if 'CrystalBlock0' not in ImageCache:
            for size in range(3):
                ImageCache['CrystalBlock%d' % size] = GetImg('crystal_block_%d.png' % size)

    def updateSize(self):

        size = (self.parent.spritedata[4] & 15) & 3
        self.image = ImageCache['CrystalBlock%d' % size]

        super().updateSize()


class SpriteImage_ColoredBox(SpriteImage): # 362
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'CBox0TL' not in ImageCache:
            for color in range(4):
                for direction in ('TL', 'T', 'TR', 'L', 'M', 'R', 'BL', 'B', 'BR'):
                    ImageCache['CBox%d%s' % (color, direction)] = GetImg('cbox_%s_%d.png' % (direction, color))

    def updateSize(self):
        super().updateSize()
        self.color = (self.parent.spritedata[3] >> 4) & 3

        size = self.parent.spritedata[4]
        width = size >> 4
        height = size & 0xF

        self.width = (width + 3) * 16
        self.height = (height + 3) * 16

    def paint(self, painter):
        super().paint(painter)

        prefix = 'CBox%d' % self.color
        xsize = self.width * 1.5
        ysize = self.height * 1.5

        painter.drawPixmap(0, 0, ImageCache[prefix + 'TL'])
        painter.drawPixmap(xsize - 25, 0, ImageCache[prefix + 'TR'])
        painter.drawPixmap(0, ysize - 25, ImageCache[prefix + 'BL'])
        painter.drawPixmap(xsize - 25, ysize - 25, ImageCache[prefix + 'BR'])

        painter.drawTiledPixmap(25, 0, xsize - 50, 25, ImageCache[prefix + 'T'])
        painter.drawTiledPixmap(25, ysize - 25, xsize - 50, 25, ImageCache[prefix + 'B'])
        painter.drawTiledPixmap(0, 25, 25, ysize - 50, ImageCache[prefix + 'L'])
        painter.drawTiledPixmap(xsize - 25, 25, 25, ysize - 50, ImageCache[prefix + 'R'])

        painter.drawTiledPixmap(25, 25, xsize - 50, ysize - 50, ImageCache[prefix + 'M'])


class SpriteImage_CubeKinokoRot(SpriteImage_SimpleDynamic): # 366
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('CubeKinokoG', 'cube_kinoko_g.png')
        loadIfNotInImageCache('CubeKinokoR', 'cube_kinoko_r.png')

    def updateSize(self):

        style = self.parent.spritedata[4] & 1
        if style == 0:
            self.image = ImageCache['CubeKinokoR']
        else:
            self.image = ImageCache['CubeKinokoG']

        super().updateSize()


class SpriteImage_CubeKinokoLine(SpriteImage_Static): # 367
    def __init__(self, parent):
        loadIfNotInImageCache('CubeKinokoP', 'cube_kinoko_p.png')
        super().__init__(
            parent,
            ImageCache['CubeKinokoP'],
            )


class SpriteImage_FlashRaft(SpriteImage_Static): # 368
    def __init__(self, parent):
        loadIfNotInImageCache('FlashlightRaft', 'flashraft.png')
        super().__init__(
            parent,
            ImageCache['FlashlightRaft'],
            (-16, -96),
            )


class SpriteImage_SlidingPenguin(SpriteImage_SimpleDynamic): # 369
    def __init__(self, parent):
        super().__init__(parent)

        if 'PenguinL' not in ImageCache:
            penguin = GetImg('sliding_penguin.png', True)
            ImageCache['PenguinL'] = QtGui.QPixmap.fromImage(penguin)
            ImageCache['PenguinR'] = QtGui.QPixmap.fromImage(penguin.mirrored(True, False))

    def updateSize(self):
        
        direction = self.parent.spritedata[5] & 1
        if direction == 0:
            self.image = ImageCache['PenguinL']
        else:
            self.image = ImageCache['PenguinR']

        super().updateSize()


class SpriteImage_CloudBlock(SpriteImage_Static): # 370
    def __init__(self, parent):
        loadIfNotInImageCache('CloudBlock', 'cloud_block.png')
        super().__init__(
            parent,
            ImageCache['CloudBlock'],
            (-4, -8),
            )


class SpriteImage_RollingHillCoin(SpriteImage_SpecialCoin): # 371
    pass


class SpriteImage_SnowWind(SpriteImage): # 374
    def __init__(self, parent):
        super().__init__(parent)
        self.updateSceneAfterPaint = True

        loadIfNotInImageCache('SnowEffect', 'snow.png')

    def updateSize(self):
        super().updateSize()
        self.parent.updateScene()

    def realViewZone(self, painter, zoneRect, viewRect):

        # (0, 0) is the top-left corner of the zone

        # For now, we only paint snow
        if self.parent.spritedata[5] & 1: return

        # Get the width and height of the zone
        zx = zoneRect.topLeft().x()
        zy = zoneRect.topLeft().y()
        zw = zoneRect.width()
        zh = zoneRect.height()

        # Get the pixmap
        mid = ImageCache['SnowEffect']

        paintLiquid(painter, None, mid, None, None, zx, zy, zw, zh, 0, False, 0)


class SpriteImage_MovingChainLink(SpriteImage_SimpleDynamic): # 376
    def __init__(self, parent):
        super().__init__(parent)

        if 'MovingChainLink0' not in ImageCache:
            LoadMovingChainLink()

    def updateSize(self):
        
        self.shape = (self.parent.spritedata[4] >> 4) % 4
        arrow = None

        size = (
            (64, 64),
            (64, 128),
            (64, 224),
            (192, 64),
            )[self.shape]

        self.xOffset = -size[0] / 2
        self.yOffset = -size[1] / 2
        self.image = ImageCache['MovingChainLink%d' % self.shape]

        super().updateSize()


class SpriteImage_Pipe_Up(SpriteImage): # 377
    pass


class SpriteImage_Pipe_Down(SpriteImage): # 378
    def __init__(self, parent):
        super().__init__(parent)
        self.direction = 'D'


class SpriteImage_Pipe_Right(SpriteImage): # 379
    def __init__(self, parent):
        super().__init__(parent)
        self.direction = 'R'


class SpriteImage_Pipe_Left(SpriteImage): # 380
    def __init__(self, parent):
        super().__init__(parent)
        self.direction = 'L'


class SpriteImage_ScrewMushroomNoBolt(SpriteImage_ScrewMushroom): # 382
    def __init__(self, parent):
        super().__init__(parent)
        self.hasBolt = False


class SpriteImage_IceBlock(SpriteImage_SimpleDynamic): # 385
    def __init__(self, parent):
        super().__init__(parent)

        if 'IceBlock00' not in ImageCache:
            for i in range(4):
                for j in range(4):
                    ImageCache['IceBlock%d%d' % (i, j)] = GetImg('iceblock%d%d.png' % (i, j))

    def updateSize(self):

        size = self.parent.spritedata[5]
        height = (size & 0x30) >> 4
        width = size & 3

        self.image = ImageCache['IceBlock%d%d' % (width, height)]
        self.xOffset = width * -4
        self.yOffset = height * -8
        
        super().updateSize()


class SpriteImage_PowBlock(SpriteImage_Static): # 386
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['POW']
            )


class SpriteImage_Bush(SpriteImage_SimpleDynamic): # 387
    def __init__(self, parent):
        super().__init__(parent)

        self.parent.setZValue(24999)

    def updateSize(self):

        props = self.parent.spritedata[5]
        style = (props >> 4) & 1
        size = (props & 3) % 4

        self.offset = (
            (-22, -25),
            (-29, -45),
            (-41, -61),
            (-52, -80),
            )[size]

        self.image = ImageCache['Bush%d%d' % (style, size)]

        super().updateSize()


class SpriteImage_Barrel(SpriteImage_Static): # 388
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Barrel'],
            (-4, -8),
            )


class SpriteImage_StarCoinBoltControlled(SpriteImage_StarCoin): # 389
    pass


class SpriteImage_BoltControlledCoin(SpriteImage_SpecialCoin): # 390
    pass


class SpriteImage_GlowBlock(SpriteImage): # 391
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        self.aux.append(AuxiliaryImage(parent, 48, 48))
        self.aux[0].image = ImageCache['GlowBlock']
        self.aux[0].setPos(-12, -12)


class SpriteImage_PropellerBlock(SpriteImage_Static): # 393
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['PropellerBlock'],
            (-1, -6),
            )


class SpriteImage_LemmyBall(SpriteImage_Static): # 394
    def __init__(self, parent):
        loadIfNotInImageCache('LemmyBall', 'lemmyball.png')
        super().__init__(
            parent,
            ImageCache['LemmyBall'],
            (-6, 0),
            )


class SpriteImage_SpinyCheep(SpriteImage_Static): # 395
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SpinyCheep'],
            (-1, -2),
            )


class SpriteImage_MoveWhenOn(SpriteImage): # 396
    def __init__(self, parent):
        super().__init__(parent)

        if 'MoveWhenOnL' not in ImageCache:
            LoadMoveWhenOn()

    def updateSize(self):
        super().updateSize()

        # get width
        raw_size = self.parent.spritedata[5] & 0xF
        if raw_size == 0:
            self.xOffset = -16
            self.width = 32
        else:
            self.xOffset = 0
            self.width = raw_size*16

        # set direction
        self.direction =(self.parent.spritedata[3] >> 4)

    def paint(self, painter):
        super().paint(painter)

        if self.direction == 0:
            direction = 'R'
        elif self.direction == 1:
            direction = 'L'
        elif self.direction == 2:
            direction = 'U'
        elif self.direction == 3:
            direction = 'D'

        raw_size = self.parent.spritedata[5] & 0xF

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
            painter.drawPixmap((self.width*1.5)-24, 2, ImageCache['MoveWhenOnR'])

        center = (self.width / 2) * 1.5
        painter.drawPixmap(center - 14, 0, ImageCache['MoveWhenOnC'])
        painter.drawPixmap(center - 12, 1, ImageCache['SmArrow%s' % self.direction])


class SpriteImage_GhostHouseBox(SpriteImage): # 397
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'GHBoxTL' not in ImageCache:
            for direction in ['TL','T','TR','L','M','R','BL','B','BR']:
                ImageCache['GHBox%s' % direction] = GetImg('ghbox_%s.png' % direction)

    def updateSize(self):
        super().updateSize()

        height = self.parent.spritedata[4] >> 4
        width = self.parent.spritedata[5] & 15

        self.width = (width + 2) * 16
        self.height = (height + 2) * 16

    def paint(self, painter):
        super().paint(painter)

        prefix = 'GHBox'
        xsize = self.width * 1.5
        ysize = self.height * 1.5

        # Corners
        painter.drawPixmap(0, 0, ImageCache[prefix + 'TL'])
        painter.drawPixmap(xsize - 24, 0, ImageCache[prefix + 'TR'])
        painter.drawPixmap(0, ysize - 24, ImageCache[prefix + 'BL'])
        painter.drawPixmap(xsize - 24, ysize - 24, ImageCache[prefix + 'BR'])

        # Edges
        painter.drawTiledPixmap(24, 0, xsize - 48, 24, ImageCache[prefix + 'T'])
        painter.drawTiledPixmap(24, ysize - 24, xsize - 48, 24, ImageCache[prefix + 'B'])
        painter.drawTiledPixmap(0, 24, 24, ysize - 48, ImageCache[prefix + 'L'])
        painter.drawTiledPixmap(xsize - 24, 24, 24, ysize - 48, ImageCache[prefix + 'R'])

        # Middle
        painter.drawTiledPixmap(24, 24, xsize - 48, ysize - 48, ImageCache[prefix + 'M'])


class SpriteImage_LineQBlock(SpriteImage_Block): # 402
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 49
        self.twelveIsMushroom = False


class SpriteImage_LineBrickBlock(SpriteImage_Block): # 403
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 48


class SpriteImage_WendyRing(SpriteImage_Static): # 413
    def __init__(self, parent):
        loadIfNotInImageCache('WendyRing', 'wendy_ring.png')
        super().__init__(
            parent,
            ImageCache['WendyRing'],
            (-4, 4),
            )


class SpriteImage_Gabon(SpriteImage_SimpleDynamic): # 414
    def __init__(self, parent):
        super().__init__(parent)

        if 'GabonLeft' not in ImageCache:
            ImageCache['GabonLeft'] = GetImg('gabon_l.png')
            ImageCache['GabonRight'] = GetImg('gabon_r.png')
            ImageCache['GabonDown'] = GetImg('gabon_d.png')

    def updateSize(self):

        throwdir = self.parent.spritedata[5] & 1
        if throwdir == 0: # down
            self.image = ImageCache['GabonDown']
            self.offset = (-5, -29)
        else: # left/right

            facing = self.parent.spritedata[4] & 1
            self.image = (
                ImageCache['GabonLeft'],
                ImageCache['GabonRight'],
                )[facing]
            self.offset = (-7, -31)

        super().updateSize()


class SpriteImage_BetaLarryKoopa(SpriteImage_Static): # 415
    def __init__(self, parent):

        # For now it will use real Larry's image,
        # but eventually it will need its own
        # because this one looks different.
        if 'LarryKoopa' not in ImageCache:
            LoadBosses()

        super().__init__(
            parent,
            ImageCache['LarryKoopa'],
            (-17, -33),
            )


class SpriteImage_InvisibleOneUp(SpriteImage_Static): # 416
    def __init__(self, parent):
        super().__init__(parent)

        if 'InvisibleOneUp' not in ImageCache:
            ImageCache['InvisibleOneUp'] = ImageCache['Blocks'][11].scaled(16, 16)

        self.image = ImageCache['InvisibleOneUp']
        self.alpha = 0.65
        self.offset = (3, 5)


class SpriteImage_SpinjumpCoin(SpriteImage_Static): # 417
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Coin'],
            )
        self.alpha = 0.55


class SpriteImage_Bowser(SpriteImage_Static): # 419
    def __init__(self, parent):
        if 'Bowser' not in ImageCache:
            LoadBosses()
        super().__init__(
            parent,
            ImageCache['Bowser'],
            (-43, -70),
            )


class SpriteImage_GiantGlowBlock(SpriteImage): # 420
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        loadIfNotInImageCache('GiantGlowBlock', 'giant_glow_block.png')
        loadIfNotInImageCache('GiantGlowBlockOff', 'giant_glow_block_off.png')

        self.aux.append(AuxiliaryImage(parent, 100, 100))
        self.aux[0].image = ImageCache['GiantGlowBlock']
        self.aux[0].setPos(-25, -30)
        self.size = (32, 32)

    def updateSize(self):
        super().updateSize()

        type = self.parent.spritedata[4] >> 4
        if type == 0:
            self.aux[0].image = ImageCache['GiantGlowBlock']
            self.aux[0].setPos(-25, -30)
            self.aux[0].setSize(100, 100)
        else:
            self.aux[0].image = ImageCache['GiantGlowBlockOff']
            self.aux[0].setPos(0, 0)
            self.aux[0].setSize(48, 48)


class SpriteImage_UnusedGhostDoor(SpriteImage_Door): # 421
    def __init__(self, parent):
        super().__init__(parent)
        self.doorName = 'GhostDoor'
        self.doorDimensions = (0, 0, 32, 48)


class SpriteImage_ToadQBlock(SpriteImage_Block): # 422
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 49
        self.contentsOverride = 16


class SpriteImage_ToadBrickBlock(SpriteImage_Block): # 423
    def __init__(self, parent):
        super().__init__(parent)
        self.tilenum = 48
        self.contentsOverride = 16


class SpriteImage_PalmTree(SpriteImage_SimpleDynamic): # 424
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.setZValue(24999)

        if 'PalmTree0' not in ImageCache:
            for i in range(8):
                ImageCache['PalmTree%d' % i] = GetImg('palmtree_%d.png' % i)

    def updateSize(self):

        size = self.parent.spritedata[5] & 7
        self.image = ImageCache['PalmTree%d' % size]
        self.yOffset = 16 - (self.image.height() / 1.5)

        super().updateSize()


class SpriteImage_Jellybeam(SpriteImage_Static): # 425
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Jellybeam'],
            (-6, 0),
            )


class SpriteImage_Kamek(SpriteImage_Static): # 427
    def __init__(self, parent):
        if 'Kamek' not in ImageCache:
            LoadBosses()
        super().__init__(
            parent,
            ImageCache['Kamek'],
            (-10, -26),
            )


class SpriteImage_MGPanel(SpriteImage_Static): # 428
    def __init__(self, parent):
        loadIfNotInImageCache('MGPanel', 'minigame_flip_panel.png')
        super().__init__(
            parent,
            ImageCache['MGPanel'],
            (-8, -8),
            )


class SpriteImage_Toad(SpriteImage_Static): # 432
    def __init__(self, parent):
        loadIfNotInImageCache('Toad', 'toad.png')
        super().__init__(
            parent,
            ImageCache['Toad'],
            (-1, -16),
            )


class SpriteImage_FloatingQBlock(SpriteImage): # 433
    def __init__(self, parent):
        loadIfNotInImageCache('FloatingQBlock', 'floating_qblock.png')
        super().__init__(
            parent,
            ImageCache['FloatingQBlock'],
            (-6, -6)
            )


class SpriteImage_WarpCannon(SpriteImage_SimpleDynamic): # 434
    def __init__(self, parent):
        super().__init__(parent)

        if 'Warp0' not in ImageCache:
            ImageCache['Warp0'] = GetImg('warp_w5.png')
            ImageCache['Warp1'] = GetImg('warp_w6.png')
            ImageCache['Warp2'] = GetImg('warp_w8.png')

    def updateSize(self):

        dest = self.parent.spritedata[5] & 3
        if dest == 3: dest = 0
        self.image = ImageCache['Warp%d' % dest]

        super().updateSize()


class SpriteImage_GhostFog(SpriteImage): # 435
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False
        self.updateSceneAfterPaint = True

        loadIfNotInImageCache('GhostFog', 'fog_ghost.png')

    def updateSize(self):
        super().updateSize()
        self.parent.updateScene()

    def realViewZone(self, painter, zoneRect, viewRect):

        if self.parent.spritedata[5]: return

        # (0, 0) is the top-left corner of the zone

        # Get the width and height of the zone
        zx = zoneRect.topLeft().x()
        zy = zoneRect.topLeft().y()
        zw = zoneRect.width()
        zh = zoneRect.height()

        # Get the y pos of the self.parent
        sy = self.parent.objy

        # Get pixmaps
        mid = ImageCache['GhostFog']

        paintLiquid(painter, None, mid, None, None, zx, zy, zw, zh, sy, False, 0)



class SpriteImage_PurplePole(SpriteImage): # 437
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'VertPole' not in ImageCache:
            ImageCache['VertPoleTop'] = GetImg('purple_pole_top.png')
            ImageCache['VertPole'] = GetImg('purple_pole_middle.png')
            ImageCache['VertPoleBottom'] = GetImg('purple_pole_bottom.png')

    def updateSize(self):
        super().updateSize()

        length = self.parent.spritedata[5]
        self.height = (length + 3) * 16

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['VertPoleTop'])
        painter.drawTiledPixmap(0, 24, 24, self.height * 1.5 - 48, ImageCache['VertPole'])
        painter.drawPixmap(0, self.height * 1.5 - 24, ImageCache['VertPoleBottom'])


class SpriteImage_CageBlocks(SpriteImage_SimpleDynamic): # 438
    def __init__(self, parent):
        super().__init__(parent)

        if 'CageBlock0' not in ImageCache:
            for type in range(8):
                ImageCache['CageBlock%d' % type] = GetImg('cage_block_%d.png' % type)

    def updateSize(self):

        type = (self.parent.spritedata[4] & 15) % 5

        self.offset = (
            (-112, -112),
            (-112, -112),
            (-97, -81),
            (-80, -96),
            (-112, -112),
            )[type]

        self.image = ImageCache['CageBlock%d' % type]

        super().updateSize()


class SpriteImage_CagePeachFake(SpriteImage_Static): # 439
    def __init__(self, parent):
        loadIfNotInImageCache('CagePeachFake', 'cage_peach_fake.png')
        super().__init__(
            parent,
            ImageCache['CagePeachFake'],
            (-18, -106),
            )


class SpriteImage_HorizontalRope(SpriteImage): # 440
    def __init__(self, parent):
        super().__init__(parent)
        loadIfNotInImageCache('HorzRope', 'horizontal_rope_middle')
        loadIfNotInImageCache('HorzRopeEnd', 'horizontal_rope_end')

    def updateSize(self):
        super().updateSize()

        length = self.parent.spritedata[5]
        self.width = (length + 3) * 16

    def paint(self, painter):
        super().paint(painter)

        endpiece = ImageCache['HorzRopeEnd']
        painter.drawPixmap(0, 0, endpiece)
        painter.drawTiledPixmap(24, 0, self.width * 1.5 - 48, 24, ImageCache['HorzRope'])
        painter.drawPixmap(self.width * 1.5 - 24, 0, endpiece)


class SpriteImage_MushroomPlatform(SpriteImage): # 441
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'RedShroomL' not in ImageCache:
            LoadMushrooms()

    def updateSize(self):
        super().updateSize()

        # get size/color
        self.color = self.parent.spritedata[4] & 1
        self.shroomsize = (self.parent.spritedata[5] >> 4) & 1
        self.height = 16 * (self.shroomsize + 1)

        # get width
        width = self.parent.spritedata[5] & 0xF
        if self.shroomsize == 0:
            self.width = (width << 4) + 32
            self.offset = (
                0 - (((width + 1) // 2) << 4),
                0,
                )
        else:
            self.width = (width << 5) + 64
            self.offset = (
                16 - (self.width / 2),
                -16,
                )

    def paint(self, painter):
        super().paint(painter)

        tilesize = 24 + (self.shroomsize * 24)
        if self.shroomsize == 0:
            if self.color == 0:
                color = 'Orange'
            else:
                color = 'Blue'
        else:
            if self.color == 0:
                color = 'Red'
            else:
                color = 'Green'

        painter.drawPixmap(0, 0, ImageCache[color + 'ShroomL'])
        painter.drawTiledPixmap(tilesize, 0, (self.width * 1.5) - (tilesize * 2), tilesize, ImageCache[color + 'ShroomM'])
        painter.drawPixmap((self.width * 1.5) - tilesize, 0, ImageCache[color + 'ShroomR'])


class SpriteImage_ReplayBlock(SpriteImage_Static): # 443
    def __init__(self, parent):
        loadIfNotInImageCache('ReplayBlock', 'replay_block.png')
        super().__init__(
            parent,
            ImageCache['ReplayBlock'],
            (-8, -16),
            )


class SpriteImage_PreSwingingVine(SpriteImage_Static): # 444
    def __init__(self, parent):
        loadIfNotInImageCache('SwingVine', 'swing_vine.png')
        super().__init__(
            parent,
            ImageCache['SwingVine'],
            )


class SpriteImage_CagePeachReal(SpriteImage_Static): # 445
    def __init__(self, parent):
        loadIfNotInImageCache('CagePeachReal', 'cage_peach_real.png')
        super().__init__(
            parent,
            ImageCache['CagePeachReal'],
            (-18, -106),
            )


class SpriteImage_UnderwaterLamp(SpriteImage): # 447
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        self.aux.append(AuxiliaryImage(parent, 105, 105))
        self.aux[0].image = ImageCache['UnderwaterLamp']
        self.aux[0].setPos(-34, -34)

        self.dimensions = (-4, -4, 24, 26)


class SpriteImage_MetalBar(SpriteImage_Static): # 448
    def __init__(self, parent):
        loadIfNotInImageCache('MetalBar', 'metal_bar.png')
        super().__init__(
            parent,
            ImageCache['MetalBar'],
            (0, -32),
            )


class SpriteImage_Pipe_EnterableUp(SpriteImage_Pipe): # 450
    pass


class SpriteImage_MouserDespawner(SpriteImage_Static): # 451
    def __init__(self, parent):
        loadIfNotInImageCache('MouserDespawner', 'mouser_despawner.png')
        super().__init__(
            parent,
            ImageCache['MouserDespawner'],
            )


class SpriteImage_BowserDoor(SpriteImage_Door): # 452
    def __init__(self, parent):
        super().__init__(parent)
        self.doorName = 'BowserDoor'
        self.doorDimensions = (-53, -134, 156, 183)


class SpriteImage_Seaweed(SpriteImage_SimpleDynamic): # 453
    def __init__(self, parent):
        super().__init__(parent)
        self.parent.setZValue(24998)

        if 'Seaweed0' not in ImageCache:
            for i in range(4):
                ImageCache['Seaweed%d' % i] = GetImg('seaweed_%d.png' % i)

    def updateSize(self):
        SeaweedSizes = [0, 1, 2, 2, 3]
        SeaweedXOffsets = [-26, -22, -31, -42]

        style = (self.parent.spritedata[5] & 0xF) % 4
        size = SeaweedSizes[style]

        self.image = ImageCache['Seaweed%d' % size]
        self.offset = (
            SeaweedXOffsets[size],
            17 - self.height,
            )

        super().updateSize()


class SpriteImage_HammerPlatform(SpriteImage_Static): # 455
    def __init__(self, parent):
        loadIfNotInImageCache('HammerPlatform', 'hammer_platform.png')
        super().__init__(
            parent,
            ImageCache['HammerPlatform'],
            (-24, -8),
            )
        self.parent.setZValue(24999)


class SpriteImage_BossBridge(SpriteImage_SimpleDynamic): # 456
    def __init__(self, parent):
        super().__init__(parent)

        if 'BossBridgeL' not in ImageCache:
            ImageCache['BossBridgeL'] = GetImg('boss_bridge_left.png')
            ImageCache['BossBridgeM'] = GetImg('boss_bridge_middle.png')
            ImageCache['BossBridgeR'] = GetImg('boss_bridge_right.png')

    def updateSize(self):

        style = (self.parent.spritedata[5] & 3) % 3
        self.image = (
            ImageCache['BossBridgeM'],
            ImageCache['BossBridgeR'],
            ImageCache['BossBridgeL'],
            )[style]

        super().updateSize()


class SpriteImage_SpinningThinBars(SpriteImage_Static): # 457
    def __init__(self, parent):
        loadIfNotInImageCache('SpinningThinBars', 'spinning_thin_bars.png')
        super().__init__(
            parent,
            ImageCache['SpinningThinBars'],
            (-114, -112),
            )


class SpriteImage_SwingingVine(SpriteImage_SimpleDynamic): # 464
    def __init__(self, parent):
        super().__init__(parent)

        loadIfNotInImageCache('SwingVine', 'swing_vine.png')
        loadIfNotInImageCache('SwingChain', 'swing_chain.png')

    def updateSize(self):

        style = self.parent.spritedata[5] & 1
        self.image = ImageCache['SwingVine'] if not style else ImageCache['SwingChain']

        super().updateSize()


class SpriteImage_LavaIronBlock(SpriteImage_Static): # 466
    def __init__(self, parent):
        loadIfNotInImageCache('LavaIronBlock', 'lava_iron_block.png')
        super().__init__(
            parent,
            ImageCache['LavaIronBlock'],
            (-2, -1),
            )


class SpriteImage_MovingGemBlock(SpriteImage_Static): # 467
    def __init__(self, parent):
        loadIfNotInImageCache('MovingGemBlock', 'moving_gem_block.png')
        super().__init__(
            parent,
            ImageCache['MovingGemBlock'],
            )


class SpriteImage_BoltPlatform(SpriteImage): # 469
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'BoltPlatformL' not in ImageCache:
            ImageCache['BoltPlatformL'] = GetImg('bolt_platform_left.png')
            ImageCache['BoltPlatformM'] = GetImg('bolt_platform_middle.png')
            ImageCache['BoltPlatformR'] = GetImg('bolt_platform_right.png')

    def updateSize(self):
        super().updateSize()

        length = self.parent.spritedata[5] & 0xF
        self.width = (length + 2) * 16

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['BoltPlatformL'])
        painter.drawTiledPixmap(24, 3, self.width * 1.5 - 48, 24, ImageCache['BoltPlatformM'])
        painter.drawPixmap(self.width * 1.5 - 24, 0, ImageCache['BoltPlatformR'])


class SpriteImage_BoltPlatformWire(SpriteImage): # 470
    def __init__(self, parent):
        loadIfNotInImageCache('BoltPlatformWire', 'bolt_platform_wire.png')
        super().__init__(
            parent,
            ImageCache['BoltPlatformWire'],
            (5, -240),
            )


class SpriteImage_PotPlatform(SpriteImage): # 471
    def __init__(self, parent):
        super().__init__(parent)
        self.showSpritebox = False

        if 'PotPlatformT' not in ImageCache:
            ImageCache['PotPlatformT'] = GetImg('pot_platform_top.png')
            ImageCache['PotPlatformM'] = GetImg('pot_platform_middle.png')

        self.offset = (-12, -2)

    def paint(self, painter):
        super().paint(painter)

        painter.drawPixmap(0, 0, ImageCache['PotPlatformT'])
        painter.drawTiledPixmap(12, 143, 52, 579, ImageCache['PotPlatformM'])


class SpriteImage_IceFloe(SpriteImage_SimpleDynamic): # 475
    def __init__(self, parent):
        super().__init__(parent)

        if 'IceFloe0' not in ImageCache:
            for size in range(16):
                ImageCache['IceFloe%d' % size] = GetImg('ice_floe_%d.png' % size)

        self.alpha = 0.65

    def updateSize(self):

        size = self.parent.spritedata[5] & 15
        self.offset = (
            (-1, -32), # 0: 3x3
            (-2, -48), # 1: 4x4
            (-2, -64), # 2: 5x5
            (-2, -32), # 3: 4x3
            (-2, -48), # 4: 5x4
            (-3, -80), # 5: 7x6
            (-3, -160), # 6: 16x11
            (-3, -112), # 7: 11x8
            (-1, -48), # 8: 2x4
            (-2, -48), # 9: 3x4
            (-2.5, -96), # 10: 6x7
            (-1, -64), # 11: 2x5
            (-1, -64), # 12: 3x5
            )[size]

        self.image = ImageCache['IceFloe%d' % size]

        super().updateSize()


class SpriteImage_FlyingWrench(SpriteImage_Static): # 476
    def __init__(self, parent):
        if 'Wrench' not in ImageCache:
            LoadDoomshipStuff()
        super().__init__(
            parent,
            ImageCache['Wrench'],
            )


class SpriteImage_SuperGuideBlock(SpriteImage_Static): # 477
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SuperGuide'],
            (-4, -4),
            )


class SpriteImage_BowserSwitchSm(SpriteImage_SimpleDynamic): # 478
    def __init__(self, parent):
        super().__init__(parent)
        if 'ESwitch' not in ImageCache:
            LoadSwitches()

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1
        if not upsideDown:
            self.image = ImageCache['ESwitch']
            self.offset = (-16, -26)
        else:
            self.image = ImageCache['ESwitchU']
            self.offset = (-16, 0)

        super().updateSize()


class SpriteImage_BowserSwitchLg(SpriteImage_SimpleDynamic): # 479
    def __init__(self, parent):
        super().__init__(parent)
        if 'ESwitchLg' not in ImageCache:
            LoadSwitches()

    def updateSize(self):

        upsideDown = self.parent.spritedata[5] & 1
        if not upsideDown:
            self.image = ImageCache['ELSwitch']
        else:
            self.image = ImageCache['ELSwitchU']

        super().updateSize()





################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################


# ---- Resource Loaders ----
def LoadBasicSuite():

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
    ImageCache['RotControlledBlock'] = GetImg('RotControlled_block.png')
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

    ImageCache['PokeyTop'] = GetImg('pokey_top.png')
    ImageCache['PokeyMiddle'] = GetImg('pokey_middle.png')
    ImageCache['PokeyBottom'] = GetImg('pokey_bottom.png')
    ImageCache['Lakitu'] = GetImg('lakitu.png')

def LoadPlatformImages():

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

    ImageCache['DSBlockTopLeft'] = GetImg('dsblock_topleft.png')
    ImageCache['DSBlockTop'] = GetImg('dsblock_top.png')
    ImageCache['DSBlockTopRight'] = GetImg('dsblock_topright.png')
    ImageCache['DSBlockLeft'] = GetImg('dsblock_left.png')
    ImageCache['DSBlockRight'] = GetImg('dsblock_right.png')
    ImageCache['DSBlockBottomLeft'] = GetImg('dsblock_bottomleft.png')
    ImageCache['DSBlockBottom'] = GetImg('dsblock_bottom.png')
    ImageCache['DSBlockBottomRight'] = GetImg('dsblock_bottomright.png')

def LoadSwitches():

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

def LoadClam():
    ImageCache['ClamEmpty'] = GetImg('clam.png')

    overlays = (
        (26, 22, 'Star', ImageCache['StarCoin']),
        (40, 42, '1Up', ImageCache['Blocks'][11]),
        (40, 42, 'PSwitch', ImageCache['PSwitch']),
        (40, 42, 'PSwitchU', ImageCache['PSwitchU']),
        )
    for x, y, clamName, overlayImage in overlays:
        newPix = QtGui.QPixmap(ImageCache['ClamEmpty'])
        painter = QtGui.QPainter(newPix)
        painter.setOpacity(0.6)
        painter.drawPixmap(overlayImage, x, y)
        del painter
        ImageCache['Clam' + clamName] = newPix

    # 2 coins special case
    newPix = QtGui.QPixmap(ImageCache['ClamEmpty'])
    painter = QtGui.QPainter(newPix)
    painter.setOpacity(0.6)
    painter.drawPixmap(ImageCache['Coin'], 28, 42)
    painter.drawPixmap(ImageCache['Coin'], 52, 42)
    del painter
    ImageCache['Clam2Coin'] = newPix

def LoadCastleStuff():

    ImageCache['Podoboo'] = GetImg('podoboo.png')
    ImageCache['Thwomp'] = GetImg('thwomp.png')
    ImageCache['GiantThwomp'] = GetImg('giant_thwomp.png')
    ImageCache['SpikeBall'] = GetImg('spike_ball.png')
    ImageCache['GiantSpikeBall'] = GetImg('giant_spike_ball.png')

def LoadEnvItems():

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
    ImageCache['CannonMultiQ'] = GetImg('RotControlled_block.png')

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

    for i in range(16):
        ImageCache['RotSpotlight%d' % i] = GetImg('rotational_spotlight_%d.png' % i)

def LoadMice():
    for i in range(8):
        ImageCache['LittleMouser%d' % i] = GetImg('little_mouser_%d.png' % i)
        originalImg = GetImg('little_mouser_%d.png' % i, True)
        ImageCache['LittleMouserFlipped%d' % i] = QtGui.QPixmap.fromImage(originalImg.mirrored(True, False))

def LoadCrabs():

    ImageCache['Huckit'] = GetImg('huckit_crab.png')
    originalImg = GetImg('huckit_crab.png', True)
    ImageCache['HuckitFlipped'] = QtGui.QPixmap.fromImage(originalImg.mirrored(True, False))

def LoadFireSnake():

    ImageCache['FireSnakeWait'] = GetImg('fire_snake_0.png')
    ImageCache['FireSnake'] = GetImg('fire_snake_1.png')

def LoadPolterItems():

    loadIfNotInImageCache('GhostHouseStand', 'ghost_house_stand.png')

    polterstand = GetImg('polter_stand.png')
    polterblock = GetImg('polter_qblock.png')

    standpainter = QtGui.QPainter(polterstand)
    blockpainter = QtGui.QPainter(polterblock)

    standpainter.drawPixmap(ImageCache['GhostHouseStand'], 18, 18)
    blockpainter.drawPixmap(ImageCache['Overrides'][9], 18, 18)

    del standpainter
    del blockpainter

    ImageCache['PolterStand'] = polterstand
    ImageCache['PolterQBlock'] = polterblock


def LoadFlyingBlocks():

    for color in ['yellow', 'blue', 'gray', 'red']:
        ImageCache['FlyingQBlock%s' % color] = GetImg('flying_qblock_%s.png' % color)

def LoadPipeBubbles():

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

    ImageCache['IcicleSmall'] = GetImg('icicle_small.png')
    ImageCache['IcicleLarge'] = GetImg('icicle_large.png')
    ImageCache['IcicleSmallS'] = GetImg('icicle_small_static.png')
    ImageCache['IcicleLargeS'] = GetImg('icicle_large_static.png')
    ImageCache['BigIceBlockEmpty'] = GetImg('big_ice_block_empty.png')
    ImageCache['BigIceBlockBobomb'] = GetImg('big_ice_block_bobomb.png')
    ImageCache['BigIceBlockSpikeBall'] = GetImg('big_ice_block_spikeball.png')
    ImageCache['PathIceBlock'] = GetImg('unused_path_ice_block.png')

def LoadMushrooms():

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

    ImageCache['MidwayFlag'] = GetImg('midway_flag.png')
    ImageCache['Flagpole'] = GetImg('flagpole.png')
    ImageCache['FlagpoleSecret'] = GetImg('flagpole_secret.png')
    ImageCache['Castle'] = GetImg('castle.png')
    ImageCache['CastleSecret'] = GetImg('castle_secret.png')
    ImageCache['SnowCastle'] = GetImg('snow_castle.png')
    ImageCache['SnowCastleSecret'] = GetImg('snow_castle_secret.png')

def LoadDoomshipStuff():

    ImageCache['Wrench'] = GetImg('wrench.png')

def LoadUnusedStuff():

    ImageCache['UnusedPlatform'] = GetImg('unused_platform.png')
    ImageCache['UnusedPlatformDark'] = GetImg('unused_platform_dark.png')
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
            dest.fill(Qt.transparent)
            p = QtGui.QPainter(dest)
            p.rotate(rotValue)
            p.drawPixmap(xpos, ypos, newgate)
            del p

            ImageCache['1WayGate%d%d' % (flip, direction)] = dest

    platform = ImageCache['UnusedPlatformDark'].scaled(
        144, 24,
        Qt.IgnoreAspectRatio, Qt.SmoothTransformation,
        )
    img = QtGui.QPixmap(432, 312)
    img.fill(Qt.transparent)
    paint = QtGui.QPainter(img)
    paint.setOpacity(0.8)
    paint.drawPixmap(144, 0,   platform) # top
    paint.drawPixmap(144, 288, platform) # bottom
    paint.drawPixmap(0,   144, platform) # left
    paint.drawPixmap(288, 144, platform) # right
    del paint
    ImageCache['UnusedRotPlatforms'] = img


def LoadMinigameStuff():

    ImageCache['MGCannon'] = GetImg('mg_cannon.png')
    ImageCache['MGChest'] = GetImg('mg_chest.png')
    ImageCache['MGToad'] = GetImg('toad.png')

def LoadCastleGears():

    ImageCache['CastleGearL'] = GetImg('castle_gear_large.png')
    ImageCache['CastleGearS'] = GetImg('castle_gear_small.png')

def LoadBosses():

    ImageCache['LarryKoopa'] = GetImg('Larry_Koopa.png')
    ImageCache['LemmyKoopa'] = GetImg('Lemmy_Koopa.png')
    ImageCache['WendyKoopa'] = GetImg('Wendy_Koopa.png')
    ImageCache['MortonKoopa'] = GetImg('Morton_Koopa.png')
    ImageCache['RoyKoopa'] = GetImg('Roy_Koopa.png')
    ImageCache['LudwigVonKoopa'] = GetImg('Ludwig_Von_Koopa.png')
    ImageCache['IggyKoopa'] = GetImg('Iggy_Koopa.png')
    ImageCache['Kamek'] = GetImg('Kamek.png')
    ImageCache['Bowser'] = GetImg('Bowser.png')



################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################
################################################################


# ---- Generic Helper Functions ----




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
