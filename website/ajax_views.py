import base, json, logging
import hashlib, time

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response, get_object_or_404
from django.core.serializers import serialize

import website.base as base
from website.settings import ADMIN_EMAIL
from website.models import UserProfile, Project, ProjectForm, Update, Organization, Opportunity, OpportunityEngagement
from website.models import STATUS_ACTIVE, STATUS_CHOICES, STATUS_INACTIVE, STATUS_CLOSED, CAUSES, COUNTRIES


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
        message = request.REQUEST.get('message')

        opp_eng = OpportunityEngagement(user=request.user, opportunity=opp, project_id=pid)
        opp_eng.response = response

        opp_eng.save()

        subject = "New engagement with %s by %s" % (opp.name, request.user.email)
        html_content = """%s<br/><br/>
            <a href='%s/admin/website/opportunityengagement/%s'>approve</a>""" % (
            message, request.get_host(), opp_eng.id)
                       
        # TODO: send to project/opp owner as well as admin
        base.send_admin_email(subject, html_content, html_content=html_content)

        response['message'] = "Thanks for your request. A project leader will get back to you as soon as possible."

    else:

        response['message'] = "No project or opportunity id."
    
    return HttpResponse(json.dumps(response), mimetype="application/json")

@csrf_exempt
@login_required
def close_opportunity(request):
    context = base.build_base_context(request)
    pid = request.REQUEST.get('projectId')
    oid = request.REQUEST.get('opportunityId')
    response = {}

    if pid and oid:
        #close opportunity engagements
        for opp_eng in OpportunityEngagement.objects.filter(opportunity__id__exact=oid):
            opp_eng.status = STATUS_CLOSED
            opp_eng.save()

        #close Opportunity
        opp = get_object_or_404(Opportunity, pk=oid)
        opp.status = STATUS_CLOSED
        opp.save()

        #add final update about closing
        message = request.REQUEST.get('message')
        update = Update.objects.create(organization_id=opp.organization_id, project_id=pid, media_url="",
                                   opportunity_id=oid, text=message, created_by=request.user)
        update.save()

        #TODO eoj Add admin_completed_opportunity_email.html template and user_completed_opportunity_email.html for kyle
        #instead of doing this inline here.

        #now notify everyone involve about the close
        subject = "Opportunity,  %s, closed by %s" % (opp.name, request.user.email)
        html_content = """%s<br/><br/>opportunity_id:%s""" % (
            message, oid)

        #email site admin
        base.send_admin_email(subject, html_content, html_content=html_content)

        #email project owner and engaged users
        emails = []
        emails.append(opp.created_by.email)
        for engaged_user in opp.engaged_by.all():
            emails.append(engaged_user.email)
        base.send_email(emails, subject, html_content, html_content)

        response['message'] = "Opportunity was successfully closed."
    else:
        response['message'] = "Opportunity was not closed. Missing project or opportunity id."
    return HttpResponse(json.dumps(response), mimetype="application/json")


@login_required
@csrf_exempt
def add_update(request, *args):

    orgid = request.REQUEST.get('orgid')
    pid = request.REQUEST.get('pid')
    oid = request.REQUEST.get('oid')
    text = request.REQUEST.get('text')
    url = None

    if request.body:

        mime_type = request.META.get('HTTP_X_MIME_TYPE')
    
        # TODO: check mimetype for proper file extensions
        # TODO: create create_s3_media_url() on update object, then move this code below object creation
        ext = 'png'
        hash = hashlib.sha1()
        hash.update(str(time.time()))
        filename = hash.hexdigest()[:10]
        
        url = base.send_to_remote_storage(request.body, 'project/%s/%s.%s' % (pid, filename, ext), mime_type)

    # TODO:  error checking.  i.e. does user have permission?
    update = Update.objects.create(organization_id=orgid, project_id=pid, media_url=url,
                                   opportunity_id=oid, text=text, created_by=request.user)

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


@login_required
@csrf_exempt
def delete_opportunity(request, *args):

    if request.POST:

        opportunity = Opportunity.objects.get(id=request.POST.get('opportunityId'))

        if opportunity:

            opportunity.delete()
    
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
        response_data = False if q else True

    elif email:

        q = User.objects.filter(email=email)
        response_data = False if q else True

    else:

        response_data = ''


    return HttpResponse(json.dumps(response_data), mimetype="application/json")


def get_orgs(request, *args):

    orgs = Organization.objects.all()
    orgs = [org.name for org in orgs]

    return HttpResponse(json.dumps(orgs))


def check_org_name(request, *args):

    name = request.REQUEST.get('name')

    if name:

        q = Organization.objects.filter(name=name)
        response_data = False if q else True

    else:

        response_data = ''


    return HttpResponse(json.dumps(response_data), mimetype="application/json")

