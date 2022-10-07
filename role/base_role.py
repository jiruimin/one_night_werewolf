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
        self.status = 0   ## 0 初始状态， 1:发动技能中,等待玩家操作  10:玩家操作完成  20:通知玩家操作结果 100:结束
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
    def operate_msg(self, player, rmsg):
        pass 
    @abc.abstractmethod
    def operate_begin(self, player):
        pass
        

# 猎人  -1
class Hunter(_baseRole):
    def __init__(self):
        super().__init__('hunter',-1)

    def operate_end(self, player):
        if self.status >= 20 or self.status < 10:
            return
        room = player.room
        openid = self._game_message[0].op_content['operate_back']['openid']
        room.players[openid]._death = True
        self.status = 20
        room.game_result()
    
    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10     

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 1
            player.send_self()
    

# 化身幽灵 0
class Doppelganger(_baseRole):
    def __init__(self):
        super().__init__('doppelganger',0)
        self.copy_role = None
        self.special_role_name = {'alphawolf','seer','robber','witch','troublemaker','drunk'}

    def to_dict(self):
        return {
            'role_name':self._role_name,
            'action_num':self._action_num,
            'game_message':[p.to_dict() for p in self._game_message],
            'status':self.status,
            'copy_role':None if self.copy_role is None else self.copy_role.to_dict()
        }
    def operate_end(self, player):
        if self.status == 20:
            return
        room = player.room
        if len(self._game_message) == 1:
            operate_back = self._game_message[0].op_content['operate_back']
            role_name = room.players[operate_back['openid']]._roles[-1]._role_name
            obj = sys.modules[__name__]
            self.copy_role = getattr(obj, role_name.capitalize())()
            room.role_to_player[self.copy_role._role_name].append(player)

            self.copy_role.operate_begin(player)
            if self.copy_role._role_name in self.special_role_name:
                self.status = 1
            else:
                self.status = 20
        elif len(self._game_message) == 2:
            self.copy_role.operate_msg(player, self._game_message[-1])
            self.copy_role.operate_end(player)
            self.status = 20
        

    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            if len(self._game_message) >= 2:
                self.status = 10
            else:
                self.operate_end(player)

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 1
            player.send_self()
        

# 普通狼人 1
class Werewolf(_baseRole):
    def __init__(self):
        super().__init__('werewolf',1)

    def operate_end(self, player):
        if self.status == 20:
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
        

    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self.status = 10   
            self._game_message.append(rmsg)
            

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 10
            player.send_self()
            

# 头狼 2
class Alphawolf(_baseRole):
    def __init__(self):
        super().__init__('alphawolf',2)

    def operate_end(self, player):
        if self.status == 20:
            return
        self.status = 20

    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 1
            player.send_self()
        

# 爪牙 3    
class Minion(_baseRole):
    def __init__(self):
        super().__init__('minion',3)

    def operate_end(self, player):
        if self.status == 20:
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
        self.status = 20
        

    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 10
            player.send_self()
        

# 守夜人  4
class Mason(_baseRole):
    def __init__(self):
        super().__init__('mason',4)

    def operate_end(self, player):
        if self.status == 20:
            return
        room = player.room
        mason_players = room.role_to_player['mason']
        data = [p.to_dict() for p in mason_players]
        for mp in mason_players:
            mp.send_msg(msg.S_msg(0,"mason", "operate_info", data))
        self.status = 20

    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 10
            player.send_self()
        

# 预言家  5
class Seer(_baseRole):
    def __init__(self):
        super().__init__('seer',5)

    def operate_end(self, player):
        if self.status == 20:
            return
        room = player.room
        operate_back = self._game_message[0].op_content['operate_back']
        if('openid' in operate_back):
            pl = room.players[operate_back['openid']]
            player.send_msg(msg.S_msg(0,"seer", "operate_end", {pl.nickName:pl._roles[-1].to_dict()}))
        elif('card' in operate_back):
            card = operate_back['card']
            content = {"0":room.left_role[card[0]].to_dict(), "1":room.left_role[card[1]].to_dict()}
            player.send_msg(msg.S_msg(0,"seer", "operate_end", content))
        self.status = 20
        

    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 1
            player.send_self()
        

# 强盗  6
class Robber(_baseRole):
    def __init__(self):
        super().__init__('robber',6)

    def operate_end(self, player):
        if self.status == 20:
            return
        room = player.room
        operate_back = self._game_message[0].op_content['operate_back']
        
        operate_player = room.players[operate_back['openid']]
        player.send_msg(msg.S_msg(0,"robber", "operate_end", {operate_back['openid']:operate_player.to_dict()}))
        
        # 交换身份
        player._roles.append(operate_player._roles[-1])
        operate_player._roles.append(player._roles[-2])
        self.status = 20
        

    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 1
            player.send_self()
        

# 女巫  7    
class Witch(_baseRole):
    def __init__(self):
        super().__init__('witch',7)

    def operate_end(self, player):
        if self.status == 20:
            return
        self.status = 20

    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 1
            player.send_self()
        

# 捣蛋鬼  8    
class Troublemaker(_baseRole):
    def __init__(self):
        super().__init__('troublemaker',8)

    def operate_end(self, player):
        if self.status == 20:
            return
        room = player.room
        operate_back = self._game_message[0].op_content['operate_back']
        
        player0 = room.players[operate_back['openid'][0]]
        player1 = room.players[operate_back['openid'][1]]
        
        # 交换身份
        player0._roles.append(player1._roles[-1])
        player1._roles.append(player0._roles[-2])
        self.status = 20
        

    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 1
            player.send_self()
        

# 失眠者 9    
class Insomniac(_baseRole):
    def __init__(self):
        super().__init__('insomniac',9)
    
    def operate_end(self, player):
        if self.status == 20:
            return
        room = player.room
        for en in room.role_to_player['insomniac']:
            en.send_msg(msg.S_msg(0,"insomniac", "operate_info", en._roles[-1].to_dict()))
        self.status = 20

    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 10
            player.send_self()
        

# 酒鬼  10
class Drunk(_baseRole):
    def __init__(self):
        super().__init__('drunk',10)
    
    def operate_end(self, player):
        if self.status == 20:
            return
        room = player.room
        operate_back = self._game_message[0].op_content['operate_back']
        role = room.left_role[int(operate_back['card'])]
        player._roles.append(role)
        room.left_role[int(operate_back['card'])] = player._roles[-2]
        self.status = 20
        

    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 1
            player.send_self()
        
class Villager(_baseRole):
    def __init__(self):
        super().__init__('drunk',10)
    
    def operate_end(self, player):
        self.status = 20

    def operate_msg(self, player, rmsg):
        if self.status < 10:
            self._game_message.append(rmsg)
            self.status = 10   

    def operate_begin(self, player):
        if self.status < 1:
            self.status = 10
            player.send_self()



if __name__ == '__main__':
    ss=  'drunk'
    obj = sys.modules[__name__]
    copy_role = getattr(obj, 'drunk')()
    print(copy_role._role_name)
