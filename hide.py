from pcrclient import PCRClient
import time
from json import load
from wechat import send_wechat


def hide_process(update=None, context=None, hide_rank="2"):
    with open('account.json', encoding='utf-8') as fp:
        load_data = load(fp)
        hide_account = load_data['hide']
        hide_user = load_data['hide_user']
        wechat_bot = load_data['wechat']
    hclient = PCRClient(hide_account["viewer_id"])
    hclient.login(hide_account["uid"], hide_account["access_key"])
    grand_info = hclient.callapi('/grand_arena/info', {})
    msg = '未找到成员'
    if 'search_opponent' in grand_info:
        for user in grand_info['search_opponent']:
            user_rank = user['rank']
            user_id = user['viewer_id']
            if user_rank == hide_user[hide_rank]['rank'] and user_id == hide_user[hide_rank]['vid']:
                hide_apply = hclient.callapi('/grand_arena/apply', {'battle_viewer_id': user_id, 'opponent_rank': user_rank})
                if not hide_apply:
                    msg = '已隐身第' + str(user_rank)+'名, 时间为'+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                else:
                    msg = '处理错误'
        loop_count = 0
        while msg == '未找到成员' and loop_count < 3:
            grand_info = hclient.callapi('/grand_arena/search', {})
            hide_apply = hclient.callapi('/grand_arena/apply',
                                         {'battle_viewer_id': int(hide_user[hide_rank]['vid']), 'opponent_rank': int(hide_user[hide_rank]['rank'])})
            if not hide_apply:
                msg = '已强制隐身第' + str(hide_user[hide_rank]['rank']) + '名, 时间为' + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                break
            loop_count += 1
            time.sleep(2)
    send_wechat(msg, wechat_bot["bot3"])
    if update:
        context.bot.send_message(update.effective_chat.id, msg)


if __name__ == '__main__':
    hide_process()
