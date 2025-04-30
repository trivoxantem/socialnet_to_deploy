# feed/admin.py
from django.contrib import admin
from .models import Post, Comment, Profile, Group, Message

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(Profile)

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    filter_horizontal = ('members',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'group', 'timestamp')
    list_filter = ('group', 'sender')
