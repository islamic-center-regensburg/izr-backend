from datetime import date, timedelta
import datetime
from pyIslam.praytimes import PrayerConf, Prayer, MethodInfo,LIST_FAJR_ISHA_METHODS,FixedTime
from pyIslam.hijri import HijriDate
import pytz
import timezonefinder
from izr_media.models import (
    PrayerConfig,
    PrayerCalculationConfig,
)  # Import the PrayerConfig model


def fixed_init(
    self,
    longitude,
    latitude,
    timezone,
    angle_ref=2,
    asr_madhab=1,
    enable_summer_time=False,
):
    self.longitude = longitude
    self.latitude = latitude
    self.timezone = timezone
    self.sherook_angle = 90.83333
    self.maghreb_angle = 90.83333

    self.asr_madhab = asr_madhab if asr_madhab == 2 else 1
    self.middle_longitude = self.timezone * 15
    self.longitude_difference = (self.middle_longitude - self.longitude) / 15
    self.summer_time = enable_summer_time

    if type(angle_ref) is int:
        method = LIST_FAJR_ISHA_METHODS[
            angle_ref - 1 if angle_ref <= len(LIST_FAJR_ISHA_METHODS) else 2
        ]
    elif type(angle_ref) is MethodInfo:  # Correct the check here
        method = angle_ref
    else:
        raise TypeError("angle_ref must be an instance of type int or MethodInfo")

    self.fajr_angle = (
        (method.fajr_angle + 90.0)
        if type(method.fajr_angle) is not FixedTime
        else method.fajr_angle
    )
    self.ishaa_angle = (
        (method.ishaa_angle + 90.0)
        if type(method.ishaa_angle) is not FixedTime
        else method.ishaa_angle
    )


# Override the original __init__ method with the fixed one
PrayerConf.__init__ = fixed_init


hijri_en_to_ar = {
    "Jumada al-Akhirah": "جمادى الآخرة",
    "Rajab": "رجب",
    "Sha’ban": "شعبان",
    "Ramadhan": "رمضان",
    "Dhu al-Qi’dah": "ذو القعدة",
    "Dhu al-Hijjah": "ذو الحجة",
    "Safar": "صفر",
    "Rabi’ al-Awwal": "ربيع الأول",
    "Rabi’ al-Thani": "ربيع الآخر",
    "Jumada al-Ula": "جمادى الأولى",
}


def get_next_prayer(prayer_times, tz):
    timezone = pytz.timezone(tz)
    current_time = datetime.datetime.now(timezone).strftime("%H:%M")
    # current_time = datetime.datetime(2024, 3, 31, 4, 53).strftime('%H:%M')
    next_prayer = None
    next_prayer_time = None
    keys = ["Shuruq", "Datum", "Hijri", "Hijri_ar", "offset", "Ramadan"]
    today = date.today()
    if today.weekday() == 4:
        keys.append("Dhuhr")
    else:
        keys.append("Jumaa")

    for prayer, time in prayer_times.items():
        if prayer not in keys:
            if time > current_time:
                if next_prayer_time is None or time < next_prayer_time:
                    next_prayer = prayer
                    next_prayer_time = time

    if next_prayer is None:
        # If no next prayer found, then the next prayer is Fajr of the following day
        next_prayer = "Fajr"
        next_prayer_time = prayer_times["Fajr"]

    return next_prayer, next_prayer_time


def getOffset(date, lat, lon):
    tf = timezonefinder.TimezoneFinder()
    tz_str = tf.certain_timezone_at(lat=lat, lng=lon)
    tz = pytz.timezone(tz_str)
    # Ensure the time is set to noon to avoid ambiguity at DST transitions
    localized_date = tz.localize(
        datetime.datetime.combine(date, datetime.time(12, 0, 0)), is_dst=None
    )
    offset_seconds = localized_date.utcoffset().total_seconds()
    offset_hours = offset_seconds / 3600
    return round(offset_hours, 1)


def getOffset_DE(date, tzone="Europe/Berlin"):
    tz = pytz.timezone(tzone)
    # Ensure the time is set to noon to avoid ambiguity at DST transitions
    localized_date = tz.localize(
        datetime.datetime.combine(date, datetime.time(12, 0, 0)), is_dst=None
    )
    offset_seconds = localized_date.utcoffset().total_seconds()
    offset_hours = offset_seconds / 3600
    return float(offset_hours)


