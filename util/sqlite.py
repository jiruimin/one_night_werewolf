import sqlite3

__user_info_table_name__ = 'user_info'
__room_record_table_name__ = 'room_record'

class SqliteUtil(object):
    """docstring for """

    def __init__(self):
        # global __table_name
        self.__functionDict = {'default': lambda x: 0}
        self._conn = sqlite3.connect('./database')
        self._cursor = self._conn.cursor()
        self._cursor.execute(f"CREATE TABLE IF NOT EXISTS {__user_info_table_name__} \
                                ('openid' TEXT PRIMARY KEY,'nickName' TEXT, 'avatarUrl' TEXT, 'create_time' TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                                'villager_win' INTEGER DEFAULT 0, 'werewolf_win' INTEGER DEFAULT 0,  'villager_lose' INTEGER DEFAULT 0, \
                                'werewolf_lose' INTEGER DEFAULT 0,'game_num' INTEGER DEFAULT 0);")
        self._cursor.execute(f"CREATE TABLE IF NOT EXISTS {__room_record_table_name__} \
                                ('id' INTEGER  PRIMARY KEY  AUTOINCREMENT,'roles' TEXT, 'players' TEXT, 'create_time' TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\
                                'status' INTEGER DEFAULT 0, 'detail' TEXT, 'game' TEXT, 'room_owner' TEXT);")


    def insert_user(self, user_info:dict):
        user = self.select_user(user_info['openid'])
        if user is not None and user_info['nickName'] != '' and user_info['avatarUrl'] != '':
            self._cursor.execute(f"update {__user_info_table_name__} set nickName = '{user_info['nickName']}', avatarUrl = '{user_info['avatarUrl']}' \
                            where openid = '{user_info['openid']}'")
        else:
            self._cursor.execute(f"INSERT INTO {__user_info_table_name__} ('openid', 'nickName', 'avatarUrl') VALUES(?, ?, ?)",
                               (user_info['openid'], user_info['nickName'], user_info['avatarUrl']))
        self._conn.commit()

    def select_user(self, openid:str)->dict:
        self._cursor.execute(f"select * from {__user_info_table_name__} where openid = '{openid}'")
        ulist = self._cursor.fetchone()
        if ulist is None:
            return None
        return {"openid":ulist[0],"nickName":ulist[1],"avatarUrl":ulist[2],"create_time":ulist[3],"villager_win":ulist[4],
                "werewolf_win":ulist[5],"villager_lose":ulist[6],"werewolf_lose":ulist[7],"game_num":ulist[8]}


    def create_room(self, room_info:dict):
        self._cursor.execute(f"INSERT INTO {__room_record_table_name__} ('roles', 'status', 'game', 'room_owner') VALUES(?, ?, ?, ?)",
                               (room_info['roles'], 0, 'one_night_werewolf', room_info['room_owner']))
        self._conn.commit()
        return self._cursor.lastrowid

    def start_room(self, room_info:dict):
        self._cursor.execute(f"UPDATE {__room_record_table_name__} SET players = '{room_info['players']}', status = 1 where id = {room_info['roomid']}")
        self._conn.commit()

if __name__ == "__main__":
    sqliteUtil = SqliteUtil()
    sqliteUtil.add_user({'openid':"jirm", 'nickName':"jirm", 'avatarUrl':"jirm"})
    user_info = sqliteUtil.select_user('jirm')

    roomid = sqliteUtil.create_room({'roles':"roles",'room_owner':'jirm'})
    print(roomid)
    sqliteUtil.start_room({'players':"jirm,jirm2,jirm3","roomid":roomid})
    print("kkk")
                              

