import os
from dotenv import load_dotenv
load_dotenv()

from pprint import pprint

from datetime import datetime, time, timedelta
from suntime import Sun
import pytz

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

def dictify_real_dict_row(row):
    def convert_value(val):
        if isinstance(val, datetime):
            return val.isoformat()
        if isinstance(val, list):
            return [convert_value(i) for i in val]
        if isinstance(val, dict):
            return {k: convert_value(v) for k, v in val.items()}
        return val

    return {k: convert_value(v) for k, v in row.items()}

def convert_datetimes(obj):
    if isinstance(obj, dict):
        return {k: convert_datetimes(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_datetimes(elem) for elem in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj
    
def mask_email(email):
    # Mask email username partially e.g. ma***@email.com
    parts = email.split('@')
    if len(parts[0]) <= 2:
        return "***@" + parts[1]
    return parts[0][:2] + "*****@" + parts[1]


def check_ip_in_portugal(ip):
    import requests
    try:
        # No token used here, but recommended to add your token as ?token=YOUR_TOKEN if needed
        url = f"https://ipinfo.io/{ip}/json"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("bogon", True):
                pprint(f"Bogon IP detected: {ip}")
                return True  # Bogon IPs are treated as local/trusted

            country_code = data.get("country", "").upper()
            region = data.get("region", "").lower()
            # Check country PT and region Lisboa or Lisbon (case insensitive)
            if country_code == "PT" and region in ["lisboa", "lisbon"]:
                return True
    except Exception as e:
        print(f"IP geolocation failed: {e}")
    return False


# if __name__ == "__main__":
#     # Example usage
#     insert_user("John Doe", "john.doe2@example.com", "123 Main St", "12345", "556-1234", "123.57.89.0")

def results_to_html_table(results):
    if not results or not isinstance(results, list):
        return "<p>No data found.</p>"
    
    if isinstance(results[0],str):
        return results

    # Extract columns from keys of the first row dict
    columns = results[0].keys()
    
    table_html = '<table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse;">'
    
    # Header row
    table_html += '<thead><tr>'
    for col in columns:
        table_html += f'<th>{col}</th>'
    table_html += '</tr></thead>'
    
    # Data rows
    table_html += '<tbody>'
    for row in results:
        table_html += '<tr>'
        for col in columns:
            val = row[col]
            table_html += f'<td>{val if val is not None else ""}</td>'
        table_html += '</tr>'
    table_html += '</tbody></table>'
    
    return table_html

