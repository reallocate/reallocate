from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import json
import website.base as base
from myproject.settings import ADMIN_EMAIL

from website.models import UserProfile, Project

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
        base.send_email([ADMIN_EMAIL, project.created_by.email],
            'new follower: %s for project: %s' % (request.user.email, project.name), '')
    if action == 'unfollow':
        project.followed_by.remove(request.user)
    print project.followed_by.all()
    project.save()
    response_data = { "success": "true" }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")


@csrf_exempt
def add_update(request, *args):
    

    project_id = request.GET.get('project_id', None)
    action = request.GET.get('action', '')
    my_profile = base.get_current_userprofile(request)
    try:
        project = Project.objects.get(pk=project_id)
    except Exception, err:
        return HttpResponse(json.dumps({'failure': 'no project found'}), status=500)
    if action == 'follow':
        my_profile.followed_projects.add(project)
    if action == 'unfollow':
        my_profile.followed_projects.remove(project)
    my_profile.save()
    response_data = { "success": "true" }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")