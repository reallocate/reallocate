from django.contrib.sites.models import Site
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

from website.models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs): 
    if created:
        UserProfile(user = instance, site = Site.objects.get_current()).save()
