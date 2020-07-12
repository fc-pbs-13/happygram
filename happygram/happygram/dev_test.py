from .settings import *

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'

# base
# dev
# dev_test
# ci
# staging
# production