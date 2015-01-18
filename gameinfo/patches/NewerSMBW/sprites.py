# Newer Super Mario Bros. Wii
# Custom Reggie! Next sprites.py Module
# By Kamek64, MalStar1000, RoadrunnerWMC


from PyQt5 import QtCore, QtGui
Qt = QtCore.Qt


import spritelib as SLib
ImageCache = SLib.ImageCache



class SpriteImage_StarCollectable(SLib.SpriteImage_Static): # 12
	def __init__(self, parent):
		super().__init__(
			parent,
			ImageCache['StarCollectable'],
			(3, 3),
			)

	@staticmethod
	def loadImages():
		SLib.loadIfNotInImageCache('StarCollectable', 'star_collectable.png')


class SpriteImage_ClownCar(SLib.SpriteImage_Static): # 13
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ClownCar'],
            (16, -28),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ClownCar', 'clown_car.png')


class SpriteImage_SamuraiGuy(SLib.SpriteImage_Static): # 19
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SamuraiGuy'],
            (-1, -4),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SamuraiGuy', 'samurai_guy.png')


class SpriteImage_NewerGoomba(SLib.SpriteImage_StaticMultiple): # 20
	@staticmethod
	def loadImages():
		SLib.loadIfNotInImageCache('Goomba', 'goomba.png')
		if 'Goomba1' in ImageCache: return
		for i in range(8):
			ImageCache['Goomba%d' % (i+1)] = SLib.GetImg('goomba_%d.png' % (i+1))

	def dataChanged(self):

		color = (self.parent.spritedata[2] & 0xF) % 9

		if color == 0:
			self.image = ImageCache['Goomba']
			self.offset = (-1, -4)
		else:
			self.image = ImageCache['Goomba%d' % color]
			self.offset = (0, -4) if color not in (7, 8) else (0, -5)

		super().dataChanged()


class SpriteImage_PumpkinGoomba(SLib.SpriteImage_StaticMultiple): # 22
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = (-4, -48)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PumpkinGoomba', 'pumpkin_goomba.png')
        SLib.loadIfNotInImageCache('PumpkinParagoomba', 'pumpkin_paragoomba.png')

    def dataChanged(self):

        para = self.parent.spritedata[5] & 1
        self.image = ImageCache['PumpkinGoomba' if not para else 'PumpkinParagoomba']

        super().dataChanged()


class SpriteImage_FakeStarCoin(SLib.SpriteImage_Static): # 49
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['FakeStarCoin'],
            (-8, -16),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FakeStarCoin', 'starcoin_fake.png')


class SpriteImage_NewerKoopa(SLib.SpriteImage_StaticMultiple): # 57
    @staticmethod
    def loadImages():
        if 'KoopaG' in ImageCache: return
        ImageCache['KoopaG'] = SLib.GetImg('koopa_green.png')
        ImageCache['KoopaR'] = SLib.GetImg('koopa_red.png')
        ImageCache['KoopaShellG'] = SLib.GetImg('koopa_green_shell.png')
        ImageCache['KoopaShellR'] = SLib.GetImg('koopa_red_shell.png')
        for flag in (0, 1):
        	for style in range(4):
        		ImageCache['Koopa%d%d' % (flag, style + 1)] = \
        			SLib.GetImg('koopa_%d%d.png'% (flag, style + 1))
        		if style < 3:
	        		ImageCache['KoopaShell%d%d' % (flag, style + 1)] = \
	        			SLib.GetImg('koopa_shell_%d%d.png'% (flag, style + 1))

    def dataChanged(self):
        # get properties
        props = self.parent.spritedata[5]
        shell = (props >> 4) & 1
        red = props & 1
        texhack = (self.parent.spritedata[2] & 0xF) % 5

        if not shell:

            if texhack == 0:
                self.offset = (-7, -15)
                self.image = ImageCache['KoopaG'] if not red else ImageCache['KoopaR']
            else:
                self.offset = (-5, -13)
                self.image = ImageCache['Koopa%d%d' % (red, texhack)]
        else:
            del self.offset

            if texhack in (0, 4):
                self.image = ImageCache['KoopaShellG'] if not red else ImageCache['KoopaShellR']
            else:
                self.image = ImageCache['KoopaShell%d%d' % (red, texhack)]

        super().dataChanged()


