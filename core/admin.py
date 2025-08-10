# core/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, CaregiverProfile, ElderlyProfile, Schedule


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'role')}),
        ('Permissions', {'fields': ('is_staff',
         'is_active', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'role', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )


@admin.register(CaregiverProfile)
class CaregiverProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'phone', 'gender',
                    'dob', 'emergency_contact')
    search_fields = ('name', 'phone', 'user__email')
    list_filter = ('gender',)


@admin.register(ElderlyProfile)
class ElderlyProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'family_member', 'gender', 'dob', 'location')
    search_fields = ('name', 'family_member__email', 'location')
    list_filter = ('gender', 'location')


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('elderly', 'date', 'start_time',
                    'end_time', 'location', 'hourly_rate')
    search_fields = ('elderly__name', 'location', 'task_list')
    list_filter = ('date', 'location')
