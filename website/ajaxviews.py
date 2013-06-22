import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login

import website.base as base
from myproject.settings import ADMIN_EMAIL
from website.models import UserProfile, Project, Update


@login_required
# this won't crash w/ login_required but redirect doesn't work on ajax call - TODO: fix rather than these hide links

def modify_project_relation(request, *args):

    # action = [follow, unfollow]
    project_id = request.GET.get('project_id', '')
    action = request.GET.get('action', '')

    try:
        project = Project.objects.get(pk=project_id)

    except Exception, err:

        return HttpResponse(json.dumps({'failure': 'no project found'}), status=500)

    if action == 'follow':

        project.followed_by.add(request.user)
        # TODO: remove admin email from this as # of follows increases
        #base.send_email([ADMIN_EMAIL, project.created_by.email],
        #    'new follower: %s for project: %s' % (request.user.email, project.name), '')

    if action == 'unfollow':

        project.followed_by.remove(request.user)

    project.save()

    response_data = { "success": "true" }

    return HttpResponse(json.dumps(response_data), mimetype="application/json")
    
   
@login_required
@csrf_exempt
def add_update(request, *args):

    organization_id = request.POST.get('organization_id', None)
    project_id = request.POST.get('project_id', None)
    opportunity_id = request.POST.get('opportunity_id', None)
    update_text = request.POST.get('update_text', None)
    
    # TODO:  error checking.  i.e. does user have permission?
    update = Update.objects.create(organization_id=organization_id, project_id=project_id,
                                   opportunity_id=opportunity_id, text=update_text, created_by=request.user)
    
    response_data = { "success": "true" }

    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@csrf_exempt
def login_user(request):

    username = request.REQUEST.get('username')
    password = request.REQUEST.get('password')

    user = authenticate(username=username, password=password)
    
    if user is not None:

      if user.is_active:

            login(request, user)
            return HttpResponse(json.dumps({ 'success': True,}), content_type="application/json")
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
