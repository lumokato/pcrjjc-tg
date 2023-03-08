from pcrclient import PCRClient, ApiException
from copy import deepcopy
from traceback import format_exc
import time
from os.path import dirname, join, exists
from json import load, dump
import logging
import csv
from wechat import send_wechat

with open('account.json', encoding='utf-8') as fp:
    jjc_account = load(fp)['jjc']

root = logging.getLogger()
root.setLevel(logging.INFO)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


bot_help = '''[竞技场绑定 chatid] 绑定竞技场排名变动推送，默认双场均启用，仅排名降低时推送

[竞技场查询 (chatid)] 查询竞技场简要信息
[停止竞技场订阅] 停止战斗竞技场排名变动推送
[停止公主竞技场订阅] 停止公主竞技场排名变动推送
[启用竞技场订阅] 启用战斗竞技场排名变动推送
[启用公主竞技场订阅] 启用公主竞技场排名变动推送
[删除竞技场订阅] 删除竞技场排名变动推送绑定
[竞技场订阅状态] 查看排名变动推送绑定状态
[详细查询 (chatid)] 查询详细状态'''


def send_jjchelp(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'{bot_help}')


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
client = PCRClient(jjc_account["viewer_id"])
client.login(jjc_account["uid"], jjc_account["access_key"])


def query(id: str):
    res = client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)
        })
    if 'user_info' not in res:
        client.login(jjc_account["uid"], jjc_account["access_key"])
        res = client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)})
    return res


def save_binds():
    with open(config, 'w') as fp:
        dump(root, fp, indent=4)


def on_arena_bind(update, context):
    global binds
    chatid = str(update.effective_chat.id)
    last = binds[chatid] if chatid in binds else None

    binds[chatid] = {
        'id': context.args[0],
        'chatid': chatid,
        'arena_on': last is None or last['arena_on'],
        'grand_arena_on': last is None or last['grand_arena_on'],
    }
    save_binds()
    context.bot.send_message(chat_id=update.effective_chat.id, text='竞技场绑定成功')


def on_query_arena(update, context):
    global binds
    try:
        id = context.args[0]
    except IndexError:
        chatid = str(update.effective_chat.id)
        if chatid not in binds:
            context.bot.send_message(chatid, '未绑定竞技场')
            return
        else:
            id = binds[chatid]['id']
    try:
        res = query(id)
        last_login_time = int(res['user_info']['last_login_time'])
        last_login_date = time.localtime(last_login_time)
        last_login_str = time.strftime('%Y-%m-%d %H:%M:%S', last_login_date)
        text = f'''昵称：{res['user_info']["user_name"]}
jjc：{res['user_info']["arena_rank"]}
pjjc：{res['user_info']["grand_arena_rank"]}
最后登录：{last_login_str}'''
        context.bot.send_message(update.effective_chat.id, text)
        # send_wechat(text)
    except ApiException as e:
        context.bot.send_message(update.effective_chat.id, f'查询出错，{e}')


def on_query_arena_all(update, context):
    global binds
    try:
        id = context.args[0]
    except IndexError:
        chatid = str(update.effective_chat.id)
        if chatid not in binds:
            context.bot.send_message(chatid, '未绑定竞技场')
            return
        else:
            id = binds[chatid]['id']
    try:
        res = query(id)
        arena_time = int(res['user_info']['arena_time'])
        arena_date = time.localtime(arena_time)
        arena_str = time.strftime('%Y-%m-%d', arena_date)

        grand_arena_time = int(res['user_info']['grand_arena_time'])
        grand_arena_date = time.localtime(grand_arena_time)
        grand_arena_str = time.strftime('%Y-%m-%d', grand_arena_date)

        last_login_time = int(res['user_info']['last_login_time'])
        last_login_date = time.localtime(last_login_time)
        last_login_str = time.strftime('%Y-%m-%d %H:%M:%S', last_login_date)
        text = f'''id：{res['user_info']["viewer_id"]}
昵称：{res['user_info']["user_name"]}
公会：{res["clan_name"]}
简介：{res['user_info']["user_comment"]}
最后登录：{last_login_str}
jjc：{res['user_info']["arena_rank"]}
pjjc：{res['user_info']["grand_arena_rank"]}
战力：{res['user_info']["total_power"]}
等级：{res['user_info']["team_level"]}
jjc场次：{res['user_info']["arena_group"]}
jjc创建日：{arena_str}
pjjc场次：{res['user_info']["grand_arena_group"]}
pjjc创建日：{grand_arena_str}
角色数：{res['user_info']["unit_num"]}
'''
        context.bot.send_message(update.effective_chat.id, text)
    except ApiException as e:
        context.bot.send_message(update.effective_chat.id, f'查询出错，{e}')


