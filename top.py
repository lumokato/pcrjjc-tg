from pcrclient import pcrclient, ApiException
import config as cg
import time
from os.path import dirname, join, exists
from json import load, dump
from copy import deepcopy


curpath = dirname(__file__)
config = join(curpath, 'binds.json')
root = {
    'arena_bind': {}
}

if exists(config):
    with open(config) as fp:
        root = load(fp)

binds = root['arena_bind']

cache = {}


def query(client, id: str):
    res = client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)
        })
    if 'user_info' not in res:
        client.login(cg.uid, cg.access_key)
        res = client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)})
    return res


def query_ranking(client):
    res = client.callapi('/arena/ranking', {'limit': 20, 'page': 1})
    ranking_dict = {}
    if 'ranking' in res:
        for user in res['ranking']:
            ranking_dict[user['viewer_id']] = user['rank']
    return ranking_dict


def query_pranking(client):
    res = client.callapi('/grand_arena/ranking', {'limit': 20, 'page': 1})
    ranking_dict = {}
    if 'ranking' in res:
        for user in res['ranking']:
            ranking_dict[user['viewer_id']] = user['rank']
    return ranking_dict


def on_query_atop(update, context):
    # chatid = str(update.effective_chat.id)
    client = pcrclient(cg.avid)
    client.login(cg.auid, cg.access_key)
    try:
        top_dict = query_ranking(client)
        last10 = []
        last30 = []
        last60 = []
        for top in top_dict.keys():
            res = query(client, int(top))
            last_login_time = int(res['user_info']['last_login_time'])
            login_from_now = int(time.time()) - last_login_time
            if login_from_now < 600:
                last10.append(str(top_dict[top]) + '-' + res['user_info']["user_name"])
            elif login_from_now < 1800:
                last30.append(str(top_dict[top]) + '-' + res['user_info']["user_name"])
            elif login_from_now < 3600:
                last60.append(str(top_dict[top]) + '-' + res['user_info']["user_name"])
        text = f'''竞技场前20名
    最近10分钟上线：{'，'.join(last10)}
    最近30分钟上线：{'，'.join(last30)}
    最近60分钟上线：{'，'.join(last60)}'''
        context.bot.send_message(update.effective_chat.id, text)
    except ApiException as e:
        context.bot.send_message(update.effective_chat.id, f'查询出错，{e}')


def on_query_ptop(update=None, context=None):
    if update:
        chat_id = str(update.effective_chat.id)
    else:
        global cache, binds
        bind_cache = {}
        bind_cache = deepcopy(binds)
        for user in bind_cache:
            info = bind_cache[user]
            chat_id = int(info['chatid'])
    client = pcrclient(cg.pvid)
    client.login(cg.puid, cg.access_key)

    try:
        top_dict = query_pranking(client)
        last10 = []
        last30 = []
        last60 = []
        for top in top_dict.keys():
            res = query(client, int(top))
            last_login_time = int(res['user_info']['last_login_time'])
            login_from_now = int(time.time()) - last_login_time

            if login_from_now < 600:
                last10.append(str(top_dict[top]) + '-' + res['user_info']["user_name"])
            elif login_from_now < 1800:
                last30.append(str(top_dict[top]) + '-' + res['user_info']["user_name"])
            elif login_from_now < 3600:
                last60.append(str(top_dict[top]) + '-' + res['user_info']["user_name"])
        bot_text = f'''公主竞技场前20名
    最近10分钟上线：{'，'.join(last10)}
    最近30分钟上线：{'，'.join(last30)}
    最近60分钟上线：{'，'.join(last60)}'''
        context.bot.send_message(chat_id, bot_text)
        # context.bot.send_message(update.effective_chat.id, bot_text)
    except ApiException as e:
        context.bot.send_message(update.effective_chat.id, f'查询出错，{e}')


if __name__ == "__main__":
    on_query_ptop()