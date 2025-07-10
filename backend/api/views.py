# 1. Standard library
import os
import uuid
# 2. Django
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.db import models, transaction
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from django.utils import timezone
# 3. Django REST Framework
from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.filters import OrderingFilter
# 4. Third-party apps
from django_filters.rest_framework import DjangoFilterBackend
# 5. Local apps
from backend.api.permissions import IsEmployer
from .models import (JobSeekerProfile, EmployerProfile,  JobPost, JobApplication, SystemReview, Message, Document, JobFavorite, Appointment)
from .serializers import (JobApplicationCreateSerializer, UserSerializer, GroupSerializer, JobFavoriteSerializer, MessageSerializer, JobSeekerProfileSerializer, EmployerProfileSerializer, JobPostSerializer, JobApplicationSerializer, SystemReviewSerializer, AppointmentSerializer)
from .pagination import JobPostPagination
from .filters import JobPostFilter
from django.utils import timezone


# Serve Vue Application
index_view = never_cache(TemplateView.as_view(template_name='index.html'))


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed, created, updated, or deleted by admin users.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows user groups to be viewed, created, updated, or deleted by admin users.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAdminUser]


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows messages to be viewed, created, updated, or deleted.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class JobSeekerProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows job seeker profiles to be viewed, created, updated, or deleted.
    """
    queryset = JobSeekerProfile.objects.all()
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def update(self, request, *args, **kwargs):
        """
        Update JobSeekerProfile with multiple documents handling.
        """
        profile = self.get_object()
        data = request.data.copy()

        # Handle CV removal
        cv_to_remove = data.get('cv_to_remove', 'false') == 'true'
        if cv_to_remove and profile.cv:
            profile.cv.delete(save=False)
            profile.cv = None

        # Handle CV upload
        if "cv" in request.FILES:
            profile.cv = request.FILES["cv"]

        # Handle additional documents upload
        additional_documents = request.FILES.getlist('additional_documents')

        # Validate document files (optional)
        for document in additional_documents:
            if document.size > 5 * 1024 * 1024:  # Limit: 5MB
                return Response({"error": f"{document.name} is too large. Max size is 5MB."}, status=status.HTTP_400_BAD_REQUEST)
            if not document.name.endswith(('.pdf', '.docx', '.png', '.jpg', '.jpeg')):
                return Response({"error": f"{document.name} is not a valid file type. Only .pdf', '.docx', '.png', '.jpg', '.jpeg"}, status=status.HTTP_400_BAD_REQUEST)

        # Save new documents
        for document in additional_documents:
            new_doc = Document(file=document)
            new_doc.save()
            profile.additional_documents.add(new_doc)

        # Handle removal of documents
        documents_to_remove = data.getlist('documents_to_remove')
        if documents_to_remove:
            for doc_id in documents_to_remove:
                try:
                    document = Document.objects.get(id=doc_id)
                    if document in profile.additional_documents.all():
                        profile.additional_documents.remove(document)
                        document.delete()
                except Document.DoesNotExist:
                    continue

        # Update other profile fields
        serializer = self.get_serializer(profile, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)


class EmployerProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows employer profiles to be viewed, created, updated, or deleted.
    """
    queryset = EmployerProfile.objects.all()
    serializer_class = EmployerProfileSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class JobPostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that provides paginated and filtered job posts, allowing employers to manage job postings.
    """
    queryset = JobPost.objects.filter(is_visible=True).select_related('employer')
    serializer_class = JobPostSerializer
    pagination_class = JobPostPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = JobPostFilter
    ordering_fields = ['title', 'salary_min', 'salary_max', 'created_at']
    ordering = ['-employer__is_premium', '-created_at']


class SystemReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to view, create, update, and delete system reviews.
    """
    queryset = SystemReview.objects.all().order_by('-created_at')
    serializer_class = SystemReviewSerializer
    
    def get_queryset(self):
        queryset = SystemReview.objects.all().order_by('-created_at')
        # Filter by user if required
        user_id = self.request.query_params.get('user_id', None)
        if user_id == 'me' and self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        elif user_id:
            queryset = queryset.filter(user__id=user_id)
        return queryset
    
    def perform_create(self, serializer):
        # Check whether the user already has a review
        if SystemReview.objects.filter(user=self.request.user).exists():
            return Response(
                {"detail": "You already have a review. Please update your existing review instead."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # Associate the current user with the review
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        # Check that the user updates their own review
        if serializer.instance.user != self.request.user:
            return Response(
                {"detail": "You can only update your own review."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        # Get general statistics on reviews
        total_reviews = SystemReview.objects.count()
        if total_reviews == 0:
            return Response({
                'total_reviews': 0,
                'average_rating': 0,
                'average_ease': 0,
                'average_job_search': 0,
                'average_application_process': 0,
                'average_message_system': 0
            })
            
        avg_rating = SystemReview.objects.aggregate(models.Avg('rating'))['rating__avg']
        avg_ease = SystemReview.objects.aggregate(models.Avg('ease_of_navigation'))['ease_of_navigation__avg']
        avg_job_search = SystemReview.objects.aggregate(models.Avg('job_search_effectiveness'))['job_search_effectiveness__avg']
        avg_application_process = SystemReview.objects.aggregate(models.Avg('application_process_simplicity'))['application_process_simplicity__avg']
        avg_message_system = SystemReview.objects.aggregate(models.Avg('message_system_effectiveness'))['message_system_effectiveness__avg']
        
        return Response({
            'total_reviews': total_reviews,
            'average_rating': avg_rating,
            'average_ease': avg_ease,
            'average_job_search': avg_job_search,
            'average_application_process': avg_application_process,
            'average_message_system': avg_message_system
        })


class CreateUserProfileView(APIView):
    """
    API endpoint that allows users to register as a job seeker or employer and create their profile.
    """
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, FormParser] 
    def post(self, request, *args, **kwargs):
        
        role = request.data.get("role")
        email = request.data.get("email")
        username = request.data.get("username", email)
        password = request.data.get("password")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")

        if not email or not password or not role:
            return Response({"error": "Email, password, and role are required."}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"error": "User with this email already exists."}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name, last_name=last_name)
            data = request.data.dict()
            if role == "jobseeker":
                if "profile_picture" in request.FILES:
                    original_file = request.FILES["profile_picture"]
                    unique_id = uuid.uuid4()
                    new_filename = f"{unique_id}{os.path.splitext(original_file.name)[1]}"
                    request.FILES["profile_picture"].name = new_filename
                
                serializer = JobSeekerProfileSerializer(data={**data, "user": user.id})
                if serializer.is_valid():
                    serializer.save()
                    jobseeker_group = Group.objects.get(name='jobseeker')
                    jobseeker_group.user_set.add(user)
                else:
                    raise ValueError(serializer.errors)

            elif role == "employer":

                if "company_logo" in request.FILES:
                    original_file = request.FILES["company_logo"]
                    unique_id = uuid.uuid4()
                    new_filename = f"{unique_id}{os.path.splitext(original_file.name)[1]}"
                    request.FILES["company_logo"].name = new_filename

                serializer = EmployerProfileSerializer(data={**data, "user": user.id})
                if serializer.is_valid():
                    serializer.save()
                    employer_group = Group.objects.get(name='employer')
                    employer_group.user_set.add(user)
                else:
                    raise ValueError(serializer.errors)
            else:
                raise ValueError({"error": "Invalid role."})
            
            login(request, user)
            
            return Response({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                },
                "profile": serializer.data
            }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """
    API endpoint that allows users to log in using their username and password.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)


            groups = [group.name for group in user.groups.all()]
            return Response({
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "roles": groups,
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    API endpoint that allows authenticated users to log out of the system.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    API endpoint that retrieves the authenticated user's profile as a job seeker or employer.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        try:
            jobseeker = JobSeekerProfile.objects.get(user=user)
            serializer = JobSeekerProfileSerializer(jobseeker)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except JobSeekerProfile.DoesNotExist:
            pass

        try:
            employer = EmployerProfile.objects.get(user=user)
            serializer = EmployerProfileSerializer(employer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except EmployerProfile.DoesNotExist:
            pass

        return Response({"error": "No profile found for this user."}, status=status.HTTP_404_NOT_FOUND)


class EmployerJobPostsView(APIView):
    """
    API endpoint that allows employers to view and create job posts associated with their profile.
    """
    permission_classes = [permissions.IsAuthenticated, IsEmployer]

    def get(self, request):
        try:
            employer = EmployerProfile.objects.get(user=request.user)

            job_posts = JobPost.objects.filter(employer=employer)

            serializer = JobPostSerializer(job_posts, many=True, context={"request": request})
            return Response(serializer.data, status=200)
        except EmployerProfile.DoesNotExist:
            return Response({"error": "Employer profile not found."}, status=404)
        
    def post(self, request):
        try:
            employer = EmployerProfile.objects.get(user=request.user)
        except EmployerProfile.DoesNotExist:
            return Response({"error": "Employer profile not found."}, status=404)

        data = request.data.copy()
        data["employer"] = employer.id
        data["company_name"] = employer.company_name
    
        data["is_visible"] = True

        job_title = data.get("title")

        existing_job = JobPost.objects.filter(
            employer=employer,
            title=job_title
        ).first()
    
        if existing_job:
            return Response(
                {"error": "A similar job posting already exists."},
                status=400
        )
    
        serializer = JobPostSerializer(data=data)
        if serializer.is_valid():
            job_post = serializer.save()
        
            if employer.company_logo:
                job_post.company_logo = employer.company_logo
                job_post.save()
            
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    

class EmployerJobPostDetailView(APIView):
    """
    API endpoint that allows employers to view, update, or delete a specific job post they created.
    """
    permission_classes = [permissions.IsAuthenticated, IsEmployer]

    def get_job_post(self, request, pk):
        try:
            employer = EmployerProfile.objects.get(user=request.user)
            job_post = JobPost.objects.get(pk=pk, employer=employer)
            return job_post
        except EmployerProfile.DoesNotExist:
            return Response({"error": "Employer profile not found."}, status=404)
        except JobPost.DoesNotExist:
            return Response({"error": "Job post not found or you don't have permission to access it."}, status=404)
    
    
    def get(self, request, pk):
        job_post = self.get_job_post(request, pk)
        serializer = JobPostSerializer(job_post, context={"request": request})
        return Response(serializer.data)
    
    def delete(self, request, pk):
        job_post = self.get_job_post(request, pk)
        job_post.delete()
        return Response({"message": "Job post deleted successfully"}, status=204)
    
    def patch(self, request, pk):
        job_post = self.get_job_post(request, pk)
        
        data = request.data.copy()
        if "employer" in data:
            del data["employer"]
        if "company_name" in data:
            del data["company_name"]
        if "company_logo" in data:
            del data["company_logo"]
     
        serializer = JobPostSerializer(job_post, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    
class SessionView(APIView):
    """
    API endpoint that provides session information for the authenticated user, including profile and group data.
    """
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = request.user
        groups = [group.name for group in user.groups.all()]
        try:
            jobseeker = JobSeekerProfile.objects.get(user=user)
            profile_serializer = JobSeekerProfileSerializer(jobseeker, context={"request": request})
        except JobSeekerProfile.DoesNotExist:
            try:
                employer = EmployerProfile.objects.get(user=user)
                profile_serializer = EmployerProfileSerializer(employer, context={"request": request})
            except EmployerProfile.DoesNotExist:
                profile_serializer = None
        response_data = {
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "groups": groups,
            },
            "profile": profile_serializer.data,
        }
        return Response(response_data, status=status.HTTP_200_OK)
    

class JobApplicationListByJobView(generics.ListAPIView):
    """
    API endpoint that retrieves job applications for a specific job post, accessible only to the employer.
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployer]
    def get_queryset(self):
        job_id = self.kwargs['job_id']
        user = self.request.user

        try:
            employer_profile = EmployerProfile.objects.get(user=user)
        except EmployerProfile.DoesNotExist:
            raise PermissionDenied("You don't have an employer profile.")

        employer_profile = self.request.user

        job = get_object_or_404(JobPost, id=job_id)
        if job.employer.user.id != employer_profile.id:
            raise PermissionDenied("You do not have permission to view applications for this job.")

        return JobApplication.objects.filter(job=job).order_by('-candidate__is_premium', '-applied_at')
    
class JobApplicationUpdateStatusView(APIView):
    """
    API endpoint that allows employers to update the status of a specific job application.
    """
    permission_classes = [permissions.IsAuthenticated, IsEmployer]

    def patch(self, request, application_id):
        try:
            employer_profile = EmployerProfile.objects.get(user=request.user)
        except EmployerProfile.DoesNotExist:
            return Response({"error": "Employer profile not found."}, status=404)

        application = get_object_or_404(JobApplication, id=application_id)
        
        if application.job.employer != employer_profile:
            return Response(
                {"error": "You do not have permission to update this application."},
                status=403
            )
        
        status = request.data.get('status')
        valid_statuses = [choice[0] for choice in JobApplication.STATUS_CHOICES]
        if status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Must be one of: {', '.join(dict(JobApplication.STATUS_CHOICES).keys())}"},
                status=400
            )
        
        application.status = status
        application.save()
        
        serializer = JobApplicationSerializer(application)
        return Response(serializer.data)
    

