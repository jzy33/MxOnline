from django.conf.urls import url

from apps.operations.views import AddFavView,CommentView

urlpatterns = [
    # 添加收藏,删除收藏接口
    url(r'^fav/$', AddFavView.as_view(), name='fav',),

    url(r'^comment/$', CommentView.as_view(), name='comment',),

]
