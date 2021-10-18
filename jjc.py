from json import load, dump
from nonebot import get_bot, on_command
from pcrclient import pcrclient, ApiException
from asyncio import Lock
from os.path import dirname, join, exists
from copy import deepcopy
from traceback import format_exc
from safeservice import SafeService
import account as account
import time
from bot import bot
bot_help = '''[竞技场绑定 uid] 绑定竞技场排名变动推送，默认双场均启用，仅排名降低时推送

[竞技场查询 (uid)] 查询竞技场简要信息
[停止竞技场订阅] 停止战斗竞技场排名变动推送
[停止公主竞技场订阅] 停止公主竞技场排名变动推送
[启用竞技场订阅] 启用战斗竞技场排名变动推送
[启用公主竞技场订阅] 启用公主竞技场排名变动推送
[删除竞技场订阅] 删除竞技场排名变动推送绑定
[竞技场订阅状态] 查看排名变动推送绑定状态
[详细查询 (uid)] 查询详细状态'''

# bot = SafeService('竞技场推送',help_=bot_help, bundle='pcr查询')

@bot.CommandHandler('竞技场帮助', only_to_me=False)
async def send_jjchelp(bot, *args):
    self_ids = bot._wsr_api_clients.keys()
    for sid in self_ids:
        gl = await bot.get_group_list(self_id=sid)
        msg = f"本Bot目前服务群数目{len(gl)}"
    await bot.send(args, f'{bot_help}\n{msg}')

curpath = dirname(__file__)
config = join(curpath, 'binds.json')
root = {
    'arena_bind': {}
}

cache = {}
client = pcrclient(account.viewer_id)
client.login(account.uid, account.access_key)

lck = Lock()

if exists(config):
    with open(config) as fp:
        root = load(fp)

binds = root['arena_bind']


qlck = Lock()

async def query(id: str):
    async with qlck:
        res = client.callapi('/profile/get_profile', {
                'target_viewer_id': int(id)
            })
        if 'user_info' not in res:
            client.login(account.uid, account.access_key)
            res = client.callapi('/profile/get_profile', {
                'target_viewer_id': int(id)})
        return res

def save_binds():
    with open(config, 'w') as fp:
        dump(root, fp, indent=4)

@bot.CommandHandler(r'^竞技场绑定 ?(\d{13})$')
async def on_arena_bind(bot, *args):
    global binds, lck

    async with lck:
        uid = str(args['user_id'])
        last = binds[uid] if uid in binds else None

        binds[uid] = {
            'id': args['match'].group(1),
            'uid': uid,
            'gid': str(args['group_id']),
            'arena_on': last is None or last['arena_on'],
            'grand_arena_on': last is None or last['grand_arena_on'],
        }
        save_binds()

    await bot.finish(args, '竞技场绑定成功', at_sender=True)

@bot.CommandHandler(r'^竞技场查询 ?(\d{13})?$')
async def on_query_arena(bot, *args):
    global binds, lck

    robj = args['match']
    id = robj.group(1)

    async with lck:
        if id == None:
            uid = str(args['user_id'])
            if not uid in binds:
                await bot.finish(args, '您还未绑定竞技场', at_sender=True)
                return
            else:
                id = binds[uid]['id']
        try:
            res = await query(id)

            last_login_time = int (res['user_info']['last_login_time'])
            last_login_date = time.localtime(last_login_time)
            last_login_str = time.strftime('%Y-%m-%d %H:%M:%S',last_login_date)

            await bot.finish(args,
f'''昵称：{res['user_info']["user_name"]}
jjc：{res['user_info']["arena_rank"]}
pjjc：{res['user_info']["grand_arena_rank"]}
最后登录：{last_login_str}''', at_sender=False)
        except ApiException as e:
            await bot.finish(args, f'查询出错，{e}', at_sender=True)

