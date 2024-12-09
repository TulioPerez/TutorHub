from django.utils.html import format_html
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, SubjectGrade, Credential


class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'nickname', 'is_tutor', 'city', 'state', 'zip_code', 'date_joined')
    list_filter = ('is_tutor', 'is_active', 'date_joined')
    search_fields = ('email', 'nickname', 'city', 'state')
    ordering = ('-date_joined',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('nickname', 'first_name', 'last_name', 'bio', 'profile_image', 'birthdate')}),
        ('Address', {'fields': ('street_address', 'city', 'state', 'zip_code')}),
        ('Tutor Details', {'fields': ('is_tutor', 'availability', 'subject_grades')}),
        ('Credentials', {'fields': ()}),  # Placeholder for credentials
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    def credentials_list(self, obj):
        """List all credentials uploaded by the user."""
        credentials = obj.credentials.all()
        if credentials.exists():
            return format_html(
                '<br>'.join([f'<a href="{cred.file.url}" target="_blank">{cred.file.name}</a>' for cred in credentials])
            )
        return "No credentials"

    readonly_fields = ('credentials_list',)


# Register SubjectGrade and Credential for the admin interface
class SubjectGradeAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'subject', 'grade_levels')
    search_fields = ('subject',)
    list_filter = ('subject',)


class CredentialAdmin(admin.ModelAdmin):
    list_display = ('user', 'file')
    search_fields = ('user__email',)


# Register models in the admin site
admin.site.register(User, UserAdmin)
admin.site.register(SubjectGrade, SubjectGradeAdmin)
admin.site.register(Credential, CredentialAdmin)
