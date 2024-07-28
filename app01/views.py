from django.shortcuts import render, redirect, HttpResponse
from io import BytesIO
from datetime import datetime
import random
import json
from app01 import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from app01.templates.utils.bootstrap import BootStrapModelForm, BootStrapForm
from app01.templates.utils.pagination import Pagination
from app01.templates.utils.encrypt import md5
from app01.templates.utils.code import check_code
from django import forms
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse

# Create your views here.
def depart_list(request):
    queryset = models.Department.objects.all()
    return render(request, 'depart_list.html', {'queryset': queryset})


def depart_add(request):
    if request.method == "GET":
        return render(request, 'depart_add.html')

    title = request.POST.get('title')

    models.Department.objects.create(title=title)

    return redirect("/depart/list/")


def depart_delete(request):
    nid = request.GET.get("nid")
    models.Department.objects.filter(id=nid).delete()

    return redirect("/depart/list")


def depart_edit(request, nid):
    if request.method == "GET":
        row_object = models.Department.objects.filter(id=nid).first()
        return render(request, 'depart_edit.html', {"row_object": row_object})
    title = request.POST.get('title')

    models.Department.objects.filter(id=nid).update(title=title)

    return redirect("/depart/list/")


def user_list(request):
    query_set = models.UserInfo.objects.all()
    return render(request, 'user_list.html', {"query_set": query_set})


def user_add(request):
    if request.method == "GET":
        context = {
            'gender_choices': models.UserInfo.gender_choice,
            "depart_list": models.Department.objects.all()
        }
        return render(request, 'user_add.html', context)
    user = request.POST.get('name')
    pwd = request.POST.get('pwd')
    age = request.POST.get('age')
    account = request.POST.get('account')
    sex = request.POST.get('sex')
    dp = request.POST.get('dp')
    create = request.POST.get('create')

    models.UserInfo.objects.create(name=user, password=pwd, age=age, account=account,
                                   gender=sex, depart_id=dp, create_time=create)


#######ModelForm示例###########
from django import forms


class UserModelForm(forms.ModelForm):
    class Meta:
        model = models.UserInfo
        fields = ['name', "password", "age", "account", "gender", "create_time", "depart"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环找到所有的插件，添加了class="form-control"
        for name, field in self.fields.items():
            # if name == "password":
            #     continue
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}


def user_model_form_add(request):
    if request.method == "GET":
        form = UserModelForm()
        return render(request, "user_model_form_add.html", {"form": form})

    form = UserModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/user/list/')
    return render(request, 'user_model_form_add.html', {"form": form})


def user_edit(request, nid):
    row_object = models.UserInfo.objects.filter(id=nid).first()

    if request.method == "GET":
        form = UserModelForm(instance=row_object)
        return render(request, 'user_edit.html', {'form': form})

    form = UserModelForm(data=request.POST, instance=row_object)

    if form.is_valid():
        form.save()
        return redirect('/user/list')

    return render(request, 'user_edit.html', {"form": form})


def user_delete(request, nid):
    models.UserInfo.objects.filter(id=nid).delete()
    return redirect('/user/list')


def pretty_list(request):
    data_dict = {}

    search_data = request.GET.get('q', "")
    if search_data:
        data_dict["mobile__contains"] = search_data

    queryset = models.PrettyNum.objects.filter(**data_dict).order_by("-level")

    page_object = Pagination(request, queryset)
    context = {
        "search_data": search_data,

        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 页码
    }
    return render(request, 'pretty_list.html', context)


class PrettyModelForm(forms.ModelForm):
    mobile = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误'), ],
    )

    class Meta:
        model = models.PrettyNum
        fields = ["mobile", 'price', 'level', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环找到所有的插件，添加了class="form-control"
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}


def pretty_add(request):
    if request.method == "GET":
        form = PrettyModelForm()
        return render(request, 'pretty_add.html', {"form": form})

    form = PrettyModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/pretty/list')
    return render(request, 'pretty_add.html', {"form": form})


