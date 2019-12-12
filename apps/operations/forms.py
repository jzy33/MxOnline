from django import forms
from apps.operations.models import UserFavorite, CourseComments


# ModelForm,以从其它model里导入字段,从而快速生成form
class UserFavForm(forms.ModelForm):
    class Meta:
        # model,指明来源于modeld的哪一张表
        model = UserFavorite
        # fields,指明哪些字段需要生成,这里我们不需要生成add_time
        fields = ['fav_id', 'fav_type']


# 用户提交对课程的评论
class CommentsForm(forms.ModelForm):
    class Meta:
        # model,指明来源于modeld的哪一张表
        model = CourseComments
        # fields,指明哪些字段需要生成
        fields = ['course', 'comments']
