import base, json, logging
import hashlib, time

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login
from django.shortcuts import render_to_response, get_object_or_404
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder

import website.base as base
from website.settings import ADMIN_EMAIL
from website.models import UserProfile, Project, ProjectForm, Update, Organization, Opportunity, OpportunityEngagement
from website.models import STATUS_ACTIVE, STATUS_CHOICES, STATUS_INACTIVE, STATUS_CLOSED, CAUSES, COUNTRIES


def projects(request, *args):

    projects = Project.objects.filter(status__iexact='Active', sites__id=settings.SITE_ID)

    if request.method == 'GET': 

        search = request.GET.get("q")

        MAX_RESULTS = 50

        if search:

            projects = projects.filter(Q(tags__contains=search) | Q(name__contains=search) | Q(short_desc__contains=search) | Q(description__contains=search)).distinct()

    results = serialize('json', projects)

    return HttpResponse(results, content_type='application/json')


@csrf_exempt
def modify_project_relation(request, *args):

    # action = [follow, unfollow]
    project_id = request.GET.get('project_id', '')
    action = request.GET.get('action', '')

    try:
        project = Project.objects.get(pk=project_id)

    except Exception, error:

        return HttpResponse(json.dumps({"success": False, "message": "Invalid project ID"}), status=500)

    if action == 'follow':

        project.followed_by.add(request.user)
        #base.send_email([ADMIN_EMAIL, project.created_by.email],
        #    'new follower: %s for project: %s' % (request.user.email, project.name), '')

    if action == 'unfollow':

        project.followed_by.remove(request.user)

    project.save()

    response = { "success": True }

    return HttpResponse(json.dumps(response), mimetype="application/json")
  

@csrf_exempt
def change_project(request, *args):

    if request.user.is_staff:

        project_id = request.REQUEST.get('id', '')

        try:
            project = Project.objects.get(pk=project_id)

        except Exception, error:

            return HttpResponse(json.dumps({'success': False, 'message': 'Invalid project ID'}), status=500)

        if request.REQUEST.get('action') == 'approve' or request.REQUEST.get('action') == 'open':

            project.status = 'Active'
            project.save()

            subject = "Your ReAllocate project has been approved!"
            html_content = "Congratulations, your project &quot;%s&quot; has been reviewed and approved." % project.name
            html_content = html_content + "<br><br>This project is now live and can be viewed at <a href='%s'>%s</a>.<br>" % (project.get_url(request), project.get_url(request))

            base.send_email(project.created_by.email, subject, html_content, html_content=html_content)

            response = { "success": True }

        elif request.REQUEST.get('action') == 'close':

            project.status = 'Closed'
            project.save()

            response = { "success": True }

        elif request.REQUEST.get('action') == 'delete':

            project.delete()

            response = { "success": True }


        return HttpResponse(json.dumps(response), mimetype="application/json")

    else:

        return HttpResponse(json.dumps({'success': False, 'message': 'Insufficient priviledges'}), mimetype="application/json")



@csrf_exempt
@login_required
def engage_opportunity(request):

    context = {}

    pid = request.REQUEST.get('projectId')
    oid = request.REQUEST.get('opportunityId')
    response = {}

    if pid and oid:

        opp = get_object_or_404(Opportunity, pk=oid)
        message = request.REQUEST.get('message')
        link = request.REQUEST.get('link')

        if link:
            message += '<br /></br />%s' % link

        if OpportunityEngagement.objects.filter(user=request.user, opportunity=opp, project_id=pid):

            response['message'] = "You are already engaged with this opportunity."

        else:

            opp_eng = OpportunityEngagement(user=request.user, opportunity=opp, project_id=pid)
            opp_eng.response = response

            opp_eng.save()

            subject = "New engagement with %s by %s" % (opp.name, request.user.email)
            html_content = "&quot;%s&quot;<br/><br/>%s" % (message, opp.project.name)
            html_content = html_content + " / <a href='http://%s/project/%s/opportunity/%s'>%s</a><br /><br />" % (request.get_host(), opp.project.id, opp.id, opp.name)
            html_content = html_content + "<a href='http://%s/admin/website/opportunityengagement/%s'>approve</a>""" % (request.get_host(), opp_eng.id)
                           
            base.send_email(opp.project.created_by.email, subject, html_content, html_content=html_content)
            base.send_admin_email(subject, html_content, html_content=html_content)

            response['message'] = "Thanks for your request. A project lead will get back to you as soon as possible."

    else:

        response['message'] = "No project or opportunity id."
    
    return HttpResponse(json.dumps(response), mimetype="application/json")


