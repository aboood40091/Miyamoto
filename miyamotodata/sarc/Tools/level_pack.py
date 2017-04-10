import os, sys
import SARC

arc = SARC.SARC_Archive()

path = sys.argv[1]

for file in os.listdir(path):
    file1 = open(os.path.join(path, file), "rb")
    file2 = file1.read()
    file1.close()
    arc.addFile(SARC.File(file, file2))

data = arc.save(0x2000)

output = open(sys.argv[2], 'wb+')
output.write(data)
output.close()
