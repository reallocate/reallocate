from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from website.lib.ses_email import send_email
from models import UserProfile
from models import Project
from models import Opportunity
from models import Update

from website.models import ProjectForm, OpportunityForm, Project, Opportunity


@login_required
def private(request):
    return render_to_response('private.html', {
        'a': 'a',
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

    # Append the newly-created user with a company.
    user_profile = UserProfile()
    user_profile.user = user
    user_profile.save()

    return HttpResponseRedirect('/login/')


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
                state = "You're successfully logged in!"
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."
    return render_to_response('login.html',{'state':state, 'username': username}, context_instance=RequestContext(request))


def view_project(request, pid=1):
    project = get_object_or_404(Project, pk=pid)
    opportunities = Opportunity.objects.filter(project=project)
    updates = Update.objects.filter(project=project)
    return render_to_response('project.html', {
        "project": project,
        "updates": updates,
        "opportunities": opportunities,
    }, context_instance=RequestContext(request))


def view_opportunity(request, *args):
    opp = get_object_or_404(Opportunity, pk=args[0])
    return render_to_response('opportunity.html', {
        "opportunity": opp,
        "project": opp.project
    }, context_instance=RequestContext(request))


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
