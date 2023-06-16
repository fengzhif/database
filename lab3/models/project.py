import string
import re
import pymysql
from typing import List


class project:
    def __init__(self) -> None:
        self.db = pymysql.connect(host='localhost',
                                  user='root',
                                  password='zhang',
                                  database='lab3')

    # 项目号
    # 项目名称
    # 项目来源
    # 项目类型
    # 总经费
    # 开始年份
    # 结束年份
    def check(self, data: dict):
        if re.match("^[0-9A-Za-z]{5}$", data['项目号']) is None:
            raise Exception('error:项目号格式有误')
        elif len(data['项目名称']) > 256:
            raise Exception('error:项目名称过长')
        elif len(data['项目来源']) > 256:
            raise Exception('error:项目来源过长')
        # 项目类型由下拉菜单确定
        elif re.match(r"^[+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)$", data['总经费']) is None:
            raise Exception('error: 总经费格式有问题')
        elif re.match("^[1-2][0-9]{3}$", data['开始年份']) is None:
            raise Exception('error:开始年份格式有误')
        elif re.match("^[1-2][0-9]{3}$", data['结束年份']) is None:
            raise Exception('error:结束年份格式有误')
        elif int(data['开始年份']) > int(data['结束年份']):
            raise Exception('error:开始时间在结束时间之后')

    def insert(self, data: dict, te_list: List[dict]):
        self.check(data)
        cursor = self.db.cursor()
        sql0 = "select * from 项目 where 项目号='%s'" % data['项目号']
        cursor.execute(sql0)
        tmp = cursor.fetchone()
        if tmp is not None:
            raise Exception('该项目已经存在')
        sql = "insert into 项目 values('%s','%s','%s',%d,%f,%d,%d)" % \
              (data['项目号'], data['项目名称'], data['项目来源'], int(data['项目类型']), float(data['总经费']),
               int(data['开始年份']),
               int(data['结束年份']))
        try:
            cursor.execute(sql)
            for index, te in enumerate(te_list):
                sql1 = "select * from 教师 where 工号='%s'" % te['工号']
                cursor.execute(sql1)
                result = cursor.fetchone()
                if result is None:
                    raise Exception('error:第%d教师对应工号不存在，请输入正确工号' % (index + 1))
                if not te['排名'].isdigit():
                    raise Exception('error:排名需为数字')
                if re.match(r"^[+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)$", te['承担经费']) is None:
                    raise Exception('error:经费需为数字')
                sql2 = "insert into 承担项目 values('%s','%s',%d,%f)" % (
                    te['工号'], data['项目号'], int(te['排名']), float(te['承担经费']))
                cursor.execute(sql2)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()

    def delete(self, pro_id: string, te_id: string):
        cursor = self.db.cursor()
        sql1 = "select * from 承担项目 where 项目号='%s' " % pro_id
        cursor.execute(sql1)
        cnt = cursor.rowcount
        if cnt == 1:
            sql = "delete from 承担项目 where 项目号='%s' and 工号='%s'" % (pro_id, te_id)
            try:
                cursor.execute(sql)
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise Exception(e)
            sql2 = "delete from 项目 where 项目号='%s' " % pro_id
            try:
                cursor.execute(sql2)
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise Exception(e)
        else:
            raise Exception('error:该教师不是项目的唯一负责人，直接删除会导致经费不一致，请通过“查看&修改”完成教师的删除')
        cursor.close()

    def delete_all(self, pro_id: string):
        sql = "delete from 承担项目 where 项目号='%s'" % pro_id
        sql1 = "delete from 项目 where 项目号='%s'" % pro_id
        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            cursor.execute(sql1)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()

    def update(self, data: dict):
        self.check(data)
        cursor = self.db.cursor()
        sql = "update 项目 set 项目号='%s',项目名称='%s',项目来源='%s',项目类型=%d,总经费=%f ," \
              "开始年份=%d,结束年份=%d where 项目号='%s' " % \
              (data['项目号'], data['项目名称'], data['项目来源'], int(data['项目类型']),
               float(data['总经费']), int(data['开始年份']), int(data['结束年份']), data['项目号'])
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()

    def update_all(self, data: dict, te_list: List[dict], te_list_new: List[dict]):
        self.check(data)
        cursor = self.db.cursor()
        sql1 = "update 项目 set 项目名称='%s',项目来源='%s',项目类型=%d,总经费=%f ," \
               "开始年份=%d,结束年份=%d where 项目号='%s' " % \
               (data['项目名称'], data['项目来源'], int(data['项目类型']),
                float(data['总经费']), int(data['开始年份']), int(data['结束年份']), data['项目号'])
        try:
            cursor.execute(sql1)
            for te in te_list:
                sql2 = "delete from 承担项目 where 项目号='%s' and 工号='%s'" % (data['项目号'], te['工号'])
                cursor.execute(sql2)
            for index, te in enumerate(te_list_new):
                sql0 = "select * from 教师 where 工号='%s'" % te['工号']
                cursor.execute(sql0)
                tmp = cursor.fetchone()
                if tmp is None:
                    raise Exception('error:第%d教师对应工号不存在，请检查工号输入' % (index + 1))
                sql3 = "insert into 承担项目 values('%s','%s',%d,%f)" % (
                    te['工号'], data['项目号'], int(te['排名']), float(te['承担经费']))
                cursor.execute(sql3)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()

    def search(self, id: string):
        cursor = self.db.cursor()
        sql = "select * from 项目 where 项目号='%s'" % id
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

    def information_check(self, te: dict):
        cursor = self.db.cursor()
        sql = "select * from 教师 where 工号='%s'" % te['工号']
        cursor.execute(sql)
        result = cursor.fetchone()
        if result is None:
            raise Exception('error:该工号不存在，请输入正确工号')
        if not te['排名'].isdigit():
            raise Exception('error:排名需为数字')
        if re.match(r"^[+]?([0-9]+(\.[0-9]+)?|\.[0-9]+)$", te['承担经费']) is None:
            raise Exception('error:经费需为数字')

    def insert_information(self, id: string, teacher: dict):
        self.information_check(teacher)
        cursor = self.db.cursor()
        sql = "insert into 承担项目 values('%s','%s',%d,%f)" % (
            teacher['工号'], id, int(teacher['排名']), float(teacher['承担经费']))
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()

    def project_search_all(self, te_id: string):
        cursor = self.db.cursor()
        project_list = []
        sql1 = "select * from 承担项目 where 工号='%s'" % te_id
        cursor.execute(sql1)
        results = cursor.fetchall()
        if len(results) == 0:
            cursor.close()
            return project_list
        for item in results:
            result = self.search(item[1])
            if len(result) > 0:
                result.update({'排名': item[2]})
                result.update({'承担经费': item[3]})
                project_list.append(result)
        cursor.close()
        return project_list

    def teacher_search_all(self, pro_id: string):
        sql = "select * from 承担项目 where 项目号='%s'" % pro_id
        cursor = self.db.cursor()
        cursor.execute(sql)

        def result2dict(result):
            return dict(
                zip([x[0] for x in cursor.description], [x for x in result]))

        result_list = list(map(result2dict, cursor.fetchall()))
        cursor.close()
        return result_list

    def delete_teacher(self, pro_id: string, te_id: string):
        sql = "delete from 承担项目 where 项目号='%s' and 工号='%s'" % (pro_id, te_id)
        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()

# a=project()
# pro1={'项目号':'p001','项目名称':'banksystem','项目来源':'database','项目类型':'1','总经费':'-100','开始年份':'2022','结束年份':'2021'}
