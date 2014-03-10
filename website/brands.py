import settings, logging, re

class Freespace(object):

	def process_request(self, request):

		if re.search(r'freespace', request.META['HTTP_HOST']):

			settings.BRAND = 'freespace'

