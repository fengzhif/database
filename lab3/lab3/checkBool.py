def checkSequence(data):
    values = set()
    for te_dict in data:
        value = te_dict['排名']
        if value in values:
            return False
        values.add(value)
    return True


def checkAuthor(data):
    cnt = 0
    for te_dict in data:
        cnt = cnt + int(te_dict['是否通讯作者'])
    return cnt == 1


def checkBunds(data, goal):
    cnt = 0.0
    for te_dict in data:
        cnt = cnt + float(te_dict['承担经费'])
    return abs(goal - cnt) < 1e-9


def checkId(data):
    values = set()
    for te_dict in data:
        value = te_dict['工号']
        if value in values:
            return False
        values.add(value)
    return True


def checkCourse(data, goal):
    cnt = 0
    for te_dict in data:
        cnt = cnt + int(te_dict['承担学时'])
    return cnt == goal
