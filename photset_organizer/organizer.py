# /usr/bin/env python
# -*- coding: UTF-8 -*-
# create on: 2022-12-25
# author: harold-chen

# usage: python organizer.py --dataset D:/dataset

import numpy as np
import argparse
import filetype
import string
import random
import shutil
import glob
import cv2
import os

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=False)
args = vars(ap.parse_args())

class PhotoSetOrganizer:
    def __init__(self):
        self.imageTypes = (".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff")
        self.videoTypes = (".mp4", ".mov")

    def list_files(self, basePath, validExts=None, contains=None):
        for (rootDir, dirNames, fileNames) in os.walk(basePath):
            for fileName in fileNames:
                if contains is not None and fileName.find(contains) == -1:
                    continue

                ext = fileName[fileName.rfind("."):].lower()

                if validExts is None or ext.endswith(validExts):
                    imagePath = os.path.join(rootDir, fileName)

                    yield imagePath

    def list_images(self, basePath, contains=None):
        return self.list_files(basePath, validExts=self.imageTypes, contains=contains)

    def list_videos(self, basePath, contains=None):
        return self.list_files(basePath, validExts=self.videoTypes, contains=contains)    
        
    def dhash(self, image_path, hashSize=8):
        gray = cv2.cvtColor(image_path, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (hashSize + 1, hashSize))

        diff = resized[:, 1:] > resized[:, :-1]

        return sum([2 ** i for (i, v) in enumerate(diff.flatten()) if v])

    def restore_file_type(self, image_path):
        # 将二级目录里的文件取出来, 变为一级目录
        filePaths = self.list_files(image_path)

        for (i, filePath) in enumerate(filePaths):
            if os.path.dirname(filePath) != image_path:
                shutil.copy(filePath, image_path + "\\temp" + str(i) + os.path.basename(filePath))
    
        for (rootDir, dirNames, fileNames) in os.walk(image_path):
            for dirName in dirNames:
                shutil.rmtree(os.path.join(rootDir, dirName))

        # 如果文件没有后缀, 添加文件后缀
        filePaths = self.list_files(image_path)
        
        for filePath in filePaths:
            if len(os.path.basename(filePath).split(".")) == 1:
                fileType = filetype.guess(filePath).extension
                os.rename(filePath, filePath + "." + fileType)
            
            if "jpeg" in filePath:
                fileType = filetype.guess(filePath).extension
                os.rename(filePath, filePath + "." + fileType)   

    def detect_and_remove_duplicate(self, image_path, visiable=0):
        imagePaths = sorted(list(self.list_images(image_path)))
        hashes = {}

        for imagePath in imagePaths:
            image = cv2.imdecode(np.fromfile(imagePath, dtype=np.int8), cv2.IMREAD_COLOR)

            try:
                h = self.dhash(image)

            except Exception as e:
                print(imagePath, e)
            
            p = hashes.get(h, [])
            p.append(imagePath)
            hashes[h] = p

        for (h, hashedPaths) in hashes.items():
            if len(hashedPaths) > 1:
                if visiable == 1:
                    montage = None

                    for p in hashedPaths:
                        image = cv2.imdecode(np.fromfile(p, dtype=np.uint8), cv2.IMREAD_COLOR)
                        image = cv2.resize(image, (300, 300))

                        if montage is None:
                            montage = image
                        
                        else:
                            montage = np.hstack([montage, image])

                    cv2.imshow("Montage", montage)
                    key = cv2.waitKey(0)

                    if key == ord("d"):
                        imagePaths = sorted(hashedPaths, key=lambda x:os.path.getsize(x), reverse=True)

                        for p in imagePaths[1:]:
                            os.remove(p)
                
                else:
                    imagePaths = sorted(hashedPaths, key=lambda x:os.path.getsize(x), reverse=True)

                    for p in imagePaths[1:]:
                        os.remove(p)

    def rename(self, image_path):
        imagePaths = self.list_images(image_path)
        randomKey = ''.join(random.sample(string.ascii_lowercase, 3))

        for (i, imagePath) in enumerate(imagePaths):
            imageType = imagePath.split(".")[-1]
            os.rename(imagePath, os.path.dirname(imagePath) + "\\{}-{}.{}".format(randomKey, i+1, imageType))

        videoPaths = list(self.list_videos(image_path))

        if len(videoPaths) > 0:
            if not os.path.exists(image_path + "\\videos"):
                os.makedirs(image_path + "\\videos")

            for (i, videoPath) in enumerate(videoPaths):
                videoType = videoPath.split(".")[-1]
                shutil.move(videoPath, image_path + "\\videos" + "\\{}.{}".format(i+1, videoType))                

    def add_label(self, image_path):
        fileSize = 0

        for (rootDir, dirNames, fileNames) in os.walk(image_path):
            fileSize += sum([os.path.getsize(os.path.join(rootDir, fileName)) for fileName in fileNames]) / 1024 / 1024

        numberOfImage = len(list(self.list_images(image_path)))
        numberOfVideo = len(list(self.list_videos(image_path)))
        label = "[{}P_{}V_{}MB]".format(numberOfImage, numberOfVideo, int(fileSize))
        
        os.rename(image_path, image_path + " " + label)

    def run(self, image_path):
        self.restore_file_type(image_path)
        self.detect_and_remove_duplicate(image_path)
        self.rename(image_path)
        self.add_label(image_path)

organizer = PhotoSetOrganizer()
multipleDir = True
path = args["dataset"]

for file in glob.glob(os.path.join(path, "*")):
    if os.path.isfile(file):
        multipleDir = False

if multipleDir == False:
    organizer.run(path)

else:
    for file in glob.glob(os.path.join(path, "*")):
        print("processing...{}".format(file))
        organizer.run(file)
