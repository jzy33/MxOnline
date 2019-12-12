from django.conf.urls import url
# 下面两个模块是给"个人中心 -> 我的课程"用的
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

from apps.users.views import UserInfoView,UploadImageView,ChangePwdView,\
    ChangeMobileView,MyCourseView,MyFavOrgView,MyFavTeacherView,MyFavCourseView,\
    MyMessageView

urlpatterns = [
    url(r'^info/$', UserInfoView.as_view(), name='info'),
    url(r'^image/upload/$', UploadImageView.as_view(), name='image'),
    url(r'^update/pwd/$', ChangePwdView.as_view(), name='update_pwd'),
    url(r'^update/mobile/$', ChangeMobileView.as_view(), name='update_mobile'),

    # 两种方式实现"个人中心 -> 我的课程"
    # url(r'^mycourse/$', MyCourseView.as_view(), name='mycourse'),
    url(r'^mycourse/$', login_required(TemplateView.as_view(template_name="usercenter-mycourse.html"),login_url="/login/"), {"current_page":"mycourse"},name='mycourse'),
    # "个人中心 -> 我的收藏(默认是机构)"
    url(r'^myfavorg/$', MyFavOrgView.as_view(), name='myfavorg'),
    # "个人中心 -> 我的收藏(老师)"
    url(r'^myfav_teacher/$', MyFavTeacherView.as_view(), name='myfav_teacher'),
    # "个人中心 -> 我的收藏(老师)"
    url(r'^myfav_course/$', MyFavCourseView.as_view(), name='myfav_course'),
    # "个人中心 -> 我的消息"
    url(r'^messages/$', MyMessageView.as_view(), name='messages'),

]
