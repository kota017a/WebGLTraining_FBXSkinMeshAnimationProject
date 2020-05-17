from PIL import Image
import numpy

import os

outputFolderName = "./output/texture/"
if not os.path.exists(outputFolderName):
    os.makedirs(outputFolderName)

fileList = os.listdir("./texture")

for tgaFileName in fileList:
    fileNameSplit = tgaFileName.split(".")
    if fileNameSplit[1] != "tga":
        print "[warning] not tga file exist"
        continue

    outputJsonFileName = fileNameSplit[0]
    print outputJsonFileName

    img = Image.open("./texture/" + tgaFileName)

    imgArray = numpy.asarray(img)

    tgaJson = {}
    tgaJson["name"] = outputJsonFileName
    tgaJson["size"] = img.size
    tgaJson["mode"] = img.mode

    import json
    of = open(outputFolderName + outputJsonFileName + ".json", "w") #書き込むファイルを開く
    json.dump(tgaJson, of) #変数 2 は辞書型

    imgList = imgArray.flatten().tolist()
    
    with open( outputFolderName + outputJsonFileName + '.bin', mode='wb') as fout:
        import struct
        fout.write(struct.pack(str(len(imgList)) + "B", *imgList))
