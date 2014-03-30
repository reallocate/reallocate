import logging, hashlib, random
import boto
import re, sys, os
import json
import stripe

from boto.s3.key import Key

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q
from django.utils.http import urlquote

import settings
import base

from models import OrganizationForm, Organization, ProjectForm, Project, Update, UserProfile
from models import OpportunityEngagement, Opportunity, OpportunityForm
from models import STATUS_ACTIVE, STATUS_CHOICES, STATUS_INACTIVE, STATUS_CLOSED, CAUSES, COUNTRIES


@login_required
def profile(request, username=None):
    """ for displaying and editing a users profile """
    
    context = {}
    if not username and not request.user:
        return HttpResponseRedirect('/')
    
    # this is a person viewing their own profile page, make it editable
    if not username: 
        user = request.user
        context['self'] = True
    elif re.match(r'^\d+', username):
        user = User.objects.filter(id=username)
    else:
        user = User.objects.filter(Q(email=username) | Q(username=username))
    
    user_profile = UserProfile.objects.filter(Q(user=user))
    if len(user_profile) == 0:
        return HttpResponseRedirect('/')

    user_profile = user_profile[0] # replace above logic with None or single object?

    if request.method == "POST":
        
        avatar = request.FILES.get('file')
        if avatar:
            user_profile.media_url = base.send_to_remote_storage(avatar, user_profile.make_s3_media_url(avatar), "image/png")
            user_profile.save()
        else:
            user_profile.user.first_name = request.POST.get("first_name")
            user_profile.user.last_name = request.POST.get("last_name")
            user_profile.user.email = request.POST.get("email")
            user_profile.bio = request.POST.get("bio")
            user_profile.occupation = request.POST.get("occupation")
            user_profile.location = request.POST.get("location")
            user_profile.skills = request.POST.get("skills")
            user_profile.user.save()
            user_profile.save()

            context['alert'] = {'type': 'success', 'message': 'Your changes have been saved.'}
    
    context['opportunities'] = Opportunity.objects.filter(engaged_by=user)
    context['my_projects'] = Project.objects.filter(Q(created_by=user)|Q(followed_by=user))

    context['user_profile'] = user_profile
    
    return render(request, 'profile.html', context)


def public_profile(request, username=None):

    user = User.objects.filter(Q(email=username) | Q(username=username))
    user_profile = UserProfile.objects.filter(Q(user=user))
    context = {}

    if len(user_profile) < 1:

        context['username'] = 'name ' + username

        return render_to_response('no_such_user.html', context)

    context['user_profile'] = user_profile[0]
    context['opportunities'] = Opportunity.objects.filter(engaged_by=user)
    context['projects'] = Project.objects.filter(followed_by=user)

    return render(request, 'public_profile.html', context)
    

def login_page(request):

    context = {}

    foo = "testing"
    
    return render(request, 'login.html', context)


def home(request):

    context = {}

    projects = Project.objects.filter(Q(status__iexact='active'))

    # cobranding
    if hasattr(settings, 'BRAND'):
        projects = projects.filter(tags__contains=settings.BRAND.get('id', ''))
    else:
        projects = projects.filter(tags__contains='hacktivation')

    context['projects'] = projects[:12]

    response = render(request, 'home.html', context)

    return response


def about(request):

    context = {}

    return render(request, 'about.html', context)


def privacy(request):

    context = {}

    return render(request, 'privacy.html', context)


def tou(request):

    context = {}

    return render(request, 'tou.html', context)


def get_started(request):
    
    context = {}

    if hasattr(request.user, 'email'):

        context['next'] = '/organization/new'

    else:

        context['next'] = '/sign-up'

    return render(request, 'get_started.html', context)


def test_email(request):

    email_type = request.GET.get('email_type')
    html_content = base.send_email_template(request, email_type, {}, "*", [], render=True)[0]

    return HttpResponse(content=html_content)


