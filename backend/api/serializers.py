from django.contrib.auth.models import User, Group
from rest_framework import serializers


from .models import JobApplication, JobFavorite, Message, JobSeekerProfile, EmployerProfile, JobPost, SystemReview, Document, Appointment



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    receiver = serializers.PrimaryKeyRelatedField(read_only=True)
    sender_username = serializers.CharField(source="sender.username", read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'body', 'created_at', 'sender','sender_username', 'receiver']

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() or obj.sender.username



class JobSeekerProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = JobSeekerProfile
        fields = '__all__'

class JobPostSerializer(serializers.ModelSerializer):
    company_logo = serializers.ImageField(required=False, allow_null=True)
    is_favorite = serializers.SerializerMethodField()
    is_employer_premium = serializers.SerializerMethodField()
    
    class Meta: 
        model = JobPost
        fields = '__all__' 
        
    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                job_seeker = JobSeekerProfile.objects.get(user=request.user)
                return JobFavorite.objects.filter(job_seeker=job_seeker, job_post=obj).exists()
            except JobSeekerProfile.DoesNotExist:
                return False
        return False 
       
    def get_is_employer_premium(self, obj):
        return obj.employer.is_premium


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = '__all__'



class JobSeekerProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    cv = serializers.FileField(required=False, allow_null=True)
    additional_documents = DocumentSerializer(many=True, read_only=True)
    class Meta:
        model = JobSeekerProfile
        fields = '__all__'



class JobApplicationSerializer(serializers.ModelSerializer):
    candidate_username = serializers.CharField(source="candidate.username", read_only=True)
    candidate_email = serializers.CharField(source="candidate.email", read_only=True)
    job_title = serializers.CharField(source="job.title", read_only=True)
    job_location = serializers.CharField(source="job.location", read_only=True)   
    job_company = serializers.CharField(source="job.company_name", read_only=True)
    candidate_name = serializers.SerializerMethodField()
    status_updated_at = serializers.DateTimeField(read_only=True)
    status_display = serializers.SerializerMethodField()
    is_candidate_premium = serializers.SerializerMethodField()
    #candidate = JobSeekerProfileSerializer()
    
    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ['id', 'applied_at', 'candidate_username', 'candidate_email', 'job_title', 'status_updated_at']
    
    def get_candidate_name(self, obj):
        if hasattr(obj.candidate, 'jobseekerprofile'):
            profile = obj.candidate.jobseekerprofile
            return f"{profile.first_name} {profile.last_name}"
        return f"{obj.candidate.first_name} {obj.candidate.last_name}"
    
    def get_status_display(self, obj):
        return dict(JobApplication.STATUS_CHOICES).get(obj.status, obj.status)
    
    def get_is_candidate_premium(self, obj):
        return obj.candidate.is_premium


class EmployerProfileSerializer(serializers.ModelSerializer):
    company_logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = EmployerProfile
        fields = '__all__'  


class SystemReviewSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = SystemReview
        fields = '__all__'
        read_only_fields = ('user',)


class JobApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['job', 'candidate', 'cv_file', 'cover_letter_file']

class JobFavoriteSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='job_post.title', read_only=True)
    company_name = serializers.CharField(source='job_post.company_name', read_only=True)
    location = serializers.CharField(source='job_post.location', read_only=True)
    salary_min = serializers.DecimalField(source='job_post.salary_min', max_digits=10, decimal_places=2, read_only=True)
    salary_max = serializers.DecimalField(source='job_post.salary_max', max_digits=10, decimal_places=2, read_only=True)
    years_experience = serializers.IntegerField(source='job_post.years_experience', read_only=True)
    description = serializers.CharField(source='job_post.description', read_only=True)
    company_logo = serializers.ImageField(source='job_post.company_logo', read_only=True)
    created_at = serializers.DateTimeField(source='job_post.created_at', read_only=True)
    
    class Meta:
        model = JobFavorite
        fields = '__all__'
        read_only_fields = ['created_at']


class AppointmentSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='employer.company_name', read_only=True)
    employer_name = serializers.SerializerMethodField(read_only=True)
    job_seeker_name = serializers.SerializerMethodField(read_only=True)
    job_title = serializers.CharField(source='job_application.job.title', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'employer', 'job_seeker', 'job_application', 
            'appointment_time', 'description', 'created_at', 
            'employer_name', 'company_name', 'job_seeker_name', 
            'job_title', 'status', 'job_seeker_response_message', 
            'job_seeker_response_date'
        ]
        read_only_fields = ['created_at', 'job_seeker_response_date']
    
    def get_employer_name(self, obj):
        return f"{obj.employer.first_name} {obj.employer.last_name}"
    
    def get_job_seeker_name(self, obj):
        return f"{obj.job_seeker.first_name} {obj.job_seeker.last_name}"