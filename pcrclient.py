import requests
import PCRPack as Pack
import hashlib
import random


class pcrclient:
    def __init__(self, viewer_id):
        self.viewer_id = viewer_id
        self.request_id = ""
        self.session_id = ""
        self.urlroot = "https://l3-prod-uo-gs-gzlj.bilibiligame.net/"
        self.default_headers = {
            "Accept-Encoding": "gzip",
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 6.0.1; VTR-AL00 Build/V417IR)",
            "X-Unity-Version": "2018.4.30f1",
            "APP-VER": "4.9.2",
            "BATTLE-LOGIC-VERSION": "4",
            "BUNDLE_VER": "",
            "CHANNEL-ID": "1",
            "DEVICE": "2",
            "DEVICE-ID": "6d3dd40c2545eab5c8a651d3359358bd",
            "DEVICE-NAME": "HUAWEI VTR-AL00",
            "EXCEL-VER": "1.0.0",
            "GRAPHICS-DEVICE-NAME": "MuMu GL (NVIDIA GeForce RTX 2070 Direct3D11 vs_5_0 ps_5_0)",
            "IP-ADDRESS": "10.1.10.1",
            "KEYCHAIN": "",
            "LOCALE": "CN",
            "PLATFORM": "2",
            "PLATFORM-ID": "4",
            "PLATFORM-OS-VERSION": "Android OS 6.0.1 / API-23 (V417IR/eng.root.20200623.095831)",
            "REGION-CODE": "",
            "RES-KEY": "d145b29050641dac2f8b19df0afe0e59",
            "RES-VER": "10002200",
            "SHORT-UDID": "0",
            "Connection": "Keep-Alive"}
        self.conn = requests.session()

    def callapi(self, apiurl, request, crypted=True):
        key = Pack.CreateKey()
        if crypted:
            request['viewer_id'] = Pack.encrypt(str(self.viewer_id), key).decode()
        else:
            request['viewer_id'] = str(self.viewer_id)
        req = Pack.Pack(request, key)
        flag = self.request_id is not None and self.request_id != ''
        flag2 = self.session_id is not None and self.session_id != ''
        headers = self.default_headers
        if flag:
            headers["REQUEST-ID"] = self.request_id
        if flag2:
            headers["SID"] = self.session_id
        resp = self.conn.post(url=self.urlroot + apiurl,
                              headers=headers, data=req)
        null = None
        if crypted:
            ret = Pack.decrypt(resp.content)
        else:
            ret = eval(resp.content.decode())
        ret_header = ret["data_headers"]
        if "sid" in ret_header:
            if ret_header["sid"] is not None and ret_header["sid"] != "":
                self.session_id = hashlib.md5((ret_header["sid"] + "c!SID!n").encode()).hexdigest()
        if "request_id" in ret_header:
            if ret_header["request_id"] is not None and ret_header["request_id"] != "" and ret_header["request_id"] != self.request_id:
                self.request_id = ret_header["request_id"]
        if "viewer_id" in ret_header:
            if ret_header["viewer_id"] is not None and ret_header["viewer_id"] != 0 and ret_header["viewer_id"] != self.viewer_id:
                self.viewer_id = int(ret_header["viewer_id"])
        return ret["data"]

    def login(self, uid, access_key):
        self.manifest = self.callapi('source_ini/get_maintenance_status', {}, False)
        ver = self.manifest["required_manifest_ver"]
        self.default_headers["MANIFEST-VER"] = ver
        self.callapi('tool/sdk_login', {"uid": uid, "access_key": access_key, "platform": self.default_headers["PLATFORM-ID"], "channel_id": self.default_headers["CHANNEL-ID"]})
        self.callapi('check/game_start', {"app_type": 0, "campaign_data": "", "campaign_user": random.randint(1, 1000000)})
        self.callapi("check/check_agreement", {})
        self.callapi("load/index", {"carrier": "google"})
        self.home = self.callapi("home/index", {'message_id': random.randint(1, 5000), 'tips_id_list': [], 'is_first': 1, 'gold_history': 0})
        return self.home


class ApiException(Exception):
    def __init__(self, message, code):
        super().__init__(message)
        self.code = code
