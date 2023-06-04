"""
URL configuration for lab3 project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.signin),
    path('index/', views.index),
    # paper
    path('paper/search/', views.paper_search),
    path('paper/insert', views.paper_insert),
    re_path(r'^paper/[A-Z0-9]{10}/update/$', views.paper_update),
    # project
    path('project/search/', views.project_search),
    path('project/insert', views.project_insert),
    re_path(r'^project/[a-zA-Z0-9]{5}/update$', views.project_update),
    #course
    path('course/search/', views.course_search),
    path('course/insert', views.course_insert),
    re_path(r'^course/[a-zA-Z0-9]{10}/update$', views.course_update)
]
