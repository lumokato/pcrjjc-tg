import requests
from requests import HTTPError
from six import string_types
import config as cg


def send(bot_key, msg_type, **body):
    raise_exception = body.pop('raise_exception', True)
    if bot_key is None or not isinstance(bot_key, string_types) or len(body) == 0:
        raise ValueError()
    if not bot_key.startswith('https://'):
        bot_key = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}'.format(key=bot_key)
    r = requests.post(bot_key, json={"msgtype": msg_type, msg_type: body})
    if r.status_code != 200:
        exception = HTTPError('access WeGroupChatBot proxy is error,please check key!', response=r)
    else:
        response_data = r.json()
        if response_data['errcode'] == 0:
            return True
        exception = HTTPError(response_data['errmsg'], response=r, )
    if raise_exception and exception is not None:
        raise exception
    return False


class WeGroupChatBot(object):
    """
        企业微信群机器人接口
    """

    def __init__(self, bot_key):
        """
            初始化群机器人
        :param bot_key: 机器人 Webhook url的key参数或webhook的url
        """
        super(WeGroupChatBot, self).__init__()
        self.bot_key = bot_key

    def send_text(self, content, mentioned_list=None, mentioned_mobile_list=None):
        """
            发送纯文本消息，支持相关人提醒功能
        :param content:  发送的文本
        :param mentioned_list:  userid的列表，提醒群中的指定成员(@某个成员)，
                @all表示提醒所有人，如果开发者获取不到userid，可以使用mentioned_mobile_list
        :param mentioned_mobile_list: 手机号列表，提醒手机号对应的群成员(@某个成员)，@all表示提醒所有人
        :return:
        """
        return send(self.bot_key, 'text', content=content,
                    mentioned_list=mentioned_list,
                    mentioned_mobile_list=mentioned_mobile_list
                    )


if __name__ == '__main__':
    bot = WeGroupChatBot(cg.wechat_bot)
    assert bot.send_text('hello!')
