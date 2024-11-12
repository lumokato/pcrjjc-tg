from pcrclient import pcrclient, ApiException
import time
from os.path import dirname, join, exists
from json import load, dump
from copy import deepcopy
from wechat import send_wechat
import logging

with open('account.json', encoding='utf-8') as fp:
    load_data = load(fp)
    grand_account = load_data['grand']
    arena_account = load_data['arena']
    wechat_bot = load_data['wechat']


root = logging.getLogger()
root.setLevel(logging.INFO)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


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

# pclient = pcrclient(grand_account["uid"])

async def query(client, id: str):
    res = await client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)
        })
    if 'user_info' not in res:
        await client.login()
        res = await client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)})
    return res


async def query_ranking(client, arena_or_grand):
    url = '/arena/ranking' if arena_or_grand == 'arena' else '/grand_arena/ranking'

    res = await client.callapi(url, {'limit': 20, 'page': 1})
    if 'ranking' not in res:
        await client.login()
        res = await client.callapi(url, {'limit': 20, 'page': 1})
    ranking_dict = {}
    if 'ranking' in res:
        for user in res['ranking']:
            ranking_dict[user['viewer_id']] = user['rank']
    return ranking_dict


async def on_query_ptop(update=None, context=None):
    if update:
        chat_id = str(update.effective_chat.id)
    else:
        global cache, binds
        bind_cache = {}
        bind_cache = deepcopy(binds)
        for user in bind_cache:
            info = bind_cache[user]
            chat_id = int(info['chatid'])

    pclient = pcrclient(grand_account["uid"])
    await pclient.login()

    try:
        top_dict = await query_ranking(pclient, 'grand')
        last10 = []
        last30 = []
        last60 = []
        for top in top_dict.keys():
            res = await query(pclient, int(top))
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
        await context.bot.send_message(chat_id, bot_text)
        # context.bot.send_message(update.effective_chat.id, bot_text)
    except ApiException as e:
        await context.bot.send_message(update.effective_chat.id, f'查询出错，{e}')


async def on_query_plist(update, context):
    pclient = pcrclient(grand_account["uid"])
    await pclient.login()
    try:
        top_dict = await query_ranking(pclient, 'grand')

        res = await pclient.callapi('/grand_arena/ranking', {'limit': 20, 'page': 1})
        if 'ranking' not in res:
            await pclient.login()
            res = await pclient.callapi('/grand_arena/ranking', {'limit': 20, 'page': 1})
        ranking_name = []

        for top in top_dict.keys():
            res_user = await query(pclient, int(top))
            ranking_name.append(str(top_dict[top]) + '-' + res_user['user_info']["user_name"])
        text = f'''公主竞技场前20名:{', '.join(ranking_name)}'''
        await context.bot.send_message(update.effective_chat.id, text)
        # send_wechat(text, wechat_bot["bot1"])
    except ApiException as e:
        await context.bot.send_message(update.effective_chat.id, f'查询出错，{e}')


async def on_query_alist(update, context):

    aclient = pcrclient(arena_account["uid"])
    await aclient.login()
    try:
        res = await aclient.callapi('/arena/ranking', {'limit': 20, 'page': 1})
        if 'ranking' not in res:
            await aclient.login()
            res = await aclient.callapi('/arena/ranking', {'limit': 20, 'page': 1})
        ranking_name = []
        if 'ranking' in res:
            for user in res['ranking']:
                res_user = await aclient.callapi('/profile/get_profile', {'target_viewer_id': int(user['viewer_id'])})
                ranking_name.append(str(user['rank']) + '-' + res_user['user_info']["user_name"])
            text = f'''竞技场前20名:{', '.join(ranking_name)}'''
        await context.bot.send_message(update.effective_chat.id, text)
        # send_wechat(text, wechat_bot["bot1"])
    except ApiException as e:
        await context.bot.send_message(update.effective_chat.id, f'查询出错，{e}')


# def on_query_pwild():
#     try:
#         with open('wild.json', encoding='utf-8') as fp:
#             group_user = load(fp)
#         logger.info('querying grand arena top')

#         res = pclient.callapi('/grand_arena/ranking', {'limit': 20, 'page': 1})
#         if 'ranking' not in res:
#             pclient.login(grand_account["uid"], grand_account["access_key"])
#             res = pclient.callapi('/grand_arena/ranking', {'limit': 20, 'page': 1})
#         user_wild = []
#         wild_flag = 0
#         write_flag = 0
#         if 'ranking' in res:
#             for user in res['ranking']:
#                 if str(user['viewer_id']) not in group_user["group"] and user['rank'] < 5:
#                     wild_flag = 1
#                     if str(user['viewer_id']) not in group_user["wild"]:
#                         write_flag = 1
#                         group_user['wild'][str(user['viewer_id'])] = user['user_name']
#                         user_wild.append(str(user['rank']) + '-' + user['user_name'])
#             if not wild_flag and group_user["wild"]:
#                 write_flag = 1
#                 group_user["wild"] = {}
#         if write_flag:
#             with open('wild.json', 'w', encoding='utf-8') as fp:
#                 dump(group_user, fp, indent=4, ensure_ascii=False)
#         if user_wild:
#             bot_text = f'''注意:{', '.join(user_wild)}'''
#             # 企业微信提醒
#             send_wechat(bot_text, wechat_bot["bot2"])
#     except Exception:
#         logger.info('查询出错\n')


# if __name__ == "__main__":
#     on_query_pwild()
