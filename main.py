from telegram.ext import Updater, CommandHandler, JobQueue
import config as cg
import time
import logging
from telegram.ext.dispatcher import run_async
import new_jjc as jjc

root = logging.getLogger()
root.setLevel(logging.INFO)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


# @run_async
# def send_async(context, *args, **kwargs):
#     context.bot.send_message(*args, **kwargs)


def main():
    bot = Updater(token=cg.TOKEN, request_kwargs={'proxy_url': cg.proxy_url}, use_context=True)
    dp = bot.dispatcher
    dp.add_handler(CommandHandler('start', jjc.start, run_async=True))
    dp.add_handler(CommandHandler('help', jjc.send_jjchelp, run_async=True))
    # dp.add_handler(JobQueue, start)
    bot.start_polling()


if __name__ == '__main__':
    main()
