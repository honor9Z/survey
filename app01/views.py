from django.shortcuts import render,HttpResponse,redirect
from app01 import models
from app01.form import *
# Create your views here.
def log_in(request):
    if request.method=="POST":
        user=request.POST.get("user")
        pwd=request.POST.get("pwd")
        obj=models.Student.objects.filter(user=user,pwd=pwd)
        print(obj)
        if obj:
            return redirect('/index/')
        else:
            return HttpResponse('错误')

    return render(request,'log_in.html')




def index(request):
    print('================')
    q_all=models.Questionnaire.objects.all()
    cls_all=models.ClassList.objects.all()
    stu_all=models.Student.objects.all()
    return render(request,'index.html',{'q_all':q_all,'cls_all':cls_all,'stu_all':stu_all})

import json
def edit(request,pid):
    print('222222222222')
    # if request.is_ajax():
    #     edit_form = Question_form()
    #     response={'form':edit_form}
    #     return HttpResponse(json.dumps(response))
    #
    # edit_form=Question_form()
    # edit_obj=models.Questionnaire.objects.get(id=id)
    # return render(request,'edit.html',{'edit_obj':edit_obj,'edit_form':edit_form})


    """
    问题
    :param request:
    :param pid: 问卷ID
    :return:
    """
    if request.method=='GET':
        print('编辑问卷页面')
        def inner():
            que_list = models.Question.objects.filter(naire_id=pid)  # [Question,Question,Question]
            print('333333',que_list)
            if not que_list:
                # 新创建的问卷，其中还么有创建问题
                form = QuestionModelForm()
                print('-------',form)
                yield {'form': form, 'obj': None, 'option_class': 'hide', 'options': None}
            else:
                # 含问题的问卷
                for que in que_list:
                    form = QuestionModelForm(instance=que)
                    temp = {'form': form, 'obj': que, 'option_class': 'hide', 'options': None}
                    if que.tp == 2:
                        temp['option_class'] = ''
                        temp['add_a'] = '添加选项'
                        temp['add_pic'] = 'glyphicon glyphicon-plus add-ques'

                        # 获取当前问题的所有选项？que
                        def inner_loop(quee):
                            option_list = models.Option.objects.filter(qs=quee)
                            for v in option_list:
                                print('======',v)
                                yield {'form': OptionModelForm(instance=v), 'obj': v}

                        # temp['options'] = inner_loop(que)
                        temp['options'] = inner_loop(que)
                    print('tttttt',temp)
                    yield temp

        return render(request, 'edit.html', {'form_list': inner(),'pid':pid})

    else:
        print('~~~~~~~~~~~~~保存问卷中')
        ret = {'status': True, 'msg': None, 'data': None}
        try:
            # 新提交的数据:
            plist=json.loads(request.POST.get('plist'))
            print('提交过来的问题',plist)
            for item in plist:
                item['id']=int(item.get('id'))
                item['tp']=int(item.get('tp'))

                if len(item['options'])>0:
                    for i in item['options']:
                        i['id']=int(i['id'])
                        i['score']=int(i['score'])

            print('转义后的问题',plist)
            # ajax_post_list = [
            #     {
            #         'id': 2,
            #         'caption': "鲁宁爱不是番禺？？",
            #         'tp': 1,
            #
            #     },
            #     {
            #         'id': None,
            #         'caption': "八级哥肾好不好？",
            #         'tp': 3
            #     },
            #     {
            #         'id': None,
            #         'caption': "鲁宁脸打不打？",
            #         'tp': 2,
            #         "options": [
            #             {'id': 1, 'name': '绿', 'score': 10},
            #             {'id': 2, 'name': '翠绿', 'score': 8},
            #         ]
            #     },
            # ]

            question_list = models.Question.objects.filter(naire_id=pid)

            # 用户提交的所有问题ID
            post_id_list = [i.get('id') for i in plist if i.get('id')]
            print('用户提交的所有问题ID',post_id_list)

            # 数据库中获取的现在已有的问题ID
            question_id_list = [i.id for i in question_list]
            print('数据库中获取的现在已有的问题ID',question_id_list)

            # 数据库中的那些ID需要删除？
            del_id_list = set(question_id_list).difference(set(post_id_list))

            print('数据库中的那些ID需要删除',del_id_list)

            # 循环ajax提交过来的所有问题信息
            for item in plist:
                print(item)
                # item就是用户提交过来的一个问题
                qid = item.get('id')
                caption = item.get('caption')
                tp = item.get('tp')
                options = item.get('options')
                print(qid,caption,tp,options)

                if qid not in question_id_list:
                    # 要新增
                    new_question_obj = models.Question.objects.create(caption=caption, tp=tp)
                    if tp == 2:
                        for op in options:
                            models.Option.objects.create(qs=new_question_obj, name=op.get('name'),
                                                         score=op.get('score'))
                    print('新增问题成功')

                else:
                    # 要更新
                    print('要更新',qid)
                    models.Question.objects.filter(id=qid).update(caption=caption, tp=tp)
                    print('更新非单选问题成功')

                    if not options:
                        #类型由单选改为了其他类型，就需要将想关联的选项删除
                        models.Option.objects.filter(qs_id=qid).delete()
                        print('删除选项成功')
                    else:
                        # 更新选项（不推荐）
                        models.Option.objects.filter(qs_id=qid).delete()
                        for op in options:
                            models.Option.objects.create(name=op.get("name"), score=op.get('score'), qs_id=qid)
                        print('更新选项成功')
            models.Question.objects.filter(id__in=del_id_list).delete()
        except Exception as e:
            ret['msg'] = str(e)
            ret['status'] = False
        print('保存问卷结束')
        return HttpResponse(json.dumps(ret))

