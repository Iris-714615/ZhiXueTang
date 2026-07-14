from django.urls import path
from . import views

app_name = 'live'

urlpatterns = [
    path('room/<str:room_id>/', views.room_info, name='room_info'),
    path('online/<str:room_id>/', views.online_count, name='online_count'),
    path('danmaku/<str:room_id>/', views.danmaku_history, name='danmaku_history'),
]
