from pcrclient import pcrclient
import config as cg
from asyncio import Lock
import time
from telegram.ext.dispatcher import run_async

bot_help = '''[竞技场绑定 uid] 绑定竞技场排名变动推送，默认双场均启用，仅排名降低时推送

[竞技场查询 (uid)] 查询竞技场简要信息
[停止竞技场订阅] 停止战斗竞技场排名变动推送
[停止公主竞技场订阅] 停止公主竞技场排名变动推送
[启用竞技场订阅] 启用战斗竞技场排名变动推送
[启用公主竞技场订阅] 启用公主竞技场排名变动推送
[删除竞技场订阅] 删除竞技场排名变动推送绑定
[竞技场订阅状态] 查看排名变动推送绑定状态
[详细查询 (uid)] 查询详细状态'''


def send_jjchelp(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{bot_help}')


_config = None
binds = None

qlck = Lock()
lck = Lock()
cache = {}
client = pcrclient(cg.viewer_id)
client.login(cg.uid, cg.access_key)


def query(id: str):
    res = client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)
        })
    if 'user_info' not in res:
        client.login(cg.uid, cg.access_key)
        res = client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)})
    return res


def start(update, context):
    res = query(context.args[0])

    last_login_time = int(res['user_info']['last_login_time'])
    last_login_date = time.localtime(last_login_time)
    last_login_str = time.strftime('%Y-%m-%d %H:%M:%S', last_login_date)

    text = f'''昵称：{res['user_info']["user_name"]}
                jjc：{res['user_info']["arena_rank"]}
                pjjc：{res['user_info']["grand_arena_rank"]}
                最后登录：{last_login_str}'''
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
