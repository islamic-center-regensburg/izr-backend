from django.test import RequestFactory

from .serializers import CalculationMethodSerializer
from django.core.mail import EmailMessage
from .serializers import GallerySerializer, GalleryImageSerializer
from .models import CalculationMethod, Gallery, GalleryImage
import json
from pathlib import Path
from django.http import JsonResponse
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status


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


from django.conf import settings
from django.http import FileResponse, Http404


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
        serializer = self.get_serializer(
            tokens, many=True)  # Serialize the queryset
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            data=request.data)  # Deserialize input data
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


class BlogDetailAPIView(generics.ListAPIView):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer


class GalleryListCreateView(generics.ListCreateAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer


class GalleryImageListCreateView(generics.ListCreateAPIView):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer


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


@csrf_exempt
def today_prayer_times(request):
    from .prayer_times.views import get_today_prayer_times
    return get_today_prayer_times(request)


@csrf_exempt
def old_get_prayer_times(request):
    from .prayer_times.views import old_calculation
    return old_calculation(request=request)


@csrf_exempt
def new_get_prayer_times(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Extract parameters from the request
            lat = data.get("lat", None)
            lng = data.get("lng", None)
            method = data.get("method", 10)  # Default method is Qatar (ID: 10)
            period = data.get("period", "monthly")  # monthlyor annual
            # Month or year, depending on the period
            value = data.get("value", None)
            hijri = data.get("hijri", False)  # Whether to use Hijri calendar

            # Fetch the latest configuration
            config = PrayerCalculationConfig.objects.latest("id")

            # If lat/lng are not provided, use the default values
            if lat is None or lng is None:
                lat = config.default_latitude
                lng = config.default_longitude

            # If method is 99 (custom), retrieve angles and tuning parameters
            if method == 99:
                fajr_angle = config.fajr_angle
                isha_angle = config.isha_angle
                tune = True
                tuning_params = {
                    "imsak_tune": config.imsak_tune,
                    "fajr_tune": config.fajr_tune,
                    "sunrise_tune": config.sunrise_tune,
                    "dhuhr_tune": config.dhuhr_tune,
                    "asr_tune": config.asr_tune,
                    "maghrib_tune": config.maghrib_tune,
                    "sunset_tune": config.sunset_tune,
                    "isha_tune": config.isha_tune,
                    "midnight_tune": config.midnight_tune,
                }
            else:
                fajr_angle = None
                isha_angle = None
                tune = False
                tuning_params = {}

            # Validate required parameters
            if lat is None or lng is None:
                return JsonResponse({"error": "Latitude and Longitude must be provided"}, status=400)
            if period != "annual" and value is None:
                return JsonResponse({"error": "Value (month/year) must be provided for non-annual periods"}, status=400)

            # Initialize the calculator
            calculator = PrayerTimesCalculator(
                latitude=lat,
                longitude=lng,
                calculation_method=method,
                # Only used for monthly/annual calculations
                fajr_angle=fajr_angle,
                isha_angle=isha_angle,
                tune=tune,
                **tuning_params,
            )

            # Fetch prayer times based on the period
            if period == "monthly":
                year = datetime.now().year  # Use current year if not provided
                month = value
                prayer_times = calculator.fetch_monthly_prayer_times(
                    month=month, year=year, hijri=hijri)
            elif period == "annual":
                year = value
                prayer_times = calculator.fetch_annual_prayer_times(
                    year=year, hijri=hijri)
            else:
                return JsonResponse({"error": "Invalid period. Must be 'monthly' or 'annual'."}, status=400)

            return JsonResponse(prayer_times, safe=False)

        except KeyError as e:
            return JsonResponse({"error": f"Missing key: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def get_prayer_times(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # Extract parameters from the request
            city_name = data.get("city_name", "Regensburg")
            lat = data.get("lat", None)
            lng = data.get("lng", None)
            method = data.get("method", 10)  # Default method is Qatar (ID: 10)

            # If city is Regensburg and lat/lng are not provided, use default values
            if city_name.lower() == "regensburg":
                config = PrayerCalculationConfig.objects.latest("id")
                lat = config.default_latitude if lat is None else lat
                lng = config.default_longitude if lng is None else lng

            # Validate required parameters
            if lat is None or lng is None:
                return JsonResponse({"error": "Latitude and Longitude must be provided"}, status=400)

            # Determine the method to use
            calculation_method = "mwl" if method != 10 else "custom"

            # Prepare the payload for the new_get_prayer_times function
            payload = {
                "lat": lat,
                "lng": lng,
                "method": calculation_method,
                "period": "annual",
                "value": datetime.now().year,  # Current year
                "hijri": False,
            }

            factory = RequestFactory()
            new_request = factory.post(
                "/new_get_prayer_times", json.dumps(payload), content_type="application/json")
            new_request.META = request.META

            # Call the new_get_prayer_times function
            return new_get_prayer_times(new_request)

        except KeyError as e:
            return JsonResponse({"error": f"Missing key: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


class CalculationMethodListAPIView(generics.ListAPIView):
    queryset = CalculationMethod.objects.all()
    serializer_class = CalculationMethodSerializer
