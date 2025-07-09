from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

app_name = 'todoapp'

urlpatterns = [
    # Main views
    path('', login_required(views.TodoListView.as_view()), name='todo_list'),
    path('dashboard/', login_required(views.DashboardView.as_view()), name='dashboard'),
    path('create/', login_required(views.TodoCreateView.as_view()), name='todo_create'),
    path('update/<int:pk>/', login_required(views.TodoUpdateView.as_view()), name='todo_update'),
    path('delete/<int:pk>/', login_required(views.TodoDeleteView.as_view()), name='todo_delete'),
    path('complete/<int:pk>/', login_required(views.TodoCompleteView.as_view()), name='todo_complete'),
    
    # Category management
    path('categories/', login_required(views.CategoryListView.as_view()), name='category_list'),
    path('categories/create/', login_required(views.CategoryCreateView.as_view()), name='category_create'),
    path('categories/update/<int:pk>/', login_required(views.CategoryUpdateView.as_view()), name='category_update'),
    path('categories/delete/<int:pk>/', login_required(views.CategoryDeleteView.as_view()), name='category_delete'),
    
    # Task scheduling and planning
    path('schedule/', login_required(views.TaskSchedulingView.as_view()), name='task_scheduling'),
    
    # Bulk operations
    path('bulk/', login_required(views.BulkOperationsView.as_view()), name='bulk_operations'),
    
    # Quick operations
    path('quick-add/', login_required(views.QuickAddView.as_view()), name='quick_add'),
    
    # Export functionality
    path('export/', login_required(views.ExportView.as_view()), name='export'),
    
    # API endpoints
    path('api/search/', views.SearchAPIView.as_view(), name='search_api'),
    path('api/analytics/', views.TodoAnalyticsView.as_view(), name='analytics_api'),
    path('api/stats/', views.TaskStatsAPIView.as_view(), name='task_stats_api'),
    path('api/notes/', views.NotesAPIView.as_view(), name='notes_api'),
    path('api/alerts/', views.AlertAPIView.as_view(), name='alerts_api'),
] 