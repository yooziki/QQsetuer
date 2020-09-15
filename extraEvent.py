from graia.application.entry import (
    GraiaMiraiApplication, Session,
    MessageChain, Group, Friend, Member, MemberInfo,
    Plain, Image, AtAll, At, Face
)
import pivixDownloader
import time
import asyncio
import os
import requests
import PIL
from PIL import Image as PILImage
from io import BytesIO

import Universe

setuList = []
haotuList = []


def getschedulepermission():
    """读取许可文件.

            Returns:
                List: 所有可以发消息的群组.
            """
    txt = open("schedules.txt", "r").read()
    sch = list(map(eval, txt.split("\n")))
    return sch


def Down(id: int = 0):
    """
    每日下载

    :param id: 最大递归次数

    :return: 下载成功与否
    """
    try:
        pivixDownloader.main()
        t = time.gmtime()
        h = time.strftime("%H", t)
        if h[0] == 0:
            h = eval(h[1]) + 8
            if h < 10:
                h = "0" + str(h)
            else:
                h = str(h)
        getPicList()
        Universe.set_value("dailyMession",[1])
    except:
        if id < 10:
            time.sleep(30 + id * 10)
            id += 1
            Down(id)
        else:
            Universe.set_value("dailyMession",[-1])

def deb():
    """
    debug

    :return: debug
    """
    print("do")
    time.sleep(5)
    print("do2")
    return "do"


def DayilyMission(group,id:int=0):
    lock = Universe.get_value("lock")
    if not lock.locked():
        lock.acquire()
        Universe.set_value("lock", lock)
        Universe.set_value("dailyMession", [0,group])
        Down()
        print("每日色图更新完成")
        lock.release()
        Universe.set_value("lock", lock)
    else:
        print("pass")



def initNow(app: GraiaMiraiApplication, message: MessageChain, friend, loop):
    global setuList, haotuList
    getPicList()
    if type(friend) is Friend:
        asyncio.run_coroutine_threadsafe(app.sendFriendMessage(friend, message.create(
            [Plain("今日色图：{}份\n今日好图：{}份".format(len(setuList), len(haotuList)))])), loop)
    elif type(friend) is Group:
        asyncio.run_coroutine_threadsafe(app.sendGroupMessage(friend, message.create(
            [Plain("今日色图：{}份\n今日好图：{}份".format(len(setuList), len(haotuList)))])), loop)

def fixPics(app:GraiaMiraiApplication,message:MessageChain, friend,loop):
    """
    修复图片感叹号

    :param app:
    :param message:
    :param friend: 这里表示friend或者group
    :param loop:
    :return:
    """
    dirs = pivixDownloader._ROOTDIC + "/" + getDate()
    for ls in pivixDownloader._MODE:
        dir = dirs + "/" + ls
        pivixDownloader.PicTransfer(dir)
    if type(friend) is Friend:
        asyncio.run_coroutine_threadsafe(app.sendFriendMessage(friend, message.create(
            [Plain("修好啦！没修好的就没救了".format(len(setuList), len(haotuList)))])), loop)
    elif type(friend) is Group:
        asyncio.run_coroutine_threadsafe(app.sendGroupMessage(friend, message.create(
            [Plain("修好啦！没修好的就没救了".format(len(setuList), len(haotuList)))])), loop)

def getPicList():
    """
    获得今日色图的Image列表

    :return: none
    """
    global setuList, haotuList
    date = pivixDownloader.todayDate()
    rootdir = pivixDownloader._ROOTDIC
    mode = pivixDownloader._MODE
    setuList = os.listdir("{}/{}/{}".format(rootdir, date, mode[1]))
    abspath_setu = os.path.abspath("{}/{}/{}".format(rootdir, date, mode[1]))
    for i in range(len(setuList)):
        setuList[i] = os.path.join(abspath_setu, setuList[i])

    haotuList = os.listdir("{}/{}/{}".format(rootdir, date, mode[0]))
    abspath_haotu = os.path.abspath("{}/{}/{}".format(rootdir, date, mode[0]))
    for i in range(len(haotuList)):
        haotuList[i] = os.path.join(abspath_haotu, haotuList[i])
    Universe.set_value("setuScan","{}/{}/{}_scan.jpg".format(rootdir,date,mode[1]))
    Universe.set_value("haotuScan", "{}/{}/{}_scan.jpg".format(rootdir, date, mode[0]))

def getDate(pattern:str="%Y-%m-%d"):
    import time
    t = time.gmtime()
    date = time.strftime(pattern, t)
    return date

def savePic(savePicLs,oth:int=0):
    lock = Universe.get_value("SavePicLock")
    lock.acquire()
    Universe.set_value("SavePicLock", lock)
    for ls in savePicLs:
        print(ls)
        print(ls.http_to_bytes(ls.url))
        direct = "{}/{}/collection".format(pivixDownloader._ROOTDIC, getDate())
        if not os.path.exists(direct):
            os.makedirs(direct)
        try:
            response = requests.get(ls.url)
            img = PILImage.open(BytesIO(response.content))
            img.save(os.path.join(direct, "{}.{}".format(ls.imageId[1:-7], img.format.lower())))
            print("saved")
        except:
            print("failed")
    #lock.release()
    Universe.set_value("SavePicLock", lock)