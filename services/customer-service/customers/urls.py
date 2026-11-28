from django.urls import path

from . import views


app_name = 'customers'
urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health')
]
