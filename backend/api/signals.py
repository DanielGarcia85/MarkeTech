from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import Group, Permission


@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    Group.objects.get_or_create(name='administrator')
    Group.objects.get_or_create(name='employer')
    Group.objects.get_or_create(name='jobseeker')
    