def reset_password(request):

    context = {}
    
    if request.POST:
        
        email = request.POST.get('email')
        temp_password = request.POST.get('temp_password')
        new_password = request.POST.get('password')
        user = User.objects.get(username=email)

        if not user:

            return HttpResponseRedirect('/')
 
        if not user.check_password(temp_password):

            context['alert'] = {'type': 'danger', 'message': "This reset request is no longer valid."}

            return render_to_response('reset_password.html', context, context_instance=RequestContext(request))

        user.set_password(new_password)
        user.save()

        user = authenticate(username=email, password=new_password)
        login(request, user)
    
        return HttpResponseRedirect("/")

    else:
    
        context['temp_password'] = request.GET.get("t")
        context['email'] = request.GET.get("e")

        return render(request, 'reset_password.html', context)
    

def forgot_password(request):

    context = {}
    
    if request.POST:

        email = request.POST.get('email')
        try:
            reset_user = User.objects.get(username=email)
        except User.DoesNotExist:
            reset_user = None

        if not reset_user:

            context['invalid_email'] = True

        else:

            temp_password = hashlib.md5(str(random.randint(0, 10000000))).hexdigest()[0:7]
            reset_user.set_password(temp_password)
            reset_user.save()

            subj = "[%s] Your password has been reset" % request.get_host()
            body = """By request, we've reset your password. <a href='http://%s/reset-password?t=%s&e=%s'>
                Choose a new password</a><br/><br/>Always happy to help,<br/>Reallocate""" % (request.get_host(), temp_password, urlquote(email))
                    
            base.send_email(email, subj, body, html_content=body)

            response = HttpResponseRedirect('/')
            alert = {'type': 'success', 'message': 'Your password has been reset'}
            response.set_cookie('alert', json.dumps(alert), max_age=2)

            return response
        
    context['email'] = request.GET.get('email', '')

    return render(request, 'forgot_password.html', context)


def sign_up(request):

    context = {}

    context['referrer'] = request.META.get('HTTP_REFERER', '/')

    if re.search(r'\/get-started', context['referrer']): 
        context['next'] = '/organization/new'
    else:
        context['next'] = context['referrer']

    if settings.INVITE_ONLY:

        if request.GET.get('invite') or request.COOKIES.get('invite'):

            response = render(request, 'sign_up.html', context)

            if request.GET.get('invite'):
                response.set_cookie('invite', request.GET['invite'], max_age=2)

            return response

        else:

            return render(request, 'request_invite.html', context)

    elif not request.POST:

        return render(request, 'sign_up.html', context)

    response = HttpResponseRedirect(request.POST.get('next', '/'))

    if request.POST.get('request-invite'):

        email = request.POST.get('email')
        name = request.POST.get('name')
        subject = "%s" % email
        content = "A new account invite request has been submitted:\n\n\t- %s\n\t- %s" % (name, email)
        if request.POST.get('blurb'):
            content += "\n\n%s" %  request.POST.get('blurb')
        if request.POST.get('contribute'):
            content += "\n\nI would like to contribute my skills, knowledge and/or resources."
        if request.POST.get('project'):
            content += "\n\nI have a project I would like to submit."

        base.send_email('invite@reallocate.org', subject, content)

        alert = {'type': 'modal', 'message': 'Thank you for your interest in Reallocate.  Your invite request has been received.'} 

        response.set_cookie('alert', json.dumps(alert), max_age=2)

    else:

        email = request.POST.get('email')
        password = request.POST.get('password')

        # Create a new user and persist it to the database.
        user = User.objects.create_user(username=email, email=email, password=password)
        user.save()

        user = authenticate(username=email, password=password)
        login(request, user)
        
        email_context = {'email': email, 'user': user}

        base.send_email_template(request, 'welcome', email_context, 'Welcome to ReAllocate!', [email])
        
        subject = "[%s] %s %s has joined ReAllocate" % (request.get_host(), user.first_name, user.last_name)
        html_content = "Username: %s <br /><br />Name: %s %s<br /><br />Email: %s <br /><br />" % (user.username, user.first_name, user.last_name, user.email)
        base.send_admin_email(subject, html_content, html_content=html_content)

    return response


