import threading


_universe_dict = {
    "lock": threading.Lock(),
    "SavePicLock": threading.Lock(),
    "setuInd": 0,
    "haotuInd": 0,
    "setuScan": "0",
    "haotuScan": "0",
    "dailyMession": [0, None],  # 锁，传入类型
    "Update": True
}


def set_value(key, value):
    """定义一个宇宙变量"""
    if type(value) is list:
        for i in range(len(value)):
            if len(_universe_dict[key]) < len(value):
                raise CustomError('传入超维列表')
            _universe_dict[key][i] = value[i]
    else:
        _universe_dict[key] = value


def get_value(key):
    """获得一个宇宙变量"""
    try:
        return _universe_dict[key]
    except KeyError:
        return None


class CustomError(Exception):
    def __init__(self, ErrorInfo):
        super().__init__(self)  # 初始化父类
        self.errorinfo = ErrorInfo

    def __str__(self):
        return self.errorinfo
