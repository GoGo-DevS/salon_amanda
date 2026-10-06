from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-salon-amanda-dev-change-in-production-abc123xyz'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

# Las fotos que Sergio sube desde su panel (las promociones) viven aca.
# R2 gana sobre Cloudinary: Cloudinary cobra por SERVIR, asi que la cuenta se
# agota justo cuando al cliente le va bien -- ya paso dos veces y el 20-08 dejo
# a Punto Parcelas sin una sola foto. R2 no cobra egreso nunca.
R2_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME', '')
R2_ACCOUNT_ID = os.environ.get('R2_ACCOUNT_ID', '')
R2_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID', '')
R2_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY', '')
R2_PUBLIC_DOMAIN = os.environ.get('R2_PUBLIC_DOMAIN', '')

# Se exigen las CUATRO, no solo el bucket. Con el bucket puesto y el account id
# vacio el endpoint queda en "https://.r2.cloudflarestorage.com" y boto3 revienta
# al primer archivo que toque: el sitio entero cae con 502 y el motivo no aparece
# en ninguna parte. Faltando alguna se cae a Cloudinary o a disco, que es
# degradarse y no morir.
USAR_R2 = bool(R2_BUCKET_NAME and R2_ACCOUNT_ID and R2_ACCESS_KEY_ID and R2_SECRET_ACCESS_KEY)

CLOUDINARY_URL = os.environ.get('CLOUDINARY_URL', '')

# Google Analytics 4. VACIO = no se carga nada, ni una peticion a Google.
# Solo lo hereda core/templates/core/base.html. El panel tiene plantilla propia
# A PROPOSITO: ahi se ven los datos de las clientas, y no van a Google.
GA4_MEASUREMENT_ID = os.environ.get('GA4_MEASUREMENT_ID', '').strip()
if CLOUDINARY_URL:
    import cloudinary
    cloudinary.config(cloudinary_url=CLOUDINARY_URL)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    *(["storages"] if USAR_R2 else []),
    *(["cloudinary_storage", "cloudinary"] if CLOUDINARY_URL and not USAR_R2 else []),
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.promocion_activa',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Con SQLite dentro del contenedor, en Render free TODO lo que Sergio carga
# desde su panel se borra en el siguiente despliegue: el contenedor se recrea y
# el archivo se va con el. Por eso las promociones nunca duraron.
#
# conn_max_age=0 NO es un descuido: Neon no suspende mientras haya una conexion
# abierta, asi que con 600 la conexion se renueva antes de expirar y el reloj no
# para nunca -- a Punto Parcelas le facturaba 24 horas por dia y llego al 80%
# del plan gratis. Con 0 se reabre en cada request y el pooler absorbe el costo.
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=0)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-cl'
TIME_ZONE = 'America/Santiago'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

_storages: dict = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
if USAR_R2:
    AWS_ACCESS_KEY_ID = R2_ACCESS_KEY_ID
    AWS_SECRET_ACCESS_KEY = R2_SECRET_ACCESS_KEY
    AWS_STORAGE_BUCKET_NAME = R2_BUCKET_NAME
    AWS_S3_ENDPOINT_URL = f'https://{R2_ACCOUNT_ID}.r2.cloudflarestorage.com'
    AWS_S3_CUSTOM_DOMAIN = R2_PUBLIC_DOMAIN  # pub-xxxx.r2.dev, SIN https://
    AWS_S3_REGION_NAME = 'auto'
    AWS_DEFAULT_ACL = None
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    _storages["default"] = {"BACKEND": "storages.backends.s3.S3Storage"}
elif CLOUDINARY_URL:
    _storages["default"] = {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    }
STORAGES = _storages

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
