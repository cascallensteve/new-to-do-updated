from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
 
class CustomAccountAdapter(DefaultAccountAdapter):
    def get_signup_redirect_url(self, request):
        return reverse('todoapp:todo_list') 