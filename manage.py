#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

	if os.environ.get('COBRAND'):
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cobrands." + os.environ['COBRAND'] + ".settings")
	else:
		os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")

	from django.core.management import execute_from_command_line

	execute_from_command_line(sys.argv)
