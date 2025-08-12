
from django.urls import path
from . import views


urlpatterns = [
    path('', views.redirect_to_login),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('caregiver-dashboard/', views.caregiver_dashboard, name='caregiver_dashboard'),
    path('caregiver/create-profile/', views.create_caregiver_profile, name='create_caregiver_profile'),
    path('caregiver/confirm/<int:elderly_id>/', views.confirm_caregiving, name='confirm_caregiving'),
    path('family-dashboard/', views.family_dashboard, name='family_dashboard'),
    path('family/create-elderly/', views.create_elderly_profile, name='create_elderly_profile'),
    path('family/set-schedule/', views.set_schedule, name='set_schedule'),
    path("set_schedule/", views.set_schedule, name="set_schedule"),
    path("list_of_people_with_schedules/", views.list_of_people_with_schedules, name="list_of_people_with_schedules"),
    path("confirm_caregiving/<int:schedule_id>/", views.confirm_caregiving, name="confirm_caregiving"),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
   

]

