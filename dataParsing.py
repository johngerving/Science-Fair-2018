import sys

def load(file):
    try:
        with open(file) as in_file:
            loaded_txt = in_file.read().strip().split('\n')
            return loaded_txt
    except IOError as e:
        print("{}\nError opening {}. Terminating program.".format(e, file), file=sys.stderr)
    sys.exit(1)

fileList = load("ETData4.txt")
newFileList = []
newNewFileList = []
newNewNewFileList = []

chars = "0123456789"

fireCount = 0
total = 0
for line in range(len(fileList)):
    if(fileList[line] != ""):
        newFileList.append(fileList[line])
for line in range(len(newFileList)):
    if(newFileList[line][0] not in chars):
        newNewFileList.append(newFileList[line])
for line in range(len(newNewFileList)):
    if(newNewFileList[line][0] == "[" and newNewFileList[line][-1] == "]" and len(newNewFileList[line]) > 2):
        newNewNewFileList.append(newNewFileList[line][1:-1])
    elif(fileList[line] == "[]"):
        newNewNewFileList.append("N")
    else:
        newNewNewFileList.append(newNewFileList[line])
for line in range(len(newNewNewFileList)):
    if(newNewNewFileList[line].startswith("List") and newNewNewFileList[line + 1].startswith("List")):
        print("Error:\n" + newNewNewFileList[line] + "\n" + newNewNewFileList[line + 1])

    if(newNewNewFileList[line] == "9" or newNewNewFileList[line] == "8"):
        fireCount += 1
        total += 1
    elif(newNewNewFileList[line] == "4" or newNewNewFileList[line] == "5"):
        total += 1
print(fireCount/total)

filename = "NewETData4.txt"
newFile = open(filename, 'w')

for line in newNewNewFileList:
    newFile.write(line + '\n')

newFile.close()
