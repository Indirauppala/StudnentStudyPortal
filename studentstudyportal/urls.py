from django.contrib import admin
from django.urls import path, include
from dashboard import views as dash_views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),  # Include your app-specific URLs
    path('register/', dash_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name="dashboard/login.html"), name='login'),
    path('', dash_views.home, name='home'),
    path('profile/', dash_views.profile, name='profile'),

]
