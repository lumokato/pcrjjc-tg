from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BlockingScheduler
from json import load
import top


with open('account.json', encoding='utf-8') as fp:
    tgbot = load(fp)['tgbot']


def main():
    bot = Updater(token=tgbot["TOKEN2"], request_kwargs={'proxy_url': tgbot["proxy_url"]}, use_context=True)
    dp = bot.dispatcher
    dp.add_handler(CommandHandler('pp', top.on_query_ptop, run_async=True))
    dp.add_handler(CommandHandler('p', top.on_query_plist, run_async=True))
    bot.start_polling()


def refresh_daily(scheduler):
    scheduler.remove_job('query')
    scheduler.add_job(top.on_query_pwild, id='query', trigger='cron', second='30', max_instances=100)


if __name__ == '__main__':
    main()
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(top.on_query_pwild, id='query', trigger='cron', second='30', max_instances=100)
    scheduler.add_job(refresh_daily, 'cron', hour='3', max_instances=100, args=[scheduler])
    scheduler.start()
