import json
import time

from django.shortcuts import render
from django.views.generic import TemplateView
from blog.models import Article, Category, Tag
import math
import markdown
from django.core.cache import cache
from django.core.serializers import serialize, deserialize
from django.http.response import JsonResponse
from rest_framework.views import APIView
from .serializers import ArticleSerializer
from django.db import transaction


# 文章列表
class IndexView(TemplateView):
    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        article_list = Article.objects.all().order_by('-create_time')

        for article in article_list:
            article.pub_date = article.create_time.strftime('%m-%d')
            article.length = len(article.text)
            article.read_time = math.ceil(len(article.text) / 180) if article.text else 0

            article.categories = article.category_set.values()
            article.tags = article.tag_set.values()

        context = {
            'article_list': article_list
        }
        return self.render_to_response(context)


# 文章详情
class DetailView(TemplateView):
    template_name = 'detail.html'

    def get(self, request, *args, **kwargs):
        print(request.path)
        article = Article.objects.get(url=request.path)
        print(article)
        content = ''

        for line in article.text.split("\n"):
            content += line.strip('  ') if '```' in line else line
            content += "\n"

        article.content = markdown.markdown(content, extensions=[
            # 标题转换
            'markdown.extensions.extra',
            # 代码高亮
            'markdown.extensions.codehilite',
            # 表单渲染
            'markdown.extensions.toc',
        ])

        next_article_set = Article.objects.raw(
            f"select * from {Article._meta.db_table} where id < {article.id} order by id desc limit 1")
        pre_article_set = Article.objects.raw(
            f"select * from {Article._meta.db_table} where id > {article.id} order by id desc limit 1")

        try:
            context = {
                'article': article,
                'next_article': next_article_set[0],
                'pre_article': pre_article_set[0]
            }
        except IndexError:
            context = {
                'article': article,
            }
        return self.render_to_response(context)


# 归档页面
class ArchiveView(TemplateView):
    template_name = 'archive.html'

    """
        archive_dict = {'year': year, article_list:[]}
    """

    def get(self, request, *args, **kwargs):

        cache_key = 'archive_key'
        cache_values = cache.get(cache_key)

        if cache_values:
            serialize_archives = json.loads(cache_values)
            archive_list = []
            article_count = 0
            for archive in serialize_archives:
                archive_list.append({
                    'year': archive['year'],
                    'article_list': [obj.object for obj in deserialize('json', archive['article_list'])]
                })
                article_count += len(archive['article_list'])

            context = {
                'archive_list': archive_list,
                'article_count': article_count,
            }

        else:
            print('not hit cache,need to query db')
            article_list = Article.objects.all()

            article_count = len(article_list)

            archive_dic = {}
            for article in article_list:
                year = article.create_time.strftime('%Y')
                article.show_time = article.create_time.strftime('%Y-%m-%d')
                archive_dic.setdefault(year, {'year': year, 'article_list': []})
                archive_dic[year]['article_list'].append(article)

            context = {
                'archive_list': archive_dic.values(),
                'article_count': article_count,
            }

            serialize_archives = []
            for archive in archive_dic.values():
                serialize_archives.append({
                    'year': archive['year'],
                    'article_list': serialize('json', archive['article_list'])
                })

            cache.set(cache_key, json.dumps(serialize_archives))
            cache.expire(cache_key, 30)

        return self.render_to_response(context)

# 分类页面
class CategoriesView(TemplateView):
    template_name = 'categories.html'

    def get(self, request, *args, **kwargs):

        categories = Category.objects.all()

        # 拿到顶部标题的名称数组
        category_names_dic = {}
        for category in categories:
            name = category.name
            article_id = category.article_id
            category_names_dic.setdefault(name, {'name': name, 'article_list': [], 'article_count': 0})

            article_list = Article.objects.raw(f'select * from {Article._meta.db_table} where id = {article_id}')

            article_list[0].show_time = article_list[0].create_time.strftime('%Y-%m-%d')
            print(article_list[0])
            category_names_dic[name]['article_list'].append(article_list[0])

        for cate in category_names_dic.values():
            cate['article_count'] = len(cate['article_list'])

        context = {
            'categories_count': len(category_names_dic.values()),
            'categories': category_names_dic.values()
        }

        return self.render_to_response(context)

# 关于
class AboutView(TemplateView):
    template_name = 'about.html'

# 文章页面
class ArticleApiView(APIView):
    def get(self, request, *args, **kwargs):
        # 获取url中的参数
        limit_num = request.GET.get('limit_num')
        print(f'==={request.path}')
        if limit_num:
            article_list = Article.objects.all()[:int(limit_num)]
        else:
            article_list = Article.objects.all()

        se_article_list = ArticleSerializer(article_list, many=True)

        return JsonResponse({
            'status': 200,
            'article_list': se_article_list.data
        }, safe=False)

    def post(self, request, *args, **kwargs):
        print("新增文章")
        try:
            message = {}
            with transaction.atomic():
                title = request.POST['title']
                text = request.POST['text']
                categories = json.loads(request.POST['categories'])
                tags = json.loads(request.POST['tags'])

                article_data = {
                    'title': title,
                    'text': text,
                    'url': f'{time.strftime("%Y%m%d")}/{title}.html/'
                }

                se_article = ArticleSerializer(data=article_data)
                se_article.is_valid()
                article = se_article.create(se_article.data)
                article.save()

                for category in categories:
                    cate = Category(
                        name=category['name'],
                        slug=category['slug'],
                        uri=f'/categories/{category["slug"]}/'
                    )
                    cate.article = article
                    cate.save()

                for tag in tags:
                    ta = Tag(
                        name=tag['name'],
                        slug=tag['slug'],
                        uri=f'/tags/{tag["slug"]}/'
                    )
                    ta.article = article
                    ta.save()
                message = {'status': 200, 'article': article_data}
        except:
            message = {'status': 500, 'reason': 'error', 'article': ''}
        finally:
            response = JsonResponse(message, safe=False)
            # 允许跨域设置 *表示任意
            # 允许跨域的主机名
            response['Access-Control-Allow-Origin'] = '*'
            # headers
            response['Access-Control-Allow-Headers'] = '*'
            # 方法
            response['Access-Control-Allow-Methods'] = 'OPTIONS, POST, GET'
            return response

    def put(self, request, *args, **kwargs):
        print("修改")
        # 无法运行
        title = request.POST['title']

        article_json = Article.objects.raw(f'select * from {Article._meta.db_table} where title like %{title}%')

        se_article = ArticleSerializer(article_json)

        article = se_article.data

        article['title'] = title
        article.save()

        message = {'status': 200, 'msg': 'Success'}
        return JsonResponse(message, safe=False)


    def delete(self, request, *args, **kwargs):
        pass
