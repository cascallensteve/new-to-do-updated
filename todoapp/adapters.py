from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from .models import PasswordResetCode
 
class CustomAccountAdapter(DefaultAccountAdapter):
    def get_signup_redirect_url(self, request):
        return reverse('todoapp:todo_list')
    
    def send_password_reset_code(self, user):
        """Send 6-digit password reset code to user's email"""
        reset_code = PasswordResetCode.generate_code(user)
        
        subject = 'Password Reset Code - Todo App'
        html_message = render_to_string('account/email/password_reset_code.html', {
            'user': user,
            'code': reset_code.code,
            'expires_in': 15  # minutes
        })
        
        text_message = f"""
        Hi {user.username},
        
        Your password reset code is: {reset_code.code}
        
        This code will expire in 15 minutes.
        
        If you didn't request this password reset, please ignore this email.
        
        Best regards,
        Todo App Team
        """
        
        send_mail(
            subject=subject,
            message=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return reset_code 