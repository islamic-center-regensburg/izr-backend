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
        # Only return events where enabled is True, ordered in reverse
        # Reverse order by ID
        return Event.objects.filter(enabled=True).order_by("-id")

    def list(self, request, *args, **kwargs):
        # Call the parent method to get the default response
        response = super().list(request, *args, **kwargs)

        # Reverse the response data list before returning
        return Response({"events": list(response.data)})


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
    def perform_update(self, serializer):
        instance = serializer.save()
        # 👇 After saving, refresh Redis
        redis_client = settings.REDIS_CLIENT
        pattern = "prayer_times:regensburg:*:static"
        keys = redis_client.keys(pattern)

        for key in keys:
            redis_client.delete(key)


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
def prayer_times(request):
    from .prayer_times.views import get_prayer_times

    return get_prayer_times(request)


@csrf_exempt
def today_prayer_times(request):
    from .prayer_times.views import get_today_prayer_times

    return get_today_prayer_times(request)


@csrf_exempt
def old_get_prayer_times(request):
    from .prayer_times.views import old_calculation
    return old_calculation(request=request)


class CalculationMethodListAPIView(generics.ListAPIView):
    queryset = CalculationMethod.objects.all()
    serializer_class = CalculationMethodSerializer
