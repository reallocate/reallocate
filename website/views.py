from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse

from website.lib.ses_email import send_email

from website.models import ProjectForm


@login_required
def private(request):
    return render_to_response('private.html', {
        'a': 'a',
    }, context_instance=RequestContext(request))


def login_test(request):
    return render_to_response('login.html', {
        'a': 'a',
    }, context_instance=RequestContext(request))


# def index(request):
#     # Show the sign page and collect emails
#
#     show_invite = True
#     if request.method == "POST":
#         myform = LandingForm(request.POST)
#         landing_instance = myform.save(commit=False)
#         if myform.is_valid():
#             landing_instance.ip_address = request.META['REMOTE_ADDR']
#             landing_instance.save()
#             show_invite = False
#
#             send_email("MY SITE: Newsletter signup", "email=" + request.POST["email"])
#
#         else:
#             return HttpResponse("error")
#
#     myform = LandingForm()
#     return render_to_response('index.html', {
#         "myform": myform,
#         "show_invite": show_invite
#     }, context_instance=RequestContext(request))
#
#
# def contribute(request):
#     # Show the sign page and collect emails
#
#     show_invite = True
#     if request.method == "POST":
#         myform = ContributeForm(request.POST)
#         landing_instance = myform.save(commit=False)
#         if myform.is_valid():
#             landing_instance.ip_address = request.META['REMOTE_ADDR']
#             landing_instance.save()
#             show_invite = False
#
#             # send_email("MY SITE: Contact Us signup", "email=" + request.POST["email"])
#
#         else:
#             return HttpResponse("error")
#
#     myform = ContributeForm()
#     return render_to_response('contribute.html', {
#         "myform": myform,
#         "show_invite": show_invite
#     }, context_instance=RequestContext(request))
#

def homepage(request):
    return render_to_response('homepage.html', {}, context_instance=RequestContext(request))
    
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
