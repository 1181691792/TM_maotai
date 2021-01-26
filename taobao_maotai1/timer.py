# -*- coding:utf-8 -*-
import time
import requests
import json

from datetime import datetime
from tb_logger import logger
from config import global_config


class Timer(object):
    def __init__(self, sleep_interval=0.5):

        self.buy_time = datetime.strptime(global_config.getRaw('config','buy_time'), "%Y-%m-%d %H:%M:%S.%f")
        self.buy_time_ms = int(time.mktime(self.buy_time.timetuple()) * 1000.0 + self.buy_time.microsecond / 1000)
        self.sleep_interval = sleep_interval

        self.diff_time = self.local_jd_time_diff()

    def jd_time(self):
        """
        从淘宝服务器获取时间毫秒
        :return:
        """

        url = 'http://api.m.taobao.com/rest/api3.do?api=mtop.common.getTimestamp'
        ret = requests.get(url).text
        js = json.loads(ret)
        v=js["data"]
        a=dict(v).values()
        b=list(a)
        return int(b[0])

    def local_time(self):
        """
        获取本地毫秒时间
        :return:
        """
        return int(round(time.time() * 1000))

    def local_jd_time_diff(self):
        """
        计算本地与淘宝服务器时间差
        :return:
        """
        return self.local_time() - self.jd_time()

    def start(self):
        logger.info('正在等待到达设定时间:{}，检测本地时间与淘宝服务器时间误差为【{}】毫秒'.format(self.buy_time, self.diff_time))
        while True:


            if self.local_time() - self.diff_time >= self.buy_time_ms:
                logger.info('时间到达，开始执行……')
                break
            else:
                time.sleep(self.sleep_interval)
