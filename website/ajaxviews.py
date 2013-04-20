from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
import json
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
        base.send_email([ADMIN_EMAIL, project.created_by.email],
            'new follower: %s for project: %s' % (request.user.email, project.name), '')
    if action == 'unfollow':
        project.followed_by.remove(request.user)
    print project.followed_by.all()
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