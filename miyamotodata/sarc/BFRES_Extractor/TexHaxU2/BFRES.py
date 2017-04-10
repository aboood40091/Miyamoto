from binascii import hexlify, unhexlify
from shutil import copyfile
from subprocess import Popen
try: import __builtin__
except: import builtins as __builtin__
import sys

def hex(value):
    if value == 0: return "NULL"
    else: return "".join(["0x" ,
        __builtin__.hex(value).lstrip("0x").rstrip("L").upper()])

def read(handle, size):
    return int(hexlify(handle.read(size)), 16)

def getstr(handle):
    string = b""; char = handle.read(1)
    while char != b"\x00":
        string += char
        char = handle.read(1)
    return string

formats = {0x00000000: 'GX2_SURFACE_FORMAT_INVALID',
           0x00000001: 'GX2_SURFACE_FORMAT_TC_R8_UNORM',
           0x00000101: 'GX2_SURFACE_FORMAT_TC_R8_UINT',
           0x00000201: 'GX2_SURFACE_FORMAT_TC_R8_SNORM',
           0x00000301: 'GX2_SURFACE_FORMAT_TC_R8_SINT',
           0x00000002: 'GX2_SURFACE_FORMAT_T_R4_G4_UNORM',
           0x00000005: 'GX2_SURFACE_FORMAT_TCD_R16_UNORM',
           0x00000105: 'GX2_SURFACE_FORMAT_TC_R16_UINT',
           0x00000205: 'GX2_SURFACE_FORMAT_TC_R16_SNORM',
           0x00000305: 'GX2_SURFACE_FORMAT_TC_R16_SINT',
           0x00000806: 'GX2_SURFACE_FORMAT_TC_R16_FLOAT',
           0x00000007: 'GX2_SURFACE_FORMAT_TC_R8_G8_UNORM',
           0x00000107: 'GX2_SURFACE_FORMAT_TC_R8_G8_UINT',
           0x00000207: 'GX2_SURFACE_FORMAT_TC_R8_G8_SNORM',
           0x00000307: 'GX2_SURFACE_FORMAT_TC_R8_G8_SINT',
           0x00000008: 'GX2_SURFACE_FORMAT_TCS_R5_G6_B5_UNORM',
           0x0000000a: 'GX2_SURFACE_FORMAT_TC_R5_G5_B5_A1_UNORM',
           0x0000000b: 'GX2_SURFACE_FORMAT_TC_R4_G4_B4_A4_UNORM',
           0x0000000c: 'GX2_SURFACE_FORMAT_TC_A1_B5_G5_R5_UNORM',
           0x0000010d: 'GX2_SURFACE_FORMAT_TC_R32_UINT',
           0x0000030d: 'GX2_SURFACE_FORMAT_TC_R32_SINT',
           0x0000080e: 'GX2_SURFACE_FORMAT_TCD_R32_FLOAT',
           0x0000000f: 'GX2_SURFACE_FORMAT_TC_R16_G16_UNORM',
           0x0000010f: 'GX2_SURFACE_FORMAT_TC_R16_G16_UINT',
           0x0000020f: 'GX2_SURFACE_FORMAT_TC_R16_G16_SNORM',
           0x0000030f: 'GX2_SURFACE_FORMAT_TC_R16_G16_SINT',
           0x00000810: 'GX2_SURFACE_FORMAT_TC_R16_G16_FLOAT',
           0x00000011: 'GX2_SURFACE_FORMAT_D_D24_S8_UNORM',
           0x00000011: 'GX2_SURFACE_FORMAT_T_R24_UNORM_X8',
           0x00000111: 'GX2_SURFACE_FORMAT_T_X24_G8_UINT',
           0x00000811: 'GX2_SURFACE_FORMAT_D_D24_S8_FLOAT',
           0x00000816: 'GX2_SURFACE_FORMAT_TC_R11_G11_B10_FLOAT',
           0x00000019: 'GX2_SURFACE_FORMAT_TCS_R10_G10_B10_A2_UNORM',
           0x00000119: 'GX2_SURFACE_FORMAT_TC_R10_G10_B10_A2_UINT',
           0x00000219: 'GX2_SURFACE_FORMAT_T_R10_G10_B10_A2_SNORM',
           0x00000219: 'GX2_SURFACE_FORMAT_TC_R10_G10_B10_A2_SNORM',
           0x00000319: 'GX2_SURFACE_FORMAT_TC_R10_G10_B10_A2_SINT',
           0x0000001a: 'GX2_SURFACE_FORMAT_TCS_R8_G8_B8_A8_UNORM',
           0x0000011a: 'GX2_SURFACE_FORMAT_TC_R8_G8_B8_A8_UINT',
           0x0000021a: 'GX2_SURFACE_FORMAT_TC_R8_G8_B8_A8_SNORM',
           0x0000031a: 'GX2_SURFACE_FORMAT_TC_R8_G8_B8_A8_SINT',
           0x0000041a: 'GX2_SURFACE_FORMAT_TCS_R8_G8_B8_A8_SRGB',
           0x0000001b: 'GX2_SURFACE_FORMAT_TCS_A2_B10_G10_R10_UNORM',
           0x0000011b: 'GX2_SURFACE_FORMAT_TC_A2_B10_G10_R10_UINT',
           0x0000081c: 'GX2_SURFACE_FORMAT_D_D32_FLOAT_S8_UINT_X24',
           0x0000081c: 'GX2_SURFACE_FORMAT_T_R32_FLOAT_X8_X24',
           0x0000011c: 'GX2_SURFACE_FORMAT_T_X32_G8_UINT_X24',
           0x0000011d: 'GX2_SURFACE_FORMAT_TC_R32_G32_UINT',
           0x0000031d: 'GX2_SURFACE_FORMAT_TC_R32_G32_SINT',
           0x0000081e: 'GX2_SURFACE_FORMAT_TC_R32_G32_FLOAT',
           0x0000001f: 'GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_UNORM',
           0x0000011f: 'GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_UINT',
           0x0000021f: 'GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_SNORM',
           0x0000031f: 'GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_SINT',
           0x00000820: 'GX2_SURFACE_FORMAT_TC_R16_G16_B16_A16_FLOAT',
           0x00000122: 'GX2_SURFACE_FORMAT_TC_R32_G32_B32_A32_UINT',
           0x00000322: 'GX2_SURFACE_FORMAT_TC_R32_G32_B32_A32_SINT',
           0x00000823: 'GX2_SURFACE_FORMAT_TC_R32_G32_B32_A32_FLOAT',
           0x00000031: 'GX2_SURFACE_FORMAT_T_BC1_UNORM',
           0x00000431: 'GX2_SURFACE_FORMAT_T_BC1_SRGB',
           0x00000032: 'GX2_SURFACE_FORMAT_T_BC2_UNORM',
           0x00000432: 'GX2_SURFACE_FORMAT_T_BC2_SRGB',
           0x00000033: 'GX2_SURFACE_FORMAT_T_BC3_UNORM',
           0x00000433: 'GX2_SURFACE_FORMAT_T_BC3_SRGB',
           0x00000034: 'GX2_SURFACE_FORMAT_T_BC4_UNORM',
           0x00000234: 'GX2_SURFACE_FORMAT_T_BC4_SNORM',
           0x00000035: 'GX2_SURFACE_FORMAT_T_BC5_UNORM',
           0x00000235: 'GX2_SURFACE_FORMAT_T_BC5_SNORM',
           0x00000081: 'GX2_SURFACE_FORMAT_T_NV12_UNORM'}

