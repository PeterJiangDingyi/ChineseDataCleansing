# -*- coding:utf-8 -*-
# @Time       :2023/5/5 10:59
# @AUTHOR     :YUNYI
# @SOFTWARE   :instruct-data-clean
# @DESC       : 读取小红书数据

from utils.DorisTools import DorisLogger, DorisSession
from xToolkit import xfile


class read_data(object):
    def __init__(self):
        """
        初始化链接信息
        """
        config = {
            'fe_servers': ['10.200.2.103:9030'],
            'database': 'dwd_jd',
            'user': 'shenxuyang',
            'passwd': 'Frontis2021xy',
            'prot': 9030,
            'charset': 'utf8'
        }
        self.client = DorisSession(doris_config=config)
        self.logger = DorisLogger

    def get_xhs_note(self, date: str):
        """
        查询指定日期小红书数据：date 2023-04-01
        返回格式：[{},{}]
        """
        self.logger.info("开始执行日期{}的数据".format(date))
        sql = """
        select note_id,title,content,like_count,collect_count,share_count,comment_count from dwd_xhs.dwd_xhs_note 
        where date(created_at) = '{dt}'
        group by note_id, title, content, like_count, collect_count, share_count, comment_count
        """.format(dt=date)
        res = self.client.select(sql)
        return res


class read_excel(object):
    def excel_read(self, file_name: str, max_lines: int = 100000000):
        """
        excel读取工具类
        :param file_name:
        :param max_lines:
        :return:
        """
        res = xfile.read(file_name).excel_to_dict(max=max_lines)
        return res
