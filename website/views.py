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
from website.models import OrganizationForm, Organization, ProjectForm, Project, Update, UserProfile
from website.models import OpportunityEngagement, Opportunity, OpportunityForm 
import website.base as base
from django.db.models import Q

@login_required
@csrf_exempt
def profile(request):
    """ for displaying and editing a users profile """
    
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
        
    user_profile = request.user.get_profile()
    topmsg = None
    if request.method == "POST":
        avatar = request.FILES.get('file')
        filename = remote_storage(avatar, request.user)
        
        user_profile.user.email = request.POST.get("email")
        user_profile.bio = request.POST.get("bio")
        user_profile.media_url = filename
        user_profile.organization = request.POST.get("organization")
        user_profile.save()
        topmsg = 'Your settings have been saved'
    
    return render_to_response('profile.html', {
        'user_profile': user_profile,
        'topmsg': topmsg,
    }, context_instance=RequestContext(request))

def public_profile(request, username=None):
    user = User.objects.filter(Q(email=username) | Q(username=username))
    user_profile = UserProfile.objects.filter(Q(user=user))
    context = base.build_base_context(request)
    if len(user_profile) < 1:
        context['username'] = 'name ' + username
        return render_to_response('nosuchuser.html', context, context_instance=RequestContext(request))
    context['profile'] = user_profile[0]
    context['opps'] = Opportunity.objects.filter(engaged_by=user)
    context['projects'] = Project.objects.filter(followed_by=user)
    return render_to_response('public_profile.html', context, context_instance=RequestContext(request))
    

def login_page(request):
    return render_to_response('login.html', {
        'a': 'a',
    }, context_instance=RequestContext(request))

def homepage(request):
    projects = Project.objects.all()[:12]
    return render_to_response('homepage.html', {'projects': projects},
                              context_instance=RequestContext(request))

def about(request):
    return render_to_response('about.html', {}, context_instance=RequestContext(request))

def learn(request):
    return render_to_response('learn.html', {}, context_instance=RequestContext(request))

@csrf_exempt
def signup(request):
    if request.method == 'GET':
        return render_to_response('signup.html', {}, context_instance=RequestContext(request))
    email = request.POST.get('email')
    password = request.POST.get('password')

    # Create a new user and persist it to the database.
    user = User.objects.create_user(username=email, email=email, password=password)
    user.save()

    user = authenticate(username=email, password=password)
    login(request, user)
    
    email_context = {'email': email, 'user': user}
    resp = base.send_email_template("welcome", email_context, "subject", [settings.ADMIN_EMAIL, email])
    if resp: # resp = (html_content, text_content) - for local development
        return HttpResponse(content=resp[0])
    return HttpResponseRedirect(settings.POST_LOGIN_URL)

@csrf_exempt
def login_user(request):
    state = ""
    username = password = ''
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(settings.POST_LOGIN_URL)
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."
    return render_to_response('login.html',{'state':state, 'username': username}, context_instance=RequestContext(request))


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
    return render_to_response('project.html', context, context_instance=RequestContext(request))

@login_required
def add_project(request):
    # Show the sign page and collect emails
    context = base.build_base_context(request)
    context['show_add_project'] = True
    if request.method == "POST":
        myform = ProjectForm(request.POST)
        project = myform.save(commit=False)
        if myform.is_valid():
            
            project.organization = request.user.get_profile().organization
            project.created_by = request.user
            project.save()
            context['show_add_project'] = False
            
            # send admin email with link adminpanel to change project status
            subj = "new project %s added by %s" % (project.name, context['user_email'])
            body = """Go here to and change status to active:<br/>
                      <a href='%s/admin/website/project/%s'>approve</a>
                      For now: remember to email the above email after their project is live""" % (
                      request.get_host(), project.id)
            base.send_admin_email(subj, body, html_content=body)
        else:
            return HttpResponse("error")

    context['myform'] = ProjectForm()
    return render_to_response('add_project.html', context, context_instance=RequestContext(request))

@csrf_exempt
def view_opportunity(request, pid):
    opp = get_object_or_404(Opportunity, pk=pid)
    project = get_object_or_404(Project, pk=opp.project.id)
    organization = project.organization
    updates = Update.objects.filter(opportunity=opp).order_by('-date_created')[0:10]
    context = base.build_base_context(request)
    context.update({
        'organization': organization,
        'opportunity': opp,
        'project': project,
        'other_opps': [rec for rec in Opportunity.objects.filter(project=opp.project).all() if rec.id != opp.id],
        'updates': updates})
    
    if request.user.is_authenticated():
        context['is_engaged'] = request.user in opp.engaged_by.all()
        context['is_following'] = request.user in project.followed_by.all()
    return render_to_response('opportunity.html', context, context_instance=RequestContext(request))

@login_required
def add_opportunity(request, oid=1):
    # Create new Opportunity
    parent_project = get_object_or_404(Project, pk=oid)
    show_form = True

    if request.method == "POST":
        myform = OpportunityForm(request.POST)
        opportunity = myform.save(commit=False)
        if myform.is_valid():
            opportunity.project = parent_project
            opportunity.save()
            show_form = False
        else:
            return HttpResponse("error")

    myform = OpportunityForm()
    
    return render_to_response('add_opportunity.html', {
        "myform": myform,
        "parent_project": parent_project,
        "show_form": show_form
    }, context_instance=RequestContext(request))
    
    
    
