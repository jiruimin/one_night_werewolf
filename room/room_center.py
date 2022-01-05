#!/usr/bin/python3

import websockets
import time
import uuid
import random
import logging
from one_night_werewolf.room import room_info

room_dict = {}

def create_room(player, roles):
    room = room_info.GameRoom(str(uuid.uuid5(uuid.NAMESPACE_DNS, player.open_id)), roles)
    room_dict[room.roomid] = room
    return room

def join_room(roomid, player):
    if roomid in room_dict:
        logging.info(f'{player.open_id}加入房间{roomid}')
        room_dict[roomid].join_room(player)
        return room_dict[roomid]
    else:
        return None

def start_game(roomid):
    if roomid in room_dict:
        return room_dict[roomid].start_game()
    