from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import redirect
from django.urls import reverse
from datetime import date, datetime
import csv
from decimal import Decimal

from .models import CustomUser, CaregiverProfile, ElderlyProfile, Schedule


# Customize Django Admin branding
admin.site.site_header = "Admin Dashboard"
admin.site.site_title = "Admin Dashboard"
admin.site.index_title = "Admin Dashboard"


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
    # Payments & Rates (duration + estimated_cost) + Monitoring (status_badge)
    list_display = (
        'elderly', 'date', 'start_time', 'end_time',
        'duration', 'hourly_rate', 'estimated_cost',
        'location', 'status_badge'
    )
    search_fields = ('elderly__name', 'location', 'task_list')
    list_filter = ('date', 'location')
    date_hierarchy = 'date'  # Monitoring & Reporting

    # ---------- Payments & Rates: computed fields ----------
    def _duration_minutes(self, obj):
        start_dt = datetime.combine(obj.date, obj.start_time)
        end_dt = datetime.combine(obj.date, obj.end_time)
        delta = end_dt - start_dt
        return int(delta.total_seconds() // 60)

    def duration(self, obj):
        total_minutes = self._duration_minutes(obj)
        hours, minutes = divmod(total_minutes, 60)
        return f"{hours:02d}:{minutes:02d}"
    duration.short_description = "Duration (hh:mm)"

    def estimated_cost(self, obj):
        # hours as decimal * hourly_rate
        minutes = self._duration_minutes(obj)
        hours_decimal = Decimal(minutes) / Decimal(60)
        return (hours_decimal * obj.hourly_rate).quantize(Decimal("0.01"))
    estimated_cost.short_description = "Est. Cost"

    # ---------- Monitoring & Reporting: status badge ----------
    def status_badge(self, obj):
        if obj.date < date.today():
            color, text = "red", "Past"
        elif obj.date == date.today():
            color, text = "orange", "Today"
        else:
            color, text = "green", "Upcoming"
        return format_html('<span style="color:{}; font-weight:bold;">{}</span>', color, text)
    status_badge.short_description = "Status"

    # ---------- Payments & Rates: actions ----------
    @admin.action(description="Increase hourly rate by 10%")
    def increase_rate_10(self, request, queryset):
        updated = 0
        for sched in queryset:
            sched.hourly_rate = (sched.hourly_rate *
                                 Decimal('1.10')).quantize(Decimal('0.01'))
            sched.save(update_fields=['hourly_rate'])
            updated += 1
        self.message_user(
            request, f"Updated hourly rate for {updated} schedule(s).")

    @admin.action(description="Decrease hourly rate by 10%")
    def decrease_rate_10(self, request, queryset):
        updated = 0
        for sched in queryset:
            sched.hourly_rate = (sched.hourly_rate *
                                 Decimal('0.90')).quantize(Decimal('0.01'))
            sched.save(update_fields=['hourly_rate'])
            updated += 1
        self.message_user(
            request, f"Updated hourly rate for {updated} schedule(s).")

    @admin.action(description="Export payments CSV (with duration & estimated cost)")
    def export_payments_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="payments_report.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Elderly', 'Date', 'Start', 'End', 'Duration(hh:mm)',
            'Hourly Rate', 'Estimated Cost', 'Location', 'Tasks'
        ])
        for obj in queryset:
            dur = self.duration(obj)
            cost = self.estimated_cost(obj)
            writer.writerow([
                obj.elderly.name,
                obj.date.isoformat(),
                obj.start_time.strftime('%H:%M'),
                obj.end_time.strftime('%H:%M'),
                dur,
                str(obj.hourly_rate),
                str(cost),
                obj.location,
                obj.task_list,
            ])
        return response

    # ---------- Communication: email reminders ----------
    @admin.action(description="Send reminder email to family members")
    def send_reminder(self, request, queryset):
        for schedule in queryset:
            family = schedule.elderly.family_member
            if not family or not family.email:
                continue
            subject = f"Reminder: Schedule for {schedule.elderly.name} on {schedule.date}"
            message = (
                f"Hello {family.username},\n\n"
                f"This is a reminder for the upcoming schedule:\n\n"
                f"Elderly: {schedule.elderly.name}\n"
                f"Date: {schedule.date}\n"
                f"Time: {schedule.start_time} - {schedule.end_time}\n"
                f"Location: {schedule.location}\n"
                f"Tasks: {schedule.task_list}\n\n"
                f"Estimated Cost: {self.estimated_cost(schedule)}\n\n"
                f"Thank you."
            )
            try:
                send_mail(subject, message, getattr(
                    settings, 'DEFAULT_FROM_EMAIL', None), [family.email])
            except Exception as e:
                self.message_user(
                    request, f"Failed to email {family.email}: {e}", level="error")
        self.message_user(request, "Reminder emails processed.")

    # ---------- Redirect to admin homepage after adding a Schedule ----------
    def response_add(self, request, obj, post_url_continue=None):
        return redirect(reverse('admin:index'))

    actions = [
        'increase_rate_10',
        'decrease_rate_10',
        'export_payments_csv',
        'send_reminder',
    ]
