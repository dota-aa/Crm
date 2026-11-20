from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from . import views


app_name = 'users'
urlpatterns = [
    path('health/', views.HealthCheckView.as_view()),
    path('register/', views.UserRegistrationView.as_view()),
    path('token/', views.TokenView.as_view()),
    path('/token/refresh/', TokenRefreshView.as_view()),
]
