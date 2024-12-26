from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from .models import User, Address, SubjectGrade, Credential, FollowRelation, Review, Level, Thread, ThreadParticipant, Message

# User Admin
# class CustomUserAdmin(UserAdmin):
#     list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_tutor')
#     list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_tutor')
#     fieldsets = UserAdmin.fieldsets + (
#         ('Additional Info', {'fields': ('nickname', 'phone_number', 'birthdate', 'bio', 'profile_image', 'role', 'is_tutor')}),
#     )
#     add_fieldsets = UserAdmin.add_fieldsets + (
#         ('Additional Info', {'fields': ('nickname', 'phone_number', 'birthdate', 'bio', 'profile_image', 'role', 'is_tutor')}),
#     )

# # Register models
# admin.site.register(User, CustomUserAdmin)
# admin.site.register(Address)
# admin.site.register(SubjectGrade)
# admin.site.register(Credential)
# admin.site.register(FollowRelation)
# admin.site.register(Review)
# admin.site.register(Level)
# admin.site.register(Thread)
# admin.site.register(ThreadParticipant)
# admin.site.register(Message)