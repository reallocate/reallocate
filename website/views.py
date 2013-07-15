import logging
import boto
from boto.s3.key import Key
from myproject import settings

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q

from website.models import OrganizationForm, Organization, ProjectForm, Project, Update, UserProfile
from website.models import OpportunityEngagement, Opportunity, OpportunityForm
from website.models import STATUS_ACTIVE, STATUS_CHOICES, STATUS_INACTIVE, STATUS_CLOSED

import website.base as base


@login_required
@csrf_exempt
def profile(request, username=None):
    """ for displaying and editing a users profile """
    
    context = base.build_base_context(request)
    if not username and not context.get('user'):
        return HttpResponseRedirect(settings.POST_LOGIN_URL)
    
    # this is a person viewing their own profile page, make it editable
    if not username: 
        user = context['user']
        context['edit'] = True
    else:
        user = User.objects.filter(Q(email=username) | Q(username=username))
    
    user_profile = UserProfile.objects.filter(Q(user=user))
    if len(user_profile) == 0:
        return render_to_response('nosuchuser.html', context)
    user_profile = user_profile[0] # replace above logic with None or single object?

    def remote_storage(uploaded_file, user):
        """ for uploading avatars to s3 """

        c = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        bucket = c.get_bucket(settings.S3_BUCKET)
        
        filename = 'users/%s/%s' % (user.email, uploaded_file.name)
        k = Key(bucket)
        k.set_metadata('Content-Type', 'image/png')
        k.key = filename
        k.set_contents_from_string(uploaded_file.read())
        k.set_acl('public-read')

        return 'http://s3.amazonaws.com/%s/%s' % (settings.S3_BUCKET, filename)
    
    if request.method == "POST":
        
        avatar = request.FILES.get('file')
        if avatar:
            filename = remote_storage(avatar, request.user) if avatar else ''
            user_profile.media_url = filename
        
        user_profile.user.email = request.POST.get("email")
        user_profile.bio = request.POST.get("bio")
        user_profile.occupation = request.POST.get("occupation")
        user_profile.location = request.POST.get("location")
        user_profile.skills.add(*[rec.strip() for rec in request.POST.get("skills", "").split(",")])
        user_profile.save()

        context['topmsg'] = 'Your settings have been saved'
    
    context['opps'] = Opportunity.objects.filter(engaged_by=user)
    context['followed_projects'] = Project.objects.filter(followed_by=user)
    context['my_projects'] = Project.objects.filter(created_by=user)
    context['user_profile'] = user_profile
    context['user_skills'] = ", ".join([rec.name for rec in user_profile.skills.all()])
    
    return render_to_response('profile.html', context, context_instance=RequestContext(request))


def public_profile(request, username=None):

    user = User.objects.filter(Q(email=username) | Q(username=username))
    user_profile = UserProfile.objects.filter(Q(user=user))
    context = base.build_base_context(request)

    if len(user_profile) < 1:

        context['username'] = 'name ' + username

        return render_to_response('nosuchuser.html', context)

    context['profile'] = user_profile[0]
    context['opps'] = Opportunity.objects.filter(engaged_by=user)
    context['projects'] = Project.objects.filter(followed_by=user)

    return render_to_response('public_profile.html', context, context_instance=RequestContext(request))
    

def login_page(request):

    context = base.build_base_context(request)
    
    return render_to_response('login.html', context, context_instance=RequestContext(request))


def home(request):

    context = base.build_base_context(request)

    context['projects'] = Project.objects.all()[:12]

    return render_to_response('home.html', context, context_instance=RequestContext(request))


def about(request):

    context = base.build_base_context(request)

    return render_to_response('about.html', context, context_instance=RequestContext(request))


def privacy(request):

    context = base.build_base_context(request)

    return render_to_response('privacy.html', context, context_instance=RequestContext(request))


def tos(request):

    context = base.build_base_context(request)

    return render_to_response('tos.html', context, context_instance=RequestContext(request))


def get_started(request):

    context = base.build_base_context(request)

    if hasattr(request.user, 'email'):

        context['next'] = '/organization/new'

    else:

        context['next'] = '/sign-up'

    return render_to_response('get_started.html', context, context_instance=RequestContext(request))


def test_email(request):

    email_type = request.GET.get('email_type')
    html_content = base.send_email_template(request, email_type, {}, "*", [], render=True)[0]

    return HttpResponse(content=html_content)


