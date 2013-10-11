from django.db import models
from django.forms import ModelForm, Textarea
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from taggit.managers import TaggableManager

STATUS_CHOICES = (('Pending', 'Pending'), ('Active', 'Active'), ('Closed', 'Closed'))
STATUS_INACTIVE = STATUS_CHOICES[0][0]
STATUS_ACTIVE = STATUS_CHOICES[1][0]
STATUS_CLOSED = STATUS_CHOICES[2][0]

CAUSES = [
    'Advocacy & Human Rights',
    'Animals',
    'Arts & Culture',
    'Children & Youth',
    'Civic Engagement',
    'Community',
    'Computers & Technology',
    'Crisis Support',
    'Disabled',
    'Disaster Relief',
    'Education & Literacy',
    'Emergency & Safety',
    'Employment',
    'Environment',
    'Spiritual',
    'Health & Medicine',
    'Homeless & Housing',
    'Hunger',
    'Immigrants & Refugees',
    'International',
    'Justice & Legal',
    'LGBT',
    'Media & Broadcasting',
    'Politics',
    'Race & Ethnicity',
    'Science & Technology',
    'Seniors',
    'Sports & Recreation',
    'Veterans & Military Families',
    'Women'
]

SKILLS = {
    'Administrative': [
        'Office Reception',
        'Office Management',
        'Executive Admin'
    ],
    'Disaster Relief': [
        'Disaster Cleanup',
        'Disaster Relief & Shelters',
        'Disaster Relief Call Center'
    ],
    'Food Service & Events': [
        'Cooking / Catering',
        'Event Design & Planning',
        'Food & Beverage Services',
        'Event Management'
    ],
    'Information Technology': [
        'Information Architecture',
        'Web Design',
        'User Experience',
        'E-commererce',
        'Software Engineering',
        'Network Administration',
        'Help Desk',
        'Quality Assurance',
        'Technical Writing'
    ],
    'Real Estate, Faciliites, Construction': [
        'Building Architecture',
        'Facilities Management',
        'Interior Design',
        'Renovation',
        'Real Estate & Leasing',
        'Landscaping',
        'Construction'
    ],
    'Legal': [
        'Legal (General)',
        'Intellectual Property',
        'Employment Law',
        'Tax Law',
        'Family Law',
        'Mergers & Aquisitions',
        'Litigation',
        'Paralegal',
        'Contract Negotiations',
        ''
    ],
    'Engineering': [
        'Systems Engineering',
        'Mechanical Engineering',
        'Civil Engineering',
        'Chemical Engineering',
        'Electrical Engineering'
    ],
    'Enviornment': [
        'Habitat Restoration',
        'Enviornmental Policy',
        'Enviornmental Education',
        'Pollution Prevention',
        'Agriculture'
    ],
    'Education': [
        'General Education',
        'Tutoring',
        'Literacy / Reading',
        'Youth Activities'
    ],
    'Healthcare': [
        'Mental Health',
        'Dental',
        'First Aid / CPR',
        'Nursing',
        'Physician',
        'EMT',
        'Message Therapy',
        'Child Medical Service'
    ],
    'Logistics': [
        'Driving',
        'Supply Chain',
        'Warehousing',
        'Inventory Management'
    ],
    'Children & Family': [
        'Youth Services',
        'Family Therapy',
        'Child Care',
        'Elder Care',
        'Crisis Intervention'
    ],
    'Business': [
        'Business Development',
        'Customer Acquisition',
        'Strategic Planning',
        'Market Research',
        'Product Development',
        'Business Analysis',
        'Marketing & Communication',
        'Public Relations',
        'Sales',
        'Brand Development & Messaging'
    ],
    'Finance': [
        'Financial Planning',
        'Budgeting',
        'Cost Analysis',
        'Tax Preperation',
        'Accounting',
        'Bookkeeping',
        'Fundraising'
    ],
    'Arts': [
        'Visual Arts',
        'Music Arts',
        'Dance',
        'Theater Arts',
        'Crafts',
        'Photography',
        'Exibition Arts'
    ]
}


