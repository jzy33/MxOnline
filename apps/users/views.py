from django.shortcuts import render
from django.views.generic.base import View
# authenticate模块可帮助我们查询用户是否存在,login模块可实现登录功能
from django.contrib.auth import authenticate, login, logout
# 不清楚HttpResponseRedirect和redirect的区别
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
import redis
# django自带的登录验证
from django.contrib.auth.mixins import LoginRequiredMixin
from pure_pagination import Paginator, PageNotAnInteger
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from apps.users.forms import LoginForm, DynamicLoginForm, DynamicLoginPostForm, RegisterForm
# 注册页面的get和post的两个表单
from apps.users.forms import RegisterForm, RegisterPostForm, UploadImageForm, UserInfoForm
from apps.users.forms import ChangePwdForm, UpdateMobileForm
# 获取云片网的cpikey
from MxOnline.settings import yp_apikey, REDIS_HOST, REDIS_PORT
# 导入云片网发送短信的函数
from apps.utils.YunPian import send_single_sms
# 导入生成随机数字的模块
from apps.utils.random_str import generate_random
# 导入model的user表,用于查询用户是否存在,和添加新用户
from apps.users.models import UserProfile
from apps.operations.models import UserFavorite, UserMessage, Banner
from apps.organizations.models import CourseOrg, Teacher
from apps.courses.models import Courses

# 自定义用户验证,让mobile也可以成为登录账号
class CustomAuth(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user=UserProfile.objects.get(Q(username=username)|Q(mobile=username))
            if user.check_password(password):
                return user
        # 如果找不到用户,就返回none
        except Exception as e:
            return None



# 添加全局变量unread_nums
def message_nums(request):
    """
    Add media-related context variables to the context.
    """
    if request.user.is_authenticated:
        return {'unread_nums': request.user.usermessage_set.filter(has_read=False).count()}
    else:
        return {}


# 个人中心 -> 我的消息
class MyMessageView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "message"

        messages = UserMessage.objects.filter(user=request.user)

        for message in messages:
            message.has_read = True
            message.save()

        # 分页配置
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 对课程机构进行分页,per_page每页显示多少条数据
        p = Paginator(messages, per_page=1, request=request)
        messages = p.page(page)  # 现在的teacher是page对象

        return render(request, "usercenter-message.html", {
            "messages": messages,
            "current_page": current_page,
        })


# 个人中心 -> 我的收藏(课程)
class MyFavCourseView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav_course"

        course_list = []
        # 先查询到当前用户收藏的所有的机构的userfavorite对象
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        for fav_course in fav_courses:
            # 再查这些机构对象
            try:
                course = Courses.objects.get(id=fav_course.fav_id)
                course_list.append(course)
            except Exception as e:
                print(e)

        return render(request, "usercenter-fav-course.html", {
            "course_list": course_list,
            "current_page": current_page,
        })


# 个人中心 -> 我的收藏(教师)
class MyFavTeacherView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfav_teacher"

        teacher_list = []
        # 先查询到当前用户收藏的所有的机构的userfavorite对象
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        for fav_teacher in fav_teachers:
            # 再查这些机构对象
            org = Teacher.objects.get(id=fav_teacher.fav_id)
            teacher_list.append(org)

        return render(request, "usercenter-fav-teacher.html", {
            "teacher_list": teacher_list,
            "current_page": current_page,
        })


# 个人中心 -> 我的收藏(默认是收藏机构)
class MyFavOrgView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "myfavorg"

        org_list = []
        # 先查询到当前用户收藏的所有的机构的userfavorite对象
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        for fav_org in fav_orgs:
            # 再查这些机构对象
            org = CourseOrg.objects.get(id=fav_org.fav_id)
            org_list.append(org)

        return render(request, "usercenter-fav-org.html", {
            "org_list": org_list,
            "current_page": current_page,
        })


# 个人中心 -> 我的课程
# 以下是实现方式一,实现方式二是使用的TemplateView,去url里面看
class MyCourseView(LoginRequiredMixin, View):
    login_url = "/login/"

    def get(self, request, *args, **kwargs):
        current_page = "mycourse"

        # 注意返回的是userCoursee对象,还不是course
        # my_courses=UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html", {
            # "my_courses":my_courses,
            "current_page": current_page,
        })


# 修改手机号
class ChangeMobileView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, *args, **kwargs):
        mobile_form = UpdateMobileForm(request.POST)
        if mobile_form.is_valid():
            mobile = mobile_form.cleaned_data["mobile"]
            # 已经注册过的手机号不能再注册
            # if request.user.mobile==mobile:
            #     return JsonResponse({
            #         "mobile":"和当前号码一致",
            #     })
            if UserProfile.objects.filter(mobile=mobile):
                return JsonResponse({
                    "mobile": "手机号已被注册",
                })
            user = request.user
            user.mobile = mobile
            user.username = mobile
            user.save()
            # logout(request)
            return JsonResponse({
                "status": "success",
            })
        # 表单验证失败
        else:
            return JsonResponse(mobile_form.errors)


