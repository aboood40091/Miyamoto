# Newer Super Mario Bros. Wii
# Custom Reggie Sprites.py Overwrite
# Most of these images are by Kamek64 and MalStar1000
# A few are by RoadrunnerWMC


def InitHeroCar(sprite): # 13
    if 'HeroCar' not in ImageCache:
        ImageCache['HeroCar'] = GetImg('hero_car.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['HeroCar']
    return (16,-32,40,48)


def InitSamuraiGuy(sprite): # 19
    if 'SamuraiGuy' not in ImageCache:
        ImageCache['SamuraiGuy'] = GetImg('samurai_guy.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SamuraiGuy']
    return (-1,-4,28,29)


def InitPumpkinGoomba(sprite): # 22
    global ImageCache
    if 'PumpkinGoomba' not in ImageCache:
        ImageCache['PumpkinGoomba'] = GetImg('pumpkingoomba.png')
        ImageCache['PumpkinParagoomba'] = GetImg('pumpkinparagoomba.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.dynamicSize = True
    sprite.dynSizer = SizePumpkinGoomba
    return (-4,-48,22,26)


def InitFakeStarcoin(sprite): # 49
    global ImageCache
    if 'FakeCoin' not in ImageCache:
        ImageCache['FakeCoin'] = GetImg('starcoinfake.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['FakeCoin']
    return (-8,-16,32,32)


def InitMeteor(sprite): # 183
    global ImageCache
    if 'Meteor' not in ImageCache:
        ImageCache['Meteor'] = GetImg('Meteor.png')
        ImageCache['MeteorElectric'] = GetImg('MeteorElectric.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeMeteor
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)


def InitTopman(sprite): # 210
    global ImageCache
    if 'Topman' not in ImageCache:
        ImageCache['Topman'] = GetImg('topman.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Topman']
    return (-22,-32,54,44)


def InitCaptainBowser(sprite): # 213
    global ImageCache
    if 'CaptainBowser' not in ImageCache:
        ImageCache['CaptainBowser'] = GetImg('captainbowser.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['CaptainBowser']
    return (0,0,256,197)


def InitRockyBoss(sprite): # 279
    global ImageCache
    if 'RockyBoss' not in ImageCache:
        ImageCache['RockyBoss'] = GetImg('rocky_boss.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['RockyBoss']
    return (0,0,56,48)


def InitMrSun(sprite): # 282
    global ImageCache
    if 'AngrySun' not in ImageCache:
        ImageCache['AngrySun'] = GetImg('angrysun.png')
        ImageCache['AngryMoon'] = GetImg('angrymoon.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeMrSun
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (-2,-2,50,50)


def InitFuzzyBear(sprite): # 283
    global ImageCache
    if 'FuzzyBear' not in ImageCache:
        ImageCache['FuzzyBear'] = GetImg('fuzzy_bear.png')
        ImageCache['FuzzyBearBig'] = GetImg('fuzzy_bear_big.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizeFuzzyBear
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,83,88)


def InitBoolossus(sprite): # 290
    global ImageCache
    if 'Boolossus' not in ImageCache:
        ImageCache['Boolossus'] = GetImg('boolossus.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Boolossus']
    return (0,0,192,176)


def InitFlipblock(sprite): # 319
    global ImageCache
    if 'Flipblock' not in ImageCache:
        ImageCache['Flipblock'] = GetImg('flipblock.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Flipblock']
    return (0,0,16,16)


def InitPodoboule(sprite): # 324
    global ImageCache
    if 'PodobouleIce' not in ImageCache:
        ImageCache['PodobouleIce'] = GetImg('podoboo_boss_ice.png')
        ImageCache['PodobouleFire'] = GetImg('podoboo_boss_fire.png')

    sprite.dynamicSize = True
    sprite.dynSizer = SizePodoboule
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,80,80)


def InitShyGuy(sprite): # 351
    if 'ShyGuy0' not in ImageCache:
        for i in range(9): # 0-8
            if i == 7: continue # there's no ShyGuy7.png
            ImageCache['ShyGuy%d' % i] = GetImg('ShyGuy%d.png' % i)

    sprite.dynamicSize = True
    sprite.dynSizer = SizeShyGuy
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    return (0,0,16,16)


def InitGigaGoomba(sprite): # 410
    global ImageCache
    if 'GoombaGiga' not in ImageCache:
        ImageCache['GoombaGiga'] = GetImg('goomba_giga.png')
    
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['GoombaGiga']
    return (-108,-160,150,180)


Initialisers = {
    13: InitHeroCar,
    19: InitSamuraiGuy,
    22: InitPumpkinGoomba,
    49: InitFakeStarcoin,
    183: InitMeteor,
    210: InitTopman,
    213: InitCaptainBowser,
    279: InitRockyBoss,
    282: InitMrSun,
    283: InitFuzzyBear,
    290: InitBoolossus,
    319: InitFlipblock,
    324: InitPodoboule,
    351: InitShyGuy,
    410: InitGigaGoomba,
    }

################################################################

def SizePumpkinGoomba(sprite): # 22
    paragoomba = ord(sprite.spritedata[5]) & 15
    if not paragoomba:
        sprite.image = ImageCache['PumpkinGoomba']
    else:
        sprite.image = ImageCache['PumpkinParagoomba']


def SizeMeteor(sprite): # 183
    multiplier = ord(sprite.spritedata[4]) / 20.0
    if multiplier == 0: multiplier = 0.01
    isElectric = (ord(sprite.spritedata[5]) >> 4) & 1

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
    x = (relXoff * multiplier) + absXoff
    y = (relYoff * multiplier) + absYoff
    w = (base.width() * multiplier) + 8
    h = (base.height() * multiplier) + 8
    sprite.image = base.scaled(w, h)
    sprite.xoffset = x
    sprite.yoffset = y
    sprite.xsize = (w * 2/3) + 1
    sprite.ysize = (h * 2/3) + 1


def SizeMrSun(sprite): # 282
    type = ord(sprite.spritedata[5]) & 15
    if type:
        sprite.image = ImageCache['AngryMoon']
        sprite.xsize = 40
        sprite.ysize = 40
        sprite.xoffset = -13
        sprite.yoffset = -13
    else:
        sprite.image = ImageCache['AngrySun']
        sprite.xsize = 50
        sprite.ysize = 50
        sprite.xoffset = -18
        sprite.yoffset = -18


def SizeFuzzyBear(sprite): # 283
    style = ord(sprite.spritedata[2]) >> 4
    if style == 0:
        sprite.xsize = 83 # original 83
        sprite.ysize = 88 # original 88
        sprite.xoffset = 00
        sprite.yoffset = 00
        sprite.image = ImageCache['FuzzyBear']
    else:
        sprite.xsize = 105 # original 83
        sprite.ysize = 100 # original 88
        sprite.xoffset = 00
        sprite.yoffset = 00
        sprite.image = ImageCache['FuzzyBearBig']


def SizePodoboule(sprite): # 324
    style = ord(sprite.spritedata[2]) >> 4
    if style == 0:
        sprite.image = ImageCache['PodobouleIce']
    else:
        sprite.image = ImageCache['PodobouleFire']


def SizeShyGuy(sprite): # 351
    type = ord(sprite.spritedata[2]) >> 4
    if type > 8: type = 0 # prevent crashes

    imgtype = type
    if imgtype == 7: imgtype = 6 # both linear ballooneers have image 6
    sprite.image = ImageCache['ShyGuy%d' % imgtype]

    if type in (0, 1): # red, blue
        xs = 18
        ys = 24
        xo = 6
        yo = -7
    elif type == 2: # red (sleeper)
        xs = 22
        ys = 21
        xo = 6
        yo = -4
    elif type == 3: # yellow (jumper)
        xs = 18
        ys = 23
        xo = 7
        yo = -6
    elif type == 4: # purple (judo)
        xs = 19
        ys = 24
        xo = 6
        yo = -8
    elif type == 5: # green (spike thrower)
        xs = 20
        ys = 25
        xo = 6
        yo = -8
    elif type in (6, 7, 8): # ballooneer
        xs = 29
        ys = 57
        xo = 2
        yo = -9

    sprite.xsize = xs
    sprite.ysize = ys
    sprite.xoffset = xo
    sprite.yoffset = yo
