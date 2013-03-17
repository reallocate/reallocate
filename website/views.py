from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, csrf_protect


from website.lib.ses_email import send_email
from models import UserProfile

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

# landing_instance.ip_address = request.META['REMOTE_ADDR']

def homepage(request):
    return render_to_response('homepage.html', {}, context_instance=RequestContext(request))

def test_project(request):
    return render_to_response('project.html', {}, context_instance=RequestContext(request))

@csrf_exempt
def signup(request):
    if request.method == 'GET':
        return render_to_response('signup.html')
    
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
    state = "Please log in below..."
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
    return render_to_response('auth.html',{'state':state, 'username': username})

def view_project(request, *args):
    try:
        project = Project.objects.get(id=args[0])
    except ObjectDoesNotExist:
        return HttpResponse("error - no project found")
    return render_to_response('project.html', {
                            "project": project
        }, context_instance=RequestContext(request))

def view_opportunity(request, *args):
    try:
        opp = Opportunity.objects.get(id=args[0])
    except ObjectDoesNotExist:
        return HttpResponse("error - no opportunity found")
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

def add_opportunity(request, *args):
    # Create new Opportunity
    
    print args
    try:
        parent_project = Project.objects.get(id=args[0])
    except ObjectDoesNotExist:
        return HttpResponse("error - no project found")
    
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
