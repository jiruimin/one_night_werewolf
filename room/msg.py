
import json

class S_msg(object):
    def __init__(self, code, msg, op_type, data):
        self.code = code
        self.msg = msg
        self.op_type = op_type
        self.data = data

class R_msg(object):
    def __init__(self, recv_str):
        json_data = json.loads(recv_str)
        self.open_id = json_data['open_id']
        self.nickName = json_data['nickName']
        self.op_type = json_data['op_type']
        self.room_id = json_data['room_id']
        if 'op_content' in json_data:
            self.op_content = json_data['op_content']    

    def to_dict(self):
        return {
        'open_id':self.open_id,
        'nickName':self.nickName,
        'op_type':self.op_type,
        'room_id':self.room_id,
        'op_content':self.op_content
    }
if __name__ == '__main__':
    smsg1 = S_msg(0,'ooo', 'iii','')
    smsg2 = S_msg(0,'ooo', 'iii','')
    ll = []
    ll.append(smsg1)
    ll.append(smsg2)
    print(json.dumps(smsg1,default=lambda o: o.__dict__))
    print(json.dumps(ll,default=lambda o: o.__dict__))
    # print(smsg.to_json());