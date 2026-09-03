from django.contrib import admin
from .models import Location, Category, Knowledge, Vote, Report


admin.site.register(Location)
admin.site.register(Category)
admin.site.register(Knowledge)
admin.site.register(Vote)
admin.site.register(Report)