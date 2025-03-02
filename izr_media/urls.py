from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BlogDetailAPIView,
    CalculationMethodListAPIView,
    EventViewSet,
    GalleryListCreateView,
    HadithDetailView,
    PrayerConfigView,
    TokenListCreateView,
    today_prayer_times,
    StatementView,
    send_email_post,
    old_get_prayer_times,
    prayer_times
)


urlpatterns = [
    path("getEvents/all", EventViewSet.as_view(), name="event-list"),
    path("statement", StatementView.as_view(), name="event-list"),
    path(
        "hadith/", HadithDetailView.as_view(), name="single-hadith"
    ),  # Access Hadith without an ID
    path("pushtokens/", TokenListCreateView.as_view(), name="token-list-create"),
    path(
        "getPrayers/", today_prayer_times, name="get_prayer_times"
    ),  # Add this line
    path("blog/", BlogDetailAPIView.as_view(), name="blog_detail_api"),
    path("galleries/", GalleryListCreateView.as_view(), name="gallery-list"),
    path("iqamah/", PrayerConfigView.as_view(), name="prayer-config"),
    path("calculTimes/", old_get_prayer_times,
         name="get_prayer_times"),  # Add this line
    path("send_email/", send_email_post, name="send_email_post"),
    path("calculation-methods/", CalculationMethodListAPIView.as_view(),
         name="calculation-methods-list"),
    path("prayer-times", prayer_times, name="monthly-prayer-times")

]
