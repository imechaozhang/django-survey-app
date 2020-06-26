import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
# DO NOT use this one for production!
SECRET_KEY = '65y!t!=p%8wa674m-34p1v#!t!@45i!k85c1zz+w%+hv3jco)j'


# Uncomment the following DATABASES block to use sqlite3

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Uncomment the following DATABASES block to use mySQL
# Remember to also create the my.cnf file and set your connection string there

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'OPTIONS': {
#             'read_default_file': os.path.join(BASE_DIR, 'my.cnf'),
#             'charset': 'utf8mb4'
#         },
#     }
# }
