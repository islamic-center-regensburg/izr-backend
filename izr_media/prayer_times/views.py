from pathlib import Path
from django.conf import settings
import numpy as np
from .old_calculation import OldPrayerTimesCalculator
from .calculation import PrayerTimesCalculator
import json
from django.http import JsonResponse
from ..models import (
    PrayerCalculationConfig,
)
import redis
import pandas as pd
from datetime import datetime
from .angles import get_regensburg_angles
from hijri_converter import Hijri, Gregorian

def old_calculation(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            print(data)

            config = PrayerCalculationConfig.objects.latest("id")
            calculation_type = config.calculation_type
            city_name = data.get("city_name", "Regensburg")
            lat = data.get("lat", None)
            lng = data.get("lng", None)

            if city_name.lower() == "regensburg":
                method = 'izr'
                lat = config.default_latitude
                lng = config.default_longitude
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
                method = "mwl"

            # Validate required parameters
            if lat is None or lng is None:
                return JsonResponse(
                    {"error": "Latitude and Longitude must be provided"}, status=400
                )
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

            current_year = datetime.now().year
            print("current year :",current_year)
            redis_client = settings.REDIS_CLIENT
            redis_key = f"prayer_times:{city_name.lower()}:{current_year}:{calculation_type}"

            
            cached_data = redis_client.get(redis_key)
            if cached_data:
                data = json.loads(cached_data)
                return JsonResponse(data, safe=False)

            prayer_times = calculator.fetch_annual_prayer_times(
                year=current_year, hijri=False
            )
            
            # --- 📘 Read CSV data for smoothed Fajr/Isha for Regensburg ---
            if city_name.lower() == 'regensburg' and  calculation_type != 'static':
                csv_path = Path(__file__).parent / "prayer-times-isha-fajr-fourier-fit.csv"
                prayer_df = pd.DataFrame(prayer_times)
                prayer_df["Day"] = np.arange(1, len(prayer_df) + 1)
                csv_df = pd.read_csv(csv_path,delimiter=";")
                print(csv_df.columns.tolist())
                print(csv_df.head(1))
                if {"Day", "Fajr", "Isha"} <= set(csv_df.columns):
                    print("here changin columns")

                    merged = prayer_df.merge(
                        csv_df[["Day", "Fajr", "Isha"]],
                        on="Day",
                        how="left",
                        suffixes=('', '_csv')
                    )

                    # Replace Fajr and Isha with CSV values when available
                    merged["Fajr"] = merged["Fajr_csv"].fillna(merged["Fajr"])
                    merged["Isha"] = merged["Isha_csv"].fillna(merged["Isha"])

                    # Drop helper columns
                    merged = merged.drop(columns=["Fajr_csv", "Isha_csv"])

                    prayer_times = merged.to_dict(orient="records")

            # --- 🧠 Store to Redis until end of the year ---
            end_of_year = datetime(current_year, 12, 31, 23, 59, 59)
            seconds_to_expire = int((end_of_year - datetime.now()).total_seconds())
            redis_client.setex(redis_key, seconds_to_expire, json.dumps(prayer_times))
            print(f"✅ Cached prayer times in Redis (expires end of {current_year})")
            
            cached_data = redis_client.get(redis_key)
            
            if cached_data:
                print("✅ Returning cached prayer times from Redis")
                return JsonResponse(json.loads(cached_data), safe=False)
            
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
        angles = get_regensburg_angles()
        # Fetch the latest configuration
        config = PrayerCalculationConfig.objects.latest("id")

        # Extract parameters from the configuration
        lat = config.default_latitude
        lng = config.default_longitude
        isha_angle = angles["isha_angle"]
        fajr_angle = angles["fajr_angle"]
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
            calculation_method="izr",  # Or fetch this from config if needed
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
        prayer_times["Jumaa"] = str(config.jumaa_time)[:5]

        if config.ramadan == "on":
            prayer_times["Tarawih"] = str(config.tarawih_time)[:5]

        # Return the response
        response = JsonResponse(prayer_times, safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


def get_prayer_times(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            config = PrayerCalculationConfig.objects.latest("id")

            # Extract parameters from the request
            lat = data.get("lat", config.default_latitude)
            lng = data.get("lng", config.default_longitude)
            # Default method is Qatar (ID: 10)
            method = data.get("method", "izr")
            period = data.get("period", "monthly")  # monthlyor annual
            # Month or year, depending on the period
            value = data.get("value", None)
            hijri = data.get("hijri", False)  # Whether to use Hijri calendar

            # If method is 99 (custom), retrieve angles and tuning parameters
            if method == "izr":
                angles = get_regensburg_angles()
                fajr_angle = angles["fajr_angle"]
                isha_angle = angles["isha_angle"]
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
                return JsonResponse(
                    {"error": "Latitude and Longitude must be provided"}, status=400
                )
            if period != "annual" and value is None:
                return JsonResponse(
                    {
                        "error": "Value (month/year) must be provided for non-annual periods"
                    },
                    status=400,
                )

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
                if hijri:
                    year = Gregorian(year, 1, 1).to_hijri().year
                month = value
                prayer_times = calculator.fetch_monthly_prayer_times(
                    month=month, year=year, hijri=hijri
                )
            elif period == "annual":
                year = value
                prayer_times = calculator.fetch_annual_prayer_times(
                    year=year, hijri=hijri
                )
            else:
                return JsonResponse(
                    {"error": "Invalid period. Must be 'monthly' or 'annual'."},
                    status=400,
                )

            return JsonResponse(prayer_times, safe=False)

        except KeyError as e:
            return JsonResponse({"error": f"Missing key: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)
