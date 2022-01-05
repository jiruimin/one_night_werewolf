#!/usr/bin/python3
import abc
import sys
from one_night_werewolf.room import msg

troublemaker_role = 'troublemaker' # 捣蛋鬼  8
robber_role = 'robber'   # 强盗  6
witch_role = 'witch'     # 女巫  7
seer_role = 'seer'       # 预言家  5
minion_role = 'minion'   # 爪牙 3
werewolf_role = 'werewolf'   # 普通狼人 1
alphawolf_role = 'alphawolf' # 头狼 2
insomniac_role = 'insomniac' # 失眠者 9
drunk_role ='drunk'      # 酒鬼  10
mason_role ='mason'      # 守夜人  4
doppelganger_role ='doppelganger'    # 化身幽灵 0
hunter_role ='hunter'    # 猎人  -1




class _baseRole(metaclass=abc.ABCMeta):
    def __init__(self, role_name, action_num):
        self._role_name = role_name
        self._action_num = action_num
        self._game_message = []
        self.status = 0   ## 0 初始状态， 1:发动技能中,等待玩家操作  10:玩家操作完成  100:通知玩家操作结果
        # logger.info(f'init role {role_name}')
    def __str__(self):
        return self._role_name
    def to_dict(self):
        return {
        'role_name':self._role_name,
        'action_num':self._action_num,
        'game_message':[p.to_dict() for p in self._game_message],
        'status':self.status
    }

    @abc.abstractmethod
    def operate_end(self, player):
        pass

    @abc.abstractmethod
    def operate_msg(self, rmsg):
        pass 

    def operate_begin(self, player):
        pass
        

