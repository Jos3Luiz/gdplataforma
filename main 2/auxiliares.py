import os
import pygame


def subTuple(t1,t2):
    return (t1[0]-t2[0],t1[1]-t2[1])


def OpenSprites(path,width,height):
    files = os.listdir(path)
    files.sort()
    if len(files)>100:
        raise Exception("this paste have more than 100 files on folder %s. Check for errors"%path)

    for i in range (len(files)):
        img=pygame.image.load(path+"/"+files[i])
        scaled=pygame.transform.scale(img,(width,height))
        files[i]=scaled
    return files


def insertDict(dicti,element):
    gid = element.id
    if gid in dicti:
        raise Exception("Elemento %i ja existe no dicionario"%gid)
    else:
        dicti[gid]=element
