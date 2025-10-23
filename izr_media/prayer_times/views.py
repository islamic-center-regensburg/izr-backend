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
    if request.method != "GET":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        # --- Base setup ---
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        day_of_year = today.timetuple().tm_yday
        current_year = today.year

        # --- Fetch latest configuration ---
        config = PrayerCalculationConfig.objects.latest("id")
        calculation_type = config.calculation_type  # "static" or "dynamic"

        # --- Redis setup ---
        redis_client = settings.REDIS_CLIENT
        redis_key = f"new_prayer_times:regensburg:{current_year}:{calculation_type}:annual"

        # --- Try reading cached annual data ---
        cached_data = redis_client.get(redis_key)
        if cached_data:
            print(f"✅ Found cached {calculation_type} prayer times for {current_year} in Redis")

            # Parse and return today's record
            cached = json.loads(cached_data)
            today_entry = next((item for item in cached if item.get("Day") == day_of_year), None)

            if today_entry:
                today_entry["Jumaa"] = str(config.jumaa_time)[:5]
                if config.ramadan == "on":
                    today_entry["Tarawih"] = str(config.tarawih_time)[:5]

                response = JsonResponse(today_entry, safe=False)
                response["Access-Control-Allow-Origin"] = "*"
                return response
            else:
                print(f"⚠️ Day {day_of_year} not found in cache; recalculating below...")

        # --- No cache found → calculate manually ---
        if calculation_type == "dynamic":
            angles = get_regensburg_angles()
            if not angles or "fajr_angle" not in angles or "isha_angle" not in angles:
                print("⚠️ get_regensburg_angles() returned invalid data, using static fallback")
                fajr_angle = config.fajr_angle
                isha_angle = config.isha_angle
            else:
                fajr_angle = angles["fajr_angle"]
                isha_angle = angles["isha_angle"]
        else:
            fajr_angle = config.fajr_angle
            isha_angle = config.isha_angle

        # --- Initialize calculator ---
        calculator = PrayerTimesCalculator(
            latitude=config.default_latitude,
            longitude=config.default_longitude,
            calculation_method="izr",
            fajr_angle=fajr_angle,
            isha_angle=isha_angle,
            tune=True,
            imsak_tune=config.imsak_tune,
            fajr_tune=config.fajr_tune,
            sunrise_tune=config.sunrise_tune,
            dhuhr_tune=config.dhuhr_tune,
            asr_tune=config.asr_tune,
            maghrib_tune=config.maghrib_tune,
            sunset_tune=config.sunset_tune,
            isha_tune=config.isha_tune,
            midnight_tune=config.midnight_tune,
        )

        # --- Fetch and format daily times ---
        prayer_times = calculator.fetch_daily_prayer_times(today_str)
        prayer_times["Jumaa"] = str(config.jumaa_time)[:5]
        if config.ramadan == "on":
            prayer_times["Tarawih"] = str(config.tarawih_time)[:5]

        # --- Return final response ---
        response = JsonResponse(prayer_times, safe=False)
        response["Access-Control-Allow-Origin"] = "*"
        return response

    except Exception as e:
        print("❌ Error in get_today_prayer_times:", e)
        return JsonResponse({"error": str(e)}, status=500)



def get_prayer_times(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body)
        config = PrayerCalculationConfig.objects.latest("id")

        # ─── Extract parameters ───────────────────────────────────
        city_name = data.get("city_name", "Regensburg")
        city_lower = city_name.lower()
        lat = data.get("lat", config.default_latitude)
        lng = data.get("lng", config.default_longitude)
        method = data.get("method", "izr")
        period = data.get("period", "annual")  # only annual is supported
        value = data.get("value")              # year
        hijri = data.get("hijri", False)
        calculation_type = config.calculation_type  # "static" or "dynamic"

        # ─── Validate inputs ──────────────────────────────────────
        if lat is None or lng is None:
            return JsonResponse(
                {"error": "Latitude and Longitude must be provided"}, status=400
            )
        if period != "annual":
            return JsonResponse(
                {"error": "Only 'annual' calculations are supported. Use period='annual'."},
                status=400,
            )

        # ─── Redis setup ──────────────────────────────────────────
        redis_client = settings.REDIS_CLIENT
        current_year = datetime.now().year
        year = value or current_year
        redis_key = f"new_prayer_times:{city_lower}:{year}:{calculation_type}:annual"

        # ─── Try returning cached data ─────────────────────────────
        cached_data = redis_client.get(redis_key)
        if cached_data:
            print(f"✅ Returning cached {calculation_type} data for {city_name} ({year})")
            return JsonResponse(json.loads(cached_data), safe=False)

        # ─── Build calculator configuration ───────────────────────
        tune = True if city_lower == "regensburg" else False
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

        # ─── Initialize calculator ────────────────────────────────
        calculator = PrayerTimesCalculator(
            latitude=lat,
            longitude=lng,
            calculation_method=method,
            fajr_angle=config.fajr_angle,   # always from config
            isha_angle=config.isha_angle,   # always from config
            tune=tune,
            **tuning_params,
        )

        # ─── Compute annual prayer times ───────────────────────────
        prayer_times = calculator.fetch_annual_prayer_times(year=year, hijri=hijri)

        # ─── Apply Fourier smoothing only for Regensburg dynamic ──
        if city_lower == "regensburg" and calculation_type == "dynamic":
            csv_path = Path(__file__).parent / "prayer-times-isha-fajr-fourier-fit.csv"
            prayer_df = pd.DataFrame(prayer_times)
            prayer_df["Day"] = np.arange(1, len(prayer_df) + 1)
            csv_df = pd.read_csv(csv_path, delimiter=";")
            if {"Day", "Fajr", "Isha"} <= set(csv_df.columns):
                merged = prayer_df.merge(
                    csv_df[["Day", "Fajr", "Isha"]],
                    on="Day",
                    how="left",
                    suffixes=('', '_csv')
                )
                merged["Fajr"] = merged["Fajr_csv"].fillna(merged["Fajr"])
                merged["Isha"] = merged["Isha_csv"].fillna(merged["Isha"])
                merged = merged.drop(columns=["Fajr_csv", "Isha_csv"])
                prayer_times = merged.to_dict(orient="records")

        # ─── Cache annual result ──────────────────────────────────
        end_of_year = datetime(current_year, 12, 31, 23, 59, 59)
        ttl = int((end_of_year - datetime.now()).total_seconds())
        redis_client.setex(redis_key, ttl, json.dumps(prayer_times))
        print(f"✅ Cached annual prayer times in Redis ({redis_key})")

        # ─── Return response ───────────────────────────────────────
        return JsonResponse(prayer_times, safe=False)

    except KeyError as e:
        return JsonResponse({"error": f"Missing key: {str(e)}"}, status=400)
    except Exception as e:
        print("❌ Error in get_prayer_times:", e)
        return JsonResponse({"error": str(e)}, status=500)
