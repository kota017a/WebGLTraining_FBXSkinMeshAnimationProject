var gl;

var BONE_MATRIX_NUM = 128

var unityMeshAnimationFileList;
var unityMeshMaterialTextureJsonMap;

var unityMesh = {};
var unityMeshBin;
var unityMeshAnimationMap = {};
var unityMeshAnimationBinMap = {};

var unityMeshMaterilImgMap = {};
var unityMeshMaterilJsonMap = {};
var unityMeshMaterilDatMap = {};
var unityMeshMaterilTextureBufferMap = {};

var initMeshJsonFetch = function(fileName){
    var url = location.origin + "/output/" + fileName + ".json"
    fetch(url)
        .then(function (response)
        {
            return response.json();
        })
        .then(function (myJson)
        {
            unityMesh = myJson["meshInfo"];
            unityMeshAnimationFileList = myJson["animationFileList"];
            unityMeshMaterialTextureJsonMap = myJson["materialTextureFileNameMap"];
            fetchMeshBin(fileName);
        });
};

var fetchMeshBin = function(fileName){
    var url = location.origin + "/output/" + fileName + ".bin"
    fetch(url)
        .then(function (response)
        {
            return response.arrayBuffer();
        })
        .then(function (myArrayBuffer)
        {
            unityMeshBin = myArrayBuffer;
            initAnimationLoad();
        });

}

var initAnimationLoad = function(){
    for (let index = 0; index < unityMeshAnimationFileList.length; index++) {
        const fileName = unityMeshAnimationFileList[index];
        fetchAnimation(fileName);
    }
};

var fetchAnimation = function(fileName){
    var url = location.origin + "/output/animation/" + fileName + ".json"
    fetch(url)
        .then(function (response)
        {
            return response.json();
        })
        .then(function (myJson)
        {
            unityMeshAnimationMap[fileName] = myJson;
            fetchAnimationBin(fileName);
        });
}

var fetchAnimationBin = function(fileName){
    var url = location.origin + "/output/animation/" + fileName + ".bin"
    fetch(url)
        .then(function (response)
        {
            return response.arrayBuffer();
        })
        .then(function (myArrayBuffer)
        {
            unityMeshAnimationBinMap[fileName] = myArrayBuffer;
            if (Object.keys(unityMeshAnimationBinMap).length == unityMeshAnimationFileList.length)
            {
                initImgJsonLoad();
            }
        });
}

var initImgJsonLoad = function(){
    for (const key in unityMeshMaterialTextureJsonMap) {
        if (unityMeshMaterialTextureJsonMap.hasOwnProperty(key)) {
            fetchImgJson(key);
        }
    }
};

var fetchImgJson = function(key){
    const jsonFileName = unityMeshMaterialTextureJsonMap[key];

    var url = location.origin + "/output/texture/" + jsonFileName + ".json"
    fetch(url)
        .then(function (response)
        {
            return response.json();
        })
        .then(function (myJson)
        {
            unityMeshMaterilJsonMap[key] = myJson;
            fetchImgBin(key);
        });
};

var fetchImgBin = function(key){
    const datFileName = unityMeshMaterialTextureJsonMap[key];

    var url = location.origin + "/output/texture/" + datFileName + ".bin"
    fetch(url)
        .then(function (response)
        {
            return response.arrayBuffer();
        })
        .then(function (myArrayBuffer)
        {
            unityMeshMaterilDatMap[key] = myArrayBuffer;
            imgBinOnload(key);
        });
};

var imgBinOnload = function(key){
    var tex = gl.createTexture();

    gl.bindTexture(gl.TEXTURE_2D, tex);
    
    gl.texImage2D(gl.TEXTURE_2D, 0, gl[unityMeshMaterilJsonMap[key]["mode"]], unityMeshMaterilJsonMap[key]["size"][0], unityMeshMaterilJsonMap[key]["size"][1], 0, gl[unityMeshMaterilJsonMap[key]["mode"]], gl.UNSIGNED_BYTE, new Uint8Array(unityMeshMaterilDatMap[key]));

    gl.generateMipmap(gl.TEXTURE_2D);

    gl.bindTexture(gl.TEXTURE_2D, null);

    unityMeshMaterilTextureBufferMap[key] = tex;

    if (Object.keys(unityMeshMaterilTextureBufferMap).length == Object.keys(unityMeshMaterialTextureJsonMap).length)
    {
        onloadFunc();
    }
};

var cWidth = 350;
var cHeight = 400;

onload = function ()
{
    var c = document.getElementById('canvas');
    c.width = cWidth;
    c.height = cHeight;

    gl = c.getContext('webgl');

    initMeshJsonFetch("unitychan")
}

