import json
from pathlib import Path
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser


from .models import (
    Blog,
    Event,
    Hadith,
    PrayerConfig,
    Statement,
    Token,
    PrayerCalculationConfig,
)
from .serializers import (
    BlogSerializer,
    EventSerializer,
    HadithSerializer,
    StatementSerializer,
    TokenSerializer,
    PrayerConfigSerializer,
)
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime


import os
from django.conf import settings
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404


from izr_media.calculation import (
    run_calculations,
)  # Replace with the actual path of the function


class EventViewSet(generics.ListAPIView):
    serializer_class = EventSerializer

    def get_queryset(self):
        # Only return events where enabled is True
        return Event.objects.filter(enabled=True)

    def list(self, request, *args, **kwargs):
        # Call the parent method to get the default response
        response = super().list(request, *args, **kwargs)

        # Modify the response data to wrap it in a custom key
        return Response({"events": response.data})


class HadithDetailView(generics.RetrieveAPIView):
    serializer_class = HadithSerializer

    def get(self, request, *args, **kwargs):
        hadith = Hadith.objects.first()
        if not hadith:
            return JsonResponse({"detail": "Hadith not found."}, status=404)

        serializer = self.get_serializer(hadith)
        response = JsonResponse(serializer.data)
        response["Access-Control-Allow-Origin"] = "*"
        return response


class TokenListCreateView(generics.ListCreateAPIView):
    queryset = Token.objects.all()  # Queryset for retrieving tokens
    serializer_class = TokenSerializer  # Use the TokenSerializer

    def get(self, request, *args, **kwargs):
        tokens = self.get_queryset()  # Retrieve all tokens
        serializer = self.get_serializer(tokens, many=True)  # Serialize the queryset
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)  # Deserialize input data
        if serializer.is_valid():  # Validate the input data
            token = serializer.save()  # Create a new token instance
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )  # Respond with created token data
        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Respond with errors


class PrayerConfigView(generics.ListAPIView):
    queryset = PrayerConfig.objects.all()
    serializer_class = PrayerConfigSerializer


class StatementView(generics.ListAPIView):
    queryset = Statement.objects.all()
    serializer_class = StatementSerializer


@csrf_exempt
def get_today_prayer_times(request):
    if request.method == "GET":
        # Get today's date
        today = datetime.now()

        # Prepare the start and end date as dictionaries
        start_date = {"y": today.year, "m": today.month, "d": today.day}
        end_date = {"y": today.year, "m": today.month, "d": today.day}

        # Run the calculation for today's prayer times
        lat = PrayerCalculationConfig.objects.latest("id").default_latitude
        lng = PrayerCalculationConfig.objects.latest("id").default_longitude

        prayer_times = run_calculations(
            lat=lat,
            lon=lng,
            start_date=start_date,
            end_date=end_date,
        )

        # Return the result as JSON
        response = JsonResponse(prayer_times[0], safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        return JsonResponse(prayer_times[0], safe=False)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def get_prayer_times(request):
    if request.method == "POST":
        try:
            # Parse the request body
            data = json.loads(request.body)

            # Extract the parameters
            city_name = data.get("city_name", "Regensburg")
            lat = data.get("lat", None)
            lng = data.get("lng", None)
            start_date = data.get("start_date", None)
            end_date = data.get("end_date", None)
            method = data.get("method", 10)  # Default method is 6
            offset = data.get("offset", None)

            # Default latitude and longitude for Regensburg
            if city_name.lower() == "regensburg":
                lat = (
                    PrayerCalculationConfig.objects.latest("id").default_latitude
                    if lat is None
                    else lat
                )
                lng = (
                    PrayerCalculationConfig.objects.latest("id").default_longitude
                    if lng is None
                    else lng
                )

            # If latitude or longitude are not provided
            if lat is None or lng is None:
                return JsonResponse(
                    {"error": "Latitude and Longitude must be provided"}, status=400
                )
            if start_date is None or end_date is None:
                return JsonResponse(
                    {"error": "Latitude and Longitude must be provided"}, status=400
                )

            # Run the calculations
            prayer_times = run_calculations(
                lon=lng,
                lat=lat,
                start_date=start_date,
                end_date=end_date,
                method=method,
                tzone="Europe/Berlin",  # Timezone can be dynamic based on the city, but set to Berlin as default
            )

            # Return the result as JSON
            return JsonResponse(prayer_times, safe=False)

        except KeyError as e:
            return JsonResponse({"error": f"Missing key: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


class BlogDetailAPIView(generics.ListAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer


def download_latest_backup(request):
    db = Path(settings.BASE_DIR) / "db.sqlite3"
    print(db)
    try:
        if not db.exists():
            raise Http404("No backup found.")

        return FileResponse(
            db.open("rb"), as_attachment=True, filename="db_latest.sqlite3"
        )

    except FileNotFoundError:
        raise Http404("Backup directory not found.")


from .models import Gallery, GalleryImage
from .serializers import GallerySerializer, GalleryImageSerializer


class GalleryListCreateView(generics.ListCreateAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer


class GalleryImageListCreateView(generics.ListCreateAPIView):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer


from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt  # Only use in development, in production use a CSRF token.
def send_email_post(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            subject = data.get("subject", "No Subject")
            message = data.get("message", "No Message")
            recipient = data.get("recipient")

            if not recipient:
                return JsonResponse(
                    {"error": "Recipient email is required"}, status=400
                )

            # Create and send the email
            email = EmailMessage(
                subject=subject,
                body=message,
                from_email="izrserver2@gmail.com",  # Replace with your sender email
                to=[recipient],
            )

            email.send()
            return JsonResponse({"message": "Email sent successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
