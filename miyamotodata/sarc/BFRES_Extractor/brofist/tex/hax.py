import os, sys, struct, re, subprocess
print('''Texture Hax Script by NWPlayer123

Usage: hax.py file.dds file.bfres minmip texpos
minmip is minimum mipmap size(IE, generate until dimensions <= NxN)
texpos is texture position in BFRES
Use: hax.py file.bfres
''')

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

def hexstr(data, length): #Convert input into hex string
    return hex(data).lstrip("0x").rstrip("L").zfill(length).upper()
def uint8(data, pos):
    return struct.unpack(">B", data[pos:pos + 1])[0]
def uint16(data, pos):
    return struct.unpack(">H", data[pos:pos + 2])[0]
def uint24(data, pos):
    return struct.unpack(">I", "\00" + data[pos:pos + 3])[0] #HAX
def uint32(data, pos):
    return struct.unpack(">I", data[pos:pos + 4])[0]
def getstr(data):
    x = data.find("\x00")
    if x != -1: return data[:x]
    else: return data

if len(sys.argv) == 2: #Assume BFRES
    f = open(sys.argv[1], 'rb')
    bfres = f.read()
    f.close()
    pos = 0
    ftex = [m.start() for m in re.finditer('FTEX', bfres)]
    for x in xrange(len(ftex)):
        pos = ftex[x]
        npos = pos + 0xA8 + uint32(bfres, pos+0xA8)
        name = getstr(bfres[npos:])
        print(str(x).zfill(2) + " " + name)

elif len(sys.argv) == 5:
    gtx1 = sys.argv[1].rstrip(".dds") + ".gtx"
    subprocess.Popen(['texconv2.exe', '-i', sys.argv[1], '-f', formats[0x41a], '-minmip', sys.argv[3], '-o', gtx1])
    i = 0
    for x in xrange(1000000): i += 1 #Delay loop because texconv2 is slow
    f = open(sys.argv[2], "rb")
    bfres = f.read()
    f.close()
    ftex = [m.start() for m in re.finditer('FTEX', bfres)]
    fpos = ftex[int(sys.argv[4])]
    print("BFRES mips: " + str(uint32(bfres, fpos + 0x14) - 1))
    f = open(gtx1, "rb")
    ftex1 = f.read()
    f.close()
    print("GTX mips: " + str(uint32(ftex1, 0x50) - 1))
    print("Swizzle: 0x" + hex(uint32(ftex1, 0x74)).lstrip("0x").upper())
    bfres[fpos+0x38:fpos+0x3C].replace(bfres[fpos+0x38:fpos+0x3C], ftex1[0x74:0x78]) #Set Swizzle
    print("Format: " + formats[uint32(bfres, fpos+0x18)])
    gtx2 = gtx1.rstrip(".gtx") + "1.gtx"
    subprocess.Popen(['texconv2.exe', '-i', gtx1, '-f', formats[uint32(bfres, fpos+0x18)], '-o', gtx2])
    i = 0
    for x in xrange(3000000): i += 1 #Delay loop because texconv2 is slow
    f = open(gtx2, "rb")
    ftex2 = f.read()
    f.close()
    texsize = uint32(ftex2, 0xF0)
    print(hexstr(texsize, 8))
    tpos = 0xFC + texsize
    start = fpos + 0xB0 + uint32(bfres, fpos + 0xB0)
    end   = fpos + 0xB4 + uint32(bfres, fpos + 0xB4)
    bfres = bfres[:start] + ftex2[0xFC:tpos] + bfres[end:]
    if (uint32(ftex1, 0x50) - 1) != 0:
        texsize = uint32(ftex2, tpos + 0x14)
        tpos += 0x20
        bfres = bfres[:end] + ftex2[tpos:tpos + texsize] + bfres[end + texsize:]
    f = open(sys.argv[2], "wb")
    f.write(bfres)
    f.close()
        
        
        
