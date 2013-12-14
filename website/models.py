import logging

from django.db import models
from django.forms import ModelForm, Textarea
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _

from taggit.managers import TaggableManager
from taggit.models import GenericTaggedItemBase, TagBase

# handle custom Country field for South
#from south.modelsinspector import add_introspection_rules
#add_introspection_rules([], ["^website\.models\.CountryField"])

# http://xml.coverpages.org/country3166.html
COUNTRIES = (
    ('AF', _('Afghanistan')), 
    ('AX', _('Aland Islands')), 
    ('AL', _('Albania')), 
    ('DZ', _('Algeria')), 
    ('AS', _('American Samoa')), 
    ('AD', _('Andorra')), 
    ('AO', _('Angola')), 
    ('AI', _('Anguilla')), 
    ('AQ', _('Antarctica')), 
    ('AG', _('Antigua and Barbuda')), 
    ('AR', _('Argentina')), 
    ('AM', _('Armenia')), 
    ('AW', _('Aruba')), 
    ('AU', _('Australia')), 
    ('AT', _('Austria')), 
    ('AZ', _('Azerbaijan')), 
    ('BS', _('Bahamas')), 
    ('BH', _('Bahrain')), 
    ('BD', _('Bangladesh')), 
    ('BB', _('Barbados')), 
    ('BY', _('Belarus')), 
    ('BE', _('Belgium')), 
    ('BZ', _('Belize')), 
    ('BJ', _('Benin')), 
    ('BM', _('Bermuda')), 
    ('BT', _('Bhutan')), 
    ('BO', _('Bolivia')), 
    ('BA', _('Bosnia and Herzegovina')), 
    ('BW', _('Botswana')), 
    ('BV', _('Bouvet Island')), 
    ('BR', _('Brazil')), 
    ('IO', _('British Indian Ocean Territory')), 
    ('BN', _('Brunei Darussalam')), 
    ('BG', _('Bulgaria')), 
    ('BF', _('Burkina Faso')), 
    ('BI', _('Burundi')), 
    ('KH', _('Cambodia')), 
    ('CM', _('Cameroon')), 
    ('CA', _('Canada')), 
    ('CV', _('Cape Verde')), 
    ('KY', _('Cayman Islands')), 
    ('CF', _('Central African Republic')), 
    ('TD', _('Chad')), 
    ('CL', _('Chile')), 
    ('CN', _('China')), 
    ('CX', _('Christmas Island')), 
    ('CC', _('Cocos (Keeling) Islands')), 
    ('CO', _('Colombia')), 
    ('KM', _('Comoros')), 
    ('CG', _('Congo')), 
    ('CD', _('Congo, The Democratic Republic of the')), 
    ('CK', _('Cook Islands')), 
    ('CR', _('Costa Rica')), 
    ('CI', _('Cote d\'Ivoire')), 
    ('HR', _('Croatia')), 
    ('CU', _('Cuba')), 
    ('CY', _('Cyprus')), 
    ('CZ', _('Czech Republic')), 
    ('DK', _('Denmark')), 
    ('DJ', _('Djibouti')), 
    ('DM', _('Dominica')), 
    ('DO', _('Dominican Republic')), 
    ('EC', _('Ecuador')), 
    ('EG', _('Egypt')), 
    ('SV', _('El Salvador')), 
    ('GQ', _('Equatorial Guinea')), 
    ('ER', _('Eritrea')), 
    ('EE', _('Estonia')), 
    ('ET', _('Ethiopia')), 
    ('FK', _('Falkland Islands (Malvinas)')), 
    ('FO', _('Faroe Islands')), 
    ('FJ', _('Fiji')), 
    ('FI', _('Finland')), 
    ('FR', _('France')), 
    ('GF', _('French Guiana')), 
    ('PF', _('French Polynesia')), 
    ('TF', _('French Southern Territories')), 
    ('GA', _('Gabon')), 
    ('GM', _('Gambia')), 
    ('GE', _('Georgia')), 
    ('DE', _('Germany')), 
    ('GH', _('Ghana')), 
    ('GI', _('Gibraltar')), 
    ('GR', _('Greece')), 
    ('GL', _('Greenland')), 
    ('GD', _('Grenada')), 
    ('GP', _('Guadeloupe')), 
    ('GU', _('Guam')), 
    ('GT', _('Guatemala')), 
    ('GG', _('Guernsey')), 
    ('GN', _('Guinea')), 
    ('GW', _('Guinea-Bissau')), 
    ('GY', _('Guyana')), 
    ('HT', _('Haiti')), 
    ('HM', _('Heard Island and McDonald Islands')), 
    ('VA', _('Holy See (Vatican City State)')), 
    ('HN', _('Honduras')), 
    ('HK', _('Hong Kong')), 
    ('HU', _('Hungary')), 
    ('IS', _('Iceland')), 
    ('IN', _('India')), 
    ('ID', _('Indonesia')), 
    ('IR', _('Iran, Islamic Republic of')), 
    ('IQ', _('Iraq')), 
    ('IE', _('Ireland')), 
    ('IM', _('Isle of Man')), 
    ('IL', _('Israel')), 
    ('IT', _('Italy')), 
    ('JM', _('Jamaica')), 
    ('JP', _('Japan')), 
    ('JE', _('Jersey')), 
    ('JO', _('Jordan')), 
    ('KZ', _('Kazakhstan')), 
    ('KE', _('Kenya')), 
    ('KI', _('Kiribati')), 
    ('KP', _('Korea, Democratic People\'s Republic of')), 
    ('KR', _('Korea, Republic of')), 
    ('KW', _('Kuwait')), 
    ('KG', _('Kyrgyzstan')), 
    ('LA', _('Lao People\'s Democratic Republic')), 
    ('LV', _('Latvia')), 
    ('LB', _('Lebanon')), 
    ('LS', _('Lesotho')), 
    ('LR', _('Liberia')), 
    ('LY', _('Libyan Arab Jamahiriya')), 
    ('LI', _('Liechtenstein')), 
    ('LT', _('Lithuania')), 
    ('LU', _('Luxembourg')), 
    ('MO', _('Macao')), 
    ('MK', _('Macedonia, The Former Yugoslav Republic of')), 
    ('MG', _('Madagascar')), 
    ('MW', _('Malawi')), 
    ('MY', _('Malaysia')), 
    ('MV', _('Maldives')), 
    ('ML', _('Mali')), 
    ('MT', _('Malta')), 
    ('MH', _('Marshall Islands')), 
    ('MQ', _('Martinique')), 
    ('MR', _('Mauritania')), 
    ('MU', _('Mauritius')), 
    ('YT', _('Mayotte')), 
    ('MX', _('Mexico')), 
    ('FM', _('Micronesia, Federated States of')), 
    ('MD', _('Moldova')), 
    ('MC', _('Monaco')), 
    ('MN', _('Mongolia')), 
    ('ME', _('Montenegro')), 
    ('MS', _('Montserrat')), 
    ('MA', _('Morocco')), 
    ('MZ', _('Mozambique')), 
    ('MM', _('Myanmar')), 
    ('NA', _('Namibia')), 
    ('NR', _('Nauru')), 
    ('NP', _('Nepal')), 
    ('NL', _('Netherlands')), 
    ('AN', _('Netherlands Antilles')), 
    ('NC', _('New Caledonia')), 
    ('NZ', _('New Zealand')), 
    ('NI', _('Nicaragua')), 
    ('NE', _('Niger')), 
    ('NG', _('Nigeria')), 
    ('NU', _('Niue')), 
    ('NF', _('Norfolk Island')), 
    ('MP', _('Northern Mariana Islands')), 
    ('NO', _('Norway')), 
    ('OM', _('Oman')), 
    ('PK', _('Pakistan')), 
    ('PW', _('Palau')), 
    ('PS', _('Palestinian Territory, Occupied')), 
    ('PA', _('Panama')), 
    ('PG', _('Papua New Guinea')), 
    ('PY', _('Paraguay')), 
    ('PE', _('Peru')), 
    ('PH', _('Philippines')), 
    ('PN', _('Pitcairn')), 
    ('PL', _('Poland')), 
    ('PT', _('Portugal')), 
    ('PR', _('Puerto Rico')), 
    ('QA', _('Qatar')), 
    ('RE', _('Reunion')), 
    ('RO', _('Romania')), 
    ('RU', _('Russian Federation')), 
    ('RW', _('Rwanda')), 
    ('BL', _('Saint Barthelemy')), 
    ('SH', _('Saint Helena')), 
    ('KN', _('Saint Kitts and Nevis')), 
    ('LC', _('Saint Lucia')), 
    ('MF', _('Saint Martin')), 
    ('PM', _('Saint Pierre and Miquelon')), 
    ('VC', _('Saint Vincent and the Grenadines')), 
    ('WS', _('Samoa')), 
    ('SM', _('San Marino')), 
    ('ST', _('Sao Tome and Principe')), 
    ('SA', _('Saudi Arabia')), 
    ('SN', _('Senegal')), 
    ('RS', _('Serbia')), 
    ('SC', _('Seychelles')), 
    ('SL', _('Sierra Leone')), 
    ('SG', _('Singapore')), 
    ('SK', _('Slovakia')), 
    ('SI', _('Slovenia')), 
    ('SB', _('Solomon Islands')), 
    ('SO', _('Somalia')), 
    ('ZA', _('South Africa')), 
    ('GS', _('South Georgia and the South Sandwich Islands')), 
    ('ES', _('Spain')), 
    ('LK', _('Sri Lanka')), 
    ('SD', _('Sudan')), 
    ('SR', _('Suriname')), 
    ('SJ', _('Svalbard and Jan Mayen')), 
    ('SZ', _('Swaziland')), 
    ('SE', _('Sweden')), 
    ('CH', _('Switzerland')), 
    ('SY', _('Syrian Arab Republic')), 
    ('TW', _('Taiwan, Province of China')), 
    ('TJ', _('Tajikistan')), 
    ('TZ', _('Tanzania, United Republic of')), 
    ('TH', _('Thailand')), 
    ('TL', _('Timor-Leste')), 
    ('TG', _('Togo')), 
    ('TK', _('Tokelau')), 
    ('TO', _('Tonga')), 
    ('TT', _('Trinidad and Tobago')), 
    ('TN', _('Tunisia')), 
    ('TR', _('Turkey')), 
    ('TM', _('Turkmenistan')), 
    ('TC', _('Turks and Caicos Islands')), 
    ('TV', _('Tuvalu')), 
    ('UG', _('Uganda')), 
    ('UA', _('Ukraine')), 
    ('AE', _('United Arab Emirates')), 
    ('GB', _('United Kingdom')), 
    ('US', _('United States')), 
    ('UM', _('United States Minor Outlying Islands')), 
    ('UY', _('Uruguay')), 
    ('UZ', _('Uzbekistan')), 
    ('VU', _('Vanuatu')), 
    ('VE', _('Venezuela')), 
    ('VN', _('Viet Nam')), 
    ('VG', _('Virgin Islands, British')), 
    ('VI', _('Virgin Islands, U.S.')), 
    ('WF', _('Wallis and Futuna')), 
    ('EH', _('Western Sahara')), 
    ('YE', _('Yemen')), 
    ('ZM', _('Zambia')), 
    ('ZW', _('Zimbabwe')), 
)

