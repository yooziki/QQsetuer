import datetime
import os

class logs:

    def __init__(self):
        self.exsistsFiles = [""]
        self.dir = "Pixiv" + "/logs"
        if not os.path.exists(self.dir):
            os.makedirs(self.dir)
    def readLogs(self):
        """
        清理过期log，以及把已有的文件信息读入,需要进行初始化操作

        :return: self
        """
        weekago = datetime.datetime.today() - datetime.timedelta(days=7)
        weekago = weekago.strftime("%Y-%m-%d")
        if os.path.exists(self.dir + "/{}.txt".format(weekago)):
            os.remove(self.dir + "/{}.txt".format(weekago))
        for i in range(1, 7):
            daysago = datetime.datetime.today() - datetime.timedelta(days=i)
            daysago = daysago.strftime("%Y-%m-%d")
            if os.path.exists(self.dir + "/{}.txt".format(daysago)):
                f = open("{}/{}.txt".format(self.dir, daysago), "r")
                for line in f.readlines():
                    line = line.rstrip("\n")
                    self.exsistsFiles.append(line)
                f.close()

    def setLogs(self,logls):
        """
        将本次需要下载的内容记录到log文件中

        :param logls: 列表，本次下载的内容特征码
        :return: 是否成功
        """
        today = datetime.datetime.today().strftime("%Y-%m-%d")
        for i in range(len(logls)):
            logls[i] = logls[i] + "\n"
        if not os.path.exists(self.dir + "/{}.txt".format(today)):
            f = open(self.dir + "/{}.txt".format(today),"x")
        else:
            f = open(self.dir + "/{}.txt".format(today), "a")
        f.writelines(logls)
        f.close()

    def searchLogs(self,x):
        flag = (x in self.exsistsFiles)
        return flag

logger = logs()
logger.readLogs()
print(not logger.searchLogs("1"))