class SpriteImage_BigPumpkin(SLib.SpriteImage_StaticMultiple): # 157
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = (-8, -16)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('BigPumpkin', 'giant_pumpkin.png')
        SLib.loadIfNotInImageCache('ShipKey', 'ship_key.png')
        SLib.loadIfNotInImageCache('5Coin', '5_coin.png')

        if 'YoshiFire' not in ImageCache:
            pix = QtGui.QPixmap(48, 24)
            pix.fill(Qt.transparent)
            paint = QtGui.QPainter(pix)
            paint.drawPixmap(0, 0, ImageCache['Blocks'][9])
            paint.drawPixmap(24, 0, ImageCache['Blocks'][3])
            del paint
            ImageCache['YoshiFire'] = pix

        for power in range(0x10):
            if power in (0, 8, 12, 13):
                ImageCache['BigPumpkin%d' % power] = ImageCache['BigPumpkin']
                continue

            x, y = 36, 48
            overlay = ImageCache['Blocks'][power]
            if power == 9:
                overlay = ImageCache['YoshiFire']
                x = 24
            elif power == 10:
                overlay = ImageCache['5Coin']
            elif power == 14:
                overlay = ImageCache['ShipKey']
                x, y = 34, 42

            new = QtGui.QPixmap(ImageCache['BigPumpkin'])
            paint = QtGui.QPainter(new)
            paint.drawPixmap(x, y, overlay)
            del paint
            ImageCache['BigPumpkin%d' % power] = new

    def dataChanged(self):

        power = self.parent.spritedata[5] & 0xF
        self.image = ImageCache['BigPumpkin%d' % power]
        super().dataChanged()


class SpriteImage_Meteor(SLib.SpriteImage_StaticMultiple): # 183
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Meteor', 'meteor.png')
        SLib.loadIfNotInImageCache('MeteorElectric', 'meteor_electric.png')

    def dataChanged(self):

        multiplier = self.parent.spritedata[4] / 20.0
        if multiplier == 0: multiplier = 0.01
        isElectric = (self.parent.spritedata[5] >> 4) & 1

        # Get the size data, taking into account the size
        # differences between the non-electric and
        # electric varieties.
        sizes = (
            # Relative X offset (size 0x14),
            # relative Y offset (size 0x14),
            # absolute X offset,
            # absolute Y offset
            (-54, -53, 6, -1),
            (-61, -68, 6, 0),
            )
        size = sizes[1] if isElectric else sizes[0]
        relXoff = size[0]
        relYoff = size[1]
        absXoff = size[2]
        absYoff = size[3]

        base = ImageCache['MeteorElectric' if isElectric else 'Meteor']

        self.image = base.scaled(
            (base.width() * multiplier) + 8,
            (base.height() * multiplier) + 8,
            )
        self.offset = (
            (relXoff * multiplier) + absXoff,
            (relYoff * multiplier) + absYoff,
            )

        super().dataChanged()


class SpriteImage_MidwayFlag(SLib.SpriteImage_StaticMultiple): # 188
    def __init__(self, parent):
        super().__init__(parent)
        self.yOffset = -37

    @staticmethod
    def loadImages():
        if 'MidwayFlag0' in ImageCache: return
        for i in range(18):
            ImageCache['MidwayFlag%d' % i] = SLib.GetImg('midway_flag_%d.png' % i)

    def dataChanged(self):

        style = self.parent.spritedata[2]
        if style > 17: style = 0

        self.image = ImageCache['MidwayFlag%d' % style]

        super().dataChanged()


class SpriteImage_Topman(SLib.SpriteImage_Static): # 210
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Topman'],
            (-22, -32),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Topman', 'topman.png')


