from django.shortcuts import render
from django.views.generic.base import View
# 分页用的
from pure_pagination import Paginator, PageNotAnInteger
from django.http import HttpResponseRedirect, JsonResponse
from apps.operations.models import UserFavorite
from django.db.models import Q

from apps.organizations.models import CourseOrg, City, Teacher
from apps.organizations.forms import AddAskForm


# 讲师详情页
class TeacherDetailView(View):
    def get(self, request, teacher_id, *args, **kwargs):
        # 拿到当前teacher对象
        teacher = Teacher.objects.get(id=teacher_id)

        # 老师收藏,机构收藏功能
        teacher_fav = False
        org_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher_id, fav_type=3):
                teacher_fav = True
            if UserFavorite.objects.filter(user=request.user, fav_id=teacher_id, fav_type=2):
                org_fav = True

        # 讲师排行榜
        # 获取所有的teachers对象
        all_teachers = Teacher.objects.all()
        hot_teachers = all_teachers.order_by("-click_nums")[:3]

        return render(request, 'teacher-detail.html', {
            "teacher": teacher,
            "teacher_fav": teacher_fav,
            "org_fav": org_fav,
            "hot_teachers": hot_teachers,
        })


# 讲师页面
class TeacherListView(View):
    def get(self, request, *args, **kwargs):
        # 获取所有的teachers对象
        all_teachers = Teacher.objects.all()
        # 统计老师个数
        teacher_nums = all_teachers.count()

        # 搜索关键词
        keywords=request.GET.get("keywords","")
        # 把keywords,和s_type传递给html,好让搜索的条件在刷新网页后还存在
        s_type="teacher"
        if keywords:
            all_teachers = all_teachers.filter(Q(name__icontains=keywords))


        # 讲师排行榜
        hot_teachers = all_teachers.order_by("-click_nums")[:3]

        # 对讲师进行排序,按点击数从高到低
        sort = request.GET.get('sort', '')
        if sort == 'hot':
            # 默认是升序,加上负号-就意味着是降序
            all_teachers = all_teachers.order_by('-click_nums')

        # 分页配置
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 对课程机构进行分页,per_page每页显示多少条数据
        p = Paginator(all_teachers, per_page=1, request=request)
        teachers = p.page(page)  # 现在的teacher是page对象

        return render(request, 'teachers-list.html', {
            'teachers': teachers,
            'teacher_nums': teacher_nums,
            'sort': sort,
            'hot_teachers': hot_teachers,
            'keywords': keywords,
            's_type': s_type,

        })


# 机构列表页, 从服务器获取数据,填充到html中
class OrgView(View):
    def get(self, request, *args, **kwargs):
        # 获取所有CourseOrg对象
        all_orgs = CourseOrg.objects.all()
        # 统计共多少个城市
        all_citys = City.objects.all()
        # 对机构进行排序,倒序,只显示前3,放在这儿是因为在所有排序中,其优先级最高
        # 切片会产生新的对象,不会影响原本的all_orgs
        hot_orgs = all_orgs.order_by('-click_nums')[:3]

        # 搜索关键词
        keywords = request.GET.get("keywords", "")
        # 把keywords,和s_type传递给html,好让搜索的条件在刷新网页后还存在
        s_type="org"
        if keywords:
            all_orgs = all_orgs.filter(
                Q(name__icontains=keywords) | Q(desc__icontains=keywords))

        # 获取当前机构类别,对课程机构进行筛选
        category = request.GET.get('ct', '')
        if category:
            all_orgs = all_orgs.filter(category=category)
        # 统计共多少家机构
        org_nums = all_orgs.count()

        # 获取当前city,对城市进行筛选
        city_id = request.GET.get('city', '')
        if city_id:
            # 先判断拿到的是不是数字类型,防止程序崩溃
            if city_id.isdigit():
                all_orgs = all_orgs.filter(city_id=city_id)

        # 对机构进行排序
        sort = request.GET.get('sort', '')
        if sort == 'students':
            # 默认是升序,加上负号-就意味着是降序
            all_orgs = all_orgs.order_by('-students')
        if sort == 'courses':
            all_orgs = all_orgs.order_by('-course_nums')
        # 统计共多少家机构
        org_nums = all_orgs.count()

        # 分页配置
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 对课程机构进行分页,per_page每页显示多少条数据
        p = Paginator(all_orgs, per_page=4, request=request)
        orgs = p.page(page)

        return render(request, 'org-list.html', {
            'all_orgs': orgs,
            'org_nums': org_nums,
            'all_citys': all_citys,
            # 传递category是为了在进行机构筛选的时候,给对应的标签添加选中状态
            'category': category,
            # 传递当前city_id是为了在进行城市筛选的时候,给对应的标签添加选中状态
            'city_id': city_id,
            # 传递排序规则给前端
            'sort': sort,
            # 授课机构排序
            'hot_orgs': hot_orgs,
            'keywords': keywords,
            's_type': s_type,
        })


