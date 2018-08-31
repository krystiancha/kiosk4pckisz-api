from .base import *

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'kbhrgn0mbif08om8!%et^xy6ffy7fik+8_o)4b-u-%!1!s(8i6'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Database
# https://docs.djangoproject.com/en/2.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