onloadFunc = function(){
    var vShader = createShader('vs');
    var fShader = createShader('fs');

    var prg = createProgram(vShader, fShader);

    var attLocation = new Array();
    attLocation[0] = gl.getAttribLocation(prg, 'position');
    attLocation[1] = gl.getAttribLocation(prg, 'textureCoord');
    attLocation[2] = gl.getAttribLocation(prg, 'weight');
    attLocation[3] = gl.getAttribLocation(prg, 'boneIndex');

    var attStride = new Array();
    attStride[0] = 3;
    attStride[1] = 2;
    attStride[2] = 4;
    attStride[3] = 4;

    var uniLocation = new Array();
    uniLocation[0] = gl.getUniformLocation(prg, 'mvpMatrix');
    uniLocation[1] = gl.getUniformLocation(prg, 'texture');
    uniLocation[2] = gl.getUniformLocation(prg, 'boneMatrix');

    var m = new matIV();
    var mMatrix = m.identity(m.create());
    var vMatrix = m.identity(m.create());
    var pMatrix = m.identity(m.create());
    var vpMatrix = m.identity(m.create());
    var mvpMatrix = m.identity(m.create());

    m.lookAt([0.0, 75.0, 200.0], [0, 75, 0], [0, 1, 0], vMatrix);
    // m.lookAt([0.0, 135.0, 50.0], [0, 135, 0], [0, 1, 0], vMatrix);
    m.perspective(45, cWidth / cHeight, 1, 300, pMatrix);
    m.multiply(pMatrix, vMatrix, vpMatrix);

    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);
    gl.enable(gl.CULL_FACE);

    gl.activeTexture(gl.TEXTURE0);

    gl.enable(gl.BLEND);
    gl.blendFuncSeparate(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA, gl.ONE, gl.ONE);

    var count = 0;

    var unityMeshBuffer = {};
    for (const key in unityMesh)
    {
        if (unityMesh.hasOwnProperty(key))
        {
            const mesh = unityMesh[key];
            const bin = unityMeshBin;
            var positionVbo = createVbo(bin, mesh.vertexTbl["byteOffset"], mesh.vertexTbl["byteLength"]);
            var textureVbo = createVbo(bin, mesh.textureTbl["byteOffset"], mesh.textureTbl["byteLength"]);
            var weightListVbo = createVbo(bin, mesh.weightList["byteOffset"], mesh.weightList["byteLength"]);
            var boneIndexVbo = createVbo(bin, mesh.boneIndexList["byteOffset"], mesh.boneIndexList["byteLength"]);
            unityMeshBuffer[key] = {
                vbo: [positionVbo, textureVbo, weightListVbo, boneIndexVbo],
            };

        }
    }

    var unityMeshBoneInverseInitMatrixList = {};
    for (const key in unityMesh)
    {
        if (unityMesh.hasOwnProperty(key))
        {
            const mesh = unityMesh[key];
            const bin = unityMeshBin;

            var inverseInitMatrixList = [];
            unityMeshBoneInverseInitMatrixList[key] = inverseInitMatrixList;

            var length = mesh.boneInfoList["byteLength"] / mesh.boneInfoList["linkNodeNameList"].length;
            for (let boneIndex = 0; boneIndex < mesh.boneInfoList["linkNodeNameList"].length; boneIndex++)
            {
                var byteOffset = mesh.boneInfoList["byteOffset"] + length * boneIndex;
                var inverseInitMatrix = new Float32Array(bin, byteOffset, length / 4);

                inverseInitMatrixList.push(inverseInitMatrix);
            }
        }
    }

    var unityMeshAnimationFrameList = {}
    for (const animationName in unityMeshAnimationMap) {
        if (unityMeshAnimationMap.hasOwnProperty(animationName)) {
            const animationInfo = unityMeshAnimationMap[animationName];
            const animationBin = unityMeshAnimationBinMap[animationName];
            
            var frameInfos = {}
            unityMeshAnimationFrameList[animationName] = frameInfos;

            for (const meshName in animationInfo["frameInfos"]) {
                if (animationInfo["frameInfos"].hasOwnProperty(meshName)) {

                    frameInfos[meshName] = [];

                    const frameInfo = animationInfo["frameInfos"][meshName];
                    var length = frameInfo["byteLength"] / animationInfo["frameNum"];

                    for (let frame = 0; frame < animationInfo["frameNum"]; frame++) {
                        var byteOffset = frameInfo["byteOffset"] + frame * length;
                        frameInfos[meshName].push(new Float32Array(animationBin, byteOffset, length / 4));
                    }
                }
            }
        }
    }

    var boneMatrixListRaw = new ArrayBuffer( 4 * 16 * BONE_MATRIX_NUM);
    var boneMatrixList = new Float32Array(boneMatrixListRaw);

    var boneMatrixs = []
    var length = boneMatrixListRaw.byteLength / BONE_MATRIX_NUM;
    for (let index = 0; index < BONE_MATRIX_NUM; index++)
    {
        var byteOffset = length * index;
        boneMatrixs[index] = new Float32Array(boneMatrixListRaw, byteOffset, length / 4);
    }

    var animationList = Object.keys(unityMeshAnimationMap);
    var playAnimationIndex = 0;

    (function ()
    {
        gl.clearColor(0.0, 0.0, 0.0, 1.0);
        gl.clearDepth(1.0);
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT);

        count++;

        var rad = (count % 360) * Math.PI / 180;

        var animationKey = animationList[playAnimationIndex % (animationList.length-1)]

        var playAnimationInfo = unityMeshAnimationMap[animationKey];
        var playAnimationFrameInfo = unityMeshAnimationFrameList[animationKey];

        var frame = (count % (playAnimationInfo["frameNum"] - 1)) + 1
        if (frame == playAnimationInfo["frameNum"]-1){
            playAnimationIndex++;
        }

        m.identity(mMatrix);
        m.rotate(mMatrix, rad, [0, 1, 0], mMatrix);
        m.multiply(vpMatrix, mMatrix, mvpMatrix);
        gl.uniformMatrix4fv(uniLocation[0], false, mvpMatrix);

        // TODO cheekは最後に描画する必要がある？（z値が同一の関係...?）。普通どうするんだろうか？
        unityMeshKeys = []
        for (const key in unityMesh) {
            if (unityMesh.hasOwnProperty(key)) {
                if(key == "cheek"){
                    unityMeshKeys.push(key);
                }else{
                    unityMeshKeys.unshift(key);
                }
            }
        }
        unityMeshKeys.push("cheek");

        for (let unityMeshKeyIndex = 0; unityMeshKeyIndex < unityMeshKeys.length; unityMeshKeyIndex++) {
            const key = unityMeshKeys[unityMeshKeyIndex];            
            if (unityMesh.hasOwnProperty(key))
            {
                const buffer = unityMeshBuffer[key];
                const mesh = unityMesh[key];
                const boneInverseInitMatrixList = unityMeshBoneInverseInitMatrixList[key];
                const texture = unityMeshMaterilTextureBufferMap[mesh.materialName];

                for (let boneIndex = 0; boneIndex < boneInverseInitMatrixList.length; boneIndex++) {
                    var linkNodeName = mesh.boneInfoList["linkNodeNameList"][boneIndex];
                    var inverseInitMatrix = boneInverseInitMatrixList[boneIndex];

                    var frameInfo = playAnimationFrameInfo[linkNodeName][frame];

                    m.multiply(frameInfo, inverseInitMatrix, boneMatrixs[boneIndex]);
                }

                gl.uniformMatrix4fv(uniLocation[2], false, boneMatrixList);
                
                setAttribute(buffer.vbo, attLocation, attStride);

                gl.activeTexture(gl.TEXTURE0)
                gl.bindTexture(gl.TEXTURE_2D, texture);
                gl.uniform1i(uniLocation[1], 0);
                
                gl.drawArrays(gl.TRIANGLES, 0, mesh.vertexTbl["byteLength"] / (4 * 3));
            }
        }

        gl.flush();
        setTimeout(arguments.callee, 1000 / 30);
    })();
}

