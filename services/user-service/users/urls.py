from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import SimpleRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from . import views


router = SimpleRouter()
router.register('permissions', views.PermissionView, basename='permissions')
router.register('roles', views.RoleView, basename='roles')
router.register('', views.UserReadOnlyView, basename='read_users')

app_name = 'users'
urlpatterns = [
    path('health/', views.HealthCheckView.as_view(), name='health'),
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('token/', views.TokenView.as_view(), name='token'),
    path('me/', views.MeView.as_view(), name='me'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('<int:pk>/update/', views.UserUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.UserDestroyView.as_view(), name='delete'),
    path('create/', views.UserCreateView.as_view(), name='create'),

    # API guide
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    # UI
    path('docs/', SpectacularSwaggerView.as_view(url_name='users:schema'), name='docs'),
    path('redoc/', SpectacularRedocView.as_view(url_name='users:schema'), name='redoc'),

    #
    path('', include(router.urls)),
]
