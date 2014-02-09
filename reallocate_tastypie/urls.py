from django.conf.urls import patterns, include, url
from tastypie.api import Api

from reallocate_tastypie.api import (OrganizationResource,
                                     ProjectResource,
                                     UserResource,
                                     OpportunityResource,
                                     UserProfileResource,
                                     UpdateResource,
                                     OpportunityEngagementResource)


v1_api = Api(api_name='v1')
map(lambda Resource: v1_api.register(Resource()),
    [OrganizationResource,
     ProjectResource,
     UserResource,
     OpportunityResource,
     UserProfileResource,
     UpdateResource,
     OpportunityEngagementResource]
)

urlpatterns = patterns(
    '',
    (r'',include(v1_api.urls))
)
