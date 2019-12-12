from django.db import models
from DjangoUeditor.models import UEditorField

from apps.users.models import BaseModel
from apps.organizations.models import Teacher, CourseOrg


class Courses(BaseModel):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='讲师')

    # 由于一个机构有多个老师,一个老师有多个课程,但是课程和机构没有直接的联系,
    # 所以当课程和机构之间出现查询时就会比较麻烦,所以需要一个课程和机构之间的外键
    course_org = models.ForeignKey(CourseOrg, null=True, blank=True, on_delete=models.CASCADE, verbose_name='课程的机构')

    name = models.CharField(verbose_name='课程名', max_length=50)
    desc = models.CharField(verbose_name='课程描述', max_length=300)
    learn_times = models.IntegerField(verbose_name='学习时长(分钟数)', default=0)
    degree = models.CharField(verbose_name='难度', choices=(('cj', '初级'), ('zj', '中级'), ('gj', '高级')), max_length=2)
    students = models.IntegerField(verbose_name='学习人数', default=0)
    fav_nums = models.IntegerField(verbose_name='收藏人数', default=0)
    click_nums = models.IntegerField(verbose_name='点击数', default=0)
    notice = models.CharField(verbose_name='课程公告', max_length=300, default='')
    category = models.CharField(verbose_name='课程类别', max_length=20, default=u'后端开发')
    tag = models.CharField(verbose_name='课程标签', max_length=10, default='')
    youneed_know = models.CharField(verbose_name='课程须知', max_length=300, default='')
    teacher_tell = models.CharField(verbose_name='老师告诉你', max_length=300, default='')

    # 是否是广告位
    is_banner = models.BooleanField(default=False, verbose_name="是否广告位")
    # 是否是经典课程
    is_classics = models.BooleanField(default=False, verbose_name='是否经典')

    # detail使用富文本字段
    detail = UEditorField(verbose_name='课程详情',width=600,height=300,
                          imagePath='courses/ueditor/images/',
                          filePath='courses/ueditor/files',
                          default='',
                          )
    image = models.ImageField(verbose_name='封面图', upload_to='courses/%Y/%m', max_length=100)

    def lesson_nums(self):
        return self.lesson_set.all().count()

    class Meta:
        verbose_name = '课程信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    # 需求: 让"课程信息"页面可直接看到各个课程的图片
    # 别忘记配置adminx的list_display = ['name', 'desc', 'show_image', 'go_to', .....
    def show_image(self):
        from django.utils.safestring import mark_safe
        return mark_safe("<img src='{}'>".format(self.image.url))
    # 给当前功能列命名
    show_image.short_description = "图片"

    # 需求: 让"课程信息"页面增加跳转功能,可直接跳转到当前课程的html
    # 别忘记配置adminx的list_display = ['name', 'desc', 'show_image', 'go_to', .....
    def go_to(self):
        from django.utils.safestring import mark_safe
        return mark_safe("<a href='/course/{}'>跳转</a>".format(self.id))
    # 给当前功能列命名
    go_to.short_description = "跳转"


# 需求,单独一张表来管理首页的轮播图中的课程,即多个管理器管理同一张表的某些数据(需要重载queryset)
# 需要继承想要管理的表
class BannerCourse(Courses):
    class Meta:
        verbose_name = "轮播课程"
        verbose_name_plural = verbose_name
        # proxy=True,指仅仅作为代理管理,而不需要真正在数据库新建这么一张表
        proxy = True


# 一门课程应该有多个tag,所以单独弄一张表
class CourseTag(BaseModel):
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name='课程')
    tag = models.CharField(max_length=100, verbose_name='标签')

    class Meta:
        verbose_name = '课程标签'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.tag


class Lesson(BaseModel):
    name = models.CharField(max_length=20, verbose_name='章节名字')
    learn_times = models.IntegerField(verbose_name='学习时长(分钟数)', default=0)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name='课程')

    class Meta:
        verbose_name = '课程章节'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Video(BaseModel):
    name = models.CharField(max_length=100, verbose_name='视频名')
    learn_times = models.IntegerField(verbose_name='学习时长(分钟数)', default=0)
    url = models.CharField(verbose_name='访问地址', max_length=1000)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name='章节')

    class Meta:
        verbose_name = '视频'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class CourseResource(BaseModel):
    name = models.CharField(max_length=50, verbose_name='名称')
    file = models.FileField(upload_to='courses/resource/%Y/%m', verbose_name='下载地址', max_length=200)
    course = models.ForeignKey(Courses, on_delete=models.CASCADE, verbose_name='课程')

    class Meta:
        verbose_name = '课程资源'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
