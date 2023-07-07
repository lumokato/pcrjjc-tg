from telegram.ext import Updater, CommandHandler
# from apscheduler.schedulers.background import BlockingScheduler
from json import load
import top
import hide

with open('account.json', encoding='utf-8') as fp:
    tgbot = load(fp)['tgbot']


def main():
    bot = Updater(token=tgbot["TOKEN2"], request_kwargs={'proxy_url': tgbot["proxy_url"]}, use_context=True)
    dp = bot.dispatcher
    dp.add_handler(CommandHandler('pp', top.on_query_ptop, run_async=True))
    dp.add_handler(CommandHandler('p', top.on_query_plist, run_async=True))
    dp.add_handler(CommandHandler('hide', hide.hide_process, run_async=True))
    bot.start_polling()


def refresh_daily(scheduler):
    scheduler.remove_job('query')
    scheduler.add_job(top.on_query_pwild, id='query', trigger='cron', second='30', max_instances=100)


if __name__ == '__main__':
    main()
    # scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    # scheduler.add_job(top.on_query_pwild, id='query', trigger='cron', second='30', max_instances=100)
    # scheduler.add_job(hide.hide_process, id='hide1', trigger='cron', hour='14', minute='52', second='45', args=["1"])
    # scheduler.add_job(hide.hide_process, id='hide2', trigger='cron', hour='14', minute='55', second='56', args=["2"])
    # scheduler.start()
