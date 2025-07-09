from django.contrib import admin
from .models import Todo, Category, Tag, Comment, TaskActivity

@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'created_at', 'due_date', 'completed', 'priority')
    list_filter = ('completed', 'priority', 'created_at')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 20

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user',)
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    list_filter = ('user',)
    search_fields = ('name',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('todo', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('content',)

@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = ('todo', 'user', 'action', 'created_at')
    list_filter = ('action', 'created_at')
    search_fields = ('description',) 