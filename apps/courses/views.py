from django.shortcuts import render
from django.views.generic.base import View
# 导入分页设置
from pure_pagination import Paginator, PageNotAnInteger
# django自带的登录验证
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q

# 查询是否收藏
from apps.operations.models import UserFavorite, UserCourse, CourseComments
from apps.courses.models import Courses, CourseTag, CourseResource, Video


class VideoView(LoginRequiredMixin, View):
    # LoginRequiredMixin需要的配置
    login_url = '/login/'

    # 别忘记这个地方有额外的参数,course_id
    def get(self, request, course_id, video_id, *args, **kwargs):
        # 根据course_id获取课程详情,点击数加1
        course = Courses.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        # 获取当前video对象
        video = Video.objects.get(id=video_id)
        url=video.url

        # 首先要查该用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        # 如果没有关联,就先把该用户和该课程关联
        if not user_courses:
            user_courses = UserCourse(user=request.user, course=course)
            user_courses.save()
            # 记得学生数得加1
            course.students += 1
            course.save()

        # 显示右下的'学习过该课程的同学还学过哪些课程'
        # 找到学过该课程的所有'用户课程对象'
        user_courses = UserCourse.objects.filter(course=course)
        # 找到这些学生的id
        user_ids = [user_course.user.id for user_course in user_courses]
        # 找这些学生学过的所有课程的'用户课程对象',并根据课程的点击数进行倒序排列,并设置最多取5个
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by("-course__click_nums")[:5]
        # 最后,取所有的学习过该课程的同学还学过哪些课程,并排除掉当前课程
        related_courses = [user_course.course for user_course in all_courses if user_course.course.id != course.id]

        # 课程资源展示
        course_resources = CourseResource.objects.filter(course=course)

        return render(request, 'course-play.html', {
            "course": course,
            "course_resources": course_resources,
            "related_courses": related_courses,
            "video": video,
        })


# 课程评论,需要用户登录后才能访问
class CourseCommentsView(LoginRequiredMixin, View):
    # LoginRequiredMixin需要的配置
    login_url = '/login/'

    # 别忘记这个地方有额外的参数,course_id
    def get(self, request, course_id, *args, **kwargs):
        # 根据course_id获取课程详情,点击数加1
        course = Courses.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        # 获取当前课程的评论
        comments = CourseComments.objects.filter(course=course)

        # 首先要查该用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        # 如果没有关联,就先把该用户和该课程关联
        if not user_courses:
            user_courses = UserCourse(user=request.user, course=course)
            user_courses.save()
            # 记得学生数得加1
            course.students += 1
            course.save()

        # 显示右下的'学习过该课程的同学还学过哪些课程'
        # 找到学过该课程的所有'用户课程对象'
        user_courses = UserCourse.objects.filter(course=course)
        # 找到这些学生的id
        user_ids = [user_course.user.id for user_course in user_courses]
        # 找这些学生学过的所有课程的'用户课程对象',并根据课程的点击数进行倒序排列,并设置最多取5个
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by("-course__click_nums")[:5]
        # 最后,取所有的学习过该课程的同学还学过哪些课程,并排除掉当前课程
        related_courses = [user_course.course for user_course in all_courses if user_course.course.id != course.id]

        # 课程资源展示
        course_resources = CourseResource.objects.filter(course=course)

        return render(request, 'course-comment.html', {
            "course": course,
            "course_resources": course_resources,
            "related_courses": related_courses,
            "comments": comments,
        })


