ps aux|grep bot.py|grep -v grep |awk '{print $2}'|xargs kill -9
ps aux|grep bot2.py|grep -v grep |awk '{print $2}'|xargs kill -9
nohup python3 bot.py &
nohup python3 bot2.py &
