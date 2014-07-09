# Newer Summer Sun
# Custom Reggie Sprites.py Overwrite

def InitCustomModelSprite(sprite): # 11
    if 'ModeAnim01' not in ImageCache:
        for anim in (True, False):
            for model in range(0x15):
                name = 'model_%s%02X.png' % ('anim_' if anim else '', model)
                img = GetImg(name)
                if img != None: ImageCache['Model%s%02X' % (('Anim' if anim else ''), model)] = img

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.dynamicSize = True
    sprite.dynSizer = SizeCustomModelSprite
    return (0,0,16,16)

def InitCharginChuck(sprite): # 102
    if 'CharginChuck' not in ImageCache:
        ImageCache['CharginChuck'] = GetImg('charginchuck.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['CharginChuck']
    return (-9,-24,34,42)

def InitChompStatueOpen(sprite): # 143
    if 'ChompStatueOpen' not in ImageCache:
        ImageCache['ChompStatueOpen'] = GetImg('chompstatueopen.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ChompStatueOpen']
    return (-70,-101,172,172)

def InitUnagi(sprite): # 193
    if 'Unagi' not in ImageCache:
        ImageCache['Unagi'] = GetImg('unagi.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['Unagi']
    return (-11,-17,47,285)

def InitChompStatueClosed(sprite): # 321
    if 'ChompStatueClosed' not in ImageCache:
        ImageCache['ChompStatueClosed'] = GetImg('chompstatueclosed.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['ChompStatueClosed']
    return (-70,-69,172,172)

def InitSumSunRaft(sprite): # 368
    if 'SumSunRaft' not in ImageCache:
        ImageCache['SumSunRaft'] = GetImg('raft.png')

    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject
    sprite.image = ImageCache['SumSunRaft']
    return (-16,-20,225,40)


Initialisers = {
    11: InitCustomModelSprite,
    102: InitCharginChuck,
    143: InitChompStatueOpen,
    193: InitUnagi,
    321: InitChompStatueClosed,
    368: InitSumSunRaft,
    }

def SizeCustomModelSprite(sprite): # 11
    # Get all neccessary values: anim, type, and multiplier
    anim = ord(sprite.spritedata[4]) & 1
    type = ord(sprite.spritedata[5])
    if (type in (0, 8, 9)) or (type > 0x11): type = None
    if not anim:
        # Non-animated models use the same 3 images
        if type in (1, 2, 3, 4, 5, 6, 7): type = 1
        elif type in (0xA, 0xB, 0xC, 0xD, 0xE, 0xF): type = 0xA
        elif type in (0x10, 0x11): type = 0x10
    size = ord(sprite.spritedata[2])
    if size == 0: size = 4 # sizes 0x00 and 0x04 are identical
    multiplier = size/8.0 # all images are taken at size 8
    if type == None:
        # Take away the image
        sprite.customPaint = False
        sprite.customPainter = None
        sprite.xsize = 16
        sprite.ysize = 16
        sprite.xoffset = 0
        sprite.yoffset = 0
        return

    animPositions = {
        # Usage: (xpos, ypos)
        # One entry per model animation
        # No 0x00 (crash)
        0x01: (-76, -92),
        0x02: (-41, -92),
        0x03: (-73, -86),
        0x04: (-75, -88),
        0x05: (-39, -86),
        0x06: (-39, -88),
        0x07: (-38, -77),
        # No 0x08 (crash)
        # No 0x09 (crash)
        0x0A: (-42, -129),
        0x0B: (-41, -129),
        0x0C: (-41, -129),
        0x0D: (-52, -129),
        0x0E: (-44, -129),
        0x0F: (-42, -129),
        0x10: (-189, -409),
        0x11: (-217, -60),
        }
    nonanimPositions = {
        # Same usage as animPositions
        # One entry per model
        0x01: (-42, -175),
        0x0A: (-43, -130),
        0x10: (-232, -407),
        }

    # Set up the Reggie stuff to display an image
    sprite.customPaint = True
    sprite.customPainter = PaintGenericObject

    # Pick an image and scale it
    img = ImageCache['Model%s%02X' % ('Anim' if anim else '', type)]
    w = img.width() * multiplier
    h = img.height() * multiplier
    img = img.scaled(w, h)
    sprite.image = img

    # Set up the image position and size
    pos = animPositions[type] if anim else nonanimPositions[type]
    sprite.xoffset = (pos[0] * multiplier)
    sprite.yoffset = (pos[1] * multiplier)
    sprite.xsize = int(w*2.0/3) + 1
    sprite.ysize = int(h*2.0/3) + 1

