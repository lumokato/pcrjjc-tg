from telegram.ext import Updater, CommandHandler, JobQueue
import config as cg
import time
import logging
from telegram.ext.dispatcher import run_async

root = logging.getLogger()
root.setLevel(logging.INFO)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


@run_async
def send_async(context, *args, **kwargs):
    context.bot.send_message(*args, **kwargs)


def main():
    bot = Updater(token='2096122895:AAEZstwii4QrlrIK8HvHAey36VTNDebVEfk', request_kwargs={'proxy_url': cg.proxy_url}, use_context=True)
    dp = bot.dispatcher
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(JobQueue, start)
    bot.start_polling()


if __name__ == '__main__':
    main()
