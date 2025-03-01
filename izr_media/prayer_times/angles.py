from izr_media.models import (
    PrayerCalculationConfig,
)  # Import the PrayerConfig model


def get_regensburg_angles():
    config = PrayerCalculationConfig.objects.latest("id")
    if config.calculation_type == "static":
        return {"fajr_angle": config.fajr_angle, "isha_angle": config.isha_angle}
    else:
        print("get_regensburg_angles : DYNAMIC calculation not implemented yet! ")
