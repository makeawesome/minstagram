from django.contrib import admin
from . import models

# model이 admin panel에서 어떻게 시각화할 것인지 결정

@admin.register(models.Image) # decorator
class ImageAdmin(admin.ModelAdmin):
    list_display_links = ( # admin panel에 출력된 object의 field에 링크를 걸 목록        
        'location',
    )

    search_fields = ( # 검색 필드로 사용할 field 목록
        'location',
    )

    list_filter = ( # filter로 사용할 field 목록
        'location',
        'creator',
    )

    list_display = (
        'file',
        'location',
        'caption',
        'creator',
        'created_at',
        'updated_at',
    )

@admin.register(models.Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = (
        'creator',
        'image',
        'created_at',
        'updated_at',
    )

@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'message',
        'creator',
        'image',
        'created_at',
        'updated_at',
    )