@csrf_exempt
@login_required
def close_opportunity(request):

    pid = request.REQUEST.get('projectId')
    oid = request.REQUEST.get('opportunityId')
    response = {}

    if pid and oid:

        # close opportunity engagements
        for opp_eng in OpportunityEngagement.objects.filter(opportunity__id__exact=oid):
            opp_eng.status = STATUS_CLOSED
            opp_eng.save()

        #close Opportunity
        opp = get_object_or_404(Opportunity, pk=oid)
        opp.status = STATUS_CLOSED
        opp.save()

        # add final update about closing
        message = request.REQUEST.get('message')
        update = Update.objects.create(organization_id=opp.organization_id, project_id=pid, media_url="",
                                   opportunity_id=oid, text=message, created_by=request.user)
        update.save()

        #now notify everyone involve about the close
        subject = "Opportunity,  %s, closed by %s" % (opp.name, request.user.email)

        # context here only used by email template(s), so add the variables that your template will need.
        context = {}
        context['opportunity_name'] = opp.name
        context['project_name'] = opp.project.name
        context['message'] = message

        #email site admin
        base.send_email_template(request, "closed_opportunity_admin", context, subject, [ADMIN_EMAIL])

        #email project admin
        base.send_email_template(request, "closed_opportunity_admin", context, subject, [opp.created_by.email])

        #email engaged users
        for engaged_user in opp.engaged_by.all():
            context['user'] = engaged_user
            base.send_email_template(request, "closed_opportunity_user", context, subject, [engaged_user.email])

        response['message'] = "Opportunity was successfully closed."
    else:
        response['message'] = "Opportunity was not closed. Missing project or opportunity id."

    return HttpResponse(json.dumps(response), mimetype="application/json")


@login_required
@csrf_exempt
def add_update(request, *args):

    if request.REQUEST.get('id'):

        update = Update.objects.get(id=request.REQUEST['id'])
        orgid = update.organization.id if update.organization else None
        pid = update.project.id if update.project else None
        oid = update.opportunity.id if update.opportunity else None

    else:

        update = None
        orgid = request.REQUEST.get('orgid')
        pid = request.REQUEST.get('pid')
        oid = request.REQUEST.get('oid')

    text = request.REQUEST.get('text')
    url = None
    response = {"success": "true"}

    project = Project.objects.get(id=pid)

    # handle file upload
    if request.body:

        mime_type = request.META.get('HTTP_X_MIME_TYPE')
    
        # TODO: check mimetype for proper file extensions
        # TODO: create create_s3_media_url() on update object, then move this code below object creation
        ext = 'png'
        hash = hashlib.sha1()
        hash.update(str(time.time()))
        filename = hash.hexdigest()[:10]
        
        url = base.send_to_remote_storage(request.body, 'project/%s/%s.%s' % (pid, filename, ext), mime_type)

    # edit previous post
    if update:

        if update.created_by == request.user or project.created_by == request.user:

            if text:
                update.text = text
            if url:
                update.media_url = url

            update.save()

        else:

            response.update({'success':False, 'message': "You don't have permission to edit this post."})

    # create new post
    elif (oid and OpportunityEngagement.objects.get(opportunity_id=oid, user=request.user)) or project.created_by == request.user:

        Update.objects.create(organization_id=orgid, opportunity_id=oid, project_id=pid, text=text, created_by=request.user, media_url=url)
        
    else:

        response.update({'success': False, 'message': 'Not a valid project id'})


    return HttpResponse(json.dumps(response), mimetype="application/json")


@login_required
@csrf_exempt
def delete_update(request, *args):

    if request.POST:

        update = Update.objects.get(id=request.POST.get('updateId'))

        if update:

            update.delete()
    
            response_data = { "success": "true" }

        else:

            response_data = { "success": "false" } 

    else:

        response_data = { "sucess": "false" }

    return HttpResponse(json.dumps(response_data), mimetype="application/json")


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
@login_required
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

    email = request.REQUEST.get('email')
    password = request.REQUEST.get('password')

    user = authenticate(username=email, password=password)
    
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


def invite_users(request):

    if request.REQUEST:

        message = request.REQUEST.get('message')
        emails = request.REQUEST.get('emails').split(',')

        for email in emails:

            salt = '1nv1t3'
            hash = hashlib.md5(salt + email).hexdigest()
            link = 'http://beta.reallocate.org/sign-up?invite=%s' % hash

            subject = "You've been invited to join ReAllocate!"

            context = {}
            context.update({
                'email': email,
                'subject': subject,
                'link': link,
                'message': message
            })

            base.send_email_template(request, "invite-user", context, subject, email)


        #return render_to_response('emails/invite-user.html', context, context_instance=RequestContext(request))  
        return HttpResponse(json.dumps({ 'success': True, 'message': 'Invite(s) sent' }), content_type="application/json", status=200)

    else:

        return HttpResponse(json.dumps({ 'success': False, 'message': 'No data posted' }), content_type="application/json", status=403)


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

    orgs = []

    for org in Organization.objects.all():

        orgs.append({
            'id': org.id,
            'name': org.name,
            'phone': org.phone,
            'URL': org.URL,
            'country': org.country,
            'org_mission': org.org_mission
        })


    return HttpResponse(json.dumps(orgs))


def check_org_name(request, *args):

    name = request.REQUEST.get('name')

    if name:

        q = Organization.objects.filter(name=name)
        response_data = False if q else True

    else:

        response_data = ''


    return HttpResponse(json.dumps(response_data), mimetype="application/json")

