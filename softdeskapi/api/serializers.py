from dataclasses import fields
from pyexpat import model
from urllib import request
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault
from api.models import Project, Issue, Comment, Contributor


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "title", "description", "type"]


class NewIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "desc",
            "tag",
            "priority",
        ]

    def create(self, validated_data):
        user = None
        project_id = self.context.get("project_id")
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user

        project = Project.objects.get(id=project_id)

        issue = Issue.objects.create(
            title=validated_data["title"],
            desc=validated_data["desc"],
            tag=validated_data["tag"],
            priority=validated_data["priority"],
            project=project,
            author_user=user,
            assignee_user=user,
        )
        issue.save()

        return issue


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            "id",
            "title",
            "desc",
            "tag",
            "priority",
            "assignee_user_id",
            "author_user_id",
        ]
        # fields = "__all__"


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "description",
        ]

    def create(self, validated_data):
        issue_id = self.context.get("issue_id")
        request = self.context.get("request")
        user = request.user

        issue = Issue.objects.get(id=issue_id)

        comment = Comment.objects.create(description=validated_data["description"], author_user=user, issue=issue)
        comment.save()

        return comment


class CommentDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name"]


class UserRegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(required=True, write_only=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "username", "password", "password_confirm"]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password": "Les mots de passe ne correspondent pas."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            username=validated_data["username"],
        )

        user.password = make_password(validated_data["password"])
        user.save()

        return user

    # def get_password_confirm(self, obj):
    #     return obj


class ContributorSerializer(serializers.ModelSerializer):
    # user = UserSerializer(many=False, instance=None)
    # project = ProjectSerializer(many=False)

    class Meta:
        model = Contributor
        fields = ["user", "permission", "role"]


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ("username", "password")
#         extra_kwargs = {"password": {"write_only": True}}

#     def register(self, validated_data):
#         password = validated_data.pop('password')
#         user = User(**validated_data)
#         user.set_password(password)
#         user.save()
#         return user
