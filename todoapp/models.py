from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from taggit.managers import TaggableManager
from colorfield.fields import ColorField
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

class Category(models.Model):
    name = models.CharField(max_length=100)
    color = ColorField(default='#FF0000')
    icon = models.CharField(max_length=50, default='fas fa-tasks')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

class Todo(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=200)
    description = RichTextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Advanced features
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    tags = TaggableManager(blank=True)
    
    # Time management
    estimated_time = models.DurationField(null=True, blank=True)
    actual_time = models.DurationField(null=True, blank=True)
    start_time = models.DateTimeField(null=True, blank=True)
    reminder_time = models.DateTimeField(null=True, blank=True)
    
    # Recurring tasks
    is_recurring = models.BooleanField(default=False)
    recurring_frequency = models.CharField(max_length=20, null=True, blank=True)
    recurring_end_date = models.DateTimeField(null=True, blank=True)
    
    # Collaboration
    assigned_to = models.ManyToManyField(User, related_name='assigned_tasks', blank=True)
    is_shared = models.BooleanField(default=False)
    
    # UI/UX
    color = ColorField(default='#FF0000')
    is_favorite = models.BooleanField(default=False)
    order_index = models.IntegerField(default=0)
    
    # Progress tracking
    progress = models.IntegerField(default=0, validators=[
        MinValueValidator(0),
        MaxValueValidator(100)
    ])
    notes = models.TextField(blank=True)
    attachments = models.FileField(upload_to='todo_attachments/', null=True, blank=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('todoapp:todo_list')

    def mark_completed(self):
        self.completed = True
        self.completed_at = timezone.now()
        self.status = 'completed'
        self.save()

    def toggle_favorite(self):
        self.is_favorite = not self.is_favorite
        self.save()

    def update_progress(self, value):
        self.progress = max(0, min(100, value))
        if self.progress == 100:
            self.mark_completed()
        self.save()

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]

class Comment(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

class TaskActivity(models.Model):
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE, related_name='activities')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Task Activities'

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, default='Dashboard Notes')
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    class Meta:
        ordering = ['-updated_at']

class Alert(models.Model):
    ALERT_TYPES = [
        ('due_today', 'Due Today'),
        ('due_soon', 'Due Soon'),
        ('overdue', 'Overdue'),
        ('reminder', 'Reminder'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    todo = models.ForeignKey(Todo, on_delete=models.CASCADE)
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    priority = models.CharField(max_length=10, choices=PRIORITY_LEVELS, default='medium')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    triggered_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.alert_type} - {self.todo.title} - {self.user.username}"
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'todo', 'alert_type'] 