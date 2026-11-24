from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import SimpleRouter

from . import views


router = SimpleRouter()
router.register('permissions', views.PermissionView)
router.register('roles', views.RoleView)
router.register('', views.UserReadOnlyView)

app_name = 'users'
urlpatterns = [
    path('health/', views.HealthCheckView.as_view()),
    path('register/', views.UserRegistrationView.as_view()),
    path('token/', views.TokenView.as_view()),
    path('me/', views.MeView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('<int:pk>/update/', views.UserUpdateView.as_view()),
    path('<int:pk>/delete/', views.UserDestroyView.as_view()),
    path('create/', views.UserCreateView.as_view()),
    path('', include(router.urls)),
]
