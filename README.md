Name: 名前  
====
WebGL3DModelProject

Overview: 概要  

This project's purpose is personal training to analyze fbx file and animate with WebGL.  
unitychan.fbxを解析して、WebGLでアニメーションさせることを目的とした個人的な訓練用プロジェクト

## Description: 詳細

This project has two programs. one of them extract infomation needed to animate with WebGL. The other render with WebGl based on the extracted infomation.   
FBXSDKを用いて、WebGLでアニメーションするために必要な情報を抽出するプログラムと抽出した情報を基にWebGL上でレンダリングを行うプログラムが含まれています。  

I think this project is useful for who trying to do the same. Because this project are using FBX SDK 2017 for Python.
FBXSDKのバージョンは2017、かつ、Python版を使用しており、本プロジェクトと同様の事を今やってみたいと考えている方には参考になるかと思います。

I referred to the sites written below.  
主に参考にしているサイトは、以下のものです。

[「〇×(まるぺけ)つくろーどっとコム」さんの「FBX習得編」](http://marupeke296.com/FBX_main.html)
[WebGL 開発支援サイト webgl.org](https://wgld.org/)

## Requirement: 必要なソフトウェア

- npm
- Python 2.7
- Pillow
- [FBX SDK for Python](https://help.autodesk.com/view/FBX/2019/ENU/?guid=FBX_Developer_Help_scripting_with_python_fbx_html)

## Usage: 使用方法

There is no simplified execution method.  
簡素化された実行方法は用意していません  

You need to do the following steps for checking the operation of the program.  
動作を確認するためには以下の手順を踏んでください  

1. Execute  「getAnimationInfo.py」「getMeshInfo.py」「tgaPixelConverter.py」. These programs are under 「pythonProject」 folder.
1. Copy 「output」Folder created under 「pythonProject」 folder up one level.
1. Execute `npm install` under project root folder.  
1. Execute `npm start` under project root folder.  
1. Go to the URL displayed on terminal.  

<br/>

1. 「pythonProject」フォルダ以下にある「getAnimationInfo.py」「getMeshInfo.py」「tgaPixelConverter.py」を実行してください
1. 同一階層に出力された「output」フォルダを、一つ上の階層にコピーしてください
1. プロジェクト直下で`npm install`を実行してください  
1. プロジェクト直下で`npm start`を実行してください
1. ターミナルに表示されているURLアドレスにアクセスしてください

## Licence: ライセンス

[MIT](/LICENCE)  

This project include unitychan fbx files. So  I show license of UCL.  
unitychanのfbxファイルをプロジェクトに含めているので、UCLライセンスも表記しておきます  

© UTJ/UCL

## Author: 制作者

[kota017a](https://github.com/kota017a)

## Other: その他

I published articles about this project on Qiita.  
Qiitaでこのプロジェクトに関する記事を公開しています  

[FBX SDK(Python)でunityちゃんを解析し、WebGLでアニメーションする！](https://qiita.com/kota017a/items/dd0fab59c06ca72dd3f6)
