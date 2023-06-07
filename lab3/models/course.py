import string
import re
import pymysql
from typing import List


class course:
    def __init__(self) -> None:
        self.db = pymysql.connect(host='localhost',
                                  user='root',
                                  password='zhang',
                                  database='lab3')

    # 课程号
    # 课程名称
    # 学时数
    # 课程性质
    def search(self, id: string):
        cursor = self.db.cursor()
        sql = "select * from 课程 where 课程号='%s'" % id
        cursor.execute(sql)
        result = {}
        tmp = cursor.fetchone()
        if tmp is None:
            return result
        result = dict(
            zip([x[0] for x in cursor.description],
                [x for x in tmp]))
        cursor.close()
        return result

    def insert(self, te_list: List[dict]):
        cursor = self.db.cursor()
        try:
            for index, te in enumerate(te_list):
                sql0 = "select * from 教师 where 工号='%s'" % te['工号']
                cursor.execute(sql0)
                tmp = cursor.fetchone()
                if tmp is None:
                    raise Exception('error:第%d教师对应工号不存在，请检查工号输入' % (index + 1))
                sql = "insert into 主讲课程 values('%s','%s',%d,%d,%d)" % \
                      (te['工号'], te['课程号'], int(te['年份']), int(te['学期']), int(te['承担学时']))
                cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()

    def delete(self, cou_id: string, te_id: string, te_time: int):
        cursor = self.db.cursor()
        sql1 = "select * from 课程 where 课程号='%s' " % cou_id
        cursor.execute(sql1)
        result = dict(
            zip([x[0] for x in cursor.description],
                [x for x in cursor.fetchone()])
        )
        if result['学时数'] == te_time:
            sql = "delete from 主讲课程 where 课程号='%s' and 工号='%s'" % (cou_id, te_id)
            try:
                cursor.execute(sql)
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise Exception(e)
        else:
            raise Exception('error:该教师不是课程的唯一主讲人，直接删除会导致学时不一致，请通过“查看&修改”完成教师的删除')
        cursor.close()

    def update_all(self, data: dict, te_list: List[dict], te_list_new: List[dict]):
        cursor = self.db.cursor()
        try:
            for te in te_list:
                sql2 = "delete from 主讲课程 where 课程号='%s' and 工号='%s'" % (data['课程号'], te['工号'])
                cursor.execute(sql2)
            for index, te in enumerate(te_list_new):
                sql0 = "select * from 教师 where 工号='%s'" % te['工号']
                cursor.execute(sql0)
                tmp = cursor.fetchone()
                if tmp is None:
                    raise Exception('error:第%d教师对应工号不存在，请检查工号输入' % (index + 1))
                sql3 = "insert into 主讲课程 values('%s','%s',%d,%d,%d)" % \
                       (te['工号'], te['课程号'], int(te['年份']), int(te['学期']), int(te['承担学时']))
                cursor.execute(sql3)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()

    def course_search_all(self, te_id: string):
        cursor = self.db.cursor()
        course_list = []
        sql1 = "select * from 主讲课程 where 工号='%s'" % te_id
        cursor.execute(sql1)
        results = cursor.fetchall()
        if len(results) == 0:
            cursor.close()
            return course_list
        for item in results:
            result = self.search(item[1])
            if len(result) > 0:
                result.update({'年份': item[2]})
                result.update({'学期': item[3]})
                result.update({'承担学时': item[4]})
                course_list.append(result)
        cursor.close()
        return course_list

    def teacher_search_all(self, cou_id: string, cou_year: int, cou_term: int):
        sql = "select * from 主讲课程 where 课程号='%s' and 年份=%d and 学期=%d " % (
            cou_id, int(cou_year), int(cou_term))
        cursor = self.db.cursor()
        cursor.execute(sql)

        def result2dict(result):
            return dict(
                zip([x[0] for x in cursor.description], [x for x in result]))

        result_list = list(map(result2dict, cursor.fetchall()))
        cursor.close()
        return result_list

    def delete_teacher(self, cou_id: string, te_id: string):
        sql = "delete from 主讲课程 where 课程号='%s' and 工号='%s'" % (cou_id, te_id)
        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()
