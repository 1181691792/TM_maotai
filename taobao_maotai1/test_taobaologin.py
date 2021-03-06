import re
import os
import json
import requests
import random
from timer import Timer
import time
from fake_useragent import UserAgent


'''hzj出版'''
s = requests.Session()
COOKIES_FILE_PATH = 'taobao_login_cookies.txt'
S=Timer().jd_time()
class UsernameLogin():

    def __init__(self, loginId, umidToken, ua, password2):
        self.user_check_url = 'https://login.taobao.com/newlogin/account/check.do?appName=taobao&fromSite=0'
        self.verify_password_url = "https://login.taobao.com/newlogin/login.do?appName=taobao&fromSite=0"
        self.vst_url = 'https://login.taobao.com/member/vst.htm?st={}'
        self.my_taobao_url = 'http://i.taobao.com/my_taobao.htm'
        self.loginId = loginId
        self.umidToken = umidToken
        self.ua = ua
        self.password2 = password2
        self.timeout = 3


    def _user_check(self):

        data = {
            'loginId': self.loginId,
            'ua': self.ua,
        }
        try:
            response = s.post(self.user_check_url, data=data, timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            print('检测是否需要验证码请求失败，原因：')
            raise e
        check_resp_data = response.json()['content']['data']
        needcode = False
        if 'isCheckCodeShowed' in check_resp_data:
            needcode = True
        print('是否需要滑块验证：{}'.format(needcode))
        return needcode

    def _get_umidToken(self):

        response = s.get('https://login.taobao.com/member/login.jhtml')
        st_match = re.search(r'"umidToken":"(.*?)"', response.text)
        print(st_match.group(1))
        return st_match.group(1)

    @property
    def _verify_password(self):
        verify_password_headers = {
            'Origin': 'https://login.taobao.com',
            'content-type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Referer': 'https://login.taobao.com/member/login.jhtml?spm=a21bo.2017.754894437.1.5af911d9HjW9WC&f=top&redirectURL=https%3A%2F%2Fwww.taobao.com%2F',
        }
        verify_password_data = {
            'ua': self.ua,
            'loginId': self.loginId,
            'password2': self.password2,
            'umidToken': self.umidToken,
            'appEntrance': 'taobao_pc',
            'isMobile': 'false',
            'returnUrl': 'https://www.taobao.com/',
            'navPlatform': 'MacIntel',
        }
        try:
            response = s.post(self.verify_password_url, headers=verify_password_headers, data=verify_password_data,
                              timeout=self.timeout)
            response.raise_for_status()
        except Exception as e:
            print('验证用户名和密码请求失败，原因：')
            raise e
        apply_st_url_match = response.json()['content']['data']['asyncUrls'][0]
        if apply_st_url_match:
            print('验证用户名密码成功，st码申请地址：{}'.format(apply_st_url_match))
            return apply_st_url_match
        else:
            raise RuntimeError('用户名密码验证失败！response：{}'.format(response.text))

    def _apply_st(self):
        apply_st_url = self._verify_password
        try:
            response = s.get(apply_st_url)
            response.raise_for_status()
        except Exception as e:
            print('申请st码请求失败，原因：')
            raise e
        st_match = re.search(r'"data":{"st":"(.*?)"}', response.text)
        if st_match:
            print('获取st码成功，st码：{}'.format(st_match.group(1)))
            return st_match.group(1)
        else:
            raise RuntimeError('获取st码失败！response：{}'.format(response.text))

    def login(self):
        if self._load_cookies():
            return True
        self._user_check()
        st = self._apply_st()
        headers = {
            'Host': 'login.taobao.com',
            'Connection': 'Keep-Alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        try:
            response = s.get(self.vst_url.format(st), headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('st码登录请求，原因：')
            raise e

        my_taobao_match = re.search(r'top.location.href = "(.*?)"', response.text)
        if my_taobao_match:
            print('登录淘宝成功，跳转链接：{}'.format(my_taobao_match.group(1)))
            self.my_taobao_url = my_taobao_match.group(1)
            self._serialization_cookies()
            return True
        else:
            raise RuntimeError('登录失败！response：{}'.format(response.text))

    def _load_cookies(self):
        if not os.path.exists(COOKIES_FILE_PATH):
            return False
        s.cookies = self._deserialization_cookies()
        try:
            self.get_taobao_nick_name()
        except Exception as e:
            os.remove(COOKIES_FILE_PATH)
            print('cookies过期，删除cookies文件！')
            return False
        print('加载淘宝cookies登录成功!!!')
        return True

    def _serialization_cookies(self):

        cookies_dict = requests.utils.dict_from_cookiejar(s.cookies)
        with open(COOKIES_FILE_PATH, 'w+', encoding='utf-8') as file:
            json.dump(cookies_dict, file)
            print('保存cookies文件成功！')

    def _deserialization_cookies(self):

        with open(COOKIES_FILE_PATH, 'r+', encoding='utf-8') as file:
            cookies_dict = json.load(file)
            cookies = requests.utils.cookiejar_from_dict(cookies_dict)
            return cookies

    def get_taobao_nick_name(self):

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        try:
            response = s.get(self.my_taobao_url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            print('获取淘宝主页请求失败！原因：')
            raise e
        # 提取淘宝昵称
        nick_name_match = re.search(r'<input id="mtb-nickname" type="hidden" value="(.*?)"/>', response.text)
        if nick_name_match:
            print('登录淘宝成功，你的用户名是：{}'.format(nick_name_match.group(1)))
            return nick_name_match.group(1)
        else:
            raise RuntimeError('获取淘宝昵称失败！response：{}'.format(response.text))

    def check_demo1(self):
        ua = UserAgent()
        # print(ua.random)  # 随机产生
        headers = {
            'User-Agent': ua.random
        }
        st = self._apply_st()
        data = {
            'item': '2328048666056_20739895092_1_4227830352490_3001638840_0_0_0_buyerCondition~0~~dpbUpgrade~null~~cartCreateTime~',
            'buyer_from': 'cart',
            'source_time': S
        }

        url = "https://buy.taobao.com/auction/order/confirm_order.htm?"

        r=s.post(url.format(st),data=data,headers=headers,proxies="58.52.112.35:4245")
        # r = s.post(url, data=data, headers=headers)
        print(r.status_code)
        print(r.raise_for_status())
        print(r.reason)
        fg = (r.text.encode('GBK', 'ignore').decode('GBk'))
        DE1 = re.search(r'"reason":"(.*?)"', fg)
        print(DE1)


    def get_proxies(self):
        with open('proxy.txt', 'r') as f:
            result = f.readlines()  # 读取所有行并返回列表
        proxy_ip = random.choice(result)[:-1]  # 获取了所有代理IP
        L = proxy_ip.split(':')
        proxy_ip = {
            'http': 'http://{}:{}'.format(L[0], L[1]),
            'https': 'https://{}:{}'.format(L[0], L[1])
        }
        return proxy_ip

    def check_demo(self):
        ua = UserAgent()
        # print(ua.random)  # 随机产生
        headers = {
            'User-Agent': ua.random
        }
        # st = self._apply_st()
        data = {
            'item': '2328048666056_20739895092_1_4227830352490_3001638840_0_0_0_buyerCondition~0~~dpbUpgrade~null~~cartCreateTime~',
            'buyer_from': 'cart',
            'source_time': S
        }

        url = "https://buy.taobao.com/auction/order/confirm_order.htm?"

        # r=s.post(url.format(st),data=data,headers=headers)
        # r = s.post(url, data=data, headers=headers, proxies=proxies)
        r = s.post(url, data=data, headers=headers)
        print(r.status_code)
        print(r.raise_for_status())
        print(r.reason)
        fg = (r.text.encode('GBK', 'ignore').decode('GBk'))
        # print(fg)
        DE=re.search(r'"reason":"(.*?)"', fg)
        print(DE)
        
        
    def post_demo1(self):
        url = "https://gm.mmstat.com//fsp.1.3"
        data = {"gmkey": "OTHER",
                "gokey": "appcacheTime=0&connectTime=0&delay=10.99&domReadyTime=714&effectiveType=4g&firstPaintTime=310&hash=&initDomTreeTime=113&last_pos=130.5%252C381&loadEventTime=51&loadTime=1035&lookupDomainTime=0&page=https%253A%252F%252Fbuy.tmall.com%252Forder%252Fconfirm_order.htm&patch_ver=-&pid=punish-page&query=spm%253Da1z0d.6639537.0.0.undefined&raw_ua=Mozilla%252F5.0%2520(Windows%2520NT%25206.1%253B%2520Win64%253B%2520x64)%2520AppleWebKit%252F537.36%2520(KHTML%252C%2520like%2520Gecko)%2520Chrome%252F86.0.4240.111%2520Safari%252F537.36&readyStart=10&redirectTime=0&referrer=https%253A%252F%252Fcart.taobao.com%252F&rel=&requestTime=147&scr=1920x1080&spm_a=0&spm_b=0&tillDomLookupEndTime=10&tillDomReadyTime=280&tillResponseEndTime=167&title=%25E9%25AA%258C%25E8%25AF%2581%25E7%25A0%2581%25E6%258B%25A6%25E6%2588%25AA&totalTime=1045&tracker_ver=4.0.0&type=3&ua=Mozilla%252F5.0%2520(Windows%2520NT%25206.1%253B%2520Win64%253B%2520x64)%2520AppleWebKit%252F537.36%2520(KHTML%252C%2520like%2520Gecko)%2520Chrome%252F86.0.4240.111%2520Safari%252F537.36&uid=b682bbeb3edea6620c2257ce9b3ce628__1.1.1&unloadEventTime=0",
                "logtype": "2"}
        headers = {'Content-Type': 'text/plain;charset=UTF-8',
                   'Sec-Fetch-Dest': 'empty',
                   'Sec-Fetch-Mode': 'no-cors',
                   'Sec-Fetch-Site': 'cross-site',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
        json = {
            "gmkey": "OTHER",
            "gokey": "appcacheTime=0&connectTime=0&delay=10.99&domReadyTime=714&effectiveType=4g&firstPaintTime=310&hash=&initDomTreeTime=113&last_pos=130.5%252C381&loadEventTime=51&loadTime=1035&lookupDomainTime=0&page=https%253A%252F%252Fbuy.tmall.com%252Forder%252Fconfirm_order.htm&patch_ver=-&pid=punish-page&query=spm%253Da1z0d.6639537.0.0.undefined&raw_ua=Mozilla%252F5.0%2520(Windows%2520NT%25206.1%253B%2520Win64%253B%2520x64)%2520AppleWebKit%252F537.36%2520(KHTML%252C%2520like%2520Gecko)%2520Chrome%252F86.0.4240.111%2520Safari%252F537.36&readyStart=10&redirectTime=0&referrer=https%253A%252F%252Fcart.taobao.com%252F&rel=&requestTime=147&scr=1920x1080&spm_a=0&spm_b=0&tillDomLookupEndTime=10&tillDomReadyTime=280&tillResponseEndTime=167&title=%25E9%25AA%258C%25E8%25AF%2581%25E7%25A0%2581%25E6%258B%25A6%25E6%2588%25AA&totalTime=1045&tracker_ver=4.0.0&type=3&ua=Mozilla%252F5.0%2520(Windows%2520NT%25206.1%253B%2520Win64%253B%2520x64)%2520AppleWebKit%252F537.36%2520(KHTML%252C%2520like%2520Gecko)%2520Chrome%252F86.0.4240.111%2520Safari%252F537.36&uid=b682bbeb3edea6620c2257ce9b3ce628__1.1.1&unloadEventTime=0",
            "logtype": "2"
        }
        r = s.post(url, data=data, headers=headers, json=json)
        print(r.status_code)
        print(r.raise_for_status())
        print(r.reason)
        fg = (r.text.encode('GBK', 'ignore').decode('GBk'))
        DE1 = re.search(r'"reason":"(.*?)"', fg)
        print(fg)

    def post_demo2(self):
        url = "https://gm.mmstat.com/x.p.d"
        data = {"gmkey": "OTHER",
                "gokey": "_s%3D1611713061163%26_e%3D1611713072150%26from%3Dbeforeunload%26uidaplus%3D1085830744%26_hng%3DCN%25257Czh-CN%25257CCNY%25257C156%26aws%3D1%26jsver%3Daplus_std%26lver%3D8.14.8%26pver%3D0.7.11%26cache%3D44a774d%26page_cna%3Dnl8ZGHHK9kYCAduHteKJcpFo%26_slog%3D0",
                "cna": "nl8ZGHHK9kYCAduHteKJcpFo",
                "_p_url": "https%3A%2F%2Fbuy.tmall.com%2Forder%2Fconfirm_order.htm%3Fspm%3Da1z0d.6639537.0.0.undefined",
                "_gr_uid_": "1085830744",
                "spm-cnt": "0.0.0.0.2eb5QK5cQK5cL1",
                "logtype": "2"}
        headers = {'Content-Type': 'text/plain;charset=UTF-8',
                   'Sec-Fetch-Dest': 'empty',
                   'Sec-Fetch-Mode': 'no-cors',
                   'Sec-Fetch-Site': 'cross-site',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
        json = {
            "gmkey": "OTHER",
            "gokey": "_s%3D1611713061163%26_e%3D1611713072150%26from%3Dbeforeunload%26uidaplus%3D1085830744%26_hng%3DCN%25257Czh-CN%25257CCNY%25257C156%26aws%3D1%26jsver%3Daplus_std%26lver%3D8.14.8%26pver%3D0.7.11%26cache%3D44a774d%26page_cna%3Dnl8ZGHHK9kYCAduHteKJcpFo%26_slog%3D0",
            "cna": "nl8ZGHHK9kYCAduHteKJcpFo",
            "_p_url": "https%3A%2F%2Fbuy.tmall.com%2Forder%2Fconfirm_order.htm%3Fspm%3Da1z0d.6639537.0.0.undefined",
            "_gr_uid_": "1085830744",
            "spm-cnt": "0.0.0.0.2eb5QK5cQK5cL1",
            "logtype": "2"
        }
        r = s.post(url, data=data, headers=headers,json=json)
        print(r.status_code)
        print(r.status_code)
        print(r.raise_for_status())
        print(r.reason)
        fg = (r.text.encode('GBK', 'ignore').decode('GBk'))
        DE1 = re.search(r'"reason":"(.*?)"', fg)
        print(fg)




