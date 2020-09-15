from graia.application.entry import (
    GraiaMiraiApplication, Session,
    MessageChain, Group, Friend, Member, MemberInfo, MemberPerm,
    Plain, Image, AtAll, At, Face,
)
from graia.application.entry import (
    BotMuteEvent, BotGroupPermissionChangeEvent,
)
from graia.broadcast import (
    Broadcast,
)
from graia.scheduler import (
    timers,
)
import graia.scheduler as scheduler
import datetime,time
import asyncio
# 增强功能
import threading, os, pivixDownloader, extraEvent, Universe,re

# daily锁
Universe.set_value("lock", threading.Lock())
# 录入图片锁
Universe.set_value("SavePicLock", threading.Lock())

# 色图总览
schedulepermission = extraEvent.getschedulepermission()

# 管理员
_MANAGER = [775086089, 315067671]
loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:8080",  # 填入 httpapi 服务运行的地址
        authKey="INITKEYqrgJFDys",  # 填入 authKey
        account=3491230400,  # 你的机器人的 qq 号
        websocket=True  # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)
sche = scheduler.GraiaScheduler(loop=loop,broadcast=bcc)

@bcc.receiver("BotGroupPermissionChangeEvent")
async def getOwnerAccess(app: GraiaMiraiApplication):
    print(await app.groupList())


# 由于mirai问题，pcqq好友 无法接受
@bcc.receiver("FriendMessage")
async def friend_message_listener(app: GraiaMiraiApplication, message: MessageChain, friend: Friend):
    if friend.id in _MANAGER:
        if message.asDisplay() == "UpdateToday":
            await app.sendFriendMessage(friend, message.create([Plain("开始更新今日色图......")]))
            thread = threading.Thread(target=extraEvent.DayilyMission, args=(friend,0))
            thread.start()
        elif message.asDisplay() == "Init":
            await app.sendFriendMessage(friend, message.create([Plain("初始化......")]))
            extraEvent.initNow(app, message, friend, loop)
        elif message.asDisplay() == "图裂了":
            await app.sendFriendMessage(friend, message.create([Plain("正在想办法处理......")]))
            extraEvent.fixPics(app, message, friend, loop)
        '''if message.asDisplay() == "今日色图":
            try:
                print(Universe.get_value("setuScan"))
                print(os.path.abspath(Universe.get_value("setuScan")))
                await app.sendFriendMessage(friend,
                                            message.create([Image.fromUnsafePath("Pixiv/2020-09-12/day_r18_scan.jpg")]))
            except:
                extraEvent.initNow(app, message, friend, loop)
                await app.sendFriendMessage(friend,
                                            message.create([Image.fromUnsafePath("Pixiv/2020-09-12/day_r18_scan.jpg")]))
        elif message.asDisplay() == "今日好图":
            try:
                await app.sendFriendMessage(friend,
                                            message.create([Image.fromLocalFile(Universe.get_value("haotuScan"))]))
            except:
                extraEvent.initNow(app, message, friend, loop)
                await app.sendFriendMessage(friend,
                                            message.create([Image.fromLocalFile(Universe.get_value("haotuScan"))]))'''# 错误待解决
        if re.search("色图$", message.asDisplay()):
            setuInd = Universe.get_value("setuInd")
            imgid= await app.sendFriendMessage(friend, message.create(
                [Image.fromLocalFile(extraEvent.setuList[setuInd % len(extraEvent.setuList)])]))
            print(imgid)
            await app.sendFriendMessage(friend, message.create([Plain("今日发送的第{}份色图".format(setuInd))]))
            setuInd += 1
            Universe.set_value("setuInd", setuInd)
        elif re.search("好图$", message.asDisplay()):
            haotuInd = Universe.get_value("haotuInd")
            await app.sendFriendMessage(friend, message.create(
                [Image.fromLocalFile(extraEvent.haotuList[haotuInd % len(extraEvent.haotuList)])]))
            await app.sendFriendMessage(friend, message.create([Plain("今日发送的第{}份好图".format(haotuInd))]))
            print(extraEvent.haotuList[haotuInd % len(extraEvent.haotuList)])
            haotuInd += 1
            Universe.set_value("haotuInd", haotuInd)
        if message.has(Image):
            savePicLs = message[Image]
            counter = len(savePicLs)
            await app.sendFriendMessage(friend, message.create([Plain("{}张".format(counter))]))
            threadPic = threading.Thread(target=extraEvent.savePic, args=(savePicLs, 3))
            threadPic.start()


