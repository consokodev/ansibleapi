from django.contrib import admin

# Register your models here.
from api.models import Projects, History

admin.site.register(Projects)
admin.site.register(History)