def login_user(request):

    context = {}

    if request.POST:

        username = request.POST.get('username')
        password = request.POST.get('password')

        context['username'] = username

        user = authenticate(username=username, password=password)

        if user is not None:

            if user.is_active:

                login(request, user)

                next = request.POST.get('next') or settings.POST_LOGIN_URL
                logging.error(next)

                return HttpResponseRedirect(next)

            else:
                context['state'] = "Your account is not active, please contact the site admin."
        else:
            context['state'] = "Your username and/or password were incorrect."

    return render(request, 'login.html', context)


def view_project(request, pid=1):

    project = get_object_or_404(Project, pk=pid)
    opps = Opportunity.objects.filter(project=project).order_by('-sponsorship')
    engagement = OpportunityEngagement.objects.filter(project=project).filter(user__id__gt=1).distinct()
    context = {}

    context.update({
        "project": project,
        "opportunities": opps,
        "engagement": engagement,
        "updates": Update.objects.filter(project=project).order_by('-date_created')})
    
    if project.video_url:
        (project.video, foo) = base.embed_video(project.video_url)

    for u in context['updates']:

        u.original_text = u.text
        (u.video, u.text) = base.embed_video(u.text)

    if request.user.is_authenticated():
        context['is_following'] = request.user in project.followed_by.all()
        context['is_owner'] = True if request.user == project.created_by else False
        context['is_admin'] = True if request.user.username == 'admin' else False

    context['is_pending'] = True if project.status == 'Pending' else False

    # temp var for testing stripe payments
    context['is_live'] = True if re.match(r'^beta', request.get_host()) else False

    return render(request, 'project.html', context)


def manage_project(request, pid=1):

    project = get_object_or_404(Project, pk=pid)

    if (not request.user.is_authenticated() or project.created_by != request.user) and not request.user.is_staff:
        return HttpResponseRedirect('/')

    opps = Opportunity.objects.filter(project=project)

    context = {}
    context['no_sponsorship'] = False if opps.filter(sponsorship = True) else True
    context['COUNTRIES'] = COUNTRIES

    engagements = OpportunityEngagement.objects.filter(project_id=pid)
    context.update({
        "project": project,
        "opportunities": opps,
        "engagements": engagements,
        "updates": Update.objects.filter(project=project).order_by("-date_created")
    })
    
    for u in context['updates']:

        (u.video, u.text) = base.embed_video(u.text)

    if request.user.is_authenticated():
        context['is_following'] = request.user in project.followed_by.all()

    if request.method == "POST":

        if request.POST.get('type', '') == 'opportunity':

            opportunity = get_object_or_404(Opportunity, pk=request.POST['id'])
            opportunity_form = OpportunityForm(request.POST or None, instance=opportunity)
            opportunity = opportunity_form.save(commit=False)

            media_file = request.FILES.get('file')
            if media_file:
                opportunity.media_url = base.send_to_remote_storage(media_file, opportunity.make_s3_media_url(media_file), "image/png")

            if opportunity_form.is_valid():
                opportunity.save()
            else:
                context['error'] = "failed to update opportunity"

        else:

            project_form = ProjectForm(request.POST or None, instance=project)
            original_media_url = project.media_url
            project = project_form.save(commit=False)

            media_file = request.FILES.get('file')

            if media_file:
                project.media_url = base.send_to_remote_storage(media_file, project.make_s3_media_url(media_file), "image/png")
            else:
                project.media_url = original_media_url

            if project_form.is_valid():

                project.save()

            else:

                context['error'] = "failed to update project"

    return render(request, 'manage_project.html', context)


