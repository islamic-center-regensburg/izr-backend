# urls.py

from django.urls import path
from .views import PersonDetailView, PersonListCreateView

urlpatterns = [
    path("persons/", PersonListCreateView.as_view(), name="person-list-create"),
    path("persons/<int:pk>/", PersonDetailView.as_view(), name="person-detail"),
]