def func(val):
    if len(val) < 15:
        raise ValidationError('你太短了')
def score(request, class_id, qn_id):
    """
    :param request:
    :param class_id: 班级ID
    :param qn_id: 问卷ID
    :return:
    """
    # student_id = request.session['student_info']['id']
    student_id = 1
    # 1. 当前登录用户是否是要评论的班级的学生
    ct1 = models.Student.objects.filter(id=student_id, cls_id=class_id).first()
    if not ct1:
        return HttpResponse('你只能评论自己班级的问卷，是不是想转班？')

    # 2. 你是否已经提交过当前问卷答案
    ct2 = models.Answer.objects.filter(stu_id=student_id, question__naire_id=qn_id).first()
    if ct2:
        return HttpResponse('你已经参与过调查，无法再次进行')

    # 3. 展示当前问卷下的所有问题
    # question_list = models.Question.objects.filter(naire_id=qn_id)

    from django.forms import Form
    from django.forms import fields
    from django.forms import widgets

    # # 类：方式一
    # class TestForm(Form):
    #     tp1 = fields.ChoiceField(label='路宁傻不傻？',choices=[ (i,i) for i in range(1,11)],widget=widgets.RadioSelect)
    #     tp2 = fields.ChoiceField(label='路宁傻不傻？',choices=[ (i,i) for i in range(1,11)],widget=widgets.RadioSelect)
    #     tp3 = fields.CharField(label='对路宁的建议？',widget=widgets.Textarea)
    #     tp4 = fields.ChoiceField(label='路宁帽子颜色？',choices=[ (i,i) for i in range(1,11)],widget=widgets.RadioSelect)
    #
    # # 类：方式二
    # MyTestForm = type("MyTestForm",(Form,),{
    #     'tp1': fields.ChoiceField(label='路宁傻不傻？',choices=[ (i,i) for i in range(1,11)],widget=widgets.RadioSelect),
    #     'tp2': fields.ChoiceField(label='路宁傻不傻？',choices=[ (i,i) for i in range(1,11)],widget=widgets.RadioSelect),
    #     'tp3': fields.CharField(label='对路宁的建议？',widget=widgets.Textarea),
    #     'tp4': fields.ChoiceField(label='路宁帽子颜色？',choices=[ (i,i) for i in range(1,11)],widget=widgets.RadioSelect),
    # })
    # return render(request,'score.html',{'question_list':question_list,'form':MyTestForm()})
    question_list = models.Question.objects.filter(naire_id=qn_id)
    field_dict = {}
    for que in question_list:
        if que.tp == 1:
            field_dict['val_%s' % que.id] = fields.ChoiceField(
                label=que.caption,
                error_messages={'required':'必填'},
                widget=widgets.RadioSelect,
                choices=[(i, i) for i in range(1, 11)]
            )
        elif que.tp == 2:
            field_dict['option_id_%s' % que.id] = fields.ChoiceField(
                label=que.caption,
                widget=widgets.RadioSelect,
                choices=models.Option.objects.filter(
                    qs_id=que.id).values_list('id', 'name'))
        else:
            from django.core.exceptions import ValidationError
            from django.core.validators import RegexValidator
            # field_dict['x_%s' % que.id] = fields.CharField(
            #     label=que.caption, widget=widgets.Textarea,validators=[RegexValidator(regex=""),])
            field_dict['content_%s' % que.id] = fields.CharField(
                label=que.caption, widget=widgets.Textarea, validators=[func, ])
    # 类：方式二
    MyTestForm = type("MyTestForm", (Form,), field_dict)

    if request.method == 'GET':
        form = MyTestForm()
        return render(request, 'score.html', {'question_list': question_list, 'form': form})
    else:
        # 15字验证
        # 不允许为空
        form = MyTestForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            # {'x_2': '3', 'x_9': 'sdfasdfasdfasdfasdfasdfasdf', 'x_10': '13'}
            objs = []
            for key,v in form.cleaned_data.items():
                k,qid = key.rsplit('_',1)
                answer_dict = {'stu_id':student_id,'question_id':qid,k:v}
                objs.append(models.Answer(**answer_dict))
            models.Answer.objects.bulk_create(objs)
            return HttpResponse('感谢您的参与!!!')

        return render(request, 'score.html', {'question_list': question_list, 'form': form})