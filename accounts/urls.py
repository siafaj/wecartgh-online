from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', views.dashboard, name='dashboard'),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_validate, name='reset_password_validate'),
    path('reset-password/', views.reset_password, name='reset_password'),

    path('my-orders/', views.my_orders, name='my_orders'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
]