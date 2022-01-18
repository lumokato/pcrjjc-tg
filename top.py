from pcrclient import pcrclient, ApiException
import config as cg
import time


client = pcrclient(cg.viewer_id2)
client.login(cg.uid2, cg.access_key)


def query(id: str):
    res = client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)
        })
    if 'user_info' not in res:
        client.login(cg.uid, cg.access_key)
        res = client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)})
    return res


def query_ranking():
    res = client.callapi('/arena/ranking', {'limit': 20, 'page': 1})
    ranking_dict = {}
    if 'ranking' in res:
        for user in res['ranking']:
            ranking_dict[user['viewer_id']] = user['rank']
    return ranking_dict


def on_query_top(update, context):
    # chatid = str(update.effective_chat.id)
    try:
        top_dict = query_ranking()
        last10 = []
        last30 = []
        last60 = []
        for top in top_dict.keys():
            res = query(int(top))
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


if __name__ == "__main__":
    on_query_top()
