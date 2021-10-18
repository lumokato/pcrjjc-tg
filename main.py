from telegram.ext import Updater, CommandHandler
# import logging
import account as account
import time
# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
from telegram.ext import Updater, CommandHandler
REQUEST_KWARGS = {
    # "USERNAME:PASSWORD@" is optional, if you need authentication:
    # 'proxy_url': 'http://127.0.0.1:10809/',
}

bot = Updater(token='2096122895:AAEZstwii4QrlrIK8HvHAey36VTNDebVEfk', request_kwargs=REQUEST_KWARGS, use_context=True)

dispatcher = bot.dispatcher
from pcrclient import pcrclient, ApiException

def query(client, id: str):
    res = client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)
        })
    if 'user_info' not in res:
        client.login(account.uid, account.access_key)
        res = client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)})
    return res


def start(update, context):
    client = pcrclient(account.viewer_id)
    client.login(account.uid, account.access_key)
    res = query(client,"1193285189140")

    last_login_time = int(res['user_info']['last_login_time'])
    last_login_date = time.localtime(last_login_time)
    last_login_str = time.strftime('%Y-%m-%d %H:%M:%S',last_login_date)

    text = f'''昵称：{res['user_info']["user_name"]}
jjc：{res['user_info']["arena_rank"]}
pjjc：{res['user_info']["grand_arena_rank"]}
最后登录：{last_login_str}'''
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

bot.start_polling()
