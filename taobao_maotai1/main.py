# coding=utf-8
from test_taobaologin import *
import threading
import  time

#账号
loginId = ''

#抓包数据
umidToken = ''
ua = ''
#加密密码，抓包可得
password2 = ''

# for i in range(0,30):
#     time.sleep(2)
#     ul.check_demo()

exitFlag = 0

class myThread (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        print ("开始线程：" + self.name)
        ul = UsernameLogin(loginId, umidToken, ua, password2)
        ul.login()
        ul.get_taobao_nick_name()

        Timer().start()
        try:
            ul.check_demo1()
            # ul.post_demo1()
            # ul.post_demo2()
        except:
            # ul.post_demo1()
            # ul.post_demo2()
            pass
        for i in range(0,30):
            time.sleep(2)
            ul.check_demo()
        print ("退出线程：" + self.name)

def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            threadName.exit()
        time.sleep(delay)
        print ("%s: %s" % (threadName, time.ctime(time.time())))
        counter -= 1

# 创建新线程
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# 开启新线程
thread1.start()
thread2.start()
thread1.join()
thread2.join()
print ("退出主线程")
