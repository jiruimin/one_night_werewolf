#!/usr/bin/python3

import time
import json
import uuid
import _thread
import asyncio
import logging
from one_night_werewolf.room import msg

class Player(object):
    # open_id : str
    # name : str
    # websocket : WebSocket
    
    def __init__(self, open_id, name, websocket):
        self.open_id = open_id
        self.name = name
        self.websocket = websocket
        self._roles = []
        self._death = False
        self.room = None
    def to_dict(self):
        return {'open_id':self.open_id,'name':self.name,'_roles':[o.to_dict() for o in self._roles]}

    def send_self(self):
        self.send_msg(msg.S_msg(0, '', 'player_info', self.to_dict()))

    def send_msg(self, smsg):
        def send(smsg):
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.websocket.send_text(json.dumps(smsg,default=lambda o: o.__dict__,ensure_ascii=False)))
            except Exception as e:
                logging.error(e)
        _thread.start_new_thread(send, [smsg])

    def recv_msg(self, rmsg):
        fun = rmsg.op_type
        ## globals()[item]()
        return getattr(self, fun)(rmsg)

    def create_room(self, rmsg):
        from one_night_werewolf.room import room_center
        room = room_center.create_room(self, rmsg.op_content['roles'])
        self.room = room
        logging.info('创建房间成功')
        return msg.S_msg(0, '创建房间成功', 'info', {'room_id':self.room.roomid})

    def join_room(self, rmsg):
        from one_night_werewolf.room import room_center
        roomid = rmsg.op_content['room_id']
        if roomid not in room_center.room_dict:
            logging.info('房间不存在')
            return msg.S_msg(-1, '房间不存在', 'info', self.room.roomid)
        logging.info(f'{self.name}加入房间{roomid}成功')
        self.room = room_center.room_dict[roomid]
        room_center.join_room(roomid, self)
        return msg.S_msg(0, '加入房间成功', 'info', self.room.roomid)

    def start_game(self, rmsg):
        return self.room.start_game()

    def operate_msg(self, rmsg):
        self._roles[0].operate_msg(rmsg)
        self.room.cal_game()

    def debug(self, rmsg):
        lr_msg = [o.to_dict() for o in self.room.left_role]
        logging.info('left_role:'+ json.dumps(lr_msg))
        for player in self.room.players_order_list:
            player.send_self()
            

if __name__ == '__main__':
    player1 = Player('111', '111', None)
    player2 = Player('222', '222', None)
    ll = [player1, player2]
    res = [p.to_dict() for p in ll]
    print(f'res:{res}')