# 修改密码接口
class ChangePwdView(LoginRequiredMixin, View):
    login_url = "/login/"

    def post(self, request, *args, **kwargs):
        pwd_form = ChangePwdForm(request.POST)
        if pwd_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            # pwd2 = request.POST.get("password2", "")
            # if pwd1 != pwd2:
            #     return JsonResponse({
            #         "status": "fail",
            #         "msg": "密码不一致",
            #     })
            user = request.user
            user.set_password(pwd1)
            user.save()  # django在检测到密码修改后,会退出当前用户的登录状态,并自动返回登录页面
            # login(request,user)  # 这行代码可以在改完密码后又立即登录

            return JsonResponse({
                "status": "success",
            })
        else:
            return JsonResponse(pwd_form.errors)

        # 修改头像接口


# 修改头像接口
class UploadImageView(LoginRequiredMixin, View):
    # LoginRequiredMixin需要的配置
    login_url = '/login/'

    # 原始处理办法:
    # 1.如果同一个文件名多次上传,该如何处理
    # 2.文件的保存路径应该写入user.image字段里面
    # 3.还没有做表单验证......等等很多细节
    # def save_file(self,file):
    #     with open("G:/PycharmProjects/Jzy/07.xadmin/MxOnline/media/head_img/upload.jpg",'wb') as f:
    #         for chunk in file.chunks():
    #             f.write(chunk)
    # def post(self, request, *args, **kwargs):
    #     files=request.FILES["image"]
    #     self.save_file(files)
    #     pass

    # 这里的使用办法,ModelForm
    def post(self, request, *args, **kwargs):
        # 把用户上传的图片交给modelForm处理,并且要指明当前的用户对象实例是哪一个
        image_form = UploadImageForm(request.POST, request.FILES, instance=request.user)
        if image_form.is_valid():
            image_form.save()
            return JsonResponse({
                "status": "success",
            })
        else:
            return JsonResponse({
                "status": "fail",
            })


# 个人中心
# 需要登录才能访问
# 包含修改个人信息的功能
class UserInfoView(LoginRequiredMixin, View):
    # LoginRequiredMixin需要的配置
    login_url = '/login/'

    def get(self, request, *args, **kwargs):
        current_page = "info"

        # 获取图形码
        captcha_form = RegisterForm()
        return render(request, 'usercenter-info.html', {
            "captcha_form": captcha_form,
            "current_page": current_page,
        })

    def post(self, request, *args, **kwargs):
        # 指定了实例对象instance,它就知道现在是想修改数据
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return JsonResponse({
                "status": "success",
            })
        else:
            return JsonResponse(user_info_form.errors)


# 注册页面
class RegisterView(View):
    def get(self, request, *args, **kwargs):
        register_get_form = RegisterForm()
        banners = Banner.objects.all()[:3]
        return render(request, 'register.html', {
            'register_get_form': register_get_form,
            'banners': banners,
        })

    def post(self, request, *args, **kwargs):
        register_post_form = RegisterPostForm(request.POST)
        # 校验手机号(是否已经注册),动态验证码,密码
        banners = Banner.objects.all()[:3]
        if register_post_form.is_valid():
            # 获取手机号码和密码
            mobile = register_post_form.cleaned_data['mobile']
            password = register_post_form.cleaned_data['password']
            # 新建一个用户
            # 默认用户名=手机号
            user = UserProfile(username=mobile)
            user.set_password(password)
            # 别忘记存手机号
            user.mobile = mobile
            # 最后对新建的对象进行保存,否则不会存进数据库
            user.save()
            # 注册成功后,跳转首页
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
        # 若验证失败
        else:
            register_get_form = RegisterForm()
            return render(request, 'register.html', {
                'register_get_form': register_get_form,
                'register_post_form': register_post_form,
                'banners': banners,
            })