class CountryField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 2)
        kwargs.setdefault('choices', COUNTRIES)

        super(CountryField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"
    
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
    'Economic Development',
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
    'Open Data',
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
    country = CountryField(blank=True)
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
    cause = TaggableManager(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = CountryField(blank=True)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='Pending')
    industry = models.CharField(max_length=100, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    short_desc = models.TextField(blank=True)
    description = models.TextField(blank=True)
    description2 = models.TextField(blank=True)
    description3 = models.TextField(blank=True)
    description4 = models.TextField(blank=True)
    media_url = models.CharField(max_length=200, blank=True)
    video_url = models.CharField(max_length=200, blank=True, null=True)
    created_by = models.ForeignKey(User)
    followed_by = models.ManyToManyField(User, blank=True, related_name='followed_by')
    
    def __unicode__(self):
        return "Name: %s" % self.name
    
    def make_s3_media_url(self, uploaded_file):
        return 'projects/%s/%s' % (self.id, uploaded_file.name)


class ProjectForm(ModelForm):

    class Meta:

        model = Project
        fields = ('name', 'industry', 'short_desc', 'description', 'video_url', 'media_url')

        widgets = {
            'description': Textarea(attrs={'cols': 80, 'rows': 10}),
        }


OPP_TYPE_CHOICES = ((u'Equipment', u'Equipment'), (u'Knowledge', u'Knowledge'), (u'Money', u'Money'), (u'Skills', u'Skills'),)


class Opportunity(models.Model):

    tags = TaggableManager(blank=True)
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
    organization = models.ForeignKey(Organization, null=True, blank=True, on_delete=models.SET_NULL)
    location = models.CharField(max_length=200, blank=True)
    occupation = models.CharField(max_length=200, blank=True)
    causes = models.CharField(max_length=2000, blank=True)
    skills = TaggableManager(blank=True)

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


