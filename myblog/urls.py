"""myblog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from blog.views import IndexView, DetailView, ArchiveView, ArticleApiView, CategoriesView, AboutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', IndexView.as_view()),
    path('archives/', ArchiveView.as_view()),
    path('categories/', CategoriesView.as_view()),
    path('about/', AboutView.as_view()),
    path('api/article/', ArticleApiView.as_view()),
    path('api/article', ArticleApiView.as_view()),
    path('<str:date>/<str:uri>/', DetailView.as_view()),
    path('mdeditor/', include('mdeditor.urls'))
] + static(settings.STATIC_URL) + static(settings.MEDIA_URL, documents=settings.MEDIA_ROOT)
