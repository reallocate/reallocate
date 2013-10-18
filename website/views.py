import logging, hashlib, random
import boto
import re
from boto.s3.key import Key
from website import settings

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q

from website.models import OrganizationForm, Organization, ProjectForm, Project, Update, UserProfile
from website.models import OpportunityEngagement, Opportunity, OpportunityForm
from website.models import STATUS_ACTIVE, STATUS_CHOICES, STATUS_INACTIVE, STATUS_CLOSED, CAUSES

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
        
        user_profile.user.first_name = request.POST.get("first_name")
        user_profile.user.last_name = request.POST.get("last_name")
        user_profile.user.email = request.POST.get("email")
        user_profile.bio = request.POST.get("bio")
        user_profile.occupation = request.POST.get("occupation")
        user_profile.location = request.POST.get("location")
        user_profile.skills.add(*[rec.strip() for rec in request.POST.get("skills", "").split(",")])
        user_profile.save()

        context['alert'] = 'Your changes have been saved.'
    
    context['opportunities'] = Opportunity.objects.filter(engaged_by=user)
    context['followed_projects'] = Project.objects.filter(followed_by=user)
    context['my_projects'] = Project.objects.filter(created_by=user)
    for p in context['my_projects']:
        p.is_admin = True
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

    context['user_profile'] = user_profile[0]
    context['opportunities'] = Opportunity.objects.filter(engaged_by=user)
    context['projects'] = Project.objects.filter(followed_by=user)

    return render_to_response('public_profile.html', context, context_instance=RequestContext(request))
    

def login_page(request):

    context = base.build_base_context(request)
    
    return render_to_response('login.html', context, context_instance=RequestContext(request))


def home(request):

    context = base.build_base_context(request)

    context['projects'] = Project.objects.filter(Q(status__iexact='pending')|Q(status__iexact='active'))[:36]

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
def reset_password(request):

    context = base.build_base_context(request)
    
    if request.POST:
        email = request.POST.get('email')
        temp_password = request.POST.get('temp_password')
        new_password = request.POST.get('password')
        user = User.objects.filter(email=email)
        if not user:
            return HttpResponseRedirect('/')
        user = user[0]
        if not user.check_password(temp_password):
            context['alert'] = "You have entered an incorrect temporary password."
            return render_to_response('temp_password.html', context, context_instance=RequestContext(request))
        user.set_password(new_password)
        user.save()
        
        user = authenticate(username=email, password=new_password)
        login(request, user)
    
        return HttpResponseRedirect("/")
    
    context['temp_password'] = request.GET.get("temp_password", "")
    context['email'] = request.GET.get("email", "")
    return render_to_response('reset_password.html', context, context_instance=RequestContext(request))
    

@csrf_exempt
def forgot_password(request):

    context = base.build_base_context(request)
    
    if request.POST:
        email = request.POST.get('email')
        reset_user = User.objects.filter(email=email)
        if not reset_user:
            return HttpResponseRedirect('/')
        
        temp_password = hashlib.md5(str(random.randint(0, 10000000))).hexdigest()[0:7]
        reset_user = reset_user[0]
        reset_user.set_password(temp_password)
        reset_user.save()
        
        subj = "Your password on Reallocate has been reset"
        body = """Click this link to choose a new password.<br/><a href='%s/reset-password?temp_password=%s&email=%s'>
            Choose a new password</a><br/><br/>Thanks,<br/>Reallocate""" % (request.get_host(), temp_password, email)
                
        base.send_email(email, subj, body, html_content=body)
        return HttpResponseRedirect('/forgot-password?alert=Your+password+has+been+reset.')
        
    context['email'] = request.GET.get('email', '')

    return render_to_response('forgot_password.html', context, context_instance=RequestContext(request))


@csrf_exempt
def sign_up(request):

    context = base.build_base_context(request)

    context['referrer'] = request.META.get('HTTP_REFERER', '/')

    if re.search(r'\/get-started', context['referrer']): 
        logging.error('get-started') 
        context['next'] = '/organization/new'
    else:
        context['next'] = context['referrer']

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

                next = request.POST.get('next') or settings.POST_LOGIN_URL
                logging.error(next)

                return HttpResponseRedirect(next)

            else:
                context['state'] = "Your account is not active, please contact the site admin."
        else:
            context['state'] = "Your username and/or password were incorrect."

    return render_to_response('login.html', context, context_instance=RequestContext(request))


def view_project(request, pid=1):

    project = get_object_or_404(Project, pk=pid)
    opps = Opportunity.objects.filter(project=project)
    engagement = OpportunityEngagement.objects.filter(project=project)
    context = base.build_base_context(request)

    context.update({
        "project": project,
        "opportunities": opps,
        "engagement": engagement,
        "updates": Update.objects.filter(project=project).order_by('-date_created')})
    
    if project.video_url:
        (project.video, foo) = embed_video(project.video_url)

    for u in context['updates']:

        (u.video, u.text) = embed_video(u.text)

    if request.user.is_authenticated():
        context['is_following'] = request.user in project.followed_by.all()
        context['is_admin'] = True if request.user == project.created_by else False

    return render_to_response('project.html', context, context_instance=RequestContext(request))