@bot.CommandHandler(r'^详细查询 ?(\d{13})?$')
async def on_query_arena_all(bot, *args):
    global binds, lck

    robj = args['match']
    id = robj.group(1)

    async with lck:
        if id == None:
            uid = str(args['user_id'])
            if not uid in binds:
                await bot.finish(args, '您还未绑定竞技场', at_sender=True)
                return
            else:
                id = binds[uid]['id']
        try:
            res = await query(id)
            arena_time = int (res['user_info']['arena_time'])
            arena_date = time.localtime(arena_time)
            arena_str = time.strftime('%Y-%m-%d',arena_date)

            grand_arena_time = int (res['user_info']['grand_arena_time'])
            grand_arena_date = time.localtime(grand_arena_time)
            grand_arena_str = time.strftime('%Y-%m-%d',grand_arena_date)

            last_login_time = int (res['user_info']['last_login_time'])
            last_login_date = time.localtime(last_login_time)
            last_login_str = time.strftime('%Y-%m-%d %H:%M:%S',last_login_date)

            await bot.finish(args,
f'''id：{res['user_info']["viewer_id"]}
昵称：{res['user_info']["user_name"]}
公会：{res["clan_name"]}
简介：{res['user_info']["user_comment"]}
最后登录：{last_login_str}
jjc：{res['user_info']["arena_rank"]}
pjjc：{res['user_info']["grand_arena_rank"]}
战力：{res['user_info']["total_power"]}
等级：{res['user_info']["team_largsel"]}
jjc场次：{res['user_info']["arena_group"]}
jjc创建日：{arena_str}
pjjc场次：{res['user_info']["grand_arena_group"]}
pjjc创建日：{grand_arena_str}
角色数：{res['user_info']["unit_num"]}
''', at_sender=False)
        except ApiException as e:
            await bot.finish(args, f'查询出错，{e}', at_sender=True)

@bot.CommandHandler('(启用|停止)(公主)?竞技场订阅')
async def change_arena_sub(bot, *args):
    global binds, lck

    key = 'arena_on' if args['match'].group(2) is None else 'grand_arena_on'
    uid = str(args['user_id'])

    async with lck:
        if not uid in binds:
            await bot.send(args,'您还未绑定竞技场',at_sender=True)
        else:
            binds[uid][key] = args['match'].group(1) == '启用'
            save_binds()
            await bot.finish(args, f'{args["match"].group(0)}成功', at_sender=True)

@bot.CommandHandler('删除竞技场订阅')
async def delete_arena_sub(bot,args):
    global binds, lck

    uid = str(args['user_id'])

    if args.message[0].type == 'at':
        uid = str(args.message[0].data['qq'])
    elif len(args.message) == 1 and args.message[0].type == 'text' and not args.message[0].data['text']:
        uid = str(args['user_id'])


    if not uid in binds:
        await bot.finish(args, '未绑定竞技场', at_sender=True)
        return

    async with lck:
        binds.pop(uid)
        save_binds()

    await bot.finish(args, '删除竞技场订阅成功', at_sender=True)

@bot.CommandHandler('竞技场订阅状态')
async def send_arena_sub_status(bot,args):
    global binds, lck
    uid = str(args['user_id'])

    
    if not uid in binds:
        await bot.send(args,'您还未绑定竞技场', at_sender=True)
    else:
        info = binds[uid]
        await bot.finish(args,
    f'''
    当前竞技场绑定ID：{info['id']}
    竞技场订阅：{'开启' if info['arena_on'] else '关闭'}
    公主竞技场订阅：{'开启' if info['grand_arena_on'] else '关闭'}''',at_sender=True)


@bot.scheduled_job('interval', minutes=1) # minutes是刷新频率，可按自身服务器性能输入其他数值，可支持整数、小数
async def on_arena_schedule():
    global cache, binds, lck
    bot = get_bot()
    
    bind_cache = {}

    async with lck:
        bind_cache = deepcopy(binds)


    for user in bind_cache:
        info = bind_cache[user]
        try:
            bot.logger.info(f'querying {info["id"]} for {info["uid"]}')
            res = await query(info['id'])
            res = (res['user_info']['arena_rank'], res['user_info']['grand_arena_rank'])

            if user not in cache:
                cache[user] = res
                continue

            last = cache[user]
            cache[user] = res

            if res[0] > last[0] and info['arena_on']:
                await bot.send_group_msg(
                    group_id = int(info['gid']),
                    message = f'[CQ:at,qq={info["uid"]}]jjc：{last[0]}->{res[0]} ▼{res[0]-last[0]}'
                )

            if res[1] > last[1] and info['grand_arena_on']:
                await bot.send_group_msg(
                    group_id = int(info['gid']),
                    message = f'[CQ:at,qq={info["uid"]}]pjjc：{last[1]}->{res[1]} ▼{res[1]-last[1]}'
                )
        except ApiException as e:
            bot.logger.info(f'对{info["id"]}的检查出错\n{format_exc()}')
            if e.code == 6:

                async with lck:
                    binds.pop(user)
                    save_binds()
                bot.logger.info(f'已经自动删除错误的uid={info["id"]}')
        except:
            bot.logger.info(f'对{info["id"]}的检查出错\n{format_exc()}')

