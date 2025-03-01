
from .old_calculation import OldPrayerTimesCalculator
from .calculation import PrayerTimesCalculator
import json
from django.http import JsonResponse
from ..models import (
    PrayerCalculationConfig,
)

from datetime import datetime


def old_calculation(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            print(data)

            city_name = data.get("city_name", "Regensburg")
            lat = data.get("lat", None)
            lng = data.get("lng", None)
            start_date = data.get("start_date", None)
            end_date = data.get("end_date", None)
            method = data.get("method", 10)
            if end_date and start_date:
                start_date = f"{start_date["y"]}-{start_date["m"]}-{start_date["d"]}"
                end_date = f"{end_date["y"]}-{end_date["m"]}-{end_date["d"]}"

            if city_name.lower() == "regensburg":
                lat = PrayerCalculationConfig.objects.latest(
                    "id").default_latitude if lat is None else lat
                lng = PrayerCalculationConfig.objects.latest(
                    "id").default_longitude if lng is None else lng

            if lat is None or lng is None:
                return JsonResponse({"error": "Latitude and Longitude must be provided"}, status=400)
            if start_date is None or end_date is None:
                return JsonResponse({"error": "Start date and End date must be provided"}, status=400)

            calculator = OldPrayerTimesCalculator(
                start_date, end_date, lng, lat, method)
            prayer_times = calculator.get_prayer_times()

            return JsonResponse(prayer_times, safe=False)

        except KeyError as e:
            return JsonResponse({"error": f"Missing key: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


def get_today_prayer_times(request):
    if request.method == "GET":
        today = datetime.now().strftime("%Y-%m-%d")

        # Fetch the latest configuration
        config = PrayerCalculationConfig.objects.latest("id")

        # Extract parameters from the configuration
        lat = config.default_latitude
        lng = config.default_longitude
        isha_angle = config.isha_angle
        fajr_angle = config.fajr_angle
        imsak_tune = config.imsak_tune
        fajr_tune = config.fajr_tune
        sunrise_tune = config.sunrise_tune
        dhuhr_tune = config.dhuhr_tune
        asr_tune = config.asr_tune
        maghrib_tune = config.maghrib_tune
        sunset_tune = config.sunset_tune
        isha_tune = config.isha_tune
        midnight_tune = config.midnight_tune

        # Initialize the calculator with all parameters
        calculator = PrayerTimesCalculator(
            latitude=lat,
            longitude=lng,
            calculation_method="custom",  # Or fetch this from config if needed
            fajr_angle=fajr_angle,
            isha_angle=isha_angle,
            tune=True,  # Enable tuning
            imsak_tune=imsak_tune,
            fajr_tune=fajr_tune,
            sunrise_tune=sunrise_tune,
            dhuhr_tune=dhuhr_tune,
            asr_tune=asr_tune,
            maghrib_tune=maghrib_tune,
            sunset_tune=sunset_tune,
            isha_tune=isha_tune,
            midnight_tune=midnight_tune,
        )

        # Fetch prayer times
        prayer_times = calculator.fetch_daily_prayer_times(today)

        # Return the response
        response = JsonResponse(prayer_times, safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
