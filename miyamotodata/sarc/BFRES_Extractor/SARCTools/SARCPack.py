'''Made by NWPlayer123, no rights reserved, feel free to do whatever'''
import os, sys, struct

def hexstr(data, length): #Convert input into hex string
    return hex(data).lstrip("0x").rstrip("L").zfill(length).upper()
def calchash(name):
    result = 0
    for x in xrange(len(name)):
        result = (ord(name[x]) + (result * 0x65)) & 0xFFFFFFFF
    return result

class SimpleArchive(object):
    def pack(self, folder, padding):
        '''Generate string list for finding and writing'''
        filedata = [];lenfiles = 0;numfiles = 0;lennames = 0
        print("Generating file list....")
        for path, dirs, files in os.walk(folder):
            path = "/".join(path.split("\\")[1:]) #Rearrange Paths for writing
            for f in files: #Read each file
                '''Because we're reading one folder in'''
                if path != "": filename = (path + "/" + f)
                else:          filename = f
                realname =     folder + "/" + filename
                print(filename)
                '''Calculate filesize for storing'''
                filesize  =    os.path.getsize(realname)
                if filesize %  padding: filesize += (padding - (filesize % padding))
                '''Calculate name length for writing'''
                namesize  =    len(filename)
                namesize +=    (4 - (namesize % 4))
                lennames +=    namesize
                numfiles +=    1
                filedata.append([filename, realname, filesize, namesize, len(files)])
            print #Pretty print
        '''Calculate hashes and sort'''
        hashes = []
        for x in xrange(numfiles):
            hash = calchash(filedata[x][0])
            hashes.append([hash, x])
        hashes = sorted(hashes, key=lambda hash:hash[0])
        for x in xrange(numfiles - 1):
            lenfiles += filedata[hashes[x][1]][2]
        lastfile = os.path.getsize(filedata[hashes[-1][1]][1])
        lenfiles += lastfile #Don't pad last file
        '''Header + File Entries + SFNT Header + Names'''
        filesize = 32 + (16 * numfiles) + 8 + lennames
        print(filesize)
        padSFAT = (padding - (filesize % padding))
        datastart = padSFAT + filesize
        filesize += padSFAT + lenfiles #Padding and all file data
        '''Time to start writing the SARC'''
        print("Writing SARC Files....")
        sarc = open(folder + ".sarc", "wb") #SARC of the same name
        sarc.write("SARC\x00\x14\xFE\xFF")     #Magic + Hdr Size + Byte Order
        sarc.write(struct.pack(">I", filesize ))
        sarc.write(struct.pack(">I", datastart))
        sarc.write("\x01\x00\x00\x00SFAT\x00\x0C") #Attribute Table
        sarc.write(struct.pack(">H", numfiles))
        sarc.write("\x00\x00\x00\x65") #Hash Multiplier
        strpos = 0;filepos = 0
        for x in xrange(numfiles): #Write the actual table
            sarc.write(struct.pack(">I", hashes[x][0]))
            sarc.write("\x01") #Unknown, see mk8.tockdom.com
            sarc.write(hexstr(strpos / 4, 4).decode("hex").rjust(3, "\x00")) #Ugly
            strpos += filedata[hashes[x][1]][3]
            sarc.write(struct.pack(">I", filepos)) #Start of data
            filesize = os.path.getsize(filedata[hashes[x][1]][1])
            sarc.write(struct.pack(">I", filepos + filesize)) #End of data
            filepos += filedata[hashes[x][1]][2]
        sarc.write("SFNT\x00\x08\x00\x00") #Name Table Header
        for x in xrange(numfiles): #Write all strings
            sarc.write(filedata[hashes[x][1]][0]) #Actual string
            sarc.write("\x00" * (filedata[hashes[x][1]][3] - len(filedata[hashes[x][1]][0])))
        sarc.write("\x00" * padSFAT) #Write padding
        print("Adding file data....")
        for x in xrange(numfiles):
            f = open(filedata[hashes[x][1]][1], "rb")
            sarc.write(f.read())
            f.close()
            filesize = os.path.getsize(filedata[hashes[x][1]][1])
            if x != numfiles - 1: #Don't pad last file
                sarc.write("\x00" * (filedata[hashes[x][1]][2] - filesize))
        sarc.close()
        
def main():
    print("SARCPack v0.2.1 by NWPlayer123")
    if len(sys.argv) not in [2, 3]:
        print("Usage: SARCPack folder [pad value]")
        sys.exit(1)
    if not os.path.isdir(sys.argv[1]): #Not a folder, not gonna bother
        sys.exit(1)
    test = SimpleArchive()
    if len(sys.argv) == 3:
        test.pack(sys.argv[1], sys.argv[2])
    else: #two with a folder
        test.pack(sys.argv[1], 0x100)

if __name__ == "__main__":
    main()
