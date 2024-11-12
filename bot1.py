from telegram.ext import ApplicationBuilder, CommandHandler
from json import load
import jjc

import logging
from datetime import timedelta

# 启用日志
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


with open('account.json', encoding='utf-8') as fp:
    tgbot = load(fp)['tgbot']


def main():
    proxy_url = tgbot["proxy_url"]
    if proxy_url:
        app = ApplicationBuilder().token(tgbot["TOKEN1"]).proxy(proxy_url).get_updates_proxy(proxy_url).build()
    else:
        app = ApplicationBuilder().token(tgbot["TOKEN1"]).build()
    app.add_handler(CommandHandler('query', jjc.on_query_arena))
    app.add_handler(CommandHandler('q', jjc.on_query_arena_all))
    app.add_handler(CommandHandler('help', jjc.send_jjchelp))
    app.add_handler(CommandHandler('bind', jjc.on_arena_bind))
    app.add_handler(CommandHandler('change', jjc.change_arena_sub))
    app.add_handler(CommandHandler('del', jjc.delete_arena_sub))
    app.add_handler(CommandHandler('status', jjc.send_arena_sub_status))

    app.job_queue.run_repeating(jjc.on_arena_schedule, interval=timedelta(seconds=30), first=0)
    app.run_polling()

if __name__ == '__main__':
    main()
