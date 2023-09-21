import json
import os

"""
这里是配置信息的类，方便解耦合。
其中USERS_DATA的内容格式为：
[
    {
        "channel":"notice_1", //此处是选择通知的通道（在下面notice_channel配置）,选填。
        "group":[
            {
                "id": 0,
                "name": "an",
                "cookies": "xxx",
            },...,
            {
                "id": 10x,
                "name": "anx",
                "cookies": "xxx",
            }
        ]
    },...,
    {
        "channel":"notice_x",
        "group":[
            {
                "id": 11x,
                "name": "an",
                "cookies": "xxx",
            },...,
            {
                "id": 20x,
                "name": "anx",
                "cookies": "xxx",
            }
        ]
    },
    {
        # 若没有通知需求，可空白。
        "notice_channels": {
            # 每个组中的通知方式选填，若没有则不通知。
            # notice_1 可自定义，上面notice字段引用正确即可。
            "notice_1": {
                "WECOM":{
                    "TYPE":"text(markdown)",
                    "SECRET":"xxx",
                    "ENTERPRISE_ID":"xxx",
                    "APP_ID":"xxx"
                },
                "WECOM_WEBHOOK":"xxx",
                "PUSHPLUS_TOKEN":"xxx",
            },
            "notice_x": {
                "WECOM":{
                    "TYPE":"text(markdown)",
                    "SECRET":"xxx",
                    "ENTERPRISE_ID":"xxx",
                    "APP_ID":"xxx"
                },
                "WECOM_WEBHOOK":"xxx",
                "PUSHPLUS_TOKEN":"xxx",
                "SERVER_SCKEY":"xxx",
                "BARK_DEVICEKEY":"xxx"
            }
        }
    }
]

USERS_CLOSERS为想关闭的用户，避免重复填写USERS_DATA，其格式如下:
{
    "pass_ids":[0,1...]
}
"""


class Config:

    def __init__(self) -> None:
        # 用户数据列表
        self.datas_str = os.getenv('USERS_DATA', '[]')

        # print(f'CLOSERS:{self.closers_str}and type{type(self.closers_str)}')

        # 书写检查
        assert self.datas_str != '[]' and len(
            self.datas_str) != 0, "Users data is empty!"

        self.datas: list[dict] = json.loads(self.datas_str)

    def load_users(self) -> list[dict]:
        users = list[dict]()

        for data in self.datas:
            group: list[dict] = data.get("group")
            chan_tokens = self.get_tokens_by_channel(data.get("channel"))
            if group != None:
                for user in group:
                    user["token"] = chan_tokens
                    users.append(user)
        return users

    def get_tokens_by_channel(self, name):
        channel = dict()

        for data in self.datas:
            channels = data.get("notice_channels")
            if channels != None:
                channel = channels.get(name)
        return channel