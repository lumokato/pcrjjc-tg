from telegram.ext import Updater, CommandHandler
# from apscheduler.schedulers.background import BlockingScheduler
import config as cg
# import logging
import jjc
# import os

# root = logging.getLogger()
# root.setLevel(logging.INFO)

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
# logger = logging.getLogger(__name__)


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
    bot.job_queue.run_repeating(jjc.on_arena_schedule, 30, job_kwargs={'max_instances': 100})
    # dp.add_handler(CommandHandler('aa', top.on_query_atop, run_async=True))
    # dp.add_handler(CommandHandler('pp', top.on_query_ptop, run_async=True))
    # dp.add_handler(CommandHandler('a', top.on_query_alist, run_async=True))
    # dp.add_handler(CommandHandler('p', top.on_query_plist, run_async=True))
    # dp.add_handler(CommandHandler('start', jjc.start_schedule, pass_job_queue=True))
    # scheduler = BlockingScheduler(timezone="Asia/Shanghai")
    # scheduler.add_job(top.on_query_pwild, 'cron', second='55', max_instances=4)
    # bot.job_queue.run_repeating(top.on_query_pwild, 60, 15, job_kwargs={'max_instances': 100})
    bot.start_polling()
    # _error_log_file = os.path.expanduser('./error.txt')
    # error_handler = logging.FileHandler(_error_log_file, encoding='utf8')
    # error_handler.setLevel(logging.ERROR)
    # formatter = logging.Formatter('[%(asctime)s %(name)s] %(levelname)s: %(message)s')
    # error_handler.setFormatter(formatter)
    # logger.addHandler(error_handler)


if __name__ == '__main__':
    main()
