from fbx import *

import os

inputFolderName = "./fbx/animation/"
outputFolderName = "./output/animation/"
if not os.path.exists(outputFolderName):
    os.makedirs(outputFolderName)

fileList = os.listdir(inputFolderName)
for fbxFileName in fileList:
    fileNameSplit = fbxFileName.split(".")
    if fileNameSplit[1] != "fbx":
        print "[warning] not fbx file exist"
        continue

    outputJsonFileName = fileNameSplit[0]
    print outputJsonFileName

    manager = FbxManager.Create()

    scene = FbxScene.Create(manager, "Scene")

    importer = FbxImporter.Create(manager, "myImporter")
    if not importer.Initialize(inputFolderName + fbxFileName):
        print("Fail: Create Importer ", inputFolderName + fbxFileName)
        continue
    elif not importer.Import(scene):
        print("Fail: Import scene")
        continue

    if importer.GetAnimStackCount() == 0:
        print "error :" + "no animation fbx"
        continue

    globalSettings = scene.GetGlobalSettings()
    timeMode = globalSettings.GetTimeMode()
    currentTakeInfo = importer.GetTakeInfo(0)

    start = currentTakeInfo.mLocalTimeSpan.GetStart()
    stop = currentTakeInfo.mLocalTimeSpan.GetStop()
    period = FbxTime()
    period.SetTime( 0, 0, 0, 1, 0, timeMode)

    frameNum = stop.Get() / period.Get()

    geometryConverter = FbxGeometryConverter(manager)

    geometryConverter.Triangulate(scene, True)

    fbxJson = {}

    fbxJson["frameNum"] = frameNum
    fbxJson["frameInfos"] = {}

    def dumpNodeInfo(node):
        attr = node.GetNodeAttribute()

        if(attr is not None):
            attrType = attr.GetAttributeType()

            if(attrType == FbxNodeAttribute.eSkeleton or attrType == FbxNodeAttribute.eMesh):
                nodeName = node.GetName()

                frameInfo = []

                for frameIndex in range(frameNum):
                    time = start + period * frameIndex
                    mat = scene.GetAnimationEvaluator().GetNodeGlobalTransform(node, time, FbxNode.eSourcePivot, True, True)

                    # FBX SDKの行列は行オーダーなので、WebGLの列オーダーに合わせる
                    matrix = [
                        mat.Get(0, 0), mat.Get(0, 1), mat.Get(0, 2), mat.Get(0, 3),
                        mat.Get(1, 0), mat.Get(1, 1), mat.Get(1, 2), mat.Get(1, 3),
                        mat.Get(2, 0), mat.Get(2, 1), mat.Get(2, 2), mat.Get(2, 3),
                        mat.Get(3, 0), mat.Get(3, 1), mat.Get(3, 2), mat.Get(3, 3),
                    ]

                    frameInfo.append(matrix)

                fbxJson["frameInfos"][nodeName] = frameInfo
                
        # 子nodeを探索し，再帰的にdumpする．
        num_childrens = node.GetChildCount()
        for ci in range(num_childrens):
            child_node = node.GetChild(ci)
            dumpNodeInfo(child_node)

    # Root nodeの取得
    root_node = scene.GetRootNode()

    # 再帰的にnode情報を出力
    dumpNodeInfo(root_node)

    manager.Destroy()

    fbxMetaJson = {}
    fbxMetaJson["frameNum"] = fbxJson["frameNum"]
    fbxMetaJson["frameInfos"] = {}

    # float = Float32Array = 4 byte
    with open(outputFolderName + outputJsonFileName + '.bin', mode='wb') as fout:
        byteOffset = 0
        for meshName in fbxJson["frameInfos"]:
            metaJson = {}
            fbxMetaJson["frameInfos"][meshName] = metaJson

            frameInfo = fbxJson["frameInfos"][meshName]
            import itertools
            frameInfoList = list(itertools.chain.from_iterable(frameInfo))

            length = len(frameInfoList)
            byteLength = length * 4
            import struct
            fout.write(struct.pack(str(length) + "f", *frameInfoList))

            metaJson["byteOffset"] = byteOffset
            metaJson["byteLength"] = byteLength

            byteOffset += byteLength
    
    import json
    of = open(outputFolderName + outputJsonFileName + ".json", "w") #書き込むファイルを開く
    json.dump(fbxMetaJson, of)  # 変数 2 は辞書型
