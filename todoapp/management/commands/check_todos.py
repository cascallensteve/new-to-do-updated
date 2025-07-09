from django.core.management.base import BaseCommand
from todoapp.models import Todo
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Check todos in the database'

    def handle(self, *args, **options):
        users = User.objects.all()
        self.stdout.write(f"Total users: {users.count()}")
        
        for user in users:
            todos = Todo.objects.filter(user=user)
            self.stdout.write(f"\nUser: {user.username}")
            self.stdout.write(f"Total todos: {todos.count()}")
            for todo in todos:
                self.stdout.write(f"- {todo.title} (Created: {todo.created_at})") 