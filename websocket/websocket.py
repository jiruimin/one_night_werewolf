import asyncio
import websockets
import json
import _thread
import logging
from one_night_werewolf.room import player_info
from one_night_werewolf.room import msg
player_dict = {}

# 检测客户端权限，用户名密码通过才能退出循环
async def check_permit(websocket):
    while True:
        recv_str = await websocket.recv()
        logging.info(f"player loading:{recv_str}")
        rmsg = msg.R_msg(recv_str)
        if rmsg.open_id is not None:
            player = player_info.Player(rmsg.open_id,rmsg.name,websocket)
            player_dict[rmsg.open_id]=player
            return player
        else:
            return None


# 接收客户端消息并处理，这里只是简单把客户端发来的返回回去
async def recv_msg(player):
    while True:
        recv_str = await player.websocket.recv()
        try:
            rmsg = msg.R_msg(recv_str)
            re = player.recv_msg(rmsg)
            if re is not None:
                await player.websocket.send(json.dumps(re,default=lambda o: o.__dict__,ensure_ascii=False))
        except Exception as e:
                logging.error(e)
   
# 服务器端主逻辑
# websocket和path是该函数被回调时自动传过来的，不需要自己传
async def main_logic(websocket, path):
    player = await check_permit(websocket)
    if(player is None):
        await websocket.send('{"code":-1,"msg":"登陆出错！","data":null}')
    else:
        await websocket.send('{"code":0,"msg":"登陆成功！","data":"登陆成功！"}')
        await recv_msg(player)

# 把ip换成自己本地的ip
start_server = websockets.serve(main_logic, 'localhost', 5678)
# 如果要给被回调的main_logic传递自定义参数，可使用以下形式
# 一、修改回调形式
# import functools
# start_server = websockets.serve(functools.partial(main_logic, other_param="test_value"), '10.10.6.91', 5678)
# 修改被回调函数定义，增加相应参数
# async def main_logic(websocket, path, other_param)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()