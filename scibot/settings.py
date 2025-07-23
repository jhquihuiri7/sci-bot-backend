# -*- coding: utf-8 -*-

"""
Configuración de Django para el proyecto scibot.

Para más información sobre este archivo, consulta:
https://docs.djangoproject.com/en/5.2/topics/settings/

Para la lista completa de configuraciones y sus valores, consulta:
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
from dotenv import load_dotenv  # Para cargar variables de entorno desde un archivo .env.
import os

# --- Configuración de Rutas y Variables de Entorno ---

# Directorio base del proyecto (un nivel arriba de este archivo).
BASE_DIR = Path(__file__).resolve().parent.parent
# Carga las variables desde el archivo .env en el entorno.
load_dotenv()

# --- Configuraciones de Seguridad y Desarrollo ---

# ¡ADVERTENCIA DE SEGURIDAD! No uses esta clave secreta en producción.
# Es crucial para la seguridad criptográfica de Django.
SECRET_KEY = 'django-insecure-_13^gf@(9v57mvyj)6fms69liv0hmf4nrp6#dimwn8f32=b)8u'

# Tokens para los servicios de modelos de IA, cargados desde variables de entorno.
MODEL_TOKEN = os.getenv("modeltoken")
OPEN_TOKEN = os.getenv("opentoken")

# ¡ADVERTENCIA DE SEGURIDAD! No ejecutes la aplicación con DEBUG activado en producción.
# DEBUG = True muestra páginas de error detalladas. Cambiar a False para producción.
DEBUG = True

# Hosts/dominios permitidos para servir esta aplicación. '*' es inseguro y solo para desarrollo.
ALLOWED_HOSTS = ["*"]

# No añade una barra (/) al final de las URLs.
APPEND_SLASH = False

# --- Definición de Aplicaciones ---

# Lista de todas las aplicaciones de Django que están activadas en este proyecto.
INSTALLED_APPS = [
    'django.contrib.admin',       # Interfaz de administración.
    'django.contrib.auth',        # Framework de autenticación.
    'django.contrib.contenttypes',# Framework para tipos de contenido.
    'django.contrib.sessions',    # Framework de sesiones.
    'django.contrib.messages',    # Framework de mensajería.
    'django.contrib.staticfiles', # Framework para manejar archivos estáticos.
    'pdf.apps.PdfConfig',         # La aplicación personalizada 'pdf'.
]

# --- Middleware ---

# Lista de "hooks" en el procesamiento de solicitudes/respuestas de Django.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware', # Desactivado para las vistas con @csrf_exempt.
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- Configuración de URLs y Plantillas ---

# Archivo principal de configuración de URLs del proyecto.
ROOT_URLCONF = 'scibot.urls'

# Configuración del sistema de plantillas de Django.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # Directorios adicionales para buscar plantillas.
        'APP_DIRS': True, # Busca plantillas dentro de los directorios de las aplicaciones.
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# --- Configuración de WSGI ---

# Punto de entrada para servidores web compatibles con WSGI.
WSGI_APPLICATION = 'scibot.wsgi.application'


# --- Base de Datos ---
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# Las siguientes líneas imprimen las credenciales de la base de datos en la consola
# al iniciar la aplicación. Útil para depuración, pero se debe eliminar en producción.
print("user:", os.getenv("user"))
print("password:", os.getenv("password"))
print("host:", os.getenv("host"))
print("port:", os.getenv("port"))
print("dbname:", os.getenv("dbname"))

# Configuración de la base de datos. Utiliza PostgreSQL y carga las credenciales
# desde las variables de entorno para mayor seguridad.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('dbname'),
        'USER': os.getenv('user'),
        'PASSWORD': os.getenv('password'),
        'HOST': os.getenv('host'),
        'PORT': os.getenv('port'),
    }
}


# --- Validación de Contraseñas ---
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

# Validadores utilizados para comprobar la seguridad de las contraseñas de los usuarios.
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# --- Internacionalización ---
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'es-es' # Código de idioma para el proyecto.

TIME_ZONE = 'UTC' # Zona horaria para el almacenamiento de fechas y horas.

USE_I18N = True # Activa el sistema de traducción de Django.

USE_TZ = True # Activa el soporte de zonas horarias.


# --- Archivos Estáticos (CSS, JavaScript, Imágenes) ---
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/' # URL base para los archivos estáticos.
# Directorio donde `collectstatic` reunirá todos los archivos estáticos para producción.
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# --- Tipo de Clave Primaria por Defecto ---
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

# Tipo de campo a utilizar para las claves primarias autoincrementales.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