function createShader(id)
{
    var shader;

    var scriptElement = document.getElementById(id);

    if (!scriptElement) { return; }

    switch (scriptElement.type)
    {
        case 'x-shader/x-vertex':
            shader = gl.createShader(gl.VERTEX_SHADER);
            break;
        case 'x-shader/x-fragment':
            shader = gl.createShader(gl.FRAGMENT_SHADER);
            break;
        default:
            return;
    }

    gl.shaderSource(shader, scriptElement.text);

    gl.compileShader(shader);

    if (gl.getShaderParameter(shader, gl.COMPILE_STATUS))
    {
        return shader;
    } else
    {
        alert(gl.getShaderInfoLog(shader));
    }
}

function createProgram(vs, fs)
{
    var program = gl.createProgram();

    gl.attachShader(program, vs);
    gl.attachShader(program, fs);

    gl.linkProgram(program);

    if (gl.getProgramParameter(program, gl.LINK_STATUS))
    {
        gl.useProgram(program);
        return program;
    } else
    {
        alert(gl.getProgramInfoLog(program));
    }
}

function createVbo(data, byteOffset, byteLength)
{
    var vbo = gl.createBuffer();

    gl.bindBuffer(gl.ARRAY_BUFFER, vbo);

    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(data, byteOffset, byteLength / 4), gl.STATIC_DRAW);

    gl.bindBuffer(gl.ARRAY_BUFFER, null);

    return vbo;
}

function setAttribute(vbo, attL, attS)
{
    for (const i in vbo)
    {
        gl.bindBuffer(gl.ARRAY_BUFFER, vbo[i]);

        gl.enableVertexAttribArray(attL[i]);

        gl.vertexAttribPointer(attL[i], attS[i], gl.FLOAT, false, 0, 0);
    }
}
