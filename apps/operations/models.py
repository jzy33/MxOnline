from django.db import models
from django.contrib.auth import get_user_model  # django内置方法,获取setting里的AUTH_USER_MODEL变量

from apps.users.models import BaseModel
from apps.courses.models import Courses

UserProfile = get_user_model()


# 轮播图用的model
class Banner(BaseModel):
    title = models.CharField(max_length=100, verbose_name="标题")
    image = models.ImageField(upload_to="banner/%Y/%m", max_length=200, verbose_name="轮播图")
    url = models.URLField(max_length=200, verbose_name="访问地址")
    # 顺序,谁在前,谁在后
    index = models.IntegerField(default=0, verbose_name="顺序")

    class Meta:
        verbose_name = '轮播图'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


# 用户咨询,不需要用户登录,所以不需要设置user的外键
class UserAsk(BaseModel):
    name = models.CharField(max_length=20, verbose_name='姓名')
    mobile = models.CharField(max_length=11, verbose_name='手机')
    course_name = models.CharField(max_length=50, verbose_name='课程名')

    class Meta:
        verbose_name = '用户咨询'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}_{self.course_name}({self.mobile})"


# 用户对课程的评论,需要登录之后,所以需要设置user外键(外键名最好使用全局变量AUTH_USER_MODEL,方便后期更改)
# 也需要知道是哪一个课程,所以需要courses外键
class CourseComments(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name='课程')
    comments = models.CharField(max_length=200, verbose_name='评论内容')

    class Meta:
        verbose_name = '课程评论'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.comments


# 用户收藏,用户可以收藏course,CourseOrg,Teacher等.
# 需要设置user外键,course外键,Teacher外键,但这种做法明显不合理,当后面需要新增外键时,无疑会导致修改表结构
# 所以,应该以choice的方式
class UserFavorite(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    # course = models.ForeignKey(Courses, verbose_name='课程')
    # teacher = models.ForeignKey(Teacher, verbose_name='讲师')
    fav_id = models.IntegerField(verbose_name='数据id')
    fav_type = models.IntegerField(choices=((1, '课程'), (2, '课程机构'), (3, '讲师')), default=1, verbose_name='收藏类型')

    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username}_{self.fav_id}"


# 用户消息,注意应该设置一个布尔类型(点一下,就清空未读消息)
class UserMessage(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    message = models.CharField(max_length=200, verbose_name='消息内容')
    has_read = models.BooleanField(default=False, verbose_name='是否已读')

    class Meta:
        verbose_name = '用户消息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.message


# 用户学习的课程,先设置一对多,后面再来设置多对多,不影响
class UserCourse(BaseModel):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, verbose_name='用户')
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name='课程')

    class Meta:
        verbose_name = '用户课程'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.course.name
