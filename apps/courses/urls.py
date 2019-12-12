from django.conf.urls import url
from django.urls import path
from apps.courses.views import CourseListView,CourseDetailView,CourseLessonView,CourseCommentsView,VideoView

urlpatterns = [
    url(r'list/$', CourseListView.as_view(), name='list'),
    url(r'(?P<course_id>\d+)/$', CourseDetailView.as_view(), name='detail'),
    # 章节页面
    url(r'(?P<course_id>\d+)/lesson/$', CourseLessonView.as_view(), name='lesson'),
    # 评论页面
    url(r'(?P<course_id>\d+)/comments/$', CourseCommentsView.as_view(), name='comments'),
    # 视屏播放
    url(r'(?P<course_id>\d+)/video/(?P<video_id>\d+)$', VideoView.as_view(), name='video'),

]
