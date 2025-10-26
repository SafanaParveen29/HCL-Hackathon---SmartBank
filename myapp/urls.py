from django.urls import path
from .import views

urlpatterns = [
    path('User-Register/',views.UserRegister, name='UserRegister'),    
    path('KYC-Update/',views.KYC_update, name='KYC_update'),    
    path('User-login/',views.user_login, name='user_login'),    
    path('user_logout/',views.user_logout, name='user_logout'),    
    path('',views.user_dashboard, name='user_dashboard'),    
    path('Request-Account',views.request_account, name='request_account'),
    path('View-Account',views.view_account, name='view_account'),
]