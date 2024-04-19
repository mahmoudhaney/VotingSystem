from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import JWTLoginView, SignupView, PasswordChangeView, UserProfileView

app_name = 'users'

password_urls = [
    path('change/', PasswordChangeView.as_view(), name='password_change'),
    path('reset/', include('django_rest_passwordreset.urls', namespace='reset')),
]

auth_urls = [
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', JWTLoginView.as_view(), name='login'),
    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('password/', include(password_urls))
]

urlpatterns = [
    path('auth/', include(auth_urls)),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]