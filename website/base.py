from myproject import settings
import re
from website.models import UserProfile
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from myproject.settings import FROM_EMAIL, ADMIN_EMAIL, DEPLOY_ENV

import boto
from boto.s3.key import Key

def get_current_userprofile(request):
    try:
        return UserProfile.objects.get(user=request.user)
    except Exception, err:
        raise err
        if request.is_ajax():
            return HttpResponse(json.dumps({'failure': 'no user'}), status=500)
        return HttpResponse("error getting user profile")

def build_base_context(request):

    context = {}
    if request.user.is_authenticated():
        context['user'] = request.user

    context['topmsg'] = request.GET.get('topmsg')

    return context


def generate_base_email_context(request):
    # add email template variables needed among all emails
    return {'server_url': request.get_host(),
           'facebook_url': 'https://www.facebook.com/reallocate.org',
           'twitter_url': 'https://twitter.com/reallocate'}

def send_email_template(request, email_type, context, subject, recipients, render=False, *kwargs):
    context.update(generate_base_email_context(request))
    html_content = render_to_string("emails/" + email_type + ".html", context)
    try:
        text_content = render_to_string("emails/" + email_type + ".txt", context)
    except: # for now - if we dont have the .txt, just strip the html render
        text_content = re.sub("<[^a].*?>", "", html_content)
    # TODO: check to see if recipient user acct wants this email type based on settings
    # or should this be done by the caller?
    if render:
        return html_content, text_content
    send_email(recipients, subject, text_content, html_content=html_content, *kwargs)

def send_email(recipients, subject, text_content, html_content=None, from_email=FROM_EMAIL, headers=None):
    # https://docs.djangoproject.com/en/dev/topics/email/
    if not isinstance(recipients, list):
        recipients = recipients.split(",")
    print "sending email to: %s with subj:%s and body:%s" % (", ".join(recipients), subject, text_content[:500])
    # TODO: make sure we don't send real email to recipients if not production
    msg = EmailMultiAlternatives(subject, text_content, from_email, recipients, headers=headers)
    if html_content:
        msg.attach_alternative(html_content, "text/html")
        msg.content_subtype = "html" # defaults to show as html, txt if html not viewable
    if DEPLOY_ENV != 'local':
        msg.send()

def send_admin_email(subject, text_content, html_content=None):
    send_email([ADMIN_EMAIL], "admin: " + subject, text_content, html_content=html_content)
    

def remote_storage(uploaded_file, filename, mime_type):
    """ for uploading images to S3 """
    c = boto.connect_s3(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = c.get_bucket(settings.S3_BUCKET)
    
    k = Key(bucket)
    k.set_metadata('Content-Type', mime_type)
    k.key = filename
    k.set_contents_from_string(uploaded_file)
    k.set_acl('public-read')
    return 'http://s3.amazonaws.com/%s/%s' % (settings.S3_BUCKET, filename)