class Organization(models.Model):

    name = models.CharField(max_length=100, blank=True)
    business_type = models.CharField(max_length=100, blank=True, default='nonprofit')
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')
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
    cause = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100,blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')
    industry = models.CharField(max_length=100, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    short_desc = models.TextField(blank=True)
    description = models.TextField(blank=True)
    description2 = models.TextField(blank=True)
    description3 = models.TextField(blank=True)
    description4 = models.TextField(blank=True)
    media_url = models.CharField(max_length=200, blank=True)
    video_url = models.CharField(max_length=200, blank=True)
    created_by = models.ForeignKey(User)
    followed_by = models.ManyToManyField(User, blank=True, related_name='followed_by')
    
    def __unicode__(self):
        return "Name: %s" % self.name
    
    def make_s3_media_url(self, uploaded_file):
        return 'projects/%s/%s' % (self.id, uploaded_file.name)


class ProjectForm(ModelForm):

    class Meta:

        model = Project
        fields = ('name', 'industry', 'short_desc', 'description', 'description2', 'description3', 'description4',  'video_url', 'media_url')

        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 10}),
        }


OPP_TYPE_CHOICES = ((u'Equipment', u'Equipment'), (u'Knowledge', u'Knowledge'), (u'Money', u'Money'), (u'Skills', u'Skills'),)


class Opportunity(models.Model):

    tags = TaggableManager()
    organization = models.ForeignKey(Organization, blank=True)
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=100, blank=True)
    media_url = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Active')
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name="created_by_related")
    short_desc = models.TextField(blank=True)
    description = models.TextField(blank=True)
    resources = models.TextField(blank=True)
    featured = models.BooleanField(default=False, blank=True)

    opp_type = models.CharField(max_length=100, choices=OPP_TYPE_CHOICES, blank=True) 
    #opp_category = models.CharField(max_length=100, blank=True)

    engaged_by = models.ManyToManyField(User, blank=True, through='OpportunityEngagement')

    # prerequisites = models.ManyToManyField(Opportunity)  - assuming that pre-reqs = other opps
    # time estimate - TODO: See v2 Feature Doc https://docs.google.com/a/reallocate.org/document/d/1AY-2h9pa028USr3ofwUQjjoZ2kKGnRQZ0xoIQYk-urs/edit
    # deliverable - TODO: separate free-form text field
    # followup gift to volunteer - TODO: separate free-form text field

    def __unicode__(self):
        return "Name: %s" % self.name

    class Meta:
        verbose_name_plural = "opportunities"
        
    def make_s3_media_url(self, uploaded_file):
        return 'opportunities/%s/%s' % (self.id, uploaded_file.name)


class OpportunityForm(ModelForm):

    class Meta:
        model = Opportunity
        fields = ('name', 'description', 'short_desc', 'opp_type', 'resources', 'media_url')

        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 10}),
        }
    
###########  Extend user profile
# Docs: http://stackoverflow.com/a/965883/705945

class UserProfile(models.Model):

    user = models.OneToOneField(User)
    bio = models.CharField(max_length=2000, blank=True)
    media_url = models.CharField(max_length=2000, blank=True)
    organization = models.ForeignKey(Organization, null=True, blank=True)
    location = models.CharField(max_length=200, blank=True)
    occupation = models.CharField(max_length=200, blank=True)
    causes = models.CharField(max_length=100, blank=True)
    skills = TaggableManager()
    
    # skills
    # interests

    def __str__(self):
        return "%s's profile" % self.user
    
    def make_s3_media_url(self, uploaded_file):
        return 'users/%s/%s' % (self.user.email, uploaded_file.name)
        

def create_user_profile(sender, instance, created, **kwargs):

    if created:
        profile, created = UserProfile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)

 
class Update(models.Model):

    organization = models.ForeignKey(Organization)
    project = models.ForeignKey(Project)
    opportunity = models.ForeignKey(Opportunity, blank=True, null=True)
    text = models.TextField(blank=True, null=True)
    media_url = models.CharField(max_length=1000, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User)
    
    def __unicode__(self):
        return "Update: %s" % "Coming soon!"


class OpportunityEngagement(models.Model):

    # to keep the project + reallocate in the loop, reallocate will approve the engagements
    # and stay in each conversation
    user = models.ForeignKey(User)
    opportunity = models.ForeignKey(Opportunity)
    project = models.ForeignKey(Project)
    date_created = models.DateField(auto_now_add=True)
     # this will be where the opp engagements can be approved
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=STATUS_CHOICES[1][1])
    response = models.CharField(max_length=2000, blank=True) # response to the engagement
    