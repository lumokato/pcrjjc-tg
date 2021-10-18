from telegram.ext import Updater, CommandHandler
REQUEST_KWARGS = {
    # "USERNAME:PASSWORD@" is optional, if you need authentication:
    'proxy_url': 'http://127.0.0.1:10809/',
}

bot = Updater(token='2096122895:AAEZstwii4QrlrIK8HvHAey36VTNDebVEfk', request_kwargs=REQUEST_KWARGS, use_context=True)
