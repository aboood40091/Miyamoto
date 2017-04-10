'''Copyright (C) 2015, NWPlayer123
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, pulverize, distribute,
synergize, compost, defenestrate, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

If the Author of the Software (the "Author") needs a place to crash and
you have a sofa available, you should maybe give the Author a break and
let them sleep on your couch.

If you are caught in a dire situation wherein you only have enough time
to save one person out of a group, and the Author is a member of that
group, you must save the Author.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO BLAH BLAH BLAH ISN"T IT FUNNY
HOW UPPER-CASE MAKES IT SOUND LIKE THE LICENSE IS ANGRY AND SHOUTING AT YOU.'''
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

def main():
    print("IPK Extract by NWPlayer123")
    if len(sys.argv) != 2: #Only want script + file
        print("Usage: %s file.ipk" % sys.argv[0].split("\\")[-1])

    f = open(sys.argv[1], "rb")
    data = f.read()
    f.close()

    folder = sys.argv[1][:-4] #minus .ipk, very hacky but I'm lazy
    pos = 0
    magic = uint32(data, pos);pos += 12
    assert magic == 1357648570 #50EC12BA
    data_offset = uint32(data, pos);pos += 4
    num_files = uint32(data, pos)
    pos = 48 #Skip to file entries
    files = []
    filepos = 0
    for x in xrange(num_files):
        '''Getting data'''
        pos += 4
        filesize = uint32(data, pos);pos += 20
        filedata = uint32(data, pos);pos += 4 #Size of data in file
        filepos += filesize #Counter for debug
        folder_length = uint32(data, pos);pos += 4
        foldername = data[pos:pos + folder_length];pos += folder_length
        file_length = uint32(data, pos);pos += 4 #of the name
        filename = data[pos:pos + file_length];pos += file_length + 8
        print(foldername + filename) #name for debug
        print("Filesize: " + hexstr(filesize, 8)) #debug
        print("File Pos: " + hexstr(filepos + data_offset, 8)) #debug
        print #prettyprint
        '''File writing'''
        try: os.makedirs(folder + "/" + foldername)
        except: pass #Need to do this because os is picky
        f = open(folder + "/" + foldername + filename, "wb")
        datapos = data_offset + filedata #Need to create file data offset
        f.write(data[datapos:datapos + filesize]) #then add size of file
        f.close()

if __name__ == "__main__":
    main()
