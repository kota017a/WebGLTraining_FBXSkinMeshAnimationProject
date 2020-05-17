from fbx import *

inputFolderName = "./fbx/"

fbxFileName = "unitychan"

# TODO python の FBX SDK だと、template関係でGetSrcObjectが使えないっぽいので、テクスチャの名前が取れない...
# しょうがないので、ファイル名との対応表を別途手作業で作って、用意している...
unityMeshMaterialTextureJsonMap = {
    "body": "body_01",
    "eyeline": "eyeline_00",
    "skin1": "skin_01",
    "face": "face_00",
    "eye_R1": "eye_iris_R_00",
    "hair": "hair_01",
    "eye_L1": "eye_iris_L_00",
    "eyebase": "eyeline_00",
    "mat_cheek": "cheek_00",
}

import os
outputFolderName = "./output/"
if not os.path.exists(outputFolderName):
    os.makedirs(outputFolderName)

outputJsonFileName = fbxFileName

manager = FbxManager.Create()

scene = FbxScene.Create(manager, "Scene")

importer = FbxImporter.Create(manager, "myImporter")
if not importer.Initialize(inputFolderName + fbxFileName + ".fbx"):
    print("Fail: Create Importer ", inputFolderName + fbxFileName + ".fbx")
elif not importer.Import(scene):
    print("Fail: Import scene")

geometryConverter = FbxGeometryConverter(manager)

# 4頂点ポリゴンが混ざっているので...
geometryConverter.Triangulate(scene, True)

fbxJson = {}

fbxJson["materialTextureFileNameMap"] = unityMeshMaterialTextureJsonMap
fbxJson["animationFileList"] = map(lambda n: n.split(".")[0], os.listdir("./fbx/animation/"))
fbxJson["meshInfo"] = {}

