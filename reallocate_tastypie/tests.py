from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client
from tastypie.test import ResourceTestCase,TestApiClient

from reallocate_tastypie.api import (OrganizationResource,
                                     ProjectResource,
                                     OpportunityResource,
                                     UserProfileResource,
                                     UpdateResource,
                                     OpportunityEngagementResource,
                                     UserResource)

class TestAPI(ResourceTestCase):
    '''
    There are 3 clients making queries on the API endpoints:
    api_client - authenticated user accessing its own models
    hacker_client - authenticated user accessing models it doesn't own
    noauth_client - non-authenticated user
    '''

    fixtures = ["test_auth.json","test_website.json"]

    def setUp(self):
        self.user = User.objects.all()[0]
        self.api_client = TestApiClient()
        self.api_client.client.login(username="test",password="test")

        self.hacker_client = TestApiClient()
        self.hacker_client.client.login(username="hacker",password="password")

        self.noauth_client = TestApiClient()

    def _generate_detail_endpoint(self, resource_name, pk):
        '''helper method to generate tastypie detail_endpoint'''

        detail_kwargs = {
            "resource_name": resource_name,
            "api_name": "v1",
            "pk": pk
        }
        detail_endpoint = reverse("api_dispatch_detail",kwargs=detail_kwargs)

        return detail_endpoint

    def _generate_list_endpoint(self, resource_name):
        '''helper method to generate tastypie list_endpoint'''

        list_kwargs = {
            "resource_name":resource_name,
            "api_name":"v1"
        }
        list_endpoint = reverse("api_dispatch_list",kwargs=list_kwargs)

        return list_endpoint

    ###
    # Read
    ###

    def _test_read(self,resource_name,pk):
        '''
        Test read assumes that both hacker_client and api_client
        have read access to the resource.
        '''
        list_endpoint = self._generate_list_endpoint(resource_name)
        detail_endpoint = self._generate_detail_endpoint(resource_name,pk)


        self.assertHttpOK(self.api_client.get(detail_endpoint))
        self.assertHttpOK(self.api_client.get(list_endpoint))
        self.assertHttpOK(self.hacker_client.get(detail_endpoint))
        self.assertHttpOK(self.hacker_client.get(list_endpoint))
        self.assertHttpOK(self.noauth_client.get(detail_endpoint))
        self.assertHttpOK(self.noauth_client.get(list_endpoint))

    def test_read_organization(self):
        self._test_read(OrganizationResource._meta.resource_name,1)

    def test_read_project(self):
        self._test_read(ProjectResource._meta.resource_name,1)

    def test_read_opportunity(self):
        self._test_read(OpportunityResource._meta.resource_name,1)

    def test_read_userprofile(self):
        self._test_read(UserProfileResource._meta.resource_name,1)

    def test_read_update(self):
        self._test_read(UpdateResource._meta.resource_name,1)

    def test_read_opportunityengagement(self):
        self._test_read(OpportunityEngagementResource._meta.resource_name,1)

    def test_read_user(self):
        self._test_read(UserResource._meta.resource_name,1)

    ###
    # Update
    ###

    def _test_update(self,resource_name,pk,update={}):
        '''
        Test update assumes that only api_client has privilege to update the resource
        hacker_client and noauth_client should get an unauthorized response
        '''

        detail_endpoint = self._generate_detail_endpoint(resource_name,pk)


        self.assertHttpAccepted(self.api_client.put(detail_endpoint,data=update))
        self.assertHttpUnauthorized(self.hacker_client.put(detail_endpoint,data=update))
        self.assertHttpUnauthorized(self.noauth_client.put(detail_endpoint,data=update))

    def test_update_organization(self):
        self._test_update(OrganizationResource._meta.resource_name,1,{"name":"neworg"})

    def test_update_project(self):
        self._test_update(ProjectResource._meta.resource_name,1,{"name":"newproj"})

    def test_update_opportunity(self):
        self._test_update(OpportunityResource._meta.resource_name,1,{"name":"newopp"})

    def test_update_userprofile(self):
        self._test_update(UserProfileResource._meta.resource_name,1,{"bio":"newbio"})

    def test_update_update(self):
        self._test_update(UpdateResource._meta.resource_name,1,{"text":"newtest"})

    def test_update_opportunityengagement(self):
        self._test_update(OpportunityEngagementResource._meta.resource_name,1,{"response":"newres"})

    def test_update_user(self):
        detail_endpoint = self._generate_detail_endpoint(UserResource._meta.resource_name,1)
        payload = {'username':'sdfsdf'}

        self.assertHttpUnauthorized(self.api_client.put(detail_endpoint,data=payload))
        self.assertHttpUnauthorized(self.noauth_client.put(detail_endpoint,data=payload))
        self.assertHttpUnauthorized(self.hacker_client.put(detail_endpoint,data=payload))


    ###
    # Create and Delete
    ###

    def _test_create_delete(self,resource_name,payload):
        '''
        Test that api_client can create resources and noauth_client can't.
        Test that hacker_client can't delete api_client data.
        All resources currently have 1 instance, so the created instance will have a pk of 2
        '''
        list_endpoint = self._generate_list_endpoint(resource_name)
        detail_endpoint = self._generate_detail_endpoint(resource_name,2)


        self.assertHttpCreated(self.api_client.post(list_endpoint,data=payload))
        self.assertHttpUnauthorized(self.noauth_client.post(list_endpoint,data=payload))
        self.assertHttpUnauthorized(self.noauth_client.delete(detail_endpoint))
        self.assertHttpUnauthorized(self.hacker_client.delete(detail_endpoint))
        self.assertHttpAccepted(self.api_client.delete(detail_endpoint))


    def test_create_delete_organization(self):
        created_by = self._generate_detail_endpoint(UserResource._meta.resource_name,1)
        payload = {
            "status": "Pending",
            "name": "test org",
            "URL": "http://example.org",
            "country": "US",
            "org_mission": "test",
            "phone": "9999999999",
            "created_by":created_by
        }

        self._test_create_delete(OrganizationResource._meta.resource_name,payload)

    def test_create_delete_project(self):
        created_by = self._generate_detail_endpoint(UserResource._meta.resource_name,1)
        organization = self._generate_detail_endpoint(OrganizationResource._meta.resource_name,1)
        payload = {
            "status": "Pending",
            "name": "test project",
            "short_desc": "teset",
            "created_by": created_by,
            "organization": organization,
            "description": "test"
        }

        self._test_create_delete(ProjectResource._meta.resource_name,payload)

    def test_create_delete_opportunity(self):
        created_by = self._generate_detail_endpoint(UserResource._meta.resource_name,1)
        organization = self._generate_detail_endpoint(OrganizationResource._meta.resource_name,1)
        project = self._generate_detail_endpoint(ProjectResource._meta.resource_name,1)
        payload = {
            "status": "Active",
            "opp_type": "Knowledge",
            "name": "test",
            "description": "test",
            "short_desc": "test",
            "created_by": created_by,
            "project": project,
            "featured": False,
            "organization": organization,
            "resources": "test",
        }

        self._test_create_delete(OpportunityResource._meta.resource_name,payload)

    def test_create_delete_update(self):
        created_by = self._generate_detail_endpoint(UserResource._meta.resource_name,1)
        organization = self._generate_detail_endpoint(OrganizationResource._meta.resource_name,1)
        project = self._generate_detail_endpoint(ProjectResource._meta.resource_name,1)
        opportunity = self._generate_detail_endpoint(OpportunityResource._meta.resource_name,1)
        payload = {
            "organization": organization,
            "project": project,
            "opportunity": opportunity,
            "text": "test",
            "created_by": created_by
        }

        self._test_create_delete(UpdateResource._meta.resource_name,payload)

    def test_create_delete_userprofile(self):
        user = self._generate_detail_endpoint(UserResource._meta.resource_name,1)
        organization = self._generate_detail_endpoint(OrganizationResource._meta.resource_name,1)
        payload = {
            "organization": organization,
            "user": user
        }

        list_endpoint = self._generate_list_endpoint(UserProfileResource._meta.resource_name)
        detail_endpoint = self._generate_detail_endpoint(UserProfileResource._meta.resource_name,1)

        self.assertHttpUnauthorized(self.api_client.post(list_endpoint,data=payload))
        self.assertHttpUnauthorized(self.noauth_client.post(list_endpoint,data=payload))

        self.assertHttpUnauthorized(self.api_client.delete(detail_endpoint))
        self.assertHttpUnauthorized(self.hacker_client.delete(detail_endpoint))
        self.assertHttpUnauthorized(self.noauth_client.delete(detail_endpoint))

    def test_create_delete_user(self):
        list_endpoint = self._generate_list_endpoint(UserResource._meta.resource_name)
        detail_endpoint = self._generate_detail_endpoint(UserResource._meta.resource_name,1)
        payload = {}

        self.assertHttpUnauthorized(self.api_client.post(list_endpoint,data=payload))
        self.assertHttpUnauthorized(self.hacker_client.post(list_endpoint,data=payload))
        self.assertHttpUnauthorized(self.noauth_client.post(list_endpoint,data=payload))

        self.assertHttpUnauthorized(self.api_client.delete(detail_endpoint))
        self.assertHttpUnauthorized(self.hacker_client.delete(detail_endpoint))
        self.assertHttpUnauthorized(self.noauth_client.delete(detail_endpoint))

    def test_create_delete_opportunityengagement(self):
        user = self._generate_detail_endpoint(UserResource._meta.resource_name,1)
        project = self._generate_detail_endpoint(ProjectResource._meta.resource_name,1)
        opportunity = self._generate_detail_endpoint(OpportunityResource._meta.resource_name,1)
        payload = {
            "user": user,
            "opportunity": opportunity,
            "project": project,
            "status": "Pending",
            "response": "test"
        }

        self._test_create_delete(OpportunityEngagementResource._meta.resource_name,payload)
