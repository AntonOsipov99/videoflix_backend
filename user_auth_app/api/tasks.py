from django.core.mail import send_mail
from django.conf import settings

def send_password_reset_email(user_email, reset_url):
    """Send an email with password reset link"""
    subject = "Password Reset Request"
    message = f"""
    Hello,
    
    You requested a password reset. Please click the link below to reset your password:
    
    {reset_url}
    
    This link will expire in 24 hours.
    
    If you did not request this, please ignore this email.
    
    Thank you,
    Your Videoflix Team
    """
    
    return send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
    
def send_activation_email_task(email, activation_url):
    subject = 'Videoflix - Activate your account'
    message = (
        f'Hello and welcome to Videoflix!\n\n'
        f'Thank you for registering with our service. To complete your registration and start enjoying our content, '
        f'please activate your account by clicking on the link below:\n\n'
        f'{activation_url}\n\n'
        f'This link will expire in 24 hours. If you did not create this account, please ignore this email.\n\n'
        f'Best regards,\nThe Videoflix Team'
    )
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )