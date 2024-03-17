# url_shortener/admin.py

from django.contrib import admin
from .models import URLMapping

admin.site.register(URLMapping)
