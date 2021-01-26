# coding=utf-8
from test_taobaologin import *
import  time

#账号
loginId = ''

#抓包数据
umidToken = '',
ua = ''

#加密密码，抓包可得
password2 = ''


ul = UsernameLogin(loginId, umidToken, ua, password2)
ul.login()
ul.get_taobao_nick_name()
Timer().start()
try:
    ul.check_demo1()
except:
    pass
for i in range(0,6):
    time.sleep(0.5)
    ul.check_demo()