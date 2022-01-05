import json
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

from one_night_werewolf.room import player_info
from one_night_werewolf.room import msg
import logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s %(name)s %(levelname)s %(message)s",
                    datefmt = '%Y-%m-%d  %H:%M:%S'    #注意月份和天数不要搞乱了，这里的格式化符与time模块相同
                    )
player_dict = {}

pity = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <h1>WebSocket Chat</h1>
        <h2>Your ID: <span id="ws-id"></span></h2>
        <form action="" onsubmit="sendMessage(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <ul id='messages'>
        </ul>
        <script>
            var client_id = Date.now()
            document.querySelector("#ws-id").textContent = client_id;
            var ws = new WebSocket(`ws://localhost:8000/ws/${client_id}`);
            ws.onmessage = function(event) {
                var messages = document.getElementById('messages')
                var message = document.createElement('li')
                var content = document.createTextNode(event.data)
                message.appendChild(content)
                messages.appendChild(message)
            };
            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send_text()input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""

async def check_permit(websocket):
    while True:
        recv_str = await websocket.receive_text()
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



@pity.get("/")
async def get():
    return HTMLResponse(html)


@pity.websocket("/ws/{name}")
async def websocket_endpoint(websocket: WebSocket, name: str):
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

if __name__ == "__main__":
    uvicorn.run(app=pity, host="127.0.0.1", port=5000, log_level="info")
