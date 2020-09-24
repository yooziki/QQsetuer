#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import cv2
from pixivpy3 import *
import time
import re
from pivixDownloaderLogs import logs

import accounts # is a dict

_USERNAME = accounts._ACCOUNT["PIVusrname"]
_PASSWORD = accounts._ACCOUNT["PIVpasswd"]

_COUNT = 20
# 作品排行
# mode: [day, week, month, day_male, day_female, week_original, week_rookie, day_manga]
# date: '2016-08-01'
# mode (Past): [day, week, month, day_male, day_female, week_original, week_rookie,
#               day_r18, day_male_r18, day_female_r18, week_r18, week_r18g]
_MODE = ["day", "day_r18"]
_DATE = None
_ROOTDIC = "Pixiv"
_EXSISTSFILES = []
_REQUESTS_KWARGS = {
    'proxies': {
        'https': 'https://127.0.0.1:2089',
    },
    'verify': False,  # PAPI use https, an easy way is disable requests SSL verify
}


def main():
    # Init api
    sni = False
    if not sni:
        api = AppPixivAPI(**_REQUESTS_KWARGS)
        # api.set_api_proxy("https://127.0.0.1:2089")
    else:
        api = ByPassSniApi()  # Same as AppPixivAPI, but bypass the GFW
        api.require_appapi_hosts()
    api.login(_USERNAME, _PASSWORD)
    # Init logs
    logger = logs()
    logger.readLogs()
    # check DICT
    directory = _ROOTDIC
    # 精确到日期
    if _DATE is not None:
        directory = directory + "/" + _DATE
    else:
        directory = directory + "/" + todayDate()
    # 不同mode做循环
    for mode in _MODE:
        dir = directory + "/" + mode
        if not os.path.exists(dir):
            os.makedirs(dir)

        # get rankings
        # {'id': 84287640, 'title': '無題', 'type': 'illust', 'image_urls': {'square_medium': 'https://i.pximg.net/c/540x540_10_webp/img-master/img/2020/09/11/00/00/08/84287640_p0_square1200.jpg', 'medium': 'https://i.pximg.net/c/540x540_70/img-master/img/2020/09/11/00/00/08/84287640_p0_master1200.jpg', 'large': 'https://i.pximg.net/c/600x1200_90_webp/img-master/img/2020/09/11/00/00/08/84287640_p0_master1200.jpg'}, 'caption': '', 'restrict': 0, 'user': {'id': 1655331, 'name': 'Aちき@C97新刊委託中', 'account': 'atiki0322', 'profile_image_urls': {'medium': 'https://i.pximg.net/user-profile/img/2018/02/19/00/03/48/13846065_166e5f16e50a5dc2d259aa1b8ea371cf_170.png'}, 'is_followed': False}, 'tags': [{'name': 'オリジナル', 'translated_name': None}, {'name': 'オリジナル5000users入り', 'translated_name': None}, {'name': 'オリジナル10000users入り', 'translated_name': None}], 'tools': [], 'create_date': '2020-09-11T00:00:08+09:00', 'page_count': 1, 'width': 1000, 'height': 707, 'sanity_level': 2, 'x_restrict': 0, 'series': None, 'meta_single_page': {'original_image_url': 'https://i.pximg.net/img-original/img/2020/09/11/00/00/08/84287640_p0.png'}, 'meta_pages': [], 'total_view': 46167, 'total_bookmarks': 12726, 'is_bookmarked': False, 'visible': True, 'is_muted': False}
        json_result = api.illust_ranking(mode, _DATE)
        time.sleep(0.5)
        json_result2 = api.illust_ranking(mode, _DATE, offset=30)
        time.sleep(0.5)
        json_result3 = api.illust_ranking(mode, _DATE, offset=60)
        json_resultall = list(json_result.illusts + json_result2.illusts + json_result3.illusts)
        # 获取不重复的20个
        i = 0  # 有效寻找
        result = []
        logls = []
        for ls in json_resultall:
            try:
                x = "{}".format(ls.id)  # 对比库
                if not logger.searchLogs(x):
                    # print(x)
                    logls.append(x)
                    result.append(ls)
                    i += 1
                if i > _COUNT:
                    # print("找到前20")
                    break
            except:
                print("wrong")
                break
        logger.setLogs(logls)  # 写log

        # download top $_COUNT$ day rankings to 'illusts' dir
        for lis in result:
            idx = 10
            illust = lis
            time.sleep(0.5)
            image_url = illust.meta_single_page.get('original_image_url', illust.image_urls.large)
            print("%s: %s" % (illust.title, image_url))
            aname = "{}_id{}".format(illust.title, illust.id)
            aname = patterncheck(aname)

            for count in range(3):
                try:
                    if idx == 0:
                        zname = aname + ".jpg"
                        api.download(image_url, path=dir, name=zname)
                    elif idx == 1:
                        url_basename = os.path.basename(image_url)
                        extension = os.path.splitext(url_basename)[1]
                        name = "%s_illust_id_%d%s" % (illust.title, illust.id, extension)
                        api.download(image_url, path=dir, name=name)
                    elif idx == 2:
                        api.download(image_url, path=dir, fname='illust_%s.jpg' % aname)
                    else:
                        # path will not work due to fname is a handler
                        api.download(image_url, path='/foo/bar', fname=open('%s/illust_%s.jpg' % (dir, aname), 'wb'))
                    break
                except:
                    print("somethingsWrong")

        # 图像矩阵
        PicTransfer(dir)
        # 生成缩略图
        PicMerge(dir, mode)


# 今日日期转换
def todayDate(patter: str = "%Y-%m-%d"):
    import datetime
    date = datetime.datetime.today().strftime(patter)
    return date


def patterncheck(fileName: str = None):
    '''
    去除非法字

    :param fileName: 录入字符串

    :return: 合法字符串
    '''
    pattern = r'[\\/:*?"<>|。]'  # 规则
    s = re.subn(pattern, '-', fileName)
    return s[0]


def PicTransfer(dir):
    """
    图像合法性转换

    :param dir: 文件路径
    :return: 无
    """
    PicList = os.listdir(dir)
    for ls in PicList:
        pic = os.path.join(dir, ls)
        try:
            os.rename(pic, os.path.join(dir, "aaaYOOZIKI.jpg"))
            img = cv2.imread(os.path.abspath(os.path.join(dir, "aaaYOOZIKI.jpg")), cv2.IMREAD_UNCHANGED)
            cv2.imwrite(os.path.join(dir, "aaaYOOZIKI.jpg"), img)
            os.rename(os.path.join(dir, "aaaYOOZIKI.jpg"), pic)
        except:
            print("非法格式转换")


def PicMerge(dir, mode):
    PicList = os.listdir(dir)
    mat = None
    WID = 500
    ii = 0
    for ls in PicList:
        ii = ii + 1
        pic = os.path.join(dir, ls)
        try:
            os.rename(pic, os.path.join(dir, "aaaYOOZIKI.jpg"))
            img = cv2.imread(os.path.abspath(os.path.join(dir, "aaaYOOZIKI.jpg")), cv2.IMREAD_UNCHANGED)
            os.rename(os.path.join(dir, "aaaYOOZIKI.jpg"), pic)
            scale = WID / img.shape[1]
            h = int(img.shape[0] * scale)
            img = cv2.resize(img, (WID, h))
            img = cv2.putText(img, "{}".format(ii), (50,50), cv2.LINE_4, 2, (0, 0, 0), 8)
            img = cv2.putText(img, "{}".format(ii), (50, 50), cv2.LINE_4, 2, (225, 225, 225), 2)
            if mat is None:
                mat = img
            else:
                mat = cv2.vconcat([mat, img])
        except:
            print("无法拼接{}".format(ls))
    cv2.imwrite(os.path.join("Pixiv/{}".format(todayDate()), "{}_scan.jpg".format(mode)), mat)  # 生成缩略图


if __name__ == '__main__':
    main()
