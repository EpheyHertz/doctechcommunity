from django.urls import path
from . import views
from django.contrib.auth.views import (
    
    PasswordResetView, 
    PasswordResetDoneView, 
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
urlpatterns = [
    path('login/', views.loginPage, name="login"),
    path('logout/', views.logoutUser, name="logout"),
    path('register/', views.registerPage, name="register"),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('follow-user/<int:user_id>/', views.follow_user, name='follow-user'),

    # Like/dislike room
    path('like-room/<int:room_id>/', views.like_room, name='like-room'),
    path('dislike-room/<int:room_id>/', views.dislike_room, name='dislike-room'),

    # Like/dislike message
    path('like-message/<int:message_id>/', views.like_message, name='like-message'),
    path('dislike-message/<int:message_id>/', views.dislike_message, name='dislike-message'),
    
    path('password-reset/', PasswordResetView.as_view(template_name='registration/password_reset.html',
                                                      html_email_template_name='registration/password_reset_email.html'),name='password_reset'),

    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),name='password_reset_complete'),
    path('', views.home, name="home"),
    path('room/<str:pk>/', views.room, name="room"),
    path('profile/<str:pk>/', views.userProfile, name="user-profile"),

    path('create-room/', views.createRoom, name="create-room"),
    path('update-room/<str:pk>/', views.updateRoom, name="update-room"),
    path('delete-room/<str:pk>/', views.deleteRoom, name="delete-room"),
    path('delete-message/<str:pk>/', views.deleteMessage, name="delete-message"),

    path('update-user/', views.updateUser, name="update-user"),

    path('topics/', views.topicsPage, name="topics"),
    path('activity/', views.activityPage, name="activity"),
]
