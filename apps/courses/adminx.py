import xadmin  # 导入xadmin
# NewCoursesAdmin的模块,自定义排版
from xadmin.layout import Fieldset, Main, Side, Row
from import_export import resources

from apps.courses.models import Courses, Lesson, Video, CourseResource, CourseTag, BannerCourse  # 导入所有的表


# xadmin的全局配置
class GlobalSettings:
    # 系统名字
    site_title = '慕学后台管理系统'
    # 页脚
    site_footer = '慕学在线网'
    # 菜单栏折叠功能
    menu_style = 'accordion'


class BsaeSettings:
    # 打开主题功能
    enable_themes = True
    # 打开在线下载主题功能
    use_bootswatch = True


# model的注册  类名规则: 表+admin
class CoursesAdmin(object):
    # 指定显示的字段,可以有外键
    list_display = ['name', 'desc', 'detail', 'degree', 'learn_times', 'students', ]
    # 指定搜索的范围
    search_fields = ['name', 'desc', 'detail', 'degree', 'students', ]
    # 指定过滤器的范围,若是外键,需要指定外键的字段名,否则不显示
    list_filter = ['name', 'teacher__name', 'desc', 'detail', 'degree', 'learn_times', 'students', ]
    # 指定哪些字段是可编辑的
    list_editable = ['degree', 'desc', ]


# 需求,单独一张表来管理首页的轮播图中的课程,即多个管理器管理同一张表的某些数据(需要重载queryset)
class BannerCourseAdmin(object):
    # 显示字段这些还是和NewCoursesAdmin一样,也可以不一样
    list_display = ['name', 'desc', 'show_image', 'go_to', 'detail', 'degree', 'learn_times', 'students', ]
    search_fields = ['name', 'desc', 'detail', 'degree', 'students', ]
    list_filter = ['name', 'teacher__name', 'desc', 'detail', 'degree', 'learn_times', 'students', ]
    list_editable = ['degree', 'desc', ]
    model_icon = 'fa fa-microchip'

    def queryset(self):
        qs = super().queryset()
        # 该管理器中,只显示轮播课程
        qs = qs.filter(is_banner=True)
        return qs


# 需求,在course的编辑页面,同时也能编辑lesson表
class LessonInline(object):
    model = Lesson
    style = "tab"  # tab横向并排显示,默认是纵向展开
    extra = 0  # 0就是不自动新增,1就是自动增加一个提供给用户编辑
    exclude = ["add_time"]  # 也可以使用这种配置


class CourseResourceInline(object):
    model = CourseResource
    style = "tab"  # 使用tab时,手动添加数据会有bug,所有要结合extra=1一起使用
    extra = 1


# 需求,完成adminx后台管理页面的导入导出功能
class MyResource(resources.ModelResource):
    class Meta:
        model = Courses
        # fields = ('name', 'description',)
        # exclude = ()


# model的注册  自定义adminx的排版格式
class NewCoursesAdmin(object):
    # 需求,完成adminx后台管理页面的导入导出功能
    import_export_args = {'import_resource_class': MyResource, 'export_resource_class': MyResource}
    # 指定显示的字段,可以有外键
    list_display = ['name', 'desc', 'show_image', 'go_to', 'detail', 'degree', 'learn_times', 'students', ]
    # 指定搜索的范围
    search_fields = ['name', 'desc', 'detail', 'degree', 'students', ]
    # 指定过滤器的范围,若是外键,需要指定外键的字段名,否则不显示
    list_filter = ['name', 'teacher__name', 'desc', 'detail', 'degree', 'learn_times', 'students', ]
    # 指定哪些字段是可编辑的
    list_editable = ['degree', 'desc', ]
    # 指定哪些字段只读,readonly_fields的优先级大于exclude
    readonly_fields = ["students", "add_time", ]
    # 指定哪些字段不显示出来,但在'显示列'中,仍然可以把他们设置出来
    exclude = ["click_nums", "fav_nums"]
    # 指定默认排序
    ordering = ["-students"]
    # 自定义图标(需要自己下载最新的font-awesome-4.7.0,替换掉xadmin>static>xadmin>vender>font-awesome>css和fonts文件夹
    # 后台管理页面,"课程管理"的图标是他下面的表的第一个表的图标
    # http://www.fontawesome.com.cn/
    # fa-handshake-o 是图标的名称
    model_icon = 'fa fa-handshake-o'
    # 在编辑该表的同时,也可以对其它有关联的表进行新增操作
    inlines = [LessonInline, CourseResourceInline]

    # 指定detail为富文本字段格式(前提是ueditor插件已经注册了)
    style_fields = {
        "detail": "ueditor",
    }

    # 需求,teacher可以作为登录用户(需要给teacher添加一个一对一的user外键)
    # 同时,该teacher只能查看自己的课程(重载queryset方法)
    def queryset(self):
        # 取出当前表单的所有对象
        qs = super().queryset()
        if not self.request.user.is_superuser:
            # 对于OneToOne这种外键,可直接反向取user.teacher
            qs = qs.filter(teacher=self.request.user.teacher)
        return qs

    def get_form_layout(self):
        # self.org_obj指的是,仅当修改的时候才采用本设置,新建还是老样式
        if self.org_obj:
            self.form_layout = (
                Main(
                    Fieldset('讲师信息',
                             'teacher', 'course_org',
                             # 不给当前区域取名
                             css_class='unsort no_title'
                             ),
                    Fieldset('基本信息',
                             'name', 'desc',
                             Row('learn_times', 'degree'),
                             Row('category', 'tag'),
                             'youneed_know', 'teacher_tell', 'detail',
                             ),
                ),
                Side(
                    Fieldset('访问信息',
                             # 'fav_nums', 'click_nums',
                             'students', 'add_time',
                             ),
                ),
                Side(
                    Fieldset('选择信息',
                             'is_banner', 'is_classics',
                             ),
                ),
            )
        # print(self.__class__.__mro__)
        # print(NewCoursesAdmin.mro())
        return super(NewCoursesAdmin, self).get_form_layout()


class LessonAdmin(object):
    list_display = ['course', 'name', 'add_time', ]
    search_fields = ['course', 'name', ]
    list_filter = ['course__name', 'name', 'add_time', ]


class VideoAdmin(object):
    list_display = ['lesson', 'name', 'add_time', ]
    search_fields = ['lesson', 'name', ]
    list_filter = ['lesson', 'name', 'add_time', ]


class CourseResourceAdmin(object):
    list_display = ['course', 'name', 'file', 'add_time', ]
    search_fields = ['course', 'name', 'file', ]
    list_filter = ['course', 'name', 'file', 'add_time', ]


class CourseTagAdmin(object):
    list_display = ['course', 'tag', 'add_time', ]
    search_fields = ['course', 'tag', ]
    list_filter = ['course', 'tag', 'add_time', ]


# 注册model
# xadmin.site.register(Courses, CoursesAdmin)
xadmin.site.register(Courses, NewCoursesAdmin)
xadmin.site.register(BannerCourse, BannerCourseAdmin)
xadmin.site.register(Lesson, LessonAdmin)
xadmin.site.register(Video, VideoAdmin)
xadmin.site.register(CourseResource, CourseResourceAdmin)
xadmin.site.register(CourseTag, CourseTagAdmin)
# 注册全局配置
xadmin.site.register(xadmin.views.CommAdminView, GlobalSettings, )
xadmin.site.register(xadmin.views.BaseAdminView, BsaeSettings, )
