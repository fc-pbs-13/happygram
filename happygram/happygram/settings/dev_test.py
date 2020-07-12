from .base import *

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'
