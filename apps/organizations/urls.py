from django.conf.urls import url
from django.urls import path
from apps.organizations.views import OrgView, AddAskView, OrgHomeView, OrgTeacherView, OrgCourseView, OrgDescView, \
    TeacherListView,TeacherDetailView

urlpatterns = [
    url(r'^list/$', OrgView.as_view(), name='list'),
    url(r'^add_ask/$', AddAskView.as_view(), name='add_ask'),
    url(r'^add_ask/$', AddAskView.as_view(), name='add_ask'),
    url(r'^(?P<org_id>\d+)/$', OrgHomeView.as_view(), name='home'),
    # 下面这个是官方写法,更推荐上面正则表达式的写法
    # path('<int:org_id>/', OrgHomeView.as_view(), name='home',),

    url(r'^(?P<org_id>\d+)/teacher/$', OrgTeacherView.as_view(), name='teacher'),
    url(r'^(?P<org_id>\d+)/course/$', OrgCourseView.as_view(), name='course'),
    url(r'^(?P<org_id>\d+)/desc/$', OrgDescView.as_view(), name='desc'),

    # 讲师页
    url(r'^teachers/$', TeacherListView.as_view(), name='teachers'),
    url(r'^teachers/(?P<teacher_id>\d+)/$', TeacherDetailView.as_view(), name='teacher_detail'),

]
