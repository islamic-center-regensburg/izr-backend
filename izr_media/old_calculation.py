from datetime import datetime, time, timedelta
from pyIslam.praytimes import PrayerConf, Prayer, MethodInfo, LIST_FAJR_ISHA_METHODS, FixedTime
from pyIslam.hijri import HijriDate
from pytz import timezone
from timezonefinder import TimezoneFinder
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
        raise TypeError(
            "angle_ref must be an instance of type int or MethodInfo")

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


def round_time_to_minute(time):
    """
    Rounds time to the nearest minute: 
    If seconds >= 30, round up, otherwise round down.
    """
    from datetime import datetime, timedelta

    # Convert time to a datetime object
    temp_datetime = datetime.combine(datetime.today(), time)

    # Round the time
    if temp_datetime.second >= 5:
        rounded_time = (temp_datetime + timedelta(minutes=1)
                        ).replace(second=0, microsecond=0)
    else:
        rounded_time = temp_datetime.replace(second=0, microsecond=0)

    return rounded_time.time()


class OldPrayerTimesCalculator:
    def __init__(self, start_date, end_date, longitude, latitude, method=10):
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
        self.longitude = longitude
        self.latitude = latitude
        self.tz_finder = TimezoneFinder()
        self.method = method

    def get_prayer_times(self):
        prayer_times_list = []
        calc_config = PrayerCalculationConfig.objects.first()

        correction_day = calc_config.correction_day
        if self.method == 10:
            custom_fajr_angle = calc_config.fajr_angle
            custom_isha_angle = calc_config.isha_angle
            fajr_isha_method = MethodInfo(
                9, "Custom", custom_fajr_angle, custom_isha_angle)
        else:
            fajr_isha_method = self.method

        asr_fiqh = 1

        for day in range((self.end_date - self.start_date).days + 1):
            current_date = self.start_date + timedelta(days=day)
            tz_name = self.tz_finder.timezone_at(
                lng=self.longitude, lat=self.latitude)
            local_tz = timezone(tz_name)
            utc_offset = local_tz.utcoffset(datetime.combine(
                current_date, time(12, 0))).total_seconds() / 3600

            prayer_conf = PrayerConf(
                self.longitude, self.latitude, utc_offset, fajr_isha_method, asr_fiqh)
            prayer = Prayer(prayer_conf, current_date)
            hijri = HijriDate.get_hijri(
                current_date, correction_val=correction_day)

            prayer_times = {
                "Datum": current_date.strftime("%d-%m-%Y"),
                "Hijri": hijri.format(2),
                "Hijri_ar": hijri.format(1),
                "Fajr": round_time_to_minute(prayer.fajr_time()).strftime("%H:%M"),
                "Shuruq": round_time_to_minute(prayer.sherook_time()).strftime("%H:%M"),
                "Dhuhr": round_time_to_minute(prayer.dohr_time()).strftime("%H:%M"),
                "Asr": round_time_to_minute(prayer.asr_time()).strftime("%H:%M"),
                "Maghrib": round_time_to_minute(prayer.maghreb_time()).strftime("%H:%M"),
                "Isha": round_time_to_minute(prayer.ishaa_time()).strftime("%H:%M"),
                "Ramadan": calc_config.ramadan,
                "Jumaa": calc_config.jumaa_time.strftime("%H:%M"),
                "Tarawih": calc_config.tarawih_time.strftime("%H:%M"),
            }

            prayer_times_list.append(prayer_times)
        return prayer_times_list
