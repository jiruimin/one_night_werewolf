#!/usr/bin/python3

import asyncio
import websockets
import time
import uuid
import random
import time
import json
import logging
from one_night_werewolf.role import base_role
from one_night_werewolf.room import msg
from one_night_werewolf.room import player_info


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
    def __init__(self, roomid, roles_config):
        # 房间信息
        self.roomid = roomid
        self._owner = ''
        self._room_create_time = time.time()
        self._game_start_time = time.time()
        self._game_end_time = None
        self.roles_config = roles_config
        self.player_max = len(roles_config) - 3
        # 游戏信息
        self.players = {}  # key：openid, value : player
        self.players_order_list = []  # 玩家列表，按行动顺序排序
        self.role_to_player = {}  # key：_baseRole._role_name, value : player
        self.left_role = []

    def to_dict(self):
        return {'roomid': self.roomid, 'room_create_time': self._room_create_time, 'game_start_time': self._game_start_time,
                'game_end_time': self._game_end_time, 'player_max': self.player_max, 'roles_config': self.roles_config,
                'players': [o.to_dict() for o in self.players.values()],
                'left_role': [o.to_dict() for o in self.left_role]}

    def join_room(self, player: player_info.Player):
        self.players[player.openid] = player
        for player in self.players.values():
            player.send_msg(
                msg.S_msg(0, f'{player.nickName}加入了房间...', 'info', None))

    def leave_room(self, player: player_info.Player):
        player = self.players.pop(player.openid)
        for player in self.players.values():
            player.send_msg(
                msg.S_msg(0, f'{player.nickName}离开了房间...', 'info', None))

    def start_game(self) -> msg.S_msg:
        self._game_start_time = time.time()
        self._game_end_time = None
        self.role_to_player = {}
        self.left_role = []
        players_order_list = list(self.players.values())
        if(len(players_order_list) != self.player_max):
            logging.info('room start faile..')
            return msg.S_msg(-1, '房间玩家不够开始游戏', 'info', [o.to_dict() for o in players_order_list])
        self._game_start_time = time.time()
        logging.info('room start...')

        # 随机分配角色
        roles_obj = []
        for role in self.roles_config:
            role_class = getattr(base_role, role.capitalize())
            role_obj = role_class()
            roles_obj.append(role_obj)
        logging.info('roles load success......')
        random.shuffle(roles_obj)
        self.left_role = roles_obj[len(players_order_list):]
        for i in range(len(players_order_list)):
            # self.player_to_role[players_list[i].openid] = roles_obj[i]
            players_order_list[i]._roles = [roles_obj[i]]
            rp = []
            if roles_obj[i]._role_name in self.role_to_player:
                rp = self.role_to_player[roles_obj[i]._role_name]
            rp.append(players_order_list[i])
            self.role_to_player[roles_obj[i]._role_name] = rp
            players_order_list[i]._death = False
            players_order_list[i].vote_msg = None
            players_order_list[i].vote_num = 0
            players_order_list[i].is_win = None

        logging.info('player_role: ' + str([player.nickName+":" +
                     player._roles[0]._role_name for player in self.players.values()]))
        logging.info('left_role: %s' % str([x._role_name for x in self.left_role]))

        players_order_list.sort(
            key=lambda player: player._roles[0]._action_num)
        self.players_order_list = players_order_list
        for pen in players_order_list:
            logging.info(pen.nickName+':operate_begin: ' +
                         json.dumps(pen._roles[0].to_dict()))
            pen._roles[0].operate_begin(pen)
        return None

    def cal_game(self):
        flag = True
        for player in self.players.values():
            if player._roles[0].status < 10 and player._roles[0]._action_num > 0:
                logging.info(
                    f'{player.nickName}[{player._roles[0].to_dict()}]未操作')
                flag = False
                break
        if flag:
            logging.info(f'房间[{self.roomid}]所有玩家操作完成')
            for pen in self.players_order_list:
                pen._roles[0].operate_end(pen)
            start = random.randint(1, len(self.players))
            time.sleep(5)
            for player in self.players.values():
                player.send_msg(
                    msg.S_msg(0, f'游戏开始，请从{start}号开始发言......', 'info', None))
        return None

    def end_game(self):
        for player in self.players.values():
            if player.vote_msg is None:
                logging.info(
                    f'房间[{self.roomid}]等待玩家[{player.nickName}]投票完成......')
                return None
        logging.info(f'房间[{self.roomid}]所有玩家投票完成')
        d_player = set()
        d_vote_num = 0
        # vote_res = dict()
        for player in self.players.values():
            openid = player.vote_msg.op_content['vote_msg']['openid']
            # 记录投票结果
            dest_p = self.players[openid]
            dest_p.vote_num = dest_p.vote_num + 1

            # 记录投票最多的玩家
            if dest_p.vote_num > d_vote_num:
                d_player = {dest_p}
                d_vote_num = dest_p.vote_num
            elif dest_p.vote_num == d_vote_num:
                d_player.add(dest_p)

        logging.info(f'房间[{self.roomid}]投票出局的玩家：[{[o.to_dict() for o in d_player]}]')
        hunter = None
        for player in d_player:
            player._death = True
            if player._roles[-1]._role_name == 'hunter':
                hunter = player

        '''通知猎人发动技能'''
        if hunter != None:
            hunter.send_msg(msg.S_msg(0, 'hunter', 'wait_back',
                            {'hunter': hunter.to_dict()}))
        else:
            self.game_result()
        return None

    def game_result(self):
        def get_last_role_name(player):
            last_role = player._roles[-1]._role_name
            if last_role == 'doppelganger':
                last_role = player._roles[-1].copy_role._role_name
            return last_role
        if self._game_end_time is None:
            villager_win = False
            death_role_name = set()
            last_role_name = set()
            for player in self.players_order_list:
                lrn = get_last_role_name(player)
                last_role_name.add(lrn)
                if player._death:
                    death_role_name.add(lrn)
            # 场上存在狼人  狼人死则村民获胜
            if len({'werewolf', 'alphawolf'}.intersection(death_role_name)) > 0:
                villager_win = True
            # 场上不存在狼人  爪牙死则村民获胜
            if 'minion' in death_role_name and len({'werewolf', 'alphawolf'}.intersection(last_role_name)) == 0:
                villager_win = True
            for player in self.players_order_list:
                last_role_name = get_last_role_name(player)
                if last_role_name in {'minion', 'werewolf', 'alphawolf'}:
                    player.is_win = not villager_win
                else:
                    player.is_win = villager_win
            logging.info(
                f'房间[{self.roomid}]游戏结束villager_win:[{villager_win}], [{self.to_dict()}]')
            self._game_end_time = time.time()

        for player in self.players_order_list:
            player.send_msg(
                msg.S_msg(0, 'game_over', 'game_info', self.to_dict()))


if __name__ == '__main__':
    room = GameRoom(str(uuid.uuid5(uuid.NAMESPACE_DNS, 'jirm')), [
                    'troublemaker', 'werewolf', 'mason', 'drunk', 'seer', 'minion', 'robber'])
    room.join_room(['jirm1', 'jirm2', 'jirm3', 'jirm4'])
    room.start_game()
    print(f'roomid:{room.roomid}')
