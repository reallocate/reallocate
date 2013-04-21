from website.models import UserProfile
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from myproject.settings import FROM_EMAIL, ADMIN_EMAIL, DEPLOY_ENV
import re

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
        context['logged_in'] = True
        context['user_email'] = request.user.email
    context['topmsg'] = request.GET.get('topmsg')
    return context

def send_email_template(email_type, context, subject, recipients, *kwargs):
    html_content = render_to_string("emails/" + email_type + ".html", context)
    try:
        text_content = render_to_string("emails/" + email_type + ".txt", context)
    except: # for now - if we dont have the .txt, just strip the html render
        text_content = re.sub("<[^a].*?>", "", html_content)
    # TODO: check to see if recipient user acct wants this email type based on settings
    # or should this be done by the caller?
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