class PrettyEditModelForm(forms.ModelForm):
    mobile = forms.CharField(
        label="手机号",
        validators=[RegexValidator(r'^1[3-9]\d{9}$', '手机号格式错误'), ],
    )

    class Meta:
        model = models.PrettyNum
        fields = ['mobile', 'price', 'level', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 循环找到所有的插件，添加了class="form-control"
        for name, field in self.fields.items():
            field.widget.attrs = {"class": "form-control", "placeholder": field.label}

    def clean_mobile(self):
        txt_mobile = self.cleaned_data["mobile"]
        exists = models.PrettyNum.objects.exclude(id=self.instance.pk).filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError("手机号已经存在")
        return txt_mobile


def pretty_edit(request, nid):
    row_object = models.PrettyNum.objects.filter(id=nid).first()
    if request.method == "GET":
        form = PrettyEditModelForm(instance=row_object)
        return render(request, 'pretty_edit.html', {"form": form})

    form = PrettyEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/pretty/list/')

    return render(request, 'pretty_edit.html', {"form": form})


def pretty_delete(request, nid):
    models.PrettyNum.objects.filter(id=nid).delete()
    return redirect('/pretty/list')


def admin_list(request):
    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict["username__contains"] = search_data

    # 根据搜索条件去数据库获取
    queryset = models.Admin.objects.filter(**data_dict)
    # 分页
    page_object = Pagination(request, queryset)
    context = {
        'queryset': page_object.page_queryset,
        'page_string': page_object.html(),
        "search_data": search_data
    }
    return render(request, 'admin_list.html', context)


class AdminModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.Admin
        fields = ["username", "password", "confirm_password"]

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get("password")
        confirm = md5(self.cleaned_data.get("confirm_password"))
        if confirm != pwd:
            raise ValidationError("密码不一致")
        return confirm


def admin_add(request):
    if request.method == "GET":
        form = AdminModelForm()
        return render(request, 'change.html', {'form': form})

    form = AdminModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/admin/list')
    return render(request, 'change.html', {'form': form})


class LoginForm(BootStrapForm):
    username = forms.CharField(
        label="用户名",
        widget=forms.TextInput,
        required=True
    )
    password = forms.CharField(
        label="密码",
        widget=forms.PasswordInput(render_value=True),
        required=True
    )
    code = forms.CharField(
        label="验证码",
        widget=forms.TextInput,
        required=True
    )

    def clean_password(self):
        pwd = self.cleaned_data.get("password")
        return md5(pwd)


def image_code(request):
    img, code_string = check_code()
    request.session['image_code'] = code_string
    request.session.set_expiry(60)
    stream = BytesIO()

    img.save(stream, 'png')
    return HttpResponse(stream.getvalue())


def login(request):

    if request.method == "GET":
        form = LoginForm()
        return render(request, 'login.html', {'form': form})
    form = LoginForm(data=request.POST)
    if form.is_valid():
        # 验证码校验
        user_image_code = form.cleaned_data.pop('code')
        code = request.session.get('image_code', "")
        if code.upper() != user_image_code.upper():
            form.add_error("code", "验证码错误")
            return render(request, "login.html", {'form': form})


    admin_object = models.Admin.objects.filter(**form.cleaned_data).first()
    if not admin_object:
        form.add_error("password", "用户名或者密码错误")
        return render(request, 'login.html', {'form': form})

    request.session["info"] = {'id': admin_object.id, 'name': admin_object.username}
    request.session.set_expiry(60 * 60 * 24 * 7)
    return redirect("/admin/list/")

    return render(request, 'login.html', {'form': form})


def logout(request):
    request.session.clear()
    return redirect('/login/')


def task_list(request):
    '''任务列表'''
    queryset = models.Task.objects.all().order_by('-id')
    page_object = Pagination(request,queryset)
    form = TaskModelForm()
    context = {
        "form": form,
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 生成页码
    }
    return  render(request,"task_list.html",context)

@csrf_exempt
def task_ajax(request):
    print(request.GET)
    print(request.POST)

    data_dict = {"status": True, 'data': [11, 22, 33, 44]}
    return HttpResponse(json.dumps(data_dict))

class TaskModelForm(BootStrapModelForm):
    class Meta:
        model = models.Task
        fields = "__all__"
        widgets = {
            "detail": forms.TextInput
        }

@csrf_exempt
def task_add(request):
    form = TaskModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        data_dict = {"status":True}
        return HttpResponse(json.dumps(data_dict))

    data_dict = {"status":False,'error':form.errors}

    return HttpResponse(json.dumps(data_dict,ensure_ascii=False))

class OrderModelForm(BootStrapModelForm):
    class Meta:
        model = models.Order
        exclude = ['oid']



def order_list(request):
    queryset = models.Order.objects.all().order_by('-id')
    page_object = Pagination(request,queryset)
    form = OrderModelForm()

    context = {
        'form': form,
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 生成页码
    }

    return render(request, 'order_list.html', context)

@csrf_exempt
def order_add(request):
    form = OrderModelForm(data=request.POST)
    if form.is_valid():
        form.instance.oid = datetime.now().strftime("%Y%m%d%H%M%S") + str(random.randint(1000, 9999))
        form.save()
        return JsonResponse({"status":True})

    return JsonResponse({"status":False,"error":form.errors})


def order_delete(request):
    uid = request.GET.get('uid')
    exists = models.Order.objects.filter(id=uid).exists()
    if not exists:
        return JsonResponse({"status":False,'error':"删除失败，数据不存在"})
    models.Order.objects.filter(id=uid).delete()
    return JsonResponse({"status": True})

def order_detail(request):
    uid = request.GET.get("uid")
    row_dict = models.Order.objects.filter(id=uid).values("title","price","status").first()

    if not row_dict:
        return JsonResponse({"status": False,"error":"数据不存在"})

    result = {
        "status": True,
        "data": row_dict
    }
    return JsonResponse(result)

@csrf_exempt
def order_edit(request):
    """编辑订单"""
    uid = request.GET.get("uid")
    row_object = models.Order.objects.filter(id=uid).first()
    if not row_object:
        return JsonResponse({"status": False,"tips":"数据不存在，请刷新后重试"})

    form = OrderModelForm(data=request.POST,instance=row_object)
    if form.is_valid():
        form.save()
        return JsonResponse({"status": True})
    return JsonResponse({"status": False,"error":form.errors})