def run_calculations(
    lon=12.102841,
    lat=49.007734,
    start_date=None,
    end_date=None,
    method=10,
    tzone="Europe/Berlin",
):

    tz = pytz.timezone(tzone)
    data = []
    today = datetime.datetime.now(tz)

    first = datetime.datetime(today.year, today.month, today.day, 12, 0, 0, tzinfo=tz)
    last = datetime.datetime(today.year, today.month, today.day, 12, 0, 0, tzinfo=tz)
    if end_date == {"y": 2024, "m": 5, "d": 25}:
        print(lon, lat, method, tzone)
    if tzone != "Europe/Berlin":
        print("today there:", first)
        print(lon, lat, method, tzone)

    if start_date != None:
        first = datetime.datetime(
            start_date["y"], start_date["m"], start_date["d"], 12, 0, 0, tzinfo=tz
        )
        last = datetime.datetime(
            end_date["y"], end_date["m"], end_date["d"], 12, 0, 0, tzinfo=tz
        )

    try:
        prayer_config = PrayerConfig.objects.latest(
            "id"
        )  # Get the latest config by ID or another field
    except PrayerConfig.DoesNotExist:
        prayer_config = None

    correction_value = prayer_config.day_correction
    current_date = first
    print("offset : ", getOffset_DE(current_date, tzone))
    while current_date <= last:
        hijri = HijriDate.get_hijri(current_date, correction_val=correction_value)
        dt = int()
        dt = getOffset_DE(current_date, tzone)
        if tzone != "Europe/Berlin":
            print("Zone : ", tzone, dt)
        if method != 10:
            pconf = PrayerConf(lon, lat, dt, method, 1)
        else:
            angle = PrayerCalculationConfig.objects.latest("id").calculation_angle
            prayertime_info = MethodInfo(9, "Custom", angle, angle, ())
            pconf = PrayerConf(lon, lat, dt, prayertime_info, 1)

        pt = Prayer(pconf, current_date)
        fajr_time = pt.fajr_time()
        fajr = (
            (
                datetime.datetime.combine(datetime.date.today(), fajr_time)
                + datetime.timedelta(minutes=1)
            ).time()
            if fajr_time.second >= 5
            else fajr_time.replace(second=0)
        )
        sherook_time = pt.sherook_time()
        sherook = (
            (
                datetime.datetime.combine(datetime.date.today(), sherook_time)
                + datetime.timedelta(minutes=1)
            ).time()
            if sherook_time.second >= 5
            else sherook_time.replace(second=0)
        )
        dohr_time = pt.dohr_time()
        dohr = (
            (
                datetime.datetime.combine(datetime.date.today(), dohr_time)
                + datetime.timedelta(minutes=1)
            ).time()
            if dohr_time.second >= 5
            else dohr_time.replace(second=0)
        )
        asr_time = pt.asr_time()
        asr = (
            (
                datetime.datetime.combine(datetime.date.today(), asr_time)
                + datetime.timedelta(minutes=1)
            ).time()
            if asr_time.second >= 5
            else asr_time.replace(second=0)
        )
        maghreb_time = pt.maghreb_time()
        maghreb = (
            (
                datetime.datetime.combine(datetime.date.today(), maghreb_time)
                + datetime.timedelta(minutes=1)
            ).time()
            if maghreb_time.second >= 5
            else maghreb_time.replace(second=0)
        )
        ishaa_time = pt.ishaa_time()
        ishaa = (
            (
                datetime.datetime.combine(datetime.date.today(), ishaa_time)
                + datetime.timedelta(minutes=1)
            ).time()
            if ishaa_time.second >= 5
            else ishaa_time.replace(second=0)
        )

        current_day_times = {
            "Datum": str(current_date.day)
            + "-"
            + str(current_date.month)
            + "-"
            + str(current_date.year),
            "Hijri": hijri.format(2),
            "Hijri_ar": hijri.format(1),
            "Fajr": fajr.strftime("%H:%M"),
            "Shuruq": sherook.strftime("%H:%M"),
            "Dhuhr": dohr.strftime("%H:%M"),
            "Asr": asr.strftime("%H:%M"),
            "Maghrib": maghreb.strftime("%H:%M"),
            "Isha": ishaa.strftime("%H:%M"),
        }
        tarawih = prayer_config.tarawih
        ramadan = prayer_config.ramadan
        if ramadan == "on":
            current_day_times["Tarawih"] = tarawih
            current_day_times["Ramadan"] = "on"
        else:
            current_day_times["Ramadan"] = "off"

        if dt == 1:
            current_day_times["Jumaa"] = "13:30"
        else:
            current_day_times["Jumaa"] = "15:00"
        next_prayer, next_prayer_time = get_next_prayer(current_day_times, tzone)
        # print(next_prayer, next_prayer_time)
        current_day_times["NextPrayer"] = {
            "prayer": next_prayer,
            "time": next_prayer_time,
        }
        data.append(current_day_times)
        # Move to the next day
        current_date += timedelta(days=1)
    if start_date == None:
        return data[0]
    return data
