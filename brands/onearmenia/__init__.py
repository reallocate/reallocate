import logging, re, os
import settings

class Middleware(object):

	def process_request(self, request):

		request.session['brand'] = settings.BRAND

		return