class SpriteImage_CaptainBowser(SLib.SpriteImage_Static): # 213
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['CaptainBowser'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CaptainBowser', 'captain_bowser.png')


class SpriteImage_RockyBoss(SLib.SpriteImage_Static): # 279
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['RockyBoss'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('RockyBoss', 'rocky_boss.png')


class SpriteImage_AngrySun(SLib.SpriteImage_StaticMultiple): # 282
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('AngrySun', 'angry_sun.png')
        SLib.loadIfNotInImageCache('AngryMoon', 'angry_moon.png')

    def dataChanged(self):

        isMoon = self.parent.spritedata[5] & 1
        self.image = ImageCache['AngrySun' if not isMoon else 'AngryMoon']
        self.offset = (-18, -18) if not isMoon else (-13, -13)

        super().dataChanged()


class SpriteImage_FuzzyBear(SLib.SpriteImage_StaticMultiple): # 283
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FuzzyBear', 'fuzzy_bear.png')
        SLib.loadIfNotInImageCache('FuzzyBearBig', 'fuzzy_bear_big.png')

    def dataChanged(self):

        big = (self.parent.spritedata[2] >> 4) & 1
        self.image = ImageCache['FuzzyBear' if not big else 'FuzzyBearBig']

        super().dataChanged()


class SpriteImage_Boolossus(SLib.SpriteImage_Static): # 290
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Boolossus'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Boolossus', 'boolossus.png')


class SpriteImage_Flipblock(SLib.SpriteImage_Static): # 319
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Flipblock'],
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Flipblock', 'flipblock.png')


class SpriteImage_Podoboule(SLib.SpriteImage_StaticMultiple): # 324
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PodobouleFire', 'podoboule_fire.png')
        SLib.loadIfNotInImageCache('PodobouleIce', 'podoboule_ice.png')

    def dataChanged(self):

        fire = (self.parent.spritedata[2] >> 4) & 1
        self.image = ImageCache['PodobouleFire' if fire else 'PodobouleIce']

        super().dataChanged()


class SpriteImage_ShyGuy(SLib.SpriteImage_StaticMultiple): # 351
    @staticmethod
    def loadImages():
        if 'ShyGuy0' in ImageCache: return
        for i in range(9): # 0-8
            if i == 7: continue # there's no ShyGuy7.png
            ImageCache['ShyGuy%d' % i] = SLib.GetImg('shyguy_%d.png' % i)

    def dataChanged(self):
        type = (self.parent.spritedata[2] >> 4) % 9

        imgtype = type if type != 7 else 6 # both linear ballooneers have image 6
        self.image = ImageCache['ShyGuy%d' % imgtype]

        self.offset = (
            (6, -7), # 0: red
            (6, -7), # 1: blue
            (6, -4), # 2: red (sleeper)
            (7, -6), # 3: yellow (jumper)
            (6, -8), # 4: purple (judo)
            (6, -8), # 5: green (spike thrower)
            (2, -9), # 6: red (ballooneer - vertical)
            (2, -9), # 7: red (ballooneer - horizontal)
            (2, -9), # 8: blue (ballooneer - circular)
            )[type]

        super().dataChanged()


class SpriteImage_GigaGoomba(SLib.SpriteImage_Static): # 410
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['GigaGoomba'],
            (-108, -160),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('GigaGoomba', 'goomba_giga.png')


ImageClasses = {
	12: SpriteImage_StarCollectable,
    13: SpriteImage_ClownCar,
    19: SpriteImage_SamuraiGuy,
    20: SpriteImage_NewerGoomba,
    22: SpriteImage_PumpkinGoomba,
    49: SpriteImage_FakeStarCoin,
    57: SpriteImage_NewerKoopa,
    157: SpriteImage_BigPumpkin,
    183: SpriteImage_Meteor,
    188: SpriteImage_MidwayFlag,
    210: SpriteImage_Topman,
    213: SpriteImage_CaptainBowser,
    279: SpriteImage_RockyBoss,
    282: SpriteImage_AngrySun,
    283: SpriteImage_FuzzyBear,
    290: SpriteImage_Boolossus,
    319: SpriteImage_Flipblock,
    324: SpriteImage_Podoboule,
    351: SpriteImage_ShyGuy,
    410: SpriteImage_GigaGoomba,
    }
