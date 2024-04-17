from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from .views import JWTLoginView, SignupView, PasswordChangeView

app_name = 'users'

password_urls = [
    path('change/', PasswordChangeView.as_view()),
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
]