@login_required
def new_project(request):

    # Show the sign page and collect emails
    context = {}
    context['causes'] = CAUSES

    allow_sponsorship = True

    if request.GET.get('org'):
        org = Organization.objects.get(id=request.GET.get('org'))
        context['organization'] = org

    if request.method == "POST":

        project_form = ProjectForm(request.POST)
        project = project_form.save(commit=False)

        if project_form.is_valid():

            project.organization = request.user.get_profile().organization
            project.created_by = request.user

            # limit to cobranded projects if appropriate
            if hasattr(settings, 'BRAND'):
                if project.tags:
                    t = project.tags.split(',')
                    t.append(settings.BRAND.get('id'))
                    project.tags = t
                else:
                    project.tags = settings.BRAND.get('id')

            project.save()

            if allow_sponsorship:

                project.create_sponsorship()
            
            # this has to occur after initial save b/c we use pk id as part of the s3 filepath
            media_file = request.FILES.get('file')
            if media_file:
                project.media_url = base.send_to_remote_storage(media_file, project.make_s3_media_url(media_file), "image/png")
                project.save()
            
            # send admin email with link adminpanel to change project status
            created_by = project.created_by.first_name + ' ' + project.created_by.last_name
            subj = "[%s] A new project submission" % request.get_host()
            body = """
                A new project has been submitted by %s:<br /><br />
                <b>%s</b><br /><br />
                %s<br /><br />
                <a href='%s'>View this project</a><br />
                """ % (created_by, project.name, project.short_desc, project.get_url(request))

            base.send_admin_email(subj, body, html_content=body)

            return HttpResponseRedirect('/project/%s/opportunity/add' % project.id)

        else:

            return HttpResponse("error")

    else:

        return render(request, 'new_project.html', context)


def view_opportunity(request, pid, oid):

    opp = get_object_or_404(Opportunity, pk=oid)
    updates = Update.objects.filter(opportunity=opp).order_by('-date_created')[0:10]
    context = {}
    
    context.update({
        'opportunity': opp,
        'project': opp.project,
        'resources': opp.resources.split(','),
        'other_opps': [rec for rec in Opportunity.objects.filter(project=opp.project).all() if rec.id != opp.id],
        'updates': updates,
        'is_engaged': False,
        'is_open' : True if opp.status != STATUS_CLOSED else False,
    })
    
    for u in context['updates']:

        u.original_text = u.text
        (u.video, u.text) = base.embed_video(u.text)

    if request.user.is_authenticated():

        context['is_following'] = request.user in opp.project.followed_by.all()
        context['is_owner'] = True if request.user == opp.project.created_by else False

        try:
            ue = OpportunityEngagement.objects.get(opportunity=opp.id, user=request.user.id)
        except ObjectDoesNotExist:
            ue = None

        if ue:
            if ue.status == 'Unpublished' or ue.status == 'Pending':
                context['pending'] = True
            if ue.status == STATUS_ACTIVE: 
                context['engaged'] = True
            
    return render(request, 'opportunity.html', context)    


@login_required
def new_organization(request):

    context = {}
    user_profile = request.user.get_profile()
    context['COUNTRIES'] = COUNTRIES

    if user_profile.organization_id:

        org = Organization.objects.get(id=user_profile.organization_id)
        context['organization'] = org

    if request.method == "POST":

        if not request.POST.get('use_users_org'):

            org_form = OrganizationForm(request.POST)
            org = org_form.save(commit=False)

            if org_form.is_valid():

                org.created_by = request.user
                org.save()
                
                user_profile.organization_id = org.id
                user_profile.save()
                
                org_url = org.URL if re.match(r'^http://', org.URL) else "http://" + org.URL

                # send admin email with link adminpanel to change project status
                subj = "[%s] New organization: %s" % (request.get_host(), org.name)
                body = "A new organization was added by %s:<br /><br /><b>%s</b><br /><br />" % (org.created_by, org.name)
                if org.URL:
                    body = body + "<a href='%s'>%s</a><br /><br />" % (org_url, org.URL)
                body = body + "Country: %s<br /><br />Mission Statement:<br /><br />\"%s\"<br /><br />" % (org.country, org.org_mission)

                base.send_admin_email(subj, body, html_content=body)
                          
            else:

                return HttpResponse("error")

        next = '/project/new?org=%s' % org.id

        return HttpResponseRedirect(next)

    return render(request, 'new_organization.html', context)
        

