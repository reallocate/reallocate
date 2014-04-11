import logging

from website.models import *

class Project(Project):

	def save(self, *args, **kwargs):

		logging.error(self)

		super(Project, self).save(*args, **kwargs)