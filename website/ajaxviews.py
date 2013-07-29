import base, json, logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response, get_object_or_404

import website.base as base
from myproject.settings import ADMIN_EMAIL
from website.models import UserProfile, Project, ProjectForm, Update, Opportunity, OpportunityEngagement


@login_required
# this won't crash w/ login_required but redirect doesn't work on ajax call - TODO: fix rather than these hide links

def modify_project_relation(request, *args):

    # action = [follow, unfollow]
    project_id = request.GET.get('project_id', '')
    action = request.GET.get('action', '')

    try:
        project = Project.objects.get(pk=project_id)

    except Exception, error:

        return HttpResponse(json.dumps({'failure': 'no project found'}), status=500)

    if action == 'follow':

        project.followed_by.add(request.user)
        # TODO: remove admin email from this as # of follows increases
        #base.send_email([ADMIN_EMAIL, project.created_by.email],
        #    'new follower: %s for project: %s' % (request.user.email, project.name), '')

    if action == 'unfollow':

        project.followed_by.remove(request.user)

    project.save()

    response = { "success": "true" }

    return HttpResponse(json.dumps(response), mimetype="application/json")
  

@csrf_exempt
@login_required
def engage_opportunity(request):

    context = base.build_base_context(request)

    pid = request.REQUEST.get('projectId')
    oid = request.REQUEST.get('opportunityId')
    response = {}

    if pid and oid:

        opp = get_object_or_404(Opportunity, pk=oid)
        response = {}

        opp_eng = OpportunityEngagement(user=request.user, opportunity=opp)
        opp_eng.response = response

        opp_eng.save()

        subject = "New engagement with %s by %s" % (opp.name, request.user.email)
        html_content = """Their response is: %s<br/>
                       <a href='%s/admin/website/opportunityengagement/%s'>approve</a>""" % (
                        response, request.get_host(), opp_eng.id)
                       
        # TODO: send to project/opp owner as well as admin
        base.send_admin_email(subject, html_content, html_content=html_content)

        response['message'] = "Thanks for your request. A project leader will get back to you as soon as possible."

    else:

        response['message'] = "No project or opportunity id."
    
    return HttpResponse(json.dumps(response), mimetype="application/json")


@login_required
@csrf_exempt
def add_update(request, *args):

    orgid = request.GET.get('orgid')
    pid = request.GET.get('pid')
    oid = request.GET.get('oid')
    update_text = request.GET.get('update_text')
    mime_type = request.META.get('HTTP_X_MIME_TYPE')
    
    # TODO: check mimetype for proper file extensions
    # TODO: make image name unique hash based on time to avoid collisions
    filename = base.remote_storage(request.body, 'project/%s/opportunity/%s/image.png' % (pid, oid), mime_type)

    # TODO:  error checking.  i.e. does user have permission?
    update = Update.objects.create(organization_id=orgid, project_id=pid, media_url=filename,
                                   opportunity_id=oid, text=update_text, created_by=request.user)

    return HttpResponse(json.dumps({ "success": "true" }), mimetype="application/json")


@login_required
@csrf_exempt
def update_project(request, *args):

    if request.POST:

        project = Project.objects.get(id=request.POST.get('id'))

        if project:

            project.name = request.POST.get('name')
            project.short_desc = request.POST.get('short_desc')
            project.description = request.POST.get('description')

            project.save()
    
            response_data = { "success": "true" }

        else:

            response_data = { "success": "false" } 

    else:

        response_data = { "sucess": "false" }

    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@csrf_exempt
def login_user(request):

    username = request.REQUEST.get('username')
    password = request.REQUEST.get('password')

    user = authenticate(username=username, password=password)
    
    if user is not None:

      if user.is_active:

            login(request, user)

            response = { 'success': True, 'user': {'email': user.email, 'firstName': user.first_name, 'lastName': user.last_name} }
            if request.POST.get('next'):
                response['next'] = request.POST.get('next')

            return HttpResponse(json.dumps(response), content_type="application/json")

      else:
            return HttpResponse(json.dumps({ 'success': False, 'message': 'Your account has been disabled' }), content_type="application/json", status=403)
    else:

      return HttpResponse(json.dumps({ 'success': False, 'message': 'Invalid username or password' }), content_type="application/json", status=403)


def check_available(request, *args):

    username = request.REQUEST.get('username')
    email = request.REQUEST.get('email')

    if username:

        q = User.objects.filter(username=username)
        response_data = True if q else False

    elif email:

        q = User.objects.filter(email=email)
        response_data = True if q else False

    else:

        response_data = ''


    return HttpResponse(json.dumps(response_data), mimetype="application/json")