def manage_project(request, pid=1):

    project = get_object_or_404(Project, pk=pid)

    if not request.user.is_authenticated() or project.created_by != request.user:
        return HttpResponseRedirect('/')

    opps = Opportunity.objects.filter(project=project)
    context = base.build_base_context(request)
    engagements = OpportunityEngagement.objects.filter(project_id=pid)
    context.update({
        "project": project,
        "opportunities": opps,
        "engagements": engagements,
        "updates": Update.objects.filter(project=project).order_by("-date_created")
    })
    
    for u in context['updates']:

        (u.video, u.text) = embed_video(u.text)

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
            project = project_form.save(commit=False)

            media_file = request.FILES.get('file')

            if media_file:
                project.media_url = base.send_to_remote_storage(media_file, project.make_s3_media_url(media_file), "image/png")

            if project_form.is_valid():

                project.save()

            else:

                context['error'] = "failed to update project"

    return render_to_response('manage_project.html', context, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def new_project(request):

    # Show the sign page and collect emails
    context = base.build_base_context(request)
    context['causes'] = CAUSES

    if request.GET.get('org'):
        org = Organization.objects.get(id=request.GET.get('org'))
        context['organization'] = org

    if request.method == "POST":

        project_form = ProjectForm(request.POST)
        project = project_form.save(commit=False)

        if project_form.is_valid():

            project.organization = request.user.get_profile().organization
            project.created_by = request.user
            project.save()
            
            # this has to occur after initial save b/c we use pk id as part of the s3 filepath
            media_file = request.FILES.get('file')
            if media_file:
                project.media_url = base.send_to_remote_storage(media_file, project.make_s3_media_url(media_file), "image/png")
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
    updates = Update.objects.filter(opportunity=opp).order_by('-date_created')[0:10]
    context = base.build_base_context(request)
    
    context.update({
        'opportunity': opp,
        'project': opp.project,
        'resources': opp.resources.split(','),
        'other_opps': [rec for rec in Opportunity.objects.filter(project=opp.project).all() if rec.id != opp.id],
        'updates': updates,
        'is_engaged': False
    })
    
    for u in context['updates']:

        (u.video, u.text) = embed_video(u.text)

    if request.user.is_authenticated():

        context['is_following'] = request.user in opp.project.followed_by.all()
        context['is_engaged'] = True if request.user == opp.project.created_by else False

        try:
            ue = OpportunityEngagement.objects.get(opportunity=opp.id, user=request.user.id)
        except ObjectDoesNotExist:
            ue = None

        if ue:
            if ue.status == 'Unpublished' or ue.status == 'Pending':
                context['pending'] = True
            if ue.status == STATUS_ACTIVE: 
                context['engaged'] = True
            
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
        alert = 'Thanks for your engagement - a project leader will get back to you as soon as possible'

        return HttpResponseRedirect("/project/%s/opportunity/%s?alert=%s" % (pid, oid, alert))
    
    context['opportunity'] = opp

    return render_to_response('engage.html', context, context_instance=RequestContext(request))


@csrf_exempt
@login_required
def new_organization(request):

    context = base.build_base_context(request)
    user_profile = request.user.get_profile()

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
                
                # send admin email with link adminpanel to change project status
                subj = "[ReAlloBot] New organization %s added by %s" % (org.name, request.user.username)
                body = """Go here to and change status to active:<br/>
                          <a href='%s/admin/organization/%s'>approve</a>
                          For now: remember to email the above email after their organization is approved""" % (
                          request.get_host(), org.id)

                #base.send_admin_email(subj, body, html_content=body)
                          
            else:

                return HttpResponse("error")

        next = '/project/new?org=%s' % org.id

        return HttpResponseRedirect(next)

    return render_to_response('new_organization.html', context, context_instance=RequestContext(request))
        

@csrf_exempt
@login_required
def add_opportunity(request, pid=None):

    context = base.build_base_context(request)
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

    else:

        return render_to_response('add_opportunity.html', context, context_instance=RequestContext(request))

    
def search(request):

    context = base.build_base_context(request)

    if request.method == 'POST': 

        # search text
        search = request.POST.get("search")
        opp_type = request.POST.get("opp_type")

        if opp_type == '':
            opportunities = Opportunity.objects.filter(Q(name__contains=search) | Q(status__contains=search) | Q(short_desc__contains=search) | Q(description__contains=search) | Q(opp_type__contains=search) | Q(tags__name__in=[search])).distinct()[:12]
        elif search == 'Search...':    
            opportunities = Opportunity.objects.filter(opp_type=opp_type).distinct()[:12]
        else:    
            opportunities = Opportunity.objects.filter(Q(name__contains=search) | Q(status__contains=search) | Q(short_desc__contains=search) | Q(description__contains=search) | Q(opp_type__contains=search) | Q(tags__name__in=[search])).filter(opp_type=opp_type).distinct()[:12]

    else:

        opportunities = Opportunity.objects.all()

    context['opportunities'] = opportunities

    return render_to_response('search.html', context, context_instance=RequestContext(request))


def embed_video(update_text):

    vimeo = re.search(r'(http[s]*:\/\/vimeo\.com/([0-9]+).*?)[\s|$]*', update_text)
    youtube = re.search(r'(http[s]*:\/\/www\.youtube\.com/watch\?v=([a-z|A-Z|0-9]+).*?)[\s|$]*', update_text)

    if youtube:

        video_id = youtube.group(2)

        embed_tag = '<object data="http://www.youtube.com/v/%s" type="application/x-shockwave-flash"><param name="src" value="http://www.youtube.com/v/%s" /></object>' % (video_id, video_id)

        return [embed_tag, update_text.replace(youtube.group(1), '')]

    elif vimeo:

        video_id = vimeo.group(2)

        embed_tag = '<iframe src="http://player.vimeo.com/video/%s" frameborder="0" webkitAllowFullScreen mozallowfullscreen allowFullScreen></iframe>' % video_id

        return [embed_tag, update_text.replace(vimeo.group(1), '')]

    else:

        return [None, update_text]

