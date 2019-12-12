from django import forms
from captcha.fields import CaptchaField
import redis

# 获取redis相关设置
from MxOnline.settings import REDIS_HOST, REDIS_PORT
# 为了查询对象
from apps.users.models import UserProfile


# 手机登录的动态验证,验证手机号码,和手机验证码
class UpdateMobileForm(forms.Form):
    mobile = forms.CharField(required=True, max_length=11, min_length=11)
    code = forms.CharField(required=True, max_length=4, min_length=4)

    # code校验方式一,局部勾子
    def clean_code(self):
        # 由于cleaned_data是在clean执行之后才有的,所以有时候可能没有想取的数据
        # 如果cleaned_data取不到,就是用debug模式去看self.data,和self.initial,一般都在self.data里面
        mobile = self.data.get('mobile')
        code = self.data.get('code')

        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset='utf-8', decode_responses=True)
        redis_code = r.get(str(mobile))
        if code != redis_code:
            raise forms.ValidationError('手机验证码不正确')
        return self.cleaned_data


# 修改密码
class ChangePwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)

    def clean(self):
        pwd1 = self.cleaned_data["password1"]
        pwd2 = self.cleaned_data["password2"]
        if pwd1 != pwd2:
            raise forms.ValidationError("两次密码不一致")
        return self.cleaned_data


# 修改个人信息用的
class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["nick_name", "gender", "birthday", "address"]


# 修改头像用的
class UploadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["image"]


# 注册页面,处理get请求的图片验证码
class RegisterForm(forms.Form):
    # captcha字段会自行检测图片验证码是否正确,要理解
    captcha = CaptchaField()


# 注册页面,处理post请求
class RegisterPostForm(forms.Form):
    mobile = forms.CharField(required=True, max_length=11, min_length=11)
    code = forms.CharField(required=True, max_length=4, min_length=4)
    password = forms.CharField(required=True, )

    # 手机号校验,
    def clean_mobile(self):
        mobile = self.data.get('mobile')
        users = UserProfile.objects.filter(mobile=mobile)
        if users:
            raise forms.ValidationError('该手机号码已经注册')
        return mobile

    # code校验,局部勾子
    def clean_code(self):
        # 由于cleaned_data是在clean执行之后才有的,所以有时候可能没有想取的数据
        # 如果cleaned_data取不到,就是用debug模式去看self.data,和self.initial,一般都在self.data里面
        mobile = self.data.get('mobile')
        code = self.data.get('code')

        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset='utf-8', decode_responses=True)
        redis_code = r.get(str(mobile))
        if code != redis_code:
            raise forms.ValidationError('手机验证码不正确')
        return code


class LoginForm(forms.Form):
    # 字段名要和html里面input提交的name一致
    username = forms.CharField(required=True, min_length=2)
    password = forms.CharField(required=True, min_length=3)


# 验证手机号,图片验证码
class DynamicLoginForm(forms.Form):
    # 这个mobile的意思是把手机号码交给云片网来验证
    mobile = forms.CharField(required=True, max_length=11, min_length=11)
    # captcha字段会自行检测图片验证码是否正确,要理解
    captcha = CaptchaField()


# 手机登录的动态验证,验证手机号码,和手机验证码
class DynamicLoginPostForm(forms.Form):
    mobile = forms.CharField(required=True, max_length=11, min_length=11)
    code = forms.CharField(required=True, max_length=4, min_length=4)

    # code校验方式一,局部勾子
    def clean_code(self):
        # 由于cleaned_data是在clean执行之后才有的,所以有时候可能没有想取的数据
        # 如果cleaned_data取不到,就是用debug模式去看self.data,和self.initial,一般都在self.data里面
        mobile = self.data.get('mobile')
        code = self.data.get('code')

        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset='utf-8', decode_responses=True)
        redis_code = r.get(str(mobile))
        if code != redis_code:
            raise forms.ValidationError('手机验证码不正确')
        return self.cleaned_data

    # code校验方式二,全局勾子
    # def clean(self):
    #     mobile = self.cleaned_data['mobile']
    #     code = self.cleaned_data['code']
    #
    #     r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset='utf-8', decode_responses=True)
    #     redis_code=r.get(str(mobile))
    #     if code!=redis_code:
    #         # 全局钩子返回的是全局错误,所以需要手动 self.add_error('code',...)
    #         self.add_error('code','手机验证码不正确')
    #         raise forms.ValidationError('手机验证码不正确')
    #     return self.cleaned_data
