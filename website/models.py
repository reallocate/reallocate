from django.db import models
from django.forms import ModelForm, Textarea
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Project(models.Model):
    name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=100, blank=True, default='unpublished')
    industry = models.CharField(max_length=100, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=1000, blank=True)
    media_url = models.CharField(max_length=200, blank=True)
    followed_by = models.ManyToManyField(User, blank=True)
    def __unicode__(self):
        return "Name: %s" % self.name


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'industry', 'description', )

        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 10}),
        }


class Opportunity(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=100, blank=True)
    media_url = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=100, blank=True, default='unpublished')
    date_created = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=1000, blank=True)
    featured = models.BooleanField(default=False, blank=True)
    # engaged_users = models.ManyToManyField(Users)
    # prerequisites = models.ManyToManyField(Opportunity)  - assuming that pre-reqs = other opps
    # time estimate - TODO: do we do this in days?
    # deliverable - TODO: separate free-form text field
    # followup gift to volunteer - TODO: separate free-form text field

    def __unicode__(self):
        return "Name: %s" % self.name


class OpportunityForm(ModelForm):
    class Meta:
        model = Opportunity
        fields = ('name', 'description',)

        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 10}),
        }


###########  Extend user profile
# Docs: http://stackoverflow.com/a/965883/705945

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    bio = models.CharField(max_length=2000, blank=True)
    media_url = models.CharField(max_length=2000, blank=True)
    # engaged_opportunities = models.ManyToManyField(Opportunity, blank=True)
    # skills
    # interests

    def __str__(self):
        return "%s's profile" % self.user

class Update(models.Model):
    project = models.ForeignKey(Project)
    opportunity = models.ForeignKey(Opportunity)
    user_profile = models.ForeignKey(UserProfile)
    text = models.CharField(max_length=1000, blank=True)
    media_url = models.CharField(max_length=1000, blank=True)

    def __unicode__(self):
        return "Update: %s" % "Coming soon!"

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)