# 猎人  -1
class hunter(_baseRole):
    def __init__(self):
        super().__init__('hunter',-1)

    def operate_end(self, player):
        if self.status == 100:
            return
        room = player.room
        open_id = self._game_message[0].op_content['killed']
        room.players[open_id]._death = True
        room.role_to_player['hunter'][0].send_msg(msg.S_msg(0,"hunter", "operate_end", True))
        self.status = 100
    
    def operate_msg(self, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10     

    def operate_begin(self, player):
        if self.status < 1:
            player.send_self()
            self.status = 1
        

# 化身幽灵 0
class doppelganger(_baseRole):
    def __init__(self):
        super().__init__('doppelganger',0)
        self.copy_role = None
        self.special_role_name = {'alphawolf','seer','robber','witch','troublemaker','drunk'}

    def operate_end(self, player):
        if self.status == 100:
            return
        room = player.room
        if len(self._game_message) == 1:
            operate_back = self._game_message[0].op_content['operate_back']
            role_name = room.players[operate_back['open_id']]._roles[-1]._role_name
            obj = sys.modules[__name__]
            self.copy_role = getattr(obj, role_name)()

            room.role_to_player[self.copy_role._role_name].append(player)

            self.copy_role.operate_begin(player)
            if self.copy_role._role_name in self.special_role_name:
                self.status = 1
            else:
                self.status = 100
        elif len(self._game_message) == 2:
            self.copy_role.operate_msg(self._game_message[-1])
            self.copy_role.operate_end(player)
            self.status = 100
        

    def operate_msg(self, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            if len(self._game_message) >= 2:
                self.status = 10

    def operate_begin(self, player):
        if self.status < 1:
            player.send_self()
            self.status = 1
        

# 普通狼人 1
class werewolf(_baseRole):
    def __init__(self):
        super().__init__('werewolf',1)

    def operate_end(self, player):
        if self.status == 100:
            return
        room = player.room
        were_players = []
        if 'werewolf' in room.role_to_player:
            were_players.extend(room.role_to_player['werewolf'])
        if 'alphawolf' in room.role_to_player:
            were_players.extend(room.role_to_player['alphawolf'])
        data = [p.to_dict() for p in were_players]
        for wp in were_players:
            wp.send_msg(msg.S_msg(0,"werewolf", "operate_info", data))
        self.status = 100

    def operate_msg(self, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            player.send_self()
            self.status = 10

# 头狼 2
class alphawolf(_baseRole):
    def __init__(self):
        super().__init__('alphawolf',2)

    def operate_end(self, player):
        if self.status == 100:
            return
        room = player.room
        self.status = 100

    def operate_msg(self, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            player.send_self()
            self.status = 1
        

# 爪牙 3    
class minion(_baseRole):
    def __init__(self):
        super().__init__('minion',3)

    def operate_end(self, player):
        if self.status == 100:
            return
        room = player.room
        were_players = []
        if 'werewolf' in room.role_to_player:
            were_players.extend(room.role_to_player['werewolf'])
        if 'alphawolf' in room.role_to_player:
            were_players.extend(room.role_to_player['alphawolf'])
        data = [p.to_dict() for p in were_players]
        for en in room.role_to_player['minion']:
            en.send_msg(msg.S_msg(0,"minion", "operate_info", data))
        self.status = 100
        

    def operate_msg(self, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            player.send_self()
            self.status = 10
        

# 守夜人  4
class mason(_baseRole):
    def __init__(self):
        super().__init__('mason',4)

    def operate_end(self, player):
        if self.status == 100:
            return
        room = player.room
        mason_players = room.role_to_player['mason']
        data = [p.to_dict() for p in mason_players]
        for mp in mason_players:
            mp.send_msg(msg.S_msg(0,"mason", "operate_info", data))
        self.status = 100

    def operate_msg(self, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            player.send_self()
            self.status = 10
        

# 预言家  5
class seer(_baseRole):
    def __init__(self):
        super().__init__('seer',5)

    def operate_end(self, player):
        if self.status == 100:
            return
        room = player.room
        operate_back = self._game_message[0].op_content['operate_back']
        role = room.players[operate_back['open_id']]._roles[-1]
        room.role_to_player['seer'][0].send_msg(msg.S_msg(0,"seer", "operate_end", {operate_back['open_id']:role.to_dict()}))
        self.status = 100
        

    def operate_msg(self, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            player.send_self()
            self.status = 1
        

# 强盗  6
class robber(_baseRole):
    def __init__(self):
        super().__init__('robber',6)

    def operate_end(self, player):
        if self.status == 100:
            return
        room = player.room
        operate_back = self._game_message[0].op_content['operate_back']
        
        operate_player = room.players[operate_back['open_id']]
        room.role_to_player['robber'][0].send_msg(msg.S_msg(0,"robber", "operate_end", {operate_back['open_id']:operate_player.to_dict()}))
        
        # 交换身份
        robber_player = room.role_to_player['robber'][0]
        robber_player._roles.append(operate_player._roles[-1])
        operate_player._roles.append(robber_player._roles[-2])
        self.status = 100
        

    def operate_msg(self, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            player.send_self()
            self.status = 1
        

# 女巫  7    
class witch(_baseRole):
    def __init__(self):
        super().__init__('witch',7)

    def operate_end(self, player):
        if self.status == 100:
            return
        room = player.room
        self.status = 100

    def operate_msg(self, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            player.send_self()
            self.status = 1
        

# 捣蛋鬼  8    
class troublemaker(_baseRole):
    def __init__(self):
        super().__init__('troublemaker',8)

    def operate_end(self, player):
        if self.status == 100:
            return
        room = player.room
        operate_back = self._game_message[0].op_content['operate_back']
        
        player0 = room.players[operate_back['open_id'][0]]
        player1 = room.players[operate_back['open_id'][1]]
        
        # 交换身份
        player0._roles.append(player1._roles[-1])
        player1._roles.append(player0._roles[-2])
        self.status = 100
        

    def operate_msg(self, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            player.send_self()
            self.status = 1
        

# 失眠者 9    
class insomniac(_baseRole):
    def __init__(self):
        super().__init__('insomniac',9)
    
    def operate_end(self, player):
        if self.status == 100:
            return
        room = player.room
        for en in room.role_to_player['insomniac']:
            en.send_msg(msg.S_msg(0,"insomniac", "operate_info", en._roles[-1].to_dict()))
        self.status = 100

    def operate_msg(self, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            player.send_self()
            self.status = 10
        

# 酒鬼  10
class drunk(_baseRole):
    def __init__(self):
        super().__init__('drunk',10)
    
    def operate_end(self, player):
        if self.status == 100:
            return
        room = player.room
        operate_back = self._game_message[0].op_content['operate_back']
        role = room.left_role[operate_back['num']]
        room.role_to_player['drunk'][0]._roles.append(role)
        room.left_role[operate_back['num']] = room.role_to_player['drunk'][0]._roles[-2]
        self.status = 100
        

    def operate_msg(self, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            player.send_self()
            self.status = 1
        


if __name__ == '__main__':
    ss=  'drunk'
    obj = sys.modules[__name__]
    copy_role = getattr(obj, 'drunk')()
    print(copy_role._role_name)
