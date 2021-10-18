from pcrclient import pcrclient, ApiException

def query(client, id: str):
    res = client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)
        })
    if 'user_info' not in res:
        client.login(cg.uid, cg.access_key)
        res = client.callapi('/profile/get_profile', {
            'target_viewer_id': int(id)})
    return res


def start(update, context):
    client = pcrclient(cg.viewer_id)
    client.login(cg.uid, cg.access_key)
    res = query(client,"1193285189140")

    last_login_time = int(res['user_info']['last_login_time'])
    last_login_date = time.localtime(last_login_time)
    last_login_str = time.strftime('%Y-%m-%d %H:%M:%S',last_login_date)

    text = f'''昵称：{res['user_info']["user_name"]}
                jjc：{res['user_info']["arena_rank"]}
                pjjc：{res['user_info']["grand_arena_rank"]}
                最后登录：{last_login_str}'''
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)