from doctest import debug_script
from django.conf import settings
from django.db import models
from django.forms import ChoiceField


class Project(models.Model):
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=2048)
    type = models.CharField(max_length=128)
    author_user = models.ManyToManyField(settings.AUTH_USER_MODEL, through="Contributor")

    def __str__(self):
        return self.title


class Contributor(models.Model):
    CHOICES = (("U", "user"), ("A", "admin"))
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="user")
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    permission = models.CharField(max_length=128, choices=CHOICES)
    role = models.CharField(max_length=128)

    def __str__(self):
        return self.user.username + " -> " + self.project.title


class Issue(models.Model):
    title = models.CharField(max_length=128)
    desc = models.CharField(max_length=2048)
    tag = models.CharField(max_length=128)
    priority = models.CharField(max_length=128)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="issues")
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name="author_user")
    assignee_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name="assignee_user"
    )
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    description = models.CharField(max_length=2048)
    author_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "COMMENT: " + self.description + " -> ISSUE: " + self.issue.title
