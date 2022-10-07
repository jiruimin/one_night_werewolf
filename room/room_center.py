#!/usr/bin/python3

import websockets
import time
import json
import random
import logging
from one_night_werewolf.room import room_info
from one_night_werewolf.room import player_info
from one_night_werewolf.room import msg

from one_night_werewolf.util import sqlite
sqliteUtil = sqlite.SqliteUtil()

room_dict = {}


def create_room(player: player_info.Player, roles_config: dict) -> room_info.GameRoom:
    roomid = sqliteUtil.create_room(
        {'roles': json.dumps(roles_config), 'room_owner': player.openid})
    roomid = 22
    room = room_info.GameRoom(roomid, roles_config)

    room_dict[room.roomid] = room
    return room


def join_room(roomid: int, player: player_info.Player) -> room_info.GameRoom:
    if roomid in room_dict:
        logging.info(f'{player.openid},{player.nickName}加入房间{roomid}')
        room_dict[roomid].join_room(player)
        return room_dict[roomid]
    else:
        return None


def start_game(roomid: int) -> msg.S_msg:
    if roomid in room_dict:
        room = room_dict[roomid]
        sqliteUtil.start_room({'players': room.players, "roomid": roomid})
        return room_dict[roomid].start_game()


def get_room(roomid: int) -> room_info.GameRoom:
    if roomid in room_dict:
        return room_dict[roomid]
