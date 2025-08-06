
from django.urls import path
from . import views

urlpatterns = [
    path('', views.redirect_to_login),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
]
