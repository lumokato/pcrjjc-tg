from telegram.ext import Updater, CommandHandler
import config as cg
import logging
import jjc

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
    dp.add_handler(CommandHandler('query', jjc.on_query_arena, run_async=True))
    dp.add_handler(CommandHandler('queryall', jjc.on_query_arena_all, run_async=True))
    dp.add_handler(CommandHandler('help', jjc.send_jjchelp, run_async=True))
    dp.add_handler(CommandHandler('bind', jjc.on_arena_bind, run_async=True))
    dp.add_handler(CommandHandler('change', jjc.change_arena_sub, run_async=True))
    dp.add_handler(CommandHandler('del', jjc.delete_arena_sub, run_async=True))
    dp.add_handler(CommandHandler('status', jjc.send_arena_sub_status, run_async=True))
    # dp.add_handler(CommandHandler('start', jjc.start_schedule, pass_job_queue=True))
    bot.job_queue.run_repeating(jjc.on_arena_schedule, 60)
    bot.start_polling()


if __name__ == '__main__':
    main()
