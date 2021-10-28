import requests
import csv
import json
import pandas as pd


class WebClient0:
    def __init__(self):
        self.urlroot = "https://api.infedg.xyz"
        self.default_headers = {
            "Host": "api.infedg.xyz",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
            "Custom-Source": "Kyaru",
            "Content-Type": "application/json",
            "Origin": "https://kyaru.infedg.xyz",
            "Sec-Ch-Ua": "Chromium",
            "Sec-Fetch-Site": "same-site",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://kyaru.infedg.xyz/",
            "Accept-Language": "zh-CN,zh",
            "Accept": "application/json, text/javascript, */*",
            "Connection": "close"
            }
        self.conn = requests.session()

    def Callapi(self, apiurl, request):
        headers = self.default_headers
        # resp = self.conn.request("OPTIONS", url= self.urlroot + apiurl, headers = headers)
        resp = self.conn.post(url=self.urlroot + apiurl, headers=headers, data=json.dumps(request))
        ret = eval(resp.content.decode())
        return ret["data"]


client = WebClient0()


def query_date(date: str):
    try:
        res = client.Callapi('/search/rank', {"filename": "qd/1/2021"+date+"0500", "search": "", "page": 0, "page_limit": 200})
        return res
    except Exception:
        return False


def page_to_csv(date: str):
    detail = query_date(date)
    if detail:
        with open('./data/' + date + '.csv', 'w', encoding="utf8") as csvfile:
            for line in detail.values():
                data = '\"""{0}\""",{1},\"""{2}\""",{3},{4}\n'.format(line['clan_name'], line['damage'], line['leader_name'], line['grade_rank'], line['rank'])
                csvfile.write(data)
        csvfile.close()


def walk_date():
    date_list = ["412", "413", "414", "415", "416"]
    for date in date_list:
        page_to_csv(date)


def read_damage_grade_rank(date: str):
    damage = {}
    with open('./data/' + date + '.csv', 'r', encoding="utf8") as csvfile:
        lines = csv.reader(csvfile)
        for line in lines:
            damage[line[3]] = line[1]
        csvfile.close()
    return damage


def read_detail(date: str):
    datail = {}
    with open('./data/' + date + '.csv', 'r', encoding="utf8") as csvfile:
        lines = csv.reader(csvfile)
        for line in lines:
            datail[line[4]] = [line[3], line[0], line[2]]
        csvfile.close()
    return datail


def find_index(finder: int, lister: list):
    index = 0
    while index < 150:
        if finder <= lister[index]:
            index += 1
        else:
            break
    return index


def find_rank():
    b_day1 = []
    b_day2 = []
    b_day3 = []
    b_day4 = []
    b_day5 = []
    qd_data = []
    with open('./rank/damage_byrankqd.csv', 'r', encoding="utf8") as csvfile:
        for line in csv.reader(csvfile):
            b_day1.append(int(line[0]))
            b_day2.append(int(line[1]))
            b_day3.append(int(line[2]))
            b_day4.append(int(line[3]))
            b_day5.append(int(line[4]))
        csvfile.close()
    with open('./rank/damage_qd.csv', 'r', encoding="utf8") as csvfile:
        for line in csv.reader(csvfile):
            qd_data.append('{0},{1},{2},{3},{4},{5},{6},{7}\n'.format(line[0], line[1], line[2], find_index(int(line[3]), b_day1), find_index(int(line[4]), b_day2), find_index(int(line[5]), b_day3), find_index(int(line[6]), b_day4), find_index(int(line[7]), b_day5)))
        csvfile.close()
    with open('./rank/rank_qd2.csv', 'w', encoding="utf8") as csvfile:
        for line in qd_data:
            csvfile.write(line)
        csvfile.close()


