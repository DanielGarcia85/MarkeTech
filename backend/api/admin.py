from django.contrib import admin
from .models import Message, JobPost, JobSeekerProfile, EmployerProfile, SystemReview, JobApplication, Document, Appointment
from django.contrib.auth.models import Group, User
from django.contrib.auth.admin import GroupAdmin as DefaultGroupAdmin, UserAdmin as DefaultUserAdmin
from django.utils.html import format_html, format_html_join


admin.site.unregister(Group)
@admin.register(Group)
class CustomGroupAdmin(DefaultGroupAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_list_filter(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_search_fields(self, request):
        return [field.name for field in self.model._meta.fields if field.get_internal_type() in ['CharField', 'TextField', 'EmailField']]
    ordering = ('id',)
    

admin.site.unregister(User)
@admin.register(User)
class CustomUserAdmin(DefaultUserAdmin):
    list_display = ('id','username','email','first_name','last_name','display_groups','is_active','is_staff','is_superuser','last_login','date_joined')
    list_filter = ('id','username','email','first_name','last_name','is_active','is_staff','is_superuser','last_login','date_joined')
    search_fields = ('id','username','email','first_name','last_name','is_active','is_staff','is_superuser','last_login','date_joined')
    def display_groups(self, obj):
        return ", ".join([group.name for group in obj.groups.all()]) or '-'
    display_groups.short_description = 'Groups'
    ordering = ('id',)


@admin.register(Message)
class MessageModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_list_filter(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_search_fields(self, request):
        return [field.name for field in self.model._meta.fields if field.get_internal_type() in ['CharField', 'TextField', 'EmailField']]
    ordering = ('id',)


@admin.register(JobSeekerProfile)
class JobSeekerProfilModeleAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields] + ['document_links']
    def get_list_filter(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_search_fields(self, request):
        return [field.name for field in self.model._meta.fields if field.get_internal_type() in ['CharField', 'TextField', 'EmailField']]
    def document_links(self, obj):
        """ Display links to additional documents """
        documents = obj.additional_documents.all()
        if not documents:
            return "-"
        links = format_html_join(
            '\n',
            '<a href="{}" target="_blank">{}</a>',
            ((doc.file.url, doc.file.name.split('/')[-1]) for doc in documents)
        )
        return links
    document_links.short_description = "Documents"
    ordering = ('id',)


@admin.register(Document)
class DocumentModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_list_filter(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_search_fields(self, request):
        return [field.name for field in self.model._meta.fields if field.get_internal_type() in ['CharField', 'TextField']]
    ordering = ('id',)


@admin.register(EmployerProfile)
class EmployerProfileModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_list_filter(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_search_fields(self, request):
        return [field.name for field in self.model._meta.fields if field.get_internal_type() in ['CharField', 'TextField', 'EmailField']]
    ordering = ('id',)
    

@admin.register(JobPost)
class JobPostModelAdmin(admin.ModelAdmin):
       def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
       def get_list_filter(self, request):
        return [field.name for field in self.model._meta.fields]
       def get_search_fields(self, request):
        return [
            field.name for field in self.model._meta.fields if field.get_internal_type() in ['CharField', 'TextField', 'EmailField']]
       ordering = ('id',)


@admin.register(SystemReview)
class SystemReviewModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_list_filter(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_search_fields(self, request):
        return [
            field.name for field in self.model._meta.fields if field.get_internal_type() in ['CharField', 'TextField', 'EmailField']]
    ordering = ('id',)


@admin.register(JobApplication)
class JobApplicationModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_list_filter(self, request):
        return [field.name for field in self.model._meta.fields]
    def get_search_fields(self, request):
        return [
            field.name for field in self.model._meta.fields if field.get_internal_type() in ['CharField', 'TextField', 'EmailField']]
    ordering = ('id',)

@admin.register(Appointment)
class AppointmentModelAdmin(admin.ModelAdmin):
    def get_list_display(self, request):
        return [field.name for field in self.model._meta.fields] 
    
    def get_list_filter(self, request):
        return ['employer', 'job_seeker', 'appointment_time', 'created_at', 'job_application']
    
    def get_search_fields(self, request):
        return ['description', 'employer__user__username', 'job_seeker__user__username']
    
    ordering = ('-appointment_time',)
    date_hierarchy = 'appointment_time'
    list_per_page = 20
    
