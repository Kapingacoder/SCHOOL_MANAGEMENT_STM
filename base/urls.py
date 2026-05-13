from django.urls import path
from . import views
from parent_dashboard import views as parent_views

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('parent/all-results/', views.parent_all_children_results, name='parent_all_children_results'),
    path('parent/documents/', parent_views.documents_list, name='parent_documents'),
]