def dumpNodeInfo(node):
    attr = node.GetNodeAttribute()

    if(attr is not None):
        attrType = attr.GetAttributeType()
        if(attrType == FbxNodeAttribute.eMesh):
            meshJson = {}
            mesh = attr

            print node.GetName()

            meshNode = mesh.GetNode()
            if(meshNode != 0):
                materialNum = meshNode.GetMaterialCount()
                if(materialNum != 0):
                    for materialIndex in range(materialNum):
                        material = meshNode.GetMaterial(materialIndex)
                        if (material != 0):
                            meshJson["materialName"] = material.GetName()
                            diffuseProperty = material.FindProperty(FbxSurfaceMaterial.sDiffuse)
                            # TODO python の FBX SDK だと、template関係でGetSrcObjectが使えないっぽいので、テクスチャの名前が取れない...
                            # https://help.autodesk.com/view/FBX/2017/ENU/?guid=__files_GUID_363E55D8_6EDB_40F8_8F58_E42F8D525D3D_htm
                            # classId 指定版の関数は削除されてしまったっぽい...
                            # https://help.autodesk.com/view/FBX/2017/ENU/?guid=__files_GUID_2A50CD0F_062D_4F80_88C7_BBA0483FBE0F_htm

            boneInfoList = []

            skinCount = mesh.GetDeformerCount(FbxDeformer.eSkin)
            if skinCount == 0:
                # boneがない場合は、mesh自身の情報を取る
                initMat = scene.GetAnimationEvaluator().GetNodeGlobalTransform(node, FbxTime(0), FbxNode.eSourcePivot, True, True)
                inverseInitMat = initMat.Inverse()
                # FBX SDKの行列は行オーダーなので、WebGLの列オーダーに合わせる
                inverseInitMatrix = [
                    inverseInitMat.Get(0, 0), inverseInitMat.Get(0, 1), inverseInitMat.Get(0, 2), inverseInitMat.Get(0, 3),
                    inverseInitMat.Get(1, 0), inverseInitMat.Get(1, 1), inverseInitMat.Get(1, 2), inverseInitMat.Get(1, 3),
                    inverseInitMat.Get(2, 0), inverseInitMat.Get(2, 1), inverseInitMat.Get(2, 2), inverseInitMat.Get(2, 3),
                    inverseInitMat.Get(3, 0), inverseInitMat.Get(3, 1), inverseInitMat.Get(3, 2), inverseInitMat.Get(3, 3),
                ]

                boneInfo = {}
                boneInfo["inverseInitMatrix"] = inverseInitMatrix
                boneInfo["linkNodeName"] = node.GetName()

                boneInfoList.append(boneInfo)
            else:
                skin = mesh.GetDeformer(0, FbxDeformer.eSkin)
                boneNum = skin.GetClusterCount()

                tempBoneWeightMatrix = {}
                for boneIndex in range(boneNum):
                    cluster = skin.GetCluster(boneIndex)

                    initMat = FbxAMatrix()
                    cluster.GetTransformLinkMatrix(initMat)
                    inverseInitMat = initMat.Inverse()
                    # FBX SDKの行列は行オーダーなので、WebGLの列オーダーに合わせる
                    inverseInitMatrix = [
                        inverseInitMat.Get(0, 0), inverseInitMat.Get(0, 1), inverseInitMat.Get(0, 2), inverseInitMat.Get(0, 3),
                        inverseInitMat.Get(1, 0), inverseInitMat.Get(1, 1), inverseInitMat.Get(1, 2), inverseInitMat.Get(1, 3),
                        inverseInitMat.Get(2, 0), inverseInitMat.Get(2, 1), inverseInitMat.Get(2, 2), inverseInitMat.Get(2, 3),
                        inverseInitMat.Get(3, 0), inverseInitMat.Get(3, 1), inverseInitMat.Get(3, 2), inverseInitMat.Get(3, 3),
                    ]

                    boneInfo = {}
                    boneInfo["inverseInitMatrix"] = inverseInitMatrix
                    boneInfo["linkNodeName"] = cluster.GetLink().GetName()

                    boneInfoList.append(boneInfo)

                    pointNum = cluster.GetControlPointIndicesCount()
                    pointAry = cluster.GetControlPointIndices()
                    weightAry = cluster.GetControlPointWeights()

                    for pointIndex in range(pointNum):
                        index = pointAry[pointIndex]
                        weight = weightAry[pointIndex]

                        if not index in tempBoneWeightMatrix:
                            tempBoneWeightMatrix[index] = []

                        tempBoneWeightMatrix[index].append({"boneIndex": boneIndex, "weight": weight})


                # TODO weightの要素数を4以下にするために、フィルタリングをする(weight数に応じたシェーダが用意されているのが本来正しい？)
                maxBoneNum = 4
                for key in tempBoneWeightMatrix:
                    while(len(tempBoneWeightMatrix[key]) > maxBoneNum):
                        minValue = min(tempBoneWeightMatrix[key], key=lambda n: n["weight"])
                        tempBoneWeightMatrix[key] = filter(lambda n: n["weight"] > minValue["weight"], tempBoneWeightMatrix[key])

            meshJson["boneInfoList"] = boneInfoList

            layer0 = mesh.GetLayer(0)

            uv = layer0.GetUVs()
            src = mesh.GetControlPoints()
            polygonNum = mesh.GetPolygonCount()

            vertexTbl = []
            textureTbl = []

            boneIndexList = []
            weightList = []

            # ポリゴンの頂点をそのまま利用(uv座標の都合で、IBO使わず)
            count = 0
            for polygonIndex in range(polygonNum):
                polygonVertexNum = mesh.GetPolygonSize(polygonIndex)
                for polygonVertexIndex in range(polygonVertexNum):
                    vertexIndex = mesh.GetPolygonVertex( polygonIndex, polygonVertexIndex)

                    vertexTbl.append(src[vertexIndex][0])
                    vertexTbl.append(src[vertexIndex][1])
                    vertexTbl.append(src[vertexIndex][2])

                    directIndex = uv.GetIndexArray().GetAt(count)
                    uvCoods = uv.GetDirectArray().GetAt(directIndex)
                    textureTbl.append(uvCoods[0])
                    # WebGlの座標系は「左下が原点」なので...
                    textureTbl.append(1.0 - uvCoods[1])

                    if skinCount > 0:
                        boneWeightList = tempBoneWeightMatrix[vertexIndex]
                        boneWeightList.sort(key=lambda n: n["boneIndex"])

                        maxBoneNum = 4
                        for boneWeightListIndex in range(maxBoneNum):
                            if boneWeightListIndex < len(boneWeightList):
                                boneWeightInfo = boneWeightList[boneWeightListIndex]
                                boneIndex = boneWeightInfo["boneIndex"]
                                weight = boneWeightInfo["weight"]

                                boneIndexList.append(boneIndex)
                                weightList.append(weight)
                            else:
                                # 使わない場合は、weightを0で初期化するので、boneIndexが0でも構わない
                                boneIndexList.append(0)
                                weightList.append(0)
                    else:
                        # boneがない場合は、0番目の w:1.0としてデータを構築する
                        # TODO ボーンのいらないメッシュは区別してシェーダ書いたりした方がいいかもしれない...

                        maxBoneNum = 4
                        for boneWeightListIndex in range(maxBoneNum):
                            if boneWeightListIndex == 0:
                                boneIndexList.append(0)
                                weightList.append(1.0)
                            else:
                                boneIndexList.append(0)
                                weightList.append(0)

                    count = count + 1

            meshJson["vertexTbl"] = vertexTbl
            meshJson["textureTbl"] = textureTbl
            meshJson["boneIndexList"] = boneIndexList
            meshJson["weightList"] = weightList

            fbxJson["meshInfo"][node.GetName()] = meshJson

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

