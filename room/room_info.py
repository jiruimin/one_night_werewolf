#!/usr/bin/python3

import asyncio
import websockets
import time
import uuid
import random
import json
import logging
from one_night_werewolf.role import base_role
from one_night_werewolf.room import msg


'捣蛋鬼Troublemaker'
'强盗Robber'
'女巫Witch'
'预言家Seer'
'爪牙　Minion'
'普通狼人　Werewolf'
'头狼　Alpha wolf'
'失眠者Insomniac'
'酒鬼Drunk'
'守夜人Mason'
'化身幽灵 Doppelganger'
'猎人 hunter'

class GameRoom(object):
    def __init__(self, roomid, roles):
        ## 房间信息
        self.roomid = roomid
        self._owner = ''
        self._root_create_time = time.time()
        self._game_start_time = time.time()
        self._end_time = None
        self.roles = roles
        self.player_max = len(roles) - 3

        ## 游戏信息
        self.players = {}
        self.players_order_list = []  ## key：player.open_id, value : base_role
        self.role_to_player = {}  ## key：_baseRole._role_name, value : player
        self.left_role = []
        

    def join_room(self, player):
        self.players[player.open_id] = player
        
    def start_game(self):
        self.role_to_player = {}
        self.left_role = []
        players_order_list = list(self.players.values()) 
        if(len(players_order_list) != self.player_max):
            logging.info('room start faile..')
            return msg.S_msg(-1, '房间玩家不够开始游戏', 'info', [o.to_dict() for o in players_order_list])
        self._game_start_time = time.time()
        logging.info('room start...')

        ## 随机分配角色
        roles_obj = []
        for role in self.roles:
            role_class = getattr(base_role, role)
            role_obj = role_class()
            roles_obj.append(role_obj)
        logging.info('roles load success......')
        random.shuffle(roles_obj)
        self.left_role = roles_obj[len(players_order_list):]
        for i in range(len(players_order_list)):
            # self.player_to_role[players_list[i].open_id] = roles_obj[i]
            players_order_list[i]._roles = [roles_obj[i]]
            rp = []
            if roles_obj[i]._role_name in self.role_to_player:
                rp = self.role_to_player[roles_obj[i]._role_name]
            rp.append(players_order_list[i])
            self.role_to_player[roles_obj[i]._role_name] = rp

        logging.info('player_role: ' + str([player.name+":"+player._roles[0]._role_name for player in self.players.values()]))
        logging.info('left_role: ' + str([x._role_name for x in self.left_role]))


        players_order_list.sort(key = lambda player : player._roles[0]._action_num)
        self.players_order_list = players_order_list
        for pen in players_order_list:
            logging.info(pen.name+':operate_begin: ' + json.dumps(pen._roles[0],default=lambda o: o.__dict__,ensure_ascii=False))
            pen._roles[0].operate_begin(pen)
        return None

    def cal_game(self):
        flag = True
        for player in self.players.values():
            if player._roles[0].status != 10:
                logging.info(f'{player.name}[{player._roles[0].to_dict()}]未操作')
                flag = False
                break
        if flag:
            logging.info(f'房间[{self.roomid}]所有玩家操作完成')
            for pen in self.players_order_list:
                pen._roles[0].operate_end(pen)
        return None

    def end_game(self):
        for player in self.players.values():
            player
        return None
    
        

if __name__ == '__main__':
    room = GameRoom(str(uuid.uuid5(uuid.NAMESPACE_DNS, 'jirm')), ['troublemaker','werewolf','mason','drunk','seer','minion','robber'])
    room.join_room(['jirm1','jirm2','jirm3','jirm4'])
    room.start_game()
    print(f'roomid:{room.roomid}')