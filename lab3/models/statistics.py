import string
import re
import pymysql
from typing import List


class statistics:
    def __init__(self) -> None:
        self.db = pymysql.connect(host='localhost',
                                  user='root',
                                  password='zhang',
                                  database='lab3')

    def teacher_search(self, name: string):
        cursor = self.db.cursor()
        sql = "select * from 教师 where 姓名 like '%%%s%%'" % name
        cursor.execute(sql)

        def result2dict(result):
            if result is None:
                return {}
            return dict(
                zip([x[0] for x in cursor.description], [x for x in result]))

        result_list = list(map(result2dict, cursor.fetchall()))
        cursor.close()
        return result_list

    def course_search(self, name: string):
        cursor = self.db.cursor()
        sql = "select * from 课程 where 课程名称 like '%%%s%%'" % name
        cursor.execute(sql)

        def result2dict(result):
            if result is None:
                return {}
            return dict(
                zip([x[0] for x in cursor.description], [x for x in result]))

        result_list = list(map(result2dict, cursor.fetchall()))
        cursor.close()
        return result_list

    def search(self, id: string, start: string, end: string):
        cursor = self.db.cursor()
        sql1 = "select * from 教师 where 工号='%s'" % id
        cursor.execute(sql1)
        tmp = cursor.fetchone()
        teacher = dict(
            zip([x[0] for x in cursor.description],
                [x for x in tmp]))
        sql2 = "select * from (select * from 主讲课程 where 工号='%s' and 年份>=%d and 年份<=%d)tc,课程 c " \
               "where tc.课程号=c.课程号" % (id, int(start), int(end))
        cursor.execute(sql2)

        def result2dict(result):
            if result is None:
                return {}
            return dict(
                zip([x[0] for x in cursor.description], [x for x in result]))

        course_list = list(map(result2dict, cursor.fetchall()))
        sql3 = "select * from (select * from 发表论文 where 工号='%s')pa,论文 p " \
               "where pa.序号=p.序号 and p.发表年份>=%d and p.发表年份<=%d " % (id, int(start), int(end))
        cursor.execute(sql3)
        paper_list = list(map(result2dict, cursor.fetchall()))
        sql4 = "select * from (select * from 承担项目 where 工号='%s')pro,项目 p " \
               "where pro.项目号=p.项目号 and p.结束年份>=%d and p.开始年份<=%d " % (id, int(start), int(end))
        cursor.execute(sql4)
        project_list = list(map(result2dict, cursor.fetchall()))
        result = {
            'teacher': teacher,
            'course_list': course_list,
            'paper_list': paper_list,
            'project_list': project_list
        }
        return result
