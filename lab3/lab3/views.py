from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django import forms
import re

from models.paper import paper
from models.teacher import teacher
from models.project import project
from models.course import course
from . import checkBool


@csrf_exempt
def signin(request: HttpRequest):
    if request.method == 'POST':
        data = request.POST.dict()
        if data['user'] == 'lab3' and data['password'] == 'zhang':
            return render(request, 'index.html')
    return render(request, 'signin.html')


def index(request: HttpRequest):
    return render(request, 'index.html')


def paper_search(request: HttpRequest):
    te = teacher()
    pa = paper()
    paper_list = []
    teacher_information = {}
    if 'query' in request.GET.dict():
        query = request.GET.dict()['query']
        try:
            result = te.search_id(query)
        except Exception as e:
            #  return HttpResponse(e)
            return render(request, 'paper/search.html', {'error': e})
        if len(result) == 0:
            #  return HttpResponse('error:该工号无对应教师')
            return render(request, 'paper/search.html', {'error': 'error:该工号无对应教师'})
        teacher_information = result
        te_id = result['工号']
        results = pa.paper_search_all(te_id)
        if len(results) > 0:
            paper_list = results
        return render(request, 'paper/search.html', {
            'teacher': teacher_information,
            'num': len(paper_list),
            'paper_list': paper_list
        })
    if request.method == 'POST':
        paper_id = request.POST.dict()['序号']
        te_id = request.POST.dict()['工号']
        try:
            pa.delete(paper_id, te_id)
        except Exception as e:
            return HttpResponse(e)
        return HttpResponse('success')
    return render(request, 'paper/search.html')


@csrf_exempt
def paper_insert(request: HttpRequest):
    if request.method == 'POST':
        pa = paper()
        data = request.POST.dict()
        try:
            pa.information_insert(data)
        except Exception as e:
            return HttpResponse(e)
        return HttpResponse('success')
    return render(request, 'paper/insert.html')


@csrf_exempt
def paper_update(request: HttpRequest):
    pa = paper()
    tea = teacher()
    paper_id = request.path[7:12]
    te_id = request.path[12:17]
    if request.method == 'POST':
        data = request.POST.dict()
        data['序号'] = paper_id
        data['工号'] = te_id
        try:
            pa.update(data)
        except Exception as e:
            return HttpResponse(e)
        return HttpResponse('success')
    else:
        data = pa.search(paper_id)
        te = pa.search_teacher(te_id, paper_id)
        te_ = tea.search_id(te_id)
        data['工号'] = te['工号']
        data['排名'] = te['排名']
        data['是否通讯作者'] = te['是否通讯作者']
        data['姓名'] = te_['姓名']
        return render(request, 'paper/update.html', data)


class projectForm(forms.Form):
    te_id = forms.CharField(label='工号:')
    te_seq = forms.IntegerField(label='排名')
    te_funds = forms.FloatField(label='承担经费')


def project_search(request: HttpRequest):
    te = teacher()
    pro = project()
    project_list = []
    teacher_information = {}
    if 'query' in request.GET.dict():
        query = request.GET.dict()['query']
        try:
            result = te.search_id(query)
        except Exception as e:
            #  return HttpResponse(e)
            return render(request, 'project/search.html', {'error': e})
        if len(result) == 0:
            #  return HttpResponse('error:该工号无对应教师')
            return render(request, 'project/search.html', {'error': 'error:该工号无对应教师'})
        teacher_information = result
        te_id = result['工号']
        results = pro.project_search_all(te_id)
        if len(results) > 0:
            project_list = results
        return render(request, 'project/search.html', {
            'teacher': teacher_information,
            'num': len(project_list),
            'project_list': project_list
        })
    if request.method == 'POST':
        pro_id = request.POST.dict()['项目号']
        te_id = request.POST.dict()['工号']
        try:
            pro.delete(pro_id, te_id)
        except Exception as e:
            return HttpResponse(e)
        return HttpResponse('success')
    return render(request, 'project/search.html')


def project_insert(request: HttpRequest):
    if request.method == 'POST':
        form_count = int(request.POST.get('form_count'))
        data = request.POST.dict()
        pro_information = {
            '项目号': data['项目号'],
            '项目名称': data['项目名称'],
            '项目来源': data['项目来源'],
            '项目类型': data['项目类型'],
            '总经费': data['总经费'],
            '开始年份': data['开始年份'],
            '结束年份': data['结束年份']
        }
        te_list = []
        for i in range(form_count):
            te = {
                '工号': data[str(i) + '_id'],
                '排名': data[str(i) + '_rank'],
                '承担经费': data[str(i) + '_funds']
            }
            te_list.append(te)
        if not checkBool.checkSequence(te_list):
            return HttpResponse('error:教师排名重复')
        if not checkBool.checkBunds(te_list, float(pro_information['总经费'])):
            return HttpResponse('error:经费不一致')
        pro = project()
        try:
            pro.insert(pro_information, te_list)
        except Exception as e:
            return HttpResponse(e)
        #    for te in te_list:
        #        try:
        #            pro.insert_information(pro_information['项目号'], te)
        #        except Exception as e:
        #            return HttpResponse(e)
        return HttpResponse('success')
    return render(request, 'project/insert.html')


