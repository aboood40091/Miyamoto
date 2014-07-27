# Newer Summer Sun
# Custom Reggie Sprites.py Module
# By RoadrunnerWMC


import spritelib as SLib
ImageCache = SLib.ImageCache



class SpriteImage_CustomModelSprite(SLib.SpriteImage_SimpleDynamic): # 11
    @staticmethod
    def loadImages():
        if 'ModeAnim01' in ImageCache: return
        for anim in (True, False):
            for model in range(0x15):
                name = 'model_%s%02X.png' % ('anim_' if anim else '', model)
                img = SLib.GetImg(name)
                if img != None: ImageCache['Model%s%02X' % (('Anim' if anim else ''), model)] = img

    def updateSize(self):

        # Get all neccessary values: anim, type, and multiplier
        anim = self.parent.spritedata[4] & 1
        type = self.parent.spritedata[5]
        if (type in (0, 8, 9)) or (type > 0x11): type = None
        if not anim:
            # Non-animated models use the same 3 images
            if type in (1, 2, 3, 4, 5, 6, 7): type = 1
            elif type in (0xA, 0xB, 0xC, 0xD, 0xE, 0xF): type = 0xA
            elif type in (0x10, 0x11): type = 0x10
        size = self.parent.spritedata[2]
        if size == 0: size = 4 # sizes 0 and 4 are identical
        multiplier = size / 8 # all images are taken at size 8

        if type is None:
            # Take away the image
            del self.dimensions
            self.spritebox.shown = True
            return
        else:
            self.spritebox.shown = False

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

        # Pick an image and scale it
        img = ImageCache['Model%s%02X' % ('Anim' if anim else '', type)]
        w = img.width() * multiplier
        h = img.height() * multiplier
        img = img.scaled(w, h)
        self.image = img

        # Set up the image position and size
        pos = animPositions[type] if anim else nonanimPositions[type]
        self.offset = (
            pos[0] * multiplier,
            pos[1] * multiplier,
            )

        super().updateSize()


class SpriteImage_CharginChuck(SLib.SpriteImage_Static): # 102
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['CharginChuck'],
            (-9, -24),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('CharginChuck', 'charginchuck.png')


class SpriteImage_ChompStatueOpen(SLib.SpriteImage_Static): # 143
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ChompStatueOpen'],
            (-70, -101),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ChompStatueOpen', 'chompstatueopen.png')


class SpriteImage_Unagi(SLib.SpriteImage_Static): # 193
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['Unagi'],
            (-11, -17),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('Unagi', 'unagi.png')


class SpriteImage_ChompStatueClosed(SLib.SpriteImage_Static): # 143
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['ChompStatueClosed'],
            (-70, -69),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('ChompStatueClosed', 'chompstatueclosed.png')


class SpriteImage_SumSunRaft(SLib.SpriteImage_Static): # 143
    def __init__(self, parent):
        super().__init__(
            parent,
            ImageCache['SumSunRaft'],
            (-16, -20),
            )

    @staticmethod
    def loadImages():
        SLib.loadIfNotInImageCache('SumSunRaft', 'raft.png')


ImageClasses = {
    11: SpriteImage_CustomModelSprite,
    102: SpriteImage_CharginChuck,
    143: SpriteImage_ChompStatueOpen,
    193: SpriteImage_Unagi,
    321: SpriteImage_ChompStatueClosed,
    368: SpriteImage_SumSunRaft,
    }
