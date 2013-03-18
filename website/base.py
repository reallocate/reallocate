from website.models import UserProfile
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail

def get_current_userprofile(request):
    try:
        return UserProfile.objects.get(user=request.user)
    except Exception, err:
        raise err
        if request.is_ajax():
            return HttpResponse(json.dumps({'failure': 'no user'}), status=500)
        return HttpResponse("error getting user profile")

def build_base_context(request):
    model = {}
    if request.user.is_authenticated():
        model['logged_in'] = True
        model['user_email'] = request.user.email
    model['topmsg'] = request.GET.get('topmsg')
    return model

#def notify_users(project):

