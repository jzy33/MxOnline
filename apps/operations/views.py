from django.shortcuts import render
from django.views.generic.base import View
from django.http import JsonResponse

from apps.operations.models import UserFavorite
from apps.operations.forms import UserFavForm, CommentsForm,CourseComments
# 导入课程,机构,老师,为了删除收藏个数
from apps.courses.models import Courses
from apps.organizations.models import CourseOrg, Teacher
from apps.operations.models import Banner

# 首页
class IndexView(View):
    def get(self, request, *args, **kwargs):

        # 测试用,人为制造403错误,即权限错误
        # from django.core.exceptions import PermissionDenied
        # raise PermissionDenied
        
        banners=Banner.objects.all().order_by("index")
        courses=Courses.objects.filter(is_banner=False)[:6]
        banner_courses=Courses.objects.filter(is_banner=True)
        course_orgs=CourseOrg.objects.all()[:15]
        return render(request,"index.html",{
            "banners":banners,
            "courses":courses,
            "banner_courses":banner_courses,
            "course_orgs":course_orgs,
        })





# 添加评论,为什么里面不用LoginRequiredMixin?,因为这里的添加评论是ajax发送的url
class CommentView(View):
    def post(self, request, *args, **kwargs):

        # 如果未登录,封装数据告诉ajax,ajax会返回登录页面
        # status和msg,一定要和前端的ajax一致,否则ajax处理不了
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": "fail",
                "msg": "用户未登录",
            })

        # 拿到数据给modelForm验证
        comment_form = CommentsForm(request.POST)
        # 字段检验通过
        if comment_form.is_valid():
            course = comment_form.cleaned_data['course']
            comments = comment_form.cleaned_data['comments']

            # 手动生成评论对象,保存其user,comment,course三种属性
            comment = CourseComments()
            comment.user=request.user
            comment.comments=comments
            comment.course=course
            comment.save()

            return JsonResponse({
                "status": "success",
            })
        
        # 字段检验不通过
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "参数格式错误",
            })


# 添加收藏,删除收藏
class AddFavView(View):
    def post(self, request, *args, **kwargs):

        # 如果未登录,封装数据告诉ajax,ajax会返回登录页面
        # status和msg,一定要和前端的ajax一致,否则ajax处理不了
        if not request.user.is_authenticated:
            return JsonResponse({
                "status": "fail",
                "msg": "用户未登录",
            })

        # 拿到数据给modelForm验证
        user_fav_form = UserFavForm(request.POST)
        # 字段检验通过
        if user_fav_form.is_valid():
            fav_id = user_fav_form.cleaned_data['fav_id']
            fav_type = user_fav_form.cleaned_data['fav_type']

            # 是否已经收藏
            existed_records = UserFavorite.objects.filter(user=request.user, fav_id=fav_id, fav_type=fav_type)
            # 如果已经收藏,删除当前收藏记录,其对应的收藏数量-1
            if existed_records:
                existed_records.delete()
                if fav_type == 1:
                    course = Courses.objects.get(id=fav_id)
                    course.fav_nums -= 1
                    course.save()
                elif fav_type == 2:
                    course_org = CourseOrg.objects.get(id=fav_id)
                    course_org.fav_nums -= 1
                    course_org.save()
                elif fav_type == 3:
                    teacher = Teacher.objects.get(id=fav_id)
                    teacher.fav_nums -= 1
                    teacher.save()
                return JsonResponse({
                    "status": "success",
                    "msg": "收藏",
                })

            # 如果没有收藏,自己新建一个收藏对象,
            else:
                user_fav = UserFavorite()
                user_fav.fav_id = fav_id
                user_fav.fav_type = fav_type
                # 这一步非常重要,user作为外键,是必填字段,这里只能手动添加
                user_fav.user = request.user
                user_fav.save()

                return JsonResponse({
                    "status": "success",
                    "msg": "已收藏",
                })
        # 字段检验不通过
        else:
            return JsonResponse({
                "status": "fail",
                "msg": "参数格式错误",
            })
