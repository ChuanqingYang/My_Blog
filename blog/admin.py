from django.contrib import admin
from blog.models import Article, Category, Tag
# Register your models here.

class CategoryInline(admin.TabularInline):
    model = Category

class TagInline(admin.TabularInline):
    model = Tag

class ArticleAdmin(admin.ModelAdmin):
    inlines = [CategoryInline, TagInline]

# 注册模型
admin.site.register(Article, ArticleAdmin)