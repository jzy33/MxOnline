111111111111111111111111111111
"""MxOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
import xadmin
from django.conf.urls import url,include
# 去除login.页面的手机登录验证码图片的csrf_token的校验
from django.views.decorators.csrf import csrf_exempt
# 导入serve,完成img图片的访问
from django.views.static import serve


from apps.users.views import LoginView,LogoutView,SendSmsView,DynamicLoginView,RegisterView
from apps.organizations.views import OrgView
# 导入media配置,完成图片访问
from MxOnline.settings import MEDIA_ROOT
# 静态文件接口用,当DEBUG=False时,才启用STATIC_ROOT
# from MxOnline.settings import STATIC_ROOT
from apps.operations.views import IndexView

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('xadmin/', xadmin.site.urls),
    path('', IndexView.as_view(),name='index'),

    # 登录,退出,注册
    path('login/', LoginView.as_view(),name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(),name='register'),

    # 手机验证码登录
    path('d_login/', DynamicLoginView.as_view(),name='d_login'),
    
    # 图形码接口
    url(r'^captcha/', include('captcha.urls')),
    # 校验图形验证码,验证成功后才发送手机验证码
    # 这个借口封装在'发送验证码'的input标签下的ajax请求内,源代码在login.js中
    url(r'^send_sms/', csrf_exempt(SendSmsView.as_view(),),name='send_sms'),

    # 配置上传文件的访问url
    url(r'^media/(?P<path>.*)$', serve,{'document_root':MEDIA_ROOT}),
    # 静态文件接口,当DEBUG=False时,才启用
    # url(r'^static/(?P<path>.*)$', serve,{'document_root':STATIC_ROOT}),

    # 机构相关页面
    # url(r'^org_list/', OrgView.as_view(), name='org_list'),
    url(r'^org/', include(('apps.organizations.urls', 'organizations'), namespace='org')),
    
    # 用户相关操作(收藏)
    url(r'^op/', include(('apps.operations.urls', 'operations'), namespace='op')),

    # 课程相关页面
    url(r'^course/', include(('apps.courses.urls', 'courses'), namespace='course')),

    # 个人中心
    url(r'^users/', include(('apps.users.urls', 'users'), namespace='users')),

    # course -> desc的富文本
    url(r'^ueditor/', include('DjangoUeditor.urls'),),
]
'''
编写view的步骤:
1.view代码
2.配置url
3.修改html的action,与其他配置
'''


