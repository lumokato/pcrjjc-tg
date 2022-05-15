from telegram.ext import Updater, CommandHandler
import config as cg
import logging
import jjc
import top

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
    dp.add_handler(CommandHandler('q', jjc.on_query_arena_all, run_async=True))
    dp.add_handler(CommandHandler('help', jjc.send_jjchelp, run_async=True))
    dp.add_handler(CommandHandler('bind', jjc.on_arena_bind, run_async=True))
    dp.add_handler(CommandHandler('change', jjc.change_arena_sub, run_async=True))
    dp.add_handler(CommandHandler('del', jjc.delete_arena_sub, run_async=True))
    dp.add_handler(CommandHandler('status', jjc.send_arena_sub_status, run_async=True))
    dp.add_handler(CommandHandler('rate', jjc.damage_percentage_stage, run_async=True))
    dp.add_handler(CommandHandler('aa', top.on_query_atop, run_async=True))
    dp.add_handler(CommandHandler('pp', top.on_query_ptop, run_async=True))
    dp.add_handler(CommandHandler('a', top.on_query_alist, run_async=True))
    dp.add_handler(CommandHandler('p', top.on_query_plist, run_async=True))
    # dp.add_handler(CommandHandler('start', jjc.start_schedule, pass_job_queue=True))
    bot.job_queue.run_repeating(jjc.on_arena_schedule, 30)
    bot.job_queue.run_repeating(top.on_query_ptop, 86400, first="2022-01-18 14:40:00", last="2022-12-30 23:01:00")
    bot.start_polling()


if __name__ == '__main__':
    main()
