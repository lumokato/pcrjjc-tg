from telegram.ext import Updater, CommandHandler
# from apscheduler.schedulers.background import BlockingScheduler
import config as cg
# import logging
import top
# import os
import time

def test(context):
    
    time.sleep(10000)

def main():
    bot = Updater(token=cg.TOKEN2, request_kwargs={'proxy_url': cg.proxy_url}, use_context=True)
    dp = bot.dispatcher
    dp.add_handler(CommandHandler('pp', top.on_query_ptop, run_async=True))
    dp.add_handler(CommandHandler('p', top.on_query_plist, run_async=True))
    # bot.job_queue.run_repeating(top.on_query_pwild, 60, 15, job_kwargs={'max_instances': 100})
    bot.job_queue.run_repeating(test, 1)
    bot.start_polling()


if __name__ == '__main__':
    main()
