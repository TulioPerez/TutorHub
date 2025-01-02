from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Address, SubjectLevel, Credential, FollowRelation, Review, Level, Thread, ThreadParticipant, Message

# User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_tutor')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_tutor', 'role')
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('nickname', 'role', 'phone_number', 'birthdate', 'bio', 'profile_image', 'is_tutor', 
                       'show_address', 'show_phone_number')
        }),
        ('Localization', {'fields': ('preferred_language', 'time_zone')}),
        ('Address', {'fields': ('address',)}),
        ('Tutor Specific', {'fields': ('availability',)}),  # Removed subject_levels
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {
            'fields': ('nickname', 'role', 'phone_number', 'birthdate', 'bio', 'profile_image', 'is_tutor', 
                       'show_address', 'show_phone_number')
        }),
        ('Localization', {'fields': ('preferred_language', 'time_zone')}),
        ('Address', {'fields': ('address',)}),
        ('Tutor Specific', {'fields': ('availability',)}),  # Removed subject_levels
    )


# Address Admin
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street_address', 'city', 'state_region', 'postal_code', 'country')
    search_fields = ('street_address', 'city', 'state_region', 'postal_code', 'country')

class SubjectLevelAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'subject', 'level')
    list_filter = ('tutor', 'subject', 'level')
    search_fields = ('tutor__username', 'tutor__email', 'subject')

    def display_levels(self, obj):
        return obj.level
    display_levels.short_description = 'Levels'


# Credential Admin
class CredentialAdmin(admin.ModelAdmin):
    list_display = ('user', 'credential_type')
    list_filter = ('credential_type',)
    search_fields = ('user__username', 'user__email', 'credential_type')

# FollowRelation Admin
class FollowRelationAdmin(admin.ModelAdmin):
    list_display = ('follower', 'followee', 'is_blocked')
    list_filter = ('is_blocked',)

# Review Admin
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('tutor', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')

# Level Admin
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)

# Thread Admin
class ThreadAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_group', 'created_at')
    filter_horizontal = ('participants',)

# ThreadParticipant Admin
class ThreadParticipantAdmin(admin.ModelAdmin):
    list_display = ('thread', 'user', 'role', 'joined_at')
    list_filter = ('role', 'joined_at')

# Message Admin
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'read', 'edited', 'deleted')
    list_filter = ('read', 'edited', 'deleted', 'timestamp')
    search_fields = ('content', 'sender__username', 'receiver__username')

# Register models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Address, AddressAdmin)
admin.site.register(SubjectLevel, SubjectLevelAdmin)
admin.site.register(Credential, CredentialAdmin)
admin.site.register(FollowRelation, FollowRelationAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(ThreadParticipant, ThreadParticipantAdmin)
admin.site.register(Message, MessageAdmin)
