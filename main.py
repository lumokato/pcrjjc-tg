from telegram.ext import Updater, CommandHandler
from json import load
import jjc

with open('account.json', encoding='utf-8') as fp:
    tgbot = load(fp)['tgbot']


def main():
    bot = Updater(token=tgbot["TOKEN1"], request_kwargs={'proxy_url': tgbot["proxy_url"]}, use_context=True)
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
    bot.start_polling()


if __name__ == '__main__':
    main()