def rank_byqd():
    qd_day1 = []
    qd_day2 = []
    qd_day3 = []
    qd_day4 = []
    qd_day5 = []
    qd_day6 = []
    qd_data = []
    with open('./rank/damage_qd.csv', 'r', encoding="utf8") as csvfile:
        for line in csv.reader(csvfile):
            qd_day1.append(int(line[3]))
            qd_day2.append(int(line[4]))
            qd_day3.append(int(line[5]))
            qd_day4.append(int(line[6]))
            qd_day5.append(int(line[7]))
            qd_day6.append(int(line[8]))
        csvfile.close()
    with open('./rank/damage_qd.csv', 'r', encoding="utf8") as csvfile:
        for line in csv.reader(csvfile):
            qd_data.append('{0},{1},{2},{3},{4},{5},{6},{7},{8}\n'.format(line[0], line[1], line[2], find_index(int(line[3]), sorted(qd_day1,reverse=True)), find_index(int(line[4]), sorted(qd_day2,reverse=True)), find_index(int(line[5]), sorted(qd_day3,reverse=True)), find_index(int(line[6]), sorted(qd_day4,reverse=True)), find_index(int(line[7]), sorted(qd_day5,reverse=True)), find_index(int(line[8]), sorted(qd_day6,reverse=True))))
        csvfile.close()
    with open('./rank/rank_qd3.csv', 'w', encoding="utf8") as csvfile:
        for line in qd_data:
            csvfile.write(line)
        csvfile.close()


def minus_damage(date_list, savefile: str):
    date_num = len(date_list)
    detail_clan = read_detail(date_list[-1])
    damage_list = []
    damage_avg_list = []
    clan_list = []
    for i in range(date_num):
        damage_list.append(read_damage_grade_rank(date_list[i]))
        if i > 0:
            for clan in clan_list:
                if clan not in damage_list[i].keys():
                    clan_list.remove(clan)
        else:
            for clan in damage_list[i].keys():
                clan_list.append(clan)
    detail_damage = {}
    for clan in clan_list:
        for j in range(date_num):
            if j > 0:
                detail_damage[clan].append(int(damage_list[j][clan]) - int(damage_list[j-1][clan]))
            else:
                detail_damage[clan] = [int(damage_list[j][clan])]
    raw_data = {'rank': [],
                'grade_rank': [],
                'clan_name': [],
                'leader_name': []}
    for k in range(date_num):
        row_name = 'damage_day' + str(k + 1)
        raw_data[row_name] = []
    for clan_rank in detail_clan.keys():
        if detail_clan[clan_rank][0] in detail_damage.keys():
            clan_grade_rank = detail_clan[clan_rank][0]
            raw_data['rank'].append(clan_rank)
            raw_data['grade_rank'].append(detail_clan[clan_rank][0])
            raw_data['clan_name'].append(detail_clan[clan_rank][1])
            raw_data['leader_name'].append(detail_clan[clan_rank][2])
            for k in range(date_num):
                row_name = 'damage_day' + str(k + 1)
                raw_data[row_name].append(detail_damage[clan_grade_rank][k])
    df = pd.DataFrame(raw_data)
    df.to_csv('./data/' + savefile, index=False, encoding="utf8")