# 我要咨询功能
class AddAskView(View):
    def post(self, request, *args, **kwargs):
        # modelform功能一,可以当form来使用,并执行表单验证is_valid
        userask_form = AddAskForm(request.POST)
        if userask_form.is_valid():
            # modelform功能二,可以当model来使用,实例化对象并保存到数据库,
            # 同时还可以返回这个对象
            user_ask = userask_form.save(commit=True)
            return JsonResponse({
                'status': 'success',
            })
        else:
            return JsonResponse({
                'status': 'fail',
                'msg': '添加出错',
            })


# 机构详情页首页
class OrgHomeView(View):
    # 一定注意,如果在url里设置了命名,那么这里的get和post就要多接收一个参数
    def get(self, request, org_id, *args, **kwargs):
        current_page = 'home'
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1  # 记得给点击数+1
        course_org.save()

        # 查询该用户是否已收藏该机构
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        # 反向查询该机构的所有课程和老师,分别只显示3个和1个
        all_courses = course_org.courses_set.all()[:3]
        all_teacher = course_org.teacher_set.all()[:1]

        return render(request, 'org-detail-homepage.html', {
            'all_courses': all_courses,
            'all_teacher': all_teacher,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


# 机构讲师页
class OrgTeacherView(View):
    # 一定注意,如果在url里设置了命名,那么这里的get和post就要多接收一个参数
    def get(self, request, org_id, *args, **kwargs):
        current_page = 'teacher'
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1  # 记得给点击数+1
        course_org.save()

        # 查询该用户是否已收藏该机构
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        # 反向查询该机构的所有老师
        all_teacher = course_org.teacher_set.all()
        return render(request, 'org-detail-teachers.html', {
            'all_teacher': all_teacher,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


# 机构课程页
class OrgCourseView(View):
    # 一定注意,如果在url里设置了命名,那么这里的get和post就要多接收一个参数
    def get(self, request, org_id, *args, **kwargs):
        current_page = 'course'
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1  # 记得给点击数+1
        course_org.save()

        # 查询该用户是否已收藏该机构
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        # 反向查询该机构的所有课程
        all_courses = course_org.courses_set.all()

        # 分页配置
        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 对机构进行分页,per_page每页显示多少条数据
        p = Paginator(all_courses, per_page=6, request=request)
        courses = p.page(page)  # 返回的是page对象

        return render(request, 'org-detail-course.html', {
            'all_courses': courses,
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })


# 机构介绍页
class OrgDescView(View):
    # 一定注意,如果在url里设置了命名,那么这里的get和post就要多接收一个参数
    def get(self, request, org_id, *args, **kwargs):
        current_page = 'desc'
        course_org = CourseOrg.objects.get(id=int(org_id))
        course_org.click_nums += 1  # 记得给点击数+1
        course_org.save()

        # 查询该用户是否已收藏该机构
        has_fav = False
        if request.user.is_authenticated:
            if UserFavorite.objects.filter(user=request.user, fav_id=course_org.id, fav_type=2):
                has_fav = True

        return render(request, 'org-detail-desc.html', {
            'course_org': course_org,
            'current_page': current_page,
            'has_fav': has_fav,
        })