def search(request):
    # Search for Opportunities
    opportunities = None
        
    #search form submission
    if request.method == 'POST':        
        #search text
        search = request.POST.get("search")
        print u'search: %s' % (search)

        opp_type = request.POST.get("opp_type")
        print u'opp_type: %s' % (opp_type)


        if opp_type == 'Type...':
            opportunities = Opportunity.objects.filter(Q(name__contains=search) | Q(status__contains=search) | Q(short_desc__contains=search) | Q(description__contains=search) | Q(opp_type__contains=search) | Q(tags__name__in=[search])).distinct()[:12]
        else:    
            opportunities = Opportunity.objects.filter(Q(name__contains=search) | Q(status__contains=search) | Q(short_desc__contains=search) | Q(description__contains=search) | Q(opp_type__contains=search) | Q(tags__name__in=[search])).filter(opp_type=opp_type).distinct()[:12]

    
    if not opportunities:
        opportunities = Opportunity.objects.all()[:12]

    return render_to_response('search.html', {'opportunities': opportunities},
                              context_instance=RequestContext(request))

    if request.user.is_authenticated():
        context['is_engaged'] = request.user in opp.engaged_by.all()

    return render_to_response('opportunity.html', context, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def engage(request, pid=1):
    opp = get_object_or_404(Opportunity, pk=pid)
    # todo - deal with money type => donations rather than a freeform response
    if request.method == "POST":
        response = request.POST.get("response", "")
        print response # TODO: add response to this object - was breaking the db save
        OpportunityEngagement(user=request.user, opportunity=opp).save()
        topmsg = 'Thanks for your engagement - a project leader will get back to you as soon as possible'
        return HttpResponseRedirect("/opportunity/" + str(opp.id) + "?topmsg=" + topmsg)
    
    return render_to_response('engage.html', {
        "opp": opp
    }, context_instance=RequestContext(request))

@login_required
def add_organization(request):
    context = base.build_base_context(request)
    show_invite = True
    if request.method == "POST":
        myform = OrganizationForm(request.POST)
        organization = myform.save(commit=False)
        if myform.is_valid():
            organization.ip_address = request.META['REMOTE_ADDR']
            organization.created_by = request.user
            organization.save()
            
            profile = request.user.get_profile()
            profile.organization_id = organization.id
            profile.save()
            
            show_invite = False
            # send admin email with link adminpanel to change project status
            subj = "new organization %s added by %s" % (organization.name, context['user_email'])
            body = """Go here to and change status to active:<br/>
                      <a href='%s/admin/website/organization/%s'>approve</a>
                      For now: remember to email the above email after their organization is approved""" % (
                      request.get_host(), organization.id)
            base.send_admin_email(subj, body, html_content=body)
                      
        else:
            return HttpResponse("error")

    context['myform'] = OrganizationForm()
    context['show_invite'] = show_invite
    return render_to_response('add_organization.html', context, context_instance=RequestContext(request))
        
@login_required
def add_opportunity(request, oid=None):
    # Create new Opportunity
    project = None
    show_form = True

    user_profile = base.get_current_userprofile(request)
    org = user_profile.organization
    if not org:
        return HttpResponseRedirect('/add_organization')
    
    # check the DB to see if there are any projects created by this org
    project = Project.objects.get(organization_id=org)
    if not project:
       return HttpResponseRedirect('/add_project')
        
    
    if request.method == "POST":
        
        myform = OpportunityForm(request.POST)
        opportunity = myform.save(commit=False)
        if myform.is_valid():
            opportunity.project = project
            opportunity.organization = org
            opportunity.save()
            show_form = False
        else:
            return HttpResponse("error")

    myform = OpportunityForm()
    
    return render_to_response('add_opportunity.html', {
        "myform": myform,
        "parent_project": project,
        "show_form": show_form
    }, context_instance=RequestContext(request))


    
def search(request):
    # Search for Opportunities
    opportunities = None
        
    #search form submission
    if request.method == 'POST':        
        #search text
        search = request.POST.get("search")
        print u'search: %s' % (search)

        opp_type = request.POST.get("opp_type")
        print u'opp_type: %s' % (opp_type)


        if opp_type == '':
            print u'CASE A'
            opportunities = Opportunity.objects.filter(Q(name__contains=search) | Q(status__contains=search) | Q(short_desc__contains=search) | Q(description__contains=search) | Q(opp_type__contains=search) | Q(tags__name__in=[search])).distinct()[:12]
        elif search == 'Search...':    
            print u'CASE B'
            opportunities = Opportunity.objects.filter(opp_type=opp_type).distinct()[:12]
        else:    
            print u'CASE C'
            opportunities = Opportunity.objects.filter(Q(name__contains=search) | Q(status__contains=search) | Q(short_desc__contains=search) | Q(description__contains=search) | Q(opp_type__contains=search) | Q(tags__name__in=[search])).filter(opp_type=opp_type).distinct()[:12]

    
    if not opportunities:
        print u'NO OPPORTUNITIES FOUND'
        opportunities = Opportunity.objects.all()[:12]

    return render_to_response('search.html', {'opportunities': opportunities},
                              context_instance=RequestContext(request))

    if request.user.is_authenticated():
        context['is_engaged'] = request.user in opp.engaged_by.all()

    return render_to_response('opportunity.html', context, context_instance=RequestContext(request))
