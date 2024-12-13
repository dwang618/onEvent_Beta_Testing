# signals.py
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import CommonUser

@receiver(user_logged_in)
def create_common_user(sender, request, user, **kwargs):
    # Check if the CommonUser instance already exists for the logged-in user
    if not hasattr(user, 'commonuser'):
        CommonUser.objects.create(user=user)
