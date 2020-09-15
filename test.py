'''
# -*- coding: utf-8 -*-
import asyncio
import os
import aiohttp
from pixivpy_async import AppPixivAPI
from pixivpy_async import PixivClient

def get_local_proxy():
    from urllib.request import getproxies
    proxy = getproxies()['http']
    return proxy

_USERNAME = "775086089@qq.com"
_PASSWORD = "Lqbz970715"

async def _main(papi):
    await papi.login(_USERNAME, _PASSWORD)
    #  papi.download("https://www.pixiv.net/artworks/84106669","./Pixiv")

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_main(AppPixivAPI(env=True)))
if __name__ == '__main__':
    main()


import os
from pixivpy3 import AppPixivAPI
_USERNAME = "775086089@qq.com"
_PASSWORD = "Lqbz970715"

def main():
    api = AppPixivAPI()
    api.login(_USERNAME,_PASSWORD)
    aa = api.illust_detail(84047784)
    print(aa.illust.meta_single_page.get('original_image_url', aa.illust.image_urls.large))
    print(type(aa.illust.meta_single_page.get('original_image_url', aa.illust.image_urls.large)))
    api.download(aa.illust.meta_single_page.get('original_image_url', aa.illust.image_urls.large),"./Pixiv",name="aa.jpg")


if __name__ == '__main__':
    main()
'''
# -*- coding: utf-8 -*-
import os


class logs:

    def __init__(self):
        self.exsistsFiles = []
        self.dir = "Pixiv" + "/logs"
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
    def getLogs(self):
        """
        清理过期log，以及把已有的文件信息读入,需要进行初始化操作

        :return: self
        """
        import datetime
        weekago = datetime.datetime.today() - datetime.timedelta(days=7)
        weekago = weekago.strftime("%Y-%m-%d")
        if os.path.exists(self.dir + "/{}.txt".format(weekago)):
            os.remove(self.dir + "/{}.txt".format(weekago))
        for i in range(1, 7):
            daysago = datetime.datetime.today() - datetime.timedelta(days=i)
            daysago = daysago.strftime("%Y-%m-%d")
            print(self.dir + "/{}.txt".format(daysago))
            if os.path.exists(self.dir + "/{}.txt".format(daysago)):
                print("yes")
                f = open("{}/{}.txt".format(self.dir, daysago), "r")
                for line in f.readlines():
                    line = line.rstrip("\n")
                    self.exsistsFiles.append(line)
                f.close()
    def setLogs(self,logls):
        import datetime
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        for i in range(len(logls[:-1])):
            logls[i] = logls[i] + "\n"
        f = open(self.dir + "/{}.txt".format(today),"x")
        f.writelines(logls)
        f.close()


logs.getLogs()