@csrf_exempt
def sign_up(request):

    context = base.build_base_context(request)

    context['referrer'] = request.META.get('HTTP_REFERER', '/')

    if re.match(r'/get-started', context['referrer']):  
        context['next'] = '/organization/new'
    else:
        content['next'] = context['referrer']

    if request.method == 'GET':
        return render_to_response('sign_up.html', context, context_instance=RequestContext(request))

    email = request.POST.get('email')
    password = request.POST.get('password')

    # Create a new user and persist it to the database.
    user = User.objects.create_user(username=email, email=email, password=password)
    user.save()

    user = authenticate(username=email, password=password)
    login(request, user)
    
    email_context = {'email': email, 'user': user}

    #base.send_email_template(request, "welcome", email_context, "subject", [settings.ADMIN_EMAIL, email])

    return HttpResponseRedirect(request.POST.get('next', '/'))


@csrf_exempt
def login_user(request):

    context = base.build_base_context(request)

    if request.POST:

        username = request.POST.get('username')
        password = request.POST.get('password')

        context['username'] = username

        user = authenticate(username=username, password=password)

        if user is not None:

            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(settings.POST_LOGIN_URL)
            else:
                context['state'] = "Your account is not active, please contact the site admin."
        else:
            context['state'] = "Your username and/or password were incorrect."

    return render_to_response('login.html', context, context_instance=RequestContext(request))


def view_project(request, pid=1):

    project = get_object_or_404(Project, pk=pid)
    opps = Opportunity.objects.filter(project=project)
    context = base.build_base_context(request)

    context.update({
        "project": project,
        "opportunities": opps,
        "num_opportunities": opps.count(),
        "updates": Update.objects.filter(project=project)})
    
    if request.user.is_authenticated():
        context['is_following'] = request.user in project.followed_by.all()
    
    context['num_following'] = project.followed_by.count()
    context['donation_purpose'] = project.name
    context['pid'] = project.id

    return render_to_response('project.html', context, context_instance=RequestContext(request))


