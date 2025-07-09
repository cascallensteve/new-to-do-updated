from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, View, TemplateView
from django.urls import reverse_lazy
from .models import Todo, Category, Comment, TaskActivity
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Div, Field, Submit
from crispy_forms.bootstrap import PrependedText
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
import csv
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'due_date', 'priority', 'category', 'tags', 'progress']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.Select(attrs={'class': 'form-select', 'required': False}),
            'progress': forms.NumberInput(attrs={'min': '0', 'max': '100', 'class': 'form-range'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)
            self.fields['category'].required = False  # Make category optional
        
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Div(
                Div(Field('title'), css_class='col-md-12'),
                Div(Field('description'), css_class='col-md-12'),
                css_class='row mb-3'
            ),
            Div(
                Div(Field('due_date'), css_class='col-md-6'),
                Div(Field('priority'), css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Div(
                Div(Field('category'), css_class='col-md-6'),
                Div(Field('tags'), css_class='col-md-6'),
                css_class='row mb-3'
            ),
            Div(
                Div(Field('progress'), css_class='col-md-12'),
                css_class='row'
            )
        )

class TodoListView(LoginRequiredMixin, ListView):
    model = Todo
    template_name = 'todoapp/todo_list.html'
    context_object_name = 'todos'
    paginate_by = 10

    def get_queryset(self):
        queryset = Todo.objects.filter(user=self.request.user)
        
        # Search functionality
        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        
        # Filter by status
        status_filter = self.request.GET.get('status', '')
        if status_filter:
            if status_filter == 'completed':
                queryset = queryset.filter(completed=True)
            elif status_filter == 'pending':
                queryset = queryset.filter(completed=False)
            else:
                queryset = queryset.filter(status=status_filter)
        
        # Filter by priority
        priority_filter = self.request.GET.get('priority', '')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        # Filter by category
        category_filter = self.request.GET.get('category', '')
        if category_filter:
            queryset = queryset.filter(category_id=category_filter)
        
        # Filter by due date
        due_filter = self.request.GET.get('due', '')
        if due_filter == 'today':
            queryset = queryset.filter(due_date__date=timezone.now().date())
        elif due_filter == 'week':
            week_end = timezone.now() + timedelta(days=7)
            queryset = queryset.filter(due_date__range=[timezone.now(), week_end])
        elif due_filter == 'overdue':
            queryset = queryset.filter(due_date__lt=timezone.now(), completed=False)
        
        # Sort options
        sort_by = self.request.GET.get('sort', '-created_at')
        return queryset.order_by(sort_by)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(user=self.request.user)
        context['search_query'] = self.request.GET.get('search', '')
        context['current_status'] = self.request.GET.get('status', '')
        context['current_priority'] = self.request.GET.get('priority', '')
        context['current_category'] = self.request.GET.get('category', '')
        context['current_due'] = self.request.GET.get('due', '')
        context['current_sort'] = self.request.GET.get('sort', '-created_at')
        
        # Statistics for dashboard
        user_todos = Todo.objects.filter(user=self.request.user)
        context['stats'] = {
            'total': user_todos.count(),
            'completed': user_todos.filter(completed=True).count(),
            'pending': user_todos.filter(completed=False).count(),
            'overdue': user_todos.filter(due_date__lt=timezone.now(), completed=False).count(),
            'today': user_todos.filter(due_date__date=timezone.now().date()).count(),
        }
        
        return context

class TodoCreateView(LoginRequiredMixin, CreateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todoapp/todo_form.html'
    success_url = reverse_lazy('todoapp:todo_list')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        try:
            context = super().get_context_data(**kwargs)
            # Create default category if none exists
            if not Category.objects.filter(user=self.request.user).exists():
                Category.objects.create(
                    name='General',
                    color='#1a237e',
                    icon='fas fa-tasks',
                    user=self.request.user
                )
            context['categories'] = Category.objects.filter(user=self.request.user)
            return context
        except Exception as e:
            messages.error(self.request, f'Error loading form: {str(e)}')
            return {}

    def form_valid(self, form):
        try:
            # Set the user before saving
            form.instance.user = self.request.user
            
            # Save the form
            response = super().form_valid(form)
            
            # Add success message
            messages.success(self.request, f'Task "{form.instance.title}" created successfully!')
            
            # Print debug information
            print(f"Task created - Title: {form.instance.title}, User: {self.request.user.username}, ID: {form.instance.id}")
            
            return response
        except Exception as e:
            messages.error(self.request, f'Error creating task: {str(e)}')
            print(f"Error creating task: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'Error in {field}: {error}')
        return super().form_invalid(form)

class TodoUpdateView(LoginRequiredMixin, UpdateView):
    model = Todo
    form_class = TodoForm
    template_name = 'todoapp/todo_form.html'
    success_url = reverse_lazy('todoapp:todo_list')

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class TodoDeleteView(LoginRequiredMixin, DeleteView):
    model = Todo
    template_name = 'todoapp/todo_confirm_delete.html'
    success_url = reverse_lazy('todoapp:todo_list')

    def get_queryset(self):
        return Todo.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)

class TodoCompleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        return self.toggle_completion(request, pk)
    
    def post(self, request, pk):
        return self.toggle_completion(request, pk)
    
    def toggle_completion(self, request, pk):
        try:
            todo = Todo.objects.get(pk=pk, user=request.user)
            todo.completed = not todo.completed
            if todo.completed:
                todo.mark_completed()
            todo.save()
            messages.success(request, f'Task marked as {"completed" if todo.completed else "incomplete"}!')
        except Todo.DoesNotExist:
            messages.error(request, 'Task not found.')
        
        return redirect(request.META.get('HTTP_REFERER', 'todoapp:todo_list'))

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'todoapp/enhanced_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_todos = Todo.objects.filter(user=self.request.user)
        
        # Basic statistics
        total_count = user_todos.count()
        completed_count = user_todos.filter(completed=True).count()
        
        context['stats'] = {
            'total': total_count,
            'completed': completed_count,
            'pending': user_todos.filter(completed=False).count(),
            'overdue': user_todos.filter(due_date__lt=timezone.now(), completed=False).count(),
            'today': user_todos.filter(due_date__date=timezone.now().date()).count(),
            'this_week': user_todos.filter(
                due_date__week=timezone.now().isocalendar()[1], 
                due_date__year=timezone.now().year
            ).count(),
            'completion_rate': (completed_count * 100 / total_count) if total_count > 0 else 0,
        }
        
        # Productivity statistics
        completed_this_week = user_todos.filter(
            completed_at__week=timezone.now().isocalendar()[1],
            completed_at__year=timezone.now().year,
            completed=True
        ).count()
        
        from datetime import timedelta as td
        
        context['productivity'] = {
            'completed_this_week': completed_this_week,
            'avg_completion_time': user_todos.filter(completed=True).aggregate(
                avg_time=Avg('actual_time')
            )['avg_time'] or td(0),
        }
        
        # Priority breakdown
        total_todos = context['stats']['total']
        high_count = user_todos.filter(priority='high').count()
        medium_count = user_todos.filter(priority='medium').count()
        low_count = user_todos.filter(priority='low').count()
        
        context['priority_stats'] = {
            'high': high_count,
            'medium': medium_count,
            'low': low_count,
            'high_percent': (high_count * 100 / total_todos) if total_todos > 0 else 0,
            'medium_percent': (medium_count * 100 / total_todos) if total_todos > 0 else 0,
            'low_percent': (low_count * 100 / total_todos) if total_todos > 0 else 0,
        }
        
        # Recent tasks
        context['recent_tasks'] = user_todos.order_by('-created_at')[:5]
        context['upcoming_tasks'] = user_todos.filter(
            due_date__gte=timezone.now(),
            completed=False
        ).order_by('due_date')[:5]
        
        # Category breakdown
        context['category_stats'] = Category.objects.filter(user=self.request.user).annotate(
            task_count=Count('todo')
        ).order_by('-task_count')[:5]
        
        # Weekly completion data for charts
        from datetime import timedelta
        today = timezone.now().date()
        week_data = []
        for i in range(7):
            date = today - timedelta(days=6-i)
            completed_count = user_todos.filter(
                completed_at__date=date,
                completed=True
            ).count()
            week_data.append({
                'date': date.strftime('%a'),
                'completed': completed_count
            })
        
        context['weekly_completion'] = week_data
        
        # Monthly task creation data
        month_data = []
        for i in range(12):
            month_start = timezone.now().replace(day=1, month=((timezone.now().month - i - 1) % 12) + 1)
            if month_start.month > timezone.now().month:
                month_start = month_start.replace(year=timezone.now().year - 1)
            
            tasks_created = user_todos.filter(
                created_at__year=month_start.year,
                created_at__month=month_start.month
            ).count()
            
            month_data.append({
                'month': month_start.strftime('%b'),
                'tasks': tasks_created
            })
        
        context['monthly_tasks'] = list(reversed(month_data))
        
        return context

class BulkOperationsView(LoginRequiredMixin, View):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def post(self, request):
        action = request.POST.get('action')
        task_ids = request.POST.getlist('task_ids')
        
        if not task_ids:
            return JsonResponse({'error': 'No tasks selected'}, status=400)
        
        todos = Todo.objects.filter(id__in=task_ids, user=request.user)
        
        if action == 'mark_completed':
            for todo in todos:
                todo.mark_completed()
            messages.success(request, f'{todos.count()} tasks marked as completed')
            
        elif action == 'mark_pending':
            todos.update(completed=False, status='pending')
            messages.success(request, f'{todos.count()} tasks marked as pending')
            
        elif action == 'delete':
            count = todos.count()
            todos.delete()
            messages.success(request, f'{count} tasks deleted')
            
        elif action == 'archive':
            todos.update(status='archived')
            messages.success(request, f'{todos.count()} tasks archived')
            
        elif action == 'change_priority':
            priority = request.POST.get('priority')
            if priority in ['high', 'medium', 'low']:
                todos.update(priority=priority)
                messages.success(request, f'{todos.count()} tasks priority changed to {priority}')
        
        return JsonResponse({'success': True})

class ExportView(LoginRequiredMixin, View):
    def get(self, request):
        format_type = request.GET.get('format', 'csv')
        todos = Todo.objects.filter(user=request.user)
        
        if format_type == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="tasks.csv"'
            
            writer = csv.writer(response)
            writer.writerow(['Title', 'Description', 'Status', 'Priority', 'Category', 'Due Date', 'Created', 'Progress'])
            
            for todo in todos:
                writer.writerow([
                    todo.title,
                    todo.description,
                    todo.get_status_display(),
                    todo.get_priority_display(),
                    todo.category.name if todo.category else '',
                    todo.due_date.strftime('%Y-%m-%d %H:%M') if todo.due_date else '',
                    todo.created_at.strftime('%Y-%m-%d %H:%M'),
                    todo.progress
                ])
            
            return response
            
        elif format_type == 'json':
            response = HttpResponse(content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename="tasks.json"'
            
            tasks_data = []
            for todo in todos:
                tasks_data.append({
                    'title': todo.title,
                    'description': todo.description,
                    'status': todo.status,
                    'priority': todo.priority,
                    'category': todo.category.name if todo.category else None,
                    'due_date': todo.due_date.isoformat() if todo.due_date else None,
                    'created_at': todo.created_at.isoformat(),
                    'progress': todo.progress,
                    'tags': [tag.name for tag in todo.tags.all()]
                })
            
            response.write(json.dumps(tasks_data, indent=2))
            return response

class SearchAPIView(LoginRequiredMixin, View):
    def get(self, request):
        query = request.GET.get('q', '')
        todos = Todo.objects.filter(
            user=request.user
        ).filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query)
        )[:10]
        
        results = []
        for todo in todos:
            results.append({
                'id': todo.id,
                'title': todo.title,
                'status': todo.status,
                'priority': todo.priority,
                'due_date': todo.due_date.strftime('%Y-%m-%d') if todo.due_date else None
            })
        
        return JsonResponse({'results': results})

class TodoAnalyticsView(LoginRequiredMixin, View):
    def get(self, request):
        user_todos = Todo.objects.filter(user=request.user)
        
        # Weekly completion trend
        weeks_data = []
        for i in range(8):
            week_start = timezone.now() - timedelta(weeks=i)
            week_end = week_start + timedelta(days=7)
            completed_count = user_todos.filter(
                completed_at__range=[week_start, week_end],
                completed=True
            ).count()
            weeks_data.append({
                'week': week_start.strftime('%Y-%m-%d'),
                'completed': completed_count
            })
        
        # Priority distribution
        priority_data = [
            {'priority': 'High', 'count': user_todos.filter(priority='high').count()},
            {'priority': 'Medium', 'count': user_todos.filter(priority='medium').count()},
            {'priority': 'Low', 'count': user_todos.filter(priority='low').count()},
        ]
        
        return JsonResponse({
            'weekly_trend': weeks_data,
            'priority_distribution': priority_data,
            'total_tasks': user_todos.count(),
            'completion_rate': (user_todos.filter(completed=True).count() / max(user_todos.count(), 1)) * 100
        })

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'color', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'fas fa-tasks'}),
        }

