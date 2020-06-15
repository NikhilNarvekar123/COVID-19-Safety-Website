from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('home/', views.home, name = 'home-explicit'),
    path('create-profile/', views.newProf, name = 'create-profile'),
    path('sign-in/', views.signIn, name = 'sign-in'),
    path('profile/', views.profile, name = 'profile'),
    path('about/', views.about, name = 'about'),
    path('logout/', views.logout, name = 'logout'),
    path('tracker/', views.tracker, name = 'tracker'),
    path('initiate/', views.initiateTracker, name = 'initiate'),
    path('suspend/', views.suspendTracker, name = 'suspend'),
    path('update/', views.updateTracker, name = 'update'),
    path('password-reset/', views.passwordReset, name = 'password-reset')
]
