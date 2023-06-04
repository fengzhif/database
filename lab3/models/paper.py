import string
import re
import pymysql


class paper:
    def __init__(self) -> None:
        self.db = pymysql.connect(host='localhost',
                                  user='root',
                                  password='zhang',
                                  database='lab3')

    # 序号 varchar 8
    # 论文名称 varchar
    # 发表源   varchar
    # 发表年份 date
    # 类型    int
    # 级别    int
    def check(self, data: dict):
        if re.match("^[0-9A-Z]{5}$", data['序号']) is None:
            raise Exception('error:序号格式有误')
        elif len(data['论文名称']) > 256:
            raise Exception('error:论文名称过长')
        elif len(data['发表源']) > 256:
            raise Exception('error:发表源内容过长')
        elif re.match("^[0-9]{4}$", data['发表年份']) is None:
            raise Exception('error:发表年份格式有误')
        # 类型和级别通过下拉菜单确定

    def insert(self, data: dict):
        self.check(data)
        sql = "insert into 论文 (序号,论文名称,发表源,发表年份,类型,级别)" \
              " values ('%s','%s','%s',%d,%d,%d)" % \
              (data['序号'], data['论文名称'], data['发表源'], int(data['发表年份']), int(data['类型']),
               int(data['级别']))
        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()

    def delete(self, paper_id: string, te_id: string):
        cursor = self.db.cursor()
        sql = "delete from 发表论文 where 序号='%s' and 工号='%s'" % (paper_id, te_id)
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        sql1 = "select * from 发表论文 where 序号='%s' " % paper_id
        cursor.execute(sql1)
        cnt = cursor.rowcount
        if cnt == 0:
            sql2 = "delete from 论文 where 序号='%s' " % paper_id
            try:
                cursor.execute(sql2)
                self.db.commit()
            except Exception as e:
                self.db.rollback()
                raise Exception(e)
        cursor.close()

    def update(self, data: dict):
        self.check(data)
        sql = "update 论文 set 论文名称='%s',发表源='%s',发表年份=%d,类型=%d,级别=%d where 序号='%s' " % \
              (data['论文名称'], data['发表源'], int(data['发表年份']), int(data['类型']), int(data['级别']),
               data['序号'])
        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        sql1 = "update 发表论文 set 排名=%d , 是否通讯作者=%d where 工号='%s' and 序号='%s'" % \
               (int(data['排名']), int(data['是否通讯作者']), data['工号'], data['序号'])
        try:
            cursor.execute(sql1)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()

    def search(self, id: string):
        cursor = self.db.cursor()
        sql = "select * from 论文 where 序号='%s'" % id
        cursor.execute(sql)
        tmp = cursor.fetchone()
        if tmp is None:
            cursor.close()
            return {}
        else:
            result = dict(
                zip([x[0] for x in cursor.description],
                    [x for x in tmp]))
            cursor.close()
            return result

    def search_teacher(self, te_id: string, pa_id: string):
        cursor = self.db.cursor()
        sql = "select * from 发表论文 where 工号='%s' and 序号='%s'" % (te_id, pa_id)
        cursor.execute(sql)
        result = dict(
            zip([x[0] for x in cursor.description],
                [x for x in cursor.fetchone()])
        )
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

    def information_insert(self, data: dict):
        def result2dict(result):
            if len(result) == 0:
                return {}
            return dict(zip([x[0] for x in cursor.description], [x for x in result]))

        self.information_check(data)
        cursor = self.db.cursor()
        paper_list = self.search(data['序号'])
        if len(paper_list) == 0:
            self.insert(data)
        else:
            if paper_list['论文名称'] != data['论文名称'] or paper_list['发表源'] != data['发表源'] \
                    or paper_list['发表年份'] != int(data['发表年份']) or paper_list['类型'] != int(data['类型']) \
                    or paper_list['级别'] != int(data['级别']):
                raise Exception('error:论文与数据库已存在信息不一样，请重新输入正确信息，或查询后重新输入')
            sql1 = "select * from 发表论文 where 序号='%s'" % data['序号']
            cursor.execute(sql1)
            information_list = list(map(result2dict, cursor.fetchall()))
            if len(information_list) > 0:
                for item in information_list:
                    if item['工号'] == data['工号']:
                        raise Exception('error:该论文发表记录已经存在')
                    elif item['是否通讯作者'] == 1 and int(data['是否通讯作者']) == 1:
                        raise Exception('error:通讯作者已经存在')
                    elif item['排名'] == int(data['排名']):
                        raise Exception('error:论文排名重复')
        sql2 = "insert into 发表论文  values('%s','%s',%d,%d)" % (
            data['工号'], data['序号'], int(data['排名']), int(data['是否通讯作者']))
        try:
            cursor.execute(sql2)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise Exception(e)
        cursor.close()

    def paper_search_all(self, te_id: string):
        cursor = self.db.cursor()
        paper_list = []
        sql1 = "select * from 发表论文 where 工号='%s'" % te_id
        cursor.execute(sql1)
        results = cursor.fetchall()
        if len(results) == 0:
            cursor.close()
            return paper_list
        for item in results:
            result = self.search(item[1])
            if len(result) > 0:
                result.update({'排名': item[2]})
                result.update({'是否通讯作者': item[3]})
                paper_list.append(result)
        cursor.close()
        return paper_list

# a = paper()
# p1 = {'序号':'PA001','论文名称': '教学科研管理', '发表源': 'ustc', '发表年份': '2023','类型':'1','级别':'2','工号':'PA001','排名':'1','是否通讯作者':'1'}
