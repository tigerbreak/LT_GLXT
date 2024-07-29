from django.db import models

# Create your models here.
class Department(models.Model):
    title = models.CharField(verbose_name='标题',max_length=32)
    def __str__(self):
        return self.title


class UserInfo(models.Model):
    name = models.CharField(verbose_name='姓名',max_length=16)
    password = models.CharField(verbose_name='密码',max_length=64)
    age = models.IntegerField(verbose_name='年龄')
    account = models.DecimalField(verbose_name='账号余额',max_digits=10,decimal_places=2,default=0)
    create_time = models.DateTimeField(verbose_name='入职时间')

    depart = models.ForeignKey(to='Department',to_field='id',on_delete=models.CASCADE)
    #在djanogo中做的约束
    gender_choice = (
        (1,"男"),
        (2,"女"),
    )
    gender = models.SmallIntegerField(verbose_name='性别',choices=gender_choice)

class PrettyNum(models.Model):
    mobile = models.CharField(verbose_name="手机号",max_length=11)
    price = models.IntegerField(verbose_name="价格",default=0)

    level_choinces = (
        (1,"1级"),
        (2,"2级"),
        (3,"3级"),
        (4,"4级"),
    )

    level = models.SmallIntegerField(verbose_name="级别",choices=level_choinces,default=1)

    status_choices = (
        (1,"已占用"),
        (2,"未占用"),
    )
    status = models.SmallIntegerField(verbose_name="状态",choices=status_choices,default=2)


class Admin(models.Model):
    """ 管理员 """
    username = models.CharField(verbose_name="用户名", max_length=32)
    password = models.CharField(verbose_name="密码", max_length=64)

    def __str__(self):
        return self.username


class Task(models.Model):
    level_choices = (
        (1,"紧急"),
        (2,"重要"),
        (1,"临时"),
    )
    level = models.SmallIntegerField(verbose_name="级别",choices=level_choices,default=1)
    title = models.CharField(verbose_name="标题",max_length=64)
    detail = models.TextField(verbose_name="详细信息")
    user = models.ForeignKey(verbose_name="负责人",to="admin",on_delete=models.CASCADE)

class Order(models.Model):
    oid = models.CharField(verbose_name="订单号",max_length=64)
    title = models.CharField(verbose_name="名称",max_length=32)
    price = models.IntegerField(verbose_name="价格")

    status_choices = (
        (1,"待支付"),
        (2,"已支付"),
    )
    status = models.SmallIntegerField(verbose_name="状态",choices=status_choices,default=1)

    admin = models.ForeignKey(verbose_name="管理员",to="admin",on_delete=models.CASCADE)