def change_arena_sub(update, context):
    global binds
    key = 'arena_on' if context.args[0] == 'jjc' else 'grand_arena_on'
    chatid = str(update.effective_chat.id)
    if chatid not in binds:
        context.bot.send_message(chatid, '未绑定竞技场')
    else:
        binds[chatid][key] = context.args[1] == 'on'
        save_binds()
        context.bot.send_message(chatid, '修改成功')


def delete_arena_sub(update, context):
    global binds
    chatid = str(update.effective_chat.id)
    if chatid not in binds:
        context.bot.send_message(chatid, '未绑定竞技场')
        return
    binds.pop(chatid)
    save_binds()
    context.bot.send_message(chatid, '删除竞技场订阅成功')


def send_arena_sub_status(update, context):
    global binds
    chatid = str(update.effective_chat.id)
    if chatid not in binds:
        context.bot.send_message(chatid, '未绑定竞技场')
    else:
        info = binds[chatid]
        context.bot.send_message(chatid, f'''
    当前竞技场绑定ID：{info['id']}
    竞技场订阅：{'开启' if info['arena_on'] else '关闭'}
    公主竞技场订阅：{'开启' if info['grand_arena_on'] else '关闭'}''')


def on_arena_schedule(context):
    time0 = time.time()
    global cache, binds
    bind_cache = {}
    bind_cache = deepcopy(binds)
    t = time.localtime()
    if (t.tm_hour, t.tm_min) in [(14, 58), (14,59)]:
        loop = 1
    else:
        loop = 0
    while time.time() - time0 < 29:
        for user in bind_cache:
            info = bind_cache[user]
            try:
                logger.info(f'querying {info["id"]} for {info["chatid"]}')
                res = query(info['id'])
                res = (res['user_info']['arena_rank'], res['user_info']['grand_arena_rank'])
                if user not in cache:
                    cache[user] = res
                    continue
                last = cache[user]
                cache[user] = res

                if res[0] > last[0] and info['arena_on']:
                    bot_text = f'jjc：{last[0]}->{res[0]} ▼{res[0]-last[0]}'
                    context.bot.send_message(chat_id=int(info['chatid']), text=bot_text)
                    # 添加企业微信提醒
                    send_wechat(bot_text)

                if res[1] > last[1] and info['grand_arena_on']:
                    bot_text = f'pjjc：{last[1]}->{res[1]} ▼{res[1]-last[1]}'
                    context.bot.send_message(chat_id=int(info['chatid']), text=bot_text)
                    # 添加企业微信提醒
                    send_wechat(bot_text)
            except ApiException as e:
                logger.info(f'对{info["id"]}的检查出错\n{format_exc()}')
                if e.code == 6:
                    binds.pop(user)
                    save_binds()
            except Exception:
                logger.info(f'对{info["id"]}的检查出错\n{format_exc()}')
        # time1 = time.time()
        # print(time1 - time0)
        if not loop:
            break
        time.sleep(2)

def start_schedule(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text='开启定时')
    update.job_queue.run_repeating()


