from tastypie.resources import ModelResource
from tastypie import fields
from tastypie.authorization import (Authorization,
                                    ReadOnlyAuthorization)
from tastypie.resources import ResourceOptions
from tastypie.exceptions import Unauthorized
from django.contrib.auth.models import User

from website.models import (Organization,
                            Project,
                            Opportunity,
                            UserProfile,
                            Update,
                            OpportunityEngagement)

##
#Authorizations
##

class ReallocateAuthorization(Authorization):
    '''
    By default, allow users to read and create all models.
    Users can only update / delete models if they are reference by 'owner_field'
    'owner_field' is required because the fields are not consistent with current models
    '''
    @property
    def owner_field(self):
        raise NotImplementedError("ReallocateAuthorization requires owner_field")

    def update_list(self, object_list, bundle):
        return filter(lambda obj: getattr(obj,self.owner_field) == bundle.request.user,
                      object_list)

    def update_detail(self, object_list, bundle):
        return getattr(bundle.obj,self.owner_field) == bundle.request.user

    def create_detail(self, object_list, bundle):
        return bundle.request.user.is_authenticated()

    def create_list(self, object_list, bundle):
        return object_list if bundle.request.user.is_authenticated() else []

    def delete_list(self, object_list, bundle):
        return filter(lambda obj: getattr(obj,self.owner_field) == bundle.request.user,
                      object_list)

    def delete_detail(self, object_list, bundle):
        return getattr(bundle.obj,self.owner_field) == bundle.request.user

class OrganizationAuthorization(ReallocateAuthorization):
    @property
    def owner_field(self):
        return "created_by"

class ProjectAuthorization(ReallocateAuthorization):
    @property
    def owner_field(self):
        return "created_by"

class OpportunityAuthorization(ReallocateAuthorization):
    @property
    def owner_field(self):
        return "created_by"

class UpdateAuthorization(ReallocateAuthorization):
    @property
    def owner_field(self):
        return "created_by"

class OpportunityEngagementAuthorization(ReallocateAuthorization):
    @property
    def owner_field(self):
        return "user"

class UserProfileAuthorization(ReallocateAuthorization):
    @property
    def owner_field(self):
        return "user"

    def create_detail(self,object_list,bundle):
        raise Unauthorized("Don't allow users create user profiles")

    def create_list(self,object_list,bundle):
        raise Unauthorized("Don't allow users create user profiles")

    def delete_detail(self,object_list,bundle):
        raise Unauthorized("Don't allow users delete user profiles")

    def delete_list(self,object_list,bundle):
        raise Unauthorized("Don't allow users delete user profiles")

##
#Resources
##

class UserResource(ModelResource):
    class Meta(ResourceOptions):
        queryset = User.objects.all()
        resource_name = "user"
        authorization = ReadOnlyAuthorization()
        #limit access to user information.
        #Since user is really only for authentication, users should require
        #specific user information. If they do, it should be in UserProfile
        fields = ["username"]

class UserProfileResource(ModelResource):
    user = fields.ForeignKey(UserResource,'user')

    class Meta(ResourceOptions):
        queryset = UserProfile.objects.all()
        resource_name = "userprofile"
        authorization = UserProfileAuthorization()

class OrganizationResource(ModelResource):
    created_by = fields.ForeignKey(UserResource,'created_by')

    class Meta(ResourceOptions):
        queryset = Organization.objects.all()
        resource_name = "organization"
        authorization = OrganizationAuthorization()

class ProjectResource(ModelResource):
    organization = fields.ForeignKey(OrganizationResource,'organization')
    created_by = fields.ForeignKey(UserResource,'created_by')

    class Meta(ResourceOptions):
        queryset = Project.objects.all()
        resource_name = "project"
        authorization = ProjectAuthorization()

class OpportunityResource(ModelResource):
    project = fields.ForeignKey(ProjectResource,'project')
    organization = fields.ForeignKey(OrganizationResource,'organization')
    created_by = fields.ForeignKey(UserResource,'created_by')

    class Meta(ResourceOptions):
        queryset = Opportunity.objects.all()
        resource_name = "opportunity"
        authorization = OpportunityAuthorization()

class UpdateResource(ModelResource):
    opportunity = fields.ForeignKey(OpportunityResource,'opportunity')
    project = fields.ForeignKey(ProjectResource,'project')
    organization = fields.ForeignKey(OrganizationResource,'organization')
    created_by = fields.ForeignKey(UserResource,'created_by')

    class Meta(ResourceOptions):
        queryset = Update.objects.all()
        resource_name = "update"
        authorization = UpdateAuthorization()

class OpportunityEngagementResource(ModelResource):
    opportunity = fields.ForeignKey(OpportunityResource,'opportunity')
    project = fields.ForeignKey(ProjectResource,'project')
    user = fields.ForeignKey(UserResource,'user')

    class Meta(ResourceOptions):
        queryset = OpportunityEngagement.objects.all()
        resource_name = "opportunityengagement"
        authorization = OpportunityEngagementAuthorization()
