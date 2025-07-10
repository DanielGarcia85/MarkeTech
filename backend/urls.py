"""djangoHeroku URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from django.conf.urls.static import static
from django.conf import settings
from backend.api.views import MessageListCreateView, MyConversationsView
from backend.api.views import start_conversation

from .api.views import (
    BulkCheckFavoritesView,
    CheckFavoriteView,
    GetPremiumStatusView,
    JobApplicationUpdateStatusView,
    JobFavoriteViewSet,
    SubmitJobApplicationView,
    ToggleFavoriteView,
    TogglePremiumView,
    index_view,
    MessageViewSet,
    UserViewSet,
    GroupViewSet,
    JobPostViewSet,
    JobSeekerProfileViewSet,
    JobSeekerApplicationsView,
    EmployerProfileViewSet,
    CreateUserProfileView,
    LoginView,
    LogoutView,
    SessionView,
    EmployerJobPostsView,
    UserProfileView,
    JobApplicationListByJobView,
    MessageListCreateView,
    MyConversationsView,
    JobApplicationDetailView,
    EmployerJobPostDetailView,
    SystemReviewViewSet,
    AppointmentCreateView,
    UserAppointmentsView,
    AppointmentResponseView
)

router = routers.DefaultRouter()
router.register('messages', MessageViewSet)
router.register('users', UserViewSet)
router.register('groups', GroupViewSet)
router.register('jobposts', JobPostViewSet)
router.register('system-reviews', SystemReviewViewSet)
router.register('jobseekers', JobSeekerProfileViewSet)
router.register('employers', EmployerProfileViewSet)
router.register('job-favorites', JobFavoriteViewSet, basename='job-favorites')

urlpatterns = [
    # http://localhost:8000/
    path('', index_view, name='index'),

    # http://localhost:8000/api/<router-viewsets>
    path('api/', include(router.urls)),

    path('api/accounts/', include('allauth.urls')),
    path("api/allauth/", include("allauth.headless.urls")),

    path('api/explorer/', include('rest_framework.urls', namespace='rest_framework')),

    # http://localhost:8000/api/admin/
    path('api/admin/', admin.site.urls),

    # Route created by Daniel to create a user profile
    # http://localhost:8000/api/create-profile/
    path("api/create-profile/", CreateUserProfileView.as_view(), name="create-profile"),

    # Route created by Jonathan and Daniel to login
    # http://localhost:8000/api/login/
    path("api/login/", LoginView.as_view(), name="login"),

    # Route created by Jonathan to logout
    # http://localhost:8000/api/logout/
    path("api/logout/", LogoutView.as_view(), name="logout"),

    # Route created by Jonathan to recover the session of the logged-in user
    # http://localhost:8000/api/session/
    path("api/session/", SessionView.as_view(), name="session"),

    # Route created by Jonathan that can :
    # [GET] Retrieve job offers from the authenticated employer
    # [POST] Create a new job offer for the authenticated employer
    # http://localhost:8000/api/employer-job-posts/
    path("api/employer-job-posts/", EmployerJobPostsView.as_view(), name="employer-job-posts"),

    # Route created by Jonathan to retrieve or perform operations on a specific job offer
    # [GET] Récupérer une offre d'emploi spécifique http://localhost:8000/api/employer-job-posts/{id}/
    # [PUT] Mettre à jour une offre d'emploi http://localhost:8000/api/employer-job-posts/{id}/
    # [DELETE] Supprimer une offre d'emploi http://localhost:8000/api/employer-job-posts/{id}/
    path('api/employer-job-posts/<int:pk>/', EmployerJobPostDetailView.as_view(), name='employer-job-post-detail'),
    
    # Route created by Daniel to retrieve the user profile
    # http://localhost:8000/api/user-profile/
    path("api/user-profile/", UserProfileView.as_view(), name="user-profile"),

    # Route created by Alexis to retrieve applications for an offer
    # http://localhost:8000/jobposts/5/applications/
    path('api/jobposts/<int:job_id>/applications/', JobApplicationListByJobView.as_view(), name='job-applications-by-job'),
    
    # Route created by Ysias to update the status of a job application
    # [PATCH] Update the status of a job application http://localhost:8000/api/applications/{id}/update-status/
    path('api/applications/<int:application_id>/update-status/', JobApplicationUpdateStatusView.as_view(), name='application-update-status'),
    
    # Route created by Ysias to allow job seekers to view their applications and track status
    # [GET] View all applications submitted by the current user http://localhost:8000/api/jobseeker/applications/
    path('api/jobseeker/applications/', JobSeekerApplicationsView.as_view(), name='jobseeker-applications'),
    
    # Route created by Ysias to allow job seekers to submit job applications
    # [POST] Submit application for a specific job http://localhost:8000/api/jobs/{job_id}/apply/
    path('api/jobs/<int:job_id>/apply/', SubmitJobApplicationView.as_view(), name='submit-job-application'),

    # Route created by Alexis to retrieve or send messages relating to a job application
    # http://localhost:8000/api/applications/5/messages/
    path("api/applications/<int:application_id>/messages/", MessageListCreateView.as_view(), name="application-messages"),
   
    # Route created by Alexis to retrieve the conversations of the connected user (employer or candidate)
    # http://localhost:8000/api/conversations/
    path("api/conversations/", MyConversationsView.as_view(), name="my-conversations"),

    # Route created by Alexis to retrieve information on a specific application
    # http://localhost:8000/api/applications/1/
    path("api/applications/<int:application_id>/", JobApplicationDetailView.as_view(), name="application-detail"),

    # Route created by Alexis to start a conversation (‘Message Employer’ button)
    path("api/start-conversation/", start_conversation, name="start-conversation"),

    # Route created by Jonathan to create a appointment
    # [POST] Create a new appointment http://localhost:8000/api/appointments/
    path('api/appointments/', AppointmentCreateView.as_view(), name='appointment-create'),

    # Route created by Jonathan to retrieve all appointments for authenticated user
    # [GET] Retrieve all appointments for the authenticated user http://localhost:8000/api/user-appointments/
    path('api/user-appointments/', UserAppointmentsView.as_view(), name='appointment-list'),

    # Route created by Jonathan to to update an appointment response for a job seeker
    # [PATCH] Update appointment response http://localhost:8000/api/appointments/{id}/respond/
    path('api/appointments/<int:appointment_id>/respond/', AppointmentResponseView.as_view(), name='appointment-respond'),

    
    # Route created by Ysias
    path('api/jobs/<int:job_id>/toggle-favorite/', ToggleFavoriteView.as_view(), name='toggle-favorite'),
    path('api/jobs/<int:job_id>/check-favorite/', CheckFavoriteView.as_view(), name='check-favorite'),
    path('api/check-favorites/', BulkCheckFavoritesView.as_view(), name='check-favorites'),
      # Routes premium
    path("api/toggle-premium/", TogglePremiumView.as_view(), name="toggle-premium"),
    path("api/premium-status/", GetPremiumStatusView.as_view(), name="get-premium-status"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
