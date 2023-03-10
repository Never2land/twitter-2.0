from django.contrib import admin

from tweets.models import Tweet, TweetPhoto


@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'content', 'created_at')
    date_hierarchy = 'created_at'


@admin.register(TweetPhoto)
class TweetPhotoAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'tweet',
        'user',
        'file',
        'status',
        'has_deleted',
        'created_at',
    )
    date_hierarchy = 'created_at'