class JobSeekerApplicationsView(generics.ListAPIView):
    """
    API endpoint that allows job seekers to see all their job applications.
    Only users in the 'job_seeker' group can access this.
    """
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        user_groups = [group.name for group in user.groups.all()]
        print("Groupes utilisateur :", user_groups)
        if not user.groups.filter(name='jobseeker').exists():
            raise PermissionDenied("You do not have permission to view job applications.")

        applications = JobApplication.objects.filter(candidate=user.jobseekerprofile)
        return applications.select_related('job')

class SubmitJobApplicationView(APIView):
    """
    API endpoint that allows job seekers to submit a job application to a specific job post.
    """
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, job_id):
        job = get_object_or_404(JobPost, id=job_id)

        try:
            jobseeker_profile = JobSeekerProfile.objects.get(user=request.user)
        except JobSeekerProfile.DoesNotExist:
            return Response({"error": "You must have a job seeker profile to apply for a job."}, status=400)

        if JobApplication.objects.filter(job=job, candidate=jobseeker_profile).exists():
            return Response({"error": "You have already applied to this job."}, status=400)

        data = request.data.copy()
        data['job'] = job.id
        data['candidate'] = jobseeker_profile.id 

        serializer = JobApplicationCreateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Application submitted successfully!"}, status=201)
        return Response(serializer.errors, status=400)

      
