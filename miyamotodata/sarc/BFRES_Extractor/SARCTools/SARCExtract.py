'''Made by NWPlayer123, no rights reserved, feel free to do whatever'''
import os, sys, struct

def hexstr(data, length): #Convert input into hex string
    return hex(data).lstrip("0x").rstrip("L").zfill(length).upper()
def binr(byte):
    return bin(byte).lstrip("0b").zfill(8)
def uint8(data, pos):
    return struct.unpack(">B", data[pos:pos + 1])[0]
def uint16(data, pos):
    return struct.unpack(">H", data[pos:pos + 2])[0]
def uint24(data, pos):
    return struct.unpack(">I", "\00" + data[pos:pos + 3])[0] #HAX
def uint32(data, pos):
    return struct.unpack(">I", data[pos:pos + 4])[0]
def check(length, size, percent, count):
    length = float(length);size = float(size)
    test = round(length / size, 2) #Percent complete as decimal
    test = test * 100 #Percent
    if test % count == 0:
        if percent != test: #New Number
            print(str(test)[:-2] + "%")
            percent = test
    return percent
def calchash(name, multiplier):
    result = 0
    for x in xrange(len(name)):
        result = ord(name[x]) + result * multiplier
    return result
def getstr(data):
    x = data.find("\x00")
    if x != -1:
        return data[:x]
    else:
        return data
def intify(out, data, length = 0):
    if type(data) == str:
        for x in xrange(len(data)):
            out.append(ord(data[x]))
    if type(data) == int:
        data = hexstr(data, length * 2)
        for x in xrange(length):
            out.append(int(data[x * 2:(x * 2) + 2], 16))
    return out

class Yaz0(object):
    def decompress(self, data):
        '''Thanks to thakis for yaz0dec, which I modeled this on after
        I cleaned it up in v0.2, what with bit-manipulation and looping
        Thanks to Kinnay for suggestions to make this even faster'''
        print("Decompressing Yaz0....")
        pos = 16
        size = uint32(data, 4) #Uncompressed filesize
        out = [];dstpos = 0
        percent = 0;bits = 0
        if len(data) >= 5242880: count = 5 #5MB is gonna take a while
        else: count = 10
        while len(out) < size: #Read Entire File
            percent = check(len(out), size, percent, count)
            if bits == 0:
                code = uint8(data, pos);pos += 1;bits = 8
            if (code & 0x80) != 0: #Copy 1 Byte
                out.append(data[pos]);pos += 1
            else:
                rle = uint16(data, pos);pos += 2
                dist = rle & 0xFFF
                dstpos = len(out) - (dist + 1)
                read = (rle >> 12)
                if (rle >> 12) == 0:
                    read = ord(data[pos]) + 0x12;pos += 1
                else:
                    read += 2
                for x in xrange(read):
                    out.append(out[dstpos + x])
            code <<= 1;bits -= 1
        out = "".join(out)
        SARChive = SARC()
        SARChive.extract(out, 1)

class SARC(object):
    def extract(self, data, mode):
        print("Reading SARC....")
        pos = 6
        if mode == 1: #Don"t need to check again with normal SARC
            magic1 = data[0:4]
            if magic1 != "SARC":
                print("Not a SARC Archive!")
                print("Writing Decompressed File....")
                f = open(name + ".bin", "wb")
                f.write(data)
                f.close()
                print("Done!")
        name, ext = os.path.splitext(sys.argv[1])
        order = uint16(data, pos);pos += 6 #Byte Order Mark
        if order != 65279: #0xFEFF - Big Endian
            print("Little endian not supported!")
            sys.exit(1)
        doff = uint32(data, pos);pos += 8 #Start of data section
        #---------------------------------------------------------------
        magic2 = data[pos:pos + 4];pos += 6
        assert magic2 == "SFAT"
        nodec = uint16(data, pos);pos += 6 #Node Count
        nodes = [];percent = 0
        print("Reading File Attribute Table...")
        for x in xrange(nodec):
            pos += 8
            srt  = uint32(data, pos);pos += 4 #File Offset Start
            end  = uint32(data, pos);pos += 4 #File Offset End
            nodes.append([srt, end])
        #---------------------------------------------------------------
        magic3 = data[pos:pos + 4];pos += 8
        assert magic3 == "SFNT"
        strings = [];percent = 0
        print("Reading Filenames....")
        nonames = 0
        if getstr(data[pos:]) == "":
            print("No filenames found....")
            nonames = 1
            for x in xrange(nodec):
                strings.append("bfbin" + str(x) + ".bfbin")
        else:
            for x in xrange(nodec):
                string = getstr(data[pos:]);pos += len(string)
                while ord(data[pos]) == 0: pos += 1 #Move to the next string
                strings.append(string)
        #---------------------------------------------------------------
        print("Writing Files....")
        try: os.mkdir(name)
        except: print("Folder already exists, continuing....")
        print
        
        if nonames:
            print("ayy lmao")
            '''Let's do some guessing, shall we?'''
            bflim = 0
            bflan = 0
            bflyt = 0
        for x in xrange(nodec):
            filename = name + "/" + strings[x]
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
            filedata = data[doff + nodes[x][0]:doff + nodes[x][1]]
            if nonames:
                if filedata[-0x28:-0x24] == "FLIM":
                    filename = name + "/" + "bflim" + str(bflim) + ".bflim"
                    bflim += 1
                if filedata[0:4] == "FLAN":
                    filename = name + "/" + "bflan" + str(bflim) + ".bflan"
                    bflan += 1
                if filedata[0:4] == "FLYT":
                    filename = name + "/" + "bflyt" + str(bflim) + ".bflyt"
                    bflyt += 1
            print(filename)
            f = open(filename, "wb")
            f.write(filedata)
            f.close()
        print("Done!")

def main():
    print("SARCExtract v0.4 by NWPlayer123")
    print("Thanks to Kinnay and thakis")
    if len(sys.argv) != 2:
        print("Usage: SARCExtract archive.szs")
        sys.exit(1)
    f = open(sys.argv[1], "rb")
    data = f.read()
    f.close()
    magic = data[0:4]
    if magic == "Yaz0":
        SARChive = Yaz0()
        SARChive.decompress(data)
    elif magic == "SARC":
        SARChive = SARC()
        SARChive.extract(data, 0)
    else:
        print("Unknown File Format!")
        sys.exit(1)

if __name__ == "__main__":
    main()