# 手机登录的动态验证,验证手机号码,和手机验证码
class DynamicLoginView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse("index"))
        next = request.GET.get("next", "")
        login_form = DynamicLoginForm()
        banners = Banner.objects.all()[:3]
        return render(request, "login.html", {
            "login_form": login_form,
            "next": next,
            "banners": banners,
        })

    def post(self, request, *args, **kwargs):
        dynamic_login = True
        login_form = DynamicLoginPostForm(request.POST)
        # 校验手机号码(下面),和手机验证码(内嵌在DynamicLoginPostForm里面了)
        banners = Banner.objects.all()[:3]
        if login_form.is_valid():
            # 去数据库查是否存在该用户
            mobile = login_form.cleaned_data['mobile']
            existed_user = UserProfile.objects.filter(mobile=mobile)
            # 如果用户存在,则直接登录
            if existed_user:
                user = existed_user[0]
            # 如果用户不存在,则新建一个用户
            else:
                # 默认用户名=手机号
                user = UserProfile(username=mobile)
                # 使用明文密码不安全,所以先生存随机密码,再用AbstractUser自带的set_password来进行hash加密存储,防止被破解
                password = generate_random(10, 2)
                user.set_password(password)
                # 别忘记存手机号
                user.mobile = mobile
                # 最后对新建的对象进行保存,否则不会存进数据库
                user.save()
            # 登录后,跳转首页
            login(request, user)
            next = request.GET.get('next', '')
            if next:
                return HttpResponseRedirect(next)
            return HttpResponseRedirect(reverse('index'))
        # 手机号码或手机验证码,验证失败就跳回登录页面
        # 需求,显示错误信息
        else:
            # 生成d_form对象是为了当验证失败返回登录页面的时候,能够带上captcha字段
            d_form = DynamicLoginForm()
            return render(request, 'login.html', {
                'login_form': login_form,
                'dynamic_login': dynamic_login,
                'd_form': d_form,
                "banners": banners,
            })


# 检查图片验证码 + 发送手机验证码
class SendSmsView(View):
    def post(self, request, *args, **kwargs):
        # 把传递过来的信息都交给DynamicLoginForm会校验,主要是校验captcha字段
        send_sms_form = DynamicLoginForm(request.POST)
        re_dict = {}
        # 如果图片验证码正确(大概理了一下验证流程:ajax前端先验证手机号->验证图片码->发送手机验证码)
        if send_sms_form.is_valid():
            # 连接云片网,发送动态手机验证码
            mobile = send_sms_form.cleaned_data['mobile']
            # 随机生成数字验证码
            code = generate_random(4, 0)
            re_json = send_single_sms(yp_apikey, code, mobile)
            # 如果发送成功,返回success
            if re_json['code'] == 0:
                re_dict['status'] = 'success'
                r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset='utf-8', decode_responses=True)
                r.set(str(mobile), code)
                r.expire(str(mobile), 60 * 5)  # 验证码300秒后过期
            # 如果发送失败,把云片网返回的错误信息交给前端,注意:云片网也会对手机号码进行校验
            else:
                re_dict['msg'] = re_json['msg']
        # 如果图片验证码不正确
        else:
            # 循环错误,把所有的错误都添加进re_dict
            for key, value in send_sms_form.errors.items():
                # value是个列表,所以要用索引
                re_dict[key] = value[0]
        # JsonResponse返回给浏览器的是Content-Type: application/json,这样浏览器会自动反序列化
        return JsonResponse(re_dict)


# 退出功能,
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        # logout()函数会删掉当前用户request.user的,浏览器的sessionid,同时删除数据库中对应的session数据
        logout(request)
        return HttpResponseRedirect(reverse('index'))


# 登录页面 /login
class LoginView(View):
    def get(self, request, *args, **kwargs):
        # 如果已经登录,就重定向到首页
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('index'))

        # 轮播图
        banners = Banner.objects.all()[:3]

        next = request.GET.get('next', '')
        # 如果未登录,就在手机登录框架内,使用DynamicLoginForm自动生成captcha图片验证码
        login_form = DynamicLoginForm()
        return render(request, 'login.html', {
            'login_form': login_form,
            'next': next,
            'banners': banners,
        })

    def post(self, request, *args, **kwargs):
        # 表单验证
        # 把post提交的信息传递给自定义的form类
        login_form = LoginForm(request.POST)
        # 如果is_valid为true,说明验证通过

        banners = Banner.objects.all()[:3]

        if login_form.is_valid():
            # 通过cleaned_data来获取用户名和密码,cleaned_data是dict格式
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            # 不建议自己去数据库查,因为密码是经过计算加密的,所以用django自己封装的authenticate更好
            user = authenticate(username=username, password=password)
            if user:
                # 使用login函数帮助我们登录,这里会去取session_id,并把它保存到cookie中
                login(request, user)
                next = request.GET.get('next', '')
                if next:
                    return HttpResponseRedirect(next)
                return HttpResponseRedirect(reverse('index'))
            else:
                return render(request, 'login.html', {
                    'msg': '用户名或密码错误',
                    'login_form': login_form,
                    'banners': banners,
                })
        else:
            return render(request, 'login.html', {
                'login_form': login_form,
                'banners': banners,
            })
