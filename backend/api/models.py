from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        # Displays only the file name, not the full path
        return self.file.name.split('/')[-1]


class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    birthdate = models.DateField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True, default="profile_pictures/place_holder.png")
    cv = models.FileField(upload_to='cvs/', blank=True, null=True)
    additional_documents = models.ManyToManyField(Document, blank=True, related_name='jobseeker_profiles')
    is_premium = models.BooleanField(default=False)
    premium_since = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"JobSeeker: {self.user.username}"


class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    birthdate = models.DateField()
    company_name = models.CharField(max_length=255)
    company_address = models.CharField(max_length=255)
    company_postal_code = models.CharField(max_length=20)
    company_city = models.CharField(max_length=100)
    company_phone = models.CharField(max_length=20)
    company_logo = models.ImageField(upload_to="company_logos/", blank=True, null=True,default="company_logos/place_holder.png")
    is_premium = models.BooleanField(default=False)
    premium_since = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Employer: {self.user.username} ({self.company_name})"


class JobPost(models.Model):
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100)
    salary_min = models.DecimalField(max_digits=10, decimal_places=2)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2)
    years_experience = models.PositiveIntegerField()
    company_name = models.CharField(max_length=200)
    company_logo = models.ImageField(upload_to="company_logos/", blank=True, null=True,default="company_logos/place_holder.png")
    is_visible = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"
    

class JobApplication(models.Model):
    STATUS_CHOICES = [
        ('received', 'Received'),
        ('in_progress', 'In Progress'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
        
    job = models.ForeignKey("JobPost", on_delete=models.CASCADE, related_name="applications")
    candidate = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    cover_letter_file = models.FileField(upload_to="cover_letters/", blank=True, null=True)
    cv_file = models.FileField(upload_to="cvs/", blank=True, null=True)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='received')
    status_updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.candidate.user.username} -> {self.job.title}"
    


class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    application = models.ForeignKey('JobApplication', on_delete=models.CASCADE, related_name='messages')
    subject = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f'Message from {self.sender.username} on {self.application.id}'


class SystemReview(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='system_reviews')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    job_search_effectiveness = models.IntegerField(choices=RATING_CHOICES)
    application_process_simplicity = models.IntegerField(choices=RATING_CHOICES)
    message_system_effectiveness = models.IntegerField(choices=RATING_CHOICES)
    ease_of_navigation = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # A user can only give one review on the system
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_system_review_per_user')
        ]

    def __str__(self):
        return f"System review by {self.user.username} - {self.rating}/5"

class JobApplicationStatusHistory(models.Model):
    application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="status_history")
    status = models.CharField(max_length=20, choices=JobApplication.STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        

class JobFavorite(models.Model):
    job_seeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name="favorites")
    job_post = models.ForeignKey(JobPost, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job_seeker', 'job_post')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.job_seeker.user.username} - {self.job_post.title}"
    
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Accepté'),
        ('rejected', 'Refusé')
    ]
    
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE, related_name="appointments")
    job_seeker = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name="appointments")
    job_application = models.ForeignKey(JobApplication, on_delete=models.CASCADE, related_name="appointments")
    appointment_time = models.DateTimeField()
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    job_seeker_response_message = models.TextField(blank=True, null=True)
    job_seeker_response_date = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Appointment: {self.job_seeker.user.username} with {self.employer.user.username} on {self.appointment_time} ({self.status})"