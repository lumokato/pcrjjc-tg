from telegram.ext import Updater, CommandHandler
from apscheduler.schedulers.background import BlockingScheduler
import config as cg
import top


def main():
    bot = Updater(token=cg.TOKEN2, request_kwargs={'proxy_url': cg.proxy_url}, use_context=True)
    dp = bot.dispatcher
    dp.add_handler(CommandHandler('pp', top.on_query_ptop, run_async=True))
    dp.add_handler(CommandHandler('p', top.on_query_plist, run_async=True))
    bot.start_polling()


if __name__ == '__main__':
    main()
    scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    scheduler.add_job(top.on_query_pwild, 'cron', second='30', job_kwargs={'max_instances': 100})
    scheduler.start()
