from django.db import models
from django.forms import ModelForm, Textarea
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class Organization(models.Model):
    name = models.CharField(max_length=100, blank=True)
    business_type = models.CharField(max_length=100, blank=True, default='nonprofit')
    year_established = models.CharField(max_length=4, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    org_mission = models.TextField(blank=True)
    address_one = models.CharField(max_length=100, blank=True)
    address_two = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, blank=True)
    country = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=10, blank=True)
    phone = models.TextField(blank=True)
    URL = models.TextField(blank=True)
    media_url = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(User)
    
    def __unicode__(self):
        return "Name: %s" % self.name
    
class OrganizationForm(ModelForm):
    class Meta:
        model = Organization
        fields = ('name', 'business_type', 'year_established', 'org_mission', 'address_one', 'address_two', 'city', 'state', 'country', 'zip_code', 'phone', 'URL',)
    
        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 10}),
        }

class Project(models.Model):
    organization = models.ForeignKey(Organization)
    name = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=100, blank=True, default='unpublished')
    industry = models.CharField(max_length=100, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    short_desc = models.TextField(blank=True)
    description = models.TextField(blank=True)
    media_url = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(User)
    followed_by = models.ManyToManyField(User, blank=True, related_name='followed_by')
    
    def __unicode__(self):
        return "Name: %s" % self.name


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'industry', 'short_desc', 'description', )

        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 10}),
        }


class Opportunity(models.Model):
    organization = models.ForeignKey(Organization)
    OPP_TYPE_CHOICES = ((u'Equipment', u'Equipment'),(u'Knowledge', u'Knowledge'),(u'Money', u'Money'),(u'Skills', u'Skills'),)
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=100, blank=True)
    media_url = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=100, blank=True, default='unpublished')
    date_created = models.DateTimeField(auto_now_add=True)
    short_desc = models.TextField(blank=True)
    description = models.TextField(blank=True)
    featured = models.BooleanField(default=False, blank=True)
    opp_type = models.CharField(max_length=100, choices=OPP_TYPE_CHOICES, blank=True) # TODO: replace with taggit? Four main options: Service, Donation, Rental, Question
    engaged_by = models.ManyToManyField(User, blank=True, through='OpportunityEngagement')
    # prerequisites = models.ManyToManyField(Opportunity)  - assuming that pre-reqs = other opps
    # time estimate - TODO: See v2 Feature Doc https://docs.google.com/a/reallocate.org/document/d/1AY-2h9pa028USr3ofwUQjjoZ2kKGnRQZ0xoIQYk-urs/edit
    # deliverable - TODO: separate free-form text field
    # followup gift to volunteer - TODO: separate free-form text field

    def __unicode__(self):
        return "Name: %s" % self.name

    class Meta:
        verbose_name_plural = "opportunities"

class OpportunityForm(ModelForm):
    class Meta:
        model = Opportunity
        fields = ('name', 'description', 'short_desc', 'opp_type')

        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 10}),
        }
    
###########  Extend user profile
# Docs: http://stackoverflow.com/a/965883/705945

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    bio = models.CharField(max_length=2000, blank=True)
    media_url = models.CharField(max_length=2000, blank=True)
    
    # skills
    # interests

    def __str__(self):
        return "%s's profile" % self.user

class Update(models.Model):
    organization = models.ForeignKey(Organization)
    project = models.ForeignKey(Project)
    opportunity = models.ForeignKey(Opportunity)
    created_by = models.ForeignKey(User)
    text = models.TextField(blank=True)
    media_url = models.CharField(max_length=1000, blank=True)

    def __unicode__(self):
        return "Update: %s" % "Coming soon!"

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)

class OpportunityEngagement(models.Model):
    user = models.ForeignKey(User)
    opportunity = models.ForeignKey(Opportunity)
    date_created = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=100) # this will be where the opp engagements can be approved
    response = models.CharField(max_length=2000) # response to the engagement
