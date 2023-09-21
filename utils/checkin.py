import requests
from urllib.parse import quote

from config import Config
from notice import MsgSender
from passcheck import PassCheck

class Checkin:

    def __init__(self) -> None:
        self.config = Config()
        self.passCheck = PassCheck()

        self.users = self.config.load_users()
        pass

    # 签到领空间
    def checkAndSendMsg(self):
        for user in self.users:
            sender = MsgSender(user.get("token"))
            token = user['cookies']
            name = user['name']
            #获取识别并拼接好的captcha_pos
            captcha_pos = self.passCheck.get_captcha_pos(token)

            headers = {
                "cookie": f"wps_sid={token}",
                "content-type": "application/x-www-form-urlencoded",
                "accept": "*/*",
            }
            url = "https://vip.wps.cn/sign/v2"
            body = f"platform=8&captcha_pos={quote(captcha_pos)}&img_witdh=336&img_height=84"
            ret = requests.post(url=url, headers=headers, data=body).json()

            if ret['result'] == "ok":
                # send(f"{name}:签到成功")
                sender.message_notice(f"Wps→{name}:签到成功",True)
            elif ret["msg"] == "已完成签到" or ret['msg']=="10003":
                sender.message_notice(f"Wps→{name}:签到成功",False)