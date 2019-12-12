import xadmin

from apps.organizations.models import Teacher, City, CourseOrg


class TeacherAdmin(object):
    list_display = ['org', 'name', 'work_years', 'work_company']
    search_fields = ['org', 'name', 'work_years', 'work_company']
    list_filter = ['org', 'name', 'work_years', 'work_company']


class CourseOrgAdmin(object):
    list_display = ['name', 'desc', 'click_nums', 'fav_nums']
    search_fields = ['name', 'desc', 'click_nums', 'fav_nums']
    list_filter = ['name', 'desc', 'click_nums', 'fav_nums']
    style_fields = {
        "desc": "ueditor",
    }


class CityAdmin(object):
    list_display = ['id', 'name', 'desc']  # 为该表增加字段显示功能,默认只显示第一个字段
    search_fields = ['name', 'desc']  # 为该表增加搜索插件
    list_filter = ['name', 'desc', 'add_time']  # 为该表增加过滤器,并指定可过滤的字段
    list_editable = ['name', 'desc', ]  # 为该表增加过滤器,并指定可过滤的字段


xadmin.site.register(Teacher, TeacherAdmin)
xadmin.site.register(CourseOrg, CourseOrgAdmin)
xadmin.site.register(City, CityAdmin)