def validateBFRES(f, debug=False):
    assert f.read(4) == b"FRES" #Magic
    f.seek(8)
    assert f.read(2) == b"\xFE\xFF" #Big Endian
    f.seek(0, 2)
    size = f.tell() #Entire file
    f.seek(12)
    assert read(f, 4) == size
    if debug:
        print("Size: " + hex(size))
        print("Align: " + hex(read(f, 4)))
    f.seek(read(f, 4) - 4, 1)
    if debug:
        print(b"Name: " + getstr(f))
    f.seek(0x18)
    if debug:
        print("".join(["String Table: ", hex(read(f, 4)).rjust(7), "  bytes"]))
        print("".join(["String Table: ", hex(f.tell() + read(f, 4)), " offset\n"]))

def getTexInfo(num, name):
    num = int(num)
    with open(name, "rb") as f:
        validateBFRES(f)
        f.seek(0x24)
        print("======= Texture " + str(num) + " =======")
        f.seek(read(f, 4) - 4, 1) #FTEX Table
        f.seek(8 + ((num + 1) * 16) + 8, 1)
        pos = f.tell()
        f.seek(read(f, 4) - 4, 1) #Texture name
        print(b"Name: " + getstr(f))
        f.seek(pos + 4)
        f.seek(read(f, 4), 1) #Section offset
        texInfo = []
        for i in range(9):
            texInfo.append(read(f, 4))
        f.seek(4, 1)
        texInfo.append(read(f, 4))
        f.seek(4, 1)
        for i in range(4):
            texInfo.append(read(f, 4))
        f.seek(0x6C, 1)
        texInfo.append(f.tell() + read(f, 4))
        texInfo.append(f.tell() + read(f, 4))
        
        print("".join(["dim        = ", str(texInfo[0])]))
        print("".join(["width      = ", str(texInfo[1])]))
        print("".join(["height     = ", str(texInfo[2])]))
        print("".join(["depth      = ", str(texInfo[3])]))
        print("".join(["numMips    = ", str(texInfo[4])]))
        print("".join(["format     = ", formats[texInfo[5]]]))
        print("".join(["aa         = ", str(texInfo[6])]))
        print("".join(["use        = ", str(texInfo[7])]))
        print("".join(["imageSize  = ", hex(texInfo[8])]))
        print("".join(["mipSize    = ", hex(texInfo[9])]))
        print("".join(["tileMode   = ", str(texInfo[10])]))
        print("".join(["swizzle    = ", hex(texInfo[11])]))
        print("".join(["alignment  = ", str(texInfo[12])]))
        print("".join(["pitch      = ", str(texInfo[13])]))
        print("".join(["dataOffset = ", hex(texInfo[14])]))
        print("".join(["mipOffset  = ", hex(texInfo[15]), "\n"]))
    return texInfo

