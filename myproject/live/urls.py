from django.urls import path
from . import views

app_name = 'live'

urlpatterns = [
    path('room/<str:room_id>/', views.room_info, name='room_info'),
]
