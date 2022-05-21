import json
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

import time
from apscheduler.schedulers.blocking import BlockingScheduler
import requests
import _thread

from one_night_werewolf.room import msg
from one_night_werewolf.room import room_center
from one_night_werewolf.room import player_info

import logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s",
                    datefmt = '%Y-%m-%d  %H:%M:%S'    #注意月份和天数不要搞乱了，这里的格式化符与time模块相同
                    )

sched = BlockingScheduler()
from one_night_werewolf.util import sqlite
sqliteUtil = sqlite.SqliteUtil()
# access_token = ''

player_dict = {}
pity = FastAPI()
# AppID(小程序ID)  wxf5015f38fc530f6e
# AppSecret(小程序密钥)  998bac19333056b393f3731901054c5b
@sched.scheduled_job('interval', minutes=90)
def fetch_token():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=wxf5015f38fc530f6e&secret=998bac19333056b393f3731901054c5b'
    res = requests.get(url=url).text
    root = json.loads(res)
    global access_token
    access_token = root['access_token']
    logging.info(f"获取微信token:{access_token}")

async def check_permit(websocket) -> player_info.Player:
    while True:
        recv_str = await websocket.receive_text()
        logging.info(f"player loading:{recv_str}")
        rmsg = msg.R_msg(recv_str)
        if rmsg.openid is not None:
            sqliteUtil.insert_user({'openid':rmsg.openid, 'nickName':rmsg.nickName, 'avatarUrl':rmsg.avatarUrl})
            user_info = sqliteUtil.select_user(rmsg.openid)
            player = player_info.Player(user_info['openid'],user_info['nickName'],user_info['avatarUrl'],websocket)
            player_dict[rmsg.openid]=player
            return player
        else:
            return None


# 接收客户端消息并处理，这里只是简单把客户端发来的返回回去
async def recv_msg(player):
    while True:
        recv_str = await player.websocket.receive_text()
        rmsg = msg.R_msg(recv_str)
        re = player.recv_msg(rmsg)
        if re is not None:
            await player.websocket.send_text(json.dumps(re,default=lambda o: o.__dict__,ensure_ascii=False))
        # try:
        #     rmsg = msg.R_msg(recv_str)
        #     re = player.recv_msg(rmsg)
        #     if re is not None:
        #         await player.websocket.send_text(json.dumps(re,default=lambda o: o.__dict__,ensure_ascii=False))
        # except Exception as e:
        #         logging.error(str(e))

# 服务器端主逻辑
# websocket和path是该函数被回调时自动传过来的，不需要自己传
async def disconnect(websocket, path):
    player = await check_permit(websocket)
    if(player is None):
        await websocket.send_text('{"code":-1,"msg":"登陆出错！","data":null}')
    else:
        await websocket.send_text('{"code":0,"msg":"登陆成功！","data":"登陆成功！"}')
        await recv_msg(player)


@pity.get("/one_night_werewolf/room_info/{roomid}")
async def get(roomid:int):
    room = room_center.get_room(roomid)
    if(room):
        return {"code":0,"msg":"","data":room.to_dict()}
    return {"code":0,"msg":"","data":None}

@pity.get("/one_night_werewolf/access_token")
async def get_access_token():
    return {"code":0,"msg":"","data":access_token}

@pity.get("/one_night_werewolf/user_info/{openid}")
async def get_user_info(openid:str):
    user_info = sqliteUtil.select_user(openid)
    return {"code":0,"msg":"","data":user_info}
    


@pity.websocket("/one_night_werewolf/connect/{openid}")
async def websocket_endpoint(websocket: WebSocket, openid: str):
    await websocket.accept()
    try:
        while True:
            player = await check_permit(websocket)
            if(player is None):
                await websocket.send_text('{"code":-1,"msg":"登陆出错！","data":null}')
            else:
                await websocket.send_text('{"code":0,"msg":"登陆成功！","data":"登陆成功！"}')
                await recv_msg(player)
    except WebSocketDisconnect as e:
        logging.error(e)
        if openid in player_dict:
            player_dict[openid].leave_room()

if __name__ == "__main__":
    def fetch():
        fetch_token()
        sched.start()
    _thread.start_new_thread(fetch, ())
    uvicorn.run(app=pity, host="0.0.0.0", port=5010, log_level="info")