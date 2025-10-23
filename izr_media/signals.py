# signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import PrayerCalculationConfig



def clear_static_cache_for_regensburg(redis_client):
    """
    Deletes both old and new static Redis cache keys for Regensburg.
    """
    patterns = [
        "prayer_times:regensburg:*:static",       # old cache keys
        "new_prayer_times:regensburg:*:static:annual"    # new API cache keys
    ]

    total_deleted = 0

    for pattern in patterns:
        count = 0
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
            count += 1
            print(f"🗑️ Deleted Redis key: {key}")

        if count == 0:
            print(f"⚠️ No keys matched pattern: {pattern}")
        else:
            print(f"✅ Deleted {count} keys for pattern: {pattern}")

        total_deleted += count

    if total_deleted == 0:
        print("⚠️ No static cache keys found for Regensburg (old or new).")
    else:
        print(f"✅ Deleted total of {total_deleted} static cache entries for Regensburg.")



@receiver([post_save, post_delete], sender=PrayerCalculationConfig)
def delete_cache_on_change(sender, instance, **kwargs):
    redis_client = settings.REDIS_CLIENT
    clear_static_cache_for_regensburg(redis_client)
