from django.urls import path
from .views import index_izr_screen, index_izr_website, index_sarah_website

urlpatterns = [
    path("sarahfoudhaili/", index_sarah_website, name="sarahfoudhaili-index"),
    path(
        "sarahfoudhaili/<path:resource>",
        index_sarah_website,
        name="sarahfoudhaili-index-routes",
    ),  # Catch-all route for Reactpath("sarahfoudhaili/", index, name="index"),
    path("izr/", index_izr_website, name="izr-index"),  # Catch-all route for React
    path("izr/<path:resource>", index_izr_website, name="izr-index-routes"),
    path(
        "izr_screen/", index_izr_screen, name="izr-screen-index"
    ),  # Catch-all route for React
    path(
        "izr_screen/<path:resource>", index_izr_screen, name="izr-screen-index-routes"
    ),  # Catch-all route for React
]
