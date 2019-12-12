from django.db import models
from DjangoUeditor.models import UEditorField

from apps.courses.models import BaseModel


class City(BaseModel):
    name = models.CharField(max_length=20, verbose_name='城市名')
    desc = models.CharField(max_length=200, verbose_name='描述')

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

# 所有的机构
class CourseOrg(BaseModel):
    name = models.CharField(verbose_name='机构名称', max_length=50)
    desc = UEditorField(verbose_name='描述',width=600,height=300,
                          imagePath='courses/ueditor/images/',
                          filePath='courses/ueditor/files',
                          default='',
                          )
    tag = models.CharField(verbose_name='机构标签', max_length=10, default='')
    category = models.CharField(default='pxjg', verbose_name='机构类别', max_length=4,
                                choices=(('pxjg', '培训机构'), ('gr', '个人'), ('gx', '高校')))
    # 用于机构的排序
    click_nums = models.IntegerField(default=0, verbose_name='点击数')
    fav_nums = models.IntegerField(default=0, verbose_name='收藏数')
    image = models.ImageField(upload_to='org/%Y/%m', verbose_name='logo', max_length=100)
    address = models.CharField(max_length=150, verbose_name='机构地址')
    students = models.IntegerField(default=0, verbose_name='学习人数')
    course_nums = models.IntegerField(default=0, verbose_name='课程数')

    # 认证,金牌字段,用于认证和金牌图片显示
    is_auth = models.BooleanField(default=False, verbose_name='是否认证')
    is_gold = models.BooleanField(default=False, verbose_name='是否金牌')

    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='所在城市')

    # 拿到该机构所有的经典课程的前3个,返给机构页面的经典课程用的
    def courses(self):
        courses = self.courses_set.filter(is_classics=True)[:3]
        return courses

    class Meta:
        verbose_name = '课程机构'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

from apps.users.models import UserProfile
class Teacher(BaseModel):
    # 由于是中途才添加的user外键,所以当前teacher表已经存在数据,此时最好设置为SET_NULL
    user=models.OneToOneField(UserProfile,null=True,blank=True,on_delete=models.SET_NULL,verbose_name="用户")
    org = models.ForeignKey(CourseOrg, on_delete=models.CASCADE, verbose_name='所属机构')
    name = models.CharField(max_length=50, verbose_name='教师名')
    work_years = models.IntegerField(default=0, verbose_name='工作年限')
    work_company = models.CharField(max_length=50, verbose_name='就职公司')
    work_position = models.CharField(max_length=50, verbose_name='公司职位')
    points = models.CharField(max_length=50, verbose_name='教学特点')
    click_nums = models.IntegerField(default=0, verbose_name='点击数')
    fav_nums = models.IntegerField(default=0, verbose_name='收藏数')
    age = models.IntegerField(default=18, verbose_name='年龄')
    imgage = models.ImageField(upload_to='teacher/%Y/%m', max_length=100, verbose_name='头像')

    class Meta:
        verbose_name = '教师'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    # 给机构->机构讲师->课程数 用的
    def course_num(self):
        return self.courses_set.all().count()
