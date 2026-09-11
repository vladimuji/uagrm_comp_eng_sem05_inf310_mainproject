"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
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
from django.urls import path
from logistics.views import BaseView, TreeView, GraphView, HeapView
from logistics.views.api_views import TreeOperationView, ExpressionTreeView
from logistics.views.system_views import RestoreDatabaseView

urlpatterns = [
    path('', BaseView.as_view(), name='home'),
    path('base/', BaseView.as_view()),
    path('trees/', TreeView.as_view(), name='trees'),
    path('graphs/', GraphView.as_view(), name='graphs'),
    path('heaps/', HeapView.as_view(), name='heaps'),
    path('admin/', admin.site.urls),

        # avl / bst / bway / mway -> DB-backed CRUD-ish endpoint
    path('api/trees/<str:kind>/', TreeOperationView.as_view(), name='tree-api'),
 
    # expression tree -> ephemeral, no DB, no 'kind'
    path('api/trees/expression/', ExpressionTreeView.as_view(), name='expression-tree-api'),

    path('system/restore/<str:token>/', RestoreDatabaseView.as_view(), name='restore-db'),
]
