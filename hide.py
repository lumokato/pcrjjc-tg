from pcrclient import pcrclient
import time
from json import load
from wechat import send_wechat


async def hide_process(update, context):
    with open('account.json', encoding='utf-8') as fp:
        load_data = load(fp)
        hide_account = load_data['hide']
        hide_user = load_data['hide_user']
        wechat_bot = load_data['wechat']
    hclient = pcrclient(hide_account["uid"])
    await hclient.login()
    arena_info = await hclient.callapi('/arena/info', {})
    msg = '未找到成员'
    if 'search_opponent' in arena_info:
        for user in arena_info['search_opponent']:
            user_rank = user['rank']
            user_id = user['viewer_id']
            if user_rank == hide_user['rank'] and user_id == hide_user['vid']:
                hide_apply = await hclient.callapi('/arena/apply', {'battle_viewer_id': user_id, 'opponent_rank': user_rank})
                if not hide_apply:
                    msg = '已隐身第' + str(user_rank)+'名, 时间为'+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                else:
                    msg = '处理错误'
        loop_count = 0
        while msg == '未找到成员' and loop_count < 3:
            arena_info = await hclient.callapi('/arena/search', {})
            hide_apply = await hclient.callapi('/arena/apply',
                                         {'battle_viewer_id': int(hide_user['vid']), 'opponent_rank': int(hide_user['rank'])})
            if not hide_apply:
                msg = '已强制隐身第' + str(hide_user['rank']) + '名, 时间为' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                break
            loop_count += 1
            time.sleep(2)
    send_wechat(msg, wechat_bot["bot3"])
    # if update:
    #     context.bot.send_message(update.effective_chat.id, msg)
