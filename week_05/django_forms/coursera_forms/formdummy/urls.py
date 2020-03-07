from django.urls import path
from . import views

urlpatterns = [
    path('form/', views.FormDummyView.as_view()),
    path('schema/', views.SchemaView.as_view()),
]
