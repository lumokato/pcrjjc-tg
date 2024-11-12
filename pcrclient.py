from os.path import dirname, join
import traceback
from msgpack import packb, unpackb
import asyncio
from random import randint
from json import loads
from hashlib import md5
from Crypto.Cipher import AES
from base64 import b64encode, b64decode
import re
from dateutil.parser import parse
import httpx
import random
import logging

class ApiException(Exception):

    def __init__(self, message, code):
        super().__init__(message)
        self.code = code


def get_api_root():
    return random.choice([
        "https://l1-prod-uo-gs-gzlj.bilibiligame.net",
        "https://l3-prod-uo-gs-gzlj.bilibiligame.net/"
    ])

config = join(dirname(__file__), 'version.txt')

defaultHeaders = {
    'Accept-Encoding': 'gzip',
    'User-Agent': 'Dalvik/2.1.0 (Linux, U, Android 5.1.1, PCRT00 Build/LMY48Z)',
    'X-Unity-Version': '2018.4.30f1',
    'APP-VER': '7.7.2',
    'BATTLE-LOGIC-VERSION': '4',
    'BUNDLE-VER': '',
    'DEVICE': '2',
    'DEVICE-ID': 'febf37270db0254b8d1f76af92f0419f',
    'DEVICE-NAME': 'Google PIXEL 2 XL',
    'EXCEL-VER': '1.0.0',
    'GRAPHICS-DEVICE-NAME': 'Adreno (TM) 540',
    'IP-ADDRESS': '10.0.2.15',
    'KEYCHAIN': '',
    'LOCALE': 'CN',
    'PLATFORM-OS-VERSION': 'Android OS 7.1.2 / API-25 (NOF26V/4565141)',
    'REGION-CODE': '',
    'RES-KEY': 'd145b29050641dac2f8b19df0afe0e59',
    'RES-VER': '10002200',
    'SHORT-UDID': '0',
    'CHANNEL-ID': '1',
    'PLATFORM': '2',
    "Connection": "Keep-Alive"
}


class pcrclient:

    def __init__(self, account: str):
        self.viewer_id = 0
        self.uid = account
        self.access_key = "d145b29050641dac2f8b19df0afe0e59"

        self.platform_id = "4"

        self.headers = defaultHeaders.copy()
        self.headers['PLATFORM-ID'] = self.platform_id
        self.client = httpx.AsyncClient()
        self.call_lock = asyncio.Lock()


    @staticmethod
    def createkey() -> bytes:
        return bytes([ord('0123456789abcdef'[randint(0, 15)]) for _ in range(32)])

    @staticmethod
    def add_to_16(b: bytes) -> bytes:
        n = len(b) % 16
        n = n // 16 * 16 - n + 16
        return b + (n * bytes([n]))

    @staticmethod
    def pack(data: object, key: bytes) -> bytes:
        aes = AES.new(key, AES.MODE_CBC, b'ha4nBYA2APUD6Uv1')
        return aes.encrypt(pcrclient.add_to_16(packb(data, use_bin_type=False))) + key

    @staticmethod
    def encrypt(data: str, key: bytes) -> bytes:
        aes = AES.new(key, AES.MODE_CBC, b'ha4nBYA2APUD6Uv1')
        return aes.encrypt(pcrclient.add_to_16(data.encode('utf8'))) + key

    @staticmethod
    def decrypt(data: bytes):
        data = b64decode(data.decode('utf8'))
        aes = AES.new(data[-32:], AES.MODE_CBC, b'ha4nBYA2APUD6Uv1')
        return aes.decrypt(data[:-32]), data[-32:]

    @staticmethod
    def unpack(data: bytes):
        data = b64decode(data.decode('utf8'))
        aes = AES.new(data[-32:], AES.MODE_CBC, b'ha4nBYA2APUD6Uv1')
        dec = aes.decrypt(data[:-32])
        return unpackb(dec[:-dec[-1]], strict_map_key=False), data[-32:]

    async def callapi(self, apiurl: str, request: dict, crypted: bool = True, noerr: bool = True, header=False):
        async with self.call_lock:
            key = pcrclient.createkey()

            try:
                if self.viewer_id is not None:
                    request['viewer_id'] = b64encode(pcrclient.encrypt(
                        str(self.viewer_id), key)) if crypted else str(self.viewer_id)
                response = (await self.client.post(get_api_root() + apiurl, data=pcrclient.pack(request, key) if crypted else str(request).encode('utf8'), headers=self.headers, timeout=20)).content
                
                response = pcrclient.unpack(
                    response)[0] if crypted else loads(response)

                data_headers = response['data_headers']

                if 'sid' in data_headers and data_headers["sid"] != '':
                    t = md5()
                    t.update((data_headers['sid'] + 'c!SID!n').encode('utf8'))
                    self.headers['SID'] = t.hexdigest()

                if 'request_id' in data_headers:
                    self.headers['REQUEST-ID'] = data_headers['request_id']
                data = response['data']
                if not noerr and 'server_error' in data:
                    data = data['server_error']
                    logging.info(f'pcrclient: {apiurl} api failed {data}')
                    raise ApiException(data['message'], data['status'])

                return data if not header else (data, data_headers)
            except Exception as e:
                print(traceback.format_exc())
                raise ApiException("未知错误" + str(e), 501)

    async def check_gamestart(self):
        gamestart, data_headers = await self.callapi('/check/game_start', {'apptype': 0, 'campaign_data': '', 'campaign_user': randint(0, 99999)}, header=True)
        if "store_url" in data_headers:
            if version := re.compile(r"\d\.\d\.\d").findall(data_headers["store_url"]):
                version = version[0]
                with open(config, "w", encoding='utf-8') as fp:
                    print(version, file=fp)
            else:
                with open(config, encoding='utf-8') as fp:
                    version = fp.read().strip()
            defaultHeaders['APP-VER'] = version
            self.headers['APP-VER'] = version
            gamestart, data_headers = await self.callapi('/check/game_start', {'apptype': 0, 'campaign_data': '', 'campaign_user': randint(0, 99999)}, header=True)

        if 'now_tutorial' in gamestart:
            if not gamestart['now_tutorial']:
                raise ApiException("该账号没过完教程!", 403)

    async def check_dangerous(self):
        lres, data_headers = await self.callapi('/tool/sdk_login', {'uid': str(self.uid), 'access_key': self.access_key, 'channel': "1", 'platform': self.platform_id}, header=True)
        if 'is_risk' in lres and lres['is_risk'] == 1:
            raise ApiException("账号存在风险", 403)
        self.viewer_id = data_headers['viewer_id']

    async def login(self):

        if 'REQUEST-ID' in self.headers:
            self.headers.pop('REQUEST-ID')
        
        manifest = await self.callapi('/source_ini/get_maintenance_status?format=json', {}, False, noerr=True)
        if 'maintenance_message' in manifest:
            match = re.search('\d\d\d\d-\d\d-\d\d \d\d:\d\d:\d\d',
                              manifest['maintenance_message']).group()
            raise ApiException("服务器在维护", parse(match))
        
        ver = manifest['required_manifest_ver']
        logging.info(f'using manifest ver = {ver}')
        self.headers['MANIFEST-VER'] = str(ver)

        await self.check_dangerous()
        await self.check_gamestart()