class MessageListCreateView(generics.ListCreateAPIView):
    """
    API endpoint that allows users to view and send messages related to a specific job application.
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        application_id = self.kwargs.get('application_id')
        application = get_object_or_404(JobApplication, id=application_id)
        user = self.request.user
        if application.candidate.user != user and application.job.employer.user != user:
            raise PermissionDenied("You are not allowed to view these messages.")
        return Message.objects.filter(application=application).order_by('created_at')
      
    def perform_create(self, serializer):
        application_id = self.kwargs.get('application_id')
        application = get_object_or_404(JobApplication, id=application_id)
        user = self.request.user
        if application.candidate.user != user and application.job.employer.user != user:
            raise PermissionDenied("You cannot send a message on this application.")
        if user == application.candidate.user:
            receiver = application.job.employer.user
        else:
            receiver = application.candidate.user
        serializer.save(sender=user, receiver=receiver, application=application)


class MyConversationsView(APIView):
    """
    API endpoint that retrieves all conversations for the authenticated user, grouped by job applications.
    """
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        user = request.user
        applications = JobApplication.objects.filter(
            models.Q(candidate__user=user) | models.Q(job__employer__user=user)
        ).distinct()
        data = []
        for app in applications:
            if app.candidate.user == user: 
                other = app.job.employer.user
                profile = EmployerProfile.objects.filter(user=other).first()
                name = f"{profile.first_name} {profile.last_name}" if profile else other.username
                avatar = getattr(profile, "company_logo", None)
            else:  
                other = app.candidate
                profile = JobSeekerProfile.objects.filter(pk=other.pk).first()
                name = f"{profile.first_name} {profile.last_name}" if profile else other.user.username
                avatar = getattr(profile, "profile_picture", None)

            last_msg = app.messages.order_by("-created_at").first()
            last_body = last_msg.body[:50] + "..." if last_msg else "(No messages yet)"
            data.append({
                "application_id": app.id,
                "job_title": app.job.title,
                "name": name,
                "avatar":  request.build_absolute_uri(avatar.url) if avatar else request.build_absolute_uri("/media/profile_pictures/place_holder.png"),
                "last_message": last_body
            })
        return Response(data)


class JobApplicationDetailView(APIView):
    """
    API endpoint that retrieves the details of a specific job application.
    """
    permission_classes = [IsAuthenticated]
    def get(self, request, application_id):
        try:
            application = JobApplication.objects.get(pk=application_id)
        except JobApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=404)
        serializer = JobApplicationSerializer(application)
        return Response(serializer.data)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_conversation(request):
    """
    API endpoint that allows job seekers to start a conversation with an employer regarding a specific job application.
    """
    application_id = request.data.get("application_id")

    if not application_id:
        return Response({"error": "Application ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        application = JobApplication.objects.select_related('candidate', 'job__employer').get(id=application_id)
    except JobApplication.DoesNotExist:
        return Response({"error": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

    jobseeker_user = application.candidate.user
    employer_user = application.job.employer.user

    if request.user != jobseeker_user:
        return Response({"error": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

    if not Message.objects.filter(application=application).exists():
        Message.objects.create(
            application=application,
            sender=jobseeker_user,
            receiver=employer_user,
            subject="Conversation started",
            body=""
        )

    return Response({"id": application_id}, status=status.HTTP_200_OK)


class JobFavoriteViewSet(viewsets.ModelViewSet):
    """
    API endpoint pour gérer les favoris d'un chercheur d'emploi.
    """
    serializer_class = JobFavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        try:
            job_seeker = JobSeekerProfile.objects.get(user=self.request.user)
            return JobFavorite.objects.filter(job_seeker=job_seeker).select_related('job_post')
        except JobSeekerProfile.DoesNotExist:
            return JobFavorite.objects.none()
    
    def perform_create(self, serializer):
        try:
            job_seeker = JobSeekerProfile.objects.get(user=self.request.user)
            serializer.save(job_seeker=job_seeker)
        except JobSeekerProfile.DoesNotExist:
            raise PermissionDenied("You must have a job seeker profile to add favorites.")

class ToggleFavoriteView(APIView):
    """
    API endpoint pour ajouter/supprimer un favori.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, job_id):
        try:
            job_seeker = JobSeekerProfile.objects.get(user=request.user)
            job_post = JobPost.objects.get(pk=job_id)
            
            favorite, created = JobFavorite.objects.get_or_create(
                job_seeker=job_seeker,
                job_post=job_post
            )
            
            if not created:
                favorite.delete()
                return Response({"status": "removed"}, status=status.HTTP_200_OK)
            
            return Response({"status": "added"}, status=status.HTTP_201_CREATED)
            
        except JobSeekerProfile.DoesNotExist:
            return Response(
                {"error": "You must have a job seeker profile to add favorites."},
                status=status.HTTP_403_FORBIDDEN
            )
        except JobPost.DoesNotExist:
            return Response(
                {"error": "Job post not found."},
                status=status.HTTP_404_NOT_FOUND
            )

