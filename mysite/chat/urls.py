from django.urls import path
from . import views

app_name = "chat"
urlpatterns = [
    path('', views.lobby, name='lobby'),
    path('updateSession/', views.update_session, name="update-session")
]