def manage_project(request, pid=1):

    project = get_object_or_404(Project, pk=pid)
    opps = Opportunity.objects.filter(project=project)
    context = base.build_base_context(request)

    context.update({
        "project": project,
        "opportunities": opps,
        "num_opportunities": opps.count(),
        "updates": Update.objects.filter(project=project)})
    
    if request.user.is_authenticated():
        context['is_following'] = request.user in project.followed_by.all()
    
    context['num_following'] = project.followed_by.count()
    context['donation_purpose'] = project.name
    context['pid'] = project.id
    context['opps'] = opps

    return render_to_response('manage_project.html', context, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def new_project(request):

    # Show the sign page and collect emails
    context = base.build_base_context(request)

    if request.GET.get('org'):
        org = Organization.objects.get(id=request.GET.get('org'))

    if request.method == "POST":

        project_form = ProjectForm(request.POST)
        project = project_form.save(commit=False)

        if project_form.is_valid():
            
            project.organization = request.user.get_profile().organization
            project.created_by = request.user
            project.save()
            
            # send admin email with link adminpanel to change project status
            subj = "new project %s added by %s" % (project.name, request.user.email)
            body = """Go here to and change status to active:<br/>
                <a href='%s/admin/website/project/%s'>approve</a>
                For now: remember to email the above email after their project is live""" % (
                request.get_host(), project.id)

            #base.send_admin_email(subj, body, html_content=body)

            return HttpResponseRedirect('/project/%s/opportunity/add' % project.id)

        else:

            return HttpResponse("error")

    else:

        return render_to_response('new_project.html', context, context_instance=RequestContext(request))


@csrf_exempt
def view_opportunity(request, pid, oid):

    opp = get_object_or_404(Opportunity, pk=oid)
    project = get_object_or_404(Project, pk=opp.project.id)
    organization = project.organization
    updates = Update.objects.filter(opportunity=opp).order_by('-date_created')[0:10]
    context = base.build_base_context(request)
    
    context.update({
        'organization': organization,
        'opportunity': opp,
        'project': project,
        'other_opps': [rec for rec in Opportunity.objects.filter(project=opp.project).all() if rec.id != opp.id],
        'updates': updates,
        'is_engaged': False})
    
    if request.user.is_authenticated():

        context['is_following'] = request.user in project.followed_by.all()

        try:
            user_engagement = OpportunityEngagement.objects.get(opportunity=opp, user=request.user)
        except ObjectDoesNotExist:
            user_engagement = None

        if user_engagement:
            context['is_engaged'] = (user_engagement.status == STATUS_ACTIVE)
            
    return render_to_response('opportunity.html', context, context_instance=RequestContext(request))    


@csrf_exempt
@login_required
def engage_opportunity(request, pid, oid=1):
    context = base.build_base_context(request)

    opp = get_object_or_404(Opportunity, pk=oid)
    # todo - deal with money type => donations rather than a freeform response

    if request.method == "POST":
        response = request.POST.get("response", "")
        opp_eng = OpportunityEngagement(user=request.user, opportunity=opp)
        opp_eng.response = response
        opp_eng.save()
        subject = "New engagement with %s by %s" % (opp.name, request.user.email)
        html_content = """Their response is: %s<br/>
                       <a href='%s/admin/website/opportunityengagement/%s'>approve</a>""" % (
                        response, request.get_host(), opp_eng.id)
        # TODO: send to project/opp owner as well as admin
        base.send_admin_email(subject, html_content, html_content=html_content)
        topmsg = 'Thanks for your engagement - a project leader will get back to you as soon as possible'

        return HttpResponseRedirect("/project/%s/opportunity/%s?topmsg=%s" % (pid, oid, topmsg))
    
    context['opp'] = opp
    return render_to_response('engage.html', context, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def new_organization(request):

    context = base.build_base_context(request)

    if request.method == "POST":

        org_form = OrganizationForm(request.POST)
        org = org_form.save(commit=False)

        if org_form.is_valid():

            org.created_by = request.user
            org.save()
            
            profile = request.user.get_profile()
            profile.organization_id = org.id
            profile.save()
            
            # send admin email with link adminpanel to change project status
            subj = "[ReAlloBot] New organization %s added by %s" % (org.name, request.user.username)
            body = """Go here to and change status to active:<br/>
                      <a href='%s/admin/organization/%s'>approve</a>
                      For now: remember to email the above email after their organization is approved""" % (
                      request.get_host(), org.id)

            #base.send_admin_email(subj, body, html_content=body)

            next = '/project/new?org=%s' % org.id

            return HttpResponseRedirect(next)
                      
        else:

            return HttpResponse("error")

    return render_to_response('new_organization.html', context, context_instance=RequestContext(request))
        

@csrf_exempt
@login_required
def add_opportunity(request, pid=None):

    context = base.build_base_context(request)
    project = get_object_or_404(Project, pk=pid)

    context['opps'] = Opportunity.objects.filter(project=pid)

    if request.method == "POST":

        opp_form = OpportunityForm(request.POST)
        opp = opp_form.save(commit=False)

        if opp_form.is_valid():
            
            opp.project = project
            opp.organization = project.organization
            opp.created_by = request.user
            opp.save()
        
            if request.POST.get('add'):

                return HttpResponseRedirect('/project/%s/opportunity/add' % project.id)

            else:

                return HttpResponseRedirect('/')

        else:

            return HttpResponse("error")

    else:

        return render_to_response('add_opportunity.html', context, context_instance=RequestContext(request))

    
def search(request):

    context = base.build_base_context(request)

    # Search for Opportunities
    opportunities = None
        
    #search form submission
    if request.method == 'POST': 

        #search text
        search = request.POST.get("search")
        opp_type = request.POST.get("opp_type")

        if opp_type == '':
            opportunities = Opportunity.objects.filter(Q(name__contains=search) | Q(status__contains=search) | Q(short_desc__contains=search) | Q(description__contains=search) | Q(opp_type__contains=search) | Q(tags__name__in=[search])).distinct()[:12]
        elif search == 'Search...':    
            opportunities = Opportunity.objects.filter(opp_type=opp_type).distinct()[:12]
        else:    
            opportunities = Opportunity.objects.filter(Q(name__contains=search) | Q(status__contains=search) | Q(short_desc__contains=search) | Q(description__contains=search) | Q(opp_type__contains=search) | Q(tags__name__in=[search])).filter(opp_type=opp_type).distinct()[:12]

    if not opportunities:

        print u'NO OPPORTUNITIES FOUND'
        opportunities = Opportunity.objects.all()[:12]

    context['oppotunities'] = opportunities

    return render_to_response('search.html', context, context_instance=RequestContext(request))

    if request.user.is_authenticated():
        context['is_engaged'] = request.user in opp.engaged_by.all()

    return render_to_response('opportunity.html', context, context_instance=RequestContext(request))