def injectTexture(dds, num, name):
    num = int(num)
    texInfo = getTexInfo(num, name)
    copyfile(name, name + ".bak")
    gtx = dds.rstrip("dds") + "gtx"
    Popen(["texconv2.exe", "-f", formats[0x41A], "-i", dds, "-o", gtx]).wait()
    if texInfo[4] != 0:
        Popen(["texconv2.exe", "-f", formats[texInfo[5]], "-minmip", "1",
           "-swizzle", str((texInfo[11] & 0xFFF) >> 8), "-i", gtx, "-o", gtx]).wait()
    else:
        Popen(["texconv2.exe", "-f", formats[texInfo[5]], "-swizzle",
               str((texInfo[11] & 0xFFF) >> 8), "-i", gtx, "-o", gtx]).wait()
    
    gtx = dds.rstrip("dds") + "gtx"
    with open(gtx, "rb") as f:
        f.seek(0xDC, 0)
        assert f.read(4) == b"BLK{" #Main image
        f.seek(texInfo[8] + 0x1C, 1)
        assert f.read(4) == b"BLK{" #Mipmap data
        f.seek(texInfo[9] + 0x1C, 1)
        assert f.read(4) == b"BLK{" #End of GTX
        #Everything looks good

    with open(name, "rb+") as out:
        with open(gtx, "rb") as f:
            out.seek(texInfo[14])
            f.seek(0xFC, 0)
            out.write(f.read(texInfo[8]))
            out.seek(texInfo[15])
            f.seek(0x20, 1)
            out.write(f.read(texInfo[9]))
        

if __name__ == "__main__":
    print("BFRES Texture Explorer v0.1")
    print("By NWPlayer123, June 24, 2016")
    print("Usage: BFRES.py [-printinfo num/all] [-replace dds num] file.bfres\n")

    try: assert len(sys.argv) > 1
    except: sys.exit(1) #Just print help
    for var in sys.argv:
        if var == "-printinfo":
            num = sys.argv[sys.argv.index("-printinfo") + 1]
            if num.lower() == "all":
                with open(sys.argv[-1], "rb") as f:
                    f.seek(0x52)
                    count = read(f, 2)
                for i in range(count):
                    getTexInfo(i, sys.argv[-1])
            else:
                getTexInfo(num, sys.argv[-1])
        elif var == "-replace":
            num = sys.argv.index("-replace")
            injectTexture(sys.argv[num + 1], sys.argv[num + 2], sys.argv[-1])
