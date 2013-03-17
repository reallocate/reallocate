from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from website.lib.ses_email import send_email
from website.models import ProjectForm, OpportunityForm, Project, Opportunity, Update, UserProfile
from website.models import OpportunityEngagements
import website.base as base

@login_required
@csrf_exempt
def profile(request):
    user_profile = base.get_current_userprofile(request)
    topmsg = None
    
    if request.method == "POST":
        user_profile.user.email = request.POST.get("email")
        user_profile.bio = request.POST.get("bio")
        user_profile.media_url = request.POST.get("media_url")
        user_profile.save()
        topmsg = 'Your settings have been saved'
    
    return render_to_response('profile.html', {
        'user_profile': user_profile,
        'topmsg': topmsg,
    }, context_instance=RequestContext(request))

def login_page(request):
    return render_to_response('login.html', {
        'a': 'a',
    }, context_instance=RequestContext(request))

def homepage(request):
    opportunities = Opportunity.objects.all()[:4]
    return render_to_response('homepage.html', {'opportunities': opportunities},
                              context_instance=RequestContext(request))

def about(request):
    return render_to_response('about.html', {}, context_instance=RequestContext(request))

def opportunity_list(request):
    opportunities = Opportunity.objects.all()[:6]
    projects = Opportunity.objects.all()[:6]

    return render_to_response('opportunity_list.html', {'opportunities': opportunities},
                              context_instance=RequestContext(request))

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
    return HttpResponseRedirect('/find-opportunity')

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
                return HttpResponseRedirect('/find-opportunity')
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."
    return render_to_response('login.html',{'state':state, 'username': username}, context_instance=RequestContext(request))


def view_project(request, pid=1):
    project = get_object_or_404(Project, pk=pid)
    model = {
        "project": project,
        "opportunities": Opportunity.objects.filter(project=project),
        "num_opportunities": Opportunity.objects.filter(project=project).count(),
        "updates": Update.objects.filter(project=project)
    }
    
    if request.user.is_authenticated():
        model['user_profile'] = base.get_current_userprofile(request)
        model['is_following'] = model['user_profile'].followed_projects.all().count() > 0
        model['num_following'] = UserProfile.objects.filter(followed_projects=project).count()
    
    return render_to_response('project.html', model, context_instance=RequestContext(request))


def view_opportunity(request, pid=1):
    opp = get_object_or_404(Opportunity, pk=pid)
    project = get_object_or_404(Project, pk=opp.project.id)
    updates = Update.objects.filter(opportunity=opp)
    topmsg = request.GET.get('topmsg')

    other_opps = Opportunity.objects.filter(project=opp.project)
    other_opps_clean = []
    for other_opp in other_opps:
        if not opp.id == other_opp.id:
            other_opps_clean.append(other_opp)

    return render_to_response('opportunity.html', {
        "opportunity": opp,
        "project": project,
        "other_opps": other_opps_clean,
        "updates": updates,
        "topmsg": topmsg
    }, context_instance=RequestContext(request))

@csrf_exempt
@login_required
def engage(request, pid=1):
    opp = get_object_or_404(Opportunity, pk=pid)
    
    # todo - deal with money type => donations rather than a freeform response
    if request.method == "POST":
        response = request.POST.get("response", "")
        user_profile = base.get_current_userprofile(request)
        OpportunityEngagements(user_profile=user_profile, opportunity=opp).save()
        topmsg = 'Thanks for your engagement - a project leader will get back to you as soon as possible'
        return HttpResponseRedirect("/opportunity/" + str(opp.id) + "?topmsg=" + topmsg)
    
    return render_to_response('engage.html', {
        "opp": opp,
        "show_form": show_form,
        "topmsg": topmsg
    }, context_instance=RequestContext(request))

@login_required
def add_project(request):
    # Show the sign page and collect emails
    show_invite = True
    if request.method == "POST":
        myform = ProjectForm(request.POST)
        landing_instance = myform.save(commit=False)
        if myform.is_valid():
            landing_instance.ip_address = request.META['REMOTE_ADDR']
            landing_instance.save()
            show_invite = False

            # send_email("MY SITE: Contact Us signup", "email=" + request.POST["email"])

        else:
            return HttpResponse("error")

    myform = ProjectForm()
    return render_to_response('add_project.html', {
        "myform": myform,
        "show_invite": show_invite
    }, context_instance=RequestContext(request))

@login_required
def add_opportunity(request, oid=1):
    # Create new Opportunity
    parent_project = get_object_or_404(Project, pk=oid)
    show_form = True

    if request.method == "POST":
        myform = OpportunityForm(request.POST)
        new_instance = myform.save(commit=False)
        if myform.is_valid():
            new_instance.project = parent_project
            new_instance.save()
            show_form = False
        else:
            return HttpResponse("error")

    myform = OpportunityForm()
    
    return render_to_response('add_opportunity.html', {
        "myform": myform,
        "parent_project": parent_project,
        "show_form": show_form
    }, context_instance=RequestContext(request))
