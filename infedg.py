import requests
import csv
import json
import time


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
        return True
    else:
        return False


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


def minus_damage(date_list, savefile: str):
    date_num = len(date_list)
    detail_clan = read_detail(date_list[-1])
    damage_list = []
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
    with open('./data/damage.csv', 'w', encoding="utf8") as csvfile:
        for i in range(len(raw_data['rank'])):
            line = ''
            for keyword in raw_data.keys():
                line += str(raw_data[keyword][i]) + ','
            csvfile.write(line[:-1] + '\n')
        csvfile.close()


def damage_to_data():
    date_num = 0
    date_list = ["0122", "0123", "0124", "0125", "0126"]
    for date in date_list:
        if page_to_csv(date):
            date_num += 1
            time.sleep(5)
        else:
            break
    minus_damage(date_list[0: date_num], "damage.csv")
    return True


def refresh_damage(update, context):
    text = ""
    if damage_to_data():
        text = "已刷新工会战伤害"
    chatid = str(update.effective_chat.id)
    context.bot.send_message(chatid, text)


if __name__ == "__main__":
    damage_to_data()
