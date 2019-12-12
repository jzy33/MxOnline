import xadmin

from apps.operations.models import UserAsk, UserMessage, UserCourse, UserFavorite, CourseComments
from apps.operations.models import Banner


# 轮播图
class BannerAdmin(object):
    list_display = ['title', 'image', 'url', 'index']
    search_fields = ['title', 'image', 'url', 'index']
    list_filter = ['title', 'image', 'url', 'index']


class UserAskAdmin(object):
    list_display = ['name', 'mobile', 'course_name', 'add_time']
    search_fields = ['name', 'mobile', 'course_name', ]
    list_filter = ['name', 'mobile', 'course_name', 'add_time']


class CourseCommentsAdmin(object):
    list_display = ['user', 'course', 'comments', 'add_time']
    search_fields = ['user', 'course', 'comments', ]
    list_filter = ['user', 'course__name', 'comments', 'add_time']


class UserFavoriteAdmin(object):
    list_display = ['user', 'fav_id', 'fav_type', 'add_time']
    search_fields = ['user', 'fav_id', 'fav_type', ]
    list_filter = ['user', 'fav_id', 'fav_type', 'add_time']


class UserMessageAdmin(object):
    list_display = ['user', 'message', 'has_read', 'add_time']
    search_fields = ['user', 'message', 'has_read', ]
    list_filter = ['user', 'message', 'has_read', 'add_time']


class UserCourseAdmin(object):
    list_display = ['user', 'course', 'add_time', ]
    search_fields = ['user', 'course', ]
    list_filter = ['user', 'course__name', 'add_time', ]

    # 需求:当新增usercourse时,让course.students字段自动加1
    def save_models(self):
        # 当新增或修改当前表时,都会自动封装self.new_obj
        # 若self.new_obj有id说明是修改,若没有则说明是新增
        obj=self.new_obj
        if not obj.id:
            # 检查到时新增数据,首先保存当前对象
            obj.save()
            # 再取出器course对象
            course=obj.course
            # 然后执行学生+1
            course.students+=1
            course.save()


xadmin.site.register(UserAsk, UserAskAdmin)
xadmin.site.register(CourseComments, CourseCommentsAdmin)
xadmin.site.register(UserFavorite, UserFavoriteAdmin)
xadmin.site.register(UserMessage, UserMessageAdmin)
xadmin.site.register(UserCourse, UserCourseAdmin)
xadmin.site.register(Banner, BannerAdmin)