class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'todoapp/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user).annotate(
            task_count=Count('todo')
        )

class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'todoapp/category_form.html'
    success_url = reverse_lazy('todoapp:category_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, f'Category "{form.instance.name}" created successfully!')
        return super().form_valid(form)

class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'todoapp/category_form.html'
    success_url = reverse_lazy('todoapp:category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f'Category "{form.instance.name}" updated successfully!')
        return super().form_valid(form)

class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = 'todoapp/category_confirm_delete.html'
    success_url = reverse_lazy('todoapp:category_list')

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Category deleted successfully!')
        return super().delete(request, *args, **kwargs)

class TaskSchedulingView(LoginRequiredMixin, TemplateView):
    template_name = 'todoapp/task_scheduling.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_todos = Todo.objects.filter(user=self.request.user)
        
        # Tasks due today
        context['today_tasks'] = user_todos.filter(
            due_date__date=timezone.now().date(),
            completed=False
        ).order_by('due_date')
        
        # Tasks due this week
        week_start = timezone.now().date()
        week_end = week_start + timedelta(days=7)
        context['week_tasks'] = user_todos.filter(
            due_date__date__range=[week_start, week_end],
            completed=False
        ).exclude(due_date__date=timezone.now().date()).order_by('due_date')
        
        # Overdue tasks
        context['overdue_tasks'] = user_todos.filter(
            due_date__lt=timezone.now(),
            completed=False
        ).order_by('due_date')
        
        # Tasks without due date
        context['no_due_date'] = user_todos.filter(
            due_date__isnull=True,
            completed=False
        ).order_by('-priority', '-created_at')
        
        return context

class QuickAddView(LoginRequiredMixin, View):
    def post(self, request):
        title = request.POST.get('title', '').strip()
        if not title:
            return JsonResponse({'error': 'Title is required'}, status=400)
        
        todo = Todo.objects.create(
            title=title,
            user=request.user,
            priority='medium'
        )
        
        return JsonResponse({
            'success': True,
            'task': {
                'id': todo.id,
                'title': todo.title,
                'created_at': todo.created_at.strftime('%Y-%m-%d %H:%M')
            }
        })

class TaskStatsAPIView(LoginRequiredMixin, View):
    def get(self, request):
        user_todos = Todo.objects.filter(user=request.user)
        
        # Daily completion for last 30 days
        daily_stats = []
        for i in range(30):
            date = timezone.now().date() - timedelta(days=i)
            completed = user_todos.filter(
                completed_at__date=date,
                completed=True
            ).count()
            created = user_todos.filter(
                created_at__date=date
            ).count()
            daily_stats.append({
                'date': date.isoformat(),
                'completed': completed,
                'created': created
            })
        
        # Category distribution
        category_stats = Category.objects.filter(user=request.user).annotate(
            total_tasks=Count('todo'),
            completed_tasks=Count('todo', filter=Q(todo__completed=True)),
            pending_tasks=Count('todo', filter=Q(todo__completed=False))
        ).values('name', 'total_tasks', 'completed_tasks', 'pending_tasks')
        
        return JsonResponse({
            'daily_stats': daily_stats,
            'category_stats': list(category_stats),
            'total_tasks': user_todos.count(),
            'completion_rate': (user_todos.filter(completed=True).count() / max(user_todos.count(), 1)) * 100
        })

class NotesAPIView(LoginRequiredMixin, View):
    def get(self, request):
        from .models import Note
        note, created = Note.objects.get_or_create(
            user=request.user,
            title='Dashboard Notes',
            defaults={'content': ''}
        )
        return JsonResponse({
            'content': note.content,
            'updated_at': note.updated_at.isoformat()
        })
    
    def post(self, request):
        from .models import Note
        import json
        
        data = json.loads(request.body)
        content = data.get('content', '')
        
        note, created = Note.objects.get_or_create(
            user=request.user,
            title='Dashboard Notes',
            defaults={'content': content}
        )
        
        if not created:
            note.content = content
            note.save()
        
        return JsonResponse({
            'success': True,
            'updated_at': note.updated_at.isoformat()
        })

class AlertService:
    @staticmethod
    def generate_alerts_for_user(user):
        from .models import Alert
        from datetime import timedelta
        
        now = timezone.now()
        today = now.date()
        tomorrow = today + timedelta(days=1)
        day_after = today + timedelta(days=2)
        
        user_todos = Todo.objects.filter(user=user, completed=False)
        
        # Clear old alerts that are no longer relevant
        Alert.objects.filter(
            user=user,
            todo__completed=True
        ).delete()
        
        # Generate overdue alerts
        overdue_todos = user_todos.filter(due_date__lt=now)
        for todo in overdue_todos:
            alert, created = Alert.objects.get_or_create(
                user=user,
                todo=todo,
                alert_type='overdue',
                defaults={
                    'priority': 'critical' if todo.priority == 'high' else 'high',
                    'message': f"Task '{todo.title}' is overdue! Due: {todo.due_date.strftime('%m/%d/%Y %I:%M %p')}",
                    'triggered_at': now
                }
            )
            
        # Generate due today alerts
        today_todos = user_todos.filter(due_date__date=today)
        for todo in today_todos:
            alert, created = Alert.objects.get_or_create(
                user=user,
                todo=todo,
                alert_type='due_today',
                defaults={
                    'priority': 'high' if todo.priority == 'high' else 'medium',
                    'message': f"Task '{todo.title}' is due today at {todo.due_date.strftime('%I:%M %p')}",
                    'triggered_at': now
                }
            )
            
        # Generate due soon alerts (tomorrow and day after)
        soon_todos = user_todos.filter(due_date__date__in=[tomorrow, day_after])
        for todo in soon_todos:
            days_until = (todo.due_date.date() - today).days
            alert, created = Alert.objects.get_or_create(
                user=user,
                todo=todo,
                alert_type='due_soon',
                defaults={
                    'priority': 'medium' if todo.priority == 'high' else 'low',
                    'message': f"Task '{todo.title}' is due in {days_until} day{'s' if days_until > 1 else ''} ({todo.due_date.strftime('%m/%d/%Y %I:%M %p')})",
                    'triggered_at': now
                }
            )

class AlertAPIView(LoginRequiredMixin, View):
    def get(self, request):
        from .models import Alert
        
        # Generate fresh alerts
        AlertService.generate_alerts_for_user(request.user)
        
        # Get all alerts (not dismissed)
        all_alerts = Alert.objects.filter(
            user=request.user,
            is_dismissed=False
        ).select_related('todo')
        
        # Get unread count before slicing
        unread_count = all_alerts.filter(is_read=False).count()
        
        # Get latest 10 alerts
        alerts = all_alerts[:10]
        
        alert_data = []
        for alert in alerts:
            alert_data.append({
                'id': alert.id,
                'type': alert.alert_type,
                'priority': alert.priority,
                'message': alert.message,
                'todo_id': alert.todo.id,
                'todo_title': alert.todo.title,
                'is_read': alert.is_read,
                'created_at': alert.created_at.isoformat(),
                'time_ago': self.time_ago(alert.created_at)
            })
        
        return JsonResponse({
            'alerts': alert_data,
            'unread_count': unread_count
        })
    
    def post(self, request):
        from .models import Alert
        import json
        
        data = json.loads(request.body)
        action = data.get('action')
        alert_id = data.get('alert_id')
        
        try:
            alert = Alert.objects.get(id=alert_id, user=request.user)
            
            if action == 'mark_read':
                alert.is_read = True
                alert.save()
            elif action == 'dismiss':
                alert.is_dismissed = True
                alert.save()
            elif action == 'dismiss_all':
                Alert.objects.filter(user=request.user, is_dismissed=False).update(is_dismissed=True)
                
            return JsonResponse({'success': True})
            
        except Alert.DoesNotExist:
            return JsonResponse({'error': 'Alert not found'}, status=404)
    
    def time_ago(self, dt):
        now = timezone.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "Just now" 