# 课程章节页(我要学习),需要用户登录后才能访问
class CourseLessonView(LoginRequiredMixin, View):
    # 1.用户和课程之间的关联
    # 2.对view整体进行登录验证
    # 3.其它课程

    # LoginRequiredMixin需要的配置
    login_url = '/login/'

    # 别忘记这个地方有额外的参数,course_id
    def get(self, request, course_id, *args, **kwargs):
        # 根据course_id获取课程详情,点击数加1
        course = Courses.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        # 首先要查该用户是否已经关联了该课程
        user_courses = UserCourse.objects.filter(user=request.user, course=course)
        # 如果没有关联,就先把该用户和该课程关联
        if not user_courses:
            user_courses = UserCourse(user=request.user, course=course)
            user_courses.save()
            # 记得学生数得加1
            course.students += 1
            course.save()

        # 显示右下的'学习过该课程的同学还学过哪些课程'
        # 找到学过该课程的所有'用户课程对象'
        user_courses = UserCourse.objects.filter(course=course)
        # 找到这些学生的id
        user_ids = [user_course.user.id for user_course in user_courses]
        # 找这些学生学过的所有课程的'用户课程对象',并根据课程的点击数进行倒序排列,并设置最多取5个
        all_courses = UserCourse.objects.filter(user_id__in=user_ids).order_by("-course__click_nums")[:5]
        # 最后,取所有的学习过该课程的同学还学过哪些课程,并排除掉当前课程
        related_courses = [user_course.course for user_course in all_courses if user_course.course.id != course.id]

        # 课程资源展示
        course_resources = CourseResource.objects.filter(course=course)

        return render(request, 'course-video.html', {
            "course": course,
            "course_resources": course_resources,
            "related_courses": related_courses,
        })


# 课程详情页
class CourseDetailView(View):
    # 别忘记这个地方有额外的参数,course_id
    def get(self, request, course_id, *args, **kwargs):
        # 根据course_id获取课程详情,点击数加1
        course = Courses.objects.get(id=int(course_id))
        course.click_nums += 1
        course.save()

        # 获取收藏状态,由于详情页有两个地方设计到收藏,所以要设置两个
        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated:
            # 注意,即使没有用户登录,request.user内部也会封装一个对象
            # 所以判断收藏的时候,尽量全字段匹配
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True

        # 通过课程的tag做课程的推荐
        # tag = course.tag
        # # 为防止程序报错,应提前给related_courses赋值,且是可迭代的类型
        # related_courses = []
        # if tag:
        #     related_courses = Courses.objects.filter(tag=tag).exclude(id__in=[course_id])[:3]

        # 此时tag已单独是一张表,所以用法不一样了,这里有些model的基础知识,忘记了要去补
        tags = course.coursetag_set.all()  # tags是QuerySet
        tag_list = [tag.tag for tag in tags]  # 列表生成式
        # 流程: 拿到该课程所有的标签->找到拥有同样标签的所有CourseTag对象->排除当前课程本身->返回一堆CourseTag对象
        course_tags = CourseTag.objects.filter(tag__in=tag_list).exclude(course__id=course.id)
        # 如果是列表,那么如果有一门课程2拥有多个tag和当前课程一样,那么推荐课程那里就会重复显示课程2
        # 解决办法就是,用set(),自动去重
        # related_courses=[]
        related_courses = set()
        for course_tag in course_tags:
            related_courses.add(course_tag.course)

        return render(request, 'course-detail.html', {
            "course": course,
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org,
            "related_courses": related_courses,
        })


# 公开课首页
class CourseListView(View):
    def get(self, request, *args, **kwargs):
        # 获取所有课程对象,按添加时间倒序排列
        all_courses = Courses.objects.order_by('-add_time')
        # 右侧热门课程推荐,只展示3个
        hot_courses = Courses.objects.order_by('-click_nums')[:3]

        # 搜索关键词
        keywords=request.GET.get("keywords","")
        # 把keywords,和s_type传递给html,好让搜索的条件在刷新网页后还存在
        s_type="course"
        if keywords:
            all_courses = all_courses.filter(Q(name__icontains=keywords)|Q(desc__icontains=keywords)|Q(detail__contains=keywords))

        # 课程排序
        sort = request.GET.get('sort')
        if sort == 'students':
            all_courses = Courses.objects.order_by('-students')
        if sort == 'hot':
            # 热度就是点击数
            all_courses = Courses.objects.order_by('-click_nums')

        # 分页配置
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 对机构进行分页,per_page每页显示多少条数据
        p = Paginator(all_courses, per_page=4, request=request)
        courses = p.page(page)  # 返回的是page对象

        return render(request, 'course-list.html', {
            'all_courses': courses,
            # sort用于完成排序按钮的选中功能
            'sort': sort,
            # hot_courses用于完成右侧'热门课程推荐'
            'hot_courses': hot_courses,
            'keywords': keywords,
            's_type': s_type,
        })