def project_update(request: HttpRequest):
    pro = project()
    pro_id = request.path[9:14]
    if request.method == 'POST':
        data = request.POST.dict()
        data['项目号'] = pro_id
        try:
            pro.update(data)
        except Exception as e:
            return HttpResponse(e)
        te_list = pro.teacher_search_all(data['项目号'])
        for te in te_list:
            pro.delete_teacher(data['项目号'], te['工号'])
        form_count = int(request.POST.get('form_count'))
        te_list_new = []
        for i in range(form_count):
            te = {
                '工号': data[str(i) + '_id'],
                '排名': data[str(i) + '_rank'],
                '承担经费': data[str(i) + '_funds']
            }
            te_list_new.append(te)
        if not checkBool.checkSequence(te_list_new):
            return HttpResponse('error:教师排名重复')
        if not checkBool.checkBunds(te_list_new, float(data['总经费'])):
            return HttpResponse('error:经费不一致')
        for te in te_list_new:
            try:
                pro.insert_information(data['项目号'], te)
            except Exception as e:
                return HttpResponse(e)
        return HttpResponse('success')
    else:
        te_list = pro.teacher_search_all(pro_id)
        pro_information = pro.search(pro_id)
        return render(request, 'project/update.html', {
            'project': pro_information,
            'te_list': te_list
        })


def course_search(request: HttpRequest):
    te = teacher()
    cou = course()
    course_list = []
    teacher_information = {}
    if 'query' in request.GET.dict():
        query = request.GET.dict()['query']
        try:
            result = te.search_id(query)
        except Exception as e:
            return render(request, 'project/search.html', {'error': e})
        if len(result) == 0:
            return render(request, 'project/search.html', {'error': 'error:该工号无对应教师'})
        teacher_information = result
        te_id = result['工号']
        results = cou.course_search_all(te_id)
        if len(results) > 0:
            course_list = results
        return render(request, 'course/search.html', {
            'teacher': teacher_information,
            'num': len(course_list),
            'course_list': course_list
        })
    if request.method == 'POST':
        cou_id = request.POST.dict()['课程号']
        te_id = request.POST.dict()['工号']
        te_time=request.POST.dict()['承担学时']
        try:
            cou.delete(cou_id, te_id,int(te_time))
        except Exception as e:
            return HttpResponse(e)
        return HttpResponse('success')
    return render(request, 'course/search.html')


def course_insert(request: HttpRequest):
    if request.method == 'POST':
        form_count = int(request.POST.get('form_count'))
        data = request.POST.dict()
        cou = course()
        if re.match("^[0-9]{4}$", data['年份']) is None:
            return HttpResponse('error:年份格式有误')
        course_information = cou.search(data['课程号'])
        if len(course_information) == 0:
            return HttpResponse('error:该课程不存在，请检查课程号')
        te_list = []
        for i in range(form_count):
            te = {
                '工号': data[str(i) + '_id'],
                '课程号': data['课程号'],
                '年份': data['年份'],
                '学期': data['学期'],
                '承担学时': data[str(i) + '_time']
            }
            te_list.append(te)
        if not checkBool.checkCourse(te_list, course_information['学时数']):
            return HttpResponse("error:学时不一致，该课程学时数为 '%s'" % course_information['学时数'])
        try:
            cou.insert(te_list)
        except Exception as e:
            return HttpResponse(e)
        return HttpResponse('success')
    return render(request, 'course/insert.html')


def course_update(request: HttpRequest):
    cou = course()
    cou_id = request.path[8:13]
    cou_year = request.path[13:17]
    cou_term = request.path[17:18]
    if request.method == 'POST':
        data = request.POST.dict()
        data['课程号'] = cou_id
        course_information = cou.search(cou_id)
        te_list = cou.teacher_search_all(cou_id, int(cou_year), int(cou_term))
        for te in te_list:
            cou.delete_teacher(data['课程号'], te['工号'])
        form_count = int(request.POST.get('form_count'))
        te_list_new = []
        for i in range(form_count):
            te = {
                '工号': data[str(i) + '_id'],
                '课程号': data['课程号'],
                '年份': data['年份'],
                '学期': data['学期'],
                '承担学时': data[str(i) + '_time']
            }
            te_list_new.append(te)
        if not checkBool.checkCourse(te_list_new, course_information['学时数']):
            return HttpResponse('error:学时不一致')
        try:
            cou.insert(te_list_new)
        except Exception as e:
            return HttpResponse(e)
        return HttpResponse('success')
    else:
        te_list = cou.teacher_search_all(cou_id, cou_year, cou_term)
        course_information = cou.search(cou_id)
        course_information['年份'] = cou_year
        course_information['学期'] = cou_term
        return render(request, 'course/update.html', {
            'course': course_information,
            'te_list': te_list
        })