class CheckFavoriteView(APIView):
    """
    API endpoint pour vérifier si une offre est dans les favoris.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, job_id):
        try:
            job_seeker = JobSeekerProfile.objects.get(user=request.user)
            is_favorite = JobFavorite.objects.filter(
                job_seeker=job_seeker,
                job_post_id=job_id
            ).exists()
            
            return Response({"is_favorite": is_favorite})
            
        except JobSeekerProfile.DoesNotExist:
            return Response({"is_favorite": False})

class BulkCheckFavoritesView(APIView):
    """
    API endpoint pour vérifier en masse si plusieurs offres sont dans les favoris.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        job_ids = request.data.get('job_ids', [])
        
        if not job_ids or not isinstance(job_ids, list):
            return Response(
                {"error": "A list of job_ids is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            job_seeker = JobSeekerProfile.objects.get(user=request.user)
            
            favorites = JobFavorite.objects.filter(
                job_seeker=job_seeker,
                job_post_id__in=job_ids
            ).values_list('job_post_id', flat=True)
            
            favorite_statuses = {
                job_id: job_id in favorites
                for job_id in job_ids
            }
            
            return Response(favorite_statuses)
            
        except JobSeekerProfile.DoesNotExist:
            return Response({job_id: False for job_id in job_ids})


class TogglePremiumView(APIView):
    """
    API endpoint pour activer/désactiver le statut premium d'un utilisateur.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        user = request.user
        
        # Vérifier si l'utilisateur a un profil JobSeeker ou Employer
        try:
            jobseeker = JobSeekerProfile.objects.get(user=user)
            jobseeker.is_premium = not jobseeker.is_premium
            if jobseeker.is_premium:
                jobseeker.premium_since = timezone.now()
            else:
                jobseeker.premium_since = None
            jobseeker.save()
            
            return Response({
                "is_premium": jobseeker.is_premium,
                "user_type": "jobseeker",
                "message": "Premium status updated successfully"
            })
            
        except JobSeekerProfile.DoesNotExist:
            try:
                employer = EmployerProfile.objects.get(user=user)
                employer.is_premium = not employer.is_premium
                if employer.is_premium:
                    employer.premium_since = timezone.now()
                else:
                    employer.premium_since = None
                employer.save()
                
                return Response({
                    "is_premium": employer.is_premium,
                    "user_type": "employer",
                    "message": "Premium status updated successfully"
                })
                
            except EmployerProfile.DoesNotExist:
                return Response(
                    {"error": "No profile found for this user"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

class GetPremiumStatusView(APIView):
    """
    API endpoint pour récupérer le statut premium de l'utilisateur.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        try:
            jobseeker = JobSeekerProfile.objects.get(user=user)
            return Response({
                "is_premium": jobseeker.is_premium,
                "user_type": "jobseeker",
                "premium_since": jobseeker.premium_since
            })
        except JobSeekerProfile.DoesNotExist:
            try:
                employer = EmployerProfile.objects.get(user=user)
                return Response({
                    "is_premium": employer.is_premium,
                    "user_type": "employer",
                    "premium_since": employer.premium_since
                })
            except EmployerProfile.DoesNotExist:
                return Response(
                    {"error": "No profile found for this user"}, 
                    status=status.HTTP_404_NOT_FOUND
                )


class AppointmentCreateView(APIView):
    """
    API endpoint pour permettre aux employeurs de créer des rendez-vous avec les jobseekers.
    """
    permission_classes = [permissions.IsAuthenticated, IsEmployer]
    
    def post(self, request):
        try:
            employer_profile = EmployerProfile.objects.get(user=request.user)
        except EmployerProfile.DoesNotExist:
            return Response({"error": "Employer profile not found."}, status=404)
        
        data = request.data.copy()
        data['employer'] = employer_profile.id
        
        job_application_id = data.get('job_application')
        if not job_application_id:
            return Response({"error": "Job application ID is required."}, status=400)
        
        try:
            job_application = JobApplication.objects.get(id=job_application_id)
            if job_application.job.employer.id != employer_profile.id:
                return Response({"error": "You can only create appointments for your own job applications."}, status=403)
            
            data['job_seeker'] = job_application.candidate.id
        except JobApplication.DoesNotExist:
            return Response({"error": "Job application not found."}, status=404)
        
        serializer = AppointmentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class UserAppointmentsView(APIView):
    """
    API endpoint qui permet à l'utilisateur authentifié de voir ses rendez-vous,
    qu'il soit employeur ou jobseeker.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        try:
            employer_profile = EmployerProfile.objects.get(user=user)
            appointments = Appointment.objects.filter(employer=employer_profile)
            
            serializer = AppointmentSerializer(appointments, many=True)
            return Response(serializer.data)
            
        except EmployerProfile.DoesNotExist:
            try:
                jobseeker_profile = JobSeekerProfile.objects.get(user=user)
                appointments = Appointment.objects.filter(job_seeker=jobseeker_profile)
                
                serializer = AppointmentSerializer(appointments, many=True)
                return Response(serializer.data)
                
            except JobSeekerProfile.DoesNotExist:
                return Response(
                    {"error": "No profile found for this user."},
                    status=status.HTTP_404_NOT_FOUND
                )
            
class AppointmentResponseView(APIView):
    """
    API endpoint permettant aux jobseekers de répondre à une demande de rendez-vous
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, appointment_id):
        try:
            jobseeker = JobSeekerProfile.objects.get(user=request.user)
            appointment = Appointment.objects.get(id=appointment_id,job_seeker=jobseeker)
            
            status = request.data.get('status')
            if not status or status not in ['accepted', 'rejected']:
                return Response(
                    {"error": "Status must be either 'accepted' or 'rejected'"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            response_message = request.data.get('response_message')
            if not response_message:
                return Response(
                    {"error": "Response message is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            appointment.status = status
            appointment.job_seeker_response_message = response_message
            appointment.job_seeker_response_date = timezone.now()
            appointment.save()
            
            serializer = AppointmentSerializer(appointment)
            return Response(serializer.data)
            
        except JobSeekerProfile.DoesNotExist:
            return Response(
                {"error": "Job seeker profile not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Appointment.DoesNotExist:
            return Response(
                {"error": "Appointment not found or you don't have permission to modify it"},
                status=status.HTTP_404_NOT_FOUND
            )

