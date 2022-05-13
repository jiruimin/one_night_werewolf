
import json

class S_msg(object):
    def __init__(self, code, msg, msg_type, data):
        self.code = code
        self.msg = msg
        self.msg_type = msg_type
        self.op_type = ''
        self.data = data

class R_msg(object):
    def __init__(self, recv_str):
        json_data = json.loads(recv_str)
        self.openid = json_data['openid']
        self.nickName = json_data['nickName'] if('nickName' in json_data) else ""
        self.avatarUrl = json_data['avatarUrl'] if('avatarUrl' in json_data) else ""
        self.op_type = json_data['op_type']
        self.roomid = json_data['roomid'] if('roomid' in json_data) else ""
        if 'op_content' in json_data:
            self.op_content = json_data['op_content']    

    def to_dict(self):
        return {
        'openid':self.openid,
        'nickName':self.nickName,
        'op_type':self.op_type,
        'roomid':self.roomid,
        'op_content':self.op_content
    }
if __name__ == '__main__':
    smsg1 = S_msg(0,'ooo','iii','')
    smsg2 = S_msg(0,'ooo','iii','')
    smsg1.op_type = 'iiiiiiii'
    ll = []
    ll.append(smsg1)
    ll.append(smsg2)
    print(json.dumps(smsg1,default=lambda o: o.__dict__))
    print(json.dumps(ll,default=lambda o: o.__dict__))
    # print(smsg.to_json());