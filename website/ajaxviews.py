from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
import json

from website.models import UserProfile, Project

@login_required
# this won't crash w/ login_required but redirect doesn't work on ajax call - TODO: fix rather than these hide links
def follow_project(request, *args):
    project_id = request.GET.get('project_id', '')
    try:
        my_profile = UserProfile.objects.get(user=request.user)
    except Exception, err:
        return HttpResponse(json.dumps({'failure': 'no user'}), status=500)
    try:
        project = Project.objects.get(pk=project_id)
    except Exception, err:
        return HttpResponse(json.dumps({'failure': 'no project found'}), status=500)
    my_profile.followed_projects.add(project)
    my_profile.save()
    response_data = { "success": "true" }
    return HttpResponse(json.dumps(response_data), mimetype="application/json")