# float = Float32Array = 4 byte
def writeBin(writeList):
    length = len(writeList)
    byteLength = length * 4
    import struct
    fout.write(struct.pack(str(length) + "f", *writeList))

    return byteLength

keyList = [
    "vertexTbl",
    "textureTbl",
    "boneIndexList",
    "weightList",
]

fbxMetaJson = {}
fbxMetaJson["materialTextureFileNameMap"] = fbxJson["materialTextureFileNameMap"]
fbxMetaJson["animationFileList"] = fbxJson["animationFileList"]
fbxMetaJson["meshInfo"] = {}

with open(outputFolderName + outputJsonFileName + '.bin', mode='wb') as fout:
    byteOffset = 0
    for meshName in fbxJson["meshInfo"]:
        metaJson = {}
        fbxMetaJson["meshInfo"][meshName] = metaJson

        meshJson = fbxJson["meshInfo"][meshName]

        metaJson["materialName"] = meshJson["materialName"]

        for key in keyList:
            byteLength = writeBin(meshJson[key])
            metaJson[key] = {"byteOffset": byteOffset, "byteLength": byteLength}
            byteOffset += byteLength

        boneInfoList = meshJson["boneInfoList"]
        linkNodeNameList = []

        inverseInitMatrixList = []
        for boneIndex in range(len(boneInfoList)):
            boneInfo = boneInfoList[boneIndex]

            inverseInitMatrix = boneInfo["inverseInitMatrix"]
            linkNodeName = boneInfo["linkNodeName"]

            inverseInitMatrixList.extend(inverseInitMatrix)
            linkNodeNameList.append(linkNodeName)

        key = "boneInfoList"

        byteLength = writeBin(inverseInitMatrixList)
        metaJson[key] = {"byteOffset": byteOffset, "byteLength": byteLength, "linkNodeNameList": linkNodeNameList}
        byteOffset += byteLength

import json
of = open(outputFolderName + outputJsonFileName + ".json", "w") #書き込むファイルを開く
json.dump(fbxMetaJson, of) #変数 2 は辞書型
