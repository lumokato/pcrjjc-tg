from pcrclient import pcrclient
import config as cg
import pandas as pd
# import csv
from datetime import datetime

BOSS_LIFE_LIST = [[6000000, 8000000, 10000000, 12000000, 15000000], [6000000, 8000000, 10000000, 12000000, 15000000], [7000000, 9000000, 13000000, 15000000, 20000000], [15000000, 16000000, 18000000, 19000000, 20000000]]
BOSS_SCORE_MUTIPILE = [[1.2, 1.2, 1.3, 1.4, 1.5], [1.6, 1.6, 1.8, 1.9, 2.0], [2.0, 2.0, 2.4, 2.4, 2.6], [3.5, 3.5, 3.7, 3.8, 4.0]]
LAP_UPGRADE = [4, 11, 35]


def boss_status(score):
    lap = 1
    boss_id = 0
    ptr = 0
    while True:
        tmp = int(BOSS_LIFE_LIST[ptr][boss_id] * BOSS_SCORE_MUTIPILE[ptr][boss_id])
        if score < tmp:
            remaining = int(BOSS_LIFE_LIST[ptr][boss_id] - score / BOSS_SCORE_MUTIPILE[ptr][boss_id])
            return lap, boss_id + 1, remaining, ptr
        score -= tmp
        boss_id += 1
        if boss_id > 4:
            boss_id = 0
            lap += 1
            if ptr <= 1:
                if lap >= LAP_UPGRADE[ptr]:
                    ptr += 1


def process_data(temp):
    if 'rank' not in temp:
        temp['rank'] = -1
    if 'damage' not in temp:
        temp['damage'] = 0
    if 'clan_name' not in temp:
        temp['clan_name'] = '此行会已解散'
    if 'member_num' not in temp:
        temp['member_num'] = 0
    if 'leader_name' not in temp:
        temp['leader_name'] = 'unknown'
    if 'grade_rank' not in temp:
        temp['grade_rank'] = 0
    return temp


class ClanBattle:
    def __init__(self, viewer_id, uid, access_key):
        self.uid = uid
        self.access_key = access_key
        self.Client = pcrclient(viewer_id)
        self.Client.login(uid, access_key)
        self.clan_id = 54

    def get_page_status(self, page):
        temp = self.Client.callapi('clan_battle/period_ranking', {'clan_id': self.clan_id, 'clan_battle_id': -1, 'period': -1, 'month': 0, 'page': page, 'is_my_clan': 0, 'is_first': 1})
        if 'period_ranking' not in temp:
            self.Client.login(self.uid, self.access_key)
            temp = self.Client.callapi('clan_battle/period_ranking', {'clan_id': self.clan_id, 'clan_battle_id': -1, 'period': -1, 'month': 0, 'page': page, 'is_my_clan': 0, 'is_first': 1})
        return temp['period_ranking']

    def get_rank_status(self, rank):
        temp1 = self.get_page_status((rank - 1) // 10)
        if (rank - 1) % 10 < len(temp1):
            temp = temp1[(rank - 1) % 10]
        else:
            temp = {}
        return process_data(temp)

    def get_page_data(self, page):
        temp1 = self.get_page_status(page)
        for i in range(0, len(temp1)):
            temp1[i] = process_data(temp1[i])
            lap, boss_id, remain, ptr = boss_status(temp1[i]['damage'])
            temp1[i]['lap'] = lap
            temp1[i]['boss_id'] = boss_id
            temp1[i]['remain'] = remain
            temp1[i]['ptr'] = ptr
        return temp1

    def rank_to_string(self, status, long_info=False):
        lap, boss_id, remaining = boss_status(status['damage'])

        if long_info:
            return '第{}名：{}，会长：{}，成员数：{}/30，分数：{}，当前进度：{}周目{}王，剩余血量：{}/{}，上期排名：{}'.format(status['rank'], status['clan_name'], status['leader_name'], status['member_num'], status['damage'], lap, boss_id, remaining, BOSS_LIFE_LIST[boss_id - 1], status['grade_rank'])
        else:
            return '第{}名：{}，分数：{}，当前进度：{}周目{}王，剩余血量{}/{}'.format(status['rank'], status['clan_name'], status['damage'], lap, boss_id, remaining, BOSS_LIFE_LIST[boss_id - 1])


def stage_data():
    App = ClanBattle(cg.pvid, cg.puid, cg.access_key)
    # save_data = [['rank', 'clan_name', 'leader_name', 'member_num', 'damage', 'lap', 'boss_id', 'remain', 'grade_rank']]
    save_data = []
    for page in range(30):
        try:
            temp = App.get_page_data(page)
            for status in temp:
                save_data.append([status['rank'], status['clan_name'], status['leader_name'], status['member_num'], status['damage'], status['lap'], status['boss_id'], status['remain'], status['grade_rank']])
        except Exception:
            continue
    df = pd.DataFrame(save_data)
    df.columns = ['rank', 'clan_name', 'leader_name', 'member_num', 'damage', 'lap', 'boss_id', 'remain', 'grade_rank']
    now = datetime.now()
    filename = str(now.strftime("%Y%m%d%H")) + str(int(int(now.strftime("%M"))/30)*30).zfill(2)
    df.to_csv('qd/1/'+filename+'.csv')


if __name__ == '__main__':
    stage_data()
