from graia.application.entry import (
    GraiaMiraiApplication, Session,
    MessageChain, Group, Friend, Member, MemberInfo, MemberPerm,
    Plain, Image, AtAll, At, Face, Quote,Source,
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
import datetime, time
import asyncio
# 增强功能
import threading, os, pivixDownloader, extraEvent, Universe, re, accounts

# daily锁
Universe.set_value("lock", threading.Lock())
# 录入图片锁
Universe.set_value("SavePicLock", threading.Lock())
# 每日更新进度
isFresh = extraEvent.freshChecker()
# 色图总览
schedulepermission = extraEvent.getschedulepermission()

# 管理员
_MANAGER = accounts._ACCOUNT["BOTmanager"]
loop = asyncio.get_event_loop()

bcc = Broadcast(loop=loop)
app = GraiaMiraiApplication(
    broadcast=bcc,
    connect_info=Session(
        host="http://localhost:8080",  # 填入 httpapi 服务运行的地址
        authKey=accounts._ACCOUNT["BOTauthKey"],  # 填入 authKey
        # authKey="INITKEYqrgJFDys",  # 填入 authKey
        account=accounts._ACCOUNT["BOTaccount"],  # 你的机器人的 qq 号
        websocket=True  # Graia 已经可以根据所配置的消息接收的方式来保证消息接收部分的正常运作.
    )
)
sche = scheduler.GraiaScheduler(loop=loop, broadcast=bcc)


@bcc.receiver("BotGroupPermissionChangeEvent")
async def getOwnerAccess(app: GraiaMiraiApplication):
    print(await app.groupList())


# 由于mirai问题，pcqq好友 无法接受
@bcc.receiver("FriendMessage")
async def friend_message_listener(app: GraiaMiraiApplication, message: MessageChain, friend: Friend):
    if friend.id in _MANAGER:
        if message.asDisplay() == "UpdateToday":
            await app.sendFriendMessage(friend, message.create([Plain("开始更新今日色图......")]))
            thread = threading.Thread(target=extraEvent.DayilyMission, args=(friend, 0))
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
                                            message.create([Image.fromLocalFile(Universe.get_value("haotuScan"))]))'''  # 错误待解决
        if re.search("色图$", message.asDisplay()):
            setuInd = Universe.get_value("setuInd")
            imgid = await app.sendFriendMessage(friend, message.create(
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
            At(member.id),Plain(message.exclude(Image).asDisplay())
        ]),quote=message.__root__[0].id)



    if re.search(r"色图 \d", message.asDisplay()) and (group.id in schedulepermission):
        setuInd = Universe.get_value("setuInd")
        setuId = message.asDisplay().split(" ")[1]
        setuId = eval(setuId) - 1
        await app.sendGroupMessage(group, message.create(
            [Image.fromLocalFile(extraEvent.setuList[setuId % len(extraEvent.setuList)])]))
        await app.sendGroupMessage(group, message.create([Plain("今日发送的第{}份色图".format(setuInd))]))
        print(extraEvent.setuList[setuInd % len(extraEvent.setuList)])
        setuInd += 1
        Universe.set_value("setuInd", setuInd)
    elif re.search(r"好图 \d", message.asDisplay()) and (group.id in schedulepermission):
        haotuInd = Universe.get_value("haotuInd")
        haotuId = message.asDisplay().split(" ")[1]
        haotuId = eval(haotuId) - 1
        await app.sendGroupMessage(group, message.create(
            [Image.fromLocalFile(extraEvent.haotuList[haotuId % len(extraEvent.haotuList)])]))
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

    if member.permission is MemberPerm.Owner:
        if message.asDisplay().startswith("Update"):
            await app.sendGroupMessage(group, message.create([Plain("开始更新今日色图......")]))
            threadDaily = threading.Thread(target=extraEvent.DayilyMission, args=(group, 0))
            threadDaily.start()
        elif message.asDisplay().startswith("Init"):
            await app.sendGroupMessage(group, message.create([Plain("初始化......")]))
            extraEvent.initNow(app, message, group, loop)
        elif message.asDisplay() == "图裂了":
            await app.sendFriendMessage(group, message.create([Plain("正在想办法处理......")]))
            extraEvent.fixPics(app, message, group, loop)

    if message.has(Image):  #图片保存
        # 日常收集图片
        savePicLs = message[Image]
        counter = len(savePicLs)
        sourceid = message.__root__[0].id
        #await app.sendGroupMessage(group, message.create([Plain("{}张".format(counter))]))
        threadPic = threading.Thread(target=extraEvent.savePic, args=(savePicLs, counter, app, sourceid, group, loop))
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
            await app.sendGroupMessage(sender, MessageChain.create([
                Plain(f"今日色图更新成功，发送 色图 或者 好图 进行查看")
            ]))
        elif type(sender) is Friend:
            await app.sendFriendMessage(sender, MessageChain.create([
                Plain(f"今日色图更新成功，发送 色图 或者 好图 进行查看")
            ]))
        elif type(sender) is list:  # 只会是自动更新
            for ls in sender:
                await app.sendGroupMessage(ls, MessageChain.create([
                    Plain(f"今日色图更新成功，发送 色图 或者 好图 进行查看")
                ]))
                await app.sendGroupMessage(ls,
                                           MessageChain.create(
                                               [Plain("色图一览"), Image.fromLocalFile(Universe.get_value("setuScan"))
                                                ]))
                await app.sendGroupMessage(ls,
                                           MessageChain.create(
                                               [Plain("好图一览"), Image.fromLocalFile(Universe.get_value("haotuScan"))]))

        Universe.set_value("dailyMession", [0, None])
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

    global isFresh
    if not isFresh:
        if extraEvent.getDate("%H") == "08":
            isFresh = True
            await app.sendFriendMessage(775086089, MessageChain.create([
                Plain(f"开始更新")
            ]))
            for ls in await app.groupList():
                if ls.id in schedulepermission:
                    await app.sendGroupMessage(ls, MessageChain.create([Plain("开始更新每日色图......")]))
            await app.sendFriendMessage(775086089, MessageChain.create([
                Plain(f"群消息发送成功")
            ]))
            threadDaily = threading.Thread(target=extraEvent.DayilyMission, args=(schedulepermission, 0))
            threadDaily.start()


'''
@sche.schedule(timers.every_hours())
async def eventChecker3600():
    
    if extraEvent.getDate("%H") == "09":
        await app.sendFriendMessage(775086089, MessageChain.create([
            Plain(f"开始更新")
        ]))
        for ls in await app.groupList():
            if ls.id in schedulepermission:
                await app.sendGroupMessage(ls, MessageChain.create([Plain("开始更新每日色图......")]))
        await app.sendFriendMessage(775086089, MessageChain.create([
            Plain(f"群消息发送成功")
        ]))
        threadDaily = threading.Thread(target=extraEvent.DayilyMission, args=(schedulepermission, 0))
        threadDaily.start()
    '''

app.launch_blocking()
