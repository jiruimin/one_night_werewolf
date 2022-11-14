
git add . && git commit -m "uuuuu" && git push origin master
git fetch --all && git reset --hard origin/master && git pull origin master


{"code": 0, "msg": "创建房间成功", "op_type": "info", "op_type": "info", "data": {"roomid": "24d1607d-4c6f-552b-8063-ee861f2bd8ed"}}

服务端发送消息说明：
op_type：
    info            所有玩家【通知类】消息，提示内容msg字段
    player_info     指定玩家初始身份【通知类/交互类】消息，具体内容data
    game_info       所有玩家游戏【通知类】消息，具体内容data
    operate_info    指定玩家技能【通知类】消息，具体内容data
    operate_end     指定玩家技能操作完成【通知类】消息，具体内容data
    wait_back       特殊【交互类】消息（目前：猎人技能发动使用），具体内容data


服务端接受消息说明：
