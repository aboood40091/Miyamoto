# Newer Super Mario Bros. Wii
# Custom Reggie! Next sprites.py Module
# By Kamek64, MalStar1000, RoadrunnerWMC


import spritelib as SLib
ImageCache = SLib.ImageCache



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


class SpriteImage_PumpkinGoomba(SLib.SpriteImage_StaticMultiple): # 22
    def __init__(self, parent):
        super().__init__(parent)
        self.offset = (-4, -48)

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('PumpkinGoomba', 'pumpkin_goomba.png')
        SLib.loadIfNotInImageCache('PumpkinParagoomba', 'pumpkin_paragoomba.png')

    def updateSize(self):

        para = self.parent.spritedata[5] & 1
        self.image = ImageCache['PumpkinGoomba' if not para else 'PumpkinParagoomba']

        super().updateSize()


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


class SpriteImage_Meteor(SLib.SpriteImage_StaticMultiple): # 183
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Meteor', 'meteor.png')
        SLib.loadIfNotInImageCache('MeteorElectric', 'meteor_electric.png')

    def updateSize(self):

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

        super().updateSize()


class SpriteImage_MidwayFlag(SLib.SpriteImage_StaticMultiple): # 188
    def __init__(self, parent):
        super().__init__(parent)
        self.yOffset = -37

    @staticmethod
    def loadImages():
        if 'MidwayFlag0' in ImageCache: return
        for i in range(18):
            ImageCache['MidwayFlag%d' % i] = SLib.GetImg('midway_flag_%d.png' % i)

    def updateSize(self):

        style = self.parent.spritedata[2]
        if style > 17: style = 0

        self.image = ImageCache['MidwayFlag%d' % style]

        super().updateSize()


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

    def updateSize(self):

        isMoon = self.parent.spritedata[5] & 1
        self.image = ImageCache['AngrySun' if not isMoon else 'AngryMoon']
        self.offset = (-18, -18) if not isMoon else (-13, -13)

        super().updateSize()


class SpriteImage_FuzzyBear(SLib.SpriteImage_StaticMultiple): # 283
    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('FuzzyBear', 'fuzzy_bear.png')
        SLib.loadIfNotInImageCache('FuzzyBearBig', 'fuzzy_bear_big.png')

    def updateSize(self):

        big = (self.parent.spritedata[2] >> 4) & 1
        self.image = ImageCache['FuzzyBear' if not big else 'FuzzyBearBig']

        super().updateSize()


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

    def updateSize(self):

        fire = (self.parent.spritedata[2] >> 4) & 1
        self.image = ImageCache['PodobouleFire' if fire else 'PodobouleIce']

        super().updateSize()


class SpriteImage_ShyGuy(SLib.SpriteImage_StaticMultiple): # 351
    @staticmethod
    def loadImages():
        if 'ShyGuy0' in ImageCache: return
        for i in range(9): # 0-8
            if i == 7: continue # there's no ShyGuy7.png
            ImageCache['ShyGuy%d' % i] = SLib.GetImg('shyguy_%d.png' % i)

    def updateSize(self):
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

        super().updateSize()


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
    13: SpriteImage_ClownCar,
    19: SpriteImage_SamuraiGuy,
    22: SpriteImage_PumpkinGoomba,
    49: SpriteImage_FakeStarCoin,
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