@bcc.receiver("GroupMessage")
async def group_message_handler(app: GraiaMiraiApplication, message: MessageChain, group: Group, member: Member):
    if message.asDisplay().startswith("复读"):
        await app.sendGroupMessage(group, message.create([
            Plain(message.exclude(Image).asDisplay())
        ]))

    if re.search("色图$", message.asDisplay()) and (group.id in schedulepermission):
        setuInd = Universe.get_value("setuInd")
        await app.sendGroupMessage(group, message.create(
            [Image.fromLocalFile(extraEvent.setuList[setuInd % len(extraEvent.setuList)])]))
        await app.sendGroupMessage(group, message.create([Plain("今日发送的第{}份色图".format(setuInd))]))
        print(extraEvent.setuList[setuInd % len(extraEvent.setuList)])
        setuInd += 1
        Universe.set_value("setuInd", setuInd)
    elif re.search("好图$", message.asDisplay()) and (group.id in schedulepermission):
        haotuInd = Universe.get_value("haotuInd")
        await app.sendGroupMessage(group, message.create(
            [Image.fromLocalFile(extraEvent.haotuList[haotuInd % len(extraEvent.haotuList)])]))
        await app.sendGroupMessage(group, message.create([Plain("今日发送的第{}份好图".format(haotuInd))]))
        print(extraEvent.haotuList[haotuInd % len(extraEvent.haotuList)])
        haotuInd += 1
        Universe.set_value("haotuInd", haotuInd)

    if message.asDisplay() == "色图一览":
        print(Universe.get_value("setuScan"))
        print(os.path.abspath(Universe.get_value("setuScan")))
        await app.sendGroupMessage(group,
                                    message.create([Image.fromLocalFile(Universe.get_value("setuScan"))]))
    elif message.asDisplay() == "好图一览":
        await app.sendGroupMessage(group,
                                    message.create([Image.fromLocalFile(Universe.get_value("haotuScan"))]))

    if (member.id - 2854196310 == 0):
        # 群管家日常运维
        await app.sendGroupMessage(group, message.create([Plain("开始更新今日色图......")]))
        threadDaily = threading.Thread(target=extraEvent.DayilyMission, args=(group,0))
        threadDaily.start()
    elif member.permission is MemberPerm.Owner:
        if message.asDisplay().startswith("Update"):
            await app.sendGroupMessage(group, message.create([Plain("开始更新今日色图......")]))
            threadDaily = threading.Thread(target=extraEvent.DayilyMission, args=(group,0))
            threadDaily.start()
        elif message.asDisplay().startswith("Init"):
            await app.sendGroupMessage(group, message.create([Plain("初始化......")]))
            extraEvent.initNow(app, message, group, loop)
        elif message.asDisplay() == "图裂了":
            await app.sendFriendMessage(group, message.create([Plain("正在想办法处理......")]))
            extraEvent.fixPics(app, message, group, loop)

    if message.has(Image):
        # 日常收集图片
        savePicLs = message[Image]
        counter = len(savePicLs)
        await app.sendGroupMessage(group, message.create([Plain("{}张".format(counter))]))
        threadPic = threading.Thread(target=extraEvent.savePic, args=(savePicLs, 3))
        threadPic.start()
    # print(message)


@bcc.receiver(BotGroupPermissionChangeEvent)
async def permission_listener(bgp: BotGroupPermissionChangeEvent):
    print(bgp.current)
    print(bgp.origin)


@sche.schedule(timers.every_custom_seconds(60))
async def eventChecker60():
    if Universe.get_value("dailyMession")[0] is 1:
        sender = Universe.get_value("dailyMession")[1]
        if type(sender) is Group:
            await app.sendGroupMessage(sender,MessageChain.create([
                Plain(f"今日色图更新成功，发送 色图 或者 好图 进行查看")
            ]))
        elif type(sender) is Friend:
            await app.sendFriendMessage(sender, MessageChain.create([
                Plain(f"今日色图更新成功，发送 色图 或者 好图 进行查看")
            ]))
        Universe.set_value("dailyMession",[0,None])
    elif Universe.get_value("dailyMession")[0] is -1:
        sender = Universe.get_value("dailyMession")[1]
        if type(sender) is Group:
            await app.sendGroupMessage(sender, MessageChain.create([
                Plain(f"今日色图更新失败")
            ]))
        elif type(sender) is Friend:
            await app.sendFriendMessage(sender, MessageChain.create([
                Plain(f"今日色图更新失败")
            ]))
        await app.sendFriendMessage(775086089, MessageChain.create([
                Plain(f"今日色图更新失败,请检查网络设置")
            ]))
        Universe.set_value("dailyMession", [0, None])

app.launch_blocking()
