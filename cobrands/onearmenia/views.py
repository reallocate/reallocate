import logging, hashlib, random
import boto
import re, sys, os
import json
import stripe

from boto.s3.key import Key

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.db.models import Q
from django.utils.http import urlquote

import settings

from models import OrganizationForm, Organization, ProjectForm, Project, Update, UserProfile
from models import OpportunityEngagement, Opportunity, OpportunityForm
from models import STATUS_ACTIVE, STATUS_CHOICES, STATUS_INACTIVE, STATUS_CLOSED, CAUSES, COUNTRIES


@login_required
def new_project(request):

    # Show the sign page and collect emails
    context = {}
    context['causes'] = CAUSES

    allow_sponsorship = True

    org = Organization.objects.get(id=request.GET.get('org'))
    context['organization'] = org

    if request.method == "POST":

        project_form = ProjectForm(request.POST)
        project = project_form.save(commit=False)

        if project_form.is_valid():

            project.organization = request.user.get_profile().organization
            project.created_by = request.user

            project.save()

            if allow_sponsorship:

                project.create_sponsorship()
            
            # this has to occur after initial save b/c we use pk id as part of the s3 filepath
            media_file = request.FILES.get('file')
            if media_file:
                project.media_url = base.send_to_remote_storage(media_file, project.make_s3_media_url(media_file), "image/png")
                project.save()
            
            # send admin email with link adminpanel to change project status
            created_by = project.created_by.first_name + ' ' + project.created_by.last_name
            subj = "[%s] A new project submission" % request.get_host()
            body = """
                A new project has been submitted by %s:<br /><br />
                <b>%s</b><br /><br />
                %s<br /><br />
                <a href='%s'>View this project</a><br />
                """ % (created_by, project.name, project.short_desc, project.get_url(request))

            base.send_admin_email(subj, body, html_content=body)

            return HttpResponseRedirect('/project/%s/opportunity/add' % project.id)

        else:

            return HttpResponse("error")

    else:

        return render(request, 'new_project.html', context)

