from typing import NoReturn, Optional

from graia.application.event.mirai import EmptyDispatcher
from pydantic import Field
from graia.application.context import application
from graia.application.group import Group, Member, MemberPerm
from graia.application.exceptions import InvaildArgument, InvaildSession
from graia.application.utilles import raise_for_return_code
from graia.application.event import ApplicationDispatcher, MiraiEvent
from graia.broadcast.entities.dispatcher import BaseDispatcher
from graia.broadcast.interfaces.dispatcher import DispatcherInterface
from datetime import datetime


class FriendInputStatusChangeEvent(MiraiEvent):
    """当该事件发生时, 好友的输入状态改变

    ** 注意: 当监听该事件或该类事件时, 请优先考虑使用原始事件类作为类型注解, 以此获得事件类实例, 便于获取更多的信息! **

    Allowed Extra Parameters(提供的额外注解支持):
        GraiaMiraiApplication (annotation): 发布事件的应用实例
    """

    type = "FriendInputStatusChangeEvent"
    friend: int
    inputting: bool

    class Dispatcher(BaseDispatcher):
        mixin = [ApplicationDispatcher]

        @staticmethod
        def catch(interface: DispatcherInterface):
            pass

