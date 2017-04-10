import sys, struct, zlib

def uint8(data, pos):
    return struct.unpack(">B", data[pos:pos + 1])[0]
def uint16(data, pos):
    return struct.unpack(">H", data[pos:pos + 2])[0]
def uint24(data, pos):
    return struct.unpack(">I", "\00" + data[pos:pos + 3])[0] #HAX
def uint32(data, pos):
    return struct.unpack(">I", data[pos:pos + 4])[0]
def getstr(string):
    x = string.find("\x00")
    if x != -1:
        return string[:x]
    else:
        return string

print("""RPX Symbols Printer by NWPlayer123
Usage: symbols.py file.rpx/rpl 0/1
1 tells it to just print symbol names""")

text = 1
if len(sys.argv) == 3: #symbols.py file.rpx/rpl 0/1
    if sys.argv[2] == "1": #Just print symbols
        text = 0
if len(sys.argv) not in [2, 3]: sys.exit(1) #No, stop that
f = open(sys.argv[1], "rb") #Assuming symbols.py file.rpx/rpl
rpl = f.read()
f.close()
assert  uint32(rpl, 0) == 2135247942 #.ELF
assert  uint16(rpl, 7) == 51966    #0xCAFE
if text: print( "Looks like a Wii U binary, continuing...")
numsections = uint16(rpl, 0x30)
pos = 0x70;found = 0;secpos = 0
for x in xrange(numsections):
    if uint32(rpl, pos + 4) == 0xC0000000:
        secpos = pos
        found = 1
        break
    pos += 40
if text:
    if found:
        print("Found the right section...")
    else:
        print("Section not found, exiting...")
        sys.exit(1)
offset  = uint32(rpl, secpos + 8) + 4
size    = uint32(rpl, secpos + 12) - 4
symbols = zlib.decompress(rpl[offset:offset + size])
numsymbols = uint32(symbols, 0)
pos = 8 + (8 * (numsymbols + 1))
if text: print
for x in xrange(numsymbols):
    string = getstr(symbols[pos:])
    pos += len(string) + 1
    print(string)