def query_page(page: int):
    temp = client.callapi('clan_battle/period_ranking', {'clan_id': 53, 'clan_battle_id': -1, 'period': -1, 'month': 0, 'page': page, 'is_my_clan': 0, 'is_first': 1})
    if 'period_ranking' not in temp:
        client.login(jjc_account["uid"], jjc_account["access_key"])
        temp = client.callapi('clan_battle/period_ranking', {'clan_id': 53, 'clan_battle_id': -1, 'period': -1, 'month': 0, 'page': page, 'is_my_clan': 0, 'is_first': 1})
    time.sleep(1)
    return temp['period_ranking']


def damage_percentage(update, context):
    data = {}
    with open('./data/damage.csv', 'r', encoding="utf8") as f:
        for line in csv.reader(f):
            try:
                data[int(line[1])] = line
            except ValueError:
                continue
    # data = pd.read_csv('./data/damage.csv')
    text = '本日推测进度：' + '\n'
    for clan in query_page(0):
        damage_now = clan['damage']
        grade_rank = clan['grade_rank']
        damage_yesterday = int(data[grade_rank][-1])
        damage_all = 0
        for i in range(4, len(data[grade_rank])):
            damage_all += int(data[grade_rank][i])
        damage_today = damage_now - damage_all
        text += str(clan['rank']) + ': ' + clan['clan_name'] + '  ' + '{:.0%}'.format(damage_today/damage_yesterday) + '\n'
    chatid = str(update.effective_chat.id)
    context.bot.send_message(chatid, text)


def damage_stage(context):
    stage_data = {}
    try:
        with open('./data/stage.csv', 'r', encoding="utf8") as f:
            for line in csv.reader(f):
                try:
                    stage_data[int(line[1])] = line
                except ValueError:
                    break
    except FileNotFoundError:
        print('不存在文件')
    for i in range(5):
        for clan in query_page(i):
            damage_now = clan['damage']
            grade_rank = clan['grade_rank']
            if grade_rank in stage_data.keys():
                stage_data[grade_rank].append(str(damage_now))
            else:
                stage_data[grade_rank] = [str(clan['rank']), str(clan['grade_rank']), clan['clan_name'], clan['leader_name'], str(clan['damage'])]
    with open('./data/stage.csv', 'w', encoding="utf8") as f:
        for clan_rank in stage_data.keys():
            f.write(','.join(stage_data[clan_rank])[:-1]+'\n')
        f.close()


def damage_percentage_stage(update, context):
    data = {}
    with open('./data/damage.csv', 'r', encoding="utf8") as f:
        for line in csv.reader(f):
            try:
                data[int(line[1])] = line
            except ValueError:
                continue
    stage_data = {}
    with open('./data/stage.csv', 'r', encoding="utf8") as f:
        for line in csv.reader(f):
            try:
                stage_data[int(line[1])] = line
            except ValueError:
                break
    # data = pd.read_csv('./data/damage.csv')
    text = '本日推测进度/上小时进度' + '\n'
    for clan in query_page(0):
        damage_now = clan['damage']
        grade_rank = clan['grade_rank']
        damage_yesterday = int(data[grade_rank][-1])
        damage_all = 0
        for i in range(4, len(data[grade_rank])):
            damage_all += int(data[grade_rank][i])
        damage_today = damage_now - damage_all
        try:
            damage_stage = int(stage_data[grade_rank][-1]) - int(stage_data[grade_rank][-3])
        except Exception:
            damage_stage = 0
        text += str(clan['rank']) + ': ' + clan['clan_name'] + '  ' + '{:.0%}'.format(damage_today/damage_yesterday) + '  ' + '{:.2%}'.format(10*damage_stage/damage_yesterday) + '\n'
    chatid = str(update.effective_chat.id)
    context.bot.send_message(chatid, text)


if __name__ == "__main__":
    damage_stage(0)