@login_required
def add_opportunity(request, pid=None, sponsorship=False):

    context = {}
    project = get_object_or_404(Project, pk=pid)

    context['project'] = project
    context['opportunities'] = Opportunity.objects.filter(project=pid)

    if request.method == "POST":

        if request.POST.get('name') == '' and request.POST.get('short_desc') == '' and not request.POST.get('add'):
            return HttpResponseRedirect('/project/%s/manage' % project.id)

        opp_form = OpportunityForm(request.POST)
        opp = opp_form.save(commit=False)

        if opp_form.is_valid():
            
            opp.project = project
            opp.organization = project.organization
            opp.created_by = request.user

            # limit to cobranded opportunities if appropriate
            if hasattr(settings, 'BRAND'):
                if opp.tags:
                    t = opp.tags.split(',')
                    t.append(settings.BRAND.get('id'))
                    opp.tags = t
                else:
                    opp.tags = settings.BRAND.get('id')

            opp.save()
        
            # this has to occur after initial save b/c we use pk id as part of the s3 filepath
            media_file = request.FILES.get('file')
            if media_file:
                opp.media_url = base.send_to_remote_storage(media_file, opp.make_s3_media_url(media_file), "image/png")
                opp.save()
            
            
            if request.POST.get('add'):

                return HttpResponseRedirect('/project/%s/opportunity/add' % project.id)

            else:

                return HttpResponseRedirect('/project/%s/manage' % project.id)

        else:

            return HttpResponse("error")

    elif sponsorship:

        project.create_sponsorship()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    else:

        return render(request, 'add_opportunity.html', context)

    
def find_opportunity(request):

    context = {}

    opportunities = Opportunity.objects.filter(status__iexact='Active')
    # cobranding
    if hasattr(settings, 'BRAND'):
        opportunities = opportunities.filter(tags__contains=settings.BRAND.get('id', ''))

    if request.method == 'POST': 

        search = request.POST.get("search")
        opp_type = request.POST.get("opp_type")
        context['search_term'] = search
        context['type'] = opp_type

        MAX_RESULTS = 50

        if search:

            opportunities = opportunities.filter(Q(name__contains=search) | Q(short_desc__contains=search) | Q(description__contains=search)).distinct()

        if opp_type:

            opportunities = opportunities.filter(opp_type=opp_type)

    opportunities = opportunities.filter(Q(sponsorship__isnull = True)|Q(sponsorship = False))

    context['opportunities'] = opportunities

    return render(request, 'find_opportunity.html', context)


def find_project(request):

    context = {}

    projects = Project.objects.filter(status__iexact='Active')
    # cobranding
    if hasattr(settings, 'BRAND'):
        projects = projects.filter(tags__contains=settings.BRAND.get('id', ''))

    if request.method == 'POST': 

        search = request.POST.get("search")
        context['search_term'] = search

        MAX_RESULTS = 50

        if search:

            projects = projects.filter(Q(name__contains=search) | Q(short_desc__contains=search) | Q(description__contains=search)).distinct()

    context['projects'] = projects

    return render(request, 'find_project.html', context)


def stripe_subscription(request):

    context = {}

    next = "/"

    if request.method == 'POST': 

        stripe.api_key = settings.STRIPE_KEY_SECRET

        next = request.POST.get('next', '/')
        amount = request.POST.get('amount')
        pid = request.POST.get('pid', '1')
        token = request.POST['stripeToken']
        plan_id = 'p%s-m%s' % (pid, amount)

        try:

            plan = stripe.Plan.retrieve(plan_id)

        except stripe.error.InvalidRequestError, e:

            plan = stripe.Plan.create(
                amount=amount,
                interval='month',
                name='Testing Project Sponsorship / project %s / amount %s' % (pid, amount),
                currency='usd',
                id=plan_id
            )

        customer = stripe.Customer.create(
            card=token,
            plan=plan_id,
            email=request.user.email
        )

        logging.error(customer)

        sub = customer.subscriptions.create(plan=plan_id)

        logging.error(sub)


    return HttpResponseRedirect(next)