def minus_damage_avg(date_list, savefile: str):
    date_num = len(date_list)
    detail_clan = read_detail(date_list[-1])
    damage_list = []
    damage_avg_list = []
    clan_list = []
    for i in range(date_num):
        damage_list.append(read_damage_grade_rank(date_list[i]))
        if i > 0:
            for clan in clan_list:
                if clan not in damage_list[i].keys():
                    clan_list.remove(clan)
        else:
            for clan in damage_list[i].keys():
                clan_list.append(clan)
    detail_damage = {}
    for clan in clan_list:
        for j in range(date_num):
            if j > 0:
                detail_damage[clan].append(int(damage_list[j][clan]) - int(damage_list[j-1][clan]))
            else:
                detail_damage[clan] = [int(damage_list[j][clan])]
    raw_data = {'rank': [],
                'clan_name': [],
                'leader_name': []}
    for k in range(date_num):
        row_name = 'damage_avg_day' + str(k + 1)
        raw_data[row_name] = []
    for clan_rank in detail_clan.keys():
        if detail_clan[clan_rank][0] in detail_damage.keys():
            clan_grade_rank = detail_clan[clan_rank][0]
            raw_data['rank'].append(clan_rank)
            raw_data['clan_name'].append(detail_clan[clan_rank][1])
            raw_data['leader_name'].append(detail_clan[clan_rank][2])
            for l in range(date_num):
                row_name = 'damage_avg_day' + str(l + 1)
                if l == 0:
                    raw_data[row_name].append(str(round(damage_status(detail_damage[clan_grade_rank][l])/900000, 2))+'w')
                else:
                    raw_data[row_name].append(str(round((damage_status(detail_damage[clan_grade_rank][l] + detail_damage[clan_grade_rank][l-1]) - damage_status(detail_damage[clan_grade_rank][l-1]))/900000, 2))+'w')            
    df = pd.DataFrame(raw_data)
    df.to_csv('./rank/' + savefile, index=False, encoding="utf8")


def rank_byqda(openfile: str, savefile: str):
    qd_data = []
    with open('./rank/' + openfile, 'r', encoding="utf8") as csvfile:
        for line in csv.reader(csvfile):
            if line[0] == 'rank':
                day_num = len(line) - 3
                day_str = line[3:]
                for i in day_str:
                    globals()[i] = []
            if line[0] != 'rank':
                for day in day_str:
                    index = int(day[-1]) + 2
                    exec(f"{day}.append(int(line[{index}]))")
        csvfile.close()
    with open('./rank/' + openfile, 'r', encoding="utf8") as csvfile:
        for line in csv.reader(csvfile):
            if line[0] != 'rank':
                # append_line = '{0},{1},{2}'.format(line[0], line[1], line[2])
                append_line = '{0},{1}'.format(line[0], line[1])
                rank_list = []
                for day in day_str:
                    index = int(day[-1]) + 2
                    exec(f"rank_list.append(find_index(int(line[{index}]), sorted({day},reverse=True)))")
                for rank in rank_list:
                    append_line += ',' + str(rank)
                qd_data.append(append_line + '\n')
        csvfile.close()
    with open('./rank/' + savefile, 'w', encoding="utf8") as csvfile:
        for line in qd_data:
            csvfile.write(line)
        csvfile.close()


BOSS_LIFE_LIST = [6000000, 8000000, 10000000, 12000000, 15000000]
BOSS_SCORE_MUTIPILE = [[1.0, 1.0, 1.3, 1.3, 1.5], [1.4, 1.4, 1.8, 1.8, 2.0], [2.0, 2.0, 2.5, 2.5, 3.0]]
LAP_UPGRADE = [4, 11]


def damage_status(score):
    lap = 1
    boss_id = 0
    ptr = 0
    damage = 0
    while True:
        tmp = int(BOSS_LIFE_LIST[boss_id] * BOSS_SCORE_MUTIPILE[ptr][boss_id])
        if score < tmp:
            remaining = int(BOSS_LIFE_LIST[boss_id] - score / BOSS_SCORE_MUTIPILE[ptr][boss_id])
            return damage + BOSS_LIFE_LIST[boss_id] - remaining
        score -= tmp
        damage += BOSS_LIFE_LIST[boss_id]
        boss_id += 1
        if boss_id > 4:
            boss_id = 0
            lap += 1
            if ptr <= 1:
                if lap >= LAP_UPGRADE[ptr]:
                    ptr += 1


def average_damage():
    print((damage_status(607742210)-damage_status(0))/90)
    print((damage_status(1375051245)-damage_status(607742210))/90)


if __name__ == "__main__":
    page_to_csv("1027")
    page_to_csv("1028")
    minus_damage(["1027", "1028"], "damage.csv")
    # data = pd.read_csv('./data/damage.csv')
