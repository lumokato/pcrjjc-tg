from telegram.ext import ApplicationBuilder, CommandHandler, JobQueue
# from apscheduler.schedulers.background import BlockingScheduler
from json import load
import top
import hide
from datetime import datetime, timedelta

with open('account.json', encoding='utf-8') as fp:
    tgbot = load(fp)['tgbot']


def main():
    proxy_url = tgbot["proxy_url"]
    if proxy_url:
        app = ApplicationBuilder().token(tgbot["TOKEN2"]).proxy(proxy_url).get_updates_proxy(proxy_url).read_timeout(600).write_timeout(600).connect_timeout(600).pool_timeout(600).build()
    else:
        app = ApplicationBuilder().token(tgbot["TOKEN2"]).read_timeout(600).write_timeout(600).connect_timeout(600).pool_timeout(600).build()

    app.add_handler(CommandHandler('pp', top.on_query_ptop))
    app.add_handler(CommandHandler('a', top.on_query_alist))
    app.add_handler(CommandHandler('p', top.on_query_plist))
    app.add_handler(CommandHandler('hide', hide.hide_process))

    now = datetime.now()
    run_time = datetime(now.year, now.month, now.day, 14, 55, 50)
    if now > run_time:
        run_time += timedelta(days=1)
    first = (run_time - now).total_seconds()
    app.job_queue.run_repeating(hide.hide_process, first, 86400)

    app.run_polling()

# def refresh_daily(scheduler):
#     scheduler.remove_job('query')
#     scheduler.add_job(top.on_query_pwild, id='query', trigger='cron', second='30', max_instances=100)

if __name__ == '__main__':
    main()
    # scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    # scheduler.add_job(top.on_query_pwild, id='query', trigger='cron', second='30', max_instances=100)
    # scheduler.add_job(hide.hide_process, id='hide1', trigger='cron', hour='14', minute='55', second='45', args=["1"])
    # scheduler.start()
