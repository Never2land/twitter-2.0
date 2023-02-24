from django.contrib import admin
from friendships.models import Friendships


@admin.register(Friendships)
class FriendshipAdmin(admin.ModelAdmin):
    list_display = ('id', 'from_user', 'to_user', 'created_at')
    ordering = ('-created_at',)
