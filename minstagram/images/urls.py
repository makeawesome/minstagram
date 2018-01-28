from django.conf.urls import url
from . import views

urlpatterns = [
    # url은 3가지로 이루어짐
    # 1. Regular expression 2. view 3. name
    # 위에서부터 순차적으로 url과 매칭되는 정규식을 찾는다.
    # 정규식을 찾으면 view를 실행한다.
    url(
        regex = r'^$',
        view = views.Feed.as_view(),
        name = 'feed',
    ),

    url(
        regex = r'^(?P<image_id>[0-9]+)/likes/',
        view = views.LikeImage.as_view(),
        name='like_image',
    ),

    url(
        regex=r'^(?P<image_id>[0-9]+)/unlikes/',
        view=views.UnlikeImage.as_view(),
        name='like_image',
    ),

    url(
        regex = r'^(?P<image_id>[0-9]+)/comments/',
        view = views.CommentOnImage.as_view(),
        name='comment_on_image'
    ),

    url(
        regex = r'^comments/(?P<comment_id>[0-9]+)/$',
        view = views.Comment.as_view(),
        name = 'comment',
    ),

    url(
        regex=r'^search/$',
        view = views.Search.as_view(),
        name = 'search'
    ),
]
