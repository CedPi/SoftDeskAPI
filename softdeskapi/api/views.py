from urllib import request, response
from django.shortcuts import render
from django.http import Http404
from django.db import IntegrityError, transaction
from django.contrib.auth.models import User

from rest_framework import generics, permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response

from api.models import Project, Issue, Comment, Contributor
from api.serializers import (
    ProjectSerializer,
    IssueSerializer,
    NewIssueSerializer,
    CommentSerializer,
    CommentDetailSerializer,
    ContributorSerializer,
    UserSerializer,
    UserRegisterSerializer,
)


class Check:
    def isContrib(self, project_id, user):
        try:
            project = Project.objects.get(id=project_id)
            contributor = Contributor.objects.get(project=project, user=user)
            return contributor
        except Contributor.DoesNotExist:
            return None


class UserRegisterAPIView(CreateAPIView):

    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserRegisterSerializer


class ProjectAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer

    def get(self, request, format=None):
        contributor_projects = Contributor.objects.filter(user=request.user).values("project_id")
        projects = Project.objects.filter(id__in=contributor_projects)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    serializer.save()
                    user = request.user
                    contributor = Contributor()
                    contributor.user = user
                    contributor.project = serializer.instance
                    contributor.permission = "A"
                    contributor.role = "admin"
                    contributor.save()
            except IntegrityError:
                pass
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectDetailAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ProjectSerializer

    def get_object(self, project_id):
        try:
            return Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise Http404

    def get(self, request, project_id, format=None):
        project = self.get_object(project_id)
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    def put(self, request, project_id, format=None):
        project = self.get_object(project_id)
        serializer = ProjectSerializer(project, data=request.data)
        if serializer.is_valid():
            auth_user = request.user.id
            user = User.objects.get(id=auth_user)
            try:
                contributor = Contributor.objects.get(project=project, user=user)
            except Contributor.DoesNotExist:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            if contributor.permission == "A":
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id, format=None):
        project = self.get_object(project_id)
        auth_user = request.user.id
        user = User.objects.get(id=auth_user)
        try:
            contributor = Contributor.objects.get(project=project, user=user)
        except Contributor.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        if contributor.permission == "A":
            project.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class UserAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContributorSerializer

    def get(self, request, project_id, format=None):
        contributors = Contributor.objects.filter(project_id=project_id).values("user")
        users = User.objects.filter(id__in=[contributor["user"] for contributor in contributors])
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, project_id, format=None):
        project = Project.objects.get(id=project_id)
        serializer = ContributorSerializer(data=request.data)
        if serializer.is_valid():
            auth_user = request.user.id
            user = User.objects.get(id=auth_user)
            try:
                contributor = Contributor.objects.get(
                    project=project, user=user
                )
            except Contributor.DoesNotExist:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

            if contributor.permission == "A":
                serializer.save(project_id=project_id)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContributorSerializer

    def get(self, request, project_id, user_id, format=None):
        contributor = Contributor.objects.get(project=project_id, user=user_id)
        serializer = ContributorSerializer(contributor)
        return Response(serializer.data)

    def delete(self, request, project_id, user_id, format=None):
        auth_user = request.user.id
        user = User.objects.get(id=auth_user)
        try:
            author = Contributor.objects.get(project=project_id, user=user)
        except Contributor.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if author.permission == "A":
            contributor = Contributor.objects.filter(project=project_id, user=user_id)
            contributor.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class IssueAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id, format=None):
        contributor = Check().isContrib(project_id=project_id, user=request.user)

        if contributor is not None:
            issues = Issue.objects.filter(project=project_id)
            serializer = IssueSerializer(issues, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, project_id, format=None):
        auth_user = request.user.id
        user = User.objects.get(id=auth_user)
        try:
            author = Contributor.objects.get(project=project_id, user=user)
        except Contributor.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        context = {"request": request, "project_id": project_id}
        serializer = NewIssueSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IssueDetailAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, issue_id):
        try:
            return Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            raise Http404

    def get(self, request, project_id, issue_id, format=None):
        contributor = Check().isContrib(project_id, request.user)
        if contributor is not None:
            issue = self.get_object(issue_id)
            serializer = IssueSerializer(issue)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, project_id, issue_id, format=None):
        project = Project.objects.get(id=project_id)
        issue = self.get_object(issue_id)
        serializer = IssueSerializer(issue, data=request.data)
        if serializer.is_valid():
            contributor = Check().isContrib(project_id, request.user)
            if contributor is not None:
                if issue.author_user == request.user:
                    serializer.save()
                    return Response(serializer.data)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, project_id, issue_id, format=None):
        issue = self.get_object(issue_id)
        contributor = Check().isContrib(project_id, request.user)
        if contributor is not None:
            if issue.author_user == request.user:
                issue.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class CommentAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def get(self, request, project_id, issue_id, format=None):
        contributor = Check().isContrib(project_id, request.user)
        if contributor is not None:
            issue = Issue.objects.filter(id=issue_id)
            if len(issue) == 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            comments = Comment.objects.filter(issue__in=issue)
            if len(comments) == 0:
                return Response(status=status.HTTP_204_NO_CONTENT)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request, project_id, issue_id, format=None):
        contributor = Check().isContrib(project_id, request.user)
        if contributor is not None:
            pass
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        context = context = {"request": request, "issue_id": issue_id}
        serializer = CommentSerializer(data=request.data, context=context)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CommentSerializer

    def get_object(self, comment_id):
        try:
            return Comment.objects.get(id=comment_id)
        except Issue.DoesNotExist:
            raise Http404

    def get(self, request, project_id, issue_id, comment_id, format=None):
        contributor = Check().isContrib(project_id, request.user)
        if contributor is not None:
            comment = self.get_object(comment_id)
            serializer = CommentDetailSerializer(comment)
            return Response(serializer.data)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def put(self, request, project_id, issue_id, comment_id, format=None):
        contributor = Check().isContrib(project_id, request.user)
        if contributor is not None:
            comment = self.get_object(comment_id)
            serializer = CommentSerializer(comment, data=request.data)
            if serializer.is_valid():
                if comment.author_user == request.user:
                    serializer.save()
                    return Response(serializer.data)
                else:
                    return Response(status=status.HTTP_401_UNAUTHORIZED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

    def delete(self, request, project_id, issue_id, comment_id, format=None):
        contributor = Check().isContrib(project_id, request.user)
        if contributor is not None:
            comment = self.get_object(comment_id)
            if comment.author_user == request.user:
                comment.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
