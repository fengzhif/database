import string
import pymysql


# 工号 char(5)
# 姓名 varchar
# 性别 int
# 职称 int
class teacher:
    def __init__(self) -> None:
        self.db = pymysql.connect(host='localhost',
                                  user='root',
                                  password='zhang',
                                  database='lab3')

    def check(self, data: dict):
        if not (str.isalnum(data['工号'])
                and len(data['工号']) == 5):
            raise Exception('error:工号格式有误')
        elif len(data['姓名']) > 256:
            raise Exception('error:姓名过长')
        # 性别和职称由下拉框选择

    def insert(self, data: dict):
        self.check(data)
        cursor = self.db.cursor()
        sql = "insert into 教师 values('%s','%s','%s','%s')" % (data['工号'], data['姓名'], data['性别'], data['职称'])
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()

    def delete(self, id: string):
        cursor = self.db.cursor()
        sql = "delete from 教师 where 工号='%s'" % id
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception('error:教师信息不能删除')
        cursor.close()

    def update(self, data: dict):
        self.check(data)
        cursor = self.db.cursor()
        sql = "update 教师 set 工号='%s',姓名='%s',性别='%s',职称='%s' where 工号='%s'" % \
              (data['工号'], data['姓名'], data['性别'], data['职称'], data['工号'])
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception('error:更新教师的输入格式有误')
        cursor.close()

    def search_id(self, id: string):
        if not (str.isalnum(id)
                and len(id) == 5):
            raise Exception('error:工号格式有误')
        cursor = self.db.cursor()
        sql = "select * from 教师 where 工号='%s'" % id
        cursor.execute(sql)
        tmp=cursor.fetchone()
        if tmp is None:
            cursor.close()
            return {}
        result = dict(
            zip([x[0] for x in cursor.description],
                [x for x in tmp]))
        cursor.close()
        return result

    def search_name(self, name: string):
        cursor = self.db.cursor()
        sql = "select * from 教师 where 姓名 like '%%%s%%'" % name
        cursor.execute(sql)

        def result2dict(result):
            return dict(
                zip([x[0] for x in cursor.description], [x for x in result]))

        result_list = list(map(result2dict, cursor.fetchall()))
        cursor.close()
        return result_list

# a=teacher()
# t1={'工号':'00001','姓名':'张五','性别':'1','职称':'1'}
# a.update(t1)
# a.insert(t1)
# print(a.search_id('00001'))
# print(a.search_name('张'))
