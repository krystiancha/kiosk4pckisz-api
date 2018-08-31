import django_heroku

# noinspection PyUnresolvedReferences
from .base import *

DEBUG = False

django_heroku.settings(locals())
