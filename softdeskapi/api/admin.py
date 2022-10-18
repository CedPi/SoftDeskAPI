from django.contrib import admin
from api.models import Comment, Contributor, Issue, Project

admin.site.register((Comment, Contributor, Issue, Project))
