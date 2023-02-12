########## 说明 ##########  
这是一个图集整理脚本  
可以删除重复的图片并且重命名文件  

示例:  
python organizer.py --dataset D:/dataset  
  
文件结构应该如下面所示二级目录  
|--dataset  
|--|--xx.jpg  
|--|--xx.jpg  
|--|--videoDir  
|--|--|--video1.mp4  
...  
或三级目录  
|--dataset  
|--|--fileDir1    
|--|--|--xx.jpg  
|--|--|--xx.jpg  
|--|--fileDir2  
|--|--|--xx.jpg  
|--|--|--xx.jpg  
|--|--|--|videoDir  
|--|--|--|--|video1.mp4  
...  
输出的文件会变成  
|--dataset [nP_nV_nMB]  
|--|--xxx-1.jpg(xxx为随机的三个字母)  
|--|--xxx-2.jpg  
|--|--|videos  
|--|--|--1.mp4  
...
