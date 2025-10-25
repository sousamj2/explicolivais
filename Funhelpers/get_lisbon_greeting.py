from datetime import datetime, timedelta, time
import pytz
from suntime import Sun


def get_lisbon_greeting():
    latitude, longitude = 38.7169, -9.1399
    lisbon_tz = pytz.timezone('Europe/Lisbon')
    sun = Sun(latitude, longitude)

    now = datetime.now(lisbon_tz)
    today_datetime = datetime.combine(now.date(), time.min)

    # Get sunrise and sunset for today
    sunrise_utc = sun.get_sunrise_time(today_datetime)
    sunset_utc = sun.get_sunset_time(today_datetime)

    sunrise = sunrise_utc.astimezone(lisbon_tz)
    sunset = sunset_utc.astimezone(lisbon_tz)

    # If now is past today's sunset, get sunset for tomorrow
    if now > sunset:
        tomorrow_datetime = today_datetime + timedelta(days=1)
        sunset_utc = sun.get_sunset_time(tomorrow_datetime)
        sunset = sunset_utc.astimezone(lisbon_tz)

    # If now is earlier than today's sunrise, get sunrise for yesterday
    if now < sunrise:
        yesterday_datetime = today_datetime - timedelta(days=1)
        sunrise_utc = sun.get_sunrise_time(yesterday_datetime)
        sunrise = sunrise_utc.astimezone(lisbon_tz)

    noon = now.replace(hour=12, minute=0, second=0, microsecond=0)

    if sunrise <= now < noon:
        return "Bom dia"
    elif noon <= now < sunset:
        return "Boa tarde"
    else:
        return "Boa noite"