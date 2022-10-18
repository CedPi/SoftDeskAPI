"""softdeskapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from posixpath import basename
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# from api.views import ProjectAPIView, CommentAPIView, ContributorAPIView, IssueAPIView
from api.views import (
    UserRegisterAPIView,
    ProjectAPIView,
    ProjectDetailAPIView,
    UserAPIView,
    UserDetailAPIView,
    IssueAPIView,
    IssueDetailAPIView,
    CommentAPIView,
    CommentDetailAPIView,
)


router = routers.SimpleRouter()


urlpatterns = [
    path("admin/", admin.site.urls),
    # path("api-auth/", include("rest_framework.urls")),
    path("api/signup/", UserRegisterAPIView.as_view()),
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/project/", ProjectAPIView.as_view()),
    path("api/project/<int:project_id>/", ProjectDetailAPIView.as_view()),
    path("api/project/<int:project_id>/user/", UserAPIView.as_view()),
    path("api/project/<int:project_id>/user/<int:user_id>/", UserDetailAPIView.as_view()),
    path("api/project/<int:project_id>/issue/", IssueAPIView.as_view()),
    path("api/project/<int:project_id>/issue/<int:issue_id>/", IssueDetailAPIView.as_view()),
    path("api/project/<int:project_id>/issue/<int:issue_id>/comment/", CommentAPIView.as_view()),
    path(
        "api/project/<int:project_id>/issue/<int:issue_id>/comment/<int:comment_id>/", CommentDetailAPIView.as_view()
    ),
    path("api/", include